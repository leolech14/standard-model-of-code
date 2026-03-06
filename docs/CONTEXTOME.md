---
id: contextome
title: "CONTEXTOME — The Context Infrastructure of PROJECT_elements"
status: active
created: 2026-03-06
last_updated: 2026-03-06
maturity: 2/10
tcp_tier: T2
---

# CONTEXTOME

> The complete context-injection, navigation, and intelligence infrastructure
> that enables agents and humans to understand PROJECT_elements.

<!-- T1:END -->

## 1. What Is the Contextome?

The **Contextome** is the complement to the **Codome** (particle/). Where the Codome
is the body — deterministic analysis engine, pipeline, type system — the Contextome
is the brain: everything that provides *understanding* of the codebase without being
the codebase itself.

Formally:

```
Contextome = { f ∈ PROJECT_elements | f provides context about code, not code itself }
           = .agent/ ∪ docs/nav/ ∪ docs/theory/ ∪ context-injection mechanisms
```

The Codome answers "what IS this code?" The Contextome answers "what does this code MEAN?"

## 2. Architecture

```
CONTEXTOME
├── Intelligence Layer    (.agent/intelligence/)     209 files, 21MB
│   ├── Data Assets       (JSONL, CSV indices)       ~30MB telemetry + indices
│   ├── Analysis Docs     (MD synthesis files)        ~5MB findings + audits
│   └── Confidence        (reports/, scans/)          Quality control
│
├── Navigation Layer      (docs/nav/)                10 files
│   └── Conceptual Guides (PURPOSE, ATOMS, ROLES...) Human-readable theory
│
├── Agent Layer           (.agent/)                  649 files, 50MB
│   ├── Registry          (registry/)                167 task files
│   ├── Tools             (tools/)                   101 automation scripts
│   ├── Macros            (macros/)                  80 reusable patterns
│   ├── Specs             (specs/)                   18 specifications
│   ├── Emergency         (emergency/)               9 crisis references
│   └── Manifests         (KERNEL, CODOME, META)     Bootstrap documents
│
├── Theory Layer          (particle/docs/theory/)    ~30 files
│   ├── Foundations       (foundations/L0-L3)         Axioms → Applications
│   └── Frameworks        (frameworks/8 theories)    Mathematical backing
│
└── Injection Layer       (context routing)          Runtime mechanisms
    ├── context_router.py (wave/dashboard/)           Context election
    ├── prompt_assembler  (wave/dashboard/)           Prompt assembly
    └── workspace_reader  (wave/dashboard/)           L1 workspace context
```

## 3. Relationship to Codome

The Brain-Body duality:

| Aspect | Codome (Body) | Contextome (Brain) |
|--------|--------------|-------------------|
| Root | `particle/` | `.agent/` + `docs/` + `wave/dashboard/` |
| Output | `unified_analysis.json` | Understanding, decisions, navigation |
| Determinism | Yes (same input → same output) | No (context-dependent) |
| Entry point | `collider-hub full` | `.agent/KERNEL.md` bootstrap |
| Schema | 167 atom types, 33 roles | CODOME_MANIFEST.yaml regions |
| Evolution | Versioned releases | Continuous accrual |
| Consumers | Pipeline stages | Agents (Claude, Gemini, Grok) |

The Codome produces facts. The Contextome produces meaning.

## 4. Key Schemata

### 4.1 CODOME_MANIFEST.yaml

Single source of truth for project architecture. Defines three realms:

- **Particle** (Body): Collider engine, pipeline, type system
- **Wave** (Brain): AI tools, context management, library
- **Observer** (Eyes): Agent infrastructure, task management

### 4.2 META_REGISTRY.yaml

Navigation registry — "where to find what":

```yaml
registries:
  tasks: .agent/registry/
  intelligence: .agent/intelligence/
  body: particle/
  brain: wave/
```

### 4.3 sos_map_compact.yaml

System-of-Systems in compact form (v1.2):
- 13 subsystems (S1-S13)
- 90/100 coherence score
- Realm assignments for each subsystem

### 4.4 Intelligence File Schema

Files in `.agent/intelligence/` follow implicit conventions:

