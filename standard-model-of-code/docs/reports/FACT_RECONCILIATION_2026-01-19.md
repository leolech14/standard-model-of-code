# Fact Reconciliation Audit

> **Generated:** 2026-01-19
> **Purpose:** Identify all factual claims across docs, verify consistency, flag contradictions

---

## Summary of Contradictions (RESOLVED)

| Concept | Values Found | Canonical Value | Resolution |
|---------|--------------|-----------------|------------|
| **Atom Count** | 167 vs 200 | **200** | FORMAL_PROOF.md is V1, schema/fixed/200_ATOMS.md is V2 |
| **Role Count** | 27 vs 33 | **33** | FORMAL_PROOF.md is V1, schema/roles.json is V2 |
| **Tier System** | None vs T0/T1/T2 | **T0/T1/T2** | Not in formal docs, exists in src/patterns/ |
| **Pipeline Stages** | 10 vs 12 | **12** | Implementation has 12 stages (full_analysis.py) |
| **Semantic Space** | 45M vs 66M | **66M** | 200 × 33 × 10,000 = 66,000,000 |
| **RPBL Range** | [1,10] int vs 0-10 float | **TBD** | Check implementation |

---

## KEY FINDING: Major Version Mismatch

**FORMAL_PROOF.md documents V1 theory:**
- 167 atoms
- 27 roles
- 45,090,000 semantic space
- No tier system

**Actual current state (V2+):**
- **200 atoms** (schema/fixed/200_ATOMS.md)
- **33 roles** (schema/fixed/roles.json)
- **66,000,000 semantic space** (200 × 33 × 10,000)
- **T0/T1/T2 tier system** (src/patterns/ATOMS_UNIVERSAL_INDEX.yaml)
- **Target: ~600 atoms** for ecosystem coverage (user vision)

**See: `docs/CONSOLIDATED_UNDERSTANDING.md` for authoritative current state**

---

## The 200 Atoms (from schema/fixed/200_ATOMS.md)

| Phase | Families | Atoms |
|-------|----------|-------|
| DATA | 5 | 28 |
| LOGIC | 6 | 58 |
| ORGANIZATION | 5 | 52 |
| EXECUTION | 6 | 62 |
| **TOTAL** | **22** | **200** |

---

## The Tier System (from src/patterns/)

| Tier | Name | Atoms | Description |
|------|------|-------|-------------|
| T0 | Core Syntax | 43 (in YAML) / 200 (in 200_ATOMS.md) | Universal constructs |
| T1 | Standard Library | 24 | Built-in runtime |
| T2 | Ecosystems | 17 | Framework patterns |

**Note:** The 200 atoms in 200_ATOMS.md appear to be the expanded T0 core set.

---

## ACTION REQUIRED: Update FORMAL_PROOF.md to reflect V2+ theory

---

## 1. ATOMS (WHAT Dimension)

### 1.1 Total Atom Count

| File:Line | Claim | Match |
|-----------|-------|-------|
| FORMAL_PROOF.md:16 | "167-atom taxonomy" | ✓ |
| FORMAL_PROOF.md:54 | "\|A\| = 167" | ✓ |
| FORMAL_PROOF.md:165 | "167 atoms" | ✓ |
| ATOMS_REFERENCE.md:8 | "4 phases and 16 families" | ✓ |
| ATOMS_REFERENCE.md:280 | "Total: 167 atoms across 4 phases and 16 families" | ✓ |
| THEORY_MAP.md:285 | "Open schema across 16 families in 4 phases" | ✓ (no number) |
| ARCHITECTURE.md:32 | "4 phases, 16 families" | ✓ |

**VERDICT: CONSISTENT** - All sources agree: 167 atoms, 4 phases, 16 families

### 1.2 Atom Phase Breakdown

| Phase | FORMAL_PROOF.md | ATOMS_REFERENCE.md (counted) | Match |
|-------|-----------------|------------------------------|-------|
| DATA | :59 → 26 | Bits(4)+Bytes(4)+Primitives(10)+Variables(8) = 26 | ✓ |
| LOGIC | :60 → 61 | Expressions(15)+Statements(10)+Control(14)+Functions(22) = 61 | ✓ |
| ORG | :61 → 45 | Aggregates(16)+Services(12)+Modules(9)+Files(8) = 45 | ✓ |
| EXEC | :62 → 35 | Handlers(9)+Workers(8)+Initializers(8)+Probes(10) = 35 | ✓ |
| **TOTAL** | 26+61+45+35 = **167** | **167** | ✓ |

