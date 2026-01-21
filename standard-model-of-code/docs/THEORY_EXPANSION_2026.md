# Theory Expansion 2026: The Standard Model of Code v2.1

> **Consolidation of Core Concepts (Jan 2026)**
> Defining the relationship between Atoms (Matter), Roles (Function), and Context (Situation).

---

## 1. The Core Distinction: Atoms vs. Roles

**The fundamental question:** Are the 200 Atoms defined by what they *are* (Structure) or what they *do* (Purpose)?

### 1.1 The Definition
*   **Atoms (The 200)** are **Syntactic Universals**. They are defined by **Structure (Syntax)**. They are the "bricks" or "matter" of code.
    *   *Example:* A `Class` atom is defined by the syntax `class Name { ... }`.
    *   *Example:* A `WhileLoop` atom is defined by `while (cond) { ... }`.

*   **Roles (The 33)** are **Architectural Verbs**. They are defined by **Function (Teleology)**. They are the "blueprints" or "jobs" assigned to that matter.
    *   *Example:* A `Repository` role is defined by the function "Persist Data".
    *   *Example:* A `Validator` role is defined by the function "Ensure Integrity".

### 1.2 The Relationship
The relationship is hierarchical:
> **Atom (Vessel) → Role (Job) → Purpose (Goal)**

While the atoms are grouped into phases (DATA, LOGIC, ORGANIZATION, EXECUTION) based on their *potential* utility, their definition remains structural.

**Key Insight:** A single Atom (e.g., `Class`) can fulfill multiple different Roles (e.g., `Service`, `Entity`, `Factory`) depending on the context.

---

## 2. The First Purpose Equation

The "Purpose" of a code component is not ambiguous. It is mathematically defined by its Role.

> **π₁(node) = role(node)**
> *"The Atomic Purpose (π₁) of any code node IS its Role."*

This means:
1.  We have **infinite** code components (`UserRepository`, `PaymentService`, `NuclearLauncher`).
2.  But we have a **finite** set of architectural purposes (33 Roles).
3.  Therefore, the "Purpose" of any component, at the architectural level, is one of the 33 Roles.

---

## 3. The "Situation" (Context)
*Or: How 33 Roles Create Infinite Possibilities*

If we only have 33 Roles, where does the complexity of software come from? It comes from the **Situation** (Context). The Situation is the intersection of 4 Dimensions.

### 3.1 The 4 Dimensions of Context

**Formula:**
`Situation` = `Role` (33) × `Layer` (4) × `Lifecycle` (3) × `RPBL` (6,561) × `Domain` (∞)

#### Dimension 1: The Space (Architectural Layer)
*Where does it live?*
*   **Definition:** The architectural zone governs the allowable dependencies and level of abstraction.
*   **The Multiplier:** 4 Primary Layers (Presentation, Application, Domain, Infrastructure).
*   **Example:** A `Validator` role behaves differently in:
    *   **UI Layer:** Validates format (e.g., "Is this an email string?"). Immediate feedback, stateless.
    *   **Domain Layer:** Validates invariance (e.g., "Is this email unique?"). Deep check, stateful, constrained.
*   **Impact:** The Layer constrains *what* a Role is allowed to touch.

#### Dimension 2: The Time (Lifecycle)
*When does it happen?*
*   **Definition:** The temporal phase of execution in which the component is active.
*   **The Multiplier:** 3 Main Phases (Bootstrap/Init, Request/Runtime, Teardown/Dispose).
*   **Example:** A `Loader` role:
    *   **Init Time:** Loads configuration files once. Failure is fatal. Impact provides "Static Immutable State".
    *   **Runtime:** Loads user data per request. Failure is an exception. Impact provides "Dynamic Mutable State".

#### Dimension 3: The Physics (RPBL)
*How does it behave?*
*   **Definition:** The 4 fundamental forces that constrain a component's potential energy.
*   **The Multiplier:** 6,561 permutations ($9^4$).
*   **Forces:**
    *   **Responsibility (R):** Single vs. Omnibus. (Does it do one thing or many?)
    *   **Purity (P):** Deterministic vs. Side-Effects. (Does it change the world?)
    *   **Boundary (B):** Internal vs. External. (Does it talk to the outside?)
    *   **Lifecycle (L):** Ephemeral vs. Singleton. (Does it live forever?)
