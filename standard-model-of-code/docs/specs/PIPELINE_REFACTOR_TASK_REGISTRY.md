# PIPELINE REFACTOR TASK REGISTRY

> Master registry tracking pipeline class-based refactoring implementation.
>
> **Created:** 2026-01-22
> **Last Updated:** 2026-01-22
> **Status:** PLANNING
> **Decision Source:** Holographic Socratic Layer + Architect Analysis

---

## EXECUTIVE SUMMARY

### The Problem

The Holographic Socratic Layer detected **systemic non-compliance** in the pipeline:

| Invariant | Expected | Actual | Status |
|-----------|----------|--------|--------|
| BaseStage inheritance | Class hierarchy | Standalone functions | FAIL |
| `execute`/`run` method | Standardized interface | Function names vary | FAIL |
| Statelessness | No side effects | Mutates input args | PARTIAL |
| Standard result format | `ProcessingResult` | `dict` | FAIL |

### The Decision

**Option B: Refactor to Classes** (Architect verdict)

Rationale grounded in Standard Model theory:
- Functions are L2/L3 holons; Stages should be L4 CONTAINERs
- Class-based stages have higher Q-Score (coherence, simplicity)
- Enables composite pattern over brittle linear chain
- Aligns implementation with theoretical framework

### Success Criteria

- [ ] All 18 pipeline stages wrapped in Stage classes
- [ ] `PipelineManager` orchestrates execution
- [ ] `CodebaseState` flows between stages (no mutation)
- [ ] Holographic Socratic audit shows COMPLIANT
- [ ] All 216 tests passing
- [ ] No performance regression (< 20s for self-analysis)

---

## CURRENT PIPELINE INVENTORY

### Stages in `full_analysis.py` (18 total)

| # | Stage | Function | Lines | Side Effects | Priority |
|---|-------|----------|-------|--------------|----------|
| 1 | File Discovery | `_discover_files()` | ~50 | I/O (glob) | P1 |
| 2 | AST Extraction | `TreeSitterUniversalEngine.analyze_file()` | external | I/O (read) | P1 |
| 3 | Node Assembly | inline in `run_full_analysis` | ~30 | None | P1 |
| 4 | Edge Extraction | `EdgeExtractor.extract_edges()` | external | None | P1 |
| 5 | Scope Analysis | `ScopeAnalyzer.analyze()` | external | None | P2 |
| 6 | Control Flow | `ControlFlowAnalyzer.analyze()` | external | None | P2 |
| 7 | Data Flow | `DataFlowAnalyzer.analyze()` | external | None | P2 |
| 8 | Codome Boundaries | `create_codome_boundaries()` | ~150 | Mutates edges | P2 |
| 9 | Atom Classification | `AtomClassifier.classify()` | external | None | P1 |
| 10 | Role Assignment | `TopologyReasoning.assign_roles()` | external | None | P2 |
| 11 | Graph Metrics | `compute_graph_metrics()` | ~80 | Mutates nodes | P2 |
| 12 | Markov Matrix | `compute_markov_matrix()` | ~60 | Mutates edges | P3 |
| 13 | Knot Detection | `detect_knots()` | ~40 | None (pure) | P3 |
| 14 | Purpose Field | `detect_purpose_field()` | ~100 | None | P3 |
| 15 | RPBL Scoring | `compute_rpbl_scores()` | ~80 | Mutates nodes | P2 |
| 16 | Health Analysis | `analyze_health()` | ~60 | None | P3 |
| 17 | Output Generation | `generate_outputs()` | ~100 | I/O (write) | P1 |
| 18 | Report Generation | `BrainDownload.generate()` | external | I/O (write) | P1 |

### External Analyzers (Already Class-Based)

These are already compliant or near-compliant:

| Class | File | Status |
|-------|------|--------|
| `TreeSitterUniversalEngine` | `tree_sitter_engine.py` | Compliant |
| `EdgeExtractor` | `edge_extractor.py` | Compliant |
| `ScopeAnalyzer` | `scope_analyzer.py` | Compliant |
| `ControlFlowAnalyzer` | `control_flow_analyzer.py` | Compliant |
| `DataFlowAnalyzer` | `data_flow_analyzer.py` | Compliant |
| `AtomClassifier` | `atom_classifier.py` | Compliant |
| `TopologyReasoning` | `topology_reasoning.py` | Compliant |
| `BrainDownload` | `brain_download.py` | Compliant |

