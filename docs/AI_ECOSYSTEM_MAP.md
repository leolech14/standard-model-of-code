# AI Ecosystem Map

**Your complete AI capabilities inventory**
**Updated:** 2026-01-30

---

## Quick Reference

| Need | Command |
|------|---------|
| Default Claude | `claude` |
| Budget daily driver | `zai` |
| Ultra-fast (1000+ t/s) | `source scripts/claude-model-switch.sh cerebras` |
| 500+ models | `source scripts/claude-model-switch.sh openrouter` |
| 1M context | `claude-1m` |
| Research query | Use `perplexity` MCP (built into this session) |
| Browser automation | Use `browser` MCP |
| HuggingFace search | Use `hf-mcp` MCP |

---

## 1. Claude Code Inference Providers

### Primary Providers (Configured & Tested)

| Provider | How to Use | Speed | Models | Cost |
|----------|------------|-------|--------|------|
| **Anthropic** | `claude` (default) | Standard | Opus 4.5, Sonnet, Haiku | $$$ |
| **Z.ai GLM** | `zai` or `claude-zai` | Standard | GLM-4.6/4.7 | $3-15/mo |
| **Cerebras** | `source scripts/claude-model-switch.sh cerebras` | 1000-3000 t/s | llama-3.3-70b, qwen-3-235b, gpt-oss-120b, glm-4.7 | Pay-per-token |
| **OpenRouter** | `source scripts/claude-model-switch.sh openrouter` | Varies | 346+ models | Pay-per-token |

### Special Aliases

```bash
# 1M context window (Anthropic beta)
claude-1m "analyze this entire codebase"

# Z.ai budget mode
zai "refactor this function"
ZAI "same thing"
claude-zai "same thing"
```

### Model Switcher Commands

```bash
source scripts/claude-model-switch.sh anthropic   # Default
source scripts/claude-model-switch.sh openrouter  # 346+ models
source scripts/claude-model-switch.sh cerebras    # Ultra-fast
source scripts/claude-model-switch.sh glm         # Direct Zhipu
source scripts/claude-model-switch.sh local       # Docker Model Runner
source scripts/claude-model-switch.sh help        # Show all options
```

---

## 2. MCP Servers (Tools Inside Claude Code)

### Active MCPs

| MCP | What It Does | Example Use |
|-----|--------------|-------------|
| **perplexity** | Web research with citations | "Research best practices for X" |
| **deepwebresearch** | Deep multi-page research | "Deep research on topic Y" |
| **browser** | Puppeteer browser automation | "Navigate to URL and screenshot" |
| **chrome-devtools** | Debug Chrome, inspect pages | "Take page snapshot" |
| **hf-mcp** | Search HuggingFace Hub, use Gradio Spaces | "Find models for image generation" |

### Using MCPs

MCPs are **automatic** - just ask naturally:

```
You: "Search Hugging Face for Qwen3 Coder models"
→ Claude uses hf-mcp automatically

You: "Research the latest on transformer architectures"
→ Claude uses perplexity automatically

You: "Take a screenshot of google.com"
→ Claude uses browser automatically
```

---

## 3. Direct API Access (For Scripts/Apps)

### Text/Chat Models

| Service | Key | How to Use |
|---------|-----|------------|
| **OpenAI** | `OPENAI_API_KEY` | `doppler run -- python script.py` |
| **Gemini** | `GEMINI_API_KEY` | `gemini-ai` alias or API calls |
| **Perplexity** | `PERPLEXITY_API_KEY` | Research API |
| **Vertex AI** | `VERTEX_AI_API_KEY` + credentials | Google Cloud AI |

### Image/Video Generation

| Service | Key | Capability |
|---------|-----|------------|
| **Replicate** | `REPLICATE_API_TOKEN` | Run any model (Stable Diffusion, etc.) |
| **RunPod** | `RUNPOD_API_KEY` | Serverless GPU inference |
| **HuggingFace** | `HF_TOKEN` | Inference Endpoints, Spaces |

