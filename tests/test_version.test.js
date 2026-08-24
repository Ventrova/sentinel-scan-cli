// Test for `--version` (Node build), kept in parity with tests/test_version.py.
// Uses Node's built-in test runner (node:test / node:assert), no dependencies.
// Run with:
//   node --test tests/test_version.test.js
'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('path');
const { spawnSync } = require('child_process');

const REPO_ROOT = path.join(__dirname, '..');
const SCAN_JS = path.join(REPO_ROOT, 'bin', 'sentinel-scan.js');

test('--version prints version and exits 0', () => {
  const proc = spawnSync(process.execPath, [SCAN_JS, '--version'], {
    cwd: REPO_ROOT, encoding: 'utf-8',
  });
  assert.equal(proc.status, 0);
  assert.match(proc.stdout.trim(), /^\d+\.\d+\.\d+$/);
});
