# L2 Hypotheses: 33-Repo Calibration

> **Status:** DRAFT - Pending 99-repo validation
> **Date:** 2026-01-23
> **Evidence Base:** 33 repos, 77,265 nodes, 6 languages

---

## Summary Statistics

| Metric | Value | 95% CI |
|--------|-------|--------|
| **Repos analyzed** | 33 | - |
| **Total nodes** | 77,265 | - |
| **Top-4 mass mean** | 97.0% | ±1.3% |
| **Top-4 mass median** | 98.8% | - |
| **Unknown rate mean** | 0.34% | ±0.15% |
| **Unknown rate max** | 1.82% | - |

---

## H1: Pareto Concentration (Primary Hypothesis)

### Statement
> **The top 4 structural atoms account for ≥90% of all nodes in any well-formed codebase.**

### Evidence (n=33)
- Mean: 97.0%
- Median: 98.8%
- Min: 85.0% (fastapi)
- Max: 100.0% (7 repos)
- Stdev: 3.9%

### Statistical Test
- 30/33 repos (91%) exceed 90% threshold
- 26/33 repos (79%) exceed 95% threshold
- Only 3/33 repos fall below 90%

### Falsification Criteria
```
FALSIFIED IF:
- >10% of repos in 99-corpus have top-4 mass <80%
- Mean top-4 mass falls below 90%
- Any language stratum has mean <85%
```

### Confidence: **HIGH (91%)**

---

## H2: Function Dominance

### Statement
> **LOG.FNC.M (function/method) is the dominant atom in the majority of codebases.**

### Evidence (n=33)
| Dominant Atom | Repos | Percentage |
|---------------|-------|------------|
| LOG.FNC.M | 19 | 58% |
| ORG.AGG.M | 7 | 21% |
| EXT.GO.013 | 5 | 15% |
| Other | 2 | 6% |

### Interpretation
- Functions dominate in Python, TypeScript, JavaScript, Rust
- Go has different patterns (EXT.GO.013 = Go-specific constructs)
- Java shows ORG.AGG.M dominance (class-based)

### Falsification Criteria
```
FALSIFIED IF:
- LOG.FNC.M dominates <40% of repos in 99-corpus
- A new atom type dominates >30% of repos
```

### Confidence: **HIGH (88%)**

---

## H3: Language Independence

### Statement
> **The Pareto concentration holds across all programming languages with similar effect sizes.**

### Evidence by Language (n=33)

| Language | n | Top-4 Mean | Stdev | Unknown |
|----------|---|------------|-------|---------|
| Java | 5 | **100.0%** | 0.0 | 0.28% |
| TypeScript | 6 | 99.9% | 0.2 | 0.39% |
| JavaScript | 4 | 98.7% | 1.5 | 0.92% |
| Python | 5 | 96.4% | 6.4 | 0.22% |
| Rust | 6 | 94.2% | 2.5 | 0.27% |
| Go | 6 | **93.4%** | 3.3 | 0.12% |

### Observations
- Java shows perfect concentration (likely due to fallback parser)
- Go shows lowest concentration (more diverse atom distribution)
- Python has highest variance (σ=6.4)

### Falsification Criteria
```
FALSIFIED IF:
- Any language has mean top-4 <85% in 99-corpus
- Language variance exceeds 15pp between highest and lowest
- Currently: Java(100%) - Go(93.4%) = 6.6pp variance ✓
```

### Confidence: **MEDIUM (76%)**
*Note: Go/Rust show lower concentration - may indicate real language differences or detector gaps*

---

## H4: Unknown Rate Bound

### Statement
> **A well-tuned parser achieves <5% unknown rate on any mainstream codebase.**

### Evidence (n=33)
- Mean: 0.34%
- Max: 1.82% (express)
- All repos below 2%

### By Language
| Language | Unknown Rate |
|----------|--------------|
| Go | 0.12% |
| Python | 0.22% |
| Rust | 0.27% |
| Java | 0.28% |
| TypeScript | 0.39% |
| JavaScript | 0.92% |

### Falsification Criteria
```
FALSIFIED IF:
- Any repo exceeds 10% unknown rate
- Mean unknown rate exceeds 5%
- Any language stratum exceeds 5% mean
```

### Confidence: **VERY HIGH (97%)**

---

## H5: Domain Invariance

### Statement
> **The structural distribution is invariant across software domains (web, CLI, library, systems).**

### Evidence by Domain (n=33)

| Domain | n | Top-4 Mean |
|--------|---|------------|
| library | 12 | 98.8% |
| web_frontend | 2 | 98.6% |
| ml | 1 | 98.3% |
| web_backend | 6 | 96.1% |
| cli | 8 | 95.4% |
| systems | 3 | 93.6% |

### Observations
- Libraries show highest concentration (closest to "pure" code)
- Systems code shows lowest (more diverse patterns)
- CLI falls between (user-facing complexity)

### Falsification Criteria
```
FALSIFIED IF:
- Domain variance exceeds 10pp in 99-corpus
- Currently: library(98.8%) - systems(93.6%) = 5.2pp ✓
- Any domain falls below 85% mean
```

### Confidence: **MEDIUM (72%)**
*Note: Only 3 systems repos - need more data*

---

## Outlier Analysis

### Repos Below 95% Threshold (n=7)

| Repo | Language | Top-4 | Potential Cause |
|------|----------|-------|-----------------|
| fastapi | Python | 85.0% | Heavy decorator usage |
| hugo | Go | 88.9% | Template system complexity |
| k9s | Go | 89.9% | TUI framework patterns |
| serde | Rust | 90.1% | Macro-heavy code |
| bat | Rust | 92.6% | Syntax highlighting complexity |
| lazygit | Go | 93.6% | Terminal UI patterns |
| alacritty | Rust | 94.7% | GPU/systems code |

### Pattern
- **Go**: 3/6 outliers (50%) - may need Go-specific detector improvements
- **Rust**: 3/6 outliers (50%) - macro system creates edge cases
- **Python**: 1/5 outlier (20%) - fastapi's heavy metaprogramming

### Hypothesis H6 (Emerging)
> **Metaprogramming-heavy codebases show 5-15% lower Pareto concentration.**

---

## Validation Requirements for L2 → L3

To promote these hypotheses to L3 (stable theory):

| Requirement | Threshold | Current |
|-------------|-----------|---------|
| Sample size | ≥99 repos | 33 ✓ (need more) |
| H1 (Pareto) holds | >85% of repos | 91% ✓ |
| H2 (Function dominance) | >50% of repos | 58% ✓ |
| H3 (Language independence) | <15pp variance | 6.6pp ✓ |
| H4 (Unknown bound) | <5% all repos | 1.82% max ✓ |
| H5 (Domain invariance) | <10pp variance | 5.2pp ✓ |

---

## Next Steps

1. **Run 99-repo validation** - Triple sample size
2. **Investigate Go/Rust outliers** - Detector gaps or real patterns?
3. **Add metaprogramming metric** - Track decorator/macro density
4. **Formalize H6** - Metaprogramming penalty hypothesis

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2026-01-23 | Initial 33-repo hypotheses |
