#!/usr/bin/env python3
"""
GENERATE METADATA CSV
=====================
Scans the entire repository and generates a detailed CSV audit of every file.
Fields: Path, Extension, SizeBytes, CreatedISO, ModifiedISO, LineCount, Category.

Usage:
    python generate_metadata_csv.py
"""

import csv
import os
import mimetypes
from datetime import datetime
from pathlib import Path

# Config
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "context-management/output"
OUTPUT_FILE = OUTPUT_DIR / "file_metadata_audit.csv"

# Categorization
CATEGORIES = {
    ".py": "Code (Python)",
    ".js": "Code (JS)",
    ".ts": "Code (TS)",
    ".md": "Documentation",
    ".json": "Data (JSON)",
    ".yaml": "Config",
    ".yml": "Config",
    ".sh": "Script",
    ".html": "Web",
    ".css": "Web",
    ".png": "Asset (Image)",
    ".jpg": "Asset (Image)",
    ".zip": "Archive",
}

def count_lines(path):
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    except:
        return 0

def scan_files():
    print(f"Scanning {PROJECT_ROOT}...")
    
    rows = []
    
    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Exclude common ignores
        if ".git" in dirs: dirs.remove(".git")
        if "__pycache__" in dirs: dirs.remove("__pycache__")
        if "node_modules" in dirs: dirs.remove("node_modules")
        if ".venv" in dirs: dirs.remove(".venv")
        if "venv" in dirs: dirs.remove("venv")
        
        for file in files:
            full_path = Path(root) / file
            rel_path = str(full_path.relative_to(PROJECT_ROOT))
            
            # Skip .DS_Store
            if file == ".DS_Store": continue

            try:
                stats = full_path.stat()
                ext = full_path.suffix.lower()
                
                # timestamps
                created = datetime.fromtimestamp(stats.st_ctime).isoformat()
                modified = datetime.fromtimestamp(stats.st_mtime).isoformat()
                
                # category
                category = CATEGORIES.get(ext, "Other")
                if "archive/" in rel_path:
                    category = "Archived/Legacy"
                
                # line count for text
                lines = 0
                if category.startswith("Code") or category == "Documentation" or category == "Config":
                    lines = count_lines(full_path)
                
                rows.append({
                    "Path": rel_path,
                    "Filename": file,
                    "Extension": ext,
                    "Category": category,
                    "SizeBytes": stats.st_size,
                    "SizeKB": round(stats.st_size / 1024, 2),
                    "LineCount": lines,
                    "Created": created,
                    "Modified": modified
                })
            except Exception as e:
                print(f"Error scanning {rel_path}: {e}")

    # Sort by path
    rows.sort(key=lambda x: x['Path'])
    return rows

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    print("Generating comprehensive metadata audit...")
    data = scan_files()
    
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        fields = ["Path", "Filename", "Extension", "Category", "SizeBytes", "SizeKB", "LineCount", "Created", "Modified"]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)
        
    print("-" * 50)
    print(f"Audit Complete. Scanned {len(data)} files.")
    print(f"Output: {OUTPUT_FILE}")
    print("-" * 50)

if __name__ == "__main__":
    main()
