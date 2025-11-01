"""Data models representing problem metadata and generation specs."""

from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class Difficulty(str, Enum):
    """Enumerates supported difficulty tiers."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class ProblemMetadata(BaseModel):
    """Schema for Codebase Online Judge metadata.json."""

    title: str = Field(..., min_length=1)
    problem_code: str = Field(..., pattern=r"^[A-Z0-9_-]{3,32}$")
    difficulty: Difficulty
    topic: str = Field(..., min_length=1)
    tags: List[str] = Field(default_factory=list)
    source: Optional[str] = Field(default=None, description="Original source URL or identifier")
    seed: Optional[int] = Field(default=None, description="Deterministic seed used during generation")

    @field_validator("tags")
    @classmethod
    def _normalise_tags(cls, value: List[str]) -> List[str]:
        """Normalize tags to lowercase snake-case."""

        return [tag.strip().lower().replace(" ", "_") for tag in value if tag.strip()]


class ProblemStatement(BaseModel):
    """Represents the Markdown problem statement content."""

    markdown: str = Field(..., min_length=1, description="Markdown-formatted statement")


class TestcaseSpec(BaseModel):
    """Represents a single generated testcase."""

    index: int = Field(..., ge=1)
    input_data: str = Field(..., description="Raw stdin contents")
    output_data: Optional[str] = Field(default=None, description="Expected stdout contents if known")


class ProblemBundle(BaseModel):
    """Aggregates all artefacts for a single problem export."""

    metadata: ProblemMetadata
    statement: ProblemStatement
    testcases: List[TestcaseSpec] = Field(default_factory=list)
