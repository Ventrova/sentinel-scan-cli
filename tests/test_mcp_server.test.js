// End-to-end stdio test for `sentinel-scan mcp-server` (the MCP server
// entrypoint used by MCP clients/registries), driving raw JSON-RPC over
// stdin/stdout without depending on an MCP client SDK.
//
// Regression coverage: bin/sentinel-scan.js used to assign module.exports
// AFTER its `if (require.main === module)` entrypoint block, so the
// circular require('./sentinel-scan.js') from sentinel-scan-mcp-server.js
// saw an empty exports object and scanMcpManifest() was undefined. This
// test would fail with "scanMcpManifest is not a function" if that
// ordering regresses.
'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('path');
const { spawn } = require('child_process');

const REPO_ROOT = path.join(__dirname, '..');
const SCAN_JS = path.join(REPO_ROOT, 'bin', 'sentinel-scan.js');

function runMcpSession(requests) {
  return new Promise((resolve, reject) => {
    const proc = spawn(process.execPath, [SCAN_JS, 'mcp-server'], {
      cwd: REPO_ROOT,
      stdio: ['pipe', 'pipe', 'pipe'],
    });

    let buf = '';
    const responses = [];
    let stderr = '';
    const timer = setTimeout(() => {
      proc.kill();
      reject(new Error(`mcp-server timed out; stderr so far: ${stderr}`));
    }, 10000);

    proc.stdout.on('data', (d) => {
      buf += d.toString();
      let idx;
      while ((idx = buf.indexOf('\n')) >= 0) {
        const line = buf.slice(0, idx);
        buf = buf.slice(idx + 1);
        if (line.trim()) responses.push(JSON.parse(line));
      }
      if (responses.length >= requests.filter((r) => r.id !== undefined).length) {
        clearTimeout(timer);
        proc.kill();
        resolve(responses);
      }
    });
    proc.stderr.on('data', (d) => { stderr += d.toString(); });
    proc.on('error', reject);

    for (const req of requests) {
      proc.stdin.write(JSON.stringify(req) + '\n');
    }
  });
}

test('mcp-server: initialize, tools/list, tools/call round-trip over stdio', async () => {
  const manifest = {
    tools: [
      {
        name: 'send_email',
        description: 'Send an email on behalf of the user.',
        inputSchema: { type: 'object', properties: { to: { type: 'string' }, body: { type: 'string' } } },
        scopes: ['*'],
      },
    ],
  };

  const responses = await runMcpSession([
    { jsonrpc: '2.0', id: 1, method: 'initialize', params: { protocolVersion: '2024-11-05', capabilities: {}, clientInfo: { name: 'test-client', version: '1.0.0' } } },
    { jsonrpc: '2.0', method: 'notifications/initialized' },
    { jsonrpc: '2.0', id: 2, method: 'tools/list', params: {} },
    { jsonrpc: '2.0', id: 3, method: 'tools/call', params: { name: 'scan_mcp_manifest', arguments: { manifest } } },
  ]);

  const byId = Object.fromEntries(responses.map((r) => [r.id, r]));

  assert.equal(byId[1].result.serverInfo.name, 'sentinel-scan-mcp');

  const toolNames = byId[2].result.tools.map((t) => t.name);
  assert.ok(toolNames.includes('scan_mcp_manifest'));

  assert.equal(byId[3].result.isError, undefined);
  const out = JSON.parse(byId[3].result.content[0].text);
  assert.ok(out.summary.num_findings >= 1);
  assert.ok(out.results.some((f) => f.heuristic === 'overbroad_tool_scope'));
});
