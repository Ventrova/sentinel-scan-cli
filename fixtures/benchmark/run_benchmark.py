#!/usr/bin/env python3
"""Run each installed/available MCP manifest scanner against the 40-fixture
benchmark corpus and record honest detection/false-positive/runtime numbers.

Only scanners that could actually be built and run in this environment are
scored. Scanners that could not be installed/run are recorded as
"not evaluated" with the exact reason - no numbers are guessed for them.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent  # sentinel-scan-cli-work/
MANIFEST_PATH = HERE / "manifest.json"

with open(MANIFEST_PATH) as f:
    MANIFEST = json.load(f)

FIXTURES = MANIFEST["fixtures"]


def fixture_path(rel):
    return str(HERE / rel)


def run_sentinel_python(path):
    """sentinel-scan-cli (Python) mcp scan. Returns (flagged: bool, num_findings: int, error: str|None)."""
    out_file = HERE / "_tmp_py_out.json"
    try:
        subprocess.run(
            [sys.executable, str(REPO_ROOT / "sentinel_scan.py"), "mcp",
             "--manifest", path, "--output", str(out_file)],
            cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=30,
        )
        with open(out_file) as f:
            data = json.load(f)
        n = data["summary"]["num_findings"]
        return n > 0, n, None
    except Exception as e:
        return None, None, str(e)
    finally:
        out_file.unlink(missing_ok=True)


def run_sentinel_node(path):
    """sentinel-scan-cli (Node port) mcp scan. Returns (flagged: bool, num_findings: int, error: str|None)."""
    out_file = HERE / "_tmp_js_out.json"
    try:
        subprocess.run(
            ["node", str(REPO_ROOT / "bin" / "sentinel-scan.js"), "mcp",
             "--manifest", path, "--output", str(out_file)],
            cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=30,
        )
        with open(out_file) as f:
            data = json.load(f)
        n = data["summary"]["num_findings"]
        return n > 0, n, None
    except Exception as e:
        return None, None, str(e)
    finally:
        out_file.unlink(missing_ok=True)


# Scanner registry. `run` is None for scanners that could not be built/run in
# this environment - `not_evaluated_reason` records exactly why.
SCANNERS = {
    "sentinel-scan-cli (Python)": {
        "run": run_sentinel_python,
        "network_free": True,
        "not_evaluated_reason": None,
    },
    "sentinel-scan-cli (Node)": {
        "run": run_sentinel_node,
        "network_free": True,
        "not_evaluated_reason": None,
    },
    "MCP-Scan (Invariant Labs)": {
        "run": None,
        "network_free": False,
        "not_evaluated_reason": (
            "pip install mcp-scan succeeded into benchmark_envs/venv_mcpscan, "
            "but mcp-scan's static `scan` command requires invoking each "
            "MCP server's tools/list over a live client-server connection "
            "(stdio/SSE) rather than reading a manifest file directly, and "
            "also calls out to Invariant's hosted guardrail API by default "
            "for the prompt-injection classifier. Our fixtures are raw "
            "mcp.json tool manifests with no runnable server process behind "
            "them, and wiring 40 stub servers plus disabling the network "
            "call was out of scope for this benchmark round. Not scored."
        ),
    },
    "Cisco mcp-scanner": {
        "run": None,
        "network_free": False,
        "not_evaluated_reason": (
            "pip install into benchmark_envs/venv_cisco and venv_cisco312 "
            "(Python 3.12 required, project's default 3.14 is unsupported) "
            "was completed, but Cisco mcp-scanner's non-network-calling mode "
            "is YARA-rule based over server source/config and does not "
            "accept a bare mcp.json tool-manifest as input the way this "
            "benchmark corpus is structured; its LLM-judge and OSV/vuln "
            "lookup modes require network access, which this environment's "
            "network-free scoring column excludes. Not scored this round."
        ),
    },
    "mcpshield (npm)": {
        "run": None,
        "network_free": True,
        "not_evaluated_reason": (
            "npm install completed into benchmark_envs/npm_mcpshield, but "
            "the package's CLI expects a running MCP server endpoint to "
            "connect to and probe, not a static manifest file, so it could "
            "not be pointed at these 40 fixture files without standing up "
            "40 live stub servers. Not scored this round."
        ),
    },
}


def score_scanner(name, cfg):
    if cfg["run"] is None:
        return {
            "scanner": name,
            "status": "not_evaluated",
            "reason": cfg["not_evaluated_reason"],
            "network_free": cfg["network_free"],
        }

    run_fn = cfg["run"]
    tp = fp = tn = fn = 0
    errors = 0
    total_time = 0.0
    per_fixture = []

    for fx in FIXTURES:
        path = fixture_path(fx["filename"])
        expected = fx["expected"]  # "clean" or "malicious"
        start = time.perf_counter()
        flagged, n_findings, err = run_fn(path)
        elapsed = time.perf_counter() - start
        total_time += elapsed

        if err is not None:
            errors += 1
            per_fixture.append({"file": fx["filename"], "expected": expected,
                                 "flagged": None, "error": err})
            continue

        per_fixture.append({"file": fx["filename"], "expected": expected,
                             "flagged": flagged, "num_findings": n_findings})

        if expected == "malicious":
            if flagged:
                tp += 1
            else:
                fn += 1
        else:  # clean
            if flagged:
                fp += 1
            else:
                tn += 1

    n_malicious = tp + fn
    n_clean = tn + fp
    detection_rate = tp / n_malicious if n_malicious else None
    false_positive_rate = fp / n_clean if n_clean else None

    return {
        "scanner": name,
        "status": "evaluated",
        "network_free": cfg["network_free"],
        "num_fixtures": len(FIXTURES),
        "true_positives": tp,
        "false_negatives": fn,
        "true_negatives": tn,
        "false_positives": fp,
        "errors": errors,
        "detection_rate": detection_rate,
        "false_positive_rate": false_positive_rate,
        "total_runtime_seconds": round(total_time, 4),
        "avg_runtime_ms_per_fixture": round((total_time / len(FIXTURES)) * 1000, 2),
        "per_fixture": per_fixture,
    }


def main():
    results = [score_scanner(name, cfg) for name, cfg in SCANNERS.items()]

    output = {
        "corpus_version": MANIFEST["corpus_version"],
        "total_fixtures": MANIFEST["total_fixtures"],
        "num_clean": MANIFEST["num_clean"],
        "num_malicious": MANIFEST["num_malicious"],
        "results": results,
    }

    with open(HERE / "benchmark_results.json", "w") as f:
        json.dump(output, f, indent=2)

    # CSV summary (one row per scanner, no per-fixture detail)
    import csv
    with open(HERE / "benchmark_results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "scanner", "status", "network_free", "detection_rate",
            "false_positive_rate", "true_positives", "false_negatives",
            "true_negatives", "false_positives", "errors",
            "total_runtime_seconds", "avg_runtime_ms_per_fixture", "not_evaluated_reason",
        ])
        for r in results:
            if r["status"] == "not_evaluated":
                writer.writerow([r["scanner"], r["status"], r["network_free"],
                                  "", "", "", "", "", "", "", "", "", r["reason"]])
            else:
                writer.writerow([
                    r["scanner"], r["status"], r["network_free"],
                    f'{r["detection_rate"]:.3f}' if r["detection_rate"] is not None else "",
                    f'{r["false_positive_rate"]:.3f}' if r["false_positive_rate"] is not None else "",
                    r["true_positives"], r["false_negatives"], r["true_negatives"],
                    r["false_positives"], r["errors"], r["total_runtime_seconds"],
                    r["avg_runtime_ms_per_fixture"], "",
                ])

    print(json.dumps(output, indent=2)[:3000])
    print(f"\nWrote {HERE / 'benchmark_results.json'}")
    print(f"Wrote {HERE / 'benchmark_results.csv'}")


if __name__ == "__main__":
    main()
