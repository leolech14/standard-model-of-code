# QUALITY GATES - Automated Integrity Checks

**📍 Governance:** [DECISIONS](./DECISIONS.md) | [ROADMAP](./ROADMAP.md) | [Definition of Done](./DEFINITION_OF_DONE.md)
**📊 Architecture:** [SUBSYSTEMS.yaml](./SUBSYSTEMS.yaml) | [DOMAINS.yaml](./DOMAINS.yaml) | [PIPELINES.md](./PIPELINES.md)

**Purpose:** Mechanical gates that prevent drift and enforce canonical registries
**Authority:** ChatGPT 5.2 Pro audit + "prevent unfinished" strategy
**Updated:** 2026-01-28

---

## GATE ARCHITECTURE

```
┌─────────────────────────────────────────┐
│   Commit Attempt                        │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│   Pre-commit Hook                       │
│   Runs: ./pe verify --quick            │
│   Time limit: 10 seconds               │
└─────────────────┬───────────────────────┘
                  ↓
         ┌────────┴────────┐
         ↓                 ↓
    P0 Gates          P1 Gates
    (MUST pass)       (SHOULD pass)
         ↓                 ↓
    ✅ All pass       ⚠️ Warnings
         ↓                 ↓
    Commit OK         Commit OK
                          ↓
┌─────────────────────────────────────────┐
│   CI Pipeline (on push)                 │
│   Runs: ./pe verify --full             │
│   Time limit: 5 minutes                │
└─────────────────┬───────────────────────┘
                  ↓
         All P0 + P1 gates
                  ↓
            ✅ Deploy OK
```

---

## P0 GATES (MUST PASS - Block Commit)

### G1: Atom ID Uniqueness ✅

**Rule:** All atom IDs must be unique within each YAML file.

**Check:**
```bash
python tools/verify_atoms.py --check-duplicates
# Exit 0 = pass, non-zero = fail
```

**Threshold:** 0 duplicates allowed

**Current status:** ✅ PASS (fixed 2026-01-27)

**Failure example:**
```
❌ GATE FAILED: G1 Atom Uniqueness
Found 16 duplicate IDs in ATOMS_T2_OTHER.yaml:
  - EXT.CRYPTO.SEC.001 (2x)
  - EXT.CRYPTO.SEC.002 (2x)
  ...
Fix: Remove duplicates from YAML file
```

---

### G2: Registry Count Consistency ❌

**Rule:** Generated indexes must match source registries.

**Check:**
```bash
python tools/verify_counts.py
# Compares ATOMS_UNIVERSAL_INDEX counts vs actual YAML
# Compares PIPELINE_STAGES count vs src/core/pipeline/stages/
```

**Threshold:** 0 mismatches allowed

**Current status:** ❌ FAIL
- Atoms: Index claims T0=43 T1=24, registry has T0=42 T1=21
- Pipeline: STAGES.md says 28, REGISTRY says 18

**Failure example:**
```
❌ GATE FAILED: G2 Count Consistency
Atom count mismatch:
  Index: T0=43, T1=24
  Registry: T0=42, T1=21
  Δ: T0=-1, T1=-3

Pipeline stage mismatch:
  PIPELINE_STAGES.md: 28 stages
  REGISTRY_OF_REGISTRIES.md: 18 stages
  Δ: -10 stages

Fix: Regenerate indexes from canonical sources
```

---

### G3: Active Link Integrity ❌

**Rule:** Zero broken internal links in active docs.

**Check:**
```bash
python tools/verify_links.py --active-only
# Scans all .md in active, checks local links
# Ignores: archive/, http://, mailto:
```

**Threshold:** 0 broken links in active

**Current status:** ❌ FAIL (14 broken links in non-archive docs)

**Failure example:**
```
❌ GATE FAILED: G3 Link Integrity
Broken links in active docs (14):
  context-management/docs/deep/PURPOSE_EMERGENCE.md:23
    → ../standard-model-of-code/MODEL.md (should be ../../)

  .agent/registry/INDEX.md:45
    → standard-model-of-code/docs/OPEN_CONCERNS.md (wrong path)

Fix: Correct relative paths or use root-relative (/path/to/file)
```

---

### G4: No Unresolved Placeholders ❌

**Rule:** Active docs cannot contain unresolved `{...}`, `TODO`, `FIXME` without linked issues.

**Check:**
```bash
python tools/verify_placeholders.py --active-only
# Scans for: {integration_status}, TODO, FIXME, XXX
# Allows: TODO(#123) or {value|default}
```

**Threshold:** 0 unresolved placeholders

**Current status:** ❌ FAIL
- `.agent/intelligence/SKEPTICAL_AUDIT_20260126.md` has `{integration_status}`

