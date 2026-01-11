# Standard Model of Code: Foundational Theories Integration

> **Purpose**: Document the intellectual ancestors of the Standard Model of Code, what has been integrated (often by accident), what is missing, and how to improve the synthesis.

---

# Table of Contents

1. [Overview: The Synthesis](#overview-the-synthesis)
2. [Koestler's Holons](#1-koestlers-holons)
3. [Popper's Three Worlds](#2-poppers-three-worlds)
4. [Ranganathan's Faceted Classification](#3-ranganathans-faceted-classification)
5. [Shannon's Information Theory](#4-shannons-information-theory)
6. [Clean Architecture](#5-clean-architecture)
7. [Domain-Driven Design](#6-domain-driven-design)
8. [Dijkstra's Abstraction Layers](#7-dijkstras-abstraction-layers)
9. [Synthesis Gaps](#synthesis-gaps)
10. [For AI: Why This Matters](#for-ai-why-this-matters)

---

# Overview: The Synthesis

The Standard Model of Code synthesizes 7+ foundational theories into a unified framework:

```
                    STANDARD MODEL OF CODE
                           ↑
    ╔══════════════════════════════════════════════════════╗
    ║                                                      ║
    ║  KOESTLER ─────→ Holons, Holarchy, L3-L12 levels     ║
    ║  POPPER ───────→ 3 Planes (Physical/Virtual/Semantic)║
    ║  RANGANATHAN ──→ 8 Dimensions as Facets              ║
    ║  SHANNON ──────→ Transformation (Input→Output)       ║
    ║  MARTIN ───────→ Layer Dimension (Clean Arch)        ║
    ║  EVANS ────────→ 33 Roles (DDD tactical patterns)   ║
    ║  DIJKSTRA ─────→ Abstraction levels concept          ║
    ║                                                      ║
    ╚══════════════════════════════════════════════════════╝
```

---

# 1. Koestler's Holons

## The Theory (Ghost in the Machine, 1967)

**Definition**: A *holon* is something that is simultaneously a WHOLE in itself and a PART of a larger whole.

**Key Properties**:
| Property | Description |
|----------|-------------|
| **Janus-faced** | Every holon looks UP (to the whole it belongs to) and DOWN (to its parts) |
| **Self-assertive tendency** | The drive to maintain identity and autonomy |
| **Integrative tendency** | The drive to belong and contribute to the larger whole |
| **Holarchy** | Holons form *holarchies* (not hierarchies) - nested wholes within wholes |

**The Crucial Insight**: A cell is a complete whole, but also a part of an organ. An organ is a complete whole, but also part of an organism. This pattern repeats infinitely.

```
UNIVERSE (L12)
  └── DOMAIN (L11) ──────────────────────────── holon
       └── ORGANIZATION (L10) ──────────────── holon
            └── SYSTEM (L7) ────────────────── holon
                 └── PACKAGE (L6) ──────────── holon
                      └── CLASS (L4) ────────── holon
                           └── FUNCTION (L3) ── holon (THE ATOM)
                                └── BLOCK (L2) ─ holon
```

## What Standard Model Already Integrates ✅

| Koestler | Standard Model | How |
|----------|----------------|-----|
| Holon as whole/part | 16 Levels (L-3 to L12) | Each level is both container and contained |
| Janus-faced property | BOUNDARY dimension (D4) | Internal vs External facing |
| Self-assertive | STATE dimension (D5) | Maintaining identity |
| Integrative | ROLE dimension (D3) | Purpose in larger context |
| Holarchy | Containment edges | `contains` / `is_part_of` |

## What's Missing ⚠️

| Gap | Description | Suggested Addition |
|-----|-------------|-------------------|
| **Tension dynamics** | Koestler emphasized the *conflict* between self-assertive and integrative tendencies | Add "Coupling Tension" metric |
| **Emergent properties** | Properties that emerge at higher levels, unpredictable from lower levels | Add "Emergence" classification |
| **Pathological holarchies** | When holons become too autonomous (cancer) or too subservient | Add anti-pattern detection for "God Classes" (cancer) vs "Anemic Models" (subservience) |

---

# 2. Popper's Three Worlds

## The Theory (Objective Knowledge, 1972)

**Definition**: Reality consists of THREE distinct but interacting worlds:

| World | Contents | Examples |
|-------|----------|----------|
| **World 1** | Physical objects and states | Bytes on disk, electrons, paper |
| **World 2** | Mental states, subjective experiences | Programmer's understanding, intentions |
| **World 3** | Abstract objects, objective knowledge | Theories, programs, problems, arguments |

**The Crucial Insight**: World 3 objects are REAL even though they're abstract. A theorem exists independently of anyone thinking about it. It has causal power - it can change World 1 through World 2.

```
WORLD 3 (Abstract)
    │
    │ interpretation
    ▼
WORLD 2 (Mental) ←───────── Programmer understands the code
    │
    │ action
    ▼
WORLD 1 (Physical) ←──────── Programmer types, bytes written to disk
```

## What Standard Model Already Integrates ✅

| Popper | Standard Model | How |
|--------|----------------|-----|
| World 1 | P1 PHYSICAL plane | Bytes, characters, storage |
| World 2 | *Not directly modeled* | Gap! |
| World 3 | P3 SEMANTIC plane | Meaning, purpose, intent |
| World 1→3 flow | P1→P2→P3 encoding/interpretation | Same flow structure |

**Note**: The Standard Model uses P2 VIRTUAL (symbols, AST) which is between World 1 and World 3.

## What's Missing ⚠️

| Gap | Description | Suggested Addition |
|-----|-------------|-------------------|
| **World 2 (Mental)** | The programmer's understanding is not modeled | Could add DOCUMENTATION lens or INTENT dimension |
| **Autonomy of World 3** | Programs can have properties their creators don't know about (emergent bugs, undiscovered optimizations) | Add "Discovered vs Intended" properties |
| **Causal interaction** | How World 3 (abstract program) affects World 1 (execution) | Already modeled via EXECUTION phase |

---

# 3. Ranganathan's Faceted Classification

## The Theory (Colon Classification, 1933)

**Definition**: Instead of putting things in pre-defined boxes (enumerative classification), analyze each entity along INDEPENDENT FACETS (dimensions) that can be combined freely.

**PMEST Formula** (Five Fundamental Facets):
| Facet | Question | Examples |
|-------|----------|----------|
| **P**ersonality | What is the core entity? | The book, the disease, the function |
| **M**atter | What is it made of? | Material, medium, language |
| **E**nergy | What action/operation? | Analysis, synthesis, treatment |
| **S**pace | Where? | Location, scope, context |
| **T**ime | When? | Period, lifecycle phase |

**The Crucial Insight**: Facets are ORTHOGONAL - you can combine any P with any M with any E without explosion. A book about "Physics + English language + Teaching + United States + 2020s" is synthesized, not enumerated.

**Example - Colon Notation**:
```
O:51;4:f.44'N5 = 
  O (Literature) : 51 (English) ; 4 (Drama) : f (Shakespeare) . 44 (Hamlet) 'N5 (1960s criticism)
```

## What Standard Model Already Integrates ✅

| Ranganathan | Standard Model | How |
|-------------|----------------|-----|
| Facets as independent axes | 8 DIMENSIONS (D1-D8) | Each dimension is orthogonal |
| PMEST Personality | D1 WHAT (Type) | Core entity type |
| PMEST Matter | Not explicitly mapped | Gap - could be "language"? |
| PMEST Energy | D3 ROLE, D6 EFFECT | What it does, side effects |
| PMEST Space | D2 LAYER, D4 BOUNDARY | Architectural location |
| PMEST Time | D7 LIFECYCLE | Create/Use/Destroy |
| Synthesis vs enumeration | 8D manifold | 200 atoms × 5 layers × 33 roles × ... |

## What's Missing ⚠️

| Gap | Description | Suggested Addition |
|-----|-------------|-------------------|
| **Explicit PMEST mapping** | The dimensions don't perfectly align with PMEST | Consider renaming or adding facets |
| **Citation order** | Ranganathan defined citation ORDER (PMEST) for notation | Define canonical dimension ordering for IDs |
| **Matter facet** | The "material/medium" aspect is weak | Add LANGUAGE or PLATFORM dimension? |
| **Colon notation** | No Standard Model notation system | Create `τ` (tau) notation for particles |

---

# 4. Shannon's Information Theory

## The Theory (Mathematical Theory of Communication, 1948)

**Definition**: Information is the reduction of uncertainty. Communication has:
- **Source** → produces message
- **Encoder** → converts to signal
- **Channel** → transmits (with noise)
- **Decoder** → recovers message
- **Destination** → receives

**Key Concepts**:
| Concept | Definition | In Code |
|---------|------------|---------|
| **Entropy** | Measure of uncertainty/information content | Code complexity |
| **Redundancy** | Extra bits for error correction | Defensive coding, assertions |
| **Channel capacity** | Maximum information rate | API bandwidth limits |
| **Noise** | Corruption in transmission | Bugs, misunderstanding |

**The IPO Model** (Input → Process → Output):
```
INPUT ──→ TRANSFORMATION ──→ OUTPUT
  │              │              │
parameters    algorithm      return value
request       business logic  response
data          function        result
```

## What Standard Model Already Integrates ✅

| Shannon | Standard Model | How |
|---------|----------------|-----|
| IPO model | R6 TRANSFORMATION lens | Input → Output as core question |
| IPO at all scales | Fractal self-similarity | Gateway→Logic→Persistence pattern |
| Entropy | Not directly modeled | Gap! |
| Encoding/Decoding | P1→P2→P3 planes | Same structure |

## What's Missing ⚠️

| Gap | Description | Suggested Addition |
|-----|-------------|-------------------|
| **Entropy dimension** | No measure of information density/complexity | Add COMPLEXITY or ENTROPY metric |
| **Noise modeling** | How bugs/errors propagate | Add to TRUST dimension calculation |
| **Channel concept** | Interfaces as "channels" with capacity | Enrich BOUNDARY dimension |
| **Redundancy** | Defensive coding, assertions | Add to VALIDATION role family |

---

# 5. Clean Architecture

## The Theory (Robert C. Martin, 2012)

**Definition**: Software architecture should be organized in concentric circles where dependencies ONLY point INWARD.

**The Layers**:
```
         ┌─────────────────────────────────────────┐
         │        FRAMEWORKS & DRIVERS             │  ← Outermost
         │   ┌─────────────────────────────────┐   │
         │   │    INTERFACE ADAPTERS           │   │
         │   │   ┌─────────────────────────┐   │   │
         │   │   │     USE CASES           │   │   │
         │   │   │   ┌─────────────────┐   │   │   │
         │   │   │   │   ENTITIES      │   │   │   │  ← Innermost (Core)
         │   │   │   └─────────────────┘   │   │   │
         │   │   └─────────────────────────┘   │   │
         │   └─────────────────────────────────┘   │
         └─────────────────────────────────────────┘
```

**The Dependency Rule**: Source code dependencies can ONLY point INWARD. Inner circles know nothing about outer circles.

| Layer | Standard Model | Purpose |
|-------|----------------|---------|
| Entities | CORE | Business rules, domain logic |
| Use Cases | APPLICATION | Application-specific business rules |
| Interface Adapters | INTERFACE | Controllers, presenters, gateways |
| Frameworks | INFRASTRUCTURE | DB, web, devices |
| (Test) | TEST | Verification layer |

## What Standard Model Already Integrates ✅

| Clean Architecture | Standard Model | How |
|--------------------|----------------|-----|
| 4+1 layers | D2 LAYER dimension | Interface/Application/Core/Infrastructure/Test |
| Dependency Rule | Dependency edges | `imports`, `uses` - could validate direction |
| Separation of concerns | ROLE dimension | Roles map to layer responsibilities |
| Plugin architecture | BOUNDARY dimension | I-O boundaries |

## What's Missing ⚠️

| Gap | Description | Suggested Addition |
|-----|-------------|-------------------|
| **Dependency direction validation** | The "inward only" rule isn't enforced | Add LAYER VIOLATION antimatter law |
| **Concentric visualization** | Current model is more "stacked" than "concentric" | Add alternative view |
| **Screaming architecture** | Top-level folders should scream the use case | Add DOMAIN_ALIGNMENT metric |

---

# 6. Domain-Driven Design

## The Theory (Eric Evans, 2003)

**Definition**: Software design should be driven by the DOMAIN (business reality), not by technical concerns.

**Strategic Patterns**:
| Pattern | Description | In Standard Model |
|---------|-------------|-------------------|
| **Bounded Context** | Explicit boundary around a domain model | L6 Package / L7 System |
| **Ubiquitous Language** | Shared vocabulary between devs and domain experts | Naming patterns |
| **Context Map** | How bounded contexts relate | Cross-system edges |
| **Core Domain** | The competitive advantage | Priority/importance metric |

**Tactical Patterns (Building Blocks)**:
| Pattern | Description | Standard Model Role |
|---------|-------------|-------------------|
| **Entity** | Has identity, mutable | Stateful + Identity |
| **Value Object** | No identity, immutable | Stateless + No Identity |
| **Aggregate** | Consistency boundary | Container with invariants |
| **Repository** | Collection-like persistence | REPOSITORY role |
| **Service** | Stateless domain operation | SERVICE role |
| **Factory** | Complex object creation | FACTORY role |
| **Domain Event** | Something that happened | HANDLER/LISTENER roles |

## What Standard Model Already Integrates ✅

| DDD | Standard Model | How |
|-----|----------------|-----|
| Entity/Value Object | D5 STATE (Stateful/Stateless) | Direct mapping |
| Repository | REPOSITORY role | Direct mapping |
| Service | SERVICE role | Direct mapping |
| Factory | FACTORY role | Direct mapping |
| Event Handler | HANDLER/LISTENER roles | Direct mapping |
| Aggregate | L4 CONTAINER + invariants | Partial |

## What's Missing ⚠️

| Gap | Description | Suggested Addition |
|-----|-------------|-------------------|
| **Aggregate root detection** | Which entity is the root? | Add AGGREGATE_ROOT property |
| **Bounded Context** | Not explicitly modeled at L6-L7 | Add CONTEXT_BOUNDARY property |
| **Ubiquitous Language** | Naming alignment not measured | Add DOMAIN_NAMING validation |
| **Invariants** | Business rules not explicitly tracked | Add CONSTRAINT/INVARIANT concept |

---

# 7. Dijkstra's Abstraction Layers

## The Theory (THE Multiprogramming System, 1968)

**Definition**: Complex systems should be built in LAYERS where each layer only uses the layer immediately below it.

**The THE System Layers**:
```
Layer 5: User programs
Layer 4: Console handling
Layer 3: I/O devices
Layer 2: Message passing
Layer 1: Memory management
Layer 0: CPU allocation
```

**Key Principle**: A layer is a COMPLETE abstraction. Layer N doesn't need to know HOW Layer N-1 works, only what it provides.

## What Standard Model Already Integrates ✅

| Dijkstra | Standard Model | How |
|----------|----------------|-----|
| Layered abstraction | 16 Levels (L-3 to L12) | Same concept, extended |
| Each layer complete | Holons at each level | Each level is self-contained |
| Only uses layer below | Dependency edges | Could validate this constraint |

## What's Missing ⚠️

| Gap | Description | Suggested Addition |
|-----|-------------|-------------------|
| **Layer skip detection** | When L5 directly calls L2 (bad) | Add LAYER_SKIP_VIOLATION |
| **Abstraction completeness** | Is each layer a complete abstraction? | Add ABSTRACTION_COHERENCE metric |

---

# Synthesis Gaps

> **Updated**: 2026-01-07
> **Status**: Major gaps now implemented in schema v2.0

## Critical Gaps (High Priority)

| # | Gap | Source Theory | Status | Implementation |
|---|-----|---------------|--------|----------------|
| 1 | **World 2 (Mental)** | Popper | ✅ DONE | D9_INTENT dimension added to particle schema |
| 2 | **Entropy/Complexity** | Shannon | ✅ DONE | `metrics.complexity` with cyclomatic, cognitive, entropy |
| 3 | **Layer violation detection** | Clean Arch + Dijkstra | ✅ DONE | AM001, AM002 in antimatter_laws.yaml |
| 4 | **Bounded Context** | DDD | ✅ DONE | `ddd.bounded_context` + AM005 violation |

## Medium Gaps

| # | Gap | Source Theory | Status | Implementation |
|---|-----|---------------|--------|----------------|
| 5 | Tension dynamics | Koestler | ✅ DONE | `metrics.coupling.tension` |
| 6 | Matter facet | Ranganathan | ✅ DONE | D10_LANGUAGE dimension |
| 7 | Canonical notation (tau) | Ranganathan | ✅ DONE | τ() format defined in schema |
| 8 | Aggregate roots | DDD | ✅ DONE | `ddd.is_aggregate_root`, `ddd.aggregate_id` |
| 9 | Noise/error propagation | Shannon | ⏳ Partial | Planned via edge confidence propagation |

## Low Priority / Nice to Have

| # | Gap | Source Theory | Status | Notes |
|---|-----|---------------|--------|-------|
| 10 | World 3 autonomy | Popper | ⏳ Planned | Emergent properties detection |
| 11 | Holon pathologies | Koestler | ✅ DONE | AM003 (GodClass), AM004 (AnemicModel) |
| 12 | Screaming architecture | Clean Arch | ⏳ Planned | Domain alignment score |

## Implementation Files

| File | What was added |
|------|---------------|
| `schema/particle.schema.json` | D9_INTENT, D10_LANGUAGE, metrics, ddd, violations |
| `schema/types.ts` | TypeScript types for all new components |
| `schema/types.py` | Python dataclasses for all new components |
| `schema/antimatter_laws.yaml` | 5 core violation rules (AM001-AM005) |
| `docs/SYNTHESIS_GAP_IMPLEMENTATION.md` | Full implementation roadmap |

---

# For AI: Why This Matters

## The Problem with Code-as-Text

When an LLM processes code, it sees **tokens**:

```
def get_user_by_id(user_id: int) -> User:
    return self.repository.find(user_id)
```

The LLM predicts: *"What token comes next?"*

It does NOT inherently understand:
- This is a **Query** (Role)
- In the **Application** layer
- With **Read** side effects
- Crossing an **I-O Boundary** to the database
- Part of a **User** aggregate
- At **L3** in a system up to **L12**

## The Solution: Semantic Scaffold

The Standard Model provides AI with a **cognitive framework**:

```json
{
  "particle": {
    "node_id": "core.user.get_user_by_id",
    "type": "Function",
    "dimensions": {
      "D1_WHAT": "Function",
      "D2_LAYER": "Application",
      "D3_ROLE": "Query",
      "D4_BOUNDARY": "I-O",
      "D5_STATE": "Stateless",
      "D6_EFFECT": "Read",
      "D7_LIFECYCLE": "Use",
      "D8_TRUST": 0.92
    },
    "level": "L3",
    "plane": "Semantic",
    "edges": [
      {"target": "repository.find", "type": "calls"},
      {"target": "User", "type": "returns"}
    ]
  }
}
```

Now the AI thinks: *"This is an L3 Query in the Application layer with I-O boundary crossing and Read effects."*

**This is architectural thinking, not text prediction.**

## Usefulness Rating: 9/10

| Aspect | Rating | Notes |
|--------|--------|-------|
| **Conceptual Framework** | 10/10 | Comprehensive, unified |
| **Multi-dimensional Classification** | 10/10 | 8D is unprecedented |
| **Practical Implementation** | 8/10 | Collider exists but atoms not fully enumerated |
| **AI Training Data** | 7/10 | Needs annotated corpus |
| **Cross-Language Support** | 8/10 | Python/TS/Java/Go/Rust but mappings incomplete |

**Overall: 9/10** - The framework is there. The remaining work is enumeration and training data.

---

# Next Steps

1. **Complete the 200 atoms enumeration** - Full periodic table with all atoms
2. **Add missing dimensions** - D9 DOCUMENTATION? D10 LANGUAGE?
3. **Create formal JSON schema** - Machine-readable particle format
4. **Build annotated training corpus** - Code labeled with Standard Model dimensions
5. **Validate layer violation detection** - Implement as Antimatter law
6. **Define tau notation** - Canonical particle ID system like `τ(Function:Query:App:IO:SL:R:U:92)`
