"""Render a SearchResult as JSON or Markdown."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from paper_search.paper import Paper
    from paper_search.search import SearchResult

_AUTHOR_LIMIT: int = 10


def to_json(result: SearchResult, *, indent: int = 2) -> str:
    """Serialize the search result to a pretty-printed JSON string."""
    return json.dumps(result.to_dict(), indent=indent, ensure_ascii=False)


def to_markdown(result: SearchResult) -> str:
    """Render the search result as a Markdown reference list."""
    lines = [f"# Search results for {result.query!r}", ""]
    if not result.papers:
        lines.append("No papers found.")
        return "\n".join(lines)
    for index, paper in enumerate(result.papers, start=1):
        lines.append(_paper_bullet(index, paper))
    lines.append("")
    lines.append(f"Found {len(result.papers)} paper(s) from {len(result.per_source)} queried source(s).")
    return "\n".join(lines)


def _paper_bullet(index: int, paper: Paper) -> str:
    authors = ", ".join(paper.authors[:_AUTHOR_LIMIT]) or "Unknown"
    year = str(paper.year) if paper.year is not None else "n.d."
    citation = f" ({paper.citation_count} citations)" if paper.citation_count is not None else ""
    link = paper.url or paper.doi
    lines = [f"{index}. {paper.title}", f"   {authors} ({year}). *{paper.source}*{citation}."]
    if link:
        lines.append(f"   <{link}>")
    return "\n".join(lines)
