"""User configuration loaded once at import time from ``~/.config/paper-search/config.toml``."""

from __future__ import annotations

import tomllib
from pathlib import Path

CONFIG_DIR: Path = Path.home() / ".config" / "paper-search"
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


_API: dict[str, str | None] = _load()


def _get(key: str) -> str | None:
    value = _API.get(key)
    return value if value else None


MAILTO: str | None = _get("mailto")
OPENALEX_API_KEY: str | None = _get("openalex_api_key")
SEMANTIC_SCHOLAR_API_KEY: str | None = _get("semantic_scholar_api_key")
NCBI_API_KEY: str | None = _get("ncbi_api_key")
