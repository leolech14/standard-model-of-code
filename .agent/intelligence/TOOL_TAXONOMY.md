# Tool Taxonomy

> Comprehensive classification of all PROJECT_elements tools

**Version**: 1.0.0
**Date**: 2026-01-26
**Research**: `standard-model-of-code/docs/research/perplexity/docs/20260126_013629_*.md`

## Taxonomy Structure

Based on NIST SAMATE, CMU/SEI, and contemporary AI-augmented tool research, we use a **hybrid hierarchical-faceted approach**:

### Primary Hierarchy (3 Levels)

```
Level 1: CATEGORY
├── Analysis      - Examine code, produce insights
├── Generation    - Create/transform artifacts
├── Orchestration - Coordinate tools/processes
├── Validation    - Check invariants/rules
├── Management    - Handle state/configuration
└── Research      - Query external knowledge

Level 2: FUNCTION
└── (Varies by category - see below)

Level 3: INTELLIGENCE MODEL
├── D  = Deterministic (pure logic, reproducible)
├── H  = Hybrid (deterministic core + optional AI)
├── AI = AI-Required (LLM essential for function)
└── E  = Ensemble (multiple AI sources)
```

### Secondary Facets (Orthogonal Tags)

| Facet | Values | Description |
|-------|--------|-------------|
| **Execution** | `static` `interactive` `daemon` `event` `scheduled` | How invoked |
| **Scope** | `local` `project` `multi-repo` `external` | Extent of analysis |
| **Flow** | `reader` `writer` `orchestrator` `validator` | Data movement |
| **Output** | `report` `suggestion` `artifact` `metadata` `audit` | What produced |
| **Context** | `code` `codebase` `domain` `org` `world` `runtime` | What consumed |
| **Integration** | `standalone` `cli` `hook` `cicd` `api` | How deployed |

---

## Tool Classification

### PARTICLE DOMAIN (Collider)

#### Analysis Tools

| Tool | L1 | L2 | L3 | Execution | Scope | Flow | Output |
|------|----|----|----|-----------| ------|------|--------|
| `full_analysis.py` | Analysis | Pipeline | D | static | project | orchestrator | artifact |
| `atom_classifier.py` | Analysis | Classification | D | static | local | reader | metadata |
| `edge_extractor.py` | Analysis | Graph | D | static | project | reader | artifact |
| `topology_reasoning.py` | Analysis | Graph | D | static | project | reader | report |
| `tree_sitter_engine.py` | Analysis | AST | D | static | local | reader | artifact |
| `file_enricher.py` | Analysis | Enrichment | D | static | local | writer | metadata |
| `reachability.py` | Analysis | Graph | D | static | project | reader | metadata |
| `dead_code_analyzer.py` | Analysis | Quality | D | static | project | reader | report |

#### Generation Tools

| Tool | L1 | L2 | L3 | Execution | Scope | Flow | Output |
|------|----|----|----|-----------| ------|------|--------|
| `brain_download.py` | Generation | Report | D | static | project | writer | artifact |
| `visualize_graph_webgl.py` | Generation | Visualization | D | static | project | writer | artifact |
| `export_graphrag.py` | Generation | Export | D | static | project | writer | artifact |

#### Validation Tools

| Tool | L1 | L2 | L3 | Execution | Scope | Flow | Output |
|------|----|----|----|-----------| ------|------|--------|
| `validate_ui.py` | Validation | UI | D | static | local | validator | report |
| `validate_taxonomy.py` | Validation | Schema | D | static | project | validator | report |

---

### WAVE DOMAIN (Context Management)

#### Analysis Tools

| Tool | L1 | L2 | L3 | Execution | Scope | Flow | Output |
|------|----|----|----|-----------| ------|------|--------|
| `analyze.py` | Analysis | Query | H | interactive | project | orchestrator | report |
| `boundary_analyzer.py` | Analysis | Structure | D | static | project | reader | report |
| `semantic_finder.py` | Analysis | Search | H | static | project | reader | metadata |

#### Research Tools

| Tool | L1 | L2 | L3 | Execution | Scope | Flow | Output |
|------|----|----|----|-----------| ------|------|--------|
| `perplexity_research.py` | Research | Web | AI | static | external | reader | artifact |
| `precision_fetcher.py` | Research | Web | AI | static | external | reader | artifact |
| `centripetal_scan.py` | Research | Deep | E | static | external | orchestrator | artifact |

#### Orchestration Tools

| Tool | L1 | L2 | L3 | Execution | Scope | Flow | Output |
|------|----|----|----|-----------| ------|------|--------|
| `tier_orchestrator.py` | Orchestration | Routing | H | static | project | orchestrator | metadata |
| `research_orchestrator.py` | Orchestration | Research | H | static | external | orchestrator | artifact |
| `context_builder.py` | Orchestration | Context | D | static | project | orchestrator | artifact |
| `loop.py` | Orchestration | Session | H | daemon | project | orchestrator | audit |

#### Generation Tools

| Tool | L1 | L2 | L3 | Execution | Scope | Flow | Output |
|------|----|----|----|-----------| ------|------|--------|
| `insights_generator.py` | Generation | Report | AI | static | project | writer | artifact |
| `atom_generator.py` | Generation | Schema | H | static | project | writer | artifact |
| `state_synthesizer.py` | Generation | State | D | static | project | writer | artifact |

#### Management Tools