*   **Example:**
    *   `Service` (High Purity) = Calculation Engine.
    *   `Service` (Low Purity) = Notification Sender.

#### Dimension 4: The Meaning (Domain Intent)
*What is it about?*
*   **The Infinite Variable.** This is where the 33 Roles meet the real world.
    *   Role: `Mutator`
    *   Context A: `PhysicsEngine.applyForce(gravity)`
    *   Context B: `BankAccount.withdraw(money)`
*   The Role is constant; the Domain is variable.

---

## 4. Open Questions & Expansion Areas

### 4.1 Missing Contexts
*   **[TODO]**: Are there situations not covered by Layer/Lifecycle/RPBL/Domain?
*   **[TODO]**: How do we model "Framework Context" (e.g., React Component vs. Spring Bean)?

### 4.2 The "200th Atom" Problem
*   **[TODO]**: How do we handle "Composite Atoms" (like the Color Engine) that don't fit neatly? (Is it a Config? A Service? A ValueObject?)

### 4.3 Validation Strategy
*   **[TODO]**: How do we empirically verify the "Situation" formula?

---

## 5. Systems of Systems: The True Frame (Jan 21, 2026)

> **Discovery:** The right analogy is not "code is like biology." Both code AND biology are instances of a deeper pattern: **Systems of Systems**.

### 5.1 The Reframe

```
NOT THIS:
  Code ──analogous to──► Living Beings

THIS:
                    SYSTEMS OF SYSTEMS
                          │
            ┌─────────────┴─────────────┐
            ▼                           ▼
      Living Beings                   Code
      (biological SoS)            (computational SoS)
```

### 5.2 The Core Insight: Recursive Composition (Clarified Jan 21, 2026)

**Critical clarification:** SoS is NOT about external connections (repo connecting to other repos). It IS about **recursive composition looking BOTH directions**.

> "It's turtles all the way down AND all the way up."

Every level of code is a **system made of systems**:

```
TURTLES ALL THE WAY UP:
L12 UNIVERSE
 └── L11 DOMAIN
      └── L10 ORGANIZATION
           └── L9 PLATFORM
                └── L8 ECOSYSTEM
                     └── L7 SYSTEM
                          └── L6 PACKAGE
                               └── L5 FILE ← You are here
                                    └── L4 CONTAINER
                                         └── L3 NODE
                                              └── L2 BLOCK
                                                   └── L1 STATEMENT
                                                        └── L0 TOKEN
                                                             └── L-1 CHARACTER
                                                                  └── L-2 BYTE
                                                                       └── L-3 BIT

TURTLES ALL THE WAY DOWN:
```

**Key properties:**
1. **Every level is a system.** A function is a system. A statement is a system. A token is a system.
2. **Every level is composed of systems.** A function is made of statements, which are made of tokens.
3. **Emergence happens at EVERY level.** Not just at the top - three nodes consolidating purpose exhibit emergent properties.
4. **The 16-level scale IS a holarchy.** Each level is a **holon** (Koestler 1967) - simultaneously a WHOLE and a PART.

### 5.3 Holon Theory Connection

Arthur Koestler (1967) defined a **holon** as an entity that is:
- A **WHOLE** when looking DOWN (it contains parts)
- A **PART** when looking UP (it is contained)

This is the **Janus-faced** nature of code elements:

| Looking | The node is | It exhibits |
|---------|-------------|-------------|
| DOWN (inward) | A whole containing parts | Self-assertive tendency (autonomy) |
| UP (outward) | A part within a whole | Integrative tendency (belonging) |

**Example: A Function**
- Looking DOWN: It's a whole composed of statements, variables, control flow
- Looking UP: It's a part of a class, which is part of a module, which is part of a package...

**The holarchy** (hierarchy of holons) is NOT a dominance hierarchy. Each level has its own logic, its own emergent properties, its own purpose.

### 5.4 Emergence at Every Level

The "purpose" we compute (π₁, π₂, π₃...) isn't just top-down inheritance. Emergence happens at **each transition**:

```
π₁(statement) = atomic purpose (role of single node)
π₂(block) = emergent from {π₁(statements)} - NEW PROPERTY APPEARS
π₃(function) = emergent from {π₂(blocks)} - NEW PROPERTY APPEARS
π₄(class) = emergent from {π₃(functions)} - NEW PROPERTY APPEARS
...continues up...
```