**VERDICT: CONSISTENT** - Phase breakdown matches explicit atom list

### 1.3 Atom Family Breakdown (per FORMAL_PROOF.md:147-163)

| Family | Atoms | Phase |
|--------|-------|-------|
| Bits | 4 | DATA |
| Bytes | 4 | DATA |
| Primitives | 10 | DATA |
| Variables | 8 | DATA |
| Expressions | 15 | LOGIC |
| Statements | 10 | LOGIC |
| Control | 14 | LOGIC |
| Functions | 22 | LOGIC |
| Aggregates | 16 | ORG |
| Services | 12 | ORG |
| Modules | 9 | ORG |
| Files | 8 | ORG |
| Handlers | 9 | EXEC |
| Workers | 8 | EXEC |
| Initializers | 8 | EXEC |
| Probes | 10 | EXEC |

**VERDICT: CONSISTENT** - ATOMS_REFERENCE.md explicit listing matches counts

---

## 2. ROLES (WHY Dimension)

### 2.1 Role Count

| File:Line | Claim | Version |
|-----------|-------|---------|
| FORMAL_PROOF.md:65 | "\|R\| = 27" | **V1 (outdated)** |
| FORMAL_PROOF.md:174 | "27-role taxonomy" | **V1 (outdated)** |
| FORMAL_PROOF.md:549-579 | Lists exactly 27 roles | **V1 (outdated)** |
| schema/fixed/roles.json:4 | "count": 33 | **V2 (current)** |
| PURPOSE_FIELD.md:208 | "33 roles detected with >90% accuracy" | **V2 (current)** |

**VERDICT: RESOLVED**
- **Canonical value: 33 roles (V2 theory)**
- FORMAL_PROOF.md needs update to reflect V2 theory
- The 33 roles are explicitly enumerated in `schema/fixed/roles.json`

### 2.2 Role List Comparison

**V1 (FORMAL_PROOF.md:551-579) - 27 roles (OUTDATED):**
```
Test, Query, Command, Factory, Service, Repository, EventHandler,
UseCase, Validator, Specification, Mapper, Adapter, Builder,
Controller, Iterator, Configuration, Policy, Job, Lifecycle,
DTO, Exception, Property, Internal, Dunder, Utility, Utility2, Unknown
```

**V2 (schema/fixed/roles.json) - 33 roles (CANONICAL):**
```
Query, Finder, Loader, Getter, Command, Creator, Mutator, Destroyer,
Factory, Builder, Repository, Store, Cache, Service, Controller,
Manager, Orchestrator, Validator, Guard, Asserter, Transformer,
Mapper, Serializer, Parser, Handler, Listener, Subscriber, Emitter,
Utility, Formatter, Helper, Internal, Lifecycle
```

**Key changes V1 → V2:**
- Split Query into: Query, Finder, Loader, Getter
- Split Command into: Command, Creator, Mutator, Destroyer
- Added: Store, Cache, Manager, Orchestrator, Guard, Asserter
- Added: Transformer, Serializer, Parser, Handler, Listener, Subscriber, Emitter
- Added: Formatter, Helper
- Removed: Test, EventHandler, UseCase, Specification, Adapter, Iterator
- Removed: Configuration, Policy, Job, DTO, Exception, Property, Dunder, Utility2, Unknown

**Canonical Source: schema/fixed/roles.json**

---

## 3. RPBL (HOW Dimension)

### 3.1 RPBL Range Definition

| File:Line | Claim | Status |
|-----------|-------|--------|
| FORMAL_PROOF.md:72 | "[1,10]^4 ⊂ Z^4" (integers 1-10) | Source A |
| FORMAL_PROOF.md:227 | "[1, 10] ∩ Z" (integers) | Source A |
| FORMAL_PROOF.md:437 | "bounded integers in [1,10]" | Source A |
| GLOSSARY.md:52 | "float 0-10" for Responsibility | **CONFLICT** |
| GLOSSARY.md:53 | "float 0-10" for Purity | **CONFLICT** |
| GLOSSARY.md:54 | "float 0-10" for Boundary | **CONFLICT** |
| GLOSSARY.md:55 | "float 0-10" for Lifecycle | **CONFLICT** |

**VERDICT: CONFLICT**
- FORMAL_PROOF.md (formal definition): integers [1,10]
- GLOSSARY.md (implementation reference): floats 0-10

**Questions:**
1. Is the implementation using 0-10 floats while theory says 1-10 integers?
2. Does 0 have meaning (undefined/unknown)?

