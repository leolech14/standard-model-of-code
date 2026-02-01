# ACI Diagnosis and Fixes

**Date:** 2026-01-30
**Status:** CRITICAL FIXES APPLIED

---

## Issues Found

### 1. Stale Paths (CRITICAL)
- `archive/` directory does not exist
- Sets `archive` and `archeology` had 0 matching files
- **Fix:** Marked as `[BROKEN]` in descriptions

### 2. `**/*.py` Patterns Not Working
- `list_local_files()` uses `fnmatch`, not `glob.glob()`
- `fnmatch` doesn't support `**` for recursive matching
- Sets affected: `recent_7d`, `recent_30d`, `docs_active`
- **Fix:** Changed to explicit paths like `particle/src/**/*.py`

### 3. Filters Not Being Applied (BUG FIXED)
- `resolve_set()` extracted filters but `list_local_files()` was called
- Temporal filters (`max_age_days`) were ignored
- **Fix:** Added conditional call to `list_and_filter_files()` with filters

---

## Changes Made

### config/analysis_sets.yaml
```yaml
# BEFORE (broken):
recent_7d:
  patterns:
    - "**/*.py"  # fnmatch doesn't support **

# AFTER (fixed):
recent_7d:
  patterns:
    - "particle/src/**/*.py"
    - "wave/tools/**/*.py"
    - ...
```

### analyze.py (line ~3167)
```python
# BEFORE (filters ignored):
selected_files = list_local_files(base_dir, patterns, user_excludes)

# AFTER (filters applied):
if args.set and set_filters and HAS_FILTERS:
    selected_files = list_and_filter_files(
        base_dir, patterns, user_excludes,
        filters=set_filters, verbose=...
    )
    print(f"  Filters applied: {filter_desc}", file=sys.stderr)
else:
    selected_files = list_local_files(base_dir, patterns, user_excludes)
```

---

## Verification

```bash
# Before fix: 837K tokens (filters ignored)
$ python analyze.py --set recent_7d "query"
Using Set: RECENT_7D
Warning: Found 1441 files
Estimated: 837,379 tokens

# After fix: 170K tokens (filters applied)
$ python analyze.py --set recent_7d "query"
Using Set: RECENT_7D
Filters applied: max_age_days=7, sort_by=mtime, limit=50
Estimated: 170,435 tokens
```

---

## Working vs Broken Sets

### Working Sets (26 within budget)
```
deck_state, agent_kernel, role_registry, constraints, repo_theory,
deck, roadmap, classifiers, tests, research_tools, pipeline,
architecture_review, agent_full, agent_session, repo_docs, repo_tool,
aci_siblings, agent_specs, aci_audit, deck_cards, agent_tasks,
agent_intelligence, viz, body
```

### Broken/Empty Sets (2)
```
archive     - directory does not exist
archeology  - depends on archive/
```

### Over Budget Sets (15)
```
theory, research_full, viz_core, brain_active, implementation_review,
aci_core, research_validation, research_atoms, research_core,
docs_core, schema, foundations, brain, docs_active, recent_7d/30d
```

---

## Diagnostic Tools Created

```bash
# Check set budgets
python wave/docs/research/scripts/check_set_budgets.py --viable

# Diagnose path issues
python wave/docs/research/scripts/diagnose_aci_paths.py --fix
```

---

## Recommendations

1. **For Research:** Use only "Working Sets" from the list above
2. **For Large Contexts:** Use `--force` with budget warnings
3. **For Broken Sets:** Either create `archive/` directory or delete the sets
4. **For Over-Budget Sets:** Increase budgets or reduce patterns

---

## Root Cause Analysis

The ACI system grew organically without validation:
- Patterns were added assuming `glob.glob()` behavior
- `archive/` was referenced but never created
- Filters were implemented but not wired into main path
- No CI/tests to catch pattern drift

**Lesson:** Add `--validate-sets` command to check all patterns on startup.
