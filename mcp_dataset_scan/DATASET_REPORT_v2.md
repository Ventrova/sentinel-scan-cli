# sentinel-scan mcp: real-world scan of 83 public MCP servers (v2, expanded)

**Date:** 2026-08-24
**Tool:** `sentinel-scan mcp` (static heuristic scanner, v1.3.0, no network calls, no server execution)
**Source:** [awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers) community index
**Sample:** 83 MCP servers - 73 randomly sampled community entries (35 from the v1 batch + 38 newly sampled, see `final35.json` + `batch2_40.json`) + 10 official Anthropic reference servers (everything, fetch, filesystem, git, gitlab, google-maps, memory, postgres, puppeteer, sqlite)

This is v2 of the dataset first published at [ventrova.dev/blog/state-of-mcp-server-security](https://ventrova.dev). v1 covered N=45. This expansion adds a second, independently-sampled batch of 40 community entries drawn from the same source index (38 successfully built into manifests; 2 had no fetchable README and were dropped) to test whether the v1 findings held at roughly 2x sample size.

## Method (unchanged from v1, applied to the new batch)

1. `awesome-mcp-servers.md` already fetched from the upstream repo in v1 (`extract.py`, 256 total candidates with inline install commands across the target categories).
2. Of the 221 candidates not used in v1's 35, randomly sampled 40 more with the same category-diversity caps used for v1 (fixed seed 42), see `batch2_40.json`.
3. Fetched each project's public README via a public, unauthenticated GET to `raw.githubusercontent.com` (`fetch_readmes_batch2.py`) - same method as v1, normal rate limiting (150ms between requests), no scraping of private/gated content. 38/40 READMEs fetched successfully; 2 repos had no README on `main`/`master` at the expected path and were dropped from the sample (not counted as findings either way).
4. Built an `mcp.json`-style manifest per server (`build_manifests_batch2.py`): preferred a published `mcpServers` JSON block from the README when present (`published_json_config`, 6 of 38), otherwise fell back to tokenizing the documented install one-liner (`awesome_list_install_oneliner`, 32 of 38). No server was executed; manifests are static config only.
5. Ran `sentinel-scan mcp --manifest <file>` (real CLI, same code path as the public tool, v1.3.0) against each of the 38 new manifests, same as v1's 45.
6. Aggregated all 83 manifests' per-server findings into OWASP-mapped classes (`aggregate_all.py`, replacing v1's `aggregate_results.json` with `aggregate_results_all.json`).

No server was contacted, executed, or sent data, in either batch. This remains static text/manifest analysis of publicly documented configuration.

## Results (N=83, up from N=45 in v1)

| Finding class | v1 (N=45) | v2 (N=83) | v2 % |
|---|---|---|---|
| `missing_provenance` | 41/45 (91.1%) | 77/83 | 92.8% |
| `unpinned_remote_source` | 39/45 (86.7%) | 71/83 | 85.5% |
| `hardcoded_credential` | 2/45 (4.4%) | 4/83 | 4.8% |
| `overbroad_tool_scope` | 0/45 (0.0%) | 0/83 | 0.0% |

## Delta vs v1

The rates barely moved when the sample nearly doubled: `missing_provenance` +1.7pp, `unpinned_remote_source` -1.2pp, `hardcoded_credential` +0.4pp, `overbroad_tool_scope` unchanged at zero. That stability across an independently-drawn second batch is itself evidence the v1 headline numbers weren't a small-sample artifact - roughly 9 in 10 public MCP servers still ship with no provenance/signature metadata, and roughly 6 in 7 pull an unpinned remote source. The credential-leak base rate stayed low but nonzero (4/83, two new hits in the second batch on top of the two from v1).

`overbroad_tool_scope` still never fired, for the same structural reason as v1: this heuristic needs full tool-call schemas, which install-only manifests built from READMEs and one-liners generally don't carry. Treat 0/83 as "not observed in this manifest slice," not "MCP servers don't have this problem" - see caveats.

## Caveats (unchanged from v1, still apply)

- This scans **install manifests**, not full tool-call schemas for every server - `overbroad_tool_scope` and prompt-injection heuristics need the server's actual tool descriptions, which aren't always in the README.
- Sample is drawn from `awesome-mcp-servers`, a curated but self-submitted index - it skews toward newer/smaller community projects rather than the full population of deployed MCP servers.
- 10 of 83 are official Anthropic reference servers (fixed, not randomly sampled) - included as a known-quality baseline; the community-only rate is measured across the other 73 (`final35.json` + `batch2_40.json`).
- No live server was scanned, contacted, or executed at any point in either batch - this is static analysis of publicly published manifests/READMEs only, per this task's authorization scope.

## Files

- `aggregate_results_all.json` - machine-readable combined summary (N=83) + per-server finding list
- `aggregate_results.json` - v1 summary (N=45), kept for the delta comparison above
- `manifests/` - all 83 built manifests actually scanned (45 from v1 + 38 new)
- `results/` - raw `sentinel-scan mcp` JSON output per server, all 83
- `batch2_40.json` / `manifests_meta_batch2.json` - sampling and manifest-build provenance for the new 38, back to the source index
- `final35.json` / `candidates.json` - v1 sampling provenance (unchanged)
