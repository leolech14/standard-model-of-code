#!/usr/bin/env python3
"""
FABRIC BRIDGE - Communication Fabric Integration for Decision Deck
===================================================================

Bridges the gap between system-level Communication Fabric metrics
and agent-level decision making.

This module provides:
1. Fabric-aware precondition checks (e.g., "stability_ok", "noise_acceptable")
2. Risk assessment based on current fabric state
3. Context injection with fabric awareness
4. Card filtering based on system health

The key insight: Agents need to CONSUME fabric metrics at decision time,
not just observe them in dashboards.

Usage in card YAML:
    preconditions:
      - check: "fabric.stability_ok"
        description: "System stability margin must be positive"
      - check: "fabric.noise_acceptable"
        description: "Noise level must be below 0.7"

Usage in code:
    from fabric_bridge import FabricBridge
    bridge = FabricBridge()

    # Check if action is safe
    safe, warnings = bridge.assess_action_risk("refactor")

    # Get fabric-aware context
    context = bridge.get_fabric_context()
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

# Add paths for imports
SCRIPT_DIR = Path(__file__).parent.resolve()  # This is deck/
# SCRIPT_DIR parents: [0]=ai, [1]=tools, [2]=context-management, [3]=PROJECT_elements
REPO_ROOT = SCRIPT_DIR.parents[3]  # PROJECT_elements

# Try to import fabric module
FABRIC_AVAILABLE = False
compute_state_vector = None

# First try direct path import
fabric_path = REPO_ROOT / ".agent" / "intelligence" / "comms" / "fabric.py"
if fabric_path.exists():
    import importlib.util
    spec = importlib.util.spec_from_file_location("fabric", fabric_path)
    if spec and spec.loader:
        fabric_module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(fabric_module)
            compute_state_vector = fabric_module.compute_state_vector
            FABRIC_AVAILABLE = True
        except Exception:
            pass


class ActionRisk(Enum):
    """Risk levels for actions based on fabric state."""
    SAFE = "safe"           # All metrics healthy
    CAUTION = "caution"     # Some warnings, proceed carefully
    RISKY = "risky"         # System stressed, prefer conservative actions
    BLOCKED = "blocked"     # Critical state, only safe actions allowed


@dataclass
class FabricState:
    """Simplified fabric state for agent consumption."""
    available: bool
    stability_margin: float
    stability_ok: bool
    noise: float
    noise_acceptable: bool
    mi: float
    mi_adequate: bool
    r_auto: float
    redundancy_ok: bool
    delta_h: float
    system_stable: bool
    health_tier: str
    risk_level: ActionRisk
    warnings: List[str]
    recommendations: List[str]


# Thresholds for agent decisions
THRESHOLDS = {
    "stability_ok": 0.1,        # Margin above this = stable
    "stability_caution": 0.3,   # Below this = be careful
    "noise_acceptable": 0.7,    # Noise below this = acceptable
    "noise_low": 0.4,           # Noise below this = clean
    "mi_adequate": 0.5,         # MI above this = docs trustworthy
    "mi_good": 0.7,             # MI above this = excellent alignment
    "redundancy_ok": 0.5,       # R_auto above this = tests adequate
    "delta_h_stable": 0.5,      # Below this = system not in flux
}


class FabricBridge:
    """
    Bridge between Communication Fabric and Decision Deck.

    Translates system-level metrics into agent-actionable signals.
    """

    def __init__(self, cache_seconds: int = 60):
        self._cache: Optional[FabricState] = None
        self._cache_time: float = 0
        self._cache_seconds = cache_seconds

    def get_state(self, force_refresh: bool = False) -> FabricState:
        """
        Get current fabric state, with caching.

        Returns a simplified state object optimized for agent decisions.
        """
        import time

        now = time.time()
        if not force_refresh and self._cache and (now - self._cache_time) < self._cache_seconds:
            return self._cache

        if not FABRIC_AVAILABLE:
            # Return safe defaults when fabric not available
            return FabricState(
                available=False,
                stability_margin=1.0,
                stability_ok=True,
                noise=0.0,
                noise_acceptable=True,
                mi=1.0,
                mi_adequate=True,
                r_auto=1.0,
                redundancy_ok=True,
                delta_h=0.0,
                system_stable=True,
                health_tier="UNKNOWN",
                risk_level=ActionRisk.SAFE,
                warnings=["Fabric module not available - assuming safe defaults"],
                recommendations=[],
            )

        try:
            # Get live metrics
            sv = compute_state_vector()

            # Compute agent-relevant flags
            stability_ok = sv.stability_margin > THRESHOLDS["stability_ok"]
            noise_acceptable = sv.N < THRESHOLDS["noise_acceptable"]
            mi_adequate = sv.MI > THRESHOLDS["mi_adequate"]
            redundancy_ok = sv.R_auto > THRESHOLDS["redundancy_ok"]
            system_stable = stability_ok and sv.delta_H < THRESHOLDS["delta_h_stable"]

            # Assess risk level
            warnings = []
            recommendations = []

            if sv.stability_margin < 0:
                risk_level = ActionRisk.BLOCKED
                warnings.append(f"CRITICAL: Stability margin negative ({sv.stability_margin:.4f})")
                recommendations.append("Only execute low-risk, reversible actions")
            elif sv.stability_margin < THRESHOLDS["stability_ok"]:
                risk_level = ActionRisk.RISKY
                warnings.append(f"Stability margin critically low ({sv.stability_margin:.4f})")
                recommendations.append("Prefer conservative actions")
            elif sv.stability_margin < THRESHOLDS["stability_caution"]:
                risk_level = ActionRisk.CAUTION
                warnings.append(f"Stability margin below comfort ({sv.stability_margin:.4f})")
            else:
                risk_level = ActionRisk.SAFE

            # Additional warnings
            if sv.N > THRESHOLDS["noise_acceptable"]:
                if risk_level == ActionRisk.SAFE:
                    risk_level = ActionRisk.CAUTION
                warnings.append(f"High noise level ({sv.N:.4f}) - analysis results may be noisy")
                recommendations.append("Consider cleanup before major analysis")

            if sv.MI < THRESHOLDS["mi_adequate"]:
                warnings.append(f"Low mutual information ({sv.MI:.4f}) - docs may not reflect code")
                recommendations.append("Verify assumptions against actual code")

            if sv.delta_H > THRESHOLDS["delta_h_stable"]:
                warnings.append(f"High change entropy ({sv.delta_H:.4f}) - system in flux")
                recommendations.append("Be prepared for context to shift")

            state = FabricState(
                available=True,
                stability_margin=sv.stability_margin,
                stability_ok=stability_ok,
                noise=sv.N,
                noise_acceptable=noise_acceptable,
                mi=sv.MI,
                mi_adequate=mi_adequate,
                r_auto=sv.R_auto,
                redundancy_ok=redundancy_ok,
                delta_h=sv.delta_H,
                system_stable=system_stable,
                health_tier=sv.health_tier,
                risk_level=risk_level,
                warnings=warnings,
                recommendations=recommendations,
            )

            self._cache = state
            self._cache_time = now
            return state

        except Exception as e:
            return FabricState(
                available=False,
                stability_margin=1.0,
                stability_ok=True,
                noise=0.0,
                noise_acceptable=True,
                mi=1.0,
                mi_adequate=True,
                r_auto=1.0,
                redundancy_ok=True,
                delta_h=0.0,
                system_stable=True,
                health_tier="ERROR",
                risk_level=ActionRisk.SAFE,
                warnings=[f"Fabric error: {e}"],
                recommendations=[],
            )

    def check_precondition(self, condition: str) -> Tuple[bool, str]:
        """
        Check a fabric-related precondition.

        Args:
            condition: Precondition string like "fabric.stability_ok"

        Returns:
            (passed, message)
        """
        state = self.get_state()

        # Parse condition
        if not condition.startswith("fabric."):
            return True, "Not a fabric condition"

        check = condition[7:]  # Remove "fabric." prefix

        checks = {
            "stability_ok": (state.stability_ok, f"Stability margin: {state.stability_margin:.4f}"),
            "stability_positive": (state.stability_margin > 0, f"Margin: {state.stability_margin:.4f}"),
            "noise_acceptable": (state.noise_acceptable, f"Noise: {state.noise:.4f}"),
            "noise_low": (state.noise < THRESHOLDS["noise_low"], f"Noise: {state.noise:.4f}"),
            "mi_adequate": (state.mi_adequate, f"MI: {state.mi:.4f}"),
            "mi_good": (state.mi > THRESHOLDS["mi_good"], f"MI: {state.mi:.4f}"),
            "redundancy_ok": (state.redundancy_ok, f"R_auto: {state.r_auto:.4f}"),
            "system_stable": (state.system_stable, f"Stable: {state.system_stable}"),
            "not_blocked": (state.risk_level != ActionRisk.BLOCKED, f"Risk: {state.risk_level.value}"),
            "safe_for_refactor": (
                state.stability_ok and state.redundancy_ok,
                f"Margin: {state.stability_margin:.4f}, R_auto: {state.r_auto:.4f}"
            ),
            "safe_for_analysis": (
                state.noise_acceptable,
                f"Noise: {state.noise:.4f}"
            ),
        }

        if check in checks:
            passed, detail = checks[check]
            return passed, detail

        return True, f"Unknown fabric check: {check}"

    def assess_action_risk(self, action_type: str) -> Tuple[ActionRisk, List[str]]:
        """
        Assess the risk of performing a specific type of action.

        Args:
            action_type: Type of action (refactor, analyze, commit, etc.)

        Returns:
            (risk_level, warnings)
        """
        state = self.get_state()
        warnings = list(state.warnings)  # Copy

        # Action-specific risk assessment
        if action_type in ["refactor", "restructure", "migrate"]:
            # High-risk actions need stable system
            if not state.stability_ok:
                return ActionRisk.BLOCKED, warnings + ["Refactoring blocked: stability too low"]
            if not state.redundancy_ok:
                return ActionRisk.RISKY, warnings + ["Low test coverage - refactoring risky"]
            if state.delta_h > THRESHOLDS["delta_h_stable"]:
                return ActionRisk.CAUTION, warnings + ["System in flux - proceed carefully"]

        elif action_type in ["analyze", "collider", "scan"]:
            # Analysis quality depends on noise
            if not state.noise_acceptable:
                return ActionRisk.CAUTION, warnings + ["High noise will affect analysis quality"]

        elif action_type in ["commit", "save"]:
            # Commits are generally safe
            pass

        elif action_type in ["document", "docs"]:
            # Documentation updates need MI context
            if not state.mi_adequate:
                return ActionRisk.CAUTION, warnings + ["Existing docs may be stale (low MI)"]

        return state.risk_level, warnings

    def get_fabric_context(self) -> str:
        """
        Generate human-readable context about fabric state for agent injection.

        This is what agents should SEE when making decisions.
        """
        state = self.get_state()

        if not state.available:
            return "## System Health: UNKNOWN (Fabric unavailable)\n"

        lines = [
            "## System Health Context",
            f"Health Tier: **{state.health_tier}**",
            f"Risk Level: **{state.risk_level.value.upper()}**",
            "",
            "### Key Metrics",
            f"- Stability Margin: {state.stability_margin:+.4f} ({'OK' if state.stability_ok else 'LOW'})",
            f"- Noise Level: {state.noise:.4f} ({'OK' if state.noise_acceptable else 'HIGH'})",
            f"- Mutual Information: {state.mi:.4f} ({'OK' if state.mi_adequate else 'LOW'})",
            f"- Test Coverage (R_auto): {state.r_auto:.4f} ({'OK' if state.redundancy_ok else 'LOW'})",
            f"- Change Entropy: {state.delta_h:.4f} ({'STABLE' if state.delta_h < 0.5 else 'IN FLUX'})",
            "",
        ]

        if state.warnings:
            lines.append("### Warnings")
            for w in state.warnings:
                lines.append(f"- {w}")
            lines.append("")

        if state.recommendations:
            lines.append("### Recommendations")
            for r in state.recommendations:
                lines.append(f"- {r}")
            lines.append("")

        return "\n".join(lines)

    def filter_cards_by_risk(self, cards: List[Any], max_risk: ActionRisk = ActionRisk.CAUTION) -> List[Any]:
        """
        Filter cards based on system risk level.

        In stressed systems, only allow low-risk cards.
        """
        state = self.get_state()

        # Risk ordering
        risk_order = [ActionRisk.SAFE, ActionRisk.CAUTION, ActionRisk.RISKY, ActionRisk.BLOCKED]
        max_index = risk_order.index(max_risk)

        # If system is blocked, only allow explicitly safe cards
        if state.risk_level == ActionRisk.BLOCKED:
            return [c for c in cards if c.cost.get("risk_level", "MEDIUM").upper() == "LOW"]

        # If system is risky, filter out high-risk cards
        if state.risk_level == ActionRisk.RISKY:
            return [c for c in cards if c.cost.get("risk_level", "MEDIUM").upper() != "HIGH"]

        return cards


# Singleton for easy access
_bridge: Optional[FabricBridge] = None

def get_bridge() -> FabricBridge:
    """Get or create the singleton bridge instance."""
    global _bridge
    if _bridge is None:
        _bridge = FabricBridge()
    return _bridge


def check_fabric_precondition(condition: str) -> Tuple[bool, str]:
    """Convenience function for precondition checks."""
    return get_bridge().check_precondition(condition)


def get_fabric_context() -> str:
    """Convenience function for context injection."""
    return get_bridge().get_fabric_context()


def assess_risk(action_type: str) -> Tuple[ActionRisk, List[str]]:
    """Convenience function for risk assessment."""
    return get_bridge().assess_action_risk(action_type)


# CLI for testing
if __name__ == "__main__":
    import json

    bridge = FabricBridge()
    state = bridge.get_state()

    print("=" * 60)
    print("FABRIC BRIDGE - Agent Decision Context")
    print("=" * 60)
    print()
    print(bridge.get_fabric_context())

    print("=" * 60)
    print("PRECONDITION CHECKS")
    print("=" * 60)
    checks = [
        "fabric.stability_ok",
        "fabric.noise_acceptable",
        "fabric.mi_adequate",
        "fabric.redundancy_ok",
        "fabric.safe_for_refactor",
        "fabric.safe_for_analysis",
    ]
    for check in checks:
        passed, detail = bridge.check_precondition(check)
        status = "PASS" if passed else "FAIL"
        print(f"  {check}: {status} ({detail})")

    print()
    print("=" * 60)
    print("ACTION RISK ASSESSMENT")
    print("=" * 60)
    actions = ["refactor", "analyze", "commit", "document"]
    for action in actions:
        risk, warnings = bridge.assess_action_risk(action)
        print(f"  {action}: {risk.value}")
        if warnings:
            for w in warnings[:2]:
                print(f"    - {w}")
