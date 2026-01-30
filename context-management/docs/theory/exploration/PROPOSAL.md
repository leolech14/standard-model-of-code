# Coordinate System Proposal: Disambiguating Holarchy from Meta-Levels

**Date:** 2026-01-29
**Status:** DRAFT - AWAITING VALIDATION
**Type:** Theory Exploration

---

## 1. Problem Statement

The Standard Model of Code has a **notation collision**: the symbol "L" is used for two fundamentally different concepts:

| Usage | Location | Meaning |
|-------|----------|---------|
| L-3 to L12 | Holarchy scale | **Containment** (Code entities, tree-sitter kinds) |
| L₀, L₁, L₂... | Tarski hierarchy | **Abstraction/Description** (Meta-levels) |

This collision causes confusion when:
1. Positioning new tools (e.g., DocsIntel)
2. Understanding what the "L" in L0_AXIOMS.md refers to
3. Mapping Contextome artifacts (which have no tree-sitter kinds)

---

## 2. Core Discovery

### 2.1 The L-Scale is Codome-Specific

The 16-level holarchy (L-3 to L12) applies **exclusively to Codome**:
- Requires tree-sitter AST kinds (function, class, module, etc.)
- Based on syntactic containment hierarchy
- λ: N → L where N ⊆ C (nodes are code entities)

**Contextome has no tree-sitter kinds. Therefore λ is undefined for Contextome.**

### 2.2 Tarski Hierarchy is Orthogonal

Tarski's meta-language hierarchy:
- L₀ = Object language (the code itself)
- L₁ = Meta-language (describes L₀)
- L₂ = Meta-meta-language (describes L₁)
- ... infinite levels

This is about **description/abstraction**, not **containment**.

### 2.3 Key Insight: Two Orthogonal Axes

| Axis | Relation | Question | Applies To |
|------|----------|----------|------------|
| **Containment** | "part-of" | What contains this entity? | Code structure |
| **Abstraction** | "describes" | What does this describe? | All artifacts |

These axes are **independent** and should not share notation.

---

## 3. Proposed Resolution: Config A (Two-Axis System)

### 3.1 Notation

| Scale | Symbol | Range | Domain | Relation |
|-------|--------|-------|--------|----------|
| **C-scale** | C-3 to C12 | 16 levels | Codome only | Containment |
| **M-scale** | M₀, M₁, M₂... | Infinite | All artifacts | Abstraction |

Note: "M" for Meta (Tarski), "C" for Codome containment.

### 3.2 Mapping Rules

**For Code Entities (Codome):**
```
Position = (C-level, M-level)
Example: A function in src/utils.py
  C-level = C3 (ROUTINE)
  M-level = M₀ (object-language, is code)
  Position = (C3, M₀)
```

**For Documentation (Contextome):**
```
Position = (about_C, M-level)
Example: README.md describing the utils module
  about_C = "describes C5" (MODULE)
  M-level = M₁ (meta-language, describes code)
  Position = (about_C5, M₁)
```

**For Meta-Documentation:**
```
Position = (about_*, M-level)
Example: L0_AXIOMS.md (theory document)
  about_* = "describes theory itself"
  M-level = M₂ (meta-meta, describes how we describe)
  Position = (about_theory, M₂)
```

### 3.3 Key Relationships

```
M₀ (Object Level)
├── Codome: Has internal C-structure (C-3 to C12)
│   └── level_classifier.py is at C5, positioned (C5, M₀)
│
└── External code: Also at M₀ (but outside our Projectome)

M₁ (Meta Level)
├── DOCINTEL.md: Describes DocsIntel, positioned (about_DocsIntel, M₁)
├── README.md: Describes module, positioned (about_C5, M₁)
└── providers.yaml: Config describing providers, positioned (about_*, M₁)

M₂ (Meta-Meta Level)
├── L0_AXIOMS.md: Describes the theory itself
├── POSITIONING.md: Explains how to position things
└── This file (PROPOSAL.md): Proposes coordinate systems
```

---

## 4. Benefits of Config A

1. **No Collision:** C and M are distinct symbols
2. **Extensibility:** M-scale is infinite (Tarski)
3. **Clarity:** C explicitly means "Codome containment"
4. **Backward Compatible:** Can map existing L → C for code
5. **Principled:** Orthogonal axes for orthogonal concepts

---

## 5. Migration Path

### 5.1 Axiom Files

```diff
- L0_AXIOMS.md → M0_AXIOMS.md (or keep filename, clarify content)
- L1_DEFINITIONS.md → M1_DEFINITIONS.md
- L2_LAWS.md → M2_LAWS.md
```

### 5.2 Code Level References

```diff
- "L3 (ROUTINE)" → "C3 (ROUTINE)"
- "L5 (MODULE)" → "C5 (MODULE)"
- KIND_TO_LEVEL → KIND_TO_C_LEVEL
```

### 5.3 Tarski References

```diff
- "L₀ object language" → "M₀ object language"
- "L₁ meta-language" → "M₁ meta-language"
```

---

## 6. Open Questions

1. **Naming:** Is "C-scale" clear enough? Alternative: "H-scale" (Holarchy)?
2. **Subscript Style:** C3 vs C₃? (Plain vs subscript for containment)
3. **Documentation of about_C:** How formally should we track what Contextome describes?
4. **Existing Tools:** How much code uses "L" that needs updating?

---

## 7. Validation Required

Before canonizing, test against:
- [ ] 30+ diverse artifacts (see TESTS.yaml)
- [ ] Edge cases (configs, generated code, vendor)
- [ ] Observer realm tools (DocsIntel, Autopilot)
- [ ] Cross-project references

---

## 8. Decision Criteria

Config A is ACCEPTED if:
1. Every artifact can be unambiguously classified
2. No position requires combining containment and abstraction
3. Migration path is tractable
4. Community (GPT review) finds it coherent

---

*See ALTERNATIVES.md for other configurations considered.*
