# StatusCraft — MCP Service Status Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Node: >=18](https://img.shields.io/badge/Node-%3E%3D18-brightgreen)](https://nodejs.org)
[![MCP Compatible](https://img.shields.io/badge/MCP-compatible-blue)](https://modelcontextprotocol.io)

> **MCP server that checks the live status of 3355 software services in real time.** Ask your AI agent "is GitHub down?" or "what's wrong with Sentry?" — and get a live answer pulled directly from official status pages, including full incident detail when something is broken.

**Install:** `npx -y github:jabbawocky/statuscraft` (no API key needed)  
**Works with:** Claude Desktop, Claude Code, Cursor, Windsurf, any MCP-compatible client

---

## What it does

StatusCraft gives your AI client 5 tools that fetch live status from **3355 major services**:

| Tool | What it does |
|---|---|
| `get_status` | Check one service — returns normalized status + incident detail when non-operational |
| `get_all_status` | Check all 3355 services at once, grouped by status (cached 60s) |
| `list_services` | List all tracked services with IDs and tags — filter by category |
| `check_multiple` | Check a specific list of services in parallel |
| `refresh_status` | Force a live re-fetch, bypassing the 60s cache — useful during active incidents |

### Incident detail

When a service is non-operational, StatusCraft automatically fetches the incidents API and returns structured detail alongside the status:

```json
{
  "id": "sentry",
  "name": "Sentry",
  "status": "degraded",
  "description": "Partially Degraded Service",
  "incident": {
    "name": "Notification delivery",
    "impact": "minor",
    "status": "monitoring",
    "started_at": "2026-06-11T09:50:38.604Z",
    "latest_update": "Notifications delivery is now close to fully functional. Root cause identified as a cloud provider issue — monitoring closely.",
    "affected_components": ["Notifications"]
  },
  "last_checked": "2026-06-11T13:20:00.000Z",
  "source_url": "https://status.sentry.io"
}
```

No extra latency when everything is green — the incident fetch only fires for non-operational services.

---

## Services tracked (3355)

### AI & LLMs
| ID | Service |
|---|---|
| `anthropic` | Anthropic |
| `openai` | OpenAI |
| `google_ai` | Google AI |
| `cohere` | Cohere |
| `replicate` | Replicate |

### Cloud & Infrastructure
| ID | Service |
|---|---|
| `aws` | AWS |
| `azure` | Azure |
| `google_cloud` | Google Cloud |
| `digitalocean` | DigitalOcean |

### Hosting & Deployment
| ID | Service |
|---|---|
| `vercel` | Vercel |
| `netlify` | Netlify |
| `render` | Render |
| `fly` | Fly.io |
| `heroku` | Heroku |
| `railway` | Railway |

### Developer Tools & APIs
| ID | Service |
|---|---|
| `github` | GitHub |
| `postman` | Postman |
| `clerk` | Clerk |
| `launchdarkly` | LaunchDarkly |
| `linear` | Linear |
| `atlassian` | Atlassian |
| `jira_cloud` | Jira Cloud |
| `confluence` | Confluence |
| `bitbucket` | Bitbucket |

### Databases
| ID | Service |
|---|---|
| `supabase` | Supabase |
| `neon` | Neon |
| `mongodb_atlas` | MongoDB Atlas |
| `planetscale` | PlanetScale |

### Payments & Fintech
| ID | Service |
|---|---|
| `stripe` | Stripe |
| `brex` | Brex |

### Communication & Messaging
| ID | Service |
|---|---|
| `slack` | Slack |
| `discord` | Discord |
| `twilio` | Twilio |
| `sendgrid` | SendGrid |
| `resend` | Resend |

### Observability & Monitoring
| ID | Service |
|---|---|
| `datadog` | Datadog |
| `sentry` | Sentry |
| `new_relic` | New Relic |
| `grafana_cloud` | Grafana Cloud |
| `pagerduty` | PagerDuty |

### Analytics & Data
| ID | Service |
|---|---|
| `segment` | Segment |
| `amplitude` | Amplitude |
| `mixpanel` | Mixpanel |

### CDN & Networking
| ID | Service |
|---|---|
| `cloudflare` | Cloudflare |
| `cloudinary` | Cloudinary |

### Productivity & Workspace
| ID | Service |
|---|---|
| `notion` | Notion |
| `airtable` | Airtable |
| `zapier` | Zapier |
| `hubspot` | HubSpot |
| `intercom` | Intercom |
| `shopify` | Shopify |
| `figma` | Figma |
| `loom` | Loom |
| `zoom` | Zoom |
| `onepassword` | 1Password |
| `box` | Box |
| `dropbox` | Dropbox |

### Identity & Authentication
| ID | Service |
|---|---|
| `auth0` | Auth0 |
| `okta` | Okta |

### Project Management & Collaboration
| ID | Service |
|---|---|
| `asana` | Asana |
| `miro` | Miro |
| `monday` | monday.com |

### No-code & Web Builders
| ID | Service |
|---|---|
| `webflow` | Webflow |

### Marketing & CRM
| ID | Service |
|---|---|
| `activecampaign` | ActiveCampaign |
| `typeform` | Typeform |

### Search & Observability
| ID | Service |
|---|---|
| `elastic` | Elastic Cloud |

### Fintech & Payments
| ID | Service |
|---|---|
| `plaid` | Plaid |

### Security
| ID | Service |
|---|---|
| `snyk` | Snyk |

### Networking
| ID | Service |
|---|---|
| `tailscale` | Tailscale |

### Infrastructure & DevOps
| ID | Service |
|---|---|
| `hashicorp` | HashiCorp |

### Data & Analytics
| ID | Service |
|---|---|
| `snowflake` | Snowflake |

### Internal Tools & Automation
| ID | Service |
|---|---|
| `retool` | Retool |
| `make` | Make |

### Notifications & Background Jobs
| ID | Service |
|---|---|
| `courier` | Courier |
| `inngest` | Inngest |

### Workflow Orchestration
| ID | Service |
|---|---|
| `temporal` | Temporal Cloud |

### Data Pipeline & ETL
| ID | Service |
|---|---|
| `fivetran` | Fivetran |
| `dbt_cloud` | dbt Cloud |

### Testing & QA
| ID | Service |
|---|---|
| `browserstack` | BrowserStack |
| `saucelabs` | Sauce Labs |

### Documents & Signatures
| ID | Service |
|---|---|
| `docusign` | DocuSign |

### Work Management
| ID | Service |
|---|---|
| `smartsheet` | Smartsheet |
| `shortcut` | Shortcut |
| `productboard` | Productboard |

### Documents & Collaboration
| ID | Service |
|---|---|
| `coda` | Coda |

### CMS & Content
| ID | Service |
|---|---|
| `contentful` | Contentful |

### Error Tracking
| ID | Service |
|---|---|
| `rollbar` | Rollbar |
| `honeybadger` | Honeybadger |

### Incident Management
| ID | Service |
|---|---|
| `incident_io` | incident.io |

### Accounting & Finance
| ID | Service |
|---|---|
| `xero` | Xero |

### Email Marketing & Automation
| ID | Service |
|---|---|
| `iterable` | Iterable |
| `klaviyo` | Klaviyo |
| `mailgun` | Mailgun |
| `sparkpost` | SparkPost |

### Compliance & Security Auditing
| ID | Service |
|---|---|
| `vanta` | Vanta |
| `drata` | Drata |
| `secureframe` | Secureframe |

### Video & Real-time Communications
| ID | Service |
|---|---|
| `livekit` | LiveKit |
| `daily` | Daily |
| `bandwidth` | Bandwidth |
| `plivo` | Plivo |

### CI/CD & Registries
| ID | Service |
|---|---|
| `circleci` | CircleCI |
| `npm` | npm |

### Entertainment & Media
| ID | Service |
|---|---|
| `twitch` | Twitch |

### Product Analytics & UX
| ID | Service |
|---|---|
| `heap` | Heap |
| `hotjar` | Hotjar |
| `fullstory` | FullStory |
| `logrocket` | LogRocket |
| `contentsquare` | Contentsquare |
| `appcues` | Appcues |
| `pendo` | Pendo |

### Vector Databases
| ID | Service |
|---|---|
| `pinecone` | Pinecone |

### Log Management
| ID | Service |
|---|---|
| `mezmo` | Mezmo |
| `sumo_logic` | Sumo Logic |

### BI & Data Exploration
| ID | Service |
|---|---|
| `metabase` | Metabase |

### Billing & Subscriptions
| ID | Service |
|---|---|
| `chargebee` | Chargebee |

### Sales Intelligence & CRM
| ID | Service |
|---|---|
| `salesloft` | Salesloft |
| `gong` | Gong |
| `clearbit` | Clearbit |
| `close` | Close |

### Customer Support & Helpdesk
| ID | Service |
|---|---|
| `helpscout` | Help Scout |
| `talkdesk` | Talkdesk |

### Project Management
| ID | Service |
|---|---|
| `teamwork` | Teamwork |

### Forms & Surveys
| ID | Service |
|---|---|
| `jotform` | JotForm |
| `surveymonkey` | SurveyMonkey |
| `qualtrics` | Qualtrics |

### BI & Data Notebooks
| ID | Service |
|---|---|
| `mode` | Mode |
| `sisense` | Sisense |
| `hex` | Hex |

### Localization & i18n
| ID | Service |
|---|---|
| `crowdin` | Crowdin |
| `lokalise` | Lokalise |

### Video & Media Processing
| ID | Service |
|---|---|
| `mux` | Mux |
| `bunny` | Bunny.net |
| `imgix` | Imgix |

### Headless CMS
| ID | Service |
|---|---|
| `prismic` | Prismic |

### Databases
| ID | Service |
|---|---|
| `neo4j` | Neo4j Aura |

### Developer Tools / Testing
| ID | Service |
|---|---|
| `coveralls` | Coveralls |
| `hcti` | HTML/CSS to Image |
| `rainforestqa` | Rainforest QA |
| `applitools` | Applitools |
| `testsigma` | Testsigma |
| `katalon` | Katalon |
| `bugfender` | Bugfender |

### Mobile Attribution
| ID | Service |
|---|---|
| `singular` | Singular |
| `airbridge` | Airbridge |

### Open Banking / Financial Data
| ID | Service |
|---|---|
| `mono` | Mono |
| `tink` | Tink |
| `yapily` | Yapily |

### Sales Intelligence / B2B Data
| ID | Service |
|---|---|
| `leadfeeder` | Leadfeeder |
| `phantombuster` | PhantomBuster |
| `uplead` | UpLead |
| `bookyourdata` | BookYourData |

### Email Builder Tools
| ID | Service |
|---|---|
| `dyspatch` | Dyspatch |
| `movableink` | Movable Ink |
| `beefree` | Beefree |
| `stripo` | Stripo |

### API Management
| ID | Service |
|---|---|
| `tyk` | Tyk Cloud |

### Crypto Exchanges
| ID | Service |
|---|---|
| `bitstamp` | Bitstamp |
| `crypto_com` | Crypto.com |

### Customer Support
| ID | Service |
|---|---|
| `helpdesk` | HelpDesk |

### Security Automation / SOAR
| ID | Service |
|---|---|
| `torq` | Torq |

### SEO / Web Crawling
| ID | Service |
|---|---|
| `lumar` | Lumar |

### AI / ML Platforms
| ID | Service |
|---|---|
| `lightning_ai` | Lightning AI |

### HR Integrations
| ID | Service |
|---|---|
| `stackone` | StackOne |

### Authorization
| ID | Service |
|---|---|
| `authzed` | Authzed |

### Creator Economy
| ID | Service |
|---|---|
| `stan_store` | Stan |

### Conversational AI
| ID | Service |
|---|---|
| `cognigy` | Cognigy |

### Data Lakehouse
| ID | Service |
|---|---|
| `dremio` | Dremio Cloud |

### Data Catalog
| ID | Service |
|---|---|
| `alation` | Alation |

---

## Install

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "statuscraft": {
      "command": "npx",
      "args": ["-y", "github:jabbawocky/statuscraft"]
    }
  }
}
```

### Claude Code

```bash
claude mcp add statuscraft npx -- -y github:jabbawocky/statuscraft
```

No API key required.

---

## Example prompts

- *"Is GitHub down right now?"*
- *"Check the status of all my services"*
- *"What's wrong with Sentry?"*
- *"Are Stripe and SendGrid both operational?"*
- *"Which AI services are having issues?"*
- *"Show me all observability services"*
- *"Check openai, anthropic, and github"*
- *"Is Grafana Cloud having a major outage?"*
- *"Is CircleCI down? What's the current incident?"*
- *"Check Figma, Notion, and Loom status"*
- *"Is Jira Cloud having issues?"*
- *"Check Box and Dropbox"*
- *"Is Okta down?"*
- *"Check Asana, Miro, and monday.com"*

---

## Status values

| Value | Meaning |
|---|---|
| `operational` | All systems normal |
| `degraded` | Performance issues or minor disruption |
| `partial_outage` | Some features or regions affected |
| `major_outage` | Widespread outage |
| `maintenance` | Scheduled maintenance in progress |
| `unknown` | Could not reach status page |

---

## Adding new services

Most services that run Statuspage expose a standard `/api/v2/status.json` endpoint — adding a new service is a 6-line entry in `src/index.ts`:

```typescript
{
  id: "myservice",
  name: "My Service",
  tags: ["hosting", "api"],
  status_url: "https://status.myservice.com/api/v2/status.json",
  page_url: "https://status.myservice.com",
  type: "statuspage",
}
```

Services using non-standard status pages (Azure RSS, AWS JSON, Slack, incident.io) use custom handler types already implemented in the codebase.

PRs welcome.

---

## Requirements

- Node.js 18+
- Claude Desktop or any MCP-compatible client

---

## License

MIT
