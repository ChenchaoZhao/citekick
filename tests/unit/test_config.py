"""Unit tests for config.py: TOML loading from ~/.config/citekick/config.toml."""

from __future__ import annotations

from typing import TYPE_CHECKING

import citekick.config as config_module
from citekick.config import _get, _load

if TYPE_CHECKING:
    from pathlib import Path


def _api(path: Path) -> dict[str, str | None]:
    return _load(path)


def test_loads_mailto_from_toml(tmp_path) -> None:
    config_file = tmp_path / "config.toml"
    config_file.write_text('[api]\nmailto = "user@example.com"\n')

    assert _api(config_file)["mailto"] == "user@example.com"


def test_loads_api_keys_from_toml(tmp_path) -> None:
    config_file = tmp_path / "config.toml"
    config_file.write_text(
        '[api]\nopenalex_api_key = "oa-key"\nsemantic_scholar_api_key = "ss-key"\nncbi_api_key = "ncbi-key"\n'
    )
    api = _api(config_file)

    assert api["openalex_api_key"] == "oa-key"
    assert api["semantic_scholar_api_key"] == "ss-key"
    assert api["ncbi_api_key"] == "ncbi-key"


def test_missing_file_returns_empty(tmp_path) -> None:
    assert _api(tmp_path / "nonexistent.toml") == {}


def test_empty_string_treated_as_missing(tmp_path, monkeypatch) -> None:
    config_file = tmp_path / "config.toml"
    config_file.write_text('[api]\nmailto = ""\n')
    monkeypatch.setattr(config_module, "_API", _api(config_file))

    assert _get("mailto") is None


def test_missing_table_returns_empty(tmp_path) -> None:
    config_file = tmp_path / "config.toml"
    config_file.write_text("[other]\nkey = 'value'\n")

    assert _api(config_file) == {}


def test_missing_key_returns_none(tmp_path) -> None:
    config_file = tmp_path / "config.toml"
    config_file.write_text("[api]\n")
    api = _api(config_file)

    assert api.get("mailto") is None


def test_loads_search_config_from_toml(tmp_path) -> None:
    config_file = tmp_path / "config.toml"
    config_file.write_text(
        '[search]\nsources = "arxiv,pubmed"\nmax_results = 5\nyear_from = 2019\nyear_to = 2023\nformat = "markdown"\nno_cache = true\n'
    )
    search = config_module._load_search(config_file)  # noqa: SLF001
    assert search["sources"] == "arxiv,pubmed"
    assert search["max_results"] == 5
    assert search["year_from"] == 2019
    assert search["year_to"] == 2023
    assert search["format"] == "markdown"
    assert search["no_cache"] is True
