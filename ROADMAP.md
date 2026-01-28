# ROADMAP - Path to v1.0.0

**Purpose:** Clear path from current state to shippable v1
**Strategy:** Fix gates in priority order, ship when 5/5 pass
**Updated:** 2026-01-27

---

## CURRENT STATE (Baseline)

**Progress:** 🔴 25% complete (1/5 P0 gates passing)

| Gate | Status | Blocker |
|------|--------|---------|
| G1: Atom uniqueness | ✅ PASS | - |
| G2: Count consistency | ❌ FAIL | Index≠registry |
| G3: Link integrity | ❌ FAIL | 14 broken links |
| G4: Placeholder check | ❌ FAIL | 3 unresolved |
| G5: Validation naming | ❌ FAIL | 2 misleading files |

**Deliverables complete:**
- ✅ Duplicate atoms fixed (16 removed)
- ✅ SUBSYSTEMS.yaml created
- ✅ DOMAINS.yaml created
- ✅ DECISIONS.md locked
- ✅ Documentation organized (INDEX, THEORY_MAP)

---

## PHASE 1: Stabilize Canon (Week 1)

**Goal:** Stop the bleeding - fix all P0 drift

### Task 1.1: Fix Count Drift (2 hours)

**Blocker:** Generated indexes don't match registries

**Actions:**
1. Count atoms in YAML files → write canonical_counts.json
2. Regenerate ATOMS_UNIVERSAL_INDEX.yaml from YAML sources
3. Count pipeline stages in code → stages.json
4. Regenerate PIPELINE_STAGES.md from stages.json
5. Add generator headers to all generated files

**Deliverable:** G2 gate passes

---

### Task 1.2: Fix Broken Links (1 hour)

**Blocker:** 14 broken links in active docs

**Actions:**
1. Run link checker: `python tools/verify_links.py --active-only --list`
2. Fix top 5 (highest priority):
   - `context-management/docs/deep/PURPOSE_EMERGENCE.md` (wrong ../)
   - `.agent/registry/INDEX.md` (wrong path to OPEN_CONCERNS)
   - Gemini research doc (wrong relative path)
3. Standardize on root-relative links (`/path/from/root`)
4. Re-run verification

**Deliverable:** G3 gate passes

---

### Task 1.3: Resolve Placeholders (30 min)

**Blocker:** 3 unresolved placeholders in active docs

**Actions:**
1. `.agent/intelligence/SKEPTICAL_AUDIT_20260126.md` → fill `{integration_status}` or archive
2. Any `TODO` without issue → create issue or archive
3. Re-run verification

**Deliverable:** G4 gate passes

---

### Task 1.4: Fix Validation Artifacts (15 min)

**Blocker:** Misleading "validated_*" files

**Actions:**
1. Rename `validated_theory.md` → `archive/FAILED_theory_validation_20260126.md`
2. Add header to `validated_pipeline.md`: `Status: PARTIAL (3/10 passed)`
3. Update any references to these files

**Deliverable:** G5 gate passes

---

**Phase 1 Complete:** 🟢 5/5 P0 gates pass (4 hours total)

---

## PHASE 2: Build Verification Tooling (Week 2)

**Goal:** Make gates mechanical, not manual

### Task 2.1: Create verify_atoms.py (1 hour)

```python
#!/usr/bin/env python3
# tools/verify_atoms.py

import yaml, sys
from pathlib import Path
from collections import Counter

def check_duplicates(yaml_file):
    with open(yaml_file) as f:
        data = yaml.safe_load(f)
    ids = [a['id'] for a in data.get('atoms', [])]
    dupes = {id: count for id, count in Counter(ids).items() if count > 1}
    return dupes

# Check all atom YAML files
# Exit 0 if all unique, 1 if duplicates found
```

**Deliverable:** `./pe verify atoms` works

---

### Task 2.2: Create verify_links.py (2 hours)

