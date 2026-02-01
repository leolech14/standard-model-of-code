# Theory Exploration: Coordinate System Resolution

**Date:** 2026-01-29
**Status:** AWAITING VALIDATION
**Reviewer(s):** GPT 5.2 Pro (queued)

---

## Purpose

This proposal pack addresses the **notation collision** discovered in the Standard Model of Code, where "L" is used for both:

1. **Holarchy containment levels** (L-3 to L12) - code structure
2. **Tarski meta-language levels** (L₀, L₁, L₂...) - abstraction hierarchy

---

## Discovery Origin

While positioning DocsIntel (a documentation intelligence tool), we discovered:

> **The L-scale (L-3 to L12) applies EXCLUSIVELY to Codome.**

This is documented in `FUNDAMENTAL_INSIGHT_L_SCALE_SCOPE.md`.

---

## Proposal Pack Contents

| File | Purpose | Status |
|------|---------|--------|
| **PROPOSAL.md** | Main proposal with Config A (two-axis system) | Complete |
| **ALTERNATIVES.md** | All 4 configurations compared (A, B, C, D) | Complete |
| **TESTS.yaml** | 35+ artifacts for validation | Complete |
| **VALIDATION.md** | Validation protocol and checklists | Complete |
| **DECISION.md** | ADR template for final decision | Template |
| **NOTATION_REGISTRY.md** | Guard rail against future collisions | Complete |
| **INDEX.md** | This file | Complete |

---

## Recommended Configuration

**Config A: Two-Axis System**

| Scale | Symbol | Range | Domain | Relation |
|-------|--------|-------|--------|----------|
| **C-scale** | C-3 to C12 | 16 levels | Codome only | Containment |
| **M-scale** | M₀, M₁, M₂... | Infinite | All artifacts | Abstraction |

**Why:**
- Orthogonal concepts get orthogonal axes
- No symbol overloading
- Aligns with Tarski (infinite M levels)
- Preserves holarchy semantics

---

## Validation Path

1. [ ] Self-review: Test 35+ artifacts in TESTS.yaml
2. [ ] External review: Send pack to GPT 5.2 Pro
3. [ ] User review: Final decision by Leonardo
4. [ ] Canonize: Update theory documents if accepted

---

## Key Questions for Reviewer

1. Is the two-axis system (C-scale + M-scale) coherent?
2. Are there edge cases the test matrix misses?
3. Does the "C" symbol collision (set vs level) need resolution?
4. Is Config A better than Config B (Tarski-only rename)?
5. What migration risks exist?

---

## How to Use This Pack

### For Review

Read in order:
1. `PROPOSAL.md` - Understand the proposal
2. `ALTERNATIVES.md` - See what else was considered
3. `TESTS.yaml` - Check artifact classifications
4. `VALIDATION.md` - Review validation protocol

### For Decision

After review:
1. Fill in `DECISION.md` with verdict
2. Update `NOTATION_REGISTRY.md` with final notation
3. Plan migration if accepted

---

## Context Links

| Document | Location | Relevance |
|----------|----------|-----------|
| L0_AXIOMS.md | particle/docs/theory/ | Source of collision |
| FUNDAMENTAL_INSIGHT_L_SCALE_SCOPE.md | wave/docs/theory/ | Discovery document |
| POSITIONING.md | wave/tools/docsintel/ | DocsIntel analysis |
| level_classifier.py | particle/src/core/ | Code using L-scale |

---

## Archival

After decision is made:
- Accepted configs → promote to main theory docs
- Rejected configs → keep here as historical record
- Decision → copy to `particle/docs/adr/`

---

*Created as part of DocsIntel positioning work, 2026-01-29*
