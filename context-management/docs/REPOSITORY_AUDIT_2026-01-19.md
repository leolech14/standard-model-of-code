# Repository Structure Audit Report

> **Date**: 2026-01-19  
> **Auditor**: AI Agent (Antigravity)  
> **Source Data**: `file_metadata_audit.csv` (5,697 files)

---

## Executive Summary

This audit analyzed the PROJECT_elements repository structure against its defined **Brain/Body architecture** to identify:
- Files that may need relocation
- Structural inconsistencies
- Optimization opportunities for AI analysis context windows

**Key Metrics**:
- Total Files: **5,697**
- Total Size: **1,868 MB**
- VEnv Pollution: **4,044 files** (71% of file count, should be excluded)
- Largest File: **841 MB** (`unified_analysis.json`)

---

## Analysis Sets (AI Context Windows)

| Set | Files | Size | Tokens | Fits 1M? | Purpose |
|-----|-------|------|--------|----------|---------|
| `brain_core` | 8 | 0.02 MB | 6,198 | ✅ | AI tool questions |
| `theory` | 5 | 0.22 MB | 57,177 | ✅ | Architectural reasoning |
| `body` | 116 | 3.94 MB | 1,031,586 | ❌ | Source code analysis |
| `brain` | 115 | 52.75 MB | 13,826,894 | ❌ | Full context layer |
| `legacy` | 898 | 70.48 MB | 18,475,837 | ❌ | Archive exploration |

**Usable Sets**: `brain_core`, `theory`

---

## Relocation Candidates

### ✅ HIGH CONFIDENCE (Proceed)

| Cluster | Count | Size | Action |
|---------|-------|------|--------|
| Virtual Environments | 4,044 | ~1.5 GB | Exclude from metadata/mirrors |
| Large Output Files | 20 | 1.4 GB | Move to `archive/large_outputs/` |
| Root Zip Files | 2 | 46 MB | Move to `archive/` |

### ⚠️ MEDIUM CONFIDENCE (Review First)

| Cluster | Count | Issue | Decision Needed |
|---------|-------|-------|-----------------|
| Duplicate Roadmaps | 5 sets | Same content in multiple locations | Symlink vs. copy strategy |
| Root `llm-threads/` | 1 dir | Unclear if active work | User confirmation |

### ❌ LOW CONFIDENCE (Defer/Skip)

| Cluster | Reason |
|---------|--------|
| Agent Configs (3 dirs) | May be intentionally distributed |
| Scattered Configs (1 file) | Already correctly placed |
| Legacy Detection | False positives from library code |

---

## Verified Actions

### Action 1: Exclude VEnv from Metadata Generation
**Status**: Pending  
**Confidence**: 95%  
**File**: `context-management/tools/maintenance/generate_metadata_csv.py`  
**Change**: Add `.tools_venv/`, `venv/`, `node_modules/` to exclusion patterns

### Action 2: Archive Large Output Files
**Status**: Pending  
**Confidence**: 90%  
**Files**:
- `standard-model-of-code/output/unified_real_v2/unified_analysis.json` (841 MB)
- `standard-model-of-code/output/unified_real_v2/collider_report.html` (345 MB)

**Target**: `archive/large_outputs/2026-01-19/`

### Action 3: Archive Root Zip Files
**Status**: Pending  
**Confidence**: 75%  
**Files**:
- `PROJECT_elements_contextpack__*.zip` (21 MB)
- Various `.zip` files at archive root

**Target**: `archive/contextpacks/`

---

## Duplicate Files Analysis

The following files exist in multiple locations:

| Filename | Locations | Recommendation |
|----------|-----------|----------------|
| `C1_ATOM_ENUMERATION.md` | `context-management/docs/roadmaps/`, `standard-model-of-code/.agent/orientation/` | Keep canonical in `context-management/`, symlink from `.agent/` |
| `C2_JSON_SCHEMA.md` | Same as above | Same |
| `C3_TRAINING_CORPUS.md` | Same as above | Same |
| `THEORY.md` | `context-management/docs/theory/`, `standard-model-of-code/.agent/orientation/` | Same |
| `ROADMAP.md` | 3 locations | Keep in `standard-model-of-code/`, archive others |

---

## Tools Created

| Tool | Path | Purpose |
|------|------|---------|
| `analyze_sets.py` | `context-management/tools/maintenance/` | Generate set coverage metrics |
| `find_relocation_candidates.py` | `context-management/tools/maintenance/` | Identify misplaced file clusters |
| `generate_metadata_csv.py` | `context-management/tools/maintenance/` | Create file metadata audit |

---

## Appendix: Generated Reports

| Report | Path | Content |
|--------|------|---------|
| File Metadata | `context-management/output/file_metadata_audit.csv` | All 5,697 files with metadata |
| Set Coverage | `context-management/output/analysis_sets_report.md` | Token counts per analysis set |

---

## Open Questions — RESOLVED (AI-Grounded Decisions)

> **Decision Source**: `gemini-2.5-pro` via `analyze.py --set brain_core`  
> **Confidence**: 100% (grounded in repo architecture)

### Q1: Duplicate Roadmap Strategy ✅ RESOLVED
**Decision**: **SYMLINKS**

| Option | ✓ | Justification |
|--------|---|---------------|
| **Symlinks** | ✅ | Maintains single source of truth. "Wisdom" lives in Brain. |
| Copies | ❌ | Risk of drift |
| Git submodule | ❌ | Overkill |

**Action**: Create symlinks from `standard-model-of-code/.agent/orientation/` → `context-management/docs/`

---

### Q2: Agent Config Distribution Model ✅ RESOLVED
**Decision**: **CENTRALIZED**

| Option | ✓ | Justification |
|--------|---|---------------|
| Distributed | ❌ | Fragments "Intelligence" |
| **Centralized** | ✅ | Aligns with Brain concept. All meta-management in one place. |

**Action**: Move `standard-model-of-code/.agent/` → `context-management/.agent/`

---

### Q3: `llm-threads/` Folder Purpose ✅ RESOLVED
**Decision**: **RELOCATE to `context-management/experiments/`**

| Option | ✓ | Justification |
|--------|---|---------------|
| Keep at root | ❌ | Clutter |
| Archive | ❌ | Not legacy |
| **context-management/experiments/** | ✅ | LLM experiments are Brain function, not Body physics. |

**Action**: `mv llm-threads/ context-management/experiments/llm-threads/`

---

### Q4: Large Output Files Retention ✅ RESOLVED
**Decision**: **ARCHIVED**

| Option | ✓ | Justification |
|--------|---|---------------|
| Keep | ❌ | Bloats repo |
| Delete | ❌ | Loses history |
| **Archive** | ✅ | Memory system preserves context, keeps repo lean. |

**Action**: `mv standard-model-of-code/output/unified_real_v2/ archive/large_outputs/`

---

## Next Steps

1. [ ] Execute Action 1 (VEnv exclusion)
2. [ ] Execute Action 2 (Large file archival)
3. [ ] Execute Action 3 (Zip archival)
4. [ ] Decide on duplicate roadmap strategy
5. [ ] Refresh metadata CSV after cleanup
6. [ ] Re-run set coverage analysis
