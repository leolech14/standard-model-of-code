# Alternative Configurations for Coordinate System

**Date:** 2026-01-29
**Status:** EXPLORATION

---

## Overview

Four candidate configurations have been identified for resolving the notation collision between the holarchy scale (containment) and Tarski hierarchy (abstraction).

---

## Config A: Two-Axis System (RECOMMENDED)

### Description

Separate symbols for separate axes:
- **C-scale** (C-3 to C12): Codome containment hierarchy
- **M-scale** (M₀, M₁, M₂...): Tarski meta-levels

### Notation

| Artifact Type | Position Format | Example |
|---------------|-----------------|---------|
| Code entity | (C-level, M₀) | (C3, M₀) |
| Documentation | (about_C, M₁) | (about_C5, M₁) |
| Theory doc | (about_theory, M₂) | (about_theory, M₂) |

### Pros
- Clear separation of concerns
- Each axis has dedicated symbol
- No ambiguity in notation
- Infinite M-scale matches Tarski
- Backward-compatible mapping

### Cons
- Requires renaming existing L references
- "C" might be confused with Codome set (C)
- Two-coordinate positions are more complex

### Migration Effort
- MEDIUM: Rename L→C in code level refs, L→M in Tarski refs

---

## Config B: Rename Tarski Only

### Description

Keep L for holarchy, use different symbol for Tarski:
- **L-scale** (L-3 to L12): Code containment (unchanged)
- **T-scale** (T₀, T₁, T₂...): Tarski meta-levels

### Notation

| Artifact Type | Position Format | Example |
|---------------|-----------------|---------|
| Code entity | L-level | L3 |
| Documentation | (about_L, T₁) | (about_L5, T₁) |
| Theory doc | T₂ | T₂ |

### Pros
- Minimal change to existing holarchy references
- "T" clearly stands for Tarski
- Documentation is familiar with L-levels

### Cons
- L still appears to be universal (it's not)
- Must remember L = Codome-only (implicit constraint)
- "L0_AXIOMS" filename becomes confusing (is that T₀ or L0?)

### Migration Effort
- LOW: Only rename Tarski references

---

## Config C: Unified Continuous Scale

### Description

Merge containment and abstraction into one continuous scale:
- C-3 to C12: Code containment (bottom)
- L1 to L∞: Meta-levels (top)
- Junction at C12 → L1

### Notation

```
... → C10 → C11 → C12 → L1 → L2 → L3 → ...
        |                |
     UNIVERSE        META-UNIVERSE
```

### Pros
- Single scale to learn
- "Higher" always means "more abstract"

### Cons
- **REJECTED BY RESEARCH:** Containment ≠ abstraction
- Orthogonal concepts forced onto single axis
- TOPSA framework explicitly separates these
- Would create false implications (C12 "contains" L1? No.)

### Migration Effort
- HIGH: Complete reconceptualization

### Status: **NOT RECOMMENDED** (orthogonality violation)

---

## Config D: Three-Coordinate System

### Description

Add explicit "Universe" dimension:
- **C-scale** (C-3 to C12): Containment
- **M-scale** (M₀, M₁, M₂...): Abstraction
- **U-scale** (U_codome, U_contextome, U_external): Universe

### Notation

| Artifact Type | Position Format | Example |
|---------------|-----------------|---------|
| Code entity | (U_codome, C3, M₀) | Function in codebase |
| Internal doc | (U_contextome, -, M₁) | README.md |
| External doc | (U_external, -, M₁) | Anthropic docs |
| Theory | (U_contextome, -, M₂) | L0_AXIOMS.md |

### Pros
- Most explicit: every dimension named
- Handles external knowledge cleanly
- No ambiguity possible

### Cons
- Three coordinates is complex
- Universe is already implied by artifact type
- Over-engineering for current needs

### Migration Effort
- HIGH: Add universe tracking to all artifacts

---

## Comparison Matrix

| Criterion | Config A | Config B | Config C | Config D |
|-----------|----------|----------|----------|----------|
| Notation clarity | HIGH | MEDIUM | LOW | HIGH |
| Theoretical soundness | HIGH | HIGH | LOW | HIGH |
| Migration effort | MEDIUM | LOW | HIGH | HIGH |
| Future extensibility | HIGH | MEDIUM | LOW | HIGH |
| Cognitive load | MEDIUM | LOW | HIGH | HIGH |
| Recommended? | **YES** | MAYBE | NO | OVERKILL |

---

## Decision Rationale

**Config A is recommended** because:

1. **Principled:** Orthogonal concepts get orthogonal axes
2. **Clear:** No overloaded symbols
3. **Tractable:** Migration is manageable
4. **Extensible:** M-scale is infinite per Tarski
5. **Validated:** Perplexity research confirms containment ≠ abstraction

Config B is acceptable fallback if C-scale rename is too disruptive.

Config C is **rejected** based on TOPSA framework showing orthogonality.

Config D is valid but overkill for current needs (can evolve to it later).

---

## Test Plan

Each configuration should be tested against:
1. Core code artifacts (30+ diverse files)
2. Contextome artifacts (docs, configs)
3. External knowledge (provider docs)
4. Observer realm tools (DocIntel, Autopilot)
5. Edge cases (generated code, vendor, binaries)

See TESTS.yaml for full artifact list.

---

*Config A proceeds to validation.*
