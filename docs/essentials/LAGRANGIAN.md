# LAGRANGIAN - The Incoherence Functional

> The one equation that connects everything. Every SMoC concept -- health, antimatter, orphans, concordance, drift, emergence -- derived from a single functional.

---

## The Problem

The Standard Model of Code has 15 ingredients. Each has its own algebra, its own metrics, its own rules. Antimatter doesn't formally derive from purpose. Orphans aren't defined as purpose-field consequences. Health doesn't connect to concordance. The ingredients are chopped -- not mixed.

Physics solved this with a Lagrangian: one functional from which all particle interactions, conservation laws, and coupling constants derive. The SMoC needs the same.

The existing axiom D7 already contains the answer: `d𝒫/dt = -∇Incoherence(𝕮)`. Development is gradient descent on incoherence. That IS the Lagrangian. We just need to define what Incoherence actually computes.

---

## The Incoherence Functional

```
𝓘(𝕮) = 𝓘_struct + 𝓘_telic + 𝓘_sym + 𝓘_bound + 𝓘_flow
```

Five terms. Everything else follows.

| Term | Measures | Produces |
|------|----------|----------|
| **𝓘_struct** | Graph violations (cycles, god classes) | Antimatter patterns |
| **𝓘_telic** | Purpose misalignment | Orphans + drift |
| **𝓘_sym** | Code-doc divergence | Concordance states |
| **𝓘_bound** | Layer/ring violations | Architecture warnings |
| **𝓘_flow** | Resistance to change propagation | Flow health |

---

## The Five Terms

### 𝓘_struct (Structural Incoherence)

```
𝓘_struct(G) = (1/|E|) × Σ_e violation(e)

violation(e) = 1  if e triggers AM001-AM007
             = 0  otherwise
```

**Consequence:** Antimatter patterns ARE 𝓘_struct. They are not a separate concept -- they are the computation of structural incoherence. An edge is antimatter if and only if it increases 𝓘_struct.

### 𝓘_telic (Teleological Incoherence)

```
𝓘_telic(G) = (1/|N|) × Σ_n (1 - alignment(n))

alignment(n) = cos(𝒫(n), 𝒫(parent(n)))

WHEN ‖𝒫(n)‖ = 0:  alignment = 0  (maximally incoherent)
```

**Consequence:** Orphans are nodes where 𝓘_telic contribution is maximal. A node with zero purpose magnitude has alignment = 0, contributing maximum incoherence. Orphans aren't a separate taxonomy -- they are the extremum of teleological incoherence.

**Consequence:** Drift is the time derivative: `Drift = d𝓘_telic/dt`. As human intent evolves but code stays crystallized, teleological incoherence accumulates.

### 𝓘_sym (Symmetry Incoherence)

```
𝓘_sym(𝕮) = (1/|C|) × Σ_c cost(S(c))

cost(SYMMETRIC) = 0
cost(ORPHAN)    = 1       [code without docs]
cost(PHANTOM)   = 0.5     [docs without code]
cost(DRIFT)     = d(𝒫_code, 𝒫_docs)   [proportional to divergence]
```

**Consequence:** Concordance score = 1 - 𝓘_sym. The four symmetry states (Symmetric, Orphan, Phantom, Drift) are not a separate classification -- they are the case analysis of 𝓘_sym.

### 𝓘_bound (Boundary Incoherence)

```
𝓘_bound(G) = (1/|E|) × Σ_e bv(e)

bv(e) = |layer(src) - layer(tgt)| - 1   if layer skip (AM001)
       = 1                                if reverse dep (AM002)
       = ring_violation(e)                if centrifugal (AM006)
       = 0                                otherwise
```

**Consequence:** 𝓘_bound refines 𝓘_struct for architectural violations specifically. Layer skips and reverse dependencies have magnitudes proportional to the "distance" of the violation, not just binary flags.

### 𝓘_flow (Flow Incoherence)

```
𝓘_flow(G) = (1/|N|) × Σ_n resistance(n)

resistance(n) = f(fan_out(n), CC(n), coupling(n))
```

