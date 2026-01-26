# OBSERVABILITY TRIAD
# Canonical Mapping of Observability to the Standard Model of Code

> **Status:** CANONIZED (2026-01-25)
> **Created:** 2026-01-25
> **Theory Integration:** Maps to FOUNDATIONS_INTEGRATION.md, THEORY_AXIOMS.md
> **Implementation:** POM, observability.py, observe_session.py

---

## Abstract

The Standard Model of Code has THREE observability modules that are NOT arbitrary tooling choices but NECESSARY manifestations of Peirce's triadic semiotics. This document formalizes their relationship to the theoretical framework.

**Key Claim:** Complete observability requires THREE orthogonal axes corresponding to Peirce's Firstness, Secondness, and Thirdness.

---

## 1. THE OBSERVABILITY TRIAD

### 1.1 Definition

```
OBSERVABILITY_TRIAD = (STRUCTURAL, OPERATIONAL, GENERATIVE)

WHERE:
  STRUCTURAL  = POM                  (what EXISTS)
  OPERATIONAL = observability.py     (what HAPPENS)
  GENERATIVE  = observe_session.py   (what BECOMES)
```

### 1.2 The Three Modules

| Module | File | Domain | Question |
|--------|------|--------|----------|
| **POM** | `tools/pom/projectome_omniscience.py` | Structure | "What EXISTS in PROJECTOME?" |
| **observability.py** | `standard-model-of-code/src/core/observability.py` | Runtime | "How does Collider PERFORM?" |
| **observe_session.py** | `tools/ai/observe_session.py` | Interaction | "What is being CREATED?" |

---

## 2. TARSKI HIERARCHY MAPPING

The observability modules operate at DIFFERENT LEVELS of the Tarski meta-hierarchy:

```
L₃  FOUNDATIONS ──────────────────────────────────
    │ Axioms defining the framework itself
    │ (THEORY_AXIOMS.md, FOUNDATIONS_INTEGRATION.md)
    │
L₂  THEORY ───────────────────────────────────────
    │ Tools that analyze L₀
    │ Collider = Functor: CODOME → Graph
    │
    │ ★ observability.py OBSERVES HERE
    │   (watches the analyzer run)
    │
L₁  CONTEXTOME ───────────────────────────────────
    │ Meta-language defining meaning of L₀
    │ Documentation, specs, human knowledge
    │
    │ ★ POM OBSERVES HERE (L₀ ∪ L₁)
    │   (inventories both universes)
    │
    │ ★ observe_session.py OBSERVES L₁ CREATION
    │   (captures meaning being generated)
    │
L₀  CODOME ───────────────────────────────────────
    │ Object language (source code, syntax)
    │ What can be DERIVED
    │
    └─────────────────────────────────────────────
```

### 2.1 Tarski Level Summary

| Module | Tarski Level | Relationship |
|--------|--------------|--------------|
| **POM** | L₁ (reading L₀ ∪ L₁) | Inventories the partition P = C ⊔ X |
| **observability.py** | L₂ | Monitors the L₂ tool (Collider) |
| **observe_session.py** | L₁→L₂ boundary | Captures L₁ content being created |

---

## 3. TWO ORTHOGONAL HIERARCHIES

**CRITICAL:** Tarski and Scale are ORTHOGONAL axes, not the same hierarchy.

### 3.1 The Orthogonality

```
                         TARSKI HIERARCHY (Meta-level)
                         ────────────────────────────────────────
                         L₀ Code    L₁ Meta    L₂ Theory   L₃ Found.
                         │          │          │           │
    ┌───────────────────┼──────────┼──────────┼───────────┼────
S   │ L₁₂ Universe      │          │          │           │
C   │ L₁₁ Domain        │          │   POM spans this region
A   │ L₁₀ System        │          │   ┌─────────────────┐│
L   │ L₉  Subsystem     │          │   │                 ││
E   │ L₈  Ecosystem     │          │   │    observe_     ││
    │ L₇  Service       │          │   │    session.py   ││
H   │ L₆  Package       │          │   └─────────────────┘│
I   │ L₅  File          │ ┌────────┼──────────┐          │
E   │ L₄  Container     │ │CODOME  │ observ.py│          │
R   │ L₃  Node          │ │entities│          │          │
A   │ L₂  Block         │ └────────┼──────────┘          │
R   │ L₁  Statement     │          │          │           │
C   │ L₀  Token         │          │          │           │
H   │ L₋₁ Type          │          │          │           │
Y   │ L₋₂ Byte          │          │          │           │
    │ L₋₃ Bit           │          │          │           │
    └───────────────────┴──────────┴──────────┴───────────┴────
```

### 3.2 Why This Matters

| Confusion | Reality |
|-----------|---------|
| "POM is at L₁₀" | WRONG. POM operates at Tarski L₁, spanning Scale L₃-L₁₀ |
| "observability.py is at L₆" | PARTIAL. It's at Tarski L₂, tracking stages (Scale L₄-L₆) |
| "Higher scale = more meta" | WRONG. Tarski and Scale are independent axes |

### 3.3 Correct Mapping

