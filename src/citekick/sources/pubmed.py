"""PubMed search strategy (NCBI E-utilities: esearch + esummary)."""

from __future__ import annotations

from citekick.config import NCBI_API_KEY
from citekick.http import fetch_json
from citekick.paper import Paper
from citekick.sources.base import SearchStrategy, year_from_pubdate

_ESEARCH_URL: str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
_ESUMMARY_URL: str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"


class PubmedStrategy(SearchStrategy):
    label: str = "PubMed"

    async def search(self, query: str, *, max_results: int = 10) -> list[Paper]:
        search_params: dict[str, object] = {"db": "pubmed", "term": query, "retmax": max_results, "retmode": "json"}
        if NCBI_API_KEY:
            search_params["api_key"] = NCBI_API_KEY
        search = await fetch_json(self._client, _ESEARCH_URL, params=search_params, cache=self._cache)
        idlist = (search.get("esearchresult") or {}).get("idlist") or []
        if not idlist:
            return []
        summary_params: dict[str, object] = {"db": "pubmed", "id": ",".join(idlist), "retmode": "json"}
        if NCBI_API_KEY:
            summary_params["api_key"] = NCBI_API_KEY
        summary = await fetch_json(self._client, _ESUMMARY_URL, params=summary_params, cache=self._cache)
        result = summary.get("result") or {}
        return [self._parse(pmid, result.get(pmid) or {}) for pmid in idlist if pmid in result]

    def _parse(self, pmid: str, item: dict) -> Paper:
        authors = [a.get("name", "") for a in item.get("authors") or [] if a.get("name")]
        doi = _doi_from_ids(item.get("articleids") or [])
        return Paper(
            title=item.get("title") or "",
            authors=authors,
            year=year_from_pubdate(item.get("pubdate", "")),
            doi=doi,
            source=self.label,
            url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
        )


def _doi_from_ids(article_ids: list[dict]) -> str | None:
    for entry in article_ids:
        if entry.get("idtype") == "doi" and entry.get("value"):
            return entry["value"]
    return None
