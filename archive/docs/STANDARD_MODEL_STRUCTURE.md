# Standard Model of Code — Canon Sets (Reframed)

This project originally used a clean numeric hierarchy (11 / 12 / 96 / 384 / 42 / 1440). The workspace evidence now makes it clear we need a **more truthful structure**:

- **Catalog sizes are not sacred** (laws, archetypes, impossibles can grow/shrink).
- **`1440` is a purpose/coordinate map**, not “1,440 code entities”.
- “Impossible” needs a split between **hard impossibility** vs **soft smells**.

This doc defines the model in a way that stays correct even as counts change.

---

## 1) Entities vs Maps (critical)

### Entities (things that exist in a codebase)
- **Artifacts**: files, directories, manifests, configs, tests, docs.
- **Symbols**: modules/packages, classes/types, functions/methods, fields/vars.
- **Edges**: imports, references, calls (at minimum: import edges).

### Maps (ways to describe purpose/physics)
- **RPBL purpose space**: `Responsibility × Purity × Boundary × Lifecycle`.
  - Grid size is fixed: `12 × 4 × 6 × 5 = 1440`.
  - A component can be **placed onto** this map (scored), but the cells are not “components”.

Canonical data: `1440_csv.csv`

---

## 2) Canon Sets (new names, flexible counts)

| Old name | New name | What it is | Current evidence in repo |
|---|---|---|---|
| “Laws (11)” | **Constraints** | Rules that define *hard impossibility* or *soft violations* | v1 set: `spectrometer_v12_minimal/LAW_11_CANONICAL.json` |
| “Hadrons (96)” | **Role Catalog** | Universal-ish component roles we want to recognize | `HADRONS_96_FULL.md` (canon list) |
| “Subhadrons (384)” | **Archetype Catalog** | Named role+purpose patterns we care about (size can change) | Canvas snapshot: `spectrometer_v12_minimal/validation/subhadrons_384_from_canvas.csv` |
| “Impossible (42)” | **Forbidden Archetypes** | The hard-impossible subset, justified by constraints | Skeleton: `spectrometer_v12_minimal/IMPOSSIBLE_42_CANONICAL.csv` |
| “1440 grid points” | **RPBL Purpose Map** | Coordinate system for describing a role/archetype | Summary: `spectrometer_v12_minimal/1440_summary.json` |

Important: today the canvas “ANTIMATTER” marking is a **superset** of the strict-42 target: see `spectrometer_v12_minimal/validation/384_42_consistency_report.md`.

---

## 3) The three-level “minimal pieces” model (Atoms → Molecules → Organelles)

This is the practical structure for repo reverse-engineering.

### Atoms (syntax + flow primitives)
Language-agnostic, low-level, high coverage:
- literals, identifiers, assignments, calls, returns
- branching, loops, exceptions/try-catch

### Molecules (program structure)
Still mostly language-agnostic:
- module/package, class/type, function/method
- config/test/source files

### Organelles (architecture roles)
Inferred from evidence:
- boundary handlers (API/CLI/Controller), orchestration (UseCase/Service)
- domain models (Entity/ValueObject/Aggregate), infra (Repository/Adapter)
- runtime concerns (Worker/Consumer/Scheduler), ops (Health/Metrics/Tracing)

The **Role Catalog** should mostly live here, while Atoms/Molecules ensure we still cover “everything else” when roles are ambiguous.

---

## 4) How “Impossible” should work (to stay stable)

To avoid drifting counts:

- **Hard Impossible**: violates a *constraint* that is intended to be axiomatic for a detected architecture mode (e.g., CQRS mode). These populate **Forbidden Archetypes**.
- **Soft Smell**: undesirable but not logically impossible. These should be tracked as **smells** with severity, not merged into the Forbidden set.

---

## 5) What “recounting” looks like (today, in this workspace)

- RPBL purpose grid: **1440 cells** (map, not entities): `spectrometer_v12_minimal/1440_summary.json`
- RPBL dataset rows: **3888** (hadron-specific allowed cells): `1440_csv.csv`
- Role canon list: **96** (doc-canon): `HADRONS_96_FULL.md`
- V12 Minimal engine types: **22**: `spectrometer_v12_minimal/patterns/particle_defs.json`
- Archetype snapshot (canvas): **384** nodes; “antimatter” marked: **239**: `spectrometer_v12_minimal/validation/subhadrons_384_from_canvas.md`
- Constraint v1 list: **11**: `spectrometer_v12_minimal/LAW_11_CANONICAL.json`
- Forbidden archetype skeleton: **42 target**, **16 confirmed**: `spectrometer_v12_minimal/IMPOSSIBLE_42_CANONICAL.csv`

