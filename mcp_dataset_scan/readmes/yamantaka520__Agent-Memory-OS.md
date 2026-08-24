<!-- mcp-name: io.github.yamantaka520/agent-memory-os -->
<p align="center">
  <img src="https://raw.githubusercontent.com/yamantaka520/Agent-Memory-OS/main/assets/agent-memory-os-logo-integrated-v2.png" alt="Agent Memory OS" width="560">
</p>

<p align="center">
  <a href="https://pypi.org/project/agent-memory-os/"><img src="https://img.shields.io/pypi/v/agent-memory-os?color=4F46E5" alt="PyPI"></a>
  <a href="https://pypi.org/project/agent-memory-os/"><img src="https://img.shields.io/pypi/pyversions/agent-memory-os" alt="Python"></a>
  <a href="https://github.com/yamantaka520/Agent-Memory-OS/actions"><img src="https://img.shields.io/github/actions/workflow/status/yamantaka520/Agent-Memory-OS/ci.yml?branch=main&label=CI" alt="CI"></a>
  <a href="https://hub.docker.com/r/yamantaka520/agent-memory-os"><img src="https://img.shields.io/docker/pulls/yamantaka520/agent-memory-os?color=2496ED&logo=docker&logoColor=white" alt="Docker Pulls"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-green" alt="License"></a>
  <a href="https://glama.ai/mcp/servers/yamantaka520/Agent-Memory-OS"><img src="https://glama.ai/mcp/servers/yamantaka520/Agent-Memory-OS/badges/score.svg" alt="Glama score"></a>
</p>

<p align="center">
  <b>English</b> · <a href="README.zh-Hant.md">繁體中文</a>
</p>

A **local-first memory system for AI-agent teams** — not just giving one agent a memory, but a shared memory fabric for a *fleet* of agents working together: private, team, and project-scoped memories behind a hard ACL, associative recall, and federated sync that keeps a mesh of nodes (and their org structure) in agreement. One SQLite file, zero required dependencies, Apache-2.0.

<p align="center">
  <a href="#why">Why</a> · <a href="#how-it-compares">Compare</a> · <a href="#install">Install</a> · <a href="#quickstart">Quickstart</a> · <a href="#features">Features</a> · <a href="#federation-multi-host-sync">Federation</a> · <a href="#web-ui">Web&nbsp;UI</a> · <a href="docs/USER_GUIDE.md">User&nbsp;Guide</a>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/yamantaka520/Agent-Memory-OS/main/assets/console-demo.gif" alt="AgentMemoryOS web console — dashboard, browse, association graph" width="820">
  <br><sub>The built-in web console: token-usage by agent/team/project, memory browse, and the ACL-safe association graph.</sub>
</p>

## Why

Real work happens in **teams of agents** — a project might mix Claude Code, Codex, OpenClaw, and several Hermes profiles, across multiple teams and projects, on one machine or many. They need to share the *right* knowledge with the *right* teammates and keep private what should stay private:

- **Per-agent memory** is the floor, not the ceiling: durable facts, preferences, procedures, and lessons that survive across sessions.
- **Team & project memory** is the point: a team sees `team:<id>` memory; a project (a subset of the team) sees `project:<id>` memory; nothing leaks across the boundary. Membership is first-class and manageable, and drives the ACL.
- **Federation** keeps a mesh honest: memories *and* the org structure (teams/projects/memberships) converge across nodes, so `project:<id>` means the same thing everywhere.
- **Local-first** avoids the latency, cost, and privacy tradeoffs of cloud memory platforms — memories live in a local SQLite file, and each prompt receives only the relevant, budgeted slice.

## Features

