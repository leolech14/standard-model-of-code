#!/usr/bin/env python3
"""
Decision Deck Router - Constrained Action Space for AI Agents

This module implements the "Game Master" layer from the Decision Deck architecture:
1. Loads certified moves (cards) from YAML definitions
2. Evaluates preconditions against current state
3. Routes natural language intents to appropriate cards
4. Provides structured action execution

The Deck constrains AI agents to certified moves rather than free-form improvisation.
Each card has: preconditions, steps, expected outcomes, rollback procedures.

See: docs/research/perplexity/20260123_150543_*.md for theoretical background.
"""

import re
import yaml
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

# Intent patterns for routing natural language to cards
INTENT_PATTERNS = {
    "CARD-ANA-001": [
        r"analy[sz]e.*(?:code|codebase|repo)",
        r"run.*collider",
        r"scan.*(?:code|project)",
    ],
    "CARD-RES-001": [
        r"research",
        r"investigate",
        r"deep.*dive",
        r"validate.*(?:claim|theory|hypothesis)",
    ],
    "CARD-RES-002": [
        r"perplexity",
        r"external.*research",
        r"grounding",
    ],
    "CARD-GIT-001": [
        r"commit",
        r"save.*changes",
        r"checkpoint",
    ],
    "CARD-DOC-001": [
        r"document",
        r"update.*(?:docs|readme|claude)",
        r"write.*(?:spec|guide)",
    ],
    "CARD-SES-001": [
        r"start.*session",
        r"init(?:ialize)?",
        r"boot",
    ],
    "CARD-AUD-001": [
        r"audit",
        r"verify",
        r"check.*(?:docs|drift|symmetry)",
        r"hsl",
        r"socratic",
    ],
    "CARD-WLD-000": [
        r"wildcard",
        r"custom",
        r"other",
        r"unknown",
    ],
}


