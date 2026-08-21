"""Unit tests for EuropePmcStrategy: URL/params and result parsing."""

from __future__ import annotations

import asyncio

from citekick.sources import europepmc
from citekick.sources.europepmc import EUROPE_PMC_URL, EuropePmcStrategy

PAYLOAD = {
    "resultList": {
        "result": [
            {
                "title": "Monte Carlo in Biology",
                "authorString": "Eve, Frank, Grace",
                "pubYear": "2019",
                "doi": "10.1/epmc",
                "abstractText": "Biomolecular abstract.",
                "url": "https://europepmc.org/article/MED/1",
            }
        ]
    }
}


def test_search_requests_search_api_with_query(client, mock_fetch) -> None:
    calls = mock_fetch(europepmc, "fetch_json", PAYLOAD)

    papers = asyncio.run(EuropePmcStrategy(client).search("sampling", max_results=5))

    url, params, _, _ = calls[0]
    assert url == EUROPE_PMC_URL
    assert params == {"query": "sampling", "format": "json", "pageSize": 5}
    assert len(papers) == 1


def test_search_parses_result_fields(client, mock_fetch) -> None:
    mock_fetch(europepmc, "fetch_json", PAYLOAD)

    paper = asyncio.run(EuropePmcStrategy(client).search("sampling"))[0]

    assert paper.title == "Monte Carlo in Biology"
    assert paper.authors == ["Eve", "Frank", "Grace"]
    assert paper.year == 2019
    assert paper.doi == "10.1/epmc"
    assert paper.abstract == "Biomolecular abstract."
    assert paper.url == "https://europepmc.org/article/MED/1"
    assert paper.source == "Europe PMC"
