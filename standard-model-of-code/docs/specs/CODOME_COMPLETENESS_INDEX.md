# Codome Completeness Index (CCI)

> **Status:** DRAFT
> **Date:** 2026-01-23
> **Phase:** 10 (Adaptive Intelligence Layer)

---

## Problem Statement

When analyzing a codebase, we must determine:

1. **ALL the codebase nodes there are** (no false negatives)
2. **ONLY the codebase nodes there are** (no false positives)

This is a classification problem where we must distinguish:
- **Signal:** Code written by/for this project
- **Noise:** External dependencies, generated artifacts, build outputs

---

## The Completeness Model

### Ground Truth Categories

Every file/node in a repository belongs to one category:

| Category | Code | Description | Treatment |
|----------|------|-------------|-----------|
| **SOURCE** | S | Original source code written for this project | MUST analyze |
| **VENDOR** | V | Third-party dependencies (node_modules, vendor/) | MUST exclude |
| **GENERATED** | G | Machine-generated code (protobuf, lockfiles) | SHOULD exclude |
| **BUILD** | B | Build artifacts (dist/, out/, coverage/) | MUST exclude |
| **CONFIG** | C | Configuration files (yaml, json, env) | MAY analyze |
| **DOCS** | D | Documentation (md, rst, txt) | MAY analyze |

### Analysis Outcomes

| Outcome | Symbol | Description |
|---------|--------|-------------|
| **True Positive** | TP | SOURCE correctly analyzed |
| **False Positive** | FP | VENDOR/BUILD incorrectly analyzed |
| **True Negative** | TN | VENDOR/BUILD correctly excluded |
| **False Negative** | FN | SOURCE incorrectly excluded |

---

## The CCI Formula

### Primary Metrics

```
SENSITIVITY (Recall) = TP / (TP + FN)
"What % of our code did we capture?"

SPECIFICITY = TN / (TN + FP)
"What % of vendor code did we exclude?"

PRECISION = TP / (TP + FP)
"What % of analyzed nodes are actually ours?"

F1_SCORE = 2 * (Precision * Recall) / (Precision + Recall)
"Harmonic mean of precision and recall"

F2_SCORE = 5 * (Precision * Recall) / (4 * Precision + Recall)
"Recall-weighted harmonic mean (prioritizes completeness)"
```

### Codome Completeness Index

**RECOMMENDATION (Validated by AI Review):** Use F2 Score for completeness-focused analysis.

| Formula | Use Case | Rationale |
|---------|----------|-----------|
| **F2** (Recommended) | Completeness | Weights Recall higher - penalizes missing code |
| G-Mean | Balanced | `sqrt(Sensitivity * Specificity)` - geometric mean |
| Original | Legacy | `Sensitivity * Specificity` - has "zero penalty" issue |

**Why F2 over F1?**
- For "completeness," Sensitivity (Recall) is more important than Precision
- We want to find ALL atoms first, then filter noise later
- F2 penalizes missing an IIFE pattern (False Negative) more than misclassifying a comment (False Positive)

**Why not raw Sensitivity × Specificity?**
1. **Zero Penalty:** If either metric is 0, entire score is 0 (hides progress)
2. **Specificity Trap:** In code analysis, True Negatives are conceptually infinite (whitespace, comments, non-target constructs)

```
CCI_F2 = F2_SCORE * 100

CCI_GMEAN = sqrt(Sensitivity * Specificity) * 100  (Alternative)

Interpretation:
  CCI >= 95%  → EXCELLENT (production ready)
  CCI 85-94%  → GOOD (minor gaps)
  CCI 70-84%  → FAIR (needs tuning)
  CCI < 70%   → POOR (significant blind spots)
```

---

## Root Cause Attribution

When CCI < 100%, we must attribute the gap:

### Attribution Categories

