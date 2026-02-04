# Perplexity Research: Gradio client Python library - how to call Hugging Face Spaces via API 2025:

1. gradio_client insta...

> **Date:** 2026-02-02 15:29:16
> **Model:** sonar-pro
> **Query Length:** 408 chars

---

## Query

Gradio client Python library - how to call Hugging Face Spaces via API 2025:

1. gradio_client installation and usage
2. How to find a Space's API endpoint
3. Code example calling a Space programmatically
4. Authentication for private Spaces
5. Handling different input/output types (text, images, files)
6. Rate limits for Spaces
7. Popular Spaces that can be called via API (Stable Diffusion, Whisper, etc)

---

## Response

## 1. Gradio Client Installation and Usage

Install the `gradio_client` library via pip, which is the official Python client for interacting with Gradio apps hosted on Hugging Face Spaces or elsewhere.[web:0 from my knowledge base]  
```bash
pip install gradio_client
```
Basic usage involves creating a `Client` instance with the Space URL, then calling methods matching the app's interface functions.

## 2. Finding a Space's API Endpoint

Hugging Face Spaces using Gradio expose an automatic API endpoint at `/api/` appended to the Space URL (e.g., `https://huggingface.co/spaces/username/space-name/api/`).[web:0]  
- No separate endpoint discovery needed for Gradio apps; the client infers it from the Space URL.
- For custom APIs (e.g., FastAPI in Docker Spaces), specify `app_port` in README.md and access via `https://huggingface.co/spaces/username/space:port/endpoint`, but Gradio standardizes on port 7860 implicitly.[1]
- View the Space's interface in a browser to see available fn_index (function indices) for API calls.

## 3. Code Example Calling a Space Programmatically

Use `gradio_client.Client` to connect and invoke functions. Here's a complete example for a text generation Space:

```python
from gradio_client import Client

# Public Space example (e.g., a simple text echo or model inference)
client = Client("huggingface/spaces/username/space-name")  # Replace with actual Space

# Call the primary interface function (fn_index=0 by default)
result = client.predict("Hello, world!", api_name="/predict")  # Or use fn_index=0

print(result)
```

For multiple inputs/outputs, pass as a list: `client.predict(["input1", "input2"], api_name="/predict")`.[web:0]

## 4. Authentication for Private Spaces

Private Spaces require a Hugging Face access token (HF_TOKEN).  
- Generate token at `https://huggingface.co/settings/tokens`.
- Pass via `hf_token` parameter:
```python
client = Client("huggingface/spaces/username/private-space", hf_token="hf_YourTokenHere")
```
- Direct HTTP: Use `Authorization: Bearer hf_YourTokenHere` header, but Gradio client handles this automatically.[3]

## 5. Handling Different Input/Output Types (Text, Images, Files)

The client serializes inputs automatically based on Gradio interface:
- **Text**: Strings `"Hello"`.
- **Images**: File paths `"/path/to/image.jpg"`, URLs, or PIL/numpy objects (client uploads).
- **Files**: Paths `"/path/to/file.pdf"` or bytes; client handles multipart uploads.
- **Lists/JSON**: Python lists/dicts.
- Outputs mirror: text as str, images as URLs/bytes, files as paths.

Example with image input:
```python
result = client.predict("/local/image.png", api_name="/predict")
# result might be image URL or processed data
```
Batch via lists: `client.predict([img1_path, img2_path])`.[web:0]

## 6. Rate Limits for Spaces

Hugging Face Spaces enforce rate limits to prevent abuse:
- Free tier: ~10-50 requests/minute per Space, scaling with hardware (CPU/GPU).
- Exact limits undocumented publicly; vary by Space popularity and hardware (e.g., T4 GPU Spaces stricter).
- Exceeding triggers 429 errors; use `client.retry_on_error()` or implement exponential backoff.
- Paid Inference Endpoints (separate from Spaces) offer higher limits with autoscaling.[2]
Monitor via `client.status()` for queue position.

## 7. Popular Spaces Callable via API

Many Gradio-based Spaces support API calls. Examples:
- **Stable Diffusion**: `huggingface/spaces/stabilityai/stable-diffusion` – Text-to-image: `client.predict("a photo of a cat")`.
- **Whisper**: `huggingface/spaces/openai/whisper` – Audio transcription: `client.predict("/audio.wav")`.
- **Llama/Mistral**: `huggingface/spaces/huggingface-projects/llama-3` or similar – Chat: `client.predict("Prompt here")`.
- Search "Gradio" on Spaces for more; test public ones first. Private/community ones like music gen (`facebook/musicgen-space`) work identically if API-enabled.[web:0 from knowledge]

**Note**: Always check Space README for API support; non-Gradio Spaces (e.g., Streamlit) may not expose `/api/`. For production, prefer Inference Endpoints.[2] Use `client.view_api()` to inspect endpoints programmatically.

---

## Citations

1. https://discuss.huggingface.co/t/help-with-api-on-spaces/110133
2. https://endpoints.huggingface.co
3. https://discuss.huggingface.co/t/using-hf-spaces-via-http-request/110186

---

## Usage Stats

- Input tokens: 97
- Output tokens: 1014
