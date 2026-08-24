<!-- mcp-name: io.github.omniologynow-rgb/scout-intel-mcp -->
<p align="center">
  <strong>Scout MCP</strong><br>
  Business & Market Intelligence for AI Agents
</p>

<p align="center">
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.11+-blue.svg" alt="Python 3.11+"></a>
  <a href="https://gofastmcp.com"><img src="https://img.shields.io/badge/FastMCP-3.x-00d4aa.svg" alt="FastMCP 3.x"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License"></a>
  <img src="https://img.shields.io/badge/tools-6-cyan.svg" alt="6 Tools">
  <img src="https://img.shields.io/badge/data_sources-5+-orange.svg" alt="5+ Data Sources">
  <a href="https://pypi.org/project/scout-intel-mcp/"><img src="https://img.shields.io/pypi/v/scout-intel-mcp?color=%2334D058&label=pypi" alt="PyPI version"></a>
  <a href="https://pepy.tech/project/scout-intel-mcp"><img src="https://static.pepy.tech/badge/scout-intel-mcp/month" alt="PyPI Downloads/month"></a>
  <a href="https://mcpize.com/mcp/scout-intel"><img src="https://img.shields.io/badge/MCPize-blue?label=marketplace" alt="MCPize"></a>
</p>

---

> **Google for AI agents** — instead of web pages, it returns clean, structured JSON that agents can reason over.

Scout MCP gives any AI agent instant access to structured business intelligence, market research, and competitive analysis. It aggregates data from **DuckDuckGo, NewsAPI, Wikipedia, web scraping, and social profiles** into Pydantic-validated JSON responses with **per-source confidence breakdowns** and **data quality grades**.

---

## Table of Contents

