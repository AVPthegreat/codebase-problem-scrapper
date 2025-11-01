"""Live scraper implementation for GeeksforGeeks practice problems."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

import httpx
from bs4 import BeautifulSoup

from app.services.models import ScrapeQuery, ScrapedProblem, Testcase
from app.services.scrapers.base import Scraper, ScraperError, ScraperResult

_HEADERS = {"User-Agent": "ProblemScraper/0.1"}
_PROBLEM_URL_TEMPLATE = "https://www.geeksforgeeks.org/problems/{slug}/1"


@dataclass
class _GFGProblem:
    slug: str
    difficulty: str
    topics: List[str]


_PROBLEM_BANK: List[_GFGProblem] = [
    _GFGProblem("value-equal-to-index-value1330", "easy", ["arrays", "searching"]),
    _GFGProblem("palindrome-string0817", "easy", ["strings"]),
    _GFGProblem("kadanes-algorithm-1587115620", "medium", ["arrays", "dp"]),
    _GFGProblem("detect-loop-in-linked-list", "medium", ["linked list", "hashing"]),
    _GFGProblem("topological-sort", "hard", ["graphs"]),
    _GFGProblem("longest-sub-array-with-sum-k0809", "hard", ["arrays", "hashing"]),
]

_DIFFICULTY_ORDER = {"easy": 0, "medium": 1, "hard": 2, "expert": 2, None: 0}


class GeeksforGeeksScraper(Scraper):
    site_name = "GeeksforGeeks"

    def __init__(self, client: Optional[httpx.Client] = None) -> None:
        self._client = client or httpx.Client(headers=_HEADERS, timeout=20.0)

    def fetch(self, query: ScrapeQuery, limit: int) -> ScraperResult:
        if limit <= 0:
            return ScraperResult(site=self.site_name, problems=[])

        candidates = self._select_candidates(query, limit * 2)
        problems: List[ScrapedProblem] = []
        for candidate in candidates:
            if len(problems) >= limit:
                break
            try:
                problems.append(self._fetch_problem(candidate))
            except ScraperError:
                continue
        return ScraperResult(site=self.site_name, problems=problems)

    def fetch_problem_by_slug(self, slug: str) -> ScrapedProblem:
        return self._fetch_problem(_GFGProblem(slug=slug, difficulty="easy", topics=[]))

    def _select_candidates(self, query: ScrapeQuery, budget: int) -> Iterable[_GFGProblem]:
        target_rank = _DIFFICULTY_ORDER.get(query.difficulty, 0)
        topics = set(topic.lower() for topic in query.topics)

        ranked = sorted(_PROBLEM_BANK, key=lambda item: (_DIFFICULTY_ORDER[item.difficulty], item.slug))
        selected: List[_GFGProblem] = []
        for problem in ranked:
            if len(selected) >= budget:
                break
            if _DIFFICULTY_ORDER[problem.difficulty] < target_rank:
                continue
            if topics and not (topics & {topic.lower() for topic in problem.topics}):
                continue
            selected.append(problem)

        if not selected:
            selected = ranked[:budget]
        return selected

    def _fetch_problem(self, problem: _GFGProblem) -> ScrapedProblem:
        url = _PROBLEM_URL_TEMPLATE.format(slug=problem.slug)
        response = self._client.get(url)
        if response.status_code != 200:
            raise ScraperError(f"GeeksforGeeks HTTP error: {response.status_code}")

        soup = BeautifulSoup(response.text, "html.parser")
        next_data = soup.find("script", id="__NEXT_DATA__")
        if not next_data or not next_data.string:
            raise ScraperError("GeeksforGeeks payload missing Next.js state")

        state = json.loads(next_data.string)
        initial_state = state.get("props", {}).get("pageProps", {}).get("initialState", {})
        prob_data = initial_state.get("problemData", {}).get("allData", {}).get("probData")
        if not isinstance(prob_data, dict):
            raise ScraperError("GeeksforGeeks problem data unavailable")

        statement_html = prob_data.get("problem_question", "")
        if not statement_html:
            raise ScraperError("GeeksforGeeks problem missing statement")

        statement_markdown, testcases = self._render_problem(statement_html)
        if not testcases:
            raise ScraperError("GeeksforGeeks problem missing sample cases")

        title = prob_data.get("problem_name", problem.slug.replace("-", " ").title())
        difficulty = prob_data.get("problem_level_text") or problem.difficulty.title()
        metadata_lines = [f"# {title}", "", f"**Difficulty:** {difficulty}"]
        if prob_data.get("marks"):
            metadata_lines.append(f"**Marks:** {prob_data['marks']}")
        metadata_lines.extend(["", statement_markdown])
        markdown = "\n".join(line.rstrip() for line in metadata_lines if line is not None).strip() + "\n"

        code = f"GFG-{prob_data.get('slug', problem.slug).replace('-', '_').upper()}"

        return ScrapedProblem(
            site=self.site_name,
            code=code,
            title=title,
            statement_markdown=markdown,
            source_url=url,
            testcases=testcases,
        )

    def _render_problem(self, html: str) -> tuple[str, List[Testcase]]:
        soup = BeautifulSoup(html, "html.parser")
        samples = self._extract_samples(soup)
        for pre in soup.find_all("pre"):
            pre.decompose()
        for br in soup.find_all("br"):
            br.replace_with("\n")
        body = soup.get_text("\n", strip=True)
        lines = [line.rstrip() for line in body.splitlines() if line.strip()]
        text = "\n".join(lines)
        return text, samples

    def _extract_samples(self, soup: BeautifulSoup) -> List[Testcase]:
        cases: List[Testcase] = []
        for index, pre in enumerate(soup.find_all("pre"), start=1):
            text = pre.get_text("\n", strip=False)
            parsed = self._parse_sample_block(text)
            if not parsed:
                continue
            cases.append(
                Testcase(
                    index=index,
                    input_data=self._ensure_newline(parsed["input"]),
                    output_data=self._ensure_newline(parsed["output"]),
                )
            )
        return cases

    def _parse_sample_block(self, text: str) -> Optional[Dict[str, str]]:
        input_lines: List[str] = []
        output_lines: List[str] = []
        current: Optional[str] = None
        for raw_line in text.splitlines():
            stripped = raw_line.strip()
            lower = stripped.lower()
            if lower.startswith("input:"):
                current = "input"
                remainder = stripped.split(":", 1)[1].strip()
                if remainder:
                    input_lines.append(remainder)
                continue
            if lower.startswith("output:"):
                current = "output"
                remainder = stripped.split(":", 1)[1].strip()
                if remainder:
                    output_lines.append(remainder)
                continue
            if lower.startswith("explanation"):
                current = None
                continue
            if not stripped:
                current = None
                continue
            if current == "input":
                input_lines.append(stripped)
            elif current == "output":
                output_lines.append(stripped)

        if not input_lines or not output_lines:
            return None
        return {
            "input": "\n".join(input_lines),
            "output": "\n".join(output_lines),
        }

    def _ensure_newline(self, text: str) -> str:
        clean = text.replace("\r", "")
        if not clean.endswith("\n"):
            clean += "\n"
        return clean
