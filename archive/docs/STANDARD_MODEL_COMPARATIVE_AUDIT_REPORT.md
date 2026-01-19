# Standard Model — Comparative Audit Report (Current State)

This is an **audit of the Standard Model system as it exists in this workspace**, using several external lenses (DDD/Clean/Hex/C4/static analysis). It focuses on internal consistency, falsifiability, and what must change to reach the project DoD.

Primary architecture snapshot (what we are auditing): `STANDARD_MODEL_ARCHITECTURE_AUDIT.md`

---

## 1) Executive Summary

### What’s strong (already “real”)
- You have an end-to-end **repo scanning pipeline** that outputs a component inventory + stable IDs + Markdown+Mermaid (`spectrometer_v12_minimal/output/report.md`).
- You have a working concept of a **purpose map** (RPBL) that is correctly treated as a coordinate space (`1440_csv.csv`).
- You have a functioning **known-architecture evaluation harness** (one fixture) that can measure correctness in a falsifiable way (`spectrometer_v12_minimal/validation/run_known_arch_suite.py`).
- You preserve **Unknown/unclassified** instead of dropping it, which is essential for iterative taxonomy evolution (`spectrometer_v12_minimal/core/report_generator.py`).

### What’s blocking “Standard Model worthy” right now
- **Canon drift**: multiple competing catalogs exist (96 roles vs 22 engine types vs 66 canvas types).
- **“Impossible” semantics are unstable**: the canvas marks 239 “antimatter” archetypes, which can’t be reconciled with “42 impossibles” unless you split hard forbidden vs soft smells.
- **Parsing reality**: current extraction is regex-first; generalization beyond convention-heavy repos is not proven.
- **Benchmarks are too small**: one “known architecture” fixture is not enough to claim universality.

Bottom line: the architecture is promising but currently **under-specified at the canon layer** and **over-loaded at the “antimatter” layer**.

---

## 2) Evidence-Based Consistency Checks (Numbers That Matter)

### 2.1 RPBL is a purpose map (good)
- RPBL grid size is fixed by definition: `12 × 4 × 6 × 5 = 1440`.
- The checked-in dataset contains **3888** hadron-specific rows, and validates cleanly: `spectrometer_v12_minimal/1440_summary.json`.

### 2.2 Role catalog vs implementations (not aligned)
Using `1440_csv.csv` as a canonical “96 roles present” list:
- **Roles present:** 96 (from `hadron_subtipo`)
- **V12 Minimal engine types:** 22 (`spectrometer_v12_minimal/patterns/particle_defs.json`)
- **Overlap between engine types and 96 roles:** 8 (`AggregateRoot`, `DTO`, `Entity`, `EventHandler`, `Factory`, `Projection`, `ReadModel`, `ValueObject`)

Implication:
- The current engine’s taxonomy is **not a strict subset** of the 96-role catalog (it introduces types like `UseCase`, `Service`, `Policy` that are not in the 96-role dataset).

### 2.3 Archetype catalog (canvas) is not “96 × 4”
From the canvas snapshot:
- Total archetypes extracted: **384**
- Unique `Type:` values: **66**
- Only **2 types** have exactly 4 archetypes (so it’s not “4 per role”).

Implication:
- The “384 = 96×4” framing is not reflected in the current artifact set; 384 exists as a curated catalog, but not distributed evenly by role.

### 2.4 “Impossible” is currently a superset (hard + soft mixed)
- Canvas marks **239** as antimatter.
- Only **51/239** antimatter items fall inside the scope of the v1 constraint set (L1–L11 types).

Implication:
- The current “antimatter” label is functioning as a **general smell flag**, not a strict “hard impossible” catalog.

---

## 3) Comparative Audit Lenses

### 3.1 DDD (Tactical + Strategic)
**Where you match well**
- Tactical vocabulary exists (Entity/ValueObject/AggregateRoot/Repository/Events, etc. appear across assets).
- Boundary dimension in RPBL is compatible with DDD layer thinking (Domain vs Application vs Infrastructure vs Interface).

**What’s missing**
- Strategic DDD: bounded context identification and context map inference are not yet first-class outputs.
- Tactical semantics: you don’t (yet) prove “Entity has identity” or “ValueObject is immutable” semantically; you infer mostly by naming/path.
- Domain events and invariants are not extracted as graph facts (they appear as concepts, not as computed evidence).

**Audit verdict**
- Good conceptual alignment; implementation still needs semantic extraction to be DDD-auditable.

### 3.2 Clean Architecture / Hexagonal / Ports & Adapters
**Where you match well**
- RPBL `Boundary` axis mirrors Clean/Hex layers (Domain/Application/Infrastructure/Interface/Test).
- Dependency rules can be expressed in your model (“domain should not import infrastructure”).

**What’s missing**
- Actual detection of ports/adapters and enforcement of dependency direction is incomplete (imports only, limited symbol reasoning).
- Mode detection is missing: not every repo is layered; constraints must be conditional.

