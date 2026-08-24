#!/usr/bin/env bash
# Single reproducible publish entry point for npm + PyPI.
#
# Default mode is a dry run: it verifies version parity across every source
# of truth, builds both packages, and runs npm pack --dry-run + twine check
# (neither needs real credentials). It never publishes anything by default.
#
# Real publish only happens when the matching token env var is set AND
# --publish is passed. Tokens are read from the environment (populated by
# the secret broker / CI secrets) and are never hardcoded, logged, or
# written to disk.
#
#   scripts/publish.sh                 # dry run only (safe, no creds needed)
#   scripts/publish.sh --publish       # also publish, using env token(s) present
#   scripts/publish.sh --publish --npm-only
#   scripts/publish.sh --publish --pypi-only
#
# Env vars read (never printed):
#   NPM_TOKEN           -> written to a throwaway .npmrc for `npm publish`
#   TWINE_USERNAME / TWINE_PASSWORD   -> consumed directly by twine
#   (or PYPI_API_TOKEN, mapped to TWINE_USERNAME=__token__ / TWINE_PASSWORD)
#
# CI (.github/workflows/release.yml, npm-publish.yml) is the preferred path:
# `git tag vX.Y.Z && git push origin vX.Y.Z` publishes both registries via
# OIDC/Trusted Publishing with zero local tokens. This script exists for a
# manual/local publish (e.g. mid-launch, before OIDC trust is wired) and to
# give a single dry-run command that proves everything is publish-ready.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

DO_PUBLISH=0
DO_NPM=1
DO_PYPI=1

for arg in "$@"; do
  case "$arg" in
    --publish) DO_PUBLISH=1 ;;
    --npm-only) DO_PYPI=0 ;;
    --pypi-only) DO_NPM=0 ;;
    --help|-h)
      sed -n '2,25p' "$0"
      exit 0
      ;;
    *)
      echo "unknown argument: $arg" >&2
      exit 1
      ;;
  esac
done

echo "== 1. Version parity check =="
PKG_VERSION="$(python3 - <<'PY'
import json
print(json.load(open("package.json"))["version"])
PY
)"
PYPROJECT_VERSION="$(python3 - <<'PY'
import tomllib
print(tomllib.load(open("pyproject.toml", "rb"))["project"]["version"])
PY
)"
PY_VERSION="$(grep -m1 '^VERSION = ' sentinel_scan.py | sed -E 's/VERSION = "(.*)"/\1/')"
JS_VERSION="$(grep -a -m1 "VERSION = '" bin/sentinel-scan.js | sed -E "s/.*VERSION = '(.*)'.*/\1/")"

echo "  package.json:      $PKG_VERSION"
echo "  pyproject.toml:    $PYPROJECT_VERSION"
echo "  sentinel_scan.py:  $PY_VERSION"
echo "  sentinel-scan.js:  $JS_VERSION"

for v in "$PYPROJECT_VERSION" "$PY_VERSION" "$JS_VERSION"; do
  if [[ "$v" != "$PKG_VERSION" ]]; then
    echo "FAIL: version mismatch ($v != $PKG_VERSION). Bump all four before publishing." >&2
    exit 1
  fi
done
VERSION="$PKG_VERSION"
echo "  ok: all four sources agree on $VERSION"

TAG="v$VERSION"
if git rev-parse "$TAG" >/dev/null 2>&1; then
  echo "  ok: git tag $TAG already exists (matches Show HN git-install reference)"
else
  echo "  note: git tag $TAG does not exist yet locally. Create + push it to trigger CI publish:"
  echo "        git tag $TAG && git push origin $TAG"
fi

if [[ "$DO_NPM" == "1" ]]; then
  echo
  echo "== 2. npm build + dry run =="
  npm pack --dry-run
  echo "  ok: npm pack --dry-run clean"
fi

if [[ "$DO_PYPI" == "1" ]]; then
  echo
  echo "== 3. PyPI build + check =="
  rm -rf dist build ./*.egg-info
  python3 -m pip install --quiet --upgrade build twine
  python3 -m build
  python3 -m twine check dist/*
  echo "  ok: twine check passed for dist/*"
fi

if [[ "$DO_PUBLISH" != "1" ]]; then
  echo
  echo "Dry run complete. Nothing was published (pass --publish to publish)."
  exit 0
fi

if [[ "$DO_NPM" == "1" ]]; then
  echo
  echo "== 4. npm publish =="
  if [[ -n "${NPM_TOKEN:-}" ]]; then
    NPMRC="$(mktemp)"
    trap 'rm -f "$NPMRC"' EXIT
    echo "//registry.npmjs.org/:_authToken=${NPM_TOKEN}" > "$NPMRC"
    npm publish --provenance --userconfig "$NPMRC"
    echo "  ok: published $VERSION to npm"
  else
    echo "  skip: NPM_TOKEN not set in environment (or already authenticated via 'npm login' -" \
         "run 'npm publish --provenance' directly in that case)." >&2
  fi
fi

if [[ "$DO_PYPI" == "1" ]]; then
  echo
  echo "== 5. PyPI publish (twine) =="
  if [[ -n "${PYPI_API_TOKEN:-}" ]]; then
    export TWINE_USERNAME="__token__"
    export TWINE_PASSWORD="$PYPI_API_TOKEN"
  fi
  if [[ -n "${TWINE_USERNAME:-}" && -n "${TWINE_PASSWORD:-}" ]]; then
    python3 -m twine upload dist/*
    echo "  ok: published $VERSION to PyPI"
  else
    echo "  skip: no PyPI credentials in environment (TWINE_USERNAME/TWINE_PASSWORD or" \
         "PYPI_API_TOKEN). Prefer the CI Trusted Publishing workflow instead: 'git tag $TAG" \
         "&& git push origin $TAG' (see PUBLISH.md)." >&2
  fi
fi

echo
echo "Publish run complete for $VERSION."
