"""
Purpose Decomposition -- Top-Down Constraint Analysis

Given a node's purpose, determines what sub-compartments SHOULD exist,
what DOES exist, and where the gaps are.

CONSTRAINT_RULES define top-down expectations: "A Repository REQUIRES
Persist and Query children." This reverses the EMERGENCE_RULES direction
(which go bottom-up: "children with Persist + Query = Repository").

Theory: docs/essentials/LAGRANGIAN.md (I_telic term)
Pattern: Kirschner & Gerhart compartmentation + MECE stable partitions
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# CONSTRAINT_RULES -- what each purpose REQUIRES, EXPECTS, and FORBIDS
# ---------------------------------------------------------------------------
# Derived by reversing EMERGENCE_RULES and enriching with architectural knowledge.
#
# "required" = MUST have at least one child with this purpose/role
# "expected" = SHOULD have (absence is a gap, not a violation)
# "forbidden" = SHOULD NOT have (presence is a violation)
#
# Roles checked against: node['role'] field from Collider output.

CONSTRAINT_RULES: Dict[str, Dict[str, List[str]]] = {
    # ── Infrastructure Layer ──────────────────────────────────────────────
    "Repository": {
        "required": ["Query", "Command"],
        "expected": ["Validator", "Factory"],
        "forbidden": ["Controller", "View"],
    },
    "DataAccess": {
        "required": ["Query"],
        "expected": ["Mapper", "Command"],
        "forbidden": ["Controller", "View", "Orchestrator"],
    },
    "Gateway": {
        "required": ["Command"],
        "expected": ["Query", "Mapper"],
        "forbidden": ["Controller", "View"],
    },
    "Adapter": {
        "required": ["Mapper"],
        "expected": ["Validator"],
        "forbidden": ["Controller", "Orchestrator"],
    },

    # ── Domain Layer ──────────────────────────────────────────────────────
    "Service": {
        "required": ["Command", "Query"],
        "expected": ["Validator", "Transformer"],
        "forbidden": ["Controller", "View", "Repository"],
    },
    "DomainService": {
        "required": ["Command"],
        "expected": ["Validator", "Query"],
        "forbidden": ["Controller", "Gateway", "Repository"],
    },
    "Entity": {
        "required": ["Internal"],
        "expected": ["Validator", "Factory"],
        "forbidden": ["Controller", "Repository", "Gateway"],
    },
    "Transformer": {
        "required": ["Mapper"],
        "expected": ["Validator", "Factory"],
        "forbidden": ["Controller", "Repository"],
    },

    # ── Application Layer ─────────────────────────────────────────────────
    "ApplicationService": {
        "required": ["UseCase"],
        "expected": ["Command", "Query", "Validator"],
        "forbidden": ["View", "Repository"],
    },
    "Orchestrator": {
        "required": ["Command"],
        "expected": ["Query", "EventHandler"],
        "forbidden": ["View", "Internal"],
    },
    "UseCase": {
        "required": ["Command"],
        "expected": ["Validator", "Query"],
        "forbidden": ["View", "Repository"],
    },

    # ── Presentation Layer ────────────────────────────────────────────────
    "Controller": {
        "required": ["Internal"],
        "expected": ["Validator"],
        "forbidden": ["Repository", "Gateway"],
    },
    "APILayer": {
        "required": ["Controller"],
        "expected": ["Validator"],
        "forbidden": ["Repository", "Entity"],
    },
    "View": {
        "required": ["Internal"],
        "expected": ["Mapper"],
        "forbidden": ["Repository", "Command", "Service"],
    },

    # ── Testing Layer ─────────────────────────────────────────────────────
    "TestSuite": {
        "required": ["Asserter"],
        "expected": ["Factory"],
        "forbidden": [],
    },

    # ── Cross-cutting ─────────────────────────────────────────────────────
    "Utility": {
        "required": ["Internal"],
        "expected": [],
        "forbidden": ["Controller", "Repository", "Service"],
    },
    "Configuration": {
        "required": ["Internal"],
        "expected": [],
        "forbidden": ["Controller", "Command", "Service"],
    },
}


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class SubCompartment:
    """A sub-purpose that should (or should not) exist within a container."""
    name: str               # e.g., "Query"
    requirement: str        # "required" | "expected" | "forbidden"
    present: bool = False   # whether found in children
    child_ids: List[str] = field(default_factory=list)  # matching children

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class PurposeManifest:
    """What a given purpose SHOULD contain."""
    purpose: str
    required: List[SubCompartment] = field(default_factory=list)
    expected: List[SubCompartment] = field(default_factory=list)
    forbidden: List[SubCompartment] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "purpose": self.purpose,
            "required": [s.to_dict() for s in self.required],
            "expected": [s.to_dict() for s in self.expected],
            "forbidden": [s.to_dict() for s in self.forbidden],
        }


@dataclass
class DecompositionResult:
    """Result of decomposing a single container node."""
    node_id: str
    purpose: str
    pi3_purpose: str
    compartment: str
    child_count: int
    manifest: PurposeManifest
    present: List[str]      # sub-purposes found
    missing: List[str]      # required but absent
    gaps: List[str]         # expected but absent
    violations: List[str]   # forbidden but present
    completeness: float     # |present required+expected| / |required+expected|

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "purpose": self.purpose,
            "pi3_purpose": self.pi3_purpose,
            "compartment": self.compartment,
            "child_count": self.child_count,
            "manifest": self.manifest.to_dict(),
            "present": self.present,
            "missing": self.missing,
            "gaps": self.gaps,
            "violations": self.violations,
            "completeness": self.completeness,
        }


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def _build_parent_child_map(nodes: list) -> Dict[str, List[dict]]:
    """Build a map from container node IDs to their child nodes.

    Uses the 'parent' field from Collider output. Nodes whose parent
    field is empty or missing are top-level (no parent).

    When resolving bare-name parents (e.g., 'main' without file path),
    only resolves if the bare name is unambiguous (exactly one node).
    This prevents 46 different main() functions from collapsing into one.
    """
    children_of: Dict[str, List[dict]] = {}
    node_by_id: Dict[str, dict] = {}
    # Track bare-name → full-ID, but mark ambiguous names
    bare_name_to_id: Dict[str, Optional[str]] = {}

    for n in nodes:
        nid = n.get("id", "")
        node_by_id[nid] = n
        bare = nid.split("::")[-1] if "::" in nid else nid
        if bare in bare_name_to_id:
            bare_name_to_id[bare] = None  # ambiguous — don't resolve
        else:
            bare_name_to_id[bare] = nid

    for n in nodes:
        parent = n.get("parent", "")
        if not parent:
            continue
        # Try file-scoped resolution first: same file_path as child
        if parent not in node_by_id:
            child_file = n.get("file_path", "")
            scoped_id = f"{child_file}::{parent}" if child_file else ""
            if scoped_id and scoped_id in node_by_id:
                parent = scoped_id
            elif parent in bare_name_to_id and bare_name_to_id[parent] is not None:
                # Unambiguous bare name — safe to resolve
                parent = bare_name_to_id[parent]
            # If ambiguous, leave parent as-is (won't match, child is orphaned)
        children_of.setdefault(parent, []).append(n)

    return children_of


def _get_child_roles(children: List[dict]) -> Dict[str, List[str]]:
    """Get a map from role -> list of child node IDs."""
    role_map: Dict[str, List[str]] = {}
    for child in children:
        role = child.get("role", "Unknown")
        cid = child.get("id", "")
        role_map.setdefault(role, []).append(cid)
    return role_map


def decompose_node(
    node: dict,
    children: List[dict],
) -> Optional[DecompositionResult]:
    """Decompose a single container node against CONSTRAINT_RULES.

    Args:
        node: The container node dict from Collider output.
        children: List of child node dicts.

    Returns:
        DecompositionResult if the node's role has constraint rules, else None.
    """
    role = node.get("role", "Unknown")
    rules = CONSTRAINT_RULES.get(role)

    if rules is None:
        return None

    child_roles = _get_child_roles(children)
    all_child_role_set = set(child_roles.keys())

    # Build manifest
    required_subs = []
    for r in rules.get("required", []):
        ids = child_roles.get(r, [])
        required_subs.append(SubCompartment(
            name=r,
            requirement="required",
            present=bool(ids),
            child_ids=ids,
        ))

    expected_subs = []
    for e in rules.get("expected", []):
        ids = child_roles.get(e, [])
        expected_subs.append(SubCompartment(
            name=e,
            requirement="expected",
            present=bool(ids),
            child_ids=ids,
        ))

    forbidden_subs = []
    for f in rules.get("forbidden", []):
        ids = child_roles.get(f, [])
        forbidden_subs.append(SubCompartment(
            name=f,
            requirement="forbidden",
            present=bool(ids),
            child_ids=ids,
        ))

    manifest = PurposeManifest(
        purpose=role,
        required=required_subs,
        expected=expected_subs,
        forbidden=forbidden_subs,
    )

    # Classify outcomes
    present = [s.name for s in required_subs + expected_subs if s.present]
    missing = [s.name for s in required_subs if not s.present]
    gaps = [s.name for s in expected_subs if not s.present]
    violations = [s.name for s in forbidden_subs if s.present]

    # Completeness: fraction of required + expected that are present
    total_expected = len(required_subs) + len(expected_subs)
    total_present = len([s for s in required_subs + expected_subs if s.present])
    completeness = total_present / max(total_expected, 1)

    return DecompositionResult(
        node_id=node.get("id", ""),
        purpose=role,
        pi3_purpose=node.get("pi3_purpose", ""),
        compartment=node.get("compartment", ""),
        child_count=len(children),
        manifest=manifest,
        present=present,
        missing=missing,
        gaps=gaps,
        violations=violations,
        completeness=round(completeness, 4),
    )


def decompose_purposes(full_output: dict) -> List[DecompositionResult]:
    """Decompose all container nodes in the Collider output.

    Finds nodes that have children and whose role matches CONSTRAINT_RULES,
    then checks each against the expected sub-compartment structure.

    Args:
        full_output: The unified analysis dict from Collider.

    Returns:
        List of DecompositionResult for all analyzable containers.
    """
    nodes = full_output.get("nodes", [])
    if not nodes:
        return []

    children_of = _build_parent_child_map(nodes)

    results = []
    for node in nodes:
        nid = node.get("id", "")
        children = children_of.get(nid, [])

        # Only analyze container nodes (those with children OR pi3 containers)
        pi3_children = node.get("pi3_child_count", 0)
        if not children and not pi3_children:
            continue

        result = decompose_node(node, children)
        if result is not None:
            results.append(result)

    # Sort by completeness (worst first) for actionability
    results.sort(key=lambda r: r.completeness)

    return results


def summarize_decomposition(results: List[DecompositionResult]) -> dict:
    """Produce summary statistics from decomposition results.

    Returns:
        Dict with overall completeness, counts of missing/gaps/violations.
    """
    if not results:
        return {
            "total_containers": 0,
            "avg_completeness": 1.0,
            "total_missing": 0,
            "total_gaps": 0,
            "total_violations": 0,
            "worst_nodes": [],
        }

    total_missing = sum(len(r.missing) for r in results)
    total_gaps = sum(len(r.gaps) for r in results)
    total_violations = sum(len(r.violations) for r in results)
    avg_completeness = sum(r.completeness for r in results) / len(results)

    # Top 5 worst nodes
    worst = results[:5]  # already sorted ascending by completeness

    return {
        "total_containers": len(results),
        "avg_completeness": round(avg_completeness, 4),
        "total_missing": total_missing,
        "total_gaps": total_gaps,
        "total_violations": total_violations,
        "worst_nodes": [
            {
                "node_id": w.node_id,
                "purpose": w.purpose,
                "completeness": w.completeness,
                "missing": w.missing,
                "violations": w.violations,
            }
            for w in worst
        ],
    }
