# Contributing to Sentinel Scan CLI

Thanks for taking a look. This is a small, single-file tool, so contributions
are easy to review and easy to make.

## Reporting a bug or false positive/negative

Open an issue with:

- The command you ran (redact your API key, endpoint URL is fine)
- What you expected vs what happened
- The relevant snippet from your output JSON (`--output` file)

## Proposing a new attack

The attack corpus in `sentinel_scan.py` (`ATTACKS`) is intentionally small and
bounded so a scan stays fast and auditable. If you have a known
prompt-injection or jailbreak technique that isn't covered:

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
