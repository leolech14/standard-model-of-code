# 🎛️ PROJECT_elements - MISSION CONTROL
## Strategic Command & Control Panel

**Last Updated:** 2026-01-28 18:07
**Git SHA:** f0314e2d

---

## 📦 REPOSITORY SCALE

```
┌─────────────────────────────────────────────────┐
│  FILESYSTEM                                     │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  Files:       19,067                            │
│  Directories:    806                            │
│  Disk Usage:    13GB                            │
│  Commits:       789                             │
│                                                 │
│  ACTIVE SURFACE (Last 30 days)                  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  Files touched: 4,848 (25%)                     │
│  Commits:         405                           │
│  Avg/day:          58                           │
└─────────────────────────────────────────────────┘
```

---

## 💻 CODE BREAKDOWN

```
┌─────────────────────────────────────────────────┐
│  LANGUAGES                    Lines      Files  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  Python                     769,266     26,189  │
│  JavaScript                 731,201      1,062  │
│  Markdown                   977,130      1,584  │
│  TypeScript                  56,201         71  │
│  TSX                         10,277         48  │
│  YAML                        96,663        336  │
│  JSON                    77,779,115 ← 3,652    │
│  Shell                        3,605         47  │
│                                                 │
│  TOTAL (excl. JSON)       2,644,343     29,337  │
│  TOTAL (incl. JSON)      79,423,458     32,989  │
└─────────────────────────────────────────────────┘
```

**Key Insight:** 97% of lines are JSON artifacts, not code.

---

## 🏗️ SUBSYSTEMS

```
┌──────────────────────────────────────────────────────┐
│  DIRECTORY               Files    Lines       Size   │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  context-management     16,960  1,174,133     6.0GB  │
│  standard-model-of-code 15,586  1,810,787     2.5GB  │
│  .agent                    523     56,114      49MB  │
│  governance                  9      1,850      68KB  │
│  Other (experiments, etc)  ~2K         ?     ~4.5GB  │
└──────────────────────────────────────────────────────┘
```

---

## 📋 TASK SYSTEM STATE

```
┌─────────────────────────────────────────────────┐
│  AGENT REGISTRY                                 │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  Active Tasks:           7                      │
│  Opportunities:         69                      │
│  Run Records:            1                      │
│  Registry YAML:        147                      │
└─────────────────────────────────────────────────┘
```

---

## 📚 DOCUMENTATION HEALTH

```
┌─────────────────────────────────────────────────┐
│  MARKDOWN FILES                                 │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  Total:              1,584 files (977K lines)   │
│  Context-mgmt docs:    143 files                │
│  Active (non-archive):  69 files                │
│                                                 │
│  QUALITY GATES (G3/G4/G5)                       │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  G3: Link Integrity      ❌ FAIL (8 broken)     │
│  G4: Placeholders        ❌ FAIL (163 found)    │
│  G5: Validation Files    ✅ PASS (0 issues)     │
│                                                 │
│  Overall: 1/3 gates passing                     │
└─────────────────────────────────────────────────┘
```

---

## 🚨 TOP ISSUES

```
┌─────────────────────────────────────────────────┐
│  PRIORITY                              Impact    │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  1. JSON Bloat (77M lines)              🔴 HIGH │
│     → Archive old research to GCS       -5GB    │
│                                                 │
│  2. Doc Link Integrity (8 broken)       🟡 MED  │
│     → Fix with docs_audit.py            G3 pass │
│                                                 │
│  3. Package Fragmentation (33 pkg.json) 🟡 MED  │
│     → Consolidate to 3 workspaces       Clean   │
│                                                 │
│  4. Dormant Files (75% untouched)       🟢 LOW  │
│     → Archive >90 day files             -10GB   │
└─────────────────────────────────────────────────┘
```

---

## 🎯 CONSOLIDATION TARGETS

```
┌──────────────────────────────────────────────┐
│  METRIC            Current  →  Target  (Δ)   │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  Disk usage         13GB   →   1GB   (-92%)  │
│  File count        19,067  →  1,000  (-95%)  │
│  JSON lines          77M   →  500K   (-99%)  │
│  Active files      4,848   →    880  (-82%)  │
│  Doc orphans         733   →      0  (-100%) │
│  Workspaces           33   →      3  (-91%)  │
└──────────────────────────────────────────────┘
```

**Timeline:** 3 months (Phase 1: 1 day, Phase 2: 3 days, Phase 3: ongoing)

---

## 🔗 RELATED DOCUMENTS

- **INTELLIGENCE_BRIEF.md** - Full statistical breakdown
- **OPERATIONS_PLAN.md** - Decision framework + action plan
- **governance/QUALITY_GATES.md** - Integrity checks (G1-G8)
- **governance/DEFINITION_OF_DONE.md** - v1 release criteria
- **context-management/reports/refinery/docs_audit_latest.md** - Latest audit

---

## 🚀 QUICK ACTIONS

```bash
# Update intelligence brief
bash /tmp/repo_census.sh > INTELLIGENCE_BRIEF_$(date +%Y%m%d).md

# Run docs audit
python3 context-management/tools/refinery/docs_audit.py

# Check active surface
git log --since="30 days ago" --name-only --pretty=format: | sort -u | wc -l

# View disk usage by subsystem
du -sh */ | sort -hr | head -10

# Count dormant files
find . -type f -mtime +90 | wc -l
```

---

## 📊 COMMAND PHILOSOPHY

**This panel shows THREE NUMBERS:**
1. **What EXISTS** (19K files, 13GB)
2. **What's ACTIVE** (25% modified in 30 days)
3. **What's the TARGET** (1K files, 1GB)

**The gap between 1 and 3 is your mission.**

---

**Update this panel weekly. Watch the numbers shrink.**
