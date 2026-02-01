# Research: How to use HuggingFace Spaces programmatically from terminal/scripts:

1. How does the HuggingFace M...

> **Date:** 2026-01-30 22:37:01
> **Source:** perplexity-mcp
> **Model:** sonar-pro
> **Checksum:** `sha256:a728dd3a4757c6e35b996d9154432db808e4fb2335e24a1488064ef0aeb4da12`
> **Raw JSON:** `raw/20260130_223701_how_to_use_huggingface_spaces_programmatically_fro.json`

---

## Query

How to use HuggingFace Spaces programmatically from terminal/scripts:

1. How does the HuggingFace MCP server work with Gradio Spaces? Can Claude Code call Spaces as tools?

2. How to use gradio_client Python library to call HuggingFace Spaces from command line or scripts?

3. Can HuggingFace Spaces be used for LLM inference (like running Qwen, Llama models hosted on Spaces)?

4. What's the authentication flow - do you need HF_TOKEN for all Spaces or only private ones?

5. Are there rate limits or costs for using public Spaces via API?

Provide practical examples for automated/scripted usage.

---

## Response

### 1. HuggingFace MCP Server with Gradio Spaces and Claude Code Integration
No information on **HuggingFace MCP server** (possibly referring to Model Control Plane or a specific tool) or its integration with Gradio Spaces is available in search results. Claude Code (Anthropic's coding agent) cannot directly call Spaces as tools based on provided data, as no mentions of Claude or tool-calling protocols like OpenAI-compatible endpoints for Spaces appear[1][2].

### 2. Using `gradio_client` Python Library for Command-Line/Script Calls
The **`gradio_client`** library enables programmatic access to HuggingFace Spaces (which typically run Gradio apps) via API. Install it with `pip install gradio_client`. Key steps from examples:

- Initialize a client with the Space URL and optional **HF_TOKEN** for authentication.
- Call the Space's `predict` method, specifying the function name (e.g., `run_inference`), inputs like files/images/text, and API name if duplicated.

**Practical Python script example** (adapted from ZeroGPU Qwen2 Vision Space usage)[1]:
```python
from gradio_client import Client
import os

# Set HF_TOKEN as env var or pass directly (required for private Spaces)
hf_token = os.getenv("HF_TOKEN")  # e.g., "hf_xxxxxxxxxxxxxxxx"

# Connect to Space (replace with your Space URL, e.g., https://huggingface.co/spaces/user/space-name)
client = Client("https://huggingface.co/spaces/katanaml/sparrow-q12", hf_token=hf_token)

# Call predict: fn_index=0 for first fn, api_name="run_inference" if specified
result = client.predict(
    fn_index=0,  # Or api_name="run_inference"
    files=["path/to/image.jpg"],  # handle_file for images
    text_input="Your query/prompt here",
    api_name="run_inference"  # Matches Gradio fn responsible for inference
)

print(result)  # Processed response (e.g., cleaned LLM output)
```
- Run from terminal: `python script.py`.
- For CLI one-liner, wrap in a bash script or use `python -c "from gradio_client import Client; c=Client('SPACE_URL'); print(c.predict(...))"`.
- Handles secure connections; processes responses (e.g., cleanup before return)[1].

### 3. Using Spaces for LLM Inference (e.g., Qwen, Llama Models)
Yes, **HuggingFace Spaces** support LLM inference for models like **Qwen** (e.g., Qwen2-Vision on ZeroGPU) and Llama variants, hosted via Gradio apps. Spaces use annotations like `@spaces.GPU` to allocate GPU/ZeroGPU pools for inference. Access via `gradio_client` as above—send prompts/images, get generated outputs. Limitations: Large models (>10GB) require Spaces or dedicated endpoints, not free inference APIs[1][2].

**Example for Qwen inference** (from script above): Pass image + text prompt to `run_inference`; Space executes on ZeroGPU, returns structured results (e.g., instrument names, prices from vision LLM)[1].

### 4. Authentication Flow
**HF_TOKEN** is required for **private Spaces** (set via env var, CLI, or client init for secure connections). Public Spaces often work without it, but token ensures access/stability. Flow: Generate token at huggingface.co/settings/tokens; pass to `Client(..., hf_token=token)` or env `HF_TOKEN`. Not exposed in code—read from session[1].

### 5. Rate Limits and Costs for Public Spaces
Search results lack specifics on **rate limits** or **costs**. Public Spaces use free tiers (e.g., ZeroGPU pools), but heavy usage may queue or hit soft limits (inferred from GPU allocation needs). No paid costs mentioned for API calls to public Spaces; monitor via Space dashboard. For high volume, upgrade to paid hardware (e.g., dedicated GPUs) or Inference Endpoints[1][2].

**Automated usage tips**:
- Factory pattern for routing: Script decides local vs. Space inference based on flags[1].
- Batch scripts: Loop `client.predict()` with inputs from CSV/files.
- Error handling: Retry on API errors (e.g., model too large)[2].

---

## Citations

1. https://www.youtube.com/watch?v=UkOzw6NVIoI
2. https://github.com/safevideo/autollm/discussions/211
3. https://www.youtube.com/watch?v=uvSEmGUqGEk

---

## Usage Stats

- Prompt tokens: 130
- Completion tokens: 930
- Total tokens: 1060
