# VISION - Why "Standard Model"

> The ambition, the physics parallel, and the six commitments that make this a Standard Model -- not just another taxonomy.

---

## The Claim

The Standard Model of Physics classifies every fundamental particle and every force. No exceptions. No "other" bucket. Every interaction in the universe maps to the model.

The Standard Model of Code makes the same claim for software:

**Every code element gets a classification. Every relationship gets a type. Every architectural pattern is a measurable configuration of the graph. No exceptions.**

This is not a linting tool. Not a style guide. Not "best practices." It is a claim that code has *physics* -- discoverable, classifiable, measurable structure -- and that structure can be captured in a single unified model.

---

## The Physics Parallel

| Standard Model of Physics | Standard Model of Code |
|---------------------------|------------------------|
| Classifies all particles (quarks, leptons, bosons) | Classifies all code elements (94 atoms in 3 tiers) |
| Describes 4 fundamental forces | Describes 6 edge types (calls, imports, inherits, implements, contains, uses) |
| Particles have quantum numbers (charge, spin, color) | Nodes have 8 dimensions (WHAT, LAYER, ROLE, BOUNDARY, STATE, EFFECT, LIFECYCLE, TRUST) |
| Conservation laws constrain interactions | Graph invariants constrain architecture |
| Periodic table organizes elements by properties | Atom taxonomy organizes code by structural identity |
| Emergent properties at scale (atoms → molecules → matter) | Emergent properties at scale (nodes → modules → systems) |

The analogy is structural, not decorative. Both models achieve the same thing: **take an apparently chaotic domain and show it has a finite, classifiable vocabulary of building blocks and a rule-governed grammar of combinations.**

---

## The Six Commitments

### 1. Completeness

Classification is a **total function**: every node gets an atom, every node gets a role, every node gets dimensions. The taxonomy does not have an escape hatch.

```
sigma: N -> A       (total function -- no node unclassified)
```

100% classification has been achieved on every tested codebase. When a new pattern appears, the taxonomy expands -- the "Unknown" atom is a flag for the taxonomy to grow, not a permanent category.

### 2. Determinism

The Collider is a deterministic classifier. No machine learning. No neural networks. No probabilities in the core engine. Given the same input, it produces the same output, every time.

This is a deliberate philosophical choice:

- **Most code analysis tools** use ML: probabilistic, opaque, non-reproducible
- **The Collider** uses AST parsing + graph topology + pattern matching: deterministic, transparent, reproducible

AI is a *consumer* of the Collider's output, not a component of its engine. The analysis is the foundation; AI interprets the results. You don't want your periodic table to change its mind depending on the weather.

### 3. Unification

Three kinds of analysis that are traditionally separate:

| Analysis Type | Traditional Tool | SMoC |
|---------------|-----------------|------|
| **Structural** | AST parsers, linters | Atom classification (WHAT dimension) |
| **Architectural** | Manual diagrams, dependency tools | Graph topology + layer detection |
| **Teleological** | Human judgment, documentation | Purpose field over nodes |

The Standard Model unifies these under one graph, one classification system, one model. Structure, architecture, and purpose are three views of the same underlying reality -- not three different tools giving three different answers.

### 4. Measurability

If it is in the model, it is computable. Every concept has a metric:

| Concept | Metric |
|---------|--------|
| Purpose alignment | Cosine distance between purpose vectors |
| Architectural health | H = f(Topology, Encapsulation, Growth, Antimatter) |
| Code-doc agreement | Concordance score across 4 states |
| Classification confidence | Trust dimension (0-100%) |
| Structural role | Topological centrality + pattern matching |

"Architecture astronautics" -- drawing pretty diagrams that can't be computed -- is explicitly excluded. The measurement mandate: **if you can't compute it from the graph, it doesn't belong in the model.**

### 5. Emergence

Properties change at scale boundaries. A function behaves differently than a module which behaves differently than a system. These aren't just differences of size -- they are **phase transitions** where the rules change:

| Boundary | Below | Above | What Changes |
|----------|-------|-------|--------------|
| L0 → L1 | Tokens | Statements | Syntax → semantics |
| L3 → L4 | Functions | Containers | Standalone → composed |
| L7 → L8 | Systems | Ecosystems | Internal coupling → external boundaries |

The invariants that survive abstraction change *discontinuously* at these boundaries. This is directly from physics: the laws governing quarks are not the laws governing galaxies, even though galaxies are made of quarks.

### 6. Falsifiability

The model makes testable predictions:

| Prediction | Test | Current Status |
|------------|------|----------------|
| Every file is Codome XOR Contextome | Classify 100 projects | Passed (100%) |
| Every atom derivable from 8 dimensions | Express each as dimensional conjunction | In progress |
| Graph topology predicts architectural role | Compare detected vs. human-labeled roles | Validated |
| Orphan taxonomy covers all disconnection types | Find orphan not in the 7 types | No counterexample found |
| Antimatter patterns are exhaustive for structural flaws | Find anti-pattern not in AM001-AM007 | Open |

A model that can't be wrong isn't a model. It's marketing.

---

## What This Is Not

- **Not a linter.** Linters enforce style. The SMoC describes structure.
- **Not an AI tool.** The core engine is deterministic. AI is a consumer, not a component.
- **Not a framework.** It doesn't tell you how to write code. It tells you what code IS.
- **Not finished.** The 16-level scale, constructal flow, and Betti numbers are research directions. The classification system and graph analysis are production.

---

## The Accelerator Metaphor

The Collider is named after CERN's particle collider. The analogy:

- **CERN smashes particles** to reveal fundamental structure → **The Collider parses codebases** to reveal fundamental architecture
- **CERN classifies what comes out** using the Standard Model → **The Collider classifies what it finds** using the SMoC
- **CERN's detectors** are deterministic instruments → **The Collider's 28-stage pipeline** is a deterministic instrument
- **Physicists interpret** detector output → **AI agents interpret** Collider output

The output is a structured graph -- often thousands of nodes -- that humans don't read directly. Like a particle detector's readout, it is a **stone tool**: an instrument designed to be read by another instrument (AI), not by human eyes. This is a valid design choice, not a limitation.

---

*Source: L0_AXIOMS.md (design choices), PREDICTIONS.md (falsifiability), MODEL.md (classification)*
*See also: [THEORY_WINS.md](THEORY_WINS.md) for the 13 key ideas, [ARCHITECTURE.md](ARCHITECTURE.md) for the implementation*
