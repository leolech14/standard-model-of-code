---
id: GRAPH_THEORY
title: "Graph Theory: Structural Metrics on Purpose Space"
layer: L1 (Structure)
prerequisites:
  - PURPOSE_SPACE
exports:
  - newman_modularity
  - purpose_weighted_modularity
  - centrality_metrics
  - community_detection
status: IMPLEMENTED
implementation:
  file: src/core/graph_metrics.py
  lines: "1-290"
  coverage: "betweenness, closeness, PageRank, Louvain communities, critical nodes"
glossary_terms:
  - newman_modularity
  - purpose_community
---

# Graph Theory: Structural Metrics on Purpose Space

> **Navigation:** [INDEX](../INDEX.md) | [PURPOSE_SPACE](./PURPOSE_SPACE.md) > **GRAPH_THEORY**
> **Depends on:** [PURPOSE_SPACE.md](./PURPOSE_SPACE.md) SS3 (Metric Structure)

---

## Abstract

Graph theory provides the **first-order structural analysis** of Purpose Space M. Where PURPOSE_SPACE.md defines M = (S, d, mu, tau, A) as a continuous space, this document defines how to extract discrete structure from M using graph-theoretic tools: centrality metrics, community detection, and modularity scoring.

The central insight: a codebase's dependency graph G = (V, E) is the **discretization of Purpose Space** — nodes are atoms, edges are relationships, and graph metrics reveal purpose through connectivity patterns. Newman modularity Q quantifies how well purpose assignments partition the graph into coherent communities. Centrality metrics identify structurally significant atoms (bridges, coordinators, hubs) whose graph position reveals architectural role.

**Implementation status:** Fully implemented in `graph_metrics.py` (290 lines). Betweenness, closeness, PageRank, Louvain community detection, and critical node identification are operational.

---

## SS1. Code as Graph

### 1.1 The Dependency Graph

Given a codebase analyzed by the Collider pipeline, define:

```
G = (V, E)
where:
  V = {v_1, ..., v_n}     set of atoms (files, classes, modules)
  E subset V x V           directed dependency edges
  (v_i, v_j) in E  iff  v_i depends on v_j (imports, inherits, calls)
```

Each vertex v_i carries a **purpose vector** p_i in M (from PURPOSE_SPACE.md SS2). The graph G is thus a **discrete skeleton** of the continuous Purpose Space — it captures the relational structure that PURPOSE_SPACE.md's metric d formalizes.

### 1.2 From Continuous to Discrete

The relationship between Purpose Space and the dependency graph is:

```
d(p_i, p_j) = 1 - cos(p_i, p_j)      (continuous metric from PURPOSE_SPACE.md)
w(v_i, v_j) = 1/d(p_i, p_j)           (edge weight: closer purpose = stronger link)
```

This weighting turns the dependency graph into a **purpose-weighted graph** where edges between same-purpose atoms are heavy and edges between different-purpose atoms are light. Community detection on this weighted graph recovers purpose clusters.

---

## SS2. Centrality Metrics

### 2.1 Betweenness Centrality (Bridge Detection)

```
C_B(v) = sum_{s != v != t} sigma_st(v) / sigma_st
where:
  sigma_st     = number of shortest paths from s to t
  sigma_st(v)  = number of shortest paths from s to t passing through v
```

**Purpose interpretation:** High betweenness reveals **bridge atoms** — components that mediate information flow between otherwise disconnected purpose clusters. A service with high C_B sits between the presentation and infrastructure layers, acting as a critical path in the architecture.

**Implementation:** `graph_metrics.py:42-49` — `nx.betweenness_centrality(G, normalized=True)`. Categorized as "bridges" in `identify_critical_nodes()`.

### 2.2 Closeness Centrality (Coordinator Detection)

```
C_C(v) = (n-1) / sum_{u != v} d_G(v, u)
where:
  d_G(v, u)  = shortest path distance from v to u in G
  n          = |V|
```

**Purpose interpretation:** High closeness reveals **coordinator atoms** — components that can reach many others quickly. Orchestrators, application services, and use cases naturally have high closeness because they coordinate across layers.

**Implementation:** `graph_metrics.py:51-59` — `nx.closeness_centrality(G)`. Categorized as "coordinators".

### 2.3 PageRank (Influence Propagation)

```
PR(v) = (1-alpha)/n + alpha * sum_{u in B(v)} PR(u) / L(u)
where:
  alpha  = 0.85  (damping factor)
  B(v)   = set of nodes linking TO v (in-neighbors)
  L(u)   = out-degree of u
```

**Purpose interpretation:** High PageRank reveals **influential atoms** — components that many important components depend on. Base classes, core domain entities, and shared utilities accumulate PageRank through transitive dependency.

**Implementation:** `graph_metrics.py:61-71` — `nx.pagerank(G, alpha=0.85, max_iter=100)`. Categorized as "influential".

### 2.4 Centrality-Purpose Correspondence

The Collider maps centrality profiles to architectural roles:

| Centrality Profile | Architectural Purpose | Example |
|---|---|---|
| High betweenness, moderate others | Bridge / Gateway | API adapter between services |
| High closeness, low betweenness | Coordinator / Orchestrator | Application service |
| High PageRank, low closeness | Foundation / Core Entity | Base domain class |
| Uniform low scores | Leaf / Peripheral | Utility, test fixture |

This correspondence connects graph structure (L1) to purpose assignment (L2), validating [L0_AXIOMS.md](../foundations/L0_AXIOMS.md) Axiom A2: "Structure reveals purpose."

---

## SS3. Community Detection

### 3.1 Newman Modularity

Modularity Q measures how well a partition of G into communities corresponds to actual edge density:

