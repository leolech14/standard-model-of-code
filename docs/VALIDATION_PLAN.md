# Scientific Validation Plan: Standard Model of Code

> **Goal:** Establish empirical validity of claims with publishable rigor (ICSE/OOPSLA standards)

---

## 1. Research Questions

### RQ1: Completeness
**Claim:** The 167-atom taxonomy covers 100% of syntactic structures.

**Null Hypothesis (H₀):** The taxonomy fails to cover ≥5% of code elements.

**Validation:** Measure coverage on diverse codebases.

---

### RQ2: Accuracy
**Claim:** Pattern-based role detection achieves >85% accuracy.

**Null Hypothesis (H₀):** Role detection accuracy ≤ random baseline.

**Validation:** Compare against ground truth (manual annotation).

---

### RQ3: Orthogonality
**Claim:** Dimensions (WHAT, WHY, HOW) have mutual information < 0.2 bits.

**Null Hypothesis (H₀):** MI ≥ 0.5 bits (dimensions are correlated).

**Validation:** Measure MI on multiple datasets.

---

### RQ4: Generalization
**Claim:** Results generalize across languages and domains.

**Null Hypothesis (H₀):** Accuracy drops >10% on unseen languages/domains.

**Validation:** Cross-language, cross-domain testing.

---

## 2. Dataset Construction

### 2.1 Benchmark Suite (REQUIRED)

**Size:** 100+ repositories, 1M+ code elements

**Diversity:**
| Dimension | Coverage |
|-----------|----------|
| **Languages** | Python, JavaScript, TypeScript, Java, Rust, Go |
| **Domains** | Web apps, data science, infrastructure, games, finance |
| **Size** | Small (<1k LOC), Medium (1k-10k), Large (>10k) |
| **Age** | Recent (2023-2025), Legacy (pre-2020) |
| **Style** | OOP, Functional, Procedural |

**Selection Criteria:**
- Popular (>1k GitHub stars)
- Actively maintained (commits in last 6 months)
- Well-documented (READMEs, comments)
- Diverse teams (avoid single-author bias)

**Public availability:** All repos must be open-source (reproducibility)

---

### 2.2 Ground Truth Establishment

**Problem:** We need "correct answers" to measure accuracy.

**Solution: Multi-Rater Annotation**

1. **Sample:** Randomly select 2,000 code elements from benchmark
2. **Annotators:** 3 independent experts (CS PhDs or senior engineers)
3. **Task:** Manually classify each element:
   - Atom (167 options)
   - Role (27 options)
   - RPBL scores (4 dimensions, 1-10 scale)

