# Contributing to Sentinel Scan CLI

Thanks for taking a look. This is a small, single-file tool, so contributions
are easy to review and easy to make.

## Reporting a false positive/negative

Use the [Report a false positive/negative](https://github.com/Ventrova/sentinel-scan-cli/issues/new?template=false_positive_negative.yml)
issue form. It asks for exactly what we need to reproduce and fix it:
which check/OWASP tag fired, what endpoint type you scanned, what you
expected vs what actually happened, and the sanitized scan output.

## Proposing a new attack or heuristic

The attack corpus in `sentinel_scan.py` (`ATTACKS`) and the MCP heuristics
are intentionally small and bounded so a scan stays fast and auditable. If
you have a known prompt-injection technique or MCP manifest pattern that
isn't covered, use the [Missing attack / heuristic suggestion](https://github.com/Ventrova/sentinel-scan-cli/issues/new?template=missing_attack.yml)
issue form, or:

1. Open an issue describing the technique and a source/reference if you have one.
2. If you'd like to submit a PR directly, add one `(name, prompt)` tuple to
   `ATTACKS`, keep the prompt text self-contained (no external calls), and
   explain in the PR description what class of attack it tests.

## Development

No dependencies beyond the Python 3 standard library. Sanity-check any change
with the built-in demo target before opening a PR:

```bash
python sentinel_scan.py --demo
```

## Scope

This CLI is intentionally a fast heuristic smoke test, not a full audit
engine (that's the paid [Sentinel Scan audit](https://ventrova.dev/audit)).
PRs that keep it dependency-free, fast, and easy to read in one sitting are
the easiest to merge.
