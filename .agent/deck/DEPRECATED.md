# DEPRECATED

This directory has been **consolidated** into the AI subsystem.

## New Location

```
context-management/tools/ai/deck/
```

## Access via ./pe

```bash
./pe deck list     # Show all cards
./pe deck deal     # Show available cards (preconditions met)
./pe deck route "analyze code"  # Route intent to card
./pe deck show CARD-ANA-001     # Show card details
```

## Why Moved

Per Perplexity validation (20260126_012105):
- Decision Deck is AI agent governance
- Belongs with AI tools, not Observer realm
- Enables ./pe unified CLI integration
- Maintains separation between intent routing (Layer 1) and certified moves (Layer 2)

## Do Not Delete

Keep these files as reference for card definitions.
The Python router at `context-management/tools/ai/deck/deck_router.py` loads from its new location.

---
Consolidated: 2026-01-26
