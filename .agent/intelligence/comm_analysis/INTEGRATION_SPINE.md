# Integration Spine - The Core That Everything Adapts To
**Date:** 2026-01-27 06:00
**Principle:** Stop analyzing. Start integrating.
**Status:** DESIGN → BUILD → TEST → ADAPT

---

## THE SPINE (What Everything Connects To)

```
                    AGENT STARTS
                         ↓
                  ┌──────────────┐
                  │  CONCIERGE   │ ← THE SPINE
                  │   (Hub)      │
                  └──────────────┘
                         ↓
              ┌──────────┴──────────┐
              ↓                     ↓
        ┌──────────┐          ┌──────────┐
        │  PALACE  │          │  OLLAMA  │
        │ BUTLERS  │          │  (Fast)  │
        └──────────┘          └──────────┘
              ↓                     ↓
    ┌─────────┴─────────┐    ┌─────┴──────┐
    ↓         ↓         ↓    ↓            ↓
  [GIT]   [FABRIC]  [DECK]  [SEARCH]   [SUGGEST]
    ↓         ↓         ↓    ↓            ↓
 Status   Health    Cards  Chunks    Assistance
```

**The Concierge is the HUB. Everything else ADAPTS to connect to it.**

---

## INTEGRATION PROTOCOL

### Step 1: Define the Interface Contract
**What Concierge MUST provide to agents:**

```python
class AgentContext:
    """What every new agent inherits."""

    # System state (from butlers)
    git_status: dict          # branch, uncommitted count, clean
    system_health: dict       # fabric metrics, tier, warnings
    knowledge_state: dict     # chunks, freshness, git SHA
    automation_status: dict   # autopilot, systems, circuit breakers

    # Work queue (from task butlers)
    active_tasks: list        # Current work
    inbox: list               # Opportunities
    available_cards: list     # Certified moves

    # Assistance (from AI butlers)
    ollama_available: bool    # Can use fast local LLM
    search_available: bool    # Can search chunks
    fabric_warnings: list     # Current alerts

    def ask(self, query: str) -> str:
        """Ask Ollama anything, get answer in <100ms."""

    def search(self, query: str, limit: int = 5) -> list:
        """Search knowledge chunks, return relevant context."""

    def deal_cards(self) -> list:
        """Get available cards with fabric context."""

    def get_card(self, card_id: str) -> dict:
        """Load card with surgical context injection."""
```

**Every butler ADAPTS to provide data to this interface.**

---

### Step 2: Concierge Becomes the Spine

**Current concierge.py:** Standalone script

**New concierge.py:** Importable module + CLI

```python
#!/usr/bin/env python3
"""
Concierge - The Integration Spine

All butlers connect here. All agents start here.
Nothing is "perfect" - everything adapts to integrate.
"""

class Concierge:
    """The hub that connects all palace systems."""

    def __init__(self):
        # Load all butler interfaces (they adapt to be queryable)
        self.git = GitButler()
        self.fabric = FabricButler()
        self.refinery = RefineryButler()
        self.deck = DeckButler()
        self.ollama = OllamaButler() if ollama_available() else None
        self.autopilot = AutopilotButler()

    def greet(self) -> AgentContext:
        """Greet new agent, return complete context."""

        # Query all butlers in parallel (each adapts to be fast)
        context = AgentContext(
            git_status=self.git.status(),
            system_health=self.fabric.state(),
            knowledge_state=self.refinery.stats(),
            automation_status=self.autopilot.status(),
            active_tasks=self.deck.active_tasks(),
            inbox=self.deck.inbox(),
            available_cards=self.deck.deal(),
            ollama_available=self.ollama is not None,
            search_available=self.refinery.has_chunks(),
            fabric_warnings=self.fabric.warnings(),
        )

        return context

    def interactive_mode(self):
        """Run interactive concierge UI."""
        context = self.greet()
        self.display(context)

        while True:
            choice = input("\nChoice: ").strip()

            if choice == "D" or choice == "d":
                self.show_deck(context)
            elif choice == "R" or choice == "r":
                self.resume_task(context)
            elif choice == "?":
                self.help()
            elif choice.startswith("/"):
                # Ollama command mode
                self.ask_ollama(choice[1:])
            else:
                break
```

**Each butler provides a simple interface:**

```python
class GitButler:
    def status(self) -> dict:
        """Adapt git status to return dict."""

class FabricButler:
    def state(self) -> dict:
        """Adapt fabric.py to return current state."""
    def warnings(self) -> list:
        """Return active alerts."""

class RefineryButler:
    def stats(self) -> dict:
        """Adapt state synthesizer output."""
    def search(self, query: str) -> list:
        """Search chunks."""

class DeckButler:
    def deal(self) -> list:
        """Adapt deck_router to return cards."""
    def active_tasks(self) -> list:
        """Read from registry/active/."""
```

**Nobody rewrites their code. Each just adds a butler interface.**