This is why three nodes consolidating purpose IS emergence - you don't need the full codebase. Emergence is **fractal**: it happens at every scale.

### 5.5 Open Questions (Refined)

**Resolved:**
- ~~What makes something a System of Systems?~~ → Recursive composition (systems made of systems)
- ~~Is it systems all the way down?~~ → YES. And all the way UP.

**Still Open:**
- At what level does "meaning" emerge? Can a token have meaning, or only aggregates?
- Is there a "ground level" where systems become mere structure?
- How do we formalize the holon's dual nature (whole/part) in our schema?
- Can we compute emergence (detect when π(n+1) > Σ π(n))?

**Reference:** See `/assets/Universal_Laws_of_Software_Organisms_Page_*.png` for foundational research connecting Constructal Law, Cybernetics, VSM, and Synergetics to code.

---

## 6. Topology: Position in Flow (Jan 21, 2026)

> **Implemented:** `topology_role` property on nodes (commit 5b4ec51)

### 6.1 The Discovery

The term "leaf" already existed in `graph_type_inference.py` (line 93: `"leaf_called_by_service"`). We formalized what was implicit.

**Topology Role** = A node's structural position in the dependency flow.

| Role | Condition | Meaning |
|------|-----------|---------|
| `orphan` | in=0, out=0 | Disconnected (⚠️ see §13 - this is a misclassification bucket) |
| `root` | in=0, out>0 | Entry point, initiator |
| `leaf` | in>0, out=0 | Terminal, no outgoing dependencies |
| `hub` | high degree | Central coordinator |
| `internal` | in>0, out>0 | Normal flow-through |

> **⚠️ WARNING:** The `orphan` classification is structurally correct but semantically lazy. It conflates 7+ distinct phenomena (dead code, entry points, test fixtures, cross-language boundaries, etc.). See **Section 13: Disconnection Taxonomy** for the proper treatment.

### 6.2 Relational vs Intrinsic Properties

**Key Insight:** `topology_role` is a **relational property** - it cannot be determined from a node in isolation. It requires the whole graph.

| Property Type | Source | Example |
|---------------|--------|---------|
| Intrinsic | Node alone | atom, role, complexity |
| Relational | Graph context | topology_role, centrality, component_id |

**Open Questions:**
- What other relational properties matter?
  - `component_id` (which island?)
  - `is_bridge` (connects otherwise disconnected parts?)
  - `depth` (distance from roots?)
  - `betweenness` (how many paths pass through?)
- Is there a fundamental set of relational properties, or infinite?
- How do relational properties interact with intrinsic ones?

---

## 7. Flow Substances: What Moves Through the Graph? (Jan 21, 2026)

> **Direction:** We track structure, but what actually FLOWS through it?

### 7.1 Candidate Substances

| Layer | Substance | Source | Status |
|-------|-----------|--------|--------|
| **Static** | Dependencies | Code analysis | ✅ Tracked |
| **Static** | Import chains | Code analysis | ✅ Tracked |
| **Static** | Type flow | Code analysis | ⚪ Not yet |
| **Runtime** | Control flow | Profiler | ⚪ Not yet |
| **Runtime** | Execution time | Profiler | ⚪ Not yet |
| **Runtime** | Data/payloads | Tracer | ⚪ Not yet |
| **Runtime** | Memory | Profiler | ⚪ Not yet |
| **Change** | Impact propagation | Git + Graph | ⚪ Not yet |
| **Change** | Error cascade | Logs | ⚪ Not yet |
| **Human** | Cognitive load | Heuristics | ⚪ Not yet |
| **Human** | Understanding path | ? | ⚪ Not yet |

### 7.2 Open Questions

- Is there a "primary" substance, or are all equal?
- Do different substances flow through different subgraphs?
- Can we measure substance without instrumenting runtime?
- What is the relationship between static structure and dynamic flow?
  - Does structure PREDICT flow?
  - Or does flow SHAPE structure over time?

**Reference:** Constructal Law (Adrian Bejan) - "For a finite-size system to persist in time, it must evolve in such a way that it provides easier access to the currents that flow through it."

---

## 8. Interface Surface: The Membrane (Jan 21, 2026)

