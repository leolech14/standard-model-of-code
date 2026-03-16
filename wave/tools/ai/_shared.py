"""
Shared utilities for wave/tools/ai/ ecosystem.

Extracted from analyze.py to break the os.execv() venv bootstrap dependency.
This module has ZERO side effects on import -- no process replacement, no
interactive prompts. If the venv is wrong, imports fail cleanly via ImportError.

Foundation for: socratic/, future ACI Router extraction, Research Engine extraction.
"""

import json
import os
import random
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# --- Path constants ---
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
SETS_CONFIG_PATH = PROJECT_ROOT / "wave/config/analysis_sets.yaml"
PROMPTS_CONFIG_PATH = PROJECT_ROOT / "wave/config/prompts.yaml"
SEMANTIC_MODELS_PATH = PROJECT_ROOT / "wave/config/semantic_models.yaml"

# --- Config loading ---
def _load_prompts_config() -> dict:
    """Load prompts.yaml for model names, pricing, modes."""
    if PROMPTS_CONFIG_PATH.exists():
        with open(PROMPTS_CONFIG_PATH) as f:
            return yaml.safe_load(f) or {}
    return {}

_PROMPTS = _load_prompts_config()

# Model selection
DEFAULT_MODEL = _PROMPTS.get("default_model", "gemini-3-pro-preview")
FAST_MODEL = _PROMPTS.get("fast_model", "gemini-2.0-flash-001")
FALLBACK_MODELS = _PROMPTS.get("fallback_models", [])
PRICING = _PROMPTS.get("pricing", {})
MODES = _PROMPTS.get("modes", {})

# Backend selection
GEMINI_API_KEY_ENV = _PROMPTS.get("api_key_env", "GEMINI_API_KEY")
_GEMINI_BACKEND_ENV = os.environ.get("GEMINI_BACKEND", "")
BACKEND = _GEMINI_BACKEND_ENV or _PROMPTS.get("backend", "aistudio")


