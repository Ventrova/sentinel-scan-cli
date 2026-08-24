# npm publish

`package.json` and `bin/sentinel-scan.js` moved to the repo root (2026-08-23) so that
`npx github:ventrova/sentinel-scan-cli --demo` resolves without any npm registry publish
(npm's `github:` installer requires `package.json` at the repo root, it does not support
a subdirectory). Live-verified against the pushed `master` branch.

Re-verified 2026-08-23: `npm publish --dry-run` from the repo root is clean (no warnings,
4-file tarball: `bin/sentinel-scan.js`, `package.json`, plus the always-included
`README.md`/`LICENSE`). `package.json`'s `repository.url` uses the `git+https://...`
form npm expects. `bin/sentinel-scan.js` has the `#!/usr/bin/env node` shebang and is
executable (`-rwxr-xr-x`), and `files` is scoped to just `bin/sentinel-scan.js`.

Regression fix (2026-08-23): `sentinel-scan --demo` had drifted from the Python v1.1.0
output in two spots - `literal_leak=` printed JS's lowercase `true`/`false` instead of
Python's `True`/`False`, and `wall_clock_s` printed as a bare `0` instead of `0.0`. Both
are fixed in `bin/sentinel-scan.js` (console line now maps the boolean to `'True'`/`'False'`,
and `wall_clock_s` is forced to one decimal place via a token-substitution in the JSON
stringify step). Diffed `python sentinel_scan.py --demo` against
`node bin/sentinel-scan.js --demo` again after the fix: byte-identical modulo Windows
CRLF vs LF (Python's text-mode stdout on Windows adds `\r`; Node doesn't - not a logic
difference, confirmed by stripping `\r` from the Python output before diffing).

## Two ways to unblock this without ever storing an npm password

### Option A (preferred): npm Trusted Publishing (OIDC), same model as the PyPI fix

npm added OIDC-based Trusted Publishing in mid-2025 (npm CLI >= 11.5.1): a GitHub
Actions workflow with `id-token: write` authenticates straight to the npm registry,
no `NPM_TOKEN` secret anywhere. Requires:

1. A publish workflow (mirrors `.github/workflows/release.yml` for PyPI) that runs
   `npm publish --provenance` on a tag push, with `permissions: id-token: write`.
2. One human step on npmjs.com: log into (or create) the `Ventrova` npm account/org,
   go to the package's Settings -> Trusted Publisher (for a brand-new package name
   this has to be done right after the very first publish, since npm - unlike PyPI -
   doesn't support reserving a trusted publisher before the package exists yet), and
   link it to `Ventrova/sentinel-scan-cli` + the release workflow file.

Because npm requires the package to exist before a trusted publisher can be attached,
the very first publish still needs a one-time credential (see Option B) - after that,
every subsequent publish can run token-free via OIDC.

### Option B (fallback / first publish): granular automation token

Create a granular access token scoped to `sentinel-scan-cli` only, "Automation" type
(bypasses 2FA-on-publish, safe for CI since it's package-scoped and revocable), store
it as the `NPM_TOKEN` repo secret, and run `npm publish --provenance` with
`NODE_AUTH_TOKEN`. This is the one npm step that needs the owner: create that token at
https://www.npmjs.com/settings/~/tokens (Granular Access Token, expiry set, scoped to
publish-only on this one package) - no full-account password or 2FA seed needed, and
it can be deleted immediately after the first publish once Option A's trusted
publisher is linked.

## One command to publish to the npm registry, once an npm auth token or `npm adduser` login lands

From the repo root:

```
npm publish
```

(Or `npm login` first if not already authenticated on this machine.)

After that, `npx sentinel-scan-cli --demo` (no `github:` prefix, no clone) works for
anyone, and the root README's `npx github:ventrova/sentinel-scan-cli --demo` line should
be simplified to the direct registry form. Until then, the `github:` form already works
with zero signup and is what's used in launch materials.

## Version-parity gap found in the 2026-08-24 dry run

`sentinel_scan.py`'s internal `VERSION` was bumped to `1.2.0` then `1.3.0` when the
`sentinel-scan mcp` static heuristic scanner and its GitHub Action were added, but
`bin/sentinel-scan.js` never got an `mcp` subcommand port and its `VERSION` constant is
still `1.1.0`. Left `package.json`/`bin/sentinel-scan.js` at `1.1.0` rather than bumping
the number to match Python, since bumping the version alone without the `mcp` feature
would misrepresent what the npm package actually does. The Python package is correctly
at `1.3.0` (see PUBLISH.md). Porting `sentinel-scan mcp` to `bin/sentinel-scan.js` is
follow-up feature work, not a packaging fix.

## Keeping this in sync with the Python original

`bin/sentinel-scan.js` is a manual, dependency-free port of `sentinel_scan.py`. The
attack corpus, OWASP LLM Top 10 tags, heuristics, and output JSON shape must stay in
lockstep - if you add/change an attack or the scoring logic in one, mirror it in the other.
As of 2026-08-24 the `mcp` subcommand exists only in the Python original; the npm port's
version number intentionally trails Python's until that gap is closed.
