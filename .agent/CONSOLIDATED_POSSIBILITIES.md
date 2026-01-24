# Consolidated Possibilities - PROJECT_elements

**Generated:** 2026-01-24
**Session:** Claude + Leonardo

---

## Legend

| Grade | Confidence | Meaning |
|-------|-----------|---------|
| A++ | 99%+ | Execute immediately |
| A+ | 95%+ | Validated, ready |
| A | 85-94% | Needs minor refinement |
| B | 70-84% | Needs research |
| C | <70% | Unrefined |

---

## TIER 1: COMPLETED (This Session)

| ID | Title | Status |
|----|-------|--------|
| SPRINT-003 | Context Refinery Foundation | COMPLETE |
| REFINERY | 5-tool pipeline (corpus, boundary, delta, atom, state) | OPERATIONAL |
| TASK-019 | Gemini Context Caching | COMPLETE |
| TASK-020 | HSL Daemon Doppler Fix | COMPLETE |
| TASK-021 | Rate Limiting Fix | COMPLETE |
| CCI | Codome Completeness Index | INTEGRATED |

---

## TIER 2: READY TO EXECUTE (Grade A+)

### OPP-060: Autonomous Enrichment Pipeline (AEP)
**Confidence:** 92% (was blocked by TASK-019, now UNBLOCKED)
**Description:** AI pipeline that auto-enriches opportunities:
- Watches `.agent/registry/inbox/` for new OPPs
- Runs research loops (Gemini + Perplexity + Collider)
- Auto-promotes at 85%+ confidence
- Maps execution steps

**Dependencies:** TASK-019 (COMPLETE), loop.py, analyze.py
**Next:** Implement local cron MVP

---

### OPP-064: Hierarchical Tree Layout for File View
**Confidence:** 95% (Perplexity validated)
**Description:** TRUE tree layout for file navigation:
- Root at TOP, depth increases DOWN
- Thick visual layers per depth level
- d3.cluster() for leaf spacing
- Hybrid mode toggle (classic/force)

**Files:** `file-tree-layout.js`, `sidebar.js`
**Next:** Add classic tree mode to existing layout

---

### OPP-065: Always-Green Continuous Refinement
**Confidence:** 85%
**Description:** The META-GOAL - perpetual green state:
- HSL watches for changes
- Socratic validates against laws
- Cloud refinery enriches
- Auto-promote at thresholds

**Dependencies:** OPP-060 (AEP), OPP-066 (rate limits)
**Next:** Wire AEP into HSL daemon loop

---

## TIER 3: HIGH VALUE INFRASTRUCTURE

### OPP-062: BARE Phase 2 - CrossValidator
**Confidence:** 35% (needs research)
**Description:** Detect code-docs drift via semantic analysis
**Next:** Deep read semantic_models.yaml, map to analyze.py

### OPP-063: GCS Mirror Verification
**Confidence:** 70%
**Description:** Verify .repos_cache archive retrievable
**Next:** Run verification commands

### OPP-059: Sprawl Consolidation
**Confidence:** 90% (partial complete)
**Remaining:** Run GCS offload, audit 528 .md files

---

## TIER 4: VISUALIZATION (UPB System)

### OPP-005: Token System Refactoring
**10 tasks** to remove hardcoded values from app.js
- T001-T006: Edge/node opacity, color schemes
- All 95%+ confidence with step-by-step

### OPP-010: Create presets.yaml
**90% confidence** - Declarative binding config

### OPP-015-019: UPB Integration
- control-bar.js delegation (85%)
- file-viz.js integration (78%)
- edge-system.js integration (75%)
- UPB_BLENDERS wiring (95%)
- endpoints.js minOutput/blendMode (92%)

### OPP-051-056: Modularization Tests
- Node colors, topology tooltips, physics, datamap, groups, hover
- All 70% confidence, need verification

---

## TIER 5: PIPELINE ARCHITECTURE

### OPP-006: Class-Based Stage Architecture
**35 tasks** to refactor pipeline from functions to classes
**Critical Finding:** CodebaseState already exists at `data_management.py:106`

**Phases:**
- P1 Foundation (4 tasks): BaseStage ABC, CodebaseState, Manager
- P2 Wrappers (25 tasks): One wrapper per stage
- P3 Integration (3 tasks): run_full_analysis refactor
- P4 Cleanup (3 tasks): Remove mutations, HSL audit

---

## TIER 6: OPEN CONCERNS (Bugs/Tech Debt)

### OC-009: Scope Leakage (CRITICAL)
- Core node count: Expected 1,179, Actual 2,809 (+138%)
- Check exclusion list loading, verify `include_all` defaults

### OC-001: Tree-sitter Test Failures
- 11 tests fail due to missing module
- Fix: Pin `tree-sitter>=0.20,<0.22` + implement fallback

### OC-010: 88 Skipped Tests
- ~40% of suite silently skipped
- Audit skip reasons, ensure no critical logic hidden

### OC-002: Pipeline Snapshot Missing Node Counts
- Navigator shows timing, not data flow deltas
- Instrument snapshot.py per-stage

### OC-004: Physics Inconsistency
- File view has `forceCenter(0,0,0)`, Atom doesn't
- Align forces between views

---

## TIER 7: FUTURE VISION

### Context Refinery → BARE Phase 2
**Path:** REFINERY atoms feed into CrossValidator for drift detection

### AEP → Always-Green
**Path:** Once AEP runs, wire into HSL daemon for continuous enrichment

### UPB Completion → Viz Excellence
**Path:** Complete token migration → Declarative visual bindings

### Pipeline Refactor → Maintainability
**Path:** Class-based stages → Better testing → Faster iteration

---

## PRIORITY EXECUTION ORDER

1. **OPP-060 (AEP MVP)** - Unblocked, highest leverage
2. **OPP-064 (Tree Layout)** - User-facing, validated
3. **OC-009 (Scope Fix)** - Data quality critical
4. **OPP-005 (Token System)** - Reduces app.js tech debt
5. **OPP-006 Phase 1** - Foundation for all future work

---

## INVENTORY SUMMARY

| Category | Count | Grade A+ | Grade A | Unrefined |
|----------|-------|----------|---------|-----------|
| Infrastructure | 7 | 3 | 2 | 2 |
| Visualization | 18 | 2 | 8 | 8 |
| Pipeline | 35 | 0 | 35 | 0 |
| Open Concerns | 6 | - | - | 6 |
| **TOTAL** | **66** | **5** | **45** | **16** |

---

## Quick Reference: Source Files

| Registry | Location |
|----------|----------|
| Opportunities | `.agent/registry/inbox/OPP-*.yaml` |
| Active Tasks | `.agent/registry/active/TASK-*.yaml` |
| Sprints | `.agent/sprints/SPRINT-*.yaml` |
| Open Concerns | `standard-model-of-code/docs/OPEN_CONCERNS.md` |
| This File | `.agent/CONSOLIDATED_POSSIBILITIES.md` |

---

*"TASK = VALIDATED, READY TO EXECUTE. No more boost workflows."*
