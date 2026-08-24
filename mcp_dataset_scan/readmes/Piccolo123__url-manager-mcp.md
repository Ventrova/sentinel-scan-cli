<!-- mcp-name: io.github.Piccolo123/url-manager-mcp -->

# URL Manager MCP Server

[![url-manager-mcp MCP server](https://glama.ai/mcp/servers/Piccolo123/url-manager-mcp/badges/score.svg)](https://glama.ai/mcp/servers/Piccolo123/url-manager-mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/Piccolo123/url-manager-mcp/blob/main/LICENSE)

[English](./README.md) | [简体中文](./README.zh-CN.md)

**Deliver results as beautiful cards, not raw link dumps.** A Model Context Protocol server for saving, organizing, searching, and sharing web resources — cross-device sync, categories, tags, full-text search, batch operations, and team sharing. 21 tools with auto-registration so no manual setup is required.

> 📖 **Usage patterns and best practices → [URL Manager Skill](https://github.com/Piccolo123/url-manager/blob/main/SKILL.md)**

## What This Tool Gives Humans

The content human users want to save is everywhere — a YouTube workout video, an Amazon gear link, a Substack training plan — scattered across platforms with no connection.

**URL Manager fixes this.** Paste any link from any platform. AI auto-identifies the content and suggests a category — confirm and it's a footprint. All saves flow into one platform-agnostic library, organized and always findable. Then **share in one click** — hand your curated knowledge base to your team, and everyone stays in sync.

## System Concepts

### Footprint (the fundamental unit)

A structured, searchable record — a web link, a plain-text note, an idea, or anything worth saving.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Permanent unique identifier — use for all operations |
| `url` | string (8192) | Original link. **Can be empty** for text-only footprints |
| `title` | string (512) | Short title |
| `description` | string (1024) | Additional context or notes |
| `content_type` | string (50) | Free text (e.g. `article`, `video`, `image`). Use `list_content_types()` to see existing values |
| `category_ids` | list[int] | Which categories this belongs to — **you assign** |
| `tag_names` | list[str] | Free-form keywords — **you assign** |

A footprint can belong to **multiple categories simultaneously**.

### Category (a named label)

Like a folder, but a footprint can be in several at once.

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Permanent numeric identifier — always reference by ID |
| `name` | string (50) | Display name |
| `mode` | string \| null | `null` = personal, `"cocreate"` = shared co-edit, `"subscribe"` = shared read-only |

### Category Set (a workspace)

A container that groups related categories. Every user starts with "My Categories" (personal) and "Shared Categories" (shared container).

### Data hierarchy

```
Category Sets (workspaces)
  └── Categories (labels like "Shopping", "Learning")
        └── Footprints
             └── Tags (free-form keywords)
```

### Personal vs Shared

| | Personal | Shared |
|---|---|---|
| `mode` | `null` | `"cocreate"` or `"subscribe"` |
| Visible to | Only you | You + invited members |
| Members & invite links | No | Yes |

**Cocreate** — everyone adds/removes footprints. **Subscribe** — read-only for members (writing returns 403).

| Action | Owner | Admin | Member |
|--------|:-----:|:-----:|:------:|
| Add/remove footprints (cocreate) | ✅ | ✅ | ✅ |
| Add/remove footprints (subscribe) | ✅ | ❌ | ❌ |
| Generate invite link (cocreate) | ✅ | ✅ | ✅ |
| Generate invite link (subscribe) | ✅ | ❌ | ❌ |
| Switch cocreate ↔ subscribe | ✅ | ❌ | ❌ |
| Manage members | Web UI only | — | — |

## Tools

### Registration & Identity

- **`agent_register()`**
  Create a new account. No parameters. Token is auto-applied for all subsequent calls.
  ⚠️ Call once only — each invocation creates a fresh account.

- **`my_info()`**
  Verify connection and token validity. Returns username and membership status.

### Bookmarks

- **`search_footprints(query, limit, offset)`**
  Full-text search across titles, descriptions, and URLs.
  - `query` _(required)_ — Search keywords
  - `limit` — Results per page (default 10, max 100)
  - `offset` — Pagination offset (default 0)

- **`list_footprints(category_id, limit, offset)`**
  List bookmarks by category. `category_id=0` returns all.
  - `limit` — Results per page (default 20, max 100)
  - `offset` — Pagination offset (default 0)

- **`get_footprint(footprint_id)`**
  Get full details of a single bookmark.
  - `footprint_id` _(required)_ — From `list_footprints` or `search_footprints` results (field `id`)

- **`add_footprint(url, title, description, category_ids, tag_names)`**
  Add a new bookmark. Call `list_categories()` and `list_tags()` first to discover existing structure.
  - `url` _(required)_ — Web page URL
  - `title` — Leave empty to auto-extract from the page
  - `description` — Summary or notes
  - `category_ids` — Comma-separated IDs, e.g. `"1,3"`
  - `tag_names` — Comma-separated names, e.g. `"AI,tutorial"`

- **`update_footprint(footprint_id, title, description, category_ids, tag_names)`**
  Update a bookmark. Omitted fields stay unchanged.
  ⚠️ `category_ids` **replaces** the entire list — not append. Call `get_footprint()` first, then merge IDs.
  - `footprint_id` _(required)_ — From search or list results

### Categories & Tags

- **`list_categories()`**
  List all categories (personal + shared). Returns `id`, `name`, and `mode` fields.
  `mode=null` → personal; `mode="cocreate"/"subscribe"` → shared.

- **`create_category(name, category_set_id)`**
  Create a new category. Check `list_categories()` first to avoid duplicates.
  - `name` _(required)_ — Category name
  - `category_set_id` — Parent category set (0 = default)

- **`list_tags()`**
  List all tags used by this account.

- **`list_content_types()`**
  List all content types the user has used (e.g. article, video, image), ordered most-used first. Use before adding to pick a consistent content_type.

### Category Sets

- **`list_category_sets()`**
  List all category sets.

- **`create_category_set(name)`**
  Create a new category set (a container of categories).
  - `name` _(required)_ — Category set name

### Shared Categories

- **`create_shared_category(name, mode, description)`**
  Create a shared category for team collaboration.
  - `name` _(required)_
  - `mode` _(required)_ — `"cocreate"` (multiple editors) or `"subscribe"` (read-only)
  - `description` — Optional description
  ⚠️ In `subscribe` mode, adding bookmarks returns **403**. Use `"cocreate"` for editable collaboration.

- **`create_invite_link(shared_category_id, duration_hours)`**
  Generate an invite link for others to join.
  - `shared_category_id` _(required)_ — From `list_categories()` (shared entries)
  - `duration_hours` — Default 24

- **`join_shared_category(invite_code)`**
  Join a shared category by invite code.
  - `invite_code` _(required)_ — 8-character code from the invite link

- **`add_to_shared_category(shared_category_id, footprint_id)`**
  Add one of your own bookmarks to a shared category.
  - Both parameters required

- **`remove_from_shared_category(shared_category_id, footprint_id)`**
  Remove a bookmark from a shared category. Does not delete the bookmark itself.
  - Both parameters required

- **`copy_footprint(footprint_id, category_ids)`**
  Copy a bookmark from a shared category into your personal collection.
  - Both parameters required

### Batch & Delivery

- **`batch_update_footprints(updates)`**
  Bulk edit up to 50 bookmarks at once.
  - `updates` _(required)_ — JSON string: `[{"id":"...", "title":"New Title", "category_ids":"1,3"}, ...]`
  Each object may contain `title`, `description`, `category_ids`, `tag_names`; `id` is required.

- **`agent_magic_link()`**
  🔑 The delivery loop core. After organizing, generate a link → send to user. They click to see a card-based interface with all their organized bookmarks. **Valid for 30 days, reusable.**

## Workflows

### New User — Zero Setup
```
1. agent_register() → get token (auto-memorized)
2. add_footprint(url="...") × N → save bookmarks one by one
3. list_categories() → understand current structure
4. create_category(name="Learning") → create a category
5. update_footprint(id, category_ids="...") → categorize
6. agent_magic_link() → "Done! View your collection here → [link]"
```

### Returning User — Daily Use
```
1. my_info() → confirm identity
2. list_categories() + list_tags() → understand current structure
3. search_footprints(query) or list_footprints(category_id) → find targets
4. add_footprint / update_footprint → operate
5. agent_magic_link() → deliver results
```

### Create Shared Category
```
1. create_shared_category(name="Team KB", mode="cocreate")
2. create_invite_link(shared_category_id=<returned ID>)
3. Send invite code to user → user shares with teammates
4. Teammates' agents join via join_shared_category(invite_code)
```

## ⚠️ Critical Pitfalls

### category_ids REPLACES, not appends
```
# ❌ Wrong: moving bookmark 42 to category 7 loses existing categories 3 and 5
update_footprint(42, category_ids="7")

# ✅ Right: fetch current categories first, then merge
get_footprint(42) → existing categories [3, 5]
update_footprint(42, category_ids="3,5,7")
```

### Subscribe mode is READ-ONLY
Writing to a subscribe-mode shared category returns 403. If the user says "I subscribed but can't add anything", explain it's read-only — the creator needs to change it to cocreate.

### NEVER call agent_register twice
Each call creates a fresh empty account. Always check for a saved token first. If unsure, call `my_info()` to verify the current token is valid.

### Rate Limiting
Rapid consecutive calls may trigger HTTP 429. Add short delays between batch operations; on 429, wait a few seconds and retry.

### No member management via API
Inviting or removing members from shared categories requires the web UI at https://ai.ocean94.com. You cannot do this programmatically.

## Guidelines

### Always
- **Auto-register silently** — never interrupt the user for account setup
- **Search before listing** — use `search_footprints` for targeted queries instead of dumping everything
- **Discover before creating** — call `list_categories()` and `list_tags()` before adding to avoid duplicates
- **Deliver with magic link** — after organizing, always generate and share a link

### Confirm before
- Removing bookmark-category associations (irreversible)
- Clearing tags
- Modifying cocreate shared categories (affects others)
- Removing bookmarks from shared categories (other members lose access)

## Pairing with Popular MCP Servers

URL Manager excels at **saving and organizing**. Pair it with tools that excel at **discovering and fetching**:

```
Fetch MCP scrapes web  →  add_footprint()  →  auto-categorized, permanent, searchable
Firecrawl crawls pages →  add_footprint()  →  organized into cards
Brave Search finds URLs →  add_footprint()  →  one-click save from search results
```

Agents just pass the upstream MCP's URL + title as params to `add_footprint`.

## Installation

```bash
git clone https://github.com/Piccolo123/url-manager-mcp.git
cd url-manager-mcp
pip install -r requirements.txt
```

Or from PyPI:

```bash
uvx url-manager-mcp   # or: pip install url-manager-mcp
```

### Prerequisites

- Python 3.10+
- Network access to `https://ai.ocean94.com`

## DeepSeek Harness (dsh)

Add to your profile's `cordis.patch.yml` (e.g. `~/.dsh/profiles/headless/cordis.patch.yml` or the `web` profile):

```yaml
- insert:
    - id: mcp-url-manager
      name: '@deepseek-ai/dsh-mcp-client'
      config:
        serverName: url_manager
        transport: stdio
        command: uvx
        args: ['url-manager-mcp']
        env:
          FOOTPRINTS_ENDPOINT: 'https://ai.ocean94.com'
```

All 21 tools appear as `mcp__url_manager__*` (add_footprint, search_footprints, list_categories, agent_magic_link, …). The model auto-registers on first use — no API key needed. The companion skill (`Piccolo123/url-manager`) is also auto-discovered by dsh when cloned into `~/.dsh/skills/`.

## Configuration

### Claude Desktop / Claude Code

```json
{
  "mcpServers": {
    "url-manager": {
      "command": "python",
      "args": ["path/to/url-manager-mcp/server.py"]
    }
  }
}
```

If the user has an existing account:

```json
{
  "mcpServers": {
    "url-manager": {
      "command": "python",
      "args": ["path/to/url-manager-mcp/server.py"],
      "env": {
        "FOOTPRINTS_TOKEN": "FA_xxxxxxxxxxxx"
      }
    }
  }
}
```

### Cursor / Windsurf / Cherry Studio

Same JSON structure as above. Works with any MCP-compatible client supporting STDIO transport.

### Other Clients

This server supports both **STDIO** (default) and **Streamable HTTP** transports:

```bash
# STDIO (default)
python server.py

# Streamable HTTP (for Docker / Glama / hosted environments)
python server.py --http
```

## Deployment

### Docker

```bash
docker build -t url-manager-mcp .
docker run -e FOOTPRINTS_TOKEN="FA_xxx" url-manager-mcp
```

### ModelScope

One-click hosted deployment: [url-manager-mcp](https://modelscope.cn/mcp/servers/Piccoloxl/url-manager)

## Why URL Manager

Browser bookmarks are flat lists with no organization, no search, and no sharing. URL Manager adds:

- **Categories, category sets, and tags** — Hierarchical organization
- **Full-text search** — Find anything across all titles, descriptions, and URLs
- **Cross-device sync** — Save on one device, access on all
- **Batch management** — Sort and organize hundreds of links at once
- **Team sharing** — Co-editing and read-only shared collections with invite links
- **Card-based delivery** — Send organized collections as a polished interface, not raw URLs
