# ⚡ QUICK START - Safe AI Queries
## 95% Confidence - Production Ready

**Updated:** 2026-01-28

---

## 🎯 FAST TRACK (Copy-Paste Commands)

### Query Context-Management Code
```bash
python analyze.py "how does ACI work" --set brain_active
```

### Query Recent Changes
```bash
python analyze.py "what did we build today" --set recent_7d
```

### Query Documentation
```bash
python analyze.py "explain the architecture" --set docs_active
```

### Query Active Surface (Last 30 Days)
```bash
python analyze.py "show me what's active" --set recent_30d
```

---

## 🛡️ SAFE SETS (Use These)

| Set | Use When | Tokens | Result |
|-----|----------|-------:|--------|
| **brain_active** | Analyzing Wave/ACI code | ~150K | ✅ Safe |
| **recent_7d** | Recent changes only | ~50K | ✅ Safe |
| **recent_30d** | Active surface | ~100K | ✅ Safe |
| **docs_active** | Documentation queries | ~80K | ✅ Safe |

---

## ⚠️ DANGEROUS SETS (Avoid)

| Set | Why Dangerous | Tokens | Result |
|-----|---------------|-------:|--------|
| **brain** | Includes archive/ | 8.3M | ❌ QUOTA FAIL |
| **body** | All of src/ | 3.5M | ❌ QUOTA FAIL |
| **complete** | Entire repo | 10M+ | ❌ QUOTA FAIL |

**System will block these** unless you use `--force`

---

## 🔧 COMMAND FLAGS

```bash
# Basic query
python analyze.py "question" --set brain_active

# Force over-budget query (careful!)
python analyze.py "question" --set brain --force

# Reduce file count
python analyze.py "question" --set large_set --max-files 50

# Interactive mode
python analyze.py "question" --set brain_active --interactive

# Show what will be included (dry run)
python analyze.py "question" --set brain_active --explain-context
```

---

## 📊 WHAT HAPPENS (Budget Check)

```
Step 1: Select files (with filters)
  710 files matched
  → Apply exclude_patterns (archive/, experiments/)
  → Apply max_age_days (90 days)
  → Apply max_file_size_kb (500KB)
  → Result: 69 files ✅

Step 2: Estimate tokens
  Method: accurate (tiktoken)
  Tokens: 152,340
  Budget: 150,000
  Ratio: 101.6%
  → ⚠️  WARNING: Slightly over budget

Step 3: Check budget
  Over by 1.6% → ALLOWED with warning
  → Proceed with query ✅

Step 4: Send to API
  Actual tokens sent: 152,340
  Quota remaining: OK
  → ✅ SUCCESS
```

---

## 🎨 VISUAL BUDGET REPORT

When you run a query, you'll see:

```
============================================================
TOKEN BUDGET CHECK
============================================================
  Estimated:  152,340 tokens (method: accurate)
  Budget:     150,000 tokens
  Usage:      101.6%
  [████████████████████████████████████████░]

⚠️  WARNING: 152,340 tokens is 101.6% of budget 150,000
============================================================

Proceeding (within tolerance)...
```

---

## 🚨 ERROR EXAMPLES

### Over Budget (Blocked)
```bash
$ python analyze.py "query" --set brain

============================================================
TOKEN BUDGET CHECK
============================================================
  Estimated:  8,347,513 tokens (method: fast)
  Budget:     150,000 tokens
  Usage:      5565.0%
  [████████████████████████████████████████]

❌ BLOCKED: 8,347,513 tokens exceeds 150,000 budget (55.7x over)
============================================================

⚠️  BUDGET EXCEEDED - Options:
  1. Use filtered set: --set brain_active (not brain)
  2. Reduce files: --max-files 50
  3. Force anyway: --force (may hit quota)

Top 5 files by token count:
   1,234,567 tokens - context-management/archive/references/huge.json
     876,543 tokens - context-management/archive/large_outputs/big.json
     543,210 tokens - standard-model-of-code/artifacts/analysis.json
     ...
```

### Solution Applied
```bash
$ python analyze.py "query" --set brain_active

============================================================
TOKEN BUDGET CHECK
============================================================
  Estimated:  148,920 tokens (method: medium)
  Budget:     150,000 tokens
  Usage:      99.3%
  [███████████████████████████████████████░]
============================================================

✅ Proceeding (within budget)...
```

---

## 📚 FULL DOCS

- **CONFIDENCE_ACHIEVED.md** - This implementation summary
- **CONFIDENCE_FILTERING_SPEC.md** - Technical specification
- **PHASE_1_USAGE.md** - Detailed usage guide
- **MISSION_CONTROL.md** - Repository overview

---

## ✅ YOU'RE READY

**95% confidence = Production ready**

```bash
# Just use filtered sets
python analyze.py "your question" --set brain_active

# System handles the rest:
✅ Filters out archive/
✅ Checks token budget
✅ Warns if approaching limit
✅ Blocks if over budget
✅ Shows which files are largest
✅ Recommends alternatives
```

**Query with confidence.** 🚀
