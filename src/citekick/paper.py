"""Normalized paper record shared across all literature sources."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Paper:
    """A single paper with metadata normalized across sources."""

    title: str
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    doi: str | None = None
    abstract: str | None = None
    citation_count: int | None = None
    source: str = ""
    url: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-friendly mapping."""
        return asdict(self)
