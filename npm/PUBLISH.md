# npm publish

Verified 2026-08-23: package name `sentinel-scan-cli` is unclaimed on the npm registry,
`npm pack` produces a clean 2-file tarball (`bin/sentinel-scan.js`, `package.json`, plus
the always-included `README.md`/`LICENSE`), and installing that tarball + running the
`sentinel-scan` bin reproduces the exact same output as the Python original (byte-for-byte
identical `--demo` JSON summary and console report). Requires Node 18+ (uses global `fetch`,
zero dependencies).

## Once an npm auth token or `npm adduser` login lands

From this directory:

```
npm publish
```

(Or `npm login` first if not already authenticated on this machine.)

After that, `npx sentinel-scan-cli --demo` works for anyone, and the root README's
"pending" language should be updated to the direct `npx` one-liner.

## Keeping this in sync with the Python original

`bin/sentinel-scan.js` is a manual, dependency-free port of `../sentinel_scan.py`. The
attack corpus, OWASP LLM Top 10 tags, heuristics, and output JSON shape must stay in
lockstep - if you add/change an attack or the scoring logic in one, mirror it in the other.
