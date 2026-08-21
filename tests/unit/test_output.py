"""Tests for JSON and Markdown output rendering."""

from __future__ import annotations

import json

from citekick.output import to_json, to_markdown
from citekick.paper import Paper
from citekick.search import SearchResult, SourceResult
from citekick.sources import Source


def _sample_result() -> SearchResult:
    paper = Paper(
        title="Hamiltonian Monte Carlo",
        authors=["Alice Example", "Bob Example"],
        year=2024,
        doi="10.1/hmc",
        citation_count=3,
        source="arXiv",
        url="http://arxiv.org/abs/2401.00001",
    )
    return SearchResult(
        query="hmc",
        papers=[paper],
        per_source=[SourceResult(source=Source.ARXIV, papers=[paper])],
        total_fetched=1,
    )


def test_to_json_serializes_normalized_paper_fields() -> None:
    payload = json.loads(to_json(_sample_result()))

    assert payload["query"] == "hmc"
    assert payload["result_count"] == 1
    paper = payload["papers"][0]
    assert paper["title"] == "Hamiltonian Monte Carlo"
    assert paper["authors"] == ["Alice Example", "Bob Example"]
    assert paper["year"] == 2024
    assert paper["doi"] == "10.1/hmc"
    assert paper["source"] == "arXiv"
    assert paper["url"] == "http://arxiv.org/abs/2401.00001"


def test_to_json_includes_per_source_summary() -> None:
    payload = json.loads(to_json(_sample_result()))

    assert payload["per_source"] == [{"source": "arxiv", "count": 1, "error": None}]
    assert payload["total_fetched"] == 1


def test_to_markdown_lists_papers_with_metadata() -> None:
    markdown = to_markdown(_sample_result())

    assert "Hamiltonian Monte Carlo" in markdown
    assert "Alice Example, Bob Example" in markdown
    assert "2024" in markdown
    assert "*arXiv*" in markdown
    assert "http://arxiv.org/abs/2401.00001" in markdown
    assert "1 paper(s)" in markdown


def test_to_markdown_empty_result_returns_explicit_message() -> None:
    empty = SearchResult(query="nothing", papers=[], per_source=[], total_fetched=0)

    markdown = to_markdown(empty)

    assert "No papers found." in markdown
