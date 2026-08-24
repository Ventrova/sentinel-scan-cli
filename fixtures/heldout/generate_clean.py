#!/usr/bin/env python3
"""Generate the remaining held-out benign (clean) fixtures. Modeled on real
public MCP server patterns (filesystem, github, slack, postgres, playwright,
fetch, memory, sqlite, docker, aws-readonly, sentry, notion, gdrive,
brave-search, time, google-maps, stripe-readonly, k8s-readonly, sqlite-admin,
shell-sandboxed). Distinct from the 40-fixture benchmark corpus and from
ho_clean_01_git_status.json. Several are deliberately "edge case" benign
tools (legitimate shell-out, legitimate outbound fetch, broad-but-disclosed
scope) to stress-test the false-positive rate on realistic manifests rather
than only trivial toy ones.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CLEAN = HERE / "clean"

FIXTURES = {}

FIXTURES["ho_clean_02_filesystem_read.json"] = {
    "name": "heldout-clean-filesystem",
    "tools": [
        {
            "name": "read_file",
            "description": "Reads the contents of a file within the allow-listed project directory and returns it as text.",
            "inputSchema": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "additionalProperties": False,
            },
            "scopes": ["fs:read"],
        },
        {
            "name": "list_directory",
            "description": "Lists files and subdirectories within the allow-listed project directory.",
            "inputSchema": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "additionalProperties": False,
            },
            "scopes": ["fs:read"],
        },
    ],
    "mcpServers": {
        "filesystem": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/project"],
            "publisher": "Model Context Protocol (verified)",
            "sha256": "9f1c2b5e2d0a4a2e9d0b7c6f1a3e5d8c0b9a7e6f4d2c1b0a9e8d7c6b5a4f3e2d",
        }
    },
}

FIXTURES["ho_clean_03_github_read.json"] = {
    "name": "heldout-clean-github",
    "tools": [
        {
            "name": "get_pull_request",
            "description": "Fetches metadata, diff stats, and review status for a pull request by owner, repo, and number.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "owner": {"type": "string"},
                    "repo": {"type": "string"},
                    "pull_number": {"type": "integer"},
                },
                "additionalProperties": False,
            },
            "scopes": ["repo:read"],
        },
        {
            "name": "list_issues",
            "description": "Lists open issues for a repository, optionally filtered by label.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "owner": {"type": "string"},
                    "repo": {"type": "string"},
                    "label": {"type": "string"},
                },
                "additionalProperties": False,
            },
            "scopes": ["repo:read"],
        },
    ],
    "mcpServers": {
        "github": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-github"],
            "publisher": "Model Context Protocol (verified)",
            "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PAT}"},
            "sha256": "1b2c3d4e5f60718293a4b5c6d7e8f9019283746556473829102938475869301",
        }
    },
}

FIXTURES["ho_clean_04_slack_read.json"] = {
    "name": "heldout-clean-slack",
    "tools": [
        {
            "name": "list_channel_messages",
            "description": "Returns the most recent messages in a Slack channel the bot has been invited to.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "channel_id": {"type": "string"},
                    "limit": {"type": "integer", "default": 20},
                },
                "additionalProperties": False,
            },
            "scopes": ["channels:history"],
        }
    ],
    "mcpServers": {
        "slack": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-slack"],
            "publisher": "Model Context Protocol (verified)",
            "env": {"SLACK_BOT_TOKEN": "${SLACK_BOT_TOKEN}"},
        }
    },
}

FIXTURES["ho_clean_05_postgres_readonly.json"] = {
    "name": "heldout-clean-postgres",
    "tools": [
        {
            "name": "run_readonly_query",
            "description": "Executes a read-only SQL SELECT statement against the configured Postgres database and returns rows. The server enforces a read-only transaction, rejecting any non-SELECT statement before execution.",
            "inputSchema": {
                "type": "object",
                "properties": {"sql": {"type": "string"}},
                "additionalProperties": False,
            },
            "scopes": ["db:read"],
        }
    ],
    "mcpServers": {
        "postgres": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://localhost/analytics"],
            "publisher": "Model Context Protocol (verified)",
        }
    },
}

FIXTURES["ho_clean_06_playwright_browser.json"] = {
    "name": "heldout-clean-playwright",
    "tools": [
        {
            "name": "navigate",
            "description": "Navigates the sandboxed headless browser to a given URL and returns the page title.",
            "inputSchema": {
                "type": "object",
                "properties": {"url": {"type": "string"}},
                "additionalProperties": False,
            },
        },
        {
            "name": "screenshot",
            "description": "Takes a screenshot of the current page in the sandboxed headless browser.",
            "inputSchema": {
                "type": "object",
                "properties": {"full_page": {"type": "boolean", "default": False}},
                "additionalProperties": False,
            },
        },
    ],
    "mcpServers": {
        "playwright": {
            "command": "npx",
            "args": ["-y", "@playwright/mcp@latest"],
            "publisher": "Microsoft (verified)",
        }
    },
}

FIXTURES["ho_clean_07_fetch_web.json"] = {
    "name": "heldout-clean-fetch",
    "tools": [
        {
            "name": "fetch_url",
            "description": "Fetches a public URL over HTTPS and returns the page content converted to markdown, truncated to 5000 characters. Used to let the model read a web page the user links to.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "url": {"type": "string"},
                    "max_length": {"type": "integer", "default": 5000},
                },
                "additionalProperties": False,
            },
        }
    ],
    "mcpServers": {
        "fetch": {
            "command": "uvx",
            "args": ["mcp-server-fetch"],
            "publisher": "Model Context Protocol (verified)",
        }
    },
}

FIXTURES["ho_clean_08_memory_knowledge_graph.json"] = {
    "name": "heldout-clean-memory",
    "tools": [
        {
            "name": "create_entities",
            "description": "Adds new entities with names, types, and observations to the local persistent knowledge graph file.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "entities": {"type": "array", "items": {"type": "object"}}
                },
                "additionalProperties": False,
            },
            "scopes": ["fs:read", "fs:write"],
        },
        {
            "name": "search_nodes",
            "description": "Searches the local knowledge graph file for entities matching a query string.",
            "inputSchema": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "additionalProperties": False,
            },
        },
    ],
    "mcpServers": {
        "memory": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-memory"],
            "publisher": "Model Context Protocol (verified)",
        }
    },
}

FIXTURES["ho_clean_09_sqlite_local.json"] = {
    "name": "heldout-clean-sqlite",
    "tools": [
        {
            "name": "query_database",
            "description": "Runs a SQL query against a local SQLite database file and returns the result rows.",
            "inputSchema": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "additionalProperties": False,
            },
        },
        {
            "name": "list_tables",
            "description": "Lists table names in the local SQLite database file.",
            "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
        },
    ],
    "mcpServers": {
        "sqlite": {
            "command": "uvx",
            "args": ["mcp-server-sqlite", "--db-path", "./local.db"],
            "publisher": "Model Context Protocol (verified)",
        }
    },
}

FIXTURES["ho_clean_10_docker_readonly.json"] = {
    "name": "heldout-clean-docker",
    "tools": [
        {
            "name": "list_containers",
            "description": "Lists running Docker containers on the local daemon with their names, images, and status.",
            "inputSchema": {"type": "object", "properties": {"all": {"type": "boolean", "default": False}}, "additionalProperties": False},
        },
        {
            "name": "get_container_logs",
            "description": "Returns the last N lines of logs for a given container ID.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "container_id": {"type": "string"},
                    "tail": {"type": "integer", "default": 100},
                },
                "additionalProperties": False,
            },
        },
    ],
    "mcpServers": {
        "docker": {
            "command": "npx",
            "args": ["-y", "docker-mcp"],
            "publisher": "unverified community server",
        }
    },
}

FIXTURES["ho_clean_11_aws_cost_explorer.json"] = {
    "name": "heldout-clean-aws-cost",
    "tools": [
        {
            "name": "get_cost_and_usage",
            "description": "Returns AWS billing cost and usage totals for a given date range and service, via the read-only Cost Explorer API.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "start_date": {"type": "string"},
                    "end_date": {"type": "string"},
                    "service": {"type": "string"},
                },
                "additionalProperties": False,
            },
            "scopes": ["ce:GetCostAndUsage"],
        }
    ],
    "mcpServers": {
        "aws-cost-explorer": {
            "command": "uvx",
            "args": ["aws-cost-explorer-mcp"],
            "publisher": "AWS Labs (verified)",
            "env": {"AWS_PROFILE": "readonly-billing"},
        }
    },
}

FIXTURES["ho_clean_12_sentry_issues.json"] = {
    "name": "heldout-clean-sentry",
    "tools": [
        {
            "name": "get_issue_details",
            "description": "Fetches the stack trace, event count, and status for a single Sentry issue by ID.",
            "inputSchema": {
                "type": "object",
                "properties": {"issue_id": {"type": "string"}},
                "additionalProperties": False,
            },
        }
    ],
    "mcpServers": {
        "sentry": {
            "command": "npx",
            "args": ["-y", "@sentry/mcp-server"],
            "publisher": "Sentry (verified)",
            "env": {"SENTRY_AUTH_TOKEN": "${SENTRY_AUTH_TOKEN}"},
        }
    },
}

FIXTURES["ho_clean_13_notion_pages.json"] = {
    "name": "heldout-clean-notion",
    "tools": [
        {
            "name": "get_page",
            "description": "Retrieves the content blocks of a Notion page the integration has been shared with.",
            "inputSchema": {
                "type": "object",
                "properties": {"page_id": {"type": "string"}},
                "additionalProperties": False,
            },
        },
        {
            "name": "append_block",
            "description": "Appends a new text block to the end of a Notion page the integration has been shared with.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "page_id": {"type": "string"},
                    "text": {"type": "string"},
                },
                "additionalProperties": False,
            },
        },
    ],
    "mcpServers": {
        "notion": {
            "command": "npx",
            "args": ["-y", "@notionhq/notion-mcp-server"],
            "publisher": "Notion (verified)",
            "env": {"NOTION_TOKEN": "${NOTION_TOKEN}"},
        }
    },
}

FIXTURES["ho_clean_14_gdrive_readonly.json"] = {
    "name": "heldout-clean-gdrive",
    "tools": [
        {
            "name": "search_files",
            "description": "Searches the user's Google Drive by filename and returns matching file IDs and metadata (read-only scope).",
            "inputSchema": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "additionalProperties": False,
            },
            "scopes": ["drive.readonly"],
        }
    ],
    "mcpServers": {
        "gdrive": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-gdrive"],
            "publisher": "Model Context Protocol (verified)",
        }
    },
}

FIXTURES["ho_clean_15_brave_search.json"] = {
    "name": "heldout-clean-search",
    "tools": [
        {
            "name": "web_search",
            "description": "Runs a public web search query and returns the top results with title, URL, and snippet.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "count": {"type": "integer", "default": 10},
                },
                "additionalProperties": False,
            },
        }
    ],
    "mcpServers": {
        "brave-search": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-brave-search"],
            "publisher": "Model Context Protocol (verified)",
            "env": {"BRAVE_API_KEY": "${BRAVE_API_KEY}"},
        }
    },
}

FIXTURES["ho_clean_16_time_zone.json"] = {
    "name": "heldout-clean-time",
    "tools": [
        {
            "name": "get_current_time",
            "description": "Returns the current time in a given IANA timezone.",
            "inputSchema": {
                "type": "object",
                "properties": {"timezone": {"type": "string"}},
                "additionalProperties": False,
            },
        },
        {
            "name": "convert_time",
            "description": "Converts a time from one IANA timezone to another.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "time": {"type": "string"},
                    "from_timezone": {"type": "string"},
                    "to_timezone": {"type": "string"},
                },
                "additionalProperties": False,
            },
        },
    ],
    "mcpServers": {
        "time": {
            "command": "uvx",
            "args": ["mcp-server-time"],
            "publisher": "Model Context Protocol (verified)",
        }
    },
}

FIXTURES["ho_clean_17_google_maps.json"] = {
    "name": "heldout-clean-maps",
    "tools": [
        {
            "name": "geocode_address",
            "description": "Converts a street address into latitude/longitude coordinates using the Google Maps Geocoding API.",
            "inputSchema": {
                "type": "object",
                "properties": {"address": {"type": "string"}},
                "additionalProperties": False,
            },
        }
    ],
    "mcpServers": {
        "google-maps": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-google-maps"],
            "publisher": "Model Context Protocol (verified)",
            "env": {"GOOGLE_MAPS_API_KEY": "${GOOGLE_MAPS_API_KEY}"},
        }
    },
}

FIXTURES["ho_clean_18_stripe_readonly.json"] = {
    "name": "heldout-clean-stripe",
    "tools": [
        {
            "name": "list_recent_charges",
            "description": "Lists the 20 most recent successful charges using a Stripe restricted API key scoped to read-only Charges access.",
            "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
            "scopes": ["charges:read"],
        }
    ],
    "mcpServers": {
        "stripe": {
            "command": "npx",
            "args": ["-y", "@stripe/mcp-server"],
            "publisher": "Stripe (verified)",
            "env": {"STRIPE_RESTRICTED_KEY": "${STRIPE_RESTRICTED_KEY}"},
        }
    },
}

FIXTURES["ho_clean_19_kubectl_readonly.json"] = {
    "name": "heldout-clean-k8s",
    "tools": [
        {
            "name": "get_pod_status",
            "description": "Runs 'kubectl get pods -n <namespace>' against the configured read-only kubeconfig context and returns pod status.",
            "inputSchema": {
                "type": "object",
                "properties": {"namespace": {"type": "string"}},
                "additionalProperties": False,
            },
            "annotations": {
                "implementation": "subprocess.run(['kubectl', 'get', 'pods', '-n', namespace], check=True)"
            },
        }
    ],
    "mcpServers": {
        "k8s-readonly": {
            "command": "uvx",
            "args": ["kubectl-mcp-server", "--context", "prod-readonly"],
            "publisher": "community (unverified)",
        }
    },
}

FIXTURES["ho_clean_20_pdf_text_extract.json"] = {
    "name": "heldout-clean-pdf",
    "tools": [
        {
            "name": "extract_pdf_text",
            "description": "Extracts plain text from a locally uploaded PDF file for summarization. Runs fully offline with no network access.",
            "inputSchema": {
                "type": "object",
                "properties": {"file_path": {"type": "string"}},
                "additionalProperties": False,
            },
            "scopes": ["fs:read"],
        }
    ],
}

for filename, data in FIXTURES.items():
    with open(CLEAN / filename, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

print(f"Wrote {len(FIXTURES)} clean fixtures to {CLEAN}")
