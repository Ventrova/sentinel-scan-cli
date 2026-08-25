#!/usr/bin/env node
'use strict';

const { Client } = require('@modelcontextprotocol/sdk/client/index.js');
const { StdioClientTransport } = require('@modelcontextprotocol/sdk/client/stdio.js');
const { DEMO_MCP_MANIFEST } = require('../bin/sentinel-scan.js');

const tgz = process.argv[2];
if (!tgz) {
  console.error('usage: node test-mcp-server-npx.js <path-to-tgz>');
  process.exit(1);
}

async function main() {
  const transport = new StdioClientTransport({
    command: 'npx',
    args: ['--yes', tgz, 'mcp-server'],
  });
  const client = new Client({ name: 'sentinel-scan-mcp-npx-test-client', version: '1.0.0' });
  await client.connect(transport);

  const tools = await client.listTools();
  console.log('tools via npx:', tools.tools.map((t) => t.name));

  const result = await client.callTool({
    name: 'scan_mcp_manifest',
    arguments: { manifest: DEMO_MCP_MANIFEST },
  });
  const text = result.content.find((c) => c.type === 'text').text;
  const parsed = JSON.parse(text);
  console.log('num findings via npx:', parsed.results.length);
  if (!(parsed.results.length > 0)) throw new Error('expected findings');

  await client.close();
  console.log('OK: npx-based MCP server invocation works end-to-end');
}

main().catch((err) => {
  console.error('FAILED:', err);
  process.exit(1);
});
