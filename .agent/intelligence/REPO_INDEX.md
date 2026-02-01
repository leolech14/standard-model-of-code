# PROJECT_elements — Repository Index (Generated)

**Generated:** 2026-01-27
**Source snapshot:** `full_contextome.zip` (this pack is docs+registries+artifacts; it is *not* the full executable repo)

This index is meant to answer:

- *“What is in here?”* (filesystem map)
- *“Where are the entry points?”* (start docs)
- *“What should we separate / prioritize?”* (artifact vs canon)
- *“Why does it feel chain-like?”* (doc graph is sparse)

---

## Top-level structure

| path | files | MB | md | json | yaml |
|---|---|---|---|---|---|
| particle/ | 1496 | 951.20 | 643 | 824 | 29 |
| .agent/ | 321 | 3.23 | 73 | 34 | 214 |
| wave/ | 304 | 6.91 | 131 | 138 | 35 |
| archive/ | 208 | 8.00 | 159 | 44 | 5 |
| related/ | 4 | 0.01 | 1 | 3 | 0 |
| .claude/ | 3 | 0.00 | 2 | 1 | 0 |
| .collider-full/ | 3 | 71.50 | 0 | 3 | 0 |
| architecture_report/ | 3 | 15.59 | 0 | 3 | 0 |
| collider_output_small/ | 3 | 38.46 | 0 | 3 | 0 |
| .gemini/ | 2 | 0.00 | 2 | 0 | 0 |
| evolution_report/ | 2 | 0.24 | 0 | 2 | 0 |
| .pytest_cache/ | 1 | 0.00 | 1 | 0 | 0 |
| .vscode/ | 1 | 0.00 | 0 | 1 | 0 |
| roadmap_report/ | 1 | 0.00 | 0 | 1 | 0 |

### Quick read (what each top-level is)

- `particle/` — **“Body”**: Collider theory + specs + implementation *docs*, plus very large analysis artifacts.
- `wave/` — **“Brain”**: operational docs + tools + registries for context and AI workflows.
- `.agent/` — **“Observer”**: governance, decks, registries, emergency maps, and agent intelligence outputs.
- `archive/` — cold storage snapshots and legacy docs.
- `.collider-full/`, `collider_output_small/`, `architecture_report/` — generated scan outputs (JSON).
- `related/` — external dependency snapshots (e.g., chrome-mcp).

---

## Root entry points (what you should read first)

| file | title | bytes |
|---|---|---|
| AGENTKNOWLEDGEDUMP.md | Agent Knowledge Dump | 16116 |
| AGENTS.md | AGENTS – Intelligence Registry | 1217 |
| ARCHITECTURE_MAP.md | PROJECT_elements Architecture Map | 6115 |
| AUDIT_MANIFEST.md | PROJECT_elements - Theory Audit Manifest | 6651 |
| CLAUDE.md | PROJECT_elements | 2799 |
| DEEP_GHOSTS_REPORT.md | PROJECT_elements: Deep Ghosts Report | 9343 |
| GEMINI.md | PROJECT_elements | 1849 |
| PROJECT_MAP.md | Project Map: State of the Topology | 3008 |
| PROJECT_METADATA.md | PROJECT_elements - File Metadata | 158087 |
| QUICK_START.md | Quick Start | 689 |
| README.md | PROJECT_elements | 841 |
| orphans_report.md | Analysis Report: Orphaned Code Candidates | 17428 |
| validated_pipeline.md | Validated Semantic Map: PIPELINE | 2716 |
| validated_theory.md | Validated Semantic Map: THEORY | 270 |

---

## Subsystem maps

### `particle/` (Collider / Standard Model)

