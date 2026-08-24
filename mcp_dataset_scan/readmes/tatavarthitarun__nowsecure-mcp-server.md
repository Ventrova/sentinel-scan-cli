# NowSecure MCP Server 🎈💜

> Made by **Tatavarthi Tarun** · [LinkedIn](https://www.linkedin.com/in/tatav)

A small Model Context Protocol (MCP) server for NowSecure Platform. Built to work
around the broken UI PDF export
(`Failed to load report data: Enum "JiraIntegrationCustomFieldType" cannot represent value: ""`)
by pulling findings through the REST + GraphQL APIs and, when needed, rendering
the remediation PDF locally instead of relying on NowSecure's report service.

## Requirements

- **Node.js >= 18** (the only prerequisite — `npx` fetches the package on demand)
- A **NowSecure Platform API token (PAT)** — each user supplies their own (see [Auth](#auth-each-user-uses-their-own-token))

## Tools

| Tool | What it does |
|------|--------------|
| `list_applications` | Lists your portfolio apps (REST). Find app refs + latest assessment. |
| `get_remediation_findings` | Returns findings needing remediation as JSON (GraphQL). Ideal for feeding an agent. |
| `generate_remediation_pdf` | Renders a clean PDF **locally** from the findings. Works even when NowSecure's renderer fails. |
| `download_assessment_pdf` | Tries NowSecure's REST PDF endpoint (separate path from the broken UI export). |

## Auth (each user uses their own token)

Every user generates their **own** NowSecure Platform API bearer token (PAT) and
puts it in their local MCP config. No token is bundled with this package.

Create one in Platform: Profile icon (top right) > Tokens.

- `NOWSECURE_TOKEN` (required) — your personal PAT
- `NOWSECURE_API_BASE` (optional) — defaults to `https://api.nowsecure.com`

## Install

No clone or manual install needed — `npx` fetches and runs the latest version.
You just need Node.js >= 18.

## MCP client config

All examples run the package via `npx` (no clone/install needed — just Node.js
>= 18). Replace the token with your **own** personal PAT.

### Claude Code

Use the CLI (recommended — it validates and writes to the right file):

```bash
claude mcp add nowsecure --env NOWSECURE_TOKEN=<your-personal-pat-here> -- npx -y nowsecure-mcp-server
```

Add `--scope user` to make it available across all your projects. Or edit
`.mcp.json` (project) / `~/.claude.json` (user) directly:

```json
{
  "mcpServers": {
    "nowsecure": {
      "command": "npx",
      "args": ["-y", "nowsecure-mcp-server"],
      "env": { "NOWSECURE_TOKEN": "<your-personal-pat-here>" }
    }
  }
}
```

### Cursor

Edit `~/.cursor/mcp.json` (global) or `.cursor/mcp.json` (per project):

```json
{
  "mcpServers": {
    "nowsecure": {
      "command": "npx",
      "args": ["-y", "nowsecure-mcp-server"],
      "env": { "NOWSECURE_TOKEN": "<your-personal-pat-here>" }
    }
  }
}
```

### Google Antigravity

In the agent panel / Settings, open **MCP Servers → Manage / Raw Config** to edit
`mcp_config.json`, then add:

```json
{
  "mcpServers": {
    "nowsecure": {
      "command": "npx",
      "args": ["-y", "nowsecure-mcp-server"],
      "env": { "NOWSECURE_TOKEN": "<your-personal-pat-here>" }
    }
  }
}
```

### GitHub Copilot (VS Code)

VS Code uses a top-level `servers` key (not `mcpServers`). Add to `.vscode/mcp.json`
in your workspace, or your user `mcp.json` (Command Palette → *MCP: Open User
Configuration*):

```json
{
  "servers": {
    "nowsecure": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "nowsecure-mcp-server"],
      "env": { "NOWSECURE_TOKEN": "<your-personal-pat-here>" }
    }
  }
}
```

### Kiro

Add to `~/.kiro/settings/mcp.json` (global) or `.kiro/settings/mcp.json` (workspace):

```json
{
  "mcpServers": {
    "nowsecure": {
      "command": "npx",
      "args": ["-y", "nowsecure-mcp-server"],
      "env": { "NOWSECURE_TOKEN": "<your-personal-pat-here>" },
      "disabled": false,
      "autoApprove": ["list_applications", "get_remediation_findings"]
    }
  }
}
```

> If published to a private/scoped registry, use the scoped name instead, e.g.
> `"args": ["-y", "@your-scope/nowsecure-mcp-server"]`.

## Example usage

First list your apps with `list_applications` to find an app ref, then ask your
agent (placeholders shown — substitute your own refs):

> Generate a remediation PDF for app `<app-ref-uuid>` to ./remediation.pdf

If you omit the assessment ref, the latest assessment for that app is used.

---

## Author

**Tatavarthi Tarun** 🎈💜
[linkedin.com/in/tatav](https://www.linkedin.com/in/tatav)

If this saved you from NowSecure's broken PDF export, a connect on LinkedIn is appreciated!
