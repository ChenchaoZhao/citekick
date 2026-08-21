"""Unit tests for the search orchestrator: dedupe, rank, filtering, and failure isolation.

The strategy interface (strategy.search) is mocked; no HTTP or network is involved.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

from citekick.paper import Paper
from citekick.search import SearchResult, dedupe, rank, search_papers
from citekick.search import year_range as build_year_range
from citekick.sources import _STRATEGIES, Source
from citekick.sources.base import SearchStrategy

if TYPE_CHECKING:
    from collections.abc import Awaitable


def _run(awaitable: Awaitable[Any]) -> Any:
    return asyncio.run(awaitable)


def _paper(title: str, *, doi: str | None = None, year: int | None = None, citations: int | None = None) -> Paper:
    return Paper(title=title, doi=doi, year=year, citation_count=citations, source="Test")


def _stub_strategy(papers: list[Paper], error: Exception | None = None) -> type[SearchStrategy]:
    """Build a strategy class whose search returns fixed papers or raises."""

    class Stub(SearchStrategy):
        async def search(self, query: str, *, max_results: int = 10) -> list[Paper]:  # noqa: ARG002 - names must match the strategy interface; behavior comes from the closure
            if error is not None:
                raise error
            return papers

    return Stub


def test_dedupe_by_doi_keeps_first_occurrence() -> None:
    first = _paper("A", doi="10.1/same")
    duplicate = _paper("A duplicate", doi="10.1/SAME")

    assert dedupe([first, duplicate]) == [first]


def test_dedupe_by_normalized_title_when_no_doi() -> None:
    first = _paper("Hamiltonian Monte Carlo")
    duplicate = _paper("hamiltonian monte-carlo!")

    assert dedupe([first, duplicate]) == [first]


def test_dedupe_keeps_richer_duplicate_metadata() -> None:
    sparse = _paper("Shared", doi="10.1/shared")
    rich = _paper("Shared", doi="10.1/shared", citations=42, year=2024)

    assert dedupe([sparse, rich]) == [rich]


def test_dedupe_keeps_distinct_papers() -> None:
    papers = [_paper("A", doi="10.1/a"), _paper("B", doi="10.1/b")]

    assert dedupe(papers) == papers


def test_rank_orders_by_citation_count_descending() -> None:
    low = _paper("low", citations=2)
    high = _paper("high", citations=50)
    unknown = _paper("unknown", citations=None)

    assert rank([low, high, unknown]) == [high, low, unknown]


def test_rank_is_stable_for_equal_citations() -> None:
    first = _paper("first", citations=3)
    second = _paper("second", citations=3)

    assert rank([first, second]) == [first, second]


def test_search_papers_merges_dedupes_and_ranks_across_sources(monkeypatch: Any) -> None:
    shared = _paper("Shared", doi="10.1/shared", citations=100)
    monkeypatch.setitem(_STRATEGIES, Source.ARXIV, _stub_strategy([shared]))
    monkeypatch.setitem(
        _STRATEGIES,
        Source.SEMANTIC_SCHOLAR,
        _stub_strategy([_paper("Shared", doi="10.1/SHARED", citations=50), _paper("Other", citations=5)]),
    )

    result = _run(search_papers("q", sources=(Source.ARXIV, Source.SEMANTIC_SCHOLAR)))

    assert result.total_fetched == 3
    assert [paper.title for paper in result.papers] == ["Shared", "Other"]
    assert len(result.per_source) == 2


def test_search_papers_records_error_but_keeps_other_sources(monkeypatch: Any) -> None:
    monkeypatch.setitem(_STRATEGIES, Source.ARXIV, _stub_strategy([], error=RuntimeError("boom")))
    monkeypatch.setitem(_STRATEGIES, Source.SEMANTIC_SCHOLAR, _stub_strategy([_paper("OK")]))

    result = _run(search_papers("q", sources=(Source.ARXIV, Source.SEMANTIC_SCHOLAR)))

    assert [paper.title for paper in result.papers] == ["OK"]
    arxiv_result = next(source_result for source_result in result.per_source if source_result.source is Source.ARXIV)
    assert arxiv_result.error == "boom"
    assert len(result.per_source) == 2


def test_search_papers_filters_by_year_range(monkeypatch: Any) -> None:
    monkeypatch.setitem(_STRATEGIES, Source.ARXIV, _stub_strategy([_paper("Old", year=2019), _paper("New", year=2022)]))

    result = _run(search_papers("q", sources=(Source.ARXIV,), year_range=(2020, 2023)))

    assert [paper.title for paper in result.papers] == ["New"]
    assert result.total_fetched == 2


def test_search_papers_passes_query_and_max_results_to_strategy(monkeypatch: Any) -> None:
    seen: dict[str, Any] = {}

    class Capturing(SearchStrategy):
        async def search(self, query: str, *, max_results: int = 10) -> list[Paper]:
            seen["query"] = query
            seen["max_results"] = max_results
            return []

    monkeypatch.setitem(_STRATEGIES, Source.ARXIV, Capturing)

    _run(search_papers("q", sources=(Source.ARXIV,), max_results_per_source=3))

    assert seen == {"query": "q", "max_results": 3}


def test_year_range_none_when_no_bounds() -> None:
    assert build_year_range() is None
    assert build_year_range(from_year=2020) == (2020, 2100)
    assert build_year_range(to_year=2021) == (1900, 2021)


def test_search_result_to_dict_includes_summary() -> None:
    paper = _paper("A", citations=3)
    result = SearchResult(query="q", papers=[paper], total_fetched=1)

    payload = result.to_dict()

    assert payload["query"] == "q"
    assert payload["result_count"] == 1
    assert payload["total_fetched"] == 1
    assert payload["per_source"] == []
    assert payload["papers"][0]["title"] == "A"
