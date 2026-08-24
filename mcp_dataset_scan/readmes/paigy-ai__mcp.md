# Paigy — MCP server

A voice inbox for your AI agents. When an agent needs your input — mid-task, blocked, or done with something long-running — it can place an actual phone call and read the question aloud, text, push, or ring your phone with a banner, so you can reply by voice instead of babysitting a terminal.

Without Paigy, a long agent session means one of two bad options: sit and watch the terminal so you don't miss the moment it needs you, or walk away and come back to a task that stalled an hour ago waiting on a question you never saw. Paigy closes that gap — the moment your agent actually needs a decision, your phone gets pulled into the loop with the level of urgency that matches the moment (a silent inbox card, a quiet push, a banner, or a real ringing call), so you find out immediately instead of on your next check-in. Answer by voice or text and the reply lands back with the agent exactly like any other tool response, so it just continues — no copy-pasting, no reopening the terminal. It also pairs with the native Paigy iOS app, so a call rings through like a real phone call (CallKit) even when your phone is locked, and you can glance at or reply to anything from the lock screen.

## Works with

A standard MCP server (stdio, TypeScript) — no client-specific code anywhere, verified over the raw protocol against a non-Claude client identity.

- Claude Code (this repo is also the plugin + marketplace for it)
- Codex CLI
- Gemini CLI
- Any other MCP client via standard config: Cline, Continue.dev, Zed, Cursor, Goose, mcphost — including local-model setups over Ollama, LM Studio, or llama.cpp

(The app + backend live in a separate repo.)

## Install

**One line, any terminal** — detects your agents (Claude Code, Codex,
Antigravity), wires Paigy into each, and pairs your phone once. Prints every
command before running it; `--dry-run` shows the plan:
```
curl -fsSL https://paigy.ai/install | sh
```

Prefer to do it by hand? Pick your client below.

**Claude Code** (plugin — easiest path on Claude):
```
/plugin marketplace add paigy-ai/mcp
/plugin install paigy
```
Connects automatically; the first time an agent uses it while unpaired, it'll
prompt you to pair — run `/paigy-onboard` (opens your browser to approve).

