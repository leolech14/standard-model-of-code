#!/usr/bin/env python3
"""
HuggingFace Spaces API Tool
===========================
Direct API access to HuggingFace Spaces via gradio_client.

Usage:
    python hf_spaces.py generate "a cute robot" --output /tmp/robot.webp
    python hf_spaces.py generate "sunset over ocean" --model flux-dev --size 1024
    python hf_spaces.py transcribe audio.wav
    python hf_spaces.py list-spaces

Requires:
    pip install gradio_client huggingface_hub

Environment:
    HF_TOKEN or uses Doppler: ai-tools/dev/HF_TOKEN
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime

def get_hf_token():
    """Get HF token from env or Doppler."""
    token = os.environ.get("HF_TOKEN")
    if token:
        return token

    # Try Doppler
    try:
        result = subprocess.run(
            ["doppler", "secrets", "get", "HF_TOKEN", "--plain",
             "--project", "ai-tools", "--config", "dev"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass

    # Fallback to hardcoded (from mcp.json)
    return "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"


# Available models
MODELS = {
    "flux": {
        "space": "black-forest-labs/FLUX.1-schnell",
        "api": "/infer",
        "params": {"num_inference_steps": 4},
        "description": "Fast image generation (~10s)"
    },
    "flux-dev": {
        "space": "black-forest-labs/FLUX.1-dev",
        "api": "/infer",
        "params": {"num_inference_steps": 28, "guidance_scale": 3.5},
        "description": "Higher quality (~30s)"
    },
    "sd35": {
        "space": "stabilityai/stable-diffusion-3.5-large",
        "api": "/infer",
        "params": {"num_inference_steps": 28, "guidance_scale": 4.5},
        "description": "Stable Diffusion 3.5 Large"
    },
    "whisper": {
        "space": "hf-audio/whisper-large-v3-turbo",
        "api": "/transcribe",
        "description": "Audio transcription"
    }
}


def generate_image(prompt: str, model: str = "flux", width: int = 768,
                   height: int = 768, seed: int = None, output: str = None) -> str:
    """Generate an image using HuggingFace Spaces."""
    from gradio_client import Client
    import huggingface_hub

    token = get_hf_token()
    huggingface_hub.login(token=token, add_to_git_credential=False)

    if model not in MODELS:
        raise ValueError(f"Unknown model: {model}. Available: {list(MODELS.keys())}")

    config = MODELS[model]

    print(f"[HF Spaces] Model: {model} ({config['space']})")
    print(f"[HF Spaces] Prompt: {prompt[:80]}...")

    client = Client(config["space"], verbose=False)

    # Build params
    params = {
        "prompt": prompt,
        "width": width,
        "height": height,
        "seed": seed or int(time.time()) % 10000,
        "randomize_seed": seed is None,
        **config.get("params", {})
    }

    # Add negative prompt for SD
    if "sd" in model:
        params["negative_prompt"] = "ugly, blurry, low quality, distorted"

    start = time.time()
    result = client.predict(**params, api_name=config["api"])
    elapsed = time.time() - start

    # Extract image path
    if isinstance(result, tuple):
        img_path = result[0]
    elif isinstance(result, dict):
        img_path = result.get('path', result)
    else:
        img_path = result

    # Copy to output location
    if output:
        import shutil
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(img_path, output_path)
        img_path = str(output_path)

    print(f"[HF Spaces] Generated in {elapsed:.1f}s")
    print(f"[HF Spaces] Output: {img_path}")

    return img_path


def transcribe_audio(audio_path: str) -> str:
    """Transcribe audio using Whisper."""
    from gradio_client import Client
    import huggingface_hub

    token = get_hf_token()
    huggingface_hub.login(token=token, add_to_git_credential=False)

    config = MODELS["whisper"]

    print(f"[HF Spaces] Transcribing: {audio_path}")

    client = Client(config["space"], verbose=False)

    start = time.time()
    result = client.predict(audio_path, api_name=config["api"])
    elapsed = time.time() - start

    print(f"[HF Spaces] Transcribed in {elapsed:.1f}s")

    return result


def list_spaces():
    """List available models/spaces."""
    print("\nAvailable HuggingFace Spaces:")
    print("-" * 60)
    for name, config in MODELS.items():
        print(f"  {name:12} - {config['description']}")
        print(f"               Space: {config['space']}")
    print()


def main():
    parser = argparse.ArgumentParser(description="HuggingFace Spaces API Tool")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Generate command
    gen = subparsers.add_parser("generate", help="Generate an image")
    gen.add_argument("prompt", help="Image prompt")
    gen.add_argument("--model", "-m", default="flux", choices=list(MODELS.keys()),
                     help="Model to use (default: flux)")
    gen.add_argument("--width", "-W", type=int, default=768)
    gen.add_argument("--height", "-H", type=int, default=768)
    gen.add_argument("--seed", "-s", type=int, help="Random seed")
    gen.add_argument("--output", "-o", help="Output path")

    # Transcribe command
    trans = subparsers.add_parser("transcribe", help="Transcribe audio")
    trans.add_argument("audio", help="Audio file path")

    # List command
    subparsers.add_parser("list-spaces", help="List available spaces")

    args = parser.parse_args()

    if args.command == "generate":
        output = args.output
        if not output:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output = f"/tmp/hf_gen_{timestamp}.webp"
        generate_image(args.prompt, args.model, args.width, args.height,
                      args.seed, output)
    elif args.command == "transcribe":
        result = transcribe_audio(args.audio)
        print(f"\nTranscription:\n{result}")
    elif args.command == "list-spaces":
        list_spaces()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
