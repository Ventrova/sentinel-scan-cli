# PUBLISH-READY.md — sentinel-scan-cli v1.4.0

Status as of 2026-08-24: **zero blockers except credentials.** Everything below was
verified by a clean rebuild in this working copy. Publishing is a single command
per registry the instant `PYPI_API_TOKEN` / `NPM_TOKEN` land.

## PyPI (package: `sentinel-scan-cli`)

- Built fresh: `dist/sentinel_scan_cli-1.4.0-py3-none-any.whl` and
  `dist/sentinel_scan_cli-1.4.0.tar.gz` (`python -m build`, from a clean `dist/`).
- `twine check --strict dist/*` → **PASSED** for both artifacts (long_description
  renders clean as GitHub-flavored Markdown on PyPI; no RST/metadata errors).
- Name check: `sentinel-scan-cli` already exists on PyPI (200) — it's **our own**
  project (author `Ventrova`, current live release `1.0.0`), so v1.4.0 is a normal
  new-version upload, not a name claim. (Note: the *unhyphenated* `sentinel-scan`
  is unrelated and already taken on PyPI by a third-party Linux server scanner —
  not a concern since our project name is `sentinel-scan-cli`.)
- Metadata verified from the built wheel (`METADATA` file):
  - `Name: sentinel-scan-cli`, `Version: 1.4.0` ✓ matches target launch version
  - `License-Expression: MIT` ✓ (SPDX form, no setuptools deprecation warning)
  - `Project-URL: Homepage` → `https://github.com/Ventrova/sentinel-scan-cli` ✓
  - `Project-URL: Managed audit` → `https://ventrova.dev/audit` ✓
  - Classifiers: Development Status :: 4 - Beta, Environment :: Console,
    Intended Audience :: Developers, Programming Language :: Python :: 3,
    Topic :: Security ✓
  - `Description-Content-Type: text/markdown` ✓
  - README's absolute image/badge URLs are pinned to the `v1.4.0` git tag, which
    is already pushed to `origin` (`refs/tags/v1.4.0`), so they resolve correctly
    when PyPI renders the long_description.

**Command to run once `PYPI_API_TOKEN` is available:**

```bash
python -m twine upload --username __token__ --password "$PYPI_API_TOKEN" dist/*
```

(Artifacts are already built in `dist/`; re-run `python -m build` first if the
tree has changed since this check.)

## npm (package: `sentinel-scan-cli`, bin: `sentinel-scan`)

- `package.json` verified: `name: sentinel-scan-cli`, `version: 1.4.0`,
  `bin: { "sentinel-scan": "bin/sentinel-scan.js" }`, `files: ["bin/sentinel-scan.js"]`,
  `prepublishOnly: "node --test tests/*.test.js"`.
- `bin/sentinel-scan.js` has a `#!/usr/bin/env node` shebang and is executable
  (`-rwxr-xr-x`).
- Name check: `sentinel-scan-cli` is unclaimed on the npm registry (404) — clean
  land for this exact package name.
- `npm test` (same command `prepublishOnly` runs): **6/6 tests pass.**
- `npm publish --dry-run`: **clean.** Tarball contents are exactly the 4 files
  npm always includes plus `bin/`: `LICENSE`, `README.md`, `bin/sentinel-scan.js`,
  `package.json` — 29.4 kB packed / 90.7 kB unpacked, no test files or dev cruft
  leaking into the published package.
- Not currently logged in to the npm registry (`npm whoami` → `ENEEDAUTH`), as
  expected with no token yet.

**Command to run once `NPM_TOKEN` is available** (from a shell with
`//registry.npmjs.org/:_authToken=$NPM_TOKEN` in `.npmrc`, or via CI env):

```bash
npm publish --access public
```

(`prepublishOnly` re-runs the test suite automatically as a publish gate — no
separate test step needed.)

## Preconditions confirmed clean

- `dist/`, `build/`, `*.egg-info/` are gitignored — no publish artifacts leaking
  into git history.
- Repo is on `master`, up to date with `origin`, tag `v1.4.0` pushed.
- No uncommitted changes to source, `pyproject.toml`, or `package.json` (only
  untracked `benchmark_envs/` and `fixtures/real-world-sample/` scratch dirs
  present, unrelated to the release).

## The only remaining blocker

Credentials: `PYPI_API_TOKEN` (PyPI API token scoped to the `sentinel-scan-cli`
project) and `NPM_TOKEN` (npm automation/publish token for the `Ventrova` npm
account or org). The moment either lands, run the matching command above —
no further prep, rebuild, or verification needed.
