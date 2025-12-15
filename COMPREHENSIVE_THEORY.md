# 🌌 COMPREHENSIVE THEORY: Standard Model for Computer Language

> **The Complete Reference for Code Physics v14**

This document synthesizes all discoveries, suggestions, and key concepts for understanding "what is what" across all levels of computational systems.

---

## Part 1: The Core Insight

**The useful unit of software is NOT the file.**

It's the **things inside files** (functions, classes, data structures) and the **relationships between them** (calls, imports, inheritance). Files are just packaging.

This matters for AI because LLMs can't "see" structure—they need an **explicit map**.

---

## Part 2: The 4 Scale Levels

Every entity in code exists at one of four granularity levels:

| Level | Name | What It Is | Examples |
|-------|------|------------|----------|
| **L1** | Atom | Indivisible syntax unit | Variable, Operator, Literal, Expression |
| **L2** | Molecule | Composed of atoms | Function, Method, Handler, Validator |
| **L3** | Organism | Composed of molecules | Class, Module, Service, Component |
| **L4** | Ecosystem | The whole system | Package, Repository, Microservices |

### Containment Hierarchy

```
Ecosystem (L4)
  └── Organism (L3)
        └── Molecule (L2)
              └── Atom (L1)
```

**Key Principle:** Entities at each level can share the same **PURPOSE** but differ in **granularity**.

---

## Part 3: The 8 Dimensions of Code Physics

Every particle is measured across 8 orthogonal dimensions:

| # | Dimension | Values | Question |
|---|-----------|--------|----------|
| 1 | **WHAT** | 167 atoms | What is it made of? |
| 2 | **Layer** | Interface, App, Core, Infra, Tests | Where in the stack? |
| 3 | **Role** | Orchestrator, Data, Worker | What job does it do? |
| 4 | **Boundary** | Internal, Input, I/O, Output | How does it connect? |
| 5 | **State** | Stateful, Stateless | Does it hold memory? |
| 6 | **Effect** | Read, Write, ReadModify, Pure | What does it touch? |
| 7 | **Activation** | Event, Time, Direct | How is it triggered? |
| 8 | **Lifetime** | Transient, Session, Global | How long does it live? |

### The 9th Dimension: Scale (Proposed)

```json
{
  "scale": {
    "level": "molecule",
    "parent_id": "UserService",
    "children_ids": ["validate_email", "hash_password"],
    "depth": 2
  }
}
```

---

## Part 4: The 12 Fundamental Families (Quarks)

Atoms group into 12 families based on their nature:

| Family | Phase | Purpose | Count |
|--------|-------|---------|-------|
| Bits | Data | Binary flags/masks | 2 |
| Bytes | Data | Raw byte arrays | 3 |
| Primitives | Data | Basic values (int, string, bool) | 8 |
| Variables | Data | Named storage | 5 |
| Expressions | Logic | Value-producing combinations | 8 |
| Statements | Logic | Actions (return, assert) | 10 |
| Control | Logic | Flow (if, while, for) | 10 |
| Functions | Logic | Callable units | 10 |
| Aggregates | Organization | Composite structures (class, DTO) | 6 |
| Modules | Organization | Organizational units | 4 |
| Files | Organization | File-level entities | 1 |
| Executables | Execution | Runtime entry points | 9+ |

**Total Atoms:** 167 (v14)

---

## Part 5: The 4 Phases of Matter

Families belong to 4 phases (continents):

| Phase | Color | Families | Purpose |
|-------|-------|----------|---------|
| **Data** | Cyan | Bits, Bytes, Primitives, Variables | Store information |
| **Logic** | Magenta | Expressions, Statements, Control, Functions | Process information |
| **Organization** | Green | Aggregates, Modules, Files | Structure information |
| **Execution** | Amber | Executables | Run information |

---

## Part 6: Canonical Components by Layer

Components that appear universally across codebases, organized by architectural layer:

### Interface Layer
| Symbol | Name | Role | Purpose |
|--------|------|------|---------|
| Rh | Route Handler | Orchestrator | Receives HTTP requests |
| Pr | Presenter | Data | Formats output for display |
| Iv | Input Validator | Worker | Validates incoming data |
| Uw | UI Wrapper | Data | Encapsulates UI components |

### App Layer
| Symbol | Name | Role | Purpose |
|--------|------|------|---------|
| Uc | Use Case | Orchestrator | Coordinates business flow |
| Pm | Process Manager | Orchestrator | Manages multi-step processes |
| Ap | App Policy | Worker | Enforces application rules |
| Am | App Mapper | Data | Transforms between layers |

### Core Layer
| Symbol | Name | Role | Purpose |
|--------|------|------|---------|
| Be | Business Entity | Data | Core domain model |
| Vo | Value Object | Data | Immutable domain value |
| Bs | Core Service | Worker | Domain logic execution |
| Br | Business Rule | Worker | Domain constraint |
| De | Domain Event | Data | Domain state change signal |

### Infra Layer
| Symbol | Name | Role | Purpose |
|--------|------|------|---------|
| Rp | Repository | Data | Persists/retrieves entities |
| Qo | Query Object | Data | Complex read queries |
| Ac | API Client | Worker | External API calls |
| Mp | Msg Producer | Worker | Sends messages |
| Mc | Msg Consumer | Worker | Receives messages |
| Bj | Background Job | Worker | Scheduled tasks |
| Cc | Cache | Data | Temporary storage |
| Cf | Config Loader | Data | Configuration access |
| Ff | Feature Flag | Data | Runtime toggles |
| Lg | Logger | Worker | Audit/debug output |
| Mt | Metrics | Worker | Telemetry collection |
| Sz | Serializer | Data | Data format conversion |