- [Quick Install](#quick-install)
- [The 6 Intelligence Tools](#the-6-intelligence-tools)
- [Data Quality Grades](#data-quality-grades)
- [Confidence Breakdown](#confidence-breakdown)
- [Full API Reference](#full-api-reference)
- [Example Responses](#example-responses)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Pricing & Rate Limits](#pricing--rate-limits)
- [Self-Hosting](#self-hosting)
- [Docker](#docker)
- [Tech Stack](#tech-stack)
- [Data Sources](#data-sources)
- [Contributing](#contributing)

---

## Quick Install

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "scout-mcp": {
      "command": "python",
      "args": ["-m", "scout_mcp.mcp_server"],
      "cwd": "/path/to/scout-mcp/src",
      "env": {
        "NEWS_API_KEY": "your-newsapi-key"
      }
    }
  }
}
```

### Cursor

Add to Cursor Settings > MCP:

```json
{
  "scout-mcp": {
    "command": "python",
    "args": ["-m", "scout_mcp.mcp_server"],
    "cwd": "/path/to/scout-mcp/src",
    "env": {
      "NEWS_API_KEY": "your-newsapi-key"
    }
  }
}
```

### VS Code (Copilot MCP)

Add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "scout-mcp": {
      "command": "python",
      "args": ["-m", "scout_mcp.mcp_server"],
      "cwd": "/path/to/scout-mcp/src",
      "env": {
        "NEWS_API_KEY": "your-newsapi-key"
      }
    }
  }
}
```

### pip (self-hosted)

```bash
pip install scout-mcp
scout-mcp  # starts STDIO server for MCP clients
```

---

## The 6 Intelligence Tools

| # | Tool | What It Does | Tier |
|---|------|-------------|------|
| 1 | `scout_company` | Structured intel on any company: industry, funding, tech stack, competitors, news, key people | Free |
| 2 | `scout_market` | Market research: size, CAGR, key players, trends, growth drivers, risks | Free |
| 3 | `scout_competitors` | Competitor analysis: positioning, pricing, strengths, weaknesses, differentiators | Free |
| 4 | `scout_trends` | Trend tracking: sentiment analysis, key developments, trending direction, related topics | Free |
| 5 | `scout_product` | Product intelligence: pricing, ratings, features, alternatives, recent updates | Free |
| 6 | `scout_person` | Public figure research: role, background, achievements, social profiles | **Pro** |

---

## Data Quality Grades

Every response includes a **`data_quality_grade`** — a letter grade that lets agents instantly assess intelligence reliability:

| Grade | Confidence | Meaning |
|-------|-----------|---------|
| **A+** | 90%+ | Exceptional — multiple high-quality sources confirmed |
| **A** | 80-90% | High — strong multi-source corroboration |
| **B** | 65-80% | Good — solid data from key sources |
| **C** | 45-65% | Fair — limited sources, gaps likely |
| **D** | 25-45% | Low — sparse data, treat with caution |
| **F** | <25% | Insufficient — minimal data available |

### How Agents Should Use Grades

```python
result = scout_company("Stripe")

if result["data_quality_grade"] in ("A+", "A"):
    # High confidence — safe to make decisions on this data
    proceed_with_analysis(result)
elif result["data_quality_grade"] == "B":
    # Good but verify key claims
    proceed_with_caveats(result)
else:
    # C/D/F — supplement with additional sources
    request_more_data(result)
```

---

## Confidence Breakdown

Beyond the letter grade, every response includes a **`confidence_breakdown`** dict showing per-source reliability:

```json
{
  "confidence": 0.86,
  "data_quality_grade": "A",
  "confidence_breakdown": {
    "duckduckgo": {
      "score": 0.60,
      "reason": "8 results found"
    },
    "company_website": {
      "score": 0.90,
      "reason": "scraped stripe.com, 3 data points extracted"
    },
    "wikipedia": {
      "score": 0.90,
      "reason": "page found, structured data extracted"
    },
    "newsapi": {
      "score": 0.90,
      "reason": "6 articles found"
    },
    "competitor_extraction": {
      "score": 0.80,
      "reason": "5 competitors identified"
    }
  }
}
```

### Source Weights

Different sources carry different weights in the overall confidence calculation:

| Source | Weight | Why |
|--------|--------|-----|
| Wikipedia | 3x | Curated, structured, authoritative |
| NewsAPI | 2x | Fresh, professional journalism |
| Company Website | 2x | First-party data, most current |
| DuckDuckGo Search | 1x | Broad but variable quality |
| Competitor Extraction | 1x | Derived analysis |
| Social Profiles | 1x | Supplementary |

---

## Full API Reference

### Base URL

```
POST /api/scout/{tool_name}
```

### Authentication

Pass your API key via the `X-Api-Key` header:

```bash
curl -X POST /api/scout/company \
  -H "X-Api-Key: your-key-here" \
  -H "Content-Type: application/json" \
  -d '{"name": "Stripe"}'
```

No key = free tier (50 requests/day).

### Health & Info

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/` | GET | Service info + list of tools |
| `/api/health` | GET | Health check + DuckDuckGo backoff status |
| `/api/tools` | GET | All tools with params, tiers, and grade descriptions |
| `/api/cache/stats` | GET | Cache hit/miss statistics |
| `/api/cache/clear` | POST | Clear all cached responses |

### Tool Endpoints

#### `POST /api/scout/company`

Research any company.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Company name (e.g., "Stripe", "OpenAI") |
| `domain` | string | No | Company domain (e.g., "stripe.com"). Auto-detected if omitted. |

**Response fields:** `name`, `domain`, `description`, `industry`, `founded`, `headquarters`, `employee_range`, `funding`, `tech_stack`, `social_profiles`, `recent_news`, `top_competitors`, `key_people`, `confidence`, `confidence_breakdown`, `data_quality_grade`, `data_freshness`, `sources_used`, `sources_failed`

---

#### `POST /api/scout/market`

Research any market or industry.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Market to research (e.g., "AI SaaS", "electric vehicles") |
| `depth` | string | No | `"summary"` (default) or `"detailed"` |

**Response fields:** `market_name`, `query`, `depth`, `market_size`, `market_size_projections`, `cagr`, `key_players`, `trends`, `growth_drivers`, `risks`, `source_links`, `confidence`, `confidence_breakdown`, `data_quality_grade`

---

#### `POST /api/scout/competitors`

Find and analyze competitors.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `company_or_product` | string | Yes | Company or product name (e.g., "Notion") |
| `max` | integer | No | Max competitors to return (default 10) |

**Response fields:** `target`, `competitors` (array of `{name, domain, positioning, pricing, strengths, weaknesses, key_differentiator}`), `market_positioning_summary`, `confidence`, `confidence_breakdown`, `data_quality_grade`

---

#### `POST /api/scout/trends`

Track trends and sentiment.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `topic` | string | Yes | Topic to track (e.g., "generative AI") |
| `timeframe` | string | No | `"1d"`, `"7d"` (default), `"30d"`, `"1y"` |

**Response fields:** `topic`, `timeframe`, `sentiment` (`{score, label}`), `trending_direction`, `key_developments`, `related_topics`, `social_buzz`, `confidence`, `confidence_breakdown`, `data_quality_grade`

---

#### `POST /api/scout/product`

Get intelligence on any product.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Product name (e.g., "Slack", "Vercel") |

**Response fields:** `name`, `category`, `description`, `pricing`, `ratings`, `features`, `ideal_for`, `alternatives`, `recent_updates`, `confidence`, `confidence_breakdown`, `data_quality_grade`

---

#### `POST /api/scout/person` (PRO)

Research a public figure. **Requires Pro tier or higher.**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Person's name (e.g., "Sam Altman") |
| `company` | string | No | Company context (e.g., "OpenAI") |

**Response fields:** `name`, `current_role`, `company`, `location`, `background_summary`, `social_profiles`, `recent_activity`, `notable_achievements`, `confidence`, `confidence_breakdown`, `data_quality_grade`

Returns HTTP 403 for free tier users.

---

## Example Responses

### scout_company("Stripe")

```json
{
  "name": "Stripe",
  "domain": "stripe.com",
  "description": "Stripe, Inc. is an Irish-American multinational financial services and software as a service company...",
  "industry": "Software & Technology",
  "founded": "2010",
  "headquarters": "San Francisco",
  "top_competitors": ["PayPal", "Adyen", "Square", "Braintree", "Checkout.com"],
  "tech_stack": ["Next.js", "React"],
  "recent_news": [
    {"headline": "Stripe launches AI billing features", "source": "TechCrunch", "date": "2026-04-08"},
    {"headline": "Stripe revenue grows 30% in 2025", "source": "Bloomberg", "date": "2026-03-15"}
  ],
  "confidence": 0.86,
  "data_quality_grade": "A",
  "confidence_breakdown": {
    "duckduckgo": {"score": 0.60, "reason": "8 results found"},
    "company_website": {"score": 0.90, "reason": "scraped stripe.com, 3 data points extracted"},
    "wikipedia": {"score": 0.90, "reason": "page found, structured data extracted"},
    "newsapi": {"score": 0.90, "reason": "6 articles found"},
    "competitor_extraction": {"score": 0.80, "reason": "5 competitors identified"}
  },
  "data_freshness": "2026-04-12T12:00:00Z"
}
```

### scout_trends("generative AI", timeframe="7d")

```json
{
  "topic": "generative AI",
  "timeframe": "7d",
  "sentiment": {"score": 0.72, "label": "positive"},
  "trending_direction": "up",
  "key_developments": [
    {
      "headline": "OpenAI releases GPT-5.2 with reasoning capabilities",
      "date": "2026-04-10",
      "impact_level": "high",
      "source": "The Verge"
    }
  ],
  "related_topics": ["Large Language Models", "AI Safety", "Enterprise AI"],
  "confidence": 0.83,
  "data_quality_grade": "A",
  "confidence_breakdown": {
    "duckduckgo_news": {"score": 0.90, "reason": "10 news articles found"},
    "newsapi": {"score": 0.90, "reason": "4 articles found"},
    "web_search": {"score": 0.50, "reason": "5 web results for context"}
  }
}
```

### scout_competitors("Notion")

```json
{
  "target": "Notion",
  "competitors": [
    {
      "name": "Obsidian",
      "domain": "obsidian.md",
      "positioning": "Privacy-focused local-first knowledge base with Markdown",
      "strengths": ["Open source", "Free tier available", "Offline support"],
      "key_differentiator": "Local-first with plain Markdown files"
    },
    {
      "name": "Coda",
      "positioning": "All-in-one doc with app-building capabilities",
      "strengths": ["AI-powered features"],
      "key_differentiator": "Document-as-app paradigm"
    },
    {
      "name": "Logseq",
      "positioning": "Open-source outliner with bidirectional links"
    }
  ],
  "market_positioning_summary": "Found 7 competitors for Notion. Top alternatives: Obsidian, Coda, Logseq, Anytype, AppFlowy.",
  "confidence": 0.65,
  "data_quality_grade": "B",
  "confidence_breakdown": {
    "search_Notion alternative": {"score": 0.70, "reason": "8 results for 'Notion alternatives'"},
    "search_Notion vs competi": {"score": 0.60, "reason": "6 results for 'Notion vs competitors'"},
    "extraction_quality": {"score": 0.86, "reason": "7 competitors extracted and enriched"}
  }
}
```

---

## Architecture

```
                      +------------------+
                      |  AI Agent        |
                      |  (Claude, etc.)  |
                      +--------+---------+
                               |
                    STDIO / SSE / REST
                               |
              +----------------+----------------+
              |          Scout MCP              |
              |  FastMCP 3.x + FastAPI REST     |
              +----------------+----------------+
              |  Cache (24h TTL, in-memory)     |
              |  Auth (API key, tier limits)     |
              |  Rate Limiter (per-key, daily)   |
              +----+--------+--------+----------+
                   |        |        |
          +--------+  +-----+--+  +--+--------+
          | DuckDuckGo| | NewsAPI | | Wikipedia |
          | (free)    | | (.org)  | | (free)    |
          +-----------+ +---------+ +-----------+
                   |                    |
          +--------+--------+  +-------+-------+
          | Web Scraper     |  | Social Profile |
          | (httpx + BS4)   |  | Detection      |
          +----------------+  +----------------+
```

### Exponential Backoff (DuckDuckGo)

DuckDuckGo's free API has rate limits. Scout MCP handles this with adaptive backoff:

```
Success  : interval = 2s (base)
Failure 1: interval = 4s
Failure 2: interval = 8s
Failure 3: interval = 16s
Failure 4: interval = 32s
Failure 5: interval = 48s (cap)
Next success: interval resets to 2s
```

Each call also retries once before giving up. Monitor backoff status at `GET /api/health`.

### Competitor Extraction Engine

The competitor extraction uses 6 regex pattern categories with 350+ stop words:

1. **VS patterns** — "X vs Y" matching
2. **Comma/and-separated lists** — "alternatives include X, Y, and Z"
3. **Numbered/bulleted lists** — "1. Asana 2. Monday 3. ClickUp"
4. **Header patterns** — "Asana -- project management tool"
5. **Contextual patterns** — "like X" or "such as X"
6. **Title-cased names** — capitalized product names near competitor context

Multi-word validators reject: article titles, verb-prefixed names, pronoun-prefixed names, role-suffixed names, probable person names, mega-corp parent names, and platform names.

---

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEWS_API_KEY` | Yes | — | NewsAPI.org API key ([get one free](https://newsapi.org/register)) |
| `SCOUT_API_KEY` | No | — | Master API key (auto-assigned "scale" tier) |
| `MONGO_URL` | Auto | — | MongoDB connection string (for REST API server) |
| `DB_NAME` | Auto | — | MongoDB database name |
| `CORS_ORIGINS` | No | `*` | Allowed CORS origins |

### Cache Settings

Responses are cached for **24 hours** in-memory (dict). Cache stats and clear endpoints:

```bash
# Check cache stats
curl /api/cache/stats

# Clear all cache
curl -X POST /api/cache/clear
```

---

## Pricing & Rate Limits

| Tier | Price | Daily Limit | Tools | Features |
|------|-------|-------------|-------|----------|
| **Free** | $0/mo | 50 requests | 5 of 6 | Summary depth, basic grades |
| **Pro** | $29/mo | 1,000 requests | All 6 | + `scout_person` + detailed market reports |
| **Scale** | $99/mo | 10,000 requests | All 6 | Everything + priority support |

Rate limit info is included in every response's `_meta` field:

```json
{
  "_meta": {
    "tier": "free",
    "remaining": 47
  }
}
```

---

## Self-Hosting

### Local Development

```bash
# Clone and install
git clone https://github.com/your-org/scout-mcp.git
cd scout-mcp/backend
pip install -e ".[dev,server]"

# Set up environment
echo "NEWS_API_KEY=your-key" > .env

# Run MCP server (STDIO for Claude Desktop)
cd src && python -m scout_mcp.mcp_server

# Run REST API server
uvicorn server:app --host 0.0.0.0 --port 8001 --reload

# Inspect with MCP Inspector
fastmcp inspect src/scout_mcp/mcp_server.py
```

### Running Tests

```bash
# Test the API
curl -X POST http://localhost:8001/api/scout/company \
  -H "Content-Type: application/json" \
  -d '{"name": "OpenAI"}'

# Check health + backoff status
curl http://localhost:8001/api/health

# List all tools
curl http://localhost:8001/api/tools
```

---

## Docker

```dockerfile
FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc libxml2-dev libxslt1-dev && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml .
COPY src/ src/
RUN pip install --no-cache-dir .
EXPOSE 8001
CMD ["python", "-c", "from scout_mcp.mcp_server import mcp; mcp.run(transport='sse', port=8001)"]
```

```bash
# Build and run
docker build -t scout-mcp .
docker run -p 8001:8001 -e NEWS_API_KEY=your-key scout-mcp
```

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| MCP Framework | FastMCP 3.x | Tool registration, STDIO/SSE transport |
| REST API | FastAPI | HTTP endpoints for testing |
| HTTP Client | httpx | Async web scraping |
| HTML Parser | BeautifulSoup4 + lxml | Structured data extraction |
| Search | DuckDuckGo (ddgs) | Free web + news search |
| News | NewsAPI.org | Professional news articles |
| Knowledge | Wikipedia API | Structured background data |
| Validation | Pydantic 2.x | Response model validation |
| Caching | In-memory dict (24h TTL) | Response caching |
| Server | uvicorn | ASGI production server |

---

## Data Sources

| Source | API Key? | Cost | Rate Limit | Reliability |
|--------|----------|------|------------|-------------|
| DuckDuckGo Search | No | Free | Soft limits (backoff) | Variable |
| DuckDuckGo News | No | Free | Soft limits (backoff) | Variable |
| NewsAPI.org | Yes | Free tier | 100 req/day | High |
| Wikipedia API | No | Free | Unlimited (polite) | Very High |
| Web Scraping (httpx) | No | Free | Per-site limits | Medium |
| Social Profile Detection | No | Free | Via DuckDuckGo | Variable |

### Future Sources (Planned)

- Crunchbase API (funding data)
- SimilarWeb API (traffic data)
- GitHub API (developer tools)
- SEMrush API (SEO data)

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Install dev dependencies: `pip install -e ".[dev]"`
4. Make your changes
5. Run tests: `pytest`
6. Submit a pull request

### Adding a New Data Source

1. Create `src/scout_mcp/sources/your_source.py`
2. Implement async functions that return structured data
3. Add the source to relevant tools in `src/scout_mcp/tools/`
4. Add per-source confidence scoring
5. Update this README

### Adding a New Tool

1. Create `src/scout_mcp/tools/your_tool.py`
2. Add a Pydantic model in `models.py` (include `confidence_breakdown` and `data_quality_grade`)
3. Register in `mcp_server.py` with `@mcp.tool()`
4. Add REST endpoint in `server.py`
5. Update this README

---

## License

MIT

---

<p align="center">
  Built with FastMCP, httpx, BeautifulSoup4, Pydantic<br>
  <em>Scout MCP v0.1.0</em>
</p>

---

<p align="center">
  🚀 Also check out <strong><a href="https://github.com/omniologynow-rgb/profitspot-mcp">ProfitSpot MCP</a></strong> — cross-chain DeFi intelligence for AI agents. Risk-scored yields, Monte Carlo simulations, whale tracking across 86 chains.
</p>
