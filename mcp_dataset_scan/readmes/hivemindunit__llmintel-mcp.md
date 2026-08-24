# @llmintel/mcp

An [MCP](https://modelcontextprotocol.io) server that tells your coding agent whether a model id is
safe to use.

LLMs are trained on a snapshot of the world and will confidently write `gpt-4-32k` into your code
long after it stops answering. This server gives the agent a live lookup for whether a model is
deprecated and when it stops working. It returns the replacement too. Answers are normalized across
OpenAI, Anthropic, Azure AI Foundry, AWS Bedrock, Google, and Cohere, and parsed from each
provider's own deprecation pages.

No API key, no signup. The catalog is public.

[![Add to Cursor](https://cursor.com/deeplink/mcp-install-dark.svg)](https://cursor.com/en/install-mcp?name=llmintel&config=eyJjb21tYW5kIjoibnB4IiwiYXJncyI6WyIteSIsIkBsbG1pbnRlbC9tY3AiXX0%3D)
[![Install in VS Code](https://img.shields.io/badge/VS_Code-Install_Server-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect?url=vscode%3Amcp%2Finstall%3F%257B%2522name%2522%253A%2522llmintel%2522%252C%2522command%2522%253A%2522npx%2522%252C%2522args%2522%253A%255B%2522-y%2522%252C%2522%2540llmintel%252Fmcp%2522%255D%257D)

## Install

Add it to any MCP host. The package runs straight from npm via `npx`.

### Cursor

In `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "llmintel": {
      "command": "npx",
      "args": ["-y", "@llmintel/mcp"]
    }
  }
}
```

### Claude Code

```bash
claude mcp add llmintel -- npx -y @llmintel/mcp
```

### Claude Desktop

Same shape as the Cursor block above, in `claude_desktop_config.json`.

### Hosted endpoint (no install)

The same five tools are served over Streamable HTTP at `https://llmintel.ai/v1/mcp`. Hosts that take
a URL need no Node and no package:

```json
{
  "mcpServers": {
    "llmintel": {
      "url": "https://llmintel.ai/v1/mcp"
    }
  }
}
```

The endpoint is stateless and read-only. It answers from the same catalog the npm package queries.

## Tools

| Tool | Returns |
| --- | --- |
| `check_model` | Whether one model id is safe to use: lifecycle state, the retirement deadline in days, the replacement, and the source link. |
| `list_retiring_models` | What breaks in the next 90 days. Past-due models are listed first, then upcoming ones soonest-first. |
| `suggest_replacement` | The provider's own recommendation for what to move to. Falls back to same-provider active models when none was published. |
| `search_models` | Catalog search filtered by provider and lifecycle state. |
| `recent_lifecycle_changes` | The change feed across all providers, for questions like "what was deprecated this month". |

### Example

> **You:** Before we ship this, check the model ids in `src/agents/`.

The agent calls `check_model` for each one and gets back:

```
DO NOT USE — this model is retired; API calls to it fail.

"claude-sonnet-4-20250514" resolves to the tracked model anthropic/claude-sonnet-4-20250514.
Model: claude-sonnet-4-20250514 (anthropic/claude-sonnet-4-20250514)
Provider: anthropic
Lifecycle state: retired — retired; calls fail
Deprecated: 2026-04-14 (105 days ago)
Retirement: 2026-06-15 (43 days ago)

The provider has not named a replacement. Use suggest_replacement for options.
Pricing/limits: $3/1M in · $15/1M out

Source: https://docs.anthropic.com/en/docs/about-claude/model-deprecations
Provider's own term: "Retired"
```

Deadlines are always given in days, because a model cannot reliably judge whether `2026-07-30` is
soon.

## Design notes

A failed lookup is never a safety verdict. If the catalog is unreachable, the tool returns an MCP
error and says so. An agent that read a network failure as "no deprecation found" would happily ship
a retired model id. A model that simply isn't tracked gets the same treatment: it returns "not in the
catalog, verify with the provider", never "OK".

Pass whatever string is literally in the code (`gpt-4o`, `anthropic/claude-opus-4-1`, `azure/gpt-4o`)
and it resolves to the canonical tracked model.

When the provider's own deprecation notice names a successor, that is what you get. Otherwise the
fallback list of same-provider active models is labelled as candidates to evaluate, so an agent can
tell the two apart.

Anything past its retirement date is broken now, so it gets its own heading instead of sitting in
"retiring soon".

## Configuration

Both variables are optional.

| Variable | Default | Purpose |
| --- | --- | --- |
| `LLMINTEL_API_KEY` | none | Raises the rate-limit budget. The catalog itself is public, so you do not need this. |
| `LLMINTEL_BASE_URL` | `https://llmintel.ai` | Point at a self-hosted or staging catalog. |

Anonymous callers get 30 requests/minute per IP, enough for interactive agent use.

## Data provenance

Every record links to the provider page it was parsed from and preserves the provider's verbatim
lifecycle term (`sourceTerm`), so a normalization decision is always auditable. Changes go through a
human verification queue before publication. Collector freshness is public at
[`/v1/status`](https://llmintel.ai/v1/status).

The same data is available as a plain REST API, also without a key. See
[llmintel.ai/docs](https://llmintel.ai/docs).

## Development

```bash
pnpm --filter @llmintel/mcp build
pnpm exec vitest run packages/mcp        # protocol-level tests against a fake catalog

# Drive the built binary against a live catalog
pnpm --filter @llmintel/mcp smoke
LLMINTEL_BASE_URL=http://localhost:3000 pnpm --filter @llmintel/mcp smoke
```

## License

MIT © LLMIntel