### 3.2 RPBL Space Size

| File:Line | Claim | Match |
|-----------|-------|-------|
| FORMAL_PROOF.md:230 | "\|V\| = 10^4 = 10,000" | ✓ |

**VERDICT: CONSISTENT** (if integers 1-10)

---

## 4. SEMANTIC SPACE

### 4.1 Total Semantic Space Size

| File:Line | Claim | Calculation | Version |
|-----------|-------|-------------|---------|
| FORMAL_PROOF.md:249 | "45,090,000" | 167 × 27 × 10,000 | **V1 (outdated)** |
| MECHANIZED_PROOFS.md:86 | "45,090,000 possible states" | Same | **V1 (outdated)** |
| FORMAL_PROOF.md:524 | "<50M states" | Rounded | **V1 (outdated)** |

**VERDICT: NEEDS UPDATE**

With V2 theory (33 roles):
- **V2 Calculation: 167 × 33 × 10,000 = 55,110,000 states**
- The V1 claim of 45,090,000 is based on 27 roles
- MECHANIZED_PROOFS.md Lean proofs will need updating

---

## 5. LAYERS

### 5.1 Layer Names

| File:Line | Layers Listed |
|-----------|---------------|
| FORMAL_PROOF.md:360 | Role + Layer (no explicit list) |
| GLOSSARY.md:44 | Domain, Application, Infrastructure, UI |
| PURPOSE_FIELD.md:125-140 | Presentation, Application, Domain, Infrastructure |
| ARCHITECTURE.md:35 | Domain, Infra, App, UI |
| THEORY_MAP.md:118 | Domain, Application, Infrastructure (implicit from context) |

**VERDICT: MINOR INCONSISTENCY**
- GLOSSARY uses "UI"
- PURPOSE_FIELD uses "Presentation"
- These appear synonymous but should be standardized

---

## 6. PIPELINE

### 6.1 Pipeline Stage Count

| File:Line | Claim | Status |
|-----------|-------|--------|
| FORMAL_PROOF.md:315 | "10-stage pipeline" | Source A |
| FORMAL_PROOF.md:490 | "Pipeline stages \| 10" | Source A |
| ARCHITECTURE.md:287 | "12-stage analysis pipeline" | **CONFLICT** |

**VERDICT: CONFLICT**
- FORMAL_PROOF.md (theory): 10 stages
- ARCHITECTURE.md (implementation): 12 stages

**Possible explanation:** Implementation added 2 stages not in formal model

### 6.2 Pipeline Stage Order (FORMAL_PROOF.md:336)

```
S1 → S2 → S3/S4 → S6 → S7 → S8 → S5 → S9 → S10
```

Note: S3/S4 parallel, S5 comes after S8

---

## 7. EMPIRICAL DATA

### 7.1 Node Counts

| File:Line | Claim | Context |
|-----------|-------|---------|
| FORMAL_PROOF.md:19 | "212,052 nodes across 33 repositories" | Abstract |
| FORMAL_PROOF.md:167 | "212,052 code elements" | Theorem 3.1 proof |
| FORMAL_PROOF.md:467 | "212,052" Total code elements | Experiment 5.1 |
| FORMAL_PROOF.md:214 | "139,323 analyzed nodes" | Theorem 3.2 proof |

**VERDICT: INTERNAL INCONSISTENCY**
- 212,052 = total parsed
- 139,323 = analyzed for roles (subset?)

**Question:** Why are these different? Filtered elements?

### 7.2 Repository Count

| File:Line | Claim | Match |
|-----------|-------|-------|
| FORMAL_PROOF.md:19 | "33 repositories" | ✓ |
| FORMAL_PROOF.md:295 | "33-repo benchmark" | ✓ |
| FORMAL_PROOF.md:465 | "Repositories analyzed \| 33" | ✓ |

**VERDICT: CONSISTENT** - 33 repositories

### 7.3 Language Coverage

| File:Line | Claim |
|-----------|-------|
| FORMAL_PROOF.md:466 | "Languages covered \| Python, JavaScript" |

---

## 8. THEOREMS

### 8.1 Theorem Count

| File:Line | Claim |
|-----------|-------|
| THEORY_MAP.md:26 | "Theorems 3.1-3.8" |
| MECHANIZED_PROOFS.md:14 | "Theorems 3.3, 3.4, 3.5, 3.7, 3.8, 4.1, 4.2, 4.3" (8 pure math) |
| MECHANIZED_PROOFS.md:15 | "Theorems 3.1, 3.2, 3.6" (3 with axioms) |
| FORMAL_PROOF.md:589 | "Pure Mathematics (8 theorems)" |
| FORMAL_PROOF.md:602 | "With Axioms - Empirically Validated (3 theorems)" |

