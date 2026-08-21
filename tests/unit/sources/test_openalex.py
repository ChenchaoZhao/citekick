"""Unit tests for OpenAlexStrategy: URL/params, result parsing, and abstract rebuild."""

from __future__ import annotations

import asyncio

import pytest

from citekick.sources import openalex
from citekick.sources.openalex import OPENALEX_URL, OpenAlexStrategy, _reconstruct_abstract

PAYLOAD = {
    "results": [
        {
            "title": "Deep Learning for Proteins",
            "authorships": [{"author": {"display_name": "Mia"}}],
            "publication_year": 2020,
            "doi": "https://doi.org/10.1/openalex",
            "abstract_inverted_index": {"Deep": [0], "learning": [1], "for": [2], "proteins": [3]},
            "cited_by_count": 7,
        }
    ]
}


def test_search_requests_works_api_with_query(client, mock_fetch, monkeypatch) -> None:
    monkeypatch.setattr(openalex, "OPENALEX_API_KEY", None)
    calls = mock_fetch(openalex, "fetch_json", PAYLOAD)

    papers = asyncio.run(OpenAlexStrategy(client).search("sampling", max_results=5))

    url, params, headers, _ = calls[0]
    assert url == OPENALEX_URL
    assert params == {"search": "sampling", "per-page": 5}
    assert headers is None
    assert len(papers) == 1


def test_search_sends_api_key_query_param_when_configured(client, mock_fetch, monkeypatch) -> None:
    monkeypatch.setattr(openalex, "OPENALEX_API_KEY", "test-key")
    calls = mock_fetch(openalex, "fetch_json", PAYLOAD)

    asyncio.run(OpenAlexStrategy(client).search("sampling"))

    _, params, _, _ = calls[0]
    assert params["api_key"] == "test-key"


def test_api_key_constant_reads_from_config(monkeypatch) -> None:
    monkeypatch.setattr(openalex, "OPENALEX_API_KEY", "config-key")
    assert openalex.OPENALEX_API_KEY == "config-key"

    monkeypatch.setattr(openalex, "OPENALEX_API_KEY", None)
    assert openalex.OPENALEX_API_KEY is None


def test_search_parses_result_fields(client, mock_fetch) -> None:
    mock_fetch(openalex, "fetch_json", PAYLOAD)

    paper = asyncio.run(OpenAlexStrategy(client).search("sampling"))[0]

    assert paper.title == "Deep Learning for Proteins"
    assert paper.authors == ["Mia"]
    assert paper.year == 2020
    assert paper.doi == "10.1/openalex"
    assert paper.abstract == "Deep learning for proteins"
    assert paper.citation_count == 7
    assert paper.url == "https://doi.org/10.1/openalex"
    assert paper.source == "OpenAlex"


@pytest.mark.parametrize("missing", ["", None])
def test_abstract_missing_returns_none(missing: str | None) -> None:
    assert _reconstruct_abstract(missing) is None