---

## PHASE 1: FOUNDATION

### P1-01: Define BaseStage Abstract Class

**Confidence:** 95% (Execute)

| Attribute | Value |
|-----------|-------|
| **File** | `src/core/pipeline/base_stage.py` |
| **Lines** | ~50 |
| **Dependencies** | None |
| **Atom ID** | `ORG.SYS.A` (Organization, System, Abstract) |

**Interface:**

```python
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .state import CodebaseState

class BaseStage(ABC):
    """Abstract base class for all pipeline stages."""

    name: str  # Human-readable stage name

    @abstractmethod
    def execute(self, state: "CodebaseState") -> "CodebaseState":
        """
        Execute this stage's processing.

        Args:
            state: Immutable input state

        Returns:
            New state with this stage's results added
        """
        pass

    def validate_input(self, state: "CodebaseState") -> bool:
        """Optional: Validate state has required fields."""
        return True

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"
```

**Invariants:**
1. Must not modify input state (return new state)
2. Must have a `name` attribute
3. Must implement `execute()`
4. Should be stateless (no instance variables modified)

---

### P1-02: Define CodebaseState Data Class

**Confidence:** 95% (Execute)

| Attribute | Value |
|-----------|-------|
| **File** | `src/core/pipeline/state.py` |
| **Lines** | ~100 |
| **Dependencies** | None |

**Structure:**

```python
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

@dataclass(frozen=True)  # Immutable
class CodebaseState:
    """Immutable state passed between pipeline stages."""

    # Input
    target_path: str
    output_dir: Optional[str] = None
    options: Dict[str, Any] = field(default_factory=dict)

    # Stage 1-4: Discovery & Extraction
    files: List[str] = field(default_factory=list)
    nodes: List[Dict] = field(default_factory=list)
    edges: List[Dict] = field(default_factory=list)

    # Stage 5-7: Analysis
    scope_data: Dict = field(default_factory=dict)
    control_flow_data: Dict = field(default_factory=dict)
    data_flow_data: Dict = field(default_factory=dict)

    # Stage 8-11: Classification
    codome_boundaries: Dict = field(default_factory=dict)
    atom_classifications: Dict = field(default_factory=dict)
    roles: Dict = field(default_factory=dict)
    graph_metrics: Dict = field(default_factory=dict)

    # Stage 12-16: Advanced Analysis
    markov_matrix: Dict = field(default_factory=dict)
    knots: List[Dict] = field(default_factory=list)
    purpose_field: Dict = field(default_factory=dict)
    rpbl_scores: Dict = field(default_factory=dict)
    health: Dict = field(default_factory=dict)

    # Metadata
    stage_timings: Dict[str, float] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

    def with_updates(self, **kwargs) -> "CodebaseState":
        """Return new state with specified fields updated."""
        from dataclasses import replace
        return replace(self, **kwargs)
```

**Key Design Decisions:**
- `frozen=True` ensures immutability
- `with_updates()` provides functional update pattern
- All fields have defaults for incremental population

---

### P1-03: Define PipelineManager

**Confidence:** 95% (Execute)

| Attribute | Value |
|-----------|-------|
| **File** | `src/core/pipeline/manager.py` |
| **Lines** | ~150 |
| **Dependencies** | P1-01, P1-02 |

**Structure:**

