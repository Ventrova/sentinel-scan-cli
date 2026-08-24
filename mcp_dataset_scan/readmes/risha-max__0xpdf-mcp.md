# 0xPdf MCP

[![PyPI](https://img.shields.io/pypi/v/oxpdf-mcp)](https://pypi.org/project/oxpdf-mcp/)
[![MCP](https://img.shields.io/badge/MCP-stdio-blue)](https://modelcontextprotocol.io/)

**Schema in → PDF in → JSON out** for Claude, Cursor, and other MCP clients.

This stdio MCP server wraps the [0xPdf](https://0xpdf.io) HTTP API (auth, billing, rate limits intact). Agents can parse invoices/forms into a JSON schema, generate schemas, and poll async jobs.

![0xPdf — schema in, PDF in, JSON out](https://0xpdf.io/media/social-promo.gif)

[Playground](https://0xpdf.io/samples?utm_source=github&utm_medium=readme&utm_campaign=0xpdf-mcp) · [Docs / MCP setup](https://0xpdf.io/docs#mcp) · [Pricing](https://0xpdf.io/pricing)

## Install

```bash
pip install oxpdf-mcp
# or
uvx oxpdf-mcp
```

Get an API key at [0xpdf.io/dashboard](https://0xpdf.io/dashboard).

## Cursor / Claude Desktop

```json
{
  "mcpServers": {
    "0xpdf": {
      "command": "uvx",
      "args": ["oxpdf-mcp"],
      "env": {
        "PDF_PARSING_API_BASE_URL": "https://api.0xpdf.io",
        "PDF_PARSING_API_PREFIX": "api/v1",
        "PDF_PARSING_API_KEY": "YOUR_API_KEY",
        "PDF_PARSING_ALLOWED_API_HOSTS": "api.0xpdf.io",
        "PDF_PARSING_REQUIRE_HTTPS": "true",
        "PDF_PARSING_ALLOWED_FILE_ROOTS": "/home/YOU/Downloads:/home/YOU/Documents",
        "PDF_PARSING_MCP_DISALLOW_FULL_RESPONSE_MODE": "true"
      }
    }
  }
}
```

Or with pip:

```json
"command": "oxpdf-mcp"
```

## Tools (selected)

| Tool | Purpose |
|------|---------|
| `parse_pdf_sync` | Schema-first sync parse |
| `parse_pdf_stream` | Streaming parse (SSE) |
| `submit_parse_job` / `wait_for_job_completion` | Async jobs |
| `list_schemas` / `create_schema` | Saved schemas |
| `generate_schema_from_description` | AI schema generation (wallet debit) |
| `get_pricing_current` | Balance / pricing |
| `health_check` | Liveness |

Full list and env vars: see source `oxpdf_mcp/server.py` and [docs](https://0xpdf.io/docs#mcp).

## Env

| Variable | Default | Notes |
|----------|---------|--------|
| `PDF_PARSING_API_KEY` | — | Required for authenticated tools |
| `PDF_PARSING_API_BASE_URL` | `https://api.0xpdf.io` | Production API |
| `PDF_PARSING_ALLOWED_API_HOSTS` | — | Required in production (`api.0xpdf.io`) |
| `PDF_PARSING_REQUIRE_HTTPS` | `false` | Set `true` for production |
| `PDF_PARSING_ALLOWED_FILE_ROOTS` | CWD | Colon-separated absolute paths for `pdf_path` |

## SDKs (non-MCP)

- Python: [`oxpdf`](https://pypi.org/project/oxpdf/)
- JS/TS: [`@0xpdf/client`](https://www.npmjs.com/package/@0xpdf/client)

## License

MIT
