#!/usr/bin/env python3
"""
Boundary Mapper
================
Maps analysis_sets.yaml to BoundaryNode entries in the RefineryNode format.
Creates a semantic map of all defined boundaries (brain, body, viz, etc.)

Output: context-management/intelligence/boundaries.json

Usage:
    python boundary_mapper.py                    # Map all boundaries
    python boundary_mapper.py --boundary brain   # Map single boundary
"""
import sys
import json
import yaml
import hashlib
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
ANALYSIS_SETS_PATH = PROJECT_ROOT / "context-management/config/analysis_sets.yaml"
OUTPUT_DIR = PROJECT_ROOT / "context-management/intelligence"

# ============================================================================
# HELPERS
# ============================================================================

def load_analysis_sets() -> Dict[str, Any]:
    """Load analysis_sets.yaml configuration."""
    with open(ANALYSIS_SETS_PATH, 'r') as f:
        return yaml.safe_load(f)


def expand_patterns(patterns: List[str], root: Path) -> List[str]:
    """Expand glob patterns to actual file paths."""
    files = []
    for pattern in patterns:
        for path in root.glob(pattern):
            if path.is_file():
                files.append(str(path.relative_to(root)))
    return sorted(set(files))


def create_boundary_node(
    name: str,
    config: Dict[str, Any],
    matched_files: List[str],
    root: Path
) -> Dict[str, Any]:
    """Create a BoundaryNode from an analysis set definition."""

    # Calculate content hash from all matched file paths
    content_str = "\n".join(sorted(matched_files))
    content_hash = "sha256:" + hashlib.sha256(content_str.encode()).hexdigest()

    # Calculate total size
    total_bytes = 0
    total_lines = 0
    for f in matched_files:
        try:
            path = root / f
            if path.exists():
                total_bytes += path.stat().st_size
                total_lines += path.read_bytes().count(b'\n')
        except Exception:
            pass

    now = datetime.now().isoformat()

    return {
        "id": f"BOUNDARY-{name}",
        "type": "boundary",
        "name": name,
        "source_path": "context-management/config/analysis_sets.yaml",
        "content_hash": content_hash,
        "summary": config.get("description", f"Boundary region: {name}"),

        # Boundary-specific fields
        "region_name": name,
        "include_patterns": config.get("patterns", []),
        "exclude_patterns": config.get("exclude", []),

        # Relationships
        "relationships": {
            "contains": [f"FILE-{f.replace('/', '_').replace('.', '_')}" for f in matched_files[:50]],
            # Truncate to first 50 for large boundaries
        },

        # Confidence
        "confidence": {
            "factual": 100,  # Patterns are deterministic
            "alignment": 90,  # Matches project structure
            "current": 95,   # Based on current files
            "onwards": 85,   # May need updates as project grows
            "composite": 85
        },

        # Dimensions
        "dimensions": {
            "D1_WHAT": "Boundary",
            "D2_LAYER": "Meta",
            "D3_ROLE": "Container",
            "D4_BOUNDARY": "Internal",
            "D5_STATE": "Stateless",
            "D6_EFFECT": "Pure",
            "D7_LIFECYCLE": "Singleton",
            "D8_TRUST": 95
        },

        # Timestamps
        "timestamps": {
            "created_at": now,
            "updated_at": now,
            "last_analyzed_at": now
        },

        # Metadata
        "metadata": {
            "max_tokens": config.get("max_tokens", 0),
            "auto_interactive": config.get("auto_interactive", False),
            "includes": config.get("includes", []),
            "file_count": len(matched_files),
            "total_bytes": total_bytes,
            "total_lines": total_lines,
            "critical_files": config.get("critical_files", []),
            "positional_strategy": config.get("positional_strategy")
        }
    }


# ============================================================================
# MAIN MAPPER
# ============================================================================

def map_boundaries(target_boundary: Optional[str] = None) -> Dict[str, Any]:
    """
    Map all (or specific) boundaries from analysis_sets.yaml.

    Returns:
        {
            "meta": {...},
            "summary": {...},
            "boundaries": [BoundaryNode, ...]
        }
    """
    config = load_analysis_sets()
    analysis_sets = config.get("analysis_sets", {})

    boundaries = []
    total_files = 0

    for name, set_config in analysis_sets.items():
        # Skip if filtering to specific boundary
        if target_boundary and name != target_boundary:
            continue

        patterns = set_config.get("patterns", [])
        exclude = set_config.get("exclude", [])

        # Expand patterns
        matched_files = expand_patterns(patterns, PROJECT_ROOT)

        # Apply exclusions
        if exclude:
            excluded_files = expand_patterns(exclude, PROJECT_ROOT)
            matched_files = [f for f in matched_files if f not in excluded_files]

        # Create boundary node
        boundary = create_boundary_node(name, set_config, matched_files, PROJECT_ROOT)
        boundaries.append(boundary)
        total_files += len(matched_files)

        print(f"  {name}: {len(matched_files)} files")

    return {
        "meta": {
            "tool": "boundary_mapper",
            "version": "1.0.0",
            "mapped_at": datetime.now().isoformat(),
            "source": str(ANALYSIS_SETS_PATH)
        },
        "summary": {
            "boundaries": len(boundaries),
            "total_files_mapped": total_files
        },
        "boundaries": boundaries
    }


def main():
    parser = argparse.ArgumentParser(
        description="Boundary Mapper - Map analysis_sets.yaml to BoundaryNodes"
    )
    parser.add_argument("--boundary", type=str, default=None,
                        help="Map only a specific boundary")
    parser.add_argument("--output", type=str, default=None,
                        help="Custom output path")

    args = parser.parse_args()

    output_path = Path(args.output) if args.output else OUTPUT_DIR / "boundaries.json"

    print("Mapping boundaries from analysis_sets.yaml...")

    # Map boundaries
    result = map_boundaries(target_boundary=args.boundary)

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)

    # Summary
    print(f"\nBoundary Mapping Complete:")
    print(f"  Boundaries: {result['summary']['boundaries']}")
    print(f"  Files Mapped: {result['summary']['total_files_mapped']}")
    print(f"  Output: {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
