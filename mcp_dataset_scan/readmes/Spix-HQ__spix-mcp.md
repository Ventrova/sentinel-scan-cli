# spix-mcp

> MCP server for Spix — give any MCP-compatible AI client a phone number, an inbox, and a voice.

[![spix-mcp MCP server](https://glama.ai/mcp/servers/Spix-HQ/spix-mcp/badges/score.svg)](https://glama.ai/mcp/servers/Spix-HQ/spix-mcp)
[![PyPI](https://img.shields.io/pypi/v/spix-mcp)](https://pypi.org/project/spix-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Docs](https://img.shields.io/badge/docs-docs.spix.sh%2Fmcp-blue)](https://docs.spix.sh/mcp)

`spix-mcp` is a standalone [Model Context Protocol](https://modelcontextprotocol.io) server that exposes Spix's communications infrastructure — phone calls, email, contacts, analytics — as MCP tools and resources.

Connect it to Claude Desktop, Cursor, or any MCP-compatible client and your AI can literally pick up the phone.

---

## Install

```bash
# via pip
pip install spix-mcp

# via uvx (no install needed)
uvx spix-mcp
```

The Spix CLI must also be installed and authenticated:

```bash
curl -fsSL https://spix.sh/install.sh | sh
spix auth login
```

---

## Quick setup: Claude Desktop

The fastest way — use the built-in installer from the Spix CLI:

```bash
spix mcp install claude
```

This writes the correct config to `~/Library/Application Support/Claude/claude_desktop_config.json` automatically. Restart Claude Desktop and Spix tools appear immediately.

Or configure manually in `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "spix": {
      "command": "uvx",
      "args": ["spix-mcp"],
      "env": {
        "SPIX_API_KEY": "spix_live_sk_your_key_here"
      }
    }
  }
}
```

Get your API key from [app.spix.sh/settings/api-keys](https://app.spix.sh/settings/api-keys).

---

## Quick setup: Cursor

```bash
spix mcp install cursor
```

Or add to your Cursor MCP config manually with the same JSON structure as above.

---

## What your AI can do

Once connected, your AI client has access to **43 tools** (safe profile) or **49 tools** (full profile) across all Spix capabilities:

### Phone calls

| Tool | Description |
|------|-------------|
| `spix_call_create` | Make an outbound AI phone call |
| `spix_call_show` | Get call status and metadata |
| `spix_call_list` | List recent calls |
| `spix_call_transcript` | Get full call transcript |
| `spix_call_summary` | Get call summary + extracted fields |
| `spix_call_cancel` | Cancel an in-progress call *(full profile)* |

### Email

| Tool | Description |
|------|-------------|
| `spix_email_send` | Send an email from your Spix inbox |
| `spix_email_reply` | Reply to a received email |
| `spix_email_list` | List emails in your inbox |

### SMS

| Tool | Description |
|------|-------------|
| `spix_sms_send` | Send an SMS message |
| `spix_sms_list` | List SMS messages |
| `spix_sms_thread` | Get an SMS conversation thread |

### Playbooks

| Tool | Description |
|------|-------------|
| `spix_playbook_create` | Create a call or SMS playbook |
| `spix_playbook_list` | List all playbooks |
| `spix_playbook_show` | Get playbook details |
| `spix_playbook_update` | Update playbook settings |
| `spix_playbook_clone` | Clone an existing playbook |
| `spix_playbook_pause` | Pause a playbook |
| `spix_playbook_resume` | Resume a paused playbook |
| `spix_playbook_delete` | Delete a playbook *(full profile)* |
| `spix_playbook_voice_list` | List available voices |
| `spix_playbook_language_list` | List supported languages |
| `spix_playbook_emotion_list` | List available emotions |
| `spix_playbook_rule_add` | Add a rule to a playbook |
| `spix_playbook_rule_list` | List playbook rules |
| `spix_playbook_rule_remove` | Remove a playbook rule |
| `spix_playbook_rule_clear` | Clear all playbook rules |

### Contacts

| Tool | Description |
|------|-------------|
| `spix_contact_create` | Create a contact |
| `spix_contact_show` | Get contact details |
| `spix_contact_list` | List contacts |
| `spix_contact_history` | Get communication history with a contact |
| `spix_contact_summary` | Get AI-generated contact summary |
| `spix_contact_tag` | Add tags to a contact |

### Phone numbers

| Tool | Description |
|------|-------------|
| `spix_phone_list` | List your phone numbers |
| `spix_phone_show` | Get phone number details |
| `spix_phone_bind` | Bind a number to a playbook |
| `spix_phone_unbind` | Remove a binding |
| `spix_phone_release` | Release a phone number *(full profile)* |

### Auth & API keys

| Tool | Description |
|------|-------------|
| `spix_auth_whoami` | Check current authentication |
| `spix_auth_key_list` | List API keys |
| `spix_auth_key_create` | Create a new API key |
| `spix_auth_key_revoke` | Revoke an API key *(full profile)* |

### Billing & analytics

| Tool | Description |
|------|-------------|
| `spix_billing_status` | Get billing plan status |
| `spix_billing_credits` | Check credit balance |
| `spix_billing_credits_history` | Get credit usage history |
| `spix_billing_plan_set` | Change billing plan *(full profile)* |

### Webhooks

| Tool | Description |
|------|-------------|
| `spix_webhook_endpoint_create` | Register a webhook endpoint |
| `spix_webhook_endpoint_list` | List webhook endpoints |
| `spix_webhook_subscription_create` | Subscribe to events |

---

## Resources (readable state)

The MCP server also exposes live-readable resources:

```
resource://calls/{id}/transcript     — Call transcript
resource://calls/{id}/summary        — Call summary + extraction
resource://sms/{id}/thread           — SMS thread
resource://playbook/{id}             — Playbook details
resource://contact/{id}              — Contact details
resource://contact/{id}/history      — Contact history
resource://phone/{id}/route          — Phone number routing
resource://billing/credits           — Credit balance
resource://billing                   — Billing overview
```

---

## Tool profiles

| Profile | Tools | Description |
|---------|-------|-------------|
| `safe` (default) | 43 | Excludes destructive operations: key revoke, phone release, playbook delete, call cancel, plan changes |
| `full` | 49 | All tools including destructive and billing operations |

For production deployments, `safe` is recommended. Use `full` only for trusted clients.

---

## Configuration

All configuration is via environment variables:

| Variable | Required | Description |
|----------|----------|-------------|
| `SPIX_API_KEY` | Yes | Your Spix API key |
| `SPIX_DEFAULT_PLAYBOOK` | No | Default playbook ID for calls |
| `SPIX_SESSION_NAME` | No | Session name for audit logging |
| `SPIX_TOOL_PROFILE` | No | `safe` (default) or `full` |

### Scoped access example

Restrict what your agent can access:

```json
{
  "mcpServers": {
    "spix": {
      "command": "uvx",
      "args": ["spix-mcp"],
      "env": {
        "SPIX_API_KEY": "spix_live_sk_your_key_here",
        "SPIX_DEFAULT_PLAYBOOK": "plb_call_abc123",
        "SPIX_SESSION_NAME": "sales-bot",
        "SPIX_TOOL_PROFILE": "safe"
      }
    }
  }
}
```

---

## Example: Ask Claude to make a call

Once configured, you can ask Claude (or any connected client) directly:

> "Call +19175550123 using the prospect-qualifier playbook and tell me what they said."

Claude will use `spix_call_create`, monitor the call, then call `spix_call_summary` to return the result — without you writing any code.

---

## How it works

```
Your Agent (Claude, Cursor, etc.)
    ↓ MCP tool call
Spix MCP Server (this package)
    ↓ HTTP API call
Spix Backend (api.spix.sh)
    ↓ Carrier APIs
Phone call / Email / SMS
```

The MCP server is a thin bridge between the MCP protocol and the Spix REST API. All business logic runs server-side.

### Voice calls

When your agent calls `spix_call_create`, Spix:

1. Dials the number via Telnyx/Twilio
2. Uses **Deepgram Nova-3** for real-time speech recognition
3. Uses **Claude** for conversation turn generation
4. Uses **Cartesia Sonic-3** for text-to-speech
5. Records the call and generates a transcript + summary

Your agent can then read the transcript and summary via `spix_call_transcript` and `spix_call_summary`.

---

## Relationship to spix CLI

`spix-mcp` is the standalone MCP server package. The full [Spix CLI](https://github.com/Spix-HQ/spix-cli) includes the MCP server built in (`spix mcp serve`) alongside all other Spix commands.

Use `spix-mcp` if you only need the MCP server (e.g. for Claude Desktop integration without installing the full CLI). Use the full CLI if you want all Spix commands available in your terminal.

---

## Requirements

- Python 3.10+
- Spix account (free Sandbox for email; Agent plan for calls)
- API key from [app.spix.sh](https://app.spix.sh)

---

## Links

- **Spix — AI agent communications infrastructure:** [spix.sh](https://spix.sh)
- **Dashboard:** [app.spix.sh](https://app.spix.sh)
- **Docs — MCP server reference:** [docs.spix.sh/mcp](https://docs.spix.sh/mcp)
- **Spix CLI — phone calls, SMS, email from the terminal:** [Spix-HQ/spix-cli](https://github.com/Spix-HQ/spix-cli)
- **PyPI:** [pypi.org/project/spix-mcp](https://pypi.org/project/spix-mcp/)
- **Recipes — ready-to-use agent workflows:** [spix.sh/recipes](https://spix.sh/recipes)
- **Blog — tutorials and guides:** [spix.sh/blog](https://spix.sh/blog)
- **X/Twitter:** [@spixhq](https://x.com/spixhq)

---

## License

MIT — see [LICENSE](LICENSE)
