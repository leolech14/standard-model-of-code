# Research: "Claude Code" "Max subscription" 1M context "not available" OR "not yet available" subscription vs A...

> **Date:** 2026-01-29 23:05:58
> **Source:** perplexity-mcp
> **Model:** sonar-pro
> **Checksum:** `sha256:88c17fb3a4099693c4d2e71cc10bac056bfa216e12e3b18b2eff213019f06a78`
> **Raw JSON:** `raw/20260129_230558_claude_code___max_subscription__1m_context__not_a.json`

---

## Query

"Claude Code" "Max subscription" 1M context "not available" OR "not yet available" subscription vs API tier mismatch

---

## Response

**The 1M token context window for Claude Sonnet models (e.g., sonnet[1m] or claude-sonnet-4-20250514[1m]) is not available to Claude Code users on Max subscriptions, including 20x tiers, despite being accessible via the API for qualifying tiers.**[1][4]

Users attempting `/model sonnet[1m]` in Claude Code with Max subscriptions encounter API Error 400: "The long context beta is not yet available for this subscription."[1] This limitation persists as of mid-October 2025 for Max 20x users, who previously had access but now face restrictions, prompting bug reports and feature requests.[1][4]

Anthropic limits public beta access to the Claude Developer Platform for customers with **Tier 4 and custom rate limits**, plus some Max 20x users—excluding most subscription-based Claude Code access.[1] Max plans provide higher usage limits, early feature access, and Claude Code CLI support, but do not guarantee all API capabilities like 1M context, creating a **subscription vs. API tier mismatch**.[3][1]

To use 1M context:
- Switch to an **API key** from the Console (pay-as-you-go), where it's available (e.g., set limits like $50 and select sonnet[1m]). Costs rise for inputs >200K tokens ($6/MTok input, $22.50/MTok output for Sonnet).[2][3][1]
- Workflow suggestion: Use Max for daily coding (/login with subscription), then /logout, /login with API key for 1M tasks, and switch back.[1]

This gap frustrates Max users ($200/month), some considering cancellation or alternatives like Gemini CLI, as it forces toolchain splits for large codebases.[1] No resolution noted in results up to late 2025.[1][4]

---

## Citations

1. https://github.com/anthropics/claude-code/issues/5644
2. https://www.youtube.com/watch?v=Kxnlh2rVYVE
3. https://intuitionlabs.ai/articles/claude-pricing-plans-api-costs
4. https://github.com/anthropics/claude-code/issues/15057
5. https://www.anthropic.com/news/claude-sonnet-4-5

---

## Usage Stats

- Prompt tokens: 28
- Completion tokens: 395
- Total tokens: 423
