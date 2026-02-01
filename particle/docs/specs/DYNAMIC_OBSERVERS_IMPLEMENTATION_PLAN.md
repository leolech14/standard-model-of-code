# Dynamic Observers Implementation Plan

> **Purpose:** Complete implementation plan for SMC Axiom E2 (Four Flows) and G1 (Three Observers)
> **Status:** ACTIVE - Gemini-validated architecture
> **Date:** 2026-01-31
> **Target:** Full implementation with toggle-based activation
> **Timeline:** v2.0 (post v1.0.0 stabilization)

## Related Documents

| Document | Purpose |
|----------|---------|
| `docs/theory/L0_AXIOMS.md` | Axiom E2 (Four Flows) and G1 (Three Observers) definitions |
| `docs/theory/L1_DEFINITIONS.md` | LOCUS, Realms, Flow substance definitions |
| `docs/theory/L2_LAWS.md` | Flow resistance equations, drift formulas |
| `.agent/deck/DYNAMIC_OBSERVERS_REGISTRY.yaml` | 75-task implementation registry |
| `docs/research/prompts/SONAR_PRO_IMPLEMENTATION_GAPS.md` | Deep research prompt for Perplexity |
| `docs/foundations/ieee-vocabulary/SMC_ONBOARDING.md` | Complete theory overview |
| `governance/ROADMAP.md` | Project timeline (v2.0 section) |
| `src/core/database/SCHEMA_V2_PLANNING.md` | **DATABASE SCHEMA** - SQL tables for all 4 layers |

## Existing Database Infrastructure

The current Collider database (V1) already provides foundational components:

| Component | Location | Reuse For |
|-----------|----------|-----------|
| `tracked_files` table | `sqlite_backend.py` | Change Flow - file change detection |
| `DeltaResult` | `detect_changes()` | Change Flow - diff infrastructure |
| `metadata_json` column | `nodes` table | Quick prototyping before dedicated tables |
| Feature Registry | `registry.py` | Toggle pattern for new observers |
| Migration infrastructure | `migrations/` | Versioned schema additions |
| Transaction wrapping | `DatabaseBackend` | Multi-table atomic inserts |

**Impact:** Phase 4 (Git Mining) estimated hours reduced - builds on existing `tracked_files` + `DeltaResult`.

## Validation

**Gemini Analysis (2026-01-31):** Architecture validated via `analyze.py --aci --tier gemini`. Gemini confirmed:
- Toggle architecture correct for gradual rollout
- Phase ordering optimizes incremental value
- Task granularity appropriate for registry
- No missing integration points detected

---

## Executive Summary

This plan implements the missing 3 of 4 flow substances (Axiom E2) and 1 of 3 observers (Axiom G1) to complete the SMC theory implementation.

```
CURRENT STATE:
  Axiom E2: Static Flow ✅ | Runtime Flow ❌ | Change Flow ❌ | Human Flow ❌
  Axiom G1: Structural ✅ | Operational ❌ | Generative ⚠️ (partial)

TARGET STATE:
  All flows implemented, all observers active
  Toggle system for gradual activation
```

---

## Architecture Overview

### New Directory Structure

