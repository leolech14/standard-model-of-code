#!/usr/bin/env python3
"""
GEMINI CONTEXT CACHING DEMO
===========================
Demonstrates how to use Google Gemini 2.0 Flash to analyze the mirrored codebase
directly from Google Cloud Storage without downloading it.

Usage:
    ../.tools_venv/bin/python gemini_cache_demo.py

Prerequisites:
    - virtual environment with google-cloud-aiplatform, google-generativeai
    - GCS mirror populated (tools/archive/archive.py mirror)
"""

import subprocess
import sys
import yaml
from pathlib import Path
from google import genai
from google.genai.types import Part

# Configuration
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
CONFIG_FILE = PROJECT_ROOT / "tools" / "archive" / "config.yaml"

def load_config():
    with open(CONFIG_FILE) as f:
        return yaml.safe_load(f)

def get_gcloud_project():
    try:
        res = subprocess.run(["gcloud", "config", "get-value", "project"], capture_output=True, text=True)
        return res.stdout.strip()
    except Exception:
        return None

def get_access_token():
    """Get access token from gcloud CLI (more reliable than ADC)."""
    try:
        res = subprocess.run(["gcloud", "auth", "print-access-token"], capture_output=True, text=True)
        return res.stdout.strip()
    except Exception:
        return None

def main():
    print("=== GEMINI CONTEXT CACHING DEMO ===")

    # 1. Setup
    config = load_config()
    bucket_url = config.get("mirror", {}).get("bucket")
    prefix = config.get("mirror", {}).get("prefix", "repository_mirror")

    if not bucket_url:
        print("Error: Mirror bucket not found in config.yaml")
        sys.exit(1)

    project_id = get_gcloud_project()
    if not project_id:
        print("Error: Could not detect Google Cloud Project ID.")
        print("Run: gcloud config set project <YOUR_PROJECT_ID>")
        sys.exit(1)

    print(f"Project: {project_id}")
    print(f"Bucket:  {bucket_url}")
    print("Location: us-central1 (Vertex AI default)")

    # Get access token from gcloud
    access_token = get_access_token()
    if not access_token:
        print("Error: Could not get access token. Run: gcloud auth login")
        sys.exit(1)

    # Initialize client with explicit credentials
    from google.oauth2 import credentials as oauth2_credentials
    creds = oauth2_credentials.Credentials(token=access_token)
    
    client = genai.Client(
        vertexai=True,
        project=project_id,
        location="us-central1",
        credentials=creds
    )

    # 2. Select Files for Analysis
    print("\nSelecting key context files...")

    files_to_index = [
        f"{bucket_url}/{prefix}/latest/README.md",
        f"{bucket_url}/{prefix}/latest/tools/archive/archive.py",
        f"{bucket_url}/{prefix}/latest/docs/TIMELINE_ANALYSIS.md",
        f"{bucket_url}/{prefix}/latest/AGENT_KERNEL.md"
    ]

    for f in files_to_index:
        print(f" - {f}")

    # 3. Build content with GCS file references
    print("\nConnecting to Gemini 2.0 Flash...")

    prompt = """
    You are an expert software architect.
    I am providing you with the README, the implementation plan, and the core 'archive.py' tool of this project.

    Based on these files:
    1. Summarize the purpose of the 'Repository Mirror' feature.
    2. Explain how the 'archive.py' script handles file discovery (git vs fallback).
    3. Suggest one improvement for the archive tool based on the code provided.
    """

    # 4. Generate Content
    print("\nSending prompt to Vertex AI (this reads files directly from GCS)...")

    # Build parts with GCS URIs
    contents = [Part.from_uri(file_uri=f, mime_type="text/plain") for f in files_to_index]
    contents.append(Part.from_text(text=prompt))

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=contents
        )
        print("\n=== GEMINI RESPONSE ===\n")
        print(response.text)
        print("\n=======================")
        print(f"\nUsage: {response.usage_metadata}")

    except Exception as e:
        print(f"\nError interacting with Gemini: {e}")
        print("\nTroubleshooting:")
        print("1. Run: gcloud auth login")
        print("2. Ensure Vertex AI API is enabled")
        print("3. Ensure account has 'Vertex AI User' role")

if __name__ == "__main__":
    main()
