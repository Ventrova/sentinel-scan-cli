# PyPI publish

Rebuilt and re-verified 2026-08-23: `rm -rf dist build *.egg-info && python -m build` succeeds,
`twine check dist/*` PASSED for both the wheel (`sentinel_scan_cli-1.1.0-py3-none-any.whl`) and
sdist (`sentinel_scan_cli-1.1.0.tar.gz`), version is 1.1.0, README renders as Markdown
(Description-Content-Type: text/markdown), and classifiers/metadata are valid.

v1.1.0 adds OWASP LLM Top 10 category tags to every attack/finding (README + JSON output).
Blocked on a fresh scoped API token: the `pypi` secret has the account password but the
account is 2FA (TOTP) protected and no TOTP seed or standing API token is stored, so
`twine upload` cannot authenticate headlessly. Needed from the owner: log into
pypi.org/manage/account/token/ and add a scoped token as `api_token=` in the `pypi` secret,
or provide a TOTP seed.

## Once the PyPI API token lands

One command, from this directory:

```
python -m twine upload --username __token__ --password <PYPI_TOKEN> dist/*
```

(Or set `TWINE_USERNAME=__token__` and `TWINE_PASSWORD=<PYPI_TOKEN>` as env vars and just run
`python -m twine upload dist/*`.)

If `dist/` is stale or missing, rebuild first: `rm -rf dist build *.egg-info && python -m build`.