```python
from typing import List, Optional
from .base_stage import BaseStage
from .state import CodebaseState
from ..observability import StageTimer

class PipelineManager:
    """Orchestrates pipeline stage execution."""

    def __init__(self, stages: List[BaseStage]):
        self.stages = stages
        self._timer = StageTimer()

    def run(self, initial_state: CodebaseState) -> CodebaseState:
        """Execute all stages in sequence."""
        state = initial_state

        for stage in self.stages:
            with self._timer.measure(stage.name):
                if not stage.validate_input(state):
                    raise ValueError(f"Invalid input for {stage.name}")
                state = stage.execute(state)

        # Add timing data to final state
        return state.with_updates(
            stage_timings=self._timer.get_timings()
        )

    def run_until(self, initial_state: CodebaseState,
                  stop_after: str) -> CodebaseState:
        """Execute stages until (and including) named stage."""
        state = initial_state
        for stage in self.stages:
            state = stage.execute(state)
            if stage.name == stop_after:
                break
        return state
```

---

### P1-04: Create Pipeline Package Structure

**Confidence:** 95% (Execute)

| Attribute | Value |
|-----------|-------|
| **Files** | `src/core/pipeline/__init__.py` |
| **Lines** | ~20 |
| **Dependencies** | P1-01, P1-02, P1-03 |

**Directory Structure:**

```
src/core/pipeline/
├── __init__.py          # Public exports
├── base_stage.py        # BaseStage ABC
├── state.py             # CodebaseState dataclass
├── manager.py           # PipelineManager
└── stages/              # Stage implementations (Phase 2)
    ├── __init__.py
    ├── discovery.py     # FileDiscoveryStage
    ├── extraction.py    # ASTExtractionStage, EdgeExtractionStage
    ├── analysis.py      # ScopeStage, ControlFlowStage, DataFlowStage
    ├── classification.py # AtomClassificationStage, RoleAssignmentStage
    ├── metrics.py       # GraphMetricsStage, MarkovStage, RPBLStage
    ├── advanced.py      # KnotDetectionStage, PurposeFieldStage
    └── output.py        # OutputGenerationStage, ReportStage
```

---

## PHASE 2: STAGE WRAPPERS (Facade Pattern)

### P2-01 to P2-18: Wrap Each Stage

**Confidence:** 90% (Almost Ready)

For each of the 18 stages, create a wrapper class that:
1. Inherits from `BaseStage`
2. Implements `execute(state) -> state`
3. Calls existing function internally
4. Returns new state (no mutation)

**Example: MarkovMatrixStage**

```python
# src/core/pipeline/stages/metrics.py

from ..base_stage import BaseStage
from ..state import CodebaseState

class MarkovMatrixStage(BaseStage):
    """Compute Markov transition matrix for code flow."""

    name = "markov_matrix"

    def execute(self, state: CodebaseState) -> CodebaseState:
        # Call existing function (imported from full_analysis)
        from ..full_analysis import compute_markov_matrix

        # Create copies to avoid mutation
        nodes = [n.copy() for n in state.nodes]
        edges = [e.copy() for e in state.edges]

        result = compute_markov_matrix(nodes, edges)

        return state.with_updates(
            edges=edges,  # Now includes markov_weight
            markov_matrix=result
        )
```

**Stage Implementation Priority:**

| Priority | Stages | Rationale |
|----------|--------|-----------|
| **P1 (First)** | 1, 2, 3, 4, 9, 17, 18 | Core pipeline, I/O boundaries |
| **P2 (Second)** | 5, 6, 7, 8, 10, 11, 15 | Analysis stages |
| **P3 (Third)** | 12, 13, 14, 16 | Advanced/optional stages |

---

## PHASE 3: INTEGRATION

### P3-01: Refactor run_full_analysis()

**Confidence:** 85% (Needs Work)

| Attribute | Value |
|-----------|-------|
| **File** | `src/core/full_analysis.py` |
| **Dependencies** | All P2 tasks |

**Before (current):**
```python
def run_full_analysis(target_path, output_dir, options):
    files = discover_files(target_path)
    nodes = []
    for f in files:
        nodes.extend(engine.analyze_file(f))
    edges = extractor.extract_edges(nodes)
    # ... 15 more inline stages ...
    return {"nodes": nodes, "edges": edges, ...}
```

**After (refactored):**
```python
def run_full_analysis(target_path, output_dir, options):
    from .pipeline import PipelineManager, CodebaseState
    from .pipeline.stages import ALL_STAGES

    initial_state = CodebaseState(
        target_path=target_path,
        output_dir=output_dir,
        options=options or {}
    )

    manager = PipelineManager(stages=ALL_STAGES)
    final_state = manager.run(initial_state)

    return final_state.to_dict()  # Backward compatibility
```