**Failure example:**
```
❌ GATE FAILED: G4 Placeholder Check
Unresolved placeholders (3):
  .agent/intelligence/SKEPTICAL_AUDIT_20260126.md:456
    → {integration_status}

  docs/specs/PIPELINE.md:89
    → TODO: Add stage 29
    (No issue linked)

Fix: Fill placeholders OR link to issues OR move to archive
```

---

### G5: Validation Artifact Integrity ❌

**Rule:** Files named `validated_*` must contain PASS/FAIL header.

**Check:**
```bash
python tools/verify_validated.py
# Scans for validated_*.md, checks for:
#   Status: PASS | FAIL | PARTIAL
```

**Threshold:** 100% of validated_* files have status header

**Current status:** ❌ FAIL
- `validated_theory.md` is a stack trace (no header)
- `validated_pipeline.md` has failures but unclear status

**Failure example:**
```
❌ GATE FAILED: G5 Validation Naming
Misleading validation artifacts (2):
  validated_theory.md
    → Contains stack trace, no PASS/FAIL header
    → Rename to: FAILED_theory_validation_20260126.md

  validated_pipeline.md
    → Partial results, unclear status
    → Add header: Status: PARTIAL (3/10 passed)

Fix: Rename OR add status header
```

---

## P1 GATES (SHOULD PASS - Warning Only)

### G6: Subsystem Symmetry ⚠️

**Rule:** Every subsystem must have both code and context directories.

**Check:**
```bash
python tools/verify_symmetry.py
# Reads SUBSYSTEMS.yaml, checks if paths exist
```

**Threshold:** 100% symmetry

**Current status:** ⚠️ UNKNOWN (needs verification script)

---

### G7: Documentation Coverage ⚠️

**Rule:** Every public function/class must have docstring.

**Check:**
```bash
python tools/verify_docstrings.py
```

**Threshold:** >80% coverage

**Current status:** ⚠️ UNKNOWN

---

### G8: Test Coverage ⚠️

**Rule:** Core modules must have test coverage.

**Check:**
```bash
pytest --cov=src/core --cov-report=term
```

**Threshold:** >70% coverage

**Current status:** ⚠️ UNKNOWN (422 tests pass, but coverage unknown)

---

## GATE EXECUTION

### Pre-commit (Quick - <10s)

```bash
#!/bin/bash
# .git/hooks/pre-commit

./pe verify --quick || {
  echo "❌ Quality gates failed"
  echo "Run: ./pe verify --fix"
  exit 1
}
```

**Runs:** G1, G3 (quick scans only)

---

### CI Pipeline (Full - <5min)

```bash
#!/bin/bash
# .github/workflows/verify.yml

./pe verify --full || {
  echo "❌ Full verification failed"
  exit 1
}
```

**Runs:** All P0 + P1 gates

---

### Manual Verification

```bash
# Check all gates
./pe verify v1

# Check specific gate
./pe verify atoms
./pe verify links
./pe verify counts

# Fix mode (auto-fix what's possible)
./pe verify --fix
```

---

## GATE STATUS DASHBOARD

Run: `./pe verify status`

```
╔════════════════════════════════════════════════════════════════╗
║                    QUALITY GATES STATUS                        ║
╚════════════════════════════════════════════════════════════════╝

P0 GATES (Must Pass):
  ✅ G1: Atom Uniqueness        0 duplicates
  ❌ G2: Count Consistency      3 mismatches
  ❌ G3: Link Integrity         14 broken links
  ❌ G4: Placeholder Check      3 unresolved
  ❌ G5: Validation Naming      2 misleading files

P1 GATES (Should Pass):
  ⚠️  G6: Subsystem Symmetry    Unknown (need script)
  ⚠️  G7: Doc Coverage          Unknown (need script)
  ⚠️  G8: Test Coverage         Unknown (422 tests pass)

OVERALL: 🔴 1/5 P0 gates pass — v1 BLOCKED

Next action: Fix G2 (count consistency)
```

---

## FIXING FAILURES

### When a gate fails:

1. **Understand the failure**
   - Read the error message
   - Check the evidence file

2. **Pick ONE fix approach:**
   - Fix the data (correct the registry)
   - Fix the reference (update generated doc)
   - Archive the problem (move to archive/)

3. **Apply the fix**
   - Make the change
   - Re-run verification
   - Commit if passes

4. **Never skip gates**
   - Use `--no-verify` only for emergencies
   - Fix the gate, don't bypass it

---

## RELEASE CRITERIA

### v1.0.0 Can Ship When:

```
✅ All P0 gates pass (5/5)
✅ ./pe verify v1 exits 0
✅ Generated outputs exist and fresh
✅ Orphan count = 0
✅ Archive is separated
```

### v1.1.0+ Can Ship When:

```
✅ v1.0.0 criteria +
✅ All P1 gates pass
✅ New feature added AND verified
```

---

**Gates are immutable. To ship, you pass them. To bypass, you downgrade the gate priority (requires DECISIONS.md entry).**
