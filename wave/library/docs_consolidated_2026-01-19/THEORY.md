# THEORY.md - The Standard Model of Code

> **Layer:** 1 (Bible) | **Parent:** [CLAUDE.md](../CLAUDE.md) | **Index:** [INDEX.md](INDEX.md)
> **Children:** [FORMAL_PROOF.md](FORMAL_PROOF.md), [ATOMS_REFERENCE.md](ATOMS_REFERENCE.md)
> **Purpose:** Canonical reference for all theoretical constructs

---

## Document Status

| Aspect | Status |
|--------|--------|
| Theory completeness | Stable |
| Implementation alignment | Partial (see gaps) |
| Last validated | 2026-01-19 (Gemini 2.5 Pro forensic) |

---

## Level 0: Foundational Axioms (Always True)

These are the bedrock assumptions that never change.

### The Three Planes

| Plane | What Exists | Example |
|-------|-------------|---------|
| **Physical** | Bits, bytes, files on disk | `0x48 0x65 0x6C 0x6C 0x6F` |
| **Virtual** | AST nodes, runtime objects | `FunctionDeclaration`, `ClassInstance` |
| **Semantic** | Meaning, intent, architecture | `Repository`, `Entity`, `Service` |

**Source:** Popper's Three Worlds, adapted for code.

### The 16-Level Scale (L-3 to L12)

| Level | Name | Zone | Description |
|-------|------|------|-------------|
| L12 | UNIVERSE | COSMOLOGICAL | All software ever |
| L11 | DOMAIN | COSMOLOGICAL | Business domain |
| L10 | ORGANIZATION | COSMOLOGICAL | Company/team |
| L9 | PLATFORM | COSMOLOGICAL | Deployment platform |
| L8 | ECOSYSTEM | COSMOLOGICAL | Language ecosystem |
| L7 | SYSTEM | SYSTEMIC | Application/service |
| L6 | PACKAGE | SYSTEMIC | Module/package |
| L5 | FILE | SYSTEMIC | Source file |
| L4 | CONTAINER | SYSTEMIC | Class/struct |
| L3 | NODE | SEMANTIC | Function/method (analysis unit) |
| L2 | BLOCK | SEMANTIC | Code block |
| L1 | STATEMENT | SEMANTIC | Single statement |
| L0 | TOKEN | SYNTACTIC | Lexical token |
| L-1 | CHARACTER | PHYSICAL | Unicode character |
| L-2 | BYTE | PHYSICAL | Raw byte |
| L-3 | BIT/QUBIT | PHYSICAL | Binary digit |

**Source:** Koestler's Holons + custom scale.
**Implementation:** `src/core/viz/assets/app.js:SCALE_16_LEVELS`

### The 5 Zones

| Zone | Levels | Focus |
|------|--------|-------|
| PHYSICAL | L-3 to L-1 | Hardware representation |
| SYNTACTIC | L0 | Lexical structure |
| SEMANTIC | L1 to L3 | Meaning and intent |
| SYSTEMIC | L4 to L7 | Organization and architecture |
| COSMOLOGICAL | L8 to L12 | Ecosystem and beyond |

---

## Level 1: Core Theories (Stable)

### The 4 Phases

| Phase | Question | Contains |
|-------|----------|----------|
| **DATA** | What is this made of? | Bits, Bytes, Primitives, Variables |
| **LOGIC** | What does it do? | Expressions, Statements, Control, Functions |
| **ORGANIZATION** | How is it structured? | Aggregates, Services, Modules, Files |
| **EXECUTION** | How does it run? | Handlers, Workers, Initializers, Probes |

### The 8 Dimensions

| Dimension | Question | Values |
|-----------|----------|--------|
| WHAT | What type is this? | Atom taxonomy |
| LAYER | Where in architecture? | Domain, Application, Infrastructure, UI |
| ROLE | What's its purpose? | Role taxonomy |
| BOUNDARY | Crosses boundaries? | Internal, External |
| STATE | Maintains state? | Stateless, Stateful |
| EFFECT | Side effects? | Pure, Impure |
| LIFECYCLE | In what phase? | Init, Active, Dispose |
| TRUST | How confident? | 0-100% |

### The 8 Lenses (Interrogation Framework)