- **Local-first, zero-dependency core** — one SQLite file (FTS5), no server required. `pip install` and go.
- **Teams & projects, first-class** — teams are sets of node members; a project's members are a subset of its team. `team:<id>` memory reaches the whole team, `project:<id>` memory only that project — a hard ACL, managed in the console/CLI/API. Removing a member re-scopes recall instantly; deleting a scope revokes its memory.
- **Federated across nodes, with a real trust model** — portable bundles + peer sync converge memories, links, profiles, **and the org structure** (teams/projects/memberships) with last-writer-wins + tombstones. Per-peer policy (`shared`/`full`/`team:`/`project:`) is an **enforced authorization scope**: a peer can only assert membership within its own scope and can only *shrink* a memory's visibility, never widen it — no cross-scope escalation from a bundle.
- **Revocation that propagates** — an independent ACL clock carries a post-hoc share/revoke across the mesh, so revoking access actually retracts it on peers that already synced the memory — without disturbing the decay clock.
- **Requester-aware ACL** — every agent has private, agent, team, project, and global memories; visibility is a hard gate enforced before ranking, never a soft score. Candidate indexes return IDs only; content is re-read through the gate.
- **Dynamic context packs** — token-budgeted, auditable memory selection per prompt (`context_pack_report()` explains every include/exclude decision).
- **Truth arbitration** — duplicate suppression, contradiction detection (`CONFLICT` markers), and reserved budget for core memories.
- **Associative recall (resonance)** — an authoritative `memory_links` graph lets related memories surface even when they share no query terms; traversal is ACL-safe (invisible nodes are untraversable).
- **Hebbian reinforcement** — memories recalled together grow stronger links (`record_recall`, or `auto_reinforce=True` on context packs); unhelpful recalls weaken links and confidence (`helpful=False`).
- **Per-agent recall profiles** — different agent personas weight memory types differently (an engineer leans on `procedure`, a companion on `preference`); profiles persist in the database and re-weight ranking only, never bypassing ACL.
- **Memory lifecycle** — exponential/linear decay, pinning, hard expiry, and a write-side `consolidate()` pass that merges duplicates and synthesizes strongly co-recalled clusters into concept memories.
- **Optional sidecars** — semantic vector candidates (turbovec), MCP server, and a FastAPI Web UI, all behind extras; every candidate rejoins SQLite and passes hard gates before use.

## How it compares

Most agent-memory systems optimize for LLM-driven extraction at hosted scale.
AgentMemoryOS optimizes for a different point: **local-first, team-scoped, and
federated** — memory you run yourself, shared across a fleet under a hard ACL.
This is a *positioning* comparison (architecture, not a benchmark); verify each
row against the projects' current docs.

| | **AgentMemoryOS** | Mem0 | Zep / Graphiti |
|---|---|---|---|
| **Run it** | One SQLite file, `pip install` | Self-host (configure LLM + vector DB) or hosted | Zep Cloud, or self-host Graphiti on Neo4j/FalkorDB |
| **Core needs an LLM** | **No** (FTS5 + optional local vectors) | Yes (LLM extraction, e.g. gpt-5-mini) | Yes (LLM builds the temporal graph) |
| **External services** | **None required** | LLM API + vector store | Graph DB + LLM + embeddings (3+ systems to self-host) |
| **Scope / ACL model** | Private / agent / **team / project** / global — hard gate before ranking | Per user / agent / session id | Per user / session graph |
| **Cross-node federation** | **Yes** — memories *and* org structure converge; revocation propagates | Centralized store | Centralized (Cloud or your graph DB) |
| **Built-in MCP server** | **Yes** | Via SDK | Via SDK |
| **License / self-host** | Apache-2.0, fully OSS | OSS core; graph & advanced tiers paid | Community Edition deprecated; self-host = raw Graphiti |

Mem0 and Zep are strong at LLM-based extraction and managed-scale retrieval —
things AgentMemoryOS deliberately doesn't do. Reach for AgentMemoryOS when you
want a dependency-light memory you own, shared correctly across a *team* of
agents, that keeps working offline and syncs on your terms.

## Install

```bash
pip install 'agent-memory-os[full]'    # recommended: everything (Web UI, MCP, turbovec)
```

Or pick pieces: `agent-memory-os` (core, zero dependencies), `[api]` (Web UI), `[mcp]` (MCP server), `[semantic]` (turbovec vector recall).

**Docker:** the prebuilt multi-arch image is the complete AgentMemoryOS (web console + MCP server + CLI); the first argument picks the mode:

```bash
docker run -p 8000:8000 -v amos-data:/data yamantaka520/agent-memory-os        # web console (default)
docker run -i --rm yamantaka520/agent-memory-os mcp                            # stdio MCP server
docker run --rm -v amos-data:/data yamantaka520/agent-memory-os check          # any CLI command
```

Or `docker compose up -d`. Console at http://localhost:8000, memories persist in a volume. See the [Docker guide](docs/DOCKER.md) (Docker Hub image + a two-node sync mesh).

Requires Python 3.11+ with SQLite FTS5 (included in standard CPython builds).

After installing, run two commands:

```bash
agent-memory doctor          # verifies FTS5, turbovec, and the other extras
                             # (add --install to auto-install anything missing)
agent-memory token create    # protects the Web UI API with a bearer token
```

The token is stored at `<home>/web_token` (mode 600); `agent-memory-web` picks
it up automatically and the console prompts for it on first use. Manage it
later with `agent-memory token show|rotate|disable`. Two narrower tiers exist:
`--readonly` (GET-only) and `--sync` (federation routes only — hand this to a
peer instead of the admin token).

