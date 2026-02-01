# Research Workflow Execution Engine - Complete Technical Specification

**Date:** 2026-01-28
**Status:** SPECIFICATION (Pre-Implementation)
**Purpose:** Define complete architecture for making research workflows actually execute
**Approach:** Context/Specification first, implementation second (most robust)

---

## Executive Summary

**Problem:** Research workflows (validation_trio, perplexity_optimized, etc.) are defined in YAML but don't actually execute. The orchestrator returns `[PENDING EXECUTION]` stubs instead of making real API calls.

**Solution:** Implement execution layer that routes runs to appropriate backends (Gemini, Perplexity) based on run configuration, preserves workflow intelligence (structured queries, multi-stage validation), and synthesizes results per strategy.

**Scope:** Fix `research_orchestrator.py` to call actual APIs, not stubs.

---

## Current Architecture (AS-IS)

### Component Map

```
┌─────────────────────────────────────────────────────────────┐
│ USER                                                          │
│ Command: analyze.py --research validation_trio "query"       │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│ ANALYZE.PY (Entry Point)                                     │
│ - Parses CLI arguments                                        │
│ - Routes to research_orchestrator.execute()                   │
│ - Formats/displays results                                    │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│ RESEARCH_ORCHESTRATOR.PY (Workflow Engine)                   │
│                                                               │
│ Components:                                                   │
│ 1. Schema Loader (loads YAML → ResearchSchema objects)       │
│ 2. Schema Validator (checks structure)                       │
│ 3. Execution Engine (_execute_runs) ← INCOMPLETE!            │
│ 4. Synthesis Engine (_synthesize)                            │
│                                                               │
│ Current _execute_single_run():                               │
│   return RunResult(answer="[PENDING EXECUTION]", ...)        │
│   ❌ STUB - no actual API calls!                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                    [SHOULD CALL]
                         │
                         ▼
           ┌─────────────┴──────────────┐
           │                            │
      ┌────▼────────┐          ┌───────▼────────┐
      │ GEMINI API  │          │ PERPLEXITY API │
      │ (Internal)  │          │ (External)     │
      │             │          │                │
      │ Currently:  │          │ Currently:     │
      │ ❌ Not      │          │ ❌ Not         │
      │   called!   │          │   called!      │
      └─────────────┘          └────────────────┘
```

---

## Target Architecture (TO-BE)

### Execution Flow

```
USER
  ↓ CLI command
ANALYZE.PY
  ↓ parse args, route
RESEARCH_ORCHESTRATOR
  ├─ Load schema (validation_trio, perplexity_optimized, etc.)
  ├─ Validate schema structure
  ├─ For each run in schema.runs:
  │   ├─ Evaluate condition (should this run execute?)
  │   ├─ Route based on run.type:
  │   │   ├─ INTERNAL → Call Gemini API
  │   │   └─ EXTERNAL → Call Perplexity API
  │   └─ Capture result
  ├─ Synthesize results per strategy:
  │   ├─ consensus → majority voting
  │   ├─ triangulation → cross-reference
  │   ├─ dialectic → thesis/antithesis/synthesis
  │   └─ [other strategies]
  └─ Return CompositeResult
```

---

## Data Contracts

### Input: RunConfig (Single Run Definition)

```python
@dataclass
class RunConfig:
    name: str                    # "reasoning", "fast", "external"
    description: str             # Human-readable purpose
    type: RunType               # INTERNAL | EXTERNAL
    model: str                  # "gemini-3-pro-preview" | "sonar-pro"
    tier: str                   # "long_context" | "perplexity"
    sets: List[str]             # ["theory", "pipeline"] (INTERNAL only)
    token_budget: int           # 150000 (INTERNAL only)
    temperature: float          # 0.0-1.0
    system_prompt: Optional[str] # Additional instructions
    condition: Optional[Dict]   # When to execute
    fallback: Optional[str]     # What to do if condition fails
```

### Output: RunResult (Single Run Response)

