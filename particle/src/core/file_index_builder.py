"""
File-centric view: Bridges atom-centric analysis with file-based navigation.

Builds file indices and boundary data for hybrid atom/file navigation in
the visualization layer.

Extracted from full_analysis.py during audit refactoring (2026-02-24).
"""
from collections import Counter
from pathlib import Path
from typing import Dict, List, Any


def build_file_index(nodes: List[Dict], edges: List[Dict], target_path: str = "") -> Dict[str, Any]:
    """
    Build a file-centric index of atoms for hybrid navigation.

    This bridges the atom-centric paradigm (Collider's core insight) with
    traditional file-based navigation that developers expect.

    Returns:
        {
            "file_path": {
                "atoms": [atom_indices...],
                "atom_names": ["name1", "name2"...],
                "line_range": [start, end],
                "atom_count": N,
                "imports": [...],
                "internal_edges": N,
                "external_edges": N,
                "purpose": "inferred purpose"
            }
        }
    """
    files_index: Dict[str, Dict[str, Any]] = {}

    # Group nodes by file
    for idx, node in enumerate(nodes):
        file_path = node.get("file_path", "")
        if not file_path:
            continue

        if file_path not in files_index:
            files_index[file_path] = {
                "atoms": [],
                "atom_names": [],
                "atom_types": [],
                "line_range": [float('inf'), 0],
                "atom_count": 0,
                "classes": [],
                "functions": [],
                "imports": [],
                "internal_edges": 0,
                "external_edges": 0,
                "purpose": ""
            }

        entry = files_index[file_path]
        entry["atoms"].append(idx)
        entry["atom_names"].append(node.get("name", ""))
        entry["atom_types"].append(node.get("type", "Unknown"))
        entry["atom_count"] += 1

        # Track line range
        line = node.get("line", 0)
        end_line = node.get("end_line", line)
        if line > 0:
            entry["line_range"][0] = min(entry["line_range"][0], line)
            entry["line_range"][1] = max(entry["line_range"][1], end_line)

        # Categorize by symbol kind
        kind = node.get("symbol_kind", "")
        name = node.get("name", "")
        if kind == "class":
            entry["classes"].append(name)
        elif kind in ("function", "method"):
            entry["functions"].append(name)

    # Compute edges (internal vs external)
    node_name_to_file = {n.get("name", ""): n.get("file_path", "") for n in nodes}

    for edge in edges:
        source = edge.get("source", "")
        target = edge.get("target", "")

        source_file = node_name_to_file.get(source, "")
        target_file = node_name_to_file.get(target, "")

        if source_file and source_file in files_index:
            if source_file == target_file:
                files_index[source_file]["internal_edges"] += 1
            else:
                files_index[source_file]["external_edges"] += 1

    # Infer file purpose from dominant atom types
    for file_path, entry in files_index.items():
        types = Counter(entry["atom_types"])
        dominant = types.most_common(1)
        if dominant:
            dom_type, count = dominant[0]
            if dom_type != "Unknown":
                entry["purpose"] = f"{dom_type}-dominant ({count}/{entry['atom_count']})"
            else:
                fname = Path(file_path).stem.lower()
                if "test" in fname:
                    entry["purpose"] = "Test module"
                elif "util" in fname or "helper" in fname:
                    entry["purpose"] = "Utility module"
                elif "model" in fname or "entity" in fname:
                    entry["purpose"] = "Domain model"
                elif "service" in fname:
                    entry["purpose"] = "Service layer"
                elif "controller" in fname or "handler" in fname:
                    entry["purpose"] = "Interface layer"
                else:
                    entry["purpose"] = "General module"

        # Fix line_range if no lines found
        if entry["line_range"][0] == float('inf'):
            entry["line_range"] = [0, 0]

        # Clean up atom_types (don't need in output, was for computation)
        del entry["atom_types"]

    return files_index


def build_file_boundaries(files_index: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Build file boundary data for visualization.

    Returns a list of boundary objects that can be used to draw
    visual separators between files in the atom graph.
    """
    boundaries = []

    for file_path, data in files_index.items():
        if data["atom_count"] == 0:
            continue

        boundaries.append({
            "file": file_path,
            "file_name": Path(file_path).name,
            "atom_indices": data["atoms"],
            "atom_count": data["atom_count"],
            "line_range": data["line_range"],
            "classes": data["classes"],
            "functions": data["functions"][:10],
            "cohesion": data["internal_edges"] / max(1, data["internal_edges"] + data["external_edges"]),
            "purpose": data["purpose"]
        })

    boundaries.sort(key=lambda b: b["file"])
    return boundaries


def calculate_theory_completeness(nodes: List[Dict]) -> Dict[str, Any]:
    """
    Calculate theory completeness metrics for the analysis output.

    Measures what percentage of applicable Standard Model elements
    are captured in the analysis.
    """
    if not nodes:
        return {'overall_score': 0, 'error': 'No nodes'}

    total = len(nodes)

    # D1_WHAT (atom assignment)
    d1_what_assigned = sum(
        1 for n in nodes
        if n.get('dimensions', {}).get('D1_WHAT')
        and n['dimensions']['D1_WHAT'] != 'Unknown'
    )

    # D1_ECOSYSTEM
    d1_ecosystem_assigned = sum(
        1 for n in nodes
        if n.get('dimensions', {}).get('D1_ECOSYSTEM')
    )

    # React hook metadata
    react_components = [
        n for n in nodes
        if n.get('dimensions', {}).get('D1_WHAT', '').startswith('EXT.REACT.')
    ]
    hooks_enriched = sum(
        1 for n in react_components
        if n.get('metadata', {}).get('hooks_used') is not None
    )

    # K8s metadata
    k8s_resources = [
        n for n in nodes
        if n.get('dimensions', {}).get('D1_ECOSYSTEM') == 'kubernetes'
    ]
    k8s_kind_assigned = sum(
        1 for n in k8s_resources
        if n.get('metadata', {}).get('k8s_kind')
    )

    # Calculate percentages
    d1_what_pct = (d1_what_assigned / total) * 100
    d1_ecosystem_pct = (d1_ecosystem_assigned / total) * 100
    hooks_pct = (hooks_enriched / len(react_components) * 100) if react_components else 100.0
    k8s_pct = (k8s_kind_assigned / len(k8s_resources) * 100) if k8s_resources else 100.0

    # Overall score
    overall = (d1_what_pct * 0.4 + d1_ecosystem_pct * 0.3 + hooks_pct * 0.15 + k8s_pct * 0.15)

    return {
        'd1_what_percentage': round(d1_what_pct, 1),
        'd1_ecosystem_percentage': round(d1_ecosystem_pct, 1),
        'hooks_metadata_percentage': round(hooks_pct, 1),
        'k8s_metadata_percentage': round(k8s_pct, 1),
        'overall_score': round(overall, 1)
    }
