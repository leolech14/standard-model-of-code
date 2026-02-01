#!/usr/bin/env python3
"""
HuggingFace CLI - Chat, Image Generation, and Space Access

Usage:
    # Chat with LLM (uses HF Inference API)
    ./scripts/hf-space.py chat "What is Python?"
    ./scripts/hf-space.py chat "Explain recursion" --model meta-llama/Llama-3.3-70B-Instruct

    # Generate image (uses FLUX.1-schnell Space)
    ./scripts/hf-space.py image "a red cube on white background"
    ./scripts/hf-space.py image "sunset over mountains" output.png

    # Call any Gradio Space directly
    ./scripts/hf-space.py call <space-id> <api-name> <args...>

    # List available endpoints for a Space
    ./scripts/hf-space.py info <space-id>

    # List available models for chat
    ./scripts/hf-space.py models

Requires: HF_TOKEN in environment or Doppler (ai-tools/dev)
"""

import sys
import os
import json
import requests
from gradio_client import Client

# Defaults
DEFAULT_CHAT_MODEL = "meta-llama/Llama-3.2-3B-Instruct"
DEFAULT_IMAGE_SPACE = "black-forest-labs/FLUX.1-schnell"
HF_API_BASE = "https://router.huggingface.co/v1"

# Popular models for chat (free tier compatible)
CHAT_MODELS = [
    "meta-llama/Llama-3.2-3B-Instruct",      # Fast, good quality
    "meta-llama/Llama-3.3-70B-Instruct",     # Best quality
    "Qwen/Qwen2.5-72B-Instruct",             # Strong reasoning
    "microsoft/Phi-3-mini-4k-instruct",      # Small, fast
    "mistralai/Mistral-7B-Instruct-v0.3",    # Balanced
]

def get_token():
    """Get HF token from environment or Doppler"""
    token = os.getenv("HF_TOKEN")
    if not token:
        try:
            import subprocess
            result = subprocess.run(
                ["doppler", "secrets", "get", "HF_TOKEN", "--plain",
                 "--project", "ai-tools", "--config", "dev"],
                capture_output=True, text=True
            )
            token = result.stdout.strip() if result.returncode == 0 else None
        except:
            pass
    if not token:
        print("Error: HF_TOKEN not found. Set in environment or Doppler.", file=sys.stderr)
        sys.exit(1)
    return token


def cmd_chat(prompt, model=None):
    """Chat using HF Inference API (OpenAI-compatible)"""
    token = get_token()
    model = model or DEFAULT_CHAT_MODEL

    response = requests.post(
        f"{HF_API_BASE}/chat/completions",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1024
        },
        timeout=60
    )

    if response.status_code != 200:
        print(f"Error {response.status_code}: {response.text}", file=sys.stderr)
        sys.exit(1)

    data = response.json()
    content = data["choices"][0]["message"]["content"]
    print(content)


def cmd_image(prompt, output=None):
    """Generate image with FLUX"""
    client = Client(DEFAULT_IMAGE_SPACE)

    result = client.predict(
        prompt=prompt,
        seed=0,
        randomize_seed=True,
        width=1024,
        height=1024,
        num_inference_steps=4,
        api_name="/infer"
    )

    image_path = result[0] if isinstance(result, tuple) else result

    if output:
        import shutil
        shutil.copy(image_path, output)
        print(f"Saved: {output}")
    else:
        print(f"Generated: {image_path}")

    return image_path


def cmd_models():
    """List available chat models"""
    print("Available chat models:")
    for m in CHAT_MODELS:
        default = " (default)" if m == DEFAULT_CHAT_MODEL else ""
        print(f"  {m}{default}")
    print("\nUsage: hf-space.py chat 'prompt' --model <model-id>")


def cmd_info(space_id):
    """Show available endpoints for a Space"""
    token = get_token()
    try:
        client = Client(space_id, token=token)
    except:
        client = Client(space_id)

    print(f"Space: {space_id}")
    print(f"URL: {client.src}")
    print("\nUse view_api() for detailed info:")
    client.view_api(print_info=True)


def cmd_call(space_id, api_name, *args):
    """Call any Space endpoint directly"""
    token = get_token()
    try:
        client = Client(space_id, token=token)
    except:
        client = Client(space_id)

    # Parse args as JSON if possible
    parsed_args = []
    for arg in args:
        try:
            parsed_args.append(json.loads(arg))
        except:
            parsed_args.append(arg)

    result = client.predict(*parsed_args, api_name=api_name)

    if isinstance(result, str):
        print(result)
    else:
        print(json.dumps(result, indent=2, default=str))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "chat":
        if len(sys.argv) < 3:
            print("Usage: hf-space.py chat <prompt> [--model <model-id>]")
            sys.exit(1)
        prompt = sys.argv[2]
        model = None
        if "--model" in sys.argv:
            idx = sys.argv.index("--model")
            if idx + 1 < len(sys.argv):
                model = sys.argv[idx + 1]
        cmd_chat(prompt, model)

    elif cmd == "image":
        if len(sys.argv) < 3:
            print("Usage: hf-space.py image <prompt> [output-path]")
            sys.exit(1)
        prompt = sys.argv[2]
        output = sys.argv[3] if len(sys.argv) > 3 else None
        cmd_image(prompt, output)

    elif cmd == "models":
        cmd_models()

    elif cmd == "info":
        if len(sys.argv) < 3:
            print("Usage: hf-space.py info <space-id>")
            sys.exit(1)
        cmd_info(sys.argv[2])

    elif cmd == "call":
        if len(sys.argv) < 4:
            print("Usage: hf-space.py call <space-id> <api-name> [args...]")
            sys.exit(1)
        cmd_call(sys.argv[2], sys.argv[3], *sys.argv[4:])

    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
