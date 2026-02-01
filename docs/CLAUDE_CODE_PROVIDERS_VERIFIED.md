# Claude Code Providers - Verified Technical Guide

**Verified:** 2026-01-30
**Source:** Perplexity research + live API testing

---

## The Key Insight

Claude Code CLI expects **Anthropic Messages API** format (`/v1/messages`).

Not all providers support this format. Only these work directly:

```
WORKS DIRECTLY (Anthropic Messages API)
├── Anthropic ✓
├── OpenRouter ✓ (tested)
├── Docker Model Runner ✓
└── Vercel AI Gateway ✓

NEEDS PROXY (OpenAI format only)
├── Cerebras ✗ → needs LiteLLM
├── Groq ✗ → needs LiteLLM
└── Together ✗ → needs LiteLLM
```

---

## 1. Anthropic (Default)

**Status:** Works natively

```bash
# Default - no config needed
claude "your prompt"

# Or explicitly:
unset ANTHROPIC_BASE_URL
export ANTHROPIC_API_KEY="your-key"
claude "your prompt"
```

**Your setup:**
- Account #1: `claude` command (Doppler key)
- Account #2: `claude-1m` alias (1M context beta)

---

## 2. OpenRouter (Verified Working)

**Status:** ✓ Tested and working

**API Test Result:**
```json
{
  "type": "message",
  "role": "assistant",
  "content": [{"type": "text", "text": "Hello there."}],
  "stop_reason": "end_turn"
}
```

**Configuration:**
```bash
export ANTHROPIC_BASE_URL="https://openrouter.ai/api"
export ANTHROPIC_AUTH_TOKEN="$OPENROUTER_API_KEY"
export ANTHROPIC_API_KEY=""  # MUST be empty string!

claude --model qwen/qwen-2.5-coder-32b-instruct "your prompt"
```

**Using the switcher:**
```bash
source scripts/claude-model-switch.sh openrouter
claude --model qwen/qwen-2.5-coder-32b-instruct "your prompt"
```

**Available models (346+):**
- `qwen/qwen-2.5-coder-32b-instruct` - Coding
- `deepseek/deepseek-coder-v2` - Coding
- `anthropic/claude-3.5-sonnet` - Can use Anthropic via OpenRouter too
- `meta-llama/llama-3.3-70b-instruct` - General
- Browse all: https://openrouter.ai/models

---

## 3. Z.ai GLM (Working via Alias)

**Status:** ✓ Working (separate config file)

**Configuration:** Uses `~/.claude/settings-zai.json` which sets:
```json
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "your-zai-token",
    "ANTHROPIC_BASE_URL": "https://api.z.ai/api/anthropic"
  }
}
```

**Usage:**
```bash
zai "your prompt"
# or
claude-zai "your prompt"
```

**Note:** Z.ai speaks Anthropic Messages API, so it works directly.

---

## 4. Cerebras (Needs LiteLLM Proxy)

**Status:** ⚠️ Requires proxy (OpenAI format only)

Cerebras API uses OpenAI's `/v1/chat/completions` format, NOT Anthropic Messages.

**Solution:** LiteLLM translates Anthropic → OpenAI

**Setup:**
```bash
# Terminal 1: Start LiteLLM proxy
./scripts/start-litellm-cerebras.sh

# Terminal 2: Use Claude Code
source scripts/claude-model-switch.sh litellm
claude "your prompt"
```

**Manual proxy start:**
```bash
CEREBRAS_API_KEY=$(doppler secrets get CEREBRAS_API_KEY --plain) \
  litellm --model cerebras/llama-3.3-70b --port 4000
```

**Speed:** 1000-3000 tokens/sec (once proxy is running)

---

## 5. Docker Model Runner (Works Directly)

**Status:** ✓ Supports Anthropic Messages API

**Setup:**
```bash
# Enable Docker Model Runner
docker desktop enable model-runner --tcp

# Use with Claude Code
source scripts/claude-model-switch.sh local
claude --model qwen2.5-coder:32b "your prompt"
```

---

## Provider Comparison (Corrected)

| Provider | API Format | Direct Support | Speed | Setup Complexity |
|----------|-----------|----------------|-------|------------------|
| Anthropic | Anthropic | ✓ Native | Standard | None |
| OpenRouter | Anthropic | ✓ Direct | Varies | Easy (env vars) |
| Z.ai | Anthropic | ✓ Direct | Standard | Already done (alias) |
| Docker MR | Anthropic | ✓ Direct | Hardware | Easy |
| Cerebras | OpenAI | ✗ Proxy | 1000+ t/s | Medium (LiteLLM) |
| Groq | OpenAI | ✗ Proxy | 200-400 t/s | Medium (LiteLLM) |
| Together | OpenAI | ✗ Proxy | 200-400 t/s | Medium (LiteLLM) |

---

## Quick Reference

### What Works Right Now

| Command | Provider | Status |
|---------|----------|--------|
| `claude` | Anthropic (Account #1) | ✓ |
| `claude-1m` | Anthropic (Account #2, 1M ctx) | ✓ |
| `zai` | Z.ai GLM | ✓ |
| `source ...openrouter && claude` | OpenRouter | ✓ |
| `source ...litellm && claude` | Via LiteLLM | ✓ (if proxy running) |

### Using the Model Switcher

```bash
# See options
source scripts/claude-model-switch.sh help

# OpenRouter (direct)
source scripts/claude-model-switch.sh openrouter
claude --model qwen/qwen-2.5-coder-32b-instruct "prompt"

# Back to Anthropic
source scripts/claude-model-switch.sh anthropic
claude "prompt"

# Cerebras via LiteLLM (need proxy running)
./scripts/start-litellm-cerebras.sh  # Terminal 1
source scripts/claude-model-switch.sh litellm  # Terminal 2
claude "prompt"
```

---

## Authentication Details

From official Claude Code docs:

| Variable | Purpose |
|----------|---------|
| `ANTHROPIC_BASE_URL` | Override endpoint URL |
| `ANTHROPIC_API_KEY` | API key (set to `""` when using token) |
| `ANTHROPIC_AUTH_TOKEN` | Bearer token (preferred for gateways) |

**Important:** When using `ANTHROPIC_AUTH_TOKEN`, you MUST set `ANTHROPIC_API_KEY=""` (empty string).

---

## Files

| File | Purpose |
|------|---------|
| `scripts/claude-model-switch.sh` | Switch between providers |
| `scripts/start-litellm-cerebras.sh` | Start Cerebras proxy |
| `~/.claude/settings-zai.json` | Z.ai configuration |

---

## Sources

- [Claude Code LLM Gateway Docs](https://code.claude.com/docs/en/llm-gateway)
- [OpenRouter Claude Code Integration](https://openrouter.ai/docs/guides/guides/claude-code-integration)
- [Docker Model Runner Blog](https://www.docker.com/blog/run-claude-code-locally-docker-model-runner/)
- Perplexity research (saved in `particle/docs/research/perplexity/`)
