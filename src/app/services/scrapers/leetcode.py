"""LeetCode scraper stub (pending full implementation)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import httpx

from app.services.models import ScrapeQuery, ScrapedProblem, Testcase
from app.services.scrapers.base import Scraper, ScraperError, ScraperResult

_GRAPHQL_ENDPOINT = "https://leetcode.com/graphql"
_HEADERS = {
    "Content-Type": "application/json",
    "Referer": "https://leetcode.com/problemset/",
    "User-Agent": "ProblemScraper/0.1",
}


@dataclass
class _LeetCodeProblem:
    slug: str
    title: str
    difficulty: str
    url: str


class LeetCodeScraper(Scraper):
    site_name = "LeetCode"

    def __init__(self, client: Optional[httpx.Client] = None) -> None:
        self._client = client or httpx.Client(headers=_HEADERS, timeout=20.0)

    def fetch(self, query: ScrapeQuery, limit: int) -> ScraperResult:
        # TODO: Implement GraphQL requests with pagination and sample parsing when authenticated access is available.
        raise ScraperError("LeetCode scraper not yet implemented for unauthenticated usage")