| name | files | MB | md | json | yaml |
|---|---|---|---|---|---|
| docs | 1096 | 12.60 | 520 | 575 | 1 |
| artifacts | 160 | 931.88 | 5 | 150 | 5 |
| .archive | 93 | 3.04 | 78 | 15 | 0 |
| tools | 44 | 1.11 | 4 | 40 | 0 |
| src | 35 | 1.65 | 12 | 10 | 13 |
| schema | 34 | 0.35 | 4 | 21 | 9 |
| data | 7 | 0.04 | 1 | 6 | 0 |
| research | 7 | 0.42 | 2 | 5 | 0 |
| .github | 3 | 0.00 | 3 | 0 | 0 |
| blender | 2 | 0.01 | 1 | 1 | 0 |
| AUDIT_INDEX.md | 1 | 0.01 | 1 | 0 | 0 |
| .bandit_output.json | 1 | 0.00 | 0 | 1 | 0 |
| README_HANDLER_AUDIT.md | 1 | 0.01 | 1 | 0 | 0 |
| HANDLER_COVERAGE_CORRECTED.md | 1 | 0.01 | 1 | 0 | 0 |
| CLAUDE.md | 1 | 0.01 | 1 | 0 | 0 |
| ARIADNES_THREAD.md | 1 | 0.01 | 1 | 0 | 0 |
| .pytest_cache | 1 | 0.00 | 1 | 0 | 0 |
| collider_pipeline.md | 1 | 0.00 | 1 | 0 | 0 |
| .pre-commit-config.yaml | 1 | 0.00 | 0 | 0 | 1 |
| CONTRIBUTING.md | 1 | 0.00 | 1 | 0 | 0 |
| ROADMAP.md | 1 | 0.01 | 1 | 0 | 0 |
| CHANGELOG.md | 1 | 0.00 | 1 | 0 | 0 |
| README.md | 1 | 0.02 | 1 | 0 | 0 |
| CONTROL_HANDLER_MAPPING.md | 1 | 0.01 | 1 | 0 | 0 |
| HANDLER_WIRING_AUDIT.md | 1 | 0.01 | 1 | 0 | 0 |

Notes:
- **The size is dominated by `artifacts/`** (hundreds of MB of JSON scans).
- `docs/` is where human-readable theory & usage lives.
- `schema/` and `src/` (in this snapshot) are mostly **docs/JSON/YAML**; the full codebase is likely *outside this pack* (see `PROJECT_METADATA.md`).

Key entrypoints inside `particle/`:
- `particle/README.md`
- `particle/docs/README.md`
- `particle/docs/MODEL.md`
- `particle/docs/COLLIDER.md`
- `particle/docs/specs/README.md`
- `particle/docs/reports/README.md`

---

### `wave/` (Context tools / operational docs)

| name | files | MB | md | json | yaml |
|---|---|---|---|---|---|
| intelligence | 132 | 3.20 | 1 | 130 | 1 |
| docs | 109 | 1.56 | 104 | 2 | 3 |
| tools | 38 | 0.10 | 11 | 3 | 24 |
| llm-threads | 10 | 0.56 | 10 | 0 | 0 |
| config | 8 | 0.10 | 0 | 1 | 7 |
| reference_datasets | 3 | 0.07 | 2 | 1 | 0 |
| registry | 2 | 1.31 | 1 | 1 | 0 |
| reports | 2 | 0.01 | 2 | 0 | 0 |

Key entrypoints inside `wave/`:
- `wave/docs/README.md`
- `wave/docs/AI_USER_GUIDE.md`
- `wave/docs/theory/THEORY.md` (Unified theory narrative)
- `wave/tools/` (tooling, MCP factory)

---

### `.agent/` (Governance + tasking + emergency maps)