> **Direction:** Not just THAT components connect, but HOW they touch.

### 8.1 The Concept

The interface is the membrane between components - where Systems of Systems either integrate seamlessly or break catastrophically.

```
        ┌─────────────────────────────────────────┐
        │              NODE A                     │
        │  ┌─────────────────────────────────┐    │
        │  │         INTERNALS               │    │
        │  │    (private, can evolve)        │    │
        │  └─────────────────────────────────┘    │
        │                  │                      │
        │  ╔═══════════════╧═══════════════════╗  │
        │  ║      INTERFACE SURFACE            ║  │  ← THE MEMBRANE
        │  ╚═══════════════╤═══════════════════╝  │
        └──────────────────┼──────────────────────┘
                           │
                    CONNECTION
                           │
        ┌──────────────────┼──────────────────────┐
        │  ╔═══════════════╧═══════════════════╗  │
        │  ║      INTERFACE SURFACE            ║  │
        │  ╚═══════════════════════════════════╝  │
        │              NODE B                     │
        └─────────────────────────────────────────┘
```

### 8.2 Open Questions

**What IS an interface?**
- Is it the public methods? Or everything that CAN be touched?
- Is an undocumented internal that gets imported part of the interface?
- Where does interface end and implementation begin?

**How do we measure "good" connection?**
- Is loose coupling always better? Or context-dependent?
- What makes two components "seamlessly integrate"?
- Can we detect integration friction from structure alone?

**What flows through the interface?**
- Data? Control? Errors? Expectations?
- Is the interface the same for all substances?

**Stability vs Evolution tension?**
- A stable interface enables evolution of internals...
- But what enables evolution of the interface itself?
- Is there a meta-interface?

**API principles - measurable?**
- Interface Segregation: surface_area / dependents
- Dependency Inversion: depends_on_abstractions
- Law of Demeter: call_chain_depth
- Can we detect violations from structure?

---

## 9. Evolvability: Capacity to Adapt (Jan 21, 2026)

> **Direction:** Not just current state, but capacity for change.

### 9.1 The Concept

From the research slides (Engenharia da Evoluibilidade):
- **Núcleo Invariante** (Invariant Core) - hard to change, many dependents
- **Fronteiras Estáveis** (Stable Boundaries) - interface fixed, internals can change
- **Periferia** (Periphery) - easy to change, where evolution happens

**Hypothesis:** `topology_role` correlates with evolvability zone:
- `leaf` → periphery (safe to evolve)
- `hub` → core (dangerous to change)
- `internal` → boundary (moderate)

### 9.2 Open Questions

**Can evolvability be measured from structure?**
- Or does it require observing actual evolution (git history)?
- Is a node evolvable if it COULD change, or only if it HAS changed successfully?

**Evolvability for whom?**
- For the code? For the developer? For the organization?
- Is evolvability intrinsic, or relative to who's changing it?

**Does evolvability decay?**
- Does a node become less evolvable as dependencies accumulate?
- Is there an "evolvability half-life"?

**What enables evolvability?**
- Low in_degree (fewer dependents)?
- Stable interface (can change internals)?
- Test coverage (safe to modify)?
- Compartmentalization (isolated blast radius)?

**Candidate factors (not formulas):**
```
Possible inputs to evolvability:
  - coupling_freedom (inverse of in_degree?)
  - interface_stability (signature change frequency?)
  - test_coverage (safety net?)
  - change_success_rate (historical evidence?)
  - blast_radius (impact of change?)
  - compartment_isolation (bulkhead membership?)
```

---

## 10. Research Artifacts (Jan 21, 2026)

### 10.1 Source Materials

| Document | Location | Key Concepts |
|----------|----------|--------------|
| Universal Laws of Software Organisms | `/assets/Universal_Laws_*.png` | SoS, Constructal Law, VSM, Cybernetics |
| Código Vivo: A Física dos Sistemas Evolutivos | `/assets/Código_Vivo_*.png` | Flow physics, evolutionary systems |
| Código é Biologia: Engenharia Evolutiva | `/assets/Código_é_Biologia_*.png` | Biological engineering patterns |

### 10.2 Key Theoretical Connections

