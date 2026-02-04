# CODE ZOO - Canonical Taxonomy of Software Entities

**Theory Layer:** L1 (Definitions)
**Status:** SWEBOK-ALIGNED (2026-01-31)
**Purpose:** Name every type of entity in software engineering and define its LOCUS
**SWEBOK Alignment:** 40 matches, 24 gaps addressed, 23 enhancements applied

---

## 1. WHAT IS THE CODE ZOO?

The **Code Zoo** is a taxonomy of software entity types.
The Code Zoo provides a framework for classifying a wide range of software entities.

**Principle:** If it exists in software, it has a name and a place.

---

## 2. THE LOCUS CONCEPT

**LOCUS** (Latin: "place") = The complete multi-dimensional coordinate that locates an atom in theory space.

**Canonical Definition (from L1_DEFINITIONS.md §5.8):**

```
LOCUS(atom) = ⟨λ, Ω, τ, α, R⟩

WHERE:
  λ (Level)  = L-3 to L12 (hierarchical scale position)
  Ω (Ring)   = 0-4 (dependency depth: CORE → FRAMEWORK)
  τ (Tier)   = T0, T1, T2 (abstraction tier)
  α (Role)   = 33 canonical roles (functional purpose)
  R (RPBL)   = 4-tuple (Responsibility, Purity, Boundary, Lifecycle)
```

**Example:**
```
Entity: getUserById()
Locus:  ⟨L3, R1, T1, Query, (1,2,2,1)⟩

Meaning:
  λ = L3      NODE level (function)
  Ω = R1      DOMAIN ring (depends only on core)
  τ = T1      Standard library patterns tier
  α = Query   Functional role (read without mutation)
  R = (1,2,2,1)  RPBL: single concern, mostly pure, internal, transient
```

**Key Properties:**
- Every atom has exactly one Locus
- Locus ≠ Location (file path is mutable; Locus is theory coordinates)
- Locus solves Ship of Theseus: if Locus changes, it's a different entity

**Component Quick Reference:**

| Symbol | Name | Range | Question Answered |
|--------|------|-------|-------------------|
| λ | Level | L-3 to L12 | How big is it? (scale position) |
| Ω | Ring | 0-4 | How deep in deps? (concentric layer) |
| τ | Tier | T0, T1, T2 | How abstract? (T0=AST, T1=patterns, T2=ecosystem) |
| α | Role | 33 canonical | What's it FOR? (functional purpose) |
| R | RPBL | [1-9]^4 | What's its character? (4-axis DNA) |

**RPBL Character Metric:**
```
R = Responsibility  (1 = single concern, 9 = god class)
P = Purity          (1 = pure function, 9 = impure I/O)
B = Boundary        (1 = internal, 9 = external API)
L = Lifecycle       (1 = transient, 9 = persistent session)

Example: (1,2,2,1) = simple pure internal utility
Example: (9,8,9,7) = complex god class with external API (DANGER)
```

---

## 3. THE 16-LEVEL SCALE (Habitat Zones)

```
Zone          Level   Name          Typical Entity
───────────────────────────────────────────────────────────
COSMOLOGICAL  L12     UNIVERSE      The software industry
              L11     DOMAIN        Healthcare, Finance, Gaming
              L10     ORGANIZATION  Company, Foundation
              L9      PLATFORM      AWS, Kubernetes, Browser
              L8      ECOSYSTEM     npm, PyPI, crates.io

SYSTEMIC      L7      SYSTEM        Microservice, Application
              L6      PACKAGE       npm package, Python module
              L5      FILE          .py, .ts, .go file
              L4      CONTAINER     Class, Struct, Module block

SEMANTIC      L3      NODE          Function, Method, Property
              L2      BLOCK         If/else block, Try/catch
              L1      STATEMENT     Assignment, Return, Import

SYNTACTIC     L0      TOKEN         Identifier, Keyword, Operator
              L-1     CHARACTER     'a', 'b', '{'
              L-2     BYTE          0x61, 0x7B
              L-3     BIT           0, 1
```

**Operational Zone:** L3-L7 (where Collider classifies)

---

## 4. THE 5 DEPENDENCY RINGS (Ω)

