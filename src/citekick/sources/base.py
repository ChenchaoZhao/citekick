"""Shared pieces for per-source search strategies."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import httpx

    from citekick.http import ResponseCache
    from citekick.paper import Paper


class SearchError(Exception):
    """Raised when a single source fails; the orchestrator keeps going."""


class SearchStrategy(ABC):
    """Base class for a single literature source's search strategy."""

    label: str = ""

    def __init__(self, client: httpx.AsyncClient, cache: ResponseCache | None = None) -> None:
        self._client = client
        self._cache = cache

    @abstractmethod
    async def search(self, query: str, *, max_results: int = 10) -> list[Paper]:
        """Query the source and return papers ordered by relevance."""


def as_int(value: Any) -> int | None:
    """Best-effort integer cast for source fields that may be str or int."""
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def year_from_iso(iso_date: str) -> int | None:
    """Extract the year from an ISO-8601 date string."""
    return as_int(iso_date[:4])


def year_from_pubdate(pubdate: str) -> int | None:
    """Extract the year from a PubMed-style pubdate like '2024 Jan 01'."""
    match = re.match(r"^(\d{4})", pubdate)
    return int(match.group(1)) if match else None


def year_from_epoch_ms(epoch_ms: Any) -> int | None:
    """Convert an epoch-milliseconds timestamp to a year."""
    try:
        return datetime.fromtimestamp(int(epoch_ms) / 1000, tz=UTC).year
    except (TypeError, ValueError, OSError):
        return None


def year_from_date_parts(issued: dict[str, Any] | None) -> int | None:
    """Extract the year from a Crossref 'issued' date-parts structure."""
    parts = (issued or {}).get("date-parts") or []
    if not parts or not parts[0]:
        return None
    return as_int(parts[0][0])


def strip_jats(abstract: str | None) -> str | None:
    """Strip JATS XML tags from a Crossref abstract, collapsing whitespace."""
    if not abstract:
        return None
    text = re.sub(r"<[^>]+>", " ", abstract)
    text = " ".join(text.split())
    return text or None


def author_name(author: dict[str, Any]) -> str:
    """Format a Crossref author entry (given/family or an organization name)."""
    name = author.get("name")
    if name:
        return name
    given = author.get("given", "")
    family = author.get("family", "")
    return " ".join(part for part in (given, family) if part).strip()


def dblp_authors(author_field: Any) -> list[str]:
    """Normalize a DBLP authors field, which may be str, dict, or a list."""
    author = (author_field or {}).get("author")
    if author is None:
        return []
    if isinstance(author, str):
        return [author]
    if isinstance(author, dict):
        return [author.get("text", "")] if author.get("text") else []
    names: list[str] = []
    for item in author:
        if isinstance(item, str) and item:
            names.append(item)
        elif isinstance(item, dict) and item.get("text"):
            names.append(item["text"])
    return names


def content_value(field: Any) -> Any:
    """Unwrap an OpenReview v2 content field, which stores values under 'value'."""
    if isinstance(field, dict) and "value" in field:
        return field["value"]
    return field
