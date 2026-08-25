#!/usr/bin/env python3
"""End-to-end stdio self-test for sentinel_scan_mcp_server.py (the uvx/PyPI
MCP server entrypoint), mirroring scripts/test-mcp-server.js for the Node
build. Starts the server as a subprocess over stdio, lists its tools, and
calls scan_mcp_manifest against the built-in demo manifest.

Requires the `mcp` package (pip install "sentinel-scan-cli[mcp-server]" or
pip install mcp). Run with: python scripts/test-mcp-server.py
"""
import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from sentinel_scan import DEMO_MCP_MANIFEST

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
SERVER_SCRIPT = os.path.join(REPO_ROOT, "sentinel_scan_mcp_server.py")


async def main():
    params = StdioServerParameters(command=sys.executable, args=[SERVER_SCRIPT])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            tool_names = [t.name for t in tools.tools]
            print("tools:", tool_names)
            if "scan_mcp_manifest" not in tool_names:
                raise RuntimeError(f"expected scan_mcp_manifest in tool list, got {tool_names}")

            result = await session.call_tool(
                "scan_mcp_manifest", {"manifest": DEMO_MCP_MANIFEST}
            )
            text = next(c.text for c in result.content if c.type == "text")
            parsed = json.loads(text)
            print("summary:", parsed["summary"])
            print("num findings returned:", len(parsed["results"]))
            if parsed["summary"]["num_findings"] != len(parsed["results"]):
                raise RuntimeError("mismatch between summary.num_findings and results.length")
            if parsed["summary"]["num_findings"] == 0:
                raise RuntimeError("expected demo manifest to produce findings")

    print("OK: MCP server end-to-end test passed")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as err:  # noqa: BLE001 - self-test, want a clear non-zero exit
        print("FAILED:", err, file=sys.stderr)
        sys.exit(1)
