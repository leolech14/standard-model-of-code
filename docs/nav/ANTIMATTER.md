---
id: nav_antimatter
title: "Antimatter - 7 Architectural Violations"
category: nav
theory_refs: [L2_PRINCIPLES.md §5, MODEL.md §4]
node_count: 7
---

# ANTIMATTER - 7 Architectural Violations

> When code contradicts its own architecture. Detected automatically from the graph.

<!-- T1:END -->

---

## What Is Antimatter?

An antimatter pattern is a dependency that **violates architectural intent**. Called "antimatter" because it annihilates design on contact.

These are not style violations or code smells. They are **structural contradictions** detected by analyzing role-layer-boundary combinations in the dependency graph.

---

## The 7 Canonical Patterns

### AM001: Layer Skip (Domain → Infrastructure)
```
Entity.py imports PostgresAdapter.py
         ↑ domain        ↑ infrastructure
```
Domain code must never know about infrastructure details. This is the most common violation.

**Detection:** Edge from node with layer=DOMAIN to node with layer=INFRASTRUCTURE.

---

### AM002: Reverse Layer (UI → Domain Direct)
```
UserComponent.tsx imports UserRepository.ts
         ↑ UI                    ↑ domain
```
UI should go through Application layer, never touch domain directly.

**Detection:** Edge from layer=UI to layer=DOMAIN, bypassing APPLICATION.

---

<!-- T2:END -->

### AM003: Test Leakage (Test Code in Production)
```
main_bundle.js includes test_utils.js
```
Test utilities shipping to production. Increases bundle size, exposes test infrastructure.

**Detection:** Node with role pattern `test_*` or path `*/test/*` referenced by non-test code.

---

### AM004: Circular Dependency
```
A.py → B.py → C.py → A.py
```
Creates tight coupling. Changes to any node ripple through the cycle.

**Detection:** Cycle detection in dependency graph (Tarjan's algorithm).

---

### AM005: God Class
```
UserManager.py: 20+ methods spanning 5+ roles
```
A class doing everything. Violates single responsibility.

**Detection:** Node at L4 (CONTAINER) with >20 children and role diversity >4.

---

### AM006: Feature Envy
```
OrderService.process() uses 8 fields from User, 1 from Order
```
A method that primarily uses another class's data. It belongs elsewhere.

**Detection:** Edge weight analysis -- node has more edges to external class than to its own container.

---

### AM007: Scattered Purpose
```
AuthController: login(), formatDate(), parseCSV(), sendEmail()
```
A class whose methods serve unrelated roles. The methods don't cohere.

**Detection:** Role entropy of children exceeds threshold (methods have diverse, unrelated roles).

---

## Severity Levels

| Severity | Patterns | Impact |
|----------|----------|--------|
| **Critical** | AM001, AM004 | Breaks architecture, prevents independent deployment |
| **High** | AM002, AM005 | Tight coupling, maintenance burden |
| **Medium** | AM003, AM006, AM007 | Code quality, potential bugs |

---

## Why "Antimatter"?

In physics, antimatter annihilates matter on contact. In code, these patterns annihilate the architectural rules they violate:

- Clean Architecture says domain is independent → AM001 makes it dependent
- CQRS says separate read/write → AM005 merges everything
- Modularity says cohesion → AM007 scatters purpose

---

*Source: L2_PRINCIPLES.md (§5), MODEL.md (§4)*
*See also: [GRAPH.md](GRAPH.md) for how edges are analyzed, [../essentials/THEORY_WINS.md](../essentials/THEORY_WINS.md) (Idea #10)*
