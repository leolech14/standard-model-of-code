# Research: Anthropic API Tier 4 requirements how to upgrade from tier 2 3 deposit spend

> **Date:** 2026-01-29 16:12:52
> **Source:** perplexity-mcp
> **Model:** sonar-pro
> **Checksum:** `sha256:e13e5b044bc2a0eebb5549322d06e608f8a86c8dc453297058fd9cd6a871fc08`
> **Raw JSON:** `raw/20260129_161252_anthropic_api_tier_4_requirements_how_to_upgrade_f.json`

---

## Query

Anthropic API Tier 4 requirements how to upgrade from tier 2 3 deposit spend

---

## Response

**Anthropic API Tier 4 requires a cumulative $400 deposit (prepaid credit purchase, excluding tax), unlocking maximum self-service rate limits like 4,000 RPM, up to 2,000,000 ITPM (4,000,000 for Haiku), 400,000-800,000 OTPM, and a $5,000 monthly spend limit, plus beta access to the 1M token context window for certain models.[1][8]**

**Upgrading from Tier 2 or 3 involves purchasing additional prepaid credits to reach the $400 cumulative total, with a 14-day wait period after the deposit for Tier 4 activation.[1][4][8]**
- Tier 2 typically requires around a $5-$100 cumulative deposit (exact varies), with lower limits like reduced RPM/ITPM and ~$100-$500 monthly spend.[1]
- Tier 3 requires a $200 deposit (7-day wait), offering ~2,000 RPM, 800,000+ ITPM, and $1,000 monthly spend; upgrade when hitting these limits or needing Tier 4 features.[1][4]
- Process: Log into the Claude Console (platform.claude.com), add prepaid credits via "Credit Purchase" to hit $400 cumulative; tiers advance automatically upon qualification, but monitor for wait times and approval.[1][4][8]
- Tip: Use shorter `max_tokens` (e.g., 500 vs. 4096) to optimize rate limiting via Anthropic's token bucket algorithm.[1]

For limits beyond Tier 4 or custom enterprise plans (e.g., higher capacity), contact Anthropic sales through the Console.[1][4] Sources note slight variations in deposit/wait details, with [1] and [8] (official docs) being most authoritative.[1][4][8]

---

## Citations

1. https://www.aifreeapi.com/en/posts/claude-api-quota-tiers-limits
2. https://community.clay.com/x/support/wxh39xgxdmsg/understanding-anthropic-api-tier-requirements-for
3. https://platform.claude.com/docs/en/api/service-tiers
4. https://obot.ai/resources/learning-center/claude-api/
5. https://www.metacto.com/blogs/anthropic-api-pricing-a-full-breakdown-of-costs-and-integration
6. https://www.nops.io/blog/anthropic-api-pricing/
7. https://www.finout.io/blog/anthropic-api-pricing
8. https://platform.claude.com/docs/en/api/rate-limits
9. https://www.anthropic.com/news/claude-4

---

## Usage Stats

- Prompt tokens: 18
- Completion tokens: 379
- Total tokens: 397
