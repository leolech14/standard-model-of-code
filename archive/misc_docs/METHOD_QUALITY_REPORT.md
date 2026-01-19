# Method Quality Report — Repository → Component Typing → Reverse Engineering

This report evaluates the **current, evidenced quality** of the project’s method for mapping a repository into our component taxonomy (hadrons/particles/types) to support reverse‑engineering against **known architecture ground truth**.

It is intentionally strict: claims are marked as **validated** only when we executed tooling and produced artifacts in this workspace.

---

## 1) What the “method” is (as implemented today)

There are multiple “engines” in this workspace. Two are most relevant to repo → component typing:

### A) V12 Minimal (universal detector, current active path)
- **Goal:** fast, deterministic extraction of “particles” + touchpoints + RPBL scoring.
- **Implementation reality:** despite the name, `spectrometer_v12_minimal/core/tree_sitter_engine.py` is currently **regex-based scanning**, not Tree-sitter AST parsing.
- **Taxonomy actually emitted:** currently **~20 particle types** (see `spectrometer_v12_minimal/patterns/particle_defs.json`), not the full “96 hadrons” catalog.
- **Outputs:** JSON + stats + CSV under `spectrometer_v12_minimal/output/`.

### B) v4 Hadron classifier (Python AST, limited scope)
- `spectrometer_hadrons_engine.py` implements a larger 96-hadron catalog in code and uses Python `ast` for signals.
- It currently analyzes **Python-only** repos (`*.py`).

---

## 2) What we validated (hard evidence)

### 2.1 A known-architecture benchmark: `dddpy_real` (Onion/DDD + FastAPI)
We used the local repository at:
- `spectrometer_v12_minimal/validation/dddpy_real`

We defined ground truth as a spec:
- `spectrometer_v12_minimal/validation/known_architectures/dddpy_real_onion_v1.json`

This spec labels **top-level classes** by architecture convention (domain/usecase/presentation/infrastructure) and type family:
- `Entity`, `ValueObject`, `Repository`, `RepositoryImpl`, `UseCase`, `Controller`, `DTO`

### 2.2 Validation harness (new)
We added a validator that compares predicted component typing vs the known-architecture spec:
- `spectrometer_v12_minimal/validation/validate_known_architecture.py`

And a suite runner:
- `spectrometer_v12_minimal/validation/run_known_arch_suite.py`
- `spectrometer_v12_minimal/validation/known_architectures/README.md`

### 2.3 Result (V12 Minimal on `dddpy_real`)
The run produced:
- Predictions: `spectrometer_v12_minimal/output/results.json` and `spectrometer_v12_minimal/output/particles.csv`
- Validation report: `spectrometer_v12_minimal/validation/known_architectures/dddpy_real_onion_v1.report.json`

Observed metrics (from the report JSON):
- expected_total=30
- predicted_total=30
- correct_total=30
- missed_total=0
- wrong_total=0
- extra_total=0
- accuracy_on_expected=1.0

Per-type precision/recall:
- Controller: recall=1.0, precision=1.0
- DTO: recall=1.0, precision=1.0
- Entity: recall=1.0, precision=1.0
- Repository: recall=1.0, precision=1.0
- RepositoryImpl: recall=1.0, precision=1.0
- UseCase: recall=1.0, precision=1.0
- ValueObject: recall=1.0, precision=1.0

**Validated conclusion:** For this specific repo (with conventional folder layout), V12 Minimal can label these component families correctly.

---

## 3) What this validation *does* and *does not* prove

### What it proves (high confidence)
- **Reproducible mapping** from a repo to component labels **when the architecture is expressed via conventional directory structure**.
- The detector emits machine-readable output (CSV/JSON) suitable for downstream “reverse engineering” tooling.
- The evaluation harness works (spec → expected labels → scored report).

### What it does NOT prove (yet)
- **Semantic correctness independent of path conventions.**
  - The detector currently uses strong **path-based heuristics** in `spectrometer_v12_minimal/core/tree_sitter_engine.py`.
  - The benchmark spec also labels by path. This means the evaluation is not fully independent.
- **Generalization** to different folder layouts or different DDD styles.
- **Generalization across languages.**
- **Full Standard Model coverage** (12 continents / 96 hadrons / 384 / 1440 mapping). V12 Minimal is not at 96-hadron parity.
- **Architectural relationship reconstruction** (dependencies, directionality, boundaries). Today we mostly do *typing*, not *graph extraction*.

---

## 4) Quality assessment by dimension

### 4.1 Correctness (component typing)
**Status:** strong on one benchmark, limited external validity.

Evidence:
- 100% precision/recall on the `dddpy_real` benchmark spec (`dddpy_real_onion_v1.report.json`).

Limitations:
- Path-based classification can fail if:
  - folders are named differently (`src/` + `app/` monolith)
  - layers are not represented in file paths
  - multiple bounded contexts are nested differently

### 4.2 Coverage (taxonomy breadth)
**Status:** currently **split-brain** between canon and engines.

- Canon list exists for **96 hadrons**: `HADRONS_96_FULL.md`
- V12 Minimal supports ~20 particle types:
  - `spectrometer_v12_minimal/patterns/particle_defs.json`
