// Tests for CI-friendly `--fail-on` exit codes (Node build), kept in
// parity with tests/test_exit_codes.py. Uses Node's built-in test runner
// (node:test / node:assert), no dependencies. Run with:
//   node --test tests/test_exit_codes.test.js
'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('path');
const os = require('os');
const fs = require('fs');
const { spawnSync } = require('child_process');

const { mcpFindingsBreachThreshold } = require('../bin/sentinel-scan.js');

const REPO_ROOT = path.join(__dirname, '..');
const SCAN_JS = path.join(REPO_ROOT, 'bin', 'sentinel-scan.js');
const FIXTURES_DIR = path.join(REPO_ROOT, 'fixtures', 'mcp');

function run(args) {
  const output = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'sentinel-scan-')), 'out.json');
  return spawnSync(process.execPath, [SCAN_JS, ...args, '--output', output], {
    cwd: REPO_ROOT, encoding: 'utf-8',
  });
}

test('prompt-injection scan: default --fail-on is none, exits 0 despite vulnerable findings', () => {
  const proc = run(['--demo']);
  assert.equal(proc.status, 0);
});

test('prompt-injection scan: --fail-on none exits 0', () => {
  const proc = run(['--demo', '--fail-on', 'none']);
  assert.equal(proc.status, 0);
});

test('prompt-injection scan: --fail-on any exits nonzero when attacks get past', () => {
  const proc = run(['--demo', '--fail-on', 'any']);
  assert.equal(proc.status, 1);
});

test('mcp scan: default --fail-on is none, exits 0 on vulnerable demo manifest', () => {
  const proc = run(['mcp', '--demo']);
  assert.equal(proc.status, 0);
});

test('mcp scan: --fail-on high exits nonzero on vulnerable demo manifest', () => {
  const proc = run(['mcp', '--demo', '--fail-on', 'high']);
  assert.equal(proc.status, 1);
});

test('mcp scan: --fail-on high exits 0 on clean fixture', () => {
  const proc = run(['mcp', '--manifest', path.join(FIXTURES_DIR, 'clean.json'), '--fail-on', 'high']);
  assert.equal(proc.status, 0);
});

test('mcp scan: --fail-on low exits nonzero on vulnerable fixture', () => {
  const proc = run(['mcp', '--manifest', path.join(FIXTURES_DIR, 'vulnerable.json'), '--fail-on', 'low']);
  assert.equal(proc.status, 1);
});

test('mcp scan: --fail-on none exits 0 regardless of findings', () => {
  const proc = run(['mcp', '--manifest', path.join(FIXTURES_DIR, 'vulnerable.json'), '--fail-on', 'none']);
  assert.equal(proc.status, 0);
});

test('mcp scan: --fail-on high works with --format sarif', () => {
  const proc = run(['mcp', '--demo', '--format', 'sarif', '--fail-on', 'high']);
  assert.equal(proc.status, 1);
});

test('mcpFindingsBreachThreshold: none never breaches', () => {
  assert.equal(mcpFindingsBreachThreshold([{ severity: 'HIGH' }], 'none'), false);
});

test('mcpFindingsBreachThreshold: high threshold ignores medium/low', () => {
  assert.equal(mcpFindingsBreachThreshold([{ severity: 'MEDIUM' }, { severity: 'LOW' }], 'high'), false);
});

test('mcpFindingsBreachThreshold: low threshold catches any severity', () => {
  assert.equal(mcpFindingsBreachThreshold([{ severity: 'LOW' }], 'low'), true);
});

test('mcpFindingsBreachThreshold: empty findings never breaches', () => {
  assert.equal(mcpFindingsBreachThreshold([], 'low'), false);
});
