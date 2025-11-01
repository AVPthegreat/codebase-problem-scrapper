"""Base interfaces and data structures for scrapers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from app.services.models import ScrapedProblem, ScrapeQuery


class ScraperError(Exception):
    """Raised when a scraper fails to retrieve data."""


@dataclass
class ScraperResult:
    site: str
    problems: List[ScrapedProblem]


class Scraper:
    """Abstract scraper contract."""

    site_name: str

    def fetch(self, query: ScrapeQuery, limit: int) -> ScraperResult:
        raise NotImplementedError
