<div align="center">
  <img src="https://convertica.net/static/favicon-192x192.png" width="88" height="88" alt="Convertica" />

  # Convertica MCP Server

  Convert files without leaving your AI assistant. Connect Claude, Cursor, Windsurf or any [MCP](https://modelcontextprotocol.io) client to [Convertica](https://convertica.net) and its 35+ document and image conversion tools.

  [![npm version](https://img.shields.io/npm/v/convertica-mcp?color=cb3837&logo=npm)](https://www.npmjs.com/package/convertica-mcp)
  [![npm downloads](https://img.shields.io/npm/dm/convertica-mcp?color=cb3837)](https://www.npmjs.com/package/convertica-mcp)
  [![License: MIT](https://img.shields.io/badge/license-MIT-blue)](./LICENSE)
  [![MCP Registry](https://img.shields.io/badge/MCP%20Registry-net.convertica%2Fmcp-6E56CF)](https://registry.modelcontextprotocol.io)
  [![convertica-mcp MCP server](https://glama.ai/mcp/servers/convertica-net/convertica-mcp/badges/score.svg)](https://glama.ai/mcp/servers/convertica-net/convertica-mcp)

  [Website](https://convertica.net) · [API docs](https://convertica.net/api/) · [npm](https://www.npmjs.com/package/convertica-mcp)
</div>

```
"Convert ~/Downloads/report.pdf to Word"
"Merge these three PDFs and compress the result"
"Turn this HEIC photo into a JPG"
"Render https://example.com as a PDF"
```

## MCP tools

The server exposes two tools.

### list_converters

Lists all 35+ Convertica converters with their file fields and options. Call this first to find the right `tool` slug for convert_file. Takes no input.

```json
{ "type": "object", "properties": {} }
```

### convert_file

Runs one of convertica.net's 35+ conversion tools on local file(s) and saves the result next to the input (or into output_dir). Requires authentication via the CONVERTICA_API_KEY env var.

```json
{
  "type": "object",
  "required": ["tool"],
  "properties": {
    "tool": { "type": "string", "description": "Converter slug from list_converters, e.g. pdf-to-word or pdf-organize/merge" },
    "files": { "type": "array", "items": { "type": "string" }, "description": "Absolute paths of input file(s); order matters for multi-file tools" },
    "options": { "type": "object", "description": "Tool-specific options as listed by list_converters, e.g. {angle: 90}" },
    "output_dir": { "type": "string", "description": "Directory to save the result (default: alongside the first input file)" }
  }
}
```

Supported conversions include: **PDF ⇄ Word / Excel / PowerPoint / JPG / HTML / Markdown / Text / EPUB**, **PDF → PDF/A**, **HTML / URL → PDF**, **merge / split / compress / rotate / crop / watermark / sign / protect / unlock PDF**, **image convert / optimize / HEIC → JPG·PNG·PDF**, and more. Full list via `list_converters` or at [convertica.net](https://convertica.net/).

## Setup and API key

You need a Convertica API key: subscribe at [convertica.net/pricing](https://convertica.net/pricing/), then create a key at [convertica.net/users/api-keys](https://convertica.net/users/api-keys/). API docs: [convertica.net/api/docs](https://convertica.net/api/docs/).

### Claude Code

```bash
claude mcp add convertica -e CONVERTICA_API_KEY=cvk_live_... -- npx -y convertica-mcp
```

### Claude Desktop / Cursor / Windsurf

```json
{
  "mcpServers": {
    "convertica": {
      "command": "npx",
      "args": ["-y", "convertica-mcp"],
      "env": { "CONVERTICA_API_KEY": "cvk_live_..." }
    }
  }
}
```

## Usage notes

- Files are read from and written to your local disk; results are saved next to the input file unless you pass `output_dir`.
- Conversions run synchronously over HTTPS; processed files are deleted from Convertica's servers right after the response ([details](https://convertica.net/privacy/)).
- API calls are metered against your plan's monthly quota; failed calls are not counted.

## Local development

```bash
npm install
npm run smoke                        # protocol check, no key needed
CONVERTICA_API_KEY=... npm run smoke # + one real conversion
```

## License and credits

MIT. Not affiliated with Anthropic; "Convertica" is the service behind [convertica.net](https://convertica.net).
