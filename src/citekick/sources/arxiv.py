"""arXiv search strategy (Atom XML API)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from defusedxml import ElementTree

from citekick.config import MAILTO
from citekick.http import fetch_text
from citekick.paper import Paper
from citekick.sources.base import SearchStrategy, year_from_iso

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element

ARXIV_API_URL: str = "https://export.arxiv.org/api/query"
_ARXIV_NS: dict[str, str] = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


class ArxivStrategy(SearchStrategy):
    label: str = "arXiv"

    async def search(self, query: str, *, max_results: int = 10) -> list[Paper]:
        params: dict[str, object] = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results,
        }
        if MAILTO:
            params["user"] = MAILTO
        text = await fetch_text(self._client, ARXIV_API_URL, params=params, cache=self._cache)
        root = ElementTree.fromstring(text)
        return [self._parse_entry(entry) for entry in root.findall("atom:entry", _ARXIV_NS)]

    def _parse_entry(self, entry: Element) -> Paper:
        title = _find_text(entry, "atom:title")
        authors = [name.text for name in entry.findall("atom:author/atom:name", _ARXIV_NS) if name.text]
        published = entry.findtext("atom:published", default="", namespaces=_ARXIV_NS)
        doi = _find_text(entry, "arxiv:doi")
        return Paper(
            title=title,
            authors=authors,
            year=year_from_iso(published),
            doi=doi or None,
            abstract=_find_text(entry, "atom:summary") or None,
            source=self.label,
            url=_find_text(entry, "atom:id") or None,
        )


def _find_text(element: Element, path: str) -> str:
    found = element.find(path, _ARXIV_NS)
    if found is not None and found.text:
        return " ".join(found.text.split())
    return ""
