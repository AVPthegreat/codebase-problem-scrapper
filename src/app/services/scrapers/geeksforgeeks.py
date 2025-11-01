"""GeeksforGeeks scraper stub pending full implementation."""

from __future__ import annotations

from typing import Optional

import httpx

from app.services.models import ScrapeQuery
from app.services.scrapers.base import Scraper, ScraperError, ScraperResult

_BASE_URL = "https://www.geeksforgeeks.org"
_HEADERS = {
    "User-Agent": "ProblemScraper/0.1",
}


class GeeksforGeeksScraper(Scraper):
    site_name = "GeeksforGeeks"

    def __init__(self, client: Optional[httpx.Client] = None) -> None:
        self._client = client or httpx.Client(headers=_HEADERS, timeout=20.0)

    def fetch(self, query: ScrapeQuery, limit: int) -> ScraperResult:
        # TODO: Implement article scraping with rate limiting and sample extraction once allowed by TOS.
        raise ScraperError("GeeksforGeeks scraper not yet implemented")
