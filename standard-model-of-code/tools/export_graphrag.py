#!/usr/bin/env python3
"""
GraphRAG Export Tool

Exports Collider unified_analysis.json to Microsoft GraphRAG-compatible format.

Output files (parquet):
- entities.parquet: Nodes as entities with descriptions
- relationships.parquet: Edges as relationships with weights
- text_units.parquet: Source code chunks (optional)

Usage:
    python tools/export_graphrag.py <unified_analysis.json> [--output <dir>]

Reference:
    https://microsoft.github.io/graphrag/index/byog/
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
import sys

# Check for pyarrow/pandas
try:
    import pandas as pd
    import pyarrow as pa
    import pyarrow.parquet as pq
    HAS_PARQUET = True
except ImportError:
    HAS_PARQUET = False


def load_analysis(path: Path) -> Dict[str, Any]:
    """Load unified_analysis.json."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def build_entity_description(node: Dict[str, Any]) -> str:
    """Build a rich description for an entity from node metadata."""
    parts = []

    # Basic identity
    name = node.get('name', node.get('id', 'Unknown'))
    role = node.get('role', node.get('type', 'Unknown'))
    parts.append(f"{name} is a {role}")

    # File location
    file_path = node.get('file_path', '')
    if file_path:
        start_line = node.get('start_line', '')
        if start_line:
            parts.append(f"located at {file_path}:{start_line}")
        else:
            parts.append(f"in {file_path}")

    # Dimensions (if available)
    dims = node.get('dimensions', {})
    if dims:
        dim_parts = []
        if dims.get('D3_ROLE'):
            dim_parts.append(f"role={dims['D3_ROLE']}")
        if dims.get('D4_BOUNDARY'):
            dim_parts.append(f"boundary={dims['D4_BOUNDARY']}")
        if dims.get('D5_STATE'):
            dim_parts.append(f"state={dims['D5_STATE']}")
        if dims.get('D6_EFFECT'):
            dim_parts.append(f"effect={dims['D6_EFFECT']}")
        if dim_parts:
            parts.append(f"with dimensions: {', '.join(dim_parts)}")

    # Atom classification
    atom = node.get('atom', dims.get('D1_WHAT', ''))
    if atom:
        parts.append(f"classified as atom {atom}")

    # RPBL scores
    rpbl = node.get('rpbl', {})
    if rpbl:
        rpbl_str = f"R={rpbl.get('responsibility', '?')}, P={rpbl.get('purity', '?')}, B={rpbl.get('boundary', '?')}, L={rpbl.get('lifecycle', '?')}"
        parts.append(f"RPBL scores: {rpbl_str}")

    return ". ".join(parts) + "."


def build_relationship_description(edge: Dict[str, Any], nodes_by_id: Dict[str, Dict]) -> str:
    """Build a description for a relationship from edge metadata."""
    source_id = edge.get('source', '')
    target_id = edge.get('target', '')
    edge_type = edge.get('type', edge.get('family', 'relates_to'))

    source_name = nodes_by_id.get(source_id, {}).get('name', source_id)
    target_name = nodes_by_id.get(target_id, {}).get('name', target_id)

    # Build description based on edge type
    type_descriptions = {
        'calls': f"{source_name} calls {target_name}",
        'imports': f"{source_name} imports {target_name}",
        'contains': f"{source_name} contains {target_name}",
        'inherits': f"{source_name} inherits from {target_name}",
        'implements': f"{source_name} implements {target_name}",
        'uses': f"{source_name} uses {target_name}",
        'defines': f"{source_name} defines {target_name}",
        'references': f"{source_name} references {target_name}",
    }

    description = type_descriptions.get(edge_type, f"{source_name} {edge_type} {target_name}")

    # Add weight info if significant
    weight = edge.get('weight', edge.get('markov_weight', 1.0))
    if weight != 1.0:
        description += f" (weight: {weight:.2f})"

    return description