| Module | Tarski Level | Scale Range | Interpretation |
|--------|--------------|-------------|----------------|
| **POM** | L₁ (meta-language) | L₃-L₁₀ (Node→System) | Inventories entities AT ALL SCALES |
| **observability.py** | L₂ (meta-meta) | L₄-L₆ (Container→Package) | Observes TOOL running |
| **observe_session.py** | L₁→L₂ transition | L₅-L₁₀ (File→System) | Captures CONTEXTOME being created |

### 3.4 Scale Zones (for reference)

```
Zone           Levels    Contents
──────────────────────────────────────────────────────
EXTERNAL       L₇-L₁₂    System → Universe (context-dependent)
BOUNDARY       L₄-L₆     Container → Package (interface zone)
INTERNAL       L₋₃-L₃    Bit → Node (code-proximal)
```

**Key Insight:** Observers span MULTIPLE scale levels while operating at a SINGLE Tarski level.

---

## 4. PEIRCE TRIADIC SEMIOTICS MAPPING

### 4.1 The Fundamental Categories

Peirce's three categories form the basis of all semiosis:

| Category | Definition | Mode | Example |
|----------|------------|------|---------|
| **Firstness** | Quality, possibility, potential | Monadic | "Redness" (pure quality) |
| **Secondness** | Brute fact, actuality, existence | Dyadic | "This red thing" (actual) |
| **Thirdness** | Mediation, law, interpretation | Triadic | "This red stop sign means STOP" |

### 4.2 Observability as Peircean Categories

```
PEIRCE CATEGORY          OBSERVABILITY MODULE
───────────────────────────────────────────────────────────
FIRSTNESS (potential)    [Atoms - structural types]
                         Not directly observed; implicit in POM schema

SECONDNESS (actual)      observability.py
                         Brute facts of execution:
                         - Latency (this stage took 45ms)
                         - Memory (delta +12MB)
                         - Status (OK/FAIL/WARN)

THIRDNESS (interpretant) POM
                         Mediated relationships:
                         - Purpose field 𝒫(n)
                         - Symmetry (ORPHAN = code without meaning)
                         - Cross-universe edges (C ↔ X)

TRIADIC CYCLE ITSELF     observe_session.py
                         The moment of interpretation:
                         - Human query (Sign)
                         - Code context (Object)
                         - AI response (Interpretant)
───────────────────────────────────────────────────────────
```

### 4.3 Why Three is Necessary

```
THEOREM (Peircean Completeness):

Observation is complete IFF it covers:
  1. What IS (structure/potential) → POM
  2. What HAPPENS (brute fact) → observability.py
  3. What MEANS (interpretation) → observe_session.py

Missing any category leaves observation incomplete.
```

**Corollary:** Two observability tools are insufficient. The triad is minimal.

---

## 5. PURPOSE FIELD MAPPING

### 5.1 Axiom D6 (Crystallization)

From THEORY_AXIOMS.md:

```
𝒫_human(t) = f(context(t), need(t), learning(t))    [DYNAMIC]
𝒫_code(t) = 𝒫_human(t_commit)                       [CRYSTALLIZED]

d𝒫_human/dt ≠ 0    (human purpose always changes)
d𝒫_code/dt = 0     (code purpose frozen between commits)

DRIFT:
  Δ𝒫(t) = 𝒫_human(t) - 𝒫_code(t)
```

### 5.2 Observability and the Purpose Field

| Module | Purpose Field Aspect | What It Captures |
|--------|---------------------|------------------|
| **observe_session.py** | 𝒫_human(t) | Intent AT TIME OF INTERACTION |
| **POM** | 𝒫_code(t) | Purpose CRYSTALLIZED IN ARTIFACTS |
| **observability.py** | d𝕮/dt | Rate of change (performance) |

### 5.3 Drift Detection

```
DRIFT EQUATION:
  Δ𝒫(t) = 𝒫_human(t) - 𝒫_code(t)

OBSERVABLE VIA:
  𝒫_human(t) ← observe_session.py (captured in session logs)
  𝒫_code(t)  ← POM (measured in manifest)

DRIFT STATUS:
  Δ𝒫 ≈ 0  → SYMMETRIC (code matches intent)
  Δ𝒫 > ε  → DRIFT (code diverged from intent)
```

**Key Insight:** Session logs are the FOSSIL RECORD of 𝒫_human(t). POM measures what SURVIVED crystallization. The difference is technical debt.

---

## 6. CONSTRUCTAL LAW MAPPING

### 6.1 Axiom E1 (Flow)

From THEORY_AXIOMS.md:

```
Code evolves toward configurations that provide
easier access to flow (data, control, dependencies).

d𝕮/dt = ∇H

WHERE H = constructal health metric (flow ease)
```

### 6.2 Flow Types by Module

| Module | Flow Type | Resistance (R) | Health Signal |
|--------|-----------|----------------|---------------|
| **observability.py** | Data/control through pipeline | Latency, memory spikes | Bottleneck detection |
| **POM** | Cross-universe edges (C ↔ X) | ORPHAN/PHANTOM count | Symmetry health |
| **observe_session.py** | Question → Answer dialogue | Turns to resolution | Interaction friction |

