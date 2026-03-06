# Theory Index

**Purpose:** Central navigation for all Standard Model of Code theory documents
**Organization:** Foundations (L0-L3) + Mathematical Frameworks + References
**Last updated:** 2026-03-05

---

## 1. Foundations (The Narrative Loop)

The theory is organized as a closed loop: axioms define terms, terms produce principles, principles drive applications, and applications validate axioms.

```
L0 AXIOMS ──> L1 DEFINITIONS ──> L2 PRINCIPLES ──> L3 APPLICATIONS
    ^                                                      |
    └──────────────── theory closure ──────────────────────┘
```

| Layer | File | Purpose |
|-------|------|---------|
| L0 | [L0_AXIOMS.md](./foundations/L0_AXIOMS.md) | Foundational assumptions (A1-A3, D1-D8, F1-F5) |
| L1 | [L1_DEFINITIONS.md](./foundations/L1_DEFINITIONS.md) | Precise terms: Atom, Role, Dimension, Purpose |
| L2 | [L2_PRINCIPLES.md](./foundations/L2_PRINCIPLES.md) | Behavioral laws: Role Consistency, Purpose Emergence, Structural Determinism |
| L3 | [L3_APPLICATIONS.md](./foundations/L3_APPLICATIONS.md) | Measurement and implementation: classification, detection, coherence, validation |

**See also:** [ORPHAN_SEMANTICS.md](../../wave/docs/theory/ORPHAN_SEMANTICS.md) (specialized L2 law)

---

## 2. Mathematical Frameworks

Seven mathematical frameworks operate on **Purpose Space** M = (S, d, mu, tau, A), each formalizing a different aspect of code architecture. They follow a strict reading order DAG (no circular dependencies):

```
PURPOSE_SPACE ──┬──> GRAPH_THEORY
                ├──> ORDER_THEORY
                └──> INFORMATION_THEORY
                          │
              CATEGORY_THEORY  (depends on ORDER + INFO)
                    │
              ┌─────┴─────┐
          TOPOLOGY    MATROID_THEORY
              └─────┬─────┘
           HYPERGRAPH_THEORY
```

| Framework | File | Layer | Status | Key Exports |
|-----------|------|-------|--------|-------------|
| Purpose Space | [PURPOSE_SPACE.md](./frameworks/PURPOSE_SPACE.md) | L0-L1 | PARTIALLY_IMPLEMENTED | manifold M, purpose metric d, purpose field P |
| Graph Theory | [GRAPH_THEORY.md](./frameworks/GRAPH_THEORY.md) | L1 | IMPLEMENTED | Newman modularity, centrality, community detection |
| Order Theory | [ORDER_THEORY.md](./frameworks/ORDER_THEORY.md) | L1-L3 Bridge | PARTIALLY_IMPLEMENTED | FCA lattice, Galois connections, purpose ordering |
| Information Theory | [INFORMATION_THEORY.md](./frameworks/INFORMATION_THEORY.md) | L2 | IMPLEMENTED | Shannon entropy, coherence, mutual information |
| Category Theory | [CATEGORY_THEORY.md](./frameworks/CATEGORY_THEORY.md) | L1 | PARTIALLY_IMPLEMENTED | functor F: Purp->Layer, natural transformations, presheaf |
| Topology | [TOPOLOGY.md](./frameworks/TOPOLOGY.md) | L2-L3 Bridge | THEORETICAL | persistent homology, simplicial complexes, TDA |
| Matroid Theory | [MATROID_THEORY.md](./frameworks/MATROID_THEORY.md) | L3 | PARTIALLY_IMPLEMENTED | rank function, independence, greedy decomposition |
| Hypergraph Theory | [HYPERGRAPH_THEORY.md](./frameworks/HYPERGRAPH_THEORY.md) | L1 | THEORETICAL | hyperedges, n-ary dependencies, composite emergence |

**Notation consistency:** All framework files use dim(M) = 33, d(p_i, p_j) = 1 - cos(p_i, p_j), coherence = 1 - H/H_max, as defined in PURPOSE_SPACE.md.

---

