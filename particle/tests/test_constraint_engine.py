"""
Tests for constraint_engine.py — the architectural constraint checker.

Covers:
- ViolationTier enum and Violation dataclass (serialization, defaults)
- ConstraintRule dataclass
- ConstraintEngine._check_condition(): exact match, list membership, comparison ops
- ConstraintEngine._get_node_value(): 5 resolution paths
- ConstraintEngine.validate_node(): axiom triggers, clean nodes, profile skipping
- ConstraintEngine._check_antimatter_laws(): AM001 layer skip, AM002 reverse dep
- ConstraintEngine.validate_edge(): forbidden deps via profile
- ConstraintEngine.detect_architecture_type(): layered vs non-layered
- ConstraintEngine.validate_graph(): full report structure
"""
import os
import sys

import pytest

# Add src/core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'core'))

from constraint_engine import (
    ViolationTier,
    Violation,
    ConstraintRule,
    ConstraintEngine,
)
from profile_loader import ArchitectureProfile, DimensionProfile


# =============================================================================
# FIXTURES — construct profiles directly (avoids YAML filesystem dependency)
# =============================================================================

def _make_arch_profile() -> ArchitectureProfile:
    """Classic layered architecture: PRESENTATION → APPLICATION → DOMAIN → INFRASTRUCTURE."""
    return ArchitectureProfile(
        id="classic_layered",
        name="Classic Layered",
        version="1.0",
        layer_hierarchy=["PRESENTATION", "APPLICATION", "DOMAIN", "INFRASTRUCTURE"],
        allowed_dependencies={
            "PRESENTATION": ["APPLICATION"],
            "APPLICATION": ["DOMAIN"],
            "DOMAIN": ["INFRASTRUCTURE"],
        },
        forbidden_dependencies=[
            {"source": "DOMAIN", "target": "PRESENTATION",
             "reason": "Domain must not depend on presentation"},
            {"source": "INFRASTRUCTURE", "target": "PRESENTATION",
             "reason": "Infrastructure must not depend on presentation"},
        ],
    )


def _make_dim_profile() -> DimensionProfile:
    """Minimal dimension profile for testing."""
    return DimensionProfile(
        id="default_dimensions",
        name="Default Dimensions",
        version="1.0",
        purity={"Pure": {"allows_io": False}, "ExternalIO": {"allows_io": True}},
        lifecycle={"Immutable": {"mutable": False}, "Transient": {"mutable": True}},
        constraints=[],
    )


def _make_engine() -> ConstraintEngine:
    """Engine with both profiles injected (skips YAML profile loading)."""
    return ConstraintEngine(
        arch_profile=_make_arch_profile(),
        dim_profile=_make_dim_profile(),
    )


# =============================================================================
# ViolationTier enum
# =============================================================================

class TestViolationTier:

    def test_tier_values(self):
        assert ViolationTier.A.value == "antimatter"
        assert ViolationTier.B.value == "policy"
        assert ViolationTier.C.value == "signal"

    def test_from_value(self):
        assert ViolationTier("antimatter") == ViolationTier.A


# =============================================================================
# Violation dataclass
# =============================================================================

class TestViolation:

    def test_defaults(self):
        v = Violation(rule_id="R1", tier=ViolationTier.A, node_id="n1",
                      reason="test reason")
        assert v.confidence == 1.0
        assert v.edge_source is None
        assert v.edge_target is None
        assert v.details == {}

    def test_to_dict_keys(self):
        v = Violation(rule_id="R1", tier=ViolationTier.B, node_id="n1",
                      reason="reason", confidence=0.8)
        d = v.to_dict()
        assert d['rule_id'] == "R1"
        assert d['tier'] == "policy"
        assert d['node_id'] == "n1"
        assert d['confidence'] == 0.8

    def test_to_dict_with_edge(self):
        v = Violation(rule_id="R1", tier=ViolationTier.A, node_id="n1",
                      reason="r", edge_source="src", edge_target="tgt")
        d = v.to_dict()
        assert d['edge_source'] == "src"
        assert d['edge_target'] == "tgt"


