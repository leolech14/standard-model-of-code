# COLLIDER REPORT
# PROMPT: THE COLLIDER LENS

You are the AI Operator of **Collider**, a **Diagnostic Exosuit** for software architecture.
Your goal is to help the user "fit" their code to their intentions.

## The Device Metaphor
- **The Mirror (Topology)**: You start by describing the *visual shape* (Star, Mesh, Islands). "You look like..."
- **The Translation (Semantics)**: You speak the domain language. "This is a Finance system..."
- **The Possibility (Strategy)**: Based on the physics, what *could* this become? "You have the strong core of a Platform, but you are fragmented."

## Your Voice
- Be precise, technical, but seamless.
- You are not just analyzing code; you are **measuring code physics**.
- Use the metrics provided (Knot Score, RPBL, Entropy) as physical readings.

## Instructions
1. Read the **Brain Download** data below.
2. Synthesize a "Suit Report" for the user.
3. flag "Tight Spots" (Missing capabilities) and "Tangles" (Knots).
4. Be their Mirror. Give them the clear reflection of what they built.

---

**Target**: `core`
**Generated**: 2026-01-11T13:46:33

## IDENTITY

This is a **626 node** codebase with **2288 edges**.
- Files: 57
- Entry points: 66
- Dead code: 9.2%

## CHARACTER (RPBL)

| Dimension | Score | Meaning |
|-----------|-------|---------|
| Responsibility | 3.6/10 | Focused |
| Purity | 7.0/10 | Pure (safe) |
| Boundary | 4.1/10 | Internal |
| Lifecycle | 3.4/10 | Stateless |

## ARCHITECTURE

**Types**:
- Internal: 156
- DTO: 110
- Query: 69
- Module: 57
- Factory: 52
- Utility: 51
- Constructor: 33
- DomainService: 31

**Layers**:
- presentation: 62 (10%)
- cross_cutting: 293 (47%)
- domain: 158 (25%)
- infrastructure: 40 (6%)
- application: 62 (10%)
- testing: 11 (2%)

## KEY COMPONENTS

Most connected nodes (change these carefully):

- `SchemaRepository.get` (677 callers)
- `AtomRegistry._add` (78 callers)
- `typing` (51 callers)
- `SemanticMatrix.add` (43 callers)
- `Continent` (38 callers)

## HEALTH STATUS

✅ Type coverage: 100%
⚠️ Dead code: 9.2%
❌ Knot score: 10/10 (tangled)
❌ Purpose violations: 631

## ACTIONABLE IMPROVEMENTS

Prioritized list of improvements:

### 1. [CRITICAL] Untangle Dependency Cycles
**Target**: `Modules`
**Issue**: Knot Score 10/10 (5 cycles)
**Prescription**:
1. Apply Dependency Inversion Principle
1. Extract shared interfaces to a neutral package
1. Inject dependencies via constructor

### 2. [MEDIUM] Enforce Strict Layering
**Target**: `Architecture`
**Issue**: 631 illegal flows detected (lower layers calling higher layers)
**Prescription**:
1. Refactor to unidirectional flow
1. Introduce Event Bus for upward communication
1. Use Dependency Injection

### 3. [MEDIUM] Decouple God Node
**Target**: ``SelfProofValidator``
**Issue**: High Entropic Coupling (Fan-out: 20)
**Prescription**:
1. Apply Interface Segregation
1. Split into smaller specialized services
1. Use Decorator pattern for cross-cutting concerns

### 4. [LOW] Optimize Hotspot
**Target**: ``SchemaRepository.get``
**Issue**: Central Traffic Hub (677 callers)
**Prescription**:
1. Implement caching/memoization
1. Ensure thread-safety if stateful
1. Monitor for bottleneck performance

## STRATEGIC INTELLIGENCE

### 💡 Potentials
No explicit roadmap found. Consider defining key capabilities, maturity stages, and readiness goals to guide architectural evolution.

## VISUAL REASONING (The 'Shape')

**Overall Shape**: `STAR_HUB`
Dominated by central hub 'SchemaRepository.get' (Star Topology).

### Topological Metrics
- **Centralization**: 1.08 (0=mesh, 1=star)
- **Components**: 59 (islands)
- **Largest Cluster**: 88.2% of nodes
- **Density**: 7.01 avg connections

## DOMAIN CONTEXT (Business Meaning)

**Inferred Domain**: `DevTools/Compiler`

### Top Business Concepts
Extractor (74), extract (38), Classifier (37), Generator (36), Detector (35), Atom (33), Python (31), classify (30)

## QUICK REFERENCE

```
Nodes:      626
Edges:      2288
Files:      57
Entry pts:  66
Orphans:    57
Cycles:     5
RPBL:       R=3.6 P=7.0 B=4.1 L=3.4
```
