"""
Feature Registry for Collider Database Layer.

Provides discoverability of all database features, their defaults,
CLI flags, and status (stable, beta, experimental).
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class Feature:
    """A discoverable database feature."""
    id: str
    description: str
    default: bool
    cli: str
    status: str = "stable"  # stable, beta, experimental
    requires: Optional[List[str]] = None  # Feature IDs this depends on

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for JSON serialization."""
        return {
            "id": self.id,
            "description": self.description,
            "default": self.default,
            "cli": self.cli,
            "status": self.status,
            "requires": self.requires or [],
        }


class FeatureRegistry:
    """
    Registry of all Collider database features.

    Features are categorized as:
    - stable: Production-ready, default ON where sensible
    - beta: Working but may change
    - experimental: Under development, use with caution
    """

    FEATURES: List[Feature] = [
        # Core features (default ON)
        Feature(
            id="database",
            description="Enable database persistence for analysis results",
            default=True,
            cli="--db/--no-db",
        ),
        Feature(
            id="sqlite",
            description="SQLite backend (default database)",
            default=True,
            cli="--db-backend sqlite",
        ),
        Feature(
            id="incremental",
            description="Skip unchanged files on re-analysis (BLAKE3 hashing)",
            default=True,
            cli="--incremental/--no-incremental",
        ),
        Feature(
            id="history",
            description="Keep history of analysis runs",
            default=True,
            cli="--keep-history/--no-history",
        ),

        # Search features (default OFF)
        Feature(
            id="search",
            description="Tantivy full-text search indexing",
            default=False,
            cli="--search",
            status="beta",
            requires=["database"],
        ),

        # =====================================================================
        # Multi-Layer Graph Features (SMC Axiom E2 + G1 support)
        # These support the four flow substances and three observers
        # Status: planned = reserved, not yet implemented
        # =====================================================================

        # Layer 1: Runtime Flow (Operational Observer)
        Feature(
            id="runtime_metrics",
            description="Store execution/profiling data per node (OpenTelemetry, cProfile)",
            default=False,
            cli="--runtime-metrics",
            status="planned",
            requires=["database"],
        ),

        # Layer 2: Change Flow (Temporal Observer)
        Feature(
            id="temporal_analysis",
            description="Compute temporal coupling from git history (PyDriller)",
            default=False,
            cli="--temporal-analysis",
            status="planned",
            requires=["database"],
        ),

        # Layer 3: Human Flow (Knowledge Observer)
        Feature(
            id="social_graph",
            description="Track authorship, ownership, truck factor, knowledge islands",
            default=False,
            cli="--social-graph",
            status="planned",
            requires=["database"],
        ),

        # Layer 4: Operational Flow (Incident Bridge)
        Feature(
            id="operational_bridge",
            description="Link incidents, deployments, DORA metrics to code",
            default=False,
            cli="--operational-bridge",
            status="planned",
            requires=["database"],
        ),

        # Multi-layer edge storage
        Feature(
            id="dynamic_edges",
            description="Store edges discovered at runtime/from history (not static)",
            default=False,
            cli="--dynamic-edges",
            status="planned",
            requires=["database"],
        ),
    ]

    @classmethod
    def list_features(cls) -> List[Dict[str, Any]]:
        """Return all features as dicts."""
        return [f.to_dict() for f in cls.FEATURES]

    @classmethod
    def get_feature(cls, feature_id: str) -> Optional[Feature]:
        """Get a feature by ID."""
        for f in cls.FEATURES:
            if f.id == feature_id:
                return f
        return None

    @classmethod
    def get_default_on(cls) -> List[Feature]:
        """Get features that are enabled by default."""
        return [f for f in cls.FEATURES if f.default]

    @classmethod
    def get_optional(cls) -> List[Feature]:
        """Get features that are disabled by default."""
        return [f for f in cls.FEATURES if not f.default]

    @classmethod
    def print_features(cls):
        """Print feature table for --list-features CLI."""
        print("\nCollider Database Features:")
        print("=" * 70)
        print(f"{'Feature':<15} {'Default':<10} {'Status':<12} {'CLI':<25}")
        print("-" * 70)
        for f in cls.FEATURES:
            default_str = "ON" if f.default else "OFF"
            print(f"{f.id:<15} {default_str:<10} {f.status:<12} {f.cli:<25}")
        print("-" * 70)
        print("\nUse these flags with 'collider full' to enable/disable features.")
        print("Example: collider full . --db --incremental --search")
