# DocsIntel: Documentation Intelligence Layer

**Position:** OBSERVER.Ingestor (orthogonal to L-scale)
**Realm:** OBSERVER (serves .agent/)
**Location:** context-management/tools/docsintel/
**Status:** MINIMAL / PROTOTYPE
**Created:** 2026-01-29

**Why not on L-scale?** See [POSITIONING.md](./POSITIONING.md) - The L-scale applies only to Codome (code entities with tree-sitter kinds). DocsIntel operates on external Contextome.

---

## Purpose

DocsIntel is an **umbrella layer** that provides intelligent access to provider documentation through MCP servers. It hides the complexity of multiple documentation sources behind a unified interface.

**Problem it solves:** Getting accurate, up-to-date answers about provider APIs, pricing, features, and account management (e.g., "Why does one Anthropic Max account have 1M access and another doesn't?").

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     DocsIntel (L6/L7)                            │
│                   context-management/tools/docsintel/            │
├─────────────────────────────────────────────────────────────────┤
│  Configuration:  providers.yaml                                 │
│  Interface:      MCP tools exposed to Claude                    │
│  State:          Indexed providers, cached queries              │
└─────────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   PRE-INDEXED   │  │  SELF-INDEXED   │  │   CUSTOM RAG    │
│     (L5/L6)     │  │     (L5/L6)     │  │    (L7 future)  │
├─────────────────┤  ├─────────────────┤  ├─────────────────┤
│ • Context7      │  │ • docs-mcp      │  │ • Your vector   │
│ • anthropic-    │  │   (arabold)     │  │   DB + embedder │
│   docs-mcp      │  │                 │  │ • Cross-provider│
│ • AWS MCP       │  │ Index on-demand:│  │   queries       │
│                 │  │ • GCP           │  │ • Proprietary   │
│ Pre-indexed by  │  │ • Stripe        │  │   sources       │
│ community       │  │ • Vercel        │  │                 │
│                 │  │ • Any URL       │  │                 │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

---

## The Three Layers

### Layer 1: Pre-indexed (External, Community-maintained)

| MCP Server | Providers | Install | Status |
|------------|-----------|---------|--------|
| **Context7** | React, Next.js, MongoDB, Supabase, FastAPI, 100+ | `npx @upstash/context7-mcp` | Available |
| **anthropic-docs-mcp** | Anthropic/Claude API | `npm i -g @julianoczkowski/anthropic-docs-mcp-ts` | Available |
| **AWS MCP Server** | All AWS services | AWS Marketplace | Available |
| **AWS Knowledge MCP** | AWS docs/blogs | Free, public | Available |

**Trade-off:** Fast access, but limited to what others indexed. No control over freshness.

### Layer 2: Self-indexed (On-demand via docs-mcp-server)

Use `docs-mcp-server` (arabold) to index ANY provider's documentation.

**Supported sources:**
- Websites (direct URL)
- GitHub repositories
- npm packages
- PyPI packages
- Local files (`file://`)

**How to index a new provider:**
```
"Please scrape the GCP Compute documentation from https://cloud.google.com/compute/docs
for library 'gcp-compute' version 'latest'"
```

Or use web UI at `http://localhost:6280`

**Trade-off:** Full control, but requires manual indexing. You maintain freshness.

### Layer 3: Custom RAG (Future - L7)

For when you need:
- Cross-provider comparison queries
- Proprietary documentation
- Specialized chunking strategies
- Persistent learned patterns

**Components (when built):**
- Vector DB: Qdrant, Pinecone, or pgvector
- Embeddings: OpenAI, Voyage AI, or local models
- MCP Server: Custom FastMCP implementation

---

## Current Provider Registry

| Provider | Pre-indexed? | Self-indexed? | Priority | Use Case |
|----------|--------------|---------------|----------|----------|
| **Anthropic** | anthropic-docs-mcp | - | HIGH | Account/API questions |
| **AWS** | AWS MCP | - | MEDIUM | Cloud infrastructure |
| **Google Cloud** | - | docs-mcp-server | HIGH | GCP services |
| **Vercel** | - | docs-mcp-server | MEDIUM | Deployment |
| **Supabase** | Context7 | - | MEDIUM | Database/auth |
| **Stripe** | - | docs-mcp-server | LOW | Payments |
| **React/Next.js** | Context7 | - | HIGH | UI development |