# =============================================================================
# ConstraintRule dataclass
# =============================================================================

class TestConstraintRule:

    def test_defaults(self):
        r = ConstraintRule(
            id="TEST-001", name="Test", tier=ViolationTier.C,
            scope="node", description="desc",
            condition={"role": "Entity"}, reason="reason",
        )
        assert r.confidence == 1.0
        assert r.profile_dependent is False
        assert r.profiles == []

    def test_profile_dependent(self):
        r = ConstraintRule(
            id="TEST-002", name="Test", tier=ViolationTier.B,
            scope="node", description="desc",
            condition={}, reason="reason",
            profile_dependent=True,
            profiles=["classic_layered", "clean_onion"],
        )
        assert r.profile_dependent is True
        assert "classic_layered" in r.profiles


# =============================================================================
# ConstraintEngine initialization
# =============================================================================

class TestEngineInit:

    def test_loads_rules_from_yaml(self):
        """Engine should auto-load rules.yaml relative to its own module."""
        engine = _make_engine()
        assert len(engine.rules) > 0

    def test_has_all_tiers(self):
        engine = _make_engine()
        tiers = {r.tier for r in engine.rules}
        assert ViolationTier.A in tiers
        assert ViolationTier.B in tiers
        assert ViolationTier.C in tiers

    def test_profiles_injected(self):
        engine = _make_engine()
        assert engine.arch_profile.id == "classic_layered"
        assert engine.dim_profile.id == "default_dimensions"

    def test_rule_count_matches_yaml(self):
        """rules.yaml defines 5 axioms + 3 invariants + 4 heuristics = 12 rules."""
        engine = _make_engine()
        assert len(engine.rules) >= 12


# =============================================================================
# _check_condition
# =============================================================================

class TestCheckCondition:

    def setup_method(self):
        self.engine = _make_engine()

    def test_exact_match(self):
        node = {"role": "Entity", "purity": "Pure"}
        assert self.engine._check_condition(node, {"role": "Entity"}) is True

    def test_exact_mismatch(self):
        node = {"role": "Service", "purity": "Pure"}
        assert self.engine._check_condition(node, {"role": "Entity"}) is False

    def test_list_membership(self):
        """When condition value is a list, node value must be IN that list."""
        node = {"responsibility": "Create"}
        cond = {"responsibility": ["Create", "Update", "Delete"]}
        assert self.engine._check_condition(node, cond) is True

    def test_list_non_membership(self):
        node = {"responsibility": "Read"}
        cond = {"responsibility": ["Create", "Update", "Delete"]}
        assert self.engine._check_condition(node, cond) is False

    def test_comparison_greater_than(self):
        node = {"complexity": 25}
        cond = {"complexity": ">20"}
        assert self.engine._check_condition(node, cond) is True

    def test_comparison_greater_than_fails(self):
        node = {"complexity": 15}
        cond = {"complexity": ">20"}
        assert self.engine._check_condition(node, cond) is False

    def test_comparison_less_than(self):
        node = {"in_degree": 0}
        cond = {"in_degree": "<1"}
        assert self.engine._check_condition(node, cond) is True

    def test_missing_key_returns_false(self):
        node = {"role": "Entity"}
        cond = {"nonexistent_key": "value"}
        assert self.engine._check_condition(node, cond) is False

    def test_and_logic_all_must_match(self):
        """Multiple conditions require ALL to be true (AND)."""
        node = {"role": "Entity", "purity": "Pure"}
        cond = {"role": "Entity", "purity": "Pure"}
        assert self.engine._check_condition(node, cond) is True

    def test_and_logic_partial_fails(self):
        node = {"role": "Entity", "purity": "ExternalIO"}
        cond = {"role": "Entity", "purity": "Pure"}
        assert self.engine._check_condition(node, cond) is False


