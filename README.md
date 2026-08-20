# paper-search

Agentic tools for academic paper search MCP and Skills

## Installation

You can install the `paper-search` CLI and MCP server globally using `uv`:

```bash
uv tool install paper-search
```

## Configuration

Credentials and the optional contact email are read from
`~/.config/paper-search/config.toml`. Copy `config.toml.example` to that
location and replace the placeholder values. The `[api]` values are optional;
missing or empty values leave the corresponding source keyless.

## Agent Integration

To use `paper-search` as an MCP server, add this to your agent's MCP config:

```json
{
  "mcpServers": {
    "paper-search": {
      "command": "paper-search-mcp"
    }
  }
}
```

Or using `uvx` (without prior installation):

```json
{
  "mcpServers": {
    "paper-search": {
      "command": "uvx",
      "args": ["--from", "paper-search", "paper-search-mcp"]
    }
  }
}
```

## Usage

OpenAlex retired its `mailto` polite pool in February 2026. Without an
OpenAlex key, the service provides roughly 100 free credits per day before
returning `429` or `409` responses.
