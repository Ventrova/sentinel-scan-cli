# basescope

**The read-only safety layer for onchain AI agents.**

`basescope` is a [Model Context Protocol](https://modelcontextprotocol.io) (MCP) server that gives AI assistants — Claude, Cursor, and any MCP client — **safe, read-only** onchain abilities on **Base** and other EVM chains. Its job is to answer one question before any wallet ever signs anything:

> **"Is this token / contract / approval actually safe?"**

It checks for honeypots, rug-pull authority, hidden taxes, malicious addresses, and risky approvals — and looks up balances, ENS names, Basenames (`*.base.eth`), verified source, gas, and prices along the way.

### Why it's different

- 🔒 **Read-only by design.** There is *no* code path that can sign or send a transaction, and **no private key can ever be configured.** It cannot move your funds because it literally has no way to. It's the inspector, not the wallet — a safe companion to transaction-capable agents.
- 🔑 **No API keys required.** Works out of the box on free, public data sources. (Optional keys can raise rate limits later, but nothing is required.)
- 🔵 **Base-first, multichain-ready.** Tuned for Base, and also supports Ethereum, Optimism, Arbitrum, and Polygon.
- 🧩 **One question, cross-checked.** Token safety is cross-referenced across **two independent sources** (GoPlus + honeypot.is) with provenance, so an agent can see when they disagree.

---

## Quickstart

Add basescope to any MCP client — **Claude Desktop** (`claude_desktop_config.json`), **Cursor** (`.cursor/mcp.json`), or any other. No install step; `npx` fetches it on first run:

```json
{
  "mcpServers": {
    "basescope": { "command": "npx", "args": ["-y", "basescope"] }
  }
}
```

Restart your client and ask something like *"Use basescope to check if token 0x… on Base is safe."*

<details>
<summary><b>Prefer to run from source?</b></summary>

```bash
git clone https://github.com/chasdaddy/basescope.git
cd basescope
npm install
npm run build
```

Then set the server `command` to `node` with args `["/absolute/path/to/basescope/dist/index.js"]`.

</details>

---

## Tools

All tools are read-only. `chain` accepts `base` (default), `ethereum`, `optimism`, `arbitrum`, or `polygon`. Address fields accept a `0x` address, an ENS name, **or** a Basename (`*.base.eth`) — Basenames resolve automatically via the Base L2 Resolver.

| Tool | What it does |
| --- | --- |
| **check_token_safety** | Honeypot / rug assessment: honeypot check, buy/sell tax, mint/blacklist/pausable/self-destruct authority, verified source, holder count → a normalized `riskLevel` (`critical`/`high`/`medium`/`low`). Cross-checks GoPlus + honeypot.is. |
| **check_address_safety** | Reputation check against known-malicious databases (phishing, sanctioned, scam, money-laundering, mixer, …). |
| **get_token_approvals** | Lists a wallet's outstanding ERC-20 approvals and flags risky spenders — the #1 wallet-drain vector — surfacing risky ones first. |
| **get_verified_source** | Whether a contract's source is verified (via Sourcify) + its name, compiler, and function list. |
| **inspect_contract** | Is the address a contract? Bytecode size + transaction count. |
| **get_token_info** | ERC-20 name / symbol / decimals, and optionally a holder's balance. |
| **get_native_balance** | Native coin (ETH / POL / …) balance of an address or ENS name. |
| **resolve_ens_name** / **reverse_ens_lookup** | ENS name → address, and address → primary ENS name (also reports the primary Basename on Base). |
| **resolve_basename** | Basename (`*.base.eth`) → address, via the Base L2 Resolver — Coinbase's ENS-compatible names on Base mainnet. |
| **get_gas** | Current gas price + EIP-1559 fee suggestion. |
| **get_token_price** | Current USD price for a token (via DefiLlama). |
| **list_supported_chains** | The chains this server can read. |

### Example — "is this token safe?"

```jsonc
// check_token_safety({ chain: "base", token: "0x…" })
{
  "riskLevel": "critical",
  "isHoneypot": true,
  "buyTaxPct": 0,
  "sellTaxPct": 99,
  "flags": [
    "cannot sell entire balance",
    "owner can mint more supply",
    "high sell tax (99%)"
  ],
  "sources": ["goplus", "honeypot.is"]
}
```

---

## Configuration (all optional)

Everything works with no configuration. To use your own RPC endpoints (recommended for heavier use — public RPCs are rate-limited), set any of:

```
BASE_RPC_URL, ETHEREUM_RPC_URL, OPTIMISM_RPC_URL, ARBITRUM_RPC_URL, POLYGON_RPC_URL
```

## Data sources

Standing on the shoulders of excellent free/open services: onchain reads via [viem](https://viem.sh) + public RPCs, token & address safety via [GoPlus Security](https://gopluslabs.io) and [honeypot.is](https://honeypot.is), verified source via [Sourcify](https://sourcify.dev), and prices via [DefiLlama](https://defillama.com).

## Limitations

`basescope` reports **heuristics and signals**, not guarantees, and is **not financial advice**. Safety APIs can be wrong or out of date; a "low risk" result is not a promise of safety. Always do your own research before transacting. On Base (an OP-Stack L2), `get_gas` reports L2 fees only — total cost also includes an L1 data fee.

## Roadmap

- Transaction / calldata simulation and decoding ("what will this actually do?")
- Optional Etherscan V2 fallback for source & ABI/proxy resolution
- More chains

## License

MIT © 2026
