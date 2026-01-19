# Implementation Roadmap — “Repo → Components → Dependencies → Report”

This roadmap is aligned to the project Definition of Done:

1) A universal component taxonomy that covers >95% of components in >95% of repos, plus a robust fallback for unknowns  
2) A directory scanner that outputs components + stable IDs + internal/external dependencies  
3) A Markdown report + Mermaid diagram  
4) A way to provide LLMs the “atoms → molecules → organelles” mental model (architecture-first thinking)

---

## Current Baseline (Evidence in Workspace)

- Repo scanning + typed components + stable IDs + dependency counts: `spectrometer_v12_minimal/core/report_generator.py`
- Markdown + Mermaid output: `spectrometer_v12_minimal/output/report.md`
- Dependency analyzer (Python + JS/TS): `spectrometer_v12_minimal/core/dependency_analyzer.py`
- Known-architecture evaluation harness (1 real fixture): `spectrometer_v12_minimal/validation/run_known_arch_suite.py`
- 1440 RPBL dataset validation: `tools/validate_subhadron_dataset.py`
- 384 subhadron canvas snapshot + mismatch report:
  - `tools/extract_subhadrons_from_canvas.py`
  - `spectrometer_v12_minimal/validation/384_42_consistency_report.md`

Key gap to resolve: taxonomy/canon drift (22 particle types vs 96 hadrons vs 384/42 vs 1440 truth table).

---

## Phase 0 — Canonicalize Assets (Stop Drift)

**Goal:** one source of truth for taxonomy + rules, machine-readable, versioned.

- Decide “what is a component” at each level:
  - L0 repo assets (docs/config/build/infra)
  - L1 symbols (classes/functions/modules)
  - L2 roles (Controller/Entity/Repository…)
  - L3 subroles / subhadrons (384) + impossibles (42)
- Canonicalize 384/42 semantics:
  - Separate **hard impossible (42)** from **smell/anti-pattern** (additional “antimatter” currently present in the canvas)
  - Produce canonical `subhadrons_384.csv/json` + `impossible_42.csv/json` from a single ruleset
- Define explicit mappings:
  - `particle_type (v12)` → `hadron_subtipo (96)` (many-to-one or one-to-many, but explicit)
  - `hadron_subtipo (96)` → allowed RPBL cells (from `1440_csv.csv`)

**Exit criteria:** all engines reference the same canon files; reports include canon version/hash.

---

## Phase 1 — Universal Extraction (Multi-language, Deterministic)

**Goal:** extract a consistent component list across languages with minimal false positives.

- Replace regex-first parsing with AST-first parsing:
  - Tree-sitter for multi-lang structure
  - Language-specific fallbacks where needed (Python `ast`, JS/TS parser)
- Emit a stable “component record” schema:
  - `component_id`, `kind`, `name`, `path`, `span`, `language`
  - `type` (taxonomy label) + confidence + rule trace
  - `unknown_reason` when unclassified (what signal was missing)

**Exit criteria:** on a mixed-language repo, emits stable components with <5% “obvious misses” on manual spot-check.

---

## Phase 2 — Dependency Graph + Boundary Reasoning

**Goal:** produce internal cross-dependencies + external dependencies (packages) and reason about boundaries.

- Internal dependency edges:
  - import edges (module → module)
  - symbol edges (function/class → used symbols) where feasible
- External dependencies:
  - package imports grouped by ecosystem (pip/npm/go modules/etc.)
- Boundary validation:
  - detect “domain imports infra” and other layer violations when architecture inferred/known

**Exit criteria:** graph export in JSON + a Mermaid view that is stable across runs.

---

## Phase 3 — Reporting (Markdown + Mermaid + Actionability)

**Goal:** make output usable for humans and LLMs.

- Markdown report sections:
  - component inventory (typed + unknown)
  - dependency summary (internal + external)
  - boundary violations + “impossible 42” detections
  - “next best questions” (where unknowns cluster)
- Mermaid diagram layers:
  - repo → groups (domain/usecase/infra/presentation/etc.)
  - edges weighted by dependency count

**Exit criteria:** one command outputs a report that a human can use to orient in <10 minutes.

---

## Phase 4 — Benchmark Suite (Known Architecture Pre-check)

**Goal:** your method must be testable against repos with known ground-truth architecture.

- Build/maintain a local benchmark set (offline-friendly):
  - a few **real** repos (like `dddpy_real`) + **synthetic** fixtures (tiny but strict)
  - each fixture ships with a `known_architecture/*.json` spec
- Metrics:
  - typing precision/recall per component family
  - “unknown rate” and clustering quality
  - dependency edge accuracy (import-level at minimum)

**Exit criteria:** automated suite run with trendable metrics and regression checks.

---

## Phase 5 — LLM Mental Model Packaging (Atoms → Molecules → Organelles)

**Goal:** make LLMs reason in architecture blocks, not raw code.

- Provide a compact “architecture context pack”:
  - taxonomy glossary + examples
  - repo’s component inventory + dependency graph summary
  - unknown clusters with representative evidence
- Provide prompting + tool protocol:
  - “explain repo as atoms/molecules/organelles”
  - “propose refactor while preserving boundaries”
  - “map unknown cluster to closest hadron/subhadron candidates”

**Exit criteria:** repeated LLM sessions converge to stable, correct architecture descriptions with fewer hallucinations.

