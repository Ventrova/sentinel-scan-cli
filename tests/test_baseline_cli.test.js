// CLI-level tests for `sentinel-scan mcp --baseline` / `--update-baseline`
// (Node build), kept in parity with tests/test_baseline_cli.py. Uses
// Node's built-in test runner (node:test / node:assert), no dependencies.
// Run with:
//   node --test tests/test_baseline_cli.test.js
'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('path');
const os = require('os');
const fs = require('fs');
const { spawnSync } = require('child_process');

const REPO_ROOT = path.join(__dirname, '..');
const SCAN_JS = path.join(REPO_ROOT, 'bin', 'sentinel-scan.js');

function manifest(description = 'Searches documentation by keyword.') {
  return {
    tools: [{
      name: 'search_docs',
      description,
      inputSchema: { type: 'object', properties: { query: { type: 'string' } } },
    }],
  };
}

function run(args, cwd) {
  return spawnSync(process.execPath, [SCAN_JS, ...args], { cwd, encoding: 'utf-8' });
}

function mkTmpDir() {
  return fs.mkdtempSync(path.join(os.tmpdir(), 'sentinel-scan-'));
}

test('--update-baseline writes hash file', () => {
  const tmpdir = mkTmpDir();
  const manifestPath = path.join(tmpdir, 'manifest.json');
  const baselinePath = path.join(tmpdir, 'baseline.json');
  fs.writeFileSync(manifestPath, JSON.stringify(manifest()));

  const proc = run([
    'mcp', '--manifest', manifestPath, '--baseline', baselinePath,
    '--update-baseline', '--output', path.join(tmpdir, 'out.json'),
  ], tmpdir);
  assert.equal(proc.status, 0, proc.stderr);
  assert.ok(fs.existsSync(baselinePath));
  const baseline = JSON.parse(fs.readFileSync(baselinePath, 'utf-8'));
  assert.ok('search_docs' in baseline);
});

test('unchanged definition against baseline has no drift finding', () => {
  const tmpdir = mkTmpDir();
  const manifestPath = path.join(tmpdir, 'manifest.json');
  const baselinePath = path.join(tmpdir, 'baseline.json');
  const outPath = path.join(tmpdir, 'out.json');
  fs.writeFileSync(manifestPath, JSON.stringify(manifest()));

  run(['mcp', '--manifest', manifestPath, '--baseline', baselinePath,
    '--update-baseline', '--output', outPath], tmpdir);

  const proc = run(['mcp', '--manifest', manifestPath, '--baseline', baselinePath,
    '--output', outPath], tmpdir);
  assert.equal(proc.status, 0, proc.stderr);
  const out = JSON.parse(fs.readFileSync(outPath, 'utf-8'));
  assert.deepEqual(out.results.filter((r) => r.heuristic === 'tool_definition_drift'), []);
});

test('changed definition against baseline fails --fail-on high gate', () => {
  const tmpdir = mkTmpDir();
  const manifestPath = path.join(tmpdir, 'manifest.json');
  const baselinePath = path.join(tmpdir, 'baseline.json');
  const outPath = path.join(tmpdir, 'out.json');
  fs.writeFileSync(manifestPath, JSON.stringify(manifest()));

  run(['mcp', '--manifest', manifestPath, '--baseline', baselinePath,
    '--update-baseline', '--output', outPath], tmpdir);

  fs.writeFileSync(manifestPath, JSON.stringify(manifest('Searches documentation, and also deletes files.')));

  const proc = run(['mcp', '--manifest', manifestPath, '--baseline', baselinePath,
    '--fail-on', 'high', '--output', outPath], tmpdir);
  assert.equal(proc.status, 1);
  const out = JSON.parse(fs.readFileSync(outPath, 'utf-8'));
  const hits = out.results.filter((r) => r.heuristic === 'tool_definition_drift');
  assert.equal(hits.length, 1);
  assert.equal(hits[0].tool, 'search_docs');
});

test('missing baseline file is not an error', () => {
  const tmpdir = mkTmpDir();
  const manifestPath = path.join(tmpdir, 'manifest.json');
  fs.writeFileSync(manifestPath, JSON.stringify(manifest()));

  const proc = run([
    'mcp', '--manifest', manifestPath,
    '--baseline', path.join(tmpdir, 'does-not-exist.json'),
    '--output', path.join(tmpdir, 'out.json'),
  ], tmpdir);
  assert.equal(proc.status, 0, proc.stderr);
});

test('--update-baseline without --baseline path errors', () => {
  const tmpdir = mkTmpDir();
  const manifestPath = path.join(tmpdir, 'manifest.json');
  fs.writeFileSync(manifestPath, JSON.stringify(manifest()));

  const proc = run([
    'mcp', '--manifest', manifestPath, '--update-baseline',
    '--output', path.join(tmpdir, 'out.json'),
  ], tmpdir);
  assert.equal(proc.status, 2);
});
