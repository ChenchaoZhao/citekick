"""Semantic Scholar search strategy (Graph API)."""

from __future__ import annotations

from citekick.config import SEMANTIC_SCHOLAR_API_KEY
from citekick.http import fetch_json
from citekick.paper import Paper
from citekick.sources.base import SearchStrategy

SEMANTIC_SCHOLAR_URL: str = "https://api.semanticscholar.org/graph/v1/paper/search"
_FIELDS: str = "title,authors,year,externalIds,abstract,url,citationCount"


class SemanticScholarStrategy(SearchStrategy):
    label: str = "Semantic Scholar"

    async def search(self, query: str, *, max_results: int = 10) -> list[Paper]:
        params = {"query": query, "limit": max_results, "fields": _FIELDS}
        headers = {"x-api-key": SEMANTIC_SCHOLAR_API_KEY} if SEMANTIC_SCHOLAR_API_KEY else None
        data = await fetch_json(self._client, SEMANTIC_SCHOLAR_URL, params=params, headers=headers, cache=self._cache)
        return [self._parse(item) for item in data.get("data") or []]

    def _parse(self, item: dict) -> Paper:
        authors = [a.get("name", "") for a in item.get("authors") or [] if a.get("name")]
        doi = (item.get("externalIds") or {}).get("DOI")
        return Paper(
            title=item.get("title") or "",
            authors=authors,
            year=item.get("year"),
            doi=doi,
            abstract=item.get("abstract"),
            citation_count=item.get("citationCount"),
            source=self.label,
            url=item.get("url"),
        )
