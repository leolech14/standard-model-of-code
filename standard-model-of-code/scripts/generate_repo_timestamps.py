#!/usr/bin/env python3
"""
TIMESTAMP GENERATOR
===================
Generates project_elements_file_timestamps.csv with file birth and modification times.

Usage:
    python generate_repo_timestamps.py [--output PATH]

Schema (matches historical format expected by timestamps.py, archive_stale.py):
    path, size_bytes, birth_epoch, birth_iso, modified_epoch, modified_iso

Note: Uses st_birthtime on macOS for true file creation time.
"""
import os
import csv
import sys
import argparse
from datetime import datetime
from pathlib import Path

# Directories to skip entirely
SKIP_DIRS = {
    '.git',
    'node_modules',
    '__pycache__',
    '.venv',
    'venv',
    '.archive',
    '.collider_report',
    '.eval',
    '.mypy_cache',
    '.pytest_cache',
    '.ruff_cache',
}

# File patterns to skip
SKIP_FILES = {
    '.DS_Store',
    '.gitkeep',
    'Thumbs.db',
    'desktop.ini',
}

# Extensions to skip (compiled/binary)
SKIP_EXTENSIONS = {
    '.pyc',
    '.pyo',
    '.so',
    '.dylib',
    '.whl',
}


def get_file_info(filepath):
    """Get size and timestamp info for a file.
    
    Returns tuple: (size_bytes, birth_epoch, birth_iso, modified_epoch, modified_iso)
    Uses st_birthtime on macOS for true creation time (falls back to st_ctime).
    """
    try:
        stat = os.stat(filepath)
        size_bytes = stat.st_size
        
        # macOS provides st_birthtime for true file creation
        if hasattr(stat, 'st_birthtime'):
            birth_epoch = int(stat.st_birthtime)
        else:
            birth_epoch = int(stat.st_ctime)  # Fallback for Linux
            
        birth_iso = datetime.fromtimestamp(birth_epoch).isoformat()
        modified_epoch = int(stat.st_mtime)
        modified_iso = datetime.fromtimestamp(modified_epoch).isoformat()
        return size_bytes, birth_epoch, birth_iso, modified_epoch, modified_iso
    except Exception:
        return None


def should_skip_file(name, filepath):
    """Check if a file should be skipped."""
    if name in SKIP_FILES:
        return True
    if name.startswith('.'):
        return True
    ext = Path(filepath).suffix.lower()
    if ext in SKIP_EXTENSIONS:
        return True
    return False


def main():
    parser = argparse.ArgumentParser(description='Generate file timestamp CSV')
    parser.add_argument('--output', '-o', type=str, default=None,
                        help='Output CSV path (default: project root)')
    args = parser.parse_args()
    
    # Determine repo root (script is in standard-model-of-code/scripts/)
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent.parent  # Up two levels
    
    if args.output:
        output_file = Path(args.output)
    else:
        output_file = repo_root / "project_elements_file_timestamps.csv"
    
    print(f"Scanning {repo_root}...")
    
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Schema matches historical format
        writer.writerow(['path', 'size_bytes', 'birth_epoch', 'birth_iso', 'modified_epoch', 'modified_iso'])
        
        file_count = 0
        for root, dirs, files in os.walk(repo_root):
            # Filter directories in-place
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
                
            for name in files:
                filepath = os.path.join(root, name)
                
                if should_skip_file(name, filepath):
                    continue
                    
                info = get_file_info(filepath)
                if info:
                    row = [filepath] + list(info)
                    writer.writerow(row)
                    file_count += 1
                    
    print(f"Done. Wrote {file_count} files to {output_file}")


if __name__ == "__main__":
    main()
