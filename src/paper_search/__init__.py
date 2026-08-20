"""Multi-source academic literature search, exposed as a CLI and MCP server."""

from paper_search.paper import Paper
from paper_search.search import SearchResult, SourceResult, search_papers
from paper_search.sources import DEFAULT_SOURCES, Source

__all__ = ["DEFAULT_SOURCES", "Paper", "SearchResult", "Source", "SourceResult", "search_papers"]
