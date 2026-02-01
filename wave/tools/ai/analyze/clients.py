"""
Clients Module - API Client Creation
====================================

Standard Model Classification:
-----------------------------
D1_KIND:     ORG.SVC.M (Organizational Service Module)
D2_LAYER:    Infrastructure (external API connections)
D3_ROLE:     Factory (creates client instances)
D4_BOUNDARY: I-O (network calls, subprocess for gcloud)
D5_STATE:    Stateful (clients maintain connection state)
D6_EFFECT:   Impure (network I/O, subprocess calls)
D7_LIFECYCLE: Create (initialization module)
D8_TRUST:    85 (network can fail, retries help)

RPBL: (3, 6, 7, 5)
    R=3: Multiple client types (Vertex, AI Studio, Developer)
    P=6: Network I/O with retries
    B=7: External API boundary (highest risk)
    L=5: Clients are module-lifetime

Communication Theory:
    Source:   Configuration, environment, gcloud
    Channel:  Network (HTTPS to Google APIs)
    Message:  API requests/responses
    Receiver: Gemini models
    Noise:    Rate limits, network errors, auth failures
    Redundancy: Retry with backoff, fallback models

Tool Theory:
    Universe: TOOLOME (enables analysis capability)
    Role:     T-Adapter (adapts local code to remote API)
    Stone Tool Test: FAIL (requires API, not human-usable directly)
"""

import os
import sys
import time
import random
import subprocess
from typing import Optional, Tuple, Callable, Any

# Lazy imports for google.genai (may not be available in all contexts)
_genai = None
_genai_types = None


def _ensure_genai():
    """Lazy import of google.genai module."""
    global _genai, _genai_types
    if _genai is None:
        from google import genai
        from google.genai import types
        _genai = genai
        _genai_types = types
    return _genai, _genai_types


