"""Tests for `sentinel-scan mcp --format sarif` (Python build).

Stdlib-only (unittest), no dependencies. Run with:
    python -m unittest discover -s tests
"""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sentinel_scan import scan_mcp_manifest, build_mcp_sarif, DEMO_MCP_MANIFEST

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures", "mcp")

SARIF_LEVELS = {"error", "warning", "note"}


def _load_fixture(name):
    with open(os.path.join(FIXTURES_DIR, name), "r", encoding="utf-8") as f:
        return f.read()


def _assert_valid_sarif_log(test, sarif):
    """Structural validation against the required parts of the SARIF 2.1.0
    schema (https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html):
    top-level version/runs, one tool.driver per run with a name and a rules
    array, and one result per finding with a ruleId, a level drawn from the
    standard vocabulary, a message, and at least one location."""
    test.assertEqual(sarif.get("version"), "2.1.0")
    test.assertIn("$schema", sarif)
    runs = sarif.get("runs")
    test.assertIsInstance(runs, list)
    test.assertEqual(len(runs), 1)
    run = runs[0]

    driver = run["tool"]["driver"]
    test.assertIsInstance(driver["name"], str)
    test.assertTrue(driver["name"])
    test.assertIsInstance(driver["rules"], list)
    rule_ids = {r["id"] for r in driver["rules"]}
    for rule in driver["rules"]:
        test.assertIsInstance(rule["id"], str)
        test.assertIn("text", rule["shortDescription"])

    test.assertIsInstance(run["results"], list)
    for result in run["results"]:
        test.assertIn(result["ruleId"], rule_ids)
        test.assertIn(result["level"], SARIF_LEVELS)
        test.assertIsInstance(result["message"]["text"], str)
        test.assertTrue(result["message"]["text"])
        locations = result["locations"]
        test.assertIsInstance(locations, list)
        test.assertGreaterEqual(len(locations), 1)
        for loc in locations:
            uri = loc["physicalLocation"]["artifactLocation"]["uri"]
            test.assertIsInstance(uri, str)
            test.assertTrue(uri)
            region = loc["physicalLocation"].get("region")
            if region is not None:
                test.assertIsInstance(region["startLine"], int)
                test.assertGreaterEqual(region["startLine"], 1)


class TestDemoManifestSarif(unittest.TestCase):
    def test_demo_manifest_sarif_is_valid_and_has_regions(self):
        raw_text = json.dumps(DEMO_MCP_MANIFEST, indent=2)
        out = scan_mcp_manifest(DEMO_MCP_MANIFEST)
        sarif = build_mcp_sarif(out, "demo-mcp-manifest.json", raw_text)
        _assert_valid_sarif_log(self, sarif)
        self.assertGreater(len(sarif["runs"][0]["results"]), 0)
        with_region = [
            r for r in sarif["runs"][0]["results"] if "region" in r["locations"][0]["physicalLocation"]
        ]
        self.assertGreater(len(with_region), 0)


class TestVulnerableFixtureSarif(unittest.TestCase):
    def setUp(self):
        self.raw_text = _load_fixture("vulnerable.json")
        self.manifest = json.loads(self.raw_text)
        self.out = scan_mcp_manifest(self.manifest)
        self.sarif = build_mcp_sarif(self.out, "fixtures/mcp/vulnerable.json", self.raw_text)

    def test_sarif_is_valid(self):
        _assert_valid_sarif_log(self, self.sarif)

    def test_known_malicious_fixture_produces_expected_rule_ids(self):
        expected_rule_ids = {
            "tool_description_injection",
            "tool_name_shadowing",
            "excessive_agency_schema",
            "indirect_injection_surface",
            "unpinned_remote_source",
            "hardcoded_credential",
            "overbroad_tool_scope",
            "missing_provenance",
            "missing_hitl_confirmation",
            "hidden_unicode_instructions",
        }
        run = self.sarif["runs"][0]
        rule_ids = {r["id"] for r in run["tool"]["driver"]["rules"]}
        result_rule_ids = {r["ruleId"] for r in run["results"]}
        self.assertEqual(expected_rule_ids, rule_ids)
        self.assertEqual(expected_rule_ids, result_rule_ids)
        # every result count matches the JSON-format finding count 1:1
        self.assertEqual(len(run["results"]), len(self.out["results"]))

    def test_high_severity_finding_maps_to_error_level(self):
        run = self.sarif["runs"][0]
        high_findings = [f for f in self.out["results"] if f["severity"] == "HIGH"]
        self.assertGreater(len(high_findings), 0)
        error_results = [r for r in run["results"] if r["level"] == "error"]
        self.assertEqual(len(error_results), len(high_findings))

    def test_findings_carry_file_line_locations_where_available(self):
        run = self.sarif["runs"][0]
        with_region = [
            r for r in run["results"] if "region" in r["locations"][0]["physicalLocation"]
        ]
        self.assertGreater(len(with_region), 0)
        for r in with_region:
            self.assertEqual(
                r["locations"][0]["physicalLocation"]["artifactLocation"]["uri"],
                "fixtures/mcp/vulnerable.json",
            )


class TestCleanFixtureSarif(unittest.TestCase):
    def test_no_findings_produces_empty_but_valid_sarif(self):
        raw_text = _load_fixture("clean.json")
        manifest = json.loads(raw_text)
        out = scan_mcp_manifest(manifest)
        sarif = build_mcp_sarif(out, "fixtures/mcp/clean.json", raw_text)
        _assert_valid_sarif_log(self, sarif)
        self.assertEqual(sarif["runs"][0]["results"], [])
        self.assertEqual(sarif["runs"][0]["tool"]["driver"]["rules"], [])


if __name__ == "__main__":
    unittest.main()
