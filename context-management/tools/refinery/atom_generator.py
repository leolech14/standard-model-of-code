#!/usr/bin/env python3
"""
Atom Generator
===============
Creates RefineryNode entries from source files.
Implements the "Atomization" principle - everything becomes a Node with ID.

This is the basic atom generator for files. Future versions will parse
AST to extract function/class level atoms.

Output: context-management/intelligence/atoms/

Usage:
    python atom_generator.py                      # Process all files
    python atom_generator.py --boundary brain     # Process specific boundary
    python atom_generator.py --file path/to/file  # Process single file
    python atom_generator.py --delta              # Only process changed files
"""
import sys
import json
import hashlib
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
INTELLIGENCE_DIR = PROJECT_ROOT / "context-management/intelligence"
ATOMS_DIR = INTELLIGENCE_DIR / "atoms"
CORPUS_INVENTORY_PATH = INTELLIGENCE_DIR / "corpus_inventory.json"
BOUNDARIES_PATH = INTELLIGENCE_DIR / "boundaries.json"
DELTA_REPORT_PATH = INTELLIGENCE_DIR / "delta_report.json"

# ============================================================================
# ATOM CREATION
# ============================================================================

def create_file_atom(file_info: Dict[str, Any], root: Path) -> Dict[str, Any]:
    """
    Create a RefineryNode from a file inventory entry.

    This is a "basic" atom - just the file level.
    Future: Parse AST for function/class atoms.
    """
    path = file_info["path"]
    safe_id = path.replace("/", "_").replace(".", "_").replace("-", "_")

    # Try to read first few lines for summary
    summary = f"File: {path}"
    try:
        full_path = root / path
        if full_path.exists() and full_path.stat().st_size < 100000:
            content = full_path.read_text(errors='replace')
            lines = content.split('\n')

            # Look for docstring or first comment
            for line in lines[:20]:
                stripped = line.strip()
                if stripped.startswith('"""') or stripped.startswith("'''"):
                    summary = stripped.strip('"\'')[:200]
                    break
                elif stripped.startswith('#') and len(stripped) > 5:
                    summary = stripped[1:].strip()[:200]
                    break
                elif stripped.startswith('//') and len(stripped) > 5:
                    summary = stripped[2:].strip()[:200]
                    break
    except Exception:
        pass

    now = datetime.now().isoformat()

    return {
        "id": f"FILE-{safe_id}",
        "type": "file",
        "name": Path(path).name,
        "source_path": path,
        "content_hash": file_info.get("content_hash", "sha256:unknown"),
        "summary": summary,

        # Relationships (to be enriched later)
        "relationships": {
            "contains": [],  # Will be populated with function/class atoms
            "imports": [],   # Will be populated from import analysis
            "imported_by": []
        },

        # Confidence
        "confidence": {
            "factual": 95,   # File exists
            "alignment": 70,  # Unknown without deeper analysis
            "current": 90,   # Based on hash
            "onwards": 70,   # Unknown
            "composite": 70
        },

        # Dimensions from file info
        "dimensions": {
            "D1_WHAT": "File",
            "D2_LAYER": infer_layer(path),
            "D3_ROLE": infer_role(path),
            "D4_BOUNDARY": "Internal",
            "D5_STATE": "Unknown",
            "D6_EFFECT": "Unknown",
            "D7_LIFECYCLE": "Singleton",
            "D8_TRUST": 80
        },

        # Timestamps
        "timestamps": {
            "created_at": now,
            "updated_at": now,
            "source_modified_at": file_info.get("modified_at"),
            "last_analyzed_at": now
        },

        # Metadata
        "metadata": {
            "language": file_info.get("language", "other"),
            "category": file_info.get("category", "other"),
            "lines_of_code": file_info.get("lines", 0),
            "size_bytes": file_info.get("size_bytes", 0)
        }
    }


def infer_layer(path: str) -> str:
    """Infer architectural layer from file path."""
    path_lower = path.lower()

    if 'test' in path_lower:
        return "Test"
    if 'docs' in path_lower or 'doc' in path_lower:
        return "Documentation"
    if 'config' in path_lower or path.endswith(('.yaml', '.yml', '.toml', '.json')):
        return "Configuration"
    if 'ui' in path_lower or 'component' in path_lower or 'view' in path_lower:
        return "Presentation"
    if 'api' in path_lower or 'route' in path_lower or 'handler' in path_lower:
        return "Application"
    if 'model' in path_lower or 'entity' in path_lower or 'domain' in path_lower:
        return "Domain"
    if 'db' in path_lower or 'repo' in path_lower or 'store' in path_lower:
        return "Infrastructure"
    return "Unknown"


