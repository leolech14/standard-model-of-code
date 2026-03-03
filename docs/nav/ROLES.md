# ROLES - The 33 Canonical Roles

> WHY does this code element exist? The role answers that question.

---

## Atoms vs Roles

- **Atom** = WHAT type of element (structural classification)
- **Role** = WHY it exists (purpose classification)

A `Function` (atom) might be a `Validator` (role) or a `Transformer` (role). Same structure, different purpose.

---

## The 33 Roles in 10 Categories

| Category | Roles | Purpose Pattern |
|----------|-------|-----------------|
| **Query** | Query, Finder, Loader, Getter | Read data without changing it |
| **Command** | Command, Creator, Mutator, Destroyer | Change state |
| **Factory** | Factory, Builder | Create new instances |
| **Storage** | Repository, Store, Cache | Persist and retrieve data |
| **Orchestration** | Service, Controller, Manager, Orchestrator | Coordinate workflows |
| **Validation** | Validator, Guard, Asserter | Enforce rules |
| **Transform** | Transformer, Mapper, Serializer, Parser | Convert between formats |
| **Event** | Handler, Listener, Subscriber, Emitter | React to things happening |
| **Utility** | Utility, Formatter, Helper | General-purpose tools |
| **Internal** | Internal, Lifecycle | Framework plumbing |

**29 implemented** in Collider. "Unknown" is a fallback label, not a role.

---

## How Roles Are Detected

Three deterministic signals, checked in priority order:

### 1. Topology (file path)
```
/services/UserService.py    → Service
/validators/email.py        → Validator
/repositories/user_repo.py  → Repository
/controllers/auth.py        → Controller
```

### 2. Framework (decorators/annotations)
```
@Controller        → Controller
@Injectable        → Service
@Repository        → Repository
@EventHandler      → Handler
```

### 3. Genealogy (inheritance)
```
extends Repository  → Repository
implements IValidator → Validator
extends BaseCommand  → Command
mixes in Serializer  → Serializer
```

**100% coverage** with zero unknowns. No AI needed.

---

## Role Distribution (Typical Codebase)

Most codebases follow a power-law distribution:

| Rank | Typical Top Roles | Approx % |
|------|-------------------|----------|
| 1 | Utility / Helper | 15-25% |
| 2 | Handler / Listener | 10-20% |
| 3 | Service | 10-15% |
| 4 | Transformer / Mapper | 5-10% |
| 5 | Repository / Store | 5-10% |
| ... | Everything else | Remaining |

A healthy codebase has role diversity. Monoculture (80% Utility) suggests missing abstractions.

---

## CQRS Alignment

The Query/Command split maps directly to CQRS:

| Side | Roles | Effect |
|------|-------|--------|
| **Query** | Query, Finder, Loader, Getter | Pure (no side effects) |
| **Command** | Command, Creator, Mutator, Destroyer | Impure (state changes) |

---

*Source: MODEL.md (§2), L1_DEFINITIONS.md (§4)*
*See also: [ATOMS.md](ATOMS.md) for the WHAT dimension, [../essentials/CLASSIFICATION.md](../essentials/CLASSIFICATION.md) for full reference*
