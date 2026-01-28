# DEFINITION OF DONE - v1 Core

**📍 Governance:** [DECISIONS](./DECISIONS.md) | [ROADMAP](./ROADMAP.md) | [Quality Gates](./QUALITY_GATES.md)
**📊 Architecture:** [SUBSYSTEMS.yaml](./SUBSYSTEMS.yaml) | [DOMAINS.yaml](./DOMAINS.yaml) | [PIPELINES.md](./PIPELINES.md)

**Purpose:** Clear finish line that prevents "almost done" forever
**Authority:** ChatGPT 5.2 Pro audit recommendations
**Updated:** 2026-01-28

---

## v1 Core is DONE when ALL of these are TRUE:

### 1. Canonical Registries Established ✅

- [x] SUBSYSTEMS.yaml exists and validates
- [x] DOMAINS.yaml exists with all 5 domains
- [x] Atom YAML files (T0/T1/T2) have zero duplicate IDs
- [ ] Pipeline stages encoded in canonical registry
- [ ] Dimensions encoded in canonical registry

**Current:** 3/5 complete

---

### 2. Verification Passes (5/5 Gates) 🟡

- [x] Atom uniqueness: All IDs unique within each YAML
- [ ] Count consistency: Generated indexes match registries
- [ ] Link integrity: Zero broken links in active docs
- [ ] Placeholder check: No unresolved `{...}` in active
- [ ] Validation naming: All "validated_*" have PASS/FAIL header

**Current:** 1/5 gates pass

---

### 3. One Command Verifies Everything 🔴

```bash
./pe verify v1
```

**Must check:**
- Atom ID uniqueness across all YAML files
- Count drift between registries and generated docs
- Broken links in active docs (not archive)
- Unresolved placeholders in active
- "validated_*" file integrity

**Exit code:** 0 = ship, non-zero = blocked

**Current:** Script doesn't exist yet

---

### 4. Generated Outputs Exist and Are Fresh 🔴

All of these MUST be generated from canonical sources:

- [ ] `ATOM_INDEX.md` (from `src/patterns/*.yaml`)
- [ ] `PIPELINE_SUMMARY.md` (from code)
- [ ] `SUBSYSTEM_MAP.md` (from `SUBSYSTEMS.yaml`)
- [ ] `DOMAIN_SYMMETRY_REPORT.md` (from `DOMAINS.yaml`)

**Headers required:**
```markdown
<!-- GENERATED from SUBSYSTEMS.yaml by generate_map.py v1.0.0 on 2026-01-27 -->
```

**Current:** None exist

---

### 5. Documentation is Navigable 🔴

- [ ] Root `INDEX.md` links to all subsystems
- [ ] Every subsystem has its own INDEX
- [ ] Every active doc is reachable from root
- [ ] Orphan count: 0 (currently 733/788)

**Measurement:**
```bash
python tools/check_orphans.py --active-only
# Must return: 0 orphans
```

**Current:** 733 orphans (93%)

---

### 6. Core Workflows Documented 🟡

- [x] How to run Collider (`CLAUDE.md`)
- [x] How to query analyze.py (`AI_USER_GUIDE.md`)
- [ ] How to verify integrity (`./pe verify`)
- [ ] How to regenerate indexes (`./pe generate`)
- [ ] How to extend (add atom, add stage, add domain)

**Current:** 2/5 complete

---

### 7. Drift is Mechanically Prevented 🔴

**Requirements:**
- Pre-commit hook runs `./pe verify v1` (lightweight)
- CI runs full verification suite
- Counts are NEVER hand-typed in docs
- "Canonical" claims are validated

**Current:** No hooks for this yet

---

### 8. Archive is Separated 🔴

- [ ] `archive/` contains all deprecated/historical material
- [ ] Active docs don't reference archive content
- [ ] Misleading artifacts renamed or moved

**Artifacts to fix:**
- `validated_theory.md` (stack trace, not validation)
- `validated_pipeline.md` (partial failure)
- `orphans_report.md` (absolute paths)

**Current:** Artifacts still in root

---

## ACCEPTANCE CRITERIA

### Minimum Viable v1

```
✅ All P0 gates pass (5/5)
✅ ./pe verify v1 exits 0
✅ Generated outputs exist and are fresh
✅ Zero orphan docs in active
✅ Extension guide complete
```

### Extended v1 (nice-to-have)

```
⏸️ All P1 gates pass
⏸️ CI/CD pipeline integrated
⏸️ Documentation site generated
⏸️ Release notes published
```

---

## PROGRESS TRACKER

| Criterion | Status | Blocker |
|-----------|--------|---------|
| Registries | 🟡 60% | Need pipeline + dimensions |
| Gates | 🔴 20% | 4/5 failing |
| Verify command | 🔴 0% | Script doesn't exist |
| Generated outputs | 🔴 0% | Generators don't exist |
| Navigability | 🔴 7% | 733 orphans |
| Workflows | 🟡 40% | Missing verify/generate docs |
| Drift prevention | 🔴 0% | No hooks |
| Archive separation | 🔴 0% | Artifacts in root |

**Overall:** 🔴 25% complete

---

## THE SHIPPING RULE

```
IF all 8 criteria are TRUE:
  THEN tag v1.0.0 and celebrate
  ELSE identify THE blocker and fix it
       (only 1 blocker at a time)
```

**Current blocker:** Verification script doesn't exist

**Next blocker after that:** 733 orphan docs

---

**This is the finish line. When everything above is ✅, we ship.**
