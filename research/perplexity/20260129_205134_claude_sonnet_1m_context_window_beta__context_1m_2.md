# Research: Claude Sonnet 1M context window beta "context-1m-2025" server-side flag feature

> **Date:** 2026-01-29 20:51:34
> **Source:** perplexity-mcp
> **Model:** sonar-pro
> **Checksum:** `sha256:39413b47695dfde33177375947d29033a73c3df80f330bb8d9b27c64388cdfce`
> **Raw JSON:** `raw/20260129_205134_claude_sonnet_1m_context_window_beta__context_1m_2.json`

---

## Query

Claude Sonnet 1M context window beta "context-1m-2025" server-side flag feature

---

## Response

**Claude Sonnet models (such as Sonnet 4 and 4.5) support a 1M token context window through a public beta feature activated via the server-side API header `betas=["context-1m-2025-08-07"]` or equivalent flags like `context-1m-2025-08-07`.** This is not enabled by default and requires Tier 4 or custom rate limits on Anthropic's platform, with availability also on Amazon Bedrock (in preview).[1][2][3][4]

### Activation Details
- **API Header**: Include `betas=["context-1m-2025-08-07"]` in requests to enable the 1M context on supported models like Claude Sonnet 4 or 4.5. This expands from the standard 200K token limit.[2][3]
- **CLI/Tools Flags**: In tools like Claude Code, use `/model sonnet[1m]` (maps to models like `claude-sonnet-4-20250514[1m]` or `claude-sonnet-4-5-20250929[1m]`), but it fails with a 400 error ("The long context beta is not yet available for this subscription.") for ineligible accounts (e.g., Max 20x subscriptions).[2]
- **Platforms**:
  | Platform          | Status                  | Notes |
  |-------------------|-------------------------|-------|
  | Anthropic API    | Public beta (Tier 4+)  | Header required; prompt caching available for cost reduction.[1][3] |
  | Amazon Bedrock   | Preview                | Up to 1M tokens for Sonnet 4/4.5; supports large code/docs.[4][6] |
  | Claude Code/CLI  | Partial (feature request) | [1m] flag supported for some Tier 4 users; duplicates exist.[2] |
  | Cline/Cursor     | Opt-in or manual       | Higher costs >200K tokens; auto-invocation issues reported.[1][7] |

### Requirements and Limitations
- **Access**: Limited to Tier 4/custom limits or select users (e.g., Claude Max 20x may not qualify). Check `/model` in CLI for "Sonnet (1M Context)" option.[2]
- **Costs**: Standard up to 200K ($3/$15 per MTok input/output); doubles >200K ($6/$22.50 per MTok).[1]
- **Models Affected**: Primarily Sonnet 4/4.5; Sonnet 4.5 reports 200K by default without flag.[2][5]
- **Use Cases**: Enables loading full docs, extended dev cycles, and deep planning without truncation.[1][3][4]

Availability began around August 2025; some tools lag in full support.[1][2]

---

## Citations

1. https://cline.bot/blog/two-ways-to-advantage-of-claude-sonnet-4s-1m-context-window-in-cline
2. https://github.com/anthropics/claude-code/issues/8381
3. https://www.datastudios.org/post/claude-token-limits-and-context-windows
4. https://aws.amazon.com/bedrock/anthropic/
5. https://www.anthropic.com/news/claude-sonnet-4-5
6. https://builder.aws.com/content/2tjU84jCZYTkUxJoqFqY8bvaGd8/claude-sonnet-4s-1m-context-window-on-amazon-bedrock
7. https://forum.cursor.com/t/cursor-automatically-invokes-claude-4-5-long-context-mode-context-1m-2025-08-07-increasing-costs-and-hitting-bedrock-rate-limits/139092

---

## Usage Stats

- Prompt tokens: 23
- Completion tokens: 610
- Total tokens: 633
