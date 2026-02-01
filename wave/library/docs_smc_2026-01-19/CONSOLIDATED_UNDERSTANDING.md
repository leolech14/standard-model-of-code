# Consolidated Understanding: The Standard Model of Code

> **Generated:** 2026-01-19
> **Status:** AUTHORITATIVE - This document reconciles all fragmented sources
> **Purpose:** Single source of truth for the theory's current state

---

## Executive Summary

The Standard Model of Code maps **PURPOSE** at every level of software.

| Concept | Current Truth | Documented As | Status |
|---------|---------------|---------------|--------|
| Atom Count (T0) | **200** | 167 (FORMAL_PROOF.md) | **OUTDATED** |
| Tiers | **T0/T1/T2** | Not in formal docs | **UNDOCUMENTED** |
| Role Count | **33** | 27 (FORMAL_PROOF.md) | **OUTDATED** |
| Target Coverage | **~600 atoms** | Not documented | **VISION** |

---

## 1. THE CORE PRINCIPLE: PURPOSE

> *"Every bit has a reason to be a zero or a one."*

**Atoms map specific purposes inside the world of computer programs.**

What we map is not syntax - it's **WHY the code exists**:
- What is its basic function?
- Why is it kept in the codebase?
- What work does it contribute to?

Purpose is **recursive** - it exists at every level:
- Tiny purposes combine → larger purposes
- Larger purposes combine → system purpose
- System purpose drives → application existence

---

## 2. THE 16-LEVEL SCALE (L-3 → L12)

The codespace spans 16 levels of abstraction from L-3 to L12.

**Source:** `src/core/viz/assets/app.js` (SCALE_16_LEVELS)

| Level | Name | Zone | Symbol |
|-------|------|------|--------|
| L-3 | BIT/QUBIT | PHYSICAL | ⚡ |
| L-2 | BYTE | PHYSICAL | 01 |
| L-1 | CHARACTER | PHYSICAL | a |
| L0 | TOKEN | SYNTACTIC | · |
| L1 | STATEMENT | SEMANTIC | ─ |
| L2 | BLOCK | SEMANTIC | ▣ |
| L3 | NODE | SEMANTIC | ★ |
| L4 | CONTAINER | ARCHITECTURAL | ⬢ |
| L5 | FILE | ARCHITECTURAL | 📄 |
| L6 | PACKAGE | ARCHITECTURAL | 📦 |
| L7 | SYSTEM | ARCHITECTURAL | ⬡ |
| L8 | ECOSYSTEM | COSMOLOGICAL | 🔗 |
| L9 | PLATFORM | COSMOLOGICAL | ☁️ |
| L10 | ORGANIZATION | COSMOLOGICAL | 🏢 |
| L11 | DOMAIN | COSMOLOGICAL | 🏛️ |
| L12 | UNIVERSE | COSMOLOGICAL | 🌐 |

### The Five Zones:

| Zone | Levels | Description |
|------|--------|-------------|
| **PHYSICAL** | L-3 to L-1 | Hardware, bits, memory, I/O |
| **SYNTACTIC** | L0 | Event horizon between meaning and data |
| **SEMANTIC** | L1 to L3 | Operational core (where analysis lives) |
| **ARCHITECTURAL** | L4 to L7 | Primary visible zone |
| **COSMOLOGICAL** | L8 to L12 | Beyond typical scope |

**Key insight:** Entities at each level are made from components at lower levels.
Systems inside systems. **Recursive composition.**

---

## 3. THE THREE-TIER ARCHITECTURE (T0/T1/T2)

### Current Files:
- `src/patterns/ATOMS_TIER0_CORE.yaml` - 43 core atoms
- `src/patterns/ATOMS_TIER1_STDLIB.yaml` - 24 stdlib atoms
- `src/patterns/ATOMS_TIER2_ECOSYSTEM.yaml` - 17 ecosystem atoms
- `src/patterns/ATOMS_UNIVERSAL_INDEX.yaml` - Master index

### Tier Definitions:

| Tier | Name | Specificity | Coverage | Examples |
|------|------|-------------|----------|----------|
| **T0** | Core Syntax | Universal | ~65% of all code | If, Loop, Function, Class |
| **T1** | Standard Library | Language-specific | ~25% of code | File I/O, Network, Math |
| **T2** | Ecosystems | Framework-specific | ~10% of code | React Component, Django View |

### The Specificity Gradient:

```
T0 ─────────────────────────────────────────────────────────── UNIVERSAL
     If, Loop, Function, Class, Assignment, Import

T1 ─────────────────────────────────────────────────── LANGUAGE-SPECIFIC
     File.read(), socket.connect(), json.parse()

T2 ──────────────────────────────────────────────── ECOSYSTEM-SPECIFIC
     React.Component, pandas.DataFrame, Flask.route
```

