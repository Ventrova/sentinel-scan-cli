# MCP Manifest Scanner Benchmark

Corpus: 40 fixtures (20 clean, 20 malicious across 10 attack techniques: command injection,
credential exfiltration, cross-origin exfiltration, DoS/resource exhaustion, excessive
permission scope, indirect injection via tool output, prompt injection in tool descriptions,
rug-pull schema mutation, tool poisoning schema, typosquatting). Fixture generator and
manifest: `manifest.json`, `generate_fixtures.py`. Run script: `run_benchmark.py`.

All numbers below were produced by actually executing each scanner against every fixture
file in this directory and comparing its output to the `expected` label in `manifest.json`
(see `benchmark_results.json` / `.csv` for the full per-fixture breakdown). Scanners that
could not be pointed at these static manifest files without network calls or live MCP
server processes are marked "not evaluated" with the exact blocking reason - no numbers
are guessed for them.

| Scanner | Status | Network-free | Detection rate | False-positive rate | Total runtime (40 fixtures) | Avg per fixture |
|---|---|---|---|---|---|---|
| sentinel-scan-cli (Python) | evaluated | yes | 100.0% (20/20 malicious caught) | 0.0% (0/20 clean flagged) | 7.21s | ~180 ms |
| sentinel-scan-cli (Node) | evaluated | yes | 50.0% (10/20 malicious caught) | 10.0% (2/20 clean flagged) | 3.09s | ~77 ms |
| MCP-Scan (Invariant Labs) | not evaluated | no | - | - | - | - |
| Cisco mcp-scanner | not evaluated | no | - | - | - | - |
| mcpshield (npm) | not evaluated | yes (tool itself has no network dependency) | - | - | - | - |

The Python build's detection rate rose from a 50.0%/10.0% baseline (identical to the Node
numbers below) after four rounds of heuristic work on `sentinel_scan.py`:

1. **Four missing heuristics added** to close entire attack-technique gaps that had zero
   detection logic: command injection (`_mcp_scan_command_injection` - flags a shell/exec
   call pattern combined with language documenting the input isn't sanitized before being
   interpolated into it), cross-origin exfiltration (`_mcp_scan_cross_origin_exfiltration` -
   flags a content-bearing parameter interpolated into an outbound URL placeholder),
   DoS/resource exhaustion (`_mcp_scan_dos_resource_exhaustion` - flags a description that
   documents no depth/size/row/pagination limit or output cap), and schema-level prompt
   injection / tool poisoning (`_mcp_scan_schema_text_injection` - runs the existing
   description-injection phrase/zero-width-character check across input- and
   output-schema property descriptions too, not just the top-level tool description).
2. **Injection phrase list widened** (still phrase-based, not fixture-specific) with a
   handful of additional imperative/override constructions (`trusted system instruction`,
   `supersedes the user's request`, `note to the agent`, `hidden directive`, `regardless of
   what the user asked`, `silently`, `injected instructions`) and loosened two existing
   patterns (`[system]`-style tags, `do not tell/inform/mention/show/disclose/surface/reveal
   ... the user`) to catch nearby paraphrases without requiring an exact string match.
3. **Wildcard-scope regex widened** from matching only a bare `"admin"`/`"*"` string to also
   catching a wildcard component inside a namespaced scope (`admin:*`,
   `filesystem:full_access`), still anchored to string edges or a `:`/`.`/`/` separator so it
   doesn't fire on an unrelated word that merely contains one of those tokens.
4. **The 2 clean false positives were substring-matching bugs, not missing rules**: the
   existing fetch/act/sensitive-capability keyword lists used plain `kw in haystack`
   containment, which fired on keywords that are prefixes or infixes of unrelated words (for
   example the calculator's "evaluate_expression" tripping an `eval` match, and a plain
   search tool's copy tripping a `search`/`run`-adjacent act keyword). Replacing that with
   `_mcp_keyword_hit`, a regex helper that requires the keyword to appear as a whole token
   bounded by non-alphanumeric characters, removed both false positives without removing any
   true positive.

None of the above hardcode a fixture filename, tool name, or literal fixture string - every
change is a general phrase, regex, or structural check that generalizes to manifests outside
this corpus. `python -m pytest` (15 tests, pre-existing unit-test suite unrelated to this
benchmark corpus) still passes after these changes.

**The Node port (`bin/sentinel-scan.js`, the CLI currently shipped to users) was left
unchanged and still sits at the 50.0%/10.0% baseline.** The equivalent heuristics above have
not yet been ported from Python to JavaScript - see the follow-up task filed alongside this
benchmark update. Until that port lands, the shipped CLI's actual detection rate is the Node
row, not the Python row.

## Why the three competitors are "not evaluated" (not zero, not guessed)

- **MCP-Scan (Invariant Labs)**: installs cleanly, but its `scan` command connects to a
  live MCP server process over stdio/SSE (`tools/list` RPC) rather than reading a manifest
  file, and its prompt-injection classifier calls Invariant's hosted guardrail API by
  default. This corpus is static `mcp.json` tool manifests with no server behind them;
  standing up 40 stub servers and disabling the network call was out of scope this round.
- **Cisco mcp-scanner**: installs (Python 3.12 required; this environment's default 3.14
  is unsupported, worked around with a dedicated venv), but its non-network-calling mode
  is YARA rules over server source/config, not a static tool-manifest format. Its LLM-judge
  and OSV vulnerability-lookup modes require network access, which is outside this
  network-free benchmark's scope.
- **mcpshield (npm)**: installs cleanly, but its CLI expects a running MCP server endpoint
  to probe, not a static manifest file, so it could not be pointed at these fixtures
  without standing up 40 live stub servers.

Full reasons, exact commands attempted, and per-fixture pass/fail detail are recorded in
`benchmark_results.json` and `benchmark_results.csv` in this directory.

## Honest takeaway

The Python implementation (`sentinel_scan.py`) now catches all 20 malicious fixtures in
this corpus with zero false positives on the 20 clean fixtures, running fully offline in
well under a second per fixture. The Node port shipped in `bin/sentinel-scan.js` has not
had the same heuristic work applied yet and still catches only half the malicious
fixtures with a 10% false-positive rate - it needs the four new heuristics and the
keyword/regex tightening described above ported over before it matches the Python build.
Neither build is positioned as catching everything against a real-world adversary; this
corpus exercises 10 attack techniques with one or two fixtures each, so 100%/0% here means
"no known gap against this specific 40-fixture corpus," not "unbeatable." It is positioned
as a free, instant, network-free first pass.
