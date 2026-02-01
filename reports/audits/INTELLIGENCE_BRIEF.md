# PROJECT_elements - Repository Census
## TABULA RASA (Statistical Control Panel)

**Generated:** 2026-01-28 18:07:05 -03
**Git SHA:** f0314e2d
**Purpose:** Comprehensive numerical overview of entire repository state

---

## 🔢 THE TOTALS (What exists)

### Scale
```
19,067 files
   806 directories
    13 GB disk usage
   789 commits
     1 contributor
   405 commits (last 7 days)
```

### Code Volume
```
769,266 lines of Python    (26,189 files)
731,201 lines of JavaScript (1,062 files)
 56,201 lines of TypeScript (71 files)
 10,277 lines of TSX        (48 files)
977,130 lines of Markdown   (1,584 files)
 96,663 lines of YAML       (336 files)
 77.7M  lines of JSON       (3,652 files) ← MASSIVE DATA
```

**Total code lines:** ~2.6 million (excluding JSON)
**Total with JSON:** ~79 million lines

---

## 📦 SUBSYSTEM BREAKDOWN

| Subsystem | Files | Lines (code+docs) | Size | % of Total |
|-----------|------:|------------------:|-----:|:----------:|
| **wave** | 16,960 | 1,174,133 | 6.0G | **46%** |
| **particle** | 15,586 | 1,810,787 | 2.5G | **19%** |
| **.agent** | 523 | 56,114 | 49M | <1% |
| **governance** | 9 | 1,850 | 68K | <1% |
| **Other** | ~2,000 | ? | ~4.5G | **34%** |

**Observations:**
- Context-management is 46% of disk (mostly JSON/artifacts)
- Standard-model is 19% disk but has MORE code lines (Collider core)
- "Other" 34% = node_modules, experiments, archives, viz

---

## 📚 DOCUMENTATION STATE

```
1,584 markdown files
977,130 total lines (~4,000 pages if printed)
  143 files in wave/docs
   69 files are active (non-archive)
```

**Recent audit results (G3/G4/G5):**
- 8 broken links (G3)
- 163 placeholder detections (mostly false positives)
- 0 validation file issues (G5)

---

## 🤖 AGENT / TASK STATE

```
Active Tasks:      7
Opportunities:    69
Run Records:       1
```

**Registry files:** 147 YAML files in .agent/registry + governance

---

## 🏗️ DEPENDENCIES

```
33 package.json files    (Node.js projects)
 8 requirements.txt      (Python projects)
 1 pyproject.toml        (Python packaging)
```

**Implication:** Multiple semi-independent projects within monorepo

---

## 📊 ARTIFACTS & GENERATED DATA

```
3,652 JSON files (77M+ lines)
    4 Intelligence chunks (.agent/intelligence/chunks)
    2 Refinery reports (wave/reports/refinery)
```

**JSON breakdown hypothesis:**
- Research outputs (Gemini/Perplexity)
- Collider analysis results
- Node modules (package-lock.json files)
- GraphRAG/knowledge graphs

---

## 🎯 CRITICAL RATIOS

| Metric | Value | Interpretation |
|--------|------:|----------------|
| **Lines per file** | ~4,100 | Very high (includes JSON blobs) |
| **Docs to Code ratio** | 1:1.7 | Good documentation coverage |
| **Python vs JS** | 1.05:1 | Roughly balanced |
| **YAML configs** | 336 | Heavy configuration |
| **Commits per day (7d avg)** | 58 | Very active |

---

## 🚨 CONSOLIDATION TARGETS

Based on these numbers, priority cleanup areas:

1. **JSON artifacts** - 77M lines is storage bloat
   - Move old research to archive/GCS
   - Keep only recent/canonical analyses

2. **Duplicate subsystems** - 16,960 files in wave
   - Verify no duplicate implementations
   - Archive deprecated experiments

3. **Documentation sprawl** - 1,584 MD files
   - 143 in wave/docs
   - 69 active docs have issues
   - ~1,441 other .md files (experiments? archives?)

4. **Node modules** - 33 package.json implies 33 node_modules dirs
   - Consider monorepo workspace
   - Remove unused projects

---

## 🎓 WHAT THIS TELLS US

### The Repository is MASSIVE
- 13GB, 19K files, 79M lines
- Comparable to large enterprise monorepos
- Needs aggressive pruning OR accept as "research archive"

### Heavy on Data/Artifacts
- 77M lines of JSON (97% of total lines!)
- Only 2.6M lines of actual code/docs
- Data-to-code ratio: 30:1

### Actively Developed
- 405 commits in 7 days
- 789 total commits
- Single contributor (you)

### Well-Structured (Agent System)
- 7 active tasks
- 69 opportunities in pipeline
- Governance files present
- Agent coordination working

---

## 📐 REFERENCE FRAMEWORK

Use these totals when:
- Deciding what to archive/delete
- Estimating Collider analysis time (16K+ files in standard-model)
- Planning GCS mirror strategy (13GB → cloud)
- Evaluating consolidation progress (track delta)

---

**This is your baseline.** All consolidation work should reduce these numbers while preserving capability.

**Next census:** Run `bash /tmp/repo_census.sh > REPO_CENSUS_$(date +%Y%m%d).md` after major changes.
