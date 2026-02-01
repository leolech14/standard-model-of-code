# Phase 1 Filtering - Usage Guide
## Safe AI Queries Without Quota Failures

**Status:** ✅ IMPLEMENTED (70% confidence)
**Date:** 2026-01-28

---

## 🚨 THE PROBLEM (Before Phase 1)

```bash
# This FAILED with 8.3M tokens (56x over budget)
python analyze.py "explain cleanup" --set brain
# → 710 files (includes archive/)
# → 8,347,513 tokens
# → QUOTA EXCEEDED ❌
```

---

## ✅ THE SOLUTION (After Phase 1)

```bash
# This WORKS with ~150K tokens (within budget)
python analyze.py "explain cleanup" --set brain_active
# → ~69 files (excludes archive/)
# → ~150,000 tokens
# → SUCCESS ✅
```

---

## 📋 NEW FILTERED SETS

### 1. `brain_active` (Recommended)

**Use when:** Analyzing wave code/docs

```bash
python analyze.py "how does ACI work" --set brain_active
```

**Filters applied:**
- ❌ Excludes `archive/`, `experiments/`, `legacy/`, `deprecated/`
- ⏰ Only files modified in last 90 days
- 📏 Only files <500KB
- 📊 Result: ~69 files, ~150K tokens

---

### 2. `recent_30d` (Active Surface)

**Use when:** Understanding recent changes

```bash
python analyze.py "what changed recently" --set recent_30d
```

**Filters applied:**
- ⏰ Only files modified in last 30 days
- 🔝 Top 100 files only
- 📊 Sorted by most recent first
- 📊 Result: ~100 files, ~100K tokens

---

### 3. `recent_7d` (Hot Zone)

**Use when:** Checking very recent work

```bash
python analyze.py "what did we just build" --set recent_7d
```

**Filters applied:**
- ⏰ Only files modified in last 7 days
- 🔝 Top 50 files only
- 📊 Sorted by most recent first
- 📊 Result: ~50 files, ~50K tokens

---

### 4. `docs_active` (Documentation Only)

**Use when:** Documentation queries

```bash
python analyze.py "explain the architecture" --set docs_active
```

**Filters applied:**
- ❌ Excludes `archive/`, `legacy/`
- 📏 Only files <100KB
- 📄 Only .md files
- 📊 Result: ~80 files, ~80K tokens

---

## ⚠️ DEPRECATED SETS (Don't Use)

### ❌ `brain` (OLD)

```bash
# DON'T USE THIS - includes archive/
python analyze.py "query" --set brain
# → 710 files, 8.3M tokens → QUOTA FAIL
```

**Use `brain_active` instead.**

---

## 🧪 HOW TO TEST

### Test 1: Verify Filtering Works

```bash
# Should show filter statistics
python analyze.py "test query" --set brain_active 2>&1 | grep Filters
```

**Expected output:**
```
  [Filters] Starting with 710 files
  [Filters] After exclude_patterns: 100 files
  [Filters] After max_age_days: 80 files
  [Filters] After max_file_size_kb: 69 files
  [Filters] Final count: 69 files
```

---

### Test 2: Compare Tokens

```bash
# Old way (FAILS)
python analyze.py "test" --set brain 2>&1 | grep "Context size"
# → Context size: ~8,347,513 tokens

# New way (WORKS)
python analyze.py "test" --set brain_active 2>&1 | grep "Context size"
# → Context size: ~150,000 tokens
```

---

## 📊 FILTER REFERENCE

### Available Filter Options

```yaml
filters:
  # Pattern exclusions
  exclude_patterns:
    - "**/archive/**"
    - "**/experiments/**"
    - "**/legacy/**"
    - "**/deprecated/**"

  # Recency filter
  max_age_days: 90  # Only files modified in last N days

  # Size filter
  max_file_size_kb: 500  # Skip files >500KB

  # Sorting
  sort_by: "mtime"  # Options: mtime, size, path

  # Hard limit
  limit: 100  # Maximum number of files
```

---

## 🎯 CONFIDENCE LEVELS

| Phase | Confidence | Token Accuracy | Status |
|-------|------------|----------------|--------|
| **Phase 1** | **70%** | **±50%** | **✅ DONE** |
| Phase 2 | 85% | ±20% | 🔄 Next |
| Phase 3 | 95% | ±5% | ⏸️ Future |
| Phase 4 | 99% | ±1% | ⏸️ Future |

**You are here:** Phase 1 ✅ - Safe to query with filtered sets

---

## 🚀 NEXT PHASE (Phase 2)

**Goal:** 85% confidence with better accuracy

**Changes needed:**
1. Integrate filters into ACI routing automatically
2. Add accurate token estimation (before sending)
3. Add warnings when approaching budget

**Estimated effort:** 30 minutes

---

## 💡 BEST PRACTICES

### DO ✅

```bash
# Use filtered sets
python analyze.py "query" --set brain_active

# Use recent sets for recent work
python analyze.py "what changed" --set recent_7d

# Use docs sets for documentation
python analyze.py "explain X" --set docs_active
```

### DON'T ❌

```bash
# DON'T use deprecated brain set
python analyze.py "query" --set brain  # QUOTA FAIL

# DON'T use complete set
python analyze.py "query" --set complete  # WILL FAIL

# DON'T use body set
python analyze.py "query" --set body  # TOO LARGE
```

---

## 🔧 CREATING CUSTOM FILTERED SETS

Edit `wave/config/analysis_sets.yaml`:

```yaml
my_custom_set:
  description: "My filtered set"
  max_tokens: 100000
  filters:
    exclude_patterns:
      - "**/tests/**"  # Exclude tests
    max_age_days: 30   # Last 30 days only
    max_file_size_kb: 200  # Small files only
    limit: 50          # Max 50 files
  patterns:
    - "src/**/*.py"
    - "docs/*.md"
```

---

## 📞 TROUBLESHOOTING

### Problem: "Context size exceeds budget"

```bash
# Symptom
WARNING: Estimated 500K tokens exceeds 150K budget

# Solution
Use a more filtered set:
- brain → brain_active
- recent_30d → recent_7d
- docs_active with smaller max_file_size_kb
```

### Problem: "No files found"

```bash
# Symptom
Selected 0 files

# Solution
Filters too restrictive - check:
- max_age_days (try increasing)
- exclude_patterns (remove some)
- patterns (make sure they match files)
```

### Problem: "Module context_filters not found"

```bash
# Symptom
ImportError: No module named 'context_filters'

# Solution
File not committed or wrong venv:
git pull  # Get latest
source .tools_venv/bin/activate
```

---

**Phase 1 complete. You can now query safely.** 🎉