### Coverage Target:

| Tier | Current | Target | Purpose |
|------|---------|--------|---------|
| T0 | 200 | 200 | Core working set |
| T1 | 24 | ~100 | Stdlib coverage |
| T2 | 17 | ~300 | Major ecosystem coverage |
| **Total** | ~240 | **~600** | Comprehensive analysis |

---

## 4. THE 200 T0 ATOMS

From `schema/fixed/200_ATOMS.md` (Version 2.1.0):

| Phase | Families | Atoms | Description |
|-------|----------|-------|-------------|
| **DATA** | 5 | 28 | The matter of software - what code manipulates |
| **LOGIC** | 6 | 58 | The behavior of software - what code does |
| **ORGANIZATION** | 5 | 52 | The structure of software - how code is arranged |
| **EXECUTION** | 6 | 62 | The runtime of software - how code runs |
| **TOTAL** | **22** | **200** | |

### The 22 Families:

**DATA (5 families, 28 atoms):**
- Bits (4): BitFlag, BitMask, ParityBit, SignBit
- Bytes (4): ByteArray, MagicBytes, PaddingBytes, Buffer
- Primitives (10): Boolean, Integer, Float, String, Null, etc.
- Variables (6): LocalVar, GlobalVar, Parameter, Constant, etc.
- Collections (4): ArrayLiteral, ObjectLiteral, TupleLiteral, SetLiteral

**LOGIC (6 families, 58 atoms):**
- Functions (10): Function, Method, Lambda, Constructor, etc.
- Expressions (20): BinaryExpr, UnaryExpr, CallExpr, etc.
- Statements (12): Assignment, ReturnStmt, BreakStmt, etc.
- Control Flow (10): IfBranch, ForLoop, WhileLoop, TryBlock, etc.
- Pattern Matching (6): MatchPattern, WildcardPattern, etc.

**ORGANIZATION (5 families, 52 atoms):**
- Aggregates (12): Class, Struct, Enum, Union, Trait, etc.
- Modules (8): Module, Package, ImportStmt, ExportStmt, etc.
- Files (6): SourceFile, Header, ConfigFile, TestFile, etc.
- Services/Interfaces (8): Interface, AbstractClass, Endpoint, etc.
- Type System (18): TypeRef, GenericParam, UnionType, etc.

**EXECUTION (6 families, 62 atoms):**
- Concurrency (12): Thread, Process, Goroutine, Task, Future, etc.
- Error Handling (10): Exception, Error, Result, Option, Panic, etc.
- Memory Management (8): Allocation, Deallocation, Reference, etc.
- I/O Operations (10): FileRead, FileWrite, NetworkRead, etc.
- Metaprogramming (12): MacroDef, MacroRule, Annotation, etc.
- Initialization (10): StaticInit, LazyInit, DefaultInit, etc.

---

## 5. THE 33 ROLES (WHY Dimension)

From `schema/fixed/roles.json` (Version 2.0.0):

| Category | Roles |
|----------|-------|
| **Query** | Query, Finder, Loader, Getter |
| **Command** | Command, Creator, Mutator, Destroyer |
| **Creation** | Factory, Builder |
| **Persistence** | Repository, Store, Cache |
| **Orchestration** | Service, Controller, Manager, Orchestrator |
| **Validation** | Validator, Guard, Asserter |
| **Transformation** | Transformer, Mapper, Serializer, Parser |
| **Events** | Handler, Listener, Subscriber, Emitter |
| **Utility** | Utility, Formatter, Helper, Internal |
| **Lifecycle** | Lifecycle |

**Key insight:** Roles describe PURPOSE - why the code exists.

---

## 6. THE 8 SEMANTIC DIMENSIONS

From `schema/fixed/dimensions.json`:

| # | Dimension | Question | Domain |
|---|-----------|----------|--------|
| 1 | **WHAT** | What is this made of? | 200 atoms |
| 2 | **Layer** | Where does this live? | Interface, Application, Core, Infrastructure, Test |
| 3 | **Role** | What is its purpose? | 33 roles |
| 4 | **Boundary** | Does it cross boundaries? | Internal, Input, I/O, Output |
| 5 | **State** | Does it maintain state? | Stateful, Stateless |
| 6 | **Effect** | Does it have side effects? | Pure, Read, Write, ReadModify |
| 7 | **Activation** | How is it triggered? | Direct, Event, Time |
| 8 | **Lifetime** | How long does it exist? | Transient, Session, Global |

---

## 7. THE SEMANTIC SPACE

