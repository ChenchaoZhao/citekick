"""Unit tests for PubmedStrategy: esearch + esummary flow and parsing."""

from __future__ import annotations

import asyncio

from paper_search.sources import pubmed
from paper_search.sources.pubmed import PubmedStrategy

ESEARCH = {"esearchresult": {"idlist": ["123"]}}
ESUMMARY = {
    "result": {
        "123": {
            "title": "Protein folding survey",
            "authors": [{"name": "Carlos"}],
            "pubdate": "2021 Jan 05",
            "articleids": [{"idtype": "doi", "value": "10.1/pubmed"}, {"idtype": "pubmed", "value": "123"}],
        }
    }
}


def _by_url(url: str, _params) -> dict:
    if url.endswith("esearch.fcgi"):
        return ESEARCH
    return ESUMMARY


def test_search_queries_esearch_then_esummary(client, mock_fetch, monkeypatch) -> None:
    monkeypatch.setattr(pubmed, "NCBI_API_KEY", None)
    calls = mock_fetch(pubmed, "fetch_json", _by_url)

    papers = asyncio.run(PubmedStrategy(client).search("protein", max_results=5))

    esearch_url, esearch_params, _, _ = calls[0]
    assert esearch_url.endswith("esearch.fcgi")
    assert esearch_params == {"db": "pubmed", "term": "protein", "retmax": 5, "retmode": "json"}
    esummary_url, esummary_params, _, _ = calls[1]
    assert esummary_url.endswith("esummary.fcgi")
    assert esummary_params == {"db": "pubmed", "id": "123", "retmode": "json"}
    assert len(papers) == 1


def test_search_appends_api_key_to_both_calls(client, mock_fetch, monkeypatch) -> None:
    monkeypatch.setattr(pubmed, "NCBI_API_KEY", "test-key")
    calls = mock_fetch(pubmed, "fetch_json", _by_url)

    asyncio.run(PubmedStrategy(client).search("protein"))

    assert calls[0][1]["api_key"] == "test-key"
    assert calls[1][1]["api_key"] == "test-key"


def test_api_key_constant_reads_from_config(monkeypatch) -> None:
    monkeypatch.setattr(pubmed, "NCBI_API_KEY", "config-key")
    assert pubmed.NCBI_API_KEY == "config-key"

    monkeypatch.setattr(pubmed, "NCBI_API_KEY", None)
    assert pubmed.NCBI_API_KEY is None


def test_search_parses_summary_fields(client, mock_fetch) -> None:
    mock_fetch(pubmed, "fetch_json", _by_url)

    paper = asyncio.run(PubmedStrategy(client).search("protein"))[0]

    assert paper.title == "Protein folding survey"
    assert paper.authors == ["Carlos"]
    assert paper.year == 2021
    assert paper.doi == "10.1/pubmed"
    assert paper.url == "https://pubmed.ncbi.nlm.nih.gov/123/"
    assert paper.source == "PubMed"


def test_search_skips_summary_when_no_ids(client, mock_fetch) -> None:
    mock_fetch(pubmed, "fetch_json", {"esearchresult": {"idlist": []}})

    papers = asyncio.run(PubmedStrategy(client).search("nothing"))

    assert papers == []
