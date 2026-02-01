# Fact Cross-Reference Table

> **Purpose:** Track which nodes claim which facts, detect contradictions, guide consolidation
> **Generated:** 2026-01-19

---

## FACT: Atom Count

| Node ID | File:Line | Claims | Status |
|---------|-----------|--------|--------|
| `DATM.PRO.2` | ATOMS_REFERENCE.md:280 | 167 atoms | OUTDATED |
| `DFRM.ABS.1` | FORMAL_PROOF.md:16 | 167-atom taxonomy | OUTDATED |
| `DFRM.THE31.5` | FORMAL_PROOF.md:165 | 167 atoms | OUTDATED |
| `DCON.4THE.1` | CONSOLIDATED_UNDERSTANDING.md:120 | 200 T0 atoms | CURRENT |
| `DCON.SUM.1` | CONSOLIDATED_UNDERSTANDING.md:281 | 200 atoms → ~15 IDs | CURRENT |

**Truth:** 200 named atoms in 200_ATOMS.md → ~15 base IDs in implementation
**Action:** Update DATM.PRO.2, DFRM.ABS.1, DFRM.THE31.5 to 200

---

## FACT: Role Count

| Node ID | File:Line | Claims | Status |
|---------|-----------|--------|--------|
| `DFRM.8APP.1` | FORMAL_PROOF.md:549 | 27 roles | OUTDATED |
| `DFRM.THE37.3` | FORMAL_PROOF.md:321 | 33 atoms (mislabeled?) | CHECK |
| `DCAN.SCHVAL.1` | CANONICAL_SCHEMA.md:346 | 33-role taxonomy | CURRENT |
| `DCON.5THE.1` | CONSOLIDATED_UNDERSTANDING.md:165 | 33 roles | CURRENT |
| `DCON.SUM.2` | CONSOLIDATED_UNDERSTANDING.md:283 | 33 canonical, 29 implemented | CURRENT |
| `DDIS.CURDET.2` | DISCOVERY_PROCESS.md:81 | 33 canonical roles | CURRENT |
| `DPUR.STA1.1` | PURPOSE_FIELD.md:208 | 33 roles | CURRENT |

**Truth:** 33 canonical (roles.json), 29 implemented (heuristic_classifier.py)
**Action:** Update DFRM.8APP.1 from 27 → 33

---

## FACT: Family Count

| Node ID | File:Line | Claims | Status |
|---------|-----------|--------|--------|
| `DATM.ATOREF.1` | ATOMS_REFERENCE.md:8 | 16 families | OUTDATED |
| `DATM.FORAI.1` | ATOMS_REFERENCE.md:15 | 16 families | OUTDATED |
| `DFRM.THE31.4` | FORMAL_PROOF.md:144 | 16 families | OUTDATED |
| `DTHM.THE16.1` | THEORY_MAP.md:260 | 16 families | OUTDATED |
| `DTHM.THE16.2` | THEORY_MAP.md:264 | 16 families | OUTDATED |
| `DTHM.THE16.4` | THEORY_MAP.md:285 | 16 families | OUTDATED |

**Truth:** 22 families (from 200_ATOMS.md)
**Action:** Update all from 16 → 22

---

## FACT: Level Count / Scale

| Node ID | File:Line | Claims | Status |
|---------|-----------|--------|--------|
| `DCON.2THE.1` | CONSOLIDATED_UNDERSTANDING.md:40 | 16 levels L-3→L12 | CURRENT |
| `DCON.2THE.2` | CONSOLIDATED_UNDERSTANDING.md:42 | 16 levels | CURRENT |
| `DCON.SUM.3` | CONSOLIDATED_UNDERSTANDING.md:284 | 16 levels, 5 zones | CURRENT |

**Truth:** 16 levels (L-3 to L12), 5 zones
**Action:** None - already correct in CONSOLIDATED

---

## FACT: Pipeline Stages

