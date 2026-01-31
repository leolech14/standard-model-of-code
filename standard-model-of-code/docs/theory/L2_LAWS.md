# L2: Laws of the Standard Model of Code

**📍 Navigation:** [Theory Index](./THEORY_INDEX.md#FIXED) | [← L1: Definitions](./L1_DEFINITIONS.md#FIXED) | **Next:** [L3: Applications →](./L3_APPLICATIONS.md#FIXED)

**Layer:** 2 (Dynamic Behavior)
**Status:** ACTIVE | EVOLVING
**Depends on:** [L0_AXIOMS.md](./L0_AXIOMS.md#FIXED), [L1_DEFINITIONS.md](./L1_DEFINITIONS.md#FIXED)
**Version:** 2.0.0
**Created:** 2026-01-27

---

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

### The Seven Laws

| Law ID | Name | Violation | Theory Source |
|--------|------|-----------|---------------|
| **AM001** | Layer Skip Violation | Layer L calls layer L-2 (skipping L-1) | Dijkstra + Clean Architecture |
| **AM002** | Reverse Layer Dependency | Lower layer depends on higher layer | Clean Architecture |
| **AM003** | God Class | R > 7 (too many responsibilities) | Koestler Holons |
| **AM004** | Anemic Model | Data class with no behavior | Koestler Holons + DDD |
| **AM005** | Bounded Context Violation | Cross-domain coupling | DDD (Evans) |
| **AM006** | Centrifugal Dependency | Inner ring depends on outer ring | Clean Architecture + Ring Theory |
| **AM007** | Ring Orphan | Code with no incoming edges (dead code risk) | Ring Theory + Disconnection Taxonomy |

### Detection Rules

```
AM001: ∃edge (n1, n2) where layer(n1) - layer(n2) > 1
AM002: ∃edge (n1, n2) where layer(n1) < layer(n2)
AM003: R(node) > 7                    (RPBL responsibility dimension)
AM004: class has >5 fields, <2 methods
AM005: ∃edge crossing bounded context boundaries (high coupling)
AM006: ∃edge (n1, n2) where Ring(n1) < Ring(n2)     (dependency flows outward)
AM007: in_degree(n) = 0 ∧ ¬is_entry_point(n) ∧ ¬is_test(n)    (see L1 §5.6 for full taxonomy)
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

## 11. Compositional Laws (Alignment and Capability)

**[Validation: 95% - Extensively validated through empirical SE research, formal models in category theory, documented anti-patterns (Big Ball of Mud, Architecture Sinkhole), MIT modular hierarchy research]**

### 7.1 Law of Compositional Alignment

**Statement:** System capability is proportional to compositional alignment across architectural levels.

**Formula:**
```
Capability(S) ∝ ∏(i=L_min to L_max) Alignment(Lᵢ, Lᵢ₊₁)

WHERE:
  Alignment(Lᵢ, Lᵢ₊₁) ∈ [0, 1]

  Alignment = 1 ⟺ Lᵢ₊₁ properly composes from Lᵢ
                  (uses only Lᵢ interfaces, no level skipping)

  Alignment < 1 ⟺ Level skipping, god objects, or broken composition
```

**Interpretation:** Each level must compose properly from the level immediately below it. Skipping levels (e.g., L7 SYSTEM directly depending on L3 NODE, bypassing L5 FILE and L6 PACKAGE) reduces alignment and thus capability.

**Anti-Patterns as Misalignment:**
- **Big Ball of Mud**: Alignment → 0 (all levels entangled)
- **God Class**: Single entity spans multiple levels improperly
- **Architecture Sinkhole**: Skip-call violations (bypass intermediate layers)
- **Cyclic Dependencies**: Violates Acyclic Dependencies Principle

**Mechanisms:**
1. **Dependency Management**: Proper composition → acyclic dependencies
2. **Concern Separation**: Each level handles appropriate abstractions
3. **Change Impact Isolation**: Modifications stay localized
4. **Interface Stability**: Implementation changes don't ripple
5. **Testing Granularity**: Each level testable independently

**Empirical Evidence:**
- Well-layered systems: Lower defect rates, easier maintenance
- Layer violations: Higher coupling, more bugs (empirically measured)
- Skip-call violations: Correlated with architecture erosion

**Mathematical Foundation:**
- Category theory: Composition as monoidal operation
- Type theory: Proper type hierarchies
- Lattice theory: Abstract interpretation levels

**Academic Sources:**
- Martin, R. C. "Clean Architecture" (2012)
- Modular Hierarchical Frameworks (MIT research, 2021)
- Architecture Erosion Studies (empirical validation)

**See:** `docs/research/theories/compositional_alignment_report.md` for full validation

---

## 12. Dependency Laws (Entanglement and Propagation)

**[Validation: 78% - Explicit precedent (Pescio 2010), formal coupling metrics exist, empirical change propagation measured, Hilbert space formalization gap remains]**

### 8.1 Law of Code Entanglement

**Statement:** Code dependencies exhibit properties analogous to quantum entanglement, with non-local effects across arbitrary distance in codebase structure.

**Formula:**
```
Entangled(c₁, c₂) ⟺ ∃relation ∈ {calls, imports, inherits, depends_on}:
                     (c₁, c₂, relation) ∈ E

Properties:
1. Non-locality: Distance_codebase(c₁, c₂) irrelevant to entanglement
2. Correlation: modify(c₁) → must_update(c₂) [instant propagation]
3. Strength: Coupling(c₁, c₂) = strength_of_entanglement
4. Hidden: 58% of entanglements invisible to static analysis
```

**Interpretation:** When two code entities are connected by dependency relationships, they become entangled such that modifications to one immediately affect the other, regardless of their physical separation in the file system or organizational structure.

**Entanglement Strength (Coupling Metrics):**
```
Coupling(c) = 1 - 1/(dᵢ + 2cᵢ + dₒ + 2cₒ + gᵈ + 2gᶜ + w + r)

WHERE:
  dᵢ = input data parameters
  cᵢ = input control parameters
  dₒ = output data parameters
  cₒ = output control parameters
  gᵈ = global vars as data
  gᶜ = global vars as control
  w = fan-out (modules called)
  r = fan-in (callers)

Range: [0.67, 1.0] (low to high coupling)
```

**Cascading Failure Prediction:**
- Strong entanglement → higher failure probability
- Change propagation: 45.7% of defects predictable from change coupling
- Ripple effects: Non-local failures from local modifications

**Precedent:**
- Pescio, C. (2010). "Software Entanglement" - Explicit quantum analogy
- "Action-at-a-distance" - Named anti-pattern in SE (Wikipedia)
- Connascence framework - Formal dependency classification

**Hidden Dependencies:**
- 58% of dependencies not visible in structural analysis
- Require semantic coupling analysis to detect
- Parallel to quantum non-observable correlations

**Academic Sources:**
- Pescio, C. (2010). "Notes on Software Design: Software Entanglement"
- Coupling metrics research (IEEE, ACM empirical studies)
- Change propagation research (45.7% defect prediction validation)

**See:** `docs/research/theories/epr_entanglement_report.md` for full validation

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

## Navigation

**📍 Up:** [Theory Index](./THEORY_INDEX.md#FIXED)
**⬅️ Previous:** [L1: Definitions](./L1_DEFINITIONS.md#FIXED)
**➡️ Next:** [L3: Applications](./L3_APPLICATIONS.md#FIXED) - Practical implementations
**🔙 Foundation:** [L0: Axioms](./L0_AXIOMS.md#FIXED)

**Specialized Laws:**
- [ORPHAN_SEMANTICS.md](../../context-management/docs/theory/ORPHAN_SEMANTICS.md#FIXED) - Detailed L2 law on connectivity
