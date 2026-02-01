# HuggingFace Complete Capability Guide

**Account:** leolech14 (Pro $9/mo)
**Token:** Doppler `ai-tools/dev` → `HF_TOKEN`
**Last Updated:** 2026-01-31

---

## Quick Reference

| Need | Command |
|------|---------|
| Chat with LLM | `python wave/tools/ai/hf_space.py chat "prompt"` |
| Generate image | `python wave/tools/ai/hf_space.py image "prompt" output.png` |
| Call any Space | `python wave/tools/ai/hf_space.py call <space-id> <api-name> <args>` |
| List models | `python wave/tools/ai/hf_space.py models` |

---

## 1. Your Pro Account Benefits

| Feature | Free | Pro ($9/mo) |
|---------|------|-------------|
| ZeroGPU daily quota | 3.5 min | **25 min** |
| Inference Providers | 100k units/mo | **2M units/mo** |
| Private Storage | 100GB | **1TB** |
| ZeroGPU Spaces limit | 0 | **10** |
| Queue priority | Medium | **Highest** |
| Dev Mode (SSH/VS Code) | No | **Yes** |

---

## 2. Spaces (App Hosting)

**What:** Git repos where you host ML demo apps with Gradio UI + API endpoint.

### Create a Space
1. Go to https://huggingface.co/new-space
2. Choose Gradio SDK
3. Push code → auto-deploys

### Call Any Public Space
```bash
# Via CLI
python wave/tools/ai/hf_space.py call black-forest-labs/FLUX.1-schnell /infer '{"prompt":"cat"}'

# Via Python
from gradio_client import Client
client = Client("black-forest-labs/FLUX.1-schnell")
result = client.predict(prompt="a cat", api_name="/infer")
```

### Hardware Options

| Hardware | vCPU | RAM | GPU VRAM | Price/hr |
|----------|------|-----|----------|----------|
| CPU Basic | 2 | 16GB | - | FREE |
| CPU Upgrade | 8 | 32GB | - | $0.03 |
| Nvidia T4 | 4-8 | 15-30GB | 16GB | $0.40-0.60 |
| Nvidia L4 | 8-48 | 30-186GB | 24-96GB | $0.80-3.80 |
| Nvidia A10G | 4-48 | 15-184GB | 24-96GB | $1.00-5.00 |
| Nvidia A100 | 12-96 | 142-1136GB | 80-640GB | $2.50-20.00 |

---

## 3. ZeroGPU (Free Dynamic GPUs)

**What:** Instead of renting dedicated GPU 24/7, your app grabs an H200 slice (70GB VRAM) only when needed.

### GPU Sizes

| Size | Hardware | VRAM | Quota Cost |
|------|----------|------|------------|
| `large` (default) | Half H200 | 70GB | 1x |
| `xlarge` | Full H200 | 141GB | 2x |

### Daily Quotas

| Account | Daily GPU Time | Priority |
|---------|----------------|----------|
| Unauthenticated | 2 min | Low |
| Free | 3.5 min | Medium |
| **Pro (you)** | **25 min** | **Highest** |
| Enterprise | 45 min | Highest |

### Usage in Code
```python
import spaces
from diffusers import DiffusionPipeline

pipe = DiffusionPipeline.from_pretrained(...)
pipe.to('cuda')

@spaces.GPU  # Requests GPU only when called
def generate(prompt):
    return pipe(prompt).images

@spaces.GPU(duration=120)  # Custom max duration (default 60s)
def long_task(prompt):
    return expensive_operation(prompt)

@spaces.GPU(size="xlarge")  # Full H200 (uses 2x quota)
def huge_model(prompt):
    return giant_model(prompt)
```

---

## 4. Inference Providers (17 Providers, One API)

**What:** Unified API to access models across Cerebras, Groq, Together, Replicate, Fal, etc.

### Supported Tasks by Provider

| Provider | Chat LLM | Vision | Text-to-Image | Text-to-Video | Speech |
|----------|----------|--------|---------------|---------------|--------|
| Cerebras | Y | | | | |
| Groq | Y | Y | | | |
| Together | Y | Y | Y | | |
| Fal AI | | | Y | Y | Y |
| Replicate | | | Y | Y | Y |
| HF Inference | Y | Y | Y | | Y |
| SambaNova | Y | | | | |
| Cohere | Y | Y | | | |
| Fireworks | Y | Y | | | |

