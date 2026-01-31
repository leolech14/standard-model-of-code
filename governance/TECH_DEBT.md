# Technical Debt Registry

> **Purpose:** Track known technical debt for future resolution.
> Updated: 2026-01-31

## TD-001: sys.path Hacks (77 files)

**Severity:** Medium
**Impact:** Tools break when run from wrong directory
**Files affected:** 77 Python files

### Problem
Many Python files manipulate `sys.path` to import from other directories:
```python
sys.path.insert(0, str(Path(__file__).parent.parent))
```

### Root Cause
- Project not installed as a package
- No `setup.py` or `pyproject.toml` for `pip install -e .`
- Tools need to import from `src/core/` but path isn't in PYTHONPATH

### Proper Fix
1. Create `pyproject.toml` with package definition
2. Run `pip install -e .` to install in development mode
3. Change imports to use package name: `from standard_model_of_code.src.core import ...`
4. Remove all `sys.path.insert()` calls

### Workaround (Current)
Run tools from project root or set PYTHONPATH:
```bash
PYTHONPATH=/path/to/standard-model-of-code python3 tool.py
```

### Effort
- Estimated: 4-8 hours
- Risk: Medium (may break imports temporarily)
- Priority: P2

---

## TD-002: No Unified CLI for Wave Tools (71 executables)

**Severity:** Low-Medium
**Impact:** Hard to discover and use tools
**Files affected:** 71 Python files with `if __name__ == "__main__"`

### Problem
Each tool has its own CLI entry point. No unified `pe wave <command>` interface.

### Fix
1. Create `context-management/cli.py` using Click/Typer
2. Register tools as subcommands
3. Add help/discovery system

### Effort
- Estimated: 4-6 hours
- Risk: Low
- Priority: P2

---

## TD-003: Embedded Git Repositories

**Severity:** Low
**Impact:** Git warnings, potential confusion
**Locations:**
- `context-management/library/spectrometer_benchmarks_legacy/axios/`
- `context-management/library/spectrometer_benchmarks_legacy/lodash/`

### Problem
Legacy benchmarks contain cloned git repos that cause warnings.

### Fix
1. Remove `.git/` directories from embedded repos
2. Or move to `.gitignore`
3. Or delete if not needed

### Effort
- Estimated: 30 minutes
- Risk: Low
- Priority: P3

---

## TD-004: Git Garbage Collection Needed

**Severity:** Low
**Impact:** Performance, disk space
**Evidence:** "warning: There are too many unreachable loose objects"

### Fix
```bash
git gc --prune=now
rm .git/gc.log
```

### Effort
- Estimated: 5 minutes
- Priority: P3

---

## TD-005: Inline TODO Comments (13+ locations)

**Severity:** Low
**Impact:** Incomplete implementations, deferred work
**Files affected:** 13+ Python files

### Problem
Scattered TODO/FIXME comments indicate incomplete work:

**Integration:**
- `lol_unify.py:128` - Integrate symmetry_check output
- `repo_mapper.py:429` - Integrate with cerebras_tagger

**Cloud Deployment:**
- `orchestrate_corpus.py:295` - Implement GCP Batch
- `orchestrate_corpus.py:305` - Implement Cloud Run Jobs

**Graph RAG:**
- `builder.py:260` - Delta detection for incremental updates
- `service.py:42` - Full embedding logic

**AI Tools:**
- `analyze.py:1114` - File deletion implementation
- `refinery.py:561` - Waybill cache updates
- `research_orchestrator.py:789,1093` - Multiple sets, override parsing

**Legacy (Portuguese):**
- `spectrometer_hadrons_engine.py:624` - Expand with 50+ repos
- `spectrometer_api_rest.py:313` - Implement repo clone

### Fix
1. Triage: Move critical TODOs to task tracker
2. Delete obsolete TODOs in legacy code
3. Convert remaining to GitHub issues

### Effort
- Estimated: Varies by item
- Priority: P3 (ongoing)

---

## Summary

| ID | Issue | Severity | Effort | Priority |
|----|-------|----------|--------|----------|
| TD-001 | sys.path hacks (77 files) | Medium | 4-8h | P2 |
| TD-002 | No unified wave CLI | Low-Medium | 4-6h | P2 |
| TD-003 | Embedded git repos | Low | 30m | P3 |
| TD-004 | Git GC needed | Low | 5m | P3 |
| TD-005 | Inline TODO comments (13+) | Low | Varies | P3 |
