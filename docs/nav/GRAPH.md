---
id: nav_graph
title: "Graph - Topology and Edges"
category: nav
theory_refs: [L0_AXIOMS.md B1-B2, MODEL.md §3]
edge_types: 6
---

# GRAPH - Topology and Edges

> Code is a directed graph. Nodes are code elements. Edges are dependencies. Structure reveals architecture.

<!-- T1:END -->

---

## The Graph

```
G = (N, E)    where N = nodes (code elements), E = edges (dependencies)
```

The Collider builds this graph deterministically from source code. Every node gets classified (atom + role). Every edge gets typed.

---

## Edge Types

| Type | Meaning | Example |
|------|---------|---------|
| **CALLS** | Invocation | `main() calls init()` |
| **IMPORTS** | Dependency | `app.py imports utils` |
| **INHERITS** | Extension | `Dog inherits Animal` |
| **IMPLEMENTS** | Realization | `UserRepo implements IRepo` |
| **CONTAINS** | Composition | `Class contains method` |
| **USES** | Reference | `handler uses logger` |

---

## Topology Roles

Every node gets a **topology role** based on its in-degree and out-degree:

| Role | In-degree | Out-degree | Meaning |
|------|-----------|------------|---------|
| **orphan** | 0 | 0 | Disconnected (see [ORPHANS.md](ORPHANS.md)) |
| **root** | 0 | >0 | Entry point (nothing calls it, it calls others) |
| **leaf** | >0 | 0 | Terminal (called by others, calls nothing) |
| **hub** | high | high | Central coordinator |
| **internal** | >0 | >0 | Normal flow-through node |

---

<!-- T2:END -->

## Centrality Metrics

The Collider computes centrality to find architecturally important nodes:

| Metric | What It Measures | High Value Means |
|--------|-----------------|------------------|
| **Betweenness** | How often a node sits on shortest paths | Bottleneck / gateway |
| **PageRank** | Recursive importance (who depends on me?) | Core infrastructure |
| **In-degree** | How many nodes depend on this | Widely used |
| **Out-degree** | How many nodes this depends on | High coupling |

---

## Graph Axioms

From L0_AXIOMS.md:

- **B1:** The codebase forms a directed graph G = (N, E)
- **B2:** Edges represent typed dependencies (static analysis only)

The graph is **static** -- it captures what the code declares, not what happens at runtime. Dynamic dispatch, reflection, and runtime loading create invisible edges that the Collider flags but cannot trace.

---

## What the Graph Reveals

| Pattern | Detection | Implication |
|---------|-----------|-------------|
| Circular dependency | A → B → C → A | Coupling problem |
| God node | Betweenness > 2σ | Single point of failure |
| Orphan cluster | Subgraph with no external edges | Potentially dead module |
| Layer violation | Domain → Infrastructure edge | Antimatter pattern |
| Fan-in hotspot | In-degree > 20 | Change here breaks everything |

---

## Graph vs Tree

The dependency graph is NOT a tree. It's a DAG (directed acyclic graph) in healthy codebases, but may contain cycles in unhealthy ones.

The **containment** hierarchy (file contains class contains method) IS a tree. The Collider tracks both:
- **Dependency graph:** Who calls/imports/uses whom
- **Containment tree:** Who is nested inside whom

---

*Source: L0_AXIOMS.md (Axioms B1-B2), MODEL.md (§3)*
*See also: [ANTIMATTER.md](ANTIMATTER.md) for graph violations, [ORPHANS.md](ORPHANS.md) for disconnected nodes*
