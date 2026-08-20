"""OpenReview search strategy (API v2 notes search)."""

from __future__ import annotations

from paper_search.http import fetch_json
from paper_search.paper import Paper
from paper_search.sources.base import SearchStrategy, content_value, year_from_epoch_ms

OPENREVIEW_URL: str = "https://api2.openreview.net/notes/search"


class OpenReviewStrategy(SearchStrategy):
    label: str = "OpenReview"

    async def search(self, query: str, *, max_results: int = 10) -> list[Paper]:
        data = await fetch_json(
            self._client,
            OPENREVIEW_URL,
            params={"query": query, "limit": max_results},
            cache=self._cache,
        )
        return [self._parse(note) for note in data.get("notes") or []]

    def _parse(self, note: dict) -> Paper:
        content = note.get("content") or {}
        authors = [name for name in content_value(content.get("authors")) or [] if name]
        forum = note.get("forum") or note.get("id")
        return Paper(
            title=content_value(content.get("title")) or "",
            authors=authors,
            year=year_from_epoch_ms(note.get("pdate")),
            abstract=content_value(content.get("abstract")),
            source=self.label,
            url=f"https://openreview.net/forum?id={forum}" if forum else None,
        )
