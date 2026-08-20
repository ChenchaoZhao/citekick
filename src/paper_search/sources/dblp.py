"""DBLP search strategy (public search API)."""

from __future__ import annotations

from paper_search.http import fetch_json
from paper_search.paper import Paper
from paper_search.sources.base import SearchStrategy, as_int, dblp_authors

DBLP_URL: str = "https://dblp.org/search/publ/api"


class DblpStrategy(SearchStrategy):
    label: str = "DBLP"

    async def search(self, query: str, *, max_results: int = 10) -> list[Paper]:
        data = await fetch_json(
            self._client,
            DBLP_URL,
            params={"q": query, "format": "json", "h": max_results},
            cache=self._cache,
        )
        hits = ((data.get("result") or {}).get("hits") or {}).get("hit") or []
        return [self._parse(hit.get("info") or {}) for hit in hits]

    def _parse(self, info: dict) -> Paper:
        doi = info.get("doi")
        url = info.get("ee") or (f"https://doi.org/{doi}" if doi else None)
        return Paper(
            title=info.get("title") or "",
            authors=dblp_authors(info.get("authors")),
            year=as_int(info.get("year")),
            doi=doi,
            source=self.label,
            url=url,
        )