Rings measure **dependency depth** - how many layers of internal imports exist.

```
Ring   Name         Dependencies             Typical Contents
────────────────────────────────────────────────────────────────
R0     CORE         No internal deps         Pure utilities, constants, base types
R1     DOMAIN       Only R0                  Domain entities, value objects, core logic
R2     APPLICATION  R0-R1                    Use cases, services, orchestration
R3     ADAPTER      R0-R2                    Repositories, gateways, I/O boundaries
R4     FRAMEWORK    R0-R3 + externals        Entry points, CLI, web handlers
```

**Key principle:** Dependencies flow INWARD (R4 → R0). Ring 0 should not import Ring 1+.

```
        ┌─────────────────────────────────────┐
        │  R4: FRAMEWORK (entry points)       │
        │  ┌─────────────────────────────┐    │
        │  │  R3: ADAPTER (I/O)          │    │
        │  │  ┌─────────────────────┐    │    │
        │  │  │  R2: APPLICATION    │    │    │
        │  │  │  ┌─────────────┐    │    │    │
        │  │  │  │ R1: DOMAIN  │    │    │    │
        │  │  │  │ ┌───────┐   │    │    │    │
        │  │  │  │ │R0:CORE│   │    │    │    │
        │  │  │  │ └───────┘   │    │    │    │
        │  │  │  └─────────────┘    │    │    │
        │  │  └─────────────────────┘    │    │
        │  └─────────────────────────────┘    │
        └─────────────────────────────────────┘

        Dependency direction: ────────────────►
                              (outer to inner)
```

**See:** L1_DEFINITIONS.md §5.7 for full specification.

---

## 5. THE FOUR PHASES (Kingdoms)

### PHASE 1: DATA (The Matter)
> "What is stored"

| Family | Atoms | Locus (typical) |
|--------|-------|-----------------|
| **Bits** | BitFlag, BitMask, ParityBit, SignBit | L-3 to L0 |
| **Bytes** | ByteArray, MagicBytes, Buffer | L0 to L1 |
| **Primitives** | Boolean, Integer, Float, String, Null, Enum, **Cardinality**✱ | L1 |
| **Variables** | LocalVar, GlobalVar, Parameter, InstanceField, Constant | L1 to L3 |
| **Sets**✱ | **UniversalSet, DataMart, OperationalDataStore** | L3-L4 |

✱ = SWEBOK-aligned additions

### PHASE 2: LOGIC (The Forces)
> "What computes"

| Family | Atoms | Locus (typical) |
|--------|-------|-----------------|
| **Expressions** | LiteralExpr, BinaryExpr, CallExpr, AwaitExpr, **TraceExpr**✱ | L1 |
| **Statements** | Assignment, Declaration, ReturnStmt, ThrowStmt | L1 |
| **Control** | IfBranch, ForLoop, TryBlock, CatchClause, GuardClause | L2 |
| **Functions** | PureFunction, AsyncFunction, Lambda, Validator, Mapper | L3 |
| **Analysis**✱ | **StaticAnalyzer, SecurityAnalyzer, InductiveProof** | L3-L4 |

✱ = SWEBOK-aligned additions

### PHASE 3: ORGANIZATION (The Structure)
> "What groups"

| Family | Atoms | Locus (typical) |
|--------|-------|-----------------|
| **Aggregates** | Entity, ValueObject, DTO, Command, Query, Event, **Prototype**✱, **Metric**✱ | L3-L4 |
| **Services** | DomainService, Repository, Gateway, Adapter, Facade | L4 |
| **Modules** | FeatureModule, CoreModule, Package, Namespace, Layer, **ModuleBoundary**✱, **ArchStyle**✱ | L5-L6 |
| **Files** | SourceFile, TestFile, ConfigFile, SchemaFile, Script | L5 |
| **Documents**✱ | **RequirementsSpec, V&VPlan, TraceabilityMatrix** | L5-L6 |

✱ = SWEBOK-aligned additions

### PHASE 4: EXECUTION (The Dynamics)
> "What runs"

