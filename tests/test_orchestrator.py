"""Smoke tests for ScrapeOrchestrator using a fake scraper."""

from __future__ import annotations

from dataclasses import dataclass
from zipfile import ZipFile

import httpx
import pytest

from app.services.models import ScrapeQuery, ScrapedProblem, Testcase
from app.services.orchestrator import ScrapeOrchestrator
from app.services.scrapers.base import Scraper, ScraperError, ScraperResult
from app.services.scrapers.codeforces import CodeforcesScraper
from app.services.scrapers.leetcode import LeetCodeScraper
from app.services.scrapers.codechef import CodeChefScraper
from app.services.scrapers.geeksforgeeks import GeeksforGeeksScraper
from app.services.scrapers.atcoder import AtCoderScraper


@dataclass
class _FakeScraper(Scraper):
    site_name: str = "FakeSite"

    def fetch(self, query: ScrapeQuery, limit: int) -> ScraperResult:
        problems = []
        for idx in range(1, limit + 1):
            problems.append(
                ScrapedProblem(
                    site=self.site_name,
                    code=f"FAKE{idx}",
                    title=f"Fake Problem {idx}",
                    statement_markdown=f"# Fake Problem {idx}\n",
                    source_url="https://example.com",
                    testcases=[
                        Testcase(index=1, input_data="1\n", output_data="2\n"),
                    ],
                )
            )
        return ScraperResult(site=self.site_name, problems=problems)


def test_generate_bundle_creates_zip(tmp_path) -> None:
    orchestrator = ScrapeOrchestrator(base_output=tmp_path, scrapers=[_FakeScraper()])
    zip_path = orchestrator.generate_bundle("give me 2 medium sorting questions")

    assert zip_path.exists()
    with ZipFile(zip_path, "r") as archive:
        names = archive.namelist()

    assert any(name.endswith("1.in") for name in names)
    assert any(name.endswith("1.out") for name in names)
    assert any(name.endswith("problem.md") for name in names)


@dataclass
class _EmptyScraper(Scraper):
    site_name: str = "EmptySite"

    def fetch(self, query: ScrapeQuery, limit: int) -> ScraperResult:
        return ScraperResult(site=self.site_name, problems=[])


def test_generate_bundle_logs_when_falling_back(tmp_path) -> None:
    logs: list[str] = []
    orchestrator = ScrapeOrchestrator(
        base_output=tmp_path,
        scrapers=[_EmptyScraper()],
    )

    orchestrator.generate_bundle(
        "give me 1 medium sorting question",
        log_callback=logs.append,
    )

    assert any("falling back" in message.lower() for message in logs)


def test_codeforces_watermelon_live() -> None:
    scraper = CodeforcesScraper()
    try:
        problem = scraper.fetch_problem(4, "A")
    except (ScraperError, httpx.HTTPError) as exc:
        pytest.skip(f"Codeforces unavailable: {exc}")

    assert "watermelon" in problem.title.lower()
    assert problem.statement_markdown.startswith("# ")
    assert "## Statement" in problem.statement_markdown

    assert problem.testcases, "Expected at least one sample testcase"
    first_case = problem.testcases[0]
    assert first_case.input_data.strip() == "8"
    assert first_case.output_data.strip().upper() == "YES"


def test_leetcode_two_sum_live() -> None:
    scraper = LeetCodeScraper()
    try:
        problem = scraper.fetch_problem_by_slug("two-sum")
    except (ScraperError, httpx.HTTPError) as exc:
        pytest.skip(f"LeetCode unavailable: {exc}")

    assert "two sum" in problem.title.lower()
    assert problem.statement_markdown.startswith("# ")

    assert problem.testcases, "Expected at least one LeetCode example"
    first_case = problem.testcases[0]
    assert "nums" in first_case.input_data.lower()
    assert first_case.output_data.strip() != ""


def test_codechef_flow001_live() -> None:
    scraper = CodeChefScraper()
    try:
        problem = scraper.fetch_problem_by_code("FLOW001")
    except (ScraperError, httpx.HTTPError) as exc:
        pytest.skip(f"CodeChef unavailable: {exc}")

    assert "add two numbers" in problem.title.lower()
    assert problem.statement_markdown.startswith("# ")

    assert problem.testcases, "Expected CodeChef samples"
    first_case = problem.testcases[0]
    assert first_case.input_data.splitlines()[0] == "3"
    assert first_case.output_data.splitlines()[0] == "3"


def test_geeksforgeeks_value_equals_index_live() -> None:
    scraper = GeeksforGeeksScraper()
    try:
        problem = scraper.fetch_problem_by_slug("value-equal-to-index-value1330")
    except (ScraperError, httpx.HTTPError) as exc:
        pytest.skip(f"GeeksforGeeks unavailable: {exc}")

    assert "value equal" in problem.title.lower()
    assert "difficulty" in problem.statement_markdown.lower()

    assert problem.testcases, "Expected GeeksforGeeks examples"
    first_case = problem.testcases[0]
    assert "[2, 4]" in first_case.output_data.replace("\n", " ")


def test_atcoder_product_live() -> None:
    scraper = AtCoderScraper()
    try:
        problem = scraper.fetch_problem("abc086", "a")
    except (ScraperError, httpx.HTTPError) as exc:
        pytest.skip(f"AtCoder unavailable: {exc}")

    assert problem.title.startswith("A -") or "product" in problem.title.lower()
    assert problem.statement_markdown.startswith("# ")

    assert problem.testcases, "Expected AtCoder sample"
    first_case = problem.testcases[0]
    assert first_case.input_data.strip() == "3 4"
    assert first_case.output_data.strip().lower() == "even"
