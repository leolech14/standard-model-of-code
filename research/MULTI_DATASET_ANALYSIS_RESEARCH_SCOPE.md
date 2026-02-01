# Multi-Dataset Analysis Research Scope

> Systematic evaluation of analyze.py across different datasets to understand context-performance relationships.

**Created:** 2026-01-30
**Status:** READY FOR EXECUTION

---

## Research Objective

Understand how different context configurations (datasets) affect AI reasoning quality, response time, and token efficiency when analyzing the PROJECT_elements codebase.

---

## Hypothesis Matrix

| ID | Hypothesis | Measurement |
|----|------------|-------------|
| H1 | Smaller, focused sets produce higher-quality answers for specific queries | Quality score (1-5) |
| H2 | `positional_strategy: sandwich` improves recall of critical information | Citation accuracy |
| H3 | Composed sets (`includes:`) vs monolithic sets have different cost/quality tradeoffs | Tokens/quality ratio |
| H4 | Temporal filters (`recent_7d`, `recent_30d`) outperform static sets for "current state" queries | Freshness score |
| H5 | ACI auto-routing selects optimal sets 80%+ of the time | Routing accuracy |

---

## Dataset Categories

### Category A: Size Tiers

| Set | Tokens | Use Case |
|-----|--------|----------|
| `deck_state` | 5k | Micro (surgical) |
| `agent_kernel` | 30k | Small (focused) |
| `pipeline` | 120k | Medium (substantial) |
| `architecture_review` | 200k | Large (comprehensive) |

### Category B: Domain Focus

| Set | Domain | Files |
|-----|--------|-------|
| `schema` | Data definitions | YAML/JSON schemas |
| `classifiers` | Logic | Classification algorithms |
| `theory` | Documentation | Specs and guides |
| `viz_core` | Frontend | JS/HTML/CSS |

### Category C: Temporal Filters

| Set | Window | Purpose |
|-----|--------|---------|
| `recent_7d` | 7 days | Hot zone (active development) |
| `recent_30d` | 30 days | Active surface |
| `brain_active` | 90 days + filters | Clean context |

### Category D: Composed vs Atomic

| Composed Set | Includes | Alternative |
|--------------|----------|-------------|
| `architecture_review` | pipeline, classifiers, constraints | Use each separately |
| `research_full` | research_core, research_tools, research_atoms | Use each separately |
| `agent_full` | agent_kernel, agent_tasks, agent_intelligence, agent_specs | Use each separately |

---

## Research Queries (Standardized)

### Q1: Architecture (Complex Reasoning)
```
"Explain how the Collider pipeline processes a repository from input to Codome graph output. Include the key stages and data transformations."
```

### Q2: Implementation (Code Understanding)
```
"How does the atom classification system work? What heuristics are used to identify atom types?"
```

### Q3: Debugging (Error Analysis)
```
"Why might edge extraction fail for TypeScript files? What are the failure modes?"
```

### Q4: Current State (Temporal)
```
"What has changed in the last week? Summarize recent modifications."
```

### Q5: Task Query (Agent Context)
```
"What tasks are currently ready to execute? List by priority."
```

### Q6: Needle (Specific Lookup)
```
"What is the exact definition of the 'Repository' atom type?"
```

---

## Execution Protocol

### Phase 1: Baseline (Single Set per Query)

```bash
#!/bin/bash
# research_phase1.sh - Baseline measurements

QUERIES=(
  "Q1:Explain how the Collider pipeline processes a repository"
  "Q2:How does atom classification work"
  "Q3:Why might edge extraction fail for TypeScript"
  "Q4:What changed in the last week"
  "Q5:What tasks are ready to execute"
  "Q6:What is the definition of Repository atom"
)

SETS_BY_SIZE=(
  "deck_state"
  "agent_kernel"
  "schema"
  "pipeline"
  "architecture_review"
)

OUTPUT_DIR="context-management/docs/research/results/phase1_$(date +%Y%m%d)"
mkdir -p "$OUTPUT_DIR"

for query in "${QUERIES[@]}"; do
  qid="${query%%:*}"
  qtext="${query#*:}"

  for set in "${SETS_BY_SIZE[@]}"; do
    echo "=== $qid x $set ==="

    # Run with JSON output
    python context-management/tools/ai/analyze.py \
      --set "$set" \
      --output-json \
      "$qtext" 2>&1 | tee "$OUTPUT_DIR/${qid}_${set}.json"

    # Rate limit protection
    sleep 10
  done
done
```