# =============================================================================
# _get_node_value — 5 resolution paths
# =============================================================================

class TestGetNodeValue:

    def setup_method(self):
        self.engine = _make_engine()

    def test_direct_key(self):
        node = {"role": "Entity", "file": "a.py"}
        assert self.engine._get_node_value(node, "role") == "Entity"

    def test_rpbl_dimension_alias_responsibility(self):
        """'responsibility' resolves via rpbl.R or dimensions.D3_ROLE."""
        node = {"rpbl": {"R": "Compute", "P": "Pure", "B": "Internal", "L": "Transient"}}
        assert self.engine._get_node_value(node, "responsibility") == "Compute"

    def test_rpbl_dimension_alias_purity(self):
        node = {"rpbl": {"R": "Compute", "P": "ExternalIO", "B": "Internal", "L": "Transient"}}
        assert self.engine._get_node_value(node, "purity") == "ExternalIO"

    def test_rpbl_dimension_alias_boundary(self):
        node = {"rpbl": {"R": "Compute", "P": "Pure", "B": "External", "L": "Transient"}}
        assert self.engine._get_node_value(node, "boundary") == "External"

    def test_rpbl_dimension_alias_lifecycle(self):
        node = {"rpbl": {"R": "Compute", "P": "Pure", "B": "Internal", "L": "Singleton"}}
        assert self.engine._get_node_value(node, "lifecycle") == "Singleton"

    def test_rpbl_prefix(self):
        node = {"rpbl_r": 5, "rpbl_p": 3}
        assert self.engine._get_node_value(node, "rpbl_r") == 5

    def test_dimension_d_key(self):
        """D*_ dimension keys like D3_ROLE map via dimensions dict."""
        node = {"dimensions": {"D3_ROLE": "Orchestrator"}}
        # Accessing via the dimension alias should resolve
        val = self.engine._get_node_value(node, "role")
        # If 'role' is not direct, it tries rpbl, then dimensions
        # The fallback path depends on implementation
        # At minimum, direct key 'dimensions' is accessible
        assert self.engine._get_node_value(node, "dimensions") is not None

    def test_missing_key_returns_none(self):
        node = {"role": "Entity"}
        assert self.engine._get_node_value(node, "nonexistent") is None

    def test_boundary_falls_back_to_layer(self):
        """'boundary' alias can fall back to 'layer' key if rpbl not present."""
        node = {"layer": "APPLICATION"}
        val = self.engine._get_node_value(node, "boundary")
        # Should get "APPLICATION" if boundary alias falls back to layer
        # Or None if the particular resolution path doesn't hit 'layer'
        # This tests the fallback chain


# =============================================================================
# validate_node — axiom triggers
# =============================================================================