| Pattern | Type | Example |
|---------|------|---------|
| `ALL_CAPS.md` | Analysis synthesis | `CONSOLIDATED_FINDINGS.md` |
| `ALL_CAPS.json` | Structured data | `COLLISION_CLUSTERS.json` |
| `ALL_CAPS.csv` | Tabular index | `LOL_UNIFIED.csv` |
| `ALL_CAPS.jsonl` | Event stream | `tdj.jsonl` |
| `SKEPTICAL_AUDIT_*.md` | Quality control | `SKEPTICAL_AUDIT_2026-02-24.md` |
| `subdirectory/` | Grouped artifacts | `confidence_reports/`, `comm_analysis/` |

**Proposed formal schema** (not yet enforced):

```yaml
# .agent/schema/intelligence_file.schema.yaml
required_fields:
  - created: ISO-8601 date
  - purpose: string (≤100 chars)
  - provenance: enum [manual, collider, audit, agent, research]
  - tcp_tier: enum [T0, T1, T2, T3]
optional_fields:
  - supersedes: filename
  - confidence: float [0,1]
  - related_theory: path to theory doc
```

## 5. Bootstrap Protocol

For new agents, the Contextome provides a layered onboarding:

```
L0: .agent/KERNEL.md              (identity + rules)
L1: .agent/CODOME_MANIFEST.yaml   (architecture)
L2: .agent/META_REGISTRY.yaml     (navigation)
L3: .agent/ROADMAP.yaml           (direction)
L4: .agent/intelligence/SYSTEM_OVERVIEW.md  (landscape)
```

Each layer builds on the previous. An agent can stop at any layer and
still be productive — L0 alone is sufficient for simple tasks.

## 6. Intelligence Layer Deep Dive

The intelligence layer (`.agent/intelligence/`, 209 files) is the
analytical memory of the project. Categories:

### 6.1 Data Assets (Telemetry + Indices)

| Asset | Size | Purpose |
|-------|------|---------|
| `tdj.jsonl` | 12M | Time-dimensioned journal — every execution event |
| `REPO_HISTORY.jsonl` | 9M | Linearized git history |
| `LOL_UNIFIED.csv` | 8M | Master file index (List of Lists) |
| `FILE_INDEX.csv` | 364K | Complete filesystem index |
| `DOC_GRAPH.json` | 150K | Document relationship graph |
| `THEORY_SECTION_GRAPH.json` | 29K | Theory structure graph |

### 6.2 Analysis Subdirectories

| Subdir | Files | Purpose |
|--------|-------|---------|
| `confidence_reports/` | 26 | Confidence scoring per subsystem |
| `comm_analysis/` | 29 | Inter-subsystem communication patterns |
| `centripetal_scans/` | 17 | Code coupling/gravity analysis |
| `autopilot_logs/` | 20 | Automated task execution records |
| `triage_reports/` | 10 | Issue categorization |
| `chunks/` | 4 | Parsed code chunks for semantic search |

### 6.3 Quality Control

Skeptical audits run periodically to detect overclaiming:

- `SKEPTICAL_AUDIT_2026-01-25.md` through `2026-02-24.md`
- `FULL_OVERCLAIMING_AUDIT.json` (100K evidence package)
- `OVERCLAIMING_AUDIT_REPORT.json`

## 7. Navigation Layer (docs/nav/)

10 human-readable guides that explain core concepts:

| File | Concept | Theory Source |
|------|---------|---------------|
| `ATOMS.md` | 167 structural types | L1_DEFINITIONS |
| `ROLES.md` | 33 canonical roles | L1_DEFINITIONS |
| `PURPOSE.md` | Purpose field semantics | L0_AXIOMS D1-D7 |
| `LEVELS.md` | 16-level holarchy | L1_DEFINITIONS |
| `GRAPH.md` | Dependency topology | GRAPH_THEORY |
| `FLOW.md` | Constructal law | TOPOLOGY |
| `CONCORDANCE.md` | Code-doc alignment | L2_PRINCIPLES |
| `ORPHANS.md` | Disconnection taxonomy | ORPHAN_SEMANTICS |
| `ANTIMATTER.md` | Architectural violations | L2_PRINCIPLES |
| `CONSUMERS.md` | Consumer classification | L3_APPLICATIONS |

**TCP status:** All 10 nav files have TCP markers (T0 frontmatter + T1:END + T2:END). Completed in Wave 3 (W3.3).

## 8. Maturity Assessment

Current: **2/10**

