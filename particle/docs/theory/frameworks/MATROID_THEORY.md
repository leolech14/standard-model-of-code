---
id: MATROID_THEORY
title: "Matroid Theory: Independence and Rank on Purpose Space"
layer: L3 (Interpretation)
prerequisites:
  - PURPOSE_SPACE
  - CATEGORY_THEORY
exports:
  - purpose_matroid
  - rank_function
  - greedy_decomposition
  - independence_system
status: PARTIALLY_IMPLEMENTED
implementation:
  file: src/core/purpose_field.py
  lines: "372-375"
  coverage: "God class detection (coherence < 0.4 AND unique >= 4) encodes an implicit matroid rank bound. Explicit matroid construction not implemented."
glossary_terms:
  - matroid
  - rank_function
---

# Matroid Theory: Independence and Rank on Purpose Space

> **Navigation:** [INDEX](../INDEX.md) | [PURPOSE_SPACE](./PURPOSE_SPACE.md) > [CATEGORY_THEORY](./CATEGORY_THEORY.md) > **MATROID_THEORY**
> **Depends on:** [CATEGORY_THEORY.md](./CATEGORY_THEORY.md) (functorial view of rank)

---

## Abstract

Matroid theory formalizes **which combinations of purposes can coexist coherently** within a single code component. Where information theory measures disorder (entropy) and category theory describes structure-preserving maps (functors), matroid theory captures **independence** — the combinatorial constraint on how many distinct responsibilities an atom can bear before becoming a god class.

The central construct is the **purpose matroid** M_purpose = (E, I) where E is the set of purposes and I is the family of independent (coherent) purpose combinations. The **rank function** r(S) gives the maximum number of coherent purposes in any subset S. A god class is precisely an atom whose purpose set exceeds the matroid rank bound: |purposes(v)| > r(purposes(v)).

The greedy algorithm on matroids provides a principled strategy for **splitting god classes** — at each step, remove the purpose that least fits the coherent core, yielding a sequence of increasingly focused components.

**Implementation status:** Partially implemented. The god class threshold `unique >= 4` in `purpose_field.py:374` is an implicit rank bound. The full matroid structure (independence oracle, rank function, greedy decomposition) is not explicitly encoded.

---

## SS1. Purpose Matroid

### 1.1 Definition

A **matroid** is a pair M = (E, I) where:

```
E = ground set (finite set of elements)
I = family of independent sets (subsets of E)

satisfying three axioms:
(I1) emptyset in I                              (empty set is independent)
(I2) If A in I and B subset A, then B in I      (hereditary / downward-closed)
(I3) If A, B in I and |A| < |B|, then exists    (augmentation / exchange)
     e in B\A such that A union {e} in I
```

### 1.2 Purpose Matroid M_purpose

For a given code component v, define:

```
E = {p_1, ..., p_k}    the distinct purposes among v's children
                        (i.e., the roles detected by the Collider pipeline)

I = { S subset E | S is a coherent combination of purposes }
```

A set S of purposes is **independent** (coherent) if and only if a single well-designed component could legitimately serve all purposes in S simultaneously, conforming to established architectural patterns.

**Examples of independent sets:**
```
{Query}                                 independent (pure data reader)
{Query, Command}                        independent (standard Repository)
{Query, Command, Factory}               independent (Repository with creation)
{Command, Query, Validator}             independent (Service with validation)
```

**Examples of dependent sets:**
```
{Controller, Repository, Service, Entity}  dependent (spans all layers)
{Test, Factory, Command, Mapper, Query}    dependent (too many unrelated concerns)
```

### 1.3 Connection to EMERGENCE_RULES

The EMERGENCE_RULES in `purpose_field.py:149-170` define the **bases** of M_purpose — the maximal independent sets that correspond to named architectural patterns:

```
frozenset(["Query", "Command"])           -> Repository    (basis of rank 2)
frozenset(["Query", "Command", "Factory"]) -> Repository   (basis of rank 3)
frozenset(["Command", "Query", "Validator"]) -> Service    (basis of rank 3)
frozenset(["Controller", "Validator"])    -> APILayer       (basis of rank 2)
```

Each frozenset defines a combination of child purposes that is architecturally coherent — an independent set. The composite purpose label (Repository, Service, etc.) names the architectural pattern realized by that independent set.

---

## SS2. Rank Function

### 2.1 Definition

The **rank function** r: 2^E -> N assigns to each subset S of the ground set the size of the largest independent set contained in S:

```
r(S) = max { |A| : A subset S, A in I }
```

The rank function satisfies:

