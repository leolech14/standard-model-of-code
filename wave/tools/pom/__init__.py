"""
Projectome Omniscience Module (POM)

Complete visibility across PROJECTOME = CODOME ⊔ CONTEXTOME

Usage:
    from pom import ProjectomeOmniscience

    pom = ProjectomeOmniscience("/path/to/project")
    manifest = pom.scan()
    pom.save_manifest("projectome_manifest.yaml")

Mathematical Foundation:
    P = C ⊔ X is MATHEMATICALLY NECESSARY (Lawvere 1969)
    See: docs/theory/FOUNDATIONS_INTEGRATION.md
"""

from .projectome_omniscience import (
    ProjectomeOmniscience,
    Universe,
    SymmetryState,
    EntityType,
    Layer,
    Entity,
    Purpose,
    Edge,
    Location,
    ProjectomeManifest,
    SymmetryReport,
    PurposeFieldResult,
)

__version__ = "1.0.0"
__all__ = [
    "ProjectomeOmniscience",
    "Universe",
    "SymmetryState",
    "EntityType",
    "Layer",
    "Entity",
    "Purpose",
    "Edge",
    "Location",
    "ProjectomeManifest",
    "SymmetryReport",
    "PurposeFieldResult",
]
