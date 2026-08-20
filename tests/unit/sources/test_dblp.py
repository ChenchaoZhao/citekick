"""Unit tests for DblpStrategy: URL/params and hit parsing."""

from __future__ import annotations

import asyncio

from paper_search.sources import dblp
from paper_search.sources.dblp import DBLP_URL, DblpStrategy

PAYLOAD = {
    "result": {
        "hits": {
            "hit": [
                {
                    "info": {
                        "title": "Gradient-based Sampling",
                        "authors": {"author": [{"text": "Jack"}, {"text": "Kim"}]},
                        "year": "2021",
                        "doi": "10.1/dblp",
                        "ee": "https://dblp.org/rec/x",
                    }
                }
            ]
        }
    }
}

SINGLE_AUTHOR = {
    "result": {
        "hits": {
            "hit": [
                {
                    "info": {
                        "title": "Solo Paper",
                        "authors": {"author": {"text": "Liam"}},
                        "year": "2020",
                        "doi": "10.1/solo",
                    }
                }
            ]
        }
    }
}


def test_search_requests_public_api_with_query(client, mock_fetch) -> None:
    calls = mock_fetch(dblp, "fetch_json", PAYLOAD)

    papers = asyncio.run(DblpStrategy(client).search("sampling", max_results=5))

    url, params, _, _ = calls[0]
    assert url == DBLP_URL
    assert params == {"q": "sampling", "format": "json", "h": 5}
    assert len(papers) == 1


def test_search_parses_hit_fields(client, mock_fetch) -> None:
    mock_fetch(dblp, "fetch_json", PAYLOAD)

    paper = asyncio.run(DblpStrategy(client).search("sampling"))[0]

    assert paper.title == "Gradient-based Sampling"
    assert paper.authors == ["Jack", "Kim"]
    assert paper.year == 2021
    assert paper.doi == "10.1/dblp"
    assert paper.url == "https://dblp.org/rec/x"
    assert paper.source == "DBLP"


def test_search_parses_single_author_hit(client, mock_fetch) -> None:
    mock_fetch(dblp, "fetch_json", SINGLE_AUTHOR)

    paper = asyncio.run(DblpStrategy(client).search("sampling"))[0]

    assert paper.authors == ["Liam"]
    assert paper.url == "https://doi.org/10.1/solo"
