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

## Keeping this in sync with the Python original

`bin/sentinel-scan.js` is a manual, dependency-free port of `sentinel_scan.py`. The
attack corpus, OWASP LLM Top 10 tags, heuristics, and output JSON shape must stay in
lockstep - if you add/change an attack or the scoring logic in one, mirror it in the other.