**Audit verdict**
- Excellent target fit; needs a rule engine + architecture-mode detection to avoid false positives.

### 3.3 C4 Model (Context / Container / Component / Code)
**Where you match well**
- Your current outputs are naturally C4 “Component” and “Code” level artifacts (typed inventory + edges + evidence).

**What’s missing**
- Container boundaries (process/runtime deployables) are not robustly inferred across ecosystems.
- System context boundaries (people/external systems) are not represented unless you add explicit artifact signals (docs, configs, infra manifests).

**Audit verdict**
- You have the foundations for C4 “component diagrams”, but container/context needs explicit artifact modeling.

### 3.4 Static analysis / architecture recovery literature
**Where you match well**
- Import graphs + external dependency summaries are a valid “minimum viable” recovery signal.
- Unknown retention is aligned with iterative ontology refinement.

**What’s missing**
- Call graphs / symbol resolution where imports don’t encode dependency direction (DI, reflection, runtime wiring).
- Explainability traces: you don’t yet emit “which rule fired” per classification as structured data.

**Audit verdict**
- You are at “import-level recovery”; to be competitive, you need rule traces and partial symbol graphing.

### 3.5 Code smell frameworks
**Where you match well**
- The canvas antimatter reasons clearly overlap with smell detection (“DTO must be anemic”, “controller has domain logic”, “security risk”).

**What’s missing**
- A separation between “forbidden by law” vs “smell with severity”.
- A benchmarked, precision-first approach to smells (otherwise you’ll drown users in flags).

**Audit verdict**
- Smell detection is already implicitly present; it just needs formal separation and severity semantics.

---

## 4) High-Risk Misalignments (What might be wrong)

1) **Flat-list ontology mixing abstraction levels**  
Atoms (Assignment/Return) + organelles (CQRS/Outbox/Canary) are mixed without an explicit hierarchy. This makes “coverage” claims ambiguous.

2) **Taxonomy drift across artifacts**  
96-role catalog, 22-engine types, and 66-canvas types are not the same vocabulary; without a mapping, you can’t measure coverage or correctness consistently.

3) **“Antimatter” overload**  
Using one label for “hard impossible” and “soft smell” makes the system non-auditable: it breaks count stability and traceability.

4) **Evaluation tautology risk**  
If both truth and detector use the same signal (folder names), scores can be perfect without semantic understanding.

5) **Misleading module naming**  
If a component is called “tree_sitter_engine” but behaves as regex-first extraction, audits will assume AST semantics that are not present.

---

## 5) What’s Missing (To Reach the DoD)

### 5.1 Canon unification (non-negotiable)
- One machine-readable **Role Catalog** (96 or whatever it becomes).
- One machine-readable **Archetype Catalog** (N, versioned).
- One machine-readable **Constraint Catalog** split into:
  - **Hard constraints** → forbidden archetypes (M-hard)
  - **Soft constraints** → smells (M-soft, severity-ranked)
- One explicit **mapping layer** between catalogs.

### 5.2 Extraction upgrades
- AST-first parsing (Tree-sitter or language ASTs) for symbol extraction.
- Rule traces per classification (why it was typed, what evidence).
- Unknown clustering (so “unclassified” becomes a backlog of candidate new roles/archetypes).

### 5.3 Benchmark suite
- Multiple known-architecture fixtures across languages and architectures.
- Independence: truth specs must not share the same signals as detectors.

---

## 6) Recommended Restructure (Minimal, but Correct)

Rename the system artifacts as versioned catalogs:
- **Role Catalog** (roles you want to recognize; target high coverage)
- **Archetype Catalog** (named patterns of interest; size is not fixed)
- **Constraint Catalog** (hard + soft)
- **Forbidden Catalog** (derived from hard constraints)
- **Smell Catalog** (derived from soft constraints)
- **RPBL Purpose Map** (fixed coordinate space)

And keep the operational model hierarchical:
- **Atoms → Molecules → Organelles** (so “coverage” can be measured consistently).

This restructure is already captured as a canon doc: `STANDARD_MODEL_STRUCTURE.md`.

---

## 7) Audit Questions (Answerable by Evidence)

1) Which catalog is the “truth” for role names: `HADRONS_96_FULL.md` or `1440_csv.csv`? If both, what is the canonical mapping when they disagree?
2) Do you want “forbidden” to mean **logical impossibility** or **strong dispreference**? If both, what is the label split and severity model?
3) What architecture modes exist (CQRS/DDD/FP/Event-sourcing/etc.) and which constraints are conditional on each mode?
4) What is the measurement definition of “95% coverage”: per file, per symbol, per LOC, or per “developer mental model” components?
5) What is the minimum “dependency truth” you require: import edges only, or symbol/call edges?
6) What’s the smallest benchmark suite that would convince a skeptical architect (5 repos? 10? across which languages)?

