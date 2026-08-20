"""paper-search CLI."""

from __future__ import annotations

import argparse
import asyncio
import sys
from typing import TYPE_CHECKING

from paper_search.http import ResponseCache
from paper_search.output import to_json, to_markdown
from paper_search.search import DEFAULT_MAX_RESULTS_PER_SOURCE, search_papers, year_range
from paper_search.sources import DEFAULT_SOURCES, Source

if TYPE_CHECKING:
    from collections.abc import Sequence


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="paper-search", description="Search academic literature across multiple sources."
    )
    parser.add_argument("query", help="free-text search query")
    parser.add_argument(
        "--sources",
        default=",".join(source.value for source in DEFAULT_SOURCES),
        help="comma-separated sources: semantic-scholar, arxiv, pubmed, crossref, europepmc, openreview, dblp, openalex",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=DEFAULT_MAX_RESULTS_PER_SOURCE,
        dest="max_results",
        help=f"max results per source (default: {DEFAULT_MAX_RESULTS_PER_SOURCE})",
    )
    parser.add_argument(
        "--year-from", type=int, default=None, dest="year_from", help="only include papers from this year onward"
    )
    parser.add_argument(
        "--year-to", type=int, default=None, dest="year_to", help="only include papers from this year or earlier"
    )
    parser.add_argument("--format", choices=["json", "markdown"], default="json", help="output format (default: json)")
    parser.add_argument("--no-cache", action="store_true", dest="no_cache", help="disable the on-disk response cache")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI; returns the process exit code."""
    args = _build_parser().parse_args(argv)
    try:
        sources = tuple(Source(name.strip()) for name in args.sources.split(",") if name.strip())
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if not sources:
        print("error: at least one source is required", file=sys.stderr)
        return 2
    if args.max_results < 1:
        print("error: --max-results must be >= 1", file=sys.stderr)
        return 2
    cache = None if args.no_cache else ResponseCache()
    result = asyncio.run(
        search_papers(
            args.query,
            sources=sources,
            max_results_per_source=args.max_results,
            year_range=year_range(args.year_from, args.year_to),
            cache=cache,
        )
    )
    print(to_json(result) if args.format == "json" else to_markdown(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
