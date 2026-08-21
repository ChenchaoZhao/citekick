"""OpenAlex search strategy (works API, abstracts as inverted index)."""

from __future__ import annotations

from citekick.config import OPENALEX_API_KEY
from citekick.http import fetch_json
from citekick.paper import Paper
from citekick.sources.base import SearchStrategy

OPENALEX_URL: str = "https://api.openalex.org/works"
_DOI_PREFIX: str = "https://doi.org/"


class OpenAlexStrategy(SearchStrategy):
    label: str = "OpenAlex"

    async def search(self, query: str, *, max_results: int = 10) -> list[Paper]:
        params: dict[str, object] = {"search": query, "per-page": max_results}
        if OPENALEX_API_KEY:
            params["api_key"] = OPENALEX_API_KEY
        data = await fetch_json(self._client, OPENALEX_URL, params=params, cache=self._cache)
        return [self._parse(item) for item in data.get("results") or []]

    def _parse(self, item: dict) -> Paper:
        authors = [
            a["author"]["display_name"]
            for a in item.get("authorships") or []
            if (a.get("author") or {}).get("display_name")
        ]
        doi = item.get("doi")
        if doi and isinstance(doi, str) and doi.startswith(_DOI_PREFIX):
            doi = doi.removeprefix(_DOI_PREFIX)
        url = f"https://doi.org/{doi}" if doi else item.get("id")
        return Paper(
            title=item.get("title") or "",
            authors=authors,
            year=item.get("publication_year"),
            doi=doi,
            abstract=_reconstruct_abstract(item.get("abstract_inverted_index")),
            citation_count=item.get("cited_by_count"),
            source=self.label,
            url=url,
        )


def _reconstruct_abstract(inverted_index: dict | None) -> str | None:
    """Rebuild an abstract from an OpenAlex inverted index ({word: [positions]})."""
    if not inverted_index:
        return None
    words: dict[int, str] = {}
    for word, positions in inverted_index.items():
        for position in positions:
            words[position] = word
    return " ".join(words[position] for position in sorted(words))
