"""Tests for the paper-search CLI."""

from __future__ import annotations

import io
import json
import sys
from typing import Any

from paper_search import cli
from paper_search.paper import Paper
from paper_search.search import SearchResult, SourceResult
from paper_search.sources import Source


def _run_cli(argv: list[str], monkeypatch: Any) -> tuple[int, str, str]:
    captured: dict[str, str] = {}

    async def fake_search_papers(query: str, **_kwargs: Any) -> SearchResult:
        paper = Paper(
            title=f"Result for {query}", source="arXiv", year=2023, doi="10.1/x", url="http://arxiv.org/abs/x"
        )
        return SearchResult(
            query=query,
            papers=[paper],
            per_source=[SourceResult(source=Source.ARXIV, papers=[paper])],
            total_fetched=1,
        )

    monkeypatch.setattr(cli, "search_papers", fake_search_papers)

    stdout = io.StringIO()
    stderr = io.StringIO()
    monkeypatch.setattr(sys, "stdout", stdout)
    monkeypatch.setattr(sys, "stderr", stderr)
    exit_code = cli.main(argv)
    captured["stdout"] = stdout.getvalue()
    captured["stderr"] = stderr.getvalue()
    return exit_code, captured["stdout"], captured["stderr"]


def test_cli_unknown_source_exits_with_error(monkeypatch: Any) -> None:
    exit_code, _, stderr = _run_cli(["query", "--sources", "arxiv,fake"], monkeypatch)

    assert exit_code == 2
    assert "'fake' is not a valid Source" in stderr


def test_cli_empty_source_list_exits_with_error(monkeypatch: Any) -> None:
    exit_code, _, stderr = _run_cli(["query", "--sources", ""], monkeypatch)

    assert exit_code == 2
    assert "at least one source" in stderr


def test_cli_invalid_max_results_exits_with_error(monkeypatch: Any) -> None:
    exit_code, _, stderr = _run_cli(["query", "--max-results", "0"], monkeypatch)

    assert exit_code == 2
    assert "--max-results" in stderr


def test_cli_json_format_emits_structured_output(monkeypatch: Any) -> None:
    exit_code, stdout, _ = _run_cli(["protein design"], monkeypatch)

    assert exit_code == 0
    payload = json.loads(stdout)
    assert payload["query"] == "protein design"
    assert payload["papers"][0]["title"] == "Result for protein design"


def test_cli_markdown_format_emits_reference_list(monkeypatch: Any) -> None:
    exit_code, stdout, _ = _run_cli(["protein design", "--format", "markdown"], monkeypatch)

    assert exit_code == 0
    assert "Result for protein design" in stdout
    assert "*arXiv*" in stdout
    assert "1 paper(s)" in stdout


def test_cli_passes_year_range_to_core(monkeypatch: Any) -> None:
    seen: dict[str, Any] = {}

    async def fake_search_papers(query: str, **kwargs: Any) -> SearchResult:
        seen["year_range"] = kwargs["year_range"]
        return SearchResult(query=query)

    monkeypatch.setattr(cli, "search_papers", fake_search_papers)
    monkeypatch.setattr(sys, "stdout", io.StringIO())
    monkeypatch.setattr(sys, "stderr", io.StringIO())
    exit_code = cli.main(["query", "--year-from", "2020", "--year-to", "2024"])

    assert exit_code == 0
    assert seen["year_range"] == (2020, 2024)


def test_cli_help_flag_does_not_prepend_search(monkeypatch: Any) -> None:
    exit_code, _, stderr = _run_cli(["--help"], monkeypatch)

    assert exit_code == 0
    assert "search" in stderr
    assert "config" in stderr
