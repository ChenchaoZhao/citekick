"""Source enum and strategy registry."""

from __future__ import annotations

from enum import StrEnum

from paper_search.sources.arxiv import ArxivStrategy
from paper_search.sources.base import SearchError, SearchStrategy
from paper_search.sources.crossref import CrossrefStrategy
from paper_search.sources.dblp import DblpStrategy
from paper_search.sources.europepmc import EuropePmcStrategy
from paper_search.sources.openalex import OpenAlexStrategy
from paper_search.sources.openreview import OpenReviewStrategy
from paper_search.sources.pubmed import PubmedStrategy
from paper_search.sources.semantic_scholar import SemanticScholarStrategy

__all__ = ["DEFAULT_SOURCES", "SearchError", "SearchStrategy", "Source"]


class Source(StrEnum):
    """One member per literature source, mapped to its search strategy via _STRATEGIES."""

    SEMANTIC_SCHOLAR = "semantic-scholar"
    ARXIV = "arxiv"
    PUBMED = "pubmed"
    CROSSREF = "crossref"
    EUROPE_PMC = "europepmc"
    OPENREVIEW = "openreview"
    DBLP = "dblp"
    OPENALEX = "openalex"

    @property
    def strategy_class(self) -> type[SearchStrategy]:
        """Search strategy class backing this source."""
        return _STRATEGIES[self]

    @property
    def label(self) -> str:
        """Human-readable source label, e.g. 'Semantic Scholar'."""
        return self.strategy_class.label


_STRATEGIES: dict[Source, type[SearchStrategy]] = {
    Source.SEMANTIC_SCHOLAR: SemanticScholarStrategy,
    Source.ARXIV: ArxivStrategy,
    Source.PUBMED: PubmedStrategy,
    Source.CROSSREF: CrossrefStrategy,
    Source.EUROPE_PMC: EuropePmcStrategy,
    Source.OPENREVIEW: OpenReviewStrategy,
    Source.DBLP: DblpStrategy,
    Source.OPENALEX: OpenAlexStrategy,
}

DEFAULT_SOURCES: tuple[Source, ...] = tuple(source for source in Source if source is not Source.OPENALEX)
