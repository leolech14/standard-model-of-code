#!/usr/bin/env python3
"""
File Scanner - Directory Metadata Extraction for 3D Visualization

Scans directories recursively and extracts file metadata for:
1. Database storage (SQLite for fast queries)
2. Statistics generation (formats, sizes, concentrations)
3. 3D visualization (Collider-compatible output)

Usage:
    python file_scanner.py /path/to/scan --output ./scan_results
    python file_scanner.py ~/Downloads --db ~/file_index.db
    python file_scanner.py /path --stats  # Statistics only
"""

import argparse
import hashlib
import json
import mimetypes
import os
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# File format categories based on Perplexity research
FORMAT_CATEGORIES = {
    # Documents
    'document': {
        'extensions': {'doc', 'docx', 'docm', 'dotm', 'rtf', 'pdf', 'odt', 'txt',
                      'pptx', 'ppt', 'pps', 'xlsx', 'xls', 'csv', 'mpp', 'ps', 'epub'},
        'color': 'oklch(0.7 0.15 220)',  # Blue
    },
    # Images
    'image': {
        'extensions': {'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'tiff', 'tif',
                      'svg', 'ico', 'ppm', 'pbm', 'xwd', 'xpm', 'heic', 'heif',
                      'raw', 'cr2', 'nef', 'dng', 'psd', 'ai', 'eps'},
        'color': 'oklch(0.75 0.18 145)',  # Green
    },
    # Video
    'video': {
        'extensions': {'mp4', 'mpeg', 'mpg', 'mpe', 'm1v', 'm2v', 'webm', 'avi',
                      'mov', 'mkv', 'flv', 'wmv', 'm4v', '3gp', 'ogv'},
        'color': 'oklch(0.7 0.2 25)',  # Red
    },
    # Audio
    'audio': {
        'extensions': {'mp3', 'wav', 'ogg', 'm4a', 'aac', 'flac', 'mid', 'midi',
                      'wma', 'aiff', 'ape', 'opus'},
        'color': 'oklch(0.75 0.15 300)',  # Purple
    },
    # Code
    'code': {
        'extensions': {'py', 'pyc', 'js', 'jsx', 'ts', 'tsx', 'html', 'htm', 'css',
                      'scss', 'sass', 'less', 'json', 'jsonc', 'yaml', 'yml', 'xml',
                      'sql', 'sh', 'bash', 'zsh', 'rs', 'go', 'rb', 'php', 'java',
                      'c', 'cpp', 'h', 'hpp', 'swift', 'kt', 'kts', 'toml', 'ini',
                      'cfg', 'conf', 'md', 'mdx', 'rst', 'tex', 'vue', 'svelte'},
        'color': 'oklch(0.8 0.12 80)',  # Yellow
    },
    # Data
    'data': {
        'extensions': {'json', 'xml', 'csv', 'tsv', 'parquet', 'avro', 'db',
                      'sqlite', 'sqlite3', 'sql', 'pickle', 'pkl', 'npy', 'npz',
                      'hdf5', 'h5', 'feather', 'arrow'},
        'color': 'oklch(0.7 0.15 180)',  # Cyan
    },
    # Archives
    'archive': {
        'extensions': {'zip', 'tar', 'gz', 'tgz', 'bz2', 'xz', '7z', 'rar',
                      'cab', 'dmg', 'iso', 'img'},
        'color': 'oklch(0.6 0.1 60)',  # Brown
    },
    # 3D Models
    '3d_model': {
        'extensions': {'obj', 'fbx', 'gltf', 'glb', 'stl', 'dae', '3ds', 'blend',
                      'max', 'c4d', 'ma', 'mb', 'ply', 'usd', 'usda', 'usdc', 'usdz'},
        'color': 'oklch(0.75 0.2 330)',  # Pink
    },
    # Fonts
    'font': {
        'extensions': {'ttf', 'otf', 'woff', 'woff2', 'eot', 'fon'},
        'color': 'oklch(0.65 0.1 240)',  # Dark blue
    },
    # Executables
    'executable': {
        'extensions': {'exe', 'dll', 'so', 'dylib', 'app', 'dmg', 'msi', 'deb', 'rpm'},
        'color': 'oklch(0.5 0.15 0)',  # Dark red
    },
    # Config
    'config': {
        'extensions': {'env', 'gitignore', 'dockerignore', 'editorconfig',
                      'prettierrc', 'eslintrc', 'babelrc', 'npmrc', 'nvmrc'},
        'color': 'oklch(0.6 0.08 120)',  # Olive
    },
}