| name | files | MB | md | json | yaml |
|---|---|---|---|---|---|
| registry | 152 | 0.18 | 4 | 0 | 148 |
| intelligence | 76 | 2.51 | 37 | 34 | 5 |
| deck | 24 | 0.03 | 1 | 0 | 23 |
| specs | 15 | 0.16 | 14 | 0 | 1 |
| macros | 13 | 0.05 | 1 | 0 | 12 |
| emergency | 9 | 0.13 | 9 | 0 | 0 |
| schema | 6 | 0.05 | 0 | 0 | 6 |
| state | 5 | 0.00 | 0 | 0 | 5 |
| sprints | 3 | 0.01 | 0 | 0 | 3 |
| agents | 3 | 0.00 | 0 | 0 | 3 |
| handoffs | 1 | 0.01 | 1 | 0 | 0 |
| runs | 1 | 0.00 | 0 | 0 | 1 |
| SUBSYSTEM_INTEGRATION.md | 1 | 0.02 | 1 | 0 | 0 |
| hooks | 1 | 0.00 | 1 | 0 | 0 |
| manifest.yaml | 1 | 0.00 | 0 | 0 | 1 |
| ROADMAP.yaml | 1 | 0.01 | 0 | 0 | 1 |
| KERNEL.md | 1 | 0.01 | 1 | 0 | 0 |
| CONSOLIDATED_POSSIBILITIES.md | 1 | 0.01 | 1 | 0 | 0 |
| roadmaps | 1 | 0.00 | 0 | 0 | 1 |
| docs | 1 | 0.01 | 1 | 0 | 0 |
| citizenship | 1 | 0.01 | 0 | 0 | 1 |
| META_REGISTRY.yaml | 1 | 0.00 | 0 | 0 | 1 |
| SPRAWL_CONSOLIDATION_PLAN.md | 1 | 0.00 | 1 | 0 | 0 |
| config | 1 | 0.00 | 0 | 0 | 1 |
| CODOME_MANIFEST.yaml | 1 | 0.02 | 0 | 0 | 1 |

Key entrypoints inside `.agent/`:
- `.agent/KERNEL.md` (core operating kernel)
- `.agent/manifest.yaml` + `.agent/META_REGISTRY.yaml` (system registry glue)
- `.agent/deck/` (decision cards)
- `.agent/registry/` (task tracking and state)

---

## Filesystem indexes (download / open)

- [`FILE_INDEX.csv`](FILE_INDEX.csv) — every file, bytes, extension, top-level, classification.
- [`DIRECTORY_STATS.csv`](DIRECTORY_STATS.csv) — directory-by-directory counts and size.
- [`DOCS_INDEX.csv`](DOCS_INDEX.csv) — every markdown doc with title + connectivity stats.
- [`BROKEN_LINKS.csv`](BROKEN_LINKS.csv) — broken local links (after ignoring code blocks).

---

## Documentation connectivity snapshot (why it feels “chain-like”)

This pack contains **788 active markdown files** (non-archive).
But only **64 internal doc-to-doc links** exist between them.

- **Isolated docs (no inbound *and* no outbound doc links): 733 / 788**
- **Docs explicitly marked “Generated”: 42**
- **Broken local links in active set: 14**

### Current hubs (highest link degree)

| path | degree | title |
|---|---|---|
| wave/docs/prompts/README.md | 14 | Standard Code Validation Megaprompts |
| particle/README.md | 11 | Collider: The Standard Model of Code Particles |
| particle/docs/MODEL.md | 8 | MODEL.md - The Standard Model of Code |
| particle/docs/reports/README.md | 7 | Reports |
| wave/docs/README.md | 7 | Context Management Documentation |
| particle/docs/README.md | 6 | Documentation |
| wave/tools/mcp/mcp_factory/INDEX.md | 6 | MCP Factory |
| particle/docs/COLLIDER.md | 4 | COLLIDER.md - The Tool |
| wave/tools/mcp/mcp_factory/knowledge/EXTERNAL_LINKS.md | 4 | External Resources |
| particle/docs/PURPOSE_INTELLIGENCE.md | 3 | Purpose Intelligence (Q-Scores) |
| particle/docs/specs/README.md | 3 | Specifications |
| wave/tools/mcp/mcp_factory/knowledge/TROUBLESHOOTING.md | 3 | MCP Troubleshooting Guide |

### Connected clusters that actually exist (active docs)

There are only **8** connected components with size > 1 among active docs.

### Component 1 (size 17)
Hub: `particle/docs/reports/README.md` — **Reports**

