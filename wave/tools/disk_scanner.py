#!/usr/bin/env python3
"""
Disk Scanner: Separates gold (code/text) from bloat (media/archives/binaries).
Finds duplicates, large files, and offload candidates across all projects.
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- File Classification ---

GOLD_EXTENSIONS = {
    # Code
    '.py', '.js', '.ts', '.tsx', '.jsx', '.rs', '.go', '.java', '.rb', '.php',
    '.c', '.cpp', '.h', '.hpp', '.cs', '.swift', '.kt', '.scala', '.lua',
    '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat', '.cmd',
    '.sql', '.graphql', '.gql', '.proto',
    '.r', '.jl', '.m', '.mm', '.zig', '.nim', '.ex', '.exs', '.erl',
    # Config / Infra
    '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.env', '.envrc',
    '.json', '.jsonl', '.json5', '.ndjson',
    '.xml', '.plist', '.hcl', '.tf', '.tfvars',
    '.dockerfile', '.dockerignore', '.gitignore', '.gitattributes',
    '.editorconfig', '.prettierrc', '.eslintrc', '.stylelintrc',
    # Text / Docs
    '.md', '.mdx', '.txt', '.rst', '.adoc', '.tex', '.org',
    '.csv', '.tsv',
    '.html', '.htm', '.css', '.scss', '.sass', '.less', '.styl',
    '.svg', '.vue', '.svelte', '.astro',
    # Notebooks
    '.ipynb',
    # Lock files (small, keep)
    '.lock',
}

MEDIA_EXTENSIONS = {
    # Images
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.tif', '.webp',
    '.ico', '.icns', '.heic', '.heif', '.raw', '.cr2', '.nef', '.dng',
    '.psd', '.ai', '.sketch', '.fig', '.xd',
    # Video
    '.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.webm', '.m4v',
    '.mpg', '.mpeg', '.3gp',
    # Audio
    '.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma', '.aiff',
    '.mid', '.midi',
    # 3D
    '.glb', '.gltf', '.obj', '.fbx', '.stl', '.blend', '.dae', '.3ds',
    '.usdz', '.usda', '.usdc',
}

ARCHIVE_EXTENSIONS = {
    '.zip', '.tar', '.gz', '.bz2', '.xz', '.7z', '.rar', '.tgz',
    '.tar.gz', '.tar.bz2', '.tar.xz', '.dmg', '.iso', '.img',
    '.deb', '.rpm', '.pkg', '.msi', '.exe', '.app',
}

MODEL_EXTENSIONS = {
    '.pth', '.pt', '.onnx', '.pb', '.h5', '.hdf5', '.safetensors',
    '.ckpt', '.bin', '.model', '.weights', '.tflite', '.mlmodel',
    '.gguf', '.ggml',
}

BUILD_DIRS = {
    'node_modules', '.next', '__pycache__', '.cache', 'dist', 'build',
    '.tox', '.pytest_cache', '.mypy_cache', '.ruff_cache',
    'target', '.gradle', '.cargo', 'vendor',
    '.venv', 'venv', 'env', '.env',
    '.git',
}

SKIP_DIRS = {'.Trash', '.Spotlight-V100', '.fseventsd'}


def classify_file(path: str, ext: str) -> str:
    ext_lower = ext.lower()
    # Check path components for build dirs
    parts = Path(path).parts
    for part in parts:
        if part in BUILD_DIRS:
            return 'build_artifact'
    if ext_lower in GOLD_EXTENSIONS:
        return 'gold'
    if ext_lower in MEDIA_EXTENSIONS:
        return 'media'
    if ext_lower in ARCHIVE_EXTENSIONS:
        return 'archive'
    if ext_lower in MODEL_EXTENSIONS:
        return 'model_weight'
    # Heuristic: large binaries without extension
    return 'other'


def partial_hash(filepath: str, chunk_size: int = 8192) -> str:
    """Hash first + last 8KB for fast duplicate detection."""
    try:
        size = os.path.getsize(filepath)
        h = hashlib.md5()
        with open(filepath, 'rb') as f:
            h.update(f.read(chunk_size))
            if size > chunk_size * 2:
                f.seek(-chunk_size, 2)
                h.update(f.read(chunk_size))
        return h.hexdigest()
    except (OSError, IOError):
        return ''


def scan_project(project_path: str) -> dict:
    """Scan a single project directory."""
    result = {
        'path': project_path,
        'name': os.path.basename(project_path),
        'categories': defaultdict(lambda: {'count': 0, 'bytes': 0, 'files': []}),
        'large_files': [],  # > 50MB
        'total_bytes': 0,
        'total_files': 0,
        'gold_bytes': 0,
        'bloat_bytes': 0,
        'file_hashes': [],  # (hash, size, path) for duplicate detection
    }

    try:
        for root, dirs, files in os.walk(project_path):
            # Skip hidden/system dirs at any level
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith('.Trash')]

            rel_root = os.path.relpath(root, project_path)

            for fname in files:
                filepath = os.path.join(root, fname)
                try:
                    size = os.path.getsize(filepath)
                except OSError:
                    continue

                ext = os.path.splitext(fname)[1]
                rel_path = os.path.join(rel_root, fname)
                category = classify_file(rel_path, ext)

                result['categories'][category]['count'] += 1
                result['categories'][category]['bytes'] += size
                result['total_bytes'] += size
                result['total_files'] += 1

                if category == 'gold':
                    result['gold_bytes'] += size
                else:
                    result['bloat_bytes'] += size

                # Track large files (>10MB for reporting, >50MB for offload)
                if size > 10 * 1024 * 1024:
                    result['large_files'].append({
                        'path': rel_path,
                        'size': size,
                        'category': category,
                        'ext': ext.lower(),
                    })

                # Track for duplicate detection (files > 1MB)
                if size > 1 * 1024 * 1024:
                    h = partial_hash(filepath)
                    if h:
                        result['file_hashes'].append((h, size, filepath))

    except PermissionError:
        result['error'] = 'permission_denied'

    # Sort large files
    result['large_files'].sort(key=lambda x: x['size'], reverse=True)

    # Convert defaultdict for JSON
    result['categories'] = {k: dict(v) for k, v in result['categories'].items()}
    # Don't include individual file lists in categories (too verbose)
    for cat in result['categories'].values():
        if 'files' in cat:
            del cat['files']

    return result


def find_duplicates(all_hashes: list) -> list:
    """Find duplicate files across all projects."""
    by_hash = defaultdict(list)
    for h, size, path in all_hashes:
        by_hash[(h, size)].append(path)

    duplicates = []
    for (h, size), paths in by_hash.items():
        if len(paths) > 1:
            duplicates.append({
                'hash': h,
                'size': size,
                'count': len(paths),
                'total_wasted': size * (len(paths) - 1),
                'paths': paths,
            })

    duplicates.sort(key=lambda x: x['total_wasted'], reverse=True)
    return duplicates


def fmt_size(b: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB']:
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} TB"


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else '/Users/lech/PROJECTS_all'
    output_file = sys.argv[2] if len(sys.argv) > 2 else '/tmp/disk_scan_report.json'

    print(f"Scanning: {base}")
    entries = sorted([
        os.path.join(base, d) for d in os.listdir(base)
        if os.path.isdir(os.path.join(base, d))
    ])
    print(f"Found {len(entries)} directories\n")

    # Scan all projects in parallel
    results = []
    all_hashes = []

    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(scan_project, p): p for p in entries}
        for i, future in enumerate(as_completed(futures)):
            r = future.result()
            results.append(r)
            all_hashes.extend(r.pop('file_hashes', []))
            pct = (i + 1) / len(entries) * 100
            total = fmt_size(r['total_bytes'])
            gold = fmt_size(r['gold_bytes'])
            bloat_pct = (r['bloat_bytes'] / r['total_bytes'] * 100) if r['total_bytes'] > 0 else 0
            print(f"  [{pct:5.1f}%] {r['name']:50s} {total:>10s}  gold={gold:>10s}  bloat={bloat_pct:.0f}%")

    # Find duplicates
    print(f"\nFinding duplicates across {len(all_hashes)} large files...")
    duplicates = find_duplicates(all_hashes)

    # Sort results by total size
    results.sort(key=lambda x: x['total_bytes'], reverse=True)

    # Summary
    total_all = sum(r['total_bytes'] for r in results)
    gold_all = sum(r['gold_bytes'] for r in results)
    bloat_all = sum(r['bloat_bytes'] for r in results)
    dup_waste = sum(d['total_wasted'] for d in duplicates)

    print(f"\n{'='*70}")
    print(f"SUMMARY")
    print(f"{'='*70}")
    print(f"Total scanned:     {fmt_size(total_all)}")
    print(f"Gold (code/text):  {fmt_size(gold_all)} ({gold_all/total_all*100:.1f}%)")
    print(f"Bloat:             {fmt_size(bloat_all)} ({bloat_all/total_all*100:.1f}%)")
    print(f"Duplicate waste:   {fmt_size(dup_waste)} across {len(duplicates)} sets")

    print(f"\nTOP 20 BLOATED PROJECTS:")
    for r in results[:20]:
        bloat_pct = (r['bloat_bytes'] / r['total_bytes'] * 100) if r['total_bytes'] > 0 else 0
        print(f"  {fmt_size(r['total_bytes']):>10s}  bloat={bloat_pct:4.0f}%  {r['name']}")
        for cat, info in sorted(r['categories'].items(), key=lambda x: x[1]['bytes'], reverse=True):
            if info['bytes'] > 10 * 1024 * 1024:  # >10MB
                print(f"             {fmt_size(info['bytes']):>10s}  {info['count']:5d} files  [{cat}]")

    if duplicates[:20]:
        print(f"\nTOP 20 DUPLICATE SETS (by wasted space):")
        for d in duplicates[:20]:
            print(f"  {fmt_size(d['total_wasted']):>10s} wasted  ({d['count']} copies of {fmt_size(d['size'])} file)")
            for p in d['paths']:
                print(f"             {p}")

    # Save full report
    report = {
        'summary': {
            'total_bytes': total_all,
            'gold_bytes': gold_all,
            'bloat_bytes': bloat_all,
            'duplicate_waste_bytes': dup_waste,
            'project_count': len(results),
            'duplicate_sets': len(duplicates),
        },
        'projects': results,
        'duplicates': duplicates[:100],  # Top 100
    }

    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\nFull report saved to: {output_file}")


if __name__ == '__main__':
    main()
