"""
Decision Deck MCP Server

Wraps the Decision Deck governance system -- the constrained action space
where AI agents pick certified moves (cards) instead of improvising.

Server 3 of 3 in the intelligence MCP hybrid architecture.

Tools exposed:
  - deck_list_cards: List all available cards with descriptions
  - deck_route_intent: Route a natural language intent to a card
  - deck_deal_hand: Get available cards filtered by preconditions
  - deck_get_card: Get full details of a specific card
  - deck_play_card: Execute a card's steps
  - deck_get_meters: Get current meter readings
"""

import sys
import os
import json
from pathlib import Path

from fastmcp import FastMCP

# Resolve paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent.resolve()
TOOLS_DIR = PROJECT_ROOT / "wave" / "tools" / "ai"
sys.path.insert(0, str(TOOLS_DIR))
sys.path.insert(0, str(PROJECT_ROOT / "wave" / "tools"))


# --- Server ---

mcp = FastMCP(
    "DecisionDeck",
    version="1.0.0",
    instructions=(
        "Decision Deck - Constrained action governance for AI agents. "
        "Instead of free-form improvisation, agents choose from validated "
        "cards with preconditions, steps, outcomes, and rollback procedures. "
        "Use deck_deal_hand to see available moves, deck_route_intent to "
        "find the right card, and deck_play_card to execute."
    ),
)


# ─────────────────────────────────────────────
# CARD MANAGEMENT
# ─────────────────────────────────────────────

@mcp.tool(annotations={"readOnlyHint": True})
def deck_list_cards() -> str:
    """List all certified cards in the deck with their IDs and descriptions.

    Cards are validated action templates with preconditions, steps,
    expected outcomes, and rollback procedures. Returns all cards
    regardless of precondition state.

    Returns:
        JSON with card list (id, title, description, phase_gate, tags)
    """
    from deck.deck_router import DeckRouter

    router = DeckRouter()
    cards = []
    for card_id, card in sorted(router.cards.items()):
        cards.append({
            "id": card.id,
            "title": card.title,
            "description": card.description[:200],
            "phase_gate": getattr(card, "phase_gate", ""),
            "tags": getattr(card, "tags", []),
        })

    return json.dumps({
        "total_cards": len(cards),
        "cards": cards,
    }, default=str, indent=2)


@mcp.tool(annotations={"readOnlyHint": True})
def deck_route_intent(intent: str) -> str:
    """Route a natural language intent to the best matching card.

    Maps phrases like "run analysis", "commit changes", "research topic"
    to specific cards via pattern matching.

    Args:
        intent: Natural language description of what you want to do

    Returns:
        JSON with matched card ID, title, and confidence
    """
    from deck.deck_router import DeckRouter

    router = DeckRouter()
    result = router.route_intent(intent)

    # route_intent may return Card object, card_id string, or None
    card = None
    if result is not None:
        if hasattr(result, "id"):  # Card object
            card = result
        elif isinstance(result, str) and result in router.cards:
            card = router.cards[result]

    if card:
        return json.dumps({
            "matched": True,
            "card_id": card.id,
            "title": card.title,
            "description": card.description[:300],
            "steps": [s if isinstance(s, str) else str(s) for s in getattr(card, "steps", [])][:5],
        }, default=str, indent=2)
    else:
        return json.dumps({
            "matched": False,
            "suggestion": "Try: analyze code, research, commit, document, audit, start session",
        }, indent=2)


@mcp.tool(annotations={"readOnlyHint": True})
def deck_deal_hand() -> str:
    """Get available cards filtered by current preconditions.

    Only returns cards whose preconditions are satisfied based on
    current project state (meters, session, git status, etc.).
    This is what an agent should call to see its valid moves.

    Returns:
        JSON with available cards and current system state
    """
    from deck.deck_router import DeckRouter

    router = DeckRouter()
    hand = router.deal({})  # Empty state = check all preconditions

    return json.dumps({
        "hand": hand,
    }, default=str, indent=2)