- `particle/CLAUDE.md` — Collider (Standard Model of Code)
- `particle/CONTRIBUTING.md` — Contributing to Collider
- `particle/README.md` — Collider: The Standard Model of Code Particles
- `particle/docs/COLLIDER.md` — COLLIDER.md - The Tool
- `particle/docs/MODEL.md` — MODEL.md - The Standard Model of Code
- `particle/docs/PURPOSE_INTELLIGENCE.md` — Purpose Intelligence (Q-Scores)
- `particle/docs/README.md` — Documentation
- `particle/docs/registry/HISTORY.md` — Project History: The Evolution of the Standard Model of Code
- `particle/docs/reports/DESIGN_TOKEN_SYSTEM_AUDIT.md` — Design Token System Audit
- `particle/docs/reports/DOCS_IMPROVEMENT_TASK_REGISTRY.md` — Documentation Improvement Task Registry
- `particle/docs/reports/GAPS_ANALYSIS_2026-01-19.md` — Collider Gaps Analysis Report
- `particle/docs/reports/README.md` — Reports
- `particle/docs/reports/TOKEN_SYSTEM_TASK_REGISTRY.md` — Token System Task Registry
- `particle/docs/reports/TOKEN_SYSTEM_VERIFICATION_PROTOCOL.md` — Token System Verification Protocol
- `particle/docs/specs/AI_INTERFACE_SPEC.md` — AI Interface Specification
- `particle/docs/specs/README.md` — Specifications
- `particle/src/core/INDEX.md` — src/core/ - Core Analysis Engine


### Component 2 (size 15)
Hub: `wave/docs/prompts/README.md` — **Standard Code Validation Megaprompts**

- `wave/docs/prompts/01_claims_ledger.md` — MEGAPROMPT 01: CLAIMS LEDGER & FALSIFIABILITY
- `wave/docs/prompts/02_lens_validation.md` — MEGAPROMPT 02: LENS SYSTEM VALIDATION
- `wave/docs/prompts/03_dimension_orthogonality.md` — MEGAPROMPT 03: DIMENSION ORTHOGONALITY & BOUNDARY CASES
- `wave/docs/prompts/04_atom_coverage.md` — MEGAPROMPT 04: ATOM COVERAGE & AST MAPPING
- `wave/docs/prompts/05_role_taxonomy.md` — MEGAPROMPT 05: ROLE TAXONOMY VALIDATION
- `wave/docs/prompts/06_detection_signals.md` — MEGAPROMPT 06: DETECTION SIGNALS & EVIDENCE MODEL
- `wave/docs/prompts/07_confidence_calibration.md` — MEGAPROMPT 07: CONFIDENCE & CALIBRATION SYSTEM
- `wave/docs/prompts/08_edge_semantics.md` — MEGAPROMPT 08: EDGE SEMANTICS & GRAPH SCHEMA
- `wave/docs/prompts/09_analysis_pipeline.md` — MEGAPROMPT 09: ANALYSIS PIPELINE ARCHITECTURE
- `wave/docs/prompts/10_correctness_definitions.md` — MEGAPROMPT 10: CORRECTNESS DEFINITIONS
- `wave/docs/prompts/11_benchmark_design.md` — MEGAPROMPT 11: BENCHMARK DATASET DESIGN
- `wave/docs/prompts/12_semantic_similarity.md` — MEGAPROMPT 12: SEMANTIC SIMILARITY ON 8D MANIFOLD
- `wave/docs/prompts/13_entropy_complexity.md` — MEGAPROMPT 13: ENTROPY & COMPLEXITY MEASURES
- `wave/docs/prompts/14_governance_evolution.md` — MEGAPROMPT 14: GOVERNANCE & EVOLUTION PROTOCOL
- `wave/docs/prompts/README.md` — Standard Code Validation Megaprompts


### Component 3 (size 9)
Hub: `wave/docs/README.md` — **Context Management Documentation**

- `wave/docs/AI_USER_GUIDE.md` — AI User Guide: The Alien Architecture
- `wave/docs/ASSET_INVENTORY.md` — Asset Inventory: The Automations
- `wave/docs/COLLIDER_ARCHITECTURE.md` — Collider Modular Architecture
- `wave/docs/HOLOGRAPHIC_SOCRATIC_LAYER.md` — The Holographic-Socratic Layer
- `wave/docs/ORIENTATION_FILES.md` — Orientation Files System
- `wave/docs/README.md` — Context Management Documentation
- `wave/docs/STORAGE_ARCHITECTURE.md` — 🗄️ STORAGE ARCHITECTURE
- `wave/docs/TOOL.md` — COLLIDER - THE IMPLEMENTATION
- `wave/docs/theory/THEORY.md` — STANDARD MODEL OF CODE - UNIFIED THEORY