```
particle/
├── src/
│   ├── core/                      # Existing static analysis
│   │   ├── full_analysis.py       # Main pipeline (28 stages)
│   │   └── ...
│   │
│   ├── dynamics/                  # NEW: Runtime Flow (Operational Observer)
│   │   ├── __init__.py
│   │   ├── config.py              # DynamicsConfig with toggles
│   │   ├── runtime_ingestor.py    # OpenTelemetry/profiler ingestion
│   │   ├── coverage_mapper.py     # Coverage.py → AST mapping
│   │   ├── profiler_mapper.py     # cProfile/py-spy → AST mapping
│   │   ├── identity_resolver.py   # (file, line) → node_id resolution
│   │   └── telemetry_collector.py # Local OTLP collector
│   │
│   ├── evolution/                 # NEW: Change Flow (Temporal Observer)
│   │   ├── __init__.py
│   │   ├── config.py              # EvolutionConfig with toggles
│   │   ├── git_miner.py           # PyDriller-based history mining
│   │   ├── temporal_coupling.py   # Co-change matrix computation
│   │   ├── churn_analyzer.py      # Code churn metrics
│   │   ├── impact_predictor.py    # Blast radius estimation
│   │   └── stability_tracker.py   # File stability over time
│   │
│   ├── social/                    # NEW: Human Flow (Knowledge Observer)
│   │   ├── __init__.py
│   │   ├── config.py              # SocialConfig with toggles
│   │   ├── authorship_analyzer.py # Git blame → ownership mapping
│   │   ├── truck_factor.py        # Bus factor computation
│   │   ├── knowledge_islands.py   # Single-author code detection
│   │   ├── review_patterns.py     # Code review analysis
│   │   └── conway_validator.py    # Org ↔ architecture alignment
│   │
│   ├── operational/               # NEW: Operational Feedback Loop
│   │   ├── __init__.py
│   │   ├── config.py              # OperationalConfig with toggles
│   │   ├── dora_metrics.py        # DORA metric computation
│   │   ├── incident_correlator.py # Incident → code change mapping
│   │   ├── failure_predictor.py   # Risk model from metrics
│   │   └── slo_tracker.py         # SLO/SLI → code component mapping
│   │
│   └── observers/                 # NEW: Unified Observer Framework
│       ├── __init__.py
│       ├── base_observer.py       # Abstract observer interface
│       ├── structural_observer.py # Wraps existing static analysis
│       ├── operational_observer.py# Wraps dynamics + operational
│       ├── generative_observer.py # Wraps .agent/ integration
│       └── multi_layer_graph.py   # Unified multi-dimensional graph
│
├── schema/
│   ├── dynamics_schema.json       # Runtime data schema
│   ├── evolution_schema.json      # Temporal data schema
│   ├── social_schema.json         # Knowledge data schema
│   └── operational_schema.json    # DORA/incident schema
│
└── config/
    └── observers_config.yaml      # Master toggle configuration
```

---

## Toggle System Design

### Master Configuration (`config/observers_config.yaml`)

```yaml
# Observer Toggle Configuration
# All new observers start DISABLED for gradual rollout

observers:
  structural:
    enabled: true  # Always on - existing functionality

  operational:
    enabled: false  # Toggle on when ready
    components:
      runtime_profiling: false
      coverage_mapping: false
      telemetry_collection: false

  generative:
    enabled: true  # Partial - .agent/ integration
    components:
      session_tracking: true
      commit_analysis: false

flows:
  static:
    enabled: true  # Always on

  runtime:
    enabled: false
    components:
      opentelemetry: false
      cprofile: false
      pyspy: false
      coverage: false

  change:
    enabled: false
    components:
      temporal_coupling: false
      churn_analysis: false
      impact_prediction: false

  human:
    enabled: false
    components:
      truck_factor: false
      knowledge_islands: false
      review_patterns: false
      conway_validation: false

integration:
  neo4j_multi_layer: false
  dora_metrics: false
  incident_correlation: false
```

---

## Implementation Phases

### Phase 1: Foundation (Week 1-2)

**Goal:** Build toggle infrastructure and base observer framework

| Task ID | Task | Files | Priority |
|---------|------|-------|----------|
| DYN-001 | Create observers_config.yaml schema | `config/observers_config.yaml` | P0 |
| DYN-002 | Implement config loader with toggle support | `src/observers/config.py` | P0 |
| DYN-003 | Create BaseObserver abstract class | `src/observers/base_observer.py` | P0 |
| DYN-004 | Wrap existing static analysis as StructuralObserver | `src/observers/structural_observer.py` | P0 |
| DYN-005 | Create multi-layer graph data structure | `src/observers/multi_layer_graph.py` | P1 |
| DYN-006 | Add --observers flag to CLI | `cli.py` | P1 |

**Test:** `./collider full . --observers structural` works identically to current

---

### Phase 2: Coverage Integration (Week 2-3)

**Goal:** First runtime signal - code coverage mapping

| Task ID | Task | Files | Priority |
|---------|------|-------|----------|
| DYN-010 | Create dynamics package structure | `src/dynamics/__init__.py` | P0 |
| DYN-011 | Implement Coverage.py parser | `src/dynamics/coverage_mapper.py` | P0 |
| DYN-012 | Implement identity resolver (line → node_id) | `src/dynamics/identity_resolver.py` | P0 |
| DYN-013 | Create coverage schema | `schema/dynamics_schema.json` | P1 |
| DYN-014 | Add coverage data to unified_analysis.json | `src/core/brain_download.py` | P1 |
| DYN-015 | Visualize coverage in HTML output | `src/core/viz/` | P2 |

**Test:** Run pytest with coverage, then `./collider full . --coverage-file .coverage`

---

### Phase 3: Profiler Integration (Week 3-4)

**Goal:** Execution time and call frequency data

