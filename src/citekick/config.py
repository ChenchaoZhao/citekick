"""User configuration loaded once at import time from ``~/.config/citekick/config.toml``."""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

import tomli_w

CONFIG_DIR: Path = Path.home() / ".config" / "citekick"
CONFIG_PATH: Path = CONFIG_DIR / "config.toml"


def _load(path: Path = CONFIG_PATH) -> dict[str, str | None]:
    """Read the TOML config file and return a flat dict of api values.

    Missing file, missing table, or empty/absent key all resolve to ``None``.
    """
    if not path.is_file():
        return {}
    with path.open("rb") as fh:
        data = tomllib.load(fh)
    api: dict[str, str | None] = data.get("api", {})
    return api


def _load_search(path: Path = CONFIG_PATH) -> dict[str, Any]:
    """Read the TOML config file and return a flat dict of search values."""
    if not path.is_file():
        return {}
    with path.open("rb") as fh:
        data = tomllib.load(fh)
    search: dict[str, Any] = data.get("search", {})
    return search


def _write(data: dict[str, dict[str, Any]]) -> None:
    """Write the TOML config file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with CONFIG_PATH.open("wb") as fh:
        tomli_w.dump(data, fh)


def update_config(
    api_values: dict[str, str | None] | None = None,
    search_values: dict[str, Any] | None = None,
) -> None:
    """Update or create the TOML config file with new api and/or search values."""
    if not CONFIG_PATH.is_file():
        data: dict[str, dict[str, Any]] = {}
    else:
        with CONFIG_PATH.open("rb") as fh:
            data = tomllib.load(fh)
    if api_values:
        if "api" not in data:
            data["api"] = {}
        data["api"].update(api_values)
    if search_values:
        if "search" not in data:
            data["search"] = {}
        data["search"].update(search_values)
    _write(data)


_API: dict[str, str | None] = _load()
_SEARCH: dict[str, Any] = _load_search()


def _get(key: str) -> str | None:
    value = _API.get(key)
    return value if value else None


def _get_search(key: str) -> Any:
    return _SEARCH.get(key)


MAILTO: str | None = _get("mailto")
OPENALEX_API_KEY: str | None = _get("openalex_api_key")
SEMANTIC_SCHOLAR_API_KEY: str | None = _get("semantic_scholar_api_key")
NCBI_API_KEY: str | None = _get("ncbi_api_key")

DEFAULT_SOURCES_CONFIG: str | None = _get_search("sources")
DEFAULT_MAX_RESULTS_CONFIG: int | None = _get_search("max_results")
DEFAULT_YEAR_FROM_CONFIG: int | None = _get_search("year_from")
DEFAULT_YEAR_TO_CONFIG: int | None = _get_search("year_to")
DEFAULT_FORMAT_CONFIG: str | None = _get_search("format")
DEFAULT_NO_CACHE_CONFIG: bool | None = _get_search("no_cache")