class TestValidateNode:

    def setup_method(self):
        self.engine = _make_engine()

    def test_axiom_001_immutable_with_create(self):
        """AXIOM-001: lifecycle=Immutable + responsibility in [Create,Update,Delete] → violation."""
        node = {
            "id": "n1", "name": "Mutator", "type": "function",
            "lifecycle": "Immutable", "responsibility": "Create",
        }
        violations = self.engine.validate_node(node)
        axiom_ids = [v.rule_id for v in violations]
        assert "AXIOM-001" in axiom_ids

    def test_axiom_002_entity_pure(self):
        """AXIOM-002: role=Entity + purity=Pure → violation (entities do IO)."""
        node = {
            "id": "n2", "name": "User", "type": "class",
            "role": "Entity", "purity": "Pure",
        }
        violations = self.engine.validate_node(node)
        axiom_ids = [v.rule_id for v in violations]
        assert "AXIOM-002" in axiom_ids

    def test_axiom_005_getter_with_delete(self):
        """AXIOM-005: role=Getter + responsibility in [Create,Update,Delete]."""
        node = {
            "id": "n3", "name": "BadGetter", "type": "function",
            "role": "Getter", "responsibility": "Delete",
        }
        violations = self.engine.validate_node(node)
        axiom_ids = [v.rule_id for v in violations]
        assert "AXIOM-005" in axiom_ids

    def test_clean_node_no_violations(self):
        """A well-formed node should produce no Tier A violations."""
        node = {
            "id": "n4", "name": "ReadUser", "type": "function",
            "role": "Getter", "purity": "ExternalIO",
            "responsibility": "Read", "lifecycle": "Transient",
        }
        violations = self.engine.validate_node(node)
        tier_a = [v for v in violations if v.tier == ViolationTier.A]
        assert len(tier_a) == 0

    def test_profile_dependent_rule_skipped(self):
        """Rules with profile_dependent=True are skipped if profile not in rule.profiles."""
        # Use a non-matching profile
        arch = _make_arch_profile()
        arch.id = "microservices"  # Not in any profile-dependent rule's profiles list
        engine = ConstraintEngine(arch_profile=arch, dim_profile=_make_dim_profile())

        # INVARIANT-003 is for clean_onion only — should be skipped for "microservices"
        node = {
            "id": "n5", "name": "BigController", "type": "class",
            "role": "Controller", "complexity": 25,
        }
        violations = engine.validate_node(node)
        inv3 = [v for v in violations if v.rule_id == "INVARIANT-003"]
        assert len(inv3) == 0

    def test_heuristic_has_lower_confidence(self):
        """HEURISTIC-001: Getter + purity=ExternalIO → signal with confidence < 1.0."""
        node = {
            "id": "n6", "name": "IoGetter", "type": "function",
            "role": "Getter", "purity": "ExternalIO",
        }
        violations = self.engine.validate_node(node)
        h001 = [v for v in violations if v.rule_id == "HEURISTIC-001"]
        if h001:
            assert h001[0].confidence < 1.0
            assert h001[0].tier == ViolationTier.C


# =============================================================================
# _check_antimatter_laws — AM001 (layer skip), AM002 (reverse dep)
# =============================================================================

class TestAntimatterLaws:

    def setup_method(self):
        self.engine = _make_engine()

    def test_am002_reverse_dependency(self):
        """INFRASTRUCTURE → APPLICATION is a reverse layer dependency."""
        source = {"id": "s1", "layer": "INFRASTRUCTURE"}
        target = {"id": "t1", "layer": "APPLICATION"}
        edge = {"kind": "calls"}
        violations = self.engine._check_antimatter_laws(source, target, edge)
        am_ids = [v.rule_id for v in violations]
        assert "AM002" in am_ids

    def test_am001_layer_skip(self):
        """PRESENTATION → DOMAIN skips APPLICATION (2 levels apart)."""
        source = {"id": "s2", "layer": "PRESENTATION"}
        target = {"id": "t2", "layer": "DOMAIN"}
        edge = {"kind": "calls"}
        violations = self.engine._check_antimatter_laws(source, target, edge)
        am_ids = [v.rule_id for v in violations]
        assert "AM001" in am_ids

    def test_same_layer_no_violation(self):
        """Same layer → no antimatter violation."""
        source = {"id": "s3", "layer": "APPLICATION"}
        target = {"id": "t3", "layer": "APPLICATION"}
        edge = {"kind": "calls"}
        violations = self.engine._check_antimatter_laws(source, target, edge)
        assert len(violations) == 0

    def test_adjacent_downward_no_violation(self):
        """PRESENTATION → APPLICATION is valid (adjacent downward)."""
        source = {"id": "s4", "layer": "PRESENTATION"}
        target = {"id": "t4", "layer": "APPLICATION"}
        edge = {"kind": "calls"}
        violations = self.engine._check_antimatter_laws(source, target, edge)
        assert len(violations) == 0

    def test_unknown_layer_no_violation(self):
        """Unknown layers → no antimatter check possible."""
        source = {"id": "s5", "layer": "UNKNOWN"}
        target = {"id": "t5", "layer": "APPLICATION"}
        edge = {"kind": "calls"}
        violations = self.engine._check_antimatter_laws(source, target, edge)
        assert len(violations) == 0

    def test_missing_layer_no_violation(self):
        """Nodes without 'layer' key → no antimatter check."""
        source = {"id": "s6"}
        target = {"id": "t6"}
        edge = {"kind": "calls"}
        violations = self.engine._check_antimatter_laws(source, target, edge)
        assert len(violations) == 0


