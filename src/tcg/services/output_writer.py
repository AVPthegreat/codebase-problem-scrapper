"""Utilities for emitting problem artefacts to the local filesystem."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from tcg.models.problem import ProblemBundle, TestcaseSpec


class OutputWriter:
    """Writes problem bundles to the Codebase-compliant folder layout."""

    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = base_dir or Path("output")
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def write_bundle(self, bundle: ProblemBundle) -> Path:
        """Persist the bundle to disk and return the problem directory path."""

        problem_dir = self.base_dir / bundle.metadata.problem_code
        problem_dir.mkdir(parents=True, exist_ok=True)

        self._write_metadata(problem_dir, bundle)
        self._write_statement(problem_dir, bundle)
        self._write_testcases(problem_dir, bundle.testcases)

        return problem_dir

    def _write_metadata(self, problem_dir: Path, bundle: ProblemBundle) -> None:
        metadata_path = problem_dir / "metadata.json"
        metadata_path.write_text(
            json.dumps(bundle.metadata.model_dump(mode="json"), indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )

    def _write_statement(self, problem_dir: Path, bundle: ProblemBundle) -> None:
        statement_path = problem_dir / "problem.md"
        statement_path.write_text(bundle.statement.markdown.rstrip() + "\n", encoding="utf-8")

    def _write_testcases(self, problem_dir: Path, testcases: Iterable[TestcaseSpec]) -> None:
        for testcase in testcases:
            input_path = problem_dir / f"{testcase.index}.in"
            output_path = problem_dir / f"{testcase.index}.out"

            input_path.write_text(testcase.input_data.rstrip() + "\n", encoding="utf-8")
            output_payload = (testcase.output_data or "").rstrip() + "\n"
            output_path.write_text(output_payload, encoding="utf-8")
