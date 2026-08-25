#!/usr/bin/env python3
"""Sentinel Scan MCP server - stdio wrapper around scan_mcp_manifest() from
sentinel_scan.py (sentinel_scan.py:1126).

Exposes one tool, `scan_mcp_manifest`, that runs the same static heuristic
scanner the CLI's `sentinel-scan mcp` subcommand uses and returns the
identical OWASP-mapped findings dict - no server execution, no network
calls, no LLM calls. This is the uvx/PyPI counterpart to the Node stdio
server in bin/sentinel-scan-mcp-server.js; both call into the same
heuristics (this one directly, the Node one via the JS port verified at
100% parity, see sentinel-scan-node-port-100pct memory).
"""

from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from sentinel_scan import scan_mcp_manifest

server = FastMCP(name="sentinel-scan-mcp")


@server.tool(
    name="scan_mcp_manifest",
    description=(
        "Runs a static, offline heuristic security scan (OWASP MCP Top 10 mapped) "
        "over an MCP server manifest/config (tools[] + mcpServers{}/servers{} JSON, "
        "the same shape as a client config or an mcp.json tool list). Detects tool "
        "description/name injection, excessive-agency schemas, command injection "
        "risk, hardcoded credentials, unpinned/unsigned sources, wildcard scopes, "
        "missing human-in-the-loop confirmation, hidden unicode instructions, "
        "cross-origin exfiltration, DoS/resource-exhaustion risk, and tool "
        "definition drift (vs. an optional prior-scan baseline). Does not execute "
        "any server or tool - pure static analysis of the manifest JSON."
    ),
)
def scan_mcp_manifest_tool(
    manifest: dict[str, Any],
    baseline: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """manifest: MCP manifest/config object, e.g. {"tools": [...]} and/or
    {"mcpServers": {...}} / {"servers": {...}} as found in an mcp.json or
    client config file. baseline: optional prior scan output (as previously
    returned by this tool) to diff against for tool_definition_drift detection."""
    return scan_mcp_manifest(manifest, baseline)


def main() -> None:
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
