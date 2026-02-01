#!/usr/bin/env python3
"""
Validate Collider output file against canonical contract.

Usage:
    python validate_output.py <unified_analysis.json>
    python validate_output.py .collider/unified_analysis.json
"""

import json
import sys
from pathlib import Path


def validate(file_path: str) -> dict:
    """Validate unified_analysis.json against contract."""
    result = {
        "valid": False,
        "file": file_path,
        "errors": [],
        "warnings": [],
        "stats": {}
    }

    path = Path(file_path)

    # Check file exists
    if not path.exists():
        result["errors"].append(f"File not found: {file_path}")
        return result

    # Check file size
    size_bytes = path.stat().st_size
    result["stats"]["size_bytes"] = size_bytes
    result["stats"]["size_mb"] = round(size_bytes / 1024 / 1024, 2)

    if size_bytes < 100:
        result["errors"].append(f"File too small ({size_bytes} bytes) - likely empty or corrupted")
        return result

    # Load JSON
    try:
        with open(path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        result["errors"].append(f"Invalid JSON: {e}")
        return result

    # Check required fields
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])

    result["stats"]["nodes"] = len(nodes)
    result["stats"]["edges"] = len(edges)

    if len(nodes) == 0:
        result["errors"].append("No nodes found - analysis likely failed")
        return result

    # Validate node structure (sample first 5)
    required_node_fields = ["id", "file_path"]
    for i, node in enumerate(nodes[:5]):
        for field in required_node_fields:
            if field not in node:
                result["warnings"].append(f"Node {i} missing field: {field}")

    # Validate edge structure (sample first 5)
    required_edge_fields = ["source", "target"]
    for i, edge in enumerate(edges[:5]):
        for field in required_edge_fields:
            if field not in edge:
                result["warnings"].append(f"Edge {i} missing field: {field}")

    # Check metadata
    if "metadata" not in data:
        result["warnings"].append("Missing metadata section")

    # All checks passed
    if not result["errors"]:
        result["valid"] = True

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_output.py <unified_analysis.json>")
        return 1

    file_path = sys.argv[1]
    result = validate(file_path)

    # Print result
    print("=" * 60)
    print("COLLIDER OUTPUT VALIDATION")
    print("=" * 60)
    print(f"File: {result['file']}")
    print(f"Valid: {'YES' if result['valid'] else 'NO'}")
    print()

    if result["stats"]:
        print("Stats:")
        for k, v in result["stats"].items():
            print(f"  {k}: {v}")
        print()

    if result["errors"]:
        print("ERRORS:")
        for e in result["errors"]:
            print(f"  - {e}")
        print()

    if result["warnings"]:
        print("WARNINGS:")
        for w in result["warnings"]:
            print(f"  - {w}")
        print()

    print("=" * 60)

    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
