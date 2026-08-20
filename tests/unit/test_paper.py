"""Unit tests for the normalized Paper model."""

from __future__ import annotations

from paper_search.paper import Paper


def test_paper_has_empty_defaults() -> None:
    paper = Paper(title="Only title")

    assert paper.authors == []
    assert paper.year is None
    assert paper.doi is None
    assert paper.abstract is None
    assert paper.citation_count is None
    assert paper.source == ""
    assert paper.url is None


def test_paper_to_dict_serializes_all_fields() -> None:
    paper = Paper(title="HMC", authors=["A"], year=2024, doi="10.1/x", citation_count=3, source="arXiv")

    payload = paper.to_dict()

    assert payload == {
        "title": "HMC",
        "authors": ["A"],
        "year": 2024,
        "doi": "10.1/x",
        "abstract": None,
        "citation_count": 3,
        "source": "arXiv",
        "url": None,
    }


def test_paper_to_dict_copies_authors_list() -> None:
    authors = ["A"]
    payload = Paper(title="HMC", authors=authors).to_dict()

    authors.append("B")

    assert payload["authors"] == ["A"]
