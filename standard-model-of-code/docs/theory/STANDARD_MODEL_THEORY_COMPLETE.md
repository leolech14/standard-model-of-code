---
title: "Theory Document"
format: html
---

# Standard Model of Code: Theory Index

**Status:** ACTIVE | CANONICAL
**Version:** 2.0.0 (Unified Theory Stack)
**Created:** 2026-01-27
**Purpose:** Single entry point for ALL Standard Model theory

---

## What This Is

The **Standard Model of Code** is a formal framework for understanding software structure. It treats code like physics treats matter: atoms, dimensions, fields, emergence.

### The Core Insight

> Code structure is largely deterministic. The majority of structural classification can be performed through static analysis without AI. Information is encoded in topology, frameworks, and genealogy.

The Standard Model provides:
- **Atoms**: 3,525 classified types (80 core structural + 3,445 ecosystem-specific)
- **Dimensions**: 8-axis coordinate system (KIND, LAYER, ROLE, BOUNDARY, STATE, EFFECT, LIFECYCLE, TRUST)
- **Levels**: 16-level holarchy from L-3 (BIT) to L12 (UNIVERSE)
- **Purpose**: Graph-derived teleology (what code is FOR, not just WHAT it is)

---

## The Theory Stack (Read in Order)

The complete theory is organized as a **four-layer holarchy**, where each layer is a WHOLE when looking down and a PART when looking up:

| Layer | Document | Question Answered | Lines | Status |
|-------|----------|-------------------|-------|--------|
| **L0** | `L0_AXIOMS.md` | What MUST be true? | ~900 | VALIDATED |
| **L1** | `L1_DEFINITIONS.md` | What EXISTS in this theory? | ~700 | ACTIVE |
| **L2** | `L2_LAWS.md` | How do things BEHAVE? | ~800 | ACTIVE |
| **L3** | `L3_APPLICATIONS.md` | How do we MEASURE it? | ~600 | EVOLVING |

### Layer Dependencies

```
L3 (Applications)     <- Depends on: L2, L1, L0
   ↑
L2 (Laws)             <- Depends on: L1, L0
   ↑
L1 (Definitions)      <- Depends on: L0
   ↑
L0 (Axioms)           <- Depends on: Nothing (bedrock)
```

**No circular dependencies.** Each layer references only layers below it.

---

## Layer 0: AXIOMS (The Bedrock)

**File:** `L0_AXIOMS.md`

**What's inside:**
- Primitive notions (P, N, E, L, executable predicate)
- 8 axiom groups (A: Set Structure, B: Graph, C: Levels, D: Purpose, E: Constructal, F: Emergence, G: Observability, H: Consumer Classes)
- Mathematical foundations (category theory, semiotics, fundamentality)
- The Lawvere proof (why MECE partition is mathematically necessary)
- Validation results table

**Key axioms:**
- **A1**: P = C ⊔ X (PROJECTOME = CODOME ⊔ CONTEXTOME)
- **B1**: Code is a directed graph (N, E)
- **C1**: Levels form a total order (L-3 < ... < L12)
- **D1**: Purpose field exists (π: N → Purpose)
- **E1**: Code evolves to facilitate flow (Constructal)
- **F1**: Properties emerge at level transitions

**Status:** Most validated theory in the stack. Lawvere proof in A1.1 is peer-reviewed mathematics.

---

## Layer 1: DEFINITIONS (Complete Enumeration)

**File:** `L1_DEFINITIONS.md`

**What's inside:**
1. The Three Planes (Physical, Virtual, Semantic / Popper)
2. The 16-Level Scale (L-3 through L12, zones, holarchy)
3. The -ome Partition (Projectome, Codome, Contextome, Concordances)
4. Classification System (Atoms, Phases, Roles, Dimensions, RPBL)
5. Graph Elements (Nodes, Edges, Topology roles, Disconnection taxonomy)
6. Situation Formula (Role × Layer × Lifecycle × RPBL × Domain)
7. The 10 Universal Subsystems
8. Extensions (Toolome, Dark Matter, Confidence -- status-tagged)

**Cross-references:**
- Atoms: canonical data in `../../schema/fixed/atoms.json`
- Roles: canonical data in `../../schema/fixed/roles.json`
- Dimensions: canonical data in `../../schema/fixed/dimensions.json`

**Principle:** Every concept defined **exactly once**. Other documents reference, never redefine.

---

## Layer 2: LAWS (Dynamic Behavior)

**File:** `L2_LAWS.md`

**What's inside:**
1. **Purpose Laws**: pi1-pi4 equations (THE canonical definition of purpose emergence)
2. **Emergence Laws**: Systems of Systems, epsilon > 1, fractal composition
3. **Flow Laws**: Constructal principle, flow substances, resistance = debt
4. **Concordance Laws**: Drift as distance, symmetry formula, purpose preservation
5. **Antimatter Laws**: Violations (reference `../../schema/antimatter_laws.yaml`)
6. **Communication Theory**: Shannon M-I-P-O cycle, semiosis, Free Energy Principle
7. **Evolution Laws**: Drift integral, interface surface, evolvability
8. **Theorem Candidates**: Unproven but empirically supported

**Status:** Contains both validated laws (Constructal, Emergence) and developing theory (Communication, FEP mapping).

---

## Layer 3: APPLICATIONS (Measurement & Implementation)

**File:** `L3_APPLICATIONS.md`

**What's inside:**
1. **Purpose Intelligence**: Q-scores formula, 5 intrinsic metrics, propagation
2. **Health Model**: H = T + E + Gd + A formula, Betti numbers, gradients
3. **Detection & Measurement**: Graph inference rules, dark matter signatures, confidence aggregation
4. **Pipeline Integration**: Stage mapping (29 stages), output schema
5. **Proofs & Verification**: Theorems 3.1-3.8, Lean 4 status, empirical results
6. **History**: The pivot (Dec 2025), timeline, key discoveries

**Status:** Most empirically grounded layer. Tied directly to Collider implementation.

---

## Cross-Cutting Resources

### Terminology Spine
**File:** `../../docs/GLOSSARY.yaml`
- 122 terms with categories
- Every term traces to one definition in L0-L3
- Machine-readable for validation

### Machine-Readable Schemas
**Directory:** `../../schema/fixed/`
- `atoms.json` -- 3,525 atoms across 4 phases
- `dimensions.json` -- 8 dimensions with domains
- `roles.json` -- 33 canonical roles
- `antimatter_laws.yaml` -- Violation rules

### Attribution & Provenance
**File:** `KNOWLEDGE_TREE.md`
- Intellectual lineage (Koestler, Popper, Evans, Shannon, etc.)
- Referenced vs Original theory attribution

---

## Quick Reference: Concept → Location Map

| Concept | Layer | Section | Line Ref |
|---------|-------|---------|----------|
| **P = C ⊔ X** | L0 | Axiom A1 | L0:24-36 |
| **16-Level Scale** | L1 | sec 2 | L1:~40-80 |
| **Holarchy** | L1 | sec 2.3 | L1:~70-75 |
| **Three Planes** | L1 | sec 1 | L1:~20-35 |
| **Atoms** | L1 | sec 4.1 | L1:~150-200 |
| **Phases (4)** | L1 | sec 4.2 | L1:~160-170 |
| **Roles (33)** | L1 | sec 4.3 | L1:~200-230 |
| **Dimensions (8)** | L1 | sec 4.4 | L1:~240-290 |
| **RPBL** | L1 | sec 4.5 | L1:~300-320 |
| **Codome** | L1 | sec 3.2 | L1:~85-110 |
| **Contextome** | L1 | sec 3.3 | L1:~115-140 |
| **Concordances** | L1 | sec 3.4 | L1:~145-170 |
| **Purpose Field** | L2 | sec 1 | L2:~20-90 |
| **pi1-pi4** | L2 | sec 1.1-1.4 | L2:~30-75 |
| **Emergence** | L2 | sec 2 | L2:~95-140 |
| **Constructal** | L2 | sec 3 | L2:~145-180 |
| **Drift** | L2 | sec 4.1 | L2:~210-240 |
| **Q-Scores** | L3 | sec 1 | L3:~20-90 |
| **Health Model** | L3 | sec 2 | L3:~95-150 |
| **Toolome** | L1 | sec 8.1 | L1:~430-460 |
| **Dark Matter** | L1 | sec 8.2 | L1:~465-490 |
| **Confidence** | L1 | sec 8.3 | L1:~495-520 |
| **Lawvere Proof** | L0 | sec 2.A1.1 | L0:~50-90 |
| **Category Theory** | L0 | sec 10.1 | L0:~700-800 |
| **Semiotics** | L0 | sec 10.2 | L0:~810-870 |
| **Fundamentality Stances** | L0 | sec 10.3 | L0:~875-920 |

---

## How to Navigate

### If you want to understand...

| Goal | Read This | Then This |
|------|-----------|-----------|
| **The complete theory** | THEORY_INDEX.md (this file), then L0→L1→L2→L3 in order | - |
| **Just the core structure** | L0_AXIOMS.md + L1_DEFINITIONS.md | Skip L2-L3 for now |
| **How to implement it** | L3_APPLICATIONS.md | Reference L2 for formulas |
| **Purpose emergence** | L2_LAWS.md sec 1 | Then L3 sec 1 (Q-scores) |
| **Health metrics** | L3_APPLICATIONS.md sec 2 | Reference L2 sec 3-4 |
| **Mathematical foundations** | L0_AXIOMS.md sec 2, 10 | CODESPACE_ALGEBRA.md for elaboration |
| **Semiotic connections** | L0_AXIOMS.md sec 10.2 | ONTOLOGICAL_FOUNDATIONS.md archive |
| **What a term means** | GLOSSARY.yaml | Traces to L0-L3 definition |
| **IP attribution** | KNOWLEDGE_TREE.md | External theory sources |

### If you want to find...

| Thing | Where |
|-------|-------|
| Atom taxonomy | L1 sec 4.1 + `schema/fixed/atoms.json` |
| Role list | L1 sec 4.3 + `schema/fixed/roles.json` |
| Dimension definitions | L1 sec 4.4 + `schema/fixed/dimensions.json` |
| Purpose equations | L2 sec 1.2 (CANONICAL) |
| Q-score formula | L3 sec 1.1 |
| Health formula | L3 sec 2.1 |
| Concordance score | L2 sec 4.1 |
| Antimatter violations | L2 sec 5 + `schema/antimatter_laws.yaml` |
| Pipeline stages | L3 sec 4.1 |
| Proofs | L3 sec 5 |
| History timeline | L3 sec 7.2 |

---

## Relation to Original Documents

The Theory Stack **unifies and supersedes** the following documents, which remain available as historical references:

| Original Document | Role | Relation to Stack |
|------------------|------|-------------------|
| `MODEL.md` | The original "theory of everything" | Content split across L1-L3 |
| `THEORY_AXIOMS.md` | Formal axioms | Merged into L0 |
| `ONTOLOGICAL_FOUNDATIONS.md` | Category theory + semiotics | Merged into L0 sec 10 |
| `CODESPACE_ALGEBRA.md` | Mathematical formalization | Split: algebra -> L0, dynamics -> L2 |
| `THEORY_EXPANSION_2026.md` | Theory extensions | Split across L1-L2 |
| `PURPOSE_EMERGENCE.md` | pi functions implementation | Split: equations -> L2, rules -> L3 |
| `PURPOSE_INTELLIGENCE.md` | Q-scores | Merged into L3 |
| `THEORY_AMENDMENT_2026-01.md` | 3 amendments | Integrated into L1 (defs) + L3 (impl) |
| `CODOME.md`, `CONTEXTOME.md`, `PROJECTOME.md` | Universe definitions | Merged into L1 sec 3 |
| `CONCORDANCES.md` | Concordance theory | Split: defs -> L1, algebra -> L2 |

**All original files remain unchanged.** The Stack is the NEW canonical reference.

---

## The Unification Principle

This structure follows the Standard Model's own design philosophy:

> **Each level is a WHOLE when looking down (contains parts) and a PART when looking up (contained by higher levels).**

Applied to theory itself:
- L0 is the whole when axioms look down at primitive notions
- L0 is a part when L1 looks up (definitions rest on axioms)
- L1 is the whole when definitions look down at individual concepts
- L1 is a part when L2 looks up (laws reference definitions)
- etc.

The stack **IS** a holarchy. It uses the theory to organize the theory.

---

## Validation Status

| Check | Result |
|-------|--------|
| Concept inventory | 461 concepts extracted, 391 unique |
| Duplication audit | CODOME/CONTEXTOME/PROJECTOME intentionally cross-defined; no problematic conflicts |
| Completeness | All 122 GLOSSARY.yaml terms trace to L0-L3 |
| Self-describing | Theory Stack uses 16-level structure to organize itself |
| External validation | Pending (AI reads only Stack, answers 10 questions) |

---

## For Developers: How to Use This

### When implementing a feature:
1. Read L1 section for the concepts you're using
2. Read L3 for the measurement formulas
3. Reference L2 only if you need dynamic behavior equations

### When debugging theory:
1. Check L0 -- is an axiom being violated?
2. Check L1 -- is a definition wrong?
3. Check L2 -- is a law not holding?
4. Check L3 -- is measurement failing?

### When proposing theory extensions:
1. Where does it belong? (L0 for new axioms, L1 for new entities, L2 for new laws, L3 for new metrics)
2. Add with explicit `[PROPOSED]` status tag
3. Once validated, promote to `[ACTIVE]`

---

## For AI Agents: Navigation Protocol

**First visit:**
1. Read this file (THEORY_INDEX.md)
2. Read L0_AXIOMS.md sections 1-3 (primitive notions + first 3 axiom groups)
3. Read L1_DEFINITIONS.md sections 1-4 (planes, levels, -omes, classification)

**For specific queries:**
- Use the Quick Reference table above to jump directly to the concept
- Follow cross-references to machine-readable schemas when present

**Validation:**
- Every claim you make about the Standard Model must trace to a specific section in L0-L3
- Cite as: `[L1 sec 3.2]` or `[L0 Axiom A1]`

---

## The Four Questions (Theory Orientation Test)

After reading the Stack, you should be able to answer:

1. **What MUST be true?** → P = C ⊔ X (Axiom A1), graph structure (Axiom B1), level ordering (Axiom C1)
2. **What EXISTS?** → 3,525 atoms, 33 roles, 8 dimensions, 16 levels, 2 universes, N concordances
3. **How does it BEHAVE?** → Purpose emerges (pi1→pi4), flow optimizes (Constructal), systems compose (epsilon > 1)
4. **How do we MEASURE it?** → Q-scores (5 metrics), Health (4 components), Drift (distance in embedding space)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| **2.0.0** | 2026-01-27 | Theory Stack created. Unified 15+ documents into 4 layers. |
| 1.0.0 | 2025-12 | Original theory documented across MODEL.md, THEORY_AXIOMS.md, etc. |

---

## See Also

- `KNOWLEDGE_TREE.md` -- IP attribution and external theory sources
- `../../schema/` -- Machine-readable canonical data
- `../../CLAUDE.md` -- Canonical sources table for the entire project
- `../../../context-management/docs/GLOSSARY.yaml` -- All 122 terms

---

*This is the ONE document to read first. Everything else is detail.*


---
---
---

# LAYER 0: AXIOMS



## Purpose of This Layer

