#!/usr/bin/env python3
"""Build manifest.json for the held-out validation corpus (fixtures/heldout).

Distinct from fixtures/benchmark's 40-fixture corpus used to develop the
heuristics. Purpose: check whether the 100%/0% benchmark result generalizes
to unseen malicious/benign MCP manifests, or is overfit to the tuned corpus.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

clean_files = sorted((HERE / "clean").glob("*.json"))
mal_files = sorted((HERE / "malicious").glob("*.json"))

fixtures = []
for p in clean_files:
    fixtures.append({"filename": f"clean/{p.name}", "expected": "clean"})
for p in mal_files:
    fixtures.append({"filename": f"malicious/{p.name}", "expected": "malicious"})

manifest = {
    "corpus_version": "heldout-1.0.0",
    "purpose": (
        "Held-out generalization check for the fixtures/benchmark 40-fixture "
        "corpus. None of these fixtures were used to tune sentinel_scan.py's "
        "or bin/sentinel-scan.js's heuristics. Malicious fixtures cover the "
        "same broad attack classes as the tuned corpus (command injection, "
        "prompt injection in descriptions, tool poisoning, cross-origin "
        "exfiltration, DoS resource exhaustion, credential exfiltration, "
        "excessive permission scope, rug-pull schema mutation, typosquatting, "
        "indirect-injection surface) plus one genuinely novel encoding-evasion "
        "variant (hex-encoded instruction smuggling), expressed through new "
        "scenarios, tool names, and wording not present in the tuned corpus. "
        "Clean fixtures are modeled on real public MCP servers (git, "
        "filesystem, github, slack, postgres, playwright, fetch, memory, "
        "sqlite, docker, aws-cost-explorer, sentry, notion, gdrive, "
        "brave-search, time, google-maps, stripe, kubectl, pdf-extract), "
        "including several edge cases that legitimately shell out or fetch "
        "external URLs, to stress the false-positive rate on realistic "
        "manifests rather than only trivial toy ones."
    ),
    "total_fixtures": len(fixtures),
    "num_clean": len(clean_files),
    "num_malicious": len(mal_files),
    "fixtures": fixtures,
}

with open(HERE / "manifest.json", "w") as f:
    json.dump(manifest, f, indent=2)
    f.write("\n")

print(f"Wrote manifest.json: {len(fixtures)} fixtures ({len(clean_files)} clean, {len(mal_files)} malicious)")
