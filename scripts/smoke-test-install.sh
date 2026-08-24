#!/usr/bin/env bash
# Smoke test for the two published install one-liners (README "Quick start").
# Runs each one-liner from a clean working directory and asserts the
# --demo and mcp --manifest output matches what a real run should produce,
# so a broken tag, a bad npm/pip packaging change, or an upstream registry
# outage surfaces here instead of via a manual dry run before launch.
#
# Usage: scripts/smoke-test-install.sh
# Must be run with the repo checked out (uses fixtures/mcp/vulnerable.json
# and fixtures/mcp/clean.json as fixed, versioned scan targets).

set -euo pipefail

# npx github: tracks the default branch, same as the documented one-liner,
# so this exercises whatever is currently on master (this checkout).
# pipx run --spec stays pinned to the tag the README documents, since that
# one-liner is explicitly version-pinned and the tag is immutable.
REPO_SLUG="ventrova/sentinel-scan-cli"
PINNED_TAG="v1.4.0"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VULN_MANIFEST="$REPO_ROOT/fixtures/mcp/vulnerable.json"
CLEAN_MANIFEST="$REPO_ROOT/fixtures/mcp/clean.json"

pass=0
fail=0

check() {
  local desc="$1" haystack="$2" needle="$3"
  if grep -qF -- "$needle" <<<"$haystack"; then
    echo "  ok: $desc"
    pass=$((pass + 1))
  else
    echo "  FAIL: $desc"
    echo "    expected to find: $needle"
    echo "    --- actual output ---"
    echo "$haystack" | sed 's/^/    /'
    fail=$((fail + 1))
  fi
}

run_in_clean_dir() {
  local label="$1"; shift
  local dir
  dir="$(mktemp -d)"
  echo "== $label (cwd=$dir) ==" >&2
  local out status=0
  out="$(cd "$dir" && "$@" 2>&1)" || status=$?
  echo "$out" >&2
  if [ "$status" -ne 0 ]; then
    echo "  FAIL: command exited $status" >&2
    fail=$((fail + 1))
  fi
  rm -rf "$dir"
  printf '%s' "$out"
}

# --- npx github: one-liner --------------------------------------------

npx_demo_out="$(run_in_clean_dir "npx github: --demo" npx --yes "github:${REPO_SLUG}" --demo)"
check "npx --demo: attack summary line" "$npx_demo_out" "3/15 attacks got past this system prompt"
check "npx --demo: prompt_leak_direct finding" "$npx_demo_out" "prompt_leak_direct"
check "npx --demo: markdown_exfil finding" "$npx_demo_out" "markdown_exfil"

npx_mcp_out="$(run_in_clean_dir "npx github: mcp --manifest (vulnerable)" npx --yes "github:${REPO_SLUG}" mcp --manifest "$VULN_MANIFEST")"
check "npx mcp: finding count line" "$npx_mcp_out" "17 finding(s) in 5 tool(s)"
check "npx mcp: tool_description_injection finding" "$npx_mcp_out" "tool_description_injection on search_docs"

npx_mcp_clean_out="$(run_in_clean_dir "npx github: mcp --manifest (clean)" npx --yes "github:${REPO_SLUG}" mcp --manifest "$CLEAN_MANIFEST")"
check "npx mcp clean: zero findings" "$npx_mcp_clean_out" "No heuristic findings on this manifest"

# --- pipx run --spec one-liner ------------------------------------------

if command -v pipx >/dev/null 2>&1; then
  PIPX=(pipx)
elif command -v python3 >/dev/null 2>&1 && python3 -m pipx --version >/dev/null 2>&1; then
  PIPX=(python3 -m pipx)
else
  echo "pipx not found on PATH, installing via pip (CI-only fallback)"
  python3 -m pip install --user --quiet pipx
  PIPX=(python3 -m pipx)
fi

pipx_demo_out="$(run_in_clean_dir "pipx run --spec --demo" "${PIPX[@]}" run --spec "git+https://github.com/${REPO_SLUG}.git@${PINNED_TAG}" sentinel-scan --demo)"
check "pipx --demo: attack summary line" "$pipx_demo_out" "3/15 attacks got past this system prompt"
check "pipx --demo: prompt_leak_direct finding" "$pipx_demo_out" "prompt_leak_direct"
check "pipx --demo: markdown_exfil finding" "$pipx_demo_out" "markdown_exfil"

pipx_mcp_out="$(run_in_clean_dir "pipx run --spec mcp --manifest (vulnerable)" "${PIPX[@]}" run --spec "git+https://github.com/${REPO_SLUG}.git@${PINNED_TAG}" sentinel-scan mcp --manifest "$VULN_MANIFEST")"
check "pipx mcp: finding count line" "$pipx_mcp_out" "17 finding(s) in 5 tool(s)"
check "pipx mcp: tool_description_injection finding" "$pipx_mcp_out" "tool_description_injection on search_docs"

pipx_mcp_clean_out="$(run_in_clean_dir "pipx run --spec mcp --manifest (clean)" "${PIPX[@]}" run --spec "git+https://github.com/${REPO_SLUG}.git@${PINNED_TAG}" sentinel-scan mcp --manifest "$CLEAN_MANIFEST")"
check "pipx mcp clean: zero findings" "$pipx_mcp_clean_out" "No heuristic findings on this manifest"

# --- summary -------------------------------------------------------------

echo
echo "$pass passed, $fail failed"
if [ "$fail" -gt 0 ]; then
  exit 1
fi
