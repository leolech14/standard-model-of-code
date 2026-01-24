#!/usr/bin/env python3
"""
Corpus Inventory Tool
======================
Scans the repository and produces a complete inventory of all files,
categorized by type, language, and size.

Output: context-management/intelligence/corpus_inventory.json

Usage:
    python corpus_inventory.py                    # Full scan
    python corpus_inventory.py --quick           # Quick mode (skip hashes)
    python corpus_inventory.py --output FILE     # Custom output path
"""
import sys
import json
import hashlib
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "context-management/intelligence"

# File extension to language mapping
LANGUAGE_MAP = {
    '.py': 'python',
    '.ts': 'typescript',
    '.tsx': 'typescript',
    '.js': 'javascript',
    '.jsx': 'javascript',
    '.go': 'go',
    '.rs': 'rust',
    '.java': 'java',
    '.kt': 'kotlin',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.json': 'json',
    '.md': 'markdown',
    '.html': 'html',
    '.css': 'css',
    '.scss': 'scss',
    '.sql': 'sql',
    '.sh': 'shell',
    '.bash': 'shell',
    '.toml': 'toml',
}

# Directories to always skip
SKIP_DIRS = {
    '.git', '.venv', '.tools_venv', 'node_modules', '__pycache__',
    '.pytest_cache', '.mypy_cache', '.tox', 'dist', 'build',
    '.collider', '.next', 'coverage', '.DS_Store'
}

# File patterns to skip
SKIP_PATTERNS = {
    '.pyc', '.pyo', '.so', '.dylib', '.dll',
    '.lock', '.log', '.tmp', '.bak',
    '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg',
    '.pdf', '.zip', '.tar', '.gz',
}

# ============================================================================
# HELPERS
# ============================================================================

def should_skip_path(path: Path) -> bool:
    """Check if path should be skipped."""
    # Skip hidden files/dirs (except .agent)
    if path.name.startswith('.') and path.name not in ['.agent']:
        return True
    # Skip known directories
    if path.name in SKIP_DIRS:
        return True
    # Skip by extension
    if path.suffix.lower() in SKIP_PATTERNS:
        return True
    return False


def get_file_hash(path: Path) -> str:
    """Get SHA256 hash of file content."""
    try:
        return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
    except Exception:
        return "sha256:error"


def get_language(path: Path) -> str:
    """Determine language from file extension."""
    return LANGUAGE_MAP.get(path.suffix.lower(), 'other')


def categorize_file(path: Path, rel_path: str) -> str:
    """Categorize file by its location/purpose."""
    parts = rel_path.split('/')

    if 'test' in rel_path.lower() or 'tests' in parts:
        return 'test'
    if 'docs' in parts or 'doc' in parts:
        return 'documentation'
    if 'config' in parts or path.suffix in ['.yaml', '.yml', '.toml', '.json', '.ini']:
        return 'configuration'
    if '.agent' in parts:
        return 'agent'
    if 'tools' in parts:
        return 'tooling'
    if 'src' in parts or 'lib' in parts:
        return 'source'
    if 'archive' in parts:
        return 'archive'
    if 'research' in parts:
        return 'research'
    return 'other'


# ============================================================================
# MAIN SCANNER
# ============================================================================

def scan_corpus(root: Path, quick: bool = False) -> Dict[str, Any]:
    """
    Scan the entire repository and produce inventory.

    Returns:
        {
            "meta": {...},
            "summary": {...},
            "by_language": {...},
            "by_category": {...},
            "files": [...]
        }
    """
    files = []
    by_language: Dict[str, Dict[str, Any]] = {}
    by_category: Dict[str, Dict[str, Any]] = {}
    total_bytes = 0
    total_lines = 0

    print(f"Scanning corpus from: {root}")

    for path in root.rglob('*'):
        if not path.is_file():
            continue

        # Check if should skip
        if any(p in SKIP_DIRS for p in path.parts):
            continue
        if should_skip_path(path):
            continue

        try:
            rel_path = str(path.relative_to(root))
            stat = path.stat()
            size = stat.st_size

            # Skip very large files (>1MB) for detailed processing
            if size > 1_000_000:
                lang = get_language(path)
                cat = categorize_file(path, rel_path)
                entry = {
                    "path": rel_path,
                    "language": lang,
                    "category": cat,
                    "size_bytes": size,
                    "lines": 0,
                    "content_hash": "sha256:skipped_large",
                    "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
                }
            else:
                # Read file for line count and hash
                try:
                    content = path.read_bytes()
                    lines = content.count(b'\n')
                    content_hash = "sha256:" + hashlib.sha256(content).hexdigest() if not quick else "sha256:quick_mode"
                except Exception:
                    lines = 0
                    content_hash = "sha256:error"

                lang = get_language(path)
                cat = categorize_file(path, rel_path)

                entry = {
                    "path": rel_path,
                    "language": lang,
                    "category": cat,
                    "size_bytes": size,
                    "lines": lines,
                    "content_hash": content_hash,
                    "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
                }
                total_lines += lines

            files.append(entry)
            total_bytes += size

            # Aggregate by language
            if lang not in by_language:
                by_language[lang] = {"count": 0, "bytes": 0, "files": []}
            by_language[lang]["count"] += 1
            by_language[lang]["bytes"] += size
            by_language[lang]["files"].append(rel_path)

            # Aggregate by category
            if cat not in by_category:
                by_category[cat] = {"count": 0, "bytes": 0, "files": []}
            by_category[cat]["count"] += 1
            by_category[cat]["bytes"] += size
            by_category[cat]["files"].append(rel_path)

        except Exception as e:
            print(f"  Error processing {path}: {e}")

    # Sort files by path
    files.sort(key=lambda x: x["path"])

    # Convert defaultdicts to regular dicts (but keep file lists for smaller categories)
    for lang_data in by_language.values():
        if len(lang_data["files"]) > 100:
            lang_data["files"] = lang_data["files"][:10] + ["...truncated..."]
    for cat_data in by_category.values():
        if len(cat_data["files"]) > 100:
            cat_data["files"] = cat_data["files"][:10] + ["...truncated..."]

    return {
        "meta": {
            "tool": "corpus_inventory",
            "version": "1.0.0",
            "scanned_at": datetime.now().isoformat(),
            "root": str(root),
            "quick_mode": quick
        },
        "summary": {
            "total_files": len(files),
            "total_bytes": total_bytes,
            "total_lines": total_lines,
            "languages": len(by_language),
            "categories": len(by_category)
        },
        "by_language": dict(by_language),
        "by_category": dict(by_category),
        "files": files
    }


def main():
    parser = argparse.ArgumentParser(
        description="Corpus Inventory Tool - Scan and categorize repository files"
    )
    parser.add_argument("--quick", action="store_true",
                        help="Quick mode - skip content hashing")
    parser.add_argument("--output", type=str, default=None,
                        help="Custom output path")
    parser.add_argument("--root", type=str, default=None,
                        help="Custom root path to scan")

    args = parser.parse_args()

    root = Path(args.root) if args.root else PROJECT_ROOT
    output_path = Path(args.output) if args.output else OUTPUT_DIR / "corpus_inventory.json"

    # Scan
    inventory = scan_corpus(root, quick=args.quick)

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(inventory, f, indent=2)

    # Summary
    print(f"\nCorpus Inventory Complete:")
    print(f"  Files: {inventory['summary']['total_files']}")
    print(f"  Size: {inventory['summary']['total_bytes'] / 1_000_000:.1f} MB")
    print(f"  Lines: {inventory['summary']['total_lines']:,}")
    print(f"  Languages: {inventory['summary']['languages']}")
    print(f"  Output: {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
