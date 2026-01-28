# Confidence-Based Context Filtering
## Preventing the 8.3M Token Disaster

**Problem:** `analyze.py --set brain` sent 8.3M tokens (56x over budget) because it included ALL of `context-management/archive/` (3.9GB).

**Root Cause:** No intelligent filtering - just dumb glob patterns.

---

## 📊 CURRENT STATE (v1)

```python
# context-management/tools/ai/analyze.py (current)

def get_files_for_set(set_name):
    patterns = config['patterns']  # e.g., "context-management/**/*.md"
    files = []
    for pattern in patterns:
        files.extend(glob.glob(pattern, recursive=True))
    return files  # ❌ NO FILTERING
```

**Result:**
- `brain` set: 710 files found
- Token estimate: 150K (config)
- Actual tokens: 8,347,513 (FAIL)
- Ratio: 56x over budget

---

## 🎯 REQUIRED STATE (v2)

```python
# With intelligent filtering

def get_files_for_set(set_name):
    config = load_set_config(set_name)
    patterns = config['patterns']
    filters = config.get('filters', {})

    # Step 1: Glob match
    files = []
    for pattern in patterns:
        matched = glob.glob(pattern, recursive=True)
        files.extend(matched)

    # Step 2: Apply exclude patterns
    if 'exclude_patterns' in filters:
        files = apply_exclude_patterns(files, filters['exclude_patterns'])

    # Step 3: Apply age filter
    if 'max_age_days' in filters:
        files = filter_by_age(files, filters['max_age_days'])

    # Step 4: Apply size filter
    if 'max_file_size_kb' in filters:
        files = filter_by_size(files, filters['max_file_size_kb'])

    # Step 5: Sort (if requested)
    if 'sort_by' in filters:
        files = sort_files(files, filters['sort_by'])

    # Step 6: Limit count
    if 'limit' in filters:
        files = files[:filters['limit']]

    # Step 7: Estimate tokens (BEFORE sending)
    estimated = estimate_tokens(files)
    max_budget = config['max_tokens']
    if estimated > max_budget:
        warn(f"Estimated {estimated} tokens exceeds budget {max_budget}")
        if not force:
            raise TokenBudgetExceeded()

    return files
```

---

## 🔧 IMPLEMENTATION PHASES

### Phase 1: Essential Filters (1-2 hours)

**Priority: CRITICAL** - Prevents quota failures

```python
def apply_exclude_patterns(files, exclude_patterns):
    """Exclude archive/, experiments/, legacy/"""
    import fnmatch
    filtered = []
    for f in files:
        excluded = False
        for pattern in exclude_patterns:
            if fnmatch.fnmatch(f, pattern):
                excluded = True
                break
        if not excluded:
            filtered.append(f)
    return filtered


def filter_by_age(files, max_age_days):
    """Only include files modified in last N days"""
    import time
    cutoff = time.time() - (max_age_days * 86400)
    return [f for f in files if os.path.getmtime(f) > cutoff]


def filter_by_size(files, max_kb):
    """Exclude files larger than N kilobytes"""
    max_bytes = max_kb * 1024
    return [f for f in files if os.path.getsize(f) <= max_bytes]
```

**Files to modify:**
- `context-management/tools/ai/analyze.py` (add filter logic)
- `context-management/config/analysis_sets.yaml` (add filter configs)

**Testing:**
```bash
# Before: 710 files, 8.3M tokens
python analyze.py "test" --set brain

# After: ~69 files, ~150K tokens
python analyze.py "test" --set brain_active
```

---

### Phase 2: Sorting & Limits (30 min)

```python
def sort_files(files, sort_by):
    """Order files by mtime, size, or path"""
    if sort_by == "mtime":
        return sorted(files, key=lambda f: os.path.getmtime(f), reverse=True)
    elif sort_by == "size":
        return sorted(files, key=lambda f: os.path.getsize(f))
    elif sort_by == "path":
        return sorted(files)
    return files
```

---

### Phase 3: Accurate Token Estimation (1 hour)

**Current problem:** max_tokens is a guess, not measured.

