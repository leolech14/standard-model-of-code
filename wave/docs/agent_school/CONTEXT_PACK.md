# CONTEXT_PACK - Compact Context Anchor

> **Status:** ACTIVE
> **Purpose:** Minimal, high-trust context to avoid bloating agent windows. This is safe to preload.

## Identity

- **Project:** PROJECT_elements
- **Purpose:** Standard Model of Code — a reference model for machine-actionable software architecture.
- **Core goal:** Measure code structure (Collider) and align it with context (docs, specs, registries).

## Core Ontology

- **PROJECTOME** = CODOME ⊔ CONTEXTOME (disjoint union)
- **CODOME** = executable code
- **CONTEXTOME** = non-executable content (docs/config/metadata)
- **CONCORDANCE** = purpose-aligned region spanning code + docs

## Realms (Top-Level)

- **PARTICLE** → `particle/` (Collider engine, measurement)
- **WAVE** → `wave/` (AI tools, context, analysis)
- **OBSERVER** → `.agent/` (governance, task registry, automation)

## Primary Entry Points

- CLI: `./pe`
- Collider: `./pe collider full <path> --output <dir>`
- AI Query: `./pe ask "question"`
- Verification: `./pe verify`
- Boot: `./pe boot`

## Canonical Docs (Start Here)

1. `wave/docs/PROJECTOME.md`
2. `wave/docs/CODOME.md`
3. `wave/docs/CONTEXTOME.md`
4. `wave/docs/CONCORDANCES.md`
5. `particle/docs/MODEL.md`
6. `particle/docs/COLLIDER.md`
7. `wave/docs/deep/AI_USER_GUIDE.md`

## Registries (SSoT)

- `SUBSYSTEMS.yaml` — subsystem registry
- `DOMAINS.yaml` — symmetry registry (code↔context)
- `.agent/registry/REGISTRY_OF_REGISTRIES.yaml` — registry index
- `REPO_STRUCTURE.json` — declared structure & purpose

## Invariants (Non-Negotiable)

- No dirty repo at end of work (commit or explain).
- Tests must run before claiming done.
- Search before creating new modules or docs.
- Prefer Decision Deck before complex actions: `./pe deck deal`.

## Query Templates

- `./pe ask "How is <subsystem> structured?"`
- `python3 wave/tools/ai/analyze.py "Locate <concept>" --set brain`
- `python3 wave/tools/ai/analyze.py --verify pipeline`

## Intelligence Snapshot (Existing Cerebras Outputs)

- `wave/data/repo_map/repo_map_latest.json` — 3469 files mapped
- `wave/data/enriched/enriched_latest.json` — 422 files enriched (llama3.1-8b, 2026-01-31)
- `wave/data/tags/tags_latest.json` — 566 files tagged (llama-3.3-70b, 2026-01-31)
- `wave/data/intel/unified_intel.json` — unified intel (15 files, sources: rapid_intel + enricher)

## Known Gaps (Brief)

- OBSERVER realm definition conflicts between `SUBSYSTEMS.yaml` and `REPO_STRUCTURE.json`.
- `models/` appears in `REPO_STRUCTURE.json` but is not present at repo root.
- Onboarding references were stale (fixed in current canon).

## Context Pack Usage

This file is safe to preload. For deeper context, follow links in `ONBOARDING.md` or query with `analyze.py`.
