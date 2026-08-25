"""CLI-level tests for `sentinel-scan mcp --baseline` / `--update-baseline`
(Python build), kept in parity with tests/test_baseline_cli.test.js.

Stdlib-only (unittest), no dependencies. Run with:
    python -m unittest discover -s tests
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
SCAN_PY = os.path.join(REPO_ROOT, "sentinel_scan.py")


def _manifest(description="Searches documentation by keyword."):
    return {
        "tools": [{
            "name": "search_docs",
            "description": description,
            "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}}},
        }]
    }


def _run(args, cwd):
    return subprocess.run(
        [sys.executable, SCAN_PY] + args, cwd=cwd, capture_output=True, text=True,
    )


class TestBaselineCli(unittest.TestCase):
    def test_update_baseline_writes_hash_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = os.path.join(tmpdir, "manifest.json")
            baseline_path = os.path.join(tmpdir, "baseline.json")
            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(_manifest(), f)

            proc = _run(
                ["mcp", "--manifest", manifest_path, "--baseline", baseline_path,
                 "--update-baseline", "--output", os.path.join(tmpdir, "out.json")],
                tmpdir,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertTrue(os.path.exists(baseline_path))
            with open(baseline_path, "r", encoding="utf-8") as f:
                baseline = json.load(f)
            self.assertIn("search_docs", baseline)

    def test_unchanged_definition_against_baseline_has_no_drift_finding(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = os.path.join(tmpdir, "manifest.json")
            baseline_path = os.path.join(tmpdir, "baseline.json")
            out_path = os.path.join(tmpdir, "out.json")
            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(_manifest(), f)

            _run(["mcp", "--manifest", manifest_path, "--baseline", baseline_path,
                  "--update-baseline", "--output", out_path], tmpdir)

            proc = _run(["mcp", "--manifest", manifest_path, "--baseline", baseline_path,
                         "--output", out_path], tmpdir)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            with open(out_path, "r", encoding="utf-8") as f:
                out = json.load(f)
            self.assertEqual(
                [r for r in out["results"] if r["heuristic"] == "tool_definition_drift"], []
            )

    def test_changed_definition_against_baseline_fails_high_gate(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = os.path.join(tmpdir, "manifest.json")
            baseline_path = os.path.join(tmpdir, "baseline.json")
            out_path = os.path.join(tmpdir, "out.json")
            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(_manifest(), f)

            _run(["mcp", "--manifest", manifest_path, "--baseline", baseline_path,
                  "--update-baseline", "--output", out_path], tmpdir)

            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(_manifest("Searches documentation, and also deletes files."), f)

            proc = _run(["mcp", "--manifest", manifest_path, "--baseline", baseline_path,
                         "--fail-on", "high", "--output", out_path], tmpdir)
            self.assertEqual(proc.returncode, 1)
            with open(out_path, "r", encoding="utf-8") as f:
                out = json.load(f)
            hits = [r for r in out["results"] if r["heuristic"] == "tool_definition_drift"]
            self.assertEqual(len(hits), 1)
            self.assertEqual(hits[0]["tool"], "search_docs")

    def test_missing_baseline_file_is_not_an_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = os.path.join(tmpdir, "manifest.json")
            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(_manifest(), f)

            proc = _run(
                ["mcp", "--manifest", manifest_path,
                 "--baseline", os.path.join(tmpdir, "does-not-exist.json"),
                 "--output", os.path.join(tmpdir, "out.json")],
                tmpdir,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_update_baseline_without_baseline_path_errors(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = os.path.join(tmpdir, "manifest.json")
            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(_manifest(), f)

            proc = _run(
                ["mcp", "--manifest", manifest_path, "--update-baseline",
                 "--output", os.path.join(tmpdir, "out.json")],
                tmpdir,
            )
            self.assertEqual(proc.returncode, 2)


if __name__ == "__main__":
    unittest.main()
