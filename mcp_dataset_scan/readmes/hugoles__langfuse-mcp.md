# langfuse-mcp

[![npm version](https://img.shields.io/npm/v/langfuse-mcp.svg)](https://www.npmjs.com/package/langfuse-mcp)
[![npm downloads](https://img.shields.io/npm/dm/langfuse-mcp.svg)](https://www.npmjs.com/package/langfuse-mcp)
[![CI](https://github.com/hugoles/langfuse-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/hugoles/langfuse-mcp/actions/workflows/ci.yml)
[![Node](https://img.shields.io/node/v/langfuse-mcp.svg)](https://nodejs.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

An [MCP](https://modelcontextprotocol.io) server that exposes the [Langfuse](https://langfuse.com) REST API as tools, so Claude (or any MCP client) can query your traces, observations, sessions, scores, prompts, datasets, and metrics during a conversation.

Useful when you want to ask things like:

- _"Why did trace `abc123` fail? Walk me through its observations."_
- _"List the 5 most recent traces with `level=ERROR` for user `alice@x.com`."_
- _"Summarize today's generation cost broken down by model."_
- _"Show me the production version of prompt `customer-support-v2`."_

…without leaving your assistant.

## Requirements

- **Node.js 20 or newer** (`node --version`).
- A Langfuse project with API keys ([cloud.langfuse.com → Settings → API Keys](https://cloud.langfuse.com/project/settings) on EU cloud, [us.cloud.langfuse.com](https://us.cloud.langfuse.com) on US cloud, or your self-hosted instance).

## Tools

All tools are read-only and call the [Langfuse Public API](https://api.reference.langfuse.com) over HTTPS using your project keys for Basic Auth.

### Traces & observations

| Tool               | Description                                                     |
| ------------------ | --------------------------------------------------------------- |
| `listTraces`       | List traces with filters. Returns summary metadata.             |
| `getTrace`         | Fetch a single trace by id including the full observation tree. |
| `listObservations` | List spans, generations, and events with filters.               |
| `getObservation`   | Fetch a single observation by id.                               |

### Sessions

| Tool           | Description                                  |
| -------------- | -------------------------------------------- |
| `listSessions` | List sessions within a time range.           |
| `getSession`   | Fetch a session by id, including its traces. |

### Scores

| Tool               | Description                                                  |
| ------------------ | ------------------------------------------------------------ |
| `listScores`       | List scores with filters.                                    |
| `getScore`         | Fetch a single score by id.                                  |
| `listScoreConfigs` | List score configurations (definitions, ranges, categories). |
| `getScoreConfig`   | Fetch a score configuration by id.                           |

### Prompts

| Tool          | Description                                                               |
| ------------- | ------------------------------------------------------------------------- |
| `listPrompts` | List prompt definitions, optionally filtered by name, label, or tag.      |
| `getPrompt`   | Fetch a prompt by name, optionally pinned to a specific version or label. |

### Datasets

| Tool               | Description                                                   |
| ------------------ | ------------------------------------------------------------- |
| `listDatasets`     | List datasets configured in Langfuse.                         |
| `getDataset`       | Fetch a dataset by name.                                      |
| `listDatasetItems` | List items in a dataset (inputs, expected outputs, metadata). |
| `getDatasetItem`   | Fetch a single dataset item by id.                            |
| `listDatasetRuns`  | List evaluation runs for a dataset.                           |
| `getDatasetRun`    | Fetch a specific dataset run by name.                         |

### Metrics, models & misc

| Tool              | Description                                                                                |
| ----------------- | ------------------------------------------------------------------------------------------ |
| `getMetrics`      | Run a custom metrics query (counts, latency, cost, token usage). Pass a JSON query string. |
| `getDailyMetrics` | Daily aggregated usage / cost / count metrics.                                             |
| `listModels`      | List models known to Langfuse (for cost / token attribution).                              |
| `getModel`        | Fetch a model definition by id.                                                            |
| `listProjects`    | List projects accessible to the current API key.                                           |
| `listComments`    | List comments attached to traces, observations, sessions, or prompts.                      |
| `getComment`      | Fetch a single comment by id.                                                              |
| `getMedia`        | Fetch metadata for a media attachment (image, audio, file).                                |
| `getHealth`       | Ping the Langfuse public health endpoint — useful for credential validation.               |

## Install

Zero install with `npx`:

```bash
npx -y langfuse-mcp
```

Or install globally:

```bash
npm i -g langfuse-mcp
langfuse-mcp --version
```

## Configuration

The server reads three environment variables:

| Variable              | Required | Description                                                                                             |
| --------------------- | -------- | ------------------------------------------------------------------------------------------------------- |
| `LANGFUSE_PUBLIC_KEY` | yes      | Project public key (`pk-lf-…`).                                                                         |
| `LANGFUSE_SECRET_KEY` | yes      | Project secret key (`sk-lf-…`).                                                                         |
| `LANGFUSE_BASE_URL`   | yes      | e.g. `https://cloud.langfuse.com` (EU) or `https://us.cloud.langfuse.com` (US) or your self-hosted URL. |
| `LANGFUSE_ENV_FILE`   | no       | Optional path to a `.env` file to load instead of `./.env`.                                             |

> **Where do I get my keys?** In the Langfuse UI: **Settings → API Keys → Create new API keys**. Keys are scoped to a single project and a single region (EU vs US are separate accounts — match your `LANGFUSE_BASE_URL` to the region you created the keys in).

If a `.env` file exists in the working directory it will be loaded automatically. See [`.env.example`](.env.example) for a starter file.

## Use with Claude Desktop

Edit `claude_desktop_config.json`:

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "langfuse": {
      "command": "npx",
      "args": ["-y", "langfuse-mcp"],
      "env": {
        "LANGFUSE_PUBLIC_KEY": "pk-lf-…",
        "LANGFUSE_SECRET_KEY": "sk-lf-…",
        "LANGFUSE_BASE_URL": "https://cloud.langfuse.com"
      }
    }
  }
}
```

Restart Claude Desktop after editing. The MCP server icon should appear in the chat input.

## Use with Claude Code

Project-level (`./.mcp.json`):

```json
{
  "mcpServers": {
    "langfuse": {
      "command": "npx",
      "args": ["-y", "langfuse-mcp"],
      "env": {
        "LANGFUSE_PUBLIC_KEY": "pk-lf-…",
        "LANGFUSE_SECRET_KEY": "sk-lf-…",
        "LANGFUSE_BASE_URL": "https://cloud.langfuse.com"
      }
    }
  }
}
```

User-level config lives at `~/.claude.json` and uses the same shape.

## Use with Cursor

Project-level: `.cursor/mcp.json`. User-level: `~/.cursor/mcp.json`.

```json
{
  "mcpServers": {
    "langfuse": {
      "command": "npx",
      "args": ["-y", "langfuse-mcp"],
      "env": {
        "LANGFUSE_PUBLIC_KEY": "pk-lf-…",
        "LANGFUSE_SECRET_KEY": "sk-lf-…",
        "LANGFUSE_BASE_URL": "https://cloud.langfuse.com"
      }
    }
  }
}
```

## Use with Cline (VS Code)

In VS Code settings (`settings.json`):

```json
{
  "cline.mcpServers": {
    "langfuse": {
      "command": "npx",
      "args": ["-y", "langfuse-mcp"],
      "env": {
        "LANGFUSE_PUBLIC_KEY": "pk-lf-…",
        "LANGFUSE_SECRET_KEY": "sk-lf-…",
        "LANGFUSE_BASE_URL": "https://cloud.langfuse.com"
      }
    }
  }
}
```

## Use with Continue

In `~/.continue/config.json`:

```json
{
  "mcpServers": [
    {
      "name": "langfuse",
      "command": "npx",
      "args": ["-y", "langfuse-mcp"],
      "env": {
        "LANGFUSE_PUBLIC_KEY": "pk-lf-…",
        "LANGFUSE_SECRET_KEY": "sk-lf-…",
        "LANGFUSE_BASE_URL": "https://cloud.langfuse.com"
      }
    }
  ]
}
```

## Use with Windsurf

In Windsurf's MCP settings, add:

```json
{
  "mcpServers": {
    "langfuse": {
      "command": "npx",
      "args": ["-y", "langfuse-mcp"],
      "env": {
        "LANGFUSE_PUBLIC_KEY": "pk-lf-…",
        "LANGFUSE_SECRET_KEY": "sk-lf-…",
        "LANGFUSE_BASE_URL": "https://cloud.langfuse.com"
      }
    }
  }
}
```

## Use with any other MCP client

The server speaks MCP over stdio. Any MCP client can launch it as a subprocess:

```bash
LANGFUSE_PUBLIC_KEY=pk-lf-… \
LANGFUSE_SECRET_KEY=sk-lf-… \
LANGFUSE_BASE_URL=https://cloud.langfuse.com \
npx -y langfuse-mcp
```

## Try it

Once wired up, ask your assistant things like:

- _"Use the `getHealth` tool to confirm langfuse-mcp is connected."_
- _"List the 5 most recent traces with `level=ERROR`."_
- _"Show me trace `abc123` with all its observations."_
- _"What scores did user `alice@example.com` receive this week?"_
- _"Get the production version of prompt `customer-support`."_
- _"List dataset runs for `eval-2026-q1` and tell me which one had the highest accuracy score."_

## Troubleshooting

**`401 Unauthorized` on the first call**

- Wrong region: Langfuse Cloud EU and US are separate accounts. Make sure `LANGFUSE_BASE_URL` matches the region where you created the keys (`https://cloud.langfuse.com` for EU, `https://us.cloud.langfuse.com` for US).
- Quoted keys in `.env`: this server strips surrounding quotes, but a stray space can still break Basic Auth. Re-paste the key.
- Use `getHealth` first to confirm credentials before running other tools.

**`npx` keeps using an old version**

```bash
npx -y langfuse-mcp@latest
```

`npx` caches packages aggressively. The `@latest` suffix forces a refresh.

**`LANGFUSE_BASE_URL must be a full URL` error**

The most common cause is a missing scheme. Use `https://cloud.langfuse.com`, not `cloud.langfuse.com`.

**Self-hosted Langfuse**

Use the full base URL of your deployment without a trailing slash or path. Example: `https://langfuse.mycompany.internal`. The server normalizes a single trailing slash, but anything else (`/api`, `/public`) will break path joining.

**MCP server icon doesn't appear in Claude Desktop**

- Check the Claude Desktop log: `~/Library/Logs/Claude/mcp*.log` (macOS) or `%APPDATA%\Claude\Logs\` (Windows). The server writes a `langfuse-mcp v… connected` line to stderr on success.
- Make sure Node 20+ is on your PATH (Claude Desktop uses your login shell PATH).
- Quit Claude Desktop fully (not just close the window) and relaunch.

**Cryptic `ERR_REQUIRE_ESM` / `Unexpected token` on startup**

Your Node version is too old. This package requires Node ≥ 20. Run `node --version` and upgrade if needed (e.g. via [nvm](https://github.com/nvm-sh/nvm)).

## Development

```bash
git clone https://github.com/hugoles/langfuse-mcp.git
cd langfuse-mcp
npm install
cp .env.example .env       # macOS/Linux
copy .env.example .env     # Windows cmd
npm run dev                # tsx src/index.ts (no build step)
```

Other scripts:

| Script                                    | What it does                   |
| ----------------------------------------- | ------------------------------ |
| `npm run build`                           | Compile TypeScript to `dist/`. |
| `npm start`                               | Run the built server.          |
| `npm run typecheck`                       | `tsc --noEmit`.                |
| `npm run lint`                            | ESLint.                        |
| `npm run format` / `npm run format:check` | Prettier write / check.        |
| `npm test`                                | Vitest.                        |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Bug reports and PRs are welcome — please run `npm run typecheck && npm run lint && npm test` locally before opening one.

## Security

Found a vulnerability? Please report it privately as described in [SECURITY.md](SECURITY.md). Do not open a public issue.

## License

[MIT](LICENSE) © Hugoles.
