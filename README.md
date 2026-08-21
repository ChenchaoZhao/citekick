# Citekick

Agentic tools for academic paper search MCP and Skills

## Installation

You can install the `citekick` CLI and MCP server globally using `uv`:

```bash
uv tool install citekick
```

## Configuration

Credentials and the optional contact email are read from
`~/.config/citekick/config.toml`. Copy `config.toml.example` to that
location and replace the placeholder values. The `[api]` values are optional;
missing or empty values leave the corresponding source keyless.

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
