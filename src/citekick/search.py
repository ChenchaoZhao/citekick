"""Orchestrates multi-source paper searches: fetch, filter, dedupe, rank."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import httpx

from citekick.sources import DEFAULT_SOURCES, SearchStrategy, Source

if TYPE_CHECKING:
    from citekick.http import ResponseCache
    from citekick.paper import Paper

LOGGER = logging.getLogger(__name__)

DEFAULT_MAX_RESULTS_PER_SOURCE: int = 10
MIN_YEAR: int = 1900
MAX_YEAR: int = 2100
_TIMEOUT_SECONDS: float = 30.0


def year_range(from_year: int | None = None, to_year: int | None = None) -> tuple[int, int] | None:
    """Build an inclusive year filter, or None when no bound was given."""
    if from_year is None and to_year is None:
        return None
    return (from_year if from_year is not None else MIN_YEAR, to_year if to_year is not None else MAX_YEAR)


@dataclass
class SourceResult:
    """Per-source outcome: the papers found, or the error that stopped it."""

    source: Source
    papers: list[Paper] = field(default_factory=list)
    error: str | None = None


@dataclass
class SearchResult:
    """Merged, deduplicated, and ranked results for one query."""

    query: str
    papers: list[Paper] = field(default_factory=list)
    per_source: list[SourceResult] = field(default_factory=list)
    total_fetched: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-friendly mapping."""
        return {
            "query": self.query,
            "papers": [paper.to_dict() for paper in self.papers],
            "per_source": [
                {"source": source_result.source.value, "count": len(source_result.papers), "error": source_result.error}
                for source_result in self.per_source
            ],
            "total_fetched": self.total_fetched,
            "result_count": len(self.papers),
        }


async def search_papers(
    query: str,
    *,
    sources: tuple[Source, ...] = DEFAULT_SOURCES,
    max_results_per_source: int = DEFAULT_MAX_RESULTS_PER_SOURCE,
    year_range: tuple[int, int] | None = None,
    client: httpx.AsyncClient | None = None,
    cache: ResponseCache | None = None,
) -> SearchResult:
    """Query each source, then filter, dedupe, and rank the merged papers.

    A failing source is logged and recorded on its SourceResult; the other
    sources still run and the search never raises because of one source.
    """
    owns_client = client is None
    active_client = client or httpx.AsyncClient(timeout=httpx.Timeout(_TIMEOUT_SECONDS))

    per_source: list[SourceResult] = []
    papers: list[Paper] = []
    try:
        for source in sources:
            strategy: SearchStrategy = source.strategy_class(active_client, cache)
            try:
                found = await strategy.search(query, max_results=max_results_per_source)
            except Exception as exc:  # noqa: BLE001 - isolate one bad source
                LOGGER.warning("citekick: source %s failed: %s", source.label, exc)
                per_source.append(SourceResult(source=source, error=str(exc)))
                continue
            per_source.append(SourceResult(source=source, papers=found))
            papers.extend(found)
        filtered = [paper for paper in papers if _in_year_range(paper, year_range)]
        ranked = rank(dedupe(filtered))
    finally:
        if owns_client:
            await active_client.aclose()

    return SearchResult(query=query, papers=ranked, per_source=per_source, total_fetched=len(papers))


def dedupe(papers: list[Paper]) -> list[Paper]:
    """Drop duplicates by DOI (case-insensitive), falling back to normalized title.

    When a duplicate appears, keep the record with the richer metadata (citation
    count first, then abstract/url/doi), so ranking keeps cross-source signals.
    """
    seen: dict[str, int] = {}
    unique: list[Paper] = []
    for paper in papers:
        key = _dedupe_key(paper)
        index = seen.get(key)
        if index is None:
            seen[key] = len(unique)
            unique.append(paper)
        else:
            unique[index] = _better(unique[index], paper)
    return unique


def _better(left: Paper, right: Paper) -> Paper:
    return right if _completeness(right) > _completeness(left) else left


def _completeness(paper: Paper) -> tuple[int, int]:
    fields = (paper.abstract, paper.url, paper.doi)
    return (int(paper.citation_count is not None), sum(field is not None for field in fields))


def rank(papers: list[Paper]) -> list[Paper]:
    """Rank by citation count descending; ties keep source relevance order."""
    return sorted(papers, key=lambda paper: paper.citation_count or 0, reverse=True)


def _dedupe_key(paper: Paper) -> str:
    if paper.doi:
        return f"doi:{paper.doi.casefold()}"
    title = "".join(char for char in paper.title.casefold() if char.isalnum())
    return f"title:{title}"


def _in_year_range(paper: Paper, bounds: tuple[int, int] | None) -> bool:
    if bounds is None or paper.year is None:
        return True
    return bounds[0] <= paper.year <= bounds[1]