```
Q = (1/2m) * sum_{ij} [A_ij - (k_i * k_j)/(2m)] * delta(c_i, c_j)
where:
  m       = total number of edges
  A_ij    = adjacency matrix entry (1 if edge exists, 0 otherwise)
  k_i     = degree of node i
  delta() = 1 if c_i == c_j (same community), 0 otherwise
```

**Range:** Q in [-0.5, 1]. Values above 0.3 indicate significant community structure. Well-architected codebases exhibit Q > 0.4 because clean separation of concerns creates natural communities.

### 3.2 Purpose-Weighted Modularity (Our Extension)

Standard modularity treats all edges equally. We extend by weighting edges with purpose similarity:

```
Q_purpose = (1/2m_w) * sum_{ij} [w_ij - (s_i * s_j)/(2m_w)] * delta(c_i, c_j)
where:
  w_ij  = purpose_similarity(p_i, p_j) * A_ij     (purpose-weighted adjacency)
  s_i   = sum_j w_ij                                (weighted degree)
  m_w   = (1/2) * sum_ij w_ij                       (total weighted edges)
```

**Interpretation:** Q_purpose rewards communities where connected nodes share purpose AND penalizes cross-purpose connections more heavily. A high Q_purpose means the codebase's module boundaries align with purpose boundaries — a sign of good architecture.

### 3.3 Louvain Algorithm

Community detection uses the Louvain hierarchical algorithm:

1. **Phase 1:** Each node starts as its own community. For each node, compute the modularity gain of moving it to each neighbor's community. Move it to the community with the maximum positive gain. Repeat until no move improves Q.

2. **Phase 2:** Build a new graph where each community from Phase 1 becomes a single node. Edge weights between new nodes = sum of inter-community edges.

3. **Iterate:** Repeat Phases 1-2 until Q stabilizes.

**Implementation:** `graph_metrics.py:125-146` — Uses `networkx.algorithms.community.louvain_communities` with `seed=42` for reproducibility. Falls back to `greedy_modularity_communities`, then to weakly connected components.

**Purpose connection:** Communities detected by Louvain correspond to **purpose clusters** in M. When the clustering aligns with the purpose vector assignments from EMERGENCE_RULES (see [ORDER_THEORY.md](./ORDER_THEORY.md)), the architecture is well-structured.

---

## SS4. Critical Node Identification

### 4.1 Architectural Significance

The Collider identifies three categories of architecturally significant nodes:

```python
{
    'bridges':      top_n by betweenness,     # removing fragments the system
    'influential':  top_n by PageRank,        # important in dependency flow
    'coordinators': top_n by closeness        # can reach many nodes quickly
}
```

**Implementation:** `graph_metrics.py:76-122` — `identify_critical_nodes(G, metrics, top_n=10)` sorts pre-computed centrality metrics and returns the top nodes per category.

### 4.2 Connection to Purpose Anomalies

Critical nodes often reveal purpose anomalies:

- A **bridge** with mixed purposes signals a **god class** — it mediates between clusters because it serves too many purposes simultaneously.
- A **coordinator** with no clear purpose suggests **missing abstraction** — the node coordinates but doesn't have a named architectural role.
- An **influential** leaf node (high PageRank but no outgoing edges) indicates an **over-depended utility** that should be in a shared library.

These anomaly patterns connect to [L2_PRINCIPLES.md](../foundations/L2_PRINCIPLES.md) SS5 (Anti-pattern Detection) and to [MATROID_THEORY.md](./MATROID_THEORY.md) (rank bound for coherence).

---

## SS5. Connections to Other Frameworks

| Framework | Connection |
|---|---|
| [PURPOSE_SPACE](./PURPOSE_SPACE.md) | G discretizes M; edge weights encode purpose distance d(p_i, p_j) |
| [ORDER_THEORY](./ORDER_THEORY.md) | Communities should align with FCA concept lattice clusters |
| [INFORMATION_THEORY](./INFORMATION_THEORY.md) | High modularity Q correlates with low inter-community entropy |
| [CATEGORY_THEORY](./CATEGORY_THEORY.md) | Community assignment as functor from Graph category to Partition category |
| [TOPOLOGY](./TOPOLOGY.md) | H_0 of dependency complex corresponds to connected components / communities |
| [MATROID_THEORY](./MATROID_THEORY.md) | God class detection via bridge analysis complements matroid rank bounds |
| [HYPERGRAPH_THEORY](./HYPERGRAPH_THEORY.md) | Hyperedges capture multi-node dependencies that pairwise edges miss |

---

## Appendix A: CHM Integration

The Code Health Measurement (CHM) framework from ACM TOSEM 2025 proposes 6 dimensions of code health. Graph metrics map to 3 of them:

| CHM Dimension | Graph Metric | Implementation |
|---|---|---|
| Complexity | Average betweenness centrality | `graph_metrics.py` |
| Coupling | Inter-community edge density | Derivable from modularity |
| Cohesion | Intra-community edge density | Derivable from modularity |

## Appendix B: Citations

- Newman, M. E. J. (2006). "Modularity and community structure in networks." PNAS 103(23): 8577-8582.
- Blondel, V. D. et al. (2008). "Fast unfolding of communities in large networks." J. Stat. Mech. P10008.
- ACM TOSEM (2025). CHM: 6-dimension code health measurement framework.
- Page, L. et al. (1999). "The PageRank citation ranking: Bringing order to the web." Stanford InfoLab.

---

*This document defines graph-theoretic tools on Purpose Space. For the space itself, see [PURPOSE_SPACE.md](./PURPOSE_SPACE.md). For ordering and lattice structure, see [ORDER_THEORY.md](./ORDER_THEORY.md).*
