"""Crossref search strategy (REST API)."""

from __future__ import annotations

from citekick.config import MAILTO
from citekick.http import fetch_json
from citekick.paper import Paper
from citekick.sources.base import SearchStrategy, author_name, strip_jats, year_from_date_parts

CROSSREF_URL: str = "https://api.crossref.org/works"
_SELECT: str = "DOI,title,author,issued,URL,abstract"


class CrossrefStrategy(SearchStrategy):
    label: str = "Crossref"

    async def search(self, query: str, *, max_results: int = 10) -> list[Paper]:
        params: dict[str, object] = {"query": query, "rows": max_results, "select": _SELECT}
        if MAILTO:
            params["mailto"] = MAILTO
        data = await fetch_json(self._client, CROSSREF_URL, params=params, cache=self._cache)
        items = (data.get("message") or {}).get("items") or []
        return [self._parse(item) for item in items]

    def _parse(self, item: dict) -> Paper:
        title = (item.get("title") or [""])[0]
        return Paper(
            title=title,
            authors=[author_name(a) for a in item.get("author") or []],
            year=year_from_date_parts(item.get("issued")),
            doi=item.get("DOI"),
            abstract=strip_jats(item.get("abstract")),
            source=self.label,
            url=item.get("URL"),
        )
