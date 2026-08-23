"""Tests for the `sentinel-scan mcp` static manifest heuristics.

Stdlib-only (unittest), no dependencies. Run with:
    python -m unittest discover -s tests
"""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sentinel_scan import scan_mcp_manifest, DEMO_MCP_MANIFEST

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures", "mcp")


def _load_fixture(name):
    with open(os.path.join(FIXTURES_DIR, name), "r", encoding="utf-8") as f:
        return json.load(f)


def _heuristics(findings):
    return {f["heuristic"] for f in findings}


class TestDemoManifest(unittest.TestCase):
    def test_demo_manifest_trips_all_heuristics(self):
        out = scan_mcp_manifest(DEMO_MCP_MANIFEST)
        expected = {
            "tool_description_injection",
            "tool_name_shadowing",
            "excessive_agency_schema",
            "indirect_injection_surface",
            "unpinned_remote_source",
            "hardcoded_credential",
            "overbroad_tool_scope",
            "missing_provenance",
        }
        self.assertEqual(expected, _heuristics(out["results"]))
        self.assertEqual(out["summary"]["num_tools_scanned"], 5)
        self.assertEqual(out["summary"]["num_servers_scanned"], 2)


class TestVulnerableFixture(unittest.TestCase):
    def setUp(self):
        self.out = scan_mcp_manifest(_load_fixture("vulnerable.json"))

    def test_trips_all_heuristics(self):
        expected = {
            "tool_description_injection",
            "tool_name_shadowing",
            "excessive_agency_schema",
            "indirect_injection_surface",
            "unpinned_remote_source",
            "hardcoded_credential",
            "overbroad_tool_scope",
            "missing_provenance",
        }
        self.assertEqual(expected, _heuristics(self.out["results"]))

    def test_owasp_tags_present(self):
        for finding in self.out["results"]:
            self.assertRegex(finding["owasp_category"], r"^LLM\d\d: ")


class TestCleanFixture(unittest.TestCase):
    def test_no_findings(self):
        out = scan_mcp_manifest(_load_fixture("clean.json"))
        self.assertEqual(out["results"], [])
        self.assertEqual(out["summary"]["num_findings"], 0)


class TestNewHeuristicsUnit(unittest.TestCase):
    def test_pinned_package_ref_is_not_flagged(self):
        manifest = {
            "mcpServers": {
                "pinned": {"command": "npx", "args": ["-y", "@acme/server@1.0.0"]},
                "pinned-pip": {"command": "pip", "args": ["install", "acme-server==2.1.0"]},
            }
        }
        out = scan_mcp_manifest(manifest)
        self.assertEqual(
            [f for f in out["results"] if f["heuristic"] == "unpinned_remote_source"], []
        )

    def test_env_placeholder_is_not_flagged(self):
        manifest = {
            "mcpServers": {
                "svc": {
                    "command": "npx",
                    "args": ["-y", "@acme/server@1.0.0"],
                    "env": {"API_KEY": "${API_KEY}"},
                }
            }
        }
        out = scan_mcp_manifest(manifest)
        self.assertEqual(
            [f for f in out["results"] if f["heuristic"] == "hardcoded_credential"], []
        )

    def test_enumerated_scopes_are_not_flagged(self):
        manifest = {"tools": [{"name": "t", "scopes": ["docs:read", "docs:write"]}]}
        out = scan_mcp_manifest(manifest)
        self.assertEqual(
            [f for f in out["results"] if f["heuristic"] == "overbroad_tool_scope"], []
        )

    def test_local_stdio_server_has_no_provenance_finding(self):
        manifest = {"mcpServers": {"local": {"command": "python", "args": ["./server.py"]}}}
        out = scan_mcp_manifest(manifest)
        self.assertEqual(
            [f for f in out["results"] if f["heuristic"] == "missing_provenance"], []
        )


if __name__ == "__main__":
    unittest.main()
