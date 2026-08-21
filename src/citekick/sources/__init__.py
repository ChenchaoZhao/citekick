"""Source enum and strategy registry."""

from __future__ import annotations

from enum import StrEnum

from citekick.sources.arxiv import ArxivStrategy
from citekick.sources.base import SearchError, SearchStrategy
from citekick.sources.crossref import CrossrefStrategy
from citekick.sources.dblp import DblpStrategy
from citekick.sources.europepmc import EuropePmcStrategy
from citekick.sources.openalex import OpenAlexStrategy
from citekick.sources.openreview import OpenReviewStrategy
from citekick.sources.pubmed import PubmedStrategy
from citekick.sources.semantic_scholar import SemanticScholarStrategy

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
