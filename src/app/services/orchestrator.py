"""Scraping orchestrator responsible for collecting problems and packaging outputs."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable, List, Optional
from zipfile import ZipFile, ZIP_DEFLATED

from slugify import slugify

from app.services.models import BundleResult, ScrapeQuery, ScrapedProblem, Testcase
from app.services.scrapers.base import Scraper, ScraperError
from app.services.scrapers.codeforces import CodeforcesScraper
from app.services.scrapers.leetcode import LeetCodeScraper
from app.services.scrapers.codechef import CodeChefScraper
from app.services.scrapers.geeksforgeeks import GeeksforGeeksScraper
from app.services.scrapers.atcoder import AtCoderScraper


class ScrapeOrchestrator:
    """Coordinates scraping, formatting, and ZIP packaging."""

    def __init__(
        self,
        *,
        base_output: Path | None = None,
        scrapers: Optional[List[Scraper]] = None,
    ) -> None:
        self.base_output = base_output or Path("output")
        self.base_output.mkdir(parents=True, exist_ok=True)
        self.scrapers = scrapers or self._default_scrapers()

    def generate_bundle(
        self,
        prompt: str,
        *,
        log_callback: Optional[Callable[[str], None]] = None,
        include_sites: Optional[List[str]] = None,
    ) -> Path:
        logger = log_callback or self._noop_logger

        if not prompt.strip():
            raise ValueError("Prompt must not be empty")

        logger("Parsing prompt and building scrape query...")
        query = self._build_query(prompt)
        logger(
            f"Looking for {query.count} problem(s)"
            + (f" at {query.difficulty} difficulty" if query.difficulty else "")
        )
        if query.topics:
            logger(f"Topic hints: {', '.join(query.topics)}")

        # Optionally filter scrapers by site name
        scrapers: List[Scraper] = self.scrapers
        if include_sites:
            wanted = {s.lower() for s in include_sites}
            scrapers = [s for s in self.scrapers if s.site_name.lower() in wanted]
            if not scrapers:
                logger("No matching scrapers for requested platforms; using all available scrapers.")
                scrapers = self.scrapers

        problems = self._collect_problems(scrapers, query, logger)
        if not problems:
            logger("No live sources yielded results; falling back to placeholder generator.")
            problems = self._generate_placeholder(query)

        bundle = self._write_bundle(query, problems)
        logger(f"Bundled {len(bundle.problems)} problem(s).")
        return bundle.zip_path

    def _collect_problems(
        self,
        scrapers: List[Scraper],
        query: ScrapeQuery,
        logger: Callable[[str], None],
    ) -> List[ScrapedProblem]:
        collected: List[ScrapedProblem] = []
        for scraper in scrapers:
            remaining = query.count - len(collected)
            if remaining <= 0:
                break
            logger(f"Querying {scraper.site_name} for up to {remaining} problem(s)...")
            try:
                import signal
                def timeout_handler(signum, frame):
                    raise TimeoutError(f"{scraper.site_name} timed out")
                
                # Set 15-second timeout per scraper
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(15)
                
                try:
                    result = scraper.fetch(query, remaining)
                    collected.extend(result.problems)
                    logger(
                        f"{scraper.site_name} returned {len(result.problems)} problem(s)."
                    )
                finally:
                    signal.alarm(0)
            except TimeoutError as e:
                logger(f"{scraper.site_name} timed out - skipping.")
                continue
            except ScraperError:
                logger(f"{scraper.site_name} failed to provide data.")
                continue
            except Exception as e:
                logger(f"{scraper.site_name} error: {str(e)[:100]}")
                continue
        return collected[: query.count]

    def _write_bundle(self, query: ScrapeQuery, problems: Iterable[ScrapedProblem]) -> BundleResult:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        slug = slugify(query.prompt)[:40] or "problems"
        bundle_dir = self.base_output / f"{slug}-{timestamp}"
        bundle_dir.mkdir(parents=True, exist_ok=True)

        serialized: List[ScrapedProblem] = []
        for problem in problems:
            serialized.append(problem)
            self._write_problem(bundle_dir, problem)

        zip_path = bundle_dir.with_suffix(".zip")
        self._zip_directory(bundle_dir, zip_path)
        return BundleResult(zip_path=zip_path, problems=serialized)

    def _write_problem(self, bundle_dir: Path, problem: ScrapedProblem) -> None:
        problem_dir = bundle_dir / problem.code
        problem_dir.mkdir(parents=True, exist_ok=True)

        (problem_dir / "problem.md").write_text(problem.statement_markdown, encoding="utf-8")
        metadata_path = problem_dir / "metadata.json"
        metadata_payload = {
            "title": problem.title,
            "problem_code": problem.code,
            "source_url": problem.source_url,
            "site": problem.site,
        }
        metadata_path.write_text(json.dumps(metadata_payload, indent=2), encoding="utf-8")

        for testcase in problem.testcases:
            (problem_dir / f"{testcase.index}.in").write_text(testcase.input_data, encoding="utf-8")
            (problem_dir / f"{testcase.index}.out").write_text(testcase.output_data, encoding="utf-8")

    def _zip_directory(self, source_dir: Path, zip_path: Path) -> None:
        with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as bundle:
            for path in source_dir.rglob("*"):
                bundle.write(path, path.relative_to(source_dir.parent))

    def _build_query(self, prompt: str) -> ScrapeQuery:
        return ScrapeQuery(
            prompt=prompt,
            count=self._extract_count(prompt),
            difficulty=self._extract_difficulty(prompt),
            topics=self._extract_topics(prompt),
        )

    def _extract_count(self, prompt: str) -> int:
        match = re.search(r"(\d+)", prompt)
        if match:
            return max(1, min(50, int(match.group(1))))
        return 5

    def _extract_difficulty(self, prompt: str) -> Optional[str]:
        prompt_lower = prompt.lower()
        for word in ("easy", "medium", "hard", "expert"):
            if word in prompt_lower:
                return word
        return None

    def _extract_topics(self, prompt: str) -> List[str]:
        topics: List[str] = []
        keywords = {
            "sorting": ["sort", "sorting"],
            "graphs": ["graph", "graphs"],
            "dp": ["dp", "dynamic programming"],
            "math": ["math", "number"],
            "strings": ["string", "strings"],
        }
        prompt_lower = prompt.lower()
        for topic, words in keywords.items():
            if any(word in prompt_lower for word in words):
                topics.append(topic)
        return topics

    def _generate_placeholder(self, query: ScrapeQuery) -> List[ScrapedProblem]:
        problems: List[ScrapedProblem] = []
        difficulty = query.difficulty or "medium"
        for index in range(1, query.count + 1):
            title = f"{difficulty.title()} Problem {index}"
            code = f"{difficulty[0].upper()}PL{index:03d}"
            statement = (
                f"### {title}\n\n"
                f"Generated placeholder for prompt: {query.prompt}\n\n"
                "**Input:** TBD\n\n"
                "**Output:** TBD\n"
            )
            testcases = self._generate_placeholder_testcases(index)
            problems.append(
                ScrapedProblem(
                    site="placeholder",
                    code=code,
                    title=title,
                    statement_markdown=statement,
                    source_url="",
                    testcases=testcases,
                )
            )
        return problems

    def _generate_placeholder_testcases(self, seed: int) -> List[Testcase]:
        return [
            Testcase(index=index, input_data=f"{seed * index}\n", output_data=f"{seed * index * 2}\n")
            for index in range(1, 4)
        ]

    def _default_scrapers(self) -> List[Scraper]:
        return [
            CodeforcesScraper(),
            LeetCodeScraper(),
            CodeChefScraper(),
            GeeksforGeeksScraper(),
            AtCoderScraper(),
        ]

    @staticmethod
    def _noop_logger(_: str) -> None:
        return None