```
(R1) 0 <= r(S) <= |S|           (bounded)
(R2) If S subset T, then r(S) <= r(T)  (monotone)
(R3) r(S union T) + r(S intersect T) <= r(S) + r(T)  (submodular)
```

### 2.2 Purpose Rank

For the purpose matroid, r(S) represents the **maximum number of distinct purposes** that can coherently coexist within a single component from the set S.

Empirically, architectural patterns in the Standard Model have rank at most 3-4:

| Architectural Pattern | Purposes | Rank |
|---|---|---|
| DataAccess | {Query} | 1 |
| Repository | {Query, Command} or {Query, Command, Factory} | 2-3 |
| Service | {Command, Query, Validator} | 3 |
| APILayer | {Controller, Validator} | 2 |
| TestSuite | {Test, Fixture} | 2 |
| Transformer | {Mapper, Factory} | 2 |

### 2.3 God Class as Rank Violation

The god class detection in `purpose_field.py:372-375` encodes an implicit rank bound:

```python
if node.coherence_score < 0.4 and total >= 8 and unique >= 4:
    node.is_god_class = True
```

In matroid terms, `unique >= 4` asserts:

```
|purposes(v)| >= 4 > r(purposes(v))
```

Since the maximum rank of any named architectural pattern is 3, a component serving 4 or more distinct purposes exceeds the rank bound. The additional conditions (`coherence < 0.4` and `total >= 8`) guard against false positives: a small class with 4 purposes might still be coherent if the distribution is heavily skewed toward one purpose.

**Connection to [L2_PRINCIPLES.md](../foundations/L2_PRINCIPLES.md) SS5 AM003:** The antimatter pattern AM003 (God Class) is defined as `R(node) > 7` using the RPBL responsibility dimension. The matroid rank bound provides a complementary, finer-grained detection: R > 7 counts all responsibilities, while `unique >= 4` counts distinct purpose *types*. A class with 10 methods all serving "Query" has R=10 but unique=1 — not a god class. A class with 4 methods serving 4 different purposes has R=4 but unique=4 — a god class by matroid rank.

---

## SS3. Circuits and Dependency Cycles

### 3.1 Definition

A **circuit** in a matroid is a minimal dependent set — a set C such that C is not in I, but every proper subset of C is in I.

### 3.2 Purpose Circuits

In M_purpose, circuits represent the smallest sets of purposes whose combination creates architectural incoherence:

```
If {Controller, Repository} is a circuit:
  - {Controller} alone is coherent (independent)
  - {Repository} alone is coherent (independent)
  - {Controller, Repository} together is incoherent (presentation + infrastructure)
```

Circuits identify the **minimal violations** — the pairs (or triples) of purposes that fundamentally conflict. This is more precise than simply counting: it tells you *which* purposes conflict, not just *how many*.

### 3.3 Connection to Topology

The circuits of M_purpose correspond to the H_1 generators in [TOPOLOGY.md](./TOPOLOGY.md) — both detect "structure beyond threshold." A topological cycle (H_1) represents a circular dependency that should not exist; a matroid circuit represents a purpose combination that should not coexist. The difference is perspective: topology works in the space of dependencies (edges), while matroid theory works in the space of purposes (attributes).

---

## SS4. Greedy Decomposition

### 4.1 The Greedy Algorithm

One of matroid theory's foundational results is that the **greedy algorithm is optimal** on matroids. For purpose decomposition:

```
GREEDY-SPLIT(v, M_purpose):
  Input:  atom v with purposes S = {p_1, ..., p_k} where |S| > r(S)
  Output: partition of v into coherent sub-components

  1. Sort purposes by weight w(p_i) = count of children with purpose p_i
     (descending — keep the dominant purposes together)
  2. Initialize: current = emptyset, components = []
  3. For each purpose p_i in sorted order:
       If current union {p_i} in I:     (adding p_i keeps independence)
         current = current union {p_i}
       Else:
         components.append(current)      (start a new component)
         current = {p_i}
  4. components.append(current)
  5. Return components
```

### 4.2 Optimality

On a matroid, the greedy algorithm produces a **maximum-weight independent set** — the partition that preserves the most children in each component. This is a theoretical guarantee that does not hold for arbitrary combinatorial structures; it is a unique property of matroids.

### 4.3 Refactoring Guidance

The greedy decomposition translates to concrete refactoring advice:

```
God class: UserManager (purposes = {Query, Command, Validator, Factory, Mapper})

Greedy split with rank bound = 3:
  Component 1: {Query, Command, Validator} -> UserService (Service pattern)
  Component 2: {Factory, Mapper}           -> UserTransformer (Transformer pattern)
```

