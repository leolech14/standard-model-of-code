#!/usr/bin/env python3
"""
Decision Deck Dealer

Reads current state and deals available cards to the agent.
This is the core engine of the Decision Deck Layer.

Usage:
    python deal_cards.py                    # Show available cards
    python deal_cards.py --phase DESIGNING  # Filter by phase
    python deal_cards.py --format minimal   # Minimal output
    python deal_cards.py --json             # JSON output for tooling
"""

import argparse
import os
import sys
import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any

# Paths
AGENT_DIR = Path(__file__).parent.parent
DECK_DIR = AGENT_DIR / "deck"
STATE_DIR = AGENT_DIR / "state"
METERS_FILE = STATE_DIR / "meters.yaml"
REGISTRY_DIR = AGENT_DIR / "registry"
SPRINTS_DIR = AGENT_DIR / "sprints"


def load_deck() -> List[Dict]:
    """Load all cards from deck directory."""
    cards = []
    if not DECK_DIR.exists():
        return cards

    for card_file in sorted(DECK_DIR.glob("CARD-*.yaml")):
        try:
            with open(card_file) as f:
                card = yaml.safe_load(f)
                if card:
                    cards.append(card)
        except Exception as e:
            print(f"Warning: Failed to load {card_file}: {e}", file=sys.stderr)

    return cards


def load_meters() -> Dict:
    """Load current meter values."""
    if not METERS_FILE.exists():
        return {
            "focus": 5,
            "reliability": 5,
            "debt": 2,
            "discovery": 5
        }

    with open(METERS_FILE) as f:
        data = yaml.safe_load(f)

    return {k: v["value"] for k, v in data.get("meters", {}).items()}


def get_current_phase() -> str:
    """Detect current sprint phase from active sprint."""
    # Look for active sprint
    if SPRINTS_DIR.exists():
        for sprint_file in SPRINTS_DIR.glob("SPRINT-*.yaml"):
            try:
                with open(sprint_file) as f:
                    sprint = yaml.safe_load(f)
                    if sprint.get("status") == "ACTIVE":
                        return sprint.get("phase", "DESIGNING")
            except:
                pass

    return "DESIGNING"  # Default phase


def check_precondition(precondition: Dict, state: Dict) -> bool:
    """
    Check if a precondition is satisfied.

    This is a simplified checker - in production, this would
    evaluate actual conditions against real state.
    """
    check = precondition.get("check", "")

    # Simple pattern matching for common checks
    if "file_exists" in check:
        # Extract path pattern and check
        # For now, assume true (would need real implementation)
        return True

    if "confidence" in check and "confidence_min" in precondition:
        # Check confidence thresholds
        mins = precondition["confidence_min"]
        for dim, min_val in mins.items():
            # Would need to check actual task/opportunity confidence
            pass
        return True  # Simplified

    if "meters." in check:
        # Check meter thresholds
        meters = state.get("meters", {})
        # Parse "meters.debt <= 5" style checks
        return True  # Simplified

    if "git_has_changes" in check:
        # Check for git changes
        result = os.popen("git status --porcelain 2>/dev/null").read()
        return len(result.strip()) > 0

    # Default: assume satisfied
    return True


def filter_cards(cards: List[Dict], phase: str, state: Dict) -> List[Dict]:
    """Filter cards by phase gate and preconditions."""
    playable = []

    for card in cards:
        # Skip wildcard (always added at end)
        if card.get("id") == "CARD-WLD-000":
            continue

        # Check phase gate
        gates = card.get("phase_gate", [])
        if phase not in gates and "ANY" not in gates:
            continue

        # Check preconditions
        all_satisfied = True
        for precond in card.get("preconditions", []):
            if not check_precondition(precond, state):
                all_satisfied = False
                break

        if all_satisfied:
            playable.append(card)

    return playable


def render_meter_bar(value: int, max_val: int = 10, width: int = 10) -> str:
    """Render a visual meter bar."""
    filled = int((value / max_val) * width)
    empty = width - filled
    return "█" * filled + "░" * empty


