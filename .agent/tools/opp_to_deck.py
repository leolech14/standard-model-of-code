#!/usr/bin/env python3
"""
opp_to_deck.py - Convert high-scoring opportunities to playable Decision Deck cards.

This is the HOOK that connects:
  Registry (enriched opportunities) → Decision Deck (playable cards)

The Decision Deck shows AI agents their available actions. This tool ensures
the deck is populated with real, relevant, high-value opportunities from
the task registry.

Usage:
    # Generate cards from top opportunities
    python opp_to_deck.py

    # Specify minimum confidence threshold (default: 70)
    python opp_to_deck.py --threshold 80

    # Limit number of cards (default: 10)
    python opp_to_deck.py --max-cards 5

    # Include active tasks too (default: opportunities only)
    python opp_to_deck.py --include-active

    # Dry run
    python opp_to_deck.py --dry-run

Card Naming:
    - CARD-OPP-XXX.yaml (auto-generated from opportunity)
    - CARD-REG-XXX.yaml (auto-generated from active task)
    - CARD-*.yaml (manually created cards remain untouched)
"""

import argparse
import yaml
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple

# Paths
SCRIPT_DIR = Path(__file__).parent
AGENT_DIR = SCRIPT_DIR.parent
REGISTRY_DIR = AGENT_DIR / "registry"
INBOX_DIR = REGISTRY_DIR / "inbox"
ACTIVE_DIR = REGISTRY_DIR / "active"
DECK_DIR = AGENT_DIR / "deck"

# Ensure deck directory exists
DECK_DIR.mkdir(parents=True, exist_ok=True)


def load_opportunity(path: Path) -> Optional[Dict]:
    """Load an opportunity/task YAML file."""
    try:
        with open(path, 'r') as f:
            content = f.read()
            # Handle YAML with comments/frontmatter
            if content.startswith('#'):
                # Find first non-comment line or actual YAML
                lines = content.split('\n')
                yaml_start = 0
                for i, line in enumerate(lines):
                    if line.strip() and not line.strip().startswith('#'):
                        yaml_start = i
                        break
                content = '\n'.join(lines[yaml_start:])
            return yaml.safe_load(content)
    except Exception as e:
        print(f"WARNING: Failed to load {path}: {e}")
        return None


def get_overall_confidence(opp: Dict) -> float:
    """Extract overall confidence from opportunity, normalized to 0-1."""
    conf = opp.get('confidence', {})
    if isinstance(conf, dict):
        raw = conf.get('overall', 0.5)
    else:
        raw = 0.5
    # Normalize: OPP files use 0-100 scale, cards use 0-1
    if isinstance(raw, (int, float)) and raw > 1:
        return raw / 100.0
    return raw


def category_to_phase(category: str) -> List[str]:
    """Map category to applicable phases."""
    phase_map = {
        'HEALTH_MODEL': ['DESIGNING', 'IMPLEMENTING'],
        'TECH_DEBT': ['IMPLEMENTING', 'MAINTAINING'],
        'CLI': ['IMPLEMENTING'],
        'TESTING': ['IMPLEMENTING', 'VALIDATING'],
        'DOCUMENTATION': ['DESIGNING', 'DOCUMENTING'],
        'PIPELINE': ['IMPLEMENTING'],
        'VISUALIZATION': ['IMPLEMENTING'],
        'GENERAL': ['ANY'],
    }
    return phase_map.get(category, ['ANY'])


def category_to_cost(category: str) -> Dict:
    """Estimate cost based on category."""
    cost_map = {
        'HEALTH_MODEL': {'tokens_estimate': '5K-20K', 'risk_level': 'medium'},
        'TECH_DEBT': {'tokens_estimate': '10K-50K', 'risk_level': 'high'},
        'CLI': {'tokens_estimate': '2K-5K', 'risk_level': 'low'},
        'TESTING': {'tokens_estimate': '5K-10K', 'risk_level': 'low'},
        'DOCUMENTATION': {'tokens_estimate': '2K-10K', 'risk_level': 'low'},
        'PIPELINE': {'tokens_estimate': '10K-30K', 'risk_level': 'medium'},
        'VISUALIZATION': {'tokens_estimate': '5K-15K', 'risk_level': 'medium'},
    }
    return cost_map.get(category, {'tokens_estimate': '5K', 'risk_level': 'medium'})


def opp_to_card(opp: Dict, source: str = 'inbox') -> Dict:
    """Convert an opportunity to a Decision Deck card."""
    opp_id = opp.get('id', 'UNKNOWN')
    title = opp.get('title', 'Untitled')
    description = opp.get('description', title)
    category = opp.get('category', 'GENERAL')
    confidence = get_overall_confidence(opp)
    tags = opp.get('tags', [])

    # Generate card ID
    if source == 'inbox':
        card_id = f"CARD-{opp_id}"  # e.g., CARD-OPP-067
    else:
        card_id = f"CARD-REG-{opp_id.split('-')[-1]}"  # e.g., CARD-REG-019

    card = {
        'id': card_id,
        'title': title[:60],  # Truncate for display
        'type': 'task',
        'source': f'{source}:{opp_id}',
        'phase_gate': category_to_phase(category),
        'description': description if isinstance(description, str) else str(description)[:200],
        'preconditions': [
            {
                'check': f'registry.{opp_id}.exists',
                'description': f'{opp_id} in registry'
            }
        ],
        'cost': category_to_cost(category),
        'outcomes': {
            'success': {
                'description': f'{opp_id} completed',
                'meters': {
                    'progress': 1,
                    'debt': -1 if category == 'TECH_DEBT' else 0
                }
            },
            'failure': {
                'description': f'{opp_id} blocked or deferred',
                'meters': {
                    'discovery': 1  # Learned something
                }
            }
        },
        'tags': tags[:5] + [category.lower()],
        'auto_generated': True,
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'confidence': confidence
    }

    return card


