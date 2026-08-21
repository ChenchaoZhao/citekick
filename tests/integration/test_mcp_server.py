"""Integration test: call the MCP search_papers tool against the live API."""

from __future__ import annotations

import asyncio
import json

from citekick.mcp_server import mcp


def test_search_papers_tool_queries_live_arxiv_api() -> None:
    content, _ = asyncio.run(
        mcp.call_tool(
            "search_papers", {"query": "Hamiltonian Monte Carlo", "sources": "arxiv", "max_results_per_source": 1}
        )
    )

    payload = json.loads(content[0].text)
    assert payload["query"] == "Hamiltonian Monte Carlo"
    assert payload["result_count"] == 1
    assert payload["papers"][0]["source"] == "arXiv"