## Quickstart

> Prefer a runnable script? [`examples/team_memory.py`](examples/team_memory.py) shows three agents sharing one store under a hard ACL in ~40 lines — `python examples/team_memory.py`.

```python
from agent_memory_os import MemoryClient, RecallProfile

client = MemoryClient(home="~/.agent-memory")

# Write memories with ownership and visibility
client.add("User prefers dark mode.", owner="mizuki", type="preference",
           visibility=[])                      # private to owner
client.add("Deploy target is port 8000.", owner="neo", type="environment",
           visibility=["global"])              # visible to every agent

# Requester-aware search: each agent sees only what it may see
hits = client.search("deploy port", requester_agent_id="neo")

# Token-budgeted context pack for the prompt, with reinforcement loop closed
pack = client.context_pack("deploy port", requester_agent_id="neo",
                           max_tokens=1200, auto_reinforce=True)

# Associate memories; linked memories resonate into future recalls
a = client.add("Staging deploy failed with database lock.", visibility=["global"])
b = client.add("Always snapshot before schema changes.", visibility=["global"])
client.link(a.id, b.id, relation="caused_by", weight=0.8)

# Persist an agent persona: soft ranking bias per memory type
client.save_profile(RecallProfile(agent_id="neo",
                                  type_weights={"procedure": 1.5, "note": 0.7}))

# Periodic hygiene: merge duplicates, synthesize concept memories
client.consolidate()
```

## Architecture

```text
query
  -> candidate providers (FTS5 | vector sidecar | resonance graph | fallback)
  -> merge/dedupe by stable memory_id
  -> rejoin authoritative rows from SQLite
  -> ACL hard gate -> expires_at hard gate
  -> scoring (relevance x importance x confidence x freshness x reinforcement)
  -> per-agent profile re-weighting (soft)
  -> truth arbitration + context budget allocation
```

Design invariants:

- The SQLite `memories` table is the single source of truth; FTS/vector indexes are disposable and rebuildable (`rebuild_indexes()`).
- Candidate providers return IDs and scores only — content is always re-read through SQLite behind the ACL and expiry hard gates.
- Association edges (`memory_links`) are authoritative data, survive index rebuilds, decay when unused, and never let an invisible memory bridge two visible ones.

See [SPEC.md](SPEC.md) for the full contract.

## Storage engines: SQLite + turbovec

AgentMemoryOS uses **two storage layers with strictly different authority**:

- **SQLite** (always on) is the single source of truth: memories, links,
  profiles, and the FTS5 lexical index all live in one `memories.db` file.
- **turbovec** (installed with `[full]` / `[semantic]`) is the semantic vector
  engine: an in-memory quantized index that recalls memories by meaning rather
  than keywords. It is deliberately **disposable** — it returns candidate
  `memory_id`s and scores only; every candidate rejoins SQLite and passes the
  ACL/expiry hard gates before its content can be used, and the index can be
  dropped and rebuilt at any time without touching the truth store.

Semantic recall works out of the box:

```python
client = MemoryClient(home="~/.agent-memory", semantic="auto")
```

`semantic="auto"` wires in a self-syncing turbovec index over a built-in
deterministic hashing embedder (no model downloads; typo- and
morphology-tolerant lexical vectors). The index rebuilds itself whenever the
memories table changes and degrades silently to lexical + resonance recall
when the backend isn't installed. For deeper semantics, plug any embedding
model into `TurbovecSemanticCandidateProvider.from_vectors(...)` with your
own `embed_query`. `agent-memory doctor` confirms the backend is importable.

## Memory lifecycle & retention

```bash
agent-memory retention               # archive expired + memories idle 4+ half-lives
agent-memory retention --half-lives 0   # expired only
agent-memory check                   # SQLite + FTS + link-graph integrity
```

Archived memories leave recall entirely but stay restorable (Web UI → Tools →
Retention & archive, or `POST /api/archive/{id}/restore`). Pinned and
authority-track memories are never archived by decay. Databases self-migrate
through a versioned, forward-only migration table (`agent-memory check`
reports the schema version).

## Backup & restore

```bash
agent-memory backup ~/backups/memories-$(date +%F).db --keep 14   # rotate, keep 14
agent-memory restore ~/backups/memories-2026-07-11.db --force
```

Backups use SQLite's online backup API, so they are consistent even while
agents are writing. `--keep N` rotates out older backups in the same name
series (and can never delete the live database). Disposable indexes rebuild
automatically after a restore.

