# AI Assistance System - Synthesis & Proposal
**Date:** 2026-01-27 06:05
**Context:** Decision Deck was killed as "theater." What ACTUALLY serves AI agents?
**Source:** Gemini 3 Pro + Perplexity Sonar Pro research + archaeology

---

## THE RESEARCH SAYS

**Perplexity/Gemini Consensus (60+ academic sources):**

### For Local Service Integration:
✅ **Direct Python imports** with Protocol interfaces (NOT message queues)
✅ **Synchronous calls** (co-located services, <1ms latency)
✅ **Resilience via application patterns** (timeouts, retries, circuit breakers)
✅ **Event sourcing** for recursive processing safety
✅ **Semantic caching** to prevent re-analysis loops
✅ **Idempotency** for corruption prevention

### Message Queues Only When:
- Services distributed across networks (NOT our case)
- Need permanent audit trails (event sourcing handles this)
- Services scale independently (NOT our case - all local)

**Verdict:** Message queues are over-engineering for 20 local Python services.

---

## THE ARCHAEOLOGY SAYS

**What Previous Agents Built:**

### Systems That Work (Used Daily):
- ✅ Concierge (onboarding display)
- ✅ Ollama routing (pe intent classification)
- ✅ Autopilot (post-commit orchestration)
- ✅ Refinery (semantic chunking)
- ✅ Communication Fabric (system health)
- ✅ LOL, TDJ, Collider (knowledge butlers)

### System That Failed (Abandoned):
- ❌ Decision Deck (TASK-018: WONT_DO - "spec theater")
- Why: "Created 8 cards + deal_cards.py but never actually used them"
- Research: "Should be fully purged or marked as Museum"
- Status: Dead code causing confusion

---

## THE PATTERN EMERGES

**What agents ACTUALLY use:**
- `./pe status` - Quick system overview
- `./pe ask "question"` - Query via Gemini
- Git commands directly
- Test commands directly
- Manual file editing

**What agents DON'T use:**
- Elaborate card selection UI
- Certified move templates
- Phase gating
- Meter systems

**Why Deck failed:** Too much ceremony for simple tasks. Agents want answers, not processes.

---

## THE MINIMAL VIABLE AI ASSISTANCE

**What AI agents actually need:**

### 1. Fast Onboarding (<1 second)
```
Agent opens terminal
    ↓
Concierge queries butlers:
    - Git: branch, uncommitted count
    - Health: fabric state
    - Knowledge: chunk freshness
    - Tasks: what's active
    ↓
Displays complete state
    ↓
Agent starts work immediately
```

**Don't need:** Card selection ceremony

---

### 2. Surgical Context (When Asked)
```
Agent: "What's the purpose field formula?"
    ↓
Ollama routes to refinery
    ↓
Searches chunks for "purpose field"
    ↓
Returns top 3 relevant chunks (~2K tokens, not 100K)
    ↓
Agent gets exact answer in <200ms
```

**Don't need:** Elaborate context injection protocols

---

### 3. Real-Time Health Awareness
```
Agent: "Can I refactor this?"
    ↓
Queries fabric: stability_margin, R_auto, noise
    ↓
Returns: "Safe - R_auto=1.0, tests adequate, margin +0.70"
    ↓
Agent proceeds with confidence
```

**Don't need:** Risk assessment cards, phase gates

---

### 4. Automatic Maintenance
```
Agent commits code
    ↓
Post-commit hook → autopilot
    ↓
Refinery updates chunks (only changed files)
    ↓
Fabric records new state
    ↓
Next agent inherits fresh knowledge
```

**Don't need:** Manual refresh, stale data handling

---

## THE PROPOSAL (Based on Research + Reality)

### Architecture: Direct Import Butler Protocol

**Create:** Simple Python Protocol for all butlers

```python
# .agent/lib/butler_protocol.py
from typing import Protocol, Dict, Any

class Butler(Protocol):
    """Standard interface all butlers implement."""

    @staticmethod
    def status() -> Dict[str, Any]:
        """Return current state for concierge display.

        Returns:
            {
                "name": str,           # Butler name
                "healthy": bool,       # Is butler working?
                "summary": str,        # One-line summary
                "details": dict,       # Full state (optional)
                "last_update": str,    # ISO timestamp
            }
        """
        ...
```

**Each system adds one method (NO rewrites):**

```python
# In fabric.py
class FabricButler:
    @staticmethod
    def status() -> Dict[str, Any]:
        sv = compute_state_vector()
        return {
            "name": "Communication Fabric",
            "healthy": sv.stability_margin > 0,
            "summary": f"{sv.health_tier} tier, {sv.stability_margin:+.2f} margin",
            "details": {
                "F": sv.F, "MI": sv.MI, "N": sv.N,
                "warnings": [a["message"] for a in check_stability_alerts(sv)]
            },
            "last_update": sv.timestamp
        }
```

