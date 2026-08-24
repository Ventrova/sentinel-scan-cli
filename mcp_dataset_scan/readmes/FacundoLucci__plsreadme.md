<p align="center">
  <img src="https://plsreadme.com/icon.png" alt="plsreadme" width="80" />
</p>

<h1 align="center">plsreadme</h1>

<p align="center">
  <strong>Paste markdown. Get a beautiful, shareable link. Done.</strong>
</p>

<p align="center">
  <a href="https://plsreadme.com">Website</a> ·
  <a href="https://www.npmjs.com/package/plsreadme-mcp">MCP Package</a> ·
  <a href="https://github.com/FacundoLucci/plsreadme/issues/new?labels=feature-request">Request a Feature</a>
</p>

<p align="center">
  <img src="https://img.shields.io/npm/v/plsreadme-mcp?style=flat-square&color=111827" alt="npm version" />
  <img src="https://img.shields.io/badge/Cloudflare_Workers-deployed-F38020?style=flat-square&logo=cloudflare&logoColor=white" alt="Cloudflare Workers" />
  <img src="https://img.shields.io/badge/MCP-compatible-10b981?style=flat-square" alt="MCP compatible" />
  <img src="https://img.shields.io/github/license/FacundoLucci/plsreadme?style=flat-square" alt="License" />
</p>

---

## The Problem

You wrote a README, a PRD, meeting notes, or an API doc in markdown. Now you need to share it with someone who doesn't have a markdown renderer, doesn't use GitHub, or just needs a clean link they can open in a browser.

**plsreadme** turns any markdown into a permanent, beautifully rendered web page in one step. No accounts. No sign-ups. No friction.

## ✨ Features

