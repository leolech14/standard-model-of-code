# Research: Cerebras API rate limit increase higher tier subscription enterprise 2025 2026

> **Date:** 2026-01-31 08:27:34
> **Source:** perplexity-mcp
> **Model:** sonar-pro
> **Checksum:** `sha256:6488360eab0fed7e17dfbc5707be655bd764c87e313c38479211b36d464633fc`
> **Raw JSON:** `raw/20260131_082734_cerebras_api_rate_limit_increase_higher_tier_subsc.json`

---

## Query

Cerebras API rate limit increase higher tier subscription enterprise 2025 2026

---

## Response

**Cerebras offers higher API rate limits through its paid Developer, Cerebras Code (Pro/Max), and Enterprise tiers, with Enterprise providing the highest limits for production workloads.** Specific limits vary by tier and model; for example, the free tier has base limits like 60K TPM (tokens per minute), 1M TPH/TPD (tokens per hour/day), and 30 RPM (requests per minute) for models such as `llama3.1-8b` or `gpt-oss-120b`, while higher tiers scale these up significantly.[1]

### Tiered Rate Limits and Subscriptions
- **Free Tier**: Baseline access with limits like 60K TPM, 1M TPH/TPD, 30 RPM, 900 RPH (requests per hour), and 14.4K RPD (requests per day) for most models (e.g., `llama3.1-8b`, `qwen-3-32b`). Some models like `zai-glm-4.7` have lower RPM (10).[1]
- **Developer Tier**: 10x higher rate limits than free (e.g., up to 1.5M TPM), self-serve pay-per-token starting at $10, with higher priority processing.[2][3]
- **Cerebras Code Plans** (for coding workflows):
  | Plan | Monthly Cost | Daily Token Limit | Other Notes |
  |------|--------------|-------------------|-------------|
  | Pro  | $50         | 24M tokens       | Up to 300K tokens/minute; suited for indie devs.[3][5] |
  | Max  | $200        | 120M tokens      | Up to 400K tokens/minute; for heavy workflows like IDE integrations.[2][3][5] |
- **Enterprise Tier**: Highest rate limits, dedicated queue priority for lowest latency, custom model weights, fine-tuning, and dedicated support. Exact numerical limits are not publicly detailed and require contacting sales or checking your account's Limits section.[1][3][7]

Rate limits use a token bucketing algorithm for continuous replenishment, with real-time headers like `x-ratelimit-remaining-tokens-minute` in API responses for monitoring.[1] Exceeding limits returns a 429 error.[1]

### Increasing Limits
Contact Cerebras via their website, your account representative, or sales for higher limits, custom pricing, or Enterprise upgrades—especially relevant for production needs in 2025-2026.[1][7] Public docs note that precise limits are account-specific and may evolve.[1] No search results specify 2025-2026 changes, but Enterprise is positioned for scalable, high-throughput use.[3]

---

## Citations

1. https://inference-docs.cerebras.ai/support/rate-limits
2. https://www.cerebras.ai/blog/cerebras-inference-now-available-via-pay-per-token
3. https://www.cerebras.ai/pricing
4. https://news.ycombinator.com/item?id=44762959
5. https://www.infoworld.com/article/4055909/down-and-out-with-cerebras-code.html
6. https://community.openai.com/t/faster-api-throughput-using-cerebras/1357998
7. https://inference-docs.cerebras.ai/models/openai-oss
8. https://marketplace.visualstudio.com/items?itemName=cerebras.cerebras-chat
9. https://github.com/cheahjs/free-llm-api-resources

---

## Usage Stats

- Prompt tokens: 17
- Completion tokens: 576
- Total tokens: 593
