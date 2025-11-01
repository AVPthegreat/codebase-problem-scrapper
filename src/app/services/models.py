"""Shared service-layer data structures."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class Testcase:
    index: int
    input_data: str
    output_data: str
    __test__ = False


@dataclass
class ScrapedProblem:
    site: str
    code: str
    title: str
    statement_markdown: str
    source_url: str
    testcases: List[Testcase]


@dataclass
class ScrapeQuery:
    prompt: str
    count: int
    difficulty: Optional[str]
    topics: List[str]


@dataclass
class BundleResult:
    zip_path: Path
    problems: List[ScrapedProblem]
