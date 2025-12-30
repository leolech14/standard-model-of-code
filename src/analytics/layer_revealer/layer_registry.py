"""
Layer Registry
==============

Static layer definitions and metadata for the 8-layer progressive revelation system.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict


@dataclass
class LayerInfo:
    """Information about a single layer."""
    name: str
    level: int
    description: str
    key_fields: List[str]
    requires: Optional[str]
    reveals: str


# The 8 Layers of Progressive Revelation
LAYERS: Dict[str, LayerInfo] = {
    "L0_RAW": LayerInfo(
        name="Raw AST",
        level=0,
        description="Pure syntax parse - AST nodes",
        key_fields=["node_type", "text", "start_byte", "end_byte"],
        requires=None,
        reveals="Syntax structure"
    ),
    "L1_STRUCTURAL": LayerInfo(
        name="Structural",
        level=1,
        description="Identity and location in codebase",
        key_fields=["id", "name", "kind", "file_path", "start_line", "complexity", "body_source"],
        requires="L0_RAW",
        reveals="What exists and where"
    ),
    "L2_CLASSIFICATION": LayerInfo(
        name="Classification",
        level=2,
        description="Role, atom type, architectural layer",
        key_fields=["role", "role_confidence", "atom_type", "arch_layer", "discovery_method"],
        requires="L1_STRUCTURAL",
        reveals="What kind of thing it is"
    ),
    "L3_DIMENSION": LayerInfo(
        name="8D Coordinates",
        level=3,
        description="8-dimensional classification space",
        key_fields=["D1_WHAT", "D2_LAYER", "D3_ROLE", "D4_BOUNDARY", "D5_STATE", "D6_EFFECT", "D7_LIFECYCLE", "D8_TRUST"],
        requires="L2_CLASSIFICATION",
        reveals="Position in 8D space"
    ),
    "L4_LENS": LayerInfo(
        name="8L Perspectives",
        level=4,
        description="8 epistemic lenses for interrogation",
        key_fields=["R1_IDENTITY", "R2_ONTOLOGY", "R3_CLASSIFICATION", "R4_COMPOSITION", "R5_RELATIONSHIPS", "R6_TRANSFORMATION", "R7_SEMANTICS", "R8_EPISTEMOLOGY"],
        requires="L3_DIMENSION",
        reveals="How to understand it"
    ),
    "L5_GRAPH": LayerInfo(
        name="Graph Structure",
        level=5,
        description="Relationships and edges",
        key_fields=["in_degree", "out_degree", "fan_in", "fan_out", "is_hub", "is_authority", "is_orphan"],
        requires="L4_LENS",
        reveals="How things connect"
    ),
    "L6_MATH": LayerInfo(
        name="4 Pillars",
        level=6,
        description="Mathematical metrics (Omega, pi, S, Nash)",
        key_fields=["omega", "coderank", "spaghetti_score", "nash_equilibrium", "is_optimal"],
        requires="L5_GRAPH",
        reveals="Quantitative quality"
    ),
    "L7_SEMANTIC": LayerInfo(
        name="Semantic",
        level=7,
        description="Meaning, intent, purpose",
        key_fields=["purpose", "intent", "responsibility", "is_clean", "warnings", "improvements"],
        requires="L6_MATH",
        reveals="What it means"
    )
}


def get_layer(layer_id: str) -> Optional[LayerInfo]:
    """Get layer info by ID."""
    return LAYERS.get(layer_id)


def get_all_layer_ids() -> List[str]:
    """Get all layer IDs in order."""
    return list(LAYERS.keys())


def get_layer_by_level(level: int) -> Optional[LayerInfo]:
    """Get layer info by level number."""
    for layer_id, info in LAYERS.items():
        if info.level == level:
            return info
    return None