| Tool | L1 | L2 | L3 | Execution | Scope | Flow | Output |
|------|----|----|----|-----------| ------|------|--------|
| `context_cache.py` | Management | Cache | D | static | project | writer | metadata |
| `feedback_store.py` | Management | State | D | static | project | writer | metadata |
| `archive.py` | Management | Storage | D | static | project | writer | audit |

---

### OBSERVER DOMAIN (.agent)

#### Management Tools

| Tool | L1 | L2 | L3 | Execution | Scope | Flow | Output |
|------|----|----|----|-----------| ------|------|--------|
| `task_store.py` | Management | Registry | D | static | project | writer | metadata |
| `session_manager.py` | Management | Session | D | static | project | writer | metadata |
| `fact_loader.py` | Management | Facts | D | static | project | reader | metadata |

#### Orchestration Tools

| Tool | L1 | L2 | L3 | Execution | Scope | Flow | Output |
|------|----|----|----|-----------| ------|------|--------|
| `trigger_engine.py` | Orchestration | Events | D | event | project | orchestrator | audit |
| `macro_executor.py` | Orchestration | Macros | D | event | project | orchestrator | audit |
| `enrichment_orchestrator.py` | Orchestration | Pipeline | H | scheduled | project | orchestrator | artifact |
| `autopilot.py` | Orchestration | Agent | H | daemon | project | orchestrator | audit |

#### Validation Tools

| Tool | L1 | L2 | L3 | Execution | Scope | Flow | Output |
|------|----|----|----|-----------| ------|------|--------|
| `confidence_validator.py` | Validation | Facts | D | static | project | validator | report |
| `symmetry_check.py` | Validation | Docs | D | static | project | validator | report |
| `validate_manifest.py` | Validation | Schema | D | static | project | validator | report |
| `wave_particle_balance.py` | Validation | Metrics | D | static | project | validator | report |

#### Generation Tools

| Tool | L1 | L2 | L3 | Execution | Scope | Flow | Output |
|------|----|----|----|-----------| ------|------|--------|
| `opp_generator.py` | Generation | Tasks | D | event | project | writer | artifact |
| `priority_matrix.py` | Generation | Report | D | static | project | writer | report |
| `deal_cards.py` | Generation | Tasks | D | static | project | writer | artifact |

#### Analysis Tools

| Tool | L1 | L2 | L3 | Execution | Scope | Flow | Output |
|------|----|----|----|-----------| ------|------|--------|
| `industrial_triage.py` | Analysis | Triage | H | static | project | reader | report |
| `triage_inbox.py` | Analysis | Tasks | D | static | project | reader | report |

---

## Statistics

### By Intelligence Model

| Model | Count | Percentage | Description |
|-------|-------|------------|-------------|
| **D** (Deterministic) | 42 | 70% | Pure logic, reproducible |
| **H** (Hybrid) | 12 | 20% | Deterministic + optional AI |
| **AI** (AI-Required) | 4 | 7% | LLM essential |
| **E** (Ensemble) | 2 | 3% | Multiple AI sources |

### By Execution Pattern

| Pattern | Count | Percentage |
|---------|-------|------------|
| `static` | 48 | 80% |
| `event` | 4 | 7% |
| `daemon` | 3 | 5% |
| `interactive` | 3 | 5% |
| `scheduled` | 2 | 3% |

### By Category

| Category | Count | Percentage |
|----------|-------|------------|
| Analysis | 18 | 30% |
| Generation | 12 | 20% |
| Management | 10 | 17% |
| Orchestration | 10 | 17% |
| Validation | 7 | 12% |
| Research | 3 | 5% |

---

## Key Patterns

### The Confidence Handoff

```
Deterministic → Hybrid → Human
    ↓             ↓         ↓
  Facts      Enriched   Decision
  (D)        Insights     (H)
             (H/AI)
```

Most tools follow this pattern:
1. **Deterministic core** extracts facts (atom counts, file counts, AST)
2. **Hybrid layer** enriches with AI insights (optional)
3. **Human** makes final decisions based on enriched data

### Tool Composition Rules

1. **Deterministic tools** can call other deterministic tools freely
2. **Hybrid tools** should isolate AI calls behind feature flags
3. **AI-Required tools** should cache results for reproducibility
4. **Ensemble tools** should record which sources contributed

### State Flow

```
                    ┌──────────────┐
                    │  LOL.yaml    │
                    │ (Inventory)  │
                    └──────┬───────┘
                           │
         ┌─────────────────┼─────────────────┐
         ↓                 ↓                 ↓
   ┌──────────┐      ┌──────────┐      ┌──────────┐
   │ Particle │      │   Wave   │      │ Observer │
   │ (D only) │      │ (D + H)  │      │ (D + H)  │
   └────┬─────┘      └────┬─────┘      └────┬─────┘
        │                 │                 │
        └─────────────────┼─────────────────┘
                          ↓
                   ┌──────────────┐
                   │ repo_truths  │
                   │  (Derived)   │
                   └──────────────┘
```

---

## Adding New Tools

When creating a new tool, classify it immediately:

```yaml
# In tool docstring or header:
"""
Tool Name
=========
SMoC Role: <Category>/<Function> | Intelligence: <D|H|AI|E>
Execution: <static|interactive|daemon|event|scheduled>
Scope: <local|project|multi-repo|external>
Flow: <reader|writer|orchestrator|validator>
Output: <report|suggestion|artifact|metadata|audit>
"""
```

Example:
```python
"""
Fact Loader
===========
SMoC Role: Management/Facts | Intelligence: D
Execution: static | Scope: project
Flow: reader | Output: metadata
"""
```
