# ACI Intelligence Map: How Routing Actually Works

**Purpose:** Complete understanding of ACI decision-making for intelligent Cerebras integration
**Generated:** 2026-02-02
**Status:** OPERATIONAL KNOWLEDGE (not theory)

---

## 1. The Actual Decision Flow

```
USER QUERY
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ INTENT PARSER (intent_parser.py)                            │
│                                                             │
│ Input: "how does atom classification work"                  │
│                                                             │
│ 1. Extract keywords: ["atom", "classification", "work"]     │
│ 2. Match against INTENT_KEYWORDS dict                       │
│    - "how does" → ARCHITECTURE score += 1.0                 │
│    - "work" → ARCHITECTURE score += 0.4                     │
│ 3. Complexity from keyword count (≤3 = SIMPLE)              │
│ 4. Scope from external indicators (none = INTERNAL)         │
│                                                             │
│ Output: QueryProfile {                                      │
│   intent: ARCHITECTURE,                                     │
│   complexity: MODERATE,                                     │
│   scope: INTERNAL,                                          │
│   confidence: 0.47,                                         │
│   suggested_sets: ["pipeline", "theory"]                    │
│ }                                                           │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ TIER ORCHESTRATOR (tier_orchestrator.py)                    │
│                                                             │
│ Input: QueryProfile                                         │
│                                                             │
│ 1. Check FLASH_DEEP triggers (keywords like "comprehensive")│
│    → Not triggered                                          │
│                                                             │
│ 2. Lookup in ROUTING_MATRIX:                                │
│    key = (ARCHITECTURE, MODERATE, INTERNAL)                 │
│    → Tier.LONG_CONTEXT                                      │
│    → Reasoning: "Architecture query - need multi-file"      │
│                                                             │
│ 3. Merge sets from profile + semantic match                 │
│                                                             │
│ 4. Set fallback: LONG_CONTEXT → FLASH_DEEP                  │
│                                                             │
│ Output: RoutingDecision {                                   │
│   tier: LONG_CONTEXT,                                       │
│   primary_sets: ["pipeline", "theory"],                     │
│   fallback_tier: FLASH_DEEP,                                │
│   use_truths: false,                                        │
│   reasoning: "Architecture query - need multi-file"         │
│ }                                                           │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ ANALYZE.PY EXECUTION                                        │
│                                                             │
│ Switch on decision.tier:                                    │
│                                                             │
│ case INSTANT:                                               │
│   → Load repo_truths.yaml                                   │
│   → Match query to cached answers                           │
│   → Exit if found, else fallback to RAG                     │
│                                                             │
│ case PERPLEXITY:                                            │
│   → Clean query (remove internal refs)                      │
│   → Call perplexity_research()                              │
│   → Display + auto-save                                     │
│   → Exit                                                    │
│                                                             │
│ case FLASH_DEEP:                                            │
│   → Check cache (get_or_create_cache)                       │
│   → Load 10 sets, up to 2M tokens                           │
│   → Call Gemini 2.0 Flash                                   │
│   → Exit                                                    │
│                                                             │
│ case HYBRID:                                                │
│   → Phase 1: Perplexity (clean query)                       │
│   → Phase 2: Gemini + external evidence                     │
│   → Exit                                                    │
│                                                             │
│ case LONG_CONTEXT (default):                                │
│   → Load sets from analysis_sets.yaml                       │
│   → Apply semantic attention filtering                      │
│   → Call Gemini 3 Pro                                       │
│   → Display + auto-save                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. The Routing Matrix (Actual Rules)

| Intent | Complexity | Scope | → Tier | Reasoning |
|--------|------------|-------|--------|-----------|
| COUNT | SIMPLE | INTERNAL | INSTANT | Cached truths |
| LOCATE | SIMPLE | INTERNAL | RAG | File search |
| LOCATE | MODERATE | INTERNAL | RAG | Multi-file search |
| DEBUG | SIMPLE | INTERNAL | RAG | Search errors |
| DEBUG | MODERATE | INTERNAL | LONG_CONTEXT | Multi-file reasoning |
| DEBUG | COMPLEX | INTERNAL | LONG_CONTEXT | Full context |
| ARCHITECTURE | * | INTERNAL | LONG_CONTEXT | Always needs context |
| TASK | * | INTERNAL | LONG_CONTEXT | Agent context |
| VALIDATE | * | INTERNAL | LONG_CONTEXT | Reasoning |
| EXPLAIN | SIMPLE | INTERNAL | RAG | Quick lookup |
| EXPLAIN | MODERATE | INTERNAL | LONG_CONTEXT | Needs context |
| IMPLEMENT | * | INTERNAL | LONG_CONTEXT | Code context |
| RESEARCH | * | EXTERNAL | PERPLEXITY | Web search |
| RESEARCH | * | HYBRID | HYBRID | Both |

**FLASH_DEEP triggers** (bypass matrix):
- "comprehensive", "holistic", "exhaustive"
- "entire codebase", "all files", "everything"
- "deep dive", "thorough analysis"
- 3+ domain mentions

---

## 3. What's Missing: CEREBRAS

**Current gap:** No tier for FAST, CHEAP, BULK operations.

| Use Case | Current | With Cerebras |
|----------|---------|---------------|
| Validate 100 files | LONG_CONTEXT (slow, $$$) | CEREBRAS (fast, $) |
| Tag atoms in batch | Manual or skip | CEREBRAS parallel |
| Pre-filter for Gemini | None | CEREBRAS triage |
| Interactive exploration | 60s latency | <2s latency |
| Bulk enrichment | Serial, slow | CEREBRAS queue |

**Cerebras advantage:** 3000 tokens/sec = 100x faster than Gemini for simple tasks

---

## 4. Intelligent Routing Rules for CEREBRAS

```python
# NEW ROUTING RULES TO ADD:

# Fast validation queries
(QueryIntent.VALIDATE, QueryComplexity.SIMPLE, QueryScope.INTERNAL):
    (Tier.CEREBRAS, "Fast validation - Cerebras"),

# Bulk tagging/classification
(QueryIntent.COUNT, QueryComplexity.MODERATE, QueryScope.INTERNAL):
    (Tier.CEREBRAS, "Bulk count - Cerebras parallel"),

# Quick explanations (< 500 token context)
(QueryIntent.EXPLAIN, QueryComplexity.SIMPLE, QueryScope.INTERNAL):
    (Tier.CEREBRAS, "Quick explain - Cerebras"),

# Pre-filtering/triage
(QueryIntent.LOCATE, QueryComplexity.COMPLEX, QueryScope.INTERNAL):
    (Tier.CEREBRAS, "Triage before deep search"),
```

**Escalation path:**
```
INSTANT → CEREBRAS → RAG → LONG_CONTEXT → FLASH_DEEP
```

---

## 5. Cerebras-Specific Triggers

```python
CEREBRAS_TRIGGERS = {
    # Speed keywords
    "quick", "fast", "rapid", "brief",

    # Bulk keywords
    "batch", "all files", "bulk", "mass",
    "validate all", "check all", "tag all",

    # Simple tasks
    "classify", "categorize", "label",
    "yes or no", "true or false",

    # Triage keywords
    "triage", "filter", "pre-check",
    "which files", "narrow down",
}
```

---

## 6. Integration Points in analyze.py

```python
# Line ~2680: Add CEREBRAS handling BEFORE other tiers

# TIER CEREBRAS: Fast bulk operations
if decision.tier == Tier.CEREBRAS:
    print("[CEREBRAS] Fast inference tier selected.", file=sys.stderr)
    cerebras_start = time.time()

    try:
        from cerebras_rapid_intel import cerebras_query

        # Build minimal context (Cerebras excels with focused prompts)
        context = build_minimal_context(decision.primary_sets, max_tokens=8000)

        prompt = f"""Context:
{context}

Query: {args.prompt}

Respond concisely."""

        result = cerebras_query(prompt, max_tokens=2000)

        duration_ms = int((time.time() - cerebras_start) * 1000)
        print(f"[CEREBRAS] Completed in {duration_ms}ms")
        print(result)

        # Log feedback
        log_aci_query(...)

        sys.exit(0)

    except Exception as e:
        print(f"[CEREBRAS] Error: {e}, falling back to RAG")
        decision = analyze_and_route(args.prompt, force_tier="rag")
```

---

## 7. The Intelligence Layer

**What makes it INTELLIGENT:**

1. **Query Understanding** (intent_parser.py)
   - Not just keyword matching
   - Weighted scoring by indicator length
   - Complexity estimation from structure

2. **Context Selection** (semantic_finder.py)
   - Graph-based file relevance
   - Purpose field (π₁-π₄) hierarchy
   - Upstream/downstream traversal

3. **Adaptive Escalation**
   - Fallback on failure
   - Circuit breakers prevent cascade
   - Feedback learning

4. **CEREBRAS Intelligence:**
   - Use for FAST + SIMPLE = Cerebras
   - Use for BULK + ANY = Cerebras parallel
   - Use for TRIAGE before expensive calls
   - NEVER for complex reasoning (use Gemini)

---

*This is operational knowledge for building intelligent ACI.*