**Upgrades & health.** `agent-memory update` checks PyPI, upgrades, and restarts
the running console; `--check` reports only. Point health checks at `GET /healthz`
(200/503) and a Prometheus scraper at `GET /metrics`.

## Multi-agent projects

One project can mix **Claude Code, Codex, OpenClaw, and multiple Hermes
profiles** against a single store. Register each agent with its teams —
in the console's **Agents** tab or via API — and team members automatically
see `team:<project>` memories with no extra wiring:

```bash
curl -X POST localhost:8000/api/agents -H 'content-type: application/json' \
  -d '{"id": "cc-main", "kind": "claude-code", "teams": ["apollo"]}'
```

Or declare the whole fleet as code — `<home>/agents.toml` is re-applied
every time the store opens (file-listed agents are file-authoritative;
manually registered agents are untouched):

```toml
[agents.cc-main]
kind = "claude-code"
teams = ["apollo", "shared-infra"]   # multiple teams = multiple projects

[agents.hermes-neo]
kind = "hermes"
teams = ["apollo", "ops"]
```

Each MCP server declares its identity with `AGENT_MEMORY_AGENT_ID`, so
memories default to that agent as owner and every recall carries its team
ACL. Ship one project's shared memory to another host with
`agent-memory sync export apollo.jsonl --team apollo`.

## Federation (multi-host sync)

```bash
# on the host being joined: mint a sync-scoped token for the peer
agent-memory token create --sync           # prints amos_sync_… (federation routes only)

# one-time, on the joining host
# easiest: pairing (one command on each side — tokens/mesh key exchanged for you)
#   on the existing node:  agent-memory team invite apollo
#   on the joining node:   agent-memory join <code> --url http://that-node:8000
# or wire a peer by hand:
agent-memory peers add https://other-host:8000 --peer-token <their sync token>

# converge with every registered peer (pull + push, deterministic merges)
agent-memory sync auto
```