Each resulting component has |purposes| <= r (within rank bound) and maps to a named architectural pattern via EMERGENCE_RULES. This connects matroid decomposition to the concept lattice of [ORDER_THEORY.md](./ORDER_THEORY.md) — the decomposed components correspond to formal concepts in the lattice.

---

## SS5. Matroid Operations

### 5.1 Restriction

The **restriction** of M to a subset A of E, written M|A = (A, {I intersect 2^A : I in I}), captures the matroid structure within a single module or layer:

```
M|DOMAIN = restriction of M_purpose to domain-layer purposes only
         = matroid of legitimate purpose combinations within the domain layer
```

### 5.2 Contraction

The **contraction** of M by a set A, written M/A, removes elements and adjusts the independence structure. In purpose terms, contraction by a "fixed" purpose (one that is given and cannot be changed) reduces the problem to finding coherent combinations of the remaining purposes:

```
If a class must serve purpose "Repository" (fixed),
then M/{"Repository"} gives the matroid of additional purposes
that can coherently coexist with Repository.
```

### 5.3 Dual Matroid

The **dual matroid** M* has the same ground set E but independent sets are complements of cobases. In purpose terms, the dual perspective asks: "What is the maximum number of purposes we can *remove* while still covering all architectural needs?" This connects to the minimum refactoring effort needed to split a god class.

---

## SS6. Connections to Other Frameworks

| Framework | Connection |
|---|---|
| [PURPOSE_SPACE](./PURPOSE_SPACE.md) | Matroid structure constrains the algebraic structure A of M |
| [GRAPH_THEORY](./GRAPH_THEORY.md) | God class detection via bridge analysis complements matroid rank bounds |
| [ORDER_THEORY](./ORDER_THEORY.md) | Matroid independence generalizes lattice join-irreducibility; greedy decomposition maps to FCA concepts |
| [INFORMATION_THEORY](./INFORMATION_THEORY.md) | God class threshold = matroid rank bound violation; coherence < 0.4 is entropy guard |
| [CATEGORY_THEORY](./CATEGORY_THEORY.md) | Matroid is a functor from subsets to rank values; rank is submodular |
| [TOPOLOGY](./TOPOLOGY.md) | Matroid circuits ~ H_1 generators (both detect "beyond threshold" structure) |
| [HYPERGRAPH_THEORY](./HYPERGRAPH_THEORY.md) | Matroid on hyperedges defines which multi-atom dependencies are independent |

---

## Appendix A: Matroid Axiom Verification

The purpose matroid axioms can be verified empirically:

1. **(I1) Empty set:** The empty purpose set is vacuously coherent.
2. **(I2) Hereditary:** If {Query, Command, Factory} is coherent (Repository pattern), then {Query, Command} is also coherent (simpler Repository). Removing purposes cannot create incoherence.
3. **(I3) Augmentation:** If A = {Query} and B = {Query, Command}, then |A| < |B| and we can augment A with Command from B to get {Query, Command}, which is independent. This must hold for all such pairs — an empirical constraint on the EMERGENCE_RULES.

Violation of (I3) would indicate that the EMERGENCE_RULES contain an inconsistency: two independent sets of different sizes where no element of the larger can extend the smaller. Future validation should check this automatically.

## Appendix B: Computational Complexity

| Operation | Complexity | Notes |
|---|---|---|
| Independence oracle | O(1) lookup | If EMERGENCE_RULES is precomputed as a set of frozensets |
| Rank computation | O(k * |I|) | k = |S|, |I| = number of independent sets |
| Greedy decomposition | O(k log k + k * oracle) | Sort + k oracle queries |
| Circuit enumeration | O(2^k) worst case | Exponential in number of purposes; practical for k <= 10 |

For typical Standard Model usage, k (number of distinct purposes per atom) is small (1-6), so all operations are fast.

## Appendix C: Citations

- Whitney, H. (1935). "On the abstract properties of linear dependence." American Journal of Mathematics 57(3): 509-533.
- Oxley, J. G. (2011). *Matroid Theory.* 2nd ed. Oxford University Press.
- ITP (2025). "A formal proof of the Rota basis conjecture for matroids of rank two." Conference on Interactive Theorem Proving.
- Welsh, D. J. A. (1976). *Matroid Theory.* Academic Press.

---

*This document defines matroid-theoretic independence on Purpose Space. For the space itself, see [PURPOSE_SPACE.md](./PURPOSE_SPACE.md). For topological complements, see [TOPOLOGY.md](./TOPOLOGY.md). For higher-order dependency structure, see [HYPERGRAPH_THEORY.md](./HYPERGRAPH_THEORY.md).*
