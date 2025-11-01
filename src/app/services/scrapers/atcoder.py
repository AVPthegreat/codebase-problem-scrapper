"""AtCoder scraper stub pending full implementation."""

from __future__ import annotations

from typing import Optional

import httpx

from app.services.models import ScrapeQuery
from app.services.scrapers.base import Scraper, ScraperError, ScraperResult

_BASE_URL = "https://atcoder.jp"
_HEADERS = {
    "User-Agent": "ProblemScraper/0.1",
}


class AtCoderScraper(Scraper):
    site_name = "AtCoder"

    def __init__(self, client: Optional[httpx.Client] = None) -> None:
        self._client = client or httpx.Client(headers=_HEADERS, timeout=20.0)

    def fetch(self, query: ScrapeQuery, limit: int) -> ScraperResult:
        # TODO: Implement contest problem scraping respecting robots.txt and login rules.
        raise ScraperError("AtCoder scraper not yet implemented")
