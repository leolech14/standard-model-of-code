# Consolidation Decision Matrix
## Data-Driven Cleanup Strategy

**Based on:** REPO_CENSUS.md (2026-01-28)
**Purpose:** Translate totals into actionable decisions

---

## 📊 THE PROBLEM IN NUMBERS

```
Current State:
- 19,067 files (13GB)
- 77M lines of JSON (storage bloat)
- 1,584 markdown files (documentation sprawl)
- 33 package.json files (fragmented Node projects)
- 25% active surface (4,848 files modified in last 30 days)
```

**Implication:** 75% of the repository is DORMANT or ARCHIVE material.

---

## 🎯 DECISION FRAMEWORK

### Category A: KEEP & CONSOLIDATE (Active Surface)
**Criteria:** Modified in last 30 days OR in active task registry

| Component | Files | Action |
|-----------|------:|--------|
| **Collider Core** | ~500 | Keep, optimize |
| **Context Management AI** | ~200 | Keep, refine |
| **Agent System** | ~100 | Keep, stabilize |
| **Governance** | ~10 | Keep as-is |
| **Active Docs** | ~70 | Fix links, maintain |

**Total to keep:** ~880 files (4.6% of total)

---

### Category B: ARCHIVE TO GCS (Reference, Not Active)

| Component | Size | Lines | Archive Path |
|-----------|-----:|------:|--------------|
| **Research outputs** | ~5GB | 50M+ | `gs://elements-archive/research/` |
| **Old experiments** | ~2GB | 10M+ | `gs://elements-archive/experiments/` |
| **Historical docs** | ~500MB | 500K | `gs://elements-archive/docs/legacy/` |
| **Deprecated viz** | ~1GB | 5M | `gs://elements-archive/viz/deprecated/` |

**Total to archive:** ~8.5GB (65% of disk)

---

### Category C: DELETE (Dead Code, Duplicates)

| Component | Criteria | Est. Size |
|-----------|----------|----------:|
| **node_modules** | Regenerable | ~2GB |
| **Old package-lock.json** | Regenerable | ~1GB |
| **Failed experiments** | No references | ~500MB |
| **Duplicate implementations** | Audit needed | TBD |

**Total to delete:** ~3.5GB (27% of disk)

---

## 🚦 ACTION PRIORITIES (Sorted by Impact/Effort)

### Phase 1: Quick Wins (1 day)
```
□ Delete all node_modules/ (regenerable)         → -2GB
□ Archive old research JSON to GCS               → -5GB
□ Remove experiments/ directory (after review)   → -2GB
□ Clean up old package-lock.json files           → -1GB

Expected result: 13GB → 3GB (77% reduction)
```

### Phase 2: Structural Cleanup (3 days)
```
□ Consolidate 33 package.json → 3 workspaces     → Better structure
□ Move legacy docs to archive/                   → Clarity
□ Deduplicate context-management vs standard-model → Simplicity
□ Fix 8 broken doc links (G3 gate)               → Quality

Expected result: 19K files → ~5K files (74% reduction)
```

### Phase 3: Active Refinement (ongoing)
```
□ Maintain only active 880 files + tests
□ Keep census updated (weekly)
□ Enforce dormant file policy (>90 days → archive)
□ Run docs audit monthly
```

---

## 📏 SUCCESS METRICS

Track these after each phase:

| Metric | Before | Phase 1 Target | Phase 2 Target | Final Goal |
|--------|-------:|---------------:|---------------:|-----------:|
| **Disk usage** | 13GB | 3GB | 2GB | <1GB |
| **File count** | 19,067 | 10,000 | 5,000 | <1,000 |
| **JSON lines** | 77M | 2M | 1M | <500K |
| **Active files** | 4,848 | Same | Same | ~880 |
| **Doc orphans** | 733 | Same | 0 | 0 |

---

## 🧮 SPECIFIC TARGETS BY SUBSYSTEM

### standard-model-of-code/
```
Current:  15,586 files | 2.5GB | 1.8M lines
Keep:        ~500 files (src/core, tests, docs)
Archive:  ~15,000 files (old outputs, experiments)
Target:      ~500 files | 200MB | 100K lines
```

### context-management/
```
Current:  16,960 files | 6GB | 1.1M lines
Keep:        ~300 files (tools, active docs, configs)
Archive:  ~16,500 files (research outputs, experiments)
Target:      ~300 files | 100MB | 50K lines
```

### .agent/
```
Current:     523 files | 49MB | 56K lines
Keep:        ~100 files (active tasks, runs, schemas)
Archive:     ~400 files (old runs, stale tasks)
Target:      ~100 files | 10MB | 10K lines
```

---

## 🎲 DECISION RULES

### When to KEEP a file:
1. Modified in last 30 days
2. Referenced by active code
3. Part of test suite (passing)
4. Canonical documentation (non-orphan)
5. Required for core functionality

### When to ARCHIVE a file:
1. Historical research output
2. Deprecated but valuable reference
3. Old experiment results
4. Legacy documentation (superseded)
5. Dormant >90 days BUT contextually relevant

### When to DELETE a file:
1. Regenerable (node_modules, package-lock)
2. Failed experiment with no value
3. Duplicate with no unique content
4. Broken/corrupted
5. Violates current architecture

---

## 🔄 ITERATIVE APPROACH

**Don't do everything at once.** Use this cycle:

```
1. Pick ONE category from Phase 1
2. Make changes in a branch
3. Run tests + verification
4. Update REPO_CENSUS.md
5. Commit with metrics in commit message
6. Repeat

Example commit:
"chore: Archive old research JSON to GCS (-5GB, -8K files)"
```

---

## 📋 CHECKPOINT COMMANDS

After each phase, run these:

```bash
# Update census
bash /tmp/repo_census.sh > REPO_CENSUS_$(date +%Y%m%d).md

# Verify tests still pass
cd standard-model-of-code && pytest tests/ -q

# Check doc links
python3 context-management/tools/refinery/docs_audit.py

# Verify no broken imports
python3 -m py_compile $(find . -name "*.py" -not -path "*/node_modules/*")

# Update git stats
git log --oneline | wc -l
git ls-files | wc -l
```

---

## 🎯 NORTH STAR

**Target state (3 months):**
```
- 1,000 files (down from 19K)
- <1GB disk (down from 13GB)
- 500K lines of code+docs (down from 2.6M)
- 100% active surface (no dormant files >90 days)
- 0 broken links, 0 orphan docs
- 3 workspace projects (down from 33)
```

**This is achievable** because 75% of current files are dormant/archive.

---

**Use this matrix to justify every consolidation decision with NUMBERS.**