**Consequence:** Flow health from constructal law (axiom E1) is the complement: `Flow_health = 1 - 𝓘_flow`. Refactoring is the act of reducing 𝓘_flow. Technical debt is accumulated 𝓘_flow.

---

## Derived Quantities

Every existing SMoC metric is now a view of 𝓘:

| Concept | Was | Now |
|---------|-----|-----|
| **Health** | `H = 10(0.25T + 0.25E + 0.25Gd + 0.25A)` | `H = 10 × (1 - 𝓘(𝕮))` |
| **Antimatter** | Boolean conditions AM001-AM007 | `{e : violation(e) > 0}` in 𝓘_struct |
| **Orphans** | 7-type taxonomy by connectivity | `{n : ‖𝒫(n)‖ < ε}` -- maximal 𝓘_telic contributors |
| **Concordance** | Profunctor `R: C^op × X → [0,1]` | `1 - 𝓘_sym` |
| **Drift** | `Δ𝒫(t) = 𝒫_human(t) - 𝒫_code(t)` | `d𝓘_telic/dt` |
| **Emergence** | `ε = I(System;Output) / Σ I(Comp;Output)` | `ε = 𝓘(parts) / 𝓘(whole)` -- emergence exists when the whole is more coherent than its parts |
| **Tech debt** | `∫ \|d𝒫/dt\| dt` | `∫ d𝓘/dt · dt` -- accumulated incoherence growth |

---

## The Trinity Theorem (Now Derivable)

**T2 (Conjecture → Theorem):** `Low 𝓘_flow ∧ Low 𝓘_telic ⟹ ε > 1`

**Proof sketch:** When flow incoherence is low (𝓘_flow ≈ 0), information propagates freely between components. When teleological incoherence is low (𝓘_telic ≈ 0), every node's purpose aligns with its parent's. In this regime, aggregating nodes into containers strictly reduces total incoherence because aligned purposes compose constructively -- the container's purpose is a coherent summary, not a noisy average. Therefore 𝓘(whole) < Σ 𝓘(parts), which means ε = 𝓘(parts)/𝓘(whole) > 1.

**Empirical validation:** r = 0.73 across 91 repos (L2 Principles, T2).

---

## Conservation Laws

The 6 invariants from the Codespace tuple are conserved quantities of 𝓘:

| Invariant | What It Conserves |
|-----------|-------------------|
| **P = C ⊔ X** | Every file contributes to exactly one domain of 𝓘_sym |
| **σ is total** | Every node contributes to 𝓘_telic (no unmeasured incoherence) |
| **⋃ Concordances = P** | Every file participates in 𝓘_sym (no invisible regions) |
| **λ monotonic** | 𝓘_bound = 0 when containment respects the level order |
| **κ ∈ [0,1]** | Confidence weights 𝓘_telic contributions (low confidence = discounted) |
| **Realms disjoint** | Cross-realm edges contribute to 𝓘_bound (boundary crossings) |

---

## The Equation of Motion

```
d𝒫/dt = -∇𝓘(𝕮)
```

Development is gradient descent on the Incoherence Functional.

Every commit is a step that should reduce 𝓘. When it doesn't -- when a commit increases incoherence -- that commit is either a necessary intermediate state or a mistake.

**Refactoring** = reducing 𝓘_struct + 𝓘_bound (structural cleanup)
**Documentation** = reducing 𝓘_sym (symmetry restoration)
**Purpose alignment** = reducing 𝓘_telic (teleological cleanup)
**Performance work** = reducing 𝓘_flow (flow optimization)
**Architecture** = reducing all five simultaneously

---

## What This Changes

Before: 15 standalone concepts with implicit connections.
After: 1 functional, 5 terms, 7 derived quantities, 6 conservation laws, 1 equation of motion.

The Standard Model of Code has its Lagrangian. The ingredients are mixed.

---

*Source: L0_AXIOMS.md (axiom D7), CODESPACE_ALGEBRA.md (tuple + invariants), HEALTH_MODEL_CONSOLIDATED.md (H formula), L2_PRINCIPLES.md (trinity theorem T2)*
*See also: [VISION.md](VISION.md) for the six commitments, [THEORY_WINS.md](THEORY_WINS.md) for the 13 big ideas*