# Build reverse lookup
EXT_TO_CATEGORY = {}
for cat, info in FORMAT_CATEGORIES.items():
    for ext in info['extensions']:
        EXT_TO_CATEGORY[ext] = cat

# Directories to skip
SKIP_DIRS = {
    '.git', 'node_modules', '.venv', '__pycache__', '.pytest_cache',
    '.mypy_cache', 'dist', 'build', '.eggs', '.next', '.cache',
    '.parcel-cache', '.tox', 'venv', 'env', '.env', '.idea', '.vscode'
}


def get_file_category(ext: str) -> str:
    """Get category for a file extension."""
    ext_lower = ext.lstrip('.').lower()
    return EXT_TO_CATEGORY.get(ext_lower, 'other')


def get_mime_type(path: Path) -> str:
    """Get MIME type for a file."""
    mime, _ = mimetypes.guess_type(str(path))
    return mime or 'application/octet-stream'


def compute_file_hash(path: Path, quick: bool = True) -> Optional[str]:
    """Compute MD5 hash of file (quick mode: first 64KB only)."""
    try:
        with open(path, 'rb') as f:
            if quick:
                return hashlib.md5(f.read(65536)).hexdigest()
            return hashlib.md5(f.read()).hexdigest()
    except (PermissionError, OSError):
        return None


def scan_file(path: Path, root: Path) -> Optional[Dict[str, Any]]:
    """Extract metadata from a single file."""
    try:
        stat = path.stat()
        ext = path.suffix.lstrip('.').lower()
        rel_path = str(path.relative_to(root))

        return {
            'id': str(path),
            'name': path.name,
            'path': str(path),
            'rel_path': rel_path,
            'parent': str(path.parent),
            'parent_rel': str(path.parent.relative_to(root)) if path.parent != root else '',
            'ext': ext,
            'category': get_file_category(ext),
            'mime_type': get_mime_type(path),
            'size': stat.st_size,
            'size_kb': stat.st_size / 1024,
            'size_mb': stat.st_size / (1024 * 1024),
            'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'accessed': datetime.fromtimestamp(stat.st_atime).isoformat(),
            'age_days': (datetime.now() - datetime.fromtimestamp(stat.st_mtime)).days,
            'depth': len(rel_path.split(os.sep)) - 1,
            'is_hidden': path.name.startswith('.'),
        }
    except (PermissionError, OSError, FileNotFoundError) as e:
        print(f"  [SKIP] {path}: {e}", file=sys.stderr)
        return None