| Family | Atoms | Locus (typical) |
|--------|-------|-----------------|
| **Handlers** | APIHandler, EventHandler, WebhookHandler, ErrorHandler, **DesignReviewHandler**✱ | L3-L4 |
| **Workers** | CronJob, QueueWorker, BatchProcessor, StreamProcessor | L4-L7 |
| **Initializers** | MainEntry, ServerBootstrap, DIContainer, ConfigLoader | L5-L7 |
| **Probes** | HealthCheck, MetricsExporter, CircuitBreaker, FeatureFlag | L3-L4 |
| **Governance**✱ | **Certifier, RiskAnalyzer, IntegrityChecker, CybersecurityMonitor** | L4-L7 |

✱ = SWEBOK-aligned additions

---

## 6. THE 41 CANONICAL ROLES (Species) [SWEBOK-ENHANCED from 33]

Roles define **PURPOSE** - what the entity is FOR.
*8 new roles added from SWEBOK alignment: Verifier, SecurityValidator, StatisticalAnalyzer, Tracer, ProjectManager, RiskManager, Certifier, Measurer*

### Query Roles (4) - "What retrieves"
| Role | Purpose | Typical Atom |
|------|---------|--------------|
| **Query** | Data retrieval request | ORG.AGG.M |
| **Finder** | Search by criteria | LOG.FNC.M |
| **Loader** | Bulk data loading | ORG.SVC.M |
| **Getter** | Single property access | LOG.FNC.M |

### Command Roles (4) - "What changes"
| Role | Purpose | Typical Atom |
|------|---------|--------------|
| **Command** | Intent to modify state | ORG.AGG.M |
| **Creator** | Entity instantiation | LOG.FNC.M |
| **Mutator** | State modification | LOG.FNC.M |
| **Destroyer** | Entity deletion | LOG.FNC.M |

### Factory Roles (2) - "What builds"
| Role | Purpose | Typical Atom |
|------|---------|--------------|
| **Factory** | Object creation | LOG.FNC.M |
| **Builder** | Fluent construction | LOG.FNC.M |

### Storage Roles (3) - "What persists"
| Role | Purpose | Typical Atom |
|------|---------|--------------|
| **Repository** | Aggregate persistence | ORG.SVC.M |
| **Store** | State container | ORG.SVC.M |
| **Cache** | Temporary storage | ORG.SVC.M |

### Orchestration Roles (4) - "What coordinates"
| Role | Purpose | Typical Atom |
|------|---------|--------------|
| **Service** | Business logic | ORG.SVC.M |
| **Controller** | Request handling | EXE.HDL.O |
| **Manager** | Resource management | ORG.SVC.M |
| **Orchestrator** | Multi-step workflow | ORG.SVC.M |

### Validation Roles (5) - "What checks" [SWEBOK-ENHANCED]
| Role | Purpose | Typical Atom |
|------|---------|--------------|
| **Validator** | Input validation | LOG.FNC.M |
| **Verifier** | Build correctness (SWEBOK: "built right") | LOG.FNC.M |
| **Guard** | Access control | LOG.CTL.A |
| **Asserter** | Invariant checking | LOG.FNC.M |
| **SecurityValidator** | Security-specific validation | LOG.FNC.M |

### Transform Roles (4) - "What converts"
| Role | Purpose | Typical Atom |
|------|---------|--------------|
| **Transformer** | Data transformation | LOG.FNC.M |
| **Mapper** | Type conversion | LOG.FNC.M |
| **Serializer** | Object → bytes | LOG.FNC.M |
| **Parser** | Bytes → object | LOG.FNC.M |

### Event Roles (4) - "What reacts"
| Role | Purpose | Typical Atom |
|------|---------|--------------|
| **Handler** | Event processing | EXE.HDL.O |
| **Listener** | Event subscription | ORG.SVC.M |
| **Subscriber** | Message consumption | EXE.HDL.O |
| **Emitter** | Event publication | ORG.SVC.M |

### Utility Roles (5) - "What helps" [SWEBOK-ENHANCED]
| Role | Purpose | Typical Atom |
|------|---------|--------------|
| **Utility** | Stateless helpers | LOG.FNC.M |
| **Formatter** | Output formatting | LOG.FNC.M |
| **Helper** | Support functions | LOG.FNC.M |
| **StatisticalAnalyzer** | Data analysis (SWEBOK KA-QUA) | LOG.FNC.M |
| **Tracer** | History/provenance tracking (SWEBOK traceability) | LOG.FNC.M |

