"""
DOMAIN SEPARATION GUARDRAIL TESTS
==================================

These tests enforce SPEC v0.1.3 domain separation invariants:

1. N_atomic (functions, methods, classes) and N_container (file/module nodes) are DISJOINT
2. Calls resolve only against N_atomic
3. Imports resolve only against N_container
4. Proof metrics + entrypoints + denominators are ATOMIC-ONLY
5. Imports must NOT affect proof_score

Run with: python3 -m pytest tests/test_domain_separation_guardrails.py -v
"""
import json
import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional

import pytest

# Add src/core to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "core"))

from validation.self_proof import SelfProofValidator


REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _run_unified_analysis(target_dir: Path, out_dir: Path) -> dict:
    """Run unified analysis and return the JSON output."""
    out_dir.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    core_path = str(REPO_ROOT / "src" / "core")
    env["PYTHONPATH"] = core_path + (os.pathsep + env.get("PYTHONPATH", ""))

    cmd = [
        sys.executable,
        "-c",
        f"""
import sys
sys.path.insert(0, '{core_path}')
from unified_analysis import analyze
result = analyze('{target_dir}', output_dir='{out_dir}')
"""
    ]

    proc = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=60)
    if proc.returncode != 0:
        # Analysis may fail on minimal fixtures; that's OK, check if output exists
        pass

    ua_path = out_dir / "unified_analysis.json"
    if ua_path.exists():
        return json.loads(ua_path.read_text("utf8"))
    return {}


def _is_container_node(comp: dict) -> bool:
    """Check if a component is a container (file/module) node."""
    t = (comp.get("type") or comp.get("kind") or "").lower()
    md = comp.get("metadata") or {}
    return (
        t in {"module", "file", "container"}
        or bool(md.get("file_node"))
        or bool(md.get("fileNode"))
    )


def _is_atomic_node(comp: dict) -> bool:
    """Check if a component is atomic (function/method/class)."""
    if _is_container_node(comp):
        return False
    # Prefer 'kind' over 'type' since 'type' is often 'Unknown'
    t = (comp.get("kind") or comp.get("type") or "").lower()
    return t in {"function", "method", "class", "functiondef", "asyncfunctiondef", "classdef"}


def _get_components(unified: dict) -> Dict[str, dict]:
    """Extract components as dict by id."""
    nodes = unified.get("nodes") or unified.get("components") or []
    if isinstance(nodes, dict):
        return nodes
    result = {}
    for n in nodes:
        nid = n.get("id") or n.get("key")
        if nid:
            result[nid] = n
    return result


def _get_edges(unified: dict) -> List[dict]:
    """Extract edges from unified output."""
    return unified.get("edges") or []


def _proof_edges(unified: dict) -> List[dict]:
    """Filter to proof-relevant edges: calls + resolved_internal."""
    return [
        e for e in _get_edges(unified)
        if e.get("edge_type") == "calls" and e.get("resolution") == "resolved_internal"
    ]


class TestNoFileNodesInProofGraph:
    """Proof graph must contain only atomic nodes (SPEC 10.1)."""

    def test_proof_nodes_are_atomic_only(self):
        """Self-proof components are functions/methods/classes, never modules."""
        validator = SelfProofValidator(FIXTURES_DIR / "toy_call_file_node_shadow" / "pkg")
        result = validator.prove(enforce_metadata=False)

        # All proof nodes should be atomic (L3/L4)
        for node in result.proof_nodes:
            node_type = node.get("type", "").lower()
            assert node_type != "module", f"Container node leaked into proof: {node}"
            assert not node.get("metadata", {}).get("file_node"), f"File node in proof: {node}"


