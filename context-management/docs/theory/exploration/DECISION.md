# ADR: Coordinate System Notation Resolution

**ADR ID:** ADR-2026-001
**Date:** 2026-01-29
**Status:** PROPOSED
**Decision:** [PENDING VALIDATION]

---

## Context

The Standard Model of Code uses the symbol "L" for two distinct concepts:

1. **Holarchy containment levels** (L-3 to L12): Physical structure of code
2. **Tarski meta-language levels** (L₀, L₁, L₂...): Abstraction hierarchy

This collision was discovered when attempting to position DocIntel (a documentation intelligence tool) on the L-scale. The failure revealed that:

- The L-scale (holarchy) applies **only to Codome** (code entities)
- The Tarski hierarchy applies to **all artifacts** (code and context)
- These are orthogonal dimensions, not a single scale

---

## Decision

**[TO BE FILLED AFTER VALIDATION]**

### Selected Configuration

**Config [A/B/C/D]:** [Name]

### Notation

| Scale | Symbol | Range | Domain |
|-------|--------|-------|--------|
| ... | ... | ... | ... |

### Rationale

[Why this configuration was selected]

---

## Alternatives Considered

### Config A: Two-Axis System
- C-scale (C-3 to C12) for containment
- M-scale (M₀, M₁, M₂...) for abstraction
- **Status:** [Accepted/Rejected/Considered]

### Config B: Rename Tarski Only
- Keep L-scale for containment
- T-scale for Tarski levels
- **Status:** [Accepted/Rejected/Considered]

### Config C: Unified Continuous Scale
- Merge into single scale
- **Status:** Rejected (orthogonality violation)

### Config D: Three-Coordinate System
- Add explicit Universe dimension
- **Status:** [Accepted/Rejected/Considered]

---

## Consequences

### Positive

- [List benefits of selected configuration]

### Negative

- [List drawbacks and migration costs]

### Neutral

- [List changes that are neither better nor worse]

---

## Implementation

### Phase 1: Documentation
- [ ] Update theory documents with new notation
- [ ] Create NOTATION_REGISTRY.md as guard rail
- [ ] Document migration path

### Phase 2: Code
- [ ] Update KIND_TO_LEVEL mapping (if renamed)
- [ ] Update level_classifier.py
- [ ] Update comments and docstrings

### Phase 3: Validation
- [ ] Run test matrix against all artifacts
- [ ] External review (GPT validation)
- [ ] Community feedback (if applicable)

---

## Validation Results

| Reviewer | Date | Verdict | Notes |
|----------|------|---------|-------|
| Claude | 2026-01-29 | Config A recommended | Based on orthogonality research |
| GPT 5.2 | [PENDING] | [PENDING] | [PENDING] |
| User | [PENDING] | [PENDING] | [PENDING] |

---

## References

- `PROPOSAL.md` - Detailed proposal with motivation
- `ALTERNATIVES.md` - All configurations compared
- `TESTS.yaml` - Test matrix (35+ artifacts)
- `VALIDATION.md` - Validation protocol
- `NOTATION_REGISTRY.md` - Guard rail against future collisions
- `FUNDAMENTAL_INSIGHT_L_SCALE_SCOPE.md` - Discovery that triggered this ADR

---

## Decision Record

| Date | Actor | Action |
|------|-------|--------|
| 2026-01-29 | Claude/Leonardo | Created proposal pack |
| [DATE] | [ACTOR] | [ACTION] |

---

*This ADR will be updated with the final decision after validation is complete.*