### Internal Roles (2) - "What manages"
| Role | Purpose | Typical Atom |
|------|---------|--------------|
| **Internal** | Private implementation | LOG.FNC.M |
| **Lifecycle** | Init/cleanup hooks | EXE.INI.O |

### Management Roles (4) - "What governs" [SWEBOK-NEW]
| Role | Purpose | Typical Atom |
|------|---------|--------------|
| **ProjectManager** | Resource/schedule coordination (SWEBOK KA-MGT) | ORG.SVC.M |
| **RiskManager** | Risk identification/mitigation (SWEBOK KA-MGT) | ORG.SVC.M |
| **Certifier** | Professional/product certification (SWEBOK KA-PRO) | EXE.PRB.O |
| **Measurer** | Metrics collection (SWEBOK KA-QUA) | EXE.PRB.O |

---

## 7. HABITAT MAP (Where Entities Live)

### By Architectural Layer

```
LAYER          LEVEL (λ)    RING (Ω)   TYPICAL RESIDENTS
──────────────────────────────────────────────────────────────────
Interface      L5-L7        R4         APIHandler, Controller, GraphQLResolver
Application    L4-L6        R2-R3      Service, Orchestrator, UseCase
Core/Domain    L3-L5        R1         Entity, ValueObject, DomainService
Infrastructure L4-L6        R3         Repository, Gateway, Adapter, Client
Test           L5-L6        R4         TestFile, Fixture, TestDouble
```

### By File Type

```
FILE PATTERN          TYPICAL ATOMS                    LEVEL   RING
──────────────────────────────────────────────────────────────────
*_controller.py       APIHandler, CommandHandler       L5      R4
*_service.py          ApplicationService, Orchestrator L5      R2
*_repository.py       Repository, Gateway              L5      R3
*_entity.py           Entity, AggregateRoot            L5      R1
*_dto.py              DTO, ViewModel                   L5      R2
*_test.py             TestFile, Fixture                L5      R4
*_config.py           ConfigFile, ConfigLoader         L5      R3
__init__.py           FeatureModule, SharedModule      L6      varies
main.py               MainEntry, ServerBootstrap       L7      R4
```

### By Naming Pattern

```
PATTERN               INFERRED ROLE      ATOM
──────────────────────────────────────────────────────────────
*Handler              Handler            EXE.HDL.O
*Controller           Controller         EXE.HDL.O
*Service              Service            ORG.SVC.M
*Repository           Repository         ORG.SVC.M
*Factory              Factory            LOG.FNC.M
*Builder              Builder            LOG.FNC.M
*Validator            Validator          LOG.FNC.M
*Mapper               Mapper             LOG.FNC.M
*DTO                  DTO                ORG.AGG.M
*Entity               Entity             ORG.AGG.M
*Event                Event              ORG.AGG.M
*Command              Command            ORG.AGG.M
*Query                Query              ORG.AGG.M
get*                  Getter             LOG.FNC.M
set*                  Setter             LOG.FNC.M
is*/has*/can*         Predicate          LOG.FNC.M
validate*             Validator          LOG.FNC.M
transform*/convert*   Mapper             LOG.FNC.M
create*/build*        Factory            LOG.FNC.M
handle*               EventHandler       EXE.HDL.O
on*/use*              Hook               LOG.FNC.M
```

---

## 8. CONTAINMENT RULES

### What Contains What

```
L7 (SYSTEM)    contains   L6 (PACKAGE)
L6 (PACKAGE)   contains   L5 (FILE)
L5 (FILE)      contains   L4 (CONTAINER)
L4 (CONTAINER) contains   L3 (NODE)
L3 (NODE)      contains   L2 (BLOCK)
L2 (BLOCK)     contains   L1 (STATEMENT)
L1 (STATEMENT) contains   L0 (TOKEN)
```

### Cross-Level References

```
Entity at L_a can reference Entity at L_b when:
  - Same container (sibling)
  - Parent container (import from parent)
  - Child container (delegate to child)
  - Distant container (explicit import path)

Coupling strength:
  |L_a - L_b| = 0  → Tight (same level)
  |L_a - L_b| = 1  → Normal (adjacent)
  |L_a - L_b| > 2  → Loose (far levels)
```