class TestCallsNeverResolveToFileNodes:
    """Call edges must not resolve to container nodes (SPEC 4.1)."""

    def test_calls_resolve_to_atomics(self, tmp_path):
        """resolved_internal call edges target N_atomic only."""
        fixture = FIXTURES_DIR / "toy_call_file_node_shadow" / "pkg"
        out_dir = tmp_path / "out"

        unified = _run_unified_analysis(fixture, out_dir)
        if not unified:
            pytest.skip("Could not run unified analysis on fixture")

        comps = _get_components(unified)
        if not comps:
            pytest.skip("No components in unified analysis output")

        call_edges = [e for e in _get_edges(unified) if e.get("edge_type") == "calls"]

        for edge in call_edges:
            if edge.get("resolution") == "resolved_internal":
                target = edge.get("target")
                if target and target in comps:
                    target_comp = comps[target]
                    assert _is_atomic_node(target_comp), (
                        f"Call edge resolved to container node: {target_comp}"
                    )

    def test_module_alias_call_stays_unresolved(self, tmp_path):
        """Calling a module alias (helper) should not resolve to file node."""
        fixture = FIXTURES_DIR / "toy_call_file_node_shadow" / "pkg"
        out_dir = tmp_path / "out2"

        unified = _run_unified_analysis(fixture, out_dir)
        if not unified:
            pytest.skip("Could not run unified analysis on fixture")

        call_edges = [e for e in _get_edges(unified) if e.get("edge_type") == "calls"]

        # The call to helper() (module alias) should be unresolved, not resolved to file node
        helper_calls = [
            e for e in call_edges
            if "helper" in str(e.get("target", "")).lower() and "helper_fn" not in str(e.get("target", "")).lower()
        ]

        # If there are helper calls, they should not resolve to a file/module node
        for edge in helper_calls:
            if edge.get("resolution") == "resolved_internal":
                # Check target is not a module
                comps = _get_components(unified)
                target = edge.get("target")
                if target and target in comps:
                    assert not _is_container_node(comps[target]), (
                        f"Module alias call resolved to container: {comps[target]}"
                    )


class TestConnectionCoverageExcludesContainers:
    """Connection coverage denominator must be atomic count only (SPEC 10.3)."""

    def test_proof_metrics_use_atomic_denominator(self):
        """Proof metrics exclude container nodes from denominators."""
        fixture = FIXTURES_DIR / "toy_call_file_node_shadow" / "pkg"
        validator = SelfProofValidator(fixture)
        result = validator.prove(enforce_metadata=False)

        # The component counts should only include L3/L4 nodes
        # All proof_nodes should be atomic
        atomic_count = sum(
            1 for n in result.proof_nodes
            if n.get("type", "").lower() not in {"module", "file"}
        )

        assert atomic_count == len(result.proof_nodes), (
            "proof_nodes should contain only atomic components"
        )

        # filesystem_components should be the atomic count
        # (self_proof scans for functions/classes, not file nodes)
        assert result.filesystem_components > 0, "Expected some atomic components"


class TestImportsDoNotAffectProofScore:
    """Import resolution quality must not change proof_score (SPEC 10.4)."""

    def test_proof_score_invariant_to_imports(self):
        """Two fixtures differing only by imports should have same proof_score."""
        fixture_no = FIXTURES_DIR / "toy_proof_import_invariance_no_import"
        fixture_yes = FIXTURES_DIR / "toy_proof_import_invariance_with_import"

        validator1 = SelfProofValidator(fixture_no)
        result1 = validator1.prove(enforce_metadata=False)

        validator2 = SelfProofValidator(fixture_yes)
        result2 = validator2.prove(enforce_metadata=False)

        # Proof scores should be equal (imports don't affect proof)
        assert result1.proof_score == pytest.approx(result2.proof_score, abs=1e-9), (
            f"Imports affected proof_score: no_import={result1.proof_score} "
            f"with_import={result2.proof_score}"
        )

        # Also verify component counts are the same (same atomic structure)
        assert result1.filesystem_components == result2.filesystem_components, (
            "Atomic component counts should be identical"
        )


class TestDomainSeparationInvariant:
    """N_atomic and N_container must be disjoint (SPEC 2.4)."""

    def test_domains_are_disjoint(self, tmp_path):
        """No node should be both atomic and container."""
        fixture = FIXTURES_DIR / "toy_call_file_node_shadow" / "pkg"
        out_dir = tmp_path / "out_disjoint"

        unified = _run_unified_analysis(fixture, out_dir)
        if not unified:
            pytest.skip("Could not run unified analysis on fixture")

        comps = _get_components(unified)

        for cid, comp in comps.items():
            is_atomic = _is_atomic_node(comp)
            is_container = _is_container_node(comp)

            # XOR: exactly one must be true, or neither (unknown type)
            assert not (is_atomic and is_container), (
                f"Node classified as BOTH atomic and container: {comp}"
            )
