"""Tests for CI-friendly `--fail-on` exit codes (Python build).

Stdlib-only (unittest), no dependencies. Run with:
    python -m unittest discover -s tests
"""
import os
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sentinel_scan import mcp_findings_breach_threshold

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
SCAN_PY = os.path.join(REPO_ROOT, "sentinel_scan.py")
FIXTURES_DIR = os.path.join(REPO_ROOT, "fixtures", "mcp")


def _run(args):
    with tempfile.TemporaryDirectory() as tmpdir:
        output = os.path.join(tmpdir, "out.json")
        return subprocess.run(
            [sys.executable, SCAN_PY] + args + ["--output", output],
            cwd=REPO_ROOT, capture_output=True, text=True,
        )


class TestPromptInjectionScanExitCodes(unittest.TestCase):
    def test_default_fail_on_is_none_and_exits_zero_despite_vulnerable_findings(self):
        proc = _run(["--demo"])
        self.assertEqual(proc.returncode, 0)

    def test_fail_on_none_explicit_exits_zero(self):
        proc = _run(["--demo", "--fail-on", "none"])
        self.assertEqual(proc.returncode, 0)

    def test_fail_on_any_exits_nonzero_when_attacks_get_past(self):
        proc = _run(["--demo", "--fail-on", "any"])
        self.assertEqual(proc.returncode, 1)


class TestMcpScanExitCodes(unittest.TestCase):
    def test_default_fail_on_is_none_and_exits_zero_on_vulnerable_demo_manifest(self):
        proc = _run(["mcp", "--demo"])
        self.assertEqual(proc.returncode, 0)

    def test_fail_on_high_exits_nonzero_on_vulnerable_demo_manifest(self):
        proc = _run(["mcp", "--demo", "--fail-on", "high"])
        self.assertEqual(proc.returncode, 1)

    def test_fail_on_high_exits_zero_on_clean_fixture(self):
        proc = _run(["mcp", "--manifest", os.path.join(FIXTURES_DIR, "clean.json"), "--fail-on", "high"])
        self.assertEqual(proc.returncode, 0)

    def test_fail_on_low_exits_nonzero_on_vulnerable_fixture(self):
        proc = _run(["mcp", "--manifest", os.path.join(FIXTURES_DIR, "vulnerable.json"), "--fail-on", "low"])
        self.assertEqual(proc.returncode, 1)

    def test_fail_on_none_exits_zero_regardless_of_findings(self):
        proc = _run(["mcp", "--manifest", os.path.join(FIXTURES_DIR, "vulnerable.json"), "--fail-on", "none"])
        self.assertEqual(proc.returncode, 0)

    def test_fail_on_high_works_with_sarif_format(self):
        proc = _run(["mcp", "--demo", "--format", "sarif", "--fail-on", "high"])
        self.assertEqual(proc.returncode, 1)


class TestMcpFindingsBreachThreshold(unittest.TestCase):
    def test_none_never_breaches(self):
        findings = [{"severity": "HIGH"}]
        self.assertFalse(mcp_findings_breach_threshold(findings, "none"))

    def test_high_threshold_ignores_medium_and_low(self):
        findings = [{"severity": "MEDIUM"}, {"severity": "LOW"}]
        self.assertFalse(mcp_findings_breach_threshold(findings, "high"))

    def test_low_threshold_catches_any_severity(self):
        findings = [{"severity": "LOW"}]
        self.assertTrue(mcp_findings_breach_threshold(findings, "low"))

    def test_empty_findings_never_breaches(self):
        self.assertFalse(mcp_findings_breach_threshold([], "low"))


if __name__ == "__main__":
    unittest.main()
