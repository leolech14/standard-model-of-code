# AI Models API Reference

Quick reference for AI model integrations used in this project.

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

**See also:** `~/vault/ai-models/README.md` for full model catalog