### Audio/Voice

| Service | Key | Capability |
|---------|-----|------------|
| **ElevenLabs** | `ELEVENLABS_API_KEY` | Text-to-speech, voice cloning |
| **Tavus** | `TAVUS_API_KEY` | AI video generation |

### Video/Media

| Service | Key | Capability |
|---------|-----|------------|
| **Creatomate** | `CREATOMATE_API_KEY` | Video rendering API (needs setup) |
| **OpusClip** | `OPUSCLIP_API_KEY` | Video clipping (needs setup) |
| **Magic Hour** | `MAGIC_HOUR_API_KEY` | Video effects (needs setup) |
| **Argil** | `ARGIL_API_KEY` | AI avatars (needs setup) |

---

## 4. Browser Automation

### Browser Agent (Custom Tool)

```bash
ba              # Main browser agent
bag             # Browser agent GUI mode
bat             # Browser agent task execution
bas             # Browser agent status
```

### Via MCP (Inside Claude Code)

```
"Navigate to example.com and click the login button"
"Fill out the form with name John"
"Take a screenshot of the current page"
```

---

## 5. Utility Aliases

### Claude Automation

```bash
claude-auto     # Auto-accept Claude prompts
claude-yes      # Yes to all prompts
claude-auto-on  # Enable auto mode
claude-auto-off # Disable auto mode
ai-status       # Check AI session status
```

### Secrets Management

```bash
getsecret KEY_NAME           # Get from Doppler (ai-tools)
getgcp KEY_NAME              # Get from GCP Doppler project
doppler secrets              # List all secrets
```

### Infrastructure

```bash
servers         # Manage Claude servers
START           # Start everything
fix-mcp         # Restore MCP config if broken
```

---

## 6. API Usage Examples

### OpenAI (GPT)

```python
import openai
import os

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello"}]
)
```

Run with: `doppler run -- python script.py`

### Gemini

```bash
# Via alias
gemini-ai "your prompt"

# Or in Python
import google.generativeai as genai
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
```

### Replicate (Any Model)

```python
import replicate

output = replicate.run(
    "stability-ai/sdxl:latest",
    input={"prompt": "a cat"}
)
```

Run with: `doppler run -- python script.py`

### ElevenLabs (TTS)

```python
from elevenlabs import generate, set_api_key
import os

set_api_key(os.getenv("ELEVENLABS_API_KEY"))
audio = generate(text="Hello world", voice="Rachel")
```

### HuggingFace Inference

```python
from huggingface_hub import InferenceClient
import os

client = InferenceClient(token=os.getenv("HF_TOKEN"))
response = client.text_generation("Hello, I am", model="mistralai/Mistral-7B-v0.1")
```

---

## 7. Provider Comparison Matrix

| Provider | Speed | Context | Cost | Best For |
|----------|-------|---------|------|----------|
| Anthropic (Opus) | Standard | 200K | $$$ | Complex reasoning |
| Anthropic (Sonnet) | Standard | 200K | $$ | Daily coding |
| Z.ai GLM | Standard | 128K | $ | Budget daily driver |
| Cerebras | 1000+ t/s | 128K | $$ | Fast iteration |
| OpenRouter | Varies | Varies | Varies | Model variety |
| OpenAI (GPT-4o) | Standard | 128K | $$ | Alternative reasoning |
| Gemini | Standard | 1M+ | $$ | Huge context |

---

## 8. File Locations

| File | Purpose |
|------|---------|
| `~/.claude/mcp.json` | Global MCP servers |
| `~/.claude/settings-zai.json` | Z.ai configuration |
| `~/.zshrc` | Shell aliases |
| `scripts/claude-model-switch.sh` | Provider switcher |
| `docs/OPEN_MODELS_COMPLETE_GUIDE.md` | Full setup guide |

---

## 9. Doppler Secrets Summary

