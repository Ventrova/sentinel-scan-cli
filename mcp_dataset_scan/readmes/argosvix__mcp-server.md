# @argosvix/mcp-server

Argosvix MCP server lets AI agents (Claude Desktop, Cursor, Codex CLI, custom MCP clients) query, manage, and operate their LLM observability data directly from the conversation. Supports both **stdio** (subprocess) and **HTTP** (remote / self-host) transports.

**Surface:** 89 tools (86 generally available + 3 internal operations tools that return 403 for customer accounts) / 3 resources / 8 resource templates / 3 prompts. Health and anomaly endpoints (`get_account_health` / `detect_anomaly` / `propose_alert_rules` / `classify_calls_batch` / `propose_eval_criteria`) plus a runtime control plane (budget gates / policy gates / human-approval gates) let an agent both observe and act. Release history is available on [npm](https://www.npmjs.com/package/@argosvix/mcp-server?activeTab=versions).

[![npm version](https://img.shields.io/npm/v/@argosvix/mcp-server)](https://npmjs.com/package/@argosvix/mcp-server)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Why

You're already sending LLM calls through `@argosvix/sdk` or the Python SDK. Now ask Claude / Cursor questions like:

- "What was my OpenAI cost over the past 24h?"
- "Which alerts are firing right now?"
- "Show me the 20 most expensive calls today."

No dashboard tab-switching. The agent fetches the data via this MCP server using your Argosvix API key.

## Install

**One-click** (starts keyless; set `ARGOSVIX_API_KEY` afterwards to unlock all tools):

[![Add to Cursor](https://img.shields.io/badge/Cursor-Add_MCP_server-000000?logo=cursor)](cursor://anysphere.cursor-deeplink/mcp/install?name=argosvix&config=eyJjb21tYW5kIjoibnB4IiwiYXJncyI6WyIteSIsIkBhcmdvc3ZpeC9tY3Atc2VydmVyIl19)
[![Install in VS Code](https://img.shields.io/badge/VS_Code-Install_MCP_server-0098FF?logo=githubcopilot)](https://insiders.vscode.dev/redirect/mcp/install?name=argosvix&config=%7B%22command%22%3A%22npx%22%2C%22args%22%3A%5B%22-y%22%2C%22%40argosvix%2Fmcp-server%22%5D%7D)

Claude Code users can install the [argosvix plugin](https://github.com/argosvix/claude-plugin) instead — it bundles this server plus setup skills:

```
/plugin marketplace add argosvix/claude-plugin
/plugin install argosvix@argosvix
```

**Manual:**

```bash
npm install -g @argosvix/mcp-server
```

## Configure (Claude Desktop)

Edit your Claude Desktop config:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "argosvix": {
      "command": "argosvix-mcp",
      "env": {
        "ARGOSVIX_API_KEY": "argk_..."
      }
    }
  }
}
```

Restart Claude Desktop. All 89 tools appear under the `argosvix__` prefix (e.g. `argosvix__query_calls`, `argosvix__get_account_health`, `argosvix__create_budget_gate`).

> **No API key yet?** The server also starts without `ARGOSVIX_API_KEY` in introspection-only mode: all 89 tools are listed so you can evaluate the surface, and two public data tools (`get_synth_daily` / `get_daily_readthrough` — Argosvix's own daily AI digest and OSS readthrough) work with no key at all. Every other tool call returns instructions for getting a key at https://dashboard.argosvix.com/api-keys.
>
> Notes on the public data tools: they are part of the default `full` profile only (not in `ARGOSVIX_MCP_PROFILE=core`), and like every other tool they honor `ARGOSVIX_API_BASE` — if you point the server at a different base, they fetch `/v1/synth-daily` / `/v1/readthrough` from that base without authentication.

## Configure (Cursor)

Edit `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "argosvix": {
      "command": "argosvix-mcp",
      "env": {
        "ARGOSVIX_API_KEY": "argk_..."
      }
    }
  }
}
```

## Tool profile (`ARGOSVIX_MCP_PROFILE`)

The default profile is `full` (all 89 tools). If your MCP client's context budget is tight, set `ARGOSVIX_MCP_PROFILE=core` to expose only the 11 essentials for day-to-day operations:

`query_calls` · `aggregate_calls` · `get_cost_summary` · `get_percentiles` · `get_account_health` · `detect_anomaly` · `list_alerts` · `create_alert` · `silence_alert` · `unsilence_alert` · `get_deployed_prompt`

```json
{
  "mcpServers": {
    "argosvix": {
      "command": "argosvix-mcp",
      "env": {
        "ARGOSVIX_API_KEY": "argk_...",
        "ARGOSVIX_MCP_PROFILE": "core"
      }
    }
  }
}
```

Works in both stdio and HTTP transports. Unknown values fall back to `full` with a warning on stderr.

## Description language (`ARGOSVIX_MCP_LANG`)

Tool, resource, and prompt descriptions returned by `tools/list` / `resources/list` /
`prompts/list` are in English by default. Set `ARGOSVIX_MCP_LANG=ja` to get the original
Japanese descriptions instead. Unset or unknown values fall back to `en` (with a warning
on stderr for unknown values). Tool names, input schemas, and behavior are identical in
both languages — only the human/agent-facing description text changes.

```json
{
  "mcpServers": {
    "argosvix": {
      "command": "argosvix-mcp",
      "env": {
        "ARGOSVIX_API_KEY": "argk_...",
        "ARGOSVIX_MCP_LANG": "ja"
      }
    }
  }
}
```

Works in both stdio and HTTP transports.

## Tools (highlights)

89 tools in total — the full list is returned by `tools/list`. A sample of the core read / write surface:

| Tool | Purpose | Type |
|---|---|---|
| `query_calls` | Recent LLM call records, filterable by provider / model / time range | read |
| `get_cost_summary` | Aggregate cost / calls / tokens by provider or model | read |
| `list_alerts` | Configured alerts + recent trigger status | read |
| `get_alert` | Detail of a specific alert + recent trigger history | read |
| `list_alert_events` | Alert trigger events across the account (notification history) | read |
| `silence_alert` | Mute a specific alert (= temporary notification stop, default 24h) | write |
| `unsilence_alert` | Resume notifications for a previously muted alert | write |
| `create_alert` | Create a new alert rule (cost / error rate / latency / anomaly) | write |
| `acknowledge_alert` | Mark a specific alert event as acknowledged (idempotent, orthogonal to silence) | write |

### Resources

Resources expose read-only snapshots that AI agents can pull into context without an explicit tool call.

| URI | Purpose |
|---|---|
| `argosvix://account` | Plan / quota / current-month record usage / retention snapshot (non-sensitive, Bearer-only) |
| `argosvix://alerts/active` | Snapshot of currently enabled alerts |
| `argosvix://cost/today` | Last-24h cost breakdown by provider (with `response.total`) |

### Resource templates

Resource templates let agents construct dynamic URIs from a known id. The server enforces account scope via PK lookup on the backend, so cross-account ids return 404.

| URI template | Purpose |
|---|---|
| `argosvix://calls/{id}` | Single LLM call record (provider / model / tokens / cost / latency / tags / error / trace_id). Plug in any id from `query_calls` results. |
| `argosvix://alerts/{id}` | Single alert rule (name / type / threshold / window / channelKinds / sleep / enabled / silencedUntil) + recent 20 trigger events. Plug in any id from `list_alerts` results. `channelTargets` (notification destinations) is structurally dropped. |
| `argosvix://traces/{id}` | Single trace = all spans grouped by `trace_id` (LLM call time-series). Top 50 spans only (LLM context budget cap); `errorDetails` / `requestMeta` are structurally dropped. Plug in any `traceId` from `query_calls` results. |

### Prompts

Prompts are reusable templates the user can launch as slash commands.

| Name | Purpose |
|---|---|
| `cost_review` | Compare 24h / 7d / 30d cost trends and flag anomalies |
| `alert_audit` | Audit current alert rules and propose improvements |
| `incident_triage` | Investigate recent error / latency anomalies (default last 24h) |

## Subscriptions (= v0.10, stdio only)

`resources.subscribe` capability is declared in stdio mode. Clients can subscribe to one or more of the static resources below; the server polls each subscribed resource every 60 seconds and emits `notifications/resources/updated` when the content hash changes.

Subscribable URIs (resource templates such as `argosvix://calls/{id}` are **not** subscribable):

- `argosvix://account`
- `argosvix://alerts/active`
- `argosvix://cost/today`

HTTP transport (= `argosvix-mcp --http`) does not declare `subscribe` and rejects subscribe requests, since per-request stateless mode cannot keep a subscription set or deliver server-initiated notifications. Use stdio for live updates.

`listChanged` is intentionally not declared: the resource list is fixed for the server lifetime.

Implementation notes (v0.10):
- Single-flight guard: a slow polling cycle does not start a concurrent next cycle (= no overlapping `readResource` calls).
- Unsubscribe / shutdown race: per-URI re-check before fetch and before notify, plus an `isShuttingDown` flag, so notifications are not emitted for URIs removed mid-cycle.
- Failure handling: fetch and notify failures are silent (next cycle retries). With `ARGOSVIX_MCP_DEBUG=1` the server logs `{ uri, errorClass }` to stderr — error messages are intentionally **not** logged to avoid leaking upstream payload text.
- Tests: 150 unit tests (incl. overlap single-flight + unsubscribe / shutdown race + invalid URI → `McpError(InvalidParams)` + axis 4 Tier 1 dispatcher coverage).

## Privacy

The MCP server sends queries to `https://ingest.argosvix.com` using your API key. **No prompts or completions are exposed** — only metadata (tokens, cost, latency, model name, your tags).

## Development

```bash
npm install
npm run build
npm test
```

## License

MIT © Yuto Makihara (Argosvix). See [LICENSE](LICENSE).

## HTTP transport

The server can also run as a remote MCP endpoint over HTTP, suitable for
self-hosting or multi-tenant scenarios where API key is supplied per request.

```bash
# Start HTTP transport (default: 127.0.0.1:3000)
argosvix-mcp --http

# Bind to all interfaces with custom port + allowed Host headers
MCP_HTTP_HOST=0.0.0.0 \
MCP_HTTP_PORT=4000 \
MCP_HTTP_ALLOWED_HOSTS="mcp.example.com,localhost:4000" \
  argosvix-mcp --http
```

### Endpoints

- `GET /health` → `200 OK` with server name/version (no auth)
- `POST /mcp` → MCP JSON-RPC endpoint (auth required)

### Client example

```bash
curl -X POST http://localhost:3000/mcp \
  -H "Authorization: Bearer argk_..." \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
  }'
```

### Auth model

Each request must include `Authorization: Bearer <api-key>` with a valid
Argosvix API key (issue at https://dashboard.argosvix.com/api-keys). The
server uses stateless mode (no session ID), so each request is independent
and may carry a different key.

### Security notes

- Default bind is `127.0.0.1` (localhost only). Use `MCP_HTTP_HOST=0.0.0.0`
  to expose externally, but pair with a reverse proxy + TLS in production.
- DNS rebinding protection is applied for localhost binds by checking the
  `Host` header against a known-localhost allow list. Use
  `MCP_HTTP_ALLOWED_HOSTS` (comma-separated) when binding non-locally.
- Body size is capped at 1 MiB.

### Debug logging

Backend error response bodies are **not** logged by default to keep production log
aggregators free of backend-internal payloads. To enable raw body logging for a
debugging session:

```bash
ARGOSVIX_MCP_DEBUG=1 argosvix-mcp           # stdio mode
ARGOSVIX_MCP_DEBUG=1 argosvix-mcp --http    # HTTP mode
```

Without the env var, error logs only include `path`, `status`, and `x-request-id`.