- v4 engine contains a large hadron catalog but is Python-only:
  - `spectrometer_hadrons_engine.py`
- The 384/42 layer currently exists as a **canvas snapshot**, but is not canonicalized:
  - `tools/extract_subhadrons_from_canvas.py` extracts 384 `sub_*` nodes from `THEORY_COMPLETE.canvas`
  - Current canvas marks **239** as antimatter (not the theory target 42): `spectrometer_v12_minimal/validation/384_42_consistency_report.md`

**Implication:** We can currently do reliable labeling for a *subset* of component families, but not full “96 hadrons” mapping via the V12 Minimal engine.

### 4.3 Robustness (noise tolerance / false positives)
**Status:** improving, but still heuristic-heavy.

Notable mitigation already applied:
- Python scanning now restricts to top-level `class` / `def` to avoid nested helper classes being mis-labeled (e.g., Pydantic inner `Config` classes).
  - Implemented in `spectrometer_v12_minimal/core/tree_sitter_engine.py`

Remaining risks:
- Regex-only parsing misses:
  - decorators/annotations (e.g., FastAPI route functions) beyond basic patterns
  - interface/implementation relationships
  - method semantics (mutations, I/O) unless strongly implied by names

### 4.4 Explainability (why a label was assigned)
**Status:** partial.

The detector emits:
- `evidence` (the matching line)
- a numeric `confidence` (currently simplistic)

But we do not yet emit:
- the exact rule fired (path rule vs naming tokens vs keyword detection)
- a structured explanation trace per classification

### 4.5 Reproducibility / determinism
**Status:** good locally.

- Runs are deterministic.
- Outputs are stable files.
- Benchmark evaluation produces a report JSON.

### 4.6 “Reverse engineering” readiness
**Status:** component typing is viable; architecture graph extraction is not yet complete.

What we can do now:
- Provide a list of typed components (class/function “particles”) with file locations.

What we still need for real reverse engineering:
- Dependency graph extraction (imports, calls, DI wiring)
- Boundary violation checks (e.g., domain importing infrastructure)
- Aggregation into architecture diagrams (C4-ish: contexts/modules/components)

---

## 5) Cross-check: v4 hadron engine on the same benchmark (sanity signal)

We also executed the v4 Python AST engine on the same repo (`dddpy_real`) and saved results:
- `spectrometer_v12_minimal/output/dddpy_v4_hadrons_results.json`

Observed:
- files_analyzed=42
- total_elements=114
- hadrons_found=7
- coverage=7.29% of the 96-hadron catalog

Interpretation:
- The v4 engine is currently **far from full 96-hadron coverage** on a real DDD repo.
- It may still be valuable for deeper semantic classification once expanded, but it is not “complete”.

---

## 6) Major threats to validity (what could fool us)

1) **Tautological evaluation**  
   If the benchmark truth and the detector both rely on the same signal (directory names), we can get perfect scores without true semantic understanding.

2) **Selection bias**  
   One benchmark repo is not representative of the diversity of real architectures.

3) **Taxonomy drift**  
   “Canon” docs and engine outputs are not fully synchronized (20 types vs 96 hadrons).

4) **Language bias**  
   The strongest benchmark currently is Python with a known folder layout.

5) **Ambiguity of definitions**  
   Without strict operational definitions (what makes something a ValueObject?), consistent labeling becomes subjective across languages/frameworks.

---

## 7) Recommendations (practical, high ROI)

### 7.1 Build a benchmark suite (minimum 5–10 known-architecture repos)
Target variety:
- Python: DDD/Onion, Clean, Django monolith
- TypeScript: NestJS Clean-ish
- Java: Spring Boot layered
- Go: Hexagonal / ports-adapters

For each, add a spec in:
- `spectrometer_v12_minimal/validation/known_architectures/*.json`

### 7.2 Make evaluation independent of folder layout
Add “semantic” checks per type, e.g.:
- Entity: has id/identity field + mutating behavior
- ValueObject: immutable + equality by value
- Controller: route decorators/annotations or HTTP handlers
- RepositoryImpl: performs I/O (DB client usage)

### 7.3 Implement real parsing (Tree-sitter / AST)
To support cross-language and reduce false positives, replace line-regex with:
- Tree-sitter queries (where available) or per-language AST parsing.

### 7.4 Unify taxonomy layers
Decide:
- Are we shipping “20 particle types” (component families), or “96 hadrons” (fine-grained particles)?
- If both, define a mapping table `particle_type → hadron` and keep it as a machine-readable canon.

### 7.5 Add architecture-graph output (dependencies + boundaries)
Reverse engineering needs:
- import graph
- call graph (approximate)
- layer violation detection
- output format: JSON graph + Mermaid generation

---

## 8) Bottom-line quality rating (today)

**For component typing on conventionally structured DDD/Onion repos:** **Good** (validated on `dddpy_real`).

**For general “reverse engineering” across arbitrary repos/languages:** **Not proven yet** (needs more benchmarks + semantic parsing + graph extraction).

**For full Standard Model (12/96/384/1440) coverage:** **In progress / incomplete** (canon exists, engine parity does not).