### Configured & Working
- `ANTHROPIC_API_KEY` - Claude
- `OPENROUTER_API_KEY` - 346+ models
- `CEREBRAS_API_KEY` - Ultra-fast
- `GLM_API_KEY` / `ZAI_API_KEY` - Z.ai
- `HF_TOKEN` - HuggingFace
- `OPENAI_API_KEY` - GPT models
- `GEMINI_API_KEY` - Google AI
- `PERPLEXITY_API_KEY` - Research
- `ELEVENLABS_API_KEY` - TTS
- `REPLICATE_API_TOKEN` - Any model
- `RUNPOD_API_KEY` - GPU inference
- `TAVUS_API_KEY` - Video AI
- `VERTEX_AI_API_KEY` - Google Cloud AI

### Placeholders (Need Setup)
- `ARGIL_API_KEY`
- `CREATOMATE_API_KEY`
- `MAGIC_HOUR_API_KEY`
- `OPUSCLIP_API_KEY`

---

## 10. Claude Code with Open Models (Full Agent Experience)

Claude Code CLI can use open-source models via OpenRouter (Anthropic-compatible API).

### Quick Access Aliases
```bash
# Full Claude Code experience with open models
claude-or --model qwen/qwen3-coder "refactor this function"
claude-qwen "explain this codebase"       # Qwen 2.5 Coder 32B (131K context)
claude-deepseek "debug this error"        # DeepSeek Coder
claude-llama "write tests"                # Llama 3.3 70B
```

### Top Models for Coding (via OpenRouter)
| Model | Context | Cost | Best For |
|-------|---------|------|----------|
| `qwen/qwen3-coder` | 262K | $0.22/M | Agentic coding, tool use |
| `qwen/qwen3-coder:free` | 262K | FREE | Budget daily driver |
| `meta-llama/llama-4-maverick` | 1M | $0.15/M | Huge context |
| `qwen/qwen-2.5-coder-32b-instruct` | 131K | $0.15/M | Reliable workhorse |
| `mistralai/codestral-2508` | 256K | $0.30/M | Fast, long context |

### What Works / What Doesn't
- **CLI scaffold**: File editing, tool use, multi-step workflows - ALL work
- **Model quality**: Varies - open models may need more iterations
- **Speed**: Depends on provider OpenRouter routes to

---

## 11. Quick Queries (No CLI)

For fast one-off questions without the full CLI:

```bash
cerebras "explain recursion in 3 sentences"  # 3000 t/s, Llama 3.3 70B
```

---

## 12. Common Workflows

### "I need to code fast with Claude"
```bash
claude  # Uses Opus 4.5 (smartest)
```

### "I need to code with open models (full CLI)"
```bash
claude-qwen "implement this feature"
# or
claude-or --model qwen/qwen3-coder "refactor this"
```

### "I need to save money"
```bash
zai
```

### "I need the smartest model"
```bash
claude  # Uses Opus 4.5 by default
```

### "I need a specific open model"
```bash
source scripts/claude-model-switch.sh openrouter
claude --model deepseek/deepseek-coder-v2
```

### "I need research with citations"
```
# Inside Claude Code, just ask:
"Research the latest developments in quantum computing"
# → Uses Perplexity MCP automatically
```

### "I need to automate a browser task"
```
# Inside Claude Code:
"Go to github.com, search for 'claude code', screenshot the results"
# → Uses browser MCP automatically
```

### "I need to generate an image"
```python
# Use Replicate
doppler run -- python -c "
import replicate
output = replicate.run('stability-ai/sdxl:latest', input={'prompt': 'a sunset'})
print(output)
"
```

### "I need text-to-speech"
```python
# Use ElevenLabs
doppler run -- python -c "
from elevenlabs import generate, play, set_api_key
import os
set_api_key(os.getenv('ELEVENLABS_API_KEY'))
audio = generate(text='Hello world', voice='Rachel')
play(audio)
"
```
