# Standard Model — Current Architecture (Audit Doc)

Purpose: present the **current, evidenced architecture** of the Standard Model system in this workspace so it can be audited against other models (DDD/C4/Clean/etc.). This document is written to be falsifiable: it distinguishes **canon**, **snapshots**, and **implementations**.

Canonical reframing of the model’s “numbers”: `STANDARD_MODEL_STRUCTURE.md`

---

## 1) Scope

This audit doc covers:
- The current **canon sets** (roles, constraints, purpose map, archetypes)
- The current **pipeline** (repo → components → dependencies → report)
- Current **validation assets** and what they do/don’t prove

This audit doc does not attempt to:
- Prove universality claims (“95% of 95%”) without a benchmark suite
- Reconcile all legacy scripts (many are historical prototypes)

---

## 2) Core Principle: Entities vs Maps

### Codebase entities (things that exist)
- **Artifacts:** files/dirs/configs/manifests/docs/tests
- **Symbols:** modules/packages, classes/types, functions/methods, fields/vars
- **Edges:** imports/references/calls (minimum: import edges)

### Descriptive maps (ways to describe purpose/physics)
- **RPBL purpose space:** `Responsibility × Purity × Boundary × Lifecycle`
  - Fixed coordinate space size: `12 × 4 × 6 × 5 = 1440` cells
  - Cells are **not** “repo components”; components get **placed onto** the map

RPBL dataset: `1440_csv.csv`

---

## 3) Canon Sets (What is “the Standard Model” right now)

### 3.1 Role Catalog (legacy “96 hadrons”)
- Canon list (doc): `HADRONS_96_FULL.md`
- What it represents: a vocabulary of roles that should cover most repos when applied at the right abstraction level (atoms/molecules/organelles).

### 3.2 Constraints (legacy “11 laws”, v1)
- Canon list (machine-readable): `spectrometer_v12_minimal/LAW_11_CANONICAL.json`
- Human doc: `spectrometer_v12_minimal/LAW_11_CANONICAL.md`
- What it represents: rules that can justify **hard impossibility** (forbidden patterns) and/or detect strong violations.

Important architectural decision pending:
- Which constraints are **hard** (produce forbidden archetypes)
- Which constraints are **soft** (smells, severity-ranked)

### 3.3 Forbidden Archetypes (legacy “42 impossible”, skeleton)
- Skeleton catalog: `spectrometer_v12_minimal/IMPOSSIBLE_42_CANONICAL.csv`
- Mermaid: `spectrometer_v12_minimal/CANONICAL_MERMAIDS.md`
- Status: partially confirmed (16) + placeholders (26). Treated as a tracked catalog, not a sacred number.

### 3.4 Archetype Catalog (legacy “384 subhadrons”)
Current evidence in this workspace:
- `THEORY_COMPLETE.canvas` contains 384 `sub_*` nodes
- Extracted snapshot:
  - `spectrometer_v12_minimal/validation/subhadrons_384_from_canvas.csv`
  - `spectrometer_v12_minimal/validation/subhadrons_384_from_canvas.md`
- Consistency report: `spectrometer_v12_minimal/validation/384_42_consistency_report.md`

Critical observation:
- Canvas currently marks **239** archetypes as “ANTIMATTER DETECTED”, which is incompatible with the legacy “42 impossible” framing unless we split **hard forbidden** vs **soft smells**.

### 3.5 RPBL Purpose Map (1440)
Current evidence in this workspace:
- Summary: `spectrometer_v12_minimal/1440_summary.json`
- Validated report: `spectrometer_v12_minimal/validation/1440_dataset_report.md`

What it is:
- A purpose/physics coordinate map (1440 cells) + hadron-specific allowed cells (3888 rows).

---

## 4) Implementation Architecture (What actually runs)

### 4.1 Entry point
- CLI: `python3 spectrometer_v12_minimal/main.py <repo_path>` (`spectrometer_v12_minimal/main.py`)

### 4.2 Modules (V12 Minimal)

**Orchestrator**
- `spectrometer_v12_minimal/core/universal_detector.py`
  - Coordinates parsing, dependency analysis, typing, stats, and reporting.

**Parsing / extraction**
- `spectrometer_v12_minimal/core/tree_sitter_engine.py`
  - Despite the filename, this is currently **regex-first extraction**, plus AST parsing for imports in some languages (e.g., Python).
  - Supported language extensions are hard-coded.

**Typing / RPBL scoring**
- `spectrometer_v12_minimal/core/particle_classifier.py`
  - Loads a small type list and assigns RPBL scores from `spectrometer_v12_minimal/patterns/particle_defs.json` (22 types).
  - This is currently not synchronized with the 96-role catalog.

**Dependencies**
- `spectrometer_v12_minimal/core/dependency_analyzer.py`
  - Produces internal/external/stdlib dependency summaries (import-based, language-dependent).

**Stats + persistence**
- `spectrometer_v12_minimal/core/stats_generator.py`
  - Writes `results.json`, `stats.txt`, `particles.csv`.

**Reporting**
- `spectrometer_v12_minimal/core/report_generator.py`
  - Writes `report.md` (Markdown + Mermaid) and `components.csv` (stable IDs + per-file dependency counts).

### 4.3 Outputs (contract)
Produced under: `spectrometer_v12_minimal/output/`
- `results.json`: structured output + summary
- `particles.csv`: raw particles
- `components.csv`: stable IDs + file/line + dependency counts
- `report.md`: Markdown report + Mermaid architecture diagram

Key fallback behavior:
- Unknown components are retained as `type=Unknown` and surfaced with evidence in the report, enabling iterative taxonomy expansion instead of silent drops.

---

## 5) Validation Architecture (What we can test today)

