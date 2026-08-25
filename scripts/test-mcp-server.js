#!/usr/bin/env node
'use strict';

const path = require('path');
const { Client } = require('@modelcontextprotocol/sdk/client/index.js');
const { StdioClientTransport } = require('@modelcontextprotocol/sdk/client/stdio.js');
const { DEMO_MCP_MANIFEST } = require('../bin/sentinel-scan.js');

async function main() {
  const transport = new StdioClientTransport({
    command: process.execPath,
    args: [path.join(__dirname, '..', 'bin', 'sentinel-scan-mcp-server.js')],
  });
  const client = new Client({ name: 'sentinel-scan-mcp-test-client', version: '1.0.0' });
  await client.connect(transport);

  const tools = await client.listTools();
  console.log('tools:', tools.tools.map((t) => t.name));

  const result = await client.callTool({
    name: 'scan_mcp_manifest',
    arguments: { manifest: DEMO_MCP_MANIFEST },
  });

  const text = result.content.find((c) => c.type === 'text').text;
  const parsed = JSON.parse(text);
  console.log('summary:', parsed.summary);
  console.log('num findings returned:', parsed.results.length);
  if (parsed.summary.num_findings !== parsed.results.length) {
    throw new Error('mismatch between summary.num_findings and results.length');
  }
  if (parsed.summary.num_findings === 0) {
    throw new Error('expected demo manifest to produce findings');
  }

  await client.close();
  console.log('OK: MCP server end-to-end test passed');
}

main().catch((err) => {
  console.error('FAILED:', err);
  process.exit(1);
});
