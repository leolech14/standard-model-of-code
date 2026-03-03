# ARCHITECTURE - System Overview

> The three realms, the Collider pipeline, concordances, and how it all connects.

---

## The Three Realms

```
PROJECT_elements/
├── particle/  ── PARTICLE ── Body ── Deterministic measurement
├── wave/      ── WAVE     ── Brain ── Probabilistic understanding
└── .agent/    ── OBSERVER ── Eyes  ── Reactive governance
```

| Realm | Nature | Pipeline | Output |
|-------|--------|----------|--------|
| **PARTICLE** | Deterministic | Collider (28 stages) | unified_analysis.json |
| **WAVE** | Probabilistic | Refinery (4 stages) | Context chunks, embeddings |
| **OBSERVER** | Reactive | Autopilot/Wire | Tasks, decisions |

These are **MECE by directory** -- every file belongs to exactly one realm.

---

## The Collider Pipeline

The Collider transforms raw source code into a classified, scored dependency graph. Key stages:

```
SOURCE CODE
    │
    ├─ Stage 1-2:   Parse (Tree-sitter AST extraction)
    ├─ Stage 3-4:   Extract (nodes, edges, metadata)
    ├─ Stage 5-6:   Classify (atoms, roles, layers)
    ├─ Stage 7-8:   Graph (topology, centrality, orphan detection)
    ├─ Stage 9-10:  Score (purpose, coherence, quality)
    ├─ Stage 11-14: Enrich (RPBL, antimatter, hotspots, health)
    └─ Stage 15-28: Compile (unified output, visualizations, reports)
    │
    ▼
unified_analysis.json (single source of truth)
```

**Input:** A directory of source code files.
**Output:** A graph with nodes (classified code elements) and edges (dependencies).
**Approach:** 100% deterministic. No LLM calls. Pattern matching on topology, frameworks, genealogy.

---

## The Two Universes

```
PROJECTOME (everything)
├── CODOME (executable)         ← Analyzed by Collider
│   .py, .js, .ts, .go, .rs
│
└── CONTEXTOME (non-executable) ← Analyzed by AI (Refinery/ACI)
    .md, .yaml, .json (config)
```

**Key rule:** `P = C ⊔ X` (disjoint union). Every file is in exactly one universe.

---

## Concordances

A concordance is a purpose-aligned region that spans **both** universes:

```
            │ CODOME              │ CONTEXTOME
────────────┼─────────────────────┼─────────────────
Pipeline    │ full_analysis.py    │ PIPELINE_STAGES.md
            │ survey.py           │ specs/*.md
────────────┼─────────────────────┼─────────────────
AI Tools    │ analyze.py          │ analysis_sets.yaml
            │ aci/*.py            │ prompts.yaml
────────────┼─────────────────────┼─────────────────
Governance  │ task_store.py       │ registry/*.yaml
            │ confidence.py       │ ROADMAP.yaml
```

Health is measured by alignment between the code and docs within each concordance.

| Health | Meaning |
|--------|---------|
| CONCORDANT | Code and docs agree on purpose |
| UNVOICED | Code exists, docs missing |
| UNREALIZED | Docs exist, code missing |
| DISCORDANT | Both exist, purposes conflict |

---

## Subsystems

| ID | Subsystem | Realm | Purpose |
|----|-----------|-------|---------|
| S1 | **Collider** | Particle | Parse code → classify atoms → build graph |
| S2 | **HSL** | Wave | Validation rules, drift detection |
| S3 | **analyze.py** | Wave | AI query interface |
| S4 | **ACI** | Wave | 5-tier complexity-based query routing |
| S5 | **BARE** | Observer | Background auto-refinement |
| S6 | **Laboratory** | Bridge | Research API (Wave→Particle) |
| S7 | **Registry** | Observer | Task tracking (persistent) |

---

## The Loop of Truth

```
[CODEBASE] ──(1. Scan)──► [COLLIDER] ──► unified_analysis.json
                                              │
                                              ▼
                          [HSL / analyze.py] ◄─┘
                                │
                         (2. Validate)
                                ▼
                          [TASK REGISTRY] ◄── (3. Claim) ── [AGENT]
                                                              │
[CODEBASE] ◄───────────── (4. Commit) ────────────────────────┘
```

The loop is: **Scan → Validate → Claim → Fix → Scan again**.
Ground truth comes from Collider (deterministic). Validation uses AI (probabilistic).

---

## Key Artifacts

| Artifact | Format | Source | Purpose |
|----------|--------|--------|---------|
| `unified_analysis.json` | JSON | Collider | Complete code graph |
| `SUBSYSTEMS.yaml` | YAML | Manual | System registry |
| `DOMAINS.yaml` | YAML | Manual | Domain registry |
| `analysis_sets.yaml` | YAML | Config | Which files to analyze |

---

## 10 Recurring Subsystem Archetypes

Most codebases organize into these ~10 patterns:

1. **Ingress** -- Routers, controllers, middleware
2. **Egress** -- External clients, webhooks
3. **Domain Core** -- Entities, rules, use-cases
4. **Persistence** -- ORM, repositories, migrations
5. **Async Processing** -- Queues, workers, schedulers
6. **Presentation** -- UI components, view models
7. **Security** -- AuthN/AuthZ, policies
8. **Observability** -- Logging, metrics, tracing
9. **Configuration** -- Config loading, env vars
10. **Delivery** -- CI/CD pipelines, IaC

---

*Source: MODEL.md, L1_DEFINITIONS.md, GLOSSARY.md*
*This file: ~130 lines*