def scan_directory(root: Path, progress: bool = True) -> Tuple[List[Dict], List[Dict], Dict]:
    """
    Scan directory recursively and extract all file metadata.

    Returns:
        Tuple of (files, folders, stats)
    """
    root = root.resolve()
    files = []
    folders = []
    stats = {
        'total_files': 0,
        'total_folders': 0,
        'total_size': 0,
        'by_category': defaultdict(lambda: {'count': 0, 'size': 0}),
        'by_extension': defaultdict(lambda: {'count': 0, 'size': 0}),
        'by_depth': defaultdict(lambda: {'count': 0, 'size': 0}),
        'scan_root': str(root),
        'scan_time': datetime.now().isoformat(),
    }

    print(f"Scanning: {root}", file=sys.stderr)

    for dirpath, dirnames, filenames in os.walk(root):
        current_dir = Path(dirpath)

        # Skip excluded directories
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith('.')]

        # Process current folder
        try:
            rel_dir = str(current_dir.relative_to(root))
            folder_stat = current_dir.stat()
            folders.append({
                'id': str(current_dir),
                'name': current_dir.name or str(root),
                'path': str(current_dir),
                'rel_path': rel_dir,
                'parent': str(current_dir.parent),
                'depth': len(rel_dir.split(os.sep)) - 1 if rel_dir != '.' else 0,
                'modified': datetime.fromtimestamp(folder_stat.st_mtime).isoformat(),
                'file_count': len(filenames),
                'subdir_count': len(dirnames),
            })
            stats['total_folders'] += 1
        except (PermissionError, OSError):
            pass

        # Process files
        for filename in filenames:
            file_path = current_dir / filename
            file_data = scan_file(file_path, root)

            if file_data:
                files.append(file_data)
                stats['total_files'] += 1
                stats['total_size'] += file_data['size']

                # Aggregate stats
                cat = file_data['category']
                ext = file_data['ext']
                depth = file_data['depth']

                stats['by_category'][cat]['count'] += 1
                stats['by_category'][cat]['size'] += file_data['size']
                stats['by_extension'][ext]['count'] += 1
                stats['by_extension'][ext]['size'] += file_data['size']
                stats['by_depth'][depth]['count'] += 1
                stats['by_depth'][depth]['size'] += file_data['size']

        if progress and stats['total_files'] % 1000 == 0:
            print(f"  Processed {stats['total_files']} files...", file=sys.stderr)

    # Convert defaultdicts to regular dicts for JSON serialization
    stats['by_category'] = dict(stats['by_category'])
    stats['by_extension'] = dict(stats['by_extension'])
    stats['by_depth'] = dict(stats['by_depth'])

    print(f"Scan complete: {stats['total_files']} files, {stats['total_folders']} folders", file=sys.stderr)

    return files, folders, stats


def create_database(db_path: Path) -> sqlite3.Connection:
    """Create SQLite database with schema."""
    conn = sqlite3.connect(str(db_path))
    conn.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id TEXT PRIMARY KEY,
            name TEXT,
            path TEXT UNIQUE,
            rel_path TEXT,
            parent TEXT,
            parent_rel TEXT,
            ext TEXT,
            category TEXT,
            mime_type TEXT,
            size INTEGER,
            created TEXT,
            modified TEXT,
            accessed TEXT,
            age_days INTEGER,
            depth INTEGER,
            is_hidden INTEGER,
            scan_time TEXT
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS folders (
            id TEXT PRIMARY KEY,
            name TEXT,
            path TEXT UNIQUE,
            rel_path TEXT,
            parent TEXT,
            depth INTEGER,
            modified TEXT,
            file_count INTEGER,
            subdir_count INTEGER,
            scan_time TEXT
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            root_path TEXT,
            scan_time TEXT,
            total_files INTEGER,
            total_folders INTEGER,
            total_size INTEGER,
            stats_json TEXT
        )
    ''')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_files_category ON files(category)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_files_ext ON files(ext)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_files_parent ON files(parent_rel)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_files_depth ON files(depth)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_files_size ON files(size)')
    conn.commit()
    return conn


def save_to_database(conn: sqlite3.Connection, files: List[Dict], folders: List[Dict], stats: Dict):
    """Save scan results to database."""
    scan_time = stats['scan_time']

    # Insert files
    for f in files:
        conn.execute('''
            INSERT OR REPLACE INTO files
            (id, name, path, rel_path, parent, parent_rel, ext, category, mime_type,
             size, created, modified, accessed, age_days, depth, is_hidden, scan_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            f['id'], f['name'], f['path'], f['rel_path'], f['parent'], f['parent_rel'],
            f['ext'], f['category'], f['mime_type'], f['size'], f['created'],
            f['modified'], f['accessed'], f['age_days'], f['depth'],
            1 if f['is_hidden'] else 0, scan_time
        ))

    # Insert folders
    for folder in folders:
        conn.execute('''
            INSERT OR REPLACE INTO folders
            (id, name, path, rel_path, parent, depth, modified, file_count, subdir_count, scan_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            folder['id'], folder['name'], folder['path'], folder['rel_path'],
            folder['parent'], folder['depth'], folder['modified'],
            folder['file_count'], folder['subdir_count'], scan_time
        ))

    # Insert scan record
    conn.execute('''
        INSERT INTO scans (root_path, scan_time, total_files, total_folders, total_size, stats_json)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        stats['scan_root'], scan_time, stats['total_files'],
        stats['total_folders'], stats['total_size'], json.dumps(stats)
    ))

    conn.commit()
    print(f"Database saved: {conn.execute('SELECT COUNT(*) FROM files').fetchone()[0]} files", file=sys.stderr)