| Task ID | Task | Files | Priority |
|---------|------|-------|----------|
| DYN-020 | Implement cProfile output parser | `src/dynamics/profiler_mapper.py` | P0 |
| DYN-021 | Implement py-spy output parser | `src/dynamics/profiler_mapper.py` | P1 |
| DYN-022 | Add execution_count to node schema | `schema/particle.schema.json` | P0 |
| DYN-023 | Add avg_latency to node schema | `schema/particle.schema.json` | P0 |
| DYN-024 | Create RuntimeIngestor stage | `src/dynamics/runtime_ingestor.py` | P0 |
| DYN-025 | Add hotspot detection | `src/dynamics/runtime_ingestor.py` | P1 |

**Test:** Profile a script, then `./collider full . --profile-file profile.prof`

---

### Phase 4: Git Mining (Week 4-5)

**Goal:** Temporal coupling and churn analysis

| Task ID | Task | Files | Priority |
|---------|------|-------|----------|
| DYN-030 | Create evolution package structure | `src/evolution/__init__.py` | P0 |
| DYN-031 | Implement GitMiner with PyDriller | `src/evolution/git_miner.py` | P0 |
| DYN-032 | Implement temporal coupling matrix | `src/evolution/temporal_coupling.py` | P0 |
| DYN-033 | Implement churn analyzer | `src/evolution/churn_analyzer.py` | P0 |
| DYN-034 | Create evolution schema | `schema/evolution_schema.json` | P1 |
| DYN-035 | Add churn_rate to node schema | `schema/particle.schema.json` | P1 |
| DYN-036 | Implement impact predictor | `src/evolution/impact_predictor.py` | P2 |

**Test:** `./collider full . --git-history --history-depth 100`

---

### Phase 5: Knowledge Analysis (Week 5-6)

**Goal:** Truck factor, knowledge islands, authorship

| Task ID | Task | Files | Priority |
|---------|------|-------|----------|
| DYN-040 | Create social package structure | `src/social/__init__.py` | P0 |
| DYN-041 | Implement authorship analyzer | `src/social/authorship_analyzer.py` | P0 |
| DYN-042 | Implement truck factor algorithm | `src/social/truck_factor.py` | P0 |
| DYN-043 | Implement knowledge island detection | `src/social/knowledge_islands.py` | P0 |
| DYN-044 | Create social schema | `schema/social_schema.json` | P1 |
| DYN-045 | Add primary_author to node schema | `schema/particle.schema.json` | P1 |
| DYN-046 | Add knowledge_risk to node schema | `schema/particle.schema.json` | P1 |

**Test:** `./collider full . --social-analysis`

---

### Phase 6: Operational Integration (Week 6-8)

**Goal:** DORA metrics, incident correlation

| Task ID | Task | Files | Priority |
|---------|------|-------|----------|
| DYN-050 | Create operational package structure | `src/operational/__init__.py` | P0 |
| DYN-051 | Implement DORA metric calculator | `src/operational/dora_metrics.py` | P0 |
| DYN-052 | Implement incident correlator | `src/operational/incident_correlator.py` | P1 |
| DYN-053 | Create operational schema | `schema/operational_schema.json` | P1 |
| DYN-054 | Add failure_rate to node schema | `schema/particle.schema.json` | P2 |
| DYN-055 | Implement failure predictor ML model | `src/operational/failure_predictor.py` | P2 |

**Test:** `./collider full . --dora-metrics --ci-log ci_history.json`

---

### Phase 7: Multi-Layer Graph (Week 8-10)

**Goal:** Unified Neo4j representation

| Task ID | Task | Files | Priority |
|---------|------|-------|----------|
| DYN-060 | Design multi-layer Neo4j schema | `docs/specs/MULTI_LAYER_GRAPH.md` | P0 |
| DYN-061 | Implement graph layer abstraction | `src/observers/multi_layer_graph.py` | P0 |
| DYN-062 | Export structural layer to Neo4j | `src/observers/neo4j_export.py` | P0 |
| DYN-063 | Export runtime layer to Neo4j | `src/observers/neo4j_export.py` | P1 |
| DYN-064 | Export temporal layer to Neo4j | `src/observers/neo4j_export.py` | P1 |
| DYN-065 | Export social layer to Neo4j | `src/observers/neo4j_export.py` | P1 |
| DYN-066 | Implement cross-layer queries | `src/observers/multi_layer_graph.py` | P2 |

**Test:** `./collider full . --export-neo4j --all-layers`

---

### Phase 8: Unified Observer API (Week 10-12)

**Goal:** Clean API for all observers

