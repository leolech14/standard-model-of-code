"""
Pipeline Booster Providers

Cloud compute provider integrations.
"""

from typing import List, Optional, Dict, Any
from ..core import ComputeBackend


PROVIDER_INFO = {
    ComputeBackend.LOCAL: {
        "name": "Local",
        "setup": "No setup required",
        "cost": "Free",
        "speed": "Depends on hardware",
    },
    ComputeBackend.MODAL: {
        "name": "Modal",
        "setup": "pip install modal && modal setup",
        "cost": "$0.001/sec GPU",
        "speed": "Fast - A100 available",
        "easiest": True,
    },
    ComputeBackend.RUNPOD: {
        "name": "RunPod",
        "setup": "pip install runpod",
        "cost": "$0.30/hr RTX 4090",
        "speed": "Fast - cheap GPUs",
    },
    ComputeBackend.GCP: {
        "name": "Google Cloud Platform",
        "setup": "gcloud auth application-default login",
        "cost": "$1-4/hr A100",
        "speed": "Fast - enterprise",
    },
}


def list_providers() -> List[Dict[str, Any]]:
    """List all available providers with info."""
    return [
        {"backend": k.value, **v}
        for k, v in PROVIDER_INFO.items()
    ]


def get_provider(backend: str) -> Optional[Dict[str, Any]]:
    """Get info for a specific provider."""
    try:
        backend_enum = ComputeBackend(backend.lower())
        return {"backend": backend_enum.value, **PROVIDER_INFO.get(backend_enum, {})}
    except ValueError:
        return None


def check_provider_available(backend: ComputeBackend) -> bool:
    """Check if a provider is configured and available."""
    import os

    if backend == ComputeBackend.LOCAL:
        return True

    if backend == ComputeBackend.MODAL:
        try:
            import modal
            return bool(os.environ.get("MODAL_TOKEN_ID"))
        except ImportError:
            return False

    if backend == ComputeBackend.RUNPOD:
        return bool(os.environ.get("RUNPOD_API_KEY"))

    if backend == ComputeBackend.GCP:
        return bool(
            os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or
            os.environ.get("GOOGLE_CLOUD_PROJECT")
        )

    return False


def get_recommended_provider() -> ComputeBackend:
    """Get the recommended provider based on what's available."""

    # Priority: Modal > RunPod > GCP > Local
    if check_provider_available(ComputeBackend.MODAL):
        return ComputeBackend.MODAL

    if check_provider_available(ComputeBackend.RUNPOD):
        return ComputeBackend.RUNPOD

    if check_provider_available(ComputeBackend.GCP):
        return ComputeBackend.GCP

    return ComputeBackend.LOCAL


def setup_instructions(backend: ComputeBackend) -> str:
    """Get setup instructions for a provider."""

    instructions = {
        ComputeBackend.LOCAL: """
# Local Setup (No action needed)
Your local CPU/GPU will be used automatically.

# To enable local GPU:
pip install torch  # For CUDA/MPS support
""",

        ComputeBackend.MODAL: """
# Modal Setup (Easiest - 2 minutes)

1. Install Modal:
   pip install modal

2. Authenticate:
   modal setup
   # Opens browser to log in

3. Done! Your functions will now run on Modal's GPUs.

# Pricing: ~$0.001/second for GPU compute
# First $30/month is free
""",

        ComputeBackend.RUNPOD: """
# RunPod Setup

1. Create account at runpod.io

2. Get API key from Settings > API Keys

3. Set environment variable:
   export RUNPOD_API_KEY="your-key"

4. Install SDK:
   pip install runpod

# Pricing: ~$0.30/hr for RTX 4090
""",

        ComputeBackend.GCP: """
# Google Cloud Platform Setup

1. Install gcloud CLI:
   brew install google-cloud-sdk

2. Authenticate:
   gcloud auth application-default login

3. Set project:
   export GOOGLE_CLOUD_PROJECT="your-project-id"

4. Enable APIs:
   gcloud services enable compute.googleapis.com

# Pricing: ~$1-4/hr for A100
""",
    }

    return instructions.get(backend, "No instructions available")
