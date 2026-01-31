#!/usr/bin/env python3
"""
Generate comprehensive file inventory for PROJECT_elements.

Output: CSV with path, extension, created, modified timestamps
"""

import os
import csv
from pathlib import Path
from datetime import datetime
from collections import Counter

PROJECT_ROOT = Path(__file__).parent.parent

# Directories to exclude
EXCLUDE_DIRS = {
    '.git', 'node_modules', '.venv', '.tools_venv', '__pycache__',
    '.pytest_cache', '.mypy_cache', 'dist', 'build', '.eggs'
}

def get_file_info(filepath: Path) -> dict:
    """Get file metadata."""
    try:
        stat = filepath.stat()
        # macOS: st_birthtime is creation time
        # Linux: st_ctime is metadata change time (fallback)
        created = getattr(stat, 'st_birthtime', stat.st_ctime)
        modified = stat.st_mtime

        return {
            'path': str(filepath.relative_to(PROJECT_ROOT)),
            'extension': filepath.suffix.lstrip('.') if filepath.suffix else '(none)',
            'created': datetime.fromtimestamp(created).strftime('%Y-%m-%d %H:%M:%S'),
            'modified': datetime.fromtimestamp(modified).strftime('%Y-%m-%d %H:%M:%S'),
            'size_bytes': stat.st_size
        }
    except (OSError, ValueError) as e:
        return None

def collect_files():
    """Walk directory and collect file info."""
    files = []

    for root, dirs, filenames in os.walk(PROJECT_ROOT):
        # Filter out excluded directories (in-place modification)
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for filename in filenames:
            filepath = Path(root) / filename
            info = get_file_info(filepath)
            if info:
                files.append(info)

    return files

def main():
    print("Scanning PROJECT_elements...")
    files = collect_files()
    print(f"Found {len(files)} files")

    # Write CSV
    output_path = PROJECT_ROOT / 'tools' / 'file_inventory.csv'
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['path', 'extension', 'created', 'modified', 'size_bytes'])
        writer.writeheader()
        writer.writerows(sorted(files, key=lambda x: x['path']))

    print(f"Written to: {output_path}")

    # Print summary statistics
    print("\n" + "=" * 60)
    print("FILE FORMAT DISTRIBUTION (Top 20)")
    print("=" * 60)
    ext_counts = Counter(f['extension'] for f in files)
    for ext, count in ext_counts.most_common(20):
        print(f"  {ext:15} {count:>6} files")

    print("\n" + "=" * 60)
    print("MOST RECENTLY MODIFIED (Top 20)")
    print("=" * 60)
    recent = sorted(files, key=lambda x: x['modified'], reverse=True)[:20]
    for f in recent:
        print(f"  {f['modified']}  {f['extension']:8}  {f['path'][:60]}")

    print("\n" + "=" * 60)
    print("DIRECTORY DISTRIBUTION (Top 15)")
    print("=" * 60)
    dir_counts = Counter(str(Path(f['path']).parent).split('/')[0] for f in files)
    for dir_name, count in dir_counts.most_common(15):
        print(f"  {dir_name:30} {count:>6} files")

    # Size summary
    total_size = sum(f['size_bytes'] for f in files)
    print(f"\nTotal size: {total_size / (1024*1024):.2f} MB")

if __name__ == '__main__':
    main()