def generate_collider_output(files: List[Dict], folders: List[Dict], stats: Dict) -> Dict:
    """
    Generate Collider-compatible JSON output for 3D visualization.

    Format matches Collider's nodes/edges structure.
    """
    nodes = []
    edges = []

    # Create folder nodes
    folder_ids = {}
    for folder in folders:
        node_id = f"folder:{folder['rel_path']}"
        folder_ids[folder['path']] = node_id

        nodes.append({
            'id': node_id,
            'name': folder['name'],
            'type': 'folder',
            'kind': 'directory',
            'file_path': folder['path'],
            'rel_path': folder['rel_path'],
            'depth': folder['depth'],
            'file_count': folder['file_count'],
            'subdir_count': folder['subdir_count'],
            # Visual properties
            'ring': 'infrastructure',  # Folders go in infrastructure ring
            'size_bucket': 'medium',
        })

        # Edge to parent folder
        if folder['parent'] in folder_ids:
            edges.append({
                'source': folder_ids[folder['parent']],
                'target': node_id,
                'type': 'contains',
            })

    # Create file nodes
    for f in files:
        node_id = f"file:{f['rel_path']}"
        category = f['category']

        # Determine ring based on category
        ring_map = {
            'code': 'core',
            'data': 'data',
            'config': 'infrastructure',
            'document': 'interface',
            'image': 'interface',
            'video': 'interface',
            'audio': 'interface',
            '3d_model': 'interface',
            'archive': 'infrastructure',
            'executable': 'infrastructure',
            'font': 'interface',
        }
        ring = ring_map.get(category, 'interface')

        # Determine size bucket
        size = f['size']
        if size < 1024:  # < 1KB
            size_bucket = 'tiny'
        elif size < 10 * 1024:  # < 10KB
            size_bucket = 'small'
        elif size < 100 * 1024:  # < 100KB
            size_bucket = 'medium'
        elif size < 1024 * 1024:  # < 1MB
            size_bucket = 'large'
        else:
            size_bucket = 'huge'

        nodes.append({
            'id': node_id,
            'name': f['name'],
            'type': category,
            'kind': 'file',
            'file_path': f['path'],
            'rel_path': f['rel_path'],
            'ext': f['ext'],
            'category': category,
            'mime_type': f['mime_type'],
            'size': f['size'],
            'size_kb': f['size_kb'],
            'modified': f['modified'],
            'age_days': f['age_days'],
            'depth': f['depth'],
            # Visual properties
            'ring': ring,
            'size_bucket': size_bucket,
            # Collider-style dimensions (for compatibility)
            'responsibility': min(10, f['depth'] + 1),
            'purity': 8 if category == 'code' else 5,
            'boundary': 3 if category in ('data', 'config') else 7,
            'lifecycle': 5,
        })

        # Edge to parent folder
        parent_id = folder_ids.get(f['parent'])
        if parent_id:
            edges.append({
                'source': parent_id,
                'target': node_id,
                'type': 'contains',
            })

    return {
        'nodes': nodes,
        'edges': edges,
        'meta': {
            'target': stats['scan_root'],
            'timestamp': stats['scan_time'],
            'version': 'FileScanner-V1',
            'generator': 'file_scanner.py',
        },
        'counts': {
            'nodes': len(nodes),
            'edges': len(edges),
            'files': stats['total_files'],
            'folders': stats['total_folders'],
        },
        'distributions': {
            'types': {cat: info['count'] for cat, info in stats['by_category'].items()},
            'extensions': dict(list(sorted(
                stats['by_extension'].items(),
                key=lambda x: x[1]['count'],
                reverse=True
            ))[:20]),
        },
        'stats': stats,
    }


