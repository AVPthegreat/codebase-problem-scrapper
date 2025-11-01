"""Tests for the local OutputWriter implementation."""

from __future__ import annotations

import json

from tcg.models.problem import Difficulty, ProblemBundle, ProblemMetadata, ProblemStatement, TestcaseSpec
from tcg.services.output_writer import OutputWriter


def test_write_bundle_creates_expected_files(tmp_path) -> None:
    metadata = ProblemMetadata(
        title="Sample",
        problem_code="ABC123",
        difficulty=Difficulty.EASY,
        topic="math",
        tags=["number theory"],
        seed=99,
    )
    bundle = ProblemBundle(
        metadata=metadata,
        statement=ProblemStatement(markdown="# Sample\n\nPlaceholder."),
        testcases=[
            TestcaseSpec(index=1, input_data="1\n", output_data="1\n"),
        ],
    )

    writer = OutputWriter(base_dir=tmp_path)
    problem_dir = writer.write_bundle(bundle)

    metadata_path = problem_dir / "metadata.json"
    statement_path = problem_dir / "problem.md"
    input_path = problem_dir / "1.in"
    output_path = problem_dir / "1.out"

    assert metadata_path.exists()
    assert statement_path.exists()
    assert input_path.exists()
    assert output_path.exists()

    metadata_payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert metadata_payload["problem_code"] == "ABC123"
    assert metadata_payload["seed"] == 99
    assert statement_path.read_text(encoding="utf-8").startswith("# Sample")
    assert input_path.read_text(encoding="utf-8").strip() == "1"
    assert output_path.read_text(encoding="utf-8").strip() == "1"
