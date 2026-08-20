# Project Design Doc

## Context

This project is refactored from a research project component.

## CLI and MCP server

A literature search tool: query multiple sources, deduplicate and rank results, and emit structured output. This is the first research tool and only one of several planned for the project; it feeds directly into the literature review (ticket 001). Because more sources are expected later, the tool uses the **strategy pattern**: each source is an enum value registered to a concrete search strategy, so adding a source only means adding an enum member and its strategy, with no changes to the CLI or orchestrator.

The search engine must be usable by LLM agents directly, so the core is exposed as a **Model Context Protocol (MCP) server** (stdio transport) with a `search_papers` tool; a thin `paper-search` CLI wraps the same core for scripting and verification.

### Acceptance Criteria

- [ ] A `paper-search` CLI exists, runnable via hatch, that accepts a query string (e.g. `hatch run paper-search "Hamiltonian Monte Carlo"`).
- [ ] The search is exposed as a Model Context Protocol (MCP) server over stdio with a `search_papers` tool that accepts the same query parameters as the CLI, runnable via `hatch run paper-search-mcp`, so LLM agents can query literature directly.
- [ ] The CLI and the MCP server share the same orchestration core; both query multiple literature sources behind a unified interface: Semantic Scholar, arXiv, PubMed, Crossref, Europe PMC, OpenReview, and DBLP (all free, keyless) plus OpenAlex (free account, per-request budget).
- [ ] Sources are modeled as a `Source` enum, one member per source, with each member mapped to its search strategy (strategy pattern); adding a source requires only a new enum member and strategy, not CLI/orchestrator changes.
- [ ] The CLI accepts a comma-separated list of sources (e.g. `--sources semantic-scholar,arxiv,pubmed`); when omitted it defaults to the keyless free sources (all except OpenAlex), and unknown source names fail with an explicit error.
- [ ] Results from across sources are deduplicated (by DOI/title) and ranked by relevance and/or citation count.
- [ ] Paper metadata is normalized to a common record: title, authors, year, DOI, abstract, source, and URL.
- [ ] Output is emitted as structured JSON and as a Markdown reference list, with configurable limits (max results per source, year range).
- [ ] [Edge Case] Source failures or rate limits are handled with retry/backoff and logging; the remaining sources continue and the run does not crash.
- [ ] [Edge Case] A query with zero results returns an explicit empty-result message rather than failing silently.
- [ ] Per-source API keys are configurable through the user TOML file `~/.config/paper-search/config.toml`, with no new CLI or MCP arguments: OpenAlex sends `api_key=` as a query param on `works` calls, Semantic Scholar sends `x-api-key` (case-sensitive) as a request header, and PubMed sends `api_key=` on both the `esearch` and `esummary` calls.
- [ ] Every key is optional: a missing or empty key never fails a search — the source runs keyless exactly as before.
- [ ] The optional `mailto` value in `~/.config/paper-search/config.toml` keeps working for arXiv (`user=`) and Crossref (`mailto=`); the retired OpenAlex `mailto` polite pool is not wired.
- [ ] [Edge Case] Keys are read once at import time and never logged or serialized — not in cache payloads, debug output, or `SourceResult.error` messages.
- [ ] A `config.toml.example` file at the repo root documents the user config schema with placeholder values and no real secrets.

### Technical Notes and Implementation Hints

- Core Files: `src/paper_search/config.py` (user TOML loading and import-time constants), `src/paper_search/__main__.py` (orchestrator), `src/paper_search/models.py` (Paper record), `src/paper_search/sources.py` (Source enum + strategy registry), `src/paper_search/sources/` (one strategy module per source: `semantic_scholar.py`, `arxiv.py`, `pubmed.py`, `openalex.py`, `crossref.py`, `europepmc.py`, `openreview.py`, `dblp.py`), `src/paper_search/output.py` (JSON + Markdown rendering), `src/paper_search/mcp_server.py` (FastMCP `search_papers` tool), `src/paper_search/cli.py`
- Tests should include unit tests (fast interface tests with mocks) and integration tests (make real api calls)
- Dependencies: `mcp` (MCP server framework), `httpx` (async HTTP client), `tenacity` (retry/backoff). The `paper-search` and `paper-search-mcp` entry points are defined in `pyproject.toml` `[project.scripts]` and exposed as `hatch run` scripts.
- API / Database Schema impact: N/A — external REST APIs only; see the Appendix for the full surveyed list of candidate APIs and their access models.
- Security/Performance considerations: Respect each source's rate limits (arXiv requires a `mailto` parameter; NCBI E-utilities ~3 req/s without an API key; Crossref "polite pool" via `mailto=`; OpenAlex has a per-day request budget). Cache responses to disk to avoid re-fetching identical queries. Keep CLI options minimal and document them in the README.
- API keys: Load the user TOML file `~/.config/paper-search/config.toml` once at import time with the standard-library `tomllib`. The file uses an `[api]` table with `mailto`, `openalex_api_key`, `semantic_scholar_api_key`, and `ncbi_api_key` string values. Missing files, tables, or values resolve to `None`; empty values are treated as missing. Source modules may expose import-time constants co-located with their request logic, populated by `config.py`: `OPENALEX_API_KEY` (OpenAlex `api_key` query param), `SEMANTIC_SCHOLAR_API_KEY` (Semantic Scholar `x-api-key` request header), and `NCBI_API_KEY` (NCBI `api_key` param on both E-utility calls). Semantic Scholar is the only source needing a header, so thread an optional `headers` kwarg through `_get`/`fetch_json`/`fetch_text`; the cache key stays URL + params only (the response is identical regardless of key). Document the config path and schema in the README, and note that OpenAlex retired its `mailto` polite pool in Feb 2026 and now effectively requires an API key (no key = ~100 free credits/day, then `429`/`409`).
- Example config file: Add `config.toml.example` at the repo root with placeholder values and no real secrets. Users copy it to `~/.config/paper-search/config.toml`; the real user config must never be committed.
- Design: Implement the strategy pattern via a `Source` enum whose members carry the concrete search strategy (e.g. via a `search(query) -> list[Paper]` protocol/ABC). The orchestrator iterates only over the requested sources, keeping CLI, MCP server, and orchestration logic decoupled from source specifics. Only free or nearly-free sources are added to the enum; paid/subscription APIs are tracked in the Appendix but excluded.