| Node ID | File:Line | Claims | Status |
|---------|-----------|--------|--------|
| `DFRM.THE37.2` | FORMAL_PROOF.md:320 | 10 stages | OUTDATED |

**Truth:** 12 stages (from implementation)
**Action:** Update DFRM.THE37.2 from 10 → 12

---

## FACT: RPBL Range

| Node ID | File:Line | Claims | Status |
|---------|-----------|--------|--------|
| (GLOSSARY implicit) | GLOSSARY.md | Float 0-10 | OUTDATED |
| (FORMAL_PROOF implicit) | FORMAL_PROOF.md | Integer [1,10] | CLOSE |

**Truth:** Integers 1-9 (from canonical_types.json)
**Action:** Fix GLOSSARY to integers

---

## STATISTICS

### By Fact Type

| Fact | Nodes | Outdated | Current | % Outdated |
|------|-------|----------|---------|------------|
| Atom Count | 5 | 3 | 2 | 60% |
| Role Count | 7 | 1 | 6 | 14% |
| Family Count | 6 | 6 | 0 | 100% |
| Level Count | 3 | 0 | 3 | 0% |
| Pipeline Stages | 1 | 1 | 0 | 100% |
| **TOTAL** | **22** | **11** | **11** | **50%** |

### By File

| File | Nodes with Facts | Outdated | Fix Priority |
|------|------------------|----------|--------------|
| FORMAL_PROOF.md | 6 | 5 | **HIGH** |
| ATOMS_REFERENCE.md | 3 | 3 | **HIGH** |
| THEORY_MAP.md | 3 | 3 | **HIGH** |
| CONSOLIDATED_UNDERSTANDING.md | 5 | 0 | NONE |
| CANONICAL_SCHEMA.md | 1 | 0 | NONE |
| DISCOVERY_PROCESS.md | 1 | 0 | NONE |
| PURPOSE_FIELD.md | 1 | 0 | NONE |

---

## CONSOLIDATION PRIORITY

### Tier 1: Must Fix (blocks understanding)

| Node ID | File:Line | Fix |
|---------|-----------|-----|
| `DFRM.ABS.1` | FORMAL_PROOF.md:16 | 167 → 200 |
| `DFRM.THE31.5` | FORMAL_PROOF.md:165 | 167 → 200 |
| `DFRM.8APP.1` | FORMAL_PROOF.md:549 | 27 → 33 |
| `DFRM.THE37.2` | FORMAL_PROOF.md:320 | 10 → 12 stages |

### Tier 2: Should Fix (consistency)

| Node ID | File:Line | Fix |
|---------|-----------|-----|
| `DATM.PRO.2` | ATOMS_REFERENCE.md:280 | 167 → 200 |
| `DATM.ATOREF.1` | ATOMS_REFERENCE.md:8 | 16 → 22 families |
| `DATM.FORAI.1` | ATOMS_REFERENCE.md:15 | 16 → 22 families |

### Tier 3: Nice to Fix (complete alignment)

| Node ID | File:Line | Fix |
|---------|-----------|-----|
| `DTHM.THE16.1` | THEORY_MAP.md:260 | 16 → 22 families |
| `DTHM.THE16.2` | THEORY_MAP.md:264 | 16 → 22 families |
| `DTHM.THE16.4` | THEORY_MAP.md:285 | 16 → 22 families |
| `DFRM.THE31.4` | FORMAL_PROOF.md:144 | 16 → 22 families |

---

## NEXT: Populate Consolidated Files

Once fixes are applied:

1. **CONSOLIDATED_UNDERSTANDING.md** - Already current, serves as truth source
2. **FORMAL_PROOF.md** - Apply Tier 1 fixes, becomes V2-aligned
3. **ATOMS_REFERENCE.md** - Apply Tier 2 fixes OR deprecate in favor of 200_ATOMS.md
4. **THEORY_MAP.md** - Apply Tier 3 fixes

---
