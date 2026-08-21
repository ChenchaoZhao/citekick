"""MCP server exposing paper search as a `search_papers` tool."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from citekick.config import (
    DEFAULT_MAX_RESULTS_CONFIG,
    DEFAULT_SOURCES_CONFIG,
    DEFAULT_YEAR_FROM_CONFIG,
    DEFAULT_YEAR_TO_CONFIG,
)
from citekick.http import ResponseCache
from citekick.output import to_json
from citekick.search import DEFAULT_MAX_RESULTS_PER_SOURCE, year_range
from citekick.search import search_papers as search_papers_core
from citekick.sources import DEFAULT_SOURCES, Source

mcp = FastMCP("citekick")

_DEFAULT_SOURCES_VALUE: str = ",".join(source.value for source in DEFAULT_SOURCES)


@mcp.tool()
async def search_papers(
    query: str,
    sources: str | None = None,
    max_results_per_source: int | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
) -> str:
    """Search academic literature across multiple sources, returning deduplicated and ranked results as JSON.

    Args:
        query: Free-text search query, e.g. "Hamiltonian Monte Carlo protein design".
        sources: Comma-separated source names: semantic-scholar, arxiv, pubmed, crossref, europepmc, openreview, dblp, openalex. Defaults to all keyless free sources.
        max_results_per_source: Maximum number of results fetched per source.
        year_from: Only include papers published in or after this year.
        year_to: Only include papers published in or before this year.
    """
    if sources is None:
        sources = DEFAULT_SOURCES_CONFIG if DEFAULT_SOURCES_CONFIG else _DEFAULT_SOURCES_VALUE
    if max_results_per_source is None:
        max_results_per_source = (
            DEFAULT_MAX_RESULTS_CONFIG if DEFAULT_MAX_RESULTS_CONFIG is not None else DEFAULT_MAX_RESULTS_PER_SOURCE
        )
    if year_from is None:
        year_from = DEFAULT_YEAR_FROM_CONFIG
    if year_to is None:
        year_to = DEFAULT_YEAR_TO_CONFIG

    selected = _parse_sources(sources)
    result = await search_papers_core(
        query,
        sources=selected,
        max_results_per_source=max_results_per_source,
        year_range=year_range(year_from, year_to),
        cache=ResponseCache(),
    )
    return to_json(result)


def _parse_sources(sources: str) -> tuple[Source, ...]:
    """Parse a comma-separated source list; the empty string means all defaults."""
    names = [name.strip() for name in sources.split(",") if name.strip()]
    if not names:
        return DEFAULT_SOURCES
    return tuple(Source(name) for name in names)


def main() -> None:
    """Run the MCP server over stdio."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
