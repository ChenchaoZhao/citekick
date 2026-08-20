"""Unit tests for the Source enum and registry in sources/__init__.py."""

from __future__ import annotations

import pytest

from paper_search.sources import DEFAULT_SOURCES, Source


def test_source_looks_up_by_name() -> None:
    assert Source("arxiv") is Source.ARXIV
    assert Source("semantic-scholar") is Source.SEMANTIC_SCHOLAR
    assert Source("openalex") is Source.OPENALEX


def test_source_label_matches_strategy() -> None:
    assert Source.ARXIV.label == "arXiv"
    assert Source.SEMANTIC_SCHOLAR.label == "Semantic Scholar"


def test_source_carries_strategy_class() -> None:
    assert Source.ARXIV.strategy_class.__name__ == "ArxivStrategy"
    assert Source.PUBMED.strategy_class.__name__ == "PubmedStrategy"


@pytest.mark.parametrize("source", list(Source))
def test_strategy_registry_covers_every_source(source: Source) -> None:
    assert isinstance(source.strategy_class, type)


def test_source_unknown_value_raises_value_error() -> None:
    with pytest.raises(ValueError, match="not a valid Source"):
        Source("nope")


def test_default_sources_exclude_openalex() -> None:
    assert Source.OPENALEX not in DEFAULT_SOURCES
    assert set(DEFAULT_SOURCES) == set(Source) - {Source.OPENALEX}