### Usage
```python
from huggingface_hub import InferenceClient

client = InferenceClient(token="hf_xxx")

# Auto-select best provider
response = client.chat.completions.create(
    model="meta-llama/Llama-3.3-70B-Instruct",
    messages=[{"role": "user", "content": "Hello"}]
)

# Force specific provider
response = client.chat.completions.create(
    model="meta-llama/Llama-3.3-70B-Instruct:cerebras",
    messages=[...]
)

# Select by policy
model="deepseek-ai/DeepSeek-R1:fastest"   # Highest throughput
model="deepseek-ai/DeepSeek-R1:cheapest"  # Lowest cost
```

### OpenAI-Compatible Endpoint
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key="hf_xxx"
)

response = client.chat.completions.create(
    model="meta-llama/Llama-3.3-70B-Instruct",
    messages=[{"role": "user", "content": "Hello"}]
)
```

---

## 5. CLI Tool: hf-space.py

Location: `wave/tools/ai/hf_space.py`

### Commands
```bash
# Chat (uses HF Inference API - reliable)
python wave/tools/ai/hf_space.py chat "What is Python?"
python wave/tools/ai/hf_space.py chat "Explain recursion" --model meta-llama/Llama-3.3-70B-Instruct

# Image generation (uses FLUX via ZeroGPU)
python wave/tools/ai/hf_space.py image "a red cube on white background"
python wave/tools/ai/hf_space.py image "sunset mountains" output.png

# List available chat models
python wave/tools/ai/hf_space.py models

# Call any Gradio Space directly
python wave/tools/ai/hf_space.py call <space-id> <api-name> [args...]

# Get Space info
python wave/tools/ai/hf_space.py info <space-id>
```

---

## 6. MCP Integration

Config: `~/.claude/mcp.json`

```json
{
  "hf-mcp": {
    "type": "http",
    "url": "https://huggingface.co/mcp",
    "headers": {
      "Authorization": "Bearer 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"
    }
  }
}
```

In Claude sessions:
- "Search HuggingFace for Qwen models"
- "Find image generation models"
- "What's trending on HuggingFace?"

---

## 7. Python Integration Examples

### Chat Completion
```python
import requests
import os

token = os.getenv("HF_TOKEN")

response = requests.post(
    "https://router.huggingface.co/v1/chat/completions",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "model": "meta-llama/Llama-3.2-3B-Instruct",
        "messages": [{"role": "user", "content": "Hello"}],
        "max_tokens": 100
    }
)
print(response.json()["choices"][0]["message"]["content"])
```

### Text-to-Image
```python
from huggingface_hub import InferenceClient

client = InferenceClient(token=os.getenv("HF_TOKEN"))
image = client.text_to_image(
    "A sunset over mountains",
    model="black-forest-labs/FLUX.1-dev"
)
image.save("sunset.png")
```

### Call Gradio Space
```python
from gradio_client import Client

client = Client("black-forest-labs/FLUX.1-schnell")
result = client.predict(
    prompt="a red cube",
    seed=0,
    randomize_seed=True,
    width=1024,
    height=1024,
    num_inference_steps=4,
    api_name="/infer"
)
```

---

## 8. Token Management

### Get Token
```bash
doppler secrets get HF_TOKEN --plain --project ai-tools --config dev
```

### Update Token
```bash
doppler secrets set HF_TOKEN="hf_new_token_here" --project ai-tools --config dev
```

### Verify Token
```bash
curl -s -H "Authorization: Bearer $(doppler secrets get HF_TOKEN --plain)" \
  https://huggingface.co/api/whoami-v2
```

---

## 9. Key URLs

| Resource | URL |
|----------|-----|
| Token settings | https://huggingface.co/settings/tokens |
| Your Spaces | https://huggingface.co/leolech14 |
| Create Space | https://huggingface.co/new-space |
| Browse models | https://huggingface.co/models |
| Inference playground | https://huggingface.co/playground |
| Provider settings | https://huggingface.co/settings/inference-providers |
| ZeroGPU Spaces list | https://huggingface.co/spaces/enzostvs/zero-gpu-spaces |

---

## 10. Sources

- [Spaces ZeroGPU](https://huggingface.co/docs/hub/en/spaces-zerogpu)
- [Spaces Overview](https://huggingface.co/docs/hub/en/spaces-overview)
- [Inference Providers](https://huggingface.co/docs/inference-providers/index)
- [Gradio Spaces](https://huggingface.co/docs/hub/en/spaces-sdks-gradio)
- [PRO Account](https://huggingface.co/pro)