### Phase 2: ACI Auto-Routing Comparison

```bash
#!/bin/bash
# research_phase2.sh - ACI vs Manual routing

QUERIES=(
  "How does the pipeline work"
  "What tasks are pending"
  "Latest changes to classifiers"
  "Definition of Entity atom"
)

OUTPUT_DIR="context-management/docs/research/results/phase2_$(date +%Y%m%d)"
mkdir -p "$OUTPUT_DIR"

for i in "${!QUERIES[@]}"; do
  query="${QUERIES[$i]}"

  # ACI auto-route
  echo "=== ACI: $query ==="
  python context-management/tools/ai/analyze.py \
    --aci --aci-debug \
    --output-json \
    "$query" 2>&1 | tee "$OUTPUT_DIR/q${i}_aci.json"

  sleep 10

  # Manual best-guess route
  echo "=== Manual: $query ==="
  python context-management/tools/ai/analyze.py \
    --set pipeline \
    --output-json \
    "$query" 2>&1 | tee "$OUTPUT_DIR/q${i}_manual.json"

  sleep 10
done
```

### Phase 3: Tier Comparison

```bash
#!/bin/bash
# research_phase3.sh - Compare tiers on same query

QUERY="How does the Collider classify atoms?"

OUTPUT_DIR="context-management/docs/research/results/phase3_$(date +%Y%m%d)"
mkdir -p "$OUTPUT_DIR"

# Tier 0: Instant (cached truths)
python context-management/tools/ai/analyze.py \
  --aci --tier instant \
  "$QUERY" 2>&1 | tee "$OUTPUT_DIR/tier0_instant.txt"

sleep 5

# Tier 1: RAG (file search)
python context-management/tools/ai/analyze.py \
  --search "$QUERY" --store-name collider-pipeline \
  2>&1 | tee "$OUTPUT_DIR/tier1_rag.txt"

sleep 5

# Tier 2: Long Context
python context-management/tools/ai/analyze.py \
  --aci --tier long_context --set classifiers \
  "$QUERY" 2>&1 | tee "$OUTPUT_DIR/tier2_long.txt"

sleep 10

# Tier 3: Perplexity (external)
python context-management/tools/ai/analyze.py \
  --aci --tier perplexity \
  "Best practices for code classification systems 2026" \
  2>&1 | tee "$OUTPUT_DIR/tier3_perplexity.txt"
```

---

## Metrics Collection

### Per-Query Metrics

| Metric | Source | Formula |
|--------|--------|---------|
| `latency_ms` | AnalyzeResult.timing.total_ms | Direct |
| `input_tokens` | AnalyzeResult.cost.input_tokens | Direct |
| `output_tokens` | AnalyzeResult.cost.output_tokens | Direct |
| `files_included` | AnalyzeResult.context.files_included | len() |
| `bundle_hash` | AnalyzeResult.context.bundle_hash | For reproducibility |

### Quality Metrics (Manual Scoring)

| Metric | Scale | Criteria |
|--------|-------|----------|
| `relevance` | 1-5 | Does it answer the question? |
| `accuracy` | 1-5 | Are the facts correct? |
| `completeness` | 1-5 | Is anything missing? |
| `citations` | count | How many file references? |
| `hallucinations` | count | False claims |

### Aggregate Metrics

```python
# efficiency.py - Calculate efficiency scores

def token_efficiency(quality_score, input_tokens):
    """Quality per 1000 tokens"""
    return (quality_score / (input_tokens / 1000))

def cost_efficiency(quality_score, estimated_usd):
    """Quality per dollar"""
    return quality_score / estimated_usd if estimated_usd > 0 else float('inf')

def routing_accuracy(aci_quality, manual_quality):
    """Did ACI match or beat manual selection?"""
    return aci_quality >= manual_quality
```