# --- Doppler / secrets ---
def _find_doppler() -> str:
    """Find doppler executable in PATH or common locations."""
    import shutil
    if shutil.which("doppler"):
        return "doppler"
    candidates = [
        os.path.expanduser("~/.local/bin/doppler"),
        "/usr/local/bin/doppler",
        "/opt/homebrew/bin/doppler",
        "/usr/bin/doppler",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return "doppler"


def get_doppler_secret(key: str) -> Optional[str]:
    """Fetch a secret from Doppler. Returns None if unavailable."""
    try:
        doppler_exe = _find_doppler()
        result = subprocess.run(
            [doppler_exe, "secrets", "get", key, "--plain"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


# --- Gemini clients ---
try:
    from google import genai
    from google.genai.types import Part
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False
    genai = None
    Part = None


def get_gcloud_project() -> Optional[str]:
    try:
        res = subprocess.run(
            ["gcloud", "config", "get-value", "project"],
            capture_output=True, text=True,
        )
        return res.stdout.strip() if res.returncode == 0 else None
    except Exception:
        return None


def get_access_token() -> Optional[str]:
    try:
        res = subprocess.run(
            ["gcloud", "auth", "print-access-token"],
            capture_output=True, text=True,
        )
        return res.stdout.strip() if res.returncode == 0 else None
    except Exception:
        return None


def create_client():
    """Create a Gemini client (AI Studio or Vertex AI).

    Returns (client, identifier_string) or (None, error_string).
    """
    if not HAS_GENAI:
        return None, "google-genai not installed"

    if BACKEND == "vertex":
        project = get_gcloud_project()
        if not project:
            return None, "No GCP project found"
        client = genai.Client(
            vertexai=True,
            project=project,
            location="us-central1",
        )
        return client, f"vertex:{project}"
    else:
        api_key = os.environ.get(GEMINI_API_KEY_ENV) or get_doppler_secret("GEMINI_API_KEY")
        if not api_key:
            return None, f"No API key (set {GEMINI_API_KEY_ENV} or configure Doppler)"
        client = genai.Client(api_key=api_key)
        return client, "aistudio"


def create_developer_client():
    """Create a Gemini Developer API client for File Search."""
    if not HAS_GENAI:
        return None

    api_key = get_doppler_secret("GEMINI_API_KEY")
    if not api_key:
        api_key = os.environ.get(GEMINI_API_KEY_ENV)
    if not api_key:
        print("File Search requires GEMINI_API_KEY (Doppler or env var)")
        return None

    return genai.Client(api_key=api_key)


# --- File operations ---
def read_file_content(file_path, with_line_numbers=False) -> str:
    """Read file content with UTF-8/latin-1 fallback."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
        except Exception:
            return f"[Binary or unreadable file: {file_path}]"
    except Exception as e:
        return f"[Error reading {file_path}: {e}]"

    if with_line_numbers:
        lines = content.split('\n')
        return '\n'.join(f"{i+1:4d}: {line}" for i, line in enumerate(lines))
    return content


def list_local_files(base_dir, patterns=None, user_excludes=None) -> List[Path]:
    """Walk filesystem with glob patterns and security excludes."""
    import fnmatch

    base = Path(base_dir)
    if not base.exists():
        return []

    # Security excludes
    security_excludes = {
        '.env', '.env.local', '.env.production', 'credentials.json',
        'serviceAccountKey.json', '.git', 'node_modules', '.venv',
        '__pycache__', '.tools_venv', 'venv', '.cache',
    }
    if user_excludes:
        security_excludes.update(user_excludes)

    # Extension excludes (binaries, media)
    ext_excludes = {
        '.pyc', '.pyo', '.so', '.dylib', '.o', '.a',
        '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico',
        '.woff', '.woff2', '.ttf', '.eot',
        '.zip', '.tar', '.gz', '.7z',
        '.mp4', '.mp3', '.wav', '.avi',
    }

    files = []
    for path in sorted(base.rglob('*')):
        if not path.is_file():
            continue
        parts = path.relative_to(base).parts
        if any(p in security_excludes for p in parts):
            continue
        if path.suffix in ext_excludes:
            continue
        if patterns:
            rel = str(path.relative_to(base))
            if not any(fnmatch.fnmatch(rel, p) for p in patterns):
                continue
        files.append(path)

    return files


# --- File Search / RAG ---
def list_file_search_stores(client) -> list:
    """List all File Search vector stores."""
    if not client:
        return []
    try:
        stores = list(client.file_search_stores.list())
        return stores
    except Exception:
        return []


def get_or_create_store(client, store_name: str) -> str:
    """Get existing store by name or create new one. Returns resource name."""
    stores = list_file_search_stores(client)
    existing = next((s for s in stores if s.display_name == store_name), None)
    if existing:
        return existing.name

    store = client.file_search_stores.create(display_name=store_name)
    return store.name


def index_files_to_store(client, store_name: str, files: list, base_dir: Path) -> dict:
    """Upload files to a File Search store."""
    stats = {"indexed": 0, "failed": 0, "skipped": 0, "errors": []}
    for f in files:
        if f.suffix in {'.yaml', '.yml'}:
            stats["skipped"] += 1
            continue
        try:
            rel = str(f.relative_to(base_dir))
            with open(f, 'rb') as fh:
                client.file_search_stores.upload(
                    name=store_name,
                    file=fh,
                    metadata={"display_name": rel},
                )
            stats["indexed"] += 1
        except Exception as e:
            stats["failed"] += 1
            stats["errors"].append(str(e)[:100])
    return stats


def search_with_file_search(client, store_name: str, query: str, model: str = None) -> dict:
    """Query a File Search store with citations."""
    if not client or not HAS_GENAI:
        return {"text": "", "citations": []}

    use_model = model or DEFAULT_MODEL
    try:
        response = client.models.generate_content(
            model=use_model,
            contents=query,
            config=genai.types.GenerateContentConfig(
                tools=[genai.types.Tool(
                    file_search=genai.types.FileSearch(
                        vector_store_names=[store_name]
                    )
                )]
            ),
        )
        citations = []
        for candidate in response.candidates:
            gm = getattr(candidate, 'grounding_metadata', None)
            if gm:
                for chunk in getattr(gm, 'grounding_chunks', []):
                    cite = {}
                    rc = getattr(chunk, 'retrieved_context', None)
                    if rc:
                        cite['file'] = getattr(rc, 'uri', '')
                        cite['title'] = getattr(rc, 'title', '')
                    if cite:
                        citations.append(cite)
        return {
            "text": response.text or "",
            "citations": citations,
            "usage": {
                "input_tokens": getattr(response.usage_metadata, 'prompt_token_count', 0) if response.usage_metadata else 0,
                "output_tokens": getattr(response.usage_metadata, 'candidates_token_count', 0) if response.usage_metadata else 0,
            },
        }
    except Exception as e:
        return {"text": "", "citations": [], "error": str(e)}


# --- Retry / resilience ---
def auto_diagnose_error(error_str: str) -> None:
    """Parse Gemini API errors and suggest fixes."""
    import re as _re
    print("\n  --- AUTO-DIAGNOSIS ---")
    match = _re.search(r'retry.*?(\d+\.?\d*)\s*s', error_str, _re.IGNORECASE)
    if match:
        print(f"  Retry in: {float(match.group(1)):.0f} seconds")
    if 'input_token' in error_str.lower():
        print("  Cause: Input token quota exceeded")
        print("  Fix: Use --model gemini-2.5-flash")
    elif 'quota' in error_str.lower():
        print("  Cause: Rate limit exceeded")
        print("  Fix: Wait 60s or use gemini-2.5-flash")


def retry_with_backoff(func, max_retries=5, base_delay=1.0):
    """Execute function with exponential backoff on rate limit errors."""
    last_error = None
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            last_error = e
            error_str = str(e).lower()
            is_rate_limit = any(
                x in error_str for x in ['429', 'rate limit', 'quota', 'resource exhausted']
            )
            if not is_rate_limit or attempt == max_retries - 1:
                if is_rate_limit:
                    auto_diagnose_error(str(e))
                raise
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            print(f"  Rate limited. Retrying in {delay:.1f}s ({attempt + 1}/{max_retries})...")
            time.sleep(delay)
    raise Exception("Max retries exceeded")


def estimate_cost(input_tokens: int, output_tokens: int, model: str) -> float:
    """Estimate cost in USD."""
    rates = PRICING.get(model, PRICING.get(DEFAULT_MODEL, {"input": 0.10, "output": 0.40}))
    return (input_tokens / 1_000_000) * rates.get("input", 0.10) + \
           (output_tokens / 1_000_000) * rates.get("output", 0.40)


def load_sets_config() -> dict:
    """Load analysis_sets.yaml."""
    if SETS_CONFIG_PATH.exists():
        with open(SETS_CONFIG_PATH) as f:
            return yaml.safe_load(f) or {}
    return {}