**Features:**
- Scan all .md files in active dirs
- Extract local links (skip http://, mailto:)
- Resolve relative vs root-relative
- Report broken + suggest fixes
- `--fix` mode: auto-correct common issues

**Deliverable:** `./pe verify links` works

---

### Task 2.3: Create verify_counts.py (1 hour)

**Logic:**
1. Load canonical registries (YAML)
2. Load generated indexes (MD/YAML)
3. Compare counts
4. Report mismatches

**Deliverable:** `./pe verify counts` works

---

### Task 2.4: Create verify_placeholders.py (30 min)

**Regex patterns:**
- `\{[a-z_]+\}` (unresolved variables)
- `TODO(?!\(#\d+\))` (TODO without issue)
- `FIXME(?!\(#\d+\))`

**Deliverable:** `./pe verify placeholders` works

---

### Task 2.5: Create verify_validated.py (30 min)

**Check:**
- Files matching `validated_*.md`
- Must contain `Status: PASS|FAIL|PARTIAL` in first 50 lines

**Deliverable:** `./pe verify validated` works

---

### Task 2.6: Integrate into ./pe verify (1 hour)

**Create:** `tools/verify.py` master script

```bash
./pe verify v1        # Run all P0 gates
./pe verify --full    # Run all P0 + P1 gates
./pe verify --quick   # Run fast gates only (pre-commit)
./pe verify atoms     # Run specific gate
./pe verify --fix     # Auto-fix what's possible
./pe verify status    # Show gate dashboard
```

**Deliverable:** One command verifies everything

---

**Phase 2 Complete:** 🟢 Verification is automated (6 hours total)

---

## PHASE 3: Generate Outputs (Week 3)

**Goal:** Auto-generate all derived docs from canonical registries

### Task 3.1: Generate atom index (1 hour)

```bash
python tools/generate_atom_index.py
# Input: src/patterns/*.yaml
# Output: generated/ATOM_INDEX.md (with header)
```

**Deliverable:** Atom counts always match registry

---

### Task 3.2: Generate pipeline summary (1 hour)

```bash
python tools/generate_pipeline_summary.py
# Input: src/core/pipeline/stages/__init__.py
# Output: generated/PIPELINE_SUMMARY.md
```

**Deliverable:** Pipeline stage count always matches code

---

### Task 3.3: Generate subsystem map (30 min)

```bash
python tools/generate_subsystem_map.py
# Input: SUBSYSTEMS.yaml
# Output: generated/SUBSYSTEM_MAP.md
```

---

### Task 3.4: Generate domain symmetry report (1 hour)

```bash
python tools/generate_domain_report.py
# Input: DOMAINS.yaml
# Output: generated/DOMAIN_SYMMETRY_REPORT.md
# Checks: code exists, context exists, links resolve
```

---

**Phase 3 Complete:** 🟢 All core docs auto-generated (3.5 hours total)

---

## PHASE 4: Fix Navigability (Week 4)

**Goal:** Zero orphan docs - everything reachable from INDEX.md

### Task 4.1: Add @PROVIDES/@DEPENDS_ON to all active docs (3 hours)

**Pattern:**
```markdown
<!--
@PROVIDES: Pipeline, Stage, Analysis
@DEPENDS_ON: THEORY_AXIOMS, MODEL
-->
```

**Tool:** `python tools/add_doc_metadata.py --scan`

---

### Task 4.2: Generate backlinks (1 hour)

```bash
python tools/generate_backlinks.py
# Scans all @PROVIDES
# Adds "Referenced by" footer to each doc
```

---

### Task 4.3: Build doc graph (1 hour)

```bash
python tools/build_doc_graph.py
# Output: DOC_GRAPH.json
# Visualization: docs/DOC_GRAPH.html
```

**Deliverable:** Can visualize doc connectivity, find orphans

---

### Task 4.4: Fix orphans (2 hours)

**Strategies:**
- Add to subsystem INDEX
- Add @PROVIDES
- Archive if obsolete

**Deliverable:** 0 orphans in active

---

**Phase 4 Complete:** 🟢 All docs navigable (7 hours total)

---

## PHASE 5: Package and Ship v1 (Week 5)

**Goal:** Create shippable v1_core/ package

### Task 5.1: Create v1_core/ structure (1 hour)

```
v1_core/
├── README.md (what is v1)
├── registries/ (SUBSYSTEMS, DOMAINS, atoms)
├── verification/ (5 scripts)
├── generated/ (indexes, summaries)
├── docs/ (THEORY_AXIOMS, MODEL, guides)
└── MANIFEST.md (complete file list)
```

---

### Task 5.2: Write extension guide (2 hours)

`v1_core/docs/EXTENSION_GUIDE.md`:
- How to add a new atom
- How to add a pipeline stage
- How to add a domain
- How to verify your addition

---

### Task 5.3: Final verification (30 min)

```bash
cd v1_core/
./verify v1
# Must exit 0
```

---

### Task 5.4: Tag and release (30 min)

```bash
git tag -a v1.0.0 -m "Contextome v1 Core - Registry-first, drift-proof"
git push origin v1.0.0
```

**Deliverable:** v1.0.0 released 🎉

---

**Phase 5 Complete:** 🟢 v1 SHIPPED (4 hours total)

---

## TIMELINE SUMMARY

| Phase | Duration | Deliverable | Status |
|-------|----------|-------------|--------|
| Phase 1 | 4 hrs | 5/5 P0 gates pass | 🔴 25% (1/5) |
| Phase 2 | 6 hrs | Verification automated | 🔴 0% |
| Phase 3 | 3.5 hrs | Outputs auto-generated | 🔴 0% |
| Phase 4 | 7 hrs | Docs interconnected | 🔴 0% |
| Phase 5 | 4 hrs | v1 packaged and released | 🔴 0% |

**Total:** 24.5 hours to v1.0.0

**Current:** Hour 4 complete (duplicate atoms fixed, registries created)

**Remaining:** 20.5 hours

---

## ANTI-STALL RULES

### Rule 1: One Blocker at a Time
Don't work on multiple P0 issues. Fix G2, then G3, then G4, then G5.

### Rule 2: No New Features Until Gates Pass
If gates fail, you can ONLY:
- Fix the gate
- Archive the blocker
- Improve verification

### Rule 3: Archive Early, Archive Often
If something blocks progress for >2 hours → archive it.

### Rule 4: Every Session Ships Something
See DEFINITION_OF_DONE.md - no research-only sessions.

---

## VELOCITY TRACKING

### This Session (2026-01-27)
- ✅ Fixed 16 duplicate atoms (G1: PASS)
- ✅ Created SUBSYSTEMS.yaml
- ✅ Created DOMAINS.yaml
- ✅ Documented 540 lines of viz changes
- ✅ Built 2,148 lines of knowledge artifacts

**Progress:** 1/5 gates → 20% closer to v1

---

## NEXT SESSION (Priority Order)

1. **Task 1.1** - Fix count drift (G2)
2. **Task 2.3** - Create verify_counts.py
3. **Task 1.2** - Fix 14 broken links (G3)
4. **Task 2.2** - Create verify_links.py

**Target:** 3/5 gates passing by end of next session

---

**The finish line is clear. 20 hours to v1. No more "almost done."**
