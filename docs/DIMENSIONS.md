# 🌌 The 8 Semantic Dimensions

## Overview

Every particle of code exists in **8 orthogonal semantic dimensions** (see §2.4 of the Standard Model paper).

| # | Dimension | Domain | Values |
|---|-----------|--------|--------|
| 1 | **WHAT** | Atom types | 167 types across 16 families |
| 2 | **Layer** | Architectural position | Interface, Application, Core, Infrastructure, Test |
| 3 | **Role** | Functional purpose | 27 canonical roles (Repository, Factory, etc.) |
| 4 | **Boundary** | Connection type | Internal, Input, I/O, Output |
| 5 | **State** | Memory behavior | Stateful, Stateless |
| 6 | **Effect** | Side effects | Pure, Read, Write, ReadModify |
| 7 | **Activation** | Trigger mechanism | Direct, Event, Time |
| 8 | **Lifetime** | Temporal scope | Transient, Session, Global |

---

## DIMENSION 1: WHAT (Material Composition)

**Question:** What is this made of?  
**Answer:** One of **167 atoms** across **16 families**.

| Phase | Families | Atoms |
|-------|----------|-------|
| DATA | Bits, Bytes, Primitives, Variables | 26 |
| LOGIC | Expressions, Statements, Control, Functions | 61 |
| ORGANIZATION | Aggregates, Services, Modules, Files | 45 |
| EXECUTION | Handlers, Workers, Initializers, Probes | 35 |
| **TOTAL** | **16 families** | **167** |

**Status:** ✅ **COMPLETE** (v14 canonical registry)

---

## DIMENSION 2: Layer (Architectural Position)

**Question:** Where does this live in the architecture?  
**Values:** Interface, Application, Core, Infrastructure, Test

**Detection:** Inferred from file paths and import patterns.

---

## DIMENSION 3: Role (Functional Purpose)

**Question:** What is the developer's intent?  
**Values:** 27 canonical roles (Repository, Factory, Service, Controller, etc.)

**Detection:** Name patterns, decorators, structural heuristics.

---

## DIMENSION 4: Boundary (Connection Type)

**Question:** Does this cross a system boundary?  
**Values:** Internal, Input, I/O, Output

**Detection:** Parameter types, return types, call targets.

---

## DIMENSION 5: State (Memory Behavior)

**Question:** Does this maintain state?  
**Values:** Stateful, Stateless

**Detection:** Presence of mutable fields, instance variables.

---

## DIMENSION 6: Effect (Side Effects)

**Question:** Does this have side effects?  
**Values:** Pure, Read, Write, ReadModify

**Detection:** Call graph analysis, I/O function calls.

---

## DIMENSION 7: Activation (Trigger Mechanism)

**Question:** How is this triggered?  
**Values:** Direct, Event, Time

**Detection:** Decorators (@event_handler, @scheduled), signatures.

---

## DIMENSION 8: Lifetime (Temporal Scope)

**Question:** How long does this exist?  
**Values:** Transient, Session, Global

**Detection:** Scope analysis, singleton patterns, request context.

---

## The 8D Coordinate System

Every particle in your code has an **8D address**:

```python
Particle(
    what="Function",           # Atom type
    layer="Core",              # Architectural layer
    role="Repository",         # Functional purpose
    boundary="I/O",            # External connection
    state="Stateless",         # No internal state
    effect="ReadModify",       # Side effects
    activation="Direct",       # Direct invocation
    lifetime="Transient"       # Per-request
)
```

---

## Dimension Status

| Dimension | Status | Detection Method |
|-----------|--------|------------------|
| WHAT | ✅ Complete | AST node mapping |
| Layer | ✅ Complete | Path + import heuristics |
| Role | ✅ Complete | Pattern matching (27 roles) |
| Boundary | ✅ Complete | Call + parameter analysis |
| State | ✅ Complete | Field analysis |
| Effect | ⚠️ Partial | Call graph (needs improvement) |
| Activation | ✅ Complete | Decorator detection |
| Lifetime | ⚠️ Partial | Scope heuristics |

---

## Canonical Constants

| Constant | Value | Source |
|----------|-------|--------|
| Atoms | 167 | `patterns/atoms.json` |
| Families | 16 | Grouped by phase |
| Phases | 4 | DATA, LOGIC, ORGANIZATION, EXECUTION |
| Dimensions | 8 | This document |
| Roles | 27 | `core/purpose_registry.py` |
