"""Test for `--version` (Python build). Stdlib-only (unittest).

Run with:
    python -m unittest discover -s tests
"""
import os
import subprocess
import sys
import unittest

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
SCAN_PY = os.path.join(REPO_ROOT, "sentinel_scan.py")


class TestVersion(unittest.TestCase):
    def test_version_flag_prints_version_and_exits_zero(self):
        proc = subprocess.run(
            [sys.executable, SCAN_PY, "--version"],
            cwd=REPO_ROOT, capture_output=True, text=True,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertRegex(proc.stdout.strip(), r"^\d+\.\d+\.\d+$")