| Theory | Author | Connection to SMC |
|--------|--------|-------------------|
| Constructal Law | Adrian Bejan | Flow must branch to persist → topology_role |
| Viable System Model | Stafford Beer | System 1-5 hierarchy → layers + roles |
| Synergetics | Hermann Haken | Order emerges via "slaving" → hubs as order parameters |
| Cybernetics | Wiener/Ashby | Feedback loops → circuit breakers, homeostasis |
| Apoptosis | Biology | Programmed cell death → orphan detection, dead code |
| Compartmentalization | Biology | Bulkheads → component isolation |

---

## 11. Summary: What We Know vs. What We're Exploring

| Category | KNOW (implemented) | EXPLORING (questions) |
|----------|-------------------|----------------------|
| Structure | Nodes, edges, atoms, roles | Boundary detection |
| Position | `topology_role` | Depth, betweenness, bridges |
| Flow | Static dependencies | Runtime flow, all substances |
| Interface | Edge exists | Surface quality, coupling nature |
| Evolution | Git history exists | Evolvability as computable property |
| Frame | Code analysis | Systems of Systems unification |
| **Disconnection** | `orphan` label exists | **7-type taxonomy (§13)** |

**Principle:** We are asking questions, not making declarations. The theory grows through exploration, not definition.

---

## 12. Tree-sitter: The Implementation Bridge (Jan 21, 2026)

> **Discovery:** Tree-sitter's underutilized capabilities directly map to our theoretical gaps.

### 12.1 The Alignment

| SoS Theory Concept | Tree-sitter Capability | Current Status |
|--------------------|----------------------|----------------|
| Flow Substances | Data flow tracking (ST-08) | 0% utilized |
| Interface Surface | Scope tracking (@local.scope) | 0% utilized |
| What's inside | @local.definition | 0% utilized |
| What crosses boundary | @local.reference | 0% utilized |
| Dead code (orphan) | Definition without reference | 0% utilized |
| External dependency | Reference without definition | 0% utilized |
| State (D5) | Assignment tracking | 0% utilized |
| Effect (D6) | I/O calls, mutations | 0% utilized |

### 12.2 The Scope Graph IS the Membrane Model

```
TREE-SITTER SCOPE GRAPH              SoS INTERFACE SURFACE
───────────────────────────────────────────────────────────
@local.scope              =          Component boundary
@local.definition         =          What's INSIDE (private)
@local.reference          =          What CROSSES (interface)
def without ref           =          Dead substance (orphan)
ref without def           =          External flow (dependency)
```

### 12.3 Open Questions

- Can scope graph analysis reveal interface quality automatically?
- Does definition-reference linking give us "substance flow" for free?
- Can we detect interface violations from scope crossings?
- Is there a mapping from Tree-sitter's scope levels to our architectural layers?

### 12.4 Key Insight

> "Tree-sitter is not a parser. It's a complete code intelligence platform."
> — TREE_SITTER_INTEGRATION_SPEC.md

Current utilization: **5-10%**. The theoretical framework (SoS, flow, interfaces) and the implementation platform (Tree-sitter) are converging. The theory asks questions that Tree-sitter can answer.

**Reference:** See `docs/specs/TREE_SITTER_INTEGRATION_SPEC.md` for full capability inventory.

---

## 13. Disconnection Taxonomy: Replacing "Orphan" (Jan 21, 2026)

> **Discovery:** "Orphan" is a misclassification bucket, not a real category. It conflates 7+ distinct phenomena.

### 13.1 The Problem

Section 6 defines `topology_role=orphan` as nodes with `in_degree=0 AND out_degree=0`. This is **structurally correct but semantically lazy**.

Research reveals "orphan" in dependency graphs is a **known bad practice** across the industry:
> "Static analysis tools handle false positive orphans via whitelist rules, annotation-based exclusion, and iterative refinement."

Translation: Everyone knows "orphan" is wrong, so they bolt on hacks.

### 13.2 What "Orphan" Actually Conflates

| What We Label | What It IS | Correct Treatment |
|---------------|------------|-------------------|
| orphan | Dead code (truly unreachable) | **DELETE** |
| orphan | Entry point (__main__, CLI) | Mark as `root` |
| orphan | Test fixture (pytest, jest) | Mark as `test_root` |
| orphan | Framework-managed (DI, decorators) | Mark as `framework_root` |
| orphan | Cross-language boundary (JS↔Python) | Mark as `boundary` |
| orphan | Dynamic dispatch target (reflection) | Mark as `dynamic_target` |
| orphan | External interface (public API) | Mark as `external_boundary` |