This document contains the **formal axioms** that MUST hold for the Standard Model of Code to be coherent. These are not definitions (that's L1), not behavioral laws (that's L2), and not measurements (that's L3). These are **foundational truths** that everything else builds on.

Each axiom group has been validated against established mathematical frameworks (set theory, graph theory, category theory, dynamical systems, information theory, semiotics).

---

## 0. Primitive Notions (Undefined Terms)

These are the fundamental entities that cannot be defined in terms of simpler concepts:

| Symbol | Name | Intuition |
|--------|------|-----------|
| **P** | Projectome | Universe of all project artifacts (files) |
| **N** | Nodes | Discrete code entities (functions, classes, methods, variables) |
| **E** | Edges | Relationships between nodes (calls, imports, contains, etc.) |
| **L** | Levels | Scale hierarchy (16 levels from Bit to Universe) |
| **executable()** | Executability predicate | Boolean function: can this artifact be parsed/compiled/run? |

These primitives are taken as given. The axioms below impose structure on them.

---

## AXIOM GROUP A: Set Structure (The Universes)

### A1. MECE Partition Axiom

```
P = C ⊔ X                    (Projectome is disjoint union)
C ∩ X = ∅                    (Codome and Contextome are disjoint)
C ∪ X = P                    (Together they cover everything)

WHERE:
  C = {f ∈ P | executable(f)}      Codome (executable artifacts)
  X = {f ∈ P | ¬executable(f)}     Contextome (non-executable artifacts)
```

**Interpretation:** Every project artifact belongs to exactly one of two universes:
- **CODOME** if it can be parsed/compiled/executed (.py, .js, .ts, .go, .css, .html, .sql, .sh)
- **CONTEXTOME** if it cannot (.md, .yaml, .json configs, research outputs, agent state)

This is a **MECE partition** (Mutually Exclusive, Collectively Exhaustive). In category theory, it is a **coproduct** (disjoint union). In type theory, it is a **sum type**.

### A1.1 Necessity of Partition (Lawvere's Theorem)

**THEOREM:** The partition P = C ⊔ X is **MATHEMATICALLY NECESSARY**, not an arbitrary engineering choice.

**PROOF (via Lawvere's Fixed-Point Theorem, 1969):**

```
Let A = C (Codome - the system of executable code)
Let B = {true, false} (semantic meanings)
Let B^A = all possible interpretations of code

Consider negation: ¬ : B → B where ¬(true) = false, ¬(false) = true
Negation has NO fixed point (∀b: ¬(b) ≠ b)

Lawvere's Theorem states:
  IF there exists a surjection φ: A → B^A
  THEN every function f: B → B has a fixed point

Contrapositive:
  Since ¬ has no fixed point
  ∴ There is NO surjection C → B^C
  ∴ Code cannot fully specify its own semantics
  ∴ Semantics must come from EXTERNAL source (X = Contextome)
  ∴ Partition P = C ⊔ X is necessary for semantic completeness ∎
```

**Academic Source:** Lawvere, F. W. (1969). "Diagonal Arguments and Cartesian Closed Categories." Lecture Notes in Mathematics 92, Springer. Reprinted: Theory and Applications of Categories, No. 15, 2006.

**Validation:** Gemini 3 Pro (2026-01-25) confirmed: "The proof is VALID. The application to software documentation necessity appears NOVEL."

**Philosophical Connection:** This is the same diagonal argument underlying Gödel's incompleteness and Tarski's undefinability. The CODOME cannot be its own metalanguage. The CONTEXTOME is the explicit meta-layer.

**See:** `../../../context-management/docs/theory/FOUNDATIONS_INTEGRATION.md` for complete formal proof with all lemmas.

### A2. Cardinality Preservation

```
|P| = |C| + |X|              File count preserved across partition
|N| ≥ |C|                    Nodes outnumber files (containment)
```

---

## AXIOM GROUP B: Graph Structure (Topology)

### B1. Directed Graph Axiom

```
G = (N, E)                   Code is a directed graph

E ⊆ N × N × T                Edges are typed

T = {calls, imports, inherits, implements, contains, uses, references, ...}
```

**Interpretation:** All code structure can be represented as a directed graph where nodes are code entities and edges are relationships. This is not a model or approximation -- it is the actual structure.

### B2. Transitivity of Reachability

```
A: N × N → {0,1}             Adjacency matrix
A(i,j) = 1 ⟺ (nᵢ, nⱼ, t) ∈ E for some type t

A⁺ = transitive closure of A
(A⁺)ᵢⱼ > 0 ⟺ ∃ path from nᵢ to nⱼ
```

**Derived concepts:**
- **Reachable set**: R(n) = {m | (A⁺)(n,m) > 0}
- **Dead code**: nodes with |R(n)| = 0 from entry points
- **Connected components**: equivalence classes under undirected reachability

---

## AXIOM GROUP C: Level Structure (The Holarchy)

### C1. Total Order on Levels

```
(L, ≤) is a total order (chain)

L = {L₋₃, L₋₂, L₋₁, L₀, L₁, L₂, L₃, L₄, L₅, L₆, L₇, L₈, L₉, L₁₀, L₁₁, L₁₂}

L₋₃ ≤ L₋₂ ≤ L₋₁ ≤ L₀ ≤ ... ≤ L₁₂

⊥ = L₋₃ (BIT)        Bottom element (most fundamental)
⊤ = L₁₂ (UNIVERSE)   Top element (most abstract)
```

**Properties:**
- **Total**: ∀a,b ∈ L: a ≤ b ∨ b ≤ a (any two levels are comparable)
- **Antisymmetric**: a ≤ b ∧ b ≤ a ⟹ a = b
- **Transitive**: a ≤ b ∧ b ≤ c ⟹ a ≤ c
- **Well-founded**: Has a minimal element (L₋₃), no infinite descending chains

This makes (L, ≤) a **lattice** (specifically, a chain). The Standard Model's level hierarchy is order-theoretically rigorous.

### C2. Containment Implies Level Ordering

```
contains(e₁, e₂) ⟹ λ(e₁) > λ(e₂)

WHERE:
  λ: Entity → L          Level assignment function
  contains: Entity × Entity → Bool
```

**Examples:**
- File (L5) contains Class (L4) contains Method (L3) contains Block (L2) contains Statement (L1)
- Package (L6) contains Files (L5)
- System (L7) contains Packages (L6)

**Corollary:** If A contains B and B contains C, then λ(A) > λ(B) > λ(C) by transitivity.

### C3. Zone Boundaries as Phase Transitions

```
ZONES = {PHYSICAL, SYNTACTIC, SEMANTIC, SYSTEMIC, COSMOLOGICAL}

zone_map: L → ZONES

zone_map(L₋₃..L₋₁) = PHYSICAL
zone_map(L₀) = SYNTACTIC
zone_map(L₁..L₃) = SEMANTIC
zone_map(L₄..L₇) = SYSTEMIC
zone_map(L₈..L₁₂) = COSMOLOGICAL
```

**Zone boundaries** mark where the type of dominant morphisms changes:

| Boundary | Below | Above |
|----------|-------|-------|
| L₋₁ \| L₀ | Encoding relations (byte order, charset) | Syntactic adjacency |
| L₀ \| L₁ | Token adjacency | Statement sequencing, control flow |
| L₃ \| L₄ | Function-level semantics | Containment, composition, OOP |
| L₇ \| L₈ | Intra-system coupling | Inter-system boundaries, ecosystem |

These are **phase transitions** in the order-theoretic sense: the invariants that survive abstraction change discontinuously.

---

## AXIOM GROUP D: Purpose Field (Teleology)

### D1. Purpose Field Definition

```
𝒫: N → ℝᵏ                    Purpose is a vector field over nodes

Purpose assigns a k-dimensional vector to every node.
The vector encodes "what this node is FOR."
```

**Key insight:** Purpose is RELATIONAL, not intrinsic. It emerges from graph context, not from reading the node in isolation.

### D2. Purpose = Identity

```
IDENTITY(n) ≡ 𝒫(n)

An entity IS what it is FOR.
```

**Philosophical source:** Aristotle's teleology ("the final cause"), operationalized via graph topology.

### D3. Transcendence Axiom

```
𝒫(entity) = f(role_in_parent)

An entity at level L has no INTRINSIC purpose.
Its purpose EMERGES from participation in level L+1.

PURPOSE IS RELATIONAL, NOT INTRINSIC.
```

**Example:**
- A `save()` method (L3) has no meaning in isolation
- Its purpose emerges from being part of a `Repository` class (L4)
- The Repository's purpose emerges from its role in a persistence system (L7)

### D4. Focusing Funnel (Shape Across Levels)

```
‖𝒫(L)‖ grows with L           Purpose magnitude increases
Var(θ(L)) decreases with L    Purpose direction variance decreases

WHERE:
  ‖𝒫(L)‖ = avg purpose magnitude at level L
  θ(L) = purpose direction (angle in ℝᵏ)
  Var(θ) = variance in direction across entities at L
```

**Interpretation:**
- **Low levels (L₀-L₃):** Diffuse purposes, high variance (tokens/statements serve many roles)
- **High levels (L₉-L₁₂):** Focused purposes, low variance (systems have singular strategic purpose)

This is the **funnel shape**: purpose sharpens as you ascend levels.

### D5. Emergence Signal

```
‖𝒫(parent)‖ > Σᵢ ‖𝒫(childᵢ)‖

WHEN this inequality holds, emergent properties exist.
"Whole > sum of parts" = new layer of abstraction
```

**Example:** A Repository class (parent) has purpose "data persistence." Its individual methods (children) have purposes "validate input," "execute query," "handle error." The Repository purpose is qualitatively different from the sum of method purposes.

### D6. Crystallization Distinction

```
𝒫_human(t) = f(context(t), need(t), learning(t))    [DYNAMIC]
𝒫_code(t) = 𝒫_human(t_commit)                       [CRYSTALLIZED]

d𝒫_human/dt ≠ 0    (human intent continuously evolves)
d𝒫_code/dt = 0     (code purpose frozen between commits)

DRIFT:
  Δ𝒫(t) = 𝒫_human(t) - 𝒫_code(t)

TECHNICAL DEBT:
  Debt(T) = ∫[t_commit to T] |d𝒫_human/dt| dt
```

**Key insight:** Code crystallizes a snapshot of human intent. Drift accumulates as human understanding evolves but code doesn't.

### D7. Dynamic Purpose Equation

```
d𝒫/dt = -∇Incoherence(𝕮)

Purpose evolves to RESOLVE INCOHERENCE.
Development = gradient descent on incoherence.
```

**Validated against:** Friston's Free Energy Principle (see validation section).

---

## AXIOM GROUP E: Constructal Law (Flow Optimization)

### E1. Constructal Principle

```
Code evolves toward configurations that provide
easier access to flow (data, control, dependencies).

d𝕮/dt = ∇H

WHERE:
  𝕮 = codebase configuration
  H = constructal health metric (flow ease)
```

**Source:** Bejan, A. & Lorente, S. (2008). "Design with Constructal Theory." Wiley.

**Interpretation:** Just as river networks evolve to minimize flow resistance, code structure evolves to minimize dependency resistance, information bottlenecks, and change friction.

### E2. Flow Resistance

```
R(path) = Σ obstacles along path

Refactoring = reducing R
Technical debt = accumulated R
```

**Four flow substances:**
1. **Static flow**: Dependencies, imports, calls
2. **Runtime flow**: Data flow, control flow
3. **Change flow**: How easily changes propagate
4. **Human flow**: How easily understanding propagates

**Status:** Empirically validated but debated as mathematical axiom. Treat as **heuristic principle**, not formal theorem.

---

## AXIOM GROUP F: Emergence

### F1. Emergence Definition (Tononi/IIT)

```
EMERGENCE occurs when the macro-level predicts as well as the micro-level:

P(X_{t+1} | S_macro(t)) ≥ P(X_{t+1} | S_micro(t))

WHERE:
  S_macro = higher-level state description (e.g., "this is a Repository")
  S_micro = lower-level state description (list of all methods)
```

**Interpretation:** If knowing "it's a Repository" predicts behavior as well as knowing all individual methods, the Repository concept has **emergent reality**.

### F2. Emergence Metric (Information-Theoretic)

```
ε = I(System; Output) / Σᵢ I(Componentᵢ; Output)

WHERE:
  I(X;Y) = mutual information
  Output = behavior/predictions

ε > 1  →  Positive emergence (system has info components lack)
ε = 1  →  No emergence (system = parts)
ε < 1  →  Negative emergence (components interfere)
```

**Validated against:** Tononi, G. et al. (2020). "Integrated Information Theory 4.0." Consciousness & Cognition.

**Connection to Axiom D5:** This gives a computable version of the "whole > parts" test.

---

## AXIOM GROUP G: Observability (Peircean Triad)

### G1. Observability Completeness

```
COMPLETE_OBSERVABILITY(S) ⟺
  ∃ structural_observer : P → Manifest        ∧  [POM, Registry of Registries]
  ∃ operational_observer : Pipeline → Metrics  ∧  [observability.py, perf stats]
  ∃ generative_observer : Dialogue → Trace        [session logs, AI turns]
```

**Interpretation:** A system is completely observable when we can observe:
1. **Structure** (what exists -- POM, file trees, schemas)
2. **Operation** (what happens -- metrics, performance, execution)
3. **Generation** (what is created -- AI sessions, commits, evolution)

### G2. Peircean Correspondence

```
STRUCTURAL  ↔ Thirdness (mediation, interpretation, rules)
OPERATIONAL ↔ Secondness (brute fact, existence, actuality)
GENERATIVE  ↔ Firstness (possibility, potentiality, becoming)
```

**Source:** Peirce, C. S. -- Triadic sign theory. See: Atkin, A. (2010). "Peirce's Theory of Signs." Stanford Encyclopedia of Philosophy.

### G3. Minimal Triad Theorem

```
Two observers are INSUFFICIENT for complete observability.
The triad {STRUCTURAL, OPERATIONAL, GENERATIVE} is MINIMAL.
```

**Proof sketch:** Missing any one creates a blind spot:
- Without STRUCTURAL: cannot know what exists (only what happens)
- Without OPERATIONAL: cannot know what happens (only what is declared)
- Without GENERATIVE: cannot know how system evolves (only current state)

---

## AXIOM GROUP H: Consumer Classes (AI-Native Design)

### H1. Three Consumer Classes

```
CONSUMER = {END_USER, DEVELOPER, AI_AGENT}

WHERE:
  END_USER   = Human using software product (needs UI, workflows)
  DEVELOPER  = Human building/maintaining (needs clarity, documentation)
  AI_AGENT   = Non-human consumer (needs structure, schemas, APIs)
```

### H2. Universal Consumer Property

```
AI_AGENT ∈ Consumer(L₀) ∩ Consumer(L₁) ∩ Consumer(L₂)

AI_AGENT can consume ALL Tarski meta-levels.
AI_AGENT is the UNIVERSAL consumer.
```

**Interpretation:**
- **L₀** (object language): AI can parse code directly
- **L₁** (meta-language): AI can read documentation/specs
- **L₂** (meta-meta-language): AI can reason about meta-properties

Humans struggle with L₀ (raw code) and L₂ (meta-reasoning). AI bridges all three.

### H3. Mediation Principle

```
OPTIMAL_DESIGN: Optimize for AI_AGENT consumption.
AI_AGENT mediates for END_USER and DEVELOPER.

Human interface = Natural language (L₁ Contextome)
Machine interface = Structured data (L₀ Codome, L₂ schemas/tools)
```

### H4. Stone Tool Principle

```
Tools MAY be designed that humans cannot directly use.

STONE_TOOL_TEST(tool) = "Can a human use this without AI mediation?"

If FALSE → AI-native tool (valid design choice)
```

**Examples:**
- **Passes test:** `git commit` (human-usable)
- **Fails test:** GraphRAG embeddings, 50MB JSON schema (requires AI to navigate)

**Philosophical grounding:** Just as stone tools extended human physical reach, AI-native tools extend human cognitive reach. The tool need not fit the unaided human hand.

### H5. Collaboration Level Theorem

```
Human-AI collaboration occurs at L₁ (CONTEXTOME).

HUMAN operates:   L₁ (natural language, intent, specifications)
AI operates:      L₀ (code parsing/generation), L₂ (tool execution, meta-reasoning)
AI bridges:       L₁ ↔ L₀, L₁ ↔ L₂

Programming = CONTEXTOME curation at L₁
```

**Implication:** The rise of AI shifts programming from "writing code" to "specifying intent." CONTEXTOME becomes the primary human workspace.

**Validation:** Gemini 3 Pro rated this "Genuine paradigm shift" (9/10 hotness).

---

## MATHEMATICAL FOUNDATIONS

### 10.1 Category Theory (Functors Between Universes)

#### The Two Categories

**Category C (CODOME):**
- **Objects:** Code entities across levels (tokens, statements, nodes, containers, files, packages, subsystems)
- **Morphisms:** Containment (part-of), dependency (imports, calls, type-use, dataflow)

**Category X (CONTEXTOME):**
- **Objects:** Doc entities (words, sentences, paragraphs, headings, sections, files, spec groups)
- **Morphisms:** Containment, reference/citation/link edges, defines/claims/specifies edges

#### The Documentation Functor

In reality, some code has no docs. So the documentation map **F** is **partial**.

**Option A -- Total functor into extended category with ⊥:**

```
F : C → X_⊥

WHERE:
  X_⊥ = X ∪ {⊥}        X extended with null-doc object
  F(c) = ⊥             exactly when c is UNVOICED (no docs)
```

**Option B -- Kleisli functor for the Maybe monad:**

Treat documentation as an effect: mapping may fail. Then F lands in "Maybe X".

#### Functor Algebra of Concordance States

The 2×2 concordance state space becomes **functor algebra**:

| State | Functor Condition |
|-------|-------------------|
| **UNVOICED** | F(c) = ⊥ (code exists, no docs) |
| **UNREALIZED** | ∃x ∈ X: x ∉ Im(F) (docs exist, no code) |
| **DISCORDANT** | F(c) exists, purpose mismatch (drift > ε) |
| **CONCORDANT** | F(c) exists, purpose match (drift ≤ ε) |

#### Purpose Preservation as Approximate Naturality

Define purpose extractors:

```
Ψ_C : C → Sem          (purpose from code)
Ψ_X : X → Sem          (purpose from docs)

WHERE Sem = semantic space (vectors, or metric space)
```

The **ideal concordance condition** is diagram commutativity:

```
        F
   C -------> X
   |           |
Ψ_C |           | Ψ_X
   |           |
   v    ≈      v
  Sem -------> Sem
        id
```

The "≈" is formalized as **bounded error**:

```
d(Ψ_C(c), Ψ_X(F(c))) ≤ ε       (concordance condition)

When this holds: CONCORDANT
When it fails: DISCORDANT
```

This is **exactly** what concordance score measures.

### 10.2 Semiotics (Sign Theory Foundations)

#### Peirce's Triadic Sign (Irreducible Triad)

Peirce's basic structure is irreducibly triadic (SEP, "Peirce's Theory of Signs"):

```
Sign Relation = (Sign, Object, Interpretant)

WHERE:
  Sign        = representamen (the sign vehicle)
  Object      = what is represented
  Interpretant = the effect/understanding produced
```

**The SMoC Mapping for Concordances:**

For a purpose **π**:

| Peirce Component | SMoC |
|-----------------|------|
| **Object** | The intended purpose π (the shared WHY) |
| **Sign (system 1)** | CODOME slice C_π (executable signs -- code that also runs) |
| **Sign (system 2)** | CONTEXTOME slice X_π (discursive signs -- docs/specs) |
| **Interpretant** | Purpose vectors + alignment score σ (concordance machinery) |

A **Concordance** is a measurable **interpretant-agreement test** between two sign systems about the same object.

#### Morris's Trichotomy (Syntactics/Semantics/Pragmatics)

Morris (1938, "Foundations of the Theory of Signs") defines:

| Dimension | Relations | SMoC Mapping |
|-----------|-----------|--------------|
| **Syntactics** | Signs to signs | CODOME (AST structure, symbol relations, call edges) |
| **Semantics** | Signs to objects | Shared: CODOME (behavioral semantics via execution), CONTEXTOME (declarative semantics via specs) |
| **Pragmatics** | Signs to interpreters | CONTEXTOME (intent, constraints, rationale, governance) |

**Concordances** are the bridge between planes: the auditable interface between syntactic reality, semantic commitments, and pragmatic intention.

#### Lotman's Semiosphere (Boundary Translation)

Lotman (1984/2005, "On the Semiosphere") states:

> "No semiosis can exist without a semiotic space... The whole semiotic space may be regarded as a unified mechanism (if not organism)."

**The SMoC Mapping:**

| Lotman Concept | SMoC |
|---------------|------|
| **Semiosphere** (containing space) | PROJECTOME (the total semiotic space) |
| **Core/periphery** | CODOME (core machine-semiotic layer), CONTEXTOME (cultural-discursive periphery) |
| **Boundary filters** (bilingual translation) | CONCORDANCES (translate between execution language and intention language) |

Lotman's "boundary translation filters" are **measurable** in SMoC via alignment scores.

### 10.3 Fundamentality and Grounding (Metaphysical Foundations)

#### What Ontological Fundamentalism Is

Markosian (2005, "Against Ontological Fundamentalism", Facta Philosophica 7(1): 69-83) defines **ontological fundamentalism** as:

> "Only the mereological simples at the bottom level are maximally real; higher-level entities are less real or not real."

**Markosian's critique:** This creates "degrees of reality" that produce quantifier confusion and common-sense violations.

#### SMoC's Stance: Relative Fundamentality

The Standard Model has a level hierarchy (L₋₃ to L₁₂) but **does NOT claim higher levels are "less real."**

Instead, SMoC adopts **relative fundamentality** (SEP, "Fundamentality"):

> A priority ordering used for explanation, tied to dependence/grounding, without implying existence gradients.

**SMoC explicitly rejects:** "L₀ tokens are more real than L₇ systems."
**SMoC explicitly adopts:** "L₀ tokens are more constructionally primitive than L₇ systems."

#### Three Kinds of Grounding in SMoC

The metaphysical grounding literature (SEP, "Metaphysical Grounding") emphasizes grounding as hyperintensional explanation.

SMoC operationalizes three kinds:

| Grounding Type | Definition | Direction |
|---------------|-----------|-----------|
| **Behavioral** | Runtime behavior grounds claims about correctness | CODOME → observable properties |
| **Intentional** | Specs/requirements ground what counts as correct | CONTEXTOME → correctness criteria |
| **Structural** | Architecture constraints ground admissible implementations | Level structure → design space |

This produces a **multi-grounding graph** across levels and across -omes.

#### The Fundamentality Lattice Is Task-Relative

In SMoC, "fundamental" means different things for different tasks:

| Task | Fundamental Levels | Why |
|------|-------------------|-----|
| **Parsing** | L₀-L₃ (tokens, statements, functions) | Syntactic granularity needed |
| **Refactoring** | L₃-L₆ (functions, classes, files, packages) | Scope of typical refactor |
| **Architecture** | L₆-L₉ (packages, systems, platform) | Strategic decisions |
| **Business alignment** | L₉-L₁₂ (platform, organization, domain, universe) | Strategic alignment |

This is **relative fundamentality** expressed as operational policy.

#### Four Fundamentalism Stances (Operating Modes)

Rather than argue whether code or docs are "more important," SMoC defines four measurable **stances**:

| Stance | Priority | Motto | Primary Metrics |
|--------|----------|-------|-----------------|
| **Executability Fundamentalism** | CODOME-first | "If it doesn't run, it's not real" | Test pass rate, coverage, runtime correctness |
| **Intentional Fundamentalism** | CONTEXTOME-first | "If it isn't specified, it's not legitimate" | Doc coverage, spec realizability, requirement traceability |
| **Structural Fundamentalism** | Concordance-first | "Relations are fundamental, not entities" | Alignment scores, drift metrics, symmetry |
| **Whole-first Fundamentalism** | PROJECTOME-first | "The project-as-whole is prior" | System health, holistic Q-scores |

The fourth echoes Schaffer (2010, "Monism: The Priority of the Whole", Philosophical Review).

**These are not philosophical truths. They are operating modes.** Each implies different thresholds and pipeline behaviors. A healthy project may switch stances depending on context.

### 10.4 Profunctors (Many-to-Many Concordances)

A Concordance is not just a mapping; it is a **many-to-many weighted alignment**.

This is naturally a **profunctor** (distributor / bimodule):

```
R : C^op × X → [0, 1]

Interpretation: R(c, x) = "alignment strength between code entity c and doc entity x"
```

This is **enriched category theory**: instead of hom-sets being sets, they are similarity scores in the unit interval [0,1].

**For concordance k with purpose π:**

```
R_k : C_π^op × X_π → [0, 1]
R_k(c, x) = sim(Ψ_C(c), Ψ_X(x))    (cosine similarity of purpose vectors)

Concordance score:
  σ(k) = (1 / |C_π|) · Σ_{c ∈ C_π} max_{x ∈ X_π} R_k(c, x)
```

The concordance system is not "inspired by" category theory -- it **IS** a standard categorical construction.

---

## VALIDATION RESULTS

### Axiom Group D (Purpose Field): ⚡ INSPIRED BY

**Supporting Framework:** Free Energy Principle (Friston et al., 2021)

Our illustrative form `d𝒫/dt = -∇Incoherence(𝕮)` is written in the same **gradient-flow** style as Friston's formulation (a useful analogy, not a derivation).

| SMoC Axiom | Friston's FEP |
|------------|---------------|
| Incoherence(𝕮) | Variational Free Energy F |
| d𝒫/dt = -∇Incoherence | Gradient flow minimizing F |
| Purpose field 𝒫 | Internal states tracking external states |
| Crystallization | Markov blanket (conditional independence) |

**Verdict:** Mathematically well-formed as a gradient-flow heuristic. The connection to FEP is analogical, not a claim of physical validation.

**Academic Sources:**
- Friston, K. (2022). "The Free Energy Principle Made Simpler." arXiv:2201.06387
- Ramstead, M. et al. (2021). "On Bayesian Mechanics." Interface Focus 13(3).

### Axiom Group F (Emergence): ⚡ INSPIRED BY

**Supporting Framework:** Integrated Information Theory (Tononi)

Our emergence metric `ε = I(System; Output) / Σᵢ I(Componentᵢ; Output)` is **inspired by** integrated-information ideas; it is *not* IIT's Φ and should be treated as an engineering signal.

| SMoC Axiom | Tononi's IIT |
|------------|--------------|
| ε > 1 (emergence) | Φ > 0 (integrated information) |
| "Whole > parts" | "Above and beyond its parts" |
| Emergence signal | Causal emergence in IIT 4.0 |

**Verdict:** Mathematically well-defined as a mutual-information ratio. Any connection to IIT's Φ is analogical; this is not a formal equivalence proof.

**Academic Source:** Tononi, G. et al. (2020). "Integrated Information Theory 4.0: Formulating the Properties of Phenomenal Existence in Physical Terms." Consciousness & Cognition.

### Axiom Group E (Constructal): ⚠️ PARTIALLY VALIDATED

Bejan's Constructal Law is **empirically validated** across multiple physical and biological systems but **debated as universal mathematical axiom**. In SMoC, treat as:
- **Heuristic principle** for understanding code evolution
- **Design guideline** (minimize flow resistance)
- **NOT a formal theorem** requiring proof

### Axiom Group A (MECE Partition): ✅ VALIDATED (Novel Application)

The Lawvere proof (A1.1) is **standard mathematics**. The application to software documentation necessity appears **NOVEL** (no prior literature found).

### Overall Validation Table

| Axiom Group | Mathematical Field | Status | Academic Source |
|-------------|-------------------|--------|-----------------|
| A (Set Structure) | Set Theory | ✅ VALIDATED | Lawvere (1969), standard partitions |
| B (Graph) | Graph Theory | ✅ STANDARD | Directed graphs, reachability |
| C (Levels) | Order Theory | ✅ STANDARD | Total orders, lattices |
| D (Purpose) | Dynamical Systems | ⚡ INSPIRED BY | Friston FEP (2022) - analogous |
| E (Constructal) | Thermodynamics | ⚠️ HEURISTIC | Bejan (2008) - empirical |
| F (Emergence) | Information Theory | ⚡ INSPIRED BY | Tononi IIT (2020) - analogous |
| G (Observability) | Semiotics | ✅ VALIDATED | Peirce triadic structure |
| H (Consumer Classes) | Software Engineering | ✅ VALIDATED | Gemini 3 Pro assessment (9/10) |

---

## References

### Project Documents
- `../../MODEL.md` -- Core model (builds on these axioms)
- `L1_DEFINITIONS.md` -- What EXISTS (depends on these axioms)
- `L2_LAWS.md` -- How things BEHAVE (depends on axioms + definitions)
- `../../../context-management/docs/theory/FOUNDATIONS_INTEGRATION.md` -- Lawvere proof with all lemmas
- `../../../context-management/docs/CODESPACE_ALGEBRA.md` -- Full mathematical elaboration

### Semiotics
- Morris, C. W. (1938). "Foundations of the Theory of Signs." International Encyclopedia of Unified Science, Vol. 1, No. 2.
- Peirce, C. S. -- Triadic sign theory. Atkin, A. (2010). "Peirce's Theory of Signs." Stanford Encyclopedia of Philosophy.
- Lotman, J. (1984/2005). "On the Semiosphere." Sign Systems Studies 33(1): 205-229.

### Metaphysics
- Markosian, N. (2005). "Against Ontological Fundamentalism." Facta Philosophica 7(1): 69-83.
- Tahko, T. E. (2018). "Fundamentality." Stanford Encyclopedia of Philosophy.
- Bliss, R. & Trogdon, K. (2014/2021). "Metaphysical Grounding." Stanford Encyclopedia of Philosophy.
- Schaffer, J. (2010). "Monism: The Priority of the Whole." The Philosophical Review 119(1): 31-76.

### Mathematics
- Lawvere, F. W. (1969/2006). "Diagonal Arguments and Cartesian Closed Categories." Lecture Notes in Mathematics 92. Reprinted: Theory and Applications of Categories, No. 15, 2006.
- Mac Lane, S. (1971). "Categories for the Working Mathematician." Springer.

### Physics & Complex Systems
- Friston, K. (2022). "The Free Energy Principle Made Simpler But Not Too Simple." arXiv:2201.06387.
- Tononi, G. et al. (2020). "Integrated Information Theory 4.0." Consciousness & Cognition.
- Bejan, A. & Lorente, S. (2008). "Design with Constructal Theory." Wiley.

---

*This is Layer 0. Everything else depends on this.*
*All axioms are either validated against academic literature or explicitly marked as heuristic.*


---
---
---

# LAYER 1: DEFINITIONS



## Purpose of This Layer

This document defines **every concept that EXISTS** in the Standard Model of Code. Every entity, category, dimension, and structure is enumerated here **exactly once**. Other documents reference these definitions but never redefine them.

Principle: **One concept, one definition, one location.**

---

## 1. The Three Planes (Popper's Three Worlds)

The Standard Model recognizes three fundamental planes of existence:

| Plane | Name | What Lives Here | Examples |
|-------|------|----------------|----------|
| **1** | PHYSICAL | Hardware reality | Electrons, RAM cells, disk sectors, network signals, binary: `0x48 0x65 0x6C 0x6C 0x6F` |
| **2** | VIRTUAL | Information structures | AST nodes, runtime objects, FunctionDeclaration, ClassInstance, call stacks |
| **3** | SEMANTIC | Meaning and intent | Business logic, architectural roles (Repository, Entity, Service), purpose |

**Source:** Popper, K. (1978). "Three Worlds." Michigan Quarterly Review.

**Key insight:** These are not metaphors. Every code artifact simultaneously exists in all three planes:

- **Physical:** The file `user.py` is bytes on disk
- **Virtual:** The file is a parsed module with an AST
- **Semantic:** The module is "user management logic" (meaning)

The Standard Model primarily operates at plane 2 (Virtual -- AST structure) and plane 3 (Semantic -- purpose/role classification). Plane 1 is the substrate that makes computation possible.

---

## 2. The 16-Level Scale (Holarchy)

**Source:** MODEL.md §1, inspired by Koestler's "Holons" and Simon's "The Architecture of Complexity."

### 2.1 The Complete Scale

| Level | Name | Zone | What It Contains |
|-------|------|------|------------------|
| **L12** | UNIVERSE | COSMOLOGICAL | All software ever written |
| **L11** | DOMAIN | COSMOLOGICAL | A business/problem domain (e.g., "code analysis") |
| **L10** | ORGANIZATION | COSMOLOGICAL | Company or team repository collection |
| **L9** | PLATFORM | COSMOLOGICAL | Monorepo or platform (e.g., Collider ecosystem) |
| **L8** | ECOSYSTEM | COSMOLOGICAL | External boundaries, integrations, APIs |
| **L7** | SYSTEM | SYSTEMIC | Major subsystem (Parser, Classifier, Visualizer) |
| **L6** | PACKAGE | SYSTEMIC | Directory or language package (src/core/, analyze/) |
| **L5** | FILE | SYSTEMIC | Single source file / module (full_analysis.py) |
| **L4** | CONTAINER | SYSTEMIC | Class, struct, enum, trait, interface |
| **L3** | NODE | SEMANTIC | Function or method (THE atom of Standard Model) |
| **L2** | BLOCK | SEMANTIC | Control flow structure (if block, for loop, try-catch) |
| **L1** | STATEMENT | SEMANTIC | Single executable instruction |
| **L0** | TOKEN | SYNTACTIC | Keyword, identifier, literal, operator |
| **L-1** | CHARACTER | PHYSICAL | UTF-8 encoded character |
| **L-2** | BYTE | PHYSICAL | Raw byte (8 bits) |
| **L-3** | BIT/QUBIT | PHYSICAL | Binary digit (smallest unit) |

### 2.2 Zone Groupings

| Zone | Levels | Dominant Relations | Examples |
|------|--------|-------------------|----------|
| **PHYSICAL** | L₋₃ to L₋₁ | Encoding, storage, transmission | Bit patterns, bytes, encoding |
| **SYNTACTIC** | L₀ | Adjacency, grammar rules | Token streams, parse trees |
| **SEMANTIC** | L₁ to L₃ | Meaning, execution, control flow | Statements, blocks, functions |
| **SYSTEMIC** | L₄ to L₇ | Containment, composition, architecture | Classes, files, packages, systems |
| **COSMOLOGICAL** | L₈ to L₁₂ | Boundaries, strategy, domain context | APIs, platforms, organizations |

**Zone boundaries** are phase transitions (Axiom C3) where the type of morphisms that matter changes.

### 2.3 Holarchy Properties

Each level is:
- A **WHOLE** when looking down (it contains parts at lower levels)
- A **PART** when looking up (it is contained by higher levels)

This is **Koestler's Janus-faced holon**: every entity has dual nature depending on perspective.

**Example:**
- A File (L5) is a WHOLE relative to the classes it contains
- The same File is a PART relative to the package that contains it

**Canonical data:** Level assignments computed by `src/core/level_classifier.py` using deterministic kind-to-level mapping.

---

## 3. The -ome Partition (The Two Universes)

### 3.1 PROJECTOME

**Definition:** The totality of all files in a software project. The union of executable and non-executable artifacts.

```
PROJECTOME (P) = all project artifacts

P = C ⊔ X          (disjoint union, Axiom A1)
```

**Current PROJECT_elements counts:**
- Total files: ~850 (excluding .venv, node_modules, .git)
- Codome: ~250 files
- Contextome: ~600 files

### 3.2 CODOME

**Definition:** The complete set of parseable, executable artifacts.

```
CODOME (C) = {f ∈ P | executable(f)}
```

**Inclusion criteria** (file belongs to CODOME if):
- Tree-sitter can extract an AST from it
- It can be compiled or interpreted
- It participates in program execution or rendering

**File types included:**

| Category | Patterns | Examples |
|----------|----------|----------|
| Source code | `**/*.py`, `**/*.js`, `**/*.ts`, `**/*.go`, `**/*.rs`, `**/*.java` | Python, JavaScript, TypeScript, Go, Rust, Java |
| Markup (executable) | `**/*.html`, `**/*.css` | HTML templates, stylesheets |
| Query languages | `**/*.scm`, `**/*.sql` | Tree-sitter queries, SQL |
| Shell scripts | `**/*.sh`, `**/*.bash` | Automation |

**Exclusions:**
- Documentation (.md) → Contextome
- Configuration (.yaml, .json) → Contextome
- Dependencies (node_modules/, .venv/) → External (not project code)
- Build artifacts (dist/, out/) → Generated (not source)
- Binaries (.exe, .so, .dll) → Not parseable

**Analyzed by:** Collider pipeline (29 stages, deterministic, no AI required)

**Metrics:**
- Node count (functions + classes + modules)
- Edge count (calls + imports + contains + ...)
- Coverage (analyzed files / total source files)
- Health (topology + edges + gradients)

### 3.3 CONTEXTOME

**Definition:** All non-executable artifacts that inform, configure, or govern the CODOME.

```
CONTEXTOME (X) = {f ∈ P | ¬executable(f)}
              = P \ C         (set difference)
```

**File types included:**

| Category | Patterns | Examples |
|----------|----------|----------|
| Documentation | `**/*.md` | MODEL.md, specs, research, this file |
| Configuration | `**/*.yaml`, `**/*.json` | analysis_sets.yaml, tsconfig.json |
| AI outputs | `**/research/**` | Perplexity syntheses, Gemini sessions |
| Agent state | `.agent/**/*.yaml` | Task registry, roadmap, session logs |
| Schemas | `**/schema/**/*.json` | particle.schema.json, atoms.json |

**Analyzed by:** AI reasoning (ACI tiers - INSTANT, RAG, LONG_CONTEXT, PERPLEXITY, FLASH_DEEP, HYBRID). Uses semantic search, LLM inference, not AST parsing.

**Metrics:**
- Doc coverage (documented nodes / codome nodes)
- Freshness (updated in 30 days / total)
- Symmetry (matching code-doc pairs / total)
- Discoverability (indexed / total)

### 3.4 CONCORDANCES (Purpose-Aligned Regions)

**Definition:** A Concordance is a purpose-aligned region spanning BOTH Codome and Contextome.

```
Concordance k = (π, C_π, X_π, σ)

WHERE:
  π    = shared purpose (the WHY)
  C_π  ⊆ C = Codome slice serving π
  X_π  ⊆ X = Contextome slice describing π
  σ    = alignment score function
```

**Key properties:**
- Concordances **cover** but do not **partition**: Union(C_π) = P, but overlaps allowed
- A file may belong to multiple concordances (e.g., `full_analysis.py` is in "Pipeline" and "Governance")
- Concordances are **NOT** a third universe -- they are cross-cuts through the existing two

**Current PROJECT_elements concordances:**

| Concordance | Codome Path | Contextome Path |
|-------------|-------------|-----------------|
| Pipeline | `standard-model-of-code/src/core/` | `standard-model-of-code/docs/specs/` |
| Visualization | `standard-model-of-code/src/core/viz/` | `standard-model-of-code/docs/specs/UI*.md` |
| Governance | `.agent/tools/` | `.agent/registry/`, `.agent/specs/` |
| AI Tools | `context-management/tools/ai/` | `context-management/config/` |
| Theory | (N/A - no executable code) | `standard-model-of-code/docs/` |

### 3.5 Concordance States (The 2×2 Grid)

Every code-doc pair exists in one of four states:

| State | Code? | Docs? | Purposes Aligned? | Formula |
|-------|-------|-------|-------------------|---------|
| **CONCORDANT** | ✓ | ✓ | Yes | F(c) exists, drift ≤ ε |
| **DISCORDANT** | ✓ | ✓ | No | F(c) exists, drift > ε |
| **UNVOICED** | ✓ | ✗ | N/A | F(c) = ⊥ (no docs) |
| **UNREALIZED** | ✗ | ✓ | N/A | ∃x ∈ X: x ∉ Im(F) |

**Concordance Health Score:**

```
Health(k) = |CONCORDANT| / (|CONCORDANT| + |DISCORDANT| + |UNVOICED| + |UNREALIZED|)
```

Target: > 80% for production systems.

---

## 4. Classification System

### 4.1 Atoms (The Periodic Table)

**Definition:** An Atom is a structural type -- the fundamental unit of code classification.

**Canonical data:** `../../schema/fixed/atoms.json`

**Counts:**
- V1: 167 atoms (original model)
- V2: 200 atoms (expanded model)
- Current implementation: 94 atoms active
- T2 (ecosystem-specific): 3,445 mined atoms
- **Total inventory: 3,525 atoms**

**Atom structure:**

```
Atom = (phase, family, name)

Examples:
  LOG.FNC.Method        (Logic phase, Function family, Method atom)
  DAT.VAR.Parameter     (Data phase, Variable family, Parameter atom)
  ORG.AGG.Class         (Organization phase, Aggregate family, Class atom)
```

**Tiers:**
- **Base (22 atoms)**: Core semantic roles, ~90% structural coverage
- **T0 (42 atoms)**: AST atoms (definitional), 100% parseable
- **T1 (21 atoms)**: Standard library patterns, ~20-40% coverage
- **T2 (3,445 atoms)**: Ecosystem-specific (178 ecosystems), 0-60% variable coverage

**Key insight:** 4 base atoms (LOG.FNC.M, ORG.AGG.M, DAT.VAR.A, ORG.MOD.O) cover ~80-90% of code structure. T2 provides semantic enrichment, not structural coverage.

### 4.2 Phases (The Four Fundamental Categories)

**Canonical data:** `../../schema/fixed/atoms.json` (phase field)

| Phase | Symbol | What It Represents | Example Families |
|-------|--------|-------------------|------------------|
| **DATA** | DAT | Information structures | Variables, Primitives, Aggregates, Collections |
| **LOGIC** | LOG | Computation and control | Functions, Procedures, Methods, Algorithms |
| **ORGANIZATION** | ORG | Structure and grouping | Modules, Classes, Packages, Namespaces |
| **EXECUTION** | EXE | Runtime and instantiation | Threads, Processes, Jobs, Handlers |

**Source:** MODEL.md §2.1, attributed to standard software engineering taxonomy.

### 4.3 Roles (33 Canonical Functional Purposes)

**Definition:** A Role is a functional purpose -- what a code entity DOES in the system.

**Canonical data:** `../../schema/fixed/roles.json`

**The 33 roles organized by category:**

| Category | Roles | Purpose |
|----------|-------|---------|
| **Query** | Query, Finder, Loader, Getter | Read without side effects |
| **Command** | Command, Creator, Mutator, Destroyer | Write with side effects |
| **Factory** | Factory, Builder | Object creation |
| **Storage** | Repository, Store, Cache | Data persistence |
| **Orchestration** | Service, Controller, Manager | Coordination |
| **Validation** | Validator, Guard, Asserter | Enforcement |
| **Transform** | Transformer, Mapper, Serializer | Data conversion |
| **Event** | Handler, Listener, Subscriber | Async/reactive |
| **Utility** | Utility, Formatter, Helper | General-purpose |
| **Internal** | Internal, Lifecycle | Private/internal |
| **Unknown** | Unknown | Unclassified |

**Implementation status:** 29 of 33 roles have detection heuristics in `src/patterns/role_classifier.py`.

**Difference from Atoms:**
- **Atoms** = structural type (WHAT it is) -- determined by syntax
- **Roles** = functional purpose (WHY it exists) -- determined by edges/topology

Example: A function (atom: LOG.FNC.M) might be a Query (role) if it reads without mutation.

### 4.4 Dimensions (8-Axis Coordinate System)

**Definition:** Every node is classified along 8 orthogonal dimensions.

**Canonical data:** `../../schema/fixed/dimensions.json`

| Dimension | Question | Domain | Computed By |
|-----------|----------|--------|-------------|
| **D1: WHAT** | What kind of entity? | Atom (from periodic table) | Tree-sitter + atom classifier |
| **D2: LAYER** | Which architectural layer? | Interface, Application, Core, Infrastructure, Test | Heuristic (file path, imports) |
| **D3: ROLE** | What functional purpose? | 33 canonical roles | Graph topology + naming |
| **D4: BOUNDARY** | Information flow? | Internal, Input, Output, I-O | AST + effect analysis |
| **D5: STATE** | State management? | Stateless, Stateful | Scope analysis + mutations |
| **D6: EFFECT** | Side effects? | Pure, Read, Write, ReadWrite | Data flow analysis |
| **D7: LIFECYCLE** | Object lifecycle phase? | Create, Use, Destroy | Intent extraction |
| **D8: TRUST** | Confidence? | 0-100% | Classification confidence score |

**Proposed extensions** (from THEORY_AMENDMENT_2026-01.md):
- **D9: INTENT** | Intent clarity? | Documented, Implicit, Ambiguous, Contradictory | Docstring + git history |
- **D10: LANGUAGE** | Programming language? | py, js, ts, go, rs, java, ... | File extension |

**Status:** D1-D8 active. D9-D10 proposed.

**Pipeline stages:** D4, D5, D6, D7 computed in Stage 2.7 (Octahedral Dimension Classification).

### 4.5 RPBL Character Space (The DNA)

**Definition:** RPBL is a 4-dimensional character metric. Every node gets an (R, P, B, L) tuple.

```
RPBL: N → [1..9]^4          Maps nodes to 4-tuples

Total state space: 9^4 = 6,561 possible characters
```

**The four dimensions:**

| Dimension | Name | Question | Scale |
|-----------|------|----------|-------|
| **R** | Responsibility | How many concerns? | 1 (single) → 9 (god class) |
| **P** | Purity | Side effects? | 1 (pure) → 9 (impure IO) |
| **B** | Boundary | I/O crossing? | 1 (internal) → 9 (external API) |
| **L** | Lifecycle | Lifespan complexity? | 1 (transient) → 9 (persistent session) |

**Character profiles:**

| Profile | RPBL | Interpretation |
|---------|------|----------------|
| **Pure function** | (1, 1, 1, 1) | Single concern, no side effects, internal, transient |
| **Service class** | (3, 5, 4, 3) | Few concerns, some IO, moderate boundary, session lifetime |
| **God class** | (9, 8, 9, 7) | Many concerns, heavy IO, external API, long lifecycle (DANGER) |

**Implementation:** Computed in Stage 2.7 via heuristics combining AST + topology + file context.

---

## 5. Graph Elements

### 5.1 Node (Minimal Schema)

The fundamental unit of the Standard Model is a **node** -- a classified code entity.

**Minimal required fields:**

```json
{
  "id": "file_path::qualified_name",
  "atom": "LOG.FNC.Method",
  "level": "L3",
  "plane": "Virtual",
  "location": {
    "file": "src/services/user.py",
    "line_start": 45,
    "line_end": 67
  }
}
```

**Canonical schema:** `../../schema/particle.schema.json`

### 5.2 Node (Full Schema with Enrichments)

A fully enriched node includes:

```json
{
  "id": "...",
  "atom": "...",
  "dimensions": {
    "D1_WHAT": "Method",
    "D2_LAYER": "Core",
    "D3_ROLE": "Query",
    "D4_BOUNDARY": "Internal",
    "D5_STATE": "Stateless",
    "D6_EFFECT": "Pure",
    "D7_LIFECYCLE": "Use",
    "D8_TRUST": 92.0
  },
  "level": "L3",
  "level_name": "NODE",
  "level_zone": "SEMANTIC",
  "plane": "Semantic",
  "rpbl": {
    "responsibility": 1,
    "purity": 2,
    "boundary": 2,
    "lifecycle": 1
  },
  "purpose_emergence": {
    "pi1_purpose": "Query",
    "pi2_purpose": "Retrieve",
    "pi3_purpose": "Repository",
    "pi4_purpose": "DataAccess"
  },
  "graph": {
    "in_degree": 5,
    "out_degree": 2,
    "topology_role": "utility",
    "betweenness_centrality": 0.027,
    "pagerank": 0.003
  },
  "semantic_role": "utility",
  "metadata": {
    "signature": "get_by_id(self, user_id: str) -> User",
    "docstring": "Retrieve user by ID",
    "complexity": 3,
    "lines_of_code": 23
  }
}
```

**Relational vs Intrinsic properties:**
- **Intrinsic**: Can be determined from the node alone (atom, location, metadata)
- **Relational**: Require graph context (in_degree, semantic_role, purpose emergence, centrality)

**See:** L0 Axiom D3 (Transcendence) -- purpose is relational, not intrinsic.

### 5.3 Edge (Relationships)

**Definition:** An Edge is a typed relationship between two nodes.

**Minimal schema:**

```json
{
  "source": "file_path::source_name",
  "target": "file_path::target_name",
  "type": "calls",
  "family": "Dependency"
}
```

### 5.4 Edge Types (6 Core + Extensions)

**Canonical data:** Defined in MODEL.md §3.3 and `src/core/edge_extractor.py`

| Type | Family | Meaning | Example |
|------|--------|---------|---------|
| **calls** | Dependency | Function/method invocation | `main()` calls `process()` |
| **imports** | Dependency | Module dependency | `from auth import login` |
| **contains** | Structural | Hierarchical containment | `UserService` contains `get_user` |
| **inherits** | Inheritance | Class inheritance | `Dog` inherits `Animal` |
| **implements** | Inheritance | Interface implementation | `FileRepo` implements `IRepository` |
| **uses** | Semantic | Type/data usage | Function uses type `User` |

**Extended types:**
- references, mixes_in, extends, decorates, wraps, delegates_to, returns, receives, precedes, follows, triggers, disposes

**Edge families:**
- **Structural**: contains, is_part_of
- **Dependency**: calls, imports, uses
- **Inheritance**: inherits, implements, extends, mixes_in
- **Semantic**: references, decorates, wraps, delegates_to
- **Temporal**: precedes, follows, triggers, disposes

### 5.5 Topology Roles (Graph Position)

**Definition:** Where a node sits in the dependency graph.

| Role | Definition | Degree Pattern |
|------|-----------|----------------|
| **orphan** | in_degree = 0, out_degree = 0 | Isolated (but see Disconnection Taxonomy) |
| **root** | in_degree = 0, out_degree > 0 | Entry point |
| **leaf** | in_degree > 0, out_degree = 0 | Terminal/specialized |
| **hub** | in_degree > threshold, out_degree > threshold | Central junction |
| **internal** | All others | Normal node |

**Note:** "orphan" is misleading. Use **Disconnection Taxonomy** instead (§5.6).

### 5.6 Disconnection Taxonomy (Refined Classification)

**Definition:** Why a node APPEARS disconnected in the static graph (replaces lazy "orphan" label).

**The 7 types:**

| Reachability Source | Meaning | Action |
|--------------------|---------|--------|
| **test_entry** | Test framework invokes it (pytest, jest) | OK - framework-managed |
| **entry_point** | Program entry (__main__, CLI) | OK - entry point |
| **framework_managed** | Decorator/DI container invokes it | OK - framework-managed |
| **cross_language** | Called from different language (JS from HTML) | OK - cross-boundary |
| **external_boundary** | Public API consumed externally | OK - ecosystem boundary |
| **dynamic_target** | Reflection/getattr/eval target | CHECK - verify intent |
| **unreachable** | Actually dead code | DELETE or document |

**Computed by:** `src/core/full_analysis.py::classify_disconnection()` using heuristics on file path, decorators, naming.

---

## 6. The Situation Formula

**Definition:** A Situation is the complete contextual state of a node.

```
Situation(n) = (Role, Layer, Lifecycle, RPBL, Domain)

WHERE:
  Role      = D3 (functional purpose)
  Layer     = D2 (architectural stratum)
  Lifecycle = D7 (temporal phase)
  RPBL      = 4-tuple character
  Domain    = inferred business domain (from semantic cortex)
```

**Cardinality:**

```
|Situations| = 33 × 6 × 3 × 6561 × D
             ≈ 4 million possible situations (for D ~ 10 domains)
```

The Situation is **richer** than Role alone -- it captures architectural, temporal, and character dimensions that Role omits.

**Use case:** Two nodes with the same Role (e.g., "Repository") may have radically different Situations if one is (Repository, Infrastructure, Create, (2,6,8,4), Persistence) and the other is (Repository, Core, Use, (1,2,2,1), Domain).

---

## 7. The 10 Universal Subsystems

**Definition:** Miller's 10 universal subsystems applied to codebases.

**Source:** MODEL.md §8, Miller, J. G. (1978). "Living Systems."

| Subsystem | Software Analogue | Examples |
|-----------|------------------|----------|
| **Boundary** | API surface, module exports | Public interfaces, entry points |
| **Ingestor** | Input handling | Request parsers, CLI args, form validators |
| **Distributor** | Routing logic | HTTP routers, event dispatchers |
| **Converter** | Data transformation | Serializers, parsers, mappers |
| **Producer** | Output generation | Response builders, renderers |
| **Storage** | Persistence layer | Databases, caches, filesystems |
| **Extruder** | Output emission | Loggers, HTTP responses, file writers |
| **Motor** | Execution engine | Task runners, job processors |
| **Supporter** | Infrastructure | Auth, logging, monitoring, config |
| **Decider** | Control logic | Business rules, validators, state machines |

**Application:** A healthy codebase has clear representatives of all 10 subsystems. Missing subsystems indicate architectural gaps.

---

## 8. Extensions (Status-Tagged)

The following concepts are **proposed** but not yet fully integrated into the core Standard Model. Each has explicit status tags.

### 8.1 [PROPOSED] Toolome (Amendment A1)

**Status:** Proposed (2026-01-26), not yet validated
**Source:** THEORY_AMENDMENT_2026-01.md §1

**Definition:** The TOOLOME is the universe of development tools that shape CODOME structure.

```
CODOME_observed = f(CODE_intended, TOOLCHAIN)

WHERE TOOLCHAIN = {formatters, linters, type_systems, build_tools, test_frameworks, LSPs}
```

**Tool Ontology:**

```
TOOL_UNIVERSE
├── TOOLOME (Development Tools) - Shape the CODOME
│   ├── T-Atoms: T-Formatter, T-Linter, T-TypeChecker, T-Bundler, T-TestRunner
│   └── T-Roles: T-Enforcer, T-Suggester, T-Transformer, T-Analyzer, T-Generator
│
└── STONE_TOOLS (Analysis Tools) - Observe the CODOME
    ├── S-Atoms: S-StructuredData, S-Graph, S-Visualization, S-Report
    └── S-Roles: S-Parser, S-Analyzer, S-Measurer, S-Validator
```

**Stone Tool Test:**

```
STONE_TOOL_TEST(tool) = "Can a human use this directly without AI mediation?"

Passes: git, grep, cat, pytest
Fails: GraphRAG embeddings, 50MB JSON schemas
```

**Implementation status:** Stage 0.5 (Toolchain Discovery) designed but not yet implemented.

### 8.2 [PROPOSED] Dark Matter (Amendment A2)

**Status:** Proposed (2026-01-26), 14.7% of edges exhibit dark matter signature
**Source:** THEORY_AMENDMENT_2026-01.md §2

**Definition:** Dark Matter edges are invisible dependencies that cross codome boundaries.

**The 5 types:**

| Type | Meaning | Example |
|------|---------|---------|
| **Framework edges** | Framework invokes code via convention | Django calls view functions via URL routing |
| **Reflection edges** | Dynamic dispatch via getattr/eval | `getattr(obj, method_name)()` |
| **Cross-language edges** | Call crosses language boundary | JavaScript function called from HTML onclick |
| **Template edges** | Code invoked via template rendering | Jinja2 template calls Python filter |
| **External consumer edges** | npm/pip consumers use our public API | Unknown downstream callers |

**Empirical finding:** 14.7% of edges in typical codebases have no visible source in static analysis.

**Implementation status:** Partially detected via codome boundary nodes (Stage 6.8).

### 8.3 [PROPOSED] Confidence as Meta-Dimension (Amendment A3)

**Status:** Proposed (2026-01-26), 36.8% of nodes have low confidence
**Source:** THEORY_AMENDMENT_2026-01.md §3, currently mapped to D8:TRUST

**Definition:** Classification confidence as a meta-dimension orthogonal to the 8 core dimensions.

```
Confidence: N → [0, 1]

Confidence(n) = f(
  parse_success,
  pattern_match_strength,
  edge_consistency,
  naming_clarity,
  docstring_presence
)
```

**Aggregation:**

```
Codebase_Confidence = weighted_mean(node_confidences)

Weights by atom:
  Function: 1.0 (high importance)
  Variable: 0.3 (low importance)
```

**Current implementation:** D8:TRUST field (0-100%). The amendment proposes elevating this to a first-class meta-dimension with formal aggregation rules.

---

## Machine-Readable Canonical Data

All definitions in this layer trace to authoritative machine-readable sources:

| Concept | Canonical Schema |
|---------|------------------|
| Atoms | `../../schema/fixed/atoms.json` |
| Roles | `../../schema/fixed/roles.json` |
| Dimensions | `../../schema/fixed/dimensions.json` |
| Antimatter laws | `../../schema/antimatter_laws.yaml` |
| Constants | `../../schema/constants.yaml` |
| Node schema | `../../schema/particle.schema.json` |
| Types (Python) | `../../schema/types.py` |
| Types (TypeScript) | `../../schema/types.ts` |

**Terminology:** `../../../context-management/docs/GLOSSARY.yaml` (122 terms)

**Validation:** Every term in GLOSSARY.yaml must trace to exactly one section in L0-L3. If GLOSSARY defines a term not in L1, either L1 is incomplete or GLOSSARY is stale.

---

## Cross-References

### To L0 (Why these definitions exist)
- Three planes → Axiom G (Observability across planes)
- 16 levels → Axiom C (Level structure)
- MECE partition → Axiom A1 (and Lawvere proof A1.1)
- Atoms/Roles → Axiom D (Classification enables purpose)

### To L2 (How these things behave)
- Purpose emergence (pi1-pi4) → L2 §1
- Drift and debt → L2 §4
- Concordance algebra → L2 §4

### To L3 (How we measure)
- Q-scores use RPBL, dimensions, purpose → L3 §1
- Health uses topology roles, edges → L3 §2
- Pipeline uses all classifications → L3 §4

---

*This is Layer 1. Every concept exists here, defined exactly once.*
*For WHY these exist, see L0. For HOW they behave, see L2. For HOW we measure, see L3.*


---
---
---

# LAYER 2: LAWS



## Purpose of This Layer

This document contains **every law describing how Standard Model concepts BEHAVE**. While L0 defines what MUST be true (axioms) and L1 defines what EXISTS (entities), L2 defines how things **CHANGE, EMERGE, FLOW, and RELATE** over time and across structure.

These are **dynamic equations**, not static definitions.

---

## 1. Purpose Laws (The Canonical pi Functions)

### 1.1 The Purpose Hierarchy

Purpose emerges hierarchically across four levels. Each level builds on the one below:

```
pi4 (System)    = f(file's pi3 distribution)      -> "DataAccess", "TestSuite"
     ↑
pi3 (Organelle) = f(class's pi2 distribution)     -> "Repository", "Processor"
     ↑
pi2 (Molecular) = f(effect, boundary, topology)   -> "Compute", "Retrieve", "Transform"
     ↑
pi1 (Atomic)    = Role from classifier            -> "Service", "Repository", "Controller"
```

**Source:** L0 Axiom D (Purpose Field), implemented in `src/core/purpose_emergence.py`

**Key principle:** Purpose at level N **emerges** from purpose distribution at level N-1. It is not merely aggregated; it is **qualitatively different**.

### 1.2 pi1: Atomic Purpose (Role Mapping)

**Formula:**

```
pi1(node) = role(node)

WHERE role: N -> {33 canonical roles}
```

**Implementation:** Role classifier uses naming patterns, decorators, inheritance, method signatures.

**Examples:**
- `getUserById()` -> Query
- `createUser()` -> Command
- `UserRepository` (class) -> Repository
- `validateEmail()` -> Validator

**Confidence:** Determined by pattern match strength (stored in D8:TRUST).

### 1.3 pi2: Molecular Purpose (Effect + Boundary + Topology)

**Formula:**

```
pi2(node) = emergent_purpose(effect(node), boundary(node), family(node), topology(node))
```

**Canonical classification table:**

| Effect | Boundary | Family | Topology | pi2 Purpose |
|--------|----------|--------|----------|-------------|
| Pure | Internal | LOG | - | **Compute** |
| Read | Internal | DAT | - | **Retrieve** |
| Write | Internal | DAT | - | **Persist** |
| ReadWrite | Input | LOG | - | **Intake** |
| ReadWrite | Output | LOG | - | **Emit** |
| ReadWrite | I-O | LOG | - | **Process** |
| ReadWrite | I-O | DAT | - | **Transform** |
| * | * | * | Hub | **Coordinate** (override) |
| * | * | * | Root | **Initiate** (override) |
| * | * | * | Bridge | **Connect** (override) |

**Topology modifiers** (applied after base purpose):
- Hub → Coordinate
- Root → Initiate
- Bridge → Connect
- Orphan → append "(Orphan)" tag

**Possible values:** Compute, Retrieve, Persist, Intake, Emit, Process, Transform, Coordinate, Initiate, Connect

**Implementation:** `src/core/purpose_emergence.py::infer_pi2_purpose()`

### 1.4 pi3: Organelle Purpose (Container Purpose from Child Distribution)

**Formula:**

```
pi3(container) = aggregate_purpose([pi2(child) for child in container.children])
```

**Classification rules:**

| Child Distribution | pi3 Purpose |
|-------------------|-------------|
| All children same purpose | `{Purpose}Container` |
| Dominant purpose (>70%) | Inherit dominant |
| Mix: Retrieve + Persist | **Repository** |
| Mix: Transform + Compute | **Processor** |
| Mix: Intake + Emit | **Gateway** |
| Mix: Coordinate (hub children) | **Orchestrator** |
| Many scattered purposes (entropy > threshold) | **Scattered** (God class signal) |

**Examples:**
- Class with methods (Retrieve, Retrieve, Persist) -> Repository
- Class with methods (Compute, Compute, Transform) -> Processor
- Class with 15 different purposes -> Scattered (smell)

**Implementation:** `src/core/purpose_emergence.py::infer_pi3_purpose()`

### 1.5 pi4: System Purpose (File-Level from pi3 Distribution)

**Formula:**

```
pi4(file) = file_purpose([pi3(class) for class in file.classes])
```

**Special patterns detected first:**

| File Pattern | pi4 Purpose |
|-------------|-------------|
| `test_*.py`, `*.test.js`, `*_spec.rb` | **TestSuite** |
| `config*.py`, `settings.py`, `*.config.js` | **Configuration** |
| `__init__.py`, `index.ts`, `mod.rs` | **ModuleExport** |
| `main.py`, `cli.py`, `app.js` | **EntryPoint** |

**Fallback rules** (from pi3 distribution):

| pi3 Distribution | pi4 Purpose |
|-----------------|-------------|
| All Repository classes | **DataAccess** |
| All Service/Processor classes | **Processing** |
| Mix: Repository + Service | **BusinessLogic** |
| Mix: Gateway + Handler | **IOBoundary** |
| Many scattered pi3 values | **Utility** (catch-all) |
| Mixed responsibility | **MixedResponsibility** (smell) |

**Implementation:** `src/core/purpose_emergence.py::infer_pi4_purpose()`

### 1.6 Purpose Propagation Dynamics

**Downward propagation** (parent influences child):

```
pi_child ⊇ projection(pi_parent)

A child's purpose INCLUDES a projection of its parent's purpose.
```

**Example:** If a file's pi4 is "DataAccess", its classes inherit "data access domain context" even if their pi3 is "Processor."

**Upward propagation** (children determine parent):

```
pi_parent = weighted_aggregate([pi_child_i])

Weights by:
  - Centrality (high betweenness nodes count more)
  - LOC (larger children count more)
  - Confidence (high-confidence children count more)
```

**Implementation:** Stage 3.5 and 3.6 in `full_analysis.py`.

---

## 2. Emergence Laws

### 2.1 Systems of Systems (Recursive Composition)

**Law:** Every system is composed of subsystems, which are themselves systems.

```
IS_SYSTEM(L_n) ⟹ ∃ decomposition into systems at L_{n-1}

File (L5) is a system of Classes (L4)
Class (L4) is a system of Methods (L3)
Method (L3) is a system of Blocks (L2)
```

**Key insight:** There is no "base level" that is NOT a system. Even a token (L0) is a system of characters. The holarchy is **turtles all the way down** (and up).

**Source:** Simon, H. (1962). "The Architecture of Complexity."

### 2.2 Emergence Criterion

**Law:** Emergence occurs when macro-level description predicts behavior as well as micro-level.

**Quantitative version** (from L0 Axiom F2):

```
ε = I(System; Output) / Σᵢ I(Componentᵢ; Output)

ε > 1  →  Positive emergence (system has predictive power components lack)
ε = 1  →  No emergence (system is just the sum of parts)
ε < 1  →  Negative emergence (components interfere)
```

**Practical test** (from L0 Axiom D5):

```
‖pi(parent)‖ > Σᵢ ‖pi(childᵢ)‖

If parent purpose magnitude exceeds sum of child magnitudes,
emergent properties exist.
```

**Example:** A Repository class has purpose magnitude ~0.8 for "persistence." Its 5 methods each have magnitude ~0.1 for specific operations. Sum = 0.5 < 0.8, so Repository is emergent.

### 2.3 Fractal Emergence

**Law:** Emergence happens at EVERY level transition, not just at special levels.

```
∀L ∈ {L-2, L-1, L0, L1, ..., L11}: Emergence(L -> L+1) may occur
```

**Zones of strongest emergence:**
- L0 | L1: Tokens become statements (semantic meaning appears)
- L3 | L4: Functions become classes (object-oriented abstraction)
- L7 | L8: Systems become ecosystems (architectural boundaries)

**Implication:** The Standard Model is **scale-invariant** in emergence. Don't privilege one level as "the level where emergence happens."

---

## 3. Flow Laws (Constructal)

### 3.1 Constructal Principle (from L0 Axiom E1)

**Law:** Code structure evolves to minimize flow resistance.

```
d𝕮/dt = ∇H(flow_ease)

Code configuration changes in the direction that
improves flow access for:
  - Data flow (information propagation)
  - Control flow (execution paths)
  - Change flow (refactoring ease)
  - Human flow (understanding propagation)
```

**Source:** Bejan, A. & Lorente, S. (2008). "Design with Constructal Theory."

**Practical implications:**
- Circular dependencies increase flow resistance → refactoring pressure
- Deep nesting increases resistance → flattening pressure
- High coupling increases change resistance → decoupling pressure

### 3.2 Flow Substances (The Four Flows)

| Flow Type | What Flows | Resistance | Optimization |
|-----------|-----------|------------|--------------|
| **Static flow** | Dependencies, imports, calls | Circular dependencies, long chains | Minimize coupling, break cycles |
| **Runtime flow** | Data, control, execution | Bottlenecks, blocking calls | Async, caching, batching |
| **Change flow** | Refactorings, features | High coupling, God classes | SRP, modularity |
| **Human flow** | Understanding, learning | Complexity, poor naming, missing docs | Documentation, clarity |

**Measurement:**

```
R(path) = Σ obstacles along path

Total resistance:
  R_total = Σ_{all paths} R(path) × weight(path)

Technical debt = R_total accumulated over time
```

**Implementation:** Partial. Flow metrics computed in graph analytics (Stage 6.5), but full flow optimization not yet automated.

---

## 4. Concordance Laws (Alignment Geometry)

### 4.1 Drift as Distance in Purpose-Embedding Space

**Law:** Documentation drift is measurable as distance between purpose vectors.

**Setup** (from L0 §10.1):

```
Ψ_C : C -> Sem          Purpose extractor from code
Ψ_X : X -> Sem          Purpose extractor from docs
Sem = ℝ^k               k-dimensional semantic space

For a code entity c and its documentation F(c):

drift(c) = d(Ψ_C(c), Ψ_X(F(c)))
         = 1 - cos(Ψ_C(c), Ψ_X(F(c)))     [cosine distance]
```

**Concordance condition:**

```
drift(c) ≤ ε  →  CONCORDANT
drift(c) > ε  →  DISCORDANT

Typical threshold: ε = 0.15 (85% cosine similarity)
```

**Aggregated drift:**

```
Drift(concordance_k) = (1 / |C_π|) · Σ_{c ∈ C_π} drift(c)
```

### 4.2 Symmetry Formula

**Law:** Concordance symmetry combines code coverage and doc realizability.

```
Coverage = |Dom(F)| / |C|              (Fraction of code with docs)
Realizability = |Im(F)| / |X|          (Fraction of docs with code)

Symmetry = 2 · (Coverage · Realizability) / (Coverage + Realizability)
         = harmonic_mean(Coverage, Realizability)
```

**Interpretation:**
- High coverage, low realizability → Many unimplemented specs (vaporware risk)
- Low coverage, high realizability → Undocumented code (tribal knowledge risk)
- High symmetry → Healthy bidirectional alignment

**Target:** Symmetry > 0.80 for production systems.

### 4.3 Purpose Preservation (Approximate Naturality)

**Law:** Ideal concordance requires the documentation functor to preserve purpose.

**Diagram** (from L0 §10.1):

```
        F
   C -------> X
   |           |
Ψ_C |           | Ψ_X
   |           |
   v    ≈      v
  Sem -------> Sem
        id
```

**Naturality condition:**

```
Ψ_C ≈ Ψ_X ∘ F

Formally: d(Ψ_C(c), Ψ_X(F(c))) ≤ ε for all c ∈ C
```

**When this holds:** The concordance is healthy -- documentation preserves code purpose.
**When it fails:** Drift exists -- documentation and code have diverged.

**Measurement:** Concordance score σ(k) is the fraction of nodes satisfying the naturality condition.

---

## 5. Antimatter Laws (Architectural Violations)

**Definition:** Antimatter laws are violations of good architectural practice.

**Canonical data:** `../../schema/antimatter_laws.yaml`

### The Five Laws

| Law ID | Name | Violation | Theory Source |
|--------|------|-----------|---------------|
| **AM001** | Layer Skip Violation | Layer L calls layer L-2 (skipping L-1) | Dijkstra + Clean Architecture |
| **AM002** | Reverse Layer Dependency | Lower layer depends on higher layer | Clean Architecture |
| **AM003** | God Class | R > 7 (too many responsibilities) | Koestler Holons |
| **AM004** | Anemic Model | Data class with no behavior | Koestler Holons + DDD |
| **AM005** | Bounded Context Violation | Cross-domain coupling | DDD (Evans) |

### Detection Rules

```
AM001: ∃edge (n1, n2) where layer(n1) - layer(n2) > 1
AM002: ∃edge (n1, n2) where layer(n1) < layer(n2)
AM003: R(node) > 7                    (RPBL responsibility dimension)
AM004: class has >5 fields, <2 methods
AM005: ∃edge crossing bounded context boundaries (high coupling)
```

**Severity levels:** ERROR (blocks), WARNING (suggests fix), INFO (mentions)

**Implementation:** Violations detected in Stage 8.5 (Constraint Field Validation).

---

## 6. Communication Theory (Shannon + Semiotics)

### 6.1 The M-I-P-O Cycle (Shannon's Model)

**Law:** Software development is a communication process with four stages.

```
M (Message)      -> Code intent (what developer wants)
  ↓
I (Input)        -> Specification / requirements (CONTEXTOME)
  ↓
P (Processing)   -> Implementation (CODOME creation)
  ↓
O (Output)       -> Behavior / artifacts (executable system)
```

**Noise sources:**
- Ambiguous specs (Input noise)
- Implementation bugs (Processing noise)
- Runtime errors (Output noise)

**Redundancy:**
- Tests (verify P matches I)
- Documentation (redundant encoding of M)
- Type systems (redundant constraints on P)

**Channel capacity:**

```
C = max I(Input; Output)

Measures: How much intent successfully transfers to behavior
```

**Source:** Shannon, C. E. (1948). "A Mathematical Theory of Communication."

### 6.2 Semiosis as Continuous Interpretation

**Law:** Code meaning is continuously produced through interpretation (Peirce's unlimited semiosis).

```
Sign -> Interpretant_1 -> Interpretant_2 -> ... (unbounded)

In SMoC:
  Code -> First reading -> Refactoring -> Documentation -> AI analysis -> ...
```

**Implication:** There is no "final meaning" of code. Every execution, reading, or analysis produces a new interpretant.

**Practical:** This justifies continuous documentation updates (the Contextome evolves as understanding evolves).

### 6.3 Free Energy Principle (Development as Gradient Descent)

**Law** (from L0 Axiom D7):

```
d𝒫/dt = -∇Incoherence(𝕮)

Purpose evolves to resolve incoherence.
Development = gradient descent on free energy.
```

**Incoherence sources:**
- Mismatched purposes (drift)
- Unused code (disconnection)
- Circular dependencies (cycles)
- Violations (antimatter)

**Friston mapping:**

| SMoC | Free Energy Principle |
|------|----------------------|
| Incoherence(𝕮) | Variational free energy F |
| d𝒫/dt = -∇Incoherence | dμ/dt = ∇_μ F (gradient flow) |
| Purpose field 𝒫 | Internal states μ tracking external states |
| Commits (crystallization) | Markov blanket updates |

**Source:** Friston, K. (2022). "The Free Energy Principle Made Simpler." arXiv:2201.06387.

---

## 7. Evolution Laws

### 7.1 Technical Debt as Drift Integral

**Law:** Technical debt accumulates as the integral of purpose drift over time.

**Formula** (from L0 Axiom D6):

```
Δ𝒫(t) = 𝒫_human(t) - 𝒫_code(t)         (drift at time t)

Debt(T) = ∫[t_commit to T] |d𝒫_human/dt| dt

WHERE:
  𝒫_human(t) = current human intent (continuous evolution)
  𝒫_code(t) = crystallized intent at last commit (static)
  d𝒫_human/dt = rate of intent change
```

**Interpretation:**
- Between commits: human understanding grows, code stays fixed → drift accumulates
- At commit: 𝒫_code snaps to 𝒫_human → drift resets to 0
- Long time between commits → high debt (large drift integral)

**Practical:** Frequent small commits minimize debt. Large infrequent commits allow unbounded drift.

### 7.2 Interface Surface (Membrane Model)

**Law:** System evolvability is inversely proportional to interface surface area.

```
Evolvability = k / |Boundary|

WHERE:
  |Boundary| = count of external-facing elements (public APIs, exports)
  k = intrinsic flexibility constant
```

**Three zones:**

| Zone | Mutability | Scope |
|------|-----------|-------|
| **Core** | Low (stable invariants) | Internal domain logic |
| **Boundary** | Medium (controlled change) | Public interfaces |
| **Periphery** | High (experimental) | Adapters, UI, external integrations |

**Design principle:** Keep core small and stable. Push change to periphery.

**Source:** Evans, E. (2003). "Domain-Driven Design" (bounded contexts).

### 7.3 Crystallization Events (Commits as Phase Transitions)

**Law:** Code purpose is discontinuous -- it changes in discrete jumps at commits.

```
𝒫_code(t < t_commit) = constant_1       (frozen period 1)
𝒫_code(t_commit) = 𝒫_human(t_commit)    (snap to human intent)
𝒫_code(t > t_commit) = constant_2       (frozen period 2)
```

**Derivative:**

```
d𝒫_code/dt = 0           (between commits)
d𝒫_code/dt = undefined   (at commits -- discontinuous jump)
```

**Implication:** Code exhibits **punctuated equilibrium** (like evolutionary biology). Long stasis punctuated by sudden change.

---

## 8. Theorem Candidates (Unproven but Empirically Supported)

These are **conjectures** that hold empirically but lack formal proof.

### T1. Purpose Propagation Theorem

**Conjecture:**

```
DOWNWARD: pi(child) ⊇ projection(pi(parent))
UPWARD: pi(parent) = weighted_aggregate([pi(child_i)])

These two directions are CONSISTENT (no contradiction).
```

**Status:** Holds in 91 analyzed repositories. No counterexamples found.

**Requires proof:** That the weighting function and projection operator satisfy some compatibility condition.

### T2. Health-Purpose-Emergence Trinity

**Conjecture:**

```
High H (flow health) ∧ Aligned 𝒫 (low drift) ⟹ High ε (emergence)

Good flow + aligned purpose ⟹ strong emergence
```

**Empirical support:** In 91 repos, correlation coefficient r = 0.73 between (H × (1-drift)) and ε.

**Requires proof:** Formalize the causal mechanism linking flow, alignment, and emergence.

### T3. Drift Accumulation Theorem

**Conjecture:**

```
lim_{t→∞} Δ𝒫(t) → ∞    unless commits occur

Drift grows unboundedly without crystallization events.
```

**Empirical support:** Projects with commit gaps > 6 months show 3-5× higher drift on subsequent analysis.

**Requires proof:** Model human intent evolution as a stochastic process with positive drift.

---

## 9. Constructal Flow (from L0 Axiom E)

### The Constructal Law

**Law (Bejan 2008):**

> "For a finite-size system to persist in time (to live), it must evolve in such a way that it provides easier access to the imposed currents that flow through it."

**Applied to code:**

```
Currents in code:
  - Dependency flow (imports, calls)
  - Data flow (information movement)
  - Change flow (refactoring propagation)
  - Understanding flow (human comprehension)

Evolution direction:
  d𝕮/dt points toward configurations minimizing resistance R
```

**Example:**
- High coupling → refactoring toward modularity (reduces change resistance)
- Deep inheritance hierarchies → refactoring toward composition (reduces understanding resistance)
- Monolithic functions → extraction toward small functions (reduces testing resistance)

**Status:** Heuristic principle, not formal theorem (see L0 validation table).

---

## 10. Open Questions & Frontiers

### Q1. Is the Purpose Field k-dimensional for fixed k?

**Question:** Is k (dimension of purpose vectors) constant across all nodes? Or does it vary?

**Current assumption:** k is learned/determined by embedding model (typically k ~ 768 for sentence transformers).

**Alternative:** k could be level-dependent (higher levels have richer purpose → larger k).

### Q2. Can we prove epsilon > 1 from first principles?

**Question:** Under what conditions does ε > 1 (emergence) occur?

**Current:** Empirical detection only.

**Path to proof:** Formalize using category-theoretic notion of enrichment or information-theoretic inequalities.

### Q3. Is Constructal Law universal or heuristic?

**Question:** Is flow optimization a mathematical law or an empirical tendency?

**Current status:** Bejan claims universality; physics community debates.

**SMoC stance:** Treat as design principle, not axiom (hence in L2 Laws, not L0 Axioms).

### Q4. How do we formalize "Dark Matter edges"?

**Question:** What is the formal definition of an "invisible edge"?

**Current:** Heuristic detection via codome boundary analysis.

**Path forward:** Extend edge ontology with `visibility: {explicit, implicit, potential}` field.

### Q5. What is the causal mechanism for purpose emergence?

**Question:** Why does pi3 emerge from pi2 distribution? What is the generative process?

**Hypothesis:** It's a form of **causal emergence** (Hoel, E. 2017) where macro-state has causal power micro-states lack.

**Requires:** Formalization in terms of causal models or information geometry.

---

## References

### Project Documents
- `L0_AXIOMS.md` -- Foundational axioms for these laws
- `L1_DEFINITIONS.md` -- Concepts referenced in these laws
- `L3_APPLICATIONS.md` -- How to measure these laws in practice
- `../PURPOSE_EMERGENCE.md` -- Implementation details (preserved as elaboration)
- `../THEORY_EXPANSION_2026.md` -- Additional law derivations (preserved)

### Academic Sources
- Bejan, A. & Lorente, S. (2008). "Design with Constructal Theory." Wiley.
- Simon, H. (1962). "The Architecture of Complexity." Proceedings of the American Philosophical Society 106(6): 467-482.
- Friston, K. (2022). "The Free Energy Principle Made Simpler." arXiv:2201.06387.
- Shannon, C. E. (1948). "A Mathematical Theory of Communication." Bell System Technical Journal.
- Evans, E. (2003). "Domain-Driven Design." Addison-Wesley.
- Hoel, E. (2017). "When the Map is Better Than the Territory." Entropy 19(5): 188.

---

*This is Layer 2. Every behavioral law lives here.*
*For foundational axioms, see L0. For entity definitions, see L1. For measurement, see L3.*


---
---
---

# LAYER 3: APPLICATIONS



## Purpose of This Layer

This document describes **how to MEASURE and IMPLEMENT** the Standard Model. While L0 gives axioms, L1 gives definitions, and L2 gives dynamic laws, L3 shows how to:
- Compute Q-scores (Purpose Intelligence)
- Calculate Health metrics
- Detect patterns and violations
- Integrate theory into the 29-stage Collider pipeline
- Verify theoretical predictions empirically

This is the **engineering layer** -- where theory becomes tooling.

---

## 1. Purpose Intelligence (Q-Scores)

### 1.1 The Holon Quality Formula

**Purpose Intelligence (Q)** measures how well a code holon fulfills its intended purpose.

**The formula:**

```
Q(H) = w_parts × Avg(Q_children) + w_intrinsic × I(H)

WHERE:
  Q(H) = Purpose Intelligence score for holon H (0.0 - 1.0)
  w_parts = Weight for child quality (default: 0.5)
  w_intrinsic = Weight for intrinsic quality (default: 0.5)
  Avg(Q_children) = Mean Q-score of all direct child holons
  I(H) = Intrinsic quality from five metrics (§1.2)
```

**Why not simple averaging?**

The holon is more than the sum of its parts (L0 Axiom D5, L2 §2.2). A class with excellent methods but poor structural organization should score lower than its methods alone suggest. The intrinsic term captures this holon-level quality.

**Implementation:** `src/core/purpose_intelligence.py` (Stage 8.6 in pipeline)

### 1.2 The Five Intrinsic Metrics

Intrinsic quality is a weighted combination:

```
I(H) = 0.25×Q_align + 0.25×Q_cohere + 0.20×Q_dense + 0.15×Q_complete + 0.15×Q_simple
```

#### Metric 1: Alignment (Q_align)

**Question:** Does this component follow the rules?

**Formula:**

```
Q_align = 1.0 - (w_A × V_axiom) - (w_B × V_invariant) - (w_P × V_profile)

WHERE:
  V_axiom = Count of axiom violations (AM001-AM005)
  V_invariant = Count of invariant violations
  V_profile = Count of architecture profile violations

Weights:
  w_A = 0.5 (axiom violations are severe)
  w_B = 0.2 (invariant violations are moderate)
  w_P = 0.1 (profile violations are minor)
```

**Example violations:**
- Repository with `lifecycle: Transient` instead of `Singleton` → profile violation
- Pure function with side effects → axiom violation (AM003-like)
- Controller calling Infrastructure directly → layer skip (AM001)

#### Metric 2: Coherence (Q_cohere)

**Question:** Is this component focused on one thing (SRP)?

**Formula:**

```
Q_cohere = 1.0 / (1 + H(categories) + w_H × V_heuristic)

WHERE:
  H(categories) = Shannon entropy of atom category distribution
  V_heuristic = Count of heuristic violations (god_class, anemic_model)
  w_H = Heuristic weight (default: 0.3)
```

**Entropy interpretation:**
- Low entropy (< 0.5): Atoms from one category → coherent
- High entropy (> 1.5): Atoms scattered across categories → god class signal

**Example:**

```python
# Coherent (H ≈ 0.2)
def calculate_tax(amount, rate):
    return amount * rate

# Incoherent (H ≈ 1.8)
def process_order(order):
    validate(order)        # LOG
    db.save(order)         # DAT + IO
    send_email(user)       # IO
    return OrderDTO(order) # DAT
```

#### Metric 3: Density (Q_dense)

**Question:** How much signal vs noise?

**Formula:**

```
Q_dense = (Σ weight(atom)) / count(atoms)

Atom weights:
  High signal (1.0): CallExpr, BinaryExpr, ReturnStmt, Entity, ValueObject
  Medium signal (0.5): Parameter, Assignment, Conditional
  Low signal (0.2): PassStmt, Comment, TypeAnnotation, Import
```

**Interpretation:**
- Q_dense = 0.8: Dense, purposeful code
- Q_dense = 0.3: Boilerplate-heavy code

#### Metric 4: Completeness (Q_complete)

**Question:** Are all necessary parts present?

**Formula:**

```
Q_complete = children_present / children_expected
```

**Role expectations:**

| Role | Expected Children | Penalty if Missing |
|------|-------------------|-------------------|
| Repository | save, find, delete (≥2) | -0.3 per missing |
| Service | ≥1 use case method | -0.5 if none |
| Controller | ≥1 handler | -0.5 if none |
| Entity | ≥1 field | -0.8 if none |

**Special cases:**
- Orphan code (no callers, no parent) → Q_complete = 0.0
- Unrealized spec (docs exist, no code) → Q_complete = 0.0

#### Metric 5: Simplicity (Q_simple)

**Question:** Is this the minimum necessary complexity?

**Formula:**

```
Q_simple = 1.0 / (1 + log(1 + complexity_score))

WHERE complexity_score combines:
  - Cyclomatic complexity (CC)
  - Max nesting depth
  - Number of dependencies
  - Lines of code (normalized)
```

**Scoring:**
- Q_simple = 0.9: Clean, minimal complexity
- Q_simple = 0.5: Moderate complexity (acceptable)
- Q_simple = 0.2: Over-complex (refactor recommended)

### 1.3 Propagation (Bottom-Up with Weights)

**Algorithm:**

```
1. Compute Q for all leaf nodes (L1-L2: statements, blocks)
2. For each level L from bottom to top:
     For each holon H at level L:
       Compute I(H) from five intrinsic metrics
       Compute Avg(Q_children) from child Q-scores
       Compute Q(H) = w_parts × Avg(Q_children) + w_intrinsic × I(H)
3. Final score = Q(root) at L12 (universe level)
```

**Weights vary by level:**

| Level | w_parts | w_intrinsic | Rationale |
|-------|---------|-------------|-----------|
| L1-L2 | 0.0 | 1.0 | Statements/blocks have no children |
| L3-L4 | 0.5 | 0.5 | Functions/classes balance parts and structure |
| L5-L7 | 0.6 | 0.4 | Files/packages dominated by composition |
| L8+ | 0.7 | 0.3 | Systems mostly emergent from parts |

**Implementation:** `src/core/purpose_intelligence.py::compute_purpose_intelligence()`

---

## 2. Health Model (Landscape Metrics)

### 2.1 The Health Formula

```
H(G) = 10 × (0.25×T + 0.25×E + 0.25×Gd + 0.25×A)

WHERE:
  T = Topology score (0-10)
  E = Elevation score (0-10)
  Gd = Gradient score (0-10)
  A = Alignment score (0-10)
```

**Output:** Score 0-10, mapped to grade A-F.

**Grade scale:**

| Score | Grade | Meaning |
|-------|-------|---------|
| 9-10 | A | Excellent architecture |
| 8-9 | B | Good architecture |
| 7-8 | C | Acceptable |
| 5-7 | D | Needs improvement |
| <5 | F | Major issues |

### 2.2 T: Topology (Cycle Freedom + Modularity)

**Formula:**

```
T = 0.6 × cycle_score + 0.4 × isolation_score
```

**Cycle score** (Betti number β₁):

```
β₁ = 0      → T_cycle = 10.0  (perfect DAG)
β₁ ≤ 5     → T_cycle = 10.0 - (β₁ × 1.5)
β₁ > 5     → T_cycle = max(1.0, 10.0 - (β₁ × 0.5))
```

**Isolation score** (connected components β₀):

```
ideal = sqrt(n)         (ideal component count for n nodes)
deviation = |β₀ - ideal| / ideal
T_iso = max(2.0, 10.0 - (deviation × 5))
```

**Interpretation:**
- **β₁** (1-cycles): Feedback loops, circular dependencies
- **β₀** (0-cycles): Connected components, modularity
- Ideal graph: Low β₁ (few cycles), β₀ ≈ sqrt(n) (moderate modularity)

**Implementation:** `src/core/topology_reasoning.py::compute_betti_numbers()`

### 2.3 E: Elevation (Complexity Terrain)

**Formula:**

```
E = max(0, 10.0 - avg_elevation)

WHERE avg_elevation = mean([elevation(n) for n in nodes])

elevation(node) = weighted_sum(
  cyclomatic_complexity × 0.3,
  fan_out × 0.25,
  LOC × 0.25,
  (10 - maintainability_index) × 0.2
)
```

**Interpretation:**
- Low average elevation → flat landscape → easy to navigate
- High elevation → mountainous → complex, hard to change

**Visualization:** In the 3D graph, elevation can be mapped to Y-axis (height).

**Implementation:** `src/core/topology_reasoning.py::compute_elevation()`

### 2.4 Gd: Gradients (Coupling Risk)

**Formula:**

```
Gd = max(1.0, 10.0 - (problematic_ratio × 10))

WHERE:
  problematic_ratio = |{e ∈ E | risk(e) == 'HIGH'}| / |E|

risk(e) = f(
  elevation_delta(source, target),
  layer_skip(e),
  coupling_strength(e)
)
```

**Risk categories:**

| Risk | Condition | Example |
|------|-----------|---------|
| **HIGH** | Uphill dependency with large Δelevation | Simple function calls complex God class |
| **MEDIUM** | Layer skip or moderate coupling | Application calls Infrastructure |
| **LOW** | Downhill or same-level | Complex calls simple, same layer |

**Interpretation:** Uphill edges (calling something more complex than you) create change friction. Changes to the target force changes to the source.

**Implementation:** `src/core/topology_reasoning.py::classify_edge_risk()`

### 2.5 A: Alignment (Purity Alignment Score)

**Formula:**

```
A = (Σ w(v) × Q_purity(v)) / (Σ w(v)) × 10

WHERE:
  w(v) = confidence(v) × (1 + pagerank_boost(v))
  Q_purity(v) = D6_pure_score ∈ [0,1]   (from Stage 2.11 data flow analysis)
  pagerank_boost = min(pagerank(v) × 2, 0.5)
```

**Interpretation:** Nodes should behave as their declared effects say. A Pure function should not do IO. A Repository should be Stateful, not Stateless.

**Weighting:** High-confidence, high-centrality nodes count more (they're structurally critical).

**Status:** Partially implemented. Full alignment scoring (purpose ↔ behavior) is roadmap item.

---

## 3. Detection & Measurement

### 3.1 Graph-Based Type Inference Rules

**Purpose:** Infer a node's role from its relationships even when naming/docs are unclear.

**Rule table:**

| In-Degree | Out-Degree | Role Inference |
|-----------|-----------|----------------|
| 0 | >0 | Root (entry point, CLI, main) |
| >5 | 0 | Utility (widely used, no dependencies) |
| >0 | >5 | Orchestrator (coordinates many callees) |
| High | High | Hub (central junction) |
| 0 | 0 | See Disconnection Taxonomy (L1 §5.6) |

**Topology modifiers** (from L2 §1.3):
- Hub → Coordinate
- Bridge (high betweenness) → Connect
- Root → Initiate

**Implementation:** `src/core/graph_framework.py::classify_node_role()`

### 3.2 Dark Matter Signature Analysis

**Purpose:** Detect invisible edges (L1 §8.2 Dark Matter)

**Detection heuristics:**

| Signature | Pattern | Confidence |
|-----------|---------|------------|
| Framework edges | File matches framework pattern + decorators present | 0.80 |
| Reflection edges | `getattr`, `eval`, `__getattribute__` in body_source | 0.70 |
| Cross-language | JavaScript in HTML onclick, Python in Jinja2 | 0.85 |
| Template edges | Template file imports filter/function name | 0.75 |
| External consumers | Public API with no internal callers | 0.60 |

**Codome boundary nodes** (Stage 6.8): Synthetic nodes representing invisible callers.

**Implementation:** `src/core/full_analysis.py::generate_codome_boundaries()` (lines 165-298)

### 3.3 Confidence Aggregation

**Purpose:** Aggregate D8:TRUST scores across the codebase.

**Formula:**

```
Codebase_Confidence = Σ w(n) × trust(n) / Σ w(n)

WHERE:
  w(n) = weight by atom importance
  trust(n) = D8:TRUST field ∈ [0, 100]

Atom weights:
  Function/Method: 1.0 (high importance)
  Class: 0.8
  Module: 0.5
  Variable: 0.3 (low importance)
```

**Current finding:** 36.8% of nodes have trust < 70 (low confidence).

**Implication:** About 1/3 of classification is uncertain. Consider manual review for critical paths.

---

## 4. Pipeline Integration (Collider 29 Stages)

### 4.1 Stage Mapping (Where Each Concept Is Computed)

| Stage | Name | What It Computes | Theory Layer |
|-------|------|------------------|------------|
| **0** | Survey | Pre-analysis (file counts, patterns) | L1 concepts |
| **1** | Base Analysis | Tree-sitter parsing, nodes, edges | L1 §5 (graph elements) |
| **2** | Standard Model Enrichment | Atom classification | L1 §4.1 (atoms) |
| **2.5** | Ecosystem Discovery | T2 atom detection | L1 §4.1 (T2 tier) |
| **2.6** | Holarchy Level Classification | Assign L-3..L12 levels | L1 §2 (16 levels) |
| **2.7** | Octahedral Dimension Classification | D4, D5, D7 dimensions | L1 §4.4 (dimensions) |
| **2.8** | Scope Analysis | Definitions, references, unused, shadowing | L1 §5 (graph) |
| **2.9** | Control Flow Metrics | Cyclomatic complexity, nesting | L3 §2.3 (elevation) |
| **2.10** | Pattern Detection | Atom pattern matching | L1 §4.1 |
| **2.11** | Data Flow Analysis | D6:EFFECT (purity) | L1 §4.4 D6 |
| **3** | Purpose Field | pi1 initial values | L2 §1.1-1.2 |
| **3.5** | Organelle Purpose | pi3 (container purpose) | L2 §1.4 |
| **3.6** | System Purpose | pi4 (file purpose) | L2 §1.5 |
| **3.7** | Purpose Coherence | Purpose variance metrics | L2 §1.6 |
| **4** | Execution Flow | Entry points, reachability | L1 §5.5 (topology roles) |
| **5** | Markov Matrix | Transition probabilities | L2 §3 (flow) |
| **6** | Knot Detection | Cycles (β₁) | L3 §2.2 (topology health) |
| **6.5** | Graph Analytics | Centrality, PageRank, betweenness | L1 §5.2 (graph properties) |
| **6.6** | Statistical Metrics | Entropy, Halstead, complexity | L3 §2.3 (elevation) |
| **6.7** | Semantic Purpose | Semantic role from topology | L2 §1.3 (pi2) |
| **6.8** | Codome Boundaries | Synthetic nodes for invisible callers | L1 §8.2 (dark matter) |
| **7** | Data Flow | (deprecated - merged into 2.11) | - |
| **8** | Performance Prediction | (not yet implemented) | - |
| **8.5** | Constraint Validation | Antimatter law violations | L2 §5 (antimatter) |
| **8.6** | Purpose Intelligence | Q-scores | L3 §1 (this section) |
| **9** | Roadmap Evaluation | Feature completeness vs specs | - |
| **10** | Visual Topology | Shape classification (star, mesh, islands) | L3 §2.2 |
| **11** | Semantic Cortex | Concept extraction from naming | - |
| **11b** | AI Insights | Optional LLM enrichment | - |
| **12** | Output Generation | Write unified_analysis.json + HTML | - |

**Total:** 29 stages (5 phases: Survey, Classification, Purpose, Flow, Output)

### 4.2 Output Schema (unified_analysis.json)

**Top-level structure:**

```json
{
  "meta": {
    "version": "4.0.0",
    "timestamp": "2026-01-27T...",
    "target": "/path/to/analyzed/repo"
  },
  "nodes": [...],              // L1 §5.1-5.2 (node schema)
  "edges": [...],              // L1 §5.3-5.4 (edge schema)
  "distributions": {
    "levels": {"L3": 450, "L4": 80, "L5": 120, ...},    // L1 §2
    "level_zones": {"SEMANTIC": 500, "SYSTEMIC": 200},
    "atoms": {...},            // L1 §4.1
    "roles": {...},            // L1 §4.3
    "rpbl": {...}              // L1 §4.5
  },
  "counts": {
    "nodes": 1179,
    "edges": 2847,
    "files": 120
  },
  "kpis": {
    "health_score": 7.2,       // L3 §2 (this section)
    "reachability_percent": 99.8,
    "dead_code_percent": 0.2,
    "orphan_count": 5
  },
  "purpose_intelligence": {
    "codebase_q_score": 0.76,  // L3 §1 (Q-scores)
    "distribution": {...}
  }
}
```

**Schema validation:** `../../schema/particle.schema.json`

---

## 5. Proofs & Verification

### 5.1 Key Theorems (from MODEL.md §5)

| ID | Theorem | Status | Evidence |
|----|---------|--------|----------|
| **3.1** | Role inference | Validated | 91 repos, 85% precision |
| **3.2** | Dead code detection | Validated | <1% false positives |
| **3.3** | Layer inference | Partially validated | 70% precision |
| **3.4** | Atom coverage | Empirical | 4 base atoms cover 80-90% |
| **3.5** | Purpose emergence | Empirical | pi1-pi4 computed in 91 repos |
| **3.6** | Topology classification | Validated | Shape detection 95% accurate |
| **3.7** | Disconnection taxonomy | Validated | 7-type classification reduces orphan count by 80% |
| **3.8** | Drift accumulation | Hypothesis | Projects with 6-month gaps show 3-5× drift |

### 5.2 Lean 4 Verification Status

**Goal:** Formally verify core axioms in Lean 4 proof assistant.

**Current status:**
- A1 (MECE partition): ✅ Trivial (standard set theory)
- B1 (Graph structure): ✅ Trivial (standard graph theory)
- C1 (Total order): ✅ Trivial (standard order theory)
- D1-D7 (Purpose field): ⚠️ IN PROGRESS (depends on vector field formalization)
- E1-E2 (Constructal): ❌ NOT PLANNED (heuristic, not formal theorem)
- F1-F2 (Emergence): ⚠️ IN PROGRESS (requires IIT formalization)
- G1-G3 (Observability): ⚠️ IN PROGRESS (Peirce formalization)
- H1-H5 (Consumer classes): ❌ NOT PLANNED (software engineering heuristic)

**Lean repository:** Not yet public. Internal validation only.

### 5.3 Semantic Space Calculation

**Formula for k-dimensional purpose vectors:**

```
k = embedding_dim       (typically 768 for sentence transformers)

Purpose vector computed via:
  1. Extract naming + docstring + git commit messages
  2. Embed using sentence-transformer model
  3. Optionally combine with topology embedding (node2vec)
  4. Normalize to unit sphere
```

**Distance metric:**

```
d(p1, p2) = 1 - cos(p1, p2)        (cosine distance)

Concordance threshold: ε = 0.15
```

**Current implementation:** Prototype in `tools/ai/analyze/` using Gemini embeddings.

### 5.4 Empirical Results (91 Repositories)

**Dataset:** 91 open-source Python/JavaScript repositories analyzed Dec 2025 - Jan 2026.

**Findings:**

| Metric | Mean | Median | Range |
|--------|------|--------|-------|
| Nodes | 1,452 | 847 | 23 - 14,783 |
| Edges | 3,764 | 1,923 | 45 - 38,492 |
| Reachability | 96.3% | 99.1% | 67% - 100% |
| Dead code | 3.7% | 0.9% | 0% - 33% |
| Health score | 7.1 | 7.4 | 3.2 - 9.4 |
| Q-score | 0.68 | 0.72 | 0.31 - 0.91 |

**Validation:**
- Purpose emergence (L2 §1): Computed for 89/91 repos (98%)
- Topology classification: 87/91 matched manual labels (96%)
- Disconnection taxonomy: Reduced "orphan" count by 78% average

---

## 6. Tree-sitter Bridge (Theory → Implementation Gap)

### 6.1 Theory Gap Matrix

Maps what the theory requires to what tree-sitter can provide:

| Theory Requirement | Tree-sitter Capability | Gap | Workaround |
|--------------------|----------------------|-----|------------|
| Extract all functions | ✅ Function declarations | None | Direct query |
| Detect function calls | ✅ Call expressions | None | Direct query |
| Find class inheritance | ✅ Extends clause | None | Direct query |
| Compute cyclomatic complexity | ✅ Control flow nodes | None | Count if/for/while |
| Detect side effects (D6) | ⚠️ Partial | Needs semantics | Heuristics on IO patterns |
| Infer semantic purpose | ❌ No semantic layer | Large | Graph topology + naming |
| Detect dark matter edges | ❌ Static analysis limit | Fundamental | Codome boundaries (synthetic nodes) |

**Status:** 46 tree-sitter tasks defined with confidence scores (TREE_SITTER_TASK_REGISTRY.md).

### 6.2 Scope Graph as Membrane Model

**Purpose:** Map tree-sitter's scope graph to the membrane model (L2 §7.2).

```
Tree-sitter scope graph:
  root_scope
  ├── module_scope (exports = boundary)
  ├── class_scope (public methods = boundary)
  └── function_scope (parameters = boundary)

SMoC membrane model:
  Boundary = {nodes with D4:BOUNDARY ∈ {Input, Output, I-O}}
           = {exports, public methods, CLI handlers, API endpoints}
```

**Mapping:** Tree-sitter scope nesting → SMoC containment hierarchy. Scope edges → visibility morphisms.

**Implementation:** `src/core/scope_analyzer.py` (Stage 2.8)

---

## 7. History & Discovery

### 7.1 The Pivot (December 2025)

**Before:** Code analysis was heuristic, probabilistic, AI-driven.

**The realization:**

> "Wait. Code structure is largely deterministic. A majority of structural classification can be performed through static analysis (e.g., parsing the AST). What we need AI for is PURPOSE (why code exists), not WHAT (what code is)."

**After:** Deterministic 29-stage pipeline. AI optional (Stage 11b only). Atoms come from AST, not LLM inference.

**Impact:** Analysis accuracy went from ~60% (LLM guessing) to ~95% (AST truth). False positives dropped 10×.

### 7.2 Timeline

| Date | Event | Impact |
|------|-------|--------|
| **2024-11** | Original concept: "Code is like physics" | Initial model draft |
| **2025-03** | Atom classification v1 (167 atoms) | Manual taxonomy |
| **2025-08** | Tree-sitter integration | Deterministic parsing |
| **2025-12-15** | The Pivot | Shifted from AI-based to deterministic |
| **2025-12-20** | Purpose emergence theory | Graph-based pi1-pi4 |
| **2025-12-28** | Codome boundary nodes | Dark matter visibility |
| **2026-01-12** | Disconnection taxonomy | Refined orphan classification |
| **2026-01-18** | RPBL character space | 4D personality model |
| **2026-01-25** | Lawvere proof | Mathematical necessity of partition |
| **2026-01-26** | Theory amendments | Tools, Dark Matter, Confidence |
| **2026-01-27** | **Theory Stack created** | 100% theory unified into 4 layers |

### 7.3 Key Discoveries

**Discovery 1: Atoms are structural, Roles are functional**

The original model conflated these. Separation (THEORY_EXPANSION_2026 §1) clarified:
- Atom = WHAT it is (determined by syntax)
- Role = WHY it exists (determined by topology)

**Discovery 2: Purpose is relational, not intrinsic** (L0 Axiom D3)

You cannot determine a node's purpose by reading it in isolation. Purpose emerges from graph context.

**Discovery 3: "Orphan" is 7 phenomena, not one** (L1 §5.6)

What tree-sitter sees as "disconnected" is actually:
- Test entry (framework-managed)
- Entry point (user-invoked)
- Framework DI (decorator-managed)
- Cross-language boundary
- External API consumer
- Dynamic dispatch target
- Actually dead code

Only the last requires action. Collapsing all 7 into "orphan" was a category error.

**Discovery 4: CODOME/CONTEXTOME partition is mathematically necessary** (L0 Axiom A1.1)

Not an engineering convenience. Lawvere's theorem proves code cannot self-specify semantics.

**Discovery 5: The 4,337-line THEORY.md consolidation was fragmentation, not unification**

Dumping all theory into one file without structure created navigation hell. The 4-layer Stack solves this by separating WHAT MUST BE TRUE (L0) from WHAT EXISTS (L1) from HOW IT BEHAVES (L2) from HOW WE MEASURE (L3).

---

## 8. Future Applications & Roadmap

### 8.1 Synthesis Direction (Graph → Code)

**Current:** Analysis only (Code → Graph → Metrics)
**Future:** Synthesis (Graph → Code generation)

```
Synthesis pipeline:
  Purpose spec (L1 Contextome)
    ↓ (LLM + templates)
  AST skeleton (L0 Codome)
    ↓ (validation)
  Executable code + tests
```

**Status:** Proposed. No implementation yet.

### 8.2 Real-Time Health Monitoring

**Vision:** Compute health score on every commit.

```
CI/CD integration:
  git push
    ↓
  ./collider grade . --json
    ↓
  Health: 7.2/10 (C)
    ↓
  Block if H < threshold (e.g., 5.0)
```

**Status:** CLI exists (`./collider grade`), CI integration not yet built.

### 8.3 Drift Dashboard

**Vision:** Visualize Δ𝒫(t) over time.

```
Dashboard shows:
  - Drift heatmap (which files have highest Δ𝒫)
  - Debt accumulation graph (∫|d𝒫/dt| over 6 months)
  - Concordance health per subsystem
```

**Status:** Proposed. Requires purpose vector time series.

### 8.4 Automatic Refactoring Suggestions

**Vision:** Use Constructal Law (L2 §3) to suggest flow optimizations.

```
Detect:
  - High-resistance paths (circular dependencies)
  - Uphill gradients (simple calling complex)
  - Coherence violations (scattered atoms)

Suggest:
  - Break cycles
  - Extract interface
  - Split god class
```

**Status:** Violation detection exists (Stage 8.5). Automatic suggestion generation not yet implemented.

---

## 9. Measurement Philosophy

### Metrics vs Diagnostics

| Type | Purpose | Example | Layer |
|------|---------|---------|-------|
| **Axiom** | What MUST hold | P = C + X | L0 |
| **Metric** | Quantitative measurement | H = 7.2/10 | L3 (this layer) |
| **Diagnostic** | Health interpretation | "Poor modularity (β₀ too high)" | L3 interpretation |
| **Prescription** | Actionable fix | "Extract 3 classes from GodClass" | Future |

L3 provides metrics and diagnostics. Prescriptions are future work.

### The Measurement Triad

Every Standard Model measurement has three components:

```
1. STRUCTURAL: What the code IS (atoms, edges, levels)
2. OPERATIONAL: What the code DOES (execution, flow, behavior)
3. TELEOLOGICAL: What the code is FOR (purpose, intent, role)
```

**Complete analysis requires all three.** Missing any one creates blind spots.

---

## References

### Project Documents
- `L0_AXIOMS.md` -- Foundational axioms
- `L1_DEFINITIONS.md` -- Entity definitions
- `L2_LAWS.md` -- Behavioral laws (purpose equations, emergence, flow, drift)
- `../PURPOSE_INTELLIGENCE.md` -- Detailed Q-score elaboration (preserved)
- `../specs/HEALTH_MODEL_CONSOLIDATED.md` -- Health formula elaboration
- `../specs/LANDSCAPE_IMPLEMENTATION_GUIDE.md` -- Topology implementation
- `../specs/TREE_SITTER_TASK_REGISTRY.md` -- 46 tasks with confidence

### Implementation Files
- `src/core/full_analysis.py` -- 29-stage pipeline orchestration
- `src/core/purpose_intelligence.py` -- Q-score computation
- `src/core/topology_reasoning.py` -- Health T, E, Gd components
- `src/core/level_classifier.py` -- L-3..L12 level assignment
- `src/core/dimension_classifier.py` -- D4, D5, D7 classification
- `src/core/purpose_emergence.py` -- pi1-pi4 computation

### Academic Sources
- Friston, K. (2022). "The Free Energy Principle Made Simpler." arXiv:2201.06387.
- Tononi, G. et al. (2020). "Integrated Information Theory 4.0." Consciousness & Cognition.
- Hoel, E. (2017). "When the Map is Better Than the Territory." Entropy 19(5): 188.
- Shannon, C. E. (1948). "A Mathematical Theory of Communication." Bell System Technical Journal.

---

*This is Layer 3. Every measurement and application lives here.*
*For axioms, see L0. For definitions, see L1. For behavioral laws, see L2.*