| Lens | Question |
|------|----------|
| IDENTITY | What is it called? |
| ONTOLOGY | What exists here? |
| CLASSIFICATION | What kind is it? |
| COMPOSITION | How is it structured? |
| RELATIONSHIPS | How is it connected? |
| TRANSFORMATION | What does it do? |
| SEMANTICS | What does it mean? |
| EPISTEMOLOGY | How certain are we? |

### The 5 Edge Families

| Family | Edges | Meaning |
|--------|-------|---------|
| Structural | contains, is_part_of | Hierarchy |
| Dependency | calls, imports, uses | Dependencies |
| Inheritance | inherits, implements, mixes_in | Type hierarchy |
| Semantic | is_a, has_role, serves, delegates_to | Intent |
| Temporal | initializes, triggers, disposes, precedes | Time |

---

## Level 2: Versioned Constants

### Atom Taxonomy

| Version | Count | Source | Status |
|---------|-------|--------|--------|
| V1 | 167 | FORMAL_PROOF.md | Documented |
| V2 | 200 | 200_ATOMS.md | Documented |
| Implemented | **94** | atom_loader.py | Active |

**Atom Breakdown (Implemented):**

| Source | Count | Integrated |
|--------|-------|------------|
| atoms.json (base) | 14 | Yes |
| ATOMS_TIER0_CORE.yaml | 42 | Yes |
| ATOMS_TIER1_STDLIB.yaml | 21 | Yes |
| ATOMS_TIER2_ECOSYSTEM.yaml | 17 | Yes |
| **Total** | **94** | Yes |

**Family Count:**

| Version | Families | Source |
|---------|----------|--------|
| V1 | 16 | FORMAL_PROOF.md |
| V2 | 22 | 200_ATOMS.md |
| Implemented | 16 | atom_loader.py |

### Role Taxonomy

| Version | Count | Source | Status |
|---------|-------|--------|--------|
| V1 | 27 | FORMAL_PROOF.md | Documented |
| V2 | 33 | UNIFIED_THEORY.md, roles.json | Documented |
| Implemented | 29 | heuristic_classifier.py | Active |

**The 33 Canonical Roles (V2):**

| Category | Roles |
|----------|-------|
| Query | Query, Finder, Loader, Getter |
| Command | Command, Creator, Mutator, Destroyer |
| Factory | Factory, Builder |
| Storage | Repository, Store, Cache |
| Orchestration | Service, Controller, Manager |
| Validation | Validator, Guard, Asserter |
| Transform | Transformer, Mapper, Serializer |
| Event | Handler, Listener, Subscriber |
| Utility | Utility, Formatter, Helper |
| Internal | Internal, Lifecycle |
| Unknown | Unknown |

### RPBL Dimensions

| Dimension | Description | Range |
|-----------|-------------|-------|
| R - Responsibility | Single purpose (1) ↔ Omnibus (9) | 1-9 |
| P - Purity | Pure/no side effects (1) ↔ Impure (9) | 1-9 |
| B - Boundary | Internal (1) ↔ External (9) | 1-9 |
| L - Lifecycle | Ephemeral (1) ↔ Singleton (9) | 1-9 |

**Note:** FORMAL_PROOF.md claims [1,10] but implementation uses [1,9].

**RPBL Space:**
- V1 formula: 10^4 = 10,000 states
- Actual: 9^4 = 6,561 states

### Semantic Space Calculation

| Version | Formula | Result |
|---------|---------|--------|
| V1 | 167 atoms × 27 roles × 10,000 RPBL | 45,090,000 |
| V2 | 200 atoms × 33 roles × 10,000 RPBL | 66,000,000 |
| Actual | 94 atoms × 29 roles × 6,561 RPBL | 17,884,806 |

---

## Level 3: The Pipeline (12 Stages)

| Stage | Name | Produces | Depends On |
|-------|------|----------|------------|
| 1 | Classification | atoms | None |
| 2 | Role Detection | roles | Stage 1 |
| 3 | Antimatter Detection | violations | Stage 2, 6 |
| 4 | Predictions | missing components | Stage 2 |
| 5 | Insights Engine | recommendations | Stage 3, 4, 6, 7, 8 |
| 6 | Purpose Field (Layers) | layers | Stage 2 |
| 7 | Execution Flow | reachable_set, orphans | Stage 6 |
| 8 | Performance Analysis | hotspots | Stage 7 |
| 9 | Visualization | HTML report | All |
| 10 | Export | unified_analysis.json | All |
| 11 | Brain Download | output.md | All |
| 12 | Topology | shape classification | Stages 1-8 |

