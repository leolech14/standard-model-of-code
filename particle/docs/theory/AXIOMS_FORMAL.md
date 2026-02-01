# Standard Model of Code: Formal Axiom Specification

**Status:** Academic Draft (LaTeX-ready)
**Version:** 1.0.0
**Date:** 2026-02-01

---

## Notation Conventions

| Symbol | Meaning |
|--------|---------|
| $\forall$ | Universal quantifier ("for all") |
| $\exists$ | Existential quantifier ("there exists") |
| $\in$ | Set membership |
| $\subseteq$ | Subset or equal |
| $\cap$ | Set intersection |
| $\cup$ | Set union |
| $\sqcup$ | Disjoint union (coproduct) |
| $\emptyset$ | Empty set |
| $\mathbb{R}$ | Real numbers |
| $\mathbb{N}$ | Natural numbers |
| $\mathcal{P}$ | Projectome (all project artifacts) |
| $\mathcal{C}$ | Codome (executable artifacts) |
| $\mathcal{X}$ | Contextome (non-executable artifacts) |
| $\mathcal{N}$ | Set of nodes (code entities) |
| $\mathcal{E}$ | Set of edges (relationships) |
| $\mathcal{L}$ | Set of levels (holarchy) |
| $\mathcal{T}$ | Set of edge types |
| $\mathcal{O}$ | Set of observers |

---

## AXIOM GROUP A: Set Structure

### Axiom A1 (MECE Partition)

The Projectome partitions into exactly two disjoint universes.

$$\mathcal{P} = \mathcal{C} \sqcup \mathcal{X}$$

**Formally:**

$$\mathcal{C} \cap \mathcal{X} = \emptyset \land \mathcal{C} \cup \mathcal{X} = \mathcal{P}$$

**Where:**
- $\mathcal{C} = \{f \in \mathcal{P} \mid \text{executable}(f)\}$ (Codome)
- $\mathcal{X} = \{f \in \mathcal{P} \mid \neg\text{executable}(f)\}$ (Contextome)

**Classification:**
- Codome: `.py`, `.js`, `.ts`, `.go`, `.css`, `.html`, `.sql`, `.sh`, etc.
- Contextome: `.md`, `.yaml`, `.json` (configs), research outputs, agent state

### Axiom A1.1 (Necessity of Partition - Lawvere)

**Theorem:** The partition $\mathcal{P} = \mathcal{C} \sqcup \mathcal{X}$ is mathematically necessary.

