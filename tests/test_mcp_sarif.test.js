// Tests for `sentinel-scan mcp --format sarif` (Node build), kept in
// parity with tests/test_mcp_sarif.py. Uses Node's built-in test runner
// (node:test / node:assert), no dependencies. Run with:
//   node --test tests/test_mcp_sarif.test.js
'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const path = require('path');

const { scanMcpManifest, buildMcpSarif, DEMO_MCP_MANIFEST } = require('../bin/sentinel-scan.js');

const FIXTURES_DIR = path.join(__dirname, '..', 'fixtures', 'mcp');
const SARIF_LEVELS = new Set(['error', 'warning', 'note']);

function loadFixtureRaw(name) {
  return fs.readFileSync(path.join(FIXTURES_DIR, name), 'utf-8');
}

// Structural validation against the required parts of the SARIF 2.1.0
// schema: top-level version/runs, one tool.driver per run with a name and a
// rules array, and one result per finding with a ruleId, a level drawn from
// the standard vocabulary, a message, and at least one location.
function assertValidSarifLog(sarif) {
  assert.equal(sarif.version, '2.1.0');
  assert.ok(sarif.$schema);
  assert.ok(Array.isArray(sarif.runs));
  assert.equal(sarif.runs.length, 1);
  const run = sarif.runs[0];

  const driver = run.tool.driver;
  assert.equal(typeof driver.name, 'string');
  assert.ok(driver.name);
  assert.ok(Array.isArray(driver.rules));
  const ruleIds = new Set(driver.rules.map((r) => r.id));
  for (const rule of driver.rules) {
    assert.equal(typeof rule.id, 'string');
    assert.equal(typeof rule.shortDescription.text, 'string');
  }

  assert.ok(Array.isArray(run.results));
  for (const result of run.results) {
    assert.ok(ruleIds.has(result.ruleId));
    assert.ok(SARIF_LEVELS.has(result.level));
    assert.equal(typeof result.message.text, 'string');
    assert.ok(result.message.text);
    assert.ok(Array.isArray(result.locations));
    assert.ok(result.locations.length >= 1);
    for (const loc of result.locations) {
      const uri = loc.physicalLocation.artifactLocation.uri;
      assert.equal(typeof uri, 'string');
      assert.ok(uri);
      const region = loc.physicalLocation.region;
      if (region !== undefined) {
        assert.equal(typeof region.startLine, 'number');
        assert.ok(region.startLine >= 1);
      }
    }
  }
}

test('demo manifest SARIF is valid and has regions', () => {
  const rawText = JSON.stringify(DEMO_MCP_MANIFEST, null, 2);
  const out = scanMcpManifest(DEMO_MCP_MANIFEST);
  const sarif = buildMcpSarif(out, 'demo-mcp-manifest.json', rawText);
  assertValidSarifLog(sarif);
  assert.ok(sarif.runs[0].results.length > 0);
  const withRegion = sarif.runs[0].results.filter((r) => r.locations[0].physicalLocation.region);
  assert.ok(withRegion.length > 0);
});

test('vulnerable fixture: SARIF is valid', () => {
  const rawText = loadFixtureRaw('vulnerable.json');
  const manifest = JSON.parse(rawText);
  const out = scanMcpManifest(manifest);
  const sarif = buildMcpSarif(out, 'fixtures/mcp/vulnerable.json', rawText);
  assertValidSarifLog(sarif);
});

test('vulnerable fixture: known malicious fixture produces expected rule IDs', () => {
  const rawText = loadFixtureRaw('vulnerable.json');
  const manifest = JSON.parse(rawText);
  const out = scanMcpManifest(manifest);
  const sarif = buildMcpSarif(out, 'fixtures/mcp/vulnerable.json', rawText);

  const expectedRuleIds = new Set([
    'tool_description_injection',
    'tool_name_shadowing',
    'excessive_agency_schema',
    'indirect_injection_surface',
    'unpinned_remote_source',
    'hardcoded_credential',
    'overbroad_tool_scope',
    'missing_provenance',
    'missing_hitl_confirmation',
    'hidden_unicode_instructions',
  ]);
  const run = sarif.runs[0];
  const ruleIds = new Set(run.tool.driver.rules.map((r) => r.id));
  const resultRuleIds = new Set(run.results.map((r) => r.ruleId));
  assert.deepEqual(ruleIds, expectedRuleIds);
  assert.deepEqual(resultRuleIds, expectedRuleIds);
  assert.equal(run.results.length, out.results.length);
});

test('vulnerable fixture: HIGH severity findings map to error level', () => {
  const rawText = loadFixtureRaw('vulnerable.json');
  const manifest = JSON.parse(rawText);
  const out = scanMcpManifest(manifest);
  const sarif = buildMcpSarif(out, 'fixtures/mcp/vulnerable.json', rawText);

  const run = sarif.runs[0];
  const highFindings = out.results.filter((f) => f.severity === 'HIGH');
  assert.ok(highFindings.length > 0);
  const errorResults = run.results.filter((r) => r.level === 'error');
  assert.equal(errorResults.length, highFindings.length);
});

test('vulnerable fixture: findings carry file/line locations where available', () => {
  const rawText = loadFixtureRaw('vulnerable.json');
  const manifest = JSON.parse(rawText);
  const out = scanMcpManifest(manifest);
  const sarif = buildMcpSarif(out, 'fixtures/mcp/vulnerable.json', rawText);

  const run = sarif.runs[0];
  const withRegion = run.results.filter((r) => r.locations[0].physicalLocation.region);
  assert.ok(withRegion.length > 0);
  for (const r of withRegion) {
    assert.equal(r.locations[0].physicalLocation.artifactLocation.uri, 'fixtures/mcp/vulnerable.json');
  }
});

test('clean fixture: no findings produces empty but valid SARIF', () => {
  const rawText = loadFixtureRaw('clean.json');
  const manifest = JSON.parse(rawText);
  const out = scanMcpManifest(manifest);
  const sarif = buildMcpSarif(out, 'fixtures/mcp/clean.json', rawText);
  assertValidSarifLog(sarif);
  assert.deepEqual(sarif.runs[0].results, []);
  assert.deepEqual(sarif.runs[0].tool.driver.rules, []);
});
