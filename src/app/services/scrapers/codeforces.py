"""Scraper implementation for Codeforces problems."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

import httpx
from bs4 import BeautifulSoup, Tag
from tenacity import retry, stop_after_attempt, wait_exponential

from app.services.models import ScrapeQuery, ScrapedProblem, Testcase
from app.services.scrapers.base import Scraper, ScraperError, ScraperResult

API_URL = "https://codeforces.com/api/problemset.problems"
PROBLEM_URL_TEMPLATE = "https://codeforces.com/problemset/problem/{contest_id}/{index}"

_DIFFICULTY_RANGES: Dict[str, range] = {
    "easy": range(800, 1300),
    "medium": range(1300, 1800),
    "hard": range(1800, 2300),
    "expert": range(2300, 4000),
}

_TOPIC_MAP: Dict[str, str] = {
    "sorting": "sortings",
    "graphs": "graphs",
    "dp": "dp",
    "math": "math",
    "strings": "strings",
}


@dataclass
class _ProblemInfo:
    contest_id: int
    index: str
    name: str
    rating: Optional[int]
    tags: List[str]

    @property
    def code(self) -> str:
        return f"CF{self.contest_id}{self.index}"

    @property
    def url(self) -> str:
        return PROBLEM_URL_TEMPLATE.format(contest_id=self.contest_id, index=self.index)


class CodeforcesScraper(Scraper):
    site_name = "Codeforces"

    def __init__(self, client: Optional[httpx.Client] = None) -> None:
        self._client = client or httpx.Client(headers={"User-Agent": "ProblemScraper/0.1"}, timeout=10.0)
        self._problem_cache: Dict[Tuple[int, str], _ProblemInfo] = {}

    def fetch(self, query: ScrapeQuery, limit: int) -> ScraperResult:
        if limit <= 0:
            return ScraperResult(site=self.site_name, problems=[])

        topics = [_TOPIC_MAP.get(topic, topic) for topic in query.topics]
        candidates = self._load_candidates(topics, query.difficulty)

        collected: List[ScrapedProblem] = []
        for info in candidates:
            if len(collected) >= limit:
                break
            try:
                collected.append(self._fetch_problem_details(info))
            except ScraperError:
                continue

        return ScraperResult(site=self.site_name, problems=collected)

    def _load_candidates(self, topics: List[str], difficulty: Optional[str]) -> Iterable[_ProblemInfo]:
        params: Dict[str, str] = {}
        if topics:
            params["tags"] = ";".join(topics)

        response = self._client.get(API_URL, params=params)
        if response.status_code != 200:
            raise ScraperError(f"Codeforces API error: {response.status_code}")

        payload = response.json()
        if payload.get("status") != "OK":
            raise ScraperError("Codeforces API returned failure status")

        problems_data = payload.get("result", {}).get("problems", [])
        for entry in problems_data:
            info = _ProblemInfo(
                contest_id=entry.get("contestId"),
                index=entry.get("index"),
                name=entry.get("name", ""),
                rating=entry.get("rating"),
                tags=entry.get("tags", []),
            )
            if not info.contest_id or not info.index:
                continue
            if difficulty and not self._matches_difficulty(info, difficulty):
                continue
            self._problem_cache[(info.contest_id, info.index)] = info
            yield info

    def _matches_difficulty(self, info: _ProblemInfo, difficulty: str) -> bool:
        if info.rating is None:
            return False
        rating_range = _DIFFICULTY_RANGES.get(difficulty)
        if rating_range is None:
            return True
        return info.rating in rating_range

    @retry(reraise=True, stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=4))
    def _fetch_problem_page(self, url: str) -> str:
        response = self._client.get(url)
        if response.status_code != 200:
            raise ScraperError(f"Failed to fetch problem page: {url}")
        return response.text

    def fetch_problem(self, contest_id: int, index: str) -> ScrapedProblem:
        key = (contest_id, index.upper())
        info = self._problem_cache.get(key)
        if info is None:
            info = self._lookup_problem(contest_id, index)
        return self._fetch_problem_details(info)

    def _lookup_problem(self, contest_id: int, index: str) -> _ProblemInfo:
        response = self._client.get(API_URL)
        if response.status_code != 200:
            raise ScraperError(f"Codeforces API error: {response.status_code}")

        payload = response.json()
        if payload.get("status") != "OK":
            raise ScraperError("Codeforces API returned failure status")

        for entry in payload.get("result", {}).get("problems", []):
            if entry.get("contestId") == contest_id and str(entry.get("index")).upper() == index.upper():
                info = _ProblemInfo(
                    contest_id=contest_id,
                    index=index.upper(),
                    name=entry.get("name", ""),
                    rating=entry.get("rating"),
                    tags=entry.get("tags", []),
                )
                self._problem_cache[(info.contest_id, info.index)] = info
                return info
        raise ScraperError("Problem not found in Codeforces problemset")

    def _fetch_problem_details(self, info: _ProblemInfo) -> ScrapedProblem:
        html = self._fetch_problem_page(info.url)
        soup = BeautifulSoup(html, "html.parser")
        statement_node = soup.select_one(".problem-statement")
        if not statement_node:
            raise ScraperError("Missing statement")

        statement_text, effective_title = self._render_statement(info, statement_node)
        testcases = self._extract_samples(statement_node)
        if not testcases:
            raise ScraperError("No sample tests found")

        problem_title = effective_title or info.name or info.code

        return ScrapedProblem(
            site=self.site_name,
            code=info.code,
            title=problem_title,
            statement_markdown=statement_text,
            source_url=info.url,
            testcases=testcases,
        )

    def _render_statement(self, info: _ProblemInfo, node: Tag) -> Tuple[str, Optional[str]]:
        title_node = node.select_one(".header .title")
        display_title = info.name
        if title_node:
            header_title = title_node.get_text(strip=True)
            if header_title:
                split_parts = header_title.split(". ", 1)
                display_title = split_parts[1] if len(split_parts) > 1 else header_title

        time_limit = self._extract_limit(node, ".time-limit", "time limit per test")
        memory_limit = self._extract_limit(node, ".memory-limit", "memory limit per test")

        lines: List[str] = [f"# {display_title}", ""]
        if time_limit:
            lines.append(f"**Time Limit:** {time_limit}")
        if memory_limit:
            lines.append(f"**Memory Limit:** {memory_limit}")
        if time_limit or memory_limit:
            lines.append("")

        legend = self._statement_body(node)
        if legend:
            lines.append("## Statement")
            lines.append("")
            lines.append(self._normalise_section(legend))
            lines.append("")

        for css_class in ("input-specification", "output-specification", "note"):
            section = node.select_one(f".{css_class}")
            if not section:
                continue
            title = section.select_one(".section-title")
            section_title = title.get_text(strip=True) if title else css_class.replace("-", " ").title()
            if title:
                title.decompose()
            lines.append(f"## {section_title}")
            lines.append("")
            lines.append(self._normalise_section(section))
            lines.append("")

        markdown = "\n".join(line.rstrip() for line in lines if line is not None)
        return markdown.strip() + "\n", display_title

    def _extract_samples(self, node: BeautifulSoup) -> List[Testcase]:
        samples: List[Testcase] = []
        sample_container = node.select_one(".sample-test")
        if not sample_container:
            return samples

        inputs = sample_container.select("div.input pre")
        outputs = sample_container.select("div.output pre")
        pairs = zip(inputs, outputs)
        for idx, (input_node, output_node) in enumerate(pairs, start=1):
            input_text = self._normalise_pre(input_node)
            output_text = self._normalise_pre(output_node)
            samples.append(Testcase(index=idx, input_data=input_text, output_data=output_text))
        return samples

    def _normalise_pre(self, node) -> str:
        text = node.get_text("\n", strip=False)
        # Preserve blank lines and trailing newline expected by judge runners.
        text = text.replace("\r", "")
        if not text.endswith("\n"):
            text += "\n"
        return text

    def _normalise_section(self, node: Tag) -> str:
        for br in node.find_all("br"):
            br.replace_with("\n")
        text = node.get_text("\n", strip=True).replace("\r", "")
        lines = [line.rstrip() for line in text.splitlines()]
        return "\n".join(lines)

    def _extract_limit(self, node: Tag, selector: str, prefix: str) -> Optional[str]:
        element = node.select_one(selector)
        if not element:
            return None
        text = element.get_text(" ", strip=True)
        return text.replace(prefix, "").strip()

    def _statement_body(self, node: Tag) -> Optional[Tag]:
        legend = node.select_one(".legend")
        if legend:
            return legend

        for child in node.find_all(recursive=False):
            child_classes = set(child.get("class", []))
            if not child_classes:
                if child.name in {"div", "p"}:
                    return child
                continue
            if {"header", "input-specification", "output-specification", "sample-test", "note"} & child_classes:
                continue
            return child
        return None
