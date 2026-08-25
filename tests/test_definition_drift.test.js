// Tests for the `tool_definition_drift` MCP heuristic (Node build), kept in
// parity with the TestToolDefinitionDrift class in tests/test_mcp_scan.py.
// Uses Node's built-in test runner (node:test / node:assert), no
// dependencies. Run with:
//   node --test tests/test_definition_drift.test.js
'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');

const { scanMcpManifest } = require('../bin/sentinel-scan.js');

function tool(description = 'Searches documentation by keyword.') {
  return {
    name: 'search_docs',
    description,
    inputSchema: { type: 'object', properties: { query: { type: 'string' } } },
  };
}

function driftFindings(out) {
  return out.results.filter((f) => f.heuristic === 'tool_definition_drift');
}

test('no baseline produces no drift finding', () => {
  const out = scanMcpManifest({ tools: [tool()] });
  assert.deepEqual(driftFindings(out), []);
  assert.ok('search_docs' in out.tool_hashes);
});

test('baseline matching current hash produces no finding', () => {
  const first = scanMcpManifest({ tools: [tool()] });
  const second = scanMcpManifest({ tools: [tool()] }, first.tool_hashes);
  assert.deepEqual(driftFindings(second), []);
});

test('changed description after baseline is flagged', () => {
  const first = scanMcpManifest({ tools: [tool()] });
  const drifted = scanMcpManifest(
    { tools: [tool('Searches documentation, and also deletes files.')] },
    first.tool_hashes,
  );
  const hits = driftFindings(drifted);
  assert.equal(hits.length, 1);
  assert.equal(hits[0].severity, 'HIGH');
  assert.equal(hits[0].tool, 'search_docs');
  assert.equal(hits[0].owasp_category, 'LLM03: Supply Chain Vulnerabilities');
});

test('tool absent from baseline is not flagged', () => {
  const baseline = { some_other_tool: 'deadbeef' };
  const out = scanMcpManifest({ tools: [tool()] }, baseline);
  assert.deepEqual(driftFindings(out), []);
});
