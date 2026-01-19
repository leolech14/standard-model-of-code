#!/usr/bin/env python3
"""
Professional Code Analysis Tool
===============================
Leverages Google Cloud Vertex AI (Gemini Models) to analyze the mirrored codebase.
Features:
- Reads directly from GCS Mirror (no local download).
- Cost-aware: Estimates tokens before running.
- Flexible: Supports file patterns, directory filtering.
- Models: Gemini 1.5 Pro (Deep Reasoning) or Gemini 2.0 Flash (Fast/Cheap).

Usage:
  python tools/ai/analyze.py "Explain the architecture of the archive tool"
  python tools/ai/analyze.py --dir tools/archive "How does file discovery work?"
  python tools/ai/analyze.py --files "README.md,implementation_plan.md" "Summarize status"
"""

import argparse
import sys
import yaml
import fnmatch
import time
import random
from pathlib import Path
from google import genai
from google.genai.types import Part
import subprocess
import json

# --- Config & Setup ---
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
CONFIG_PATH = PROJECT_ROOT / "context-management/tools/archive/config.yaml"
SETS_CONFIG_PATH = PROJECT_ROOT / "context-management/config/analysis_sets.yaml"

# Pricing Estimates (USD per 1M tokens) - approximate
PRICING = {
    "gemini-2.0-flash-001": {"input": 0.10, "output": 0.40},
    "gemini-2.5-pro":       {"input": 1.25, "output": 5.00},
    "gemini-1.5-pro-001":   {"input": 1.25, "output": 5.00},
    "gemini-1.5-pro-002":   {"input": 1.25, "output": 5.00}
}
DEFAULT_MODEL = "gemini-2.0-flash-001"  # 1M context, works with current quotas

def load_config():
    if not CONFIG_PATH.exists():
        print("Error: config.yaml not found.")
        sys.exit(1)
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)

def load_sets_config():
    if not SETS_CONFIG_PATH.exists():
        # Fallback if config is missing
        return {}
    with open(SETS_CONFIG_PATH) as f:
        return yaml.safe_load(f)

def get_gcloud_project():
    try:
        res = subprocess.run(["gcloud", "config", "get-value", "project"], capture_output=True, text=True)
        return res.stdout.strip()
    except Exception:
        return None

def get_access_token():
    try:
        res = subprocess.run(["gcloud", "auth", "print-access-token"], capture_output=True, text=True)
        return res.stdout.strip()
    except Exception:
        return None