**Proof (via Lawvere's Fixed-Point Theorem, 1969):**

Let $A = \mathcal{C}$ and $B = \{0, 1\}$ (semantic values). Consider the negation function $\neg: B \to B$ where $\neg(1) = 0$ and $\neg(0) = 1$.

The negation function has no fixed point:
$$\forall b \in B: \neg(b) \neq b$$

By Lawvere's Theorem:
$$(\exists \phi: A \twoheadrightarrow B^A) \Rightarrow (\forall f: B \to B, \exists b: f(b) = b)$$

Contrapositive:
$$(\exists f: B \to B, \forall b: f(b) \neq b) \Rightarrow (\nexists \phi: A \twoheadrightarrow B^A)$$

Since $\neg$ has no fixed point:
$$\nexists \phi: \mathcal{C} \twoheadrightarrow \{0,1\}^{\mathcal{C}}$$

Therefore code cannot fully specify its own semantics. Semantics must come from an external source $\mathcal{X}$. The partition is necessary for semantic completeness. $\square$

**Reference:** Lawvere, F.W. (1969). "Diagonal Arguments and Cartesian Closed Categories." *Lecture Notes in Mathematics* 92.

### Axiom A2 (Cardinality Preservation)

$$|\mathcal{P}| = |\mathcal{C}| + |\mathcal{X}|$$

$$|\mathcal{N}| \geq |\mathcal{C}|$$

**Interpretation:** File count is preserved. Node count exceeds file count due to containment.

---

## AXIOM GROUP B: Graph Structure

### Axiom B1 (Directed Graph)

Code structure is a typed directed graph.

$$G = (\mathcal{N}, \mathcal{E})$$

**Where:**
$$\mathcal{E} \subseteq \mathcal{N} \times \mathcal{N} \times \mathcal{T}$$

**Edge types:**
$$\mathcal{T} = \{\text{calls}, \text{imports}, \text{inherits}, \text{implements}, \text{contains}, \text{uses}, \text{references}, \ldots\}$$

### Axiom B2 (Transitivity of Reachability)

**Adjacency matrix:**
$$A: \mathcal{N} \times \mathcal{N} \to \{0, 1\}$$

$$A(i,j) = 1 \Leftrightarrow \exists t \in \mathcal{T}: (n_i, n_j, t) \in \mathcal{E}$$

**Transitive closure:**
$$A^+ = \bigcup_{k=1}^{|\mathcal{N}|} A^k$$

**Reachability:**
$$(A^+)_{ij} > 0 \Leftrightarrow \exists \text{ path from } n_i \text{ to } n_j$$

**Derived concepts:**
- Reachable set: $R(n) = \{m \in \mathcal{N} \mid (A^+)(n,m) > 0\}$
- Dead code: $\{n \in \mathcal{N} \mid R(n) = \emptyset \text{ from entry points}\}$

---

## AXIOM GROUP C: Level Structure (Holarchy)

### Axiom C1 (Total Order on Levels)

$(\mathcal{L}, \leq)$ is a totally ordered set (chain).

$$\mathcal{L} = \{L_{-3}, L_{-2}, L_{-1}, L_0, L_1, \ldots, L_{12}\}$$

$$L_{-3} \leq L_{-2} \leq L_{-1} \leq L_0 \leq \ldots \leq L_{12}$$

**With bounds:**
- $\bot = L_{-3}$ (BIT) - minimal element
- $\top = L_{12}$ (UNIVERSE) - maximal element

**Properties:**
- **Totality:** $\forall a, b \in \mathcal{L}: a \leq b \lor b \leq a$
- **Antisymmetry:** $a \leq b \land b \leq a \Rightarrow a = b$
- **Transitivity:** $a \leq b \land b \leq c \Rightarrow a \leq c$
- **Well-foundedness:** Has minimal element, no infinite descending chains

### Axiom C2 (Containment Implies Level Ordering)

$$\text{contains}(e_1, e_2) \Rightarrow \lambda(e_1) > \lambda(e_2)$$

**Where:**
$$\lambda: \text{Entity} \to \mathcal{L}$$

**Corollary:** $\text{contains}(a, b) \land \text{contains}(b, c) \Rightarrow \lambda(a) > \lambda(b) > \lambda(c)$

### Axiom C3 (Zone Boundaries)

**Zone mapping:**
$$\zeta: \mathcal{L} \to \mathcal{Z}$$

**Where:**
$$\mathcal{Z} = \{\text{PHYSICAL}, \text{SYNTACTIC}, \text{SEMANTIC}, \text{SYSTEMIC}, \text{COSMOLOGICAL}\}$$

$$\zeta(L) = \begin{cases}
\text{PHYSICAL} & L \in \{L_{-3}, L_{-2}, L_{-1}\} \\
\text{SYNTACTIC} & L = L_0 \\
\text{SEMANTIC} & L \in \{L_1, L_2, L_3\} \\
\text{SYSTEMIC} & L \in \{L_4, L_5, L_6, L_7\} \\
\text{COSMOLOGICAL} & L \in \{L_8, \ldots, L_{12}\}
\end{cases}$$

---

## AXIOM GROUP D: Purpose Field

### Axiom D1 (Purpose Field Definition)

Purpose is a vector field over nodes.

$$\pi: \mathcal{N} \to \mathbb{R}^k$$

**Where** $k$ is the purpose dimensionality (typically 8 for the dimensional classification).

### Axiom D2 (Purpose = Identity)

$$\text{Identity}(n) \equiv \pi(n)$$

**Interpretation:** An entity *is* what it is *for*.

### Axiom D3 (Transcendence - Purpose is Relational)

$$\pi(e) = f(\text{role\_in\_parent}(e))$$

An entity at level $L$ has no intrinsic purpose. Purpose emerges from participation at level $L+1$.

**Formal statement:**
$$\forall e \in \mathcal{N}, \forall L \in \mathcal{L}: \lambda(e) = L \Rightarrow \pi(e) = \Phi(\{p \in \mathcal{N} \mid \text{contains}(p, e)\})$$

### Axiom D4 (Focusing Funnel)

**Magnitude increases with level:**
$$\mathbb{E}[\|\pi(e)\| \mid \lambda(e) = L] \text{ is monotonically increasing in } L$$

**Variance decreases with level:**
$$\text{Var}[\theta(\pi(e)) \mid \lambda(e) = L] \text{ is monotonically decreasing in } L$$

**Where** $\theta$ is the angular direction of the purpose vector.

### Axiom D5 (Emergence Signal)

$$\|\pi(\text{parent})\| > \sum_{i} \|\pi(\text{child}_i)\|$$

**When** this inequality holds, emergent properties exist at the parent level.

### Axiom D6 (Crystallization)

**Human intent evolves:**
$$\frac{d\pi_{\text{human}}}{dt} \neq 0$$

**Code intent is frozen:**
$$\frac{d\pi_{\text{code}}}{dt} = 0 \text{ (between commits)}$$

**Drift:**
$$\Delta\pi(t) = \pi_{\text{human}}(t) - \pi_{\text{code}}(t)$$

**Technical debt:**
$$\text{Debt}(T) = \int_{t_{\text{commit}}}^{T} \left|\frac{d\pi_{\text{human}}}{dt}\right| dt$$

---

## AXIOM GROUP E: Flow Dynamics

### Axiom E1 (Constructal Principle)

Code evolves toward configurations that minimize flow resistance.

$$\frac{d\mathcal{C}}{dt} = \nabla H$$

**Where:**
- $\mathcal{C}$ = codebase configuration
- $H$ = constructal health metric (flow ease)

**Reference:** Bejan, A. & Lorente, S. (2008). *Design with Constructal Theory*. Wiley.

### Axiom E2 (Flow Resistance)

$$R(\text{path}) = \sum_{\text{edge} \in \text{path}} r(\text{edge})$$

**Where** $r$ is the per-edge resistance.

**Four flow types:**
1. **Static flow:** Dependencies, imports, calls
2. **Runtime flow:** Data flow, control flow
3. **Change flow:** How easily changes propagate
4. **Human flow:** How easily understanding propagates

---

## AXIOM GROUP F: Emergence

### Axiom F1 (Emergence Definition - Tononi/IIT)

Emergence occurs when macro-level predicts as well as micro-level.

$$P(X_{t+1} \mid S_{\text{macro}}(t)) \geq P(X_{t+1} \mid S_{\text{micro}}(t))$$

**Where:**
- $S_{\text{macro}}$ = higher-level state (e.g., "this is a Repository")
- $S_{\text{micro}}$ = lower-level state (list of all methods)

### Axiom F2 (Emergence Metric)

$$\varepsilon = \frac{I(\text{System}; \text{Output})}{\sum_i I(\text{Component}_i; \text{Output})}$$

**Where** $I(X; Y)$ is mutual information.

**Interpretation:**
- $\varepsilon > 1$: Positive emergence (system has information components lack)
- $\varepsilon = 1$: No emergence
- $\varepsilon < 1$: Negative emergence (components interfere)

**Reference:** Tononi, G. et al. (2020). "Integrated Information Theory 4.0." *Consciousness & Cognition*.

---

## AXIOM GROUP G: Observability (Peircean Triad)

### Axiom G1 (Observability Completeness)

$$\text{CompleteObservability}(S) \Leftrightarrow \exists O_s, O_o, O_g \in \mathcal{O}:$$

$$O_s: \mathcal{P} \to \text{Manifest} \land O_o: \text{Pipeline} \to \text{Metrics} \land O_g: \text{Dialogue} \to \text{Trace}$$

**Where:**
- $O_s$ = Structural observer (what EXISTS)
- $O_o$ = Operational observer (what HAPPENS)
- $O_g$ = Generative observer (what is CREATED)

### Axiom G2 (Peircean Correspondence)

$$\text{STRUCTURAL} \leftrightarrow \text{Thirdness}$$
$$\text{OPERATIONAL} \leftrightarrow \text{Secondness}$$
$$\text{GENERATIVE} \leftrightarrow \text{Firstness}$$

**Reference:** Peirce, C.S. Triadic sign theory. See: Atkin, A. (2010). "Peirce's Theory of Signs." *Stanford Encyclopedia of Philosophy*.

### Axiom G3 (Minimal Triad)

**Theorem:** Two observers are insufficient for complete observability. The triad $\{O_s, O_o, O_g\}$ is minimal.

**Proof sketch:**
- Without $O_s$: Cannot know what exists (only what happens)
- Without $O_o$: Cannot know what happens (only what is declared)
- Without $O_g$: Cannot know how system evolves (only current state)

Therefore each observer is necessary. $\square$

---

## AXIOM GROUP H: Consumer Classes

### Axiom H1 (Three Consumer Classes)

$$\text{Consumer} = \{\text{END\_USER}, \text{DEVELOPER}, \text{AI\_AGENT}\}$$

### Axiom H2 (Universal Consumer)

$$\text{AI\_AGENT} \in \text{Consumer}(L_0) \cap \text{Consumer}(L_1) \cap \text{Consumer}(L_2)$$

**Where:**
- $L_0$ = Object language (code)
- $L_1$ = Meta-language (documentation)
- $L_2$ = Meta-meta-language (schemas, tools)

AI can consume all Tarski meta-levels; AI is the universal consumer.

### Axiom H3 (Mediation Principle)

$$\text{OptimalDesign} \Rightarrow \text{Optimize for AI\_AGENT consumption}$$

AI mediates between:
- Human interface: Natural language ($L_1$ Contextome)
- Machine interface: Structured data ($L_0$ Codome, $L_2$ schemas)

---

## AXIOM GROUP I: Dimensional Classification

### Axiom I1 (8-Dimensional Space)

Every code entity maps to an 8-dimensional coordinate.

$$\delta: \mathcal{N} \to D_1 \times D_2 \times D_3 \times D_4 \times D_5 \times D_6 \times D_7 \times D_8$$

**Dimensions:**

| Dim | Name | Domain |
|-----|------|--------|
| $D_1$ | NATURE | $\{\text{Code}, \text{Marker}, \text{Hybrid}, \text{Unknown}\}$ |
| $D_2$ | ASPECT | $\{\text{Data}, \text{Logic}, \text{Interface}, \ldots\}$ |
| $D_3$ | ROLE | $\{\text{Service}, \text{Repository}, \text{Utility}, \text{Entity}, \ldots\}$ |
| $D_4$ | LAYER | $\{\text{Presentation}, \text{Application}, \text{Domain}, \text{Infrastructure}\}$ |
| $D_5$ | SCOPE | $\{\text{Public}, \text{Protected}, \text{Internal}, \text{Private}\}$ |
| $D_6$ | PURITY | $\{\text{Pure}, \text{Impure}\}$ |
| $D_7$ | CARDINALITY | $\{\text{Singleton}, \text{Few}, \text{Many}\}$ |
| $D_8$ | MUTABILITY | $\{\text{Immutable}, \text{Mutable}\}$ |

### Axiom I2 (Orthogonality)

The dimensions are statistically independent.

$$\forall i \neq j: \text{Corr}(D_i, D_j) \approx 0$$

**Falsifiable prediction:** If $|\text{Corr}(D_i, D_j)| > 0.7$ for any pair, this axiom is violated.

### Axiom I3 (Completeness)

$$\forall n \in \mathcal{N}: \exists! a \in \mathcal{A}: \text{atom}(n) = a$$

**Where** $\mathcal{A}$ is the set of 167 atoms.

Every entity is classifiable into exactly one atom type.

---

## AXIOM GROUP J: Atom Taxonomy

### Axiom J1 (Atom Derivation)

Atoms are derived from dimensional combinations.

$$\mathcal{A} \subseteq D_1 \times D_2 \times D_3 \times D_4 \times D_5 \times D_6 \times D_7 \times D_8$$

Not all dimensional combinations yield valid atoms (sparsity).

### Axiom J2 (Atom Cardinality)

$$|\mathcal{A}| = 167$$

**Distribution:**
- Entity atoms: 35
- Service atoms: 28
- Structure atoms: 42
- Utility atoms: 22
- Other atoms: 40

### Axiom J3 (Mutual Exclusivity)

$$\forall a_1, a_2 \in \mathcal{A}: a_1 \neq a_2 \Rightarrow \text{Extension}(a_1) \cap \text{Extension}(a_2) = \emptyset$$

**Where** $\text{Extension}(a)$ is the set of entities classified as atom $a$.

---

## AXIOM GROUP K: Ring Structure

### Axiom K1 (Ring Partition)

Every entity belongs to exactly one ring.

$$\text{Ring}: \mathcal{N} \to \{\text{CORE}, \text{INNER}, \text{OUTER}, \text{SHELL}\}$$

### Axiom K2 (Ring Semantics)

- **CORE:** Central domain logic, stable, rarely changes
- **INNER:** Supporting infrastructure, moderate stability
- **OUTER:** External integrations, adapters, bridges
- **SHELL:** Entry points, CLI, API surfaces

### Axiom K3 (Ring Health)

A healthy codebase has balanced ring distribution.

$$\text{HealthyRingBalance} \Leftrightarrow \forall r \in \text{Ring}: 0.1 \leq \frac{|\{n \mid \text{Ring}(n) = r\}|}{|\mathcal{N}|} \leq 0.4$$

---

## Summary of Axiom Groups

| Group | Focus | Key Axiom |
|-------|-------|-----------|
| A | Set Structure | $\mathcal{P} = \mathcal{C} \sqcup \mathcal{X}$ |
| B | Graph Topology | $G = (\mathcal{N}, \mathcal{E})$ |
| C | Level Holarchy | $(\mathcal{L}, \leq)$ total order |
| D | Purpose Field | $\pi: \mathcal{N} \to \mathbb{R}^k$ |
| E | Flow Dynamics | $dC/dt = \nabla H$ |
| F | Emergence | $\varepsilon = I(\text{System})/\Sigma I(\text{Components})$ |
| G | Observability | Peircean triad ${O_s, O_o, O_g}$ |
| H | Consumers | AI as universal consumer |
| I | Dimensions | 8 orthogonal classification axes |
| J | Atoms | 167 entity types |
| K | Rings | 4-ring concentric structure |

---

## Falsifiable Predictions

The formal axioms generate testable predictions:

| ID | Prediction | Falsification Criterion |
|----|------------|------------------------|
| P1 | Complete Classification | Entity exists fitting 0 or 2+ atoms |
| P2 | Dimensional Orthogonality | $\|r\| > 0.7$ between dimensions |
| P3 | Level Ordering | contains(a,b) with $\lambda(a) \leq \lambda(b)$ |
| P4 | MECE Partition | Artifact both executable and non-executable |
| P5 | Emergence Signal | Parent magnitude $\leq$ child sum |
| P6 | Ring Balance | Healthy codebases with imbalanced rings |

---

*This document addresses Gap 2 (Axiom Formalization) from the SMC Academic Gap Analysis.*

## References

1. Lawvere, F.W. (1969). "Diagonal Arguments and Cartesian Closed Categories." *Lecture Notes in Mathematics* 92.
2. Bejan, A. & Lorente, S. (2008). *Design with Constructal Theory*. Wiley.
3. Tononi, G. et al. (2020). "Integrated Information Theory 4.0." *Consciousness & Cognition*.
4. Peirce, C.S. Collected Papers. See: Atkin, A. (2010). "Peirce's Theory of Signs." *Stanford Encyclopedia of Philosophy*.
5. Tarski, A. (1944). "The Semantic Conception of Truth." *Philosophy and Phenomenological Research*.
