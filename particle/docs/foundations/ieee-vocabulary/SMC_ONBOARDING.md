# SMC Onboarding: The Complete Theory

> **Purpose:** Comprehensive introduction to the Standard Model of Code
> **Prerequisite:** Understanding of IEEE SEVOCAB (see STANDARDS_PRIORITY_MATRIX.md)
> **Date:** 2026-01-31
> **Status:** DEFINITIVE

---

## What SMC Is (And Is Not)

### SMC IS:

1. **A comprehensive theory of code** treating software as physics
2. **Covers ALL aspects of code life:**
   - Static structure (parsing, AST, dependencies)
   - **Runtime behavior** (execution, data flow, control flow)
   - **Operational concerns** (deployment, monitoring, change management)
   - Human understanding (semantics, documentation, intent)
3. **Based on established mathematics:**
   - Set theory, graph theory, category theory
   - Information theory (Shannon, Tononi)
   - Dynamical systems (Friston's Free Energy Principle)
   - Semiotics (Peirce's triadic sign theory)

### SMC IS NOT:

- "Just a static analysis tool"
- "Just another linter"
- "AST parsing with pretty visualizations"

The implementation (Collider) is partial. The **theory** is comprehensive.

---

## The Four-Layer Theory Stack

```
┌───────────────────────────────────────────────────────────────────────────┐
│  L3: APPLICATIONS - How we MEASURE (Q-scores, Health, Pipeline)           │
├───────────────────────────────────────────────────────────────────────────┤
│  L2: LAWS - How things BEHAVE (Purpose laws, Flow laws, Drift equations)  │
├───────────────────────────────────────────────────────────────────────────┤
│  L1: DEFINITIONS - What EXISTS (Atoms, Roles, Dimensions, LOCUS)          │
├───────────────────────────────────────────────────────────────────────────┤
│  L0: AXIOMS - What MUST be true (MECE partition, Purpose field, Holarchy) │
└───────────────────────────────────────────────────────────────────────────┘
```

**Key principle:** Each layer builds on the one below. You cannot understand L2 without L1, and L1 without L0.

---

## The Three Realms (Trinity Principle)

| Realm | Directory | Purpose | Pipeline | Nature |
|-------|-----------|---------|----------|--------|
| **PARTICLE** | particle/ | Analyze structure | Collider (28 stages) | Deterministic |
| **WAVE** | wave/ | Understand semantics | Refinery (4 stages) | Probabilistic |
| **OBSERVER** | .agent/ | Coordinate actions | Autopilot/Wire/Watcher | Reactive |

**Metaphors:**
- PARTICLE = Body (physical measurement, static analysis)
- WAVE = Brain (conceptual understanding, AI reasoning)
- OBSERVER = Governance (meta-coordination, operational monitoring)

---

## Critical Axiom: The Four Flow Substances (E2)

**This is what distinguishes SMC from "static analysis":**

```
E2. Flow Resistance

R(path) = Σ obstacles along path

Four flow substances:
1. Static flow    - Dependencies, imports, calls (what Collider analyzes NOW)
2. RUNTIME flow   - Data flow, control flow, execution paths
3. CHANGE flow    - How easily changes propagate, deployment, refactoring
4. Human flow     - How easily understanding propagates

Refactoring = reducing R
Technical debt = accumulated R
```

**Implication:** SMC theory explicitly requires understanding runtime and deployment, not just static structure. The current Collider implementation handles flow #1. Flows #2-4 are theory-complete but implementation-partial.

---

## Critical Axiom: The Three Observers (G1)

**Complete observability requires ALL THREE:**

```
G1. Observability Completeness

COMPLETE_OBSERVABILITY(S) ⟺
  ∃ structural_observer : P → Manifest        ∧  [what EXISTS]
  ∃ operational_observer : Pipeline → Metrics  ∧  [what HAPPENS]
  ∃ generative_observer : Dialogue → Trace        [what is CREATED]
```

| Observer | What It Sees | SMC Component | ITIL Vocabulary |
|----------|-------------|---------------|-----------------|
| **Structural** | Code structure, files, schemas | Collider | (not applicable) |
| **Operational** | Runtime, performance, incidents | (partial) | ITIL core vocab |
| **Generative** | AI sessions, commits, evolution | .agent/ | Change management |

**Key insight:** Without the OPERATIONAL observer, we cannot understand code fully. This is why ITIL vocabulary is P1 priority for SMC - it provides the language for Axiom G1.

---

## The -ome Partition (Lawvere's Theorem)

```
PROJECTOME (P) = all project artifacts

P = C ⊔ X                    (disjoint union)
C ∩ X = ∅                    (mutually exclusive)
C ∪ X = P                    (collectively exhaustive)

WHERE:
  C = CODOME (executable artifacts)
  X = CONTEXTOME (non-executable artifacts)
```

**Mathematical necessity (not engineering convenience):**

Lawvere's Fixed-Point Theorem (1969) proves that **code cannot fully specify its own semantics**. Meaning MUST come from an external source. This is why CONTEXTOME (documentation, specs, research) is mathematically necessary, not optional.

---

## The 16-Level Scale (Holarchy)

| Level | Name | Zone | What It Contains |
|-------|------|------|------------------|
| **L12** | UNIVERSE | COSMOLOGICAL | All software ever written |
| **L11** | DOMAIN | COSMOLOGICAL | Business/problem domain |
| **L10** | ORGANIZATION | COSMOLOGICAL | Company repository collection |
| **L9** | PLATFORM | COSMOLOGICAL | Monorepo or platform |
| **L8** | ECOSYSTEM | COSMOLOGICAL | External boundaries, APIs |
| **L7** | SYSTEM | SYSTEMIC | Major subsystem |
| **L6** | PACKAGE | SYSTEMIC | Directory or language package |
| **L5** | FILE | SYSTEMIC | Single source file |
| **L4** | CONTAINER | SYSTEMIC | Class, struct, enum |
| **L3** | NODE | SEMANTIC | Function or method (THE atom) |
| **L2** | BLOCK | SEMANTIC | Control flow structure |
| **L1** | STATEMENT | SEMANTIC | Single instruction |
| **L0** | TOKEN | SYNTACTIC | Keyword, identifier, literal |
| **L-1** | CHARACTER | PHYSICAL | UTF-8 character |
| **L-2** | BYTE | PHYSICAL | Raw byte |
| **L-3** | BIT | PHYSICAL | Binary digit |

---

## LOCUS: The Topological Address

Every code entity has a unique position in theory-space:

```
LOCUS(atom) = ⟨λ, Ω, τ, α, R⟩

WHERE:
  λ (Level)  = L-3 to L12 (hierarchical scale position)
  Ω (Ring)   = 0-4 (dependency depth from core)
  τ (Tier)   = T0, T1, T2 (abstraction tier)
  α (Role)   = 33 canonical roles (functional purpose)
  R (RPBL)   = 4-tuple (Responsibility, Purity, Boundary, Lifecycle)
```

**Example:**
```
getUserById() → LOCUS = ⟨L3, R1, T1, Query, (1,2,2,1)⟩

Meaning:
  L3    = NODE level (function)
  R1    = DOMAIN ring (depends only on core)
  T1    = Standard library patterns tier
  Query = Functional role (read without mutation)
  (1,2,2,1) = RPBL character
```

---

## Purpose Emergence (pi1 → pi4)

Purpose emerges hierarchically through composition:

```
pi4 (System)    = f(file's pi3 distribution)      "DataAccess", "TestSuite"
     ↑
pi3 (Organelle) = f(class's pi2 distribution)     "Repository", "Processor"
     ↑
pi2 (Molecular) = f(effect, boundary, topology)   "Compute", "Retrieve", "Transform"
     ↑
pi1 (Atomic)    = Role from classifier            "Service", "Repository", "Controller"
```

**Key principle:** Purpose is RELATIONAL, not intrinsic. A function's purpose emerges from its role in the containing class, which emerges from its role in the file, which emerges from its role in the system.

---

## Concordance States (The 2x2 Grid)

Every code-doc pair exists in one of four states:

| State | Code? | Docs? | Purposes Aligned? |
|-------|-------|-------|-------------------|
| **CONCORDANT** | Yes | Yes | Yes |
| **DISCORDANT** | Yes | Yes | No (drift) |
| **UNVOICED** | Yes | No | N/A (undocumented) |
| **UNREALIZED** | No | Yes | N/A (vaporware) |

**Health target:** > 80% CONCORDANT for production systems.

---

## Technical Debt as Drift Integral

```
Δ𝒫(t) = 𝒫_human(t) - 𝒫_code(t)         (drift at time t)

Debt(T) = ∫[t_commit to T] |d𝒫_human/dt| dt

Code crystallizes intent. Human understanding evolves.
Drift accumulates between commits.
```

**Implication:** Frequent small commits minimize debt. Large infrequent commits allow unbounded drift.

---

## Standards Foundation

SMC builds ON TOP of established standards vocabulary:

| Standard | What It Provides | SMC Usage |
|----------|------------------|-----------|
| **IEEE SEVOCAB** | 5,401 term definitions | THE foundation - every term check starts here |
| **INCOSE** | Systems thinking philosophy | Emergence, holons, physical/conceptual systems |
| **SEBoK** | 435 SE body of knowledge terms | Cross-reference for completeness |
| **ITIL** | Operational vocabulary | **Axiom G1 (Operational Observer)** |
| **OMG** | Formal notation (UML/OCL) | Role formalization |
| **CMMI** | Process maturity | Ring (Ω) concept |

**The Rule:**
> Before creating ANY SMC term:
> 1. Check IEEE SEVOCAB first
> 2. Check INCOSE second
> 3. Check SEBoK third
> 4. If found: USE the standard term
> 5. If not found: Document as SMC extension with justification

---

## Key SMC Extensions (Beyond Standards)

| SMC Concept | Status | What It Extends |
|-------------|--------|-----------------|
| **LOCUS** | NOVEL | Topological coordinate system |
| **CODOME** | EXTENDS IEEE | "source code" + executable artifacts |
| **CONTEXTOME** | EXTENDS INCOSE | "conceptual system" + all non-executable |
| **PROJECTOME** | EXTENDS IEEE | "project" as total artifact set |
| **Ring (Ω)** | EXTENDS IEEE | "layer" with formal 0-4 scale |
| **Tier (τ)** | EXTENDS IEEE | "tier" as abstraction level |
| **Level (λ)** | EXTENDS IEEE | "level" with 16-level scale |
| **RPBL** | NOVEL | 4D character metric |
| **Holon** | NOVEL (from Koestler) | Self-contained autonomous unit |
| **PARTICLE/WAVE/OBSERVER** | NOVEL | Physics metaphor for realms |
| **Purpose Field (𝒫)** | NOVEL | Vector field over nodes |
| **Concordance** | NOVEL | Purpose-aligned regions |

---

## Implementation vs Theory Status

| Component | Theory Status | Implementation Status |
|-----------|---------------|----------------------|
| Static flow analysis | Complete | Collider (28 stages) |
| Runtime flow analysis | Complete | Partial (Stage 2.11) |
| Change flow analysis | Complete | Not yet implemented |
| Human flow analysis | Complete | Refinery (AI reasoning) |
| Structural observer | Complete | Collider |
| Operational observer | Complete | **GAP - needs ITIL vocab** |
| Generative observer | Complete | .agent/ (partial) |
| Purpose emergence | Complete | Stages 3-3.7 |
| Drift measurement | Complete | Conceptual only |
| Concordance scoring | Complete | Prototype |

### Dynamic Observers Implementation Plan (v2.0)

A comprehensive 75-task implementation plan exists to close these gaps:

**Key documents:**
- **Implementation Plan:** `docs/specs/DYNAMIC_OBSERVERS_IMPLEMENTATION_PLAN.md`
- **Task Registry:** `.agent/deck/DYNAMIC_OBSERVERS_REGISTRY.yaml`
- **Research Prompt:** `docs/research/prompts/SONAR_PRO_IMPLEMENTATION_GAPS.md`

**New packages to be created:**

| Package | Purpose | Axiom |
|---------|---------|-------|
| `src/dynamics/` | Runtime flow ingestion | E2 (Runtime Flow) |
| `src/evolution/` | Git mining, temporal coupling | E2 (Change Flow) |
| `src/social/` | Authorship, truck factor | E2 (Human Flow) |
| `src/operational/` | DORA metrics, incidents | G1 (Operational Observer) |
| `src/observers/` | Unified observer framework | G1 (Complete Observability) |

**Toggle architecture:** All new observers start DISABLED by default via `config/observers_config.yaml`, enabling gradual rollout without breaking existing functionality.

---

## Learning Path

### Week 1: Foundations
- [ ] Master IEEE SEVOCAB lookup (`python3 lookup.py "term"`)
- [ ] Read L0_AXIOMS.md completely
- [ ] Understand the MECE partition and Lawvere's proof

### Week 2: Definitions
- [ ] Read L1_DEFINITIONS.md completely
- [ ] Map each SMC term to IEEE foundation
- [ ] Understand LOCUS coordinate system

### Week 3: Laws
- [ ] Read L2_LAWS.md completely
- [ ] Understand purpose emergence (pi1-pi4)
- [ ] Understand drift and technical debt formulas

### Week 4: Applications
- [ ] Read L3_APPLICATIONS.md (STANDARD_MODEL_THEORY_COMPLETE.md)
- [ ] Run Collider on a test repo
- [ ] Interpret Q-scores and health metrics

### Week 5+: Operations
- [ ] Study ITIL vocabulary for Axiom G1
- [ ] Understand change flow and deployment
- [ ] Contribute to operational observer implementation

---

## Quick Reference

**Key files:**
- `docs/theory/L0_AXIOMS.md` - Bedrock truths
- `docs/theory/L1_DEFINITIONS.md` - All concepts defined
- `docs/theory/L2_LAWS.md` - Behavioral equations
- `docs/theory/STANDARD_MODEL_THEORY_COMPLETE.md` - Everything unified

**Lookup tools:**
```bash
# IEEE lookup
python3 lookup.py "validation"

# Multi-standard comparison
python3 unified_lookup.py --compare "system"

# Check if SMC term is novel
python3 unified_lookup.py --smc-check "LOCUS"
```

**Collider commands:**
```bash
./collider full /path/to/repo --output /tmp/analysis
./collider grade /path/to/repo --json
```

---

## The Core Insight

> "Code is not just text to parse. Code is a living system with:
> - **Structure** (what it IS - static analysis)
> - **Behavior** (what it DOES - runtime flow)
> - **Purpose** (what it's FOR - semantic intent)
> - **Evolution** (how it CHANGES - drift and debt)
>
> SMC provides the mathematics to measure all four."

---

*SMC builds ON TOP of standards, not beside them.*
*The theory is comprehensive. The implementation is ongoing.*