| Code | Category | Blame | Description |
|------|----------|-------|-------------|
| **P** | Parser Blind Spot | OUR_FAULT | Our parser/queries don't detect valid patterns |
| **Q** | Query Missing | OUR_FAULT | Tree-sitter query doesn't exist for this construct |
| **R** | Repo Pollution | THEIR_FAULT | Vendor code in non-standard location |
| **M** | Minified Unmarked | THEIR_FAULT | Minified code without .min.js extension |
| **A** | Ambiguous Boundary | GRAY_ZONE | Code that could be either (vendored-then-modified) |
| **C** | Config Missing | USER_FAULT | User didn't configure exclusions |
| **U** | Unknown | UNKNOWN | Undiagnosed cause |

### Attribution Formula

```
For each False Negative (missed source code):
  Attribute to: P, Q, C, or U

For each False Positive (included vendor):
  Attribute to: R, M, A, C, or U

Gap Attribution Report:
  OUR_FAULT   = (P + Q) / Total_Errors
  THEIR_FAULT = (R + M) / Total_Errors
  GRAY_ZONE   = A / Total_Errors
  USER_FAULT  = C / Total_Errors
```

---

## Repo Health Indicators

### Pollution Index (PI)

Measures how "polluted" a repo is with non-standard structures:

```
PI = (Vendor_In_Wrong_Place + Unmarked_Minified + Mixed_Source_Vendor) / Total_Files

Interpretation:
  PI < 5%   → CLEAN (well-organized repo)
  PI 5-15%  → MODERATE (some cleanup needed)
  PI > 15%  → POLLUTED (significant structure issues)
```

### Pollution Patterns

| Pattern | Detection | Severity |
|---------|-----------|----------|
| `src/vendor/` | Vendor inside source tree | HIGH |
| `lib/*.min.js` | Minified in lib/ | MEDIUM |
| `utils/lodash.js` | Vendored single file | MEDIUM |
| `src/generated/` | Generated in source | LOW |
| No `.gitignore` | Missing ignore config | HIGH |

---

## Survey Output Schema

The survey module should output CCI metrics:

```yaml
codome_completeness:
  # Raw counts
  total_files: 4421
  source_files: 802
  vendor_files: 3540
  generated_files: 45
  build_files: 34

  # Classification results
  analyzed: 802
  excluded: 3619

  # Metrics
  sensitivity: 0.99      # 99% of source captured
  specificity: 0.98      # 98% of vendor excluded
  precision: 0.97        # 97% of analyzed is source
  cci: 97.0              # Overall completeness

  # Attribution (if CCI < 100%)
  false_negatives:
    - file: "modules/main.js"
      cause: "P"  # Parser blind spot (anonymous IIFE)

  false_positives: []

  # Repo health
  pollution_index: 0.02  # 2% pollution
  pollution_patterns:
    - pattern: "vendor_in_src"
      count: 0
    - pattern: "unmarked_minified"
      count: 0

  # Verdicts
  cci_verdict: "EXCELLENT"
  pollution_verdict: "CLEAN"
  attribution:
    our_fault: 0.01
    their_fault: 0.00
    gray_zone: 0.00
    user_fault: 0.00
```

---

## Implementation Tasks

| Task | Status | Description |
|------|--------|-------------|
| Define ground truth oracle | IN_PROGRESS | Using heuristic-based (exclusions.yaml) |
| **Add CCI to SurveyResult** | ✅ DONE | `survey.py` - CCIMetrics calculated in run_survey() |
| Implement attribution logic | TODO | Diagnose each FN/FP with category codes |
| Add pollution detection | ✅ DONE | `survey.py` - PollutionAlert detection integrated |
| **Output CCI in survey report** | ✅ DONE | `print_survey_report()` displays CCI metrics |
| **Precision Context Fetcher** | ✅ DONE | `context-management/tools/ai/research/precision_fetcher.py` |
| **F2 Formula Integration** | ✅ DONE | Spec updated with AI-validated recommendation |
| **Config for Research** | ✅ DONE | `aci_config.yaml` updated with research section |
| **CCI Unit Tests** | ✅ DONE | `tests/test_cci.py` - 10 tests covering all scenarios |
| Integrate fetcher with survey | TODO | Auto-trigger on FN detection |
| Knowledge injection pipeline | TODO | Apply guidance to patterns/learned/ |

---

## Example: viz/assets Analysis