```python
@dataclass
class RunResult:
    name: str                   # Run identifier
    success: bool               # Did it complete?
    answer: str                 # The response text
    model_used: str             # Actual model
    tier_used: str              # Actual tier
    run_type: str               # "internal" | "external"
    tokens_in: int              # Input tokens consumed
    tokens_out: int             # Output tokens generated
    latency_ms: int             # Execution time
    citations: List[str]        # Sources cited (external only)
    skipped: bool = False       # Was this run skipped?
    skipped_reason: str = ""    # Why skipped
    error: Optional[str] = None # Error message if failed
    metadata: Dict = field(default_factory=dict)
```

### Output: CompositeResult (Synthesized Multi-Run)

```python
@dataclass
class CompositeResult:
    schema_name: str            # "validation_trio"
    query: str                  # Original query
    consensus_answer: str       # Synthesized result
    agreement_score: float      # 0.0-1.0
    individual_runs: List[RunResult]
    disagreements: List[str]    # Where runs conflicted
    confidence: float           # Overall confidence
    synthesis_strategy: str     # "consensus" | "triangulation" | etc.
    decision_trace: Dict        # Metadata about execution
```

---

## API Integration Points

### 1. Gemini API (INTERNAL Runs)

**Location:** Already implemented in `analyze.py`

**Function Signature:**
```python
def execute_gemini_query(
    query: str,
    model: str,
    sets: List[str],
    token_budget: int,
    temperature: float,
    system_prompt: Optional[str] = None
) -> Dict:
    """
    Execute query using Gemini with repo context.

    Returns:
        {
            "answer": str,
            "tokens_in": int,
            "tokens_out": int,
            "latency_ms": int,
            "model": str
        }
    """
```

