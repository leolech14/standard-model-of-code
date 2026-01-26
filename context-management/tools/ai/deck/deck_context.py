#!/usr/bin/env python3
"""
Deck Context - Dynamic state generator for ACI integration

Generates context summaries about the Decision Deck for injection into AI queries.
This allows AI to be awareness of:
1. Current meter values (focus, reliability, discovery, debt, readiness)
2. Recent card plays (what was done, outcomes)
3. Available cards (what moves are currently valid)

Usage:
    # Get context for AI query injection
    from deck_context import get_deck_context
    context = get_deck_context()

    # Get specific components
    from deck_context import get_meters, get_recent_plays, get_available_cards
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent.parent
METERS_FILE = PROJECT_ROOT / ".agent" / "state" / "meters.yaml"
PLAY_LOG = PROJECT_ROOT / ".agent" / "state" / "play_log.yaml"
DECK_DIR = SCRIPT_DIR


def get_meters() -> Dict[str, int]:
    """Get current meter values."""
    if METERS_FILE.exists():
        with open(METERS_FILE) as f:
            return yaml.safe_load(f) or {}
    return {
        "focus": 0,
        "reliability": 0,
        "discovery": 0,
        "debt": 0,
        "readiness": 0,
    }


def get_recent_plays(limit: int = 5) -> List[Dict[str, Any]]:
    """Get recent card plays."""
    if not PLAY_LOG.exists():
        return []

    with open(PLAY_LOG) as f:
        history = yaml.safe_load(f) or []

    # Return most recent plays
    return history[-limit:]


def get_available_cards() -> List[Dict[str, Any]]:
    """Get list of all cards with their basic info."""
    cards = []
    for card_file in sorted(DECK_DIR.glob("CARD-*.yaml")):
        with open(card_file) as f:
            card = yaml.safe_load(f)
            if card:
                cards.append({
                    "id": card.get("id", card_file.stem),
                    "title": card.get("title", ""),
                    "phase_gate": card.get("phase_gate", []),
                    "tags": card.get("tags", []),
                })
    return cards


def get_deck_summary() -> Dict[str, Any]:
    """Get complete deck state summary."""
    meters = get_meters()
    recent_plays = get_recent_plays()
    cards = get_available_cards()

    # Calculate stats
    total_plays = len(get_recent_plays(limit=100))
    success_count = sum(1 for p in get_recent_plays(limit=100) if p.get("outcome") == "success")

    return {
        "meters": meters,
        "total_cards": len(cards),
        "total_plays": total_plays,
        "success_rate": success_count / total_plays if total_plays > 0 else 0,
        "recent_plays": recent_plays,
        "card_ids": [c["id"] for c in cards],
    }


def get_deck_context(verbose: bool = False) -> str:
    """
    Generate context string for AI query injection.

    Args:
        verbose: If True, include full card list. If False, just summary.

    Returns:
        Markdown-formatted context string
    """
    summary = get_deck_summary()
    meters = summary["meters"]

    # Build context
    lines = [
        "## Decision Deck State",
        "",
        "### Meters (Current Values)",
        f"- Focus: {meters.get('focus', 0)}",
        f"- Reliability: {meters.get('reliability', 0)}",
        f"- Discovery: {meters.get('discovery', 0)}",
        f"- Debt: {meters.get('debt', 0)}",
        f"- Readiness: {meters.get('readiness', 0)}",
        "",
        f"### Statistics",
        f"- Total Cards: {summary['total_cards']}",
        f"- Total Plays: {summary['total_plays']}",
        f"- Success Rate: {summary['success_rate']:.1%}",
    ]

    # Recent plays
    if summary["recent_plays"]:
        lines.append("")
        lines.append("### Recent Plays")
        for play in reversed(summary["recent_plays"]):
            ts = play.get("timestamp", "")[:10]  # Just date
            card = play.get("card_id", "?")
            outcome = play.get("outcome", "?")
            icon = "+" if outcome == "success" else "x"
            lines.append(f"- [{icon}] {card} ({outcome}) - {ts}")

    if verbose:
        lines.append("")
        lines.append("### Available Cards")
        for card_id in summary["card_ids"]:
            lines.append(f"- {card_id}")

    return "\n".join(lines)


def get_meter_health() -> str:
    """
    Get a one-line health summary based on meters.

    Returns:
        Health indicator: "HEALTHY", "DEGRADED", or "CRITICAL"
    """
    meters = get_meters()

    # Calculate simple health
    # High debt = bad, high reliability = good
    debt = meters.get("debt", 0)
    reliability = meters.get("reliability", 0)

    if debt > 5:
        return "CRITICAL"
    elif debt > 2 or reliability < 0:
        return "DEGRADED"
    else:
        return "HEALTHY"


def main():
    """Print deck context to stdout."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate deck context for AI queries")
    parser.add_argument("--verbose", "-v", action="store_true", help="Include full card list")
    parser.add_argument("--json", action="store_true", help="Output as JSON instead of markdown")
    parser.add_argument("--health", action="store_true", help="Just show health status")

    args = parser.parse_args()

    if args.health:
        print(get_meter_health())
    elif args.json:
        import json
        print(json.dumps(get_deck_summary(), indent=2, default=str))
    else:
        print(get_deck_context(verbose=args.verbose))


if __name__ == "__main__":
    main()
