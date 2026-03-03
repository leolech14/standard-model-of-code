# LEVELS - The 16-Level Holarchy

> From BIT to UNIVERSE. Every code element sits at a level. Emergence happens at every transition.

---

## The Full Scale

| Level | Name | Zone | What Lives Here |
|-------|------|------|-----------------|
| L12 | UNIVERSE | Cosmological | All software everywhere |
| L11 | DOMAIN | Cosmological | Business domain (e-commerce, healthcare) |
| L10 | ORGANIZATION | Cosmological | Company's entire codebase |
| L9 | PLATFORM | Cosmological | Multi-service platform |
| L8 | ECOSYSTEM | Cosmological | Service mesh, microservices |
| L7 | SYSTEM | Systemic | Single deployable application |
| L6 | PACKAGE | Systemic | Module/namespace/directory |
| L5 | FILE | Systemic | Source file (.py, .ts, .go) |
| L4 | CONTAINER | Systemic | Class, struct, interface |
| L3 | NODE | Semantic | Function, method, property |
| L2 | BLOCK | Semantic | Code block (if, loop, try) |
| L1 | STATEMENT | Semantic | Single statement |
| L0 | TOKEN | Syntactic | Lexical token |
| L-1 | CHARACTER | Physical | Single character |
| L-2 | BYTE | Physical | 8 bits |
| L-3 | BIT/QUBIT | Physical | Binary digit |

---

## The 5 Zones

Zones are **not** arbitrary groupings. They represent **phase boundaries** where the dominant relation type changes.

| Zone | Levels | Dominant Relation |
|------|--------|-------------------|
| **Physical** | L-3 to L-1 | Encoding (bits → bytes → chars) |
| **Syntactic** | L0 | Grammar rules |
| **Semantic** | L1 to L3 | Meaning and intent |
| **Systemic** | L4 to L7 | Architecture and composition |
| **Cosmological** | L8 to L12 | Organization and domain |

**Zone transitions are phase transitions.** Moving from Syntactic to Semantic is where tokens acquire meaning. Moving from Semantic to Systemic is where functions become architecture.

---

## Operational Range

The Collider operates at **L3-L7** (function to system). This is where architectural decisions live.

```
L3 (NODE)      → Individual functions, methods
L4 (CONTAINER) → Classes, structs
L5 (FILE)      → Source files
L6 (PACKAGE)   → Modules, directories
L7 (SYSTEM)    → The application
```

Below L3: handled by parsers (Tree-sitter).
Above L7: handled by organizational context.

---

## Holons (Janus-Faced)

Every level is simultaneously:
- A **whole** containing parts below it
- A **part** contained by the level above

A class (L4) contains functions (L3) and is contained by a file (L5). This is Koestler's holon concept. The containment relation is a **strict partial order**: antisymmetric, transitive, with no cycles.

---

## Emergence at Transitions

A file's purpose is NOT the sum of its functions' purposes. Each level transition creates something **qualitatively new**:

- L3 → L4: Functions combine into a class with emergent capability
- L4 → L5: Classes in a file form a cohesive module
- L5 → L6: Files in a package define a bounded context
- L6 → L7: Packages compose into a deployable system

---

*Source: L1_DEFINITIONS.md (Section 2), L0_AXIOMS.md (Axioms C1-C3)*
*See also: [../essentials/CLASSIFICATION.md](../essentials/CLASSIFICATION.md) for the full scale table*
