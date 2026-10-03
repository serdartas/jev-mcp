# Obasoft Jev MCP

Shared MCP server exposing TypeSafe Jev / System One to Obasoft agents.

## Tools

- `system_one`: submit one or more `choice`, `noul`, and/or `score` questions.
- `list_models`: list currently available TypeSafe models and aliases.

The server uses the official `typesafe-sdk` Python package and reads
`TYPESAFE_API_KEY` from its process environment.

## Local setup

```bash
uv sync --dev
uv run pytest
```

For MCP Inspector development:

```bash
TYPESAFE_API_KEY=... uv run mcp dev src/obasoft_jev_mcp/server.py
```

For normal stdio execution:

```bash
.venv/bin/obasoft-jev-mcp
```

Do not commit API keys or `.env` files.
