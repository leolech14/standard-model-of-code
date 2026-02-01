# THEORY CONSOLIDATION MAP

## Current State: Better Than Expected

The theory IS structured in `particle/docs/theory/`:

```
L0_AXIOMS.md      → Foundation (cannot be proven)
L1_DEFINITIONS.md → All concepts defined ONCE
L2_LAWS.md        → Invariant relationships
L3_APPLICATIONS.md → Practical implementation
```

---

## THE HIERARCHY (from L1_DEFINITIONS.md)

```
STANDARD MODEL OF CODE
│
├── THREE REALMS (PROJECT_elements Trinity)
│   ├── PARTICLE (particle/) → Collider
│   ├── WAVE (wave/) → Refinery
│   └── OBSERVER (.agent/) → Autopilot
│
├── THREE PLANES (Popper's Worlds)
│   ├── PHYSICAL → Hardware, bytes, bits
│   ├── VIRTUAL → AST, runtime objects
│   └── SEMANTIC → Meaning, roles, purpose
│
├── 16 LEVELS (Holarchy)
│   ├── COSMOLOGICAL: L8-L12 (Universe → Platform)
│   ├── SYSTEMIC: L4-L7 (System → Container)
│   ├── SEMANTIC: L1-L3 (Statement → Node)
│   ├── SYNTACTIC: L0 (Token)
│   └── PHYSICAL: L-3 to L-1 (Bit → Character)
│
├── PROJECTOME (All files)
│   ├── CODOME → Executable code (Collider)
│   └── CONTEXTOME → Documentation (Refinery)
│
├── 8 DIMENSIONS (Classification axes)
│   ├── D1: WHAT (atom type)
│   ├── D2: LAYER (presentation/logic/data)
│   ├── D3: ROLE (purpose)
│   ├── D4: BOUNDARY (I-O interface)
│   ├── D5: STATE (stateful/stateless)
│   ├── D6: EFFECT (read/write/pure)
│   ├── D7: LIFECYCLE (transient/persistent)
│   └── D8: TRUST (internal/external)
│
├── 200 ATOMS (Code building blocks)
│   ├── 4 PHASES: DAT, LOG, ORG, EXE
│   ├── 22 FAMILIES
│   └── 3 TIERS: A(tom), M(olecule), O(rganism)
│
├── 5 EDGE FAMILIES (Relationships)
│   ├── Structural
│   ├── Dependency
│   ├── Inheritance
│   ├── Semantic
│   └── Temporal
│
└── ANTIMATTER LAWS (What must NOT happen)
    ├── AM001: ?
    ├── AM002: Architectural Drift
    ├── AM003: Supply Chain Hallucination
    ├── AM004: Centrifugal Dependency (NEW)
    └── AM005: Orphan Code (NEW)
```

---

## WHERE RING FITS

**Ring is NOT in the current theory.**

Ring belongs as:
- A **derived metric** from Edge Families (Dependency)
- Calculated during Collider analysis
- Stored on UnifiedNode instances

### Proposed Addition to L1_DEFINITIONS.md:

```markdown
## X. Dependency Rings (Concentric Architecture)

**Definition:** Ring is the dependency depth of a node, measured as
maximum distance from nodes with zero internal imports.

| Ring | Name | Description |
|------|------|-------------|
| 0 | CORE | No internal dependencies |
| 1 | DOMAIN | Depends only on Ring 0 |
| 2 | APPLICATION | Depends on Ring 0-1 |
| 3 | ADAPTER | Depends on Ring 0-2 |
| 4 | FRAMEWORK | Depends on Ring 0-3 + externals |

**Calculation:** Derived from Dependency edges (Edge Family 2)

**Law:** AM004 - Dependencies must flow INWARD only
```

---

## GAPS IDENTIFIED

| Concept | Status | Location |
|---------|--------|----------|
| Ring (0-4) | NEW | Not in L1 yet |
| AM001 | UNDEFINED | Not documented |
| AM004-005 | NEW | Need to add to L2_LAWS |
| RPBL scores | PARTIAL | Mentioned but not enumerated |
| Tier (A/M/O) | IN ATOMS | Part of atom ID, not separate |

---

## ACTION: Single Source of Truth

The consolidation is simpler than expected:

1. **L1_DEFINITIONS.md** should be THE source
2. Add Ring definition to L1
3. Add AM004/AM005 to L2_LAWS.md
4. Everything else already exists

**Ring is the only major missing piece.**