def list_gcs_files(bucket, prefix):
    """List all files in the mirror latest directory."""
    try:
        cmd = ["gcloud", "storage", "ls", "-r", f"{bucket}/{prefix}/latest/**"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        files = []
        for line in res.stdout.splitlines():
            if line.endswith(":"): continue 
            if line.strip().endswith("/"): continue
            files.append(line.strip())
        return files
    except Exception as e:
        print(f"Error listing GCS files: {e}")
        return []

def filter_files(all_files, patterns=None, base_uri=""):
    """Filter GCS URIs based on patterns."""
    if not patterns:
        return all_files
    
    # patterns should be matched against relative paths
    filtered = []
    for f in all_files:
        if f.endswith(('.zip', '.png', '.jpg', '.jpeg', '.csv', '.lock', 'package-lock.json')):
            continue
        rel_path = f.replace(base_uri + "/", "")
        for pat in patterns:
            if fnmatch.fnmatch(rel_path, pat):
                filtered.append(f)
                break
    return filtered

def estimate_cost(token_count, model):
    rates = PRICING.get(model, PRICING[DEFAULT_MODEL])
    cost = (token_count / 1_000_000) * rates["input"]
    return cost


def retry_with_backoff(func, max_retries=5, base_delay=1.0):
    """Execute function with exponential backoff on rate limit errors."""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            error_str = str(e).lower()
            is_rate_limit = any(x in error_str for x in ['429', 'rate limit', 'quota', 'resource exhausted'])

            if not is_rate_limit or attempt == max_retries - 1:
                raise  # Re-raise if not a rate limit error or last attempt

            # Exponential backoff with jitter
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            print(f"  Rate limited. Retrying in {delay:.1f}s (attempt {attempt + 1}/{max_retries})...")
            time.sleep(delay)

    raise Exception("Max retries exceeded")


# --- System Prompts & Modes ---
MODES = {
    "standard": {
        "prompt": "You are a senior software engineer. Analyze the provided codebase context and answer the user's request."
    },
    "forensic": {
        "prompt": """
You are a FORENSIC CODE ANALYST. Your goal is to provide precise, verifiable facts about the codebase.
RULES:
1. For every claim you make, you MUST cite the specific file path and line numbers.
2. Format citations as: `[path/to/file.py:L10-L15]`
3. Do not generalize. If you cannot find the specific implementation, state "Evidence not found in provided context."
4. Quote the exact code snippet when relevant.
"""
    },
    "architect": {
        "prompt": """
You are the CHIEF ARCHITECT of the 'Standard Model of Code' project.
Your analysis must be grounded in the project's theoretical framework (Atoms, Rings, Tiers, RPBL).
RULES:
1. Use the terminology defined in `metadata/COLLIDER_ARCHITECTURE.md` (e.g., "The UnifiedNode layer...", "The RPBL classification...").
2. Connect implementation details to the architectural vision.
3. Identify topological structures (knots, cycles, layers).
"""
    }
}

def main():
    parser = argparse.ArgumentParser(description="Analyze codebase with Vertex AI")
    parser.add_argument("prompt", help="The question or instruction for the AI")
    parser.add_argument("--dir", help="Filter by directory (e.g., 'tools/archive')")
    parser.add_argument("--file", help="Specific file(s) to include (comma separated)")
    parser.add_argument("--set", help="Analysis Set (brain, body, theory, legacy)")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Model to use")
    parser.add_argument("--mode", default="standard", choices=MODES.keys(), help="Analysis mode: standard, forensic (line-level), or architect (theory-aware)")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip cost confirmation")
    args = parser.parse_args()

    # 1. Config & Auth
    config = load_config()
    bucket_url = config.get("mirror", {}).get("bucket")
    prefix = config.get("mirror", {}).get("prefix", "repository_mirror")
    mirror_base = f"{bucket_url}/{prefix}/latest"
    
    project_id = get_gcloud_project()
    if not project_id:
        print("Error: No gcloud project set.")
        sys.exit(1)

    print(f"Project: {project_id}")
    print(f"Model:   {args.model}")
    print(f"Mode:    {args.mode.upper()}")
    print("Fetching file list from Mirror...")

    # 2. File Selection
    all_files = list_gcs_files(bucket_url, prefix)
    selected_files = []
    
    if args.file:
        targets = args.file.split(",")
        selected_files = filter_files(all_files, targets, mirror_base)
    elif args.dir:
        selected_files = filter_files(all_files, [f"{args.dir}*"], mirror_base)
    elif args.set:
        sets_config = load_sets_config()
        analysis_sets = sets_config.get("analysis_sets", {})
        if args.set not in analysis_sets:
            print(f"Error: Unknown set '{args.set}'. Available: {list(analysis_sets.keys())}")
            sys.exit(1)
        
        print(f"Using Analysis Set: {args.set.upper()}")
        print(f"  {analysis_sets[args.set]['description']}")
        selected_files = filter_files(all_files, analysis_sets[args.set]['patterns'], mirror_base)
    else:
        # Default: Important docs and root files if no filter
        # In 'architect' mode, we MUST include the architecture docs
        defaults = ["README.md", "implementation_plan.md", "docs/*.md", "tools/*.py"]
        selected_files = filter_files(all_files, defaults, mirror_base)

    if args.mode == "architect":
        # Ensure architecture definitions are included
        arch_docs = filter_files(all_files, ["*COLLIDER_ARCHITECTURE.md", "*THEORY.md"], mirror_base)
        for d in arch_docs:
            if d not in selected_files:
                selected_files.insert(0, d) # High priority

    if not selected_files:
        print("No files matched your criteria.")
        sys.exit(1)

    print(f"\nSelected {len(selected_files)} files for context:")
    for f in selected_files[:5]:
        print(f" - {f.replace(mirror_base, '')}")
    if len(selected_files) > 5:
        print(f" ... and {len(selected_files)-5} more")

    # 3. Cost Estimation
    print(f"\nSending files from: {mirror_base}")
    if not args.yes:
        confirm = input("\nProceed with analysis? [Y/n] ")
        if confirm.lower() == 'n':
            sys.exit(0)

    # 4. Execution
    access_token = get_access_token()
    if not access_token:
        print("Error: Could not get access token.")
        print("Run: gcloud auth application-default login")
        sys.exit(1)

    from google.oauth2 import credentials as oauth2_credentials
    creds = oauth2_credentials.Credentials(token=access_token)
    
    client = genai.Client(
        vertexai=True, project=project_id, location="us-central1", credentials=creds
    )

    contents = [Part.from_uri(file_uri=f, mime_type="text/plain") for f in selected_files]
    
    # Inject Mode-Specific System Prompt
    full_prompt = f"{MODES[args.mode]['prompt']}\n\nUSER QUERY: {args.prompt}"
    contents.append(Part.from_text(text=full_prompt))

    print("\n--- Analyzing ---")
    try:
        # Wrap API call with retry logic for rate limits
        def make_request():
            return client.models.generate_content(
                model=args.model,
                contents=contents
            )

        response = retry_with_backoff(make_request)
        print(response.text)
        print("\n-----------------")
        if response.usage_metadata:
            print(f"Tokens Used: {response.usage_metadata.prompt_token_count} Input, {response.usage_metadata.candidates_token_count} Output")
            est = estimate_cost(response.usage_metadata.prompt_token_count, args.model)
            print(f"Estimated Cost: ${est:.4f}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