**Implementation Strategy:**
- Reuse existing `analyze.py` logic (don't duplicate)
- Extract into reusable function
- Call from orchestrator

**Technical Details:**
- API: Google Generative AI SDK
- Model: gemini-3-pro-preview (default) or gemini-2.5-flash
- Context: Load from `analysis_sets.yaml` based on `sets` parameter
- Token budget: Enforced via content slicing
- Temperature: Pass to model

---

### 2. Perplexity API (EXTERNAL Runs)

**Location:** `perplexity_research.py` already exists

**Function Signature:**
```python
from perplexity_research import research as perplexity_research

def execute_perplexity_query(
    query: str,
    model: str = "sonar-pro",
    temperature: float = 0.2,
    timeout: int = 300
) -> Dict:
    """
    Execute query using Perplexity Sonar API.

    Returns:
        {
            "content": str,         # Response text
            "citations": List[str], # Source URLs
            "usage": {
                "prompt_tokens": int,
                "completion_tokens": int
            }
        }
    """
```

**Implementation Strategy:**
- Call existing `perplexity_research.research()` function
- Map result to RunResult structure
- Auto-save handled by perplexity_research module

**Technical Details:**
- API: https://api.perplexity.ai/chat/completions
- Model: sonar-pro (default) or sonar-reasoning
- Auth: PERPLEXITY_API_KEY via Doppler or env
- Timeout: Configurable (default 300s)
- Auto-save: Automatic to `docs/research/perplexity/`

---

## Implementation Plan

### Phase 1: Extract Reusable Functions (1 hour)

**1.1 Extract Gemini Execution**
```python
# NEW FILE: wave/tools/ai/aci/executors/gemini_executor.py

from google import genai
from typing import Dict, List, Optional

def execute_gemini_internal(
    query: str,
    model: str,
    sets: List[str],
    token_budget: int,
    temperature: float,
    system_prompt: Optional[str] = None
) -> Dict:
    """
    Execute internal query using Gemini with repo context.

    Reuses analyze.py logic but as callable function.
    """
    # Import existing functions from analyze.py
    from ..analyze import (
        connect_to_gemini,
        load_context_for_sets,
        build_prompt,
        retry_with_backoff
    )

    # Connect
    client = connect_to_gemini()

    # Load context
    context_files = load_context_for_sets(sets, token_budget)

    # Build prompt
    full_prompt = build_prompt(
        query=query,
        context_files=context_files,
        system_prompt=system_prompt
    )

    # Execute
    import time
    start = time.time()

    response = retry_with_backoff(
        lambda: client.models.generate_content(
            model=model,
            contents=[{"text": full_prompt}],
            config={"temperature": temperature}
        )
    )

    latency_ms = int((time.time() - start) * 1000)

    # Extract
    return {
        "answer": response.text,
        "tokens_in": response.usage_metadata.prompt_token_count,
        "tokens_out": response.usage_metadata.candidates_token_count,
        "latency_ms": latency_ms,
        "model": model
    }
```

**1.2 Wrap Perplexity Execution**
```python
# NEW FILE: wave/tools/ai/aci/executors/perplexity_executor.py

from typing import Dict

def execute_perplexity_external(
    query: str,
    model: str = "sonar-pro",
    temperature: float = 0.2,
    timeout: int = 300
) -> Dict:
    """
    Execute external query using Perplexity.

    Thin wrapper over perplexity_research.py
    """
    import sys
    import time
    from pathlib import Path

    # Import existing perplexity module
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from perplexity_research import research

    start = time.time()
    result = research(query, model=model, timeout=timeout)
    latency_ms = int((time.time() - start) * 1000)

    # Map to standard format
    return {
        "answer": result.get("content", ""),
        "citations": result.get("citations", []),
        "tokens_in": result.get("usage", {}).get("prompt_tokens", 0),
        "tokens_out": result.get("usage", {}).get("completion_tokens", 0),
        "latency_ms": latency_ms,
        "model": model
    }
```

---

### Phase 2: Implement Router (30 min)

**2.1 Update _execute_single_run()**
```python
# IN: research_orchestrator.py

def _execute_single_run(self, run: RunConfig, query: str) -> RunResult:
    """Execute a single research run - ACTUALLY EXECUTE."""
    import time
    start_time = time.time()

    try:
        # Build full query
        full_query = query
        if run.system_prompt:
            full_query = f"{run.system_prompt.strip()}\n\nQUERY: {query}"

        # Route based on run type
        if run.type == RunType.INTERNAL:
            result = self._execute_internal(run, full_query)
        elif run.type == RunType.EXTERNAL:
            result = self._execute_external(run, full_query)
        else:
            raise ValueError(f"Unknown run type: {run.type}")

        # Convert to RunResult
        return RunResult(
            name=run.name,
            success=True,
            answer=result["answer"],
            model_used=result.get("model", run.model),
            tier_used=run.tier,
            run_type=run.type.value,
            tokens_in=result.get("tokens_in", 0),
            tokens_out=result.get("tokens_out", 0),
            latency_ms=result.get("latency_ms", 0),
            citations=result.get("citations", []),
            metadata={
                "sets": run.sets if run.type == RunType.INTERNAL else [],
                "temperature": run.temperature,
            }
        )

    except Exception as e:
        return RunResult(
            name=run.name,
            success=False,
            answer="",
            model_used=run.model,
            tier_used=run.tier,
            run_type=run.type.value,
            tokens_in=0,
            tokens_out=0,
            latency_ms=int((time.time() - start_time) * 1000),
            citations=[],
            error=str(e)
        )
```

**2.2 Add Executor Methods**
```python
def _execute_internal(self, run: RunConfig, query: str) -> Dict:
    """Execute internal run using Gemini."""
    from .executors.gemini_executor import execute_gemini_internal

    # Sanitize query (remove external references)
    clean_query = self._prepare_internal_query(query, run)

    # Execute
    return execute_gemini_internal(
        query=clean_query,
        model=run.model,
        sets=run.sets,
        token_budget=run.token_budget,
        temperature=run.temperature,
        system_prompt=None  # Already in query
    )

def _execute_external(self, run: RunConfig, query: str) -> Dict:
    """Execute external run using Perplexity."""
    from .executors.perplexity_executor import execute_perplexity_external

    # Sanitize query (external membrane enforcement)
    clean_query = self._prepare_external_query(query)

    # Execute
    return execute_perplexity_external(
        query=clean_query,
        model=run.model,
        temperature=run.temperature,
        timeout=300
    )
```

---

### Phase 3: Implement Synthesis (1 hour)

**Current Status:** Synthesis strategies defined but not implemented

**Required Implementations:**

#### 3.1 Consensus Strategy
```python
def _synthesize_consensus(
    self,
    runs: List[RunResult],
    min_agreement: int = 2
) -> Dict:
    """
    Majority voting synthesis.

    Algorithm:
    1. Extract answers from successful runs
    2. Group by similarity (fuzzy match or exact)
    3. Find majority (≥ min_agreement)
    4. Return majority answer with confidence

    Returns:
        {
            "consensus_answer": str,
            "agreement_score": float,  # fraction agreeing
            "disagreements": List[str]  # minority answers
        }
    """
    successful = [r for r in runs if r.success and not r.skipped]

    if len(successful) < min_agreement:
        return {
            "consensus_answer": "",
            "agreement_score": 0.0,
            "disagreements": ["Insufficient runs for consensus"]
        }

    # Simple exact match (could enhance with fuzzy matching)
    from collections import Counter
    answers = [r.answer for r in successful]
    counts = Counter(answers)
    most_common = counts.most_common(1)[0]

    if most_common[1] >= min_agreement:
        return {
            "consensus_answer": most_common[0],
            "agreement_score": most_common[1] / len(successful),
            "disagreements": [ans for ans, cnt in counts.items() if ans != most_common[0]]
        }
    else:
        return {
            "consensus_answer": "",
            "agreement_score": 0.0,
            "disagreements": answers
        }
```

#### 3.2 Triangulation Strategy
```python
def _synthesize_triangulation(
    self,
    runs: List[RunResult],
    query: str
) -> Dict:
    """
    Cross-reference multiple perspectives.

    Algorithm:
    1. Collect all answers
    2. Identify common themes across answers
    3. Identify unique insights per run
    4. Flag contradictions
    5. Synthesize integrated view

    For now: Use LLM to synthesize
    Future: Could use formal integration logic
    """
    successful = [r for r in runs if r.success and not r.skipped]

    if not successful:
        return {
            "consensus_answer": "",
            "agreement_score": 0.0,
            "disagreements": ["No successful runs"]
        }

    # Build synthesis prompt
    synthesis_prompt = f"""
    Original Query: {query}

    Multiple perspectives have been gathered:

    """

    for i, result in enumerate(successful, 1):
        synthesis_prompt += f"\nPerspective {i} ({result.name}):\n{result.answer}\n"

    synthesis_prompt += """

    Synthesize these perspectives by:
    1. Identifying common themes (what do all agree on?)
    2. Noting unique insights (what does each add?)
    3. Flagging contradictions (where do they disagree?)
    4. Providing integrated answer

    Format:
    COMMON: [themes all share]
    UNIQUE: [perspective-specific insights]
    CONTRADICTIONS: [disagreements]
    SYNTHESIS: [integrated answer]
    """

    # Use Gemini to synthesize
    from .executors.gemini_executor import execute_gemini_internal

    synthesis = execute_gemini_internal(
        query=synthesis_prompt,
        model="gemini-2.5-flash",  # Fast synthesis
        sets=["theory"],  # Minimal context
        token_budget=50000,
        temperature=0.2
    )

    return {
        "consensus_answer": synthesis["answer"],
        "agreement_score": 1.0,  # Synthesized view
        "disagreements": []  # Extracted from synthesis
    }
```

#### 3.3 Other Strategies
```python
def _synthesize_dialectic(self, runs, query) -> Dict:
    """Thesis + Antithesis → Synthesis"""
    # Implementation similar to triangulation
    # But expects exactly 2 runs (advocate, skeptic)
    pass

def _synthesize_bayesian(self, runs, weights) -> Dict:
    """Weighted evidence combination"""
    # Multiply evidence by weights
    # Calculate posterior probability
    pass

def _synthesize_hierarchical(self, runs, query) -> Dict:
    """Multi-scale aggregation"""
    # Organize by scale levels
    # Show cross-level flows
    pass
```

---

## Configuration Schema Validation

### What's Valid
```yaml
# VALID - has both type and tier
- name: "example"
  type: "internal"
  tier: "long_context"
  model: "gemini-3-pro-preview"
  sets: ["theory"]
  token_budget: 100000

# VALID - external with minimal config
- name: "perplexity"
  type: "external"
  tier: "perplexity"
  model: "sonar-pro"
```

### What's Invalid
```yaml
# INVALID - internal without sets
- name: "bad"
  type: "internal"
  tier: "long_context"
  # ❌ Missing: sets, token_budget

# INVALID - external with sets (membrane violation)
- name: "bad"
  type: "external"
  tier: "perplexity"
  sets: ["theory"]  # ❌ External can't use repo context
```

---

## Error Handling Strategy

### Failure Modes

**1. API Key Missing**
```
Error: PERPLEXITY_API_KEY not found
Action: Check Doppler or environment
Recovery: Skip external runs, continue with internal
```

**2. Rate Limit Hit**
```
Error: 429 Too Many Requests
Action: Exponential backoff (already in analyze.py)
Recovery: Retry with jitter
```

**3. Run Fails (timeout, error)**
```
Error: Run "external" failed with timeout
Action: Mark run as failed, continue others
Recovery: Synthesis uses only successful runs
```

**4. All Runs Fail**
```
Error: 0/3 runs succeeded
Action: Return error to user
Recovery: No synthesis possible
```

**5. Insufficient Agreement**
```
Error: Only 1/3 runs agree (need 2/3)
Action: Flag as conflict
Recovery: Return all answers, let user decide
```

---

## Testing Strategy

### Unit Tests

**Test 1: Schema Loading**
```python
def test_schema_loads():
    engine = ResearchEngine()
    schema = engine.get_schema("validation_trio")
    assert schema is not None
    assert len(schema.runs) == 3
```

**Test 2: Internal Execution**
```python
def test_internal_execution():
    run = RunConfig(
        name="test",
        type=RunType.INTERNAL,
        model="gemini-2.5-flash",
        sets=["theory"],
        token_budget=10000,
        temperature=0.1
    )
    result = execute_single_run(run, "What is a function?")
    assert result.success
    assert result.tokens_in > 0
    assert "function" in result.answer.lower()
```

**Test 3: External Execution**
```python
@pytest.mark.skipif(not has_perplexity_key(), reason="No API key")
def test_external_execution():
    run = RunConfig(
        name="test",
        type=RunType.EXTERNAL,
        tier="perplexity",
        model="sonar-pro",
        temperature=0.2
    )
    result = execute_single_run(run, "What is Python?")
    assert result.success
    assert len(result.citations) > 0
```

**Test 4: Consensus Synthesis**
```python
def test_consensus_synthesis():
    runs = [
        RunResult(answer="A", success=True, ...),
        RunResult(answer="A", success=True, ...),
        RunResult(answer="B", success=True, ...),
    ]
    synthesis = synthesize_consensus(runs, min_agreement=2)
    assert synthesis["consensus_answer"] == "A"
    assert synthesis["agreement_score"] == 2/3
```

---

### Integration Tests

**Test 5: Full Workflow Execution**
```python
def test_validation_trio_workflow():
    engine = ResearchEngine()
    result = engine.execute(
        schema_name="validation_trio",
        query="What is the purpose of L0 axioms?"
    )
    assert result.consensus_answer != ""
    assert result.agreement_score > 0
    assert len(result.individual_runs) == 3
```

**Test 6: Perplexity Optimized Workflow**
```python
@pytest.mark.skipif(not has_perplexity_key(), reason="No API key")
def test_perplexity_optimized():
    engine = ResearchEngine()
    result = engine.execute(
        schema_name="perplexity_optimized",
        query="Test query"
    )
    assert result.individual_runs[0].name == "perplexity_research"
    assert len(result.individual_runs[0].citations) > 5
```

---

## Cost & Performance Estimates

### Execution Costs

**Per Run:**
```
Internal (Gemini):
- Input: ~100K tokens × $0.001/1K = $0.10
- Output: ~1K tokens × $0.005/1K = $0.005
- Total: ~$0.10 per internal run

External (Perplexity):
- sonar-pro: $3/1M input, $15/1M output
- Typical: 500 input, 2000 output
- Cost: $0.001 + $0.030 = ~$0.03 per external run

Workflow (validation_trio):
- 2 internal + 1 external
- ~$0.10 + $0.10 + $0.03 = $0.23 total
```

### Performance

**Latency:**
```
Internal run: 30-60s (depends on context size)
External run: 15-45s (depends on query complexity)
Synthesis: 10-20s (LLM-based) or <1s (algorithmic)

Parallel execution (future): 60s max (not 90s sequential)
```

---

## Dependencies & Requirements

### Python Packages
```
# Already installed:
- google-genai (Gemini SDK)
- httpx (Perplexity API calls)
- pyyaml (schema loading)

# Might need:
- pytest (testing)
- python-dotenv (if not using Doppler)
```

### Environment Variables
```
GEMINI_API_KEY=<from Doppler or env>
PERPLEXITY_API_KEY=<from Doppler or env>
```

### File Dependencies
```
Reads:
- wave/config/research_schemas.yaml (workflow definitions)
- wave/config/analysis_sets.yaml (context sets)

Writes:
- particle/docs/research/perplexity/ (auto-save)
- particle/docs/research/gemini/ (auto-save)
```

---

## Success Criteria

### Must Have (P0)
- ✅ Workflows actually execute (not stubs)
- ✅ Internal runs call Gemini with repo context
- ✅ External runs call Perplexity
- ✅ Results returned to user
- ✅ Consensus synthesis works

### Should Have (P1)
- ✅ All synthesis strategies implemented
- ✅ Error handling robust
- ✅ Auto-save works
- ✅ Tests pass

### Nice to Have (P2)
- ⚠️ Parallel execution (speed up multi-run workflows)
- ⚠️ Caching (avoid duplicate queries)
- ⚠️ Cost tracking (accumulate spend)

---

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **API changes** | 30% | HIGH | Version pin dependencies |
| **Rate limits** | 40% | MEDIUM | Exponential backoff (exists) |
| **Cost overrun** | 25% | MEDIUM | Cost alerts in config |
| **Synthesis wrong** | 35% | MEDIUM | Human review required |
| **Over-engineering** | 40% | LOW | Keep minimal, iterate |

---

## Implementation Timeline

### Phase 1: Executors (1 hour)
- Extract gemini_executor.py
- Create perplexity_executor.py
- Unit test each

### Phase 2: Router (30 min)
- Implement _execute_single_run()
- Add _execute_internal()
- Add _execute_external()

### Phase 3: Synthesis (1 hour)
- Implement consensus
- Implement triangulation
- Test synthesis strategies

### Phase 4: Integration (30 min)
- Test full workflows
- Fix bugs
- Document usage

**Total: 3 hours**

---

## Open Questions

### Q1: Parallel vs Sequential Execution?

**Current:** Sequential (run1 → run2 → run3)
**Future:** Parallel (all 3 simultaneously)

**Decision:** Start sequential, add parallel later?

### Q2: How to handle synthesis failures?

**If synthesis can't reach consensus:**
- Return all answers?
- Mark as conflict?
- Use highest-confidence answer?

**Decision:** Mark as conflict, return all

### Q3: Should workflows cache results?

**Benefit:** Same query → instant result (no API call)
**Risk:** Stale answers

**Decision:** No caching initially, add later if needed

---

## Next Steps

**After specification approved:**

1. Create `wave/tools/ai/aci/executors/` directory
2. Implement gemini_executor.py
3. Implement perplexity_executor.py
4. Update research_orchestrator.py
5. Write tests
6. Validate with existing workflows
7. Document usage

**Estimated effort:** 3 hours focused work

---

## Validation Checklist

Before considering complete:

- [ ] validation_trio executes successfully
- [ ] perplexity_optimized executes successfully
- [ ] Consensus synthesis returns results
- [ ] Triangulation synthesis returns results
- [ ] Internal runs use repo context
- [ ] External runs hit Perplexity API
- [ ] Auto-save works for both
- [ ] Error handling catches failures gracefully
- [ ] Tests pass
- [ ] Documentation updated

---

**END OF SPECIFICATION**

**Status:** Ready for implementation
**Approval needed:** Review spec, then implement
**Estimated completion:** 3 hours from approval
