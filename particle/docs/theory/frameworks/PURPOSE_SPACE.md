# PURPOSE SPACE: The Continuous Mathematical Space for Code Purpose Analysis

**Navigation:** [Theory Index](../INDEX.md) | [L0: Axioms](../foundations/L0_AXIOMS.md) | [L1: Definitions](../foundations/L1_DEFINITIONS.md) | [Frameworks](./)

**Layer:** L0-L1 Bridge (extends Axiom Group D with formal space definition)
**Status:** THEORETICAL | PARTIALLY IMPLEMENTED
**Depends on:** [L0_AXIOMS.md](../foundations/L0_AXIOMS.md) (Axiom Group D), [L1_DEFINITIONS.md](../foundations/L1_DEFINITIONS.md) (33 canonical roles)
**Created:** 2026-03-05
**Version:** 1.0.0

---

## Motivation

Axiom D1 declares that purpose is a vector field: `P: N -> R^k`. But where do these vectors *live*? What operations are well-defined on them? Can we measure distance between purposes, detect clusters, find holes, track evolution?

This document defines the **Purpose Space** M — a continuous mathematical space equipped with metric, topological, measure-theoretic, algebraic, and categorical structure. Every code entity maps to a point in M. Every architectural question becomes a geometric question on M.

**The unifying insight:** The seven mathematical frameworks used by the Standard Model (FCA, graph modularity, information theory, category theory, TDA, matroid theory, hypergraph theory) are not separate tools. They are **natural operations on Purpose Space** — different lenses on a single underlying object.