**The Mounting Law:**
> Each stage consumes the output of its dependencies as input. Reordering creates undefined behavior or silent failures.

---

## Level 4: Derived Concepts

### The Canonical Schema (Minimal Fields)

**Nodes:**
```
id, name, kind, role, layer
```

**Edges:**
```
source, target, edge_type
```

**Why Minimal:** Removing any field loses information needed for reconstruction.

### The M-I-P-O Cycle

```
Memory → Input → Process → Output → Memory...
```

All code participates in this cycle.

### Antimatter (Impossible States)

Cross-layer violations that should never exist:

| Violation | Example |
|-----------|---------|
| Domain → Infrastructure | Entity imports PostgresAdapter |
| UI → Domain | Component calls repository directly |
| Test → Production | Test code in main bundle |

### The 10 Universal Subsystems

Every codebase clusters into ~10 meta-components:

1. **Ingress** - Routers, controllers, middleware
2. **Egress** - External clients, webhooks
3. **Domain Core** - Entities, rules, use-cases
4. **Persistence** - ORM, repositories, migrations
5. **Async Processing** - Queues, workers, schedulers
6. **Presentation** - UI components, view models
7. **Security** - AuthN/AuthZ, policies
8. **Observability** - Logging, metrics, tracing
9. **Configuration** - Config loading, env vars
10. **Delivery** - CI/CD pipelines, IaC

---

## Theoretical Lineage

```
                    FOUNDATIONAL THEORIES
                           |
    +----------------------+----------------------+
    |                      |                      |
    v                      v                      v
Koestler            Popper               Ranganathan
(Holons)         (Three Worlds)      (Faceted Classification)
    |                      |                      |
    v                      v                      v
16 LEVELS            3 PLANES              8 DIMENSIONS
(L-3 to L12)    (Physical/Virtual/       (WHAT, LAYER,
                   Semantic)             ROLE, etc.)
                           |
    +----------------------+----------------------+
    |                      |                      |
    v                      v                      v
Clean Arch              DDD                  Shannon
(Martin)              (Evans)          (Information Theory)
    |                      |                      |
    v                      v                      v
LAYER DIM            33 ROLES              M-I-P-O CYCLE
```

---

## Implementation Gaps

| Theory | Documented | Implemented | Gap |
|--------|------------|-------------|-----|
| Atoms | 200 | 94 | 106 atoms not loaded |
| Roles | 33 | 29 | 4 roles not implemented |
| Families | 22 | 16 | 6 families not in code |
| RPBL range | [1,10] | [1,9] | Docs incorrect |
| Pipeline | 12 stages | 12 stages | Aligned |

---

## Key Theorems (From FORMAL_PROOF.md)

| ID | Name | Claim | Status |
|----|------|-------|--------|
| 3.1 | WHAT Completeness | Atom taxonomy covers all syntactic structures | V1 only |
| 3.2 | WHY Completeness | Role taxonomy achieves 100% coverage | V1 only |
| 3.3 | HOW Boundedness | RPBL space is bounded (10,000 states) | Needs update |
| 3.4 | Total Space | Semantic space < 50M states | Needs recalc |
| 3.5 | Minimality | WHAT/WHY/HOW are minimal dimensions | Valid |
| 3.6 | Orthogonality | Dimensions are statistically independent | Valid |
| 3.7 | Pipeline DAG | 10-stage pipeline is valid topological order | Now 12 stages |
| 3.8 | Schema Minimality | Canonical schema is minimal | Valid |

---

## The Core Insight

> **The deterministic layer IS the intelligence. The LLM layer is optional enrichment.**

Code structure can be classified with >99% accuracy WITHOUT AI because information is encoded in:
1. **Topology** - File paths reveal role (`/services/UserService.py`)
2. **Frameworks** - Decorators reveal role (`@Controller`)
3. **Genealogy** - Inheritance reveals role (`extends Repository`)

This was **THE PIVOT** (Dec 23, 2025) - the discovery that transformed the project from AI-first to deterministic-first.

---

## References

- `schema/fixed/200_ATOMS.md` - Complete atom enumeration
- `schema/fixed/roles.json` - Role definitions
- `src/patterns/ATOMS_TIER*.yaml` - Tiered atom definitions
- `docs/FORMAL_PROOF.md` - Mathematical proofs (V1)
- `docs/registry/HISTORY.md` - Project evolution timeline
