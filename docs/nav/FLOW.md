# FLOW - Constructal Law in Code

> Code is a conduit for four types of flow. Good architecture minimizes resistance to ALL of them.

---

## The Idea

Adrian Bejan's Constructal Law: *"For a finite-size flow system to persist in time, its configuration must evolve to provide easier access to the currents that flow through it."*

Applied to code: software is a system through which multiple substances flow. Architecture is the channel geometry. Good architecture = low resistance paths for all flow types.

---

## The 4 Flow Substances

| Flow | Substance | What Moves | Example |
|------|-----------|------------|---------|
| **Static** | Data dependencies | Import chains, type hierarchies | `A imports B imports C` |
| **Runtime** | Control flow | Function calls, event propagation | `main() → init() → connect()` |
| **Change** | Development effort | Git commits, PR frequency | `auth/ modified 47 times this quarter` |
| **Human** | Attention and understanding | Reading paths, learning curves | `Where do I start reading this codebase?` |

---

## Why All Four Matter

A refactoring that improves runtime flow (faster execution paths) but makes the code harder for humans to read (worse human flow) may **not be a net win**.

```
Total resistance = R_static + R_runtime + R_change + R_human
```

The best architectures minimize resistance across all four simultaneously.

---

## Flow Resistance

Resistance on a path is the sum of obstacles:

```
R(path) = Σ obstacles_on_path
```

| Flow | Obstacles (High Resistance) | Clear Path (Low Resistance) |
|------|----------------------------|----------------------------|
| **Static** | Deep import chains, circular deps | Flat dependency tree |
| **Runtime** | Long call chains, excessive middleware | Direct invocations |
| **Change** | Tight coupling, God classes | Modular, independent files |
| **Human** | No docs, scattered purpose, naming confusion | Clear naming, cohesive modules |

---

## Detecting Flow Problems

The Collider reveals flow issues through graph metrics:

| Metric | Flow Problem |
|--------|-------------|
| High betweenness centrality | Bottleneck node (all flows pass through) |
| Deep import chains | Static flow resistance |
| High out-degree | Change flow risk (many dependencies to break) |
| Scattered roles in one file | Human flow confusion |

---

## Heuristic Status

The constructal law application to code is classified as **HEURISTIC** in the theory (inspired by Bejan, not formally derived). It provides useful intuition but lacks the formal rigor of the purpose field axioms.

The key practical takeaway: **optimize for multiple flow types, not just one.**

---

*Source: L0_AXIOMS.md (Axioms E1-E2), L2_PRINCIPLES.md (§3)*
*See also: [GRAPH.md](GRAPH.md) for centrality metrics, [../essentials/THEORY_WINS.md](../essentials/THEORY_WINS.md) (Idea #13)*