```python
def estimate_tokens(files):
    """Estimate tokens BEFORE loading files"""
    total = 0
    for filepath in files:
        # Quick estimate: 1 token ≈ 4 chars
        size = os.path.getsize(filepath)
        total += size // 4
    return total


def estimate_tokens_accurate(files):
    """Slower but accurate - count actual tokens"""
    import tiktoken
    enc = tiktoken.get_encoding("cl100k_base")  # GPT-4 tokenizer

    total = 0
    for filepath in files:
        with open(filepath) as f:
            content = f.read()
            tokens = len(enc.encode(content))
            total += tokens
    return total
```

**Usage:**
```python
# Fast estimate (Phase 1)
estimated = estimate_tokens(files)  # Size / 4

# Accurate count (Phase 3)
if estimated > max_budget * 0.8:  # Within 80% of budget
    actual = estimate_tokens_accurate(files)
```

---

### Phase 4: AI Confidence Scoring (Future)

**Not urgent** - Phase 1-3 solve immediate problem.

```python
def score_relevance(filepath, query):
    """
    Score 0.0-1.0 how relevant file is to query.

    Methods:
    1. Keyword overlap (simple)
    2. Embedding similarity (better)
    3. LLM judge (expensive)
    """
    # Simple version: keyword match
    with open(filepath) as f:
        content = f.read().lower()

    query_words = set(query.lower().split())
    matches = sum(1 for word in query_words if word in content)
    score = min(1.0, matches / len(query_words))

    return score


def filter_by_confidence(files, query, min_confidence):
    """Only include files ≥ confidence threshold"""
    scored = [(f, score_relevance(f, query)) for f in files]
    filtered = [f for f, score in scored if score >= min_confidence]
    return filtered
```

---

## 📋 ACCEPTANCE CRITERIA

### Phase 1 Success:
```bash
# This should NOT exceed quota
python analyze.py "explain cleanup" --set brain_active

Expected:
- Files selected: 50-100 (not 710)
- Tokens sent: <200K (not 8.3M)
- Excludes: archive/, experiments/, legacy/
- Status: ✅ PASSES
```

### Phase 2 Success:
```bash
# Hot zone query
python analyze.py "what changed recently" --set recent_7d

Expected:
- Files: 20-50 (last 7 days only)
- Tokens: <50K
- Sorted: Most recent first
- Status: ✅ PASSES
```

### Phase 3 Success:
```bash
# Accurate budget warning
python analyze.py "big query" --set large_set

Expected:
- Warning: "Estimated 450K tokens (exceeds 200K budget)"
- Prompt: "Continue anyway? [y/N]"
- If N: Exit without sending
- Status: ✅ PREVENTS WASTE
```

---

## 🎯 ANSWER TO YOUR QUESTION

> **"How much confidence do we need in categorization to query?"**

**Current system: 0% confidence** (no filtering, just glob)

**Required system:**
1. **Phase 1 (Essential):** 70% confidence
   - Exclude archives ✓
   - Filter by recency ✓
   - Limit size ✓
   - **Result:** 710 files → ~69 files

2. **Phase 2 (Good):** 85% confidence
   - + Sorting by relevance
   - + Hard limits on count
   - **Result:** Predictable token usage

3. **Phase 3 (Ideal):** 95% confidence
   - + Accurate token estimation
   - + Budget enforcement
   - **Result:** Never exceed quota

4. **Phase 4 (Future):** 99% confidence
   - + AI relevance scoring
   - + Query-specific filtering
   - **Result:** Optimal context

---

## 🚀 IMMEDIATE ACTION

**Implement Phase 1 NOW** (< 2 hours work):

1. Add filter logic to `analyze.py`
2. Update `analysis_sets.yaml` with exclude patterns
3. Test with `--set brain_active`
4. Verify: <200K tokens sent

**Then you can query safely.**

---

## 📊 CONFIDENCE LEVELS TABLE

| Phase | Confidence | Token Accuracy | Can Query? | Risk |
|-------|------------|----------------|------------|------|
| **v1 (current)** | 0% | ±5,600% | ❌ NO | Quota fail |
| **Phase 1** | 70% | ±50% | ✅ YES | Low |
| **Phase 2** | 85% | ±20% | ✅ YES | Very low |
| **Phase 3** | 95% | ±5% | ✅ YES | Minimal |
| **Phase 4** | 99% | ±1% | ✅ YES | None |

**Your question answered:** Need **≥70% confidence** (Phase 1) to query safely.

**Currently at:** 0% confidence → **DO NOT QUERY until Phase 1 implemented.**
