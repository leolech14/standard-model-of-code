# Collider Insights Pipeline: 3-Step Architectural Map

## The Flow

```
┌──────────────────────────────────────────────────────────────────┐
│  OUT-OF-BAND (prior run, not part of MCP call)                   │
│                                                                  │
│  ./pe collider full . ──► collider_insights.json                 │
│  (Stage 11.95)              (grade, health_score, findings,      │
│                              navigation, meta)                   │
└──────────────────────┬───────────────────────────────────────────┘
                       │ file on disk
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│  INSIDE MCP TOOL: get_collider_insights()                        │
│                                                                  │
│  ┌─── Step 1: EXTRACTION ──────────────────────────────────┐     │
│  │  _find_insights_json(db_dir)                            │     │
│  │                                                         │     │
│  │  Resolution order:                                      │     │
│  │    1. Explicit db_dir/collider_insights.json            │     │
│  │    2. ./collider/collider_insights.json (cwd)           │     │
│  │    3. /tmp/**/collider_insights.json (latest by mtime)  │     │
│  │                                                         │     │
│  │  → Returns Path or None (→ error JSON)                  │     │
│  │  → json.load(path) → raw dict                           │     │
│  │  → Staleness check: if >7 days, inject _warning         │     │
│  └─────────────────────────────────────────────────────────┘     │
│                          │                                       │
│                          ▼ raw dict                              │
│  ┌─── Step 2: PROCESSING ──────────────────────────────────┐     │
│  │  _format_insights_markdown(data)                        │     │
│  │                                                         │     │
│  │  1. Extract scalars: grade, health_score, Q-Score       │     │
│  │  2. Build health components breakdown (sorted)          │     │
│  │  3. Sort findings by severity:                          │     │
│  │     critical(0) → high(1) → medium(2) → low(3) → info   │     │
│  │  4. Map severity → GitHub Alert syntax:                 │     │
│  │     critical → [!CAUTION]                               │     │
│  │     high     → [!WARNING]                               │     │
│  │     medium   → [!IMPORTANT]                             │     │
│  │     low      → [!TIP]                                   │     │
│  │     info     → [!NOTE]                                  │     │
│  │  5. Per finding: What / Evidence / Action / Why         │     │
│  │  6. Navigation: top 5 topological entry points          │     │
│  └─────────────────────────────────────────────────────────┘     │
│                          │                                       │
│                          ▼ markdown string                       │
│  ┌─── Step 3: DELIVERY ────────────────────────────────────┐     │
│  │  return "\n".join(lines)                                │     │
│  │                                                         │     │
│  │  LLM receives:                                          │     │
│  │    # Collider Intelligence Digest                       │     │
│  │    ## 1. System State & Numbers                         │     │
│  │    ## 2. Actionable Insights & The "Why"                │     │
│  │    ## 3. Navigation Guidance                            │     │
│  │    (+ staleness warning if applicable)                  │     │
│  └─────────────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────────┘
```

## Why This Architecture Is Superior

**The core insight: move the interpretation burden from consumer to producer.**

Without this pipeline, every LLM call that needs architectural awareness must:
1. Read raw JSON (thousands of tokens of nested dicts, arrays, numeric scores)
2. Figure out what matters (severity ranking, thresholds, what "topology_score: 6.2" means)
3. Decide what to do about it (map findings to actions)
4. Repeat this work every single time

With the pipeline inside the MCP tool:

- **Token efficiency** -- The LLM receives ~200 lines of pre-digested Markdown instead of ~2000 lines of raw JSON. Roughly 10x reduction.
- **Zero interpretation overhead** -- Severity is already sorted, findings already have "What / Evidence / Action / Why" labels. The LLM reads, it doesn't parse.
- **Consistent output** -- Every agent, every session, gets the same structured digest. No variance from one LLM's JSON interpretation to another's.
- **Staleness guard** -- The 7-day `_warning` injection is automatic. No agent needs to remember to check file age.
- **Graceful degradation** -- Missing file returns actionable error JSON with the exact command to fix it. No cryptic FileNotFoundError.

**The architectural principle:** An MCP tool should return *conclusions*, not *data*. The tool is the expert on its own domain -- it knows how to read Collider output better than any general-purpose LLM. Let it do that job once, correctly, and hand the LLM the answer.
