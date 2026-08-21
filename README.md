# citekick

[![CI](https://github.com/ChenchaoZhao/citekick/actions/workflows/ci.yml/badge.svg)](https://github.com/ChenchaoZhao/citekick/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/citekick?cacheSeconds=120)](https://pypi.org/project/citekick/)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Agentic tools for academic paper search — a CLI and MCP server that query multiple literature sources in one shot.

---

## Why `citekick`?

Finding papers usually means juggling separate APIs, rate limits, and response formats for every source. `citekick` unifies them behind a single interface:

- **Multi-source search** — Query 8 sources in parallel: Semantic Scholar, arXiv, PubMed, Crossref, Europe PMC, OpenReview, DBLP, and OpenAlex.
- **CLI + MCP** — Use it directly from your terminal (`citekick`) or expose it to AI agents as an MCP server (`citekick-mcp`).
- **Agent-friendly output** — JSON or Markdown results, ready to be consumed by humans or LLMs.
- **Response caching** — Built-in HTTP cache to stay polite with APIs and speed up repeated queries.
- **Configurable defaults** — API keys, preferred sources, year ranges, and output format persisted in one TOML file.

---

## Installation

Install the `citekick` CLI and MCP server globally using `uv`:

```bash
# Install with uv (recommended)
uv tool install citekick

# Or with pip
pip install citekick
```

---

## CLI Usage

### 1. `citekick search`

Search academic literature across multiple sources.

```bash
citekick search "attention is all you need"                    # Search all default sources
citekick search "diffusion models" --sources arxiv,openalex    # Restrict to specific sources
citekick search "protein folding" --year-from 2023 --format markdown
citekick search "llm agents" --max-results 20 --no-cache
```

> Tip: the `search` subcommand is optional — `citekick "query"` works too.

### 2. `citekick config`

Configure API keys and default search settings in `~/.config/citekick/config.toml`.

```bash
citekick config                                    # Create an empty config file
citekick config --mailto you@example.com           # Set contact email (polite-pool access)
citekick config --openalex-api-key KEY --sources arxiv,pubmed
```

Credentials and optional contact email are read from `~/.config/citekick/config.toml`. The `[api]` values are all optional; missing or empty values leave the corresponding source keyless.

---

## Agent Integration

To use `citekick` as an MCP server, add this to your agent's MCP config:

```json
{
  "mcpServers": {
    "citekick": {
      "command": "citekick-mcp"
    }
  }
}
```

Or using `uvx` (without prior installation):

```json
{
  "mcpServers": {
    "citekick": {
      "command": "uvx",
      "args": ["--from", "citekick", "citekick-mcp"]
    }
  }
}
```

---

## Development

```bash
# Install hatch
uv tool install hatch

# Run full release check (linting, static typing with mypy, and test suite with coverage)
hatch run release
```

---

## License

MIT
