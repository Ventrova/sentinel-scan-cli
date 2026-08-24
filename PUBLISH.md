# PyPI publish

**One command covers both registries, dry-run by default:** `scripts/publish.sh`
(see [scripts/publish.sh](./scripts/publish.sh) - checks version parity across
`package.json`/`pyproject.toml`/`sentinel_scan.py`/`bin/sentinel-scan.js`, builds
both packages, and runs `npm pack --dry-run` + `twine check` with zero
credentials required. Pass `--publish` to actually publish once `NPM_TOKEN`
and/or `TWINE_USERNAME`/`TWINE_PASSWORD` (or `PYPI_API_TOKEN`) are present in
the environment.)


**Status: PyPI is coming soon.** `pip install sentinel-scan-cli` currently
serves a stale `1.0.0` build (missing the `mcp` subcommand and 3 releases
behind `master`). Until the trusted-publisher registration below lands, the
git-install path is the primary documented install method (see README.md
[Quick start](./README.md#quick-start)).

## Interim install path - verified working (2026-08-24)

In a clean environment (fresh pipx-managed venv, no prior sentinel-scan-cli
install):

```bash
pipx install git+https://github.com/Ventrova/sentinel-scan-cli.git@v1.3.0
```

Installed cleanly as `sentinel-scan-cli 1.3.0`, exposing the `sentinel-scan`
entry point. Confirmed both of the following work end-to-end from that
install:

```bash
sentinel-scan --help
sentinel-scan mcp --manifest fixtures/mcp/vulnerable.json
```

`--help` prints full usage. The `mcp` scan against the repo's own
`fixtures/mcp/vulnerable.json` fixture correctly found 17 findings (9 HIGH,
6 MEDIUM, 2 LOW) across 10 heuristics (tool_description_injection,
excessive_agency_schema, missing_hitl_confirmation,
hidden_unicode_instructions, overbroad_tool_scope, tool_name_shadowing,
hardcoded_credential, unpinned_remote_source, indirect_injection_surface,
missing_provenance), matching the OWASP-mapped output documented in
README.md. No PyPI dependency anywhere in this path - it installs directly
from the `v1.3.0` git tag.

## Trusted Publishing (OIDC) - blocked on a pypi.org manual step (2026-08-24)

`.github/workflows/release.yml` builds the package (`python -m build`) and publishes it
via `pypa/gh-action-pypi-publish@release/v1` using GitHub Actions OIDC (`permissions:
id-token: write`, no stored token/password anywhere in the repo or its secrets). The
workflow triggers on pushing a tag matching `v*.*.*` (e.g. `v1.3.0`) and publishes
through the `pypi` GitHub Environment.

A token-based variant (`PYPI_API_TOKEN` secret) was tried and reverted on 2026-08-24:
storing a long-lived API token is a worse security posture than OIDC and was explicitly
out of scope for this release, so the workflow stays OIDC-only.

### Confirmed blocker: trusted publisher not registered on PyPI

Pushing `v1.3.0` on 2026-08-24T02:29 UTC triggered the OIDC workflow and it failed with:

```
Trusted publishing exchange failure:
Token request failed: the server refused the request for the following reasons:
* `invalid-publisher`: valid token, but no corresponding publisher (Publisher with
  matching claims was not found)
```

(GitHub Actions run 32683219284.) This is expected: `sentinel-scan-cli` already exists
on PyPI (a stale manual `1.0.0` upload from 2026-08-23T15:53 UTC), so PyPI requires the
project owner to register the trusted publisher from the *existing-project* settings
page rather than auto-creating one from a "pending publisher" request.

**One-time manual step required (human, PyPI account owner only):**

1. Log into https://pypi.org with the account that owns the `sentinel-scan-cli` project.
2. Go to https://pypi.org/manage/project/sentinel-scan-cli/settings/publishing/.
3. Add a trusted publisher with:
   - Owner: `Ventrova`
   - Repository name: `sentinel-scan-cli`
   - Workflow name: `release.yml`
   - Environment name: `pypi`
4. Submit. No token, password, or TOTP seed needs to be stored anywhere.

### After PyPI-side registration lands

```
git tag v1.3.1 && git push origin v1.3.1
```

(or delete and re-push `v1.3.0` if no code changes are needed) - GitHub Actions builds
and publishes automatically, closing the gap between PyPI (`1.0.0`) and `master`
(currently `1.3.0`). No manual approval step once registered, unless the `pypi`
environment is configured with required reviewers.

## Manual fallback (only if Trusted Publishing is ever unavailable)

```
python -m twine upload --username __token__ --password <PYPI_TOKEN> dist/*
```

Rebuild first if `dist/` is stale or missing:
`rm -rf dist build *.egg-info && python -m build`.

## Re-verified at 1.4.0 (2026-08-24, Show HN launch version)

`package.json`, `pyproject.toml`, `sentinel_scan.py`'s `VERSION`, and
`bin/sentinel-scan.js`'s `VERSION` all agree on `1.4.0`, matching the git tag
(`v1.4.0`) referenced in the Show HN post and first comment. `scripts/publish.sh`
(dry run) passes end-to-end: `npm pack --dry-run` is clean, `python -m build` +
`twine check dist/*` both PASSED for the wheel and sdist, and the wheel's
`entry_points.txt` resolves `sentinel-scan = sentinel_scan:main` correctly. Also
fixed a `setuptools` deprecation warning by switching `license = { text = "MIT" }`
to the SPDX string form `license = "MIT"` (the TOML-table form stops working in
setuptools by 2027-02-18) - `python -m build` now runs with zero warnings.
Nothing was published. The only remaining blocker is the PyPI trusted-publisher
registration step below (human, PyPI account owner only) plus the equivalent npm
token/OIDC step in NPM_PUBLISH.md.

## Package verified ready to publish (2026-08-24)

`rm -rf dist build *.egg-info && python -m build` succeeds, `twine check dist/*`
PASSED for both the wheel (`sentinel_scan_cli-1.3.0-py3-none-any.whl`) and sdist
(`sentinel_scan_cli-1.3.0.tar.gz`), version is 1.3.0, README renders as Markdown,
entry point (`sentinel-scan = sentinel_scan:main`) resolves correctly, and
classifiers/metadata are valid. Additionally installed the built wheel into a fresh
venv (`python -m venv` + `pip install dist/*.whl`) and confirmed `sentinel-scan --demo`
and `sentinel-scan mcp --help` both run correctly from the installed entry point, with
`sentinel_scan.VERSION == "1.3.0"`.

**Zero remaining prep once the trusted publisher is registered on pypi.org**: the build
config, metadata, README-as-long_description, entry point, and OIDC workflow are all
already correct and tested - `git tag vX.Y.Z && git push origin vX.Y.Z` is the entire
release action.

## Frozen for Show HN 2026-08-25, final end-to-end smoke test (2026-08-24)

`master` frozen at `v1.4.0` (commit `fadd73e`, pushed to `origin/master`). All three
published install paths were exercised fresh (temp dirs / fresh venv / no pre-existing
local install) and produced identical, correct output:

1. `pipx run --no-cache --spec "git+https://github.com/Ventrova/sentinel-scan-cli.git@v1.4.0" sentinel-scan --demo`
   and `... mcp --manifest fixtures/mcp/vulnerable.json` - `--no-cache` used deliberately
   to rule out the known pipx stale-cache gotcha (see org memory). `--demo` found
   3/15 attacks; `mcp` found 17 findings in 5 tools, matching README.
2. `npx --yes github:Ventrova/sentinel-scan-cli --demo` and `... mcp --manifest ...`
   (tracks `master`, now pointing at the just-pushed freeze commit) - identical
   3/15 and 17-finding output.
3. `pip install .` from a fresh `git clone --branch v1.4.0` into a clean venv, then
   ran the installed `sentinel-scan` entry point directly - identical 3/15 and
   17-finding output.

`scripts/publish.sh` (dry run) re-verified green at `1.4.0` the same session: version
parity across all four source files, `npm pack --dry-run` clean, `python -m build` +
`twine check dist/*` PASSED for both wheel and sdist. Nothing was published.

**Registry status re-checked live (2026-08-24):** `registry.npmjs.org/sentinel-scan-cli`
returns 404 (never published). `pypi.org/pypi/sentinel-scan-cli/json` still serves the
stale `1.0.0` upload. Both the npm token/OIDC step (NPM_PUBLISH.md) and the PyPI
trusted-publisher registration step (above, this file) remain outstanding, human-only
actions - the `scripts/publish.sh` runbook is the entire remaining task once either
lands. No new features were added ahead of launch; this session was freeze + verify only.
