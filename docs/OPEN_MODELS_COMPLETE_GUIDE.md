# Open Models + Claude Code: Complete Setup Guide

**Created:** 2026-01-30
**Purpose:** Run Claude Code CLI with open-source models via multiple inference providers

---

## Table of Contents

1. [Setup Checklist](#setup-checklist)
2. [Architecture Overview](#architecture-overview)
3. [Current State](#current-state)
4. [Immediate Fixes Required](#immediate-fixes-required)
5. [Provider Setup](#provider-setup)
6. [Model Switching](#model-switching)
7. [MCP Configuration](#mcp-configuration)
8. [Model Reference](#model-reference)
9. [Quick Reference](#quick-reference)

---

## Setup Checklist

### Core Infrastructure
- [x] Claude Code CLI installed
- [x] Doppler configured (project: ai-tools, config: dev)
- [x] Global MCP config (`~/.claude/mcp.json`)
- [x] Model switcher script (`scripts/claude-model-switch.sh`)

### Provider Keys (Doppler)
- [x] `ANTHROPIC_API_KEY` - Default Claude
- [x] `OPENROUTER_API_KEY` - 500+ models with routing
- [x] `HF_TOKEN` - HuggingFace Hub + MCP
- [x] `GLM_API_KEY` - Zhipu GLM direct access
- [ ] `CEREBRAS_API_KEY` - Ultra-fast (1000+ t/s) - [Sign up](https://cloud.cerebras.ai/)
- [ ] `GROQ_API_KEY` - Fast (200-400 t/s) - [Sign up](https://console.groq.com/)
- [ ] `TOGETHER_API_KEY` - Long context (Qwen3-Coder 256K) - [Sign up](https://api.together.xyz/)

### MCP Servers (Global)
- [x] `chrome-devtools` - Browser debugging
- [x] `browser` - Puppeteer automation
- [x] `sniper-gun` - Custom (PROJECT_lechworld)
- [x] `hf-mcp` - HuggingFace Hub search + Gradio Spaces

### MCP Servers (PROJECT_elements only)
- [x] `perplexity` - Research queries
- [x] `deepwebresearch` - Deep web research
- [ ] Make perplexity global? (optional)
- [ ] Make deepwebresearch global? (optional)

### Shell Aliases (~/.zshrc)
- [x] `zai` / `claude-zai` - Z.ai GLM ($3-15/mo)
- [x] `claude-1m` - Anthropic 1M context beta

### Configuration Files
- [x] `~/.claude/mcp.json` - Global MCPs
- [x] `~/.claude/settings-zai.json` - Z.ai config
- [x] `~/.zshrc` - Shell aliases

### Optional Enhancements
- [ ] Upgrade Z.ai from GLM-4.6 to GLM-4.7
- [ ] Add Cerebras for ultra-fast iteration
- [ ] Add Groq for fast coding
- [ ] Add Together for 256K context Qwen3-Coder
- [ ] Make research MCPs global

### Verification
- [x] HF token works (`curl` test passed)
- [ ] Restart Claude Code to activate HF MCP
- [ ] Test: `source scripts/claude-model-switch.sh openrouter`
- [ ] Test: `zai "hello"` (Z.ai alias)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Claude Code CLI                          │
│                    (agent logic, tools, MCP)                    │
└─────────────────────────────────────────────────────────────────┘
                                │
                    ANTHROPIC_BASE_URL + ANTHROPIC_API_KEY
                                │
                                ▼
┌────────────────────────────────────────────────────────────────┐
│                     Inference Provider                         │
├──────────────┬──────────────┬──────────────┬───────────────────┤
│  Anthropic   │  OpenRouter  │    Z.ai      │   Cerebras/Groq   │
│  (default)   │ (500+ models)│  (GLM-4.7)   │   (ultra-fast)    │
└──────────────┴──────────────┴──────────────┴───────────────────┘
```

**Key Insight:** Claude Code CLI is just the "body" (agent logic, file ops, MCP tools). The "brain" (LLM) can be swapped by changing `ANTHROPIC_BASE_URL`.

---

## Current State

### Working
| Component | Status | Notes |
|-----------|--------|-------|
| Claude Code CLI | ✓ | v2.1.25 |
| Anthropic (default) | ✓ | `ANTHROPIC_API_KEY` in Doppler |
| OpenRouter | ✓ | `OPENROUTER_API_KEY` in Doppler |
| Z.ai GLM | ✓ | `~/.claude/settings-zai.json` + aliases |
| HF Token | ✓ | Updated 2026-01-30 |
| HF MCP | ✓ | Global in `~/.claude/mcp.json` |
| Model Switcher | ✓ | `scripts/claude-model-switch.sh` |

### Optional (Not Yet Configured)
| Component | Status | Action |
|-----------|--------|--------|
| Cerebras | No API key | [Sign up](https://cloud.cerebras.ai/) - ultra-fast |
| Groq | No API key | [Sign up](https://console.groq.com/) - fast |
| Together | No API key | [Sign up](https://api.together.xyz/) - long context |

---

## Immediate Fixes Required

### ~~1. Fix Hugging Face Token~~ DONE

~~Your current token `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` is invalid.~~

**FIXED:** New token `hf_iE0iHZDlgkpzJqtrItyLoLbAEebfdZSNcV` configured on 2026-01-30.

**Steps:**

```bash
# 1. Go to HuggingFace and create new token
open https://huggingface.co/settings/tokens

# 2. Create token with these permissions:
#    - Read access to contents of all repos you can access
#    - (Optional) Write access if you want to push models

# 3. Update Doppler with new token
doppler secrets set HF_TOKEN "hf_YOUR_NEW_TOKEN" --project ai-tools --config dev
doppler secrets set HUGGINGFACE_API_KEY "hf_YOUR_NEW_TOKEN" --project ai-tools --config dev

# 4. Update global MCP config (I'll do this when you provide new token)
# The token is hardcoded in ~/.claude/mcp.json for the hf-mcp server

# 5. Verify it works
curl -s -H "Authorization: Bearer hf_YOUR_NEW_TOKEN" https://huggingface.co/api/whoami
# Should return your username, not an error
```

---

## Provider Setup

### Provider Comparison

| Provider | Speed | Models | Cost | Best For |
|----------|-------|--------|------|----------|
| **Anthropic** | Standard | Opus, Sonnet, Haiku | $$$ | Premium reasoning |
| **Z.ai** | Standard | GLM-4.7 (73.8% SWE-bench) | $3-15/mo | Daily driver, budget |
| **OpenRouter** | Varies | 500+ models | Pay-per-token | Flexibility, routing |
| **Cerebras** | 1000-3000 t/s | Llama 3.x, gpt-oss | Pay-per-token | Ultra-fast iteration |
| **Groq** | 200-400 t/s | Llama, Mixtral | Pay-per-token | Fast coding |
| **Together** | 200-400 t/s | Qwen3-Coder 256K | Pay-per-token | Long context |

### Setup Each Provider

#### Anthropic (Already configured)
```bash
# Verify
doppler secrets get ANTHROPIC_API_KEY --plain | head -c 20
```

#### Z.ai GLM (Already configured)
```bash
# Your aliases in ~/.zshrc:
zai          # Uses GLM-4.6 via Z.ai
claude-zai   # Same
ZAI          # Same

# Config file: ~/.claude/settings-zai.json
# Cost: $3/mo (Lite) or $15/mo (Pro)
# Upgrade to GLM-4.7: Edit settings-zai.json, change "model": "glm-4.7"
```

#### OpenRouter (Just configured)
```bash
# Key already in Doppler
doppler secrets get OPENROUTER_API_KEY --plain | head -c 20

# Usage:
source scripts/claude-model-switch.sh openrouter
claude --model qwen/qwen3-coder-480b-a35b-instruct "prompt"

# Browse models: https://openrouter.ai/models
```

#### Cerebras (Optional - Ultra Fast)
```bash
# 1. Sign up
open https://cloud.cerebras.ai/

# 2. Get API key from dashboard

# 3. Add to Doppler
doppler secrets set CEREBRAS_API_KEY "your-key" --project ai-tools --config dev

# 4. Use
source scripts/claude-model-switch.sh cerebras
claude --model llama3.1-70b "prompt"
```

#### Groq (Optional - Fast)
```bash
# 1. Sign up
open https://console.groq.com/

# 2. Create API key

# 3. Add to Doppler
doppler secrets set GROQ_API_KEY "your-key" --project ai-tools --config dev

# 4. Use
source scripts/claude-model-switch.sh groq
claude --model llama-3.3-70b-versatile "prompt"
```

#### Together AI (Optional - Long Context)
```bash
# 1. Sign up
open https://api.together.xyz/

# 2. Get API key

# 3. Add to Doppler
doppler secrets set TOGETHER_API_KEY "your-key" --project ai-tools --config dev

# 4. Use
source scripts/claude-model-switch.sh together
claude --model Qwen/Qwen3-Coder-480B-A35B-Instruct "prompt"
```

---

## Model Switching

### Option 1: Source the Switcher (Session-based)

```bash
# From PROJECT_elements directory
source scripts/claude-model-switch.sh <provider>

# Providers: anthropic, openrouter, glm, cerebras, groq, together, local
# Example:
source scripts/claude-model-switch.sh openrouter
claude --model deepseek/deepseek-coder-v2 "Explain this repo"
```

### Option 2: Z.ai Aliases (Persistent)

```bash
# Already in your ~/.zshrc
zai                    # Uses Z.ai with GLM model
claude-1m              # Uses Anthropic with 1M context beta
```

### Option 3: Direct Environment (One-off)

```bash
ANTHROPIC_BASE_URL=https://openrouter.ai/api \
ANTHROPIC_API_KEY=$(doppler secrets get OPENROUTER_API_KEY --plain) \
claude --model qwen/qwen3-coder-480b-a35b-instruct "prompt"
```

---

## MCP Configuration

### Global MCPs (All 50 Projects)

Location: `~/.claude/mcp.json`

```json
{
  "mcpServers": {
    "sniper-gun": { ... },
    "chrome-devtools": { ... },
    "browser": { ... },
    "hf-mcp": {
      "type": "http",
      "url": "https://huggingface.co/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_HF_TOKEN"
      }
    }
  }
}
```

### Project-Specific MCPs (PROJECT_elements)

Configured via `claude mcp add` command, stored in `~/.claude.json` under project key.

Current: perplexity, deepwebresearch

### To Make MCPs Global

```bash
# Add to global config
claude mcp add <name> -s user ...

# Or edit ~/.claude/mcp.json directly
```

---

## Model Reference

### Top Open Coding Models (Jan 2026)

| Model | Context | SWE-bench | Provider |
|-------|---------|-----------|----------|
| Qwen3-Coder-480B-A35B | 256K | SOTA open | Together, OpenRouter |
| GLM-4.7 | 128K | 73.8% | Z.ai ($3-15/mo) |
| DeepSeek-Coder-V2 | 128K | Strong | OpenRouter |
| Llama 3.3 70B | 128K | Good | Cerebras, Groq |
| Qwen2.5-Coder-32B | 131K | Very good | Together, Local |

### Speed Tiers

| Tier | Provider | Speed | Notes |
|------|----------|-------|-------|
| S | Cerebras | 1000-3000 t/s | Fastest commercial |
| A | Groq | 200-400 t/s | Great for iteration |
| A | Together | 200-400 t/s | Good model selection |
| B | OpenRouter | Varies | Routes to fastest |
| C | Local | Hardware-dependent | Privacy, offline |

### Context Window Recommendations

| Use Case | Recommended |
|----------|-------------|
| Quick edits, single files | 8K-32K (any model) |
| Multi-file refactoring | 64K-128K |
| Repo-scale reasoning | 128K-256K (Qwen3-Coder) |
| Massive codebase | Use retrieval/RAG, not brute context |

---

## Quick Reference

### Daily Commands

```bash
# Default Claude (Anthropic)
claude "prompt"

# Z.ai GLM (budget daily driver)
zai "prompt"

# Switch to OpenRouter for specific model
source scripts/claude-model-switch.sh openrouter
claude --model qwen/qwen3-coder-480b-a35b-instruct "prompt"

# Ultra-fast with Cerebras
source scripts/claude-model-switch.sh cerebras
claude --model llama3.1-70b "prompt"

# Back to default
source scripts/claude-model-switch.sh anthropic
```

### Check Current Config

```bash
# Which endpoint am I using?
echo $ANTHROPIC_BASE_URL

# What keys are available?
doppler secrets | grep -iE "anthropic|openrouter|groq|cerebras|together|hf"

# MCP status
claude mcp list
```

### Troubleshooting

```bash
# Test OpenRouter connection
curl -s https://openrouter.ai/api/v1/models \
  -H "Authorization: Bearer $(doppler secrets get OPENROUTER_API_KEY --plain)" | head -c 500

# Test HF token
curl -s -H "Authorization: Bearer $(doppler secrets get HF_TOKEN --plain)" \
  https://huggingface.co/api/whoami

# Reset to Anthropic default
unset ANTHROPIC_BASE_URL
export ANTHROPIC_API_KEY=$(doppler secrets get ANTHROPIC_API_KEY --plain)
```

---

## File Locations

| File | Purpose |
|------|---------|
| `~/.claude/mcp.json` | Global MCP servers (all projects) |
| `~/.claude.json` | Main Claude Code config + per-project settings |
| `~/.claude/settings-zai.json` | Z.ai GLM configuration |
| `~/.zshrc` | Shell aliases (zai, claude-1m, etc.) |
| `scripts/claude-model-switch.sh` | Provider switching script |
| `docs/AI_MODELS_REFERENCE.md` | Quick reference (this project) |

---

## Doppler Secrets Inventory

| Secret | Project | Status |
|--------|---------|--------|
| ANTHROPIC_API_KEY | ai-tools | ✓ |
| OPENAI_API_KEY | ai-tools | ✓ |
| OPENROUTER_API_KEY | ai-tools | ✓ |
| GLM_API_KEY | ai-tools | ✓ |
| HF_TOKEN | ai-tools | ✓ (updated 2026-01-30) |
| HUGGINGFACE_API_KEY | ai-tools | ✓ (updated 2026-01-30) |
| GEMINI_API_KEY | ai-tools | ✓ |
| PERPLEXITY_API_KEY | ai-tools | ✓ |
| REPLICATE_API_TOKEN | ai-tools | ✓ |
| RUNPOD_API_KEY | ai-tools | ✓ |
| CEREBRAS_API_KEY | ai-tools | ✗ Not set (optional) |
| GROQ_API_KEY | ai-tools | ✗ Not set (optional) |
| TOGETHER_API_KEY | ai-tools | ✗ Not set (optional) |

---

## Next Steps

1. **Fix HF Token** (required) - see [Immediate Fixes](#immediate-fixes-required)
2. **Sign up for speed providers** (optional) - Cerebras, Groq, Together
3. **Upgrade Z.ai to GLM-4.7** (optional) - edit `~/.claude/settings-zai.json`
4. **Make research MCPs global** (optional) - perplexity, deepwebresearch

---

## Sources

- [OpenRouter Claude Code Integration](https://openrouter.ai/docs/guides/guides/claude-code-integration)
- [HuggingFace MCP Server](https://huggingface.co/docs/hub/en/hf-mcp-server)
- [Z.ai GLM Coding Plan](https://z.ai/subscribe)
- [Cerebras Inference](https://www.cerebras.ai/blog/introducing-cerebras-inference-ai-at-instant-speed)
- [SWE-bench Leaderboard](https://www.swebench.com/)
- [BFCL Leaderboard](https://gorilla.cs.berkeley.edu/leaderboard.html)