| Criterion | Score | Gap |
|-----------|:-----:|-----|
| Schema enforcement | 0 | No formal schema for intelligence files |
| Deduplication | 1 | Multiple overlapping indices (LOL, LOL_UNIFIED, LOL_SMOC) |
| Navigation | 3 | META_REGISTRY exists but not enforced |
| Bootstrap protocol | 5 | KERNEL.md works but undocumented layering |
| Context injection | 4 | Router exists but limited to dashboard |
| TCP coverage | 4 | All 10 nav docs + repository_history.md have markers |
| Theory linkage | 3 | Nav docs reference theory but not formally |
| Agent coordination | 2 | Agent-specific bootstraps exist but diverge |
| Quality control | 4 | Skeptical audits exist, not automated |
| Freshness tracking | 1 | No staleness detection |

### Path to 5/10 (Wave 2-3 Target)

1. Enforce intelligence file schema (proposed in §4.4)
2. TCP markers on all 10 nav docs (W3.3)
3. Deduplicate LOL variants
4. Automate staleness detection for intelligence files
5. Formalize bootstrap protocol documentation

## 9. Cross-References

- **Codome (body):** `particle/` — see `.agent/CODOME_MANIFEST.yaml`
- **Concordance (alignment):** `wave/tools/ai/boundary_analyzer.py`
- **Theory (axioms):** `particle/docs/theory/foundations/`
- **Glossary:** `particle/docs/GLOSSARY.yaml` (term: `contextome`)
- **Repository audit:** `docs/repository_history.md` (Sections 8-12)

## 10. Theory Split Rationale (wave/ vs particle/)

Theory content is deliberately split across hemispheres. This is not duplication
— it reflects the Trinity Principle's MECE separation of concerns.

### Canonical Formal Theory: `particle/docs/theory/`

The **definitive, reviewed** Standard Model theory:

```
particle/docs/theory/
├── THEORY_INDEX.md              (235 lines, canonical index)
├── foundations/
│   ├── L0_AXIOMS.md             Foundational truths
│   ├── L1_DEFINITIONS.md        What exists (atoms, dimensions, levels)
│   ├── L2_PRINCIPLES.md         How it behaves (laws)
│   └── L3_APPLICATIONS.md       How it is measured
├── frameworks/                  8 mathematical backing theories
├── synthesis/                   Integration and gap analysis
└── whitepapers/                 Academic positioning
```

This is what agents and documentation should reference as ground truth.
Cross-references in implementation files use `# Theory: L1_DEFINITIONS.md SS3.2` format.

### Exploration Drafts: `wave/docs/theory/`

Historical and exploratory theory content (20 files):

- **HISTORICAL** drafts: Original unified `THEORY.md` (4,368 lines), earlier integration notes
- **ACTIVE** unique content: TRINITY_PRINCIPLE, DUALITY_PRINCIPLE, CONTAINMENT_TOPOLOGY,
  OPTIMAL_SUBDIVISION_PRINCIPLE, ORPHAN_SEMANTICS — not yet promoted to particle/ canon
- **SUPERSEDED** files: Clearly marked with pointers to replacements

See [`wave/docs/theory/THEORY_INDEX.md`](../wave/docs/theory/THEORY_INDEX.md) for full inventory.

### Theory-Adjacent Content: `wave/docs/` root

Operational documents with theoretical grounding:

| File | Size | Content |
|------|------|---------|
| `CODESPACE_ALGEBRA.md` | 55KB | Algebraic formalization of code space |
| `CONCORDANCES.md` | 8KB | Concordance theory (replaces DOMAIN_DEEP_ANALYSIS) |
| `GLOSSARY.md` | 22KB | Wave-side glossary (see also particle/docs/GLOSSARY.yaml) |
| `PROJECTOME.md` | 6.5KB | Codome + Contextome = Projectome concept |
| `TOPOLOGY_MAP.md` | 7.7KB | System topology visualization |
| `COLLIDER_ARCHITECTURE.md` | 11KB | Collider design from wave perspective |

### The Rule

**Never move files across the hemisphere boundary.** Instead:

1. Keep particle/ as canonical formal theory — versioned, tested, cross-referenced
2. Keep wave/ as exploration space — drafts, research, integration notes
3. When wave/ content matures, **promote** it to particle/ (copy + formalize, then mark wave/ version SUPERSEDED)
4. Cross-reference with relative links across hemispheres
5. Both THEORY_INDEX files point to each other

---

*Source: Structural audit Section 8 (Observer subsystem), Section 12 (Contextome assessment)*
*See also: [CONCORDANCE.md](nav/CONCORDANCE.md) for code-doc alignment theory*

<!-- T2:END -->