## 3. Comprehensive References

### Formal Axioms
**File:** [THEORY_AXIOMS.md](./THEORY_AXIOMS.md)
Complete formal axiom system with proofs. Gemini 3 Pro reviewed.

### Complete Theory
**File:** [STANDARD_MODEL_COMPLETE.md](./STANDARD_MODEL_COMPLETE.md)
Unified theory document (all layers integrated).

### Theoretical Foundations
**File:** [STANDARD_MODEL_THEORY_COMPLETE.md](./STANDARD_MODEL_THEORY_COMPLETE.md)
Meta-theoretical framework. See also: [PROJECTOME_THEORY.md](./PROJECTOME_THEORY.md)

### Topological Boundaries
**File:** [TOPOLOGICAL_BOUNDARIES.md](./TOPOLOGICAL_BOUNDARIES.md)
Nested abstraction theory (Locus/Holon). Connects to [TOPOLOGY.md](./frameworks/TOPOLOGY.md).

### Epistemological Status
**File:** [EPISTEMOLOGICAL_STATUS.md](./EPISTEMOLOGICAL_STATUS.md)
Epistemic classification of each theoretical claim.

### Philosophical Foundations
**File:** [PHILOSOPHICAL_FOUNDATIONS.md](./PHILOSOPHICAL_FOUNDATIONS.md)

---

## 4. Contextome Theory (Cross-Subsystem)

Located in: `wave/docs/theory/`

**Foundational:**
- [THEORY.md](../../wave/docs/theory/THEORY.md) - Core theory document
- [FOUNDATIONAL_THEORIES.md](../../wave/docs/theory/FOUNDATIONAL_THEORIES.md)
- [INTELLECTUAL_FOUNDATIONS.md](../../wave/docs/theory/INTELLECTUAL_FOUNDATIONS.md)

**Specialized:**
- [THEORY_DATA_LOGISTICS.md](../../wave/docs/theory/THEORY_DATA_LOGISTICS.md)
- [ORPHAN_SEMANTICS.md](../../wave/docs/theory/ORPHAN_SEMANTICS.md) - Type-aware connectivity
- [VALUE_SCENARIOS.md](../../wave/docs/theory/VALUE_SCENARIOS.md)

**Integration:**
- [FOUNDATIONS_INTEGRATION.md](../../wave/docs/theory/FOUNDATIONS_INTEGRATION.md)
- [SYNTHESIS_GAP_IMPLEMENTATION.md](../../wave/docs/theory/SYNTHESIS_GAP_IMPLEMENTATION.md)

**References:**
- [REFERENCE_LIBRARY.md](../../wave/docs/theory/REFERENCE_LIBRARY.md)
- [AUTHOR_CORPUS.md](../../wave/docs/theory/AUTHOR_CORPUS.md)

---

## 5. Specialized Theory

| Document | Purpose |
|----------|---------|
| [ANALOGY_SCORING_METHODOLOGY.md](./ANALOGY_SCORING_METHODOLOGY.md) | How to evaluate theoretical metaphors |
| [CODE_ZOO.md](./CODE_ZOO.md) | Catalog of architectural species |
| [CROSS_DOMAIN_METHODOLOGY.md](./CROSS_DOMAIN_METHODOLOGY.md) | Cross-domain analysis methodology |
| [DETERMINISTIC_CODE_SYNTHESIS.md](./DETERMINISTIC_CODE_SYNTHESIS.md) | Deterministic code generation theory |
| [SPEC_DRIVEN_DEVELOPMENT.md](./SPEC_DRIVEN_DEVELOPMENT.md) | Specification-driven development |
| [COMPLETE_THEORY_READING_GUIDE.md](./COMPLETE_THEORY_READING_GUIDE.md) | Reading guide for theory corpus |

---

## 6. Academic Publication Package

**Status:** Draft Complete (2026-02-01)
**Target Venue:** IEEE TSE (Transactions on Software Engineering)

**Index:** [ACADEMIC_PUBLICATION_INDEX.md](./ACADEMIC_PUBLICATION_INDEX.md)