Peers are stored per-home; `sync auto` (or the console's "Sync mesh now")
converges bidirectionally with each peer — last-writer-wins on memories and
profiles, strongest-wins on links — and unreachable peers fail individually,
never fatally. File bundles (`sync export/import`) cover air-gapped moves.
Pair with `agent-memory service install` and a cron/timer entry for
continuous mesh sync.

**Encrypt the wire.** Give every node the same mesh key and sync bundles are
encrypted app-layer (Fernet), so memory content stays confidential even over
plain HTTP or through a proxy — the key is a separate secret that never travels
on the wire:

```bash
agent-memory sync genkey                   # prints amos_sk_… ; needs the [secure-sync] extra
export AGENT_MEMORY_SYNC_KEY=amos_sk_…      # set the SAME value on every node
```

The sync-scoped token still rides in the `Authorization` header, so prefer
`https://` peer URLs (certificate-verified) for non-localhost peers to protect
the token too. See [SECURITY.md](SECURITY.md) for the exact guarantees.

## Agent integrations

Step-by-step guides for wiring AgentMemoryOS into common agents — click a tile:

<p>
  <a href="docs/integrations/claude-code.md"><img src="assets/integrations/claude-code.svg" alt="Claude Code integration guide" height="56"></a>
  <a href="docs/integrations/codex.md"><img src="assets/integrations/codex.svg" alt="Codex integration guide" height="56"></a>
  <br>
  <a href="docs/integrations/openclaw.md"><img src="assets/integrations/openclaw.svg" alt="OpenClaw integration guide" height="56"></a>
  <a href="docs/integrations/hermes-agent.md"><img src="assets/integrations/hermes-agent.svg" alt="Hermes Agent integration guide" height="56"></a>
</p>

Hermes Agent gets a **native memory-provider plugin** (not just MCP):
`pip install agent-memory-os && agent-memory hermes install`, then pick
`agent-memory-os` in `hermes memory setup` — recall is injected every turn and
`amos_*` tools carry the team/project ACL. No API key, no LLM. See the
[Hermes guide](docs/integrations/hermes-agent.md).

Any MCP-capable agent can use the same pattern: run
`python -m agent_memory_os.mcp_server` as a stdio MCP server pointing at a
shared `AGENT_MEMORY_HOME`.

## MCP server

<a href="https://glama.ai/mcp/servers/yamantaka520/Agent-Memory-OS"><img width="380" height="200" src="https://glama.ai/mcp/servers/yamantaka520/Agent-Memory-OS/badges/card.svg" alt="AgentMemoryOS MCP server on Glama"></a>

```bash
pip install 'agent-memory-os[mcp]'
python -m agent_memory_os.mcp_server
```

Wire it into Claude Code in one line (set the agent identity so memories are owned correctly):

```bash
claude mcp add agent-memory --env AGENT_MEMORY_AGENT_ID=cc-main -- python -m agent_memory_os.mcp_server
```

Tools (12): `memory_add` (with a `share` arg for team/project/global), `memory_search`, `memory_context_pack`, `memory_orchestrate_context`, `memory_link`, `memory_update`, `memory_share`, `memory_recall_feedback`, `memory_consolidate`, `memory_offload_context`, `memory_reload_context`, `memory_snapshot_diff`. Set `AGENT_MEMORY_AGENT_ID` so each agent acts under its own identity — and two agents pointed at the same home instantly share `team:`/`project:` memories.

## Web UI

```bash
pip install 'agent-memory-os[api]'
agent-memory-web --host 127.0.0.1 --port 8000 --home ~/.agent-memory-web
```

The console speaks **English, 繁體中文, 简体中文, 日本語, and 한국어** — auto-detected from the browser, switchable in the header. It ships with a stats dashboard (scope/type/relation breakdowns, 14-day activity, most-recalled memories), search and recency browsing (memory cards with in-place editing, feedback, links, and delete actions), an interactive association-graph view, a context-pack preview with per-memory decisions, and add/link/consolidate tools — all driven by a global "acting as" identity.

Endpoints: health/stats/dashboard/integrity · memories CRUD + browse · search / context-pack / orchestrate · links + graph · recall feedback · share / revoke / audit · consolidate / retention / archive+restore · agents registry · peers + mesh sync · bundle export/import · owner list / reassign / purge · fleet status/trigger (Ed25519-signed cross-node ops). Full table in the [User Guide](docs/USER_GUIDE.md).

Search, browse, graph, recall feedback, and context-pack accept `requester_agent_id` and enforce the same ACL hard gates as the SDK. Requests without a requester run in unrestricted admin view — bind to localhost only, or require a bearer token on every API route with `--token <secret>` (or `AGENT_MEMORY_WEB_TOKEN`).

Note: keep the `--home` database on a local disk. Network filesystems (NFS/SMB) can fail SQLite FTS5 schema creation with `database is locked`.

### Run as a login service (macOS / Linux / Windows)

```bash
agent-memory service install [--host 127.0.0.1] [--port 8000]
agent-memory service status | start | stop | restart | uninstall
```

`install` registers the console with the native service manager so it starts
automatically at login and restarts on failure — launchd LaunchAgent on
macOS, a systemd user unit on Linux, a Task Scheduler logon task on Windows.
No admin rights required; the service runs the exact Python environment it
was installed from, and logs to `<home>/logs/web.log`. On Linux, run
`loginctl enable-linger $USER` if it must start at boot without a login.
Add `--dry-run` to preview the actions. CI runs the full test suite on
Ubuntu, macOS, and Windows across Python 3.11–3.13.

## Development

```bash
pip install -e '.[dev]'
pytest
```

## Status

**Stable — `1.x`.** The contracts above are implemented, covered by the test
suite (300+ tests across a 3-OS CI matrix, plus a migration upgrade-path job),
and audited by repeated fan-out code + security reviews (reports under
[`docs/reviews/`](docs/reviews/)). Performance is verified at 10k memories (add
0.17 ms, search <1 ms, context-pack 7.8 ms). The database self-migrates forward;
see the [CHANGELOG](CHANGELOG.md) for what each release added.

## Documentation

- **[User Guide](docs/USER_GUIDE.md)** — concepts, full CLI / HTTP API / MCP references, multi-agent and federation walkthroughs, ops checklist
- **[Docker guide](docs/DOCKER.md)** — `docker`/`docker compose` startup, config via env, two-node sync mesh
- [SPEC](SPEC.md) — contracts and invariants, by milestone
- **[Security](SECURITY.md)** & **[Threat model](docs/THREAT_MODEL.md)** — disclosure policy, trust boundaries, and honest known limitations
- **[Embeddings & scale](docs/EMBEDDINGS.md)** — plug in a real embedding model; behaviour from 10k to 1M memories
- **[Importers](docs/IMPORTERS.md)** — migrate from Mem0 / Zep / ChatGPT · **[Compatibility](COMPATIBILITY.md)** — the 1.x semver promise
- **[Reviews & reports](docs/reviews/)** — fan-out code + security reviews (through the 1.x line), the performance/security report, and the validation harness (`scripts/validation_run.py`)
- [CHANGELOG](CHANGELOG.md) · [Roadmap](docs/ROADMAP.md) · [Integration guides](docs/integrations/claude-code.md)

## License

[Apache License 2.0](LICENSE)
