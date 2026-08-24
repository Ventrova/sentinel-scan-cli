# lazaretto-mcp

[![Lazaretto on the x402 List](https://x402-list.com/badge/lazaretto.svg?data=uptime)](https://x402-list.com/services/lazaretto)

An [MCP](https://modelcontextprotocol.io) server that lets an agent verify a
skill, tool, or package before it installs it. It is a thin front end for the
[Lazaretto](https://lazaretto.dev) API. It ships no detection logic and does
nothing but make HTTPS requests, so it is easy to audit.

## Tools

### `check_lockfile` (free, no API key)

Checks every exactly-pinned dependency in your lockfile against published
malicious-package advisories. Reads `package-lock.json`, `yarn.lock`, or
`pnpm-lock.yaml` from the working directory, so the agent never has to paste a
lockfile through its context. One call covers the whole tree.

An empty `malicious` list is an all-clear only when `unverified` is also empty.


- **`known_bad_lookup`**: free, no key. Is a sha256 content hash a known-bad
  artifact? Exact-hash match against an indicator store refreshed daily.
- **`scan_artifact`**: fetches a target (npm package, GitHub repo, ClawHub
  skill, raw URL, or inline text) without running it and returns a deterministic
  verdict (`malicious`, `flagged`, `clear`, `error`) with evidence. A full scan
  needs prepaid credits (set an `X-API-Key` header). Buy them at
  https://lazaretto.dev/#pricing.

Reports are signals with evidence, not a warranty. `clear` means no known-bad
match and no rule fired. It is not a statement about risk.

## Use it (hosted, zero install)

The server is hosted at `https://lazaretto.dev/mcp`. Add it to any MCP client
that supports remote (Streamable HTTP) servers. Nothing to install, no local
process.

```json
{
  "mcpServers": {
    "lazaretto": {
      "url": "https://lazaretto.dev/mcp",
      "headers": {
        "X-API-Key": "your-prepaid-key (optional; known_bad_lookup is free)"
      }
    }
  }
}
```

`known_bad_lookup` works with no key. `scan_artifact` needs credits: buy a bundle
at https://lazaretto.dev/#pricing (an agent can also do this itself over x402 at
`POST https://lazaretto.dev/v1/credits/topup`).

## Self-host the stdio server (optional)

If you would rather run it locally over stdio instead of the hosted URL:

```bash
git clone https://github.com/jamesdfinance-dev/lazaretto-mcp
cd lazaretto-mcp && npm install
LAZARETTO_API_KEY=your-key node index.mjs
```

`LAZARETTO_BASE_URL` overrides the API host (default `https://lazaretto.dev`).

## License

MIT. The Lazaretto service and its detection engine are separate and proprietary.
