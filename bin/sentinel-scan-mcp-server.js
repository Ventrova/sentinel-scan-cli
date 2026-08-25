#!/usr/bin/env node
'use strict';

/**
 * Sentinel Scan MCP server - stdio wrapper around scanMcpManifest() from
 * bin/sentinel-scan.js (the JS port of sentinel_scan.py:scan_mcp_manifest,
 * verified at 100% parity, see sentinel-scan-node-port-100pct memory).
 *
 * Exposes one tool, `scan_mcp_manifest`, that runs the same static
 * heuristic scanner the CLI's `sentinel-scan mcp` subcommand uses and
 * returns the identical OWASP-mapped findings JSON - no server execution,
 * no network calls, no LLM calls.
 */

const { McpServer } = require('@modelcontextprotocol/sdk/server/mcp.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const { z } = require('zod');
const { scanMcpManifest, VERSION } = require('./sentinel-scan.js');

const server = new McpServer({
  name: 'sentinel-scan-mcp',
  version: VERSION,
});

server.registerTool(
  'scan_mcp_manifest',
  {
    title: 'Scan MCP manifest for security findings',
    description:
      'Runs a static, offline heuristic security scan (OWASP MCP Top 10 mapped) ' +
      'over an MCP server manifest/config (tools[] + mcpServers{}/servers{} JSON, ' +
      'the same shape as a client config or an mcp.json tool list). Detects tool ' +
      'description/name injection, excessive-agency schemas, command injection ' +
      'risk, hardcoded credentials, unpinned/unsigned sources, wildcard scopes, ' +
      'missing human-in-the-loop confirmation, hidden unicode instructions, ' +
      'cross-origin exfiltration, DoS/resource-exhaustion risk, and tool ' +
      'definition drift (vs. an optional prior-scan baseline). Does not execute ' +
      'any server or tool - pure static analysis of the manifest JSON.',
    inputSchema: {
      manifest: z
        .record(z.any())
        .describe(
          'MCP manifest/config object, e.g. { "tools": [...] } and/or ' +
            '{ "mcpServers": {...} } / { "servers": {...} } as found in an ' +
            'mcp.json or client config file.'
        ),
      baseline: z
        .record(z.any())
        .optional()
        .describe(
          'Optional prior scan output (as previously returned by this tool) ' +
            'to diff against for tool_definition_drift detection.'
        ),
    },
  },
  async ({ manifest, baseline }) => {
    const out = scanMcpManifest(manifest, baseline);
    return {
      content: [{ type: 'text', text: JSON.stringify(out, null, 2) }],
      structuredContent: out,
    };
  }
);

async function runMcpServer() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

if (require.main === module) {
  runMcpServer().catch((err) => {
    console.error('sentinel-scan-mcp fatal error:', err);
    process.exit(1);
  });
}

module.exports = { runMcpServer };
