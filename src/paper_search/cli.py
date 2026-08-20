"""paper-search CLI."""

from __future__ import annotations

import asyncio
import sys
from typing import TYPE_CHECKING, Any

import fire  # type: ignore[import-untyped]

from paper_search.config import (
    CONFIG_PATH,
    DEFAULT_FORMAT_CONFIG,
    DEFAULT_MAX_RESULTS_CONFIG,
    DEFAULT_NO_CACHE_CONFIG,
    DEFAULT_SOURCES_CONFIG,
    DEFAULT_YEAR_FROM_CONFIG,
    DEFAULT_YEAR_TO_CONFIG,
    update_config,
)
from paper_search.http import ResponseCache
from paper_search.output import to_json, to_markdown
from paper_search.search import DEFAULT_MAX_RESULTS_PER_SOURCE, search_papers, year_range
from paper_search.sources import DEFAULT_SOURCES, Source

if TYPE_CHECKING:
    from collections.abc import Sequence


DEFAULT_SOURCE_VALUES: str = ",".join(s.value for s in DEFAULT_SOURCES)


class CLI:
    """Paper search tool."""

    def search(
        self,
        query: str,
        sources: str | tuple[str, ...] | list[str] | None = None,
        max_results: int | None = None,
        year_from: int | None = None,
        year_to: int | None = None,
        format: str | None = None,  # noqa: A002
        no_cache: bool | None = None,  # noqa: FBT001
    ) -> None:
        """Search academic literature across multiple sources."""
        if sources is None:
            sources = DEFAULT_SOURCES_CONFIG if DEFAULT_SOURCES_CONFIG else DEFAULT_SOURCE_VALUES
        if max_results is None:
            max_results = (
                DEFAULT_MAX_RESULTS_CONFIG if DEFAULT_MAX_RESULTS_CONFIG is not None else DEFAULT_MAX_RESULTS_PER_SOURCE
            )
        if year_from is None:
            year_from = DEFAULT_YEAR_FROM_CONFIG
        if year_to is None:
            year_to = DEFAULT_YEAR_TO_CONFIG
        fmt = format if format is not None else (DEFAULT_FORMAT_CONFIG if DEFAULT_FORMAT_CONFIG else "json")
        if no_cache is None:
            no_cache = DEFAULT_NO_CACHE_CONFIG if DEFAULT_NO_CACHE_CONFIG is not None else False

        try:
            if isinstance(sources, str):
                source_names = [item.strip() for item in sources.split(",") if item.strip()]
            else:
                source_names = [str(item).strip() for item in sources if str(item).strip()]
            source_list = tuple(Source(name) for name in source_names)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            sys.exit(2)
        if not source_list:
            print("error: at least one source is required", file=sys.stderr)
            sys.exit(2)
        if max_results < 1:
            print("error: --max-results must be >= 1", file=sys.stderr)
            sys.exit(2)
        cache = None if no_cache else ResponseCache()
        result = asyncio.run(
            search_papers(
                query,
                sources=source_list,
                max_results_per_source=max_results,
                year_range=year_range(year_from, year_to),
                cache=cache,
            )
        )
        print(to_json(result) if fmt == "json" else to_markdown(result))

    def config(
        self,
        mailto: str | None = None,
        openalex_api_key: str | None = None,
        semantic_scholar_api_key: str | None = None,
        ncbi_api_key: str | None = None,
        sources: str | None = None,
        max_results: int | None = None,
        year_from: int | None = None,
        year_to: int | None = None,
        format: str | None = None,  # noqa: A002
        no_cache: bool | None = None,  # noqa: FBT001
    ) -> None:
        """Configure API keys and default search settings in ~/.config/paper-search/config.toml."""
        api_values: dict[str, str | None] = {
            k: v
            for k, v in {
                "mailto": mailto,
                "openalex_api_key": openalex_api_key,
                "semantic_scholar_api_key": semantic_scholar_api_key,
                "ncbi_api_key": ncbi_api_key,
            }.items()
            if v is not None
        }
        search_values: dict[str, Any] = {
            k: v
            for k, v in {
                "sources": sources,
                "max_results": max_results,
                "year_from": year_from,
                "year_to": year_to,
                "format": format,
                "no_cache": no_cache,
            }.items()
            if v is not None
        }
        if not api_values and not search_values:
            if not CONFIG_PATH.is_file():
                update_config(
                    api_values={
                        "mailto": "",
                        "openalex_api_key": "",
                        "semantic_scholar_api_key": "",
                        "ncbi_api_key": "",
                    },
                    search_values={
                        "sources": "",
                        "max_results": 10,
                    },
                )
                print(f"Created configuration file at {CONFIG_PATH}")
            else:
                print(f"Configuration file already exists at {CONFIG_PATH}")
            return
        update_config(
            api_values=api_values if api_values else None,
            search_values=search_values if search_values else None,
        )
        print("Configuration updated.")


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI."""
    if argv is None:
        argv = sys.argv[1:]
    # Prepend 'search' if no subcommand/flag is provided and query is present
    if argv and not argv[0].startswith("-") and argv[0] not in ["search", "config"]:
        argv = ["search", *argv]

    try:
        result = fire.Fire(CLI(), command=argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 2
    else:
        if isinstance(result, int):
            return result
        return 0