@mcp.tool(annotations={"readOnlyHint": True})
def deck_get_card(card_id: str) -> str:
    """Get full details of a specific card.

    Returns the complete card definition including preconditions,
    all steps, expected outcomes, meter effects, rollback procedure,
    and context injection requirements.

    Args:
        card_id: The card ID (e.g., CARD-ANA-001, CARD-RES-001)

    Returns:
        JSON with full card specification
    """
    from deck.deck_router import DeckRouter
    import dataclasses

    router = DeckRouter()
    card = router.cards.get(card_id)

    if not card:
        return json.dumps({"error": f"Card {card_id} not found"})

    return card.to_prompt() if hasattr(card, "to_prompt") else json.dumps(
        dataclasses.asdict(card), default=str, indent=2
    )


@mcp.tool(annotations={"readOnlyHint": True})
def deck_get_meters() -> str:
    """Get current meter readings (focus, reliability, discovery, debt, readiness).

    Meters track cumulative agent state across a session.
    Cards declare meter_effects that shift these values.

    Returns:
        JSON with meter values and health status
    """
    import yaml

    meters_path = PROJECT_ROOT / ".agent" / "state" / "meters.yaml"
    if not meters_path.exists():
        return json.dumps({"error": "meters.yaml not found", "path": str(meters_path)})

    with open(meters_path) as f:
        meters = yaml.safe_load(f) or {}

    # Calculate health
    debt = meters.get("debt", 0)
    if debt > 70:
        health = "CRITICAL"
    elif debt > 40:
        health = "DEGRADED"
    else:
        health = "HEALTHY"

    return json.dumps({
        "meters": meters,
        "health": health,
    }, indent=2)


@mcp.tool(annotations={"readOnlyHint": False})
def deck_play_card(card_id: str, dry_run: bool = True) -> str:
    """Execute a card's steps.

    Runs the card's defined steps with checkpoint tracking.
    Use dry_run=True (default) to preview what would happen.

    Args:
        card_id: The card to play (e.g., CARD-ANA-001)
        dry_run: If True, only preview steps without executing (default: True)

    Returns:
        JSON with execution plan or results
    """
    from deck.deck_router import DeckRouter

    router = DeckRouter()
    card = router.cards.get(card_id)

    if not card:
        return json.dumps({"error": f"Card {card_id} not found"})

    if dry_run:
        steps = getattr(card, "steps", [])
        outcomes = getattr(card, "outcomes", {})
        rollback = getattr(card, "rollback", [])
        meter_effects = getattr(card, "meter_effects", {})

        return json.dumps({
            "mode": "dry_run",
            "card_id": card.id,
            "title": card.title,
            "steps": [s if isinstance(s, str) else str(s) for s in steps],
            "expected_outcomes": outcomes if isinstance(outcomes, dict) else str(outcomes),
            "meter_effects": meter_effects,
            "rollback": rollback if isinstance(rollback, list) else [str(rollback)],
        }, default=str, indent=2)

    # Live execution via play_card.py
    import subprocess
    result = subprocess.run(
        ["python3", str(TOOLS_DIR / "deck" / "play_card.py"), card_id],
        capture_output=True, text=True, timeout=120,
        cwd=str(PROJECT_ROOT),
    )

    return json.dumps({
        "mode": "executed",
        "card_id": card_id,
        "exit_code": result.returncode,
        "output": result.stdout[-2000:] if result.stdout else "",
        "errors": result.stderr[-500:] if result.stderr else "",
    }, indent=2)


# ─────────────────────────────────────────────
# RESOURCES
# ─────────────────────────────────────────────

@mcp.resource("deck://cards-catalog")
def cards_catalog() -> str:
    """Full catalog of all certified cards."""
    from deck.deck_router import DeckRouter
    router = DeckRouter()

    catalog = []
    for card_id, card in sorted(router.cards.items()):
        catalog.append(f"## {card.id}: {card.title}\n{card.description}\n")

    return "\n".join(catalog)


@mcp.resource("deck://meters-schema")
def meters_schema() -> str:
    """Meter definitions and ranges."""
    return json.dumps({
        "focus": {"range": "0-100", "meaning": "Task coherence and concentration"},
        "reliability": {"range": "0-100", "meaning": "Trust in output quality"},
        "discovery": {"range": "0-100", "meaning": "Learning and exploration progress"},
        "debt": {"range": "0-100", "meaning": "Accumulated shortcuts and technical debt"},
        "readiness": {"range": "0-100", "meaning": "System preparation and health"},
    }, indent=2)


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")
