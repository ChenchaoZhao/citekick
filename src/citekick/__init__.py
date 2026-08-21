"""Multi-source academic literature search, exposed as a CLI and MCP server."""

from citekick.paper import Paper
from citekick.search import SearchResult, SourceResult, search_papers
from citekick.sources import DEFAULT_SOURCES, Source

__all__ = ["DEFAULT_SOURCES", "Paper", "SearchResult", "Source", "SourceResult", "search_papers"]