**Evidence from Collider self-analysis (116 "orphans"):**
- Only 11 (9%) are truly dead code
- 68 (59%) are JS functions (cross-language gap)
- 16 (14%) are test fixtures
- 15 (13%) are dataclasses (instantiation not tracked)
- 6 (5%) are script entry points

### 13.3 Proposed: `disconnection` Property

Replace the single "orphan" label with a rich taxonomy:

```python
disconnection: {
    # WHY is this node disconnected?
    reachability_source:
        "unreachable"       |  # True dead code - DELETE
        "entry_point"       |  # __main__, CLI, event handler
        "test_entry"        |  # pytest fixture, test function
        "framework_managed" |  # @Component, dataclass instantiation
        "cross_language"    |  # Called from JS, YAML, etc.
        "dynamic_target"    |  # Reflection, eval, getattr
        "external_boundary",   # Public API, exported function

    # HOW is it disconnected?
    connection_gap:
        "isolated"     |  # No incoming AND no outgoing
        "no_incoming"  |  # Nothing calls this (but it calls others)
        "no_outgoing",    # Calls nothing (terminal)

    # How confident are we?
    isolation_confidence: 0.0 - 1.0,

    # What should we do?
    suggested_action: "OK" | "CHECK" | "DELETE"
}
```

### 13.4 Detection Logic

```
IF node is disconnected:
    IF in test file           → test_entry (confidence: 0.95)
    IF has __main__ guard     → entry_point (confidence: 0.99)
    IF has framework decorator → framework_managed (confidence: 0.90)
    IF different language     → cross_language (confidence: 0.70)
    IF has dynamic patterns   → dynamic_target (confidence: 0.60)
    IF is public/exported     → external_boundary (confidence: 0.80)
    ELSE                      → unreachable (confidence: 0.85)
```

### 13.5 Visualization Implications

**Current (Wrong):**
```
All orphans → Gray → "Dead code?" tooltip
```

**Proposed (Right):**

| Category | Color | Icon | Tooltip |
|----------|-------|------|---------|
| `unreachable` | Red | 💀 | "No callers found - safe to delete?" |
| `entry_point` | Green | ▶ | "Entry point - runs via __main__" |
| `test_entry` | Blue | 🧪 | "Test fixture - framework invokes" |
| `framework_managed` | Purple | ⚙ | "Framework creates this" |
| `cross_language` | Yellow | 🌉 | "Called from other language" |
| `dynamic_target` | Orange | ⚡ | "Called via reflection/dynamic" |
| `external_boundary` | Cyan | ↗ | "Public API - external callers" |

### 13.6 Theory Connection

This connects to multiple SMC concepts:

| Concept | Connection |
|---------|------------|
| **Interface Surface (§8)** | Disconnection types are boundary crossings our analysis can't see |
| **Flow Substances (§7)** | Different substances flow through different boundaries |
| **Tree-sitter (§12)** | `@local.reference` without `@local.definition` = external boundary |
| **Systems of Systems (§5)** | Each disconnection type is a different kind of system boundary |

### 13.7 Open Questions

**Confidence calibration:**
- How do we validate confidence scores empirically?
- Should confidence decay over time (stale analysis)?

**Cross-language completeness:**
- Can we ever fully trace JS↔Python↔YAML↔HTML boundaries?
- Is "cross_language" always a temporary classification?

**The "truly dead" problem:**
- Even `unreachable` might be called via:
  - String-based imports (`importlib.import_module`)
  - Config-driven dispatch
  - Plugin systems
- Is anything TRULY dead without runtime evidence?

**Framework detection:**
- How do we know all framework patterns?
- Is there a universal "framework marker" or is it framework-specific?

### 13.8 Implementation Status

| Component | Status |
|-----------|--------|
| Research | ✅ Complete (see `docs/research/ORPHAN_TAXONOMY.md`) |
| Theory | ✅ This section |
| Detection algorithm | ⚪ Not implemented |
| Schema update | ⚪ Not implemented |
| Visualization | ⚪ Not implemented |

**Reference:** See `docs/research/ORPHAN_TAXONOMY.md` for full research and visualization mockups.
