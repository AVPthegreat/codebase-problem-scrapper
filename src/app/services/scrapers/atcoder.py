"""Live scraper implementation for AtCoder problems."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

import httpx
from bs4 import BeautifulSoup, Tag

from app.services.models import ScrapeQuery, ScrapedProblem, Testcase
from app.services.scrapers.base import Scraper, ScraperError, ScraperResult

_ARCHIVE_URL = "https://atcoder.jp/contests/archive"
_TASK_URL_TEMPLATE = "https://atcoder.jp/contests/{contest}/tasks/{task}?lang=en"
_HEADERS = {"User-Agent": "ProblemScraper/0.1"}

_DIFFICULTY_LETTERS: Dict[Optional[str], List[str]] = {
    None: ["a"],
    "easy": ["a"],
    "medium": ["c", "b"],
    "hard": ["d", "c"],
    "expert": ["e", "d"],
}


@dataclass
class _TaskRef:
    contest: str
    letter: str

    @property
    def task_id(self) -> str:
        return f"{self.contest}_{self.letter}"


class AtCoderScraper(Scraper):
    site_name = "AtCoder"

    def __init__(self, client: Optional[httpx.Client] = None) -> None:
        self._client = client or httpx.Client(headers=_HEADERS, timeout=20.0)

    def fetch(self, query: ScrapeQuery, limit: int) -> ScraperResult:
        if limit <= 0:
            return ScraperResult(site=self.site_name, problems=[])

        letters = _DIFFICULTY_LETTERS.get(query.difficulty, ["a"])
        contests = self._list_contests(len(letters) * limit * 2)

        candidates = self._enumerate_tasks(contests, letters)
        problems: List[ScrapedProblem] = []
        for ref in candidates:
            if len(problems) >= limit:
                break
            try:
                problems.append(self._fetch_task(ref))
            except ScraperError:
                continue
        return ScraperResult(site=self.site_name, problems=problems)

    def fetch_problem(self, contest: str, letter: str) -> ScrapedProblem:
        return self._fetch_task(_TaskRef(contest=contest, letter=letter.lower()))

    def _list_contests(self, budget: int) -> List[str]:
        contests: List[str] = []
        page = 1
        while len(contests) < budget and page <= 5:
            response = self._client.get(_ARCHIVE_URL, params={"category": "abc", "lang": "en", "page": page})
            if response.status_code != 200:
                raise ScraperError(f"AtCoder archive fetch failed: {response.status_code}")
            soup = BeautifulSoup(response.text, "html.parser")
            for link in soup.select("td a[href^='/contests/abc']"):
                contest = link["href"].split("/")[-1]
                if contest not in contests:
                    contests.append(contest)
            page += 1
        if not contests:
            raise ScraperError("AtCoder archive returned no contests")
        return contests

    def _enumerate_tasks(self, contests: Iterable[str], letters: List[str]) -> Iterable[_TaskRef]:
        for contest in contests:
            for letter in letters:
                yield _TaskRef(contest=contest, letter=letter.lower())

    def _fetch_task(self, ref: _TaskRef) -> ScrapedProblem:
        url = _TASK_URL_TEMPLATE.format(contest=ref.contest, task=ref.task_id)
        response = self._client.get(url)
        if response.status_code != 200:
            raise ScraperError(f"AtCoder task fetch failed: {response.status_code}")

        soup = BeautifulSoup(response.text, "html.parser")
        statement_root = soup.find("div", id="task-statement")
        if not statement_root:
            raise ScraperError("AtCoder task statement missing")
        lang_en = statement_root.find("span", class_="lang-en")
        if not lang_en:
            raise ScraperError("AtCoder English statement unavailable")

        title = self._extract_title(soup)
        markdown = self._render_statement(lang_en, title)
        testcases = self._extract_samples(lang_en)
        if not testcases:
            raise ScraperError("AtCoder problem missing sample cases")

        code = ref.task_id.upper()

        return ScrapedProblem(
            site=self.site_name,
            code=code,
            title=title,
            statement_markdown=markdown,
            source_url=url,
            testcases=testcases,
        )

    def _extract_title(self, soup: BeautifulSoup) -> str:
        title_tag = soup.find("title")
        if title_tag:
            return title_tag.get_text(strip=True)
        return "AtCoder Problem"

    def _render_statement(self, lang_en: BeautifulSoup, title: str) -> str:
        lines: List[str] = [f"# {title}", ""]
        for part in lang_en.find_all("div", class_="part"):
            heading_tag = part.find("h3")
            heading = heading_tag.get_text(strip=True) if heading_tag else ""
            if heading.lower().startswith("sample"):
                continue
            content = self._normalise_part(part)
            if not content:
                continue
            if heading:
                lines.append(f"## {heading}")
                lines.append("")
            lines.append(content)
            lines.append("")
        return "\n".join(line.rstrip() for line in lines if line is not None).strip() + "\n"

    def _normalise_part(self, part: Tag) -> str:
        part_clone = BeautifulSoup(str(part), "html.parser")
        heading = part_clone.find("h3")
        if heading:
            heading.decompose()
        blocks: List[str] = []
        for element in part_clone.children:
            if getattr(element, "name", None) == "pre":
                text = element.get_text("\n", strip=False).strip("\r")
                blocks.append("```\n" + text.rstrip("\n") + "\n```")
            elif getattr(element, "name", None) in {"p", "div", "span", "ul", "ol"}:
                blocks.append(element.get_text("\n", strip=True))
            elif isinstance(element, str):
                stripped = element.strip()
                if stripped:
                    blocks.append(stripped)
        joined = "\n\n".join(block.strip() for block in blocks if block)
        lines = [line.rstrip() for line in joined.splitlines() if line.strip()]
        return "\n".join(lines)

    def _extract_samples(self, lang_en: BeautifulSoup) -> List[Testcase]:
        samples: Dict[int, Dict[str, str]] = {}
        for part in lang_en.find_all("div", class_="part"):
            heading_tag = part.find("h3")
            if not heading_tag:
                continue
            title = heading_tag.get_text(strip=True)
            if not title.lower().startswith("sample"):
                continue
            pre = part.find("pre")
            if not pre:
                continue
            text = pre.get_text("\n", strip=False)
            index = self._extract_sample_index(title)
            store = samples.setdefault(index, {})
            if "input" in title.lower():
                store["input"] = text
            elif "output" in title.lower():
                store["output"] = text
        collected: List[Testcase] = []
        for index in sorted(samples):
            entry = samples[index]
            if "input" not in entry or "output" not in entry:
                continue
            collected.append(
                Testcase(
                    index=index,
                    input_data=self._ensure_newline(entry["input"]),
                    output_data=self._ensure_newline(entry["output"]),
                )
            )
        return collected

    def _extract_sample_index(self, title: str) -> int:
        match = re.search(r"(\d+)", title)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                pass
        return len(title)

    def _ensure_newline(self, text: str) -> str:
        clean = text.replace("\r", "")
        if not clean.endswith("\n"):
            clean += "\n"
        return clean
