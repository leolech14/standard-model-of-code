# Standard Model Audit — Responses, Corrections, Decisions (Working)

This document captures **audit responses** (including third‑party/Grok-style feedback) and converts them into:
- **falsifiable statements** (what is true/unknown today)
- **corrections** (what the repo evidence shows)
- **decisions** (what we must decide to stabilize the model)
- **next actions** (what to build next)

Primary references:
- Architecture snapshot: `STANDARD_MODEL_ARCHITECTURE_AUDIT.md`
- Reframed canon sets: `STANDARD_MODEL_STRUCTURE.md`
- Comparative audit: `STANDARD_MODEL_COMPARATIVE_AUDIT_REPORT.md`
- Canon vs implementation matrix: `GAP_ANALYSIS_MATRIX.md`

---

## 0) Current Readiness (DoD)

**Not ready for the DoD** (universal building blocks + dependency graph + markdown/mermaid + LLM mental model).

Evidence:
- Canon roles: 96; engine types: 22; direct overlap: 8; canon missing in engine: 88 → `GAP_ANALYSIS_MATRIX.md`
- Archetype snapshot exists (384), but “antimatter” is overloaded (239) and not aligned with a stable forbidden set → `spectrometer_v12_minimal/validation/384_42_consistency_report.md`
- Known-architecture validation suite exists but only has **one** fixture → `spectrometer_v12_minimal/validation/run_known_arch_suite.py`

**Ready for auditing + iteration** (the artifacts and checks exist, but the canon is not unified).

---

## A) Definitions / Ontology

### A1) What is the minimum unit we claim to “cover”?
**Decision required:** pick a primary coverage unit for the DoD.

Recommended model (3 layers):
- **Artifacts** (files/config/infra) → “what runs”
- **Symbols** (classes/functions/modules) → “what is implemented”
- **Roles** (typed components) → “what it means”

**Correction:** today, the implementation mostly extracts a subset of symbols (top-level class/function definitions) and a small role set; artifact coverage is partial.

### A2) Are we mixing abstraction levels?
**Yes.** The 96 list mixes low-level syntax atoms (e.g., `Assignment`) with high-level org/exec roles (e.g., `ChaosMonkey`).

**Decision required:** make the catalog hierarchical:
`family → role → subtype` and explicitly label each role as `atom|molecule|organelle`.

---

## B) Purpose Map (RPBL)

### B1) Do the 4 RPBL dimensions fully describe “purpose”?
**They describe a useful slice of purpose**, but not all audit‑relevant properties across ecosystems.

Third‑party suggestion often raised:
- add dimensions for concurrency, consistency, security, etc.

**Recommendation (sequencing):**
1) First, stabilize canon + extraction using the existing 4D RPBL map.
2) Only then consider adding a **separate** “qualities” layer (NFRs) instead of expanding RPBL immediately (to avoid combinatorial explosion).

### B2) Should RPBL be scoring-only or also clustering?
**It should also support clustering** (grouping components into architecture regions), but that is not implemented today.

---

## C) Constraints / Forbidden vs Smells

### C1) Hard vs soft is currently mixed
Current reality:
- v1 constraints list exists (11) → `spectrometer_v12_minimal/LAW_11_CANONICAL.json`
- archetype snapshot marks 239 antimatter reasons (many are “smells”, not hard impossibilities) → `spectrometer_v12_minimal/validation/subhadrons_384_from_canvas.md`

**Decision required:** formal split:
- **Forbidden** (hard constraints): must be traceable to constraint IDs
- **Smells** (soft constraints): severity-ranked, not counted as “impossible”

### C2) CQRS / DDD constraints must be mode-scoped
**Correction:** applying CQRS constraints globally will create false positives.

**Decision required:** architecture mode detection (or opt-in flags):
- `mode=cqrs|ddd|clean|hex|unknown`
- constraints apply only when mode is active (or probability > threshold)

---

## D) Detection / Explainability

### D1) Minimum evidence per role must be explicit
**Missing today:** per-role evidence thresholds and rule traces.

**Action:** emit a `rule_trace` for every classification:
- `rule_id`, `features`, `evidence`, `confidence_inputs`

### D2) Biggest false-positive drivers
Known risks (also noted by third-party audits):
- path conventions shared by truth and detector (tautology risk)
- naming collisions and “semantic” labels from suffixes
- generated code

---

## E) Dependency Graph / Architecture Recovery

### E1) Import-only graphs are a good baseline, not sufficient
**Correction:** import graphs miss DI wiring, reflection, and runtime call paths.

**Decision required:** define the minimum viable dependency truth:
- v1: import graph + package deps (fast, robust)
- v2: symbol reference graph (selective, language-dependent)

---

## F) Benchmarks / Validation

### F1) “95% of 95%” needs operational definitions
**Decision required:** choose measurement:
- coverage by symbols? by LOC? by files? by “developer-relevant components”?

### F2) Evaluation independence
**Missing today:** diverse fixtures with truth not derived from the same signals as the detector.

**Action:** add 5–10 fixtures across languages + styles; truth specs should be independent of folder naming.

---

## G) Output / UX / LLM Integration

### G1) Report usefulness
Current report (`spectrometer_v12_minimal/output/report.md`) already helps, but lacks:
- rule traces (“why”)
- architecture mode statement
- smell vs forbidden separation

### G2) “Context pack” for LLMs
Minimum pack should include:
- typed component inventory + unknown clusters
- dependency summary
- constraints triggered (forbidden vs smells)
- RPBL placements (scores/coordinates)

---

## Decisions Checklist (What we must decide next)

1) Canon structure: keep “96 roles” as fixed, or let it evolve (recommended: versioned role catalog).
2) Role hierarchy: `atom|molecule|organelle` labeling + parent/child relations.
3) Constraint split: forbidden vs smells (and severity model).
4) Architecture modes: how we detect/declare them.
5) Dependency truth level: import-only vs symbol graph.
6) Coverage metric: how we compute “95%”.

---

## Next Actions (High ROI, Ordered)

1) **Unify vocabulary**: mapping file between engine types ⇄ role catalog ⇄ RPBL dataset.
2) **Expand extraction downwards** (atoms): detect variables/assignments/calls/branches/loops/try-catch so “physics signals” exist.
3) **Expand extraction upwards** (artifacts/runtime): Dockerfile, K8s YAML, CI, entrypoints, config loaders.
4) **Split antimatter**: forbidden (hard constraints) vs smells (soft).
5) **Benchmark suite**: add 5–10 known-architecture fixtures and trend metrics.