---

## Results Schema

```yaml
# results/phase1_20260130/summary.yaml
experiment:
  id: "phase1_20260130"
  queries: 6
  sets: 5
  total_runs: 30

results:
  - query_id: "Q1"
    set: "pipeline"
    latency_ms: 45230
    input_tokens: 98543
    output_tokens: 1234
    quality:
      relevance: 5
      accuracy: 4
      completeness: 4
    citations: 12
    hallucinations: 0

  - query_id: "Q1"
    set: "deck_state"
    latency_ms: 3210
    input_tokens: 4521
    output_tokens: 456
    quality:
      relevance: 2
      accuracy: 3
      completeness: 1
    citations: 0
    hallucinations: 1

aggregates:
  best_set_per_query:
    Q1: "pipeline"
    Q2: "classifiers"
    Q3: "pipeline"
    Q4: "recent_7d"
    Q5: "agent_tasks"
    Q6: "schema"

  avg_token_efficiency:
    pipeline: 0.042
    schema: 0.089
    deck_state: 0.034
```

---

## Recommended Execution Schedule

```
Day 1: Phase 1 (Baseline)
  - Run all 30 combinations (6 queries x 5 sets)
  - Estimated time: ~2 hours (with rate limit protection)
  - Requires: Active Gemini quota

Day 2: Phase 2 (ACI Comparison)
  - Run 8 comparisons (4 queries x 2 modes)
  - Estimated time: ~30 minutes
  - Manual quality scoring

Day 3: Phase 3 (Tier Comparison)
  - Run 4 tier variants on 1 query
  - Estimated time: ~15 minutes
  - Deep analysis of tier tradeoffs

Day 4: Analysis
  - Aggregate results
  - Generate efficiency charts
  - Write conclusions
```

---

## Rate Limit Mitigation

```bash
# Check quota before running
python context-management/tools/ai/gemini_status.py --diagnose

# If rate limited, use these alternatives:

# 1. Switch to flash model (4x higher limit)
python analyze.py --model gemini-2.5-flash --set pipeline "query"

# 2. Use smaller sets
python analyze.py --set schema "query"  # 60k vs 200k tokens

# 3. Use RAG tier (minimal tokens)
python analyze.py --search "query" --store-name my-store

# 4. Use Perplexity for external queries
python analyze.py --aci --tier perplexity "query"

# 5. Batch with delays
for set in schema classifiers pipeline; do
  python analyze.py --set $set "query"
  sleep 60  # 1 minute between calls
done
```

---

## Expected Outputs

### Deliverables

1. **Raw Results**: `context-management/docs/research/results/phase{1,2,3}_YYYYMMDD/`
2. **Summary YAML**: `results/summary.yaml`
3. **Efficiency Chart**: `results/token_efficiency.png`
4. **Recommendations**: `DATASET_SELECTION_GUIDE.md`

### Key Questions Answered

1. Which set size is optimal for each query type?
2. Does ACI routing match human expert selection?
3. What is the cost/quality tradeoff curve?
4. Are temporal filters superior for "current state" queries?
5. When should you use composed vs atomic sets?

---

## Quick Start

```bash
# 1. Ensure venv is set up
source .tools_venv/bin/activate

# 2. Check API status
python context-management/tools/ai/gemini_status.py --diagnose

# 3. Run Phase 1 (if quota available)
chmod +x context-management/docs/research/research_phase1.sh
./context-management/docs/research/research_phase1.sh

# 4. If rate limited, run single test
python context-management/tools/ai/analyze.py \
  --set schema \
  "What is the Repository atom definition?"
```

---

## Related Documents

- `context-management/docs/ACI_DATASET_MANAGEMENT.md` - ACI architecture
- `context-management/config/analysis_sets.yaml` - Set definitions
- `.agent/intelligence/aci_feedback.yaml` - Historical query data