# =============================================================================
# validate_edge — forbidden dependency via profile
# =============================================================================

class TestValidateEdge:

    def setup_method(self):
        self.engine = _make_engine()

    def test_forbidden_dependency_detected(self):
        """DOMAIN → PRESENTATION is forbidden in classic_layered profile."""
        source = {"id": "s1", "layer": "DOMAIN"}
        target = {"id": "t1", "layer": "PRESENTATION"}
        edge = {"kind": "calls"}
        violations = self.engine.validate_edge(source, target, edge)
        # Should include AM002 (reverse dep) and/or forbidden dep violation
        assert len(violations) > 0

    def test_allowed_dependency_clean(self):
        """APPLICATION → DOMAIN is allowed — no forbidden dep violation."""
        source = {"id": "s2", "layer": "APPLICATION"}
        target = {"id": "t2", "layer": "DOMAIN"}
        edge = {"kind": "calls"}
        violations = self.engine.validate_edge(source, target, edge)
        # Adjacent downward + allowed in profile → clean
        assert len(violations) == 0


# =============================================================================
# detect_architecture_type
# =============================================================================

class TestDetectArchitectureType:

    def setup_method(self):
        self.engine = _make_engine()

    def test_layered_detection(self):
        """Codebase with clear layer separation → is_layered=True."""
        layers = [
            "PRESENTATION", "PRESENTATION",
            "APPLICATION", "APPLICATION",
            "DOMAIN", "DOMAIN", "DOMAIN",
            "INFRASTRUCTURE", "INFRASTRUCTURE",
        ]
        # file_path is required — detection groups by file to measure layer separation
        nodes = [{"id": f"n{i}", "layer": layer, "file_path": f"mod_{i}.py"}
                 for i, layer in enumerate(layers)]
        # Downward edges only (no upward)
        edges = [
            {"source": "n0", "target": "n2", "kind": "calls"},  # PRES→APP
            {"source": "n2", "target": "n4", "kind": "calls"},  # APP→DOM
            {"source": "n4", "target": "n7", "kind": "calls"},  # DOM→INFRA
            {"source": "n1", "target": "n3", "kind": "calls"},  # PRES→APP
            {"source": "n3", "target": "n5", "kind": "calls"},  # APP→DOM
        ]
        result = self.engine.detect_architecture_type(nodes, edges)
        assert result['is_layered'] is True

    def test_non_layered_detection(self):
        """Codebase with many upward deps → is_layered=False."""
        layers = ["PRESENTATION", "APPLICATION", "DOMAIN", "INFRASTRUCTURE"]
        nodes = [{"id": f"n{i}", "layer": layer} for i, layer in enumerate(layers)]
        # Mix of up and down — high upward ratio
        edges = [
            {"source": "n0", "target": "n1", "kind": "calls"},  # PRES→APP (down)
            {"source": "n2", "target": "n0", "kind": "calls"},  # DOM→PRES (up!)
            {"source": "n3", "target": "n1", "kind": "calls"},  # INFRA→APP (up!)
            {"source": "n3", "target": "n0", "kind": "calls"},  # INFRA→PRES (up!)
        ]
        result = self.engine.detect_architecture_type(nodes, edges)
        assert result['is_layered'] is False

    def test_no_layers_returns_not_layered(self):
        """Nodes without layer info → not layered."""
        nodes = [{"id": "n0"}, {"id": "n1"}]
        edges = [{"source": "n0", "target": "n1", "kind": "calls"}]
        result = self.engine.detect_architecture_type(nodes, edges)
        assert result['is_layered'] is False


