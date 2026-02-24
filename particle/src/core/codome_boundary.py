"""
Codome Boundary: Synthetic nodes representing external calling contexts.

Creates boundary nodes for disconnected nodes that are actually reachable
through external mechanisms (test frameworks, CLI entry points, etc.).

Extracted from full_analysis.py during audit refactoring (2026-02-24).
"""
from typing import Dict, List, Any

from src.core.js_edge_detection import detect_js_imports, detect_class_instantiation


# Boundary node definitions: source -> metadata
CODOME_BOUNDARIES = {
    'test_entry': {
        'name': 'TestFramework',
        'description': 'Test frameworks (pytest, jest, unittest) invoke test functions',
        'color': '#4CAF50',
        'icon': '\U0001f9ea'
    },
    'entry_point': {
        'name': 'RuntimeEntry',
        'description': 'Program entry points (__main__, CLI, scripts)',
        'color': '#2196F3',
        'icon': '\U0001f680'
    },
    'framework_managed': {
        'name': 'FrameworkDI',
        'description': 'Framework/DI container instantiates (decorators, dataclasses)',
        'color': '#9C27B0',
        'icon': '\u2699\ufe0f'
    },
    'cross_language': {
        'name': 'HTMLTemplate',
        'description': 'Cross-language callers (HTML onclick, script src)',
        'color': '#FF9800',
        'icon': '\U0001f310'
    },
    'external_boundary': {
        'name': 'ExternalAPI',
        'description': 'External consumers (npm imports, public API)',
        'color': '#00BCD4',
        'icon': '\U0001f4e1'
    },
    'dynamic_target': {
        'name': 'DynamicDispatch',
        'description': 'Dynamic invocation (getattr, eval, reflection)',
        'color': '#E91E63',
        'icon': '\U0001f52e'
    }
}


def create_codome_boundaries(nodes: List[Dict], edges: List[Dict]) -> Dict[str, Any]:
    """
    Create synthetic codome boundary nodes and inferred edges.

    For each disconnection type (test_entry, entry_point, etc.), creates:
    1. A synthetic boundary node (e.g., __codome__::pytest)
    2. Inferred edges from boundary -> disconnected nodes

    Returns:
        {
            'boundary_nodes': [node_dicts...],
            'inferred_edges': [edge_dicts...],
            'summary': {source: count}
        }
    """
    # Run Detector #1: JS Imports
    js_count = detect_js_imports(nodes, edges)
    # Run Detector #2: Class Instantiation
    class_count = detect_class_instantiation(nodes, edges)

    print(f"   \u2192 [Codome] JS import edges detected: {js_count}")
    print(f"   \u2192 [Codome] Class instantiation edges detected: {class_count}")

    # Group disconnected nodes by reachability source
    by_source: Dict[str, List[Dict]] = {}
    for node in nodes:
        disconnection = node.get('disconnection')
        if disconnection:
            source = disconnection.get('reachability_source', 'unknown')
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(node)

    boundary_nodes = []
    inferred_edges = []
    summary = {}

    for source, disconnected_nodes in by_source.items():
        # Skip 'unreachable' - those are truly dead code
        if source == 'unreachable':
            summary[source] = len(disconnected_nodes)
            continue

        # Get boundary metadata
        boundary_meta = CODOME_BOUNDARIES.get(source)
        if not boundary_meta:
            summary[source] = len(disconnected_nodes)
            continue

        # Create synthetic boundary node
        boundary_id = f"__codome__::{source}"
        boundary_node = {
            'id': boundary_id,
            'name': boundary_meta['name'],
            'type': 'CodomeBoundary',
            'file_path': '__codome__',
            'kind': 'boundary',
            'is_codome_boundary': True,
            'codome_source': source,
            'description': boundary_meta['description'],
            'color_hint': boundary_meta['color'],
            'icon': boundary_meta['icon'],
            'in_degree': 0,
            'out_degree': len(disconnected_nodes),
            'topology_role': 'external',
            'tier': 'T0',
            'dimensions': {
                'D1_WHAT': 'BOUNDARY.CODOME',
                'D2_HOW': 'EXTERNAL',
                'D3_LAYER': 'BOUNDARY'
            }
        }
        boundary_nodes.append(boundary_node)

        # Create inferred edges from boundary -> disconnected nodes
        for target_node in disconnected_nodes:
            target_id = target_node.get('id', '')
            confidence = target_node.get('disconnection', {}).get('isolation_confidence', 0.5)

            edge = {
                'source': boundary_id,
                'target': target_id,
                'edge_type': 'invokes',
                'family': 'Codome',
                'inferred': True,
                'confidence': confidence,
                'resolution': 'inferred',
                'codome_source': source,
                'description': f'{boundary_meta["name"]} invokes {target_node.get("name", "unknown")}'
            }
            inferred_edges.append(edge)

        summary[source] = len(disconnected_nodes)

    return {
        'boundary_nodes': boundary_nodes,
        'inferred_edges': inferred_edges,
        'summary': summary,
        'total_boundaries': len(boundary_nodes),
        'total_inferred_edges': len(inferred_edges)
    }