### 5.1 Known-architecture suite (ground truth specs)
- Fixture repo: `spectrometer_v12_minimal/validation/dddpy_real`
  - Origin: `https://github.com/iktakahiro/dddpy` (stored as local fixture)
- Spec: `spectrometer_v12_minimal/validation/known_architectures/dddpy_real_onion_v1.json`
- Runner: `spectrometer_v12_minimal/validation/run_known_arch_suite.py`

Evidence:
- Suite currently passes 100% for this single fixture.

Threats to validity:
- This benchmark is not yet diverse, and both truth and detector may share similar signals (e.g., path conventions).

### 5.2 Repo targets used/mentioned for iterations
- Curated extraction of repos from context/testing files: `spectrometer_v12_minimal/validation/iteration_test_repos.md`

### 5.3 Canon vs implementation gaps
- Canon vs engine vs archetype snapshot reconciliation matrix: `GAP_ANALYSIS_MATRIX.md`

---

## 6) Audit Lenses (How to compare to other models)

Use these mappings to audit the Standard Model against other frameworks:

- **C4 Model**
  - “Components” ≈ our typed components grouped by folder/module boundaries
  - “Containers” ≈ inferred boundary groups (domain/usecase/infra/presentation) + runtime deployables
  - Gap: we don’t yet robustly infer container deployment boundaries across ecosystems

- **DDD Tactical Patterns**
  - Entities/ValueObjects/Aggregates/Repositories are present in the Role Catalog
  - Gap: we don’t yet compute invariants/events/aggregate boundaries semantically (regex/path-heavy)

- **Clean / Hexagonal**
  - Boundary dimension in RPBL is conceptually compatible (Domain/Application/Infra/Interface/Test)
  - Gap: automated detection of ports/adapters and dependency direction enforcement is incomplete

- **Architecture Recovery / Static Analysis**
  - Our dependency graph is currently import-based; deeper call graphs and symbol resolution are limited
  - Gap: rule traces / explainability (why a label fired) are not fully structured

---

## 7) Known Gaps / Risks (Audit-critical)

- **Taxonomy drift:** engine emits 22 types; canon lists 96 roles; archetypes exist as a canvas snapshot.
- **Hard vs soft violation confusion:** “ANTIMATTER” currently mixes strict forbidden patterns with smells.
- **Partial “continents” evidence:** RPBL dataset currently contains 5 macro-region names (`continente_cor`).
- **Parsing reality:** current extraction is regex-first; semantic correctness beyond conventions is not proven.
- **Benchmark scarcity:** only one known-architecture fixture is scored end-to-end.

---

## 8) How to Reproduce (Quick Commands)

- Run the detector on a local repo: `python3 spectrometer_v12_minimal/main.py <repo_path>`
- Run known-architecture suite: `python3 spectrometer_v12_minimal/validation/run_known_arch_suite.py`
- Validate RPBL dataset: `python3 tools/validate_subhadron_dataset.py`
- Extract archetypes from canvas: `python3 tools/extract_subhadrons_from_canvas.py`
- Reconcile 384 snapshot vs 42 skeleton: `python3 tools/validate_384_42_consistency.py`

---

## 9) Audit Questions (Designed to Trigger “What’s Missing / Wrong?”)

### A) Definitions / Ontology
- What is the minimum unit we claim to “cover”: artifacts, symbols, or roles?
- Which items in `HADRONS_96_FULL.md` are truly universal vs framework-specific?
- Are we mixing abstraction levels (atoms vs organelles) in a single flat list?
- Should the role catalog be hierarchical (family → role → subtype) instead of a flat 96?

### B) Purpose Map (RPBL)
- Do the 4 RPBL dimensions fully describe “purpose”, or are we missing dimensions (e.g., concurrency model, consistency, security)?
- Are the axis value sets correct and complete across ecosystems (backend/frontend/infra/data/ML)?
- Should RPBL be used for scoring only, or also for clustering components into architecture groups?

### C) Constraints / Forbidden vs Smells
- Which constraints are axiomatic (hard forbidden) vs best-practice (soft smell)?
- Should CQRS constraints apply globally, or only when the repo is in a detected “CQRS mode”?
- If forbidden patterns expand beyond 42, what invariants must still hold (traceability, single-law attribution, severity semantics)?
- Do we need constraint composition (multiple-law violations), and how would we present that to users?

### D) Detection / Explainability
- For each role, what is the minimum evidence required to classify it (AST features, naming, imports, annotations)?
- What are the biggest sources of false positives (path conventions, naming collisions, codegen)?
- Should we emit a “rule trace” per component (which detector fired and why) as a first-class output?

### E) Dependency Graph / Architecture Recovery
- Is import-based dependency sufficient for the architecture diagrams we want, or do we need symbol/call graphs?
- What is the smallest “good enough” dependency model that still supports boundary violation detection?
- How should we represent external dependencies: package-level, module-level, or symbol-level?

### F) Benchmarks / Validation
- What does “95% of components” mean operationally (by LOC? by symbols? by developer-perceived architecture blocks)?
- Which benchmark suite best reflects your target audience (web apps, libs, infra tools, ML stacks)?
- How do we ensure evaluation independence (truth not sharing the same signal as the detector)?

### G) Output / UX / LLM Integration
- Does `report.md` answer the first 3 questions a new engineer asks (“what is it?”, “where is the core?”, “what depends on what?”)?
- What is the minimal “context pack” needed for an LLM to reason architecture-first without hallucinating?
- How should unknown clusters be presented so a human can quickly extend the canon (new role/archetype/constraint)?

## 10) Audit Responses (Working)

- Consolidated responses + decisions + next actions: `STANDARD_MODEL_AUDIT_RESPONSES.md`