def get_gcloud_project() -> Optional[str]:
    """Get currently configured gcloud project."""
    try:
        res = subprocess.run(
            ["gcloud", "config", "get-value", "project"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return res.stdout.strip() if res.returncode == 0 else None
    except Exception:
        return None


def get_access_token() -> Optional[str]:
    """Get gcloud access token for Vertex AI."""
    try:
        res = subprocess.run(
            ["gcloud", "auth", "print-access-token"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return res.stdout.strip() if res.returncode == 0 else None
    except Exception:
        return None


def _find_doppler() -> str:
    """Find doppler executable in PATH or common locations."""
    import shutil
    if shutil.which("doppler"):
        return "doppler"

    # Common locations on macOS/Linux
    candidates = [
        os.path.expanduser("~/.local/bin/doppler"),
        "/usr/local/bin/doppler",
        "/opt/homebrew/bin/doppler",
        "/usr/bin/doppler"
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return "doppler"


def get_doppler_secret(key: str) -> Optional[str]:
    """
    Fetch a secret from Doppler.

    Doppler is the preferred secrets manager for this project.
    Falls back to environment variables if Doppler unavailable.

    Args:
        key: Secret key name (e.g., "GEMINI_API_KEY")

    Returns:
        Secret value or None if unavailable
    """
    try:
        doppler_exe = _find_doppler()
        result = subprocess.run(
            [doppler_exe, "secrets", "get", key, "--plain"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def create_vertex_client(
    project: Optional[str] = None,
    location: str = "us-central1"
) -> Tuple[Any, str]:
    """
    Create Vertex AI client.

    Uses Application Default Credentials (ADC) - run:
        gcloud auth application-default login

    Args:
        project: GCP project ID (None = use gcloud config)
        location: GCP region

    Returns:
        Tuple of (client, project_id)

    Raises:
        RuntimeError: If authentication fails
    """
    genai, _ = _ensure_genai()

    # Get project from gcloud if not specified
    project_id = project or get_gcloud_project()
    if not project_id:
        raise RuntimeError(
            "No GCP project configured. Run: gcloud config set project <project>"
        )

    # Create Vertex client
    client = genai.Client(
        vertexai=True,
        project=project_id,
        location=location
    )

    return client, project_id


def create_developer_client(api_key: Optional[str] = None) -> Optional[Any]:
    """
    Create Gemini Developer API client.

    Required for File Search features which are not available on Vertex AI.

    Args:
        api_key: API key (None = get from Doppler/env)

    Returns:
        Client instance or None if no API key available
    """
    genai, _ = _ensure_genai()

    # Try Doppler first, then environment
    if api_key is None:
        api_key = get_doppler_secret("GEMINI_API_KEY")
        if api_key:
            print("  [Doppler] GEMINI_API_KEY loaded", file=sys.stderr)
        else:
            api_key = os.environ.get("GEMINI_API_KEY")
            if api_key:
                print("  [Env] GEMINI_API_KEY loaded", file=sys.stderr)

    if not api_key:
        print(f"\n{'='*60}", file=sys.stderr)
        print("GEMINI_API_KEY REQUIRED", file=sys.stderr)
        print(f"{'='*60}", file=sys.stderr)
        print("\nSetup Doppler (recommended):", file=sys.stderr)
        print("   doppler setup --project ai-tools --config dev", file=sys.stderr)
        print("\nOr set environment variable:", file=sys.stderr)
        print("   export GEMINI_API_KEY='your-api-key'", file=sys.stderr)
        print("\nGet API key from: https://aistudio.google.com/apikey", file=sys.stderr)
        print(f"{'='*60}\n", file=sys.stderr)
        return None

    return genai.Client(api_key=api_key)


def create_client(
    backend: str = "vertex",
    project: Optional[str] = None,
    location: str = "us-central1"
) -> Tuple[Any, str]:
    """
    Create appropriate API client based on backend configuration.

    This is the main entry point for client creation.

    Args:
        backend: "vertex" or "aistudio"
        project: GCP project (for Vertex)
        location: GCP location (for Vertex)

    Returns:
        Tuple of (client, identifier)
        For Vertex: (client, project_id)
        For AI Studio: (client, "ai-studio")

    Raises:
        RuntimeError: If client creation fails
    """
    backend = backend.lower()

    if backend == "aistudio":
        client = create_developer_client()
        if client is None:
            raise RuntimeError("Failed to create AI Studio client - no API key")
        return client, "ai-studio"

    # Default to Vertex
    return create_vertex_client(project=project, location=location)


def retry_with_backoff(
    func: Callable,
    max_retries: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 60.0
) -> Any:
    """
    Execute function with exponential backoff on failure.

    Implements the redundancy mechanism from Communication Theory -
    automatic retry compensates for transient noise (network errors,
    rate limits).

    Args:
        func: Function to execute (no arguments)
        max_retries: Maximum retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay between retries

    Returns:
        Function result

    Raises:
        Last exception if all retries fail
    """
    last_exception = None

    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            last_exception = e
            error_str = str(e).lower()

            # Check for specific error types
            if "quota" in error_str or "rate" in error_str or "429" in error_str:
                # Rate limit - definitely retry with backoff
                pass
            elif "500" in error_str or "503" in error_str or "unavailable" in error_str:
                # Server error - retry with backoff
                pass
            elif "401" in error_str or "403" in error_str or "permission" in error_str:
                # Auth error - don't retry
                raise
            elif "400" in error_str and "invalid" in error_str:
                # Invalid request - don't retry
                raise

            if attempt < max_retries - 1:
                # Calculate delay with jitter
                delay = min(base_delay * (2 ** attempt), max_delay)
                jitter = random.uniform(0, delay * 0.1)
                actual_delay = delay + jitter

                print(f"  Retry {attempt + 1}/{max_retries} after {actual_delay:.1f}s: {e}",
                      file=sys.stderr)
                time.sleep(actual_delay)

    raise last_exception


def auto_diagnose_error(error_str: str) -> None:
    """
    Diagnose common API errors and suggest fixes.

    This provides human-readable feedback for common failure modes.

    Args:
        error_str: Error message string
    """
    error_lower = error_str.lower()

    if "quota" in error_lower or "rate" in error_lower:
        print("\nDIAGNOSIS: Rate limit exceeded", file=sys.stderr)
        print("FIX: Wait a few minutes or reduce request frequency", file=sys.stderr)

    elif "permission" in error_lower or "403" in error_lower:
        print("\nDIAGNOSIS: Permission denied", file=sys.stderr)
        print("FIX: Check API is enabled and credentials have access", file=sys.stderr)

    elif "not found" in error_lower or "404" in error_lower:
        print("\nDIAGNOSIS: Resource not found", file=sys.stderr)
        print("FIX: Check model name and project configuration", file=sys.stderr)

    elif "invalid" in error_lower or "400" in error_lower:
        print("\nDIAGNOSIS: Invalid request", file=sys.stderr)
        print("FIX: Check prompt format and parameters", file=sys.stderr)

    elif "timeout" in error_lower:
        print("\nDIAGNOSIS: Request timed out", file=sys.stderr)
        print("FIX: Reduce context size or try again", file=sys.stderr)
