"""Europe PMC search strategy (RESTful Web Service)."""

from __future__ import annotations

from citekick.http import fetch_json
from citekick.paper import Paper
from citekick.sources.base import SearchStrategy, as_int

EUROPE_PMC_URL: str = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"


class EuropePmcStrategy(SearchStrategy):
    label: str = "Europe PMC"

    async def search(self, query: str, *, max_results: int = 10) -> list[Paper]:
        data = await fetch_json(
            self._client,
            EUROPE_PMC_URL,
            params={"query": query, "format": "json", "pageSize": max_results},
            cache=self._cache,
        )
        results = (data.get("resultList") or {}).get("result") or []
        return [self._parse(item) for item in results]

    def _parse(self, item: dict) -> Paper:
        authors = [name.strip() for name in (item.get("authorString") or "").split(",") if name.strip()]
        return Paper(
            title=item.get("title") or "",
            authors=authors,
            year=as_int(item.get("pubYear")),
            doi=item.get("doi"),
            abstract=item.get("abstractText"),
            source=self.label,
            url=item.get("url"),
        )
