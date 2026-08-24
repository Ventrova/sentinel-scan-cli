# mailwarden

[![npm](https://img.shields.io/npm/v/mailwarden)](https://www.npmjs.com/package/mailwarden)
[![license](https://img.shields.io/npm/l/mailwarden)](LICENSE)
[![Node](https://img.shields.io/node/v/mailwarden)](package.json)
[![Website](https://img.shields.io/badge/Website-csitte.at%2Fmailwarden-2ea44f)](https://www.csitte.at/mailwarden/)
[![Smithery](https://img.shields.io/badge/Smithery-csitte%2Fmailwarden-ea580c)](https://smithery.ai/servers/csitte/mailwarden)

A reliable, **native** Gmail [MCP](https://modelcontextprotocol.io) server — full mailbox triage for AI assistants, with the feature no other Gmail MCP server ships: **mailbox-side snooze**.

## Highlights

- **Snooze — the only *mailbox-side* snooze in a Gmail MCP server.** Archive a thread now, have it
  resurface in the inbox on a date. Built on dated labels + a sweep, so it works from any client,
  is visible in Gmail itself, and survives restarts. (Where another server offers a "snooze", it is
  a local reminder list — the mail never leaves or re-enters the inbox.)
- **Search you can trust.** Gmail's `threads.list` — the call any thread search goes through — can
  answer `is:unread` from a **stale thread-level read state**: measured in one real mailbox, **86% of
  the threads it returned held no unread message at all**; in a second mailbox, no drift whatsoever.
  You cannot tell which mailbox you are in without looking, so `search` re-verifies every hit against
  its live labels. Paginated via `pageToken`/`nextPageToken`.
- **Bulk operations that scale.** `bulk_modify` archives/labels everything matching a query at
  1000 messages per API request — with per-chunk partial-success reporting instead of
  all-or-nothing. The snooze sweep uses the same batch path.
- **Structured outputs.** Every tool declares an `outputSchema` and returns validated
  `structuredContent` alongside fenced JSON text — no parsing guesswork for clients. Failures are
  structured as well: a `code` and a `retryable` flag, so a client can tell "try again later" from
  "re-authorize" without reading prose.
- **Small attack surface.** No send tools (no exfiltration path for prompt-injected mail),
  optional read-only mode, no telemetry, no open ports by default, symlink-safe download fencing,
  injection-fenced output. And no code path that *could* send: every Gmail request passes an egress
  checkpoint that refuses `messages.send`, every draft endpoint, permanent deletion and forwarding
  settings, whatever a compromised or careless caller asks for. **One deliberate exception:**
  `unsubscribe` / `bulk_unsubscribe` (manage tier) contact the opt-out endpoint named in a message's
  own header — the only non-Google host mailwarden ever reaches, and a `read`-tier deployment makes
  no outbound request at all. Details under
  [Security & privacy](#security--privacy) and
  [Unsubscribing](#unsubscribing--the-one-outbound-request).
- **Correct with real-world mail.** RFC 2047 headers decoded (`=?UTF-8?B?…?=` → readable text),
  bodies decoded in their *declared* charset (no mojibake for ISO-8859-1/Shift_JIS mail),
  429/5xx retried with exponential backoff.

## Why

Connectors that sync or cache your mailbox can lag behind it — and even Gmail's own search index is sometimes loose (see below). `mailwarden` talks straight to the live Gmail API (no cached snapshot) and re-verifies what the index returns, so what you see is what's actually there. It's a generic Gmail capability layer — keep your own rules/logic in your AI client, not in the server.

`search` goes one step further than the raw API: Gmail's `threads.list` index can answer read-state operators from a **stale copy** of that state, so `is:unread` returns threads you finished reading weeks ago — in one measured mailbox, the large majority of what came back. Since every hit is fetched live anyway, `search` re-checks the unambiguous predicates (`is:unread`/`is:read`/`is:starred`/`in:inbox`/`category:…`, with negation) against each thread's true labels and drops the index's false positives.

## Compared to other Gmail MCP servers

Most Gmail MCP servers cover the same read/label/send surface. Two capabilities are still unique to `mailwarden` (mailbox-side snooze, search re-verification), and one deliberate omission is a security feature, not a gap. Google's own server is also narrower than it looks: draft-only, and no trash, filters or unsubscribe.

<!-- comparison-table-verified: 2026-08-20 -->

| Capability | **mailwarden** | [Google official](https://developers.google.com/workspace/gmail/api/guides/configure-mcp-server) | [taylorwilsdon](https://github.com/taylorwilsdon/google_workspace_mcp) | [a-bonus](https://github.com/a-bonus/google-docs-mcp) | [klodr](https://github.com/klodr/gmail-mcp) |
|---|:--:|:--:|:--:|:--:|:--:|
| **Mailbox-side snooze** — archive now, resurface in the inbox on a date/time or preset | ✅ | — | — | — | — |
| **Search-result re-verification** — drops the thread index's false positives against live labels | ✅ | — | — | — | — |
| **Sweep / bulk over a query** — one action across every thread a search returns | ✅ 1000/req, partial-success | — | ⚠️ batch by explicit ids | — | ⚠️ batch by explicit ids |
| **Unsubscribe** — per-sender overview + RFC 8058 one-click opt-out, no send scope needed | ✅ | — | ⚠️ header shown, no action | — | — |
| **Inbox triage overview** — one call that buckets what is waiting | ✅ sender/label/age + header signals | — | — | ✅ heuristic flags + stats | — |
| **Server-side filters** — rules that keep triaging with no assistant in the loop | ✅ never forwarding | — | ✅ | — | ✅ |
| **No send tools — by design** — a prompt-injected mail has no exfiltration path | ✅ no compose at all | ⚠️ draft-only | ❌ sends | ❌ sends | ❌ sends |
| **Least-privilege tool tiers** — OAuth scopes derived from the tools you enable | ✅ | ⚠️ scope split | — | — | ⚠️ inverse: tools gated by granted scopes |
| **Token encryption at rest** (optional) | ✅ AES-256-GCM | n/a (hosted) | ✅ | — | — |
| **No vendor cloud — you operate the server** | ✅ | ❌ Google-hosted | ✅ | ✅ | ✅ |
| **Structured outputs** — every tool declares an `outputSchema` | ✅ | — | — | — | — |

<sub>Snapshot as of 20 August 2026, from each project's public docs and source; `—` = not offered / not documented. Columns are the servers a reader is most likely to reach for — Google's first-party one, plus the two largest community servers — and `klodr`, which comes closest to `mailwarden`'s own least-privilege design. Send capability is listed as a security property: `mailwarden`'s lack of it is intentional (see [Security & privacy](#security--privacy)). The last row asks who *operates* the server, not where it happens to run: self-hosting is common ground here, and every community server on this table offers some remote deployment except `klodr` (stdio only) — `mailwarden` via `--http`, `taylorwilsdon` over streamable HTTP with OAuth 2.1, `a-bonus` on Cloud Run. Running one of them on your own host is not a cloud copy; running it on the vendor's is.</sub>

The moat isn't any single row — it's **snooze + live re-verification together**: an actual inbox-workflow layer that acts on the mailbox's *current* state, not a cached snapshot. Where others have caught up it's noted honestly above: at-rest encryption (`taylorwilsdon`), scope-driven tool gating (`klodr`), a richer per-message triage heuristic (`a-bonus`), and bulk organize over a mailbox (the hosted mcpemails.com, which has no snooze either). What none of them do is act on a *query* and check the mailbox's answer before acting on it.

### Why re-verification matters — a concrete case

Ask an assistant to *"archive the unread promotional mail that's already skipped my inbox"* and it will reach for the obvious query, `category:updates is:unread -in:inbox`. A server that trusts Gmail's index now archives threads you had already read — mail you never meant to touch, gone in a bulk action you can't easily reverse.

**Measured, not asserted.** One real mailbox (~70,000 messages), 15.08.2026, read-only:

| Query (`threads.list`) | Threads returned | With an unread message | Stale |
|---|--:|--:|--:|
| `category:updates is:unread` | 131 | 17 | **87%** |
| `category:updates is:unread -in:inbox` | 128 | 14 | 89% |
| `is:unread -in:inbox` | 235 | 99 | 58% |

The index is not *ignoring* the predicate — the same query without `is:unread` returns 800+ threads, so it is being applied. It is applied against a **thread-level read state that has not caught up**: threads whose every message is read still count as unread there. One returned thread carried a single label, `SENT`. And it is not a quirk of exotic operator combinations: the plainest query of the three shows it too — with the *lowest* share (58%) but the *most* wrong threads in absolute terms (136).

**It is the thread index specifically.** The same query, same mailbox, same minute, asked through `messages.list` instead: **19 messages, none stale.** So this is not "Gmail search is unreliable" — it is that the *thread* view of read state lags while the per-message view does not. `search` goes through `threads.list`, which is exactly why it re-verifies.

**A second mailbox, measured the same way on the same day, drifted not at all** — zero raw-index hits for `is:unread`, although it is read-marked through the API many times a day. So this is a property of *a mailbox*, not of Gmail everywhere. What separates them is open: they differ in volume (roughly three orders of magnitude) and age, and the second is missing something more basic — no thread in it was ever archived while still **unread**, which is the only shape a stale read-state can show up on. So it is not a counter-example to any particular cause; it is a mailbox without the candidate.

Which is the whole point: **a server cannot know which kind of mailbox it is in.** Re-verification costs nothing where nothing drifts, and saves you where it does — in the measurement above, every thread `search` dropped was genuinely read, and it discarded **no** genuinely unread mail.

**Where it is *not* free: the bulk tools.** `search` re-verifies because it fetches every hit anyway; `bulk_modify` (and `create_filter`'s `applyToExisting` sweep) is sized in thousands of messages, where one fetch per hit is a different order of cost. Those act on what the index returns — so they now report `unverifiedPredicates`, the conditions from your query that were taken on the index's word (`+UNREAD`, `-INBOX`, …). Empty means there was nothing to distrust. Non-empty and the result has to be read-state-precise? Resolve the set with `search` first and act on those thread ids. A `dryRun` does **not** close this gap: it re-reads the same index, so it confirms how big the set is, never whether it is right.

`mailwarden` fetches every hit live anyway, so `search` re-checks the unambiguous predicates (`is:unread`, `is:read`, `in:inbox`, `category:…`, with negation) against each thread's **true** labels and drops the index's false positives before any tool sees them. The bulk action then runs on exactly the set you asked for. This is the difference between acting on what Gmail *indexed* and acting on what's *actually in the mailbox right now* — and it's why snooze/sweep are safe to hand to an assistant: the sweep resurfaces only threads whose snooze is genuinely due, verified against live labels at run time.

**See it yourself — no Gmail account needed.** From a clone of the repo (the demo is a repo-only
verification script, not part of the npm package):

```bash
git clone https://github.com/csitte/mailwarden && cd mailwarden
npm install && npm run build
node scripts/demo-reverify.mjs
```

There is a second script next to it, `node scripts/probe-reverify.mjs`, which measures the same thing in *your* mailbox instead of a fake one — read-only, metadata only (no subject, sender or body is fetched), printing counts and label names. It is how the numbers above were produced, and how you can check whether your mailbox drifts at all.

The demo drives the real `search()` against a fake Gmail API whose index is deliberately stale (returns a read thread for an `is:unread` query, exactly as Gmail does) and shows mailwarden dropping the false positive. It asserts the outcome, so it exits non-zero if the behavior ever regresses. The same case is locked by unit tests in [`test/gmail.test.ts`](https://github.com/csitte/mailwarden/blob/main/test/gmail.test.ts) (*"drops index false positives via live-label re-verify"*).

## Tools

| Tool | What it does |
|---|---|
| `search` | Gmail query syntax → thread summaries (from/subject/date/labels/snippet); read-state/category predicates are re-verified against each hit's live labels; paginated via `pageToken`/`nextPageToken`. Each hit carries `signals` — `newsletter` (List-Id / List-Unsubscribe / Precedence bulk or list), `automated` (Auto-Submitted, auto-reply/suppress headers, no-reply-style senders), `calendar` (text/calendar or .ics part), `replyToMismatch` (Reply-To on another domain than From; a subdomain of the same domain counts as the same) — read off the first message's headers/MIME, no extra call. **Spam and trash are excluded unless the query says `in:spam` / `in:trash`** — see [Looking in spam](#looking-in-spam) |
| `get_thread` | Full thread: headers, plaintext + HTML bodies, attachment metadata |
| `list_labels` | All labels (system + user) |
| `get_profile` | Connected account's address + total message/thread counts — confirm *which* mailbox is wired up before acting |
| **`triage_digest`** | Structured overview of a mailbox slice for *decisions*: top senders (each with the signals its threads carry), label and age buckets, unread + attachment counts, and how many threads are newsletters / automated / calendar invites / reply-to mismatches — instead of a raw thread list |
| `list_unsubscribe` | What opt-out options a thread advertises (`List-Unsubscribe`) — contacts nobody |
| **`list_subscriptions`** | A mailbox slice grouped by *sender*: thread/unread counts, the date span each was seen over, and each one's opt-out options — one header fetch per sender, contacts nobody. `sendersFound` reports how many senders there were before `topN` truncated the list |
| `create_label` | Create a user label (idempotent; nested via `Parent/Child`) and return its id |
| `modify_labels` | Add/remove labels by **name or id** — an unknown name in `add` is auto-created (archive = remove `INBOX`, read = remove `UNREAD`) |
| **`bulk_modify`** | Batch label changes for every message matching a query — 1000 messages per API request, partial success reported per chunk (thread-id list capped at 500, `modifiedThreadCount` has the total). Acts on the **raw index**, so `unverifiedPredicates` names the conditions it could not vouch for (see below). `dryRun: true` resolves the query and reports the matched threads and the labels it would create, touching nothing |
| `archive` / `mark_read` / `mark_unread` | Convenience wrappers |
| `trash` / `untrash` | Move to / restore from Trash |
| `download_attachment` | Save an attachment to a local path (never overwrites — collisions get a numeric suffix) |
| **`unsubscribe`** | One-click opt-out (RFC 8058) using the endpoint from the message's own header — the only tool that contacts a non-Google host ([details](#unsubscribing--the-one-outbound-request)) |
| **`bulk_unsubscribe`** | The same for several threads, sequentially and **at most one request per sender** (remembered across calls for as long as the server runs, so a retry contacts nobody twice); partial success reported per thread. `dryRun: true` runs the same header reads and dedupe and reports the endpoint each thread `wouldCall` — contacting nobody |
| **`snooze`** | Archive now, resurface on/after a date (`YYYY-MM-DD`), a date+time (`2026-06-20 9am`), or a preset (`tomorrow`, `tomorrow 9am`, `weekend`, `next week`, a weekday name, `in N days`, `in N hours`) |
| **`unsnooze`** | Cancel a snooze, return to inbox now |
| **`list_snoozed`** | All snoozed threads + due dates |
| **`sweep_snoozed`** | Resurface threads whose snooze is due (run on demand, via cron, or the daemon); batched, with partial-failure reporting. `dryRun: true` answers "what is due right now?" (`dueLabels`/`dueThreads`) without waking anything |
| `list_filters` | All Gmail filters (criteria + label actions); surfaces any `forward` address on existing filters for auditing |
| `create_filter` | Create a server-side auto-triage rule (criteria → label actions only; **no forwarding** — see below). Optionally `applyToExisting` to also sweep matching mail already in the mailbox |
| `delete_filter` | Delete a filter by id |

All tools declare an `outputSchema` and return **structured content** (validated, machine-readable)
alongside the same JSON as fenced text — clients never have to parse prose.

A **failure** is structured too: `isError` plus a fenced JSON body with a `code`
(`not_authorized`, `needs_reauth`, `insufficient_scope`, `forbidden_operation`, `not_found`,
`rate_limited`, `upstream_unavailable`, `network_error`, `invalid_input`, `internal_error`) and a
`retryable` flag, alongside the sentence a human reads. So "wait and try again" versus "re-run
`mailwarden --auth`" is something a client can decide, not something it has to infer from wording
that may be reworded next release. (No `structuredContent` on errors: that is validated against the
tool's outputSchema, which describes a success.)

### How snooze works (no Gmail API snooze exists — we build it)

`snooze` removes `INBOX` and applies a dated label `MCP/Snoozed/<key>`, where the key is either `YYYY-MM-DD` (due all day) or `YYYY-MM-DDTHHMM` (due at that local minute). The `until` argument takes an explicit date, a date+time (`2026-06-20 9am`, `…T17:00`), or a preset resolved server-side — `today`, `tomorrow`, `weekend` (next Saturday), `next week` (next Monday), a weekday name (`monday`–`sunday`, next occurrence), `in N days`, or `in N hours` — and a date preset may carry a trailing time (`tomorrow 9am`, `monday 8:30`), so the caller never has to compute the moment itself. `sweep_snoozed` finds due labels and returns those threads to the inbox (marked unread); a timed snooze wakes at the first sweep on/after its minute, so wake latency equals your sweep interval. Run the sweep:
- on demand (`sweep_snoozed` tool),
- via cron: `mailwarden --sweep`,
- or automatically: set `MAILWARDEN_AUTO_SWEEP=1` (hourly sweep while the server runs).

### Filters (persistent auto-triage rules)

`create_filter` sets up a Gmail server-side rule: mail matching the criteria automatically gets the
given label actions — the mailbox keeps triaging itself with no assistant in the loop.

- **Criteria:** `from`, `to`, `subject`, `query` (full Gmail search syntax), `negatedQuery`,
  `hasAttachment`, `excludeChats`, and `size` + `sizeComparison` (`smaller`/`larger`, given together).
  At least one is required.
- **Actions (label only):** `addLabels` / `removeLabels`, by name or id (an unknown name in
  `addLabels` is auto-created, nested via `/`). Common recipes: skip the inbox → `removeLabels: ["INBOX"]`;
  auto-mark-read → `removeLabels: ["UNREAD"]`; auto-trash → `addLabels: ["TRASH"]`;
  star → `addLabels: ["STARRED"]`; never-spam → `removeLabels: ["SPAM"]`; file under a label → `addLabels: ["Receipts"]`.
- **Existing mail:** a filter only runs on messages arriving *after* it's created. Pass
  `applyToExisting: true` to also apply the same actions once to mail already in the mailbox —
  mailwarden builds a Gmail search from the criteria and runs a bulk modify (up to `maxMessages`,
  default 1000; same unverified-index caveat as `bulk_modify`, and the one-off pass excludes Spam/Trash).
  This requires at least one *positive* criterion (`from`/`to`/`subject`/`query`/`hasAttachment:true`/`size`):
  an exclusion-only rule (`negatedQuery` or `hasAttachment:false`) is refused for `applyToExisting`
  because it would match almost the whole mailbox — create such a filter without the flag.
  The outcome comes back under `applied` (the `query` used, `matchedMessages`/`modifiedMessages`/`modifiedThreadCount`
  counts, `capped` when the match set hit `maxMessages`, per-chunk `failed`, and an `error` string if the whole
  pass failed); it's `null` when `applyToExisting` was not set. The filter is created first, so a partial or
  failed backlog pass is *reported* in `applied`, never raised — the rule still stands.
- **No forwarding** — see [Security & privacy](#security--privacy).
- Requires the `gmail.settings.basic` scope; re-run `--auth` once if you authorized an older version.
  Not available in read-only mode.

### Unsubscribing — the one outbound request

`list_unsubscribe` (read tier) reports what the sender offers, without contacting anyone. It reads the
newest message that actually carries a `List-Unsubscribe` header — a reply threaded onto a newsletter
sits at the end and advertises nothing, which would otherwise read as "this list has no opt-out".
`list_subscriptions` (read tier) does the same across a whole slice, grouped by sender, so you can see
*who* keeps writing and which of them can actually be left — one header fetch per sender rather than
per thread. `unsubscribe` and `bulk_unsubscribe` (manage tier) act on it — and that is the **only**
place mailwarden ever talks to a host that isn't Google, so the rules are tight:

- **There is no URL parameter.** The endpoint comes from the message's own header and nowhere else.
  A URL argument would let a prompt-injected mail turn the tool into an exfiltration channel
  (mailbox content in a query string); the header cannot carry data the model chose.
- **Only RFC 8058 one-click** is performed — the sender must have opted in via `List-Unsubscribe-Post`.
  A plain `https:` link is meant for a human in a browser and is handed back, not fetched.
- **`mailto:` opt-outs are never performed.** They would require sending mail, which mailwarden cannot
  do. The address is reported so you can act on it yourself.
- **Fixed request, discarded response.** The POST body is always `List-Unsubscribe=One-Click` and is
  never derived from anything; the response body is cancelled unread. What returns to the model is the
  status code and the URL actually called — no content from the endpoint, so it cannot answer with
  instructions. (A 301/302/303 redirect is followed as a GET, i.e. with no body at all.)
- **One request per sender, sequentially, inside one budget.** `bulk_unsubscribe` takes thread ids
  (never a query — a query-driven bulk would fire off a request per matched sender before anyone had
  looked). Threads from a sender whose request already went out are reported with `duplicateOf` and
  cost no second request: two threads from one list share an opt-out, and calling it twice only
  confirms your address twice. A sender is only recorded once a request actually *reached* an
  endpoint, so a refusal or a dropped connection still leaves the next thread its own try — and if
  the skipped thread advertises a *different* endpoint, the reason says so, since one sender can run
  several lists. **That memory spans calls** for as long as the server runs, and `unsubscribe` shares
  it: a call that times out is safe to repeat, and asking twice for the same newsletter contacts the
  sender once. Pass `force: true` to `unsubscribe` for a deliberate second attempt — after an endpoint
  answered 500, say. It is kept in memory only: persisting it would mean a second kind of local state
  beside the token, which this server deliberately does not keep, so a restart forgets.
  Capped at 25 threads and 60 seconds per call; whatever the budget doesn't cover comes
  back as `skippedOutOfTime` rather than silently undone. None of it can be reversed, which is why all
  three limits exist.
- **SSRF guards.** https only, default port only, no credentials in the URL, and every hop — including
  redirects, followed at most 3 times — must resolve exclusively to globally reachable addresses. The
  check parses each address to its bytes and matches it against the IANA special-purpose registry, so
  every spelling of the same address gets the same verdict (`::1` and `0:0:0:0:0:0:0:1` alike); an
  address that does not parse is refused. DNS resolution and all hops share one 10-second budget. Not
  rebinding-proof (`fetch` resolves again when it connects) — see [SECURITY.md](SECURITY.md); what
  survives that gap is a blind POST whose response is never read.

**Check it against your own mail before you trust it.** From a repo clone (repo-only, not in the
npm package), after `npm run build` and `mailwarden --auth`:

```bash
node scripts/probe-unsubscribe.mjs --vet          # category:promotions, 25 threads
node scripts/probe-unsubscribe.mjs "from:substack.com" --max 50 --vet
```

It prints each real `List-Unsubscribe` header next to what the parser made of it, and `--vet` also
runs the endpoint through the URL vetting and the address guard — so you see both whether the parser
understood the header *and* whether the guards would have let that opt-out through. Strictly
read-only: no request is ever made to a sender, and nothing in the mailbox changes.

What it can't undo: the request tells the sender your address is live. A sender that ignores its own
opt-out is beyond any client's reach — pair `unsubscribe` with `create_filter` or `trash` for those.
Not offering an automatable option is reported as `unsubscribed:false` with the alternatives, not as an
error. A `read`-only deployment gets `list_unsubscribe` and `list_subscriptions`, and never makes the
request at all.

## Looking in spam

**A query that does not name a place never sees spam or trash.** Gmail excludes both from any
search that does not say `in:spam` / `in:trash`, so `from:someone` returns nothing for a mail that
is sitting in the spam folder — and nothing in the answer says so. Measured against a live mailbox:
the same `from:` query returned 0 hits by default and 1 with spam included.

This matters because of *why* mail gets misfiled. A spam filter judges a message on its own; it
cannot know that you signed up for something a minute ago, requested a password reset, or placed an
order — so the confirmation you are waiting for is exactly the kind of mail that lands there. You
know what you just did. The filter does not.

So when mail someone expects is missing, ask again with the place named:

```text
search("in:spam newer_than:2d")          # what got filed as spam recently
search("in:spam from:example.com")       # the confirmation that never arrived
```

A thread returns to the inbox with `modify_labels` (remove `SPAM`, add `INBOX`), and a sender that
keeps being misjudged is best fixed for good with a never-spam rule — `create_filter` with
`removeLabels: ["SPAM"]` (see [Filters](#filters-persistent-auto-triage-rules)).

Two things this server deliberately does not do. It does not scan the spam folder and *judge* what
belongs there: measured over one real spam folder, 89% of it carries no mailing-list machinery at
all, so "looks unlike bulk mail" flags nearly the whole folder and filters nothing. And it does not
act on that judgement by itself — releasing mail from spam is a decision, and the context that makes
it obvious ("I just registered there") lives in the conversation, not in the mailbox.

## Security & privacy

> For the full threat model — trust boundary, per-threat mitigations, explicit non-goals, and how to
> report a vulnerability — see **[SECURITY.md](SECURITY.md)**. The highlights:

- **No telemetry.** Nothing phones home — no analytics, no crash reporting, no tracking.
- **No open ports by default.** stdio only. The optional `--http` listener binds to `127.0.0.1`
  (not the LAN) and **refuses to start without a `MAILWARDEN_TOKEN`** bearer token — set
  `MAILWARDEN_ALLOW_NO_TOKEN=1` to override on a trusted, isolated network. On a loopback bind it
  also validates the `Host` header (DNS-rebinding defense). For remote hosting, set `MAILWARDEN_HOST`
  and front it with TLS.
- **No send tools — by design.** mailwarden cannot compose, reply, or forward. A prompt-injected
  instruction inside an email has no exfiltration path through this server. `create_filter` follows
  the same rule: it can label, archive, trash, star or mark mail, but **never** creates a *forwarding*
  filter (which would be an exfiltration path). `list_filters` still surfaces any forwarding filter
  already on the account, so you can spot one. This holds because no such tool exists and none can be
  registered at runtime; for the stronger variant, where *Google* refuses to send rather than
  mailwarden declining to, see **Read-only mode** below.
- **One outbound host, no model-chosen URL.** The `unsubscribe` tool is the only code path that
  contacts a non-Google host. Its endpoint is read from the message's `List-Unsubscribe` header —
  never from a tool argument — the request body is fixed and the response body is discarded, so it
  cannot become a data channel. https/default-port only, redirects re-validated, and any hop resolving
  to a private, loopback, link-local or metadata address is refused. See
  [Unsubscribing](#unsubscribing--the-one-outbound-request).
- **Tool tiers (progressive disclosure + least scope).** `MAILWARDEN_TOOLS` advertises only the tiers
  you name — `read` (the read tools), `manage` (mailbox mutations, snooze, downloads), `filters`
  (server-side filter CRUD, the only tier whose tools need `gmail.settings.basic`). Default is all
  three; e.g. `read,manage` gives a full triage surface without filter management. The **OAuth scopes
  requested at `--auth` are derived from the enabled tiers** — a `read` deployment asks only for
  `gmail.readonly`, and `gmail.settings.basic` is requested only when the `filters` tier is on. And the
  filter tools are **hidden automatically** when the stored token doesn't carry `gmail.settings.basic`
  (e.g. a token authorized before you enabled the tier) — re-run `--auth` to grant it. Older tokens
  without a recorded scope are advertised as before, with the runtime insufficient-scope message as the
  fallback.
- **Read-only mode.** Set `MAILWARDEN_READONLY=1` (shorthand for `MAILWARDEN_TOOLS=read`) and only the
  read tools (`search`, `get_thread`, `list_labels`, `list_snoozed`, `get_profile`, `triage_digest`,
  `list_unsubscribe`, `list_subscriptions`)
  are registered — nothing that can change the mailbox or write
  files is even advertised to clients (the filter tools, which need the broader `gmail.settings.basic`
  scope, are excluded too). Recommended for shared/HTTP deployments that only triage.
  It is also **the only tier whose no-send property Google enforces**: it holds a `gmail.readonly`
  token, which Gmail's send endpoints reject outright. `manage` needs `gmail.modify`, and Gmail
  *does* accept that scope for sending — mailwarden simply exposes no tool that would. So a `read`
  deployment could not send even if this binary were replaced; a `manage` one cannot send because
  there is nothing to call. (There is no send-free write scope to switch to — see
  [SECURITY.md](SECURITY.md), threat 1.)
- **Egress guard.** "Nothing to call" is no longer only a statement about the tool list. Every
  authenticated Gmail request passes one checkpoint that allows exactly the endpoints mailwarden
  uses and refuses the rest — with `messages.send`, `drafts.*`, `messages.import`/`insert`,
  permanent deletion and every non-filter `settings` endpoint named in a deny list checked first, so
  a later edit to the allowlist cannot reopen them by accident — including through the
  `/upload/gmail/v1/...` route `googleapis` takes when a method is handed `media`. A request whose
  host was rewritten (`GOOGLE_CLOUD_UNIVERSE_DOMAIN`, a `rootUrl` option) is refused before the token
  leaves the process. Every method in Gmail's discovery document is tested against the guard. It
  guards *this server*, not the
  token: a stolen `gmail.modify` token can still send from elsewhere.
- **Fenced downloads.** With `MAILWARDEN_DOWNLOAD_DIR` set, attachment writes are confined to that
  directory (realpath-canonicalized, symlink-aware) and never overwrite an existing file.
- **Untrusted-content fencing.** Every tool result is wrapped in `<untrusted-tool-output>` markers
  and stripped of invisible/BiDi-override characters, so clients can tell quoted mail content from
  instructions. The strip also covers Unicode tag characters and the variation selectors supplement
  (invisible ASCII smuggling), and it applies to `structuredContent` as well as the text copy — a
  client reading the machine-readable half gets the same sanitized content.
- **Live API, no copy.** No mailbox mirror or search index is stored anywhere. The only local state
  is your OAuth token in `~/.mailwarden/`.
- **Optional token encryption at rest.** `token.json` holds a refresh token; on disk it is protected
  only by `mode 0o600` (a no-op on Windows). Set `MAILWARDEN_TOKEN_PASSPHRASE` to a passphrase and the token
  is stored AES-256-GCM-encrypted (scrypt-derived key), so a *copy* of the file — a backup, a synced
  folder, another machine — is useless without the passphrase. Re-run `mailwarden --auth` once after
  setting it to encrypt the existing token. Note the boundary: this defends against file theft, **not**
  against malware running as your user (which can read the passphrase from the environment too).

## Quick start

```bash
claude mcp add mailwarden -- npx -y mailwarden
```

That's the whole install — `npx` fetches and runs the published package, no clone or build step. You only need Google OAuth credentials once (below).

## Setup

First time setting up a Google OAuth app? Follow the **[step-by-step setup guide](https://github.com/csitte/mailwarden/blob/main/docs/SETUP.md)** — it walks through the Google Cloud Console with exact click paths, explains the "unverified app" screen, and covers the trap that makes tokens die after 7 days. The short version:

1. **Google Cloud:** create a project → enable the **Gmail API** → configure the OAuth consent screen and **publish it to Production** (in *Testing* status, Google expires refresh tokens after 7 days) → create an **OAuth client ID** of type *Desktop app* → download it as `credentials.json`.
2. Put `credentials.json` in `~/.mailwarden/` (or set `MAILWARDEN_CREDENTIALS=/path/to/credentials.json`).
3. Authorize once — opens a browser, stores a refresh token in `~/.mailwarden/token.json`:
   ```bash
   npx -y mailwarden --auth
   ```
   Scopes requested: `gmail.modify` (read + label/archive/trash) and `gmail.settings.basic`
   (filter management only). If you authorized a version before filters existed, re-run `--auth`
   once to grant the added scope. To hold a token that Gmail itself refuses to send with, authorize
   with `MAILWARDEN_TOOLS=read` — see **Read-only mode** above.
4. **Verify the setup** any time with the built-in doctor:
   ```bash
   npx -y mailwarden --check
   ```
   It checks `credentials.json`, whether a token exists (and if it's encrypted), whether the
   granted scopes cover your enabled tiers, and makes one live Gmail call to prove the token
   still works — printing a concrete fix for anything that's wrong, and exiting non-zero if so
   (handy in CI/health checks). Diagnoses the common traps: no/`wrong` credentials file, never
   authorized, an encrypted token with no `MAILWARDEN_TOKEN_PASSPHRASE`, a missing scope, or the
   7-day "Testing"-consent token expiry.

## Connect

**Claude Code** (local stdio):
```bash
claude mcp add mailwarden -- npx -y mailwarden
```

**Claude Code plugin** — the same server plus a `/mailwarden:setup` skill that walks you through the
OAuth setup and diagnoses a broken one. The repo root is the plugin (`.claude-plugin/plugin.json`), so
from a clone:
```bash
claude --plugin-dir /path/to/mailwarden
```
It is submitted to Anthropic's community marketplace; once listed, `/plugin marketplace add anthropics/claude-plugins-community`
then `/plugin install mailwarden@claude-community` does the same without a clone. The plugin runs the full
tool surface — for a narrower tier (`MAILWARDEN_TOOLS=read`) or a second account, use `claude mcp add` with
the env you want instead (see [Config](#config-env) and [Multiple accounts](#multiple-accounts)).

**Claude Desktop** — add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "mailwarden": { "command": "npx", "args": ["-y", "mailwarden"] }
  }
}
```
Or install the **MCPB bundle** (`mailwarden-<version>.mcpb`, attached to
[GitHub releases](https://github.com/csitte/mailwarden/releases) from 0.10.0 on) as a Desktop extension — Settings →
Extensions → *Install extension…* — the same server, self-contained at run time (no `npx`; Claude
Desktop brings the Node runtime), with the tool tiers as a setting. The bundle is built from the packed
npm package (same file set as published; `npm run mcpb`, verified in CI: validated, unpacked and booted)
and is the same file set Smithery distributes. The one-time `npx -y mailwarden --auth` still applies
(Node needed once for that) — the bundle reads the same `~/.mailwarden/` token.

**Smithery** — listed as [`csitte/mailwarden`](https://smithery.ai/servers/csitte/mailwarden), which serves
that bundle:
```bash
npx -y @smithery/cli install csitte/mailwarden --client claude   # local stdio entry in the client's config
```
Note which of Smithery's two paths you take. The install above writes a plain local server entry: the
process, your token and your mail stay on your machine, exactly as with `npx`. Adding it to Smithery's
**toolbox** instead (`smithery mcp add`) also runs the bundle locally, but relays the tool traffic
through Smithery's gateway so a remote client can reach it — the mailbox content in those responses then
passes through a third party. That is a property of the gateway, not of mailwarden; if you want the
no-third-party guarantee, use the local install, the npm package, or the `.mcpb` from the release page.

**Remote (Streamable HTTP)** — for a VPS / claude.ai custom connector:
```bash
# Loopback + token required by default. For real hosting, bind outward and keep the token:
MAILWARDEN_TOKEN=<secret> MAILWARDEN_HOST=0.0.0.0 npx -y mailwarden --http   # :8787/mcp
```
Then in claude.ai: Settings → Connectors → *Add custom connector* → your `https://your-host/mcp` URL. In Claude Code: `claude mcp add --transport http mailwarden https://your-host/mcp`.

## Multiple accounts

One OAuth app (one `credentials.json`) can authorize several Gmail accounts. Each account keeps its
own refresh token in a separate file, selected by `MAILWARDEN_ACCOUNT`:

```bash
mailwarden --auth --account work        # stores token.work.json
mailwarden --auth --account personal    # stores token.personal.json
```

Run them side by side by registering the server **once per account**, each with its own
`MAILWARDEN_ACCOUNT`. Every instance carries its own token, its own granted scopes and its own tool
surface, and a tool call acts on the account of the entry that carries it and on no other:

```json
{
  "mcpServers": {
    "gmail-work":     { "command": "npx", "args": ["-y", "mailwarden"], "env": { "MAILWARDEN_ACCOUNT": "work" } },
    "gmail-personal": { "command": "npx", "args": ["-y", "mailwarden"], "env": { "MAILWARDEN_ACCOUNT": "personal" } }
  }
}
```

Account names are **case-insensitive** — they become filenames, so `Work` and `work` would be the
same file on Windows/macOS. mailwarden lower-cases them (`--account Work` → `token.work.json`) so a
name always maps to exactly one mailbox.

**Which file `--auth` writes depends only on `--account` / `MAILWARDEN_ACCOUNT` — never on the
account you pick in the browser.** Authorizing a second mailbox *without* `--account` would
therefore aim straight at the first one's token file, so `--auth` checks first and **refuses**
rather than replacing another mailbox's token; `--force` overrides it deliberately. The two knobs
are not interchangeable: `MAILWARDEN_ACCOUNT` is the one for several mailboxes out of one config
directory (it picks `token.<name>.json`), while `MAILWARDEN_DIR` moves the *whole* directory —
useful to keep setups apart entirely, but it does not give you a second account inside one.
`npm run auth` from a repo clone passes neither, i.e. it always serves the default account.

`mailwarden --check` shows the active account and lists the others it finds. With no
`MAILWARDEN_ACCOUNT` set, everything uses the default `token.json` exactly as before — this is fully
backward compatible.

### More than two accounts

Two entries are the easy case. Past that, two properties of this design start to matter.

**Each instance brings its own tools.** The tier split is 8 `read` + 14 `manage` + 3 `filters`, so a
full instance advertises 25 tools and four of them advertise 100. Clients that search their tool
surface on demand absorb that; clients that hold every definition in context do not.

**Several accounts in one client share one model context.** The account boundary binds a *call* to
one mailbox — it does not stop text read from one mailbox from prompting a call against another,
because all of those tool surfaces are in front of the same model. That is a limit of the boundary,
not a defect in it; see threat 8 in [SECURITY.md](SECURITY.md).

One move answers both: **give exactly one mailbox write tools and leave the rest on `read`.**

```json
{
  "mcpServers": {
    "gmail-main":   { "command": "npx", "args": ["-y", "mailwarden"], "env": { "MAILWARDEN_ACCOUNT": "main" } },
    "gmail-work":   { "command": "npx", "args": ["-y", "mailwarden"], "env": { "MAILWARDEN_ACCOUNT": "work",   "MAILWARDEN_TOOLS": "read" } },
    "gmail-club":   { "command": "npx", "args": ["-y", "mailwarden"], "env": { "MAILWARDEN_ACCOUNT": "club",   "MAILWARDEN_TOOLS": "read" } },
    "gmail-archive":{ "command": "npx", "args": ["-y", "mailwarden"], "env": { "MAILWARDEN_ACCOUNT": "archive","MAILWARDEN_TOOLS": "read" } }
  }
}
```

Three things follow at once: the `read` entries only ever ask for `gmail.readonly`, the one scope in
which no-send is enforced by Google rather than by mailwarden's tool surface; the four instances add
up to 49 tools rather than 100; and an instruction injected into any of them finds no write tool for
another mailbox to reach for. When one of the read-only mailboxes does need cleaning up, hand that
entry `manage` for as long as the work takes instead of permanently.

Separate clients — or separate sessions — remove the shared context entirely, at the price of never
having two mailboxes in view at once. Worth it when several mailboxes genuinely need write tools;
otherwise the tier split is the cheaper boundary.

**No tool reads across mailboxes.** `search`, `triage_digest` and `list_subscriptions` each serve
the one account their instance was configured with, so a question like "which newsletter writes to
all four" is four calls whose answers the caller combines. In a setup this size it is worth calling
`get_profile` before the first action that changes anything — it names the mailbox actually on the
other end.

## From source

```bash
git clone https://github.com/csitte/mailwarden && cd mailwarden
npm install && npm run build
node dist/index.js --auth
```

## Config (env)

| Var | Meaning |
|---|---|
| `MAILWARDEN_DIR` | config dir (default `~/.mailwarden`) |
| `MAILWARDEN_CREDENTIALS` | path to `credentials.json` |
| `MAILWARDEN_ACCOUNT` | select a named account (its token is `token.<name>.json`; names are lower-cased); unset = the default `token.json`. See [Multiple accounts](#multiple-accounts) |
| `MAILWARDEN_TOKEN_PASSPHRASE` | passphrase → encrypt `token.json` at rest (AES-256-GCM); re-run `--auth` after setting |
| `MAILWARDEN_AUTO_SWEEP` | `1` → snooze sweep at startup + hourly while running (writes labels — needs the `manage`/`gmail.modify` scope; a `read`-only grant can't sweep) |
| `MAILWARDEN_DOWNLOAD_DIR` | restrict `download_attachment` to this directory (strongly recommended for HTTP hosting) |
| `MAILWARDEN_READONLY` | `1` → register only the read tools (search/get_thread/list_labels/list_snoozed/get_profile/triage_digest/list_unsubscribe/list_subscriptions). Shorthand for `MAILWARDEN_TOOLS=read` |
| `MAILWARDEN_TOOLS` | comma-separated tool tiers to advertise: `read`, `manage`, `filters` (default: all). Also derives the OAuth scopes requested at `--auth`. E.g. `read,manage` drops the filter tools and their `gmail.settings.basic` scope |
| `MAILWARDEN_DEBUG` | `1` → print full errors with stack traces instead of a one-line message (for bug reports) |
| `PORT` | HTTP port (default 8787) |
| `MAILWARDEN_HOST` | HTTP bind address (default `127.0.0.1`; set e.g. `0.0.0.0` for remote hosting) |
| `MAILWARDEN_TOKEN` | bearer token for the HTTP endpoint — **required** for `--http` unless overridden |
| `MAILWARDEN_ALLOW_NO_TOKEN` | `1` → allow `--http` without a token (trusted/isolated networks only) |
| `MAILWARDEN_ALLOWED_HOSTS` | extra comma-separated `host:port` values accepted by the loopback `Host` allowlist |

## Status

Working and used in daily mailbox automation. Core Gmail tools + snooze implemented against `googleapis`, covered by a vitest suite (986 tests — `npm run coverage`). Current version: see the npm badge above, the [changelog](https://github.com/csitte/mailwarden/blob/main/CHANGELOG.md), or [releases](https://github.com/csitte/mailwarden/releases). PRs welcome.

## License

MIT © C.Sitte Softwaretechnik
