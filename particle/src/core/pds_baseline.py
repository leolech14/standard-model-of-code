"""
PDS Baseline Management.

Manages the baseline (previous analysis results) that PDS compares against.
Every successful `collider full` run saves a baseline; `collider pds` reads it.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


BASELINE_FILENAME = "pds_baseline.json"


def load_baseline(project_path: str) -> Optional[Dict[str, Any]]:
    """Load PDS baseline from a previous full analysis.

    Args:
        project_path: Root of the analyzed project.

    Returns:
        Dict with 'nodes', 'edges', 'compiled_insights' keys,
        or None if no baseline exists.
    """
    baseline_path = Path(project_path) / ".collider" / BASELINE_FILENAME
    if not baseline_path.exists():
        return None

    try:
        with open(baseline_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Validate minimum structure
        if "nodes" in data and "edges" in data:
            return data
        return None
    except (json.JSONDecodeError, OSError):
        return None


def save_baseline(project_path: str, full_output: Dict[str, Any]) -> None:
    """Save PDS baseline from a completed full analysis.

    Extracts nodes, edges, and compiled_insights from the full output
    and writes them to .collider/pds_baseline.json.

    Args:
        project_path: Root of the analyzed project.
        full_output: Complete output dict from run_full_analysis().
    """
    collider_dir = Path(project_path) / ".collider"
    collider_dir.mkdir(parents=True, exist_ok=True)

    nodes = full_output.get("nodes", [])
    edges = full_output.get("edges", [])
    compiled = full_output.get("compiled_insights", {})

    # Extract only the fields PDS needs from each node (keep it lean)
    lean_nodes = []
    for node in nodes:
        lean_nodes.append({
            "id": node.get("id", ""),
            "file_path": node.get("file_path", node.get("file", "")),
            "name": node.get("name", ""),
            "kind": node.get("kind", ""),
        })

    lean_edges = []
    for edge in edges:
        lean_edges.append({
            "source": edge.get("source", ""),
            "target": edge.get("target", ""),
            "type": edge.get("type", edge.get("edge_type", "")),
        })

    baseline = {
        "nodes": lean_nodes,
        "edges": lean_edges,
        "compiled_insights": compiled,
    }

    baseline_path = collider_dir / BASELINE_FILENAME
    with open(baseline_path, "w", encoding="utf-8") as f:
        json.dump(baseline, f, indent=2)


def map_files_to_nodes(
    nodes: List[Dict[str, Any]],
    changed_files: Set[str],
    repo_root: str = "",
) -> Set[str]:
    """Map changed file paths to node IDs in the analysis graph.

    Args:
        nodes: List of node dicts from baseline (must have 'id' and 'file_path').
        changed_files: Set of relative file paths from git diff.
        repo_root: Repository root for resolving relative paths.

    Returns:
        Set of node IDs whose file_path matches a changed file.
    """
    # Build lookup: normalize changed file paths
    root = Path(repo_root) if repo_root else None
    normalized_changed = set()
    for fp in changed_files:
        if root:
            normalized_changed.add(str((root / fp).resolve()))
        normalized_changed.add(fp)
        # Also store just the relative path for matching
        normalized_changed.add(str(Path(fp)))

    matched_nodes = set()
    for node in nodes:
        node_id = node.get("id", "")
        node_file = node.get("file_path", "")
        if not node_id or not node_file:
            continue

        # Check against all normalized forms
        if node_file in normalized_changed:
            matched_nodes.add(node_id)
            continue

        # Try resolving the node's file_path
        try:
            resolved = str(Path(node_file).resolve())
            if resolved in normalized_changed:
                matched_nodes.add(node_id)
                continue
        except (OSError, ValueError):
            pass

        # Check if any changed file is a suffix of the node file path
        # (handles relative vs absolute path mismatches)
        for changed in changed_files:
            if node_file.endswith(changed) or changed.endswith(node_file):
                matched_nodes.add(node_id)
                break

    return matched_nodes