### Component 4 (size 6)
Hub: `wave/tools/mcp/mcp_factory/INDEX.md` — **MCP Factory**

- `wave/tools/mcp/mcp_factory/CONFIG_PANEL.md` — MCP Factory - Configuration Panel
- `wave/tools/mcp/mcp_factory/INDEX.md` — MCP Factory
- `wave/tools/mcp/mcp_factory/ROADMAP.md` — MCP Factory Roadmap
- `wave/tools/mcp/mcp_factory/knowledge/CONFIGURATION.md` — MCP Configuration Deep Dive
- `wave/tools/mcp/mcp_factory/knowledge/EXTERNAL_LINKS.md` — External Resources
- `wave/tools/mcp/mcp_factory/knowledge/TROUBLESHOOTING.md` — MCP Troubleshooting Guide


### Component 5 (size 2)
Hub: `particle/docs/specs/UNIVERSAL_PROPERTY_BINDER.md` — **Universal Property Binder (UPB)**

- `particle/docs/specs/SCALE_TRANSFORMS.md` — Scale Transforms - Warp Functions for Data Visualization
- `particle/docs/specs/UNIVERSAL_PROPERTY_BINDER.md` — Universal Property Binder (UPB)


### Component 6 (size 2)
Hub: `wave/docs/deep/HOLOGRAPHIC_SOCRATIC_LAYER.md` — **The Holographic-Socratic Layer**

- `wave/docs/deep/AI_USER_GUIDE.md` — AI User Guide: The Alien Architecture
- `wave/docs/deep/HOLOGRAPHIC_SOCRATIC_LAYER.md` — The Holographic-Socratic Layer


### Component 7 (size 2)
Hub: `wave/docs/CONTEXTOME.md` — **CONTEXTOME - The Context Universe**

- `wave/docs/CONTEXTOME.md` — CONTEXTOME - The Context Universe
- `particle/docs/specs/REGISTRY_OF_REGISTRIES.md` — Registry of Registries


### Component 8 (size 2)
Hub: `particle/docs/specs/CODOME_LANDSCAPE.md` — **Codome Landscape**

- `particle/docs/specs/CODOME_LANDSCAPE.md` — Codome Landscape
- `particle/docs/specs/LANDSCAPE_IMPLEMENTATION_GUIDE.md` — Landscape Implementation Guide


### Active broken links (fix these first to keep navigation trustworthy)

