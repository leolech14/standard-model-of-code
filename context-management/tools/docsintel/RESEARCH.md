# DocsIntel Research Notes

**Date:** 2026-01-29
**Source:** Perplexity searches during session
**Trigger:** Anthropic Max 20x account 1M context access discrepancy

---

## Original Problem

Two Anthropic Max 20x accounts ($200/month each):
- `leo@lbldomain.com` - HAS Sonnet [1m] access
- `leonardo.lech@gmail.com` - MISSING Sonnet [1m] access

Both accounts verified as Max 20x. Billing active (though leo@ has overdue invoice).

---

## Research Findings

### 1. Anthropic Account Tiers

**Subscription tiers (claude.ai):**
| Tier | Price | Usage |
|------|-------|-------|
| Free | $0 | Limited |
| Pro | $20/mo | Base usage |
| Max 5x | $100/mo | 5x Pro limits |
| Max 20x | $200/mo | 20x Pro limits |
| Team | $25-150/user/mo | Collaboration |
| Enterprise | Custom (~$50K+/yr) | 70+ seats |

**API tiers (console.anthropic.com):**
| Tier | Deposit | RPM | 1M Access? |
|------|---------|-----|------------|
| 1 | $5 | 50 | No |
| 2 | $40 | 1,000 | No |
| 3 | $200 | 2,000 | No |
| 4 | $400 | 4,000 | **Yes** |

**Contradiction found:** Sources claim both:
1. "Max 20x includes all features" (subscription-based)
2. "1M requires Tier 4 API ($400 deposit)" (API-based)

**Conclusion:** The relationship between subscription tier and API tier for 1M access is unclear. May require Anthropic support to clarify.

### 2. Documentation Intelligence MCP Servers

**Pre-indexed (community-maintained):**
- **Context7** (Upstash) - 100+ dev libraries
- **anthropic-docs-mcp** (julianoczkowski) - Anthropic/Claude docs
- **AWS MCP Server** - All AWS services
- **AWS Knowledge MCP** - AWS docs/blogs

**Self-indexed (on-demand):**
- **docs-mcp-server** (arabold) - Index any URL, GitHub, npm, PyPI, local files

**Gap:** No pre-indexed MCP for Google Cloud, Azure, Stripe, Vercel.

### 3. Enterprise Options

Not suitable for individual power users:
- Minimum ~70 seats
- ~$50K/year minimum
- Contact sales required

Better option for individuals: API Tier 4 ($400 deposit) for maximum rate limits and 1M access.

---

## Key URLs

- Anthropic Pricing: https://claude.ai/pricing
- API Console: https://console.anthropic.com
- Platform Docs: https://platform.claude.com/docs
- docs-mcp-server: https://github.com/arabold/docs-mcp-server
- Context7: https://github.com/upstash/context7
- anthropic-docs-mcp: https://github.com/julianoczkowski/anthropic-docs-mcp-ts

---

## Unresolved Questions

1. Does API Tier 4 unlock 1M in the web interface (claude.ai)?
2. Does Claude Code use subscription tier or API tier for 1M?
3. Why do two identical Max 20x subscriptions have different 1M access?
4. Is there a hidden beta flag that controls 1M access?

**Only Anthropic support can answer these definitively.**

---

## Action Items

1. [x] Research documentation intelligence tools
2. [x] Identify best MCP servers for provider docs
3. [x] Create DocsIntel architecture
4. [ ] Install anthropic-docs-mcp
5. [ ] Query Anthropic docs for 1M eligibility
6. [ ] Contact Anthropic support if docs don't answer

---

## Perplexity Searches Performed

1. "Anthropic Claude enterprise account pricing token limits 2025 2026 vs Max subscription"
2. "Claude Max subscription 1 million token context window access limitations January 2026"
3. "Anthropic Claude enterprise account how to apply sign up process business requirements 2026"
4. "Claude Code enterprise Teams subscription developer AI coding January 2026"
5. "Anthropic API developer tier builder program higher rate limits individual not enterprise 2026"
6. "Claude Sonnet 1M context window unlock API spend tier subscription crossover 2026"
7. "Anthropic API Tier 4 requirements how to upgrade from tier 2 3 deposit spend"
8. "MCP server documentation RAG provider docs Anthropic Google Cloud AWS indexed search 2026"
9. "Context7 MCP documentation intelligence tool provider docs"
10. "docs-mcp-server arabold how to add custom documentation sources index website github"
11. "julianoczkowski anthropic-docs-mcp-ts install npm github"
12. "MCP servers provider documentation Google Cloud AWS Azure Stripe 2026"
13. "best MCP documentation intelligence tools comprehensive list 2026"
14. "MCP server custom RAG build your own documentation index embeddings vector database 2026"

All results auto-saved to: `standard-model-of-code/docs/research/perplexity/`

---

## Technical Findings

### Environment Variables (Current Session - leo@lbldomain.com)

```
ANTHROPIC_BETA=context-1m-2025-08-07
```

This beta flag enables 1M context. It's set server-side and synced to the client.

### Claude Settings (~/.claude/settings.json)

```json
{
  "contextWindow": 1000000,
  "env": {
    "ANTHROPIC_BETA": "context-1m-2025-08-07"
  }
}
```

### Hypothesis

The `context-1m-2025-08-07` beta flag is assigned per-account on Anthropic's servers. One account has it, one doesn't. This is NOT tied to subscription tier or API spend - it's a separate feature flag.

**To verify:** Check if leonardo.lech@gmail.com has this env var set when authenticated.
