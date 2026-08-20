"""Integration tests: query the real network API of every literature source.

These tests require live network access and are only run via
`hatch run test-integration`.
"""

from __future__ import annotations

import asyncio
import logging

import httpx
import pytest

from paper_search.sources import Source

QUERY = "Hamiltonian Monte Carlo"
_TIMEOUT = httpx.Timeout(30.0)
LOGGER = logging.getLogger(__name__)


def _run(awaitable) -> object:
    return asyncio.run(awaitable)


@pytest.mark.parametrize("source", list(Source), ids=lambda source: source.value)
def test_source_returns_parsed_papers_from_real_api(source: Source) -> None:
    async def search() -> list[object]:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            strategy = source.strategy_class(client)
            return await strategy.search(QUERY, max_results=3)

    try:
        papers = _run(search())
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 429:
            pytest.skip(f"{source.label} API is rate-limited without a key (HTTP 429)")
        raise

    assert isinstance(papers, list)
    assert all(paper.title for paper in papers)
    assert all(paper.source == source.label for paper in papers)
    LOGGER.info("%s returned %d paper(s)", source.label, len(papers))


@pytest.mark.parametrize(
    "source",
    [Source.ARXIV, Source.CROSSREF, Source.PUBMED],
    ids=lambda source: source.value,
)
def test_source_search_honors_max_results(source: Source) -> None:
    async def search() -> list[object]:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            strategy = source.strategy_class(client)
            return await strategy.search(QUERY, max_results=2)

    papers = _run(search())

    assert len(papers) <= 2