**Calculation:**
```
|Σ| = |Atoms| × |Roles| × |RPBL Space|
    = 200 × 33 × 10,000
    = 66,000,000 possible semantic coordinates
```

*Note: FORMAL_PROOF.md says 45,090,000 (based on 167 × 27 × 10,000) - this is OUTDATED.*

---

## 8. WHAT'S DOCUMENTED VS WHAT'S TRUE

### Documented but OUTDATED:
| File | Claims | Truth |
|------|--------|-------|
| FORMAL_PROOF.md | 167 atoms | **200 atoms** |
| FORMAL_PROOF.md | 27 roles | **33 roles** |
| FORMAL_PROOF.md | 45M semantic space | **66M semantic space** |
| FORMAL_PROOF.md | 10 pipeline stages | **12 pipeline stages** |
| ATOMS_REFERENCE.md | 167 atoms | **200 atoms** |
| dimensions.json | 167 atoms | **200 atoms** |

### Documented and CURRENT:
| File | Content | Status |
|------|---------|--------|
| schema/fixed/200_ATOMS.md | 200 atoms enumerated | ✓ Current |
| schema/fixed/roles.json | 33 roles | ✓ Current |
| ATOMS_UNIVERSAL_INDEX.yaml | T0/T1/T2 tiers | ✓ Current |
| ATOMS_TIER0_CORE.yaml | 43 core atoms | ✓ Current |

### NOT Documented (Vision):
| Concept | Target | Status |
|---------|--------|--------|
| 600 atom ecosystem coverage | ~600 total | Vision |
| Complete T1 stdlib atoms | ~100 | In progress |
| Complete T2 ecosystem atoms | ~300 | Early stage |

---

## 9. FILES TO UPDATE

### Priority 1: Core Theory Files
1. **FORMAL_PROOF.md** - Update all atom/role counts, semantic space calculation
2. **dimensions.json** - Change "167 atom types" to "200 atom types"
3. **ATOMS_REFERENCE.md** - Redirect to 200_ATOMS.md or update

### Priority 2: Mechanized Proofs
1. **MECHANIZED_PROOFS.md** - Update semantic space claim
2. **proofs/lean/** - Update Lean proofs for new counts

### Priority 3: Add Missing Documentation
1. **TIERS.md** - Document T0/T1/T2 architecture (doesn't exist)
2. **PURPOSE.md** - Document the purpose principle (partially in PURPOSE_FIELD.md)
3. **16_LEVELS.md** - Document the scale (not documented)

---

## 10. THE TRUTH TABLE

| Concept | FORMAL_PROOF Says | Schema Says | Implementation Says | **TRUTH** |
|---------|-------------------|-------------|---------------------|-----------|
| Atom count | 167 | 200 | ~15 base IDs | **200 concepts → ~15 IDs** |
| Role count | 27 | 33 | 29 different | **33 canonical, 29 implemented** |
| Pipeline stages | 10 | N/A | 12 | **12** |
| Tiers | None | T0/T1/T2 | YAMLs exist, NOT used | **T0/T1/T2 (docs only)** |
| Semantic space | 45M | N/A | ~5M (15×33×10K) | **5M practical, 66M theoretical** |
| RPBL range | [1,10] int | 0-10 float | Integers 1-9 | **Integers 1-9** |
| 16 levels | Not doc'd | L-3 to L12 | SCALE_16_LEVELS | **L-3 to L12 verified** |

---

## Summary

The Standard Model of Code has evolved beyond what FORMAL_PROOF.md documents:

1. **200 named atoms** (not 167) organized into 4 phases and 22 families → **map to ~15 base IDs**
2. **T0/T1/T2 tiered architecture** documented in YAMLs but **NOT integrated into implementation**
3. **33 canonical roles** (not 27) for the WHY dimension, but **only 29 implemented** (40% overlap!)
4. **16 levels from L-3 to L12** across 5 zones (Physical, Syntactic, Semantic, Architectural, Cosmological)
5. **RPBL uses integers 1-9** (not floats 0-10)
6. **Purpose at every level** - the recursive composition principle
7. **Target: ~600 atoms** for comprehensive ecosystem coverage

### CRITICAL GAPS:
- Implementation uses ~15 atom IDs, docs say 200
- 20 canonical roles NOT implemented, 16 extra roles in implementation
- Tier YAML files exist but are NOT used by code
- Theoretical semantic space (66M) vs practical (~5M)

The formal documentation (FORMAL_PROOF.md) is a V1 snapshot. The actual system is V2+ in docs, but implementation lags behind.

---

**This document supersedes conflicting claims in other files until those files are updated.**

**See also:** `docs/reports/DEEP_CHALLENGE_2026-01-19.md` for full verification details.
