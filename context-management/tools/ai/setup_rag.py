#!/usr/bin/env python3
"""
RAG SETUP & DATA CONSOLIDATION TOOL
===================================
"The Big Guns" - Automating the Knowledge Infrastructure.

Usage:
    python setup_rag.py [command]

Commands:
    init-rag        - Sets up (or guides setup of) Vertex AI Agent Builder
    bundle-docs     - Creates a optimized zip for NotebookLM upload
    check-health    - Verifies RAG APIs are enabled

Dependencies:
    pip install google-cloud-discoveryengine (Optional, falls back to gcloud)
"""

import os
import sys
import shutil
import subprocess
import zipfile
from pathlib import Path
from datetime import datetime

# --- Configuration ---
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
DOCS_DIR = PROJECT_ROOT / "context-management/docs"
OUTPUT_DIR = PROJECT_ROOT / "context-management/output"
CONFIG_FILE = PROJECT_ROOT / "context-management/tools/archive/config.yaml"

def run_cmd(args, check=True):
    try:
        return subprocess.run(args, check=check, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        print(f"Stderr: {e.stderr}")
        return None

def get_project_id():
    res = run_cmd(["gcloud", "config", "get-value", "project"])
    if res and res.stdout.strip():
        return res.stdout.strip()
    return None

def bundle_docs():
    """Bundles all documentation into a clean zip for NotebookLM."""
    print("="*50)
    print("BUNDLING FOR NOTEBOOK LM")
    print("="*50)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = OUTPUT_DIR / f"notebooklm_bundle_{timestamp}.zip"
    
    print(f"Source: {DOCS_DIR}")
    
    file_count = 0
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(DOCS_DIR):
            for file in files:
                if file.endswith('.md') or file.endswith('.pdf') or file.endswith('.png'):
                    full_path = Path(root) / file
                    rel_path = full_path.relative_to(DOCS_DIR)
                    zipf.write(full_path, arcname=str(rel_path))
                    file_count += 1
                    print(f"  Added: {rel_path}")
    
    print("-" * 50)
    print(f"Bundle created: {zip_path}")
    print(f"Total files: {file_count}")
    print("\nNEXT STEP: Go to https://notebooklm.google.com/ and drag this file in.")

def check_health():
    """Checks if necessary APIs are valid."""
    print("="*50)
    print("RAG HEALTH CHECK")
    print("="*50)
    
    project_id = get_project_id()
    if not project_id:
        print("x gcloud project not set. Run 'gcloud config set project <ID>'")
        return
        
    print(f"Project: {project_id}")
    
    # Check Discovery Engine API
    print("Checking Discovery Engine API...")
    res = run_cmd(["gcloud", "services", "list", "--enabled", "--filter=name:discoveryengine.googleapis.com"])
    if res and "discoveryengine.googleapis.com" in res.stdout:
        print("  [OK] Discovery Engine API is enabled.")
    else:
        print("  [MISSING] Discovery Engine API not enabled.")
        print("  Run: gcloud services enable discoveryengine.googleapis.com")

def init_rag():
    """Guides the user through RAG setup."""
    print("="*50)
    print("INITIATING 'THE LIBRARIAN' (Agent Builder)")
    print("="*50)
    
    project_id = get_project_id()
    if not project_id:
        print("Error: No project ID detected.")
        return

    print("This process sets up a Search App connected to your GCS Mirror.")
    
    bucket = "gs://elements-archive-2026/repository_mirror/latest"
    print(f"Target Bucket: {bucket}")
    
    # We use gcloud instructions because the Python SDK for creating Engines is complex 
    # and often requires specific IAM roles that might be missing tailored permissions.
    
    print("\n--- AUTOMATED INSTRUCTIONS ---\n")
    print("1. Enable the API (if not already done):")
    print(f"   gcloud services enable discoveryengine.googleapis.com --project={project_id}")
    print("\n2. Create the Data Store (Run this command):")
    print("   (Note: Use the Console for the best experience, but here is the CLI flow)")
    print(f"   https://console.cloud.google.com/gen-app-builder/data-stores?project={project_id}")
    
    print("\n--- WHY CONSOLE? ---")
    print("Creating RAG indices strictly via CLI is currently in Beta and flakey.")
    print("The Console provides a visual confirmation that the indexing is happening.")
    print("\nSteps to follow in Console:")
    print("1. Click 'Create Data Store' -> 'Cloud Storage'")
    print(f"2. Folder path: {bucket}")
    print("3. Data Type: 'Unstructured documents'")
    print("4. Name: 'elements-codebase'")
    print("5. After creation, create a 'Search' App and link this store.")
    
    print("\nOnce done, you can query it via API or the Widget.")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
        
    cmd = sys.argv[1]
    if cmd == "bundle-docs":
        bundle_docs()
    elif cmd == "check-health":
        check_health()
    elif cmd == "init-rag":
        init_rag()
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
