# PyPI publish

## Trusted Publishing (OIDC) - set up 2026-08-24, no stored token needed

`.github/workflows/release.yml` now builds the package and publishes it via
`pypa/gh-action-pypi-publish@release/v1` using GitHub Actions OIDC (`permissions:
id-token: write`, no `password:`/`repository-url` credential anywhere in the repo).
The workflow triggers on pushing a tag matching `v*.*.*` (e.g. `v1.3.0`) and publishes
to the `pypi` GitHub Environment.

This means once the PyPI-side trusted publisher is registered, the entire release flow
is: bump `pyproject.toml` version -> `git tag vX.Y.Z && git push origin vX.Y.Z` -> PyPI
publish happens automatically, zero secrets in the repo or in GitHub Actions secrets.

### Remaining human step (narrowed from "provide an API token" to this one PyPI console action)

Because `sentinel-scan-cli` has never been published, PyPI has no existing project to
attach a trusted publisher to, so this can't be done via API/CLI - it requires a login
to pypi.org. Someone with a PyPI account needs to:

1. Log into https://pypi.org (create an account first if none exists for Ventrova).
2. Go to https://pypi.org/manage/account/publishing/ (the "pending publisher" flow for
   a project that doesn't exist yet).
3. Fill in:
   - PyPI Project Name: `sentinel-scan-cli`
   - Owner: `Ventrova`
   - Repository name: `sentinel-scan-cli`
   - Workflow name: `release.yml`
   - Environment name: `pypi`
4. Submit. PyPI reserves the project name and will accept the first publish that
   authenticates via OIDC from that exact repo/workflow/environment combination -
   that first publish also becomes the project owner automatically.

No token, password, or TOTP seed is needed for this or any future release - this
replaces the old blocker entirely. If 2FA is required to log into pypi.org itself
(not for publishing, just for the one-time console registration), that's a normal
PyPI account security control, not something automatable.

### After PyPI-side registration lands

Trigger a real release:

```
git tag v1.3.0
git push origin v1.3.0
```

GitHub Actions builds and publishes automatically. Watch the run under the repo's
Actions tab; PyPI Trusted Publishing has no manual approval step once registered
(unless the `pypi` environment is configured with required reviewers).

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
classifiers/metadata are valid.
