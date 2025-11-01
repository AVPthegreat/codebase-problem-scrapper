"""Live scraper implementation for LeetCode problems."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

import httpx
from bs4 import BeautifulSoup

from app.services.models import ScrapeQuery, ScrapedProblem, Testcase
from app.services.scrapers.base import Scraper, ScraperError, ScraperResult

_GRAPHQL_ENDPOINT = "https://leetcode.com/graphql"
_LEETCODE_ROOT = "https://leetcode.com"
_HEADERS = {
    "Content-Type": "application/json",
    "Referer": "https://leetcode.com/problemset/",
    "User-Agent": "ProblemScraper/0.1",
    "X-Requested-With": "XMLHttpRequest",
}

_DIFFICULTY_MAP: Dict[str, str] = {
    "easy": "EASY",
    "medium": "MEDIUM",
    "hard": "HARD",
    "expert": "HARD",
}

_TOPIC_MAP: Dict[str, str] = {
    "arrays": "array",
    "sorting": "sorting",
    "graphs": "graph",
    "dp": "dynamic-programming",
    "math": "math",
    "strings": "string",
}

_PROBLEM_LIST_QUERY = """
query problemsetQuestionList($categorySlug: String, $skip: Int, $limit: Int, $filters: QuestionListFilterInput) {
  problemsetQuestionList: questionList(
    categorySlug: $categorySlug,
    skip: $skip,
    limit: $limit,
    filters: $filters
  ) {
    questions: data {
      title
      titleSlug
      difficulty
      isPaidOnly
      frontendQuestionId
    }
  }
}
"""

_QUESTION_DATA_QUERY = """
query questionData($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    questionId
    questionFrontendId
    title
    titleSlug
    difficulty
    content
    exampleTestcases
    metaData
  }
}
"""


@dataclass
class _LeetCodeProblem:
    slug: str
    frontend_id: Optional[str]
    title: str
    difficulty: str
    paid_only: bool

    @property
    def url(self) -> str:
        return f"https://leetcode.com/problems/{self.slug}/"


class LeetCodeScraper(Scraper):
    site_name = "LeetCode"

    def __init__(self, client: Optional[httpx.Client] = None) -> None:
        self._client = client or httpx.Client(headers=_HEADERS, timeout=20.0)

    def fetch(self, query: ScrapeQuery, limit: int) -> ScraperResult:
        if limit <= 0:
            return ScraperResult(site=self.site_name, problems=[])

        topics = [_TOPIC_MAP.get(topic, topic) for topic in query.topics]
        candidates = self._load_candidates(topics, query.difficulty, limit)

        collected: List[ScrapedProblem] = []
        for info in candidates:
            if len(collected) >= limit:
                break
            try:
                collected.append(self._build_problem(info))
            except ScraperError:
                continue
        return ScraperResult(site=self.site_name, problems=collected)

    def fetch_problem_by_slug(self, slug: str) -> ScrapedProblem:
        question = self._fetch_question_data(slug)
        if not question:
            raise ScraperError("Problem not found on LeetCode")
        info = _LeetCodeProblem(
            slug=question.get("titleSlug", slug),
            frontend_id=question.get("questionFrontendId") or question.get("questionId"),
            title=question.get("title", slug.replace("-", " ").title()),
            difficulty=question.get("difficulty", "Unknown"),
            paid_only=False,
        )
        return self._build_problem(info, question)

    def _load_candidates(self, topics: List[str], difficulty: Optional[str], limit: int) -> Iterable[_LeetCodeProblem]:
        variables: Dict[str, Any] = {
            "categorySlug": "algorithms",
            "skip": 0,
            "limit": max(20, limit * 3),
            "filters": {},
        }
        if topics:
            variables["filters"]["tags"] = topics
        mapped_difficulty = _DIFFICULTY_MAP.get(difficulty) if difficulty else None
        if mapped_difficulty:
            variables["filters"]["difficulty"] = mapped_difficulty

        payload = {"query": _PROBLEM_LIST_QUERY, "variables": variables}
        data = self._post_graphql(payload)
        questions = data.get("problemsetQuestionList", {}).get("questions", [])
        for entry in questions:
            candidate = _LeetCodeProblem(
                slug=entry.get("titleSlug"),
                frontend_id=entry.get("frontendQuestionId"),
                title=entry.get("title", ""),
                difficulty=entry.get("difficulty", "Unknown"),
                paid_only=entry.get("isPaidOnly", False),
            )
            if not candidate.slug or candidate.paid_only:
                continue
            yield candidate

    def _build_problem(self, info: _LeetCodeProblem, preloaded: Optional[Dict[str, Any]] = None) -> ScrapedProblem:
        question = preloaded or self._fetch_question_data(info.slug)
        if not question:
            raise ScraperError("Unable to fetch LeetCode problem details")

        statement = self._render_statement(question)
        testcases = self._extract_testcases(question)
        if not testcases:
            raise ScraperError("LeetCode problem is missing sample test cases")

        frontend_id = info.frontend_id or question.get("questionFrontendId") or question.get("questionId")
        code = f"LC{frontend_id}" if frontend_id else f"LC-{info.slug.replace('-', '').upper()}"
        title = question.get("title") or info.title
        difficulty = question.get("difficulty") or info.difficulty

        header_lines = [f"# {title}", "", f"**Difficulty:** {difficulty}"]
        body = statement.strip()
        if body:
            header_lines.extend(["", body])
        markdown = "\n".join(header_lines).rstrip() + "\n"

        return ScrapedProblem(
            site=self.site_name,
            code=code,
            title=title,
            statement_markdown=markdown,
            source_url=info.url,
            testcases=testcases,
        )

    def _fetch_question_data(self, slug: str) -> Dict[str, Any]:
        payload = {"query": _QUESTION_DATA_QUERY, "variables": {"titleSlug": slug}}
        data = self._post_graphql(payload)
        question = data.get("question")
        if not question:
            raise ScraperError("LeetCode returned empty question payload")
        return question

    def _post_graphql(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        self._ensure_csrf_token()
        headers = {}
        token = self._client.cookies.get("csrftoken")
        if token:
            headers["x-csrftoken"] = token

        response = self._client.post(_GRAPHQL_ENDPOINT, json=payload, headers=headers)
        if response.status_code != 200:
            raise ScraperError(f"LeetCode GraphQL error: {response.status_code}")

        payload_json = response.json()
        if payload_json.get("errors"):
            raise ScraperError("LeetCode GraphQL returned errors")
        return payload_json.get("data", {})

    def _ensure_csrf_token(self) -> None:
        if "csrftoken" in self._client.cookies:
            return
        response = self._client.get(_LEETCODE_ROOT)
        if response.status_code != 200:
            raise ScraperError("Failed to negotiate CSRF token with LeetCode")

    def _render_statement(self, question: Dict[str, Any]) -> str:
        content_html = question.get("content") or ""
        if not content_html:
            return "Statement unavailable."
        soup = BeautifulSoup(content_html, "html.parser")
        for br in soup.find_all("br"):
            br.replace_with("\n")

        blocks: List[str] = []
        for element in soup.find_all(["h2", "h3", "p", "pre", "li", "blockquote"], recursive=True):
            if element.name == "li":
                text = element.get_text(" ", strip=True)
                if text:
                    blocks.append(f"- {text}")
                continue
            if element.name == "pre":
                text = element.get_text("\n", strip=False).replace("\r", "")
                if not text.endswith("\n"):
                    text += "\n"
                blocks.append(f"```\n{text}```")
                continue
            text = element.get_text("\n", strip=True)
            if text:
                blocks.append(text)

        if not blocks:
            return soup.get_text("\n", strip=True)
        return "\n\n".join(blocks)

    def _extract_testcases(self, question: Dict[str, Any]) -> List[Testcase]:
        cases = self._extract_from_metadata(question.get("metaData"))
        if cases:
            return cases

        content_cases = self._extract_from_content(question.get("content", ""))
        if content_cases:
            return content_cases

        return []

    def _extract_from_metadata(self, metadata_raw: Optional[str]) -> List[Testcase]:
        if not metadata_raw:
            return []
        try:
            metadata = json.loads(metadata_raw)
        except json.JSONDecodeError:
            return []

        examples = metadata.get("examples") or []
        cases: List[Testcase] = []
        for index, example in enumerate(examples, start=1):
            input_text = self._extract_example_field(example, [
                "input",
                "inputText",
                "inputString",
                "inputValues",
                "inputFormatted",
            ])
            output_text = self._extract_example_field(example, [
                "output",
                "outputText",
                "outputString",
                "outputValues",
                "outputFormatted",
            ])
            if not input_text or not output_text:
                continue
            cases.append(
                Testcase(
                    index=index,
                    input_data=self._ensure_trailing_newline(input_text),
                    output_data=self._ensure_trailing_newline(output_text),
                )
            )
        return cases

    def _extract_from_content(self, content_html: str) -> List[Testcase]:
        if not content_html:
            return []
        soup = BeautifulSoup(content_html, "html.parser")
        cases: List[Testcase] = []
        for index, pre in enumerate(soup.find_all("pre"), start=1):
            text = pre.get_text("\n", strip=False)
            input_lines: List[str] = []
            output_lines: List[str] = []
            current_label: Optional[str] = None
            for raw_line in text.splitlines():
                stripped = raw_line.strip()
                lower = stripped.lower()
                if lower.startswith("input:"):
                    current_label = "input"
                    remainder = stripped.split(":", 1)[1].strip()
                    if remainder:
                        input_lines.append(remainder)
                    continue
                if lower.startswith("output:"):
                    current_label = "output"
                    remainder = stripped.split(":", 1)[1].strip()
                    if remainder:
                        output_lines.append(remainder)
                    continue
                if lower.startswith("explanation:"):
                    current_label = None
                    continue
                if current_label == "input" and stripped:
                    input_lines.append(stripped)
                    continue
                if current_label == "output" and stripped:
                    output_lines.append(stripped)
                    continue
                if not stripped:
                    current_label = None
            if not input_lines or not output_lines:
                continue
            cases.append(
                Testcase(
                    index=index,
                    input_data=self._ensure_trailing_newline("\n".join(input_lines)),
                    output_data=self._ensure_trailing_newline("\n".join(output_lines)),
                )
            )
        return cases

    def _extract_example_field(self, example: Dict[str, Any], keys: List[str]) -> Optional[str]:
        for key in keys:
            value = example.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return None

    def _ensure_trailing_newline(self, text: str) -> str:
        cleaned = text.replace("\r", "")
        if not cleaned.endswith("\n"):
            cleaned += "\n"
        return cleaned