| src | link | resolved | suggestion |
|---|---|---|---|
| wave/docs/archive/ROADMAP_10_OF_10.md | docs/roadmaps/C1_ATOM_ENUMERATION.md | wave/docs/archive/docs/roadmaps/C1_ATOM_ENUMERATION.md | Extra `docs/` segment; check relative base. |
| wave/docs/archive/ROADMAP_10_OF_10.md | docs/roadmaps/C2_JSON_SCHEMA.md | wave/docs/archive/docs/roadmaps/C2_JSON_SCHEMA.md | Extra `docs/` segment; check relative base. |
| wave/docs/archive/ROADMAP_10_OF_10.md | docs/roadmaps/C3_TRAINING_CORPUS.md | wave/docs/archive/docs/roadmaps/C3_TRAINING_CORPUS.md | Extra `docs/` segment; check relative base. |
| wave/docs/archive/legacy_schema_2025/theory_v2.md | ./OCTAHEDRAL_ATOM.md | wave/docs/archive/legacy_schema_2025/OCTAHEDRAL_ATOM.md |  |
| wave/docs/archive/legacy_schema_2025/theory_v2.0.md | ./OCTAHEDRAL_ATOM.md | wave/docs/archive/legacy_schema_2025/OCTAHEDRAL_ATOM.md |  |
| wave/docs/deep/PURPOSE_EMERGENCE.md | ../../particle/docs/MODEL.md | wave/particle/docs/MODEL.md | Relative path likely needs one more `../` to reach repo root (should be `../../../particle/...`). |
| wave/docs/deep/PURPOSE_EMERGENCE.md | ../../particle/docs/COLLIDER.md | wave/particle/docs/COLLIDER.md | Relative path likely needs one more `../` to reach repo root (should be `../../../particle/...`). |
| .agent/intelligence/WAVE_PARTICLE_BALANCE.md | ../specs/WAVE_PARTICLE_SYMMETRY.md | agent/specs/WAVE_PARTICLE_SYMMETRY.md | Did you mean `.agent/specs/WAVE_PARTICLE_SYMMETRY.md` (missing leading dot)? |
| .agent/intelligence/WAVE_PARTICLE_BALANCE.md | ./PRIORITY_MATRIX.md | agent/intelligence/PRIORITY_MATRIX.md | Did you mean `.agent/intelligence/PRIORITY_MATRIX.md` (missing leading dot)? |
| .agent/intelligence/PRIORITY_MATRIX.md | ../specs/WAVE_PARTICLE_SYMMETRY.md | agent/specs/WAVE_PARTICLE_SYMMETRY.md | Did you mean `.agent/specs/WAVE_PARTICLE_SYMMETRY.md` (missing leading dot)? |
| .agent/emergency/SYSTEM-CRYSTALLIZATION-INDEX.md | ./PARTICLE-COLLIDER-EMERGENCY-MAP.md | agent/emergency/PARTICLE-COLLIDER-EMERGENCY-MAP.md | Did you mean `.agent/emergency/PARTICLE-COLLIDER-EMERGENCY-MAP.md` (missing leading dot)? |
| .agent/emergency/SYSTEM-CRYSTALLIZATION-INDEX.md | ./WAVE-AI-SUBSYSTEM-EMERGENCY-MAP.md | agent/emergency/WAVE-AI-SUBSYSTEM-EMERGENCY-MAP.md | Did you mean `.agent/emergency/WAVE-AI-SUBSYSTEM-EMERGENCY-MAP.md` (missing leading dot)? |
| .agent/emergency/SYSTEM-CRYSTALLIZATION-INDEX.md | ./OBSERVER-GOVERNANCE-EMERGENCY-MAP.md | agent/emergency/OBSERVER-GOVERNANCE-EMERGENCY-MAP.md | Did you mean `.agent/emergency/OBSERVER-GOVERNANCE-EMERGENCY-MAP.md` (missing leading dot)? |
| .agent/emergency/SYSTEM-CRYSTALLIZATION-INDEX.md | ./BACKGROUND-SERVICES-EMERGENCY-MAP.md | agent/emergency/BACKGROUND-SERVICES-EMERGENCY-MAP.md | Did you mean `.agent/emergency/BACKGROUND-SERVICES-EMERGENCY-MAP.md` (missing leading dot)? |

---

## Immediate separation opportunities

If your goal is a **shippable “v1 Core”**, these are the obvious “separate from canon” zones:

- `particle/artifacts/` — massive JSON scan outputs (keep, but do not treat as canon).
- `particle/docs/research/**` and `wave/intelligence/**` — LLM run outputs and research traces.
- `.collider-full/`, `collider_output_small/`, `architecture_report/` — generated run artifacts.
- `archive/` and `particle/.archive/` — legacy snapshots.

---

## What to do next (turn “chain” into “mesh”)

**Principle:** every knowledge node must have a *home*, a *parent index*, and at least a few *related crosslinks*.

1. **Create a root `INDEX.md`** (or upgrade `PROJECT_MAP.md`) so it contains *real clickable links* to:
   - Theory (MODEL / THEORY)
   - Collider usage
   - Registries (atoms, stages, dimensions)
   - Governance (.agent kernel/deck)
   - Reports / gaps
2. **Guarantee folder-level indexes**:
   - Every `docs/` folder has a `README.md` or `INDEX.md` that links to *all children*.
   - Every child doc links back to its folder index (“Up” link).
3. **Exploit existing theory markers** (`@SECTION`, `@DEPENDS_ON`, `@PROVIDES`):
   - Auto-generate a *Theory Section Registry* and *Concept Atlas* so readers can navigate non-linearly.
4. **Automate coherence**:
   - link-check (active docs only)
   - placeholder-check (no `{TODO}` templates in active)
   - registry uniqueness checks (IDs, counts)

See also: `THEORY_SECTION_REGISTRY.csv` and `THEORY_SECTION_GRAPH.json` in this pack.
