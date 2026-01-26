#!/usr/bin/env python3
"""
Intel - Unified AI Subsystem Query Interface

The narrator's voice. Provides context to any AI agent via:
- Files (read directly)
- CLI (./pe intel)
- Import (from intel import get_context)

Context Sets:
- minimal: One-line health check (lowest tokens)
- deck: Meters + cards + recent plays
- session: Current session state
- truths: Pre-computed repository facts
- full: Everything combined

Usage:
    ./pe intel                     # Default: minimal
    ./pe intel --set deck          # Deck-focused
    ./pe intel --set full          # Everything
    ./pe intel --include meters,cards,alerts
    ./pe intel --format yaml       # YAML output (default)
    ./pe intel --format json       # JSON output
    ./pe intel --format oneline    # Single line
"""

import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
AGENT_DIR = PROJECT_ROOT / ".agent"
DECK_DIR = SCRIPT_DIR / "deck"

# State files
METERS_FILE = AGENT_DIR / "state" / "meters.yaml"
PLAY_LOG = AGENT_DIR / "state" / "play_log.yaml"
TRUTHS_FILE = AGENT_DIR / "intelligence" / "truths" / "repo_truths.yaml"
SESSION_FILE = AGENT_DIR / "state" / "session.yaml"


# =============================================================================
# DATA LOADERS
# =============================================================================

def load_meters() -> Dict[str, int]:
    """Load current meter values."""
    if METERS_FILE.exists():
        with open(METERS_FILE) as f:
            return yaml.safe_load(f) or {}
    return {"focus": 0, "reliability": 0, "discovery": 0, "debt": 0, "readiness": 0}


def load_recent_plays(limit: int = 3) -> List[Dict[str, Any]]:
    """Load recent card plays."""
    if not PLAY_LOG.exists():
        return []
    with open(PLAY_LOG) as f:
        history = yaml.safe_load(f) or []
    return history[-limit:]


def load_available_cards() -> List[str]:
    """Get list of available card IDs."""
    if not DECK_DIR.exists():
        return []
    return sorted([f.stem for f in DECK_DIR.glob("CARD-*.yaml")])


def load_truths() -> Dict[str, Any]:
    """Load pre-computed repository truths."""
    if not TRUTHS_FILE.exists():
        return {}
    with open(TRUTHS_FILE) as f:
        return yaml.safe_load(f) or {}


def load_session() -> Dict[str, Any]:
    """Load current session state."""
    if not SESSION_FILE.exists():
        return {"active": False}
    with open(SESSION_FILE) as f:
        return yaml.safe_load(f) or {"active": False}


def get_health() -> str:
    """Calculate overall health status."""
    meters = load_meters()
    debt = meters.get("debt", 0)
    reliability = meters.get("reliability", 0)

    if debt > 5:
        return "CRITICAL"
    elif debt > 2 or reliability < 0:
        return "DEGRADED"
    return "HEALTHY"


def get_alerts() -> List[str]:
    """Get current alerts (drift, issues, etc.)."""
    alerts = []

    # Check for high debt
    meters = load_meters()
    if meters.get("debt", 0) > 2:
        alerts.append(f"debt: {meters['debt']} (high)")

    # Could add: drift detection, stale files, etc.

    return alerts


# =============================================================================
# CONTEXT SETS
# =============================================================================

def get_minimal() -> Dict[str, Any]:
    """Minimal context - lowest token cost."""
    return {
        "health": get_health(),
        "cards": len(load_available_cards()),
        "alerts": len(get_alerts()),
    }


def get_deck() -> Dict[str, Any]:
    """Deck-focused context."""
    return {
        "health": get_health(),
        "meters": load_meters(),
        "available_cards": load_available_cards(),
        "recent_plays": load_recent_plays(),
        "alerts": get_alerts(),
    }


def get_session() -> Dict[str, Any]:
    """Session-focused context."""
    return {
        "health": get_health(),
        "session": load_session(),
        "meters": load_meters(),
    }


