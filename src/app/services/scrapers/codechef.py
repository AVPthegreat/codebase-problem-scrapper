"""Live scraper implementation for CodeChef practice problems."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

import httpx
from bs4 import BeautifulSoup

from app.services.models import ScrapeQuery, ScrapedProblem, Testcase
from app.services.scrapers.base import Scraper, ScraperError, ScraperResult

_LIST_URL = "https://www.codechef.com/api/list/problems"
_DETAIL_URL_TEMPLATE = "https://www.codechef.com/api/contests/PRACTICE/problems/{code}"
_HEADERS = {"User-Agent": "ProblemScraper/0.1"}

_CATEGORY_BY_DIFFICULTY: Dict[Optional[str], str] = {
    None: "school",
    "easy": "school",
    "medium": "easy",
    "hard": "medium",
    "expert": "hard",
}


@dataclass
class _ProblemStub:
    code: str
    name: str
    rating: Optional[int]


class CodeChefScraper(Scraper):
    site_name = "CodeChef"

    def __init__(self, client: Optional[httpx.Client] = None) -> None:
        self._client = client or httpx.Client(headers=_HEADERS, timeout=20.0)

    def fetch(self, query: ScrapeQuery, limit: int) -> ScraperResult:
        if limit <= 0:
            return ScraperResult(site=self.site_name, problems=[])

        category = _CATEGORY_BY_DIFFICULTY.get(query.difficulty, "school")
        search = self._build_search(query.topics)
        candidates = self._list_candidates(category, search, limit * 3)

        problems: List[ScrapedProblem] = []
        for stub in candidates:
            if len(problems) >= limit:
                break
            try:
                problems.append(self._fetch_problem_details(stub.code))
            except ScraperError:
                continue
        return ScraperResult(site=self.site_name, problems=problems)

    def fetch_problem_by_code(self, problem_code: str) -> ScrapedProblem:
        return self._fetch_problem_details(problem_code)

    def _list_candidates(self, category: str, search: Optional[str], budget: int) -> Iterable[_ProblemStub]:
        params = {"category": category, "limit": max(20, budget), "offset": 0}
        if search:
            params["search"] = search

        response = self._client.get(_LIST_URL, params=params)
        if response.status_code != 200:
            raise ScraperError(f"CodeChef list API error: {response.status_code}")

        payload = response.json()
        if payload.get("status") != "success":
            raise ScraperError("CodeChef list API returned failure status")

        for entry in payload.get("data", []):
            code = entry.get("code")
            if not code:
                continue
            yield _ProblemStub(
                code=code,
                name=entry.get("name", code),
                rating=self._parse_int(entry.get("difficulty_rating")),
            )

    def _fetch_problem_details(self, problem_code: str) -> ScrapedProblem:
        url = _DETAIL_URL_TEMPLATE.format(code=problem_code)
        response = self._client.get(url)
        if response.status_code != 200:
            raise ScraperError(f"CodeChef problem API error: {response.status_code}")

        payload = response.json()
        if payload.get("status") != "success":
            raise ScraperError("CodeChef problem API returned failure status")

        components = payload.get("problemComponents") or {}
        sample_cases = components.get("sampleTestCases") or []
        testcases = self._convert_samples(sample_cases)
        if not testcases:
            raise ScraperError("CodeChef problem missing sample test cases")

        markdown = self._build_markdown(payload, components)

        return ScrapedProblem(
            site=self.site_name,
            code=payload.get("problem_code", problem_code),
            title=payload.get("problem_name", problem_code),
            statement_markdown=markdown,
            source_url=f"https://www.codechef.com/practice/course/all?problemCode={problem_code}",
            testcases=testcases,
        )

    def _build_markdown(self, payload: Dict[str, object], components: Dict[str, Optional[str]]) -> str:
        lines: List[str] = [f"# {payload.get('problem_name', 'CodeChef Problem')}", ""]

        difficulty = payload.get("difficulty_rating")
        if difficulty not in (None, "-1"):
            lines.append(f"**Difficulty Rating:** {difficulty}")
        time_limit = payload.get("max_timelimit")
        if time_limit:
            lines.append(f"**Time Limit:** {time_limit} sec")
        if len(lines) > 2:
            lines.append("")

        mappings = [
            ("statement", "Statement"),
            ("inputFormat", "Input"),
            ("outputFormat", "Output"),
            ("constraints", "Constraints"),
            ("subtasks", "Subtasks"),
        ]

        for key, heading in mappings:
            html = components.get(key)
            if not html:
                continue
            text = self._html_to_markdown(html)
            if not text:
                continue
            lines.append(f"## {heading}")
            lines.append("")
            lines.append(text)
            lines.append("")

        return "\n".join(line.rstrip() for line in lines if line is not None).strip() + "\n"

    def _convert_samples(self, sample_cases: Iterable[Dict[str, str]]) -> List[Testcase]:
        cases: List[Testcase] = []
        for index, case in enumerate(sample_cases, start=1):
            raw_input = (case.get("input") or "").strip("\r")
            raw_output = (case.get("output") or "").strip("\r")
            if not raw_input or not raw_output:
                continue
            cases.append(
                Testcase(
                    index=index,
                    input_data=self._ensure_trailing_newline(raw_input),
                    output_data=self._ensure_trailing_newline(raw_output),
                )
            )
        return cases

    def _html_to_markdown(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        for br in soup.find_all("br"):
            br.replace_with("\n")
        for li in soup.find_all("li"):
            li.insert_before("\n- ")
        text = soup.get_text("\n", strip=True)
        lines = [line.rstrip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)

    def _build_search(self, topics: List[str]) -> Optional[str]:
        if not topics:
            return None
        return " ".join(topics[:2])

    def _parse_int(self, value: object) -> Optional[int]:
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def _ensure_trailing_newline(self, text: str) -> str:
        clean = text.replace("\r", "")
        if not clean.endswith("\n"):
            clean += "\n"
        return clean