**Claude Desktop** (MCPB bundle — no terminal needed):
download [`paigy.mcpb`](https://github.com/paigy-ai/mcp/releases/latest/download/paigy.mcpb),
then in Claude Desktop open **Settings → Extensions** and drag the file in (or
double-click it). Ask Claude to *"pair with Paigy"* — it runs pairing itself and
shows a code to approve on your phone. Also on
[Smithery](https://smithery.ai/servers/paigy/paigy-mcp).

**Codex CLI:**
```
codex plugin marketplace add paigy-ai/mcp --ref main
codex plugin add paigy@paigy-ai
PAIGY_AGENT=codex npx -y -p @paigy/mcp@latest paigy-mcp-onboard
```

The plugin configures the Paigy MCP server and includes guidance for calls, replies, and callbacks. Start a new Codex session after installation.

**Codex CLI — direct MCP fallback:**
```
codex mcp add paigy --env PAIGY_AGENT=codex -- npx -y @paigy/mcp@latest
```

**Gemini CLI:**
```
gemini mcp add -s user -e PAIGY_AGENT=gemini paigy npx -y @paigy/mcp@latest
```

**Any other MCP client** (Cline, Continue.dev, Zed, Cursor, or a CLI that
takes the standard MCP JSON config directly) — most GUI clients take this in
their MCP settings (Cline: `cline_mcp_settings.json`; Continue:
`~/.continue/config.json`):
```json
{
  "mcpServers": {
    "paigy": {
      "command": "npx",
      "args": ["-y", "@paigy/mcp@latest"],
      "env": { "PAIGY_AGENT": "local" }
    }
  }
}
```

Then pair your phone — **with the same `PAIGY_AGENT` your client's config
uses** (the token is saved per agent; each agent reads only its own slot, so a
mismatched name leaves the client "not paired" against an approved pairing):
```
PAIGY_AGENT=<your-agent-name> npx -y -p @paigy/mcp@latest paigy-mcp-onboard
```
Claude Code's plugin uses the default name — plain
`npx -y -p @paigy/mcp@latest paigy-mcp-onboard` is right there.
Approve on your phone, then sign in at [paigy.ai](https://paigy.ai) to start
receiving messages.

> Heads-up for smaller/local models: the tool descriptions ask the agent to
> pick between a few answer shapes (confirm, options, free text) based on
> context — Claude follows this reliably; smaller local models may be less
> consistent about it. Free text always works as a fallback.

## Choosing how the user answers

`notify_user` should ask in the shape that's fastest to answer — don't leave a
decision as free text. Pick with `select` (and `options`):

| You need… | Use | Answer comes back as |
|---|---|---|
| **Yes/No or Approve/Deny** | `select:"confirm"` (`confirmStyle:"approve"` for Approve/Deny) | `{kind:"confirm", approved}` |
| **Pick one of several** | `options` + `select:"one"` | `{kind:"option", optionId}` |
| **Pick several** | `options` + `select:"many"` | `{kind:"multi", optionIds}` |
| **Rank / order a subset** | `options` + `select:"rank"` | `{kind:"ranked", optionIds}` |
| **A visual choice** | options with an `html` or `image` preview | one of the above |
| **An open-ended reply** | no options | `{kind:"text", text}` |

`confirm` is **answerable straight from the banner** (Yes/No or Approve/Deny
buttons). Other paiges get banner actions **See Options · Hear them · Remind me
later**.

`urgency` is a *request*, not a guarantee — the user's account settings can
cap it lower. Four levels, low to high: `"inbox"` (silent, sits in the inbox),
`"push"` (a quiet passive notification, no sound), `"banner"` (a
time-sensitive lock-screen banner with sound), `"call"` (rings the phone —
use only when you genuinely need the user in the moment).

If you're about to start something long-running or blocking — the kind of
thing where the user would otherwise sit and wait on you — mention **once**,
in passing, that you can text or call them when it's done or if you hit a
blocker. Don't offer it for quick tasks, and don't repeat the offer once
they've answered.

## Idle escalation (automatic, no setup)

Installing this plugin also wires up Claude Code hooks (`hooks/hooks.json`,
via `${CLAUDE_PLUGIN_ROOT}` — no manual `settings.json` editing) that back
`notify_user` up with a mechanical safety net, independent of the agent
session — it still fires even if that session crashed or forgot:

- **10-minute check** (`escalate.sh`): how much is actually pending
  (`GET /api/pending/summary`, a non-claiming read) — a single fresh item
  gets a `banner`, several or a stale one gets a real `call` (routed through
  the same call-coalescing the bot uses, so several ringing things fold into
  one call instead of ringing separately).
- **2-minute check** (`quick-check.sh`): a narrower, faster check for a
  different case — you already replied to something (via the app), but no
  agent has engaged with it yet. That's not "nothing happened" (escalate.sh's
  job), it's "the agent hasn't looked." It spawns a **fresh** headless
  `claude -p` (deliberately NOT resuming your live session — no injected
  turns in a transcript you might be typing in) scoped to just the tools it
  needs; that agent acknowledges the missed reply with a natural message in
  the same thread ("sorry I missed this — starting on it now"), so what you
  see is a normal agent response, not a system nudge. Only if that's
  unavailable or fails does it fall back to a plain nudge telling you to
  reopen the session yourself.

Hooks are the *dead-session* safety net. A live-but-idle agent shouldn't
need them: the MCP server instructions tell every paired agent to schedule
its own ~2-minute wake-up (harness `ScheduleWakeup` or equivalent) and
`check_replies` whenever it ends a turn with anything possibly pending —
self-polling in its own session, full context intact.

Nothing pending/unacknowledged — including a normal "just finished" stop —
means neither check does anything.

## License

MIT