**Concierge imports and queries directly:**

```python
# In concierge.py
from fabric import FabricButler
from query_chunks import RefineryButler
# ... import all butlers

def gather_palace_state() -> Dict[str, Any]:
    """Query all butlers in <1 second."""

    state = {}

    # Query each butler (direct import, synchronous)
    # Wrapped with timeout + circuit breaker
    for butler_class in [FabricButler, RefineryButler, ...]:
        try:
            with timeout(500ms):
                state[butler_class.name] = butler_class.status()
        except Timeout:
            state[butler_class.name] = {"healthy": False, "summary": "Timeout"}
        except Exception as e:
            state[butler_class.name] = {"healthy": False, "summary": f"Error: {e}"}

    return state
```

**Benefits:**
- ✅ Fast (<1ms per butler, <20ms total)
- ✅ Simple (direct imports, no middleware)
- ✅ Resilient (timeouts + circuit breakers)
- ✅ Adaptable (each butler adds status() method, nothing else changes)

---

### Ollama Integration (Fast Queries)

```python
# In concierge.py
def ask_palace(query: str) -> str:
    """Ask Ollama to route query to right butler."""

    # Classify intent (local Ollama, ~100ms)
    intent = ollama_classify(query)

    if intent == "health":
        state = FabricButler.status()
        return f"System: {state['summary']}"

    elif intent == "search":
        results = RefineryButler.search(query, limit=3)
        return format_search_results(results)

    elif intent == "tasks":
        tasks = TaskButler.active_tasks()
        return format_tasks(tasks)

    # Fallback: Full Gemini query
    return analyze_via_gemini(query)
```

**Flow:**
```
Agent: "What's system health?"
→ Ollama classifies: "health" (~100ms)
→ Queries FabricButler.status() (~1ms)
→ Returns: "BRONZE tier, +0.70 margin, STABLE"
→ Total: ~101ms
```

---

### Recursive Processing Safety

**From Research:** Event sourcing + idempotency + convergence detection

```python
# .agent/intelligence/processing_log.jsonl (append-only)
{"event": "refinery_chunked", "git_sha": "abc123", "chunks": 2654, "ts": "..."}
{"event": "fabric_recorded", "git_sha": "abc123", "state": {...}, "ts": "..."}
{"event": "refinery_chunked", "git_sha": "abc123", "chunks": 2654, "ts": "..."}  # Duplicate!

# Idempotency check
def should_process(event_type: str, git_sha: str) -> bool:
    """Don't re-process same event for same SHA."""
    recent = load_recent_events(hours=1)

    # Check if identical event already processed
    for event in recent:
        if event["event"] == event_type and event["git_sha"] == git_sha:
            return False  # Skip - already processed

    return True  # Process - new or changed
```

**Safety guaranteed:** Same SHA = same code = don't re-process

---

## THE MINIMAL INTEGRATION (No Deck, No Theater)

### Component 1: Butler Protocol (1 hour)
Create `.agent/lib/butler_protocol.py` with Protocol definition.

Add `status()` method to:
- fabric.py → FabricButler
- query_chunks.py → RefineryButler
- autopilot.py → AutopilotButler
- (5-6 more critical butlers)

**Each takes ~10 minutes. Total: 1 hour.**

---

### Component 2: Concierge Hub (2 hours)
Rewrite concierge.py:
- Import all butler protocols
- Query all in parallel (or sequential with timeout)
- Display unified state
- Add Ollama query mode

**Result:** One command shows complete palace state

---

### Component 3: Recursive Safety (1 hour)
Add to refinery/fabric/etc:
- Event log (append-only JSONL)
- Idempotency check (git SHA + event type)
- Convergence detection (same content hash = stop)

**Result:** Safe recursive processing

---

### Component 4: Integration Testing (1 hour)
Test:
- All butlers respond to status()
- Concierge displays complete state in <1s
- Ollama routing works
- No infinite loops

---

## TOTAL: 5 Hours

**What you get:**
- Instant onboarding (complete state in <1s)
- Fast queries (Ollama <100ms)
- Surgical context (refinery chunks)
- Safe recursion (idempotency + convergence)
- NO elaborate ceremonies
- NO dead code
- NO theater

---

## THE ANSWER

**Forget the Decision Deck.** It was theater.

**What agents actually need:**
1. Fast palace state overview (concierge)
2. Quick answers (Ollama + refinery)
3. System health awareness (fabric)
4. Automatic maintenance (autopilot + butlers)

**Integration pattern (from research):**
- Direct Python imports with Butler Protocol
- Timeouts + circuit breakers for resilience
- Event sourcing for recursive safety
- No message queues (over-engineering)

**5 hours to build the integration spine.**

**Shall I proceed with this minimal, research-validated approach?**

No cards. No ceremonies. Just fast, reliable butler queries for AI agents.
