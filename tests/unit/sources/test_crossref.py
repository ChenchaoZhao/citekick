"""Unit tests for CrossrefStrategy: URL/params and REST parsing."""

from __future__ import annotations

import asyncio

from paper_search.sources import crossref
from paper_search.sources.crossref import CROSSREF_URL, CrossrefStrategy

PAYLOAD = {
    "message": {
        "items": [
            {
                "DOI": "10.1000/crossref",
                "title": ["Polynomial-time Sampling"],
                "author": [{"given": "Dana", "family": "Smith"}, {"name": "Institute of Science"}],
                "issued": {"date-parts": [[2022, 3]]},
                "URL": "https://doi.org/10.1000/crossref",
                "abstract": "<jats:p>Abstract <jats:bold>with</jats:bold> tags.</jats:p>",
            }
        ]
    }
}


def test_search_requests_works_api_with_query(client, mock_fetch, monkeypatch) -> None:
    monkeypatch.setattr(crossref, "MAILTO", None)
    calls = mock_fetch(crossref, "fetch_json", PAYLOAD)

    papers = asyncio.run(CrossrefStrategy(client).search("sampling", max_results=5))

    url, params, _, _ = calls[0]
    assert url == CROSSREF_URL
    assert params == {"query": "sampling", "rows": 5, "select": "DOI,title,author,issued,URL,abstract"}
    assert len(papers) == 1


def test_search_appends_mailto_when_configured(client, mock_fetch, monkeypatch) -> None:
    monkeypatch.setattr(crossref, "MAILTO", "me@example.com")
    calls = mock_fetch(crossref, "fetch_json", PAYLOAD)

    asyncio.run(CrossrefStrategy(client).search("sampling"))

    _, params, _, _ = calls[0]
    assert params["mailto"] == "me@example.com"


def test_search_parses_paper_fields(client, mock_fetch) -> None:
    mock_fetch(crossref, "fetch_json", PAYLOAD)

    paper = asyncio.run(CrossrefStrategy(client).search("sampling"))[0]

    assert paper.title == "Polynomial-time Sampling"
    assert paper.authors == ["Dana Smith", "Institute of Science"]
    assert paper.year == 2022
    assert paper.doi == "10.1000/crossref"
    assert paper.abstract == "Abstract with tags."
    assert paper.url == "https://doi.org/10.1000/crossref"
    assert paper.source == "Crossref"