def print_stats(stats: Dict):
    """Print statistics summary."""
    print("\n" + "=" * 60)
    print("FILE SCAN STATISTICS")
    print("=" * 60)
    print(f"\nRoot: {stats['scan_root']}")
    print(f"Time: {stats['scan_time']}")
    print(f"\nTotal Files: {stats['total_files']:,}")
    print(f"Total Folders: {stats['total_folders']:,}")
    print(f"Total Size: {stats['total_size'] / (1024*1024*1024):.2f} GB")

    print("\n--- By Category ---")
    for cat, info in sorted(stats['by_category'].items(), key=lambda x: x[1]['count'], reverse=True):
        pct = info['count'] / stats['total_files'] * 100 if stats['total_files'] else 0
        size_mb = info['size'] / (1024 * 1024)
        print(f"  {cat:15} {info['count']:6,} files ({pct:5.1f}%)  {size_mb:10.1f} MB")

    print("\n--- Top 15 Extensions ---")
    top_ext = sorted(stats['by_extension'].items(), key=lambda x: x[1]['count'], reverse=True)[:15]
    for ext, info in top_ext:
        ext_display = ext if ext else '(none)'
        pct = info['count'] / stats['total_files'] * 100 if stats['total_files'] else 0
        print(f"  .{ext_display:12} {info['count']:6,} files ({pct:5.1f}%)")

    print("\n--- By Depth ---")
    for depth, info in sorted(stats['by_depth'].items()):
        pct = info['count'] / stats['total_files'] * 100 if stats['total_files'] else 0
        print(f"  Level {depth}: {info['count']:6,} files ({pct:5.1f}%)")


def main():
    parser = argparse.ArgumentParser(
        description="Scan directory and extract file metadata for visualization"
    )
    parser.add_argument('path', help="Directory to scan")
    parser.add_argument('--output', '-o', help="Output directory for results")
    parser.add_argument('--db', help="SQLite database path")
    parser.add_argument('--stats', action='store_true', help="Print statistics only")
    parser.add_argument('--json', action='store_true', help="Output raw JSON")
    parser.add_argument('--collider', action='store_true', help="Output Collider-compatible JSON")

    args = parser.parse_args()

    scan_path = Path(args.path).expanduser().resolve()
    if not scan_path.exists():
        print(f"Error: Path does not exist: {scan_path}", file=sys.stderr)
        sys.exit(1)

    # Scan
    files, folders, stats = scan_directory(scan_path)

    # Print stats
    print_stats(stats)

    if args.stats:
        return

    # Output directory
    if args.output:
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save raw JSON
        if args.json:
            raw_path = output_dir / 'scan_raw.json'
            with open(raw_path, 'w') as f:
                json.dump({'files': files, 'folders': folders, 'stats': stats}, f, indent=2)
            print(f"\nRaw JSON: {raw_path}")

        # Save Collider-compatible JSON
        collider_data = generate_collider_output(files, folders, stats)
        collider_path = output_dir / 'scan_collider.json'
        with open(collider_path, 'w') as f:
            json.dump(collider_data, f, indent=2)
        print(f"Collider JSON: {collider_path}")

        # Save stats
        stats_path = output_dir / 'scan_stats.json'
        with open(stats_path, 'w') as f:
            json.dump(stats, f, indent=2)
        print(f"Stats JSON: {stats_path}")

    # Database
    if args.db:
        db_path = Path(args.db).expanduser()
        conn = create_database(db_path)
        save_to_database(conn, files, folders, stats)
        conn.close()
        print(f"\nDatabase: {db_path}")

    # Collider output to stdout
    if args.collider and not args.output:
        collider_data = generate_collider_output(files, folders, stats)
        print(json.dumps(collider_data, indent=2))


if __name__ == '__main__':
    main()
