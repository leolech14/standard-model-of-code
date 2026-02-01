# Fact Inventory: What Data Exists

> **Purpose:** Catalog ALL unique facts from ALL nodes → feed into single bible
> **NOT a fix list. A learning document.**

---

## UNIQUE FACTS DISCOVERED

### STRUCTURAL CONSTANTS

| Fact ID | Fact | True Value | Sources (nodes) |
|---------|------|------------|-----------------|
| F001 | Atom count | 200 named → ~15 IDs | DATM.PRO.2, DFRM.ABS.1, DFRM.THE31.5, DCON.4THE.1 |
| F002 | Role count | 33 canonical, 29 implemented | DFRM.8APP.1, DCAN.SCHVAL.1, DCON.5THE.1 |
| F003 | Family count | 22 | DATM.ATOREF.1, DTHM.THE16.1-4 |
| F004 | Phase count | 4 | DATM.ATOREF.1 |
| F005 | Level count | 16 (L-3 to L12) | DCON.2THE.1 |
| F006 | Zone count | 5 | DCON.SUM.3 |
| F007 | Pipeline stages | 12 | DFRM.THE37.2 |
| F008 | RPBL dimensions | 4 (R,P,B,L) | multiple |
| F009 | RPBL range | integers 1-9 | implementation |
| F010 | Tier count | 3 (T0/T1/T2) | DCON |

### THE 16 LEVELS (F005 detail)

| Level | Name | Zone |
|-------|------|------|
| L-3 | BIT/QUBIT | PHYSICAL |
| L-2 | BYTE | PHYSICAL |
| L-1 | CHARACTER | PHYSICAL |
| L0 | TOKEN | SYNTACTIC |
| L1 | STATEMENT | SEMANTIC |
| L2 | BLOCK | SEMANTIC |
| L3 | NODE | SEMANTIC |
| L4 | CONTAINER | ARCHITECTURAL |
| L5 | FILE | ARCHITECTURAL |
| L6 | PACKAGE | ARCHITECTURAL |
| L7 | SYSTEM | ARCHITECTURAL |
| L8 | ECOSYSTEM | COSMOLOGICAL |
| L9 | PLATFORM | COSMOLOGICAL |
| L10 | ORGANIZATION | COSMOLOGICAL |
| L11 | DOMAIN | COSMOLOGICAL |
| L12 | UNIVERSE | COSMOLOGICAL |

### THE 5 ZONES (F006 detail)

| Zone | Levels | Purpose |
|------|--------|---------|
| PHYSICAL | L-3 to L-1 | Hardware substrate |
| SYNTACTIC | L0 | Meaning/data boundary |
| SEMANTIC | L1 to L3 | Operational core |
| ARCHITECTURAL | L4 to L7 | Visible structure |
| COSMOLOGICAL | L8 to L12 | Beyond scope |

### THE 4 PHASES (F004 detail)

| Phase | Families | Atoms | Purpose |
|-------|----------|-------|---------|
| DATA | 5 | 28 | What code manipulates |
| LOGIC | 6 | 58 | What code does |
| ORGANIZATION | 5 | 52 | How code is arranged |
| EXECUTION | 6 | 62 | How code runs |

### THE 33 ROLES (F002 detail)

| Category | Roles |
|----------|-------|
| Query | Query, Finder, Loader, Getter |
| Command | Command, Creator, Mutator, Destroyer |
| Creation | Factory, Builder |
| Persistence | Repository, Store, Cache |
| Orchestration | Service, Controller, Manager, Orchestrator |
| Validation | Validator, Guard, Asserter |
| Transformation | Transformer, Mapper, Serializer, Parser |
| Events | Handler, Listener, Subscriber, Emitter |
| Utility | Utility, Formatter, Helper, Internal |
| Lifecycle | Lifecycle |

### THE 4 RPBL DIMENSIONS (F008 detail)

| Dimension | Question | Range |
|-----------|----------|-------|
| Responsibility | How much does it do? | 1-9 int |
| Purity | How pure is it? | 1-9 int |
| Boundary | Does it cross boundaries? | 1-9 int |
| Lifecycle | How long does it live? | 1-9 int |

### THE 3 TIERS (F010 detail)

| Tier | Name | Coverage | Specificity |
|------|------|----------|-------------|
| T0 | Core | ~65% | Universal |
| T1 | Stdlib | ~25% | Language-specific |
| T2 | Ecosystem | ~10% | Framework-specific |

---

## WHAT CONTENT EXISTS (by type)

From 225 nodes:

| Type | Count | Contains |
|------|-------|----------|
| TBL | 103 | Data tables, mappings |
| COD | 71 | Code examples, diagrams |
| NUM | 26 | Numeric claims |
| CLM | 15 | Theorems, proofs |
| DEF | 10 | Term definitions |

---

## BIBLE STRUCTURE PROPOSAL

### Single Source: `THEORY.md` (The Standard Model Bible)

```
THEORY.md
├── 1. CORE PRINCIPLE (Purpose)
├── 2. STRUCTURAL CONSTANTS
│   ├── 2.1 The 16 Levels (L-3 to L12)
│   ├── 2.2 The 5 Zones
│   ├── 2.3 The 4 Phases
│   ├── 2.4 The 22 Families
│   └── 2.5 The 200 Atoms (enumerated)
├── 3. CLASSIFICATION SYSTEM
│   ├── 3.1 The 33 Roles
│   ├── 3.2 The 4 RPBL Dimensions
│   └── 3.3 The 3 Tiers (T0/T1/T2)
├── 4. FORMAL PROOFS
│   ├── 4.1 Coverage Theorem
│   ├── 4.2 Determinism Theorem
│   └── 4.3 Completeness Theorem
└── 5. GLOSSARY
```

### Single Source: `TOOL.md` (The Collider Bible)

```
TOOL.md
├── 1. WHAT COLLIDER DOES
├── 2. THE 12-STAGE PIPELINE
├── 3. INPUT/OUTPUT FORMATS
├── 4. COMMANDS
├── 5. VISUALIZATION
└── 6. AI INTEGRATION
```

---

## DATA TO MIGRATE INTO BIBLES

| From | Contains | Goes To |
|------|----------|---------|
| FORMAL_PROOF.md | Proofs, theorems | THEORY.md §4 |
| GLOSSARY.md | Definitions | THEORY.md §5 |
| ATOMS_REFERENCE.md | Atom list | THEORY.md §2.5 |
| THEORY_MAP.md | Structure overview | THEORY.md §2 |
| 200_ATOMS.md | Authoritative atoms | THEORY.md §2.5 |
| roles.json | Authoritative roles | THEORY.md §3.1 |
| ARCHITECTURE.md | Pipeline, bidirectionality | TOOL.md §2 |
| COMMANDS.md | CLI reference | TOOL.md §4 |
| QUICKSTART.md | Usage | TOOL.md §1 |

---
