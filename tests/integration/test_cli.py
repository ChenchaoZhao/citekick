"""Integration test: run the citekick CLI end-to-end against the live API."""

from __future__ import annotations

import json

from citekick import cli


def test_cli_searches_live_arxiv_api_and_emits_json(capsys) -> None:
    exit_code = cli.main(["Hamiltonian Monte Carlo", "--sources", "arxiv", "--max-results", "1", "--no-cache"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["query"] == "Hamiltonian Monte Carlo"
    assert payload["result_count"] == 1
    assert payload["papers"][0]["source"] == "arXiv"


def test_cli_searches_live_arxiv_api_and_emits_markdown(capsys) -> None:
    exit_code = cli.main(
        ["Hamiltonian Monte Carlo", "--sources", "arxiv", "--max-results", "1", "--no-cache", "--format", "markdown"]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Hamiltonian Monte Carlo" in captured.out
    assert "*arXiv*" in captured.out
