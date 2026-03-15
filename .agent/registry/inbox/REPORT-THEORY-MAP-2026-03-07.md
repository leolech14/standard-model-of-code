# SMoC Theory Map — External Theories & Frameworks

> **Generated:** 2026-03-07
> **Purpose:** Catalog every external theory, framework, and mathematical concept that SMoC draws from or relates to.
> **Sources scanned:** docs/essentials/, docs/nav/, docs/frontier/, docs/specs/, .agent/KERNEL.md, standard-model-of-code/, particle/README.md, README.md

---

## Summary

**70+ external frameworks** across 14 disciplines. SMoC is not just a taxonomy — it's a formal integration layer that borrows rigorously from physics, mathematics, biology, philosophy, and CS theory.

### Connection Strengths

| Strength | Meaning | Count |
|----------|---------|-------|
| **Core Foundation** | SMoC axioms directly derive from this | 4 |
| **Core Analogy** | The central metaphor powering SMoC | 1 |
| **Core Concept** | Deeply embedded in SMoC's structure | 3 |
| **Structural Influence** | SMoC borrows math/conceptual structure | 9 |
| **Foundational Integration** | SMoC formalizes informal concepts from here | 5 |
| **Borrowed Concept** | Adopted metaphor, principle, or terminology | 8 |
| **Comparative Framework** | SMoC positions itself relative to this | 5 |
| **Methodological Principle** | Applied approach/principle | 2 |
| **Theoretical Grounding** | Philosophical/mathematical justification | 4 |
| **Practical Application** | Implementation-level usage | 4 |

---

## I. Physics & Particle Physics

