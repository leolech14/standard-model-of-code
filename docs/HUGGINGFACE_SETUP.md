# Hugging Face API Setup

## Quick Reference

**Model Documentation:** `~/vault/ai-models/huggingface/trellis-2.md`
**Doppler Project:** ai-tools
**Doppler Config:** dev

---

## Setup Instructions

### 1. Get Your Hugging Face API Token

Visit: https://huggingface.co/settings/tokens

Create a token with appropriate permissions.

### 2. Add to Doppler

```bash
cd ~/PROJECTS_all/PROJECT_elements
doppler secrets set HUGGINGFACE_API_KEY "your-token-here"
```

### 3. Verify

```bash
doppler secrets get HUGGINGFACE_API_KEY --plain
```

---

## Usage

The API key is automatically loaded from environment when using Doppler:

```bash
doppler run -- python your_script.py
```

Or in your Python code:

```python
import os
from gradio_client import Client

# Get from environment (Doppler injects this)
hf_token = os.getenv('HUGGINGFACE_API_KEY')

# Use with Gradio client
client = Client("microsoft/TRELLIS.2", hf_token=hf_token)
```

---

## Available Models

### TRELLIS.2 - Image to 3D
- **Space:** microsoft/TRELLIS.2
- **Docs:** `~/vault/ai-models/huggingface/trellis-2.md`
- **Use case:** Generate 3D GLB models from 2D images

---

**Last Updated:** 2026-01-28
