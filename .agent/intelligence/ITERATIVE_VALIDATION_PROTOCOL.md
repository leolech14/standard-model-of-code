# Iterative Validation Protocol - Analyze ↔ Perplexity Loop
**Method:** [(Analyze ↔ Perplexity) × n] until confidence ≥95%
**Tasks:** #4, #6, #7, #8 (GraphRAG completion)
**Goal:** Step-by-step instructions with validated confidence

---

## REMAINING TASKS (From Registry)

### Task #4: Run Community Detection
**Current Confidence:** 90% (Louvain algorithm ready)
**Target:** 95%+ (validate Leiden vs Louvain choice)
**Questions:**
- Is Leiden definitively better than Louvain for our 5K nodes?
- Parameters: resolution, seed, iterations?
- Integration: Store in Neo4j how?

### Task #6: Visualize Semantic Graph
**Current Confidence:** 80% (Gephi + D3.js mentioned)
**Target:** 95%+ (validate visualization stack)
**Questions:**
- Best tool for 5K nodes: Gephi, Cytoscape, or custom?
- Interactive web viz: D3.js, vis.js, or Cytoscape.js?
- Performance at 10K+ edges?

### Task #7: Integrate 1,068 Research Files
**Current Confidence:** 75% (large dataset, entity extraction)
**Target:** 95%+ (validate extraction + cost)
**Questions:**
- Batch API: Will 5.3M tokens work in one job?
- Entity quality: How to validate extracted concepts?
- Deduplication: Strategy for 1,068 diverse docs?

### Task #8: Validate GraphRAG Accuracy
**Current Confidence:** 80% (test protocol defined)
**Target:** 95%+ (validate methodology)
**Questions:**
- 50 queries: How to select representative sample?
- Metrics: Precision, recall, F1, or different?
- Baseline: Compare to what exactly?

---

## VALIDATION LOOP (Protocol)

### Iteration 1: Analyze.py Assessment

**Query:** "Detailed implementation plan for [TASK] with risks, parameters, code"
**Output:** Gemini's technical analysis
**Extract:** Confidence scores, implementation details, risks

### Iteration 2: Perplexity Validation

**Query:** "Validate [GEMINI_PLAN] against academic literature + production examples"
**Output:** External validation with 60+ sources
**Extract:** Confirm best practices, identify gaps

### Iteration 3: Synthesize

**Compare:** Gemini plan vs Perplexity validation
**Identify:** Discrepancies, missing details, risks
**Update:** Confidence scores based on agreement

### Iteration 4: Refine (if confidence <95%)

**Query Gemini:** "Address [GAPS] from Perplexity research"
**Query Perplexity:** "Validate refined [PLAN]"
**Repeat:** Until confidence converges to 95%+

### Iteration N: Generate Instructions

**When confidence ≥95%:**
- Write step-by-step implementation guide
- Include: Commands, code, parameters, validation
- Confidence: Document final 4D scores

---

## STARTING TASK #4 VALIDATION

### Round 1: Analyze.py

**Querying:** "Leiden vs Louvain for 5,284 node graph - which algorithm, parameters, Neo4j integration"

### Round 2: Perplexity

**Querying:** "Validate Leiden choice for knowledge graph community detection at 5K nodes"

### Round 3: Synthesize

**Compare results:** Agreement → increase confidence
**Identify gaps:** Disagreement → next iteration

### Round N: Final

**When 95%+ reached:** Generate complete implementation guide

---

## CONFIDENCE TRACKING

| Task | Round | Factual | Alignment | Current | Onwards | Overall | Action |
|------|-------|---------|-----------|---------|---------|---------|--------|
| #4 | 0 | 90 | 100 | 85 | 100 | 85 | Start validation |
| #4 | 1 | ? | ? | ? | ? | ? | Analyze query |
| #4 | 2 | ? | ? | ? | ? | ? | Perplexity validate |
| #4 | N | ≥95 | ≥95 | ≥95 | ≥95 | ≥95 | Generate instructions |

**Repeat for tasks #6, #7, #8**

---

## DETERMINISTIC CODOME GENERATOR CHECK

**Search results:** NOT FOUND

**Possible meanings:**
1. Schema for generating code graphs deterministically (Collider does this)
2. Automated codome partition generation (LOL does this)
3. Deterministic entity extraction (not implemented - we use LLM)

**Clarification needed:** What is "deterministic codome generator schema"?

---

## NEXT STEPS

**If proceeding with validation:**

1. Execute Round 1 (Analyze) for Task #4
2. Execute Round 2 (Perplexity) for Task #4
3. Synthesize and check confidence
4. Iterate or move to next task
5. Repeat for #6, #7, #8

**Total iterations:** Estimate 2-3 per task × 4 tasks = 8-12 queries

**Time:** 2-3 hours for complete validation

**START VALIDATION LOOP NOW?**

Or clarify: What is "deterministic codome generator schema"?

