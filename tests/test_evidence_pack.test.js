// Tests for `sentinel-scan evidence` (Annex IV evidence-pack generator) and
// the underlying lib/evidence-pack.js render module. Uses Node's built-in
// test runner (node:test / node:assert), no dependencies.
// Run with:
//   node --test tests/test_evidence_pack.test.js
'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('path');
const os = require('os');
const fs = require('fs');
const { spawnSync } = require('child_process');
const { renderPack } = require('../lib/evidence-pack.js');

const REPO_ROOT = path.join(__dirname, '..');
const SCAN_JS = path.join(REPO_ROOT, 'bin', 'sentinel-scan.js');

function run(args, cwd) {
  return spawnSync(process.execPath, [SCAN_JS, ...args], { cwd, encoding: 'utf-8' });
}

function mkTmpDir() {
  return fs.mkdtempSync(path.join(os.tmpdir(), 'sentinel-scan-evidence-'));
}

// --- CLI-level tests ---------------------------------------------------------

test('evidence --demo writes an evidence pack and both raw scan JSON files', () => {
  const tmpdir = mkTmpDir();
  const outPath = path.join(tmpdir, 'evidence-pack.md');
  const llmOutPath = path.join(tmpdir, 'llm.json');
  const mcpOutPath = path.join(tmpdir, 'mcp.json');

  const proc = run([
    'evidence', '--demo', '--output', outPath,
    '--llm-scan-output', llmOutPath, '--mcp-scan-output', mcpOutPath,
  ], tmpdir);

  assert.equal(proc.status, 0, proc.stderr);
  assert.ok(fs.existsSync(outPath));
  assert.ok(fs.existsSync(llmOutPath));
  assert.ok(fs.existsSync(mcpOutPath));

  const pack = fs.readFileSync(outPath, 'utf-8');
  assert.match(pack, /# Compliance Evidence Pack \(Annex IV Lite\)/);
  assert.match(pack, /## 4\. Prompt-Injection Findings Table/);
  assert.match(pack, /## 5\. MCP Manifest Findings Table/);
  assert.match(pack, /## 6\. Human Attestation Block/);
});

test('evidence --demo --skip-mcp omits the MCP section', () => {
  const tmpdir = mkTmpDir();
  const outPath = path.join(tmpdir, 'evidence-pack.md');

  const proc = run(['evidence', '--demo', '--skip-mcp', '--output', outPath], tmpdir);
  assert.equal(proc.status, 0, proc.stderr);

  const pack = fs.readFileSync(outPath, 'utf-8');
  assert.match(pack, /## 4\. Prompt-Injection Findings Table/);
  assert.doesNotMatch(pack, /## 5\. MCP Manifest Findings Table/);
});

test('evidence --demo --skip-llm omits the LLM section', () => {
  const tmpdir = mkTmpDir();
  const outPath = path.join(tmpdir, 'evidence-pack.md');

  const proc = run(['evidence', '--demo', '--skip-llm', '--output', outPath], tmpdir);
  assert.equal(proc.status, 0, proc.stderr);

  const pack = fs.readFileSync(outPath, 'utf-8');
  assert.doesNotMatch(pack, /## 4\. Prompt-Injection Findings Table/);
  assert.match(pack, /## 5\. MCP Manifest Findings Table/);
});

test('evidence with neither --demo, --url/--model, nor --manifest errors', () => {
  const tmpdir = mkTmpDir();
  const proc = run(['evidence'], tmpdir);
  assert.equal(proc.status, 2);
  assert.match(proc.stderr, /error: evidence requires/);
});

test('evidence --demo --system-name/--pack-id fill the cover page', () => {
  const tmpdir = mkTmpDir();
  const outPath = path.join(tmpdir, 'evidence-pack.md');

  const proc = run([
    'evidence', '--demo', '--output', outPath,
    '--system-name', 'Acme Support Bot', '--pack-id', 'EP-TEST-001',
    '--scan-date', '2026-01-01', '--report-date', '2026-01-02',
  ], tmpdir);
  assert.equal(proc.status, 0, proc.stderr);

  const pack = fs.readFileSync(outPath, 'utf-8');
  assert.match(pack, /Acme Support Bot/);
  assert.match(pack, /EP-TEST-001/);
  assert.match(pack, /2026-01-01/);
  assert.match(pack, /2026-01-02/);
});

test('evidence --help exits 0 and does not run a scan', () => {
  const tmpdir = mkTmpDir();
  const proc = run(['evidence', '--help'], tmpdir);
  assert.equal(proc.status, 0, proc.stderr);
  assert.match(proc.stdout, /Usage: sentinel-scan evidence --demo/);
  assert.ok(!fs.existsSync(path.join(tmpdir, 'evidence-pack.md')));
});

test('evidence --demo --manifest <path> scans a real manifest instead of the MCP demo', () => {
  const tmpdir = mkTmpDir();
  const manifestPath = path.join(tmpdir, 'manifest.json');
  const outPath = path.join(tmpdir, 'evidence-pack.md');
  fs.writeFileSync(manifestPath, JSON.stringify({
    tools: [{
      name: 'search_docs',
      description: 'Searches documentation by keyword.',
      inputSchema: { type: 'object', properties: { query: { type: 'string' } } },
    }],
  }));

  const proc = run(['evidence', '--skip-llm', '--manifest', manifestPath, '--output', outPath], tmpdir);
  assert.equal(proc.status, 0, proc.stderr);

  const pack = fs.readFileSync(outPath, 'utf-8');
  assert.match(pack, /MCP manifest was scanned with 1 tool\(s\)/);
  assert.doesNotMatch(pack, /## 4\. Prompt-Injection Findings Table/);
});

test('top-level help mentions the evidence subcommand', () => {
  const tmpdir = mkTmpDir();
  const proc = run(['--help'], tmpdir);
  assert.equal(proc.status, 0, proc.stderr);
  assert.match(proc.stdout, /sentinel-scan evidence --demo/);
});

// --- renderPack unit tests ---------------------------------------------------

const SAMPLE_LLM = {
  summary: { version: '1.4.3', num_attacks: 2, literal_leak_count: 0 },
  results: [
    { attack: 'direct_override', owasp_category: 'LLM01: Prompt Injection', verdict: 'SAFE' },
    { attack: 'role_play', owasp_category: 'LLM01: Prompt Injection', verdict: 'VULNERABLE', leaked_secret_literal: true },
  ],
};

const SAMPLE_MCP = {
  summary: {
    version: '1.4.3', num_tools_scanned: 1, num_servers_scanned: 1,
    num_findings: 1, findings_by_severity: { HIGH: 1, MEDIUM: 0, LOW: 0 },
  },
  results: [
    { heuristic: 'hardcoded_credential', tool: 'github-tools', owasp_category: 'LLM02: Sensitive Information Disclosure', severity: 'HIGH' },
  ],
};

test('renderPack includes both sections when both scans are supplied', () => {
  const pack = renderPack({}, SAMPLE_LLM, SAMPLE_MCP);
  assert.match(pack, /## 4\. Prompt-Injection Findings Table/);
  assert.match(pack, /## 5\. MCP Manifest Findings Table/);
  assert.match(pack, /role_play/);
  assert.match(pack, /github-tools/);
});

test('renderPack omits a section entirely when its scan result is null', () => {
  const llmOnly = renderPack({}, SAMPLE_LLM, null);
  assert.match(llmOnly, /## 4\. Prompt-Injection Findings Table/);
  assert.doesNotMatch(llmOnly, /## 5\. MCP Manifest Findings Table/);

  const mcpOnly = renderPack({}, null, SAMPLE_MCP);
  assert.doesNotMatch(mcpOnly, /## 4\. Prompt-Injection Findings Table/);
  assert.match(mcpOnly, /## 5\. MCP Manifest Findings Table/);
});

test('renderPack escapes untrusted table-cell content from a scanned manifest', () => {
  const maliciousMcp = {
    summary: {
      version: '1.4.3', num_tools_scanned: 1, num_servers_scanned: 1,
      num_findings: 1, findings_by_severity: { HIGH: 1 },
    },
    results: [
      { heuristic: 'hardcoded_credential', tool: 'evil | tool\nwith a fake row', owasp_category: 'LLM02', severity: 'HIGH' },
    ],
  };
  const pack = renderPack({}, null, maliciousMcp);
  assert.doesNotMatch(pack, /evil \| tool\nwith a fake row/);
  assert.match(pack, /evil \\\| tool with a fake row/);
});

test('renderPack defaults system name/description to REDACTED when not supplied', () => {
  const pack = renderPack({}, SAMPLE_LLM, null);
  assert.match(pack, /REDACTED \(client intake required\)/);
});

test('renderPack uses supplied packId, scanDate, reportDate verbatim', () => {
  const pack = renderPack({
    packId: 'EP-FIXED', scanDate: '2026-01-01', reportDate: '2026-01-02',
  }, SAMPLE_LLM, null);
  assert.match(pack, /EP-FIXED/);
  assert.match(pack, /2026-01-01/);
  assert.match(pack, /2026-01-02/);
});
