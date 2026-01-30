# Research: Claude Sonnet 1M context how to enable request beta flag opt-in 2026

> **Date:** 2026-01-29 16:10:23
> **Source:** perplexity-mcp
> **Model:** sonar-pro
> **Checksum:** `sha256:208b59808fafe1e1c24945de53ba5be68151e8ed64dd1f4ba6921eb8871ffd96`
> **Raw JSON:** `raw/20260129_161023_claude_sonnet_1m_context_how_to_enable_request_bet.json`

---

## Query

Claude Sonnet 1M context how to enable request beta flag opt-in 2026

---

## Response

**Claude Sonnet 4's 1M token context window is enabled via the beta header `"anthropic_beta": ["context-1m-2025-08-07"]` in API requests to Anthropic, Amazon Bedrock, or compatible clients like Cursor.[2][3][4]**

No separate "request beta flag opt-in" process exists beyond including this header; it's available in public beta/preview for higher-tier Anthropic API users or Bedrock regions like US West (Oregon).[1][2][3] Usage automatically applies higher pricing for prompts over 200K tokens (e.g., input doubles to $6/MTok, output to $22.50/MTok) and stricter rate limits, even for smaller prompts in some integrations.[1][3][4]

### How to Enable It
- **Direct Anthropic API or OpenRouter/Cline**: Add the header to your API call. Example in code:
  ```
  {
    "model": "claude-sonnet-4-2025-...",  // Or latest Sonnet 4 variant
    "messages": [...],
    "anthropic_beta": ["context-1m-2025-08-07"]
  }
  ```
  Requires Tier 4 access on Anthropic.[1]
- **Amazon Bedrock**: Available in public preview (US East/Virginia, Ohio, West/Oregon); same header invokes it.[3][4]
- **Cursor IDE**: Automatically enabled for Claude Sonnet 4/4.5 via Bedrock (since ~Oct 2025), adding higher costs/rate limits without user control—users report it as a bug and request opt-out settings.[4]

### Key Considerations
- **Availability**: Public beta since August 2025; no 2026-specific changes noted.[1][2][3]
- **Limitations**: Higher compute costs, potential focus issues on very large contexts, and separate quotas.[2][4]
- **Alternatives**: Stick to 200K default by omitting the header; prompt caching/batching can cut costs.[1]

Search results reference **Claude Sonnet 4** (not earlier versions) and do not cover a distinct "Claude Sonnet 1M context" model.[1][2][3][4]

---

## Citations

1. https://cline.bot/blog/two-ways-to-advantage-of-claude-sonnet-4s-1m-context-window-in-cline
2. https://www.infoq.com/news/2025/08/claude-sonnet-4/
3. https://aws.amazon.com/about-aws/whats-new/2025/08/anthropic-claude-sonnet-bedrock-expanded-context-window/
4. https://forum.cursor.com/t/cursor-automatically-invokes-claude-4-5-long-context-mode-context-1m-2025-08-07-increasing-costs-and-hitting-bedrock-rate-limits/139092
5. https://www.elvex.com/blog/context-length-comparison-ai-models-2026

---

## Usage Stats

- Prompt tokens: 19
- Completion tokens: 477
- Total tokens: 496