---

## 9. COMPLETE ATOM INVENTORY [SWEBOK-ENHANCED]

### Count by Phase

| Phase | Families | Atoms (Original) | Atoms (+ SWEBOK) |
|-------|----------|------------------|------------------|
| DATA | 4→5 | 26 | 30 (+4) |
| LOGIC | 4→5 | 61 | 65 (+4) |
| ORGANIZATION | 4→5 | 45 | 52 (+7) |
| EXECUTION | 4→5 | 35 | 40 (+5) |
| **TOTAL** | **16→20** | **167** | **187 (+20)** |

*20 new atoms added from SWEBOK alignment*

### Family Codes

```
DAT.BIT.A   Data > Bits (4 atoms)
DAT.BYT.A   Data > Bytes (4 atoms)
DAT.PRM.A   Data > Primitives (10 atoms)
DAT.VAR.A   Data > Variables (8 atoms)

LOG.EXP.A   Logic > Expressions (15 atoms)
LOG.STM.A   Logic > Statements (10 atoms)
LOG.CTL.A   Logic > Control (14 atoms)
LOG.FNC.M   Logic > Functions (22 atoms)

ORG.AGG.M   Organization > Aggregates (16 atoms)
ORG.SVC.M   Organization > Services (12 atoms)
ORG.MOD.O   Organization > Modules (9 atoms)
ORG.FIL.O   Organization > Files (8 atoms)

EXE.HDL.O   Execution > Handlers (9 atoms)
EXE.WRK.O   Execution > Workers (8 atoms)
EXE.INI.O   Execution > Initializers (8 atoms)
EXE.PRB.O   Execution > Probes (10 atoms)
```

---

## 10. QUICK REFERENCE CARD [SWEBOK-ALIGNED]

```
┌────────────────────────────────────────────────────────────┐
│              CODE ZOO QUICK REF (SWEBOK V4)                │
├────────────────────────────────────────────────────────────┤
│ PHASES:     DATA → LOGIC → ORGANIZATION → EXECUTION        │
│ FAMILIES:   20 (5 per phase) [was 16]                      │
│ ATOMS:      187 canonical types [was 167, +20 SWEBOK]      │
│ ROLES:      41 canonical purposes [was 33, +8 SWEBOK]      │
│ LEVELS:     L-3 (Bit) to L12 (Universe)                   │
│ RINGS:      0-4 (CORE → DOMAIN → APP → ADAPTER → FRAMEWORK)│
├────────────────────────────────────────────────────────────┤
│ LOCUS(atom) = ⟨λ, Ω, τ, α, R⟩                             │
│                                                            │
│   λ (Level)  = L-3 to L12 (scale position)                │
│   Ω (Ring)   = 0-4 (dependency depth)                     │
│   τ (Tier)   = T0, T1, T2 (abstraction tier)              │
│   α (Role)   = 41 roles (functional purpose)              │
│   R (RPBL)   = 4-tuple character metric                   │
├────────────────────────────────────────────────────────────┤
│ OPERATIONAL ZONE: L3-L7 (Node to System)                   │
│ COLLIDER CLASSIFIES: This zone                             │
│ SWEBOK ALIGNMENT: 40 matches, 24 gaps, 11 conflicts       │
└────────────────────────────────────────────────────────────┘
```

---

## 11. SWEBOK V4 ALIGNMENT

This taxonomy was validated against IEEE SWEBOK V4 (2024) using Cerebras AI (3000 t/s).

### Alignment Summary

| Metric | Count | Examples |
|--------|-------|----------|
| **Matches** | 40 | Functional Req → Query, Service-oriented → Orchestrator |
| **Gaps Filled** | 24 | Added Prototype, Metric, StaticAnalyzer, Certifier |
| **Enhancements** | 23 | Added Verifier role, SecurityValidator, Tracer |
| **Conflicts Resolved** | 11 | Verification ≠ Validation, Design reviews anytime |

### SWEBOK Knowledge Areas → CODE_ZOO Mapping

