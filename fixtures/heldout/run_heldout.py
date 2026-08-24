#!/usr/bin/env python3
"""Run sentinel-scan-cli (Python and Node builds) against the held-out
generalization corpus (fixtures/heldout) and record honest TP/FP/TN/FN
numbers, plus which heuristic fired on each true positive so we can see
which heuristics generalize to unseen fixtures vs. which don't fire at all.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
MANIFEST_PATH = HERE / "manifest.json"

with open(MANIFEST_PATH) as f:
    MANIFEST = json.load(f)

FIXTURES = MANIFEST["fixtures"]


def fixture_path(rel):
    return str(HERE / rel)


def run_sentinel_python(path):
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
        heuristics = sorted(data["summary"].get("findings_by_heuristic", {}).keys())
        return n > 0, n, heuristics, None
    except Exception as e:
        return None, None, [], str(e)
    finally:
        out_file.unlink(missing_ok=True)


def run_sentinel_node(path):
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
        heuristics = sorted(data["summary"].get("findings_by_heuristic", {}).keys())
        return n > 0, n, heuristics, None
    except Exception as e:
        return None, None, [], str(e)
    finally:
        out_file.unlink(missing_ok=True)


SCANNERS = {
    "sentinel-scan-cli (Python)": run_sentinel_python,
    "sentinel-scan-cli (Node)": run_sentinel_node,
}


def score_scanner(name, run_fn):
    tp = fp = tn = fn = 0
    errors = 0
    total_time = 0.0
    per_fixture = []
    heuristics_that_fired = set()

    for fx in FIXTURES:
        path = fixture_path(fx["filename"])
        expected = fx["expected"]
        start = time.perf_counter()
        flagged, n_findings, heuristics, err = run_fn(path)
        elapsed = time.perf_counter() - start
        total_time += elapsed

        if err is not None:
            errors += 1
            per_fixture.append({"file": fx["filename"], "expected": expected,
                                 "flagged": None, "error": err})
            continue

        per_fixture.append({"file": fx["filename"], "expected": expected,
                             "flagged": flagged, "num_findings": n_findings,
                             "heuristics": heuristics})

        if expected == "malicious":
            if flagged:
                tp += 1
                heuristics_that_fired.update(heuristics)
            else:
                fn += 1
        else:
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
        "heuristics_that_fired_on_heldout": sorted(heuristics_that_fired),
        "per_fixture": per_fixture,
    }


def main():
    results = [score_scanner(name, fn) for name, fn in SCANNERS.items()]

    output = {
        "corpus_version": MANIFEST["corpus_version"],
        "total_fixtures": MANIFEST["total_fixtures"],
        "num_clean": MANIFEST["num_clean"],
        "num_malicious": MANIFEST["num_malicious"],
        "results": results,
    }

    with open(HERE / "heldout_results.json", "w") as f:
        json.dump(output, f, indent=2)

    for r in results:
        print(f"\n=== {r['scanner']} ===")
        print(f"  detection_rate (TP/(TP+FN)): {r['detection_rate']}")
        print(f"  false_positive_rate (FP/(FP+TN)): {r['false_positive_rate']}")
        print(f"  TP={r['true_positives']} FN={r['false_negatives']} TN={r['true_negatives']} FP={r['false_positives']} errors={r['errors']}")
        print(f"  heuristics that fired on any true positive: {r['heuristics_that_fired_on_heldout']}")
        fns = [pf["file"] for pf in r["per_fixture"] if pf["expected"] == "malicious" and pf["flagged"] is False]
        fps = [pf["file"] for pf in r["per_fixture"] if pf["expected"] == "clean" and pf["flagged"] is True]
        if fns:
            print(f"  FALSE NEGATIVES (missed malicious): {fns}")
        if fps:
            print(f"  FALSE POSITIVES (flagged clean): {fps}")

    print(f"\nWrote {HERE / 'heldout_results.json'}")


if __name__ == "__main__":
    main()