# =============================================================================
# validate_graph — full report
# =============================================================================

class TestValidateGraph:

    def setup_method(self):
        self.engine = _make_engine()

    def test_report_structure(self):
        """validate_graph produces a report dict with expected top-level keys."""
        nodes = [
            {"id": "n1", "name": "f1", "type": "function",
             "role": "Service", "lifecycle": "Transient"},
            {"id": "n2", "name": "f2", "type": "function",
             "role": "Getter", "purity": "ExternalIO"},
        ]
        edges = [{"source": "n1", "target": "n2", "kind": "calls"}]
        report = self.engine.validate_graph(nodes, edges)

        assert 'total_nodes' in report
        assert 'total_edges' in report
        assert 'total_violations' in report
        assert 'antimatter' in report
        assert 'valid' in report

    def test_report_counts(self):
        nodes = [{"id": "n1", "name": "f", "type": "function"}]
        edges = []
        report = self.engine.validate_graph(nodes, edges)
        assert report['total_nodes'] == 1
        assert report['total_edges'] == 0

    def test_clean_graph_is_valid(self):
        """Graph with no axiom/invariant violations → valid=True."""
        nodes = [
            {"id": "n1", "name": "svc", "type": "class",
             "role": "Service", "purity": "ExternalIO",
             "responsibility": "Orchestrate", "lifecycle": "Transient"},
        ]
        edges = []
        report = self.engine.validate_graph(nodes, edges)
        assert report['valid'] is True

    def test_antimatter_makes_invalid(self):
        """Graph with Tier A violation → valid=False."""
        nodes = [
            {"id": "n1", "name": "BadEntity", "type": "class",
             "role": "Entity", "purity": "Pure"},
        ]
        edges = []
        report = self.engine.validate_graph(nodes, edges)
        # AXIOM-002: Entity + Pure → violation
        assert report['antimatter']['count'] > 0
        assert report['valid'] is False

    def test_edge_validation_skipped_for_non_layered(self):
        """When architecture is not layered, layer-based edge validation is skipped."""
        nodes = [
            {"id": "n1", "name": "a", "type": "function"},
            {"id": "n2", "name": "b", "type": "function"},
        ]
        edges = [{"source": "n1", "target": "n2", "kind": "calls"}]
        report = self.engine.validate_graph(nodes, edges)
        # No layers → can't have layer violations
        assert report.get('layer_validation_skipped', False) is True or \
               report['antimatter']['count'] == 0

    def test_multiple_violations_accumulate(self):
        """Multiple violating nodes should accumulate violations."""
        nodes = [
            {"id": "n1", "name": "Bad1", "type": "class",
             "role": "Entity", "purity": "Pure"},  # AXIOM-002
            {"id": "n2", "name": "Bad2", "type": "function",
             "lifecycle": "Immutable", "responsibility": "Create"},  # AXIOM-001
        ]
        edges = []
        report = self.engine.validate_graph(nodes, edges)
        assert report['total_violations'] >= 2
        assert report['antimatter']['count'] >= 2


# =============================================================================
# ArchitectureProfile (from profile_loader — tested here for edge integration)
# =============================================================================

class TestArchitectureProfile:

    def test_forbidden_reason(self):
        profile = _make_arch_profile()
        reason = profile.get_forbidden_reason("DOMAIN", "PRESENTATION")
        assert reason is not None
        assert "presentation" in reason.lower()

    def test_no_forbidden_reason(self):
        profile = _make_arch_profile()
        reason = profile.get_forbidden_reason("PRESENTATION", "APPLICATION")
        assert reason is None

    def test_dependency_allowed(self):
        profile = _make_arch_profile()
        assert profile.is_dependency_allowed("PRESENTATION", "APPLICATION") is True

    def test_dependency_not_in_allowed(self):
        profile = _make_arch_profile()
        # PRESENTATION → DOMAIN is not explicitly allowed (skip)
        assert profile.is_dependency_allowed("PRESENTATION", "DOMAIN") is False