### 6.3 Constructal Health Index

```
H_total = w₁·H_flow + w₂·H_symmetry + w₃·H_dialogue

WHERE:
  H_flow     = 1 / Σ(latency_bottlenecks)      [from observability.py]
  H_symmetry = symmetric / (orphan + phantom)   [from POM]
  H_dialogue = resolutions / total_turns        [from observe_session.py]
```

---

## 7. INTEGRATION DIAGRAM

```
┌─────────────────────────────────────────────────────────────────┐
│                    OBSERVABILITY TRIAD                          │
│                                                                 │
│   ┌───────────────┐  ┌───────────────┐  ┌───────────────┐      │
│   │ observe_      │  │     POM       │  │ observability │      │
│   │ session.py    │  │               │  │     .py       │      │
│   ├───────────────┤  ├───────────────┤  ├───────────────┤      │
│   │ GENERATIVE    │  │ STRUCTURAL    │  │ OPERATIONAL   │      │
│   │ 𝒫_human(t)    │  │ P = C ⊔ X    │  │ d𝕮/dt = ∇H   │      │
│   │ Thirdness↻    │  │ Thirdness     │  │ Secondness    │      │
│   │ Tarski L₁→L₂  │  │ Tarski L₁     │  │ Tarski L₂     │      │
│   └───────┬───────┘  └───────┬───────┘  └───────┬───────┘      │
│           │                  │                  │               │
│           ▼                  ▼                  ▼               │
│   ┌─────────────────────────────────────────────────────┐      │
│   │              UNIFIED OBSERVABILITY                   │      │
│   ├─────────────────────────────────────────────────────┤      │
│   │  DRIFT = 𝒫_human(t) - 𝒫_code(t)                    │      │
│   │  HEALTH = f(flow, symmetry, dialogue)               │      │
│   │  COMPLETENESS = Firstness ∧ Secondness ∧ Thirdness │      │
│   └─────────────────────────────────────────────────────┘      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 8. AXIOM: OBSERVABILITY COMPLETENESS

### 8.1 Formal Statement

```
AXIOM O (Observability Completeness):

For a system S with PROJECTOME P = C ⊔ X:

COMPLETE_OBSERVABILITY(S) ⟺
  ∃ structural_observer : P → Manifest        ∧  [POM]
  ∃ operational_observer : Pipeline → Metrics  ∧  [observability.py]
  ∃ generative_observer : Dialogue → Trace        [observe_session.py]

Absence of any observer leaves S partially blind.
```

### 8.2 Corollaries

```
COROLLARY O.1 (Minimal Triad):
  Two observers are insufficient for complete observability.
  The triad {STRUCTURAL, OPERATIONAL, GENERATIVE} is minimal.

COROLLARY O.2 (Peircean Necessity):
  The triad corresponds to Peirce's irreducible categories.
  Thirdness cannot be reduced to Firstness + Secondness.

COROLLARY O.3 (Drift Detectability):
  Drift Δ𝒫(t) is detectable IFF both STRUCTURAL and GENERATIVE
  observers exist. OPERATIONAL alone cannot detect drift.
```

---

## 9. IMPLEMENTATION STATUS

| Module | Status | Location | Output |
|--------|--------|----------|--------|
| **POM** | ✅ IMPLEMENTED | `context-management/tools/pom/` | YAML manifest |
| **observability.py** | ✅ IMPLEMENTED | `standard-model-of-code/src/core/` | JSON metrics |
| **observe_session.py** | ✅ IMPLEMENTED | `context-management/tools/ai/` | JSONL stream |
| **Unified Dashboard** | ❌ NOT YET | TBD | Combined view |

### 9.1 Integration Gaps

| Gap | Description | Priority |
|-----|-------------|----------|
| **No unified output** | Three separate outputs, no merger | HIGH |
| **Drift calculation** | 𝒫_human comparison not automated | MEDIUM |
| **Health index** | H_total not computed | MEDIUM |
| **Session↔POM link** | No correlation of sessions to entities | LOW |

---

## 10. REFERENCES

### 10.1 Internal

| Document | Relevance |
|----------|-----------|
| `docs/theory/FOUNDATIONS_INTEGRATION.md` | Lawvere proof, Tarski hierarchy |
| `docs/theory/THEORY_AXIOMS.md` | Axiom Groups D, E, F |
| `docs/specs/PROJECTOME_OMNISCIENCE_MODULE.md` | POM specification |
| `docs/CODESPACE_ALGEBRA.md` | Full formalization |

### 10.2 External

| Source | Relevance |
|--------|-----------|
| Peirce, C.S. - Collected Papers | Triadic semiotics foundation |
| Friston - Free Energy Principle | Purpose field dynamics |
| Bejan - Constructal Law | Flow optimization |
| Lawvere (1969) | Fixed-point theorem |

---

## CHANGELOG

| Date | Change |
|------|--------|
| 2026-01-25 | Initial canonization |

---

*This document formalizes the observability infrastructure as theoretically grounded, not ad-hoc tooling.*