| Task ID | Task | Files | Priority |
|---------|------|-------|----------|
| DYN-070 | Implement OperationalObserver | `src/observers/operational_observer.py` | P0 |
| DYN-071 | Implement GenerativeObserver | `src/observers/generative_observer.py` | P0 |
| DYN-072 | Create unified observe() API | `src/observers/__init__.py` | P0 |
| DYN-073 | Update full_analysis.py to use observers | `src/core/full_analysis.py` | P1 |
| DYN-074 | Add observer status to health report | `src/core/brain_download.py` | P1 |
| DYN-075 | Document observer API | `docs/specs/OBSERVER_API.md` | P2 |

**Test:** `./collider observe . --all-observers`

---

## Dependencies

### Python Packages (add to requirements.txt)

```
# Runtime Flow
opentelemetry-api>=1.20.0
opentelemetry-sdk>=1.20.0
opentelemetry-exporter-otlp>=1.20.0
py-spy>=0.3.14  # Optional, requires sudo
coverage>=7.0.0

# Change Flow
pydriller>=2.6.0
gitpython>=3.1.40

# Human Flow
# (uses gitpython from above)

# Operational
# (no new deps - uses existing)

# Multi-Layer Graph
neo4j>=5.0.0  # Optional
```

---

## CLI Interface Updates

```bash
# Current (unchanged)
./collider full /path/to/repo

# New flags (all optional, all off by default)
./collider full /path/to/repo \
  --coverage-file .coverage \           # Phase 2
  --profile-file profile.prof \         # Phase 3
  --git-history --history-depth 100 \   # Phase 4
  --social-analysis \                   # Phase 5
  --dora-metrics \                      # Phase 6
  --export-neo4j --all-layers           # Phase 7

# Toggle activation via config
./collider full /path/to/repo --config observers_config.yaml

# Or enable specific observers
./collider full /path/to/repo \
  --enable-observer operational \
  --enable-flow runtime,change
```

---

## Output Schema Extensions

### Node Schema Additions

```json
{
  "id": "...",
  "atom": "...",

  "// Existing fields...": "...",

  "runtime": {
    "execution_count": 1523,
    "avg_latency_ms": 2.4,
    "p99_latency_ms": 15.2,
    "memory_bytes": 1024000,
    "is_hotspot": true,
    "coverage_percent": 87.5,
    "last_profiled": "2026-01-31T12:00:00Z"
  },

  "evolution": {
    "churn_rate": 0.15,
    "stability": "volatile",
    "last_modified": "2026-01-30",
    "modification_count": 45,
    "temporal_coupling": ["file_b.py", "file_c.py"]
  },

  "social": {
    "primary_author": "developer@example.com",
    "author_count": 3,
    "knowledge_risk": "medium",
    "last_reviewer": "senior@example.com",
    "review_count": 12
  },

  "operational": {
    "failure_rate": 0.02,
    "incident_count": 1,
    "last_incident": "2026-01-15",
    "deployment_count": 25,
    "mttr_hours": 0.5
  }
}
```

---

## Success Criteria

### Per-Phase Validation

| Phase | Success Criteria |
|-------|------------------|
| 1 | Toggle system works, StructuralObserver identical to current |
| 2 | Coverage data appears in nodes, visualization works |
| 3 | Hotspots detected, execution times recorded |
| 4 | Temporal coupling matrix computed, churn metrics visible |
| 5 | Truck factor computed, knowledge islands flagged |
| 6 | DORA metrics computed from CI logs |
| 7 | Neo4j contains all 4 graph layers |
| 8 | Unified API works, all observers queryable |

### Integration Test

```bash
# Full pipeline with all observers
./collider full /path/to/repo \
  --enable-all-observers \
  --coverage-file .coverage \
  --profile-file profile.prof \
  --git-history \
  --export-neo4j

# Verify output contains all dimensions
jq '.nodes[0] | keys' unified_analysis.json
# Should include: runtime, evolution, social, operational
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Performance overhead | All new observers OFF by default |
| Breaking existing pipelines | StructuralObserver wraps existing code unchanged |
| PyDriller slow on large repos | Configurable history-depth limit |
| Neo4j not available | Graceful degradation to JSON export |
| Profiler data format changes | Abstract parser interface for multiple formats |

---

## Questions for Gemini Validation

1. Is the toggle architecture correct for gradual rollout?
2. Should phases be reordered for better incremental value?
3. Are there missing tasks in any phase?
4. What's the optimal task granularity for the registry?
5. Should we add estimated hours per task?
6. Are there integration risks between phases?
7. What test fixtures do we need to create?

---

*This plan implements SMC Axioms E2 and G1 completely.*
