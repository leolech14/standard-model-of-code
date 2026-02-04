# Adaptive Routing System Map

**Cartography Level:** SPIRAL 2 - CONTINENTS (Subsystem deep dive)
**Generated:** 2026-02-02
**Focus:** How the system interprets runs and adjusts input paths

---

## 1. Overview

PROJECT_elements has a **multi-layer adaptive routing system** that interprets queries/runs and dynamically adjusts the execution path. This is NOT a simple pipeline - it's an intelligent routing fabric.

```
USER INPUT (query/task)
        │
        ▼
┌───────────────────────────────────────────────────┐
│               ACI (Adaptive Context Intelligence)  │
│  wave/tools/ai/aci/                               │
│                                                   │
│  ┌─────────────┐    ┌─────────────┐             │
│  │ Intent      │───▶│ Tier        │             │
│  │ Parser      │    │ Orchestrator│             │
│  └─────────────┘    └──────┬──────┘             │
│                            │                     │
│                   ┌────────▼────────┐           │
│                   │ Routing Decision│           │
│                   │ - Tier          │           │
│                   │ - Sets          │           │
│                   │ - Fallback      │           │
│                   └────────┬────────┘           │
└────────────────────────────┼────────────────────┘
                             │
        ┌────────────────────┼───────────────────┐
        ▼                    ▼                   ▼
   TIER 0              TIER 1-2             TIER 3
   (INSTANT)           (RAG/LONG)           (PERPLEXITY)
   Cached truths       AI reasoning         External web
        │                    │                   │
        └────────────────────┼───────────────────┘
                             │
                             ▼
                    FEEDBACK LOOP
                    (logs success/failure)
                             │
                             ▼
                    AUTOPILOT (orchestrator)
                    - Circuit breakers
                    - Fallback levels
                    - Recovery
```

---

## 2. Key Components

### 2.1 Intent Parser (`wave/tools/ai/aci/intent_parser.py`)

**Role:** Classifies incoming queries into structured profiles

**Outputs:**
- `QueryIntent`: COUNT, LOCATE, DEBUG, ARCHITECTURE, TASK, VALIDATE, EXPLAIN, IMPLEMENT, RESEARCH
- `QueryComplexity`: SIMPLE, MODERATE, COMPLEX
- `QueryScope`: INTERNAL (codebase), EXTERNAL (web), HYBRID

**Example:**
```
Input: "how does atom classification work"
Output: {
  intent: EXPLAIN,
  complexity: MODERATE,
  scope: INTERNAL,
  suggested_sets: ["classifiers", "pipeline"]
}
```

### 2.2 Tier Orchestrator (`wave/tools/ai/aci/tier_orchestrator.py`)

**Role:** Routes queries to the appropriate execution tier

**Tiers:**
| Tier | Name | Use Case | Latency |
|------|------|----------|---------|
| 0 | INSTANT | Cached truths (counts, stats) | <100ms |
| 1 | RAG | File Search with citations | ~5s |
| 2 | LONG_CONTEXT | Gemini 3 Pro (1M tokens) | ~60s |
| 3 | PERPLEXITY | External web research | ~30s |
| 4 | FLASH_DEEP | Gemini 2.0 Flash (2M tokens) | ~120s |
| 5 | HYBRID | Multi-tier execution | Variable |

**Routing Matrix:** `(Intent, Complexity, Scope) → Tier`

Examples:
- `(COUNT, SIMPLE, INTERNAL)` → INSTANT
- `(ARCHITECTURE, COMPLEX, INTERNAL)` → LONG_CONTEXT
- `(RESEARCH, MODERATE, EXTERNAL)` → PERPLEXITY

**Escalation Path:**
```
INSTANT → RAG → LONG_CONTEXT → FLASH_DEEP → (no fallback)
```

### 2.3 Feedback Store (`wave/tools/ai/aci/feedback_store.py`)

**Role:** Logs every query execution for learning

**Captures:**
- Query profile (intent, complexity, scope)
- Routing decision (tier, sets)
- Execution metrics (tokens, duration, success)
- Retry count, fallback usage

**Outputs:**
- Rolling statistics (success rate, avg tokens, by-tier counts)
- Tier recommendations based on patterns
- Stored in `.agent/intelligence/aci_feedback.yaml`

**Adaptive Behavior:**
```python
def get_tier_recommendations(self) -> Dict[str, str]:
    # Analyze feedback to suggest routing improvements
    # E.g., "High retry rate on TIER_2, consider fallback"
```

### 2.4 Deck Router (`wave/tools/ai/deck/deck_router.py`)

**Role:** Routes natural language to certified action cards

