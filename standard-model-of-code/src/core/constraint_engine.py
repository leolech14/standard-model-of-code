#!/usr/bin/env python3
"""
Constraint Engine for the Constraint Field

Validates nodes and edges against the constraint rules defined in
schema/constraints/rules.yaml. Implements the three-tier validation
system (Axioms, Invariants, Heuristics).

Usage:
    from constraint_engine import ConstraintEngine, validate_graph

    engine = ConstraintEngine()
    violations = engine.validate_node(node)
    all_violations = engine.validate_graph(nodes, edges)

Reference: THESIS_CONSTRAINT_VALIDATION.md v3.0
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum

try:
    from core.profile_loader import (
        ProfileLoader, ArchitectureProfile, DimensionProfile,
        get_profile_loader, get_default_profiles
    )
except ImportError:
    from profile_loader import (
        ProfileLoader, ArchitectureProfile, DimensionProfile,
        get_profile_loader, get_default_profiles
    )


class ViolationTier(Enum):
    """Constraint violation tiers."""
    A = "antimatter"      # Model-level impossibility
    B = "policy"          # Architecture policy violation
    C = "signal"          # Informative heuristic


@dataclass
class Violation:
    """A constraint violation."""
    rule_id: str
    tier: ViolationTier
    node_id: str
    reason: str
    confidence: float = 1.0
    edge_source: Optional[str] = None  # For edge violations
    edge_target: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'rule_id': self.rule_id,
            'tier': self.tier.value,
            'node_id': self.node_id,
            'reason': self.reason,
            'confidence': self.confidence,
            'edge_source': self.edge_source,
            'edge_target': self.edge_target,
            'details': self.details,
        }


@dataclass
class ConstraintRule:
    """A parsed constraint rule."""
    id: str
    name: str
    tier: ViolationTier
    scope: str  # node, edge, path
    description: str
    condition: Dict[str, Any]
    reason: str
    confidence: float = 1.0
    profile_dependent: bool = False
    profiles: List[str] = field(default_factory=list)


class ConstraintEngine:
    """
    Validates nodes and edges against constraint rules.

    Implements the Constraint Field from THESIS_CONSTRAINT_VALIDATION.md.
    """

    def __init__(
        self,
        arch_profile: Optional[ArchitectureProfile] = None,
        dim_profile: Optional[DimensionProfile] = None,
        rules_path: Optional[Path] = None,
    ):
        # Load profiles
        if arch_profile is None or dim_profile is None:
            default_arch, default_dim = get_default_profiles()
            self.arch_profile = arch_profile or default_arch
            self.dim_profile = dim_profile or default_dim
        else:
            self.arch_profile = arch_profile
            self.dim_profile = dim_profile

        # Load rules
        if rules_path is None:
            rules_path = Path(__file__).parent.parent.parent / 'schema' / 'constraints' / 'rules.yaml'

        self.rules: List[ConstraintRule] = []
        self._load_rules(rules_path)

        # Separate rules by tier
        self.tier_a_rules = [r for r in self.rules if r.tier == ViolationTier.A]
        self.tier_b_rules = [r for r in self.rules if r.tier == ViolationTier.B]
        self.tier_c_rules = [r for r in self.rules if r.tier == ViolationTier.C]

    def _load_rules(self, rules_path: Path):
        """Load constraint rules from YAML."""
        if not rules_path.exists():
            print(f"Warning: Rules file not found: {rules_path}")
            return

        with open(rules_path) as f:
            data = yaml.safe_load(f)

        # Parse Tier A rules
        for rule_data in data.get('tier_a', []):
            self.rules.append(ConstraintRule(
                id=rule_data['id'],
                name=rule_data['name'],
                tier=ViolationTier.A,
                scope=rule_data.get('scope', 'node'),
                description=rule_data.get('description', ''),
                condition=rule_data.get('condition', {}),
                reason=rule_data.get('reason', ''),
                confidence=1.0,  # Tier A is always 100% confidence
            ))

        # Parse Tier B rules
        for rule_data in data.get('tier_b', []):
            self.rules.append(ConstraintRule(
                id=rule_data['id'],
                name=rule_data['name'],
                tier=ViolationTier.B,
                scope=rule_data.get('scope', 'node'),
                description=rule_data.get('description', ''),
                condition=rule_data.get('condition', {}),
                reason=rule_data.get('reason', ''),
                confidence=1.0,
                profile_dependent=rule_data.get('profile_dependent', False),
                profiles=rule_data.get('profiles', []),
            ))

        # Parse Tier C rules
        for rule_data in data.get('tier_c', []):
            self.rules.append(ConstraintRule(
                id=rule_data['id'],
                name=rule_data['name'],
                tier=ViolationTier.C,
                scope=rule_data.get('scope', 'node'),
                description=rule_data.get('description', ''),
                condition=rule_data.get('condition', {}),
                reason=rule_data.get('signal', rule_data.get('reason', '')),
                confidence=rule_data.get('confidence', 0.5),
            ))

    def _check_condition(self, node: Dict[str, Any], condition: Dict[str, Any]) -> bool:
        """
        Check if a node matches a rule condition.

        Condition format:
            lifecycle: Immutable
            responsibility: [Create, Update, Delete]

        Returns True if ALL conditions match (AND logic).
        """
        for key, expected in condition.items():
            actual = self._get_node_value(node, key)

            if actual is None:
                return False

            # Handle list of allowed values
            if isinstance(expected, list):
                if actual not in expected:
                    return False
            # Handle comparison operators
            elif isinstance(expected, str) and expected.startswith('>'):
                threshold = float(expected[1:])
                try:
                    if float(actual) <= threshold:
                        return False
                except (ValueError, TypeError):
                    return False
            elif isinstance(expected, str) and expected.startswith('<'):
                threshold = float(expected[1:])
                try:
                    if float(actual) >= threshold:
                        return False
                except (ValueError, TypeError):
                    return False
            else:
                if actual != expected:
                    return False

        return True

    def _get_node_value(self, node: Dict[str, Any], key: str) -> Any:
        """Get a value from a node, handling nested keys."""
        # Direct key
        if key in node:
            return node[key]

        # Handle RPBL dimensions
        if key == 'responsibility':
            return node.get('rpbl', {}).get('R') or node.get('dimensions', {}).get('D3_ROLE')
        if key == 'purity':
            return node.get('rpbl', {}).get('P') or node.get('dimensions', {}).get('D4_PURITY')
        if key == 'boundary':
            return node.get('rpbl', {}).get('B') or node.get('layer')
        if key == 'lifecycle':
            return node.get('rpbl', {}).get('L') or node.get('dimensions', {}).get('D8_LIFECYCLE')

        # Handle rpbl_* keys
        if key.startswith('rpbl_'):
            rpbl_key = key[5:].upper()
            return node.get('rpbl', {}).get(rpbl_key)

        # Handle dimensions
        if key.startswith('D') and '_' in key:
            return node.get('dimensions', {}).get(key)

        # Try nested access
        parts = key.split('.')
        value = node
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return None
        return value

    def validate_node(self, node: Dict[str, Any]) -> List[Violation]:
        """
        Validate a single node against all node-scope rules.

        Returns list of violations (empty if valid).
        """
        violations = []
        node_id = node.get('id', node.get('name', 'unknown'))

        for rule in self.rules:
            if rule.scope != 'node':
                continue

            # Skip profile-dependent rules if profile doesn't match
            if rule.profile_dependent and rule.profiles:
                if self.arch_profile.id not in rule.profiles:
                    continue

            # Check if condition matches
            if self._check_condition(node, rule.condition):
                violations.append(Violation(
                    rule_id=rule.id,
                    tier=rule.tier,
                    node_id=node_id,
                    reason=rule.reason,
                    confidence=rule.confidence,
                    details={
                        'condition': rule.condition,
                        'node_values': {
                            k: self._get_node_value(node, k)
                            for k in rule.condition.keys()
                        }
                    }
                ))

        return violations

    def validate_edge(
        self,
        source_node: Dict[str, Any],
        target_node: Dict[str, Any],
        edge: Dict[str, Any],
    ) -> List[Violation]:
        """
        Validate an edge against edge-scope rules.

        Checks layer dependency violations based on architecture profile.
        """
        violations = []
        source_id = source_node.get('id', source_node.get('name', 'unknown'))
        target_id = target_node.get('id', target_node.get('name', 'unknown'))
        source_layer = source_node.get('layer', '').upper()
        target_layer = target_node.get('layer', '').upper()

        # Skip if layers unknown
        if not source_layer or not target_layer or source_layer == 'UNKNOWN' or target_layer == 'UNKNOWN':
            return violations

        # Check architecture profile for layer violations
        forbidden_reason = self.arch_profile.get_forbidden_reason(source_layer, target_layer)
        if forbidden_reason:
            violations.append(Violation(
                rule_id='INVARIANT-001',
                tier=ViolationTier.B,
                node_id=source_id,
                reason=forbidden_reason,
                confidence=1.0,
                edge_source=source_id,
                edge_target=target_id,
                details={
                    'source_layer': source_layer,
                    'target_layer': target_layer,
                    'edge_type': edge.get('edge_type', 'unknown'),
                }
            ))

        return violations

    def validate_graph(
        self,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Validate all nodes and edges in a graph.

        Returns a validation report with violations by tier.
        """
        all_violations: List[Violation] = []

        # Build node lookup
        node_by_id = {}
        for node in nodes:
            node_id = node.get('id', node.get('name', ''))
            if node_id:
                node_by_id[node_id] = node

        # Validate all nodes
        for node in nodes:
            violations = self.validate_node(node)
            all_violations.extend(violations)

        # Validate all edges
        for edge in edges:
            source_id = edge.get('source', '')
            target_id = edge.get('target', '')

            source_node = node_by_id.get(source_id)
            target_node = node_by_id.get(target_id)

            if source_node and target_node:
                violations = self.validate_edge(source_node, target_node, edge)
                all_violations.extend(violations)

        # Group by tier
        tier_a = [v for v in all_violations if v.tier == ViolationTier.A]
        tier_b = [v for v in all_violations if v.tier == ViolationTier.B]
        tier_c = [v for v in all_violations if v.tier == ViolationTier.C]

        # Compute metrics
        total_nodes = len(nodes)
        antimatter_nodes = set(v.node_id for v in tier_a)
        policy_nodes = set(v.node_id for v in tier_b)

        report = {
            'total_nodes': total_nodes,
            'total_edges': len(edges),
            'total_violations': len(all_violations),

            # Tier A: Antimatter
            'antimatter': {
                'count': len(tier_a),
                'nodes_affected': len(antimatter_nodes),
                'rho_antimatter': len(antimatter_nodes) / total_nodes if total_nodes else 0,
                'violations': [v.to_dict() for v in tier_a],
            },

            # Tier B: Policy
            'policy_violations': {
                'count': len(tier_b),
                'nodes_affected': len(policy_nodes),
                'rho_policy': len(policy_nodes) / total_nodes if total_nodes else 0,
                'violations': [v.to_dict() for v in tier_b],
            },

            # Tier C: Signals
            'signals': {
                'count': len(tier_c),
                'rho_signal': sum(v.confidence for v in tier_c) / total_nodes if total_nodes else 0,
                'violations': [v.to_dict() for v in tier_c],
            },

            # Validity
            'valid_axioms': len(tier_a) == 0,
            'valid_invariants': len(tier_b) == 0,
            'valid': len(tier_a) == 0 and len(tier_b) == 0,

            # Profiles used
            'architecture_profile': self.arch_profile.id,
            'dimension_profile': self.dim_profile.id,
        }

        return report


