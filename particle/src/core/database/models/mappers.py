"""
Object-Relational Mappers for Collider Database.

Maps between:
- UnifiedNode/UnifiedEdge ↔ Database rows
- Analysis results ↔ DB storage format

Design principles:
1. Flatten core fields for efficient queries
2. Store flexible/optional data as JSON
3. Preserve all original data (no lossy conversion)
"""
import json
import warnings
from typing import Dict, Any, List, Optional, Tuple, Iterator, Generator
from dataclasses import dataclass


# Core fields stored as columns (not in JSON)
NODE_CORE_FIELDS = {
    "id", "name", "kind", "file_path", "start_line", "end_line",
    "role", "role_confidence", "atom", "ring", "level",
    "in_degree", "out_degree", "pagerank", "betweenness",
    "complexity", "q_score"
}

# Dimension fields (stored separately in dimensions_json)
DIMENSION_FIELDS = {
    "D1_structural_role", "D2_data_or_logic", "D3_scope",
    "D4_lifecycle", "D5_dependency", "D6_pure_score",
    "D7_visibility", "D8_purpose_field"
}

EDGE_CORE_FIELDS = {
    "source_id", "target_id", "edge_type", "weight", "confidence"
}


def node_to_row(node: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a node dict to database row format.

    Args:
        node: Full node dict from analysis.

    Returns:
        Dict with flattened core fields + JSON columns.
    """
    row = {}

    # Core fields
    row["id"] = node.get("id", "")
    row["name"] = node.get("name", "")
    row["kind"] = node.get("kind") or node.get("type")
    row["file_path"] = node.get("file_path") or node.get("file")
    row["start_line"] = node.get("start_line") or node.get("line")
    row["end_line"] = node.get("end_line")

    # Standard Model fields
    row["role"] = node.get("role")
    row["role_confidence"] = node.get("role_confidence") or node.get("confidence")
    row["atom"] = node.get("atom")
    row["ring"] = node.get("ring")
    row["level"] = node.get("level")

    # Graph metrics
    row["in_degree"] = node.get("in_degree", 0)
    row["out_degree"] = node.get("out_degree", 0)
    row["pagerank"] = node.get("pagerank")
    row["betweenness"] = node.get("betweenness")

    # Quality metrics
    row["complexity"] = node.get("complexity") or node.get("cyclomatic_complexity")
    row["q_score"] = node.get("q_score") or node.get("D6_pure_score")

    # Dimensions as JSON
    dimensions = {}
    for dim in DIMENSION_FIELDS:
        if dim in node:
            dimensions[dim] = node[dim]
    row["dimensions_json"] = json.dumps(dimensions) if dimensions else None

    # Everything else goes in metadata_json
    metadata = {}
    for k, v in node.items():
        if k not in NODE_CORE_FIELDS and k not in DIMENSION_FIELDS:
            try:
                json.dumps(v)
                metadata[k] = v
            except (TypeError, ValueError) as e:
                # Warn about non-serializable values being converted to strings
                warnings.warn(
                    f"Node '{node.get('id', 'unknown')}': field '{k}' is not JSON-serializable "
                    f"({type(v).__name__}), converting to string. Error: {e}",
                    category=UserWarning,
                    stacklevel=2
                )
                metadata[k] = str(v)
    row["metadata_json"] = json.dumps(metadata) if metadata else None

    return row


def row_to_node(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a database row back to a node dict.

    Args:
        row: Database row dict.

    Returns:
        Full node dict.
    """
    node = {}

    # Core fields
    for field in NODE_CORE_FIELDS:
        if field in row and row[field] is not None:
            node[field] = row[field]

    # Parse dimensions
    if row.get("dimensions_json"):
        try:
            dimensions = json.loads(row["dimensions_json"])
            node.update(dimensions)
        except (json.JSONDecodeError, TypeError):
            pass

    # Parse metadata
    if row.get("metadata_json"):
        try:
            metadata = json.loads(row["metadata_json"])
            node.update(metadata)
        except (json.JSONDecodeError, TypeError):
            pass

    return node


def edge_to_row(edge: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert an edge dict to database row format.

    Args:
        edge: Full edge dict from analysis.

    Returns:
        Dict with core fields + JSON metadata.
    """
    row = {
        "source_id": edge.get("source", ""),
        "target_id": edge.get("target", ""),
        "edge_type": edge.get("type") or edge.get("edge_type") or "unknown",
        "weight": edge.get("weight", 1.0),
        "confidence": edge.get("confidence"),
    }

    # Everything else goes in metadata
    metadata = {}
    for k, v in edge.items():
        if k not in {"source", "target", "type", "edge_type", "weight", "confidence"}:
            try:
                json.dumps(v)
                metadata[k] = v
            except (TypeError, ValueError) as e:
                # Warn about non-serializable values being converted to strings
                edge_id = f"{edge.get('source', '?')}->{edge.get('target', '?')}"
                warnings.warn(
                    f"Edge '{edge_id}': field '{k}' is not JSON-serializable "
                    f"({type(v).__name__}), converting to string. Error: {e}",
                    category=UserWarning,
                    stacklevel=2
                )
                metadata[k] = str(v)

    row["metadata_json"] = json.dumps(metadata) if metadata else None
    return row


def row_to_edge(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a database row back to an edge dict.

    Args:
        row: Database row dict.

    Returns:
        Full edge dict.
    """
    edge = {
        "source": row.get("source_id", ""),
        "target": row.get("target_id", ""),
        "type": row.get("edge_type"),
        "weight": row.get("weight", 1.0),
    }

    if row.get("confidence") is not None:
        edge["confidence"] = row["confidence"]

    if row.get("metadata_json"):
        try:
            metadata = json.loads(row["metadata_json"])
            edge.update(metadata)
        except (json.JSONDecodeError, TypeError):
            pass

    return edge


def iter_nodes_to_rows(nodes: List[Dict[str, Any]], run_id: str) -> Generator[Tuple, None, None]:
    """
    Generate row tuples from nodes for memory-efficient insertion.

    Args:
        nodes: Iterable of node dicts.
        run_id: Analysis run ID.

    Yields:
        Tuples in column order for bulk insert.
    """
    for node in nodes:
        row = node_to_row(node)
        yield (
            row["id"],
            run_id,
            row["name"],
            row["kind"],
            row["file_path"],
            row["start_line"],
            row["end_line"],
            row["role"],
            row["role_confidence"],
            row["atom"],
            row["ring"],
            row["level"],
            row["in_degree"],
            row["out_degree"],
            row["pagerank"],
            row["betweenness"],
            row["complexity"],
            row["q_score"],
            row["dimensions_json"],
            row["metadata_json"],
        )


def iter_edges_to_rows(edges: List[Dict[str, Any]], run_id: str) -> Generator[Tuple, None, None]:
    """
    Generate row tuples from edges for memory-efficient insertion.

    Args:
        edges: Iterable of edge dicts.
        run_id: Analysis run ID.

    Yields:
        Tuples in column order for bulk insert.
    """
    for edge in edges:
        row = edge_to_row(edge)
        yield (
            run_id,
            row["source_id"],
            row["target_id"],
            row["edge_type"],
            row["weight"],
            row["confidence"],
            row["metadata_json"],
        )


def batch_nodes_to_rows(nodes: List[Dict[str, Any]], run_id: str) -> List[Tuple]:
    """
    Convert batch of nodes to row tuples for efficient insertion.

    Note: For large datasets, use iter_nodes_to_rows() instead to avoid
    loading all rows into memory at once.

    Args:
        nodes: List of node dicts.
        run_id: Analysis run ID.

    Returns:
        List of tuples in column order for bulk insert.
    """
    return list(iter_nodes_to_rows(nodes, run_id))


def batch_edges_to_rows(edges: List[Dict[str, Any]], run_id: str) -> List[Tuple]:
    """
    Convert batch of edges to row tuples for efficient insertion.

    Note: For large datasets, use iter_edges_to_rows() instead to avoid
    loading all rows into memory at once.

    Args:
        edges: List of edge dicts.
        run_id: Analysis run ID.

    Returns:
        List of tuples in column order for bulk insert.
    """
    return list(iter_edges_to_rows(edges, run_id))
