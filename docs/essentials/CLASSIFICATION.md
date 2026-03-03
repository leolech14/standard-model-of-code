# CLASSIFICATION - Reference Card

> The complete classification system on one page. Levels, phases, dimensions, atoms, roles, RPBL.

---

## The 16-Level Scale

| Level | Name | Zone |
|-------|------|------|
| L12 | UNIVERSE | COSMOLOGICAL |
| L11 | DOMAIN | COSMOLOGICAL |
| L10 | ORGANIZATION | COSMOLOGICAL |
| L9 | PLATFORM | COSMOLOGICAL |
| L8 | ECOSYSTEM | COSMOLOGICAL |
| L7 | SYSTEM | SYSTEMIC |
| L6 | PACKAGE | SYSTEMIC |
| L5 | FILE | SYSTEMIC |
| L4 | CONTAINER | SYSTEMIC |
| L3 | NODE | SEMANTIC |
| L2 | BLOCK | SEMANTIC |
| L1 | STATEMENT | SEMANTIC |
| L0 | TOKEN | SYNTACTIC |
| L-1 | CHARACTER | PHYSICAL |
| L-2 | BYTE | PHYSICAL |
| L-3 | BIT/QUBIT | PHYSICAL |

**Operational range:** L3-L7 (what the Collider classifies).
**Zone transitions** are phase boundaries where the dominant relation type changes.

---

## The 4 Phases

| Phase | Question | Contains |
|-------|----------|----------|
| **DATA** | What is this made of? | Primitives, Variables, Constants |
| **LOGIC** | What does it do? | Expressions, Statements, Functions |
| **ORGANIZATION** | How is it structured? | Classes, Modules, Services |
| **EXECUTION** | How does it run? | Handlers, Workers, Initializers |

---

## The 8 Dimensions

| Dim | Question | Values |
|-----|----------|--------|
| **WHAT** | What type? | Atom taxonomy (3,610 types) |
| **LAYER** | Where in architecture? | Domain, Application, Infrastructure, UI |
| **ROLE** | What purpose? | 33 canonical roles |
| **BOUNDARY** | Crosses boundaries? | Internal, External |
| **STATE** | Maintains state? | Stateless, Stateful |
| **EFFECT** | Side effects? | Pure, Impure |
| **LIFECYCLE** | What phase? | Init, Active, Dispose |
| **TRUST** | How confident? | 0-100% |

---

## Atom Tiers

| Tier | Count | Coverage | Examples |
|------|-------|----------|----------|
| **Tier 0** (Core AST) | 42 | 100% | Function, Class, Variable, Import |
| **Tier 1** (Stdlib) | 21 | 20-40% | Decorator, Generator, Comprehension |
| **Tier 2** (Ecosystem) | 3,531 | Variable | ReactComponent, DjangoView, FastAPIRoute |
| **atoms.json** (Base) | 14 | 100% | The 14 fundamental kinds |

**Total atoms in taxonomy:** 3,610 (94 implemented in Collider).

---

## The 33 Canonical Roles

| Category | Roles |
|----------|-------|
| **Query** | Query, Finder, Loader, Getter |
| **Command** | Command, Creator, Mutator, Destroyer |
| **Factory** | Factory, Builder |
| **Storage** | Repository, Store, Cache |
| **Orchestration** | Service, Controller, Manager, Orchestrator |
| **Validation** | Validator, Guard, Asserter |
| **Transform** | Transformer, Mapper, Serializer, Parser |
| **Event** | Handler, Listener, Subscriber, Emitter |
| **Utility** | Utility, Formatter, Helper |
| **Internal** | Internal, Lifecycle |

29 implemented. "Unknown" is a fallback label, not a role.

---

## RPBL Dimensions

| Dim | Low (1) | High (9) |
|-----|---------|----------|
| **R** (Responsibility) | Single purpose | Omnibus |
| **P** (Purity) | No side effects | Heavy I/O |
| **B** (Boundary) | Internal only | External APIs |
| **L** (Lifecycle) | Ephemeral | Singleton |

**Total state space:** 9^4 = 6,561 behavioral states.

---

## Detection Signals (How Classification Works)

| Signal | Source | Example |
|--------|--------|---------|
| **Topology** | File path | `/services/UserService.py` → Service role |
| **Framework** | Decorators/annotations | `@Controller` → Controller role |
| **Genealogy** | Inheritance chain | `extends Repository` → Repository role |

All three are deterministic. No AI required. Tested on 91 repositories, 270,000+ nodes.

---

## Total Semantic Space

```
|Σ| = |Atoms| × |Roles| × |RPBL|
   = 94 × 29 × 6,561
   = 17,884,806 possible states
```

---

*Source: MODEL.md, L1_DEFINITIONS.md*
*This file: ~120 lines*