4. **Agreement:** Measure inter-rater reliability (Cohen's κ)
   - κ > 0.8 = Strong agreement → use as ground truth
   - κ < 0.8 = Resolve conflicts via discussion

5. **Budget:** ~60 hours × 3 annotators = 180 person-hours

---

## 3. Experimental Design

### 3.1 Train/Test Split

**80/20 split:**
- **Train:** 80 repos (800k elements) → tune patterns
- **Test:** 20 repos (200k elements) → measure accuracy

**Stratified:** Ensure test set has same language/domain distribution as train.

---

### 3.2 Baseline Comparisons

**We must beat baselines to claim novelty:**

| Baseline | Method | Expected Accuracy |
|----------|--------|-------------------|
| **Random** | Random role assignment | ~3.7% (1/27) |
| **Majority Class** | Always predict "Utility" | ~15% |
| **Keyword Only** | Simple prefix matching | ~60% |
| **LLM (GPT-4)** | Zero-shot classification | ~70%? |

**Our claim:** Pattern matching achieves >85% (better than all baselines)

---

### 3.3 Ablation Study

**Question:** Which patterns contribute most to accuracy?

**Method:** Remove one pattern type at a time, measure drop:

| Removed Pattern | Accuracy Drop | Conclusion |
|----------------|---------------|------------|
| Prefix (`get_`, `set_`) | -15% | Critical |
| Suffix (`Service`, `Repository`) | -8% | Important |
| Inheritance (`BaseRepository`) | -5% | Helpful |
| Path hints (`/domain/`, `/infra/`) | -2% | Minor |

**Takeaway:** Shows which patterns are load-bearing.

---

## 4. Metrics & Evaluation

### 4.1 Primary Metrics

**Accuracy:**
```
Accuracy = (Correct Classifications) / (Total Classifications)
```

**Precision & Recall (per role):**
```
Precision = TP / (TP + FP)
Recall = TP / (TP + FN)
F1 = 2 × (Precision × Recall) / (Precision + Recall)
```

**Confusion Matrix:**
- Shows which roles are confused (e.g., Query vs Command)

---

### 4.2 Secondary Metrics

**Coverage:**
```
Coverage = (Elements with assigned role) / (Total elements)
```
Target: 100%

**Confidence Calibration:**
- High-confidence predictions (>75%) should be more accurate
- Plot: Confidence vs Actual Accuracy

**Speed:**
```
Throughput = Elements analyzed / Second
```
Target: >1,000/sec (scalability)

---

## 5. Statistical Analysis

### 5.1 Confidence Intervals

**Report:**
```
Accuracy = 87.6% (95% CI: 87.4% - 87.8%)
```

**Method:** Bootstrap resampling (1,000 iterations)

---

### 5.2 Significance Testing

**Question:** Is our 87.6% significantly better than baseline (60%)?

**Method:** Paired t-test
- H₀: No difference
- H₁: Our method is better
- α = 0.05

**Expected:** p < 0.001 (highly significant)

---

### 5.3 Effect Size

**Report:**
```
Cohen's d = 2.1 (large effect)
```

**Interpretation:** Difference is not just statistically significant, but **practically meaningful**.

---

## 6. Threats to Validity

### 6.1 Internal Validity

**Threat:** Patterns overfit to our training set.

**Mitigation:** Strict train/test split, cross-validation.

---

### 6.2 External Validity

**Threat:** Results don't generalize beyond our benchmark.

**Mitigation:**
- Test on new languages (not in benchmark)
- Test on proprietary codebases (industrial case study)
- Invite community to test on their repos

---

### 6.3 Construct Validity

**Threat:** Ground truth annotations are subjective.

**Mitigation:**
- Multi-rater design (3 annotators)
- Inter-rater reliability (κ > 0.8)
- Clear annotation guidelines

---

### 6.4 Conclusion Validity

**Threat:** Statistical assumptions violated.

**Mitigation:**
- Large sample size (N > 1,000)
- Multiple testing correction (Bonferroni)
- Sensitivity analysis (vary parameters)

---

## 7. Reproduction Package

**Publish a complete artifact:**

```
standard-model-benchmark/
├── data/
│   ├── repos.csv           # List of 100 repos with metadata
│   ├── ground_truth.csv    # 2,000 annotated elements
│   └── raw/                # Full dataset (1M elements)
├── scripts/
│   ├── download.sh         # Clone all repos
│   ├── analyze.py          # Run Collider on benchmark
│   ├── evaluate.py         # Compute metrics
│   └── visualize.py        # Generate plots
├── results/
│   ├── accuracy.csv        # Per-repo accuracy
│   ├── confusion.png       # Confusion matrix
│   └── ablation.csv        # Ablation study results
├── README.md               # Instructions
└── requirements.txt
```

**Anyone can run:**
```bash
./download.sh
./analyze.py
./evaluate.py
```

**Output:** Same metrics we report (reproducibility)

---

## 8. Publication Checklist

### For ICSE/OOPSLA Submission

- [ ] Research questions clearly stated
- [ ] Null hypotheses defined
- [ ] Benchmark dataset public (Zenodo/OSF)
- [ ] Ground truth annotated (multi-rater)
- [ ] Train/test split documented
- [ ] Baselines implemented and compared
- [ ] Ablation study conducted
- [ ] Statistical significance tested
- [ ] Confidence intervals reported
- [ ] Threats to validity addressed
- [ ] Reproduction package released
- [ ] Ethics review (if human subjects involved)

---

## 9. Timeline & Resources

### Phase 1: Dataset (2 months)
- Select 100 repos
- Download and preprocess
- **Deliverable:** `repos.csv`

### Phase 2: Annotation (1 month)
- Hire 3 annotators
- Annotate 2,000 samples
- **Deliverable:** `ground_truth.csv`

### Phase 3: Experiments (1 month)
- Run Collider on benchmark
- Compute metrics
- Run ablation study
- **Deliverable:** `results/` directory

### Phase 4: Analysis (2 weeks)
- Statistical tests
- Generate plots
- **Deliverable:** Paper draft

### Phase 5: Reproduction (2 weeks)
- Package scripts
- Test on fresh machine
- **Deliverable:** Public artifact

**Total:** ~4.5 months, 3-4 researchers

---

## 10. Budget Estimate

| Item | Cost |
|------|------|
| 3 Annotators (60h each @ $50/h) | $9,000 |
| Compute (AWS for large-scale run) | $500 |
| Archive (Zenodo/OSF hosting) | Free |
| Conference submission fee | $75 |
| Open-access publication (if accepted) | $0-$3,000 |
| **Total** | **~$10,000-$13,000** |

---

## 11. Success Criteria

**For publication acceptance:**

1. Coverage ≥ 95% ✓
2. Accuracy ≥ 80% (significantly better than baselines) ✓
3. Generalization: <10% accuracy drop across languages ✓
4. Reproducibility: Others can replicate results ✓
5. Statistical rigor: p < 0.05, large effect size ✓

**For impact:**
- Tool adopted by 100+ users
- Benchmark becomes standard (like SonarQube's rule sets)
- Citations in follow-up research

---

**This is what a professional research team would do to validate the Standard Model of Code.**