def get_truths_context() -> Dict[str, Any]:
    """Truths-focused context."""
    truths = load_truths()
    return {
        "health": get_health(),
        "truths": truths,
    }


def get_full() -> Dict[str, Any]:
    """Full context - everything."""
    return {
        "timestamp": datetime.now().isoformat(),
        "health": get_health(),
        "meters": load_meters(),
        "available_cards": load_available_cards(),
        "recent_plays": load_recent_plays(5),
        "session": load_session(),
        "truths_summary": {
            "loaded": TRUTHS_FILE.exists(),
            "keys": list(load_truths().keys()) if TRUTHS_FILE.exists() else [],
        },
        "alerts": get_alerts(),
    }


# Context set registry
CONTEXT_SETS = {
    "minimal": get_minimal,
    "deck": get_deck,
    "session": get_session,
    "truths": get_truths_context,
    "full": get_full,
}


def get_custom(include: List[str]) -> Dict[str, Any]:
    """Build custom context from specified components."""
    result = {"health": get_health()}

    component_map = {
        "meters": ("meters", load_meters),
        "cards": ("available_cards", load_available_cards),
        "plays": ("recent_plays", load_recent_plays),
        "truths": ("truths", load_truths),
        "session": ("session", load_session),
        "alerts": ("alerts", get_alerts),
    }

    for component in include:
        if component in component_map:
            key, loader = component_map[component]
            result[key] = loader()

    return result


# =============================================================================
# FORMATTERS
# =============================================================================

def format_yaml(data: Dict[str, Any]) -> str:
    """Format as YAML (default - best for LLMs)."""
    return yaml.dump(data, default_flow_style=False, sort_keys=False)


def format_json(data: Dict[str, Any]) -> str:
    """Format as JSON."""
    return json.dumps(data, indent=2, default=str)


def format_oneline(data: Dict[str, Any]) -> str:
    """Format as single line (minimal tokens)."""
    parts = []
    for key, value in data.items():
        if isinstance(value, list):
            parts.append(f"{key}: {len(value)}")
        elif isinstance(value, dict):
            parts.append(f"{key}: {len(value)} keys")
        else:
            parts.append(f"{key}: {value}")
    return " | ".join(parts)


FORMATTERS = {
    "yaml": format_yaml,
    "json": format_json,
    "oneline": format_oneline,
}


# =============================================================================
# MAIN API
# =============================================================================

def get_context(
    set_name: str = "minimal",
    include: Optional[List[str]] = None,
    format: str = "yaml"
) -> str:
    """
    Get formatted context for AI injection.

    Args:
        set_name: Predefined set (minimal, deck, session, truths, full)
        include: Custom list of components (overrides set_name)
        format: Output format (yaml, json, oneline)

    Returns:
        Formatted context string
    """
    # Get data
    if include:
        data = get_custom(include)
    elif set_name in CONTEXT_SETS:
        data = CONTEXT_SETS[set_name]()
    else:
        data = get_minimal()

    # Format
    formatter = FORMATTERS.get(format, format_yaml)
    return formatter(data)


# =============================================================================
# CLI
# =============================================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Intel - Unified AI Subsystem Query Interface"
    )
    parser.add_argument(
        "--set", "-s",
        choices=list(CONTEXT_SETS.keys()),
        default="minimal",
        help="Predefined context set"
    )
    parser.add_argument(
        "--include", "-i",
        help="Custom components (comma-separated): meters,cards,plays,truths,session,alerts"
    )
    parser.add_argument(
        "--format", "-f",
        choices=list(FORMATTERS.keys()),
        default="yaml",
        help="Output format"
    )

    args = parser.parse_args()

    include = args.include.split(",") if args.include else None
    output = get_context(set_name=args.set, include=include, format=args.format)
    print(output)


if __name__ == "__main__":
    main()