def _is_promotable(opp: Dict) -> bool:
    """Check if an opportunity is eligible for deck promotion.

    Filters out:
    - Unenriched imports (confidence.needs_review = true)
    - Already promoted/completed/archived OPPs
    """
    status = opp.get('status', '').upper()
    if status in ('PROMOTED', 'COMPLETE', 'COMPLETED', 'ARCHIVED'):
        return False

    conf = opp.get('confidence', {})
    if isinstance(conf, dict) and conf.get('needs_review', False):
        return False

    return True


def load_all_opportunities(include_active: bool = False) -> List[Tuple[Dict, str]]:
    """Load all opportunities and optionally active tasks."""
    opps = []

    # Load inbox (skip non-promotable)
    for yaml_file in INBOX_DIR.glob("OPP-*.yaml"):
        opp = load_opportunity(yaml_file)
        if opp and _is_promotable(opp):
            opps.append((opp, 'inbox'))

    # Load active tasks if requested
    if include_active:
        for yaml_file in ACTIVE_DIR.glob("TASK-*.yaml"):
            task = load_opportunity(yaml_file)
            if task and task.get('status') not in ['COMPLETE', 'ARCHIVED']:
                opps.append((task, 'active'))

    return opps


def _card_content_matches(card_file: Path, new_card: Dict) -> bool:
    """Check if existing card has the same meaningful content.

    Compares all fields except generated_at (timestamp) to avoid
    regenerating cards whose content hasn't changed.
    """
    if not card_file.exists():
        return False

    existing = load_opportunity(card_file)
    if not existing:
        return False

    # Compare meaningful fields (ignore timestamps)
    for key in ('id', 'title', 'type', 'source', 'description',
                'preconditions', 'cost', 'outcomes', 'tags', 'confidence'):
        if existing.get(key) != new_card.get(key):
            return False

    return True


def clean_stale_auto_cards(keep_ids: set):
    """Remove auto-generated cards not in the keep set."""
    removed = 0
    for card_file in DECK_DIR.glob("CARD-OPP-*.yaml"):
        card_id = card_file.stem  # e.g. CARD-OPP-059
        if card_id not in keep_ids:
            card_file.unlink()
            removed += 1
    for card_file in DECK_DIR.glob("CARD-REG-*.yaml"):
        card_id = card_file.stem
        if card_id not in keep_ids:
            card_file.unlink()
            removed += 1
    return removed


def main():
    parser = argparse.ArgumentParser(description="Convert opportunities to deck cards")
    parser.add_argument('--threshold', '-t', type=float, default=0.65,
                        help='Minimum confidence threshold (default: 0.65)')
    parser.add_argument('--max-cards', '-m', type=int, default=10,
                        help='Maximum cards to generate (default: 10)')
    parser.add_argument('--include-active', '-a', action='store_true',
                        help='Include active tasks, not just inbox')
    parser.add_argument('--dry-run', '-n', action='store_true',
                        help='Show what would be done without writing')
    args = parser.parse_args()

    print("=" * 60)
    print("OPPORTUNITY → DECK CARD GENERATOR")
    print("=" * 60)

    # Load opportunities
    opps = load_all_opportunities(args.include_active)
    print(f"\nLoaded: {len(opps)} items from registry")

    # Score and filter
    scored = []
    for opp, source in opps:
        conf = get_overall_confidence(opp)
        if conf >= args.threshold:
            scored.append((opp, source, conf))

    # Sort by confidence descending
    scored.sort(key=lambda x: x[2], reverse=True)
    top = scored[:args.max_cards]

    print(f"Above threshold ({args.threshold}): {len(scored)}")
    print(f"Taking top {args.max_cards}: {len(top)}")

    if not top:
        print("\nNo opportunities meet threshold. Lower --threshold or run enrichment.")
        return

    # Build set of card IDs we want to keep
    keep_ids = set()
    for opp, source, conf in top:
        card = opp_to_card(opp, source)
        keep_ids.add(card['id'])

    # Remove cards that are no longer in the top set
    if not args.dry_run:
        removed = clean_stale_auto_cards(keep_ids)
        if removed:
            print(f"\nRemoved {removed} stale auto-generated cards")

    # Generate cards (skip if content unchanged)
    print("\nGenerating cards:")
    written = 0
    skipped = 0
    for opp, source, conf in top:
        card = opp_to_card(opp, source)
        card_file = DECK_DIR / f"{card['id']}.yaml"

        if args.dry_run:
            print(f"  [DRY] {card['id']}: {card['title'][:40]}... ({conf*100:.0f}%)")
            written += 1
        elif _card_content_matches(card_file, card):
            skipped += 1
        else:
            with open(card_file, 'w') as f:
                f.write(f"# Auto-generated from {source}:{opp.get('id')}\n")
                f.write(f"# Confidence: {conf:.0%}\n")
                f.write(f"# Generated: {datetime.now().isoformat()}\n\n")
                yaml.dump(card, f, default_flow_style=False, sort_keys=False)
            print(f"  OK: {card['id']}: {card['title'][:40]}... ({conf*100:.0f}%)")
            written += 1

    action = 'Would generate' if args.dry_run else 'Generated'
    print(f"\n{action}: {written} cards, skipped {skipped} unchanged")
    print("=" * 60)


if __name__ == "__main__":
    main()
