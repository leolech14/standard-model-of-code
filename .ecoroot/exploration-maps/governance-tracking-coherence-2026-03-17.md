# Governance Tracking Coherence: Audit & Unification

**Date:** 2026-03-17
**Surfaces audited:** Open Concerns, Current Concerns, Exploration Maps, Opportunities
**Goal:** Map schema differences, identify untracked items, propose unified schema

---

## Current State: 4 Disconnected Tracking Surfaces

| Surface | Location | Files | ID Scheme | Schema | Cross-refs |
|---------|----------|-------|-----------|--------|------------|
| Open Concerns | `governance/OPEN_CONCERNS.md` | 1 file, 42 items | `EG-001`, `OC-001`, `SG-001`, `TD-001` | severity/impact/evidence/fix/effort | 0 outbound |
| Current Concerns | `.ecoroot/current_concerns.md` | 1 file, 10 items | Numbered (#1-#10) | priority/what/why/status/next-step/references | 0 outbound |
| Exploration Maps | `.ecoroot/exploration-maps/` | 6 files | None (filename) | No schema. Pure prose. | 2 files ref opportunities |
| Opportunities | `.ecoroot/opportunities/` | 2 files | `OPP-DE-001`, `P1` | Inconsistent frontmatter | 0 outbound |

### Problems

1. **No cross-referencing.** Current Concerns #1 (Ideome) and Open Concerns EG-001 (Atlas Validator) cover overlapping territory but don't link to each other.
2. **Duplicate tracking.** The Ideome concern appears in current_concerns.md but NOT in OPEN_CONCERNS.md (which claims to be the "AUTHORITATIVE single source of truth").
3. **No shared identity protocol.** Concerns use `EG-001`, opportunities use `OPP-DE-001`, explorations have no IDs. Nothing follows the atlas entity identity pattern.
4. **No lifecycle tracking.** Explorations have no status field. Opportunities have inconsistent ones. Neither tracks when they were last reviewed or whether they've been acted on.
5. **No severity normalization.** OPEN_CONCERNS uses CRITICAL/HIGH/MEDIUM/LOW. current_concerns uses HIGH/MEDIUM/LOW. No shared scale.

---

## These Are Siblings: They're All "Tracked Knowledge Objects"

| Surface | What It Really Is | Lifecycle |
|---------|------------------|-----------|
| Concern | A problem that needs fixing | open → investigating → fixing → resolved → closed |
| Opportunity | A possibility that could be seized | identified → scoped → designing → building → shipped |
| Exploration | Research that generates understanding | started → synthesized → applied → archived |

They share: an owner, a creation date, a status, a priority, related entities, and a natural language description. They differ in: what action they require (fix vs build vs understand).

### Proposed Unified Schema

Every tracked knowledge object gets the same identity block:

```yaml
id: TKO-{NNN}           # Tracked Knowledge Object
kind: concern | opportunity | exploration
name: lowercase-hyphenated
title: Human-readable title
status: open | investigating | designing | building | resolved | shipped | archived
priority: critical | high | medium | low
owner: leo
created: 2026-03-17
last_reviewed: 2026-03-17
domain: governance | infrastructure | collider | wave | agent | ui | documentation | theory | tech_debt | atlas
related:
  - ref: CMP-052         # Atlas entity this relates to
    why: "ACI routing needs Oracle wiring"
  - ref: TKO-003
    why: "Blocked by artifact node type decision"
evidence: string          # File path or URL to evidence
next_action: string       # What to do next
```

### If adopted, the unified file would be: `.ecoroot/TRACKED_KNOWLEDGE.yaml`

One file. Machine-readable. All concerns, opportunities, and explorations in one place. Exploration maps remain as separate deep-dive documents — the TKO entry REFERENCES them, not replaces them.

---

## Untracked Items (from 2026-03-15/16/17 sessions)

### Untracked Concerns

| ID | Title | Priority | Domain | Evidence |
|----|-------|----------|--------|----------|
| — | Atlas emitter (Stage 23) unregistered as CMP-092 | medium | atlas | `grep 'emitter' atlas/ATLAS.yaml` returns only comment |
| — | Oracle Tier -1 not wired into ACI routing | medium | wave | `atlas.py` exists standalone, not in analyze.py flow |
| — | ~40 orphaned Doppler secrets | medium | infrastructure | `_inbox/SMOC_EXPLORATION_LAYER2.md` evidence |
| — | Perplexity API quota exhausted | high | wave | `CON-007 status: broken` in ATLAS.yaml |
| — | ideome_scorer.py checks YAML not source code | critical | governance | `governance/IDEOME_ARCHITECTURE_CRITIQUE.md` full analysis |
| — | ideome_synthesis.py (real Codome analysis) unused by scorer | high | governance | 501 lines of working code ignored |
| — | 277 theory docs have zero identity blocks | medium | documentation | `particle/docs/research/20260315_smoc_docs_pre_audit_snapshot.md` |
| — | new-ecosystem-component skill untested | low | governance | `memory/feedback_skill_creation_protocol.md` |
| — | Artifact node type missing from atlas schema | high | atlas | `memory/artifact_node_type_design.md` design seed |
| — | 2,941 _inbox artifacts with no formal triage process | medium | documentation | `_inbox/SMOC_ARTIFACT_INVENTORY.yaml` |

### Untracked Opportunities

| ID | Title | Priority | Domain | Evidence |
|----|-------|----------|--------|----------|
| — | Oracle: atlas-aware knowledge retrieval | high | wave | `particle/docs/plans/ORACLE_VISION.md` |
| — | Collider emitter auto-generating scaffold entries | high | collider | Stage 23 live, 28 candidates detected |
| — | Atlas-aware RAG stores with entity-tagged citations | medium | wave | Oracle vision doc |
| — | Cross-project indexing (Elements + OpenClaw + _inbox) | medium | wave | Oracle vision doc |
| — | Theory docs as ART-xxx artifact entries | high | atlas | `memory/artifact_node_type_design.md` |
| — | Channels architecture as Telegram game-changer | medium | infrastructure | `docs/ADR_CHANNELS_CAPABILITY.md` in PROJECT_openclaw |
| — | DevJournal as first Refinery ingestion pipeline | high | wave | Other session's brainstorm (5 visual pages) |

### Untracked Explorations

| Title | Evidence | Related |
|-------|----------|---------|
| 15 industry standards for connectivity schemas | Session transcript + web search results | Atlas design |
| _inbox content bucket map (8 buckets) | `_inbox/SMOC_EXPLORATION_LAYER1.md`, `LAYER2.md` | Documentation |
| Collider co-validation (24650 nodes, Grade C) | Session transcript | Atlas scaffold validation |
| Architecture fitness test (4 configs scored) | Session transcript, test branches deleted | Atlas placement |
| Scaffold hypothesis validation (6 tests, CONFIRMED) | `atlas/SCAFFOLD_HYPOTHESIS_VALIDATION.md` | Atlas foundation |

---

## Recommendation

1. **Consolidate current_concerns.md INTO governance/OPEN_CONCERNS.md** — one authoritative source, not two.
2. **Add the untracked items above** to OPEN_CONCERNS.md (concerns) and a new `.ecoroot/opportunities/` entries (opportunities).
3. **Adopt the TKO schema** for new entries going forward. Retrofit existing entries gradually.
4. **Cross-reference exploration maps** from their related concerns/opportunities via `related:` field.
5. **DON'T restructure everything at once** — this is scaffolding, not migration. Add the identity block to new entries. Old entries stay as-is until touched.
