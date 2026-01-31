---
title: "L1: Definitions"
format: html
---

---
title: "L1: Definitions"
format: html
---

# L1: Definitions of the Standard Model of Code


**📍 Navigation:** [Theory Index](./THEORY_INDEX.md#FIXED) | [← L0: Axioms](./L0_AXIOMS.md#FIXED) | **Next:** [L2: Laws →](./L2_LAWS.md#FIXED)

**Layer:** 1 (Complete Enumeration)
**Status:** ACTIVE | EVOLVING
**Depends on:** [L0_AXIOMS.md](./L0_AXIOMS.md#FIXED)
**Version:** 2.0.0
**Created:** 2026-01-27

---

## Purpose of This Layer

This document defines **every concept that EXISTS** in the Standard Model of Code. Every entity, category, dimension, and structure is enumerated here **exactly once**. Other documents reference these definitions but never redefine them.

Principle: One concept, one definition, one location.

---

## 0. The Three Realms (PROJECT_elements Trinity)

**Status:** VALIDATED 2026-01-28 (harsh MECE testing)

> The architecture is organized around three mutually exclusive, collectively exhaustive realms.

| Realm | Directory | Purpose | Pipeline | Nature |
|-------|-----------|---------|----------|--------|
| **PARTICLE** | standard-model-of-code/ | Analyze structure | Collider (28 stages) | Deterministic |
| **WAVE** | context-management/ | Understand semantics | Refinery (4 stages) | Probabilistic |
| **OBSERVER** | .agent/ | Coordinate actions | Autopilot/Wire/Watcher | Reactive |

**Key properties:**
- **Mutually Exclusive:** Each component belongs to exactly one realm
- **Collectively Exhaustive:** All active components covered (ARCHIVE is passive)
- **Fundamental:** Not derived from other principles

**Metaphors:**
- PARTICLE = Body (physical measurement)
- WAVE = Brain (conceptual understanding)
- OBSERVER = Governance (meta-coordination)

**See:** [TRINITY_PRINCIPLE.md](../../context-management/docs/theory/TRINITY_PRINCIPLE.md#FIXED)

---

## 1. The Three Planes (Popper's Three Worlds)

The Standard Model recognizes three fundamental planes of existence:

| Plane | Name | What Lives Here | Examples |
|-------|------|----------------|----------|
| **1** | PHYSICAL | Hardware reality | Electrons, RAM cells, disk sectors, network signals, binary: `0x48 0x65 0x6C 0x6C 0x6F` |
| **2** | VIRTUAL | Information structures | AST nodes, runtime objects, FunctionDeclaration, ClassInstance, call stacks |
| **3** | SEMANTIC | Meaning and intent | Business logic, architectural roles (Repository, Entity, Service), purpose |

**Source:** Popper, K. (1978). "Three Worlds." Michigan Quarterly Review.

**Key insight:** These are not metaphors. Every code artifact simultaneously exists in all three planes:

- **Physical:** The file `user.py` is bytes on disk
- **Virtual:** The file is a parsed module with an AST
- **Semantic:** The module is "user management logic" (meaning)

The Standard Model primarily operates at plane 2 (Virtual -- AST structure) and plane 3 (Semantic -- purpose/role classification). Plane 1 is the substrate that makes computation possible.

---

## 2. The 16-Level Scale (Holarchy)

**Source:** MODEL.md §1, inspired by Koestler's "Holons" and Simon's "The Architecture of Complexity."

### 2.1 The Complete Scale

| Level | Name | Zone | What It Contains |
|-------|------|------|------------------|
| **L12** | UNIVERSE | COSMOLOGICAL | All software ever written |
| **L11** | DOMAIN | COSMOLOGICAL | A business/problem domain (e.g., "code analysis") |
| **L10** | ORGANIZATION | COSMOLOGICAL | Company or team repository collection |
| **L9** | PLATFORM | COSMOLOGICAL | Monorepo or platform (e.g., Collider ecosystem) |
| **L8** | ECOSYSTEM | COSMOLOGICAL | External boundaries, integrations, APIs |
| **L7** | SYSTEM | SYSTEMIC | Major subsystem (Parser, Classifier, Visualizer) |
| **L6** | PACKAGE | SYSTEMIC | Directory or language package (src/core/, analyze/) |
| **L5** | FILE | SYSTEMIC | Single source file / module (full_analysis.py) |
| **L4** | CONTAINER | SYSTEMIC | Class, struct, enum, trait, interface |
| **L3** | NODE | SEMANTIC | Function or method (THE atom of Standard Model) |
| **L2** | BLOCK | SEMANTIC | Control flow structure (if block, for loop, try-catch) |
| **L1** | STATEMENT | SEMANTIC | Single executable instruction |
| **L0** | TOKEN | SYNTACTIC | Keyword, identifier, literal, operator |
| **L-1** | CHARACTER | PHYSICAL | UTF-8 encoded character |
| **L-2** | BYTE | PHYSICAL | Raw byte (8 bits) |
| **L-3** | BIT/QUBIT | PHYSICAL | Binary digit (smallest unit) |

### 2.2 Zone Groupings

| Zone | Levels | Dominant Relations | Examples |
|------|--------|-------------------|----------|
| **PHYSICAL** | L₋₃ to L₋₁ | Encoding, storage, transmission | Bit patterns, bytes, encoding |
| **SYNTACTIC** | L₀ | Adjacency, grammar rules | Token streams, parse trees |
| **SEMANTIC** | L₁ to L₃ | Meaning, execution, control flow | Statements, blocks, functions |
| **SYSTEMIC** | L₄ to L₇ | Containment, composition, architecture | Classes, files, packages, systems |
| **COSMOLOGICAL** | L₈ to L₁₂ | Boundaries, strategy, domain context | APIs, platforms, organizations |

**Zone boundaries** are phase transitions (Axiom C3) where the type of morphisms that matter changes.

### 2.3 Holarchy Properties

Each level is:
- A **WHOLE** when looking down (it contains parts at lower levels)
- A **PART** when looking up (it is contained by higher levels)

This is **Koestler's Janus-faced holon**: every entity has dual nature depending on perspective.

**Example:**
- A File (L5) is a WHOLE relative to the classes it contains
- The same File is a PART relative to the package that contains it

**Canonical data:** Level assignments computed by `src/core/level_classifier.py` using deterministic kind-to-level mapping.

---

## 3. The -ome Partition (The Two Universes)

### 3.1 PROJECTOME

**Definition:** The totality of all files in a software project. The union of executable and non-executable artifacts.

```
PROJECTOME (P) = all project artifacts

P = C ⊔ X          (disjoint union, Axiom A1)
```

**Current PROJECT_elements counts:**
- Total files: ~850 (excluding .venv, node_modules, .git)
- Codome: ~250 files
- Contextome: ~600 files

### 3.2 CODOME

**Definition:** The complete set of parseable, executable artifacts.

```
CODOME (C) = {f ∈ P | executable(f)}
```

**Inclusion criteria** (file belongs to CODOME if):
- Tree-sitter can extract an AST from it
- It can be compiled or interpreted
- It participates in program execution or rendering

**File types included:**

| Category | Patterns | Examples |
|----------|----------|----------|
| Source code | `**/*.py`, `**/*.js`, `**/*.ts`, `**/*.go`, `**/*.rs`, `**/*.java` | Python, JavaScript, TypeScript, Go, Rust, Java |
| Markup (executable) | `**/*.html`, `**/*.css` | HTML templates, stylesheets |
| Query languages | `**/*.scm`, `**/*.sql` | Tree-sitter queries, SQL |
| Shell scripts | `**/*.sh`, `**/*.bash` | Automation |

**Exclusions:**
- Documentation (.md) → Contextome
- Configuration (.yaml, .json) → Contextome
- Dependencies (node_modules/, .venv/) → External (not project code)
- Build artifacts (dist/, out/) → Generated (not source)
- Binaries (.exe, .so, .dll) → Not parseable

**Analyzed by:** Collider pipeline (28 stages, deterministic, no AI required)

**Metrics:**
- Node count (functions + classes + modules)
- Edge count (calls + imports + contains + ...)
- Coverage (analyzed files / total source files)
- Health (topology + edges + gradients)

### 3.3 CONTEXTOME

**Definition:** All non-executable artifacts that inform, configure, or govern the CODOME.

```
CONTEXTOME (X) = {f ∈ P | ¬executable(f)}
              = P \ C         (set difference)
```

**File types included:**

| Category | Patterns | Examples |
|----------|----------|----------|
| Documentation | `**/*.md` | MODEL.md, specs, research, this file |
| Configuration | `**/*.yaml`, `**/*.json` | analysis_sets.yaml, tsconfig.json |
| AI outputs | `**/research/**` | Perplexity syntheses, Gemini sessions |
| Agent state | `.agent/**/*.yaml` | Task registry, roadmap, session logs |
| Schemas | `**/schema/**/*.json` | particle.schema.json, atoms.json |

**Analyzed by:** AI reasoning (ACI tiers - INSTANT, RAG, LONG_CONTEXT, PERPLEXITY, FLASH_DEEP, HYBRID). Uses semantic search, LLM inference, not AST parsing.

**Metrics:**
- Doc coverage (documented nodes / codome nodes)
- Freshness (updated in 30 days / total)
- Symmetry (matching code-doc pairs / total)
- Discoverability (indexed / total)

### 3.4 CONCORDANCES (Purpose-Aligned Regions)

**Definition:** A Concordance is a purpose-aligned region spanning BOTH Codome and Contextome.

```
Concordance k = (π, C_π, X_π, σ)

WHERE:
  π    = shared purpose (the WHY)
  C_π  ⊆ C = Codome slice serving π
  X_π  ⊆ X = Contextome slice describing π
  σ    = alignment score function
```

**Key properties:**
- Concordances **cover** but do not **partition**: Union(C_π) = P, but overlaps allowed
- A file may belong to multiple concordances (e.g., `full_analysis.py` is in "Pipeline" and "Governance")
- Concordances are **NOT** a third universe -- they are cross-cuts through the existing two

**Current PROJECT_elements concordances:**

| Concordance | Codome Path | Contextome Path |
|-------------|-------------|-----------------|
| Pipeline | `standard-model-of-code/src/core/` | `standard-model-of-code/docs/specs/` |
| Visualization | `standard-model-of-code/src/core/viz/` | `standard-model-of-code/docs/specs/UI*.md` |
| Governance | `.agent/tools/` | `.agent/registry/`, `.agent/specs/` |
| AI Tools | `context-management/tools/ai/` | `context-management/config/` |
| Theory | (N/A - no executable code) | `standard-model-of-code/docs/` |

### 3.5 Concordance States (The 2×2 Grid)

Every code-doc pair exists in one of four states:

| State | Code? | Docs? | Purposes Aligned? | Formula |
|-------|-------|-------|-------------------|---------|
| **CONCORDANT** | ✓ | ✓ | Yes | F(c) exists, drift ≤ ε |
| **DISCORDANT** | ✓ | ✓ | No | F(c) exists, drift > ε |
| **UNVOICED** | ✓ | ✗ | N/A | F(c) = ⊥ (no docs) |
| **UNREALIZED** | ✗ | ✓ | N/A | ∃x ∈ X: x ∉ Im(F) |

**Concordance Health Score:**

```
Health(k) = |CONCORDANT| / (|CONCORDANT| + |DISCORDANT| + |UNVOICED| + |UNREALIZED|)
```

Target: > 80% for production systems.

---

## 4. Classification System

### 4.1 Atoms (The Periodic Table)

**Definition:** An Atom is a structural type -- the fundamental unit of code classification.

**Canonical data:** `../../schema/fixed/atoms.json`

**Counts:**
- V1: 167 atoms (original model)
- V2: 200 atoms (expanded model)
- Current implementation: 94 atoms active
- T2 (ecosystem-specific): 3,445 mined atoms
- **Total inventory: 3,525 atoms**

**Atom structure:**

```
Atom = (phase, family, name)

Examples:
  LOG.FNC.Method        (Logic phase, Function family, Method atom)
  DAT.VAR.Parameter     (Data phase, Variable family, Parameter atom)
  ORG.AGG.Class         (Organization phase, Aggregate family, Class atom)
```

**Tiers:**
- **Base (22 atoms)**: Core semantic roles, ~90% structural coverage
- **T0 (42 atoms)**: AST atoms (definitional), 100% parseable
- **T1 (21 atoms)**: Standard library patterns, ~20-40% coverage
- **T2 (3,445 atoms)**: Ecosystem-specific (178 ecosystems), 0-60% variable coverage

**Key insight:** 4 base atoms (LOG.FNC.M, ORG.AGG.M, DAT.VAR.A, ORG.MOD.O) cover ~80-90% of code structure. T2 provides semantic enrichment, not structural coverage.

### 4.2 Phases (The Four Fundamental Categories)

**Canonical data:** `../../schema/fixed/atoms.json` (phase field)

| Phase | Symbol | What It Represents | Example Families |
|-------|--------|-------------------|------------------|
| **DATA** | DAT | Information structures | Variables, Primitives, Aggregates, Collections |
| **LOGIC** | LOG | Computation and control | Functions, Procedures, Methods, Algorithms |
| **ORGANIZATION** | ORG | Structure and grouping | Modules, Classes, Packages, Namespaces |
| **EXECUTION** | EXE | Runtime and instantiation | Threads, Processes, Jobs, Handlers |

**Source:** MODEL.md §2.1, attributed to standard software engineering taxonomy.

### 4.3 Roles (33 Canonical Functional Purposes)

**Definition:** A Role is a functional purpose -- what a code entity DOES in the system.

**Canonical data:** `../../schema/fixed/roles.json`

**The 33 roles organized by category:**

| Category | Roles | Purpose |
|----------|-------|---------|
| **Query** | Query, Finder, Loader, Getter | Read without side effects |
| **Command** | Command, Creator, Mutator, Destroyer | Write with side effects |
| **Factory** | Factory, Builder | Object creation |
| **Storage** | Repository, Store, Cache | Data persistence |
| **Orchestration** | Service, Controller, Manager | Coordination |
| **Validation** | Validator, Guard, Asserter | Enforcement |
| **Transform** | Transformer, Mapper, Serializer | Data conversion |
| **Event** | Handler, Listener, Subscriber | Async/reactive |
| **Utility** | Utility, Formatter, Helper | General-purpose |
| **Internal** | Internal, Lifecycle | Private/internal |
| **Unknown** | Unknown | Unclassified |

**Implementation status:** 29 of 33 roles have detection heuristics distributed across `src/core/` (heuristic_classifier.py, universal_classifier.py, dimension_classifier.py).

**Difference from Atoms:**
- **Atoms** = structural type (WHAT it is) -- determined by syntax
- **Roles** = functional purpose (WHY it exists) -- determined by edges/topology

Example: A function (atom: LOG.FNC.M) might be a Query (role) if it reads without mutation.

### 4.4 Dimensions (8-Axis Coordinate System)

**Definition:** Every node is classified along 8 orthogonal dimensions.

**Canonical data:** `../../schema/fixed/dimensions.json`

| Dimension | Question | Domain | Computed By |
|-----------|----------|--------|-------------|
| **D1: WHAT** | What kind of entity? | Atom (from periodic table) | Tree-sitter + atom classifier |
| **D2: LAYER** | Which architectural layer? | Interface, Application, Core, Infrastructure, Test | Heuristic (file path, imports) |
| **D3: ROLE** | What functional purpose? | 33 canonical roles | Graph topology + naming |
| **D4: BOUNDARY** | Information flow? | Internal, Input, Output, I-O | AST + effect analysis |
| **D5: STATE** | State management? | Stateless, Stateful | Scope analysis + mutations |
| **D6: EFFECT** | Side effects? | Pure, Read, Write, ReadWrite | Data flow analysis |
| **D7: LIFECYCLE** | Object lifecycle phase? | Create, Use, Destroy | Intent extraction |
| **D8: TRUST** | Confidence? | 0-100% | Classification confidence score |

**Proposed extensions** (from THEORY_AMENDMENT_2026-01.md):
- **D9: INTENT** | Intent clarity? | Documented, Implicit, Ambiguous, Contradictory | Docstring + git history |
- **D10: LANGUAGE** | Programming language? | py, js, ts, go, rs, java, ... | File extension |

**Status:** D1-D8 active. D9-D10 proposed.

**Pipeline stages:** D4, D5, D6, D7 computed in Stage 2.7 (Octahedral Dimension Classification).

### 4.5 RPBL Character Space (The DNA)

**Definition:** RPBL is a 4-dimensional character metric. Every node gets an (R, P, B, L) tuple.

```
RPBL: N → [1..9]^4          Maps nodes to 4-tuples

Total state space: 9^4 = 6,561 possible characters
```

**The four dimensions:**

| Dimension | Name | Question | Scale |
|-----------|------|----------|-------|
| **R** | Responsibility | How many concerns? | 1 (single) → 9 (god class) |
| **P** | Purity | Side effects? | 1 (pure) → 9 (impure IO) |
| **B** | Boundary | I/O crossing? | 1 (internal) → 9 (external API) |
| **L** | Lifecycle | Lifespan complexity? | 1 (transient) → 9 (persistent session) |

**Character profiles:**

| Profile | RPBL | Interpretation |
|---------|------|----------------|
| **Pure function** | (1, 1, 1, 1) | Single concern, no side effects, internal, transient |
| **Service class** | (3, 5, 4, 3) | Few concerns, some IO, moderate boundary, session lifetime |
| **God class** | (9, 8, 9, 7) | Many concerns, heavy IO, external API, long lifecycle (DANGER) |

**Implementation:** Computed in Stage 2.7 via heuristics combining AST + topology + file context.

---

## 5. Graph Elements

### 5.1 Node (Minimal Schema)

The fundamental unit of the Standard Model is a **node** -- a classified code entity.

**Minimal required fields:**

```json
{
  "id": "file_path::qualified_name",
  "atom": "LOG.FNC.Method",
  "level": "L3",
  "plane": "Virtual",
  "location": {
    "file": "src/services/user.py",
    "line_start": 45,
    "line_end": 67
  }
}
```

**Canonical schema:** `../../schema/particle.schema.json`

### 5.2 Node (Full Schema with Enrichments)

A fully enriched node includes:

```json
{
  "id": "...",
  "atom": "...",
  "dimensions": {
    "D1_WHAT": "Method",
    "D2_LAYER": "Core",
    "D3_ROLE": "Query",
    "D4_BOUNDARY": "Internal",
    "D5_STATE": "Stateless",
    "D6_EFFECT": "Pure",
    "D7_LIFECYCLE": "Use",
    "D8_TRUST": 92.0
  },
  "level": "L3",
  "level_name": "NODE",
  "level_zone": "SEMANTIC",
  "plane": "Semantic",
  "rpbl": {
    "responsibility": 1,
    "purity": 2,
    "boundary": 2,
    "lifecycle": 1
  },
  "purpose_emergence": {
    "pi1_purpose": "Query",
    "pi2_purpose": "Retrieve",
    "pi3_purpose": "Repository",
    "pi4_purpose": "DataAccess"
  },
  "graph": {
    "in_degree": 5,
    "out_degree": 2,
    "topology_role": "utility",
    "betweenness_centrality": 0.027,
    "pagerank": 0.003
  },
  "semantic_role": "utility",
  "metadata": {
    "signature": "get_by_id(self, user_id: str) -> User",
    "docstring": "Retrieve user by ID",
    "complexity": 3,
    "lines_of_code": 23
  }
}
```

**Relational vs Intrinsic properties:**
- **Intrinsic**: Can be determined from the node alone (atom, location, metadata)
- **Relational**: Require graph context (in_degree, semantic_role, purpose emergence, centrality)

**See:** L0 Axiom D3 (Transcendence) -- purpose is relational, not intrinsic.

### 5.3 Edge (Relationships)

**Definition:** An Edge is a typed relationship between two nodes.

**Minimal schema:**

```json
{
  "source": "file_path::source_name",
  "target": "file_path::target_name",
  "type": "calls",
  "family": "Dependency"
}
```

### 5.4 Edge Types (6 Core + Extensions)

**Canonical data:** Defined in MODEL.md §3.3 and `src/core/edge_extractor.py`

| Type | Family | Meaning | Example |
|------|--------|---------|---------|
| **calls** | Dependency | Function/method invocation | `main()` calls `process()` |
| **imports** | Dependency | Module dependency | `from auth import login` |
| **contains** | Structural | Hierarchical containment | `UserService` contains `get_user` |
| **inherits** | Inheritance | Class inheritance | `Dog` inherits `Animal` |
| **implements** | Inheritance | Interface implementation | `FileRepo` implements `IRepository` |
| **uses** | Semantic | Type/data usage | Function uses type `User` |

**Extended types:**
- references, mixes_in, extends, decorates, wraps, delegates_to, returns, receives, precedes, follows, triggers, disposes

**Edge families:**
- **Structural**: contains, is_part_of
- **Dependency**: calls, imports, uses
- **Inheritance**: inherits, implements, extends, mixes_in
- **Semantic**: references, decorates, wraps, delegates_to
- **Temporal**: precedes, follows, triggers, disposes

### 5.5 Topology Roles (Graph Position)

**Definition:** Where a node sits in the dependency graph.

| Role | Definition | Degree Pattern |
|------|-----------|----------------|
| **orphan** | in_degree = 0, out_degree = 0 | Isolated (but see Disconnection Taxonomy) |
| **root** | in_degree = 0, out_degree > 0 | Entry point |
| **leaf** | in_degree > 0, out_degree = 0 | Terminal/specialized |
| **hub** | in_degree > threshold, out_degree > threshold | Central junction |
| **internal** | All others | Normal node |

**Note:** "orphan" is misleading. Use **Disconnection Taxonomy** instead (§5.6).

### 5.6 Disconnection Taxonomy (Refined Classification)

**Definition:** Why a node APPEARS disconnected in the static graph (replaces lazy "orphan" label).

**The 7 types:**

| Reachability Source | Meaning | Action |
|--------------------|---------|--------|
| **test_entry** | Test framework invokes it (pytest, jest) | OK - framework-managed |
| **entry_point** | Program entry (__main__, CLI) | OK - entry point |
| **framework_managed** | Decorator/DI container invokes it | OK - framework-managed |
| **cross_language** | Called from different language (JS from HTML) | OK - cross-boundary |
| **external_boundary** | Public API consumed externally | OK - ecosystem boundary |
| **dynamic_target** | Reflection/getattr/eval target | CHECK - verify intent |
| **unreachable** | Actually dead code | DELETE or document |

**Computed by:** `src/core/full_analysis.py::classify_disconnection()` using heuristics on file path, decorators, naming.

### 5.7 Dependency Rings (Concentric Architecture)

**Definition:** A Ring is the dependency depth of a node, measured as maximum distance from nodes with zero internal imports. Ring describes concentric layers of dependency flow.

**The Ring Scale (0-4):**

| Ring | Name | Definition | Typical Contents |
|------|------|------------|------------------|
| **0** | CORE | No internal dependencies | Pure utilities, constants, types, base abstractions |
| **1** | DOMAIN | Depends only on Ring 0 | Domain entities, value objects, core business logic |
| **2** | APPLICATION | Depends on Ring 0-1 | Use cases, application services, orchestration |
| **3** | ADAPTER | Depends on Ring 0-2 | Repositories, external integrations, I/O boundaries |
| **4** | FRAMEWORK | Depends on Ring 0-3 + externals | Entry points, CLI, web handlers, framework bindings |

**Ring Calculation:**

```
Ring(n) = 0                           if internal_deps(n) = ∅
Ring(n) = 1 + MAX(Ring(d) for d in internal_deps(n))   otherwise

WHERE:
  internal_deps(n) = {d ∈ nodes | n imports d ∧ d ∈ same_codebase}
```

**Edge Cases:**

| Case | Resolution |
|------|------------|
| **Circular dependencies** | All nodes in cycle get Ring = MAX(individual calculations) + 1 (cycle penalty) |
| **Entry points** | Ring 4 (even if low deps) — they are framework bindings |
| **External-only** | Ring 0 (external deps don't count for ring calculation) |
| **Orphan nodes** | Ring 0 (no deps = core) but flagged with AM005 warning |
| **Multi-path deps** | Take MAX path (worst case determines ring) |

**Antimatter Laws:**

- **AM006: Centrifugal Dependency Violation** — Inner rings MUST NOT depend on outer rings. Ring 0 cannot import Ring 1+. Violations create architectural drift.
- **AM007: Ring Orphan Warning** — Nodes with no incoming edges are Ring 0 by definition but may be dead code (see Disconnection Taxonomy §5.6 for nuanced classification).

**Key Properties:**

1. **Ring is contextual:** Same atom type (e.g., Service) can exist at different rings. Ring is a property of the instance, not the type.
2. **Ring ≠ Level:** Levels (§2) describe containment hierarchy (file contains class contains method). Rings describe dependency flow.
3. **Ring ≠ Phase:** Phases (§4.2) describe atom categories (DAT/LOG/ORG/EXE). A Method (LOG phase) can be Ring 0, 1, 2, 3, or 4.
4. **Direction:** Dependencies flow INWARD (outer → inner). Ring 4 depends on Ring 0, never reverse.

**Visualization:** Concentric circles where Ring 0 is the center (most stable) and Ring 4 is the outermost (most volatile).

```
        ┌─────────────────────────────────────┐
        │  Ring 4: FRAMEWORK (entry points)   │
        │  ┌─────────────────────────────┐    │
        │  │  Ring 3: ADAPTER (I/O)      │    │
        │  │  ┌─────────────────────┐    │    │
        │  │  │  Ring 2: APPLICATION│    │    │
        │  │  │  ┌─────────────┐    │    │    │
        │  │  │  │ Ring 1: DOM │    │    │    │
        │  │  │  │ ┌───────┐   │    │    │    │
        │  │  │  │ │ R0:   │   │    │    │    │
        │  │  │  │ │ CORE  │   │    │    │    │
        │  │  │  │ └───────┘   │    │    │    │
        │  │  │  └─────────────┘    │    │    │
        │  │  └─────────────────────┘    │    │
        │  └─────────────────────────────┘    │
        └─────────────────────────────────────┘

        Dependency direction: ────────────────►
                              (outer to inner)
```

**Derived from:** Edge Family "Dependency" (§5.4) — specifically `imports` and `calls` edges within the codebase.

**Implementation status:** Proposed for Stage 2.8 (Ring Classification) in Collider pipeline.

### 5.8 Locus (Topological Address)

**Definition:** The LOCUS is the complete multi-dimensional coordinate that locates an atom in the Standard Model's theory space. It is the "topological postal code" of a code entity.

**Etymology:** From Latin *locus* ("place"). In genetics, a locus is the specific, fixed position of a gene on a chromosome (e.g., BRCA1 at 17q21.31). In mathematics, a locus is the set of all points satisfying certain conditions.

**Source:** Validated 2026-01-31 (Gemini 98/100, Perplexity confirmed)

**Formula:**

```
LOCUS(atom) = ⟨λ, Ω, τ, α, R⟩

WHERE:
  λ (Level)  = L-3 to L12 (hierarchical scale position)
  Ω (Ring)   = 0-4 (dependency depth)
  τ (Tier)   = T0, T1, T2 (abstraction tier)
  α (Role)   = 33 canonical roles (functional purpose)
  R (RPBL)   = 4-tuple (Responsibility, Purity, Boundary, Lifecycle)
```

**Example:**

```
Physical Address:  123 Main St, Apt 4B, NYC, NY 10001, USA
Code Locus:        ⟨L3, R1, T1, Query, (1,2,2,1)⟩

Concrete example:
  getUserById() → LOCUS = ⟨L3, R1, T1, Query, (1,2,2,1)⟩

  Meaning:
    L3    = NODE level (function)
    R1    = DOMAIN ring (depends only on core)
    T1    = Standard library patterns tier
    Query = Functional role (read without mutation)
    (1,2,2,1) = RPBL character (single concern, mostly pure, internal, transient)
```

**Key Properties:**

1. **Every atom has exactly one Locus** — Locus is the unique theoretical identity
2. **Locus ≠ Location** — Location is file path (mutable); Locus is theory coordinates (invariant)
3. **Locus solves Ship of Theseus** — If Locus changes, it's a different entity, not just refactored
4. **Multi-dimensional** — Unlike genetic locus (linear on chromosome), SMC Locus is n-dimensional

**Cross-Domain Terminology:**

| Source Domain | Term | SMC Equivalent | Relationship |
|--------------|------|----------------|--------------|
| **Genetics** | Chromosome | Codebase | Container structure |
| | Gene | Atom | Functional unit |
| | Locus | **LOCUS** | Positional address |
| | Allele | Instance/Variant | Same position, different form |
| | Genome | Projectome | Complete set |
| | Genotype | Full Classification | What it IS |
| | Phenotype | Runtime Behavior | What it DOES |
| **Physics** | Atom | Atom | Fundamental unit |
| | Particle | Node | Observable entity |
| | Coordinate | LOCUS | Position in space |
| **Mathematics** | Locus (geometry) | LOCUS | Set of points satisfying conditions |
| | Dimension | 8 Dimensions | Orthogonal axes |

**Canonical data:** Locus values computed by Collider pipeline, stored in `UnifiedNode.locus` field.

**Implementation status:** Proposed for `particle.schema.json` update.

### 5.9 Holon (Self-Contained Autonomous Unit)

**Definition:** A HOLON is a self-contained, semi-autonomous unit that exhibits BOTH the properties of a whole (looking down at its parts) AND a part (looking up at its container). NOT every code entity is a holon — only those meeting specific autonomy and coherence criteria.

**Etymology:** Coined by Arthur Koestler (1967) in *The Ghost in the Machine*. From Greek *holos* ("whole") + suffix *-on* (suggesting particle, as in proton/neutron).

**Source:** Koestler, A. (1967). Validated 2026-01-31 (Perplexity deep research, 60+ academic sources)

**Qualifying Criteria (ALL required):**

| Criterion | Definition | Example |
|-----------|------------|---------|
| **Semi-autonomy** | Operates without constant instruction from higher authority | Microservice handles requests independently |
| **Self-regulation** | Maintains stability under disturbance | Service recovers from errors, maintains state |
| **Functional coherence** | Integrated unit, not arbitrary division | Complete bounded context, not half a module |
| **Clear boundary** | API surface without mingling internals | Well-defined interface, no leaky abstractions |

**What Does NOT Qualify as a Holon:**

```
✗ Random function         → No autonomy (called by others, no self-direction)
✗ Utility class           → No self-regulation (stateless helper)
✗ Arbitrary file boundary → No functional coherence (organizational, not semantic)
✗ Tightly coupled module  → No clear boundary (internals exposed)
✗ Half of a subsystem     → Arbitrary division, not functionally coherent
```

**What DOES Qualify as a Holon:**

```
✓ Microservice with API   → Autonomous, bounded, self-regulating
✓ Bounded Context (DDD)   → Self-contained domain with clear interface
✓ Self-contained subsystem → Complete functional unit with API
✓ Plugin/Extension        → Operates independently within host constraints
✓ Autonomous agent        → Self-directing with defined interface
```

**The Janus Principle:**

Every holon exhibits dual nature (named after the two-faced Roman god):
- **Looking DOWN:** It is a WHOLE containing sub-holons
- **Looking UP:** It is a PART contained by super-holons

```
Holarchy (nested holons):

  ECOSYSTEM (L8)           ← Super-holon
      │
      ├── SYSTEM (L7)      ← Holon (whole relative to packages, part relative to ecosystem)
      │       │
      │       ├── PACKAGE (L6)   ← Holon (if self-contained)
      │       │       │
      │       │       └── FILE (L5)   ← Usually NOT holon (arbitrary boundary)
      │       │               │
      │       │               └── CLASS (L4)  ← Maybe holon (if autonomous)
```

**Holon vs Related Concepts:**

| Concept | Scope | Every entity? | Key property |
|---------|-------|---------------|--------------|
| **HOLON** | Self-contained unit | NO (only qualifying) | Autonomy + coherence |
| **LOCUS** | Position in theory space | YES (every atom) | Coordinates |
| **ATOM** | Structural type | YES (every entity) | Classification |
| **RING** | Dependency depth | YES (every atom) | Concentric layer |
| **LEVEL** | Containment hierarchy | YES (every entity) | Scale position |

**Emergence and Holons:**

Holons are NOT pre-existing positions waiting to be filled. **Emergence CREATES holons:**

```
When: sum_of_parts < emergent_whole
Then: A new holon level has manifested

Example:
  - Individual functions → (organization) → Coherent service (HOLON BORN)
  - Random classes → (integration) → Bounded context (HOLON BORN)
  - Scattered code → (clustering) → Self-contained module (HOLON BORN)
```

**Detection heuristic:** Empirically examine codebase clustering. Where natural boundaries form with API surfaces, holons exist.

**Note on Holon Boundaries:**

Holon boundary violations are **runtime/deployment concerns**, not static analysis concerns. Collider analyzes one codebase at a time — external systems cannot "breach" into our code in static analysis. For internal coupling, see AM005 (Bounded Context Violation).

**Canonical reference:** Koestler, A. (1967). *The Ghost in the Machine*. Hutchinson.

**See also:** PROSA architecture (holonic manufacturing), Holonic Multi-Agent Systems (HMAS)

---

## 6. The Situation Formula

**Definition:** A Situation is the complete contextual state of a node.

```
Situation(n) = (Role, Layer, Lifecycle, RPBL, Domain)

WHERE:
  Role      = D3 (functional purpose)
  Layer     = D2 (architectural stratum)
  Lifecycle = D7 (temporal phase)
  RPBL      = 4-tuple character
  Domain    = inferred business domain (from semantic cortex)
```

**Cardinality:**

```
|Situations| = 33 × 6 × 3 × 6561 × D
             ≈ 4 million possible situations (for D ~ 10 domains)
```

The Situation is **richer** than Role alone -- it captures architectural, temporal, and character dimensions that Role omits.

**Use case:** Two nodes with the same Role (e.g., "Repository") may have radically different Situations if one is (Repository, Infrastructure, Create, (2,6,8,4), Persistence) and the other is (Repository, Core, Use, (1,2,2,1), Domain).

---

## 7. The 10 Universal Subsystems

**Definition:** Miller's 10 universal subsystems applied to codebases.

**Source:** MODEL.md §8, Miller, J. G. (1978). "Living Systems."

| Subsystem | Software Analogue | Examples |
|-----------|------------------|----------|
| **Boundary** | API surface, module exports | Public interfaces, entry points |
| **Ingestor** | Input handling | Request parsers, CLI args, form validators |
| **Distributor** | Routing logic | HTTP routers, event dispatchers |
| **Converter** | Data transformation | Serializers, parsers, mappers |
| **Producer** | Output generation | Response builders, renderers |
| **Storage** | Persistence layer | Databases, caches, filesystems |
| **Extruder** | Output emission | Loggers, HTTP responses, file writers |
| **Motor** | Execution engine | Task runners, job processors |
| **Supporter** | Infrastructure | Auth, logging, monitoring, config |
| **Decider** | Control logic | Business rules, validators, state machines |

**Application:** A healthy codebase has clear representatives of all 10 subsystems. Missing subsystems indicate architectural gaps.

---

## 8. Extensions (Status-Tagged)

The following concepts are **proposed** but not yet fully integrated into the core Standard Model. Each has explicit status tags.

### 8.1 [PROPOSED] Toolome (Amendment A1)

**Status:** Proposed (2026-01-26), not yet validated
**Source:** THEORY_AMENDMENT_2026-01.md §1

**Definition:** The TOOLOME is the universe of development tools that shape CODOME structure.

```
CODOME_observed = f(CODE_intended, TOOLCHAIN)

WHERE TOOLCHAIN = {formatters, linters, type_systems, build_tools, test_frameworks, LSPs}
```

**Tool Ontology:**

```
TOOL_UNIVERSE
├── TOOLOME (Development Tools) - Shape the CODOME
│   ├── T-Atoms: T-Formatter, T-Linter, T-TypeChecker, T-Bundler, T-TestRunner
│   └── T-Roles: T-Enforcer, T-Suggester, T-Transformer, T-Analyzer, T-Generator
│
└── STONE_TOOLS (Analysis Tools) - Observe the CODOME
    ├── S-Atoms: S-StructuredData, S-Graph, S-Visualization, S-Report
    └── S-Roles: S-Parser, S-Analyzer, S-Measurer, S-Validator
```

**Stone Tool Test:**

```
STONE_TOOL_TEST(tool) = "Can a human use this directly without AI mediation?"

Passes: git, grep, cat, pytest
Fails: GraphRAG embeddings, 50MB JSON schemas
```

**Implementation status:** Stage 0.5 (Toolchain Discovery) designed but not yet implemented.

### 8.2 [PROPOSED] Dark Matter (Amendment A2)

**Status:** Proposed (2026-01-26), 14.7% of edges exhibit dark matter signature
**Source:** THEORY_AMENDMENT_2026-01.md §2

**Definition:** Dark Matter edges are invisible dependencies that cross codome boundaries.

**The 5 types:**

| Type | Meaning | Example |
|------|---------|---------|
| **Framework edges** | Framework invokes code via convention | Django calls view functions via URL routing |
| **Reflection edges** | Dynamic dispatch via getattr/eval | `getattr(obj, method_name)()` |
| **Cross-language edges** | Call crosses language boundary | JavaScript function called from HTML onclick |
| **Template edges** | Code invoked via template rendering | Jinja2 template calls Python filter |
| **External consumer edges** | npm/pip consumers use our public API | Unknown downstream callers |

**Empirical finding:** 14.7% of edges in typical codebases have no visible source in static analysis.

**Implementation status:** Partially detected via codome boundary nodes (Stage 6.8).

### 8.3 [PROPOSED] Confidence as Meta-Dimension (Amendment A3)

**Status:** Proposed (2026-01-26), 36.8% of nodes have low confidence
**Source:** THEORY_AMENDMENT_2026-01.md §3, currently mapped to D8:TRUST

**Definition:** Classification confidence as a meta-dimension orthogonal to the 8 core dimensions.

```
Confidence: N → [0, 1]

Confidence(n) = f(
  parse_success,
  pattern_match_strength,
  edge_consistency,
  naming_clarity,
  docstring_presence
)
```

**Aggregation:**

```
Codebase_Confidence = weighted_mean(node_confidences)

Weights by atom:
  Function: 1.0 (high importance)
  Variable: 0.3 (low importance)
```

**Current implementation:** D8:TRUST field (0-100%). The amendment proposes elevating this to a first-class meta-dimension with formal aggregation rules.

---

## Machine-Readable Canonical Data

All definitions in this layer trace to authoritative machine-readable sources:

| Concept | Canonical Schema |
|---------|------------------|
| Atoms | `../../schema/fixed/atoms.json` |
| Roles | `../../schema/fixed/roles.json` |
| Dimensions | `../../schema/fixed/dimensions.json` |
| Antimatter laws | `../../schema/antimatter_laws.yaml` |
| Constants | `../../schema/constants.yaml` |
| Node schema | `../../schema/particle.schema.json` |
| Types (Python) | `../../schema/types.py` |
| Types (TypeScript) | `../../schema/types.ts` |

## 9. Architectural Properties (Invocation and Navigation)

**[Status: EMERGING - Validated 75-78%, integration of established components in novel framework]**

### 9.1 API (Application Programming Interface)

**[Validation: 78% - POINT framework from literature, boundary-crossing confirmed, exact level threshold has nuance]**

**Definition:** An API is an interface that crosses a **meaningful boundary** with formal contracts.

**POINT Framework (What makes something an API):**
```
API(interface) = true ⟺
  P - Purposeful     (formal documentation exists)
  O - Oriented       (follows architectural style: REST, gRPC, GraphQL)
  I - Isolated       (decoupled from implementation details)
  N - Negotiated     (crosses meaningful boundary)
  T - Versioned      (backward compatibility commitments)
```

**Meaningful Boundary** exists when at least one of:
- Different organizational owners/teams
- Different deployment cycles
- Different version control repositories
- Different processes or network boundaries
- Different operational requirements

**Scale Emergence:**
```
L3 (NODE - Function)    → NOT API (internal call, refactorable)
L5 (FILE - Module)      → NOT API (module interface, internal)
L6 (PACKAGE)            → MAYBE API (if crosses team boundary)
L7 (SYSTEM - Subsystem) → YES API (crosses subsystem boundary)
L8+ (ECOSYSTEM+)        → ALWAYS API (crosses organizations)
```

**Key Distinction:**
- Function call: No versioning, no contract, refactorable at will
- Module interface: Internal boundary, shared control
- **API**: Formal contract, versioned, stable, independent evolution

**Academic Sources:**
- IEEE/ISO standards on software interfaces
- Fowler, M. "Microservices" (API boundaries at service level)
- Fielding, R. "REST" (architectural style for APIs)
- SOA literature (service boundary formalization)

**See:** `docs/research/theories/api_scale_emergence_report.md`

---

### 9.2 Dual Navigation Spaces

**[Validation: 75% - Components individually established (graphs, embeddings, knowledge graphs), explicit integration emerging, HybridRAG validates effectiveness]**

**Definition:** Code exists in two simultaneous navigation spaces serving different purposes.

**Space 1: Execution Graph (Discrete, Relational)**
```
G_exec = (V, E, T)

WHERE:
  V = code entities (functions, classes, files)
  E ⊆ V × V = dependency edges
  T: E → {calls, imports, inherits, contains, ...} = edge types

Navigation: Graph traversal, reachability analysis, path finding
Used by: Computer at runtime (100%)
Used by: Humans (50% - for understanding structure)

Properties:
- Discrete (finite nodes and edges)
- Deterministic (edges are explicit)
- Computable (graph algorithms)
- Execution-relevant (runtime follows these paths)
```

**Space 2: Semantic Embedding (Continuous, Conceptual)**
```
S_semantic = (V, d)

WHERE:
  embed: V → ℝⁿ (embedding function)
  d(v₁, v₂) = 1 - cosine(embed(v₁), embed(v₂)) (distance metric)

Navigation: k-NN search, similarity queries, clustering
Used by: Computer at runtime (0% - semantics not execution-relevant)
Used by: Humans (50% - for understanding meaning/concepts)

Properties:
- Continuous (metric space)
- Probabilistic (similarity is learned)
- Semantic (meaning-based, not structure-based)
- Understanding-relevant (conceptual navigation)
```

**Integration (Galois Connection):**
```
Dual navigation uses BOTH spaces:
- Execution graph: "What calls this?" "Where is this used?"
- Semantic space: "What's similar?" "Find related concepts?"

Formal: Galois connection (α, γ) bridges discrete ↔ continuous
  α: Concrete structure → Abstract semantics
  γ: Abstract semantics → Concrete structure
```

**Critical Insight:**
Computer navigation uses ONLY execution graph (dependencies).
Human navigation uses BOTH (structure + meaning).

**Practical Implementations:**
- GraphRAG: Combines graph structure + embeddings
- HybridRAG: Dual retrieval (graph + vector)
- Code property graphs: Typed edges + semantic analysis

**Mathematical Foundations:**
- Graph theory: Dependency structure (established)
- Vector spaces: Embeddings and cosine similarity (established)
- Galois connections: Abstraction bridges (established)
- Category theory: Functors between spaces (established)
- **Integration as unified framework: EMERGING**

**Academic Sources:**
- Abstract interpretation (Cousot) - Galois connections
- Code2vec, AST embeddings - Semantic space
- GraphRAG, HybridRAG research - Hybrid models
- MATE code property graphs - Practical implementation

**See:** `docs/research/theories/dual_navigation_space_report.md`

---

**Terminology:** `../../GLOSSARY.yaml` (122 terms, canonical vocabulary)

**Validation:** Every term in GLOSSARY.yaml must trace to exactly one section in L0-L3. If GLOSSARY defines a term not in L1, either L1 is incomplete or GLOSSARY is stale.

---

## Cross-References

### To L0 (Why these definitions exist)
- Three planes → Axiom G (Observability across planes)
- 16 levels → Axiom C (Level structure)
- MECE partition → Axiom A1 (and Lawvere proof A1.1)
- Atoms/Roles → Axiom D (Classification enables purpose)

### To L2 (How these things behave)
- Purpose emergence (pi1-pi4) → L2 §1
- Drift and debt → L2 §4
- Concordance algebra → L2 §4
- Compositional alignment → L2 §7
- Code entanglement → L2 §8

### To L3 (How we measure)
- Q-scores use RPBL, dimensions, purpose → L3 §1
- Health uses topology roles, edges → L3 §2
- Pipeline uses all classifications → L3 §4

---

*This is Layer 1. Every concept exists here, defined exactly once.*
*For WHY these exist, see L0. For HOW they behave, see L2. For HOW we measure, see L3.*

---

## Navigation

**📍 Up:** [Theory Index](./THEORY_INDEX.md#FIXED)
**⬅️ Previous:** [L0: Axioms](./L0_AXIOMS.md#FIXED) - Foundation these definitions build on
**➡️ Next:** [L2: Laws](./L2_LAWS.md#FIXED) - How these definitions behave
**🔄 Loop:** [L3: Applications](./L3_APPLICATIONS.md#FIXED) → [L0: Axioms](./L0_AXIOMS.md#FIXED)