| Gap | Document | Purpose |
|-----|----------|---------|
| 1. Motivation | [PROBLEM_STATEMENT.md](./PROBLEM_STATEMENT.md) | Why SMC matters |
| 2. Formalization | [AXIOMS_FORMAL.md](./AXIOMS_FORMAL.md) | LaTeX-style axioms |
| 3. Prior Work | [RELATED_WORK.md](./RELATED_WORK.md) | 8+ frameworks compared |
| 4. Empirical | [EMPIRICAL_VALIDATION.md](./EMPIRICAL_VALIDATION.md) | Evidence + studies |
| 5. Scope | [SCOPE_LIMITATIONS.md](./SCOPE_LIMITATIONS.md) | Explicit boundaries |
| 6. Predictions | [PREDICTIONS.md](./PREDICTIONS.md) | 16 falsifiable claims |

**Original analysis:** [ACADEMIC_GAPS.md](./ACADEMIC_GAPS.md) | [ACADEMIC_POSITIONING.md](./ACADEMIC_POSITIONING.md)

---

## 7. Navigation Patterns

### For Learning (Sequential)
```
START: INDEX.md (you are here)
  ↓
  foundations/L0_AXIOMS.md (foundation)
  ↓
  foundations/L1_DEFINITIONS.md (terms)
  ↓
  foundations/L2_PRINCIPLES.md (relationships)
  ↓
  foundations/L3_APPLICATIONS.md (practice)
  ↓
  frameworks/PURPOSE_SPACE.md (mathematical space)
  ↓
  frameworks/ (7 framework files in DAG order)
  ↓
  LOOP: Back to L0 (theory closure)
```

### For Reference (Direct Access)
- Search for concept in [GLOSSARY.yaml](../GLOSSARY.yaml)
- Read standalone document
- Framework files are self-contained with navigation links

### For Comprehensive Understanding
- Read [STANDARD_MODEL_COMPLETE.md](./STANDARD_MODEL_COMPLETE.md) (all layers integrated)
- OR read [THEORY_AXIOMS.md](./THEORY_AXIOMS.md) (formal proofs)

---

## 8. Directory Structure

```
theory/
  INDEX.md                    (this file)
  foundations/                 L0-L3 narrative loop
    L0_AXIOMS.md
    L1_DEFINITIONS.md
    L2_PRINCIPLES.md
    L3_APPLICATIONS.md
  frameworks/                  mathematical frameworks (DAG-ordered)
    PURPOSE_SPACE.md
    GRAPH_THEORY.md
    ORDER_THEORY.md
    INFORMATION_THEORY.md
    CATEGORY_THEORY.md
    TOPOLOGY.md
    MATROID_THEORY.md
    HYPERGRAPH_THEORY.md
  synthesis/                   (future: cross-framework results)
  whitepapers/                 (future: standalone papers)
  *.md                         standalone theory files (root)
```

---

## 9. Cross-References to Code

| Theory | Implementation |
|--------|---------------|
| L0 Axioms (Atom structure) | `src/core/atom_loader.py` |
| L1 Definitions (Role taxonomy) | `src/patterns/*.yaml` |
| L2 Principles (Purpose dynamics) | `src/core/purpose_field.py` |
| L3 Applications (Measurement) | Collider Pipeline (28 stages) |
| Graph Theory (Metrics) | `src/core/graph_metrics.py` |
| Information Theory (Entropy) | `src/core/purpose_field.py:358-375` |
| Order Theory (Emergence rules) | `src/core/purpose_field.py:149-170` |
| Category Theory (Layer functor) | `src/core/purpose_field.py:174-216` |
| Matroid Theory (God class rank) | `src/core/purpose_field.py:372-375` |

**Practice documentation:**
- [MODEL.md](../MODEL.md) - Practical summary
- [COLLIDER.md](../COLLIDER.md) - Tool usage
- [specs/](../specs/) - Implementation specs

---

*This index supersedes THEORY_INDEX.md. The narrative loop L0->L1->L2->L3->L0 is preserved. Mathematical frameworks formalize the structure of Purpose Space M.*
