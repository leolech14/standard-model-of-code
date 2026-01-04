#!/usr/bin/env python3
"""
Dimension Enricher (Backward Compatibility Module)
==================================================

This module re-exports from the refactored dimensions package.
New code should import from src.core.dimensions directly.

Old:
    from dimension_enricher import DimensionEnricher, DimensionVector

New:
    from dimensions import DimensionEnricher, DimensionVector
"""

# Re-export everything from the new package for backward compatibility
from dimensions import (
    DimensionEnricher,
    DimensionVector,
    StructuralDimensionDetector,
    BehavioralDimensionDetector,
    SemanticDimensionDetector,
    LAYERS,
    BOUNDARIES,
    STATES,
    EFFECTS,
    LIFECYCLES,
)

__all__ = [
    'DimensionEnricher',
    'DimensionVector',
    'StructuralDimensionDetector',
    'BehavioralDimensionDetector',
    'SemanticDimensionDetector',
    'LAYERS',
    'BOUNDARIES',
    'STATES',
    'EFFECTS',
    'LIFECYCLES',
]


# CLI for backward compatibility
if __name__ == "__main__":
    import json

    # Test with sample nodes
    sample_nodes = [
        {
            "id": "1",
            "name": "getUserById",
            "kind": "function",
            "role": "Query",
            "role_confidence": 0.92,
            "file_path": "src/domain/users/queries.py",
            "params": [{"name": "user_id", "type": "str"}],
            "body_source": "def getUserById(user_id: str):\n    return db.query(User).filter_by(id=user_id).first()"
        },
        {
            "id": "2",
            "name": "createUser",
            "kind": "function",
            "role": "Creator",
            "role_confidence": 0.88,
            "file_path": "src/application/commands/user_commands.py",
            "params": [{"name": "data", "type": "dict"}],
            "body_source": "def createUser(data: dict):\n    user = User(**data)\n    db.add(user)\n    db.commit()\n    return user"
        },
        {
            "id": "3",
            "name": "UserRepository",
            "kind": "class",
            "role": "Repository",
            "role_confidence": 0.95,
            "file_path": "src/infrastructure/repositories/user_repository.py",
            "body_source": "class UserRepository:\n    def __init__(self, db):\n        self.db = db\n    def find_by_id(self, id):\n        return self.db.query(User).get(id)"
        }
    ]

    enricher = DimensionEnricher()
    enriched_nodes = enricher.enrich_nodes(sample_nodes)

    print(" DIMENSION ENRICHMENT TEST\n")
    for node in enriched_nodes:
        print(f"Node: {node['name']}")
        print(f"  Dimensions: {json.dumps(node['dimensions'], indent=4)}")
        print()
