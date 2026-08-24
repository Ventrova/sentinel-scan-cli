# @poststack.dev/mcp

Model Context Protocol server for the
[PostStack](https://poststack.dev) Email API — an
[EU-hosted, GDPR-compliant](https://poststack.dev/security)
[email API for AI agents](https://poststack.dev/docs/mcp). Lets assistants
like Claude, Cursor, and Windsurf send transactional email, draft replies
from inbound threads, run deliverability checks, summarise broadcasts, and
more — through one curated tool surface.

102 tools, 5 prompts, and 5 resources, all surfaced over either the local
stdio bin or the hosted HTTP transport at `https://api.poststack.dev/mcp`.

Full MCP reference: [poststack.dev/docs/mcp](https://poststack.dev/docs/mcp).

## Quickstart

### Hosted (Claude.ai connector, hosted agents)

Point any MCP client at:

```
https://api.poststack.dev/mcp
```

Authenticate with your PostStack API key as a Bearer token. No local install required.

### Claude Desktop (stdio)

```json
{
	"mcpServers": {
		"poststack": {
			"command": "npx",
			"args": ["-y", "@poststack.dev/mcp"],
			"env": {
				"POSTSTACK_API_KEY": "sk_live_your_api_key_here"
			}
		}
	}
}
```

Config file location:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

You can also generate the snippet with:

```bash
npx @poststack.dev/mcp --print-config claude-desktop
```

### Claude Code

```bash
claude mcp add poststack -e POSTSTACK_API_KEY=sk_live_your_api_key_here -- npx -y @poststack.dev/mcp
```

### Cursor / VS Code

Same JSON shape as Claude Desktop, in the editor's MCP settings.

## Environment variables

| Variable              | Required | Description                                                 |
| --------------------- | -------- | ----------------------------------------------------------- |
| `POSTSTACK_API_KEY`   | yes      | PostStack API key (`sk_live_…` or `sk_test_…`)              |
| `POSTSTACK_MCP_TRACE` | no       | Set to `1` to emit per-tool-call NDJSON telemetry to stderr |

## What the agent gets

The MCP server doesn't just mirror the REST API — it gives agents the context tools they need to make sensible decisions: spam-checking before sending, deliverability summaries before picking a from-address, engagement scores before re-engaging a contact.

### Worked example: welcome email

The `draft_welcome_email` prompt walks an agent through:

1. `get_contact_by_email` — confirm the contact and capture properties
2. `list_templates` — pick a published welcome template
3. `render_template` — render with the contact's properties; surface any missing variables
4. `suggest_from_address` — pick a verified from-address based on existing mailboxes
5. `preview_email` — render + spam check + deliverability warnings in one round-trip
6. `send_email` — only if preview passed

Other prompts cover re-engagement, follow-up campaigns to non-clickers, broadcast summaries, and inbound triage.

## Reference

<!-- TOOLS:START -->

### Tools (102)

#### emails

- `send_email` — Send a single transactional email immediately, or schedule it for a future time.
- `send_batch_emails` — Send multiple emails in a single batch request (up to 100 per call).
- `list_emails` — List previously-sent emails with optional filters and pagination.
- `get_email` — Get full details and event timeline for a specific email by id.
- `cancel_email` — Cancel a scheduled email that has not yet entered the sending pipeline.
- `reschedule_email` — Reschedule a scheduled email to a new send time.
- `lint_email` — Run a Rspamd-backed spam pre-flight on a draft email and return the score, action, and per-rule symbols.
- `preview_email` — Render + lint + measure an email in one shot WITHOUT sending it.

#### email-validations

- `validate_email` — Check whether an email address is safe to send to BEFORE create_contact or send_email.
- `validate_email_batch` — Validate up to 100 email addresses in a single call. Same checks as validate_email per address.

#### contacts

- `create_contact` — Create a new contact (person who can receive emails / broadcasts).
- `list_contacts` — List contacts with optional search and segment filtering.
- `get_contact` — Get full details of a contact by id.
- `update_contact` — Update an existing contact's name, properties, or subscription state.
- `delete_contact` — Permanently delete a contact (irreversible — use unsubscribe_contact for opt-outs).
- `unsubscribe_contact` — Mark a contact as unsubscribed from all email (preserves the contact record).
- `get_contact_by_email` — Look up a contact by their email address.
- `get_contact_activity` — Get a contact's recent email-event timeline grouped by event type (sent / delivered / opened / clicked / bounced / complained / failed).
- `get_engagement_summary` — Get a single contact's engagement summary: segment + lifetime counts + open / click rates + last open / click + top tags.
- `search_contacts` — Search contacts with filters (segment, engagement, unsubscribed) and a fuzzy query across email/first_name/last_name. Adds a match_reason on each row indicating which field matched the query.

#### templates

- `create_template` — Create a new email template with {{variable}} placeholders.
- `list_templates` — List email templates.
- `get_template` — Get a template's full body, subject and variables.
- `update_template` — Update an existing template's name, subject, body or variable list.
- `delete_template` — Permanently delete a template (irreversible).
- `publish_template` — Mark a template as published so it can be referenced by send_email.
- `unpublish_template` — Mark a template as unpublished so it cannot be sent.
- `duplicate_template` — Create a copy of an existing template (new id, same body, name suffixed " (copy)").
- `render_template` — Server-side render a template with the provided variables.

#### broadcasts

- `create_broadcast` — Create a draft broadcast targeted at a segment.
- `list_broadcasts` — List broadcasts.
- `get_broadcast` — Get a broadcast's details and aggregate delivery stats.
- `update_broadcast` — Edit a draft broadcast in place. Only draft broadcasts can be updated.
- `send_broadcast` — Dispatch a draft broadcast to its segment immediately.
- `cancel_broadcast` — Cancel a queued or sending broadcast.
- `broadcast_performance` — Get broadcast performance — either for one broadcast (variant breakdown if A/B) or for a leaderboard ranked by a chosen metric.
- `find_non_clickers` — List contacts who received a broadcast but did NOT click any tracked link in it.

#### segments

- `create_segment` — Create a static contact segment (manually-managed list).
- `list_segments` — List contact segments.
- `get_segment` — Get a segment's details and member count.
- `update_segment` — Rename an existing segment.
- `delete_segment` — Delete a segment definition. Contacts in it are NOT deleted.
- `add_contacts_to_segment` — Add one or more contacts to a segment.
- `remove_contact_from_segment` — Remove a single contact from a segment.

#### workflows

- `list_workflows` — List all workflows (event-triggered automation pipelines) defined for this team.
- `get_workflow` — Get full details of a workflow including its ordered steps.
- `create_workflow` — Create a new workflow shell (no steps yet, status=draft).
- `update_workflow` — Update a workflow's name, trigger type, or trigger config.
- `delete_workflow` — Permanently delete a workflow and its steps. In-flight runs are NOT cancelled — they finish on the live engine.
- `add_workflow_step` — Append (or insert) a step to a workflow.
- `update_workflow_step` — Update a step's config. Cannot change step_type or position — delete and re-add for that.
- `remove_workflow_step` — Remove a step from a workflow. Remaining steps keep their positions (gaps are allowed).
- `activate_workflow` — Move a workflow from draft/paused to active so new trigger events start runs.
- `pause_workflow` — Pause an active workflow so new trigger events DO NOT start runs. In-flight runs continue to completion.
- `trigger_workflow` — Manually fire a workflow for a specific contact. Works for any trigger_type, but most useful for "manual" workflows.

#### signup-forms

- `list_signup_forms` — List embeddable signup forms.
- `get_signup_form` — Get full details of a signup form including its fields, target segment, and submission count.
- `create_signup_form` — Create an embeddable signup form. Submissions create a contact and optionally add them to a segment / subscription topic.
- `update_signup_form` — Update a signup form's fields, target segment/topic, messaging, or active state.
- `delete_signup_form` — Permanently delete a signup form. Embedded copies on existing pages will fail with 404.

#### domains

- `create_domain` — Add a new sending domain to PostStack.
- `list_domains` — List sending domains.
- `get_domain` — Get domain details including DNS records and verification status.
- `verify_domain` — Trigger DNS verification for a domain.
- `update_domain` — Update domain settings (tracking, TLS, inbound, BIMI, sending stream).
- `delete_domain` — Permanently delete a sending domain (irreversible — historical email records remain).
- `check_deliverability` — Check whether a from-address is safe to send from RIGHT NOW.

#### mailboxes

- `create_mailbox` — Provision a mailbox (IMAP/SMTP inbox) on a verified domain.
- `list_mailboxes` — List mailboxes across all domains.
- `get_mailbox` — Get a mailbox's metadata (status, quota, last login).
- `update_mailbox` — Update a mailbox's display name, quota, status, or webhook setting.
- `delete_mailbox` — Permanently delete a mailbox and all its stored mail.
- `change_mailbox_password` — Reset a mailbox's IMAP/SMTP password.
- `suggest_from_address` — Suggest sensible from-addresses for a given purpose, drawn from the team's verified domains + existing mailboxes.

#### inbound-emails

- `list_inbound_emails` — List inbound emails received by mailboxes on this account.
- `get_inbound_email` — Get a received inbound email's full headers and body.
- `list_inbound_email_attachments` — List attachments on an inbound email (filename, size, contentType).
- `reply_to_inbound_email` — Send a reply to an inbound email (subject and threading headers are set automatically).
- `forward_inbound_email` — Forward an inbound email to other recipients with an optional cover note.
- `draft_from_thread` — Build a reply-draft skeleton for an inbound email — proper threading, quoted original, salutation/sign-off, suggested from + subject. Heuristic only; the agent fills in the body text.

#### webhooks

- `create_webhook` — Subscribe a URL to receive event notifications via signed POST requests.
- `list_webhooks` — List configured webhook endpoints.
- `get_webhook` — Get a webhook's details.
- `update_webhook` — Edit a webhook's URL, event list, or enabled state.
- `delete_webhook` — Permanently delete a webhook endpoint.

#### subscription-topics

- `create_subscription_topic` — Create a subscription topic (named opt-in/opt-out preference like "Product Updates").
- `list_subscription_topics` — List all subscription topics defined for this account.
- `delete_subscription_topic` — Permanently delete a subscription topic. Subscriptions are removed.
- `get_contact_subscriptions` — List the subscription topics a contact is currently opted in to.
- `subscribe_contact_to_topic` — Opt a contact in to a subscription topic.
- `unsubscribe_contact_from_topic` — Opt a contact out of a subscription topic.

#### contact-properties

- `create_contact_property` — Define a custom contact property (typed schema for the contact.properties field).
- `list_contact_properties` — List all custom contact properties defined for this account.
- `update_contact_property` — Edit a custom contact property's label, options or required flag.
- `delete_contact_property` — Remove a custom contact property definition. Existing contact values for this property are dropped.

#### suppressions

- `list_suppressions` — List suppressed email addresses (will not receive any emails).
- `add_suppression` — Block an email address from receiving any future sends.
- `remove_suppression` — Remove an address from the suppression list (sends will resume).

#### api-keys

- `create_api_key` — Generate a new PostStack API key. The full key is returned ONCE in this response and cannot be retrieved again.
- `list_api_keys` — List API keys (only the prefix is returned, never the full secret).
- `get_api_key` — Get an API key's metadata (the secret is never returned after creation).
- `revoke_api_key` — Permanently revoke an API key — all subsequent requests using it will fail.

### Prompts (5)

- `draft_welcome_email` — Guide the agent through drafting and sending a personalised welcome email to a new contact. Looks the contact up, picks a published welcome template, renders it, lints, and sends.
- `reengage_dormant` — Find dormant contacts and draft a re-engagement campaign. Pulls the dormant segment, picks an opt-out-friendly template, and stages a broadcast for review.
- `followup_non_clickers` — Demo B path — find the best-performing recent broadcast, identify recipients who did NOT click, and draft a follow-up to them.
- `summarize_campaign` — Produce a short performance report for a broadcast: headline metrics, A/B winner if applicable, and a one-line recommendation.
- `triage_inbound` — Read an inbound email, classify it (support / sales / billing / spam / other), and propose the next action. Drafts a reply skeleton if appropriate.

### Resources (5)

- `poststack://templates` — List of all email templates for the authenticated team. Includes id, name, subject, version, published flag.
- `poststack://templates/{id}` — A single template by publicId — full body, subject, variables.
- `poststack://domains` — List of sending domains for the authenticated team — name, status, DNS records, tracking flags.
- `poststack://segments` — List of contact segments for the authenticated team — id, name, contact count.
- `poststack://brand` — Authenticated team identity + a default sending suggestion. Includes team name, verified domain count, and the recommended from-address derived from existing mailboxes.

<!-- TOOLS:END -->

## Links

- [PostStack — EU email API](https://poststack.dev)
- [MCP server documentation](https://poststack.dev/docs/mcp) — full tool / prompt / resource reference
- [Hosted MCP transport](https://api.poststack.dev/mcp) — no local install required
- [TypeScript SDK](https://poststack.dev/docs/sdk) · [REST API](https://poststack.dev/docs)
- [Pricing](https://poststack.dev/pricing) — free 3,000 emails/month
- [Status](https://poststack.dev/status) · [Security](https://poststack.dev/security)

## License

MIT — see [LICENSE](./LICENSE).
