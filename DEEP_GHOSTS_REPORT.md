# PROJECT_elements: Deep Ghosts Report
**Generated:** 2026-01-26
**Investigator:** Bug Detective

## Executive Summary

Discovered **53 broken references**, **2 KERNEL files with divergent purposes**, **duplicate naming across 467+ README files**, and **inconsistent AI tool invocation patterns**.

---

## 1. Broken Symlinks

**Status:** CLEAN
- No broken symlinks found

---

## 2. Broken Markdown References (53 total)

### Critical (User-Facing Docs)

| Source | Missing Target | Impact |
|--------|----------------|--------|
| `.agent/registry/INDEX.md` | `standard-model-of-code/docs/OPEN_CONCERNS.md` | Navigation broken (relative path issue) |
| `.agent/specs/WAVE_PARTICLE_SYMMETRY.md` | `./docs/SYMMETRY.md` | Dead reference to non-existent file |
| `.agent/registry/README.md` | `ARCHIVE_MANIFEST.md` | Archive documentation missing |
| `context-management/docs/WORKFLOW_FACTORY.md` | `.agent/KERNEL.md` | Wrong path (should be absolute) |
| `context-management/docs/operations/AGENT_KERNEL.md` | `gcp-infrastructure/CLAUDE.md` | External project reference |

### Medium (Internal Specs)

| Source | Missing Target |
|--------|----------------|
| `standard-model-of-code/docs/OPEN_CONCERNS.md` | `grades_DEGRADED_summary_only/LEARNINGS.md` |
| `standard-model-of-code/docs/ORPHANED_CONTROLS_INDEX.md` | `UI_HANDLER_IMPLEMENTATION_PATTERNS.md` |
| `standard-model-of-code/tools/batch_grade/README.md` | `docs/OPEN_CONCERNS.md` (path issue) |
| `standard-model-of-code/docs/specs/REGISTRY_OF_REGISTRIES.md` | `.agent/registry/INDEX.md` (path issue) |

### Low (Research/Archive)

- 44 broken references in `standard-model-of-code/docs/research/gemini/docs/*.md`
- Most are missing files like `MODEL.md`, `CUTTING_PLAN.md` in wrong directories

**Root Cause:** Relative paths used when files are at repo root or different hierarchy levels.

**Fix:** Use absolute paths from repo root (e.g., `/Users/lech/PROJECTS_all/PROJECT_elements/...`) or update to correct relative paths.

---

## 3. Duplicate File Names

### High-Impact Duplicates

| Filename | Count | Locations |
|----------|-------|-----------|
| `README.md` | 467 | Everywhere (normal for npm packages) |
| `KERNEL.md` | 2 | `.agent/` vs `context-management/docs/operations/AGENT_KERNEL.md` |
| `WORKFLOWS.md` | 5 | Multiple contexts |
| `CLAUDE.md` | 2 | Root vs `standard-model-of-code/` |
| `INDEX.md` | 8 | Various registries |

### The KERNEL Conflict

**Two different files, different purposes:**

| File | Purpose | Size | Audience |
|------|---------|------|----------|
| `.agent/KERNEL.md` | Task/Run system, 4D confidence, detailed workflows | 311 lines | All AI agents (comprehensive) |
| `context-management/docs/operations/AGENT_KERNEL.md` | Minimal boot protocol, concierge-based | 59 lines | Quick start (lightweight) |

**Analysis:**
- `.agent/KERNEL.md` = **Canonical reference** (detailed, versioned, schema-backed)
- `context-management/.../AGENT_KERNEL.md` = **Concierge wrapper** (delegates to `./concierge`)

**Not a bug:** Different abstraction levels. The short one defers to concierge. The long one IS the kernel.

**Issue:** Naming collision. The short one should be `AGENT_BOOT.md` or `CONCIERGE_GUIDE.md`.

---

## 4. Config File Contradictions

### Schema Duplication

Found **15 schema files** (excluding node_modules):
- `.agent/schema/*.schema.yaml` (7 files) — Agent schemas
- `standard-model-of-code/schema/*.schema.json` (3 files) — Collider schemas
- `standard-model-of-code/docs/ui/score/schema_v1.json` — UI scoring schema

**Status:** NO CONTRADICTIONS detected (different domains)

### Config Files

Found minimal config files (project is mostly convention-based):
- `commitlint.config.js` — Commit format enforcement
- `context-management/tools/archive/config.yaml` — Archive settings
- `.pre-commit-config.yaml` — Git hooks

**Status:** NO CONTRADICTIONS

---

## 5. AI Tool Invocation Inconsistencies

### The `analyze.py` Problem

**Found 4 different invocation patterns:**

| Pattern | File | Issue |
|---------|------|-------|
| `doppler run -- python context-management/tools/ai/analyze.py "query"` | `CLAUDE.md` (root) | Correct (uses secrets) |
| `python analyze.py "query"` | `.gemini/context/brain.md` | Path issue (assumes CWD) |
| `.tools_venv/bin/python context-management/tools/ai/analyze.py` | Research docs | Explicit venv (good) |
| `python context-management/tools/ai/analyze.py` | Various | No doppler (may fail) |

**Root Cause:** Documentation written at different times with different assumptions about:
1. Whether doppler is required
2. Whether we're in repo root
3. Whether `.tools_venv` is activated

