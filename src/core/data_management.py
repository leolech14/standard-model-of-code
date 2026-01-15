"""
data_management.py

The Unified Data Layer for the Collider system.
Provides a single source of truth for Codebase State, enforcing schema integrity
and enabling cross-layer data enrichment.

CANONICAL DATA CONVENTIONS (see docs/TOOL.md Part VIII):
- ID Format: file_path::qualified_name (double-colon)
- Confidence: Always 0.0 to 1.0 (never 0-100)
- Validation: At pipeline boundaries
"""

from typing import Dict, List, Any, Optional, Set, Callable, Tuple
from collections import defaultdict
from dataclasses import asdict
from datetime import datetime
import json
import re
from pathlib import Path

from unified_analysis import UnifiedNode, UnifiedEdge, UnifiedAnalysisOutput


# =============================================================================
# VALIDATION HELPERS
# =============================================================================

# Atom format: RING.SUB.TIER (e.g., LOG.FNC.M)
ATOM_PATTERN = re.compile(r'^(LOG|DAT|ORG|EXE|EXT)\.[A-Z]{3}\.[OMCAU]$')
ID_CANONICAL_PATTERN = re.compile(r'^.+::.+$')
ID_LEGACY_PATTERN = re.compile(r'^.+:.+$')


def validate_node(node: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    """Validate a node dict. Returns (errors, warnings)."""
    errors: List[str] = []
    warnings: List[str] = []

    # Required fields
    if not node.get('id'):
        errors.append("Node missing required 'id' field")
    else:
        node_id = str(node["id"])
        if ID_CANONICAL_PATTERN.match(node_id):
            pass
        elif ID_LEGACY_PATTERN.match(node_id):
            warnings.append(f"Legacy id format: {node_id}")
        else:
            warnings.append(f"Non-canonical id format: {node_id}")

    if not node.get('name'):
        errors.append("Node missing required 'name' field")

    # Confidence range (canonical: 0.0-1.0)
    for key, value in node.items():
        if key == "confidence" or key.endswith("_confidence"):
            try:
                numeric = float(value)
            except (TypeError, ValueError):
                errors.append(f"{key} not numeric: {value}")
                continue
            if not 0.0 <= numeric <= 1.0:
                errors.append(f"{key} out of range (0.0-1.0): {value}")

    atom = node.get('atom')
    if atom and isinstance(atom, str) and not ATOM_PATTERN.match(atom):
        warnings.append(f"Atom format mismatch: {atom}")

    return errors, warnings


def validate_edge(edge: Dict[str, Any], node_ids: Set[str]) -> Tuple[List[str], List[str]]:
    """Validate an edge dict. Returns (errors, warnings)."""
    errors: List[str] = []
    warnings: List[str] = []

    if not edge.get('source'):
        errors.append("Edge missing 'source'")
    elif edge['source'] not in node_ids:
        errors.append(f"Edge source not in graph: {edge['source'][:50]}...")

    if not edge.get('target'):
        errors.append("Edge missing 'target'")
    # Target may be external - don't error

    for key, value in edge.items():
        if key == "confidence" or key.endswith("_confidence"):
            try:
                numeric = float(value)
            except (TypeError, ValueError):
                errors.append(f"Edge {key} not numeric: {value}")
                continue
            if not 0.0 <= numeric <= 1.0:
                errors.append(f"Edge {key} out of range 0.0-1.0: {value}")

    return errors, warnings


class CodebaseState:
    """
    Singleton-like container for the entire state of a codebase analysis.
    
    Acts as the central bus for all 'Islands of Analysis' (Purpose, Flow, Perf, etc.)
    to write their results back into a shared, validated graph.
    """
    
    def __init__(self, target_path: str):
        self.target_path = target_path
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {
            "created_at": datetime.now().isoformat(),
            "target": target_path,
            "layers_activated": []
        }

        # === INDEXED LOOKUPS (O(1) access) ===
        self._node_lookup: Dict[str, Dict[str, Any]] = {}
        self._by_file: Dict[str, Set[str]] = defaultdict(set)
        self._by_ring: Dict[str, Set[str]] = defaultdict(set)
        self._by_kind: Dict[str, Set[str]] = defaultdict(set)
        self._by_role: Dict[str, Set[str]] = defaultdict(set)
        self._edges_from: Dict[str, List[int]] = defaultdict(list)
        self._edges_to: Dict[str, List[int]] = defaultdict(list)

    def load_initial_graph(self, nodes: List[Any], edges: List[Any]):
        """
        Load the initial AST/Ref graph from Stage 1-2.
        Accepts dicts or objects (Dataclasses).
        Builds indexes for O(1) lookups.
        """
        # Clear existing
        self.nodes = {}
        self.edges = []
        self._node_lookup = {}
        self._by_file = defaultdict(set)
        self._by_ring = defaultdict(set)
        self._by_kind = defaultdict(set)
        self._by_role = defaultdict(set)
        self._edges_from = defaultdict(list)
        self._edges_to = defaultdict(list)

        # Ingest nodes
        for n in nodes:
            # Normalize to dict
            if hasattr(n, 'to_dict'):
                n_dict = n.to_dict()
            elif hasattr(n, '__dict__'):
                n_dict = vars(n)
            else:
                n_dict = dict(n)

            # Ensure ID
            nid = n_dict.get('id')
            if not nid:
                continue  # Skip invalid nodes

            self.nodes[nid] = n_dict
            self._node_lookup[nid] = n_dict

            # Build indexes
            file_path = n_dict.get('file_path', n_dict.get('file', ''))
            if file_path:
                self._by_file[file_path].add(nid)

            ring = n_dict.get('ring', '')
            if ring:
                self._by_ring[ring].add(nid)

            kind = n_dict.get('kind', '')
            if kind:
                self._by_kind[kind].add(nid)

            role = n_dict.get('role', n_dict.get('type', ''))
            if role:
                self._by_role[role.lower()].add(nid)

        # Ingest edges
        for i, e in enumerate(edges):
            if hasattr(e, 'to_dict'):
                e_dict = e.to_dict()
            elif hasattr(e, '__dict__'):
                e_dict = vars(e)
            else:
                e_dict = dict(e)

            self.edges.append(e_dict)

            # Build edge indexes
            src = e_dict.get('source', '')
            tgt = e_dict.get('target', '')
            if src:
                self._edges_from[src].append(i)
            if tgt:
                self._edges_to[tgt].append(i)

        print(f"  [State] Loaded {len(self.nodes)} nodes and {len(self.edges)} edges.")

    def enrich_node(self, node_id: str, layer_name: str, **attributes):
        """
        Enrich a specific node with semantic data from a layer.
        
        Args:
            node_id: The ID of the node to enrich.
            layer_name: The source of this data (e.g., "purpose", "flow").
            **attributes: Key-value pairs to merge into the node.
        """
        if node_id not in self.nodes:
            # We silently skip enrichment for non-existent nodes to avoid crashing 
            # on transient or virtual nodes created by some sub-systems
            return
            
        node = self.nodes[node_id]
        
        # Merge attributes
        for k, v in attributes.items():
            node[k] = v
            
        # Track layer activation
        if layer_name not in self.metadata["layers_activated"]:
            self.metadata["layers_activated"].append(layer_name)

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """O(1) lookup by ID."""
        return self.nodes.get(node_id)

    # =========================================================================
    # O(1) INDEXED LOOKUPS
    # =========================================================================

    def get_by_file(self, file_path: str) -> List[Dict[str, Any]]:
        """O(1) lookup nodes by file path."""
        ids = self._by_file.get(file_path, set())
        return [self.nodes[nid] for nid in ids if nid in self.nodes]

    def get_by_ring(self, ring: str) -> List[Dict[str, Any]]:
        """O(1) lookup nodes by ring (LOG, DAT, ORG, EXE, EXT)."""
        ids = self._by_ring.get(ring, set())
        return [self.nodes[nid] for nid in ids if nid in self.nodes]

    def get_by_kind(self, kind: str) -> List[Dict[str, Any]]:
        """O(1) lookup nodes by kind (class, function, method, etc.)."""
        ids = self._by_kind.get(kind, set())
        return [self.nodes[nid] for nid in ids if nid in self.nodes]

    def get_by_role(self, role: str) -> List[Dict[str, Any]]:
        """O(1) lookup nodes by role (case-insensitive)."""
        ids = self._by_role.get(role.lower(), set())
        return [self.nodes[nid] for nid in ids if nid in self.nodes]

    def get_edges_from(self, node_id: str) -> List[Dict[str, Any]]:
        """O(1) lookup edges originating from a node."""
        indices = self._edges_from.get(node_id, [])
        return [self.edges[i] for i in indices if i < len(self.edges)]

    def get_edges_to(self, node_id: str) -> List[Dict[str, Any]]:
        """O(1) lookup edges pointing to a node."""
        indices = self._edges_to.get(node_id, [])
        return [self.edges[i] for i in indices if i < len(self.edges)]

    def list_files(self) -> List[str]:
        """List all unique file paths."""
        return list(self._by_file.keys())

    def list_rings(self) -> List[str]:
        """List all rings present in the graph."""
        return list(self._by_ring.keys())

    def list_roles(self) -> List[str]:
        """List all unique roles."""
        return list(self._by_role.keys())

    # =========================================================================
    # VALIDATION
    # =========================================================================

    def validate(self) -> List[str]:
        """
        Comprehensive validation using canonical conventions.
        Returns a list of error messages.

        See docs/TOOL.md Part VIII for canonical data conventions.
        """
        errors, warnings = self.validate_with_warnings()
        if warnings:
            self.metadata["validation_warnings"] = warnings
        return errors

    def validate_with_warnings(self) -> Tuple[List[str], List[str]]:
        """Return (errors, warnings) without mutating state."""
        errors: List[str] = []
        warnings: List[str] = []
        node_ids = set(self.nodes.keys())

        # 1. Node validation
        for node in self.nodes.values():
            node_errors, node_warnings = validate_node(node)
            errors.extend(node_errors)
            warnings.extend(node_warnings)

        # 2. Edge validation (referential integrity)
        for edge in self.edges:
            edge_errors, edge_warnings = validate_edge(edge, node_ids)
            errors.extend(edge_errors)
            warnings.extend(edge_warnings)

        return errors, warnings

    def remove_dangling_edges(self) -> int:
        """Remove edges with non-existent source nodes. Returns count removed."""
        node_ids = set(self.nodes.keys())
        valid_edges = []
        removed = 0

        for edge in self.edges:
            if edge.get('source') in node_ids:
                valid_edges.append(edge)
            else:
                removed += 1

        if removed > 0:
            self.edges = valid_edges
            # Rebuild edge indexes
            self._edges_from = defaultdict(list)
            self._edges_to = defaultdict(list)
            for i, e in enumerate(self.edges):
                src = e.get('source', '')
                tgt = e.get('target', '')
                if src:
                    self._edges_from[src].append(i)
                if tgt:
                    self._edges_to[tgt].append(i)

        return removed

    def export(self) -> Dict[str, Any]:
        """
        Export the fully reconciled state as a unified dictionary
        ready for visualization or JSON dump.
        """
        return {
            "nodes": list(self.nodes.values()),
            "edges": self.edges,
            "metadata": self.metadata
        }