@dataclass
class Card:
    """A certified move in the Decision Deck."""
    id: str
    title: str
    description: str
    phase_gate: List[str]
    preconditions: List[Dict[str, Any]] = field(default_factory=list)
    steps: List[Dict[str, Any]] = field(default_factory=list)
    outcomes: Dict[str, Any] = field(default_factory=dict)
    rollback: Dict[str, Any] = field(default_factory=dict)
    context_injection: List[Dict[str, Any]] = field(default_factory=list)
    cost: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

    @classmethod
    def from_yaml(cls, path: Path) -> "Card":
        """Load a card from a YAML file."""
        with open(path, 'r') as f:
            data = yaml.safe_load(f)

        return cls(
            id=data.get("id", path.stem),
            title=data.get("title", ""),
            description=data.get("description", ""),
            phase_gate=data.get("phase_gate", ["ANY"]),
            preconditions=data.get("preconditions", []),
            steps=data.get("steps", []),
            outcomes=data.get("outcomes", {}),
            rollback=data.get("rollback", {}),
            context_injection=data.get("context_injection", []),
            cost=data.get("cost", {}),
            tags=data.get("tags", []),
        )

    def check_preconditions(self, state: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Check if all preconditions are satisfied. Returns (ok, failures)."""
        failures = []
        for pre in self.preconditions:
            check = pre.get("check", "")
            # Simple file existence checks
            if "files_must_exist" in pre:
                for file_path in pre["files_must_exist"]:
                    if not Path(file_path).exists():
                        failures.append(f"Missing file: {file_path}")
            # State checks (simplified - extend as needed)
            if check and not state.get(check, True):
                failures.append(f"Precondition failed: {pre.get('description', check)}")

        return len(failures) == 0, failures

    def to_prompt(self) -> str:
        """Generate a prompt-friendly representation of this card."""
        lines = [
            f"## {self.title} ({self.id})",
            f"{self.description}",
            "",
            "### Steps:",
        ]
        for i, step in enumerate(self.steps, 1):
            action = step.get("action", "")
            desc = step.get("description", "")
            lines.append(f"{i}. **{action}** - {desc}")

        if self.rollback.get("possible"):
            lines.append("")
            lines.append("### Rollback:")
            for step in self.rollback.get("steps", []):
                lines.append(f"  - {step}")

        return "\n".join(lines)


class DeckRouter:
    """
    The Game Master layer - routes intents to certified moves.

    Implements the Decision Deck architecture:
    - Pattern matching (<10ms) for known intents
    - Card precondition evaluation
    - Available move generation based on current state
    """

    def __init__(self, deck_dir: Optional[Path] = None):
        if deck_dir is None:
            deck_dir = Path(__file__).parent
        self.deck_dir = Path(deck_dir)
        self.cards: Dict[str, Card] = {}
        self._load_cards()

    def _load_cards(self):
        """Load all card YAML files from the deck directory."""
        for yaml_file in self.deck_dir.glob("CARD-*.yaml"):
            try:
                card = Card.from_yaml(yaml_file)
                self.cards[card.id] = card
            except Exception as e:
                print(f"Warning: Failed to load {yaml_file}: {e}")

    def route_intent(self, intent: str) -> Optional[Card]:
        """
        Route natural language intent to a card via pattern matching.

        Args:
            intent: Natural language description of what the user wants

        Returns:
            Matched Card or None if no match
        """
        intent_lower = intent.lower()

        for card_id, patterns in INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, intent_lower):
                    return self.cards.get(card_id)

        return None

    def get_available_cards(self, state: Optional[Dict[str, Any]] = None) -> List[Card]:
        """
        Get all cards whose preconditions are satisfied.

        Args:
            state: Current system state for precondition evaluation

        Returns:
            List of available cards
        """
        if state is None:
            state = {}

        available = []
        for card in self.cards.values():
            ok, _ = card.check_preconditions(state)
            if ok:
                available.append(card)

        return available

    def get_card(self, card_id: str) -> Optional[Card]:
        """Get a card by ID."""
        return self.cards.get(card_id)

    def list_cards(self) -> str:
        """Return a formatted list of all cards."""
        lines = ["# Decision Deck - Available Cards", ""]

        # Group by tag category
        categories = {}
        for card in self.cards.values():
            primary_tag = card.tags[0] if card.tags else "other"
            if primary_tag not in categories:
                categories[primary_tag] = []
            categories[primary_tag].append(card)

        for category, cards in sorted(categories.items()):
            lines.append(f"## {category.title()}")
            for card in sorted(cards, key=lambda c: c.id):
                risk = card.cost.get("risk_level", "?")
                lines.append(f"- **{card.id}**: {card.title} (Risk: {risk})")
            lines.append("")

        return "\n".join(lines)

    def deal(self, state: Optional[Dict[str, Any]] = None) -> str:
        """
        'Deal' available cards - show what moves are currently valid.
        This is the Game Master's main function.
        """
        available = self.get_available_cards(state)

        lines = [
            "# Decision Deck - Current Hand",
            f"Available moves: {len(available)} / {len(self.cards)}",
            "",
        ]

        for card in sorted(available, key=lambda c: c.id):
            risk = card.cost.get("risk_level", "?")
            lines.append(f"- [{card.id}] {card.title} (Risk: {risk})")
            lines.append(f"  {card.description[:80]}...")

        return "\n".join(lines)


def main():
    """CLI interface for the deck router."""
    import sys

    router = DeckRouter()

    if len(sys.argv) < 2:
        print(router.list_cards())
        return

    command = sys.argv[1]

    if command == "list":
        print(router.list_cards())

    elif command == "deal":
        print(router.deal())

    elif command == "route":
        if len(sys.argv) < 3:
            print("Usage: deck_router.py route <intent>")
            sys.exit(1)
        intent = " ".join(sys.argv[2:])
        card = router.route_intent(intent)
        if card:
            print(f"Matched: {card.id} - {card.title}")
            print()
            print(card.to_prompt())
        else:
            print("No matching card found. Try CARD-WLD-000 (Wildcard).")

    elif command == "show":
        if len(sys.argv) < 3:
            print("Usage: deck_router.py show <card-id>")
            sys.exit(1)
        card_id = sys.argv[2].upper()
        card = router.get_card(card_id)
        if card:
            print(card.to_prompt())
        else:
            print(f"Card not found: {card_id}")

    else:
        # Treat as intent
        card = router.route_intent(command + " " + " ".join(sys.argv[2:]))
        if card:
            print(f"Matched: {card.id} - {card.title}")
            print()
            print(card.to_prompt())
        else:
            print("No matching card. Available commands: list, deal, route, show")


if __name__ == "__main__":
    main()
