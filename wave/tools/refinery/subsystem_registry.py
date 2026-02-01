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

import yaml

# Paths
REFINERY_DIR = Path(__file__).parent
PROJECT_ROOT = REFINERY_DIR.parent.parent.parent
CONFIG_PATH = PROJECT_ROOT / "wave" / "config" / "registries" / "REFINERY_INTERNAL.yaml"


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
    """
    name: str
    module_path: str
    purpose: str
    layer: str
    dependencies: List[str]
    status: SubsystemStatus
    lines_of_code: int
    last_modified: str
    inputs: List[str]
    outputs: List[str]
    functions: List[str]
    healthy: bool = True
    issues: List[str] = None

    def __post_init__(self):
        if self.issues is None:
            self.issues = []
        if isinstance(self.status, str):
            self.status = SubsystemStatus(self.status)

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


def load_registry() -> List[Subsystem]:
    """Load subsystems from YAML."""
    if not CONFIG_PATH.exists():
        print(f"Warning: {CONFIG_PATH} not found. Using empty registry.")
        return []

    with open(CONFIG_PATH, 'r') as f:
        data = yaml.safe_load(f)

    subsystems = []
    for s_data in data.get('subsystems', []):
        subsystems.append(Subsystem(**s_data))
    return subsystems


def load_deprecated() -> List[Dict[str, str]]:
    """Load deprecated subsystems summary."""
    if not CONFIG_PATH.exists():
        return []
    with open(CONFIG_PATH, 'r') as f:
        data = yaml.safe_load(f)
    return data.get('deprecated_subsystems', [])


SUBSYSTEMS = load_registry()
# For the CLI compatibility, we'll keep a list of objects or summaries
DEPRECATED_SUBSYSTEMS = load_deprecated()



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
        for s_info in DEPRECATED_SUBSYSTEMS:
            print(f"  🔄 {s_info.get('name')}")
            print(f"     Reason: {s_info.get('reason', 'N/A')}")
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