**VERDICT: CONSISTENT** - 11 theorems total (8 pure + 3 with axioms)

### 8.2 Lean Verification Status

| Theorem | Status per MECHANIZED_PROOFS.md |
|---------|--------------------------------|
| 3.1 WHAT Completeness | ✓ Verified (axioms) |
| 3.2 WHY Completeness | ✓ Verified (axioms) |
| 3.3 RPBL Boundedness | ✓ Verified |
| 3.4 Total Space Boundedness | ✓ Verified |
| 3.5 Minimality | ✓ Verified |
| 3.6 Orthogonality | ✓ Verified (axioms) |
| 3.7 Pipeline DAG | ✓ Verified |
| 3.8 Schema Minimality | ✓ Verified |
| 4.1 Algorithm Totality | ✓ Verified |
| 4.2 Determinism | ✓ Verified |
| 4.3 State Management | ✓ Verified |

---

## 9. CONFIDENCE SCORES

### 9.1 Confidence Range

| File:Line | Claim |
|-----------|-------|
| CANONICAL_SCHEMA.md:73 | "role_confidence": 0.95 (example) |
| CANONICAL_SCHEMA.md:81 | "Confidence score (0-100)" |
| CANONICAL_SCHEMA.md:251 | "Detection confidence (0-100)" |

**Note:** Schema says 0-100 scale, example shows 0.95 (0-1 scale)

---

## 10. MUTUAL INFORMATION (Orthogonality)

| Dimension Pair | Value (FORMAL_PROOF.md:299-301) |
|----------------|--------------------------------|
| WHAT ↔ WHY | 0.12 bits |
| WHAT ↔ HOW | 0.08 bits |
| WHY ↔ HOW | 0.15 bits |

---

## 11. PERFORMANCE CLAIMS

| Metric | Value | File:Line |
|--------|-------|-----------|
| Throughput | 1,860 nodes/second | FORMAL_PROOF.md:486 |
| Django benchmark | 56,000+ nodes in 19s | FORMAL_PROOF.md:487 |
| Memory usage | < 500MB | FORMAL_PROOF.md:488 |

---

## CRITICAL ACTIONS REQUIRED

### Priority 1: Update FORMAL_PROOF.md to V2 Theory

FORMAL_PROOF.md is the most impactful file to update. It documents V1 theory but V2 is current.

**Changes needed:**
1. **Role count**: 27 → 33 (line 65, 174)
2. **Role list**: Replace 27-role table with 33-role table (lines 549-579)
3. **Semantic space**: 45,090,000 → 55,110,000 (line 249)
4. **Appendix 8**: Replace with V2 roles from `schema/fixed/roles.json`

### Priority 2: Update Dependent Documents

1. **MECHANIZED_PROOFS.md:86** - Update semantic space claim
2. **Lean proofs** - Update `proofs/lean/` for new role count and space size

### Priority 3: Standardize Terminology

1. **RPBL Range** - Decide: integers [1,10] or floats 0-10?
   - If floats: Update FORMAL_PROOF.md
   - If integers: Update GLOSSARY.md
2. **Layer Names** - Standardize "UI" vs "Presentation"
3. **Pipeline Stages** - FORMAL_PROOF says 10, implementation has 12
   - Either update theory or explain the discrepancy

### Priority 4: Clarify Internal Inconsistencies

1. **Node Counts** (212,052 vs 139,323)
   - Add explanation: "Total parsed" vs "role-analyzed subset"

---

## File Cross-Reference

| File | Primary Content | Version Status |
|------|-----------------|----------------|
| FORMAL_PROOF.md | Mathematical proofs | **V1 (NEEDS UPDATE)** |
| schema/fixed/roles.json | Role definitions | **V2 (CANONICAL)** |
| ATOMS_REFERENCE.md | Atom listing | V2 ✓ |
| GLOSSARY.md | Term definitions | Needs RPBL fix |
| PURPOSE_FIELD.md | Purpose theory | V2 ✓ |
| ARCHITECTURE.md | System architecture | V2 ✓ (12 stages) |
| MECHANIZED_PROOFS.md | Lean verification | **V1 (NEEDS UPDATE)** |
| THEORY_MAP.md | Conceptual hierarchy | V2 ✓ |
| CANONICAL_SCHEMA.md | Schema spec | Needs confidence scale fix |
