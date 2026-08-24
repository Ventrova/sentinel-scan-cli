# ClawAIMail

**Email infrastructure for AI agents.**

[![npm version](https://img.shields.io/npm/v/clawaimail.svg)](https://www.npmjs.com/package/clawaimail)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-clawaimail.com-brightgreen.svg)](https://clawaimail.com/docs)

---

ClawAIMail gives AI agents their own email addresses and full programmatic control over sending, receiving, and managing email. Built for developers who need reliable email primitives in agentic workflows.

## Features

- **REST API** -- Send, receive, search, and manage emails with a simple JSON API.
- **MCP Server** -- First-class Model Context Protocol server for Claude, Cursor, and other MCP-compatible clients.
- **WebSocket Streaming** -- Real-time email events pushed to your agent as they happen.
- **Webhooks** -- HTTP callbacks on incoming mail, delivery status, and other events.
- **Custom Domains** -- Bring your own domain or use a `@clawaimail.com` address.
- **SDKs** -- Official Node.js and Python SDKs for rapid integration.

## Quick Start

### Node.js

```bash
npm install clawaimail
```

```javascript
const { ClawAIMail } = require("clawaimail");

const client = new ClawAIMail({ apiKey: process.env.CLAWAIMAIL_API_KEY });

// Create a mailbox for your agent
const mailbox = await client.mailboxes.create({
  name: "support-agent",
  domain: "clawaimail.com",
});

// Send an email
await client.emails.send({
  from: mailbox.address,
  to: "user@example.com",
  subject: "Hello from my AI agent",
  text: "This email was sent by an autonomous agent.",
});

// List incoming emails
const inbox = await client.emails.list({
  mailbox: mailbox.id,
  unread: true,
});
```

### Python

```bash
pip install clawaimail
```

```python
from clawaimail import ClawAIMail

client = ClawAIMail(api_key="your-api-key")

# Create a mailbox
mailbox = client.mailboxes.create(name="support-agent", domain="clawaimail.com")

# Send an email
client.emails.send(
    from_address=mailbox.address,
    to="user@example.com",
    subject="Hello from my AI agent",
    text="This email was sent by an autonomous agent.",
)

# List incoming emails
inbox = client.emails.list(mailbox=mailbox.id, unread=True)
```

## MCP Server

ClawAIMail ships an MCP server so that Claude, Cursor, and other MCP-compatible clients can use email tools directly.

### Claude Desktop

Add the following to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "clawaimail": {
      "command": "npx",
      "args": ["-y", "clawaimail-mcp"],
      "env": {
        "CLAWAIMAIL_API_KEY": "your-api-key"
      }
    }
  }
}
```

### Cursor

Add to your `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "clawaimail": {
      "command": "npx",
      "args": ["-y", "clawaimail-mcp"],
      "env": {
        "CLAWAIMAIL_API_KEY": "your-api-key"
      }
    }
  }
}
```

Once configured, the agent can call tools like `send_email`, `read_inbox`, `search_emails`, and `create_mailbox` without any additional code.

## Self-Hosting

ClawAIMail can be self-hosted for full control over your email infrastructure.

```bash
# Clone the repository
git clone https://github.com/joansongjr/clawaimail.git
cd clawaimail

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with your SMTP credentials, database URL, and API keys

# Run database migrations
npm run db:migrate

# Start the server
npm start
```

The server will be available at `http://localhost:3000` by default. See the [self-hosting docs](https://clawaimail.com/docs/self-hosting) for production deployment guides (Docker, Railway, Fly.io).

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/v1/emails/send` | Send an email |
| `GET` | `/v1/emails` | List emails for a mailbox |
| `GET` | `/v1/emails/:id` | Get a single email by ID |
| `DELETE` | `/v1/emails/:id` | Delete an email |
| `POST` | `/v1/mailboxes` | Create a new mailbox |
| `GET` | `/v1/mailboxes` | List all mailboxes |
| `DELETE` | `/v1/mailboxes/:id` | Delete a mailbox |
| `POST` | `/v1/webhooks` | Register a webhook |
| `GET` | `/v1/webhooks` | List registered webhooks |
| `DELETE` | `/v1/webhooks/:id` | Remove a webhook |
| `GET` | `/v1/domains` | List verified domains |
| `POST` | `/v1/domains/verify` | Verify a custom domain |
| `GET` | `/v1/ws` | WebSocket connection for real-time events |

Full API reference: [clawaimail.com/docs/api](https://clawaimail.com/docs/api)

## Pricing

| | Free | Starter | Pro | Business |
|---|---|---|---|---|
| **Price** | $0/mo | $5/mo | $29/mo | $99/mo |
| **Emails/month** | 100 | 5,000 | 50,000 | 500,000 |
| **Mailboxes** | 1 | 10 | 100 | Unlimited |
| **Custom domains** | -- | 1 | 5 | Unlimited |
| **Webhooks** | 1 | 5 | 25 | Unlimited |
| **WebSocket** | -- | Yes | Yes | Yes |
| **Support** | Community | Email | Priority | Dedicated |

Self-hosted deployments are free and unlimited. See [clawaimail.com/pricing](https://clawaimail.com/pricing) for details.

## Links

- [Documentation](https://clawaimail.com/docs)
- [Node.js SDK](https://www.npmjs.com/package/clawaimail)
- [Python SDK](https://pypi.org/project/clawaimail/)
- [Website](https://clawaimail.com)
- [Status Page](https://status.clawaimail.com)

## License

MIT -- see [LICENSE](./LICENSE) for details.

