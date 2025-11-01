"""CodeChef scraper stub pending full implementation."""

from __future__ import annotations

from typing import Optional

import httpx

from app.services.models import ScrapeQuery
from app.services.scrapers.base import Scraper, ScraperError, ScraperResult

_BASE_URL = "https://www.codechef.com"
_HEADERS = {
    "User-Agent": "ProblemScraper/0.1",
}


class CodeChefScraper(Scraper):
    site_name = "CodeChef"

    def __init__(self, client: Optional[httpx.Client] = None) -> None:
        self._client = client or httpx.Client(headers=_HEADERS, timeout=20.0)

    def fetch(self, query: ScrapeQuery, limit: int) -> ScraperResult:
        # TODO: Implement HTML scraping with login support and sample extraction once CSRF workflow handled.
        raise ScraperError("CodeChef scraper not yet implemented")
