"""Smoke tests for ScrapeOrchestrator using a fake scraper."""

from __future__ import annotations

from dataclasses import dataclass
from zipfile import ZipFile

from app.services.models import ScrapeQuery, ScrapedProblem, Testcase
from app.services.orchestrator import ScrapeOrchestrator
from app.services.scrapers.base import Scraper, ScraperResult


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