**Pattern Matching:**
```python
INTENT_PATTERNS = {
    "CARD-ANA-001": [r"analy[sz]e.*(?:code|codebase|repo)"],
    "CARD-RES-001": [r"research", r"investigate", r"deep.*dive"],
    "CARD-GIT-001": [r"commit", r"save.*changes"],
    ...
}
```

**Cards:** YAML definitions with preconditions, steps, outcomes, rollback

### 2.5 Autopilot (`/.agent/tools/autopilot.py`)

**Role:** Master orchestrator for self-running repository

**Systems Coordinated:**
- TDJ (Technical Debt Journal)
- Trigger Engine
- Enrichment Pipeline
- Drift Guard

**Fallback Hierarchy:**
```
Level 0: Full automation (all systems green)
Level 1: Partial automation (some degraded)
Level 2: Manual mode (automation paused)
Level 3: Emergency stop (all halted)
```

**Circuit Breakers:**
- Track failures per system
- Auto-break after 3 consecutive failures
- 5-minute cooldown before retry
- Prevent cascade failures

---

## 3. Data Flow Example

**Query:** "how does edge extraction work in the pipeline"

```
1. INTENT PARSER
   - Intent: EXPLAIN
   - Complexity: MODERATE
   - Scope: INTERNAL
   - Suggested sets: ["pipeline"]

2. TIER ORCHESTRATOR
   - Matrix lookup: (EXPLAIN, MODERATE, INTERNAL)
   - Decision: TIER_2 (LONG_CONTEXT)
   - Sets: ["pipeline", "classifiers"]
   - Fallback: FLASH_DEEP
   - Reasoning: "Explanation needs context"

3. SEMANTIC FINDER (optional)
   - Detects: π₂=TRANSFORM (edge extraction is transformation)
   - Context flow: laminar
   - Adds upstream/downstream traversal

4. EXECUTION
   - Load analysis sets
   - Call Gemini 3 Pro with 1M context
   - Return response

5. FEEDBACK STORE
   - Log: success=true, tokens=450K, duration=45s
   - Update rolling stats
```

---

## 4. Path Adjustment Mechanisms

### 4.1 Dynamic Tier Escalation

If primary tier fails, automatically escalate:
```python
_get_fallback_tier(tier: Tier) -> Optional[Tier]:
    fallbacks = {
        Tier.INSTANT: Tier.RAG,
        Tier.RAG: Tier.LONG_CONTEXT,
        Tier.LONG_CONTEXT: Tier.FLASH_DEEP,
        Tier.PERPLEXITY: Tier.LONG_CONTEXT,
    }
```

### 4.2 Set Sanitization

Before execution, sets are sanitized:
```python
sanitize_sets(raw_sets, valid_set_names, max_sets=5):
    # 1. Apply alias mapping (invalid → valid)
    # 2. Validate against registry
    # 3. Deduplicate
    # 4. Cap at max_sets
```

### 4.3 Circuit Breaker Recovery

```python
def record_failure(self, system: str):
    failures = self.state["systems"][system]["failures"]
    failures += 1
    if failures >= MAX_FAILURES_BEFORE_CIRCUIT_BREAK:
        # Break circuit, set cooldown
        self.state["systems"][system]["broken_until"] = now + cooldown
```

### 4.4 Feedback-Driven Recommendations

```python
def get_tier_recommendations(self):
    # High retry rate? Suggest fallback
    # High tokens? Suggest smaller sets
    # Returns actionable suggestions
```

---

## 5. Configuration Files

| File | Purpose |
|------|---------|
| `wave/config/analysis_sets.yaml` | Define context sets |
| `.agent/state/autopilot_state.yaml` | Autopilot current state |
| `.agent/state/circuit_breakers.yaml` | Circuit breaker status |
| `.agent/intelligence/aci_feedback.yaml` | Feedback history |
| `.agent/deck/CARD-*.yaml` | Action card definitions |

---

## 6. Key Abstractions

| Abstraction | Location | Purpose |
|-------------|----------|---------|
| `QueryProfile` | aci/intent_parser.py | Structured query classification |
| `RoutingDecision` | aci/tier_orchestrator.py | Complete routing plan |
| `FeedbackEntry` | aci/feedback_store.py | Single execution record |
| `Card` | deck/deck_router.py | Certified action template |
| `CircuitBreaker` | autopilot.py | Failure protection |
| `AutopilotLevel` | autopilot.py | System health levels |

---

## 7. Gaps / Unknown

- **Semantic Finder details:** How does graph-based context selection work internally?
- **Trigger Engine:** How do triggers fire and interact with autopilot?
- **Multi-tier execution:** How does HYBRID tier orchestrate parallel calls?
- **Token budget enforcement:** What happens when context exceeds limits?

---

*Part of the Cerebras Cartography Protocol. See `CEREBRAS_CARTOGRAPHY_PROTOCOL.md` for methodology.*
