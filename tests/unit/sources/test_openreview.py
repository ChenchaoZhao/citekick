"""Unit tests for OpenReviewStrategy: URL/params and API v2 note parsing."""

from __future__ import annotations

import asyncio

from paper_search.sources import openreview
from paper_search.sources.openreview import OPENREVIEW_URL, OpenReviewStrategy

PAYLOAD = {
    "notes": [
        {
            "id": "review1",
            "forum": "forum1",
            "pdate": 1577880000000,
            "content": {
                "title": {"value": "Counterdiabatic HMC"},
                "abstract": {"value": "An abstract."},
                "authors": {"value": ["Hank", "Ivy"]},
            },
        }
    ]
}


def test_search_requests_notes_api_with_query(client, mock_fetch) -> None:
    calls = mock_fetch(openreview, "fetch_json", PAYLOAD)

    papers = asyncio.run(OpenReviewStrategy(client).search("sampling", max_results=5))

    url, params, _, _ = calls[0]
    assert url == OPENREVIEW_URL
    assert params == {"query": "sampling", "limit": 5}
    assert len(papers) == 1


def test_search_parses_note_fields(client, mock_fetch) -> None:
    mock_fetch(openreview, "fetch_json", PAYLOAD)

    paper = asyncio.run(OpenReviewStrategy(client).search("sampling"))[0]

    assert paper.title == "Counterdiabatic HMC"
    assert paper.authors == ["Hank", "Ivy"]
    assert paper.year == 2020
    assert paper.abstract == "An abstract."
    assert paper.url == "https://openreview.net/forum?id=forum1"
    assert paper.source == "OpenReview"


def test_search_falls_back_to_note_id_for_url(client, mock_fetch) -> None:
    payload = {"notes": [{"id": "only-id", "content": {"title": {"value": "Solo"}}}]}
    mock_fetch(openreview, "fetch_json", payload)

    paper = asyncio.run(OpenReviewStrategy(client).search("sampling"))[0]

    assert paper.url == "https://openreview.net/forum?id=only-id"
