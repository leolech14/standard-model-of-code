#!/usr/bin/env python3
"""
Subsystem Registry - Refinery Component Catalog
================================================

Definitive registry of all Refinery subsystems.

Like LOL (List of Lists) for entities, this is the definitive registry
of what subsystems exist, their responsibilities, their health, and how
to access them.

Philosophy: "A system that knows itself completely."

Usage:
    from refinery.subsystem_registry import SUBSYSTEMS, get_subsystem

    # List all subsystems
    for subsystem in SUBSYSTEMS:
        print(f"{subsystem.name}: {subsystem.purpose}")

    # Get specific subsystem
    scanner = get_subsystem("scanner")
    scanner.scan()
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
import importlib.util
import sys

# Paths
REFINERY_DIR = Path(__file__).parent
PROJECT_ROOT = REFINERY_DIR.parent.parent.parent


class SubsystemStatus(Enum):
    """Subsystem operational status."""
    WORKING = "working"          # Implemented and tested
    PARTIAL = "partial"          # Partially implemented
    MISSING = "missing"          # Designed but not built
    DEPRECATED = "deprecated"    # Being phased out


@dataclass
class Subsystem:
    """
    Complete description of a Refinery subsystem.

    This is the DEFINITIVE record of what subsystems exist.
    """
    # Identity
    name: str                    # Subsystem name (scanner, chunker, etc.)
    module_path: str             # Python module path
    purpose: str                 # One-line description

    # Classification
    layer: str                   # Input, Processing, Synthesis, Query, Output
    dependencies: List[str]      # Other subsystems it depends on

    # Status
    status: SubsystemStatus      # WORKING, PARTIAL, MISSING, DEPRECATED
    lines_of_code: int           # Approximate size
    last_modified: str           # ISO timestamp

    # Functionality
    inputs: List[str]            # What it consumes
    outputs: List[str]           # What it produces
    functions: List[str]         # Key functions it provides

    # Health
    healthy: bool = True         # Is it working?
    issues: List[str] = None     # Known problems

    def __post_init__(self):
        if self.issues is None:
            self.issues = []

    def load(self) -> Any:
        """Dynamically load the subsystem module."""
        if self.status == SubsystemStatus.MISSING:
            raise ImportError(f"Subsystem '{self.name}' not yet implemented")

        module_file = PROJECT_ROOT / self.module_path
        if not module_file.exists():
            raise FileNotFoundError(f"Module not found: {module_file}")

        spec = importlib.util.spec_from_file_location(self.name, module_file)
        if not spec or not spec.loader:
            raise ImportError(f"Failed to load spec for {self.name}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[self.name] = module
        spec.loader.exec_module(module)

        return module


# ============================================================================
# SUBSYSTEM REGISTRY - THE DEFINITIVE LIST
# ============================================================================

SUBSYSTEMS = [

    # ========================================================================
    # INPUT LAYER - Discovery
    # ========================================================================

    Subsystem(
        name="scanner",
        module_path="context-management/tools/refinery/corpus_inventory.py",
        purpose="Discover all files, classify, map boundaries, detect changes",
        layer="Input",
        dependencies=[],
        status=SubsystemStatus.PARTIAL,
        lines_of_code=300,
        last_modified="2026-01-24",
        inputs=["File system"],
        outputs=["corpus_inventory.json", "boundaries.json", "delta_report.json"],
        functions=["scan_files()", "classify_files()", "map_boundaries()", "detect_deltas()"],
        healthy=True,
        issues=["Currently split across 3 files (corpus_inventory, boundary_mapper, delta_detector)"]
    ),

    # ========================================================================
    # PROCESSING LAYER - Atomization
    # ========================================================================

    Subsystem(
        name="chunker",
        module_path="context-management/tools/ai/aci/refinery.py",
        purpose="Break files into semantic chunks with validation",
        layer="Processing",
        dependencies=["scanner"],
        status=SubsystemStatus.WORKING,
        lines_of_code=800,
        last_modified="2026-01-27",
        inputs=["File content"],
        outputs=["agent_chunks.json", "core_chunks.json", "aci_chunks.json"],
        functions=["chunk_file()", "validate_chunks()", "export_with_validation()"],
        healthy=True,
        issues=[]
    ),

    # ========================================================================
    # PROCESSING LAYER - Indexing
    # ========================================================================

    Subsystem(
        name="indexer",
        module_path="context-management/tools/refinery/indexer.py",
        purpose="Build search indexes (text, vector, metadata) for fast queries",
        layer="Processing",
        dependencies=["chunker"],
        status=SubsystemStatus.MISSING,
        lines_of_code=0,
        last_modified=None,
        inputs=["*_chunks.json"],
        outputs=["text_index.json", "vector_index.npy", "metadata_index.json"],
        functions=["build_text_index()", "build_vector_index()", "update_incremental()"],
        healthy=False,
        issues=["Not implemented - currently brute-force search through JSON"]
    ),

    # ========================================================================
    # QUERY LAYER - Retrieval
    # ========================================================================

    Subsystem(
        name="querier",
        module_path="context-management/tools/refinery/query_chunks.py",
        purpose="Search and retrieve relevant chunks with ranking",
        layer="Query",
        dependencies=["indexer"],
        status=SubsystemStatus.PARTIAL,
        lines_of_code=165,
        last_modified="2026-01-27",
        inputs=["Query string", "Indexes"],
        outputs=["Ranked search results"],
        functions=["text_search()", "semantic_search()", "rank_results()"],
        healthy=True,
        issues=["Text search works, semantic search not implemented (no indexer)"]
    ),

    # ========================================================================
    # SYNTHESIS LAYER - Consolidation
    # ========================================================================

    Subsystem(
        name="synthesizer",
        module_path="context-management/tools/refinery/state_synthesizer.py",
        purpose="Consolidate all outputs into single coherent state (live.yaml)",
        layer="Synthesis",
        dependencies=["scanner", "chunker", "indexer"],
        status=SubsystemStatus.WORKING,
        lines_of_code=300,
        last_modified="2026-01-27",
        inputs=["corpus_inventory.json", "boundaries.json", "chunks/*.json"],
        outputs=["live.yaml", "atoms (future)"],
        functions=["synthesize_state()", "calculate_health()", "generate_atoms()"],
        healthy=True,
        issues=["Should absorb atom_generator.py (currently separate)"]
    ),

    # ========================================================================
    # OUTPUT LAYER - Observability
    # ========================================================================

    Subsystem(
        name="reporter",
        module_path="context-management/tools/refinery/refinery_report.py",
        purpose="Generate human-readable reports (activity, library, changes)",
        layer="Output",
        dependencies=["synthesizer", "querier"],
        status=SubsystemStatus.WORKING,
        lines_of_code=230,
        last_modified="2026-01-27",
        inputs=["live.yaml", "chunks/*.json", "watcher logs"],
        outputs=["Activity reports", "Library views", "Change logs"],
        functions=["activity_report()", "library_view()", "changes_log()"],
        healthy=True,
        issues=[]
    ),
]


# Legacy subsystems (to be consolidated or removed)
DEPRECATED_SUBSYSTEMS = [
    Subsystem(
        name="boundary_mapper",
        module_path="context-management/tools/refinery/boundary_mapper.py",
        purpose="Map analysis_sets.yaml to boundaries (SHOULD BE IN SCANNER)",
        layer="Input",
        dependencies=[],
        status=SubsystemStatus.DEPRECATED,
        lines_of_code=230,
        last_modified="2026-01-24",
        inputs=["analysis_sets.yaml"],
        outputs=["boundaries.json"],
        functions=["map_boundaries()"],
        healthy=True,
        issues=["Should merge into scanner.py"]
    ),

    Subsystem(
        name="delta_detector",
        module_path="context-management/tools/refinery/delta_detector.py",
        purpose="Detect file changes (SHOULD BE IN SCANNER)",
        layer="Input",
        dependencies=[],
        status=SubsystemStatus.DEPRECATED,
        lines_of_code=240,
        last_modified="2026-01-24",
        inputs=["File system"],
        outputs=["delta_report.json"],
        functions=["detect_deltas()"],
        healthy=True,
        issues=["Should merge into scanner.py"]
    ),

    Subsystem(
        name="atom_generator",
        module_path="context-management/tools/refinery/atom_generator.py",
        purpose="Generate boundary atoms (SHOULD BE IN SYNTHESIZER)",
        layer="Synthesis",
        dependencies=["scanner"],
        status=SubsystemStatus.DEPRECATED,
        lines_of_code=390,
        last_modified="2026-01-24",
        inputs=["boundaries.json"],
        outputs=["atoms_*.json"],
        functions=["generate_atoms()"],
        healthy=True,
        issues=["Redundant - atoms are just boundary aggregations"]
    ),
]


# ============================================================================
# SUBSYSTEM REGISTRY API
# ============================================================================

def get_subsystem(name: str) -> Optional[Subsystem]:
    """Get subsystem by name."""
    for subsystem in SUBSYSTEMS:
        if subsystem.name == name:
            return subsystem
    return None


def list_subsystems(layer: Optional[str] = None, status: Optional[SubsystemStatus] = None) -> List[Subsystem]:
    """List subsystems, optionally filtered."""
    results = SUBSYSTEMS.copy()

    if layer:
        results = [s for s in results if s.layer == layer]

    if status:
        results = [s for s in results if s.status == status]

    return results


def get_subsystem_health() -> Dict[str, Any]:
    """Get health summary of all subsystems."""
    total = len(SUBSYSTEMS)
    working = len([s for s in SUBSYSTEMS if s.status == SubsystemStatus.WORKING])
    partial = len([s for s in SUBSYSTEMS if s.status == SubsystemStatus.PARTIAL])
    missing = len([s for s in SUBSYSTEMS if s.status == SubsystemStatus.MISSING])

    healthy = len([s for s in SUBSYSTEMS if s.healthy])

    return {
        "total_subsystems": total,
        "working": working,
        "partial": partial,
        "missing": missing,
        "healthy": healthy,
        "unhealthy": total - healthy,
        "completeness": working / total if total > 0 else 0,
        "deprecated_count": len(DEPRECATED_SUBSYSTEMS)
    }


def get_dependency_graph() -> Dict[str, List[str]]:
    """Get subsystem dependency graph."""
    graph = {}
    for subsystem in SUBSYSTEMS:
        graph[subsystem.name] = subsystem.dependencies
    return graph


def topological_order() -> List[str]:
    """Get subsystems in dependency order (no subsystem before its dependencies)."""
    graph = get_dependency_graph()
    order = []
    visited = set()

    def visit(name: str):
        if name in visited:
            return
        visited.add(name)
        for dep in graph.get(name, []):
            visit(dep)
        order.append(name)

    for name in graph.keys():
        visit(name)

    return order


# ============================================================================
# CLI INTERFACE
# ============================================================================

def print_registry():
    """Print complete subsystem registry."""
    print("=" * 70)
    print("REFINERY SUBSYSTEM REGISTRY")
    print("=" * 70)
    print()

    health = get_subsystem_health()
    print(f"Total Subsystems: {health['total_subsystems']}")
    print(f"Working: {health['working']} | Partial: {health['partial']} | Missing: {health['missing']}")
    print(f"Completeness: {health['completeness']:.0%}")
    print()

    # Group by layer
    layers = {}
    for subsystem in SUBSYSTEMS:
        if subsystem.layer not in layers:
            layers[subsystem.layer] = []
        layers[subsystem.layer].append(subsystem)

    for layer_name in ["Input", "Processing", "Query", "Synthesis", "Output"]:
        if layer_name not in layers:
            continue

        print(f"## {layer_name.upper()} LAYER")
        print()

        for subsystem in layers[layer_name]:
            status_icon = {
                SubsystemStatus.WORKING: "✅",
                SubsystemStatus.PARTIAL: "⚠️",
                SubsystemStatus.MISSING: "❌",
                SubsystemStatus.DEPRECATED: "🔄"
            }.get(subsystem.status, "❓")

            health_icon = "💚" if subsystem.healthy else "🔴"

            print(f"  {status_icon} {health_icon} **{subsystem.name.upper()}**")
            print(f"     Purpose: {subsystem.purpose}")
            print(f"     Status: {subsystem.status.value}")
            print(f"     Module: {subsystem.module_path}")
            print(f"     Inputs: {', '.join(subsystem.inputs)}")
            print(f"     Outputs: {', '.join(subsystem.outputs)}")
            print(f"     Size: ~{subsystem.lines_of_code} lines")

            if subsystem.issues:
                print(f"     Issues: {'; '.join(subsystem.issues)}")

            print()

    # Deprecated
    if DEPRECATED_SUBSYSTEMS:
        print("## DEPRECATED (To Be Consolidated)")
        print()
        for subsystem in DEPRECATED_SUBSYSTEMS:
            print(f"  🔄 {subsystem.name}")
            print(f"     Reason: {subsystem.issues[0] if subsystem.issues else 'N/A'}")
            print()

    print("=" * 70)


def print_dependency_graph():
    """Print subsystem dependency graph."""
    print("=" * 70)
    print("SUBSYSTEM DEPENDENCY GRAPH")
    print("=" * 70)
    print()

    order = topological_order()

    print("Execution Order (bottom-up):")
    print()

    for i, name in enumerate(order, 1):
        subsystem = get_subsystem(name)
        if not subsystem:
            continue

        deps = subsystem.dependencies
        dep_str = f"depends on: {', '.join(deps)}" if deps else "no dependencies"

        print(f"  {i}. {name.upper():15} ({dep_str})")

    print()
    print("=" * 70)


def main():
    """CLI interface."""
    import argparse

    parser = argparse.ArgumentParser(description="Subsystem Registry - Registry of Refinery Subsystems")
    parser.add_argument("--list", action="store_true", help="List all subsystems")
    parser.add_argument("--deps", action="store_true", help="Show dependency graph")
    parser.add_argument("--health", action="store_true", help="Health summary")
    parser.add_argument("--load", type=str, help="Load and inspect subsystem")

    args = parser.parse_args()

    if args.deps:
        print_dependency_graph()
    elif args.health:
        health = get_subsystem_health()
        print(f"Subsystems: {health['total_subsystems']}")
        print(f"Working: {health['working']}")
        print(f"Partial: {health['partial']}")
        print(f"Missing: {health['missing']}")
        print(f"Completeness: {health['completeness']:.0%}")
    elif args.load:
        subsystem = get_subsystem(args.load)
        if not subsystem:
            print(f"Subsystem '{args.load}' not found")
            return 1

        try:
            module = subsystem.load()
            print(f"✅ Loaded {subsystem.name}")
            print(f"   Module: {module}")
            print(f"   Functions: {', '.join(dir(module)[:10])}")
        except Exception as e:
            print(f"❌ Failed to load: {e}")
            return 1
    else:
        print_registry()

    return 0


if __name__ == "__main__":
    sys.exit(main())
