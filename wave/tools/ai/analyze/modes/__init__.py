"""
Modes Package - Analysis Mode Implementations
=============================================

Standard Model Classification:
-----------------------------
D1_KIND:     ORG.PKG.O (Organizational Package)
D2_LAYER:    Application (mode orchestration)
D3_ROLE:     Controller (routes to appropriate mode)
D4_BOUNDARY: Internal (mode selection logic)
D5_STATE:    Stateless (mode definitions are static)
D6_EFFECT:   Pure (mode lookup is deterministic)
D7_LIFECYCLE: Use (called during analysis)
D8_TRUST:    95 (simple mode selection)

Purpose Emergence: pi2 Molecular
    Each mode is a focused configuration of analysis behavior.
    Modes modify HOW analysis is done, not WHAT tier is used.

Analysis Modes:
    standard:        General codebase analysis
    forensic:        Line-by-line code inspection with citations
    architect:       Architecture-focused with theory context
    interactive:     Multi-turn conversation
    insights:        Structured JSON output
    role_validation: Role registry audit
    plan_validation: Implementation plan verification
    trace:           Evolutionary trace (archeology)
"""

from typing import Dict, Any, List

# Mode definitions (loaded from prompts.yaml in practice)
MODE_METADATA = {
    "standard": {
        "description": "General codebase analysis",
        "requires_line_numbers": False,
        "output_format": "markdown",
    },
    "forensic": {
        "description": "Line-by-line code inspection with citations",
        "requires_line_numbers": True,
        "output_format": "markdown",
    },
    "architect": {
        "description": "Architecture-focused analysis with theory context",
        "requires_line_numbers": False,
        "output_format": "markdown",
        "auto_inject": ["MODEL.md", "COLLIDER_ARCHITECTURE.md"],
    },
    "interactive": {
        "description": "Multi-turn conversation mode",
        "requires_line_numbers": True,
        "output_format": "markdown",
    },
    "insights": {
        "description": "Structured JSON output for automation",
        "requires_line_numbers": False,
        "output_format": "json",
    },
    "role_validation": {
        "description": "Role registry audit",
        "requires_line_numbers": False,
        "output_format": "json",
    },
    "plan_validation": {
        "description": "Implementation plan verification",
        "requires_line_numbers": False,
        "output_format": "json",
    },
    "trace": {
        "description": "Evolutionary trace (archeology)",
        "requires_line_numbers": False,
        "output_format": "markdown",
    },
}


def get_mode_info(mode: str) -> Dict[str, Any]:
    """
    Get metadata for an analysis mode.

    Args:
        mode: Mode name

    Returns:
        Mode metadata dict
    """
    return MODE_METADATA.get(mode, {
        "description": "Unknown mode",
        "requires_line_numbers": False,
        "output_format": "markdown",
    })


def list_modes() -> List[str]:
    """Get list of available modes."""
    return list(MODE_METADATA.keys())


def requires_line_numbers(mode: str) -> bool:
    """Check if mode requires line numbers in context."""
    return get_mode_info(mode).get("requires_line_numbers", False)


__all__ = [
    "MODE_METADATA",
    "get_mode_info",
    "list_modes",
    "requires_line_numbers",
]
