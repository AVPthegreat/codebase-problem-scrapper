"""Baseline problem generation orchestrator (stub for Sprint 1)."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Sequence

from tcg.models.problem import (
    Difficulty,
    ProblemBundle,
    ProblemMetadata,
    ProblemStatement,
    TestcaseSpec,
)
from tcg.services.output_writer import OutputWriter


class ProblemGenerator:
    """Coordinates generation and persistence of problem bundles."""

    def __init__(self, output_writer: OutputWriter | None = None) -> None:
        self._output_writer = output_writer or OutputWriter()

    def generate_placeholder(
        self,
        *,
        title: str,
        problem_code: str,
        difficulty: Difficulty,
        topic: str,
        tags: Sequence[str] | None = None,
        seed: int | None = None,
        num_examples: int = 1,
    ) -> Path:
        """Create a placeholder bundle and write it to disk.

        This method will be replaced by the real deterministic pipeline in later sprints.
        """

        bundle = self._build_placeholder_bundle(
            title=title,
            problem_code=problem_code,
            difficulty=difficulty,
            topic=topic,
            tags=list(tags or []),
            seed=seed,
            num_examples=num_examples,
        )
        return self._output_writer.write_bundle(bundle)

    def _build_placeholder_bundle(
        self,
        *,
        title: str,
        problem_code: str,
        difficulty: Difficulty,
        topic: str,
        tags: List[str],
        seed: int | None,
        num_examples: int,
    ) -> ProblemBundle:
        metadata = ProblemMetadata(
            title=title,
            problem_code=problem_code,
            difficulty=difficulty,
            topic=topic,
            tags=tags,
            seed=seed,
        )

        statement = ProblemStatement(
            markdown=(
                f"# {title}\n\n"
                "This is a placeholder problem statement. Replace it with the AI-enhanced version.\n"
                "\n"
                "## Input\n"
                "- TBD\n"
                "\n"
                "## Output\n"
                "- TBD\n"
            )
        )

        testcases = self._build_placeholder_testcases(num_examples)

        return ProblemBundle(metadata=metadata, statement=statement, testcases=testcases)

    def _build_placeholder_testcases(self, count: int) -> List[TestcaseSpec]:
        """Create simple sequential testcases as stand-ins for real data."""

        examples: List[TestcaseSpec] = []
        for index in range(1, count + 1):
            examples.append(
                TestcaseSpec(
                    index=index,
                    input_data=f"{index}\n",
                    output_data=f"{index}\n",
                )
            )
        return examples