def infer_role(path: str) -> str:
    """Infer semantic role from file path and name."""
    name = Path(path).stem.lower()
    path_lower = path.lower()

    if 'test' in name:
        return "Test"
    if 'spec' in name:
        return "Specification"
    if 'config' in name:
        return "Configuration"
    if 'util' in name or 'helper' in name:
        return "Utility"
    if 'service' in name:
        return "Service"
    if 'controller' in name or 'handler' in name:
        return "Handler"
    if 'model' in name or 'entity' in name:
        return "Entity"
    if 'repo' in name or 'repository' in name:
        return "Repository"
    if 'factory' in name:
        return "Factory"
    if 'validator' in name:
        return "Validator"
    if name in ['__init__', 'index', 'main']:
        return "EntryPoint"
    return "Unknown"


# ============================================================================
# BATCH PROCESSING
# ============================================================================

def process_files(
    files: List[Dict[str, Any]],
    boundary_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process a list of files and generate atoms.

    Returns:
        {
            "meta": {...},
            "summary": {...},
            "atoms": [RefineryNode, ...]
        }
    """
    atoms = []

    for file_info in files:
        atom = create_file_atom(file_info, PROJECT_ROOT)
        if boundary_name:
            atom["metadata"]["boundary"] = boundary_name
        atoms.append(atom)

    return {
        "meta": {
            "tool": "atom_generator",
            "version": "1.0.0",
            "generated_at": datetime.now().isoformat(),
            "boundary": boundary_name
        },
        "summary": {
            "atoms_generated": len(atoms),
            "by_layer": count_by_key(atoms, ["dimensions", "D2_LAYER"]),
            "by_role": count_by_key(atoms, ["dimensions", "D3_ROLE"]),
            "by_language": count_by_key(atoms, ["metadata", "language"])
        },
        "atoms": atoms
    }


def count_by_key(atoms: List[Dict], key_path: List[str]) -> Dict[str, int]:
    """Count atoms by a nested key path."""
    counts: Dict[str, int] = {}
    for atom in atoms:
        value = atom
        for key in key_path:
            value = value.get(key, {}) if isinstance(value, dict) else {}
        if isinstance(value, str):
            counts[value] = counts.get(value, 0) + 1
    return counts


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Atom Generator - Create RefineryNodes from files"
    )
    parser.add_argument("--boundary", type=str, default=None,
                        help="Process only files in specific boundary")
    parser.add_argument("--file", type=str, default=None,
                        help="Process single file")
    parser.add_argument("--delta", action="store_true",
                        help="Only process changed files from delta report")
    parser.add_argument("--output", type=str, default=None,
                        help="Custom output path")

    args = parser.parse_args()

    # Load inventory
    if not CORPUS_INVENTORY_PATH.exists():
        print("ERROR: No corpus inventory found. Run corpus_inventory.py first.")
        return 1

    with open(CORPUS_INVENTORY_PATH, 'r') as f:
        inventory = json.load(f)

    files = inventory.get("files", [])

    # Filter by boundary
    if args.boundary:
        if not BOUNDARIES_PATH.exists():
            print("ERROR: No boundaries found. Run boundary_mapper.py first.")
            return 1

        with open(BOUNDARIES_PATH, 'r') as f:
            boundaries = json.load(f)

        boundary_node = None
        for b in boundaries.get("boundaries", []):
            if b["region_name"] == args.boundary:
                boundary_node = b
                break

        if not boundary_node:
            print(f"ERROR: Boundary '{args.boundary}' not found.")
            return 1

        # Get files that match boundary patterns
        from fnmatch import fnmatch
        patterns = boundary_node.get("include_patterns", [])
        files = [f for f in files if any(fnmatch(f["path"], p) for p in patterns)]
        print(f"Filtering to boundary '{args.boundary}': {len(files)} files")

    # Filter to single file
    if args.file:
        files = [f for f in files if f["path"] == args.file]
        if not files:
            print(f"ERROR: File '{args.file}' not found in inventory.")
            return 1

    # Filter by delta
    if args.delta:
        if not DELTA_REPORT_PATH.exists():
            print("ERROR: No delta report found. Run delta_detector.py first.")
            return 1

        with open(DELTA_REPORT_PATH, 'r') as f:
            delta = json.load(f)

        changed_paths = set()
        for f in delta.get("changes", {}).get("added", []):
            changed_paths.add(f["path"])
        for f in delta.get("changes", {}).get("modified", []):
            changed_paths.add(f["path"])

        files = [f for f in files if f["path"] in changed_paths]
        print(f"Filtering to delta changes: {len(files)} files")

    if not files:
        print("No files to process.")
        return 0

    # Generate atoms
    print(f"Generating atoms for {len(files)} files...")
    result = process_files(files, boundary_name=args.boundary)

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    elif args.boundary:
        output_path = ATOMS_DIR / f"atoms_{args.boundary}.json"
    elif args.file:
        safe_name = Path(args.file).name.replace('.', '_')
        output_path = ATOMS_DIR / f"atom_{safe_name}.json"
    else:
        output_path = ATOMS_DIR / "atoms_all.json"

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)

    # Summary
    print(f"\nAtom Generation Complete:")
    print(f"  Atoms: {result['summary']['atoms_generated']}")
    print(f"  By Layer: {result['summary']['by_layer']}")
    print(f"  By Role: {result['summary']['by_role']}")
    print(f"  Output: {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