- **Instant sharing** — Paste markdown or upload a file, get a `plsrd.me` link
- **Beautiful rendering** — Clean typography, dark mode, mobile-responsive
- **Inline comments** — Readers can click any paragraph and leave feedback
- **Review mode (current vs timeline)** — Multi-version docs default to **Current draft** feedback with one-click access to full **Timeline** history
- **AI auto-formatting** — Throw raw text at it; it comes out as clean markdown
- **MCP server** — Share docs directly from Claude, Cursor, VS Code, or any MCP client
- **OpenClaw skill** — Available on [ClawHub](https://clawhub.com) for AI agent workflows
- **Short links** — Every doc gets a compact `plsrd.me/v/xxx` URL
- **Raw access** — Download the original `.md` file from any shared link
- **Version timeline + safe restore** — `/v/:id/versions` + `/v/:id/history` + archive-first restore API for fast rollback
- **Clerk auth foundation** — GitHub/Google sign-in wiring + Clerk-hosted email fallback + backend auth verification utilities
- **Ownership model (Phase 2)** — docs can be linked to a Clerk user (`owner_user_id`) while preserving anonymous flows
- **My Links dashboard (Phase 3)** — authenticated `/my-links` page with search/sort/pagination and quick copy/open actions
- **Legacy link claiming (Phase 4)** — signed-in users can claim older anonymous links by proving the original `admin_token`
- **Zero config website demo** — No account or API key needed to try it in the browser

## 🚀 Quick Start

### Web

Go to [plsreadme.com](https://plsreadme.com), paste your markdown, click share.

## Auth Paths And Rollout State

Recommendation order:

1. **Try in browser first** — fastest demo path, no MCP setup required.
2. **Use hosted remote MCP with browser login** when client support is verified.
3. **Use API key / local MCP fallback** when interactive login is unavailable.

Current rollout state:

| Journey | Status today | Ownership rule | Source tag |
| --- | --- | --- | --- |
| Anonymous website demo | Available now via browser-verified demo flow | `owner_user_id = NULL` until user later saves/claims the doc | `web_demo` |
| Signed-in website create | Available now | doc is created with the signed-in Clerk user as owner | `web_signed_in` |
| Hosted remote MCP with browser login | Available now in supported clients | creates owned docs for the signed-in user after browser login | `mcp_remote_login` |
| Hosted remote MCP with API key | Available now as the compatibility fallback | creates owned docs for the API key owner | `mcp_remote_api_key` |
| Local npm MCP with API key | Available now and recommended for local stdio setups | creates owned docs for the API key owner | `mcp_local_api_key` |
| Local npm MCP anonymous fallback | Still available only with explicit opt-in | remains anonymous unless later claimed/saved | `mcp_local_anonymous` |

Hosted remote MCP rollout notes:

- `https://plsreadme.com/mcp`
- `https://plsreadme.com/sse`

Those hosted remote MCP routes are live behind OAuth-protected browser login in code, including `/authorize`, `/oauth/token`, and `/oauth/register`.

Operational notes:

- D1 `doc_create_events` is the canonical create-attribution table across web, hosted MCP, and local MCP flows.
- `docs.raw_view_count` tracks every render hit, while `docs.view_count` is reserved for likely-human reads.
- See [`docs/runbooks/auth-surface-monitoring.md`](docs/runbooks/auth-surface-monitoring.md) for the production query set and response steps.

- access tokens last about `1 hour`
- refresh tokens last about `30 days`
- reconnecting the same client replaces the older grant
- signing out of the website does not revoke an existing editor grant by itself
- this repo is now wired to a dedicated Cloudflare Workers KV binding named `OAUTH_KV`

When browser login is not available in your client, create a personal API key from `/my-links` and use either the hosted remote header fallback or the local `npx -y plsreadme-mcp` package.

Website demo trust model today:

- anonymous website creates on `/api/create-link` require a short-lived browser verification grant
- signed-in website creates skip that grant and stay friction-light
- post-create UI now branches into `Save to my account`, `Connect your editor`, and `Copy link`

### API

```bash
curl -X POST https://plsreadme.com/api/render \
  -H "Content-Type: application/json" \
  -d '{"markdown": "# Hello World\n\nThis is my doc."}'
```

```json
{
  "id": "abc123def456",
  "url": "https://plsreadme.com/v/abc123def456",
  "raw_url": "https://plsreadme.com/v/abc123def456/raw",
  "admin_token": "sk_..."
}
```

Save the `admin_token` — you'll need it to edit or delete:

```bash
# Update
curl -X PUT https://plsreadme.com/v/abc123def456 \
  -H "Authorization: Bearer sk_..." \
  -H "Content-Type: application/json" \
  -d '{"markdown": "# Updated content"}'

# Delete
curl -X DELETE https://plsreadme.com/v/abc123def456 \
  -H "Authorization: Bearer sk_..."
```

#### Version timeline + safe restore

Use the timeline endpoint to review revision context during AI iteration cycles:

```bash
curl https://plsreadme.com/v/abc123def456/versions
```

```json
{
  "id": "abc123def456",
  "current_version": 5,
  "total_versions": 5,
  "versions": [
    { "version": 5, "is_current": true, "raw_url": "https://plsreadme.com/v/abc123def456/raw" },
    { "version": 4, "is_current": false, "raw_url": "https://plsreadme.com/v/abc123def456/raw?version=4" }
  ]
}
```

If an AI edit regresses the doc, restore a prior snapshot (archive-first, non-destructive):

```bash
curl -X POST https://plsreadme.com/v/abc123def456/restore \
  -H "Authorization: Bearer sk_..." \
  -H "Content-Type: application/json" \
  -d '{"version": 4}'
```

Restore is rate-limited similarly to updates (currently `60/hour` per actor key) to reduce abuse.

For docs owned by an authenticated Clerk user, update/delete/restore also require that owner session (to prevent cross-user mutation), while anonymous docs continue to work with `admin_token` only.

#### Review mode usage notes (Current draft first, Timeline on demand)

The document viewer now exposes comment review controls:

- **Current draft** — shows only comments tied to the latest doc version (default when a doc has multiple versions).
- **Timeline** — shows the full cross-version comment history.

You can fetch the same modes directly from the API:

```bash
# Latest-version comments only
curl "https://plsreadme.com/api/comments/abc123def456?view=current"

# Full timeline comments (default API behavior)
curl "https://plsreadme.com/api/comments/abc123def456?view=all"
```

Viewer links persist the mode in the URL for shareable review context:

- `https://plsreadme.com/v/abc123def456?view=current`
- `https://plsreadme.com/v/abc123def456?view=timeline`

To claim a legacy anonymous link into your signed-in account:

```bash
curl -X POST https://plsreadme.com/api/auth/claim-link \
  -H "Authorization: Bearer <clerk-session-jwt>" \
  -H "Content-Type: application/json" \
  -d '{"id":"abc123def456","adminToken":"sk_..."}'
```

### MCP (AI Editors)

Current recommendation today:

- use hosted remote MCP with browser login when your client supports it cleanly
- use personal API key fallback when remote auth is unavailable or awkward in that client
- use the local `plsreadme-mcp` package with `PLSREADME_API_KEY` for the safest stdio path

Connect your editor to plsreadme and share docs with natural language:

> *"Share this README as a plsreadme link"*
> *"Turn my PRD into a shareable page"*
> *"Make these meeting notes into a readable link"*

### MCP/agent auto-review loop with `/versions`

For iterative AI writing flows (draft → critique → revise), agents can consume `/v/:id/versions` as the source of truth:

1. Keep the canonical readable URL (`/v/:id`) for humans.
2. Poll `/v/:id/versions` between iterations.
3. Compare `current_version` to the last reviewed version.
4. If changed, fetch `raw_url` for the newest version and run review checks.
5. If quality regresses, optionally trigger `/v/:id/restore` with admin token + owner session.

This gives automation deterministic revision tracking without scraping HTML.

See [`docs/ai-iteration-versioning.md`](docs/ai-iteration-versioning.md) for a full playbook.

## 🔌 MCP Setup

### Client compatibility matrix

Current as of April 5, 2026:

| Client | Recommended path | Browser login support | API key fallback | Notes |
| --- | --- | --- | --- | --- |
| Claude Code | hosted remote MCP first | verified live | yes | best supported remote flow; local stdio with `PLSREADME_API_KEY` also works well |
| Cursor | hosted remote MCP first | documented, but build-dependent in practice | yes | use headers if your build does not surface the OAuth prompt |
| VS Code | hosted remote MCP when available | configuration exists, rollout varies by build | yes | `type: "http"` plus header fallback works when login UX is absent |
| Windsurf | hosted remote MCP when available | documented remote support | yes | use `serverUrl` + headers when browser auth is not exposed yet |
| Claude Desktop | local npm MCP | no verified remote browser flow here | yes | prefer stdio + `PLSREADME_API_KEY` |
| Raw HTTP / scripts | hosted remote header mode | no | yes | send `Authorization: Bearer $PLSREADME_API_KEY` directly |

### Hosted Remote Login (supported clients)

Claude Code:
```bash
claude mcp add --transport http plsreadme https://plsreadme.com/mcp
```

Cursor:
```json
{
  "mcpServers": {
    "plsreadme": {
      "url": "https://plsreadme.com/mcp"
    }
  }
}
```

VS Code:
```json
{
  "servers": {
    "plsreadme": {
      "type": "http",
      "url": "https://plsreadme.com/mcp"
    }
  }
}
```

Windsurf:
```json
{
  "mcpServers": {
    "plsreadme": {
      "serverUrl": "https://plsreadme.com/mcp"
    }
  }
}
```

Lifecycle notes:

- access token TTL is about `1 hour`
- refresh token TTL is about `30 days`
- reconnecting the same client replaces the older grant
- sign out ends the website session but does not automatically revoke an existing editor grant
- use `GET /api/auth/mcp-grants` and `DELETE /api/auth/mcp-grants/:grantId` to audit or revoke hosted editor grants

If your client supports browser login, prefer this path. It is the cleanest setup and keeps owned docs tied to your website account automatically.

### Hosted Remote API Key fallback

Create a personal API key from [https://plsreadme.com/my-links](https://plsreadme.com/my-links) first, then use one of these:

Claude Code:
```bash
claude mcp add --transport http \
  --header "Authorization: Bearer $PLSREADME_API_KEY" \
  plsreadme-api https://plsreadme.com/mcp
```

Cursor:
```json
{
  "mcpServers": {
    "plsreadme-api": {
      "url": "https://plsreadme.com/mcp",
      "headers": {
        "Authorization": "Bearer ${env:PLSREADME_API_KEY}"
      }
    }
  }
}
```

VS Code:
```json
{
  "inputs": [
    {
      "type": "promptString",
      "id": "plsreadme-api-key",
      "description": "plsreadme personal API key",
      "password": true
    }
  ],
  "servers": {
    "plsreadme-api": {
      "type": "http",
      "url": "https://plsreadme.com/mcp",
      "headers": {
        "Authorization": "Bearer ${input:plsreadme-api-key}"
      }
    }
  }
}
```

Windsurf:
```json
{
  "mcpServers": {
    "plsreadme-api": {
      "serverUrl": "https://plsreadme.com/mcp",
      "headers": {
        "Authorization": "Bearer ${env:PLSREADME_API_KEY}"
      }
    }
  }
}
```

Raw remote endpoint users:
```bash
curl -i https://plsreadme.com/mcp \
  -H "Authorization: Bearer $PLSREADME_API_KEY"
```

### Local npm fallback

Claude Code:
```bash
claude mcp add --transport stdio \
  --env PLSREADME_API_KEY=$PLSREADME_API_KEY \
  plsreadme -- npx -y plsreadme-mcp
```

Cursor:
Add to `~/.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "plsreadme": {
      "command": "npx",
      "args": ["-y", "plsreadme-mcp"],
      "env": {
        "PLSREADME_API_KEY": "${env:PLSREADME_API_KEY}"
      }
    }
  }
}
```

VS Code:
Add to `.vscode/mcp.json`:
```json
{
  "inputs": [
    {
      "type": "promptString",
      "id": "plsreadme-api-key",
      "description": "plsreadme personal API key",
      "password": true
    }
  ],
  "servers": {
    "plsreadme": {
      "command": "npx",
      "args": ["-y", "plsreadme-mcp"],
      "env": {
        "PLSREADME_API_KEY": "${input:plsreadme-api-key}"
      }
    }
  }
}
```

Claude Desktop:
Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "plsreadme": {
      "command": "npx",
      "args": ["-y", "plsreadme-mcp"],
      "env": {
        "PLSREADME_API_KEY": "<paste-your-personal-api-key>"
      }
    }
  }
}
```

Windsurf:
Add to `~/.codeium/windsurf/mcp_config.json`:
```json
{
  "mcpServers": {
    "plsreadme": {
      "command": "npx",
      "args": ["-y", "plsreadme-mcp"],
      "env": {
        "PLSREADME_API_KEY": "${env:PLSREADME_API_KEY}"
      }
    }
  }
}
```

Notes:

- local stdio now expects `PLSREADME_API_KEY` by default so new docs are owned
- explicit legacy anonymous mode still exists with `PLSREADME_ALLOW_ANONYMOUS=1`
- create your key from [https://plsreadme.com/my-links](https://plsreadme.com/my-links)

### Migrating existing anonymous MCP setups

If you already used `plsreadme-mcp` anonymously:

1. Create a personal API key from `/my-links`.
2. Add `PLSREADME_API_KEY` to your MCP client config.
3. Keep `PLSREADME_ALLOW_ANONYMOUS=1` only as a temporary compatibility crutch for old workflows.
4. Claim older anonymous links later with `/api/auth/claim-link` if you still have their `admin_token`.

The migration rule is simple:

- new automated/editor creates should be owned by default
- anonymous local MCP is now legacy-only and explicit
- the website demo path remains zero-setup even while editor auth gets stricter

### add-mcp
```bash
npx add-mcp plsreadme-mcp
```

### OpenClaw
```bash
clawhub install plsreadme
```

### Docker (for MCP registries / listing checks)
Build and run the stdio MCP server in a clean container:

```bash
docker build -t plsreadme-mcp:local .
docker run --rm -i plsreadme-mcp:local
```

The containerized server uses stdio (no ports, no env vars required).

## 🛠 MCP Tools

| Tool | What it does |
|------|-------------|
| `plsreadme_share_file` | Share a local file by path → returns shareable link. Re-sharing updates the same link. |
| `plsreadme_share_text` | Share markdown or plain text directly → returns shareable link |
| `plsreadme_update` | Update an existing doc with new content (by ID or file path) |
| `plsreadme_delete` | Delete a shared doc permanently (by ID or file path) |
| `plsreadme_list` | List all documents you've shared from this project |

**Prompts:**
- `share-document` — Guided flow to share content as a readable link
- `refactor-and-share` — Uses your AI model to refactor raw text into polished markdown, then shares it

Plain text input? No problem — the MCP auto-structures it into markdown, or you can use the `refactor-and-share` prompt to leverage your AI's reasoning for a polished result.

### .plsreadme Record File

The MCP server tracks your shared documents in a `.plsreadme` JSON file in your project root. This stores document IDs, URLs, and admin tokens needed for editing and deleting.

**⚠️ Add `.plsreadme` to your `.gitignore`** — it contains admin tokens. The tool will warn you if it's missing.

## 🏗 Architecture

Built on Cloudflare's edge stack for speed everywhere:

```
┌─────────────┐     ┌──────────────────┐     ┌─────────┐
│  Web / API  │────▶│  Cloudflare      │────▶│   R2    │
│  MCP Client │     │  Workers (Hono)  │     │ (docs)  │
└─────────────┘     └──────────────────┘     └─────────┘
                           │
                    ┌──────┴──────┐
                    │     D1      │
                    │ (metadata)  │
                    └─────────────┘
```

- **Hono** — Lightweight web framework on Workers
- **Cloudflare D1** — SQLite at the edge for metadata, comments, analytics
- **Cloudflare R2** — Object storage for markdown documents
- **Durable Objects** — Stateful MCP server endpoint
- **Workers AI** — Optional fallback for text-to-markdown conversion

## 📁 Project Structure

```
plsreadme/
├── worker/
│   ├── index.ts              # Main worker entry
│   ├── auth.ts               # Clerk JWT verification utilities/middleware
│   ├── routes/
│   │   ├── auth.ts           # Auth config/session/protected identity endpoints
│   │   ├── docs.ts           # Document creation & rendering
│   │   ├── comments.ts       # Inline commenting system
│   │   ├── convert.ts        # AI text→markdown conversion
│   │   ├── analytics.ts      # View tracking
│   │   ├── links.ts          # Short link handling
│   │   └── waitlist.ts       # Waitlist & notifications
│   ├── mcp-agent.ts          # Remote MCP server (Durable Object)
│   └── types.ts              # TypeScript types
├── packages/
│   └── mcp/                  # npm package: plsreadme-mcp
│       └── src/index.ts      # MCP server (stdio transport)
├── public/                   # Static assets & landing pages
├── db/
│   └── schema.sql            # D1 database schema
├── docs/
│   ├── ai-iteration-versioning.md # Version timeline/restore patterns for human + agent loops
│   ├── auth-clerk.md              # Auth setup + environment checklist
│   └── runbooks/
│       └── legacy-link-claim-rollout.md
├── skill/
│   └── plsreadme/            # OpenClaw agent skill
└── wrangler.jsonc             # Cloudflare Workers config
```

## 🔧 Development

```bash
# Install dependencies
npm install

# Run locally
npm run dev

# Deploy
npm run deploy

# Bootstrap schema (fresh local DB)
npm run db:migrate:local

# Audit unapplied migrations (remote + local)
npm run db:migrations:status

# Apply migration files explicitly
npm run db:migrations:apply        # remote
npm run db:migrations:apply:local  # local
```

Ownership phase migration notes:
- `wrangler.jsonc` points `migrations_dir` to `db/migrations`, so migration status is auditable with explicit list/apply commands.
- Apply `db/migrations/004_owner_user_id.sql` in existing environments before relying on ownership filters.
- Apply `db/migrations/007_doc_attribution_telemetry.sql` before relying on `doc_create_events` or `raw_view_count`.
- Legacy rows are intentionally backfilled as `owner_user_id = NULL` (anonymous/public behavior preserved).
- Write routes still run a safe ownership schema ensure step (duplicate-column tolerant) for mixed-env rollout safety.
- See [`docs/migrations.md`](docs/migrations.md) for the explicit audit/apply workflow.

### MCP package release
`plsreadme-mcp` is published from `packages/mcp` by pushing an `mcp-v*` tag (see `.github/workflows/publish-mcp.yml`).

```bash
cd packages/mcp
npm version patch   # or minor/major
cd ../..
git add packages/mcp/package.json packages/mcp/package-lock.json
VERSION=$(node -p "require('./packages/mcp/package.json').version")
git commit -m "chore(mcp): release v${VERSION}"
git tag "mcp-v${VERSION}"
# push commit + tag from your machine to trigger npm publish workflow
```

### Environment Variables

Start from `.env.example` and set values in your local/dev/prod environment.

> Cloudflare tip: non-sensitive values can live in `vars`; sensitive values should be set with `wrangler secret put`.

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | No | OpenAI key for `/api/convert` text→markdown |
| `DISCORD_WEBHOOK_URL` | No | Waitlist signup notifications |
| `DISCORD_LINK_WEBHOOK_URL` | No | New link creation notifications |
| `RESEND_API_KEY` | No | Email notifications |
| `NOTIFICATION_EMAIL` | No | Email recipient for notifications |
| `CLERK_PUBLISHABLE_KEY` | For auth | Clerk publishable key for frontend auth wiring (social + email fallback) |
| `CLERK_JWT_ISSUER` | For auth | Clerk JWT issuer used by worker verification |
| `CLERK_JWT_AUDIENCE` | Optional | Expected audience claim for Clerk JWTs |
| `CLERK_SIGN_IN_URL` | Optional | Clerk-hosted sign-in URL hint (default `/sign-in`) |
| `CLERK_SIGN_UP_URL` | Optional | Clerk-hosted sign-up URL hint (default `/sign-up`) |
| `CLERK_SECRET_KEY` | Optional | Reserved for future server-side Clerk integrations |

If OAuth credentials are not configured yet, users can still click **Sign in** / **Use email instead** and complete auth through the Clerk-hosted email flow immediately.

Frontend auth shell notes:
- `/app.html` and `/my-links` use `public/clerk-auth-shell.js` (Clerk-native browser SDK wiring).
- Authenticated frontend API calls should read bearer tokens through `window.plsreadmeGetAuthToken()`.

The core sharing functionality still requires **zero configuration**. Clerk auth, AI conversion, and notifications are opt-in.

For the full auth setup checklist, see [`docs/auth-clerk.md`](docs/auth-clerk.md).
For rollout + smoke checks, see [`docs/runbooks/mcp-auth-rollout-checklist.md`](docs/runbooks/mcp-auth-rollout-checklist.md).

## 📊 Limits

| Limit | Value |
|-------|-------|
| Max document size | 200 KB |
| Upload rate limit | 30/hour per actor key |
| Update/restore rate limit | 60/hour per actor key |
| AI convert rate limit | 10/hour per IP |
| Link lifetime | Permanent |

## 🤝 Contributing

Feature ideas? Bug reports? [Open an issue](https://github.com/FacundoLucci/plsreadme/issues/new?labels=feature-request).

PRs welcome for bug fixes and improvements.

## 📄 License

MIT — do whatever you want with it.

---

<p align="center">
  <sub>Built by <a href="https://github.com/FacundoLucci">Facundo Lucci</a></sub>
</p>
