"""Unit tests for ArxivStrategy: URL/params construction and Atom XML parsing."""

from __future__ import annotations

import asyncio

from citekick.sources import arxiv
from citekick.sources.arxiv import ARXIV_API_URL, ArxivStrategy

ARXIV_XML = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <id>http://arxiv.org/abs/2310.00001</id>
    <published>2023-10-01T00:00:00Z</published>
    <title>  A Test Paper on Sampling  </title>
    <summary>This is the abstract text.</summary>
    <author><name>Alice Example</name></author>
    <author><name>Bob Example</name></author>
    <arxiv:doi>10.1/paper</arxiv:doi>
  </entry>
</feed>
"""


def test_search_requests_arxiv_api_with_query(client, mock_fetch, monkeypatch) -> None:
    monkeypatch.setattr(arxiv, "MAILTO", None)
    calls = mock_fetch(arxiv, "fetch_text", ARXIV_XML)

    papers = asyncio.run(ArxivStrategy(client).search("sampling", max_results=5))

    url, params, _, _ = calls[0]
    assert url == ARXIV_API_URL
    assert params == {"search_query": "all:sampling", "start": 0, "max_results": 5}
    assert len(papers) == 1


def test_search_parses_entry_fields(client, mock_fetch) -> None:
    mock_fetch(arxiv, "fetch_text", ARXIV_XML)

    paper = asyncio.run(ArxivStrategy(client).search("sampling"))[0]

    assert paper.title == "A Test Paper on Sampling"
    assert paper.authors == ["Alice Example", "Bob Example"]
    assert paper.year == 2023
    assert paper.abstract == "This is the abstract text."
    assert paper.doi == "10.1/paper"
    assert paper.url == "http://arxiv.org/abs/2310.00001"
    assert paper.source == "arXiv"
