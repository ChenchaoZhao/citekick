"""Unit tests for SemanticScholarStrategy: URL/params and Graph API parsing."""

from __future__ import annotations

import asyncio

from paper_search.sources import semantic_scholar
from paper_search.sources.semantic_scholar import SEMANTIC_SCHOLAR_URL, SemanticScholarStrategy

PAYLOAD = {
    "data": [
        {
            "paperId": "abc",
            "title": "Markov Chains for Sampling",
            "authors": [{"name": "Alice"}, {"name": "Bob"}],
            "year": 2020,
            "externalIds": {"DOI": "10.1000/xyz"},
            "abstract": "An abstract.",
            "url": "https://api.semanticscholar.org/abc",
            "citationCount": 42,
        }
    ]
}


def test_search_requests_graph_api_with_query(client, mock_fetch, monkeypatch) -> None:
    monkeypatch.setattr(semantic_scholar, "SEMANTIC_SCHOLAR_API_KEY", None)
    calls = mock_fetch(semantic_scholar, "fetch_json", PAYLOAD)

    papers = asyncio.run(SemanticScholarStrategy(client).search("sampling", max_results=5))

    url, params, headers, _ = calls[0]
    assert url == SEMANTIC_SCHOLAR_URL
    assert params == {
        "query": "sampling",
        "limit": 5,
        "fields": "title,authors,year,externalIds,abstract,url,citationCount",
    }
    assert headers is None
    assert len(papers) == 1


def test_search_sends_api_key_header_when_configured(client, mock_fetch, monkeypatch) -> None:
    monkeypatch.setattr(semantic_scholar, "SEMANTIC_SCHOLAR_API_KEY", "test-key")
    calls = mock_fetch(semantic_scholar, "fetch_json", PAYLOAD)

    asyncio.run(SemanticScholarStrategy(client).search("sampling"))

    _, _, headers, _ = calls[0]
    assert headers == {"x-api-key": "test-key"}


def test_api_key_constant_reads_from_config(monkeypatch) -> None:
    monkeypatch.setattr(semantic_scholar, "SEMANTIC_SCHOLAR_API_KEY", "config-key")
    assert semantic_scholar.SEMANTIC_SCHOLAR_API_KEY == "config-key"

    monkeypatch.setattr(semantic_scholar, "SEMANTIC_SCHOLAR_API_KEY", None)
    assert semantic_scholar.SEMANTIC_SCHOLAR_API_KEY is None


def test_search_parses_paper_fields(client, mock_fetch) -> None:
    mock_fetch(semantic_scholar, "fetch_json", PAYLOAD)

    paper = asyncio.run(SemanticScholarStrategy(client).search("sampling"))[0]

    assert paper.title == "Markov Chains for Sampling"
    assert paper.authors == ["Alice", "Bob"]
    assert paper.year == 2020
    assert paper.doi == "10.1000/xyz"
    assert paper.abstract == "An abstract."
    assert paper.citation_count == 42
    assert paper.url == "https://api.semanticscholar.org/abc"
    assert paper.source == "Semantic Scholar"
