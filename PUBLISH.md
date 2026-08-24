# PyPI publish

## Token-based release (2026-08-24)

`.github/workflows/release.yml` builds the package (`python -m build`) and publishes it
via `pypa/gh-action-pypi-publish@release/v1` using a `PYPI_API_TOKEN` repo secret
(`password: ${{ secrets.PYPI_API_TOKEN }}`). The workflow triggers on pushing a tag
matching `v*.*.*` (e.g. `v1.3.0`) and publishes through the `pypi` GitHub Environment.

This means the entire release flow, once the `PYPI_API_TOKEN` secret exists in the repo
(Settings -> Secrets and variables -> Actions -> New repository secret, or scoped to the
`pypi` environment), is:

```
git tag v1.3.0
git push origin v1.3.0
```

No PyPI-side dashboard configuration is required first (unlike OIDC Trusted Publishing,
which needs a one-time manual "add trusted publisher" step on pypi.org before it works).
A token-scoped-to-this-project API token (created at
https://pypi.org/manage/account/token/, scope: "Entire account" for the very first
upload of a new project, or scoped to `sentinel-scan-cli` once the project exists) is
the only prerequisite.

### Note: the project already exists on PyPI

`sentinel-scan-cli` is already live on PyPI, but only as a stale `1.0.0` (uploaded
2026-08-23T15:53 UTC via a manual token upload - README quickstart's plain
`pip install sentinel-scan-cli` reflects that version and is missing everything from
`1.1.0` onward, including the `sentinel-scan mcp` subcommand). Whoever owns that PyPI
project needs to create a scoped API token for it and add it as the `PYPI_API_TOKEN`
secret; then tag-and-push closes the gap with `master` (currently `1.3.0`).

## Manual fallback (if you'd rather publish from a local machine once)

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

**Zero remaining prep once `PYPI_API_TOKEN` exists as a repo/environment secret**: the
build config, metadata, README-as-long_description, entry point, and workflow are all
already correct and tested - `git tag vX.Y.Z && git push origin vX.Y.Z` is the entire
release action.
