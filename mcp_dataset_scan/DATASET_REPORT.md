# sentinel-scan mcp: real-world scan of 45 public MCP servers

**Date:** 2026-08-24
**Tool:** `sentinel-scan mcp` (static heuristic scanner, no network calls, no server execution)
**Source:** [awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers) community index
**Sample:** 45 MCP servers - 35 randomly sampled community entries (see `final35.json`) + 10 official Anthropic reference servers (everything, fetch, filesystem, git, gitlab, google-maps, memory, postgres, puppeteer, sqlite)

## Method

1. Fetched `awesome-mcp-servers.md` from the upstream repo (`extract.py`).
2. Parsed every `- [name](github-url)` list entry into candidate records with category and any published install one-liner (`candidates.json`, `extract.py`).
3. Randomly sampled 35 community entries (`pick35.py` -> `final35.json`) and added the 10 official Anthropic MCP reference servers for a fixed, well-known baseline.
4. Fetched each project's public README (`fetch_readmes.py`) - public, unauthenticated GET requests only, respecting normal rate limits, no scraping of private/gated content.
5. Built an `mcp.json`-style manifest per server (`build_manifests.py`): preferred a published `mcpServers` JSON block from the README when present (`published_json_config`), otherwise fell back to tokenizing the documented install one-liner (`awesome_list_install_oneliner`). No server was executed; manifests are static config only.
6. Ran `sentinel-scan mcp --manifest <file>` (real CLI, same code path as the public tool) against each of the 45 manifests.
7. Aggregated per-server findings into OWASP-mapped classes.

No server was contacted, executed, or sent data. This is a static text/manifest analysis of publicly documented configuration, consistent with scope/consent norms for a community index of public, self-listed projects.

## Results (N=45)

| Finding class | Servers hit | % |
|---|---|---|
| `missing_provenance` | 41 / 45 | 91.1% |
| `unpinned_remote_source` | 39 / 45 | 86.7% |
| `hardcoded_credential` | 2 / 45 | 4.4% |
| `overbroad_tool_scope` | 0 / 45 | 0.0% |

Headline: **9 in 10 public MCP servers ship with no provenance/signature metadata, and 87% pull an unpinned remote source** (e.g. `npx -y <pkg>` / `pip install <pkg>` with no version pin), meaning every install can silently change under you. Hardcoded credentials showed up in 2 manifests (~4%) - low base rate but non-zero even in a 45-server sample, and a single hit is a real supply-chain incident if it's yours. `overbroad_tool_scope` didn't fire on this manifest-only sample since that heuristic mostly needs full tool-schema data, not just install commands - a caveat noted below.

## Caveats (for honest external use)

- This scans **install manifests**, not full tool-call schemas for every server - `overbroad_tool_scope` and prompt-injection heuristics need the server's actual tool descriptions, which aren't always in the README. Treat the 0% `overbroad_tool_scope` figure as "not observed in this manifest slice," not "MCP servers don't have this problem."
- Sample is drawn from `awesome-mcp-servers`, a curated but self-submitted index - it skews toward newer/smaller community projects rather than the full population of deployed MCP servers.
- 10 of 45 are official Anthropic reference servers (fixed, not randomly sampled) - included as a known-quality baseline; the community-only rate is measured across the other 35 in `final35.json`.

## Files

- `aggregate_results.json` - machine-readable summary + per-server finding list
- `manifests/` - 45 built manifests actually scanned
- `results/` - raw `sentinel-scan mcp` JSON output per server
- `final35.json` / `candidates.json` - sampling provenance back to the source index