---

### P3-02: Update semantic_models.yaml

**Confidence:** 95% (Execute)

| Attribute | Value |
|-----------|-------|
| **File** | `context-management/config/semantic_models.yaml` |
| **Dependencies** | P3-01 |

**Update to reflect new architecture:**

```yaml
pipeline:
  scope: "standard-model-of-code/src/core/**"
  definitions:
    Stage:
      description: "A processing unit in the analysis pipeline."
      role: "Processing"
      invariants:
        - "Must inherit from BaseStage"
        - "Must implement execute(state) -> state method"
        - "Must not modify input state (return new state)"
        - "Must have a 'name' attribute"
      anchors:
        - file: "standard-model-of-code/src/core/pipeline/base_stage.py"
          pattern: "class BaseStage"
        - file: "standard-model-of-code/src/core/pipeline/stages/*.py"
          pattern: "class *Stage(BaseStage)"
```

---

### P3-03: Update Tests

**Confidence:** 90% (Almost Ready)

| Attribute | Value |
|-----------|-------|
| **File** | `tests/test_pipeline_stages.py` (new) |
| **Dependencies** | P2 tasks |

**Test Categories:**
1. Unit tests for each Stage class
2. Integration test for PipelineManager
3. Regression test comparing old vs new output
4. Performance benchmark

---

## PHASE 4: CLEANUP

### P4-01: Remove Mutation Side Effects

**Confidence:** 80% (Needs Work)

Audit all stages for mutation:

| Stage | Current Mutation | Fix |
|-------|-----------------|-----|
| `create_codome_boundaries` | `edges.append()` | Return new list |
| `compute_markov_matrix` | `edge['markov_weight'] = ...` | Copy then modify |
| `compute_graph_metrics` | `node['pagerank'] = ...` | Copy then modify |
| `compute_rpbl_scores` | `node['rpbl_*'] = ...` | Copy then modify |

### P4-02: Remove I/O from Processing Stages

**Confidence:** 75% (Needs Work)

| Issue | Location | Fix |
|-------|----------|-----|
| `_open_file()` | `full_analysis.py` | Move to OutputStage |
| `print()` statements | Various | Use logging or remove |
| Direct file reads | `detect_js_imports()` | Pass content as param |

### P4-03: Run Holographic Socratic Audit

**Confidence:** 95% (Execute)

```bash
python context-management/tools/ai/analyze.py --verify pipeline
```

**Expected Result:** COMPLIANT for Stage concept

---

## CONFIDENCE METHODOLOGY

**Confidence = min(Factual, Alignment)**

| Level | Meaning | Action |
|-------|---------|--------|
| **95%+** | Execute immediately | Green light |
| **90-94%** | Almost ready | Minor clarification needed |
| **85-89%** | Needs work | Design review required |
| **80-84%** | Uncertain | Prototype first |
| **<80%** | Do not execute | More research needed |

---

## TASK SUMMARY

| Phase | Tasks | Confidence | Status |
|-------|-------|------------|--------|
| **P1: Foundation** | 4 | 95% | READY |
| **P2: Wrappers** | 18 | 90% | READY |
| **P3: Integration** | 3 | 85-95% | NEEDS DESIGN |
| **P4: Cleanup** | 3 | 75-95% | DEFERRED |

**Total Tasks:** 28
**Ready to Execute:** 22 (P1 + P2)
**Needs Design:** 3 (P3)
**Deferred:** 3 (P4)

---

## RISKS & MITIGATIONS

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Performance regression | Medium | High | Benchmark before/after |
| Breaking existing tests | Low | Medium | Run tests after each stage |
| Scope creep | Medium | Medium | Strict phase boundaries |
| Immutability overhead | Low | Low | Profile memory usage |

---

## DOCUMENT HISTORY

| Date | Change |
|------|--------|
| 2026-01-22 | Initial creation from Holographic Socratic audit findings |