| SWEBOK KA | Primary Phase | Primary Roles |
|-----------|---------------|---------------|
| Software Requirements | ORG | Query, Command, Validator |
| Software Architecture | ORG | Service, Orchestrator |
| Software Design | ORG+LOG | Factory, Builder, Transformer |
| Software Construction | LOG | Creator, Mutator, Helper |
| Software Testing | EXE | Validator, Asserter, Verifier |
| Software Operations | EXE | Handler, Manager |
| Software Maintenance | ALL | Mutator, Transformer |
| Software Config Mgmt | ORG | Loader, Store |
| Software Eng Mgmt | ORG | ProjectManager, RiskManager |
| Software Eng Process | EXE | Orchestrator, Controller |
| Software Quality | EXE | Validator, Measurer, StatisticalAnalyzer |
| Software Security | LOG+EXE | Guard, SecurityValidator |
| Professional Practice | EXE | Certifier |
| Software Economics | ORG | (cost modeling, ROI) |
| Computing Foundations | DAT+LOG | Primitives, Algorithms |
| Mathematical Foundations | DAT | Sets, Proofs |
| Engineering Foundations | ALL | (cross-cutting) |

### Key Additions from SWEBOK

**New Atoms:**
- `ORG.AGG.Prototype` - Validation artifacts (SWEBOK KA-REQ)
- `ORG.AGG.Metric` - Software integrity level (SWEBOK KA-QUA)
- `ORG.MOD.ModuleBoundary` - Scope definition (SWEBOK KA-REQ)
- `ORG.MOD.ArchStyle` - Architecture patterns (SWEBOK KA-ARC)
- `LOG.FNC.StaticAnalyzer` - Analysis without execution (SWEBOK KA-QUA)
- `LOG.FNC.SecurityAnalyzer` - Vulnerability detection (SWEBOK KA-SEC)
- `EXE.GOV.Certifier` - Professional certification (SWEBOK KA-PRO)
- `EXE.GOV.RiskAnalyzer` - Risk management (SWEBOK KA-MGT)

**New Roles:**
- `Verifier` - Ensures product built correctly (distinct from Validator)
- `SecurityValidator` - Security-specific validation
- `StatisticalAnalyzer` - Data analysis for quality
- `Tracer` - Traceability and provenance
- `ProjectManager` - Project coordination
- `RiskManager` - Risk identification
- `Certifier` - Certification processes
- `Measurer` - Metrics collection

### SWEBOK Conflicts Resolved

| Conflict | Resolution |
|----------|------------|
| Functions = "pure" vs "functional requirements" | Both valid: pure (code) vs functional (requirements) |
| Design reviews at end only | SWEBOK correct: design reviews can happen anytime |
| Validator = Verifier | Split: Validator (right product) vs Verifier (product right) |
| No cybersecurity | Added: SecurityAnalyzer, CybersecurityMonitor |
| No reliability concept | Added: IntegrityChecker, reliability as RPBL metric |

**Source:** `wave/data/intel/zoo_comparisons/swebok_comparison.yaml`

---

## 12. SEE ALSO

| Document | Purpose |
|----------|---------|
| `GLOSSARY.md` | Full terminology reference |
| `atoms.json` | Machine-readable atom definitions |
| `CONTAINMENT_TOPOLOGY.md` | Spatial structure theory |
| `L1_DEFINITIONS.md` | Scale hierarchy definitions |
| `semantic_finder.py` | Role-based classification in code |
| **SWEBOK References** | |
| `swebok-v4.pdf` | IEEE SWEBOK V4 (2024) original |
| `swebok_comparison.yaml` | Cerebras AI comparison results |
| `SWEBOK_CODE_ZOO_MAP.md` | Detailed KA → Atom mapping |
| `SWEBOK_QUICK_REFERENCE.md` | Practitioner cheat sheet |

---

*Created: 2026-01-31*
*Updated: 2026-01-31 (SWEBOK V4 alignment via Cerebras AI)*
*Source: GLOSSARY.md, atoms.json, CONTAINMENT_TOPOLOGY.md, SWEBOK V4*
*Classification: Standard Model of Code - Theory*
*SWEBOK Alignment: 40 matches, 24 gaps addressed, 23 enhancements, 11 conflicts resolved*
