# Research: I need technical verification for using Claude Code CLI with alternative inference providers:

1. Do...

> **Date:** 2026-01-30 20:45:16
> **Source:** perplexity-mcp
> **Model:** sonar-pro
> **Checksum:** `sha256:73f1b99476396f63b53b9fcbab26dc5121b1576bad1aaae79a67b9260ce6170d`
> **Raw JSON:** `raw/20260130_204516_i_need_technical_verification_for_using_claude_cod.json`

---

## Query

I need technical verification for using Claude Code CLI with alternative inference providers:

1. Does Claude Code CLI (Anthropic's official CLI tool) support ANTHROPIC_BASE_URL environment variable to point at custom endpoints? How does authentication work - API key or session-based?

2. Does OpenRouter support Anthropic Messages API format (/v1/messages with anthropic-style requests), or only OpenAI format? Can Claude Code connect to OpenRouter directly?

3. Does Cerebras Inference API support Anthropic Messages API format, or only OpenAI-compatible format?

4. What's the actual compatibility matrix for using Claude Code with non-Anthropic providers?

Please provide specific technical details and any official documentation references.

---

## Response

**Claude Code CLI supports the `ANTHROPIC_BASE_URL` environment variable for custom endpoints, using `ANTHROPIC_AUTH_TOKEN` or `ANTHROPIC_API_KEY` (set to empty for token priority) for authentication, with additional options like `apiKeyHelper` and `ANTHROPIC_CUSTOM_HEADERS` in `~/.claude/settings.json`.** [1][3][4][5]

**OpenRouter supports the Anthropic Messages API format (/v1/messages) directly via `ANTHROPIC_BASE_URL=https://openrouter.ai/api` and `ANTHROPIC_AUTH_TOKEN`, allowing Claude Code to connect natively.** [4]

**Cerebras Inference API compatibility with Anthropic format is not detailed in available sources; it likely requires OpenAI-compatible endpoints or proxies like LiteLLM for integration.**

**No official compatibility matrix exists, but practical support includes LiteLLM (unified `/anthropic` endpoint), OpenRouter, Vercel AI Gateway, Docker Model Runner, and custom gateways via `ANTHROPIC_BASE_URL`.** [1][3][4][5][6][7]

### 1. Claude Code CLI and `ANTHROPIC_BASE_URL` / Authentication
Claude Code CLI reads `ANTHROPIC_BASE_URL` from environment variables or `~/.claude/settings.json` to route requests to custom endpoints (e.g., `https://llm-gateway.my-company.dev`). [1][3]

Authentication prioritizes:
- `ANTHROPIC_API_KEY` (must be empty string `""` for token use). [4][5]
- `ANTHROPIC_AUTH_TOKEN` (Bearer token format). [2][4][5]
- `apiKeyHelper` command for dynamic tokens (e.g., `bash -c 'echo $(gcloud auth print-identity-token ...)'`), with `CLAUDE_CODE_API_KEY_HELPER_TTL_MS` for refresh (default 1 hour). [1]
- `ANTHROPIC_CUSTOM_HEADERS` for headers like `X-Litellm-Key: Bearer ...`. [1][5]

Example config in `~/.claude/settings.json`:
```
{
  "apiKeyHelper": "bash -c 'echo $(gcloud auth print-identity-token ...)'",
  "env": {
    "ANTHROPIC_BASE_URL": "https://llm-gateway.my-company.dev",
    "CLAUDE_CODE_API_KEY_HELPER_TTL_MS": "3600000",
    "ANTHROPIC_CUSTOM_HEADERS": "X-Litellm-Key: Bearer ..."
  }
}
``` [1]

CLI startup flow: Loads settings, executes helper if needed, sends Anthropic-format requests (`/v1/messages`) to the base URL. [1][3]

Official docs: [Claude Code LLM gateway configuration](https://code.claude.com/docs/en/llm-gateway). [3]

### 2. OpenRouter Support
OpenRouter exposes **Anthropic-native protocol** at `https://openrouter.ai/api` (handles `/v1/messages` with `anthropic` style: `model`, `max_tokens`, `messages` array). [4]

Direct Claude Code connection:
```
export ANTHROPIC_BASE_URL="https://openrouter.ai/api"
export ANTHROPIC_AUTH_TOKEN="$OPENROUTER_API_KEY"
export ANTHROPIC_API_KEY=""  # Required empty
```
Then `claude --model claude-3.5-sonnet@20240620`. [4]

GitHub Action example:
```yaml
- name: Run Claude Code
  uses: anthropics/claude-code-action@v1
  with:
    anthropic_api_key: ${{ secrets.OPENROUTER_API_KEY }}
  env:
    ANTHROPIC_BASE_URL: https://openrouter.ai/api
``` [4]

Official docs: [OpenRouter Claude Code integration](https://openrouter.ai/docs/guides/guides/claude-code-integration). [4]

### 3. Cerebras Inference API
Search results lack specifics on Cerebras. It typically offers **OpenAI-compatible** `/v1/chat/completions` endpoints, not native Anthropic `/v1/messages`. [No direct refs]

Use proxies:
- LiteLLM: `ANTHROPIC_BASE_URL="http://litellm:4000"` (unified) or `/anthropic` pass-through. [3][6]

### 4. Compatibility Matrix

| Provider/Proxy       | Endpoint Type              | Base URL Example                  | Auth Method                  | Native Anthropic? | Docs/Source |
|----------------------|----------------------------|-----------------------------------|------------------------------|-------------------|-------------|
| **LiteLLM (Rec.)**  | Unified `/` or `/anthropic`| `http://0.0.0.0:4000`            | `ANTHROPIC_AUTH_TOKEN`      | Yes              | [3][6]     |
| **OpenRouter**      | Anthropic-native          | `https://openrouter.ai/api`      | `ANTHROPIC_AUTH_TOKEN`      | Yes              | [4]        |
| **Vercel AI Gateway**| Anthropic-compatible      | `https://ai-gateway.vercel.sh`   | `ANTHROPIC_AUTH_TOKEN` or headers | Yes         | [5]        |
| **Docker Model Runner** | Anthropic-compatible   | `http://localhost:12434`         | Standard token              | Yes              | [7]        |
| **Custom Gateways** | Via `settings.json`       | e.g., `https://llm-gateway.dev`  | `apiKeyHelper`/headers      | Config-dependent | [1]        |
| **Bedrock (via LiteLLM)** | Pass-through        | `https://litellm:4000/bedrock`   | `CLAUDE_CODE_USE_BEDROCK=1` | Partial          | [3]        |
| **Cerebras**        | Likely OpenAI-only        | N/A (use LiteLLM proxy)          | Proxy-required              | No               | N/A        |

**Key technical notes:**
- All rely on Anthropic Messages API format for drop-in replacement. [1][3][4]
- Model names may need customization (e.g., `claude-sonnet-4-5-20250929` via `CLAUDE_CODE_MODEL_ALIASES`). [3][6]
- VS Code extension lags CLI support (issue open as of Oct 2025). [1]

For Cerebras or unlisted providers, test via LiteLLM proxy first. [3][6]

---

## Citations

1. https://github.com/anthropics/claude-code/issues/8727
2. https://github.com/zed-industries/zed/discussions/37842
3. https://code.claude.com/docs/en/llm-gateway
4. https://openrouter.ai/docs/guides/guides/claude-code-integration
5. https://vercel.com/docs/ai-gateway/coding-agents/claude-code
6. https://docs.litellm.ai/docs/tutorials/claude_responses_api
7. https://www.docker.com/blog/run-claude-code-locally-docker-model-runner/
8. https://news.ycombinator.com/item?id=46726391

---

## Usage Stats

- Prompt tokens: 143
- Completion tokens: 1406
- Total tokens: 1549
