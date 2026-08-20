# paper-search

Agentic tools for academic paper search MCP and Skills

## Configuration

Credentials and the optional contact email are read from
`~/.config/paper-search/config.toml`. Copy `config.toml.example` to that
location and replace the placeholder values. The `[api]` values are optional;
missing or empty values leave the corresponding source keyless.

OpenAlex retired its `mailto` polite pool in February 2026. Without an
OpenAlex key, the service provides roughly 100 free credits per day before
returning `429` or `409` responses.
