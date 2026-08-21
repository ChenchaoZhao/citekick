"""Tests for the MCP server: tool registration and the search_papers tool."""

from __future__ import annotations

import asyncio
import json
from collections.abc import Awaitable
from typing import TYPE_CHECKING, Any

import pytest

from citekick import mcp_server
from citekick.mcp_server import _parse_sources, mcp
from citekick.paper import Paper
from citekick.search import SearchResult, SourceResult
from citekick.sources import DEFAULT_SOURCES, Source

if TYPE_CHECKING:
    from collections.abc import Awaitable


def _run(awaitable: Awaitable[Any]) -> Any:
    return asyncio.run(awaitable)


def test_mcp_exposes_search_papers_tool() -> None:
    tools = _run(mcp.list_tools())

    assert "search_papers" in [tool.name for tool in tools]


def test_search_papers_tool_returns_json_with_query_and_papers(monkeypatch: Any) -> None:
    async def fake_core(query: str, **kwargs: Any) -> SearchResult:
        assert kwargs["sources"] == (Source.ARXIV,)
        assert kwargs["max_results_per_source"] == 5
        assert kwargs["year_range"] == (2020, 2024)
        paper = Paper(title="Fake Paper", source="arXiv", year=2023, doi="10.1/fake")
        return SearchResult(query=query, papers=[paper], per_source=[SourceResult(source=Source.ARXIV, papers=[paper])])

    monkeypatch.setattr(mcp_server, "search_papers_core", fake_core)

    content, _ = _run(
        mcp.call_tool(
            "search_papers",
            {"query": "protein", "sources": "arxiv", "max_results_per_source": 5, "year_from": 2020, "year_to": 2024},
        )
    )

    payload = json.loads(content[0].text)
    assert payload["query"] == "protein"
    assert payload["papers"][0]["title"] == "Fake Paper"


def test_search_papers_tool_defaults_to_all_keyless_sources(monkeypatch: Any) -> None:
    async def fake_core(query: str, **kwargs: Any) -> SearchResult:
        assert kwargs["sources"] == DEFAULT_SOURCES
        assert kwargs["year_range"] is None
        return SearchResult(query=query)

    monkeypatch.setattr(mcp_server, "search_papers_core", fake_core)

    _run(mcp.call_tool("search_papers", {"query": "hmc"}))


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("", DEFAULT_SOURCES),
        ("arxiv", (Source.ARXIV,)),
        ("arxiv, pubmed", (Source.ARXIV, Source.PUBMED)),
        ("arxiv,pubmed", (Source.ARXIV, Source.PUBMED)),
    ],
)
def test_parse_sources_maps_comma_separated_names(raw: str, expected: tuple[Source, ...]) -> None:
    assert _parse_sources(raw) == expected


def test_parse_sources_unknown_name_raises() -> None:
    with pytest.raises(ValueError, match="not a valid Source"):
        _parse_sources("arxiv,fake")