---

### Step 3: Everything Adapts

**Existing tools DON'T change internally. They just add an interface method.**

**Example: fabric.py adaptation**

```python
# In fabric.py (add at end)

class FabricButler:
    """Butler interface for Communication Fabric."""

    @staticmethod
    def state() -> dict:
        """Return current state for concierge."""
        sv = compute_state_vector()
        return {
            "tier": sv.health_tier,
            "stability": sv.stability_margin,
            "F": sv.F,
            "MI": sv.MI,
            "warnings": [w["message"] for w in check_stability_alerts(sv)[:3]]
        }

    @staticmethod
    def warnings() -> list:
        """Return active warnings."""
        sv = compute_state_vector()
        alerts = check_stability_alerts(sv)
        return [a["message"] for a in alerts if a["severity"] != "INFO"]
```

**That's it. fabric.py internals unchanged. Just adds butler interface.**

---

### Step 4: The Integration Loop

```python
# concierge.py main loop

def main():
    concierge = Concierge()

    # Greet (instant - all butlers queried)
    context = concierge.greet()
    concierge.display(context)

    # Interactive loop
    while True:
        choice = input("> ").strip()

        if not choice:
            continue

        # Route via Ollama (if available and not explicit command)
        if concierge.ollama and not choice.startswith(("[", "/")):
            intent = concierge.ollama.classify_intent(choice)

            if intent == "search_knowledge":
                results = concierge.refinery.search(choice)
                concierge.display_results(results)

            elif intent == "check_health":
                health = concierge.fabric.state()
                concierge.display_health(health)

            elif intent == "show_cards":
                cards = concierge.deck.deal()
                concierge.display_cards(cards)

            elif intent == "execute_card":
                # Extract card ID from choice
                card_id = concierge.ollama.extract_card_id(choice)
                concierge.execute_card(card_id, context)

        # Explicit commands
        elif choice in ["D", "d", "deal"]:
            cards = concierge.deck.deal()
            concierge.display_cards(cards)

        elif choice in ["R", "r", "resume"]:
            concierge.resume_task(context)

        elif choice.startswith("/"):
            # Direct Ollama query
            answer = concierge.ollama.ask(choice[1:])
            print(answer)

        elif choice in ["Q", "q", "quit", "exit"]:
            break
```

---

## THE BUILD SEQUENCE

### 1. Create Butler Interfaces (1 hour)
**Modify these files to add butler methods:**

- `fabric.py` → Add FabricButler class
- `query_chunks.py` → Add RefineryButler class
- `deck_router.py` → Add DeckButler class
- `autopilot.py` → Add AutopilotButler class

**Pattern:** Each file adds a simple class at the end, existing code unchanged

---

### 2. Rewrite Concierge as Hub (2 hours)
**Modify:** `concierge.py`

**Changes:**
- Import all butler interfaces
- Query all in parallel (async if needed)
- Display unified state
- Handle interactive loop with Ollama routing

---

### 3. Test Integration (1 hour)
**Verify:**
- ./concierge loads all butlers
- Display shows complete state
- Ollama routing works
- Cards integrate seamlessly
- Search works from concierge

---

### 4. Make Default (15 minutes)
**Add to one of:**
- `~/.zshrc` - Auto-run on cd to PROJECT_elements
- `./start` script - Wrapper that runs concierge
- CLAUDE.md - First instruction: "Run ./concierge"

---

## THE ADAPTATION PRINCIPLE

**Nobody rewrites their system.**

Each system just adds a butler interface:
```python
class XyzButler:
    @staticmethod
    def for_concierge() -> dict:
        """Return essential state for concierge display."""
        return {...}
```

Then concierge imports and queries:
```python
from fabric import FabricButler
from query_chunks import RefineryButler
from deck_router import DeckButler

state = {
    "fabric": FabricButler.for_concierge(),
    "refinery": RefineryButler.for_concierge(),
    "deck": DeckButler.for_concierge(),
}
```

**Everything adapts. Nothing breaks.**

---

## TOTAL EFFORT

**Phase 1: Basic Integration**
- Butler interfaces: 1h
- Concierge rewrite: 2h
- Testing: 1h
- **Total: 4 hours**

**Result:** Agent opens terminal → Concierge shows complete state → Agent picks action → Palace adapts to provide context

**Phase 2: Advanced (Optional)**
- Real-time assist: 3h
- Pokedex mode: 2h
- **Total: +5 hours = 9 hours total**

**Result:** Full vision - AI has its own AI assistant, <100ms responses, surgical context

---

## THE SPINE IS SIMPLE

```
Concierge = Integration Hub
Butlers = Adapt to connect
Ollama = Fast routing
Refinery = Surgical context
Fabric = Health awareness
Deck = Certified moves
```

**All pieces exist. Just need connective tissue.**

**4 hours to basic integration. 9 hours to full vision.**

---

**READY TO BUILD THE SPINE?**