---

## Installation

### 1. Verify docs-mcp-server (already installed)

```bash
# Check current MCP config
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json | jq '.mcpServers["docs-mcp-server"]'
```

### 2. Add anthropic-docs-mcp

```bash
# Install globally
npm install -g @julianoczkowski/anthropic-docs-mcp-ts

# Add to Claude Desktop config
# In mcpServers section:
"anthropic-docs": {
  "command": "anthropic-docs-mcp",
  "args": ["--transport", "stdio"]
}
```

### 3. Add Context7

```bash
# Add to Claude Desktop config
# In mcpServers section:
"context7": {
  "command": "npx",
  "args": ["-y", "@upstash/context7-mcp"]
}
```

### 4. Restart Claude Desktop

---

## Usage Patterns

### Pattern 1: Direct Query (Pre-indexed)

For providers with pre-indexed MCPs:
```
"Search Anthropic docs for Max subscription 1M context eligibility"
"use context7 - how does Next.js App Router handle streaming?"
```

### Pattern 2: Index Then Query (Self-indexed)

For providers without pre-indexed MCPs:
```
"Please scrape https://cloud.google.com/iam/docs for library 'gcp-iam'"
[wait for indexing]
"Search docs for GCP IAM service account best practices"
```

### Pattern 3: Cross-Provider (Future)

When custom RAG is built:
```
"Compare authentication approaches across Anthropic, AWS, and GCP"
```

---

## Canonical Providers (Leonardo's Stack)

These are the providers relevant to PROJECT_elements and related work:

| Domain | Providers | Index Priority |
|--------|-----------|----------------|
| **AI/ML** | Anthropic, OpenAI, Google AI, Hugging Face | HIGH |
| **Cloud** | GCP, AWS | HIGH |
| **Database** | Supabase, PostgreSQL | HIGH |
| **Deployment** | Vercel, Cloudflare | MEDIUM |
| **Payments** | Stripe | LOW |
| **Dev Tools** | GitHub, npm, PyPI | MEDIUM |

---

## Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Pre-indexed providers | 4 | 10+ |
| Self-indexed providers | 0 | 5+ |
| Query success rate | Unknown | >80% |
| Average response quality | Unknown | Useful citations |

---

## Files

```
context-management/tools/docsintel/
├── DOCSINTEL.md          # This file (architecture & usage)
├── providers.yaml       # Provider registry and config
├── install.sh           # Installation script
└── RESEARCH.md          # Research notes from Perplexity
```

---

## Relationship to Standard Model

| Aspect | Value |
|--------|-------|
| **Position** | OBSERVER.Ingestor |
| **L-Scale** | N/A (orthogonal - L-scale is Codome-only) |
| **Realm** | OBSERVER (knowledge acquisition for .agent/) |
| **Subsystem** | Ingestor (Miller's taxonomy) |
| **Location** | context-management/tools/ (physical) |

**Why not on L-scale?**

The L-scale (L-3 to L12) applies exclusively to CODOME:
- Requires tree-sitter kinds (function, class, module, etc.)
- Based on containment hierarchy (File contains Class contains Method)
- Assigns levels via `λ: Entity → L` where Entity = code construct

DocsIntel has none of these. It operates on **external Contextome** (provider documentation), making it orthogonal to the code hierarchy.

**Full analysis:** [POSITIONING.md](./POSITIONING.md)

---

## Next Steps

1. [ ] Install anthropic-docs-mcp
2. [ ] Install Context7
3. [ ] Index GCP docs via docs-mcp-server
4. [ ] Test query: "Why does Max 20x account lack 1M access?"
5. [ ] Document findings
6. [ ] Evaluate need for custom RAG (L7)

---

## Origin

Created to solve: "Two Anthropic Max 20x accounts have different 1M context access - why?"

The existing tools (web search, manual docs) couldn't give a definitive answer. DocsIntel provides structured access to provider documentation for reliable answers.