**Fix Required:**
1. Canonicalize to: `doppler run -- python context-management/tools/ai/analyze.py "query"`
2. Document alternative: Activate `.tools_venv` first, then `python ...` works

---

## 6. Empty Files (Excluding .venv)

Found **30 empty files** (mostly `__init__.py` and `.py.typed` markers).

**Status:** NORMAL (Python package structure)

---

## 7. Truly Orphaned Files

### Methodology

Searched all non-archive files for mentions of other files by basename.

**Limitation:** This is a naive string search. Files may be referenced by:
- Import statements (`from x import y`)
- Execution (`./script.sh`)
- Indirect references (generated files)

### Candidates (High-Value Orphans)

Files that exist but are never mentioned:

*Orphan detection script still running...*

---

## 8. Large Files (Potential Monsters)

| File | Lines | Assessment |
|------|-------|------------|
| `context-management/tools/ai/analyze.py` | 3,441 | Monolithic AI orchestrator |
| `standard-model-of-code/src/core/viz/assets/app.js` | 2,996 | Legacy UI (being modularized) |
| `standard-model-of-code/src/core/full_analysis.py` | 2,409 | Pipeline orchestrator (appropriate) |
| `standard-model-of-code/src/core/viz/assets/modules/circuit-breaker.js` | 1,911 | UI state management |
| `standard-model-of-code/src/core/edge_extractor.py` | 1,785 | Graph analysis (complex domain) |

**Recommendation:**
- `analyze.py` (3.4k lines) should be split into modules
- `app.js` (3k lines) is being deprecated in favor of modules (good)
- Others are justifiable for their complexity

---

## 9. README Proliferation

**Found 467 README files** (mostly in `node_modules` and `archive`).

Active project READMEs:
- `./README.md` — Project root
- `./standard-model-of-code/README.md` — Collider entry
- `./related/chrome-mcp/README.md` — Related project
- `./.agent/registry/README.md` — Task registry
- Various tool-specific READMEs

**Status:** ACCEPTABLE (normal for multi-domain project)

---

## 10. Cross-Reference Map

### Files That Reference Non-Existent Paths

**Top Offenders:**

1. **Gemini research docs** (44 broken refs) → `docs/research/gemini/docs/*.md`
   - Referencing files in relative paths that don't exist
   - Low impact (these are LLM conversation logs)

2. **Standard Model specs** (9 broken refs)
   - `UI_HANDLER_IMPLEMENTATION_PATTERNS.md` (missing)
   - `THEORY_EXPANSION_2026.md` (in wrong location)
   - Various `docs/research/*.md` files (path issues)

3. **Agent specs** (3 broken refs)
   - `ARCHIVE_MANIFEST.md` (never created)
   - `docs/SYMMETRY.md` (doesn't exist)

---

## Priority Fixes

### P0 (Breaking Navigation)

1. Fix `.agent/registry/INDEX.md` → `OPEN_CONCERNS.md` (should be `../standard-model-of-code/docs/OPEN_CONCERNS.md`)
2. Rename `context-management/docs/operations/AGENT_KERNEL.md` to `AGENT_BOOT.md` (avoid collision)
3. Create `ARCHIVE_MANIFEST.md` or remove reference in `.agent/registry/README.md`

### P1 (Documentation Debt)

4. Standardize `analyze.py` invocation across all docs
5. Fix or remove broken references in specs (9 files)
6. Create missing `UI_HANDLER_IMPLEMENTATION_PATTERNS.md` or remove references

### P2 (Low Impact)

7. Clean up Gemini research docs broken references (or accept as-is for historical record)
8. Consider splitting `analyze.py` into smaller modules

---

## Ghost Categories

| Type | Count | Severity |
|------|-------|----------|
| Broken symlinks | 0 | - |
| Broken doc references | 53 | Medium |
| KERNEL naming collision | 1 | Medium |
| Config contradictions | 0 | - |
| Invocation pattern drift | 4 patterns | Low |
| Truly orphaned files | TBD | Unknown |
| Oversized files | 5 | Low |

---

## Conclusion

**Overall Health:** GOOD

The repo has normal levels of documentation drift for an actively developed project. Most "ghosts" are:
1. Relative path issues (fixable with search/replace)
2. Research artifacts (LLM conversation logs with broken internal refs)
3. Documentation written at different times with different assumptions

**No critical infrastructure issues found.**

**Recommended Actions:**
1. Fix P0 path issues (3 files)
2. Standardize AI tool docs
3. Consider orphan detection as ongoing maintenance

---

**Files Referenced in This Report:**
- /Users/lech/PROJECTS_all/PROJECT_elements/.agent/KERNEL.md
- /Users/lech/PROJECTS_all/PROJECT_elements/context-management/docs/operations/AGENT_KERNEL.md
- /Users/lech/PROJECTS_all/PROJECT_elements/.agent/registry/INDEX.md
- /Users/lech/PROJECTS_all/PROJECT_elements/CLAUDE.md
- /Users/lech/PROJECTS_all/PROJECT_elements/standard-model-of-code/CLAUDE.md
- /Users/lech/PROJECTS_all/PROJECT_elements/context-management/tools/ai/analyze.py