def validate_graph(
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, Any]],
    arch_profile: str = 'classic_layered',
    dim_profile: str = 'oop_conventional',
) -> Dict[str, Any]:
    """
    Convenience function to validate a graph with specified profiles.

    Returns validation report.
    """
    loader = get_profile_loader()
    arch = loader.load_architecture_profile(arch_profile)
    dim = loader.load_dimension_profile(dim_profile)

    engine = ConstraintEngine(arch_profile=arch, dim_profile=dim)
    return engine.validate_graph(nodes, edges)


if __name__ == '__main__':
    # Test with sample data
    test_nodes = [
        {
            'id': 'test1',
            'name': 'ImmutableMutator',
            'role': 'Mutator',
            'rpbl': {'R': 'Create', 'P': 'Pure', 'B': 'Domain', 'L': 'Immutable'},
        },
        {
            'id': 'test2',
            'name': 'PureEntity',
            'role': 'Entity',
            'rpbl': {'R': 'Read', 'P': 'Pure', 'B': 'Domain', 'L': 'Scoped'},
        },
        {
            'id': 'test3',
            'name': 'ValidService',
            'role': 'Service',
            'layer': 'APPLICATION',
            'rpbl': {'R': 'Read', 'P': 'Impure', 'B': 'Application', 'L': 'Singleton'},
        },
    ]

    test_edges = [
        {'source': 'test3', 'target': 'test2', 'edge_type': 'calls'},
    ]

    engine = ConstraintEngine()
    report = engine.validate_graph(test_nodes, test_edges)

    print("=== CONSTRAINT VALIDATION REPORT ===")
    print(f"Total nodes: {report['total_nodes']}")
    print(f"Total violations: {report['total_violations']}")
    print(f"\nAntimatter (Tier A): {report['antimatter']['count']}")
    for v in report['antimatter']['violations']:
        print(f"  - {v['node_id']}: {v['reason']}")
    print(f"\nPolicy (Tier B): {report['policy_violations']['count']}")
    print(f"\nSignals (Tier C): {report['signals']['count']}")
    print(f"\nValid: {report['valid']}")
