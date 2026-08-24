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

### Correction (2026-08-24): the project already exists on PyPI

`sentinel-scan-cli` is already live on PyPI, but only as a stale `1.0.0` (uploaded
2026-08-23T15:53 UTC, presumably via a manual token upload predating this OIDC setup
- README quickstart's plain `pip install sentinel-scan-cli` reflects that version and
is missing everything from `1.1.0` onward, including the `sentinel-scan mcp`
subcommand). This means the project-level "pending publisher" flow below does NOT
apply - the project already has an owner account on PyPI. Someone with access to
that existing PyPI project needs to add the trusted publisher instead:

1. Log into https://pypi.org with the account that owns the `sentinel-scan-cli` project
   (or that owns whatever account performed the 1.0.0 upload).
2. Go to https://pypi.org/manage/project/sentinel-scan-cli/settings/publishing/ (the
   *existing-project* trusted-publisher form, not the "pending publisher" form for a
   name that isn't claimed yet).
3. Fill in:
   - Owner: `Ventrova`
   - Repository name: `sentinel-scan-cli`
   - Workflow name: `release.yml`
   - Environment name: `pypi`
4. Submit, then tag and push a release (see below) to get `1.3.0` live and close the
   gap with `master`.

No token, password, or TOTP seed is needed for any future release once this is set up.
If 2FA is required to log into pypi.org itself (not for publishing, just for this
one-time console step), that's a normal PyPI account security control, not something
automatable.

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