def format_card_full(card: Dict, index: int) -> str:
    """Format a card for full display."""
    lines = []
    lines.append(f"  [{index}] {card['id']}: {card['title']}")

    # Preconditions
    preconditions = card.get("preconditions", [])
    if preconditions:
        checks = ", ".join([f"✓ {p.get('description', p.get('check', '?'))[:30]}"
                          for p in preconditions[:2]])
        lines.append(f"      ├─ Preconditions: {checks}")

    # Cost
    cost = card.get("cost", {})
    tokens = cost.get("tokens_estimate", "?")
    risk = cost.get("risk_level", "?")
    lines.append(f"      ├─ Cost: ~{tokens} tokens, {risk} risk")

    # Unlocks or meters
    outcomes = card.get("outcomes", {}).get("success", {})
    unlocks = outcomes.get("unlocks", [])
    meters = outcomes.get("meters", {})

    if unlocks:
        lines.append(f"      └─ Unlocks: {', '.join(unlocks[:3])}")
    elif meters:
        meter_str = ", ".join([f"{k}: {'+' if v > 0 else ''}{v}" for k, v in meters.items()])
        lines.append(f"      └─ Meters: {meter_str}")
    else:
        lines.append(f"      └─ Tags: {', '.join(card.get('tags', [])[:3])}")

    return "\n".join(lines)


def format_card_minimal(card: Dict, index: int) -> str:
    """Format a card for minimal display."""
    title_short = card['title'][:15]
    return f"[{index}]{title_short}"


def display_full(cards: List[Dict], phase: str, meters: Dict):
    """Full display format for chat."""
    print("╔══════════════════════════════════════════════════════════════╗")
    print(f"║  AVAILABLE ACTIONS                          Phase: {phase:10} ║")
    print("╠══════════════════════════════════════════════════════════════╣")
    print("║                                                              ║")

    for i, card in enumerate(cards, 1):
        formatted = format_card_full(card, i)
        for line in formatted.split("\n"):
            print(f"║ {line:<60} ║")
        print("║                                                              ║")

    # Wildcard
    print("║  [W] WILDCARD: Custom Action (requires justification)        ║")
    print("║      └─ Warning: Exits constrained mode, logged              ║")
    print("║                                                              ║")
    print("╚══════════════════════════════════════════════════════════════╝")


def display_minimal(cards: List[Dict], phase: str):
    """Minimal display format for tight contexts."""
    card_strs = [format_card_minimal(card, i) for i, card in enumerate(cards, 1)]
    print(f"DECK [{phase}]: {' '.join(card_strs)} [W]Wildcard")


def display_meters(meters: Dict):
    """Display current meter values."""
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  METERS                                                      ║")
    print("╠══════════════════════════════════════════════════════════════╣")

    for name, value in meters.items():
        bar = render_meter_bar(value)
        status = ""
        if value <= 2:
            status = "CRITICAL"
        elif value <= 4:
            status = "LOW"
        elif value >= 8:
            status = "HIGH"

        line = f"    {name.capitalize():12} {bar} {value:2}/10 {status}"
        print(f"║ {line:<60} ║")

    print("╚══════════════════════════════════════════════════════════════╝")


def main():
    parser = argparse.ArgumentParser(description="Deal available cards from Decision Deck")
    parser.add_argument("--phase", choices=["DESIGNING", "EXECUTING", "VALIDATING", "COMPLETE"],
                       help="Override current phase")
    parser.add_argument("--format", choices=["full", "minimal"], default="full",
                       help="Output format")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--meters", action="store_true", help="Show meters")
    parser.add_argument("--max", type=int, default=5, help="Maximum cards to show")

    args = parser.parse_args()

    # Load state
    deck = load_deck()
    meters = load_meters()
    phase = args.phase or get_current_phase()

    state = {
        "meters": meters,
        "phase": phase,
    }

    # Filter cards
    playable = filter_cards(deck, phase, state)[:args.max]

    # Output
    if args.json:
        output = {
            "phase": phase,
            "meters": meters,
            "cards": [{"id": c["id"], "title": c["title"]} for c in playable],
            "wildcard": True
        }
        print(json.dumps(output, indent=2))
    elif args.format == "minimal":
        display_minimal(playable, phase)
    else:
        display_full(playable, phase, meters)
        if args.meters:
            print()
            display_meters(meters)


if __name__ == "__main__":
    main()