def export_to_graphrag(
    analysis: Dict[str, Any],
    output_dir: Path,
    include_source: bool = True
) -> Dict[str, int]:
    """
    Export unified_analysis to GraphRAG parquet format.

    Returns counts of exported entities and relationships.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    nodes = analysis.get('nodes', [])
    edges = analysis.get('edges', [])

    # Build node lookup
    nodes_by_id = {n.get('id', ''): n for n in nodes}

    # === ENTITIES ===
    entities = []
    for i, node in enumerate(nodes):
        node_id = node.get('id', f'node_{i}')

        entity = {
            'id': node_id,
            'human_readable_id': i,
            'title': node.get('name', node_id),
            'description': build_entity_description(node),
            'type': node.get('role', node.get('type', 'Unknown')),
            # GraphRAG optional fields
            'text_unit_ids': [],  # Will populate if source available
            # Collider-specific metadata (preserved for downstream use)
            'x': node.get('x', 0),
            'y': node.get('y', 0),
            'z': node.get('z', 0),
        }

        # Add text_unit reference if we have source
        if include_source and node.get('body_source'):
            entity['text_unit_ids'] = [f'text_{node_id}']

        entities.append(entity)

    # === RELATIONSHIPS ===
    relationships = []
    for i, edge in enumerate(edges):
        edge_id = edge.get('id', f'edge_{i}')
        source = edge.get('source', '')
        target = edge.get('target', '')

        # Skip invalid edges
        if not source or not target:
            continue

        # Calculate weight (normalize markov_weight or use default)
        weight = edge.get('weight', edge.get('markov_weight', 1.0))
        if isinstance(weight, (int, float)):
            weight = float(weight)
        else:
            weight = 1.0

        rel = {
            'id': edge_id,
            'human_readable_id': i,
            'source': source,
            'target': target,
            'description': build_relationship_description(edge, nodes_by_id),
            'weight': weight,
            'combined_degree': edge.get('combined_degree', 0),
            'text_unit_ids': [],
            # Collider metadata
            'type': edge.get('type', edge.get('family', 'relates_to')),
        }

        relationships.append(rel)

    # === TEXT UNITS (source code chunks) ===
    text_units = []
    if include_source:
        for node in nodes:
            body = node.get('body_source', '')
            if body:
                node_id = node.get('id', '')
                text_units.append({
                    'id': f'text_{node_id}',
                    'human_readable_id': len(text_units),
                    'text': body,
                    'n_tokens': len(body.split()),  # Rough estimate
                    'document_ids': [node.get('file_path', 'unknown')],
                    'entity_ids': [node_id],
                    'relationship_ids': [],
                })

    # === WRITE PARQUET ===
    if HAS_PARQUET:
        # Entities
        entities_df = pd.DataFrame(entities)
        entities_df.to_parquet(output_dir / 'entities.parquet', index=False)

        # Relationships
        relationships_df = pd.DataFrame(relationships)
        relationships_df.to_parquet(output_dir / 'relationships.parquet', index=False)

        # Text units (if any)
        if text_units:
            text_units_df = pd.DataFrame(text_units)
            text_units_df.to_parquet(output_dir / 'text_units.parquet', index=False)

        print(f"   Wrote parquet files to {output_dir}/")
    else:
        # Fallback to JSON
        with open(output_dir / 'entities.json', 'w') as f:
            json.dump(entities, f, indent=2)
        with open(output_dir / 'relationships.json', 'w') as f:
            json.dump(relationships, f, indent=2)
        if text_units:
            with open(output_dir / 'text_units.json', 'w') as f:
                json.dump(text_units, f, indent=2)

        print(f"   Wrote JSON files to {output_dir}/ (install pandas+pyarrow for parquet)")

    return {
        'entities': len(entities),
        'relationships': len(relationships),
        'text_units': len(text_units),
    }


def main():
    parser = argparse.ArgumentParser(
        description='Export Collider analysis to Microsoft GraphRAG format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python tools/export_graphrag.py .collider/unified_analysis.json
    python tools/export_graphrag.py analysis.json --output ./graphrag_input
    python tools/export_graphrag.py analysis.json --no-source
        """
    )
    parser.add_argument('input', type=Path, help='Path to unified_analysis.json')
    parser.add_argument('--output', '-o', type=Path, default=None,
                        help='Output directory (default: <input_dir>/graphrag)')
    parser.add_argument('--no-source', action='store_true',
                        help='Exclude source code from text_units')

    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: {args.input} not found")
        sys.exit(1)

    # Default output directory
    if args.output is None:
        args.output = args.input.parent / 'graphrag'

    print(f"Loading {args.input}...")
    analysis = load_analysis(args.input)

    print(f"Exporting to GraphRAG format...")
    counts = export_to_graphrag(
        analysis,
        args.output,
        include_source=not args.no_source
    )

    print(f"\nGraphRAG Export Complete:")
    print(f"   Entities:      {counts['entities']}")
    print(f"   Relationships: {counts['relationships']}")
    print(f"   Text Units:    {counts['text_units']}")
    print(f"\nOutput: {args.output}/")
    print(f"\nTo use with GraphRAG:")
    print(f"   graphrag init --root ./my_project")
    print(f"   cp {args.output}/*.parquet ./my_project/input/")
    print(f"   graphrag index --root ./my_project")


if __name__ == '__main__':
    main()
