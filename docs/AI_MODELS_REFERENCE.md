# AI Models API Reference

Quick reference for AI model integrations used in this project.

**Registry:** `.agent/intelligence/TOOLS_REGISTRY.yaml` (T052)

## Quick Start: Model Switching

Switch Claude Code to use different inference providers:

```bash
# Source the switcher (from PROJECT_elements)
source scripts/claude-model-switch.sh <provider>

# Then run claude normally
claude --model <model-name> "your prompt"
```

**Available providers:**
| Provider | Command | Speed | Best For |
|----------|---------|-------|----------|
| Anthropic | `source scripts/claude-model-switch.sh anthropic` | Standard | Default, premium reasoning |
| OpenRouter | `source scripts/claude-model-switch.sh openrouter` | Varies | 500+ models, routing |
| GLM | `source scripts/claude-model-switch.sh glm` | Fast | GLM-4.7 (top SWE-bench) |
| Cerebras | `source scripts/claude-model-switch.sh cerebras` | 1000+ t/s | Ultra-fast iteration |
| Groq | `source scripts/claude-model-switch.sh groq` | 200-400 t/s | Fast coding |
| Together | `source scripts/claude-model-switch.sh together` | 200-400 t/s | Qwen3-Coder 256K |
| Local | `source scripts/claude-model-switch.sh local` | Hardware | Privacy, offline |

## Storage Location

All AI model API documentation is stored in:
```
~/vault/ai-models/
```

## Available Models

### Microsoft TRELLIS.2 (Hugging Face Space)
- **Documentation:** `~/vault/ai-models/huggingface/trellis-2.md`
- **Provider:** Gradio (Hugging Face Spaces)
- **Capability:** Image to 3D model generation
- **Secret:** `HUGGINGFACE_API_KEY` (Doppler: ai-tools/dev)

**Quick Start:**
```python
from gradio_client import Client
import os

# API key from Doppler (optional for public spaces)
api_key = os.getenv('HUGGINGFACE_API_KEY')

# Connect to TRELLIS.2
client = Client("microsoft/TRELLIS.2", hf_token=api_key)

# Generate 3D model from image
result = client.predict(
    image=handle_file('/path/to/image.png'),
    api_name="/image_to_3d"
)
```

---

## Adding New Models

1. Document in `~/vault/ai-models/<provider>/<model>.md`
2. Add API key to Doppler:
   ```bash
   doppler secrets set <KEY_NAME> <value> -p ai-tools -c dev
   ```
3. Update this reference file
4. Add usage example to relevant project docs

---

## Doppler Projects

| Directory | Project | Config |
|-----------|---------|--------|
| PROJECT_elements | ai-tools | dev |
| PROJECT_lechworld | general-purpose | prd |

**View secrets:**
```bash
doppler secrets
```

**Get specific secret:**
```bash
doppler secrets get HUGGINGFACE_API_KEY --plain
```

---

## Adding New Provider Keys

To add a new inference provider, add the API key to Doppler:

```bash
# OpenRouter (recommended - 500+ models with routing)
doppler secrets set OPENROUTER_API_KEY <key>  # Get from https://openrouter.ai/keys

# Cerebras (ultra-fast, 1000+ tokens/sec)
doppler secrets set CEREBRAS_API_KEY <key>    # Get from https://cloud.cerebras.ai/

# Groq (fast, 200-400 t/s)
doppler secrets set GROQ_API_KEY <key>        # Get from https://console.groq.com/

# Together AI (Qwen3-Coder, long context)
doppler secrets set TOGETHER_API_KEY <key>    # Get from https://api.together.xyz/
```

## Top Open Models for Coding (Jan 2026)

| Model | Context | SWE-bench | Best Provider |
|-------|---------|-----------|---------------|
| Qwen3-Coder-480B-A35B | 256K | SOTA open | Together, OpenRouter |
| GLM-4.7 | 128K | Top open | Zhipu (GLM_API_KEY) |
| DeepSeek-Coder-V2 | 128K | Strong | OpenRouter |
| Qwen2.5-Coder-32B | 131K | Very good | Together, Local |

## Speed Tiers

| Tier | Provider | Speed | Models |
|------|----------|-------|--------|
| S | Cerebras | 1000-3000 t/s | Llama 3.x, gpt-oss |
| A | Groq | 200-400 t/s | Llama 3.x, Mixtral |
| A | Together | 200-400 t/s | Qwen3-Coder, Llama |
| B | OpenRouter | Varies (routes) | 500+ models |

---

**See also:** `~/vault/ai-models/README.md` for full model catalog