```
Ground Truth:
  SOURCE: 55 files (modules/*.js)
  VENDOR: 4 files (vendor/*.min.js)
  Total: 59 files

Analysis Results:
  Analyzed: 55 files → 802 nodes
  Excluded: 4 files → 0 nodes

Classification:
  TP = 54 (source files analyzed)
  FN = 1 (main.js - 0 nodes due to anonymous IIFE)
  TN = 4 (vendor files excluded)
  FP = 0 (no vendor analyzed)

Metrics:
  Sensitivity = 54/55 = 98.2%
  Specificity = 4/4 = 100%
  Precision = 802/802 = 100%
  CCI = 98.2%

Attribution:
  FN (main.js): Cause = P (Parser blind spot - anonymous IIFE)
  OUR_FAULT = 100% of errors
```

---

## Future: Ground Truth Oracle

To compute CCI accurately, we need a "ground truth" for classification.

### Option 1: Heuristic-Based (Current)

```python
def is_source(file_path):
    # Exclude known vendor patterns
    if matches_vendor_pattern(file_path):
        return False
    # Exclude generated patterns
    if matches_generated_pattern(file_path):
        return False
    # Assume source
    return True
```

**Pro:** Fast, no manual work
**Con:** Heuristics may be wrong

### Option 2: Git-Based

```python
def is_source(file_path):
    # Check if file is in .gitignore
    if is_gitignored(file_path):
        return False
    # Check if file was authored by project contributors
    authors = git_blame(file_path)
    return any(a in project_contributors for a in authors)
```

**Pro:** Uses actual project metadata
**Con:** Vendored-then-modified files still ambiguous

### Option 3: Manifest-Based

```python
def is_source(file_path):
    # Check package.json dependencies
    if in_node_modules(file_path):
        pkg = get_package_name(file_path)
        return pkg not in package_json['dependencies']
    return True
```

**Pro:** Precise for npm/pip projects
**Con:** Doesn't cover all ecosystems

### Option 4: LLM-Assisted

```python
def is_source(file_path, content):
    prompt = f"Is this file project source code or vendor dependency? {content[:1000]}"
    return llm.classify(prompt) == "SOURCE"
```

**Pro:** Handles ambiguous cases
**Con:** Slow, expensive, non-deterministic

---

## Precision Context Fetching (OUR_FAULT Resolution)

When CCI attribution reveals OUR_FAULT gaps (parser blind spots, missing patterns),
the system can auto-fetch external knowledge to close the gap.

### Architecture

```
Gap Detector → Gap Profile → Cache Check → Perplexity API (sonar-pro) → Guidance Parser → Knowledge Store
```

### Implementation

Location: `context-management/tools/ai/research/precision_fetcher.py`

```python
from precision_fetcher import PrecisionContextFetcher, GapProfile

fetcher = PrecisionContextFetcher()
gap = GapProfile(
    language="javascript",
    missing_atom="LOG.MOD.IIFE",
    context_snippet="(function() { ... })();",
    error_type="MISSING_DETECTION"
)
result = await fetcher.resolve_gap(gap)
# Returns: tree_sitter_query, detection_regex, edge_cases, implementation_tips
```

### Configuration

Add to `context-management/config/aci_config.yaml`:

```yaml
research:
  model: "sonar-pro"
  max_monthly_budget_usd: 5.00
  cache_ttl_hours: 168  # 1 week
```

### Output Schema

```json
{
  "pattern_name": "IIFE Module Pattern",
  "detection_regex": "\\(function\\s*\\(\\)\\s*\\{",
  "tree_sitter_query": "(call_expression function: (parenthesized_expression (function_expression)))",
  "edge_cases": [
    "Arrow function IIFEs: (() => {...})()",
    "Named IIFEs: (function named() {...})()",
    "IIFEs with parameters: (function(global) {...})(window)"
  ],
  "implementation_tips": "Check for call_expression where callee is parenthesized_expression containing function",
  "confidence": 0.92
}
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.2.0 | 2026-01-23 | Added F2 Score recommendation (AI validated), Precision Context Fetching architecture |
| 0.1.0 | 2026-01-23 | Initial draft |