| Theory | Where Referenced | How SMoC Uses It | Strength |
|--------|-----------------|------------------|----------|
| **Standard Model of Physics** | VISION.md | Central analogy: classifies code elements like physics classifies particles. Both have conservation laws and fundamental interactions. | Core Analogy |
| **Quantum Mechanics (Observation Paradox)** | THEORY_WINS.md (#9) | Particle/Wave/Observer duality from quantum measurement: measurement (Particle) collapses potential (Wave) based on intent (Observer). | Structural Influence |
| **Particle Accelerators (CERN Collider)** | VISION.md | Collider tool named after CERN: both smash inputs to reveal fundamental structure. | Borrowed Concept |
| **Conservation Laws** | VISION.md, LAGRANGIAN.md | 6 invariants (P = C ⊔ X, σ_total, concordances, λ monotonic, κ bounded, realms disjoint) are conserved quantities from the Incoherence Functional. | Structural Influence |
| **Phase Transitions** | CLASSIFICATION.md, LEVELS.md | Zone boundaries (L3→L4, L7→L8) treated as phase transitions where dominant relation types change discontinuously. | Borrowed Concept |

---

## II. Mathematics & Formal Systems

| Theory | Where Referenced | How SMoC Uses It | Strength |
|--------|-----------------|------------------|----------|
| **Category Theory** | RELATED_WORK.md, L0_AXIOMS.md | MECE partition as coproduct; objects, morphisms, functors for relationship modeling. (Eilenberg, Mac Lane, Pierce, Moggi, Wadler) | Structural Influence |
| **Set Theory** | L0_AXIOMS.md, LAGRANGIAN.md | Foundational: P = C ⊔ X is a set-theoretic MECE partition; closure, cardinality preservation, subsets. | Core Foundation |
| **Graph Theory** | GRAPH.md, L0_AXIOMS.md | Codebases as directed graphs G = (N, E); cycle detection (Tarjan), centrality metrics (betweenness, PageRank), DAG properties. | Core Foundation |
| **Topology & TDA** | FLOW.md, ANTIMATTER.md, L2_PRINCIPLES.md | Graph topology reveals architecture; layer violations, circular deps, bottleneck detection. | Structural Influence |
| **Linear Algebra & Vector Spaces** | PURPOSE.md, CONCORDANCE.md | Purpose field 𝒫: N → ℝᵏ; cosine distance for drift: 1 − cos(𝒫_code, 𝒫_docs). | Structural Influence |
| **Axiomatic Systems** | L0_AXIOMS.md, LAGRANGIAN.md | SMoC formalized as axiomatic system with 7 axiom groups (A–G). | Core Foundation |
| **Hoare Logic** | RELATED_WORK.md | Pre/post-condition logic; contrasted with SMoC's structural vs behavioral focus. | Comparative |
| **Type Theory** | L0_AXIOMS.md | Propositions-as-types; MECE partition modeled as sum type (Either C X). | Structural Influence |
| **Information Theory** | LAGRANGIAN.md, PURPOSE.md | Integrated Information Theory (Tononi): purpose hierarchy exhibits emergence; entropy-based analysis. | Borrowed Concept |
| **Dynamical Systems / Gradient Descent** | LAGRANGIAN.md, PURPOSE.md | Development as d𝒫/dt = −∇Incoherence(𝕮). | Structural Influence |
| **Lawvere's Fixed-Point Theorem** | L0_AXIOMS.md | Diagonal argument: code cannot be its own metalanguage → requires external docs. (Lawvere 1969) | Theoretical Grounding |
| **Tarjan's SCC Algorithm** | ANTIMATTER.md (AM004) | Cycle detection in dependency graphs. | Technical Implementation |
| **Cosine Similarity** | CONCORDANCE.md, PURPOSE.md | Drift measurement between code and docs purpose vectors. | Applied Math |
| **Betweenness / PageRank** | GRAPH.md, FLOW.md | Bottleneck identification and recursive importance computation. | Applied Math |
| **Markov Chains** | FRONTIER_REFRAMING.md | Information geometry for entanglement analysis. | Borrowed Concept |
| **Harmonic Mean** | CONCORDANCE.md | Symmetry score balancing coverage and realizability. | Applied Math |

---

## III. Biology & Systems Theory

| Theory | Where Referenced | How SMoC Uses It | Strength |
|--------|-----------------|------------------|----------|
| **Holon Concept (Koestler)** | LEVELS.md, THEORY_WINS.md (#2) | 16-level hierarchy where every level is simultaneously whole and part. (Arthur Koestler's Janus-faced holon) | Structural Influence |
| **Emergence & Self-Organization** | THEORY_WINS.md (#6), VISION.md | Properties change discontinuously at scale boundaries; class purpose ≠ sum of method purposes. | Core Concept |
| **Biological Inheritance** | ATOMS.md, ROLES.md | Inheritance chain as detection signal; phylogeny parallels. | Borrowed Concept |

---

## IV. Flow Systems

| Theory | Where Referenced | How SMoC Uses It | Strength |
|--------|-----------------|------------------|----------|
| **Constructal Law (Bejan 2000)** | FLOW.md, THEORY_WINS.md (#13), FRONTIER_REFRAMING.md | "For a finite-size flow system to persist, its configuration must evolve to provide easier access to currents." Applied to 4 flows: Static, Runtime, Change, Human. | Core Concept |
| **Resistance to Flow** | FLOW.md, FRONTIER_REFRAMING.md | 4 resistance channels: R_static, R_runtime, R_change, R_human. Total = sum. | Borrowed Concept |

---

## V. Philosophy & Epistemology

| Theory | Where Referenced | How SMoC Uses It | Strength |
|--------|-----------------|------------------|----------|
| **Semiotics (Peirce/Morris)** | L0_AXIOMS.md | Code as sign system: atoms (signifiers), roles (referents), purpose field (interpretant). | Theoretical Grounding |
| **Gödel's Incompleteness** | L0_AXIOMS.md | Diagonal argument: code cannot fully specify its own semantics. | Theoretical Grounding |
| **Tarski's Undefinability** | L0_AXIOMS.md | Code (C) as object language; docs (X) as metalanguage for semantic closure. | Theoretical Grounding |
| **Falsifiability (Popper)** | VISION.md (#6) | SMoC makes testable predictions with explicit falsification criteria. | Methodological |

---

## VI. Computer Science Theory

| Theory | Where Referenced | How SMoC Uses It | Strength |
|--------|-----------------|------------------|----------|
| **AST / Parsing** | ATOMS.md, particle/README.md | Tree-sitter provides Tier 0 atom assignment. | Implementation |
| **Design Patterns (GoF)** | ROLES.md, RELATED_WORK.md | GoF patterns are compositions of SMoC atoms (e.g. Factory = Atom with ROLE=Factory). | Foundational Integration |
| **Anti-Patterns** | ANTIMATTER.md, THEORY_WINS.md (#10) | 7 canonical violations (AM001–AM007) formalize detection via role-layer-boundary. | Foundational Integration |
| **SWEBOK v4** | RELATED_WORK.md | SMoC formalizes what SWEBOK describes in prose. | Foundational Integration |
| **SEMAT Essence (OMG)** | RELATED_WORK.md | Method elements; SMoC complements with dimensional coordinates. | Comparative |
| **ISO/IEC 24765 SEVOCAB** | RELATED_WORK.md | Formal coordinates for 5,401 terms. | Foundational Integration |
| **Code Smells (Fowler)** | RELATED_WORK.md, ANTIMATTER.md | Smells reframed as dimensional anomalies (Long Method = LEVEL mismatch, God Class = ring imbalance). | Formalization |
| **ADRs** | RELATED_WORK.md | ADR validation via predicted dimensional shifts. | Complementary |
| **Microservices Patterns** | RELATED_WORK.md | Circuit Breaker, Saga, Event Sourcing as atom compositions. | Comparative |
| **Clean Architecture** | ANTIMATTER.md | Layer dependency rules formalized as structural invariants. | Foundational Application |
| **Domain-Driven Design** | THEORY_WINS.md, ANTIMATTER.md | Bounded contexts parallel "concordances." | Comparative |
| **SOLID Principles** | Implicit in dimensions | SRP → low role entropy; DIP → layer ordering. | Implicit |
| **CQRS** | ROLES.md | Query/Command split maps directly. | Pattern Alignment |

---

## VII. Cognitive Science & AI

| Theory | Where Referenced | How SMoC Uses It | Strength |
|--------|-----------------|------------------|----------|
| **Lost-in-the-Middle (LLM Attention)** | .agent/KERNEL.md | U-shaped attention → sandwich method for token budgeting. | Practical Application |
| **Token Budget Optimization** | .agent/KERNEL.md | Treat tokens as ROI budget; information hierarchy. | Practical Application |
| **Curry-Howard Correspondence** | L0_AXIOMS.md | Propositions-as-types for the MECE partition. | Structural Influence |

---

## VIII. Cross-Disciplinary

| Framework | Where Referenced | How SMoC Uses It | Strength |
|-----------|-----------------|------------------|----------|
| **MECE (McKinsey)** | THEORY_WINS.md (#1), L0_AXIOMS.md | P = C ⊔ X ensures complete, non-redundant classification. | Core Principle |
| **Dimensional Analysis** | CLASSIFICATION.md, PURPOSE.md | 8-dimensional coordinate system for code elements. | Core Concept |
| **Conway's Law** | Implicit | Architecture reflects team structure. | Light Reference |
| **Systems Thinking** | THEORY_WINS.md, CONTEXTOME.md | Recursive, fractal view; Particle/Wave/Observer mirrors nested systems. | Borrowed Concept |

---

## Top 10 Most Foundational Theories to SMoC

1. **Standard Model of Physics** — the central analogy
2. **Set Theory** — axiom foundation (P = C ⊔ X)
3. **Graph Theory** — dependency modeling backbone
4. **Category Theory** — structural relationships
5. **Constructal Law** — flow optimization principle
6. **Holon Concept (Koestler)** — level architecture
7. **Axiomatic Method** — the formalization approach itself
8. **Design Patterns (GoF)** — atoms subsume patterns
9. **SWEBOK/ISO standards** — what SMoC formalizes
10. **Falsifiability (Popper)** — the scientific commitment

---

## Research Domains for Future Exploration

| Domain | Entry Point | Opportunity |
|--------|------------|-------------|
| Information Geometry (Amari) | FRONTIER_REFRAMING.md | φ_structural stability metrics |
| Persistent Homology (TDA) | Topology references | Shape-of-code beyond graph metrics |
| Causal Inference (Pearl) | Not yet referenced | Causality in dependency chains |
| Formal Verification | Hoare logic parallel | Proofs about architectural properties |
| Network Science (Barabási) | Graph theory extensions | Scale-free properties of codebases |
