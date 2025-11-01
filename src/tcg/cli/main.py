"""Command-line interface for the test case generator."""

from __future__ import annotations

from typing import List, Optional

import typer
from rich.console import Console

from tcg.core.generator import ProblemGenerator
from tcg.models.problem import Difficulty

app = typer.Typer(help="Generate Codebase-ready problem bundles")
console = Console()

def _parse_difficulty(value: str) -> Difficulty:
    try:
        return Difficulty(value.lower())
    except ValueError as exc:  # pragma: no cover - Typer handles messaging
        raise typer.BadParameter(
            f"Invalid difficulty '{value}'. Choose from {[d.value for d in Difficulty]}"
        ) from exc


@app.command()
def generate(
    problem_code: str = typer.Argument(..., help="Unique problem identifier"),
    title: str = typer.Option(..., "--title", help="Problem title"),
    difficulty: str = typer.Option(
        Difficulty.MEDIUM.value,
        "--difficulty",
        case_sensitive=False,
        help="Difficulty tier",
    ),
    topic: str = typer.Option(..., "--topic", help="Primary topic label"),
    tags: List[str] = typer.Option([], "--tag", help="Repeatable tag option"),
    seed: Optional[int] = typer.Option(None, "--seed", help="Deterministic RNG seed"),
    num_examples: int = typer.Option(1, "--examples", help="Number of placeholder testcases"),
) -> None:
    """Generate a placeholder problem bundle (Sprint 1 stub)."""

    generator = ProblemGenerator()
    bundle_path = generator.generate_placeholder(
        title=title,
        problem_code=problem_code,
        difficulty=_parse_difficulty(difficulty),
        topic=topic,
        tags=tags,
        seed=seed,
        num_examples=num_examples,
    )

    console.print(f"[green]Generated bundle at[/green] {bundle_path}")


def main() -> None:  # pragma: no cover - Typer handles execution
    app()


if __name__ == "__main__":  # pragma: no cover
    main()