### Tests Layer
| Symbol | Name | Role | Purpose |
|--------|------|------|---------|
| Tc | Test Case | Orchestrator | Executes assertions |
| Fx | Fixture | Data | Test data setup |
| Tr | Test Runner | Orchestrator | Executes test suites |

---

## Part 7: Cross-Level Integration (Meta-Components)

When components from different levels integrate, they form **meta-components** with shared purpose:

### Example: "User Authentication" Meta-Component

```
L4 (Ecosystem): AuthService
  └── L3 (Organism): UserAuthModule
        ├── L2 (Molecule): login_handler()
        │     ├── L1: validate_email (Expression)
        │     ├── L1: hash_password (Call)
        │     └── L1: token = jwt.encode() (Assignment)
        └── L2 (Molecule): verify_token()
              └── L1: decoded = jwt.decode() (Call)
```

**Principle:** The meta-component "Authentication" exists at ALL levels, just at different granularities.

---

## Part 8: Relationship Types (Edges)

| Edge Type | Meaning | Example |
|-----------|---------|---------|
| CONTAINS | Parent holds child | Class → Method |
| CALLS | Invokes | Function → Function |
| IMPORTS | Depends on | Module → Module |
| INHERITS | Extends | Class → BaseClass |
| IMPLEMENTS | Realizes | Class → Interface |
| READS | Accesses data | Function → Variable |
| WRITES | Mutates data | Function → Variable |
| PRODUCES | Creates output | Handler → Event |
| CONSUMES | Receives input | Handler → Event |

---

## Part 9: Complexity Metrics

| Metric | What It Measures | Threshold |
|--------|------------------|-----------|
| Cyclomatic | Branching paths | < 10 |
| Cognitive | Nesting depth | < 15 |
| Halstead Volume | Code vocabulary | < 500 |
| Depth of Inheritance | Class hierarchy | < 5 |
| Fan-In | Incoming dependencies | Context-dependent |
| Fan-Out | Outgoing dependencies | < 10 |

---

## Part 10: The Pipeline Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    INPUT: Source Code                    │
└────────────────────────┬────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│  Layer 1: PARSING (Tree-Sitter)                         │
│  • AST Extraction                                        │
│  • Syntax Nodes                                          │
│  Output: Raw Atoms                                       │
└────────────────────────┬────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│  Layer 2: GRAPH BUILDING (NetworkX/Neo4j)               │
│  • Nodes = Components                                    │
│  • Edges = Relationships                                 │
│  Output: Dependency Graph                                │
└────────────────────────┬────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│  Layer 3: HEURISTIC CLASSIFICATION                      │
│  • Pattern Matching (regex, path, decorator)            │
│  • Dimensional Tagging (8D coordinates)                 │
│  Output: Classified Particles                            │
└────────────────────────┬────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│  Layer 4: LLM ESCALATION (Ollama/GPT)                   │
│  • Low-confidence (<55%) particles                      │
│  • Purpose inference                                     │
│  • Evidence validation                                   │
│  Output: Validated Classifications                       │
└────────────────────────┬────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│  Layer 5: OUTPUT GENERATION                             │
│  • 8D Particle Registry (JSON)                          │
│  • Graph Export (Mermaid, Neo4j)                        │
│  • Violation Report                                      │
│  Output: Canonical Architecture Map                      │
└─────────────────────────────────────────────────────────┘
```

---

## Part 11: Open-Source Tools Integration

| Tool | Purpose | Layer |
|------|---------|-------|
| Tree-Sitter | AST Parsing | 1 |
| Bandit | Side-effect detection (HOW) | 3 |
| import-linter | Boundary enforcement (WHERE) | 3 |
| NetworkX | In-memory graphs | 2 |
| Neo4j | Scalable graph DB | 2 |
| Ollama | Local LLM inference | 4 |

---

## Part 12: Key Principles

1. **Truth First, Meaning Second** — Parse structure before inferring roles.
2. **Evidence-Anchored Classification** — Every role claim must cite code evidence.
3. **Graceful Degradation** — If tools fail, fall back to heuristics.
4. **Universal Meta-Components** — Group by purpose, not by syntax.
5. **Scale Awareness** — Track containment and granularity explicitly.
6. **8D Coordinates** — Every particle has a complete dimensional profile.
7. **Antimatter Detection** — Flag impossible combinations (e.g., Pure + SideEffects).

---

## Part 13: Current Coverage

| Dimension | Implementation Status | Coverage |
|-----------|----------------------|----------|
| WHAT | ✅ Complete | 167 atoms |
| Layer | ✅ Complete | 5 values |
| Role | ✅ Complete | 3 values |
| Boundary | ✅ Complete | 4 values |
| State | ✅ Complete | 2 values |
| Effect | ✅ Complete | 4 values |
| Activation | ✅ Complete | 3 values |
| Lifetime | ✅ Complete | 3 values |
| Scale | ⚠️ Proposed | 4 levels |

---

## Part 14: Next Steps

1. **Implement Scale Dimension** — Add containment tracking to particle registry
2. **Build Cross-Level Aggregator** — Group particles by shared purpose
3. **Create Meta-Component Detector** — Identify universal patterns
4. **Extend Open-Source Integration** — Add more HOW/WHERE tools
5. **Build Visualization Layer** — Interactive graph navigation

---

*This document is the canonical reference for the Standard Model for Computer Language v14.*