**Terminology note:** We use "Purpose Space" as the primary term. The more specific "Purpose Manifold" is aspirational — it implies smoothness properties we have not yet proven. See [Risk Assessment](#risk-assessment).

---

## 1. The Purpose Space M

### 1.1 Definition

**Purpose Space** is a tuple:

```
M = (S, d, mu, tau, A)

WHERE:
  S   = purpose state space (the set of all possible purpose vectors)
  d   = metric (distance function on S)
  mu  = measure (probability/entropy structure on S)
  tau = topology (neighborhoods, connectedness, holes)
  A   = algebraic structure (lattice, independence, composition)
```

Each code node n in the codebase maps to a point p(n) in M via the purpose field:

```
P: N -> M
n |-> p(n) = (r_1, r_2, ..., r_k)

WHERE:
  N = set of all code nodes (atoms, containers, files)
  k = number of canonical roles (currently k = 33)
  r_i = weight of role i in node n's purpose (r_i >= 0, sum r_i = 1)
```

**Source:** L0 Axiom D1 (`P: N -> R^k`) — this section formalizes the codomain.

### 1.2 Dimensionality

The dimension of M is determined by the number of canonical roles in the classification system:

```
dim(M) = k = |{canonical roles}| = 33

Canonical roles: Controller, Service, Repository, Query, Command,
  Validator, Mapper, Factory, Handler, Middleware, Decorator,
  Observer, Strategy, Adapter, Facade, Gateway, Processor,
  Transformer, Emitter, Listener, Scheduler, Worker, Client,
  Provider, Config, Helper, Utility, Model, Schema, DTO,
  Exception, Enum, Test
```

**Implementation:** `purpose_field.py:174-216` defines PURPOSE_TO_LAYER with these 33 roles.

**Simplification:** In practice, most codebases use a subset of roles. The *effective* dimensionality is often k_eff << 33. Principal Component Analysis (PCA) or UMAP can project M to a lower-dimensional space for visualization while preserving distance relationships.

### 1.3 Purpose Vectors

A purpose vector p(n) lives on the (k-1)-simplex:

```
Delta^{k-1} = { (r_1, ..., r_k) in R^k : r_i >= 0, sum_i r_i = 1 }
```

This is a probability distribution over roles. A node with a single clear purpose has a sharp (low-entropy) distribution. A god class has a flat (high-entropy) distribution.

**Examples:**

```
p(UserRepository) = (0, 0, 0.85, 0.10, 0.05, 0, ..., 0)
                           ^Repository ^Query ^Command
  -> Sharp: coherent purpose

p(GodClass) = (0.12, 0.15, 0.10, 0.08, 0.11, 0.09, ...)
  -> Flat: scattered purpose (entropy near H_max)
```

**Connection to L2 SS1.3:** The pi3 (organelle purpose) of a container is determined by the distribution of its children's purpose vectors in M.

---

## 2. Metric Structure (Distance)

### 2.1 Purpose Distance

The distance between two purpose vectors defines how "different" their architectural roles are:

```
d(p_i, p_j) = 1 - cos(p_i, p_j)

WHERE:
  cos(p_i, p_j) = (p_i . p_j) / (||p_i|| * ||p_j||)

PROPERTIES:
  d(p, p) = 0                    (identity)
  d(p_i, p_j) = d(p_j, p_i)     (symmetry)
  d(p_i, p_j) >= 0               (non-negativity)
  d in [0, 1]                    (bounded)
```

**Why cosine distance?** Purpose vectors are distributions — their magnitude is less important than their *direction* in role-space. A controller with 5 methods and a controller with 50 methods point in the same direction.

**Alternative metrics:**
- Jensen-Shannon divergence: `JSD(p || q) = (1/2) KL(p||m) + (1/2) KL(q||m)` where `m = (p+q)/2`. Symmetric, bounded, information-theoretically grounded. Better for comparing distributions.
- Earth mover's distance (Wasserstein): `W(p, q) = inf_{gamma} sum gamma_{ij} c_{ij}`. Accounts for semantic similarity between roles (e.g., Query is closer to Repository than to Controller).

### 2.2 Coherence as Self-Distance

A container's coherence measures how spread its children are in M:

```
Coherence(container) = 1 - H(children) / H_max

WHERE:
  H(children) = -sum_i p_i * log2(p_i)      (Shannon entropy of child purpose distribution)
  H_max = log2(k_unique)                     (maximum entropy for k_unique distinct purposes)
  p_i = fraction of children with purpose i
```

**Implementation:** `purpose_field.py:358-370` — this is the exact formula already in production.

**Geometric interpretation:** Coherence = 1 means all children cluster at a single point in M (perfect focus). Coherence = 0 means children are maximally spread across M (complete scatter).

### 2.3 Layer Distance

The distance between architectural layers is the ordinal gap:

```
d_layer(L_i, L_j) = |i - j|

Layer ordering (from purpose_field.py:19-26):
  PRESENTATION = 0
  APPLICATION = 1
  DOMAIN = 2
  INFRASTRUCTURE = 3
  TESTING = 4 (orthogonal)
```

**Connection to L0 Axiom C1:** Layer assignment L: N -> {1..6} induces a partition of M into layer-regions. Cross-layer distance > 1 signals a layer skip violation (AM001).

### 2.4 Technical Debt as Geodesic Distance

**Novel concept.** Technical debt is the geodesic distance in M between a code entity's *frozen purpose* (at last commit) and the developer's *current intent*:

```
debt(n, t) = d_M(P_code(n), P_human(n, t))

WHERE:
  P_code(n) = purpose crystallized at last commit (static)
  P_human(n, t) = current human intent (evolving continuously)
  d_M = geodesic distance on Purpose Space
```

**Connection to L0 Axiom D6 (Crystallization):** Code freezes a point in M; human intent drifts. The gap is technical debt.

**Connection to L2 SS7.1:** Technical debt as drift integral: `Debt(T) = integral from t_commit to T of |dP_human/dt| dt`.

---

## 3. Measure Structure (Entropy)

### 3.1 Shannon Entropy on M

Purpose distributions carry a natural measure — Shannon entropy quantifies uncertainty:

```
H(P_n) = -sum_{i=1}^{k} r_i * log2(r_i)

WHERE:
  P_n = purpose vector of node n
  r_i = weight of role i (r_i >= 0, sum r_i = 1)
  Convention: 0 * log2(0) = 0
```

**Range:** `0 <= H <= log2(k)`. For k = 33: `H_max = log2(33) ~ 5.04 bits`.

**Implementation:** `purpose_field.py:358-370` — production code.

### 3.2 Mutual Information (Purpose Leakage)

**Novel concept.** Mutual information between purpose distributions of two modules quantifies *purpose leakage* — how much knowing one module's purpose tells you about another's:

```
I(P_A; P_B) = H(P_A) + H(P_B) - H(P_A, P_B)

WHERE:
  H(P_A, P_B) = joint entropy of purpose distributions
  I >= 0 always
  I = 0 iff P_A and P_B are independent
```

**Architectural interpretation:**
- `I(P_A; P_B) ~ 0`: Modules have independent purposes (good separation)
- `I(P_A; P_B) >> 0`: Purposes are entangled (potential violation of bounded context)

**Connection to L0 Axiom F2:** The emergence metric `epsilon = I(System; Output) / sum I(Component_i; Output)` already uses mutual information. Purpose leakage extends this to inter-module analysis.

### 3.3 Conditional Entropy (Layer Coherence)

How much uncertainty remains about a node's purpose *given* its architectural layer:

```
H(Purpose | Layer) = sum_L P(L) * H(Purpose | Layer = L)

Low H(Purpose|Layer) -> Layers are purpose-homogeneous (good architecture)
High H(Purpose|Layer) -> Layers mix many purposes (eroded architecture)
```

### 3.4 Transfer Entropy (Directed Purpose Flow)

Transfer entropy captures *directed* information flow between modules over time:

```
T_{X->Y} = sum p(y_{t+1}, y_t, x_t) * log [ p(y_{t+1} | y_t, x_t) / p(y_{t+1} | y_t) ]
```

**Application:** Detect which modules *cause* purpose drift in others. A module with high outgoing transfer entropy is an architectural driver; one with high incoming transfer entropy is architecturally dependent.

---

## 4. Topological Structure (Shape)

### 4.1 Purpose Space as a Topological Space

The metric d induces a topology tau on M. Open balls `B(p, epsilon) = {q in M : d(p, q) < epsilon}` define neighborhoods.

**Key topological features of a codebase in M:**

| Feature | Mathematical | Architectural Meaning |
|---------|-------------|----------------------|
| Connected components | H_0 (0th homology) | Purpose clusters (groups of nodes with similar roles) |
| Holes | H_1 (1st homology) | Missing purposes or circular dependencies |
| Voids | H_2 (2nd homology) | Higher-order architectural gaps |
| Persistence | Birth-death pairs | Robustness of structural features |

### 4.2 Persistent Homology

Apply a filtration (sweep threshold parameter epsilon from 0 to max) and track which topological features appear (birth) and disappear (death):

```
Filtration: K_0 subset K_1 subset ... subset K_n

WHERE:
  K_t = simplicial complex at threshold t
  Nodes within distance t of each other form edges (1-simplices)
  Triangles of pairwise-close nodes form 2-simplices
```

**Persistence diagram:** Each feature becomes a point (birth, death). Features with long persistence (death - birth >> 0) are robust architectural structures. Short-lived features are noise.

**Novel application:** TDA is mathematically mature but has NOT been applied to software dependency graphs for architectural analysis. Our interpretation:
- `H_0` features = purpose clusters (robust communities of similarly-purposed code)
- `H_1` features = circular dependencies (cycles in the dependency graph)

**Connection to** [TOPOLOGICAL_BOUNDARIES.md](../TOPOLOGICAL_BOUNDARIES.md): Zone phase transitions are topological phase changes — the topology of M changes as we cross architectural boundaries.

### 4.3 Multi-Scale Architecture

Persistent homology reveals architecture at multiple scales simultaneously:

```
Scale 0 (fine):   Individual method purposes
Scale 1 (medium): Class-level purpose clusters
Scale 2 (coarse): Module/package-level domains
Scale 3 (macro):  System-level architectural zones
```

Features that persist across many scales are the fundamental architectural structures.

---

## 5. Algebraic Structure (Composition)

### 5.1 Purpose Lattice (FCA)

The set of all purpose concepts forms a lattice ordered by generality:

```
Concept lattice B(K) from formal context K = (G, M_attr, I)

WHERE:
  G = set of code containers (objects)
  M_attr = set of purpose attributes (roles, patterns)
  I subset G x M_attr = incidence relation (container has attribute)
```

Each concept is a pair (extent, intent):
- **Extent:** Set of containers sharing all attributes in the intent
- **Intent:** Set of attributes shared by all containers in the extent

**Implementation:** `purpose_field.py:149-170` — EMERGENCE_RULES are hand-crafted FCA concepts:

```python
# These frozensets ARE formal concepts:
frozenset(["Query", "Command"]): "Repository"    # extent: all Repos, intent: {Query, Command}
frozenset(["Transform", "Compute"]): "Processor"  # extent: all Procs, intent: {Transform, Compute}
```

The lattice provides a **partial order on purposes**: Repository is more specific than a container with only Query children.

### 5.2 Independence Structure (Matroid)

**Novel application.** A matroid on purposes formalizes which combinations of purposes can coexist coherently:

```
M_purpose = (E, I)

WHERE:
  E = {p_1, ..., p_k}     (set of possible purposes)
  I subset 2^E             (independent sets — coherent combinations)

Axioms:
  1. {} in I               (empty set is independent)
  2. J subset I in I => J in I   (hereditary)
  3. |I| < |J|, I,J in I => exists e in J\I : I + {e} in I   (exchange)
```

**Rank function:** `r(S) = max |I|` for `I subset S`, `I in I` — the maximum number of independent purposes a container can hold.

**God class formalization:** A container exceeds its matroid rank when:

```
|active_purposes(container)| > r(M_purpose)

CURRENT HEURISTIC (purpose_field.py:374-375):
  coherence < 0.4 AND total >= 8 AND unique >= 4

MATROID FORMALIZATION:
  God class <=> container's purpose set is DEPENDENT in M_purpose
  <=> it contains a CIRCUIT (minimal dependent set)
```

**Why matroid?** The greedy algorithm is optimal on matroids. This means automated refactoring (selecting which purposes to keep vs. extract) has provably optimal solutions.

### 5.3 Higher-Order Structure (Hypergraph)

**Novel application.** Standard graphs model pairwise dependencies. Hypergraphs model n-ary dependencies:

```
H = (V, E_hyper)

WHERE:
  V = code elements
  E_hyper subset 2^V   (hyperedges — subsets of any size)
```

**Application to composite purposes:**

```
Decorator stack: {base, decorator_1, decorator_2} -> composite purpose
Mixin composition: {class, mixin_1, mixin_2} -> emergent behavior
Middleware chain: {handler, auth, logging, caching} -> pipeline purpose
```

**Implementation:** `purpose_field.py:149-170` — EMERGENCE_RULES with frozenset keys ARE hyperedge definitions. Each frozenset is a hyperedge connecting multiple child purposes to produce a composite purpose.

**Connection to L2 SS2.2 (Emergence Criterion):** Hyperedges formalize the "whole > sum of parts" principle. The composite purpose of a hyperedge is not simply the union of its vertex purposes.

---

## 6. Categorical Structure (Mappings)

### 6.1 The Category of Purposes

```
Category Purp:
  Objects: purpose labels {Controller, Service, Repository, ...}
  Morphisms: subsumption relations (Repository -> DataAccess, Service -> BusinessLogic)
  Composition: transitive subsumption
  Identity: each purpose subsumes itself
```

### 6.2 The Category of Layers

```
Category Layer:
  Objects: architectural layers {Presentation, Application, Domain, Infrastructure, Testing}
  Morphisms: dependency direction (Presentation -> Application -> Domain -> Infrastructure)
  Composition: transitive dependency
  Identity: each layer depends on itself (trivially)
```

### 6.3 PURPOSE_TO_LAYER as a Functor

The mapping from purposes to layers is a functor `F: Purp -> Layer`:

```
F: Purp -> Layer

F(Controller) = Presentation
F(Service) = Application
F(Repository) = Domain
F(Factory) = Domain
F(Middleware) = Infrastructure
F(Test) = Testing
...
```

**Implementation:** `purpose_field.py:174-216` — this dict IS the functor F.

**Functor preservation:** F must preserve composition:

```
If purpose p1 subsumes p2 (morphism in Purp),
then F(p1) depends on F(p2) (morphism in Layer).

Violation of this property = architectural inconsistency.
```

**Connection to L0 SS10.1:** The Documentation Functor `F: C -> X` maps code to docs. Our PURPOSE_TO_LAYER functor maps purposes to layers. Both are concrete instances of structure-preserving maps.

### 6.4 Presheaf Model (Consistent Purpose Assignment)

**A presheaf** on the dependency DAG ensures consistent purpose assignment:

```
F: DAG^op -> Set

For each node n: F(n) = set of valid purposes for n
For each edge (n1 -> n2): F(n1->n2) = restriction map

Consistency condition:
  If n1 depends on n2, then the purposes assigned to n1
  must be compatible with purposes assigned to n2.
```

**Connection to L0 SS10.4 (Profunctors):** Concordance scoring uses profunctors `R: C^op x X -> [0,1]`. The presheaf model is a special case where we track *purpose* consistency rather than documentation concordance.

### 6.5 Natural Transformations (Reassignment)

A natural transformation `eta: F => G` between two purpose assignment functors represents a coherent reassignment:

```
For every node n:
  eta_n: F(n) -> G(n)     (reassign purpose of n)

Naturality square:
  For every dependency edge (n1 -> n2):
    G(n1->n2) o eta_n1 = eta_n2 o F(n1->n2)

  (Reassignment commutes with dependency propagation)
```

**Practical meaning:** A valid refactoring that changes purpose assignments across a codebase is a natural transformation. The naturality condition ensures that after refactoring, dependencies still flow in the correct direction.

---

## 7. Dynamics (Evolution)

### 7.1 Gradient Flow

Purpose evolves to resolve incoherence — this is the central dynamical equation:

```
dP/dt = -grad(Incoherence(C))

WHERE:
  P = purpose field (assignment of purpose vectors to nodes)
  Incoherence(C) = measure of architectural disorder
  grad = gradient on Purpose Space M
```

**Source:** L0 Axiom D7 — this is the fundamental dynamics equation.

**Incoherence functional:**

```
Incoherence(C) = alpha * sum_n H(P_n)                   (purpose entropy)
               + beta  * sum_{(i,j)} d(P_i, P_j) * w_ij  (cross-purpose coupling)
               + gamma * |violations|                     (antimatter count)

WHERE:
  alpha, beta, gamma = relative weights
  w_ij = dependency weight between nodes i, j
```

The system evolves toward states where:
- Each node has sharp (low-entropy) purpose
- Connected nodes have similar purposes
- No architectural violations exist

### 7.2 Crystallization (Freeze-Thaw Dynamics)

**Source:** L0 Axiom D6.

Code purpose exhibits **punctuated equilibrium**:

```
Phase 1 (Frozen):  P_code = constant          (between commits)
Phase 2 (Thaw):    P_code jumps to P_human    (at commit)
Phase 3 (Frozen):  P_code = new constant      (until next commit)

Meanwhile: dP_human/dt != 0 always            (human intent evolves continuously)
```

**In Purpose Space:** Commits are discrete jumps between points in M. Human intent traces a continuous curve. The distance between the discrete point and the continuous curve is technical debt (Section 2.4).

**Connection to L2 SS7.3:** Crystallization events as phase transitions.

### 7.3 Attractor Basins

Well-designed architectures create **attractor basins** in M — regions where the gradient flow naturally pulls code:

```
Attractor basin B_purpose = {p in M : gradient_flow(p) -> p_stable}

WHERE:
  p_stable = stable purpose assignment (fixed point of dP/dt = 0)
```

**Architectural implication:** If your architecture has well-defined attractor basins, new code naturally "falls into" the right purpose region. Poor architecture has shallow or overlapping basins — code can easily drift into wrong regions.

---

## 8. Calculability

### 8.1 Well-Defined Operations on M

The following operations are currently calculable (implemented or directly implementable):

| Operation | Formula | Status | Code Location |
|-----------|---------|--------|--------------|
| Purpose similarity | `cos(p_i, p_j)` | IMPLEMENTED | purpose_field.py |
| Purpose entropy | `H = -sum p_i log2(p_i)` | IMPLEMENTED | purpose_field.py:358-370 |
| Coherence score | `1 - H/H_max` | IMPLEMENTED | purpose_field.py:362-369 |
| God class detection | `coherence < 0.4 AND total >= 8 AND unique >= 4` | IMPLEMENTED | purpose_field.py:374-375 |
| Layer assignment | `PURPOSE_TO_LAYER[role]` | IMPLEMENTED | purpose_field.py:174-216 |
| Composite purpose | `EMERGENCE_RULES[frozenset(children)]` | IMPLEMENTED | purpose_field.py:149-170 |
| Purpose distance | `d(p_i, p_j) = 1 - cos(p_i, p_j)` | DERIVABLE | From existing vectors |
| Mutual information | `I(P_A; P_B) = H(A) + H(B) - H(A,B)` | THEORETICAL | Requires joint distribution |
| Persistent homology | `H_0, H_1` from filtration | THEORETICAL | Requires giotto-tda |
| Matroid rank | `r(S) = max independent subset` | THEORETICAL | Requires independence oracle |
| Hypergraph clustering | Spectral methods on incidence matrix | THEORETICAL | Requires hypergraph library |
| Presheaf consistency | Naturality check on DAG | THEORETICAL | Requires category theory tooling |

### 8.2 Purpose Aggregation

Computing a container's purpose from its children's purposes:

```
p(container) = weighted_centroid({p(child_i)})

= sum_i w_i * p(child_i) / sum_i w_i

WHERE:
  w_i = weight of child i (LOC, centrality, or confidence)
```

**Implementation:** The current EMERGENCE_RULES provide a lookup-based approximation. The centroid formula generalizes to cases not covered by rules.

### 8.3 Anomaly Detection

Nodes that are far from their cluster center in M are anomalies:

```
anomaly_score(n) = d(p(n), centroid(cluster(n)))

IF anomaly_score(n) > threshold:
  n is misplaced (wrong module, wrong layer, wrong package)
```

### 8.4 Health as a Functional on M

System health is an integral over Purpose Space:

```
Health[P] = integral_M rho(p) * q(p) dp

WHERE:
  rho(p) = density of code nodes at point p in M
  q(p) = quality function at point p (coherence, alignment, completeness)
```

This integrates quality across the entire purpose distribution, weighting by how much code occupies each region.

---

## Risk Assessment

| Risk | Mitigation |
|------|-----------|
| "Manifold" implies smoothness not yet proven | Use "Purpose Space" as primary; "manifold" aspirational |
| k=33 may be too high for practical computation | PCA/UMAP for effective dimensionality reduction |
| Cosine distance may not capture role semantics | Earth mover's distance as alternative (Section 2.1) |
| Joint distributions needed for MI are hard to estimate | Approximate via co-occurrence in dependency graphs |
| Matroid independence oracle is expensive | Start with partition matroid (simpler, tractable) |

---

## Summary: The Seven Frameworks as Operations on M

| Framework | What It Does on M | Section |
|-----------|------------------|---------|
| **FCA** | Discovers the lattice structure of M (concept ordering) | SS5.1 |
| **Graph Modularity** | Partitions M into communities (purpose clusters) | SS2.2 |
| **Information Theory** | Measures entropy and information flow on M | SS3 |
| **Category Theory** | Maps between M and other spaces (layers, docs) | SS6 |
| **TDA** | Reveals the shape of M (holes, components, persistence) | SS4 |
| **Matroid Theory** | Defines independence structure on M (coherence limits) | SS5.2 |
| **Hypergraph Theory** | Models higher-order composition in M | SS5.3 |

Each framework provides a **projection** of the full Purpose Space onto a specific structural aspect. Together, they form a comprehensive analytical toolkit.

**For detailed formulas, citations, and implementation guidance, see the individual framework files:**
- [GRAPH_THEORY.md](./GRAPH_THEORY.md) | [ORDER_THEORY.md](./ORDER_THEORY.md) | [INFORMATION_THEORY.md](./INFORMATION_THEORY.md)
- [CATEGORY_THEORY.md](./CATEGORY_THEORY.md) | [TOPOLOGY.md](./TOPOLOGY.md) | [MATROID_THEORY.md](./MATROID_THEORY.md) | [HYPERGRAPH_THEORY.md](./HYPERGRAPH_THEORY.md)

---

## References

### Foundational
- Alon, U. et al. (2019). "code2vec: Learning distributed representations of code." POPL. [3000+ citations; proves code CAN live in continuous space]
- Springer (2007). "A metric space for computer programs." J. Supercomputing. [Formal metric space axioms for programs]
- Zhang et al. (2026). "Theory of Code Space." arXiv:2603.00601. [AI agents understanding software architecture spatially]

### Cross-References (Standard Model of Code)
- [L0_AXIOMS.md](../foundations/L0_AXIOMS.md) — Axiom D1 (P: N -> R^k), D6 (Crystallization), D7 (Gradient flow), F2 (Emergence via MI)
- [L1_DEFINITIONS.md](../foundations/L1_DEFINITIONS.md) — 33 canonical roles, classification system
- [L2_PRINCIPLES.md](../foundations/L2_PRINCIPLES.md) — Purpose hierarchy (SS1), Emergence (SS2), Shannon (SS6), Evolution (SS7)
- [L3_APPLICATIONS.md](../foundations/L3_APPLICATIONS.md) — Q-scores (SS1), coherence metric Q_cohere using Shannon entropy
- [TOPOLOGICAL_BOUNDARIES.md](../TOPOLOGICAL_BOUNDARIES.md) — Zone phase transitions as topology changes
- Framework files: [GRAPH_THEORY](./GRAPH_THEORY.md) | [ORDER_THEORY](./ORDER_THEORY.md) | [INFORMATION_THEORY](./INFORMATION_THEORY.md) | [CATEGORY_THEORY](./CATEGORY_THEORY.md) | [TOPOLOGY](./TOPOLOGY.md) | [MATROID_THEORY](./MATROID_THEORY.md) | [HYPERGRAPH_THEORY](./HYPERGRAPH_THEORY.md)

### Implementation
- `src/core/purpose_field.py` — Purpose detection, entropy, coherence, god class detection, emergence rules, layer mapping

---

*This document defines the space. For the tools that operate on it, see the framework files in this directory: [GRAPH_THEORY](./GRAPH_THEORY.md), [ORDER_THEORY](./ORDER_THEORY.md), [INFORMATION_THEORY](./INFORMATION_THEORY.md), [CATEGORY_THEORY](./CATEGORY_THEORY.md), [TOPOLOGY](./TOPOLOGY.md), [MATROID_THEORY](./MATROID_THEORY.md), [HYPERGRAPH_THEORY](./HYPERGRAPH_THEORY.md).*
*For how measurements are computed in practice, see [L3_APPLICATIONS.md](../foundations/L3_APPLICATIONS.md).*
