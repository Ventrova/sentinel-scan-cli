# PyPI publish

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
