# Notation Registry: Standard Model of Code

**Date:** 2026-01-29
**Status:** DRAFT (pending coordinate system decision)
**Purpose:** Guard rail against notation collisions

---

## 1. Purpose

This registry tracks all symbolic notation used in the Standard Model of Code theory. Before introducing new notation:

1. Check this registry for conflicts
2. Add new symbols with clear definitions
3. Document any deprecated symbols

---

## 2. Active Symbols

### 2.1 Set/Universe Notation

| Symbol | Name | Definition | Source |
|--------|------|------------|--------|
| **P** | Projectome | Complete project universe | L0_AXIOMS.md |
| **C** | Codome | Executable artifacts subset | L0_AXIOMS.md |
| **X** | Contextome | Non-executable artifacts subset | L0_AXIOMS.md |
| **N** | Nodes | Discrete code entities | L0_AXIOMS.md |
| **E** | Edges | Relationships between nodes | L0_AXIOMS.md |
| **G** | Graph | (N, E) tuple | L0_AXIOMS.md |

### 2.2 Level Notation (CURRENT - COLLISION EXISTS)

| Symbol | Name | Definition | Source | Status |
|--------|------|------------|--------|--------|
| **L** | Level | OVERLOADED - see collision | L0_AXIOMS.md | **COLLISION** |
| L-3 to L12 | Holarchy levels | Containment hierarchy | L0_AXIOMS.md | Active |
| L₀, L₁, L₂... | Tarski levels | Meta-language hierarchy | L0_AXIOMS.md | Active |

### 2.3 Level Notation (PROPOSED - Config A)

| Symbol | Name | Definition | Range | Status |
|--------|------|------------|-------|--------|
| **C** | Containment level | Code containment hierarchy | C-3 to C12 | PROPOSED |
| **M** | Meta level | Tarski abstraction hierarchy | M₀, M₁, M₂... | PROPOSED |

**Note:** If Config A is accepted, the "C" symbol will be overloaded (set vs level). May need alternative like "H" (Holarchy) for containment scale.

### 2.4 Function Notation

| Symbol | Name | Definition | Source |
|--------|------|------------|--------|
| **λ** | Level assignment | λ: N → L (assigns level to entity) | L0_AXIOMS.md |
| **ε** | Edge type | ε: E → T (assigns type to edge) | L0_AXIOMS.md |
| **γ** | Granularity | γ: V → ℝ⁺ (node size metric) | L0_AXIOMS.md |
| **ρ** | Relevance | ρ: V × Q → [0,1] (query relevance) | L0_AXIOMS.md |

### 2.5 Dimension Notation

| Symbol | Name | Definition | Source |
|--------|------|------------|--------|
| **D** | Dimension count | D = 8 structural dimensions | L0_AXIOMS.md |
| **d₁...d₈** | Individual dimensions | Purpose, Structure, etc. | L0_AXIOMS.md |

### 2.6 Operator Notation

| Symbol | Name | Definition | Source |
|--------|------|------------|--------|
| **⊔** | Disjoint union | P = C ⊔ X | L0_AXIOMS.md |
| **→** | Maps to | Function mapping | Standard |
| **⟹** | Implies | Logical implication | Standard |
| **∩** | Intersection | Set intersection | Standard |
| **∪** | Union | Set union | Standard |

---

## 3. Collision Documentation

### 3.1 The L Collision (Current)

**Problem:** "L" used for two distinct concepts

| Usage | Context | Meaning | Example |
|-------|---------|---------|---------|
| L-3 to L12 | Holarchy | Containment level | L5 = MODULE |
| L₀, L₁, L₂ | Tarski | Abstraction level | L₀ = object language |

**Impact:**
- `L0_AXIOMS.md` filename: Is this Tarski L₀ or Holarchy (no L0 exists)?
- Documentation: "L-level" is ambiguous
- Code: `KIND_TO_LEVEL` mixes concepts

**Resolution:** See ADR-2026-001 (pending)

### 3.2 Potential C Collision (If Config A)

**Problem:** If Config A accepted, "C" used for two concepts

| Usage | Context | Meaning |
|-------|---------|---------|
| C | Set | Codome (executable artifacts) |
| C-3 to C12 | Scale | Containment levels |

**Mitigation options:**
1. Context distinguishes (set C vs level C5)
2. Use H-scale instead (H for Holarchy)
3. Use subscript differently (C for set, C₃ for level)

---

## 4. Reserved Symbols

Symbols reserved for future use or specific meanings:

| Symbol | Reserved For | Status |
|--------|--------------|--------|
| **T** | Potential Tarski scale (Config B) | Reserved |
| **H** | Potential Holarchy scale | Reserved |
| **U** | Potential Universe dimension (Config D) | Reserved |
| **S** | Subsystem (Miller) | Reserved |
| **R** | Realm (Particle/Wave/Observer) | Reserved |

---

## 5. Deprecated Symbols

| Symbol | Former Meaning | Deprecated Date | Replaced By |
|--------|----------------|-----------------|-------------|
| (none yet) | | | |

---

## 6. Adding New Notation

Before adding new symbols:

1. **Check registry:** Does symbol already exist?
2. **Check collision:** Does it conflict with existing meaning?
3. **Document clearly:** Add to appropriate section
4. **Source reference:** Point to defining document

Template for new symbol:
```
| **[SYMBOL]** | [Name] | [Definition] | [Source document] |
```

---

## 7. Notation Style Guide

### 7.1 Sets
- Uppercase single letters: P, C, X, N, E
- Descriptive when needed: Codome, Contextome

### 7.2 Levels
- With hyphen for negative: L-3, C-3
- Plain for positive: L5, C5, M₁
- Subscript for Tarski (infinite): M₀, M₁, M₂...

### 7.3 Functions
- Greek lowercase: λ, ε, γ, ρ
- Arrow notation: λ: N → L

### 7.4 Operators
- Standard mathematical: ⊔, ∪, ∩, →, ⟹

---

## 8. Version History

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-01-29 | Initial registry created |

---

*This registry must be updated whenever notation changes.*
