"""
Lens Interrogator (Backward Compatibility Module)
=================================================

This module re-exports from the refactored lenses package.
New code should import from src.core.lenses directly.

Old:
    from lens_interrogator import LensInterrogator, LensInquiry

New:
    from lenses import LensInterrogator, LensInquiry
"""

# Re-export everything from the new package for backward compatibility
from lenses import (
    LensInterrogator,
    LensInquiry,
    StructuralLens,
    BehavioralLens,
    SemanticLens,
)

__all__ = [
    'LensInterrogator',
    'LensInquiry',
    'StructuralLens',
    'BehavioralLens',
    'SemanticLens',
]


# CLI for backward compatibility
if __name__ == "__main__":
    import json

    test_node = {
        "id": "user_repo_1",
        "name": "getUserById",
        "kind": "function",
        "file_path": "src/domain/users/repository.py",
        "start_line": 42,
        "role": "Query",
        "role_confidence": 92.0,
        "discovery_method": "pattern",
        "params": [{"name": "user_id", "type": "int"}],
        "return_type": "Optional[User]",
        "docstring": "Retrieve a user by their unique identifier.",
        "signature": "getUserById(user_id: int) -> Optional[User]",
        "complexity": 3,
        "lines_of_code": 5,
        "decorators": ["@cache"],
        "dimensions": {
            "D1_WHAT": "FunctionDef",
            "D2_LAYER": "Core",
            "D6_EFFECT": "Read",
        }
    }

    test_edges = [
        {"source": "user_repo_1", "target": "db_connection", "edge_type": "calls"},
        {"source": "user_service", "target": "user_repo_1", "edge_type": "calls"},
    ]

    interrogator = LensInterrogator()
    inquiry = interrogator.interrogate(test_node, test_edges)

    print("8-LENS INTERROGATION")
    print("=" * 60)
    print(json.dumps(inquiry.to_dict(), indent=2))
