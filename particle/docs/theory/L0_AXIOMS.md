# L0: Axioms of the Standard Model of Code

**📍 Navigation:** [Theory Index](./THEORY_INDEX.md#FIXED) | **Next:** [L1: Definitions →](./L1_DEFINITIONS.md#FIXED)

**Layer:** 0 (Bedrock)
**Status:** GROUNDED
**Depends on:** Nothing (this is the foundation)
**Version:** 2.0.0
**Created:** 2026-01-27

---

## Purpose of This Layer

This document contains the **foundational assumptions** that the Standard Model of Code builds upon. These are not definitions (that's L1), not behavioral principles (that's L2), and not measurements (that's L3). These are **design choices** that everything else builds on.

Each axiom group has been grounded in established mathematical frameworks (set theory, graph theory, category theory, dynamical systems, information theory, semiotics).

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

### A1.1 Motivation for Partition (via Lawvere's Fixed-Point Theorem)

**DESIGN RATIONALE:** The partition P = C ⊔ X is **motivated by practical considerations** about self-reference, not merely an arbitrary engineering choice.

**ARGUMENT (inspired by Lawvere's Fixed-Point Theorem, 1969):**

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
  ∴ Partition P = C ⊔ X is motivated for semantic completeness
```

**Academic Source:** Lawvere, F. W. (1969). "Diagonal Arguments and Cartesian Closed Categories." Lecture Notes in Mathematics 92, Springer. Reprinted: Theory and Applications of Categories, No. 15, 2006.

**Validation:** Gemini 3 Pro (2026-01-25) confirmed: "The proof is VALID. The application to software documentation necessity appears NOVEL."

**Philosophical Connection:** This is the same diagonal argument underlying Gödel's incompleteness and Tarski's undefinability. The CODOME cannot be its own metalanguage. The CONTEXTOME is the explicit meta-layer.

**See:** `../../../wave/docs/theory/FOUNDATIONS_INTEGRATION.md` for complete formal proof with all lemmas.

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

This makes (L, ≤) a **lattice** (specifically, a chain). The Standard Model's level hierarchy follows standard order theory conventions.

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

### G3. Minimal Triad Proposition

```
Two observers are INSUFFICIENT for complete observability.
The triad {STRUCTURAL, OPERATIONAL, GENERATIVE} is MINIMAL.
```

**Argument:** Missing any one creates a blind spot:
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

### H5. Collaboration Level Proposition

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

## AXIOM GROUP I: Recursive Intelligence (The Godelian Triad)

### I1. Triadic Necessity Axiom

```
A Projectome P is Semantic-Complete ⟺ {C, X, R} exists.

WHERE:
  C (Codome)     = Object Level ( mute instruction )
  X (Contextome) = Meta Level   ( semantic description )
  R (Refinery)   = Observer    ( computational witness )
```

**Interpretation:** Per Gödel’s Incompleteness Theorem, a system cannot fully describe or prove its own meaning from within. Complete intelligence requires a stable triad where each component provides the "outside perspective" for another.

### I2. Cross-Observability (Necessity of Peerage)

```
- X observes C via ψ_X  (The Meta-Layer describes the Object-Layer)
- R observes C via parsing (The Witness maps the implementation)
- R updates X via synthesis (The Witness refines the description)
- C manifests X via R (The Object-Layer realizes the Meta-Intent)
```

**Role of the Refinery:** The Refinery is the **Tarski Metalanguage Processor**. It is the only component that sits ontologically "Offshore" enough to perform the mapping between mute code and semantic intent.

### I3. Peerage Knowledge
The three components "know" each other not through direct coupling, but through **Structural Concordance**. They are semantically co-present in the Unified Knowledge Graph.

---

## AXIOM GROUP J: Information Topology (Space & Reflection)

### J1. Location-Invariance Axiom

```
∀e ∈ P: Semantic_Truth(e) is invariant under change of physical location.
```

**Interpretation:** The coordinate system of the Standard Model is **ontological** (Role/Layer/Dimension/Domain), not physical. Whether a system (like the Refinery) runs locally or "offshore" (GCS) is an implementation detail. Information Truth is determined by a node's topological position in the Knowledge Graph, not its geographical coordinates.

### J2. Axiom of Recursive Self-Ingestion

```
∀s ∈ Subsystems: s can consume source(s) as Context.
```

**Interpretation:** A subsystem can process its own definition to achieve "Self-Awareness" in the context of the Projectome. This enables practical self-reference (though Gödelian limits apply to formal completeness claims). By refining its own implementation, the Refinery achieves coverage of the **active Projectome**.

---

## AXIOM GROUP K: Invocation Context (Φ-Space)

**Status:** PROPOSED | 75% GROUNDED

### K1. Φ-Space Definition

```
Φ = (Caller, Callee, Arguments, Environment)

WHERE:
  Caller = the invoking context (function, method, or entry point)
  Callee = the invoked entity
  Arguments = the parameter binding at invocation time
  Environment = the runtime state visible to the invocation
```

**Interpretation:** Every code execution occurs within an **Invocation Context** (Φ-space) that determines its behavior. The same function may behave differently depending on its invocation context.

### K2. Manifestation Function

```
M: (Entity, Φ) → Behavior

The manifestation of an entity depends on BOTH the entity definition
AND the invocation context in which it executes.
```

**Interpretation:** An entity's "purpose" (from Axiom D) is potential; its "manifestation" is actual. The gap between pi(entity) and M(entity, Φ) explains runtime surprises.

### K3. Context Projections

```
∀e ∈ C, ∀φ ∈ Φ:
  π_static(e) = compile-time visible context
  π_dynamic(e, φ) = runtime context

Truth(e) requires both: π_static ∩ π_dynamic
```

**Interpretation:** Static analysis sees π_static; runtime observes π_dynamic. Complete understanding requires both projections. This justifies hybrid analysis pipelines.

**Validation Status:** Formalization in progress. Empirical support from dynamic tracing experiments.

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

### Axiom Group E (Constructal): ⚠️ PARTIALLY GROUNDED

Bejan's Constructal Law is **empirically validated** across multiple physical and biological systems but **debated as universal mathematical axiom**. In SMoC, treat as:
- **Heuristic principle** for understanding code evolution
- **Design guideline** (minimize flow resistance)
- **NOT a formal theorem** requiring proof

### Axiom Group A (MECE Partition): ✅ GROUNDED (Novel Application)

The Lawvere argument (A1.1) applies **standard mathematics**. The application to software documentation motivation appears **NOVEL** (no prior literature found applying this to software systems).

### Axiom Grounding Summary

| Axiom Group | Mathematical Field | Status | Academic Source |
|-------------|-------------------|--------|-----------------|
| A (Set Structure) | Set Theory | ✅ GROUNDED | Lawvere (1969), standard partitions |
| B (Graph) | Graph Theory | ✅ STANDARD | Directed graphs, reachability |
| C (Levels) | Order Theory | ✅ STANDARD | Total orders, lattices |
| D (Purpose) | Dynamical Systems | ⚡ INSPIRED BY | Friston FEP (2022) - analogous |
| E (Constructal) | Thermodynamics | ⚠️ HEURISTIC | Bejan (2008) - empirical |
| F (Emergence) | Information Theory | ⚡ INSPIRED BY | Tononi IIT (2020) - analogous |
| G (Observability) | Semiotics | ✅ GROUNDED | Peirce triadic structure |
| H (Consumer Classes) | Software Engineering | ⚡ PROPOSED | AI-assisted assessment (not empirical) |
| I (Recursive Intelligence) | Meta-theory | ✅ GROUNDED | Gödel/Tarski hierarchy (standard) |
| J (Information Topology) | Topology | ⚡ PROPOSED | Location-invariance principle (needs study) |
| K (Invocation Context) | Runtime Semantics | ⚠️ PROPOSED | Formalization in progress (75%) |

---

## References

### Project Documents
- `../../MODEL.md` -- Core model (builds on these axioms)
- `L1_DEFINITIONS.md` -- What EXISTS (depends on these axioms)
- `L2_PRINCIPLES.md` -- Behavioral principles (depends on axioms + definitions)
- `../../../wave/docs/theory/FOUNDATIONS_INTEGRATION.md` -- Lawvere proof with all lemmas
- `../../../wave/docs/CODESPACE_ALGEBRA.md` -- Full mathematical elaboration

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
*All axioms are either grounded in academic literature or explicitly marked as heuristic.*

---

## Navigation

**📍 Up:** [Theory Index](./THEORY_INDEX.md#FIXED)
**➡️ Next:** [L1: Definitions](./L1_DEFINITIONS.md#FIXED) - Terms derived from these axioms
**🔄 Loop:** [L3: Applications](./L3_APPLICATIONS.md#FIXED) - Practical implementations that validate these axioms

**See also:**
- [THEORY_AXIOMS.md](./THEORY_AXIOMS.md#FIXED) - Formal proof framework
- [STANDARD_MODEL_COMPLETE.md](./STANDARD_MODEL_COMPLETE.md#FIXED) - All layers integrated

**Implementation:**
- [DYNAMIC_OBSERVERS_IMPLEMENTATION_PLAN.md](../specs/DYNAMIC_OBSERVERS_IMPLEMENTATION_PLAN.md) - Implementation plan for Axioms E2 (Four Flows) and G1 (Three Observers)
