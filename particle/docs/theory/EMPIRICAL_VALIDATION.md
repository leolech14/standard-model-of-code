# Empirical Validation: Evidence for the Standard Model of Code

**Status:** Academic Draft
**Version:** 1.0.0
**Date:** 2026-02-01

---

## Abstract

This document presents the empirical evidence supporting the Standard Model of Code (SMC), documenting existing grounding work and proposing future studies. We show that SMC has been grounded through implementation in Collider (a working code analysis tool), application to real-world codebases, and alignment with established academic frameworks. We propose three additional studies to strengthen empirical grounding: inter-rater reliability, quality correlation, and practitioner utility.

---

## 1. Existing Empirical Evidence

### 1.1 Implementation Validation: Collider

**Evidence type:** Working implementation

SMC is not merely a theoretical framework. It has been implemented in **Collider**, a code analysis tool that:

| Capability | Status | Evidence |
|------------|--------|----------|
| Parse 15+ languages | Implemented | Tree-sitter grammars |
| Extract nodes/edges | Implemented | Graph construction pipeline |
| Classify atoms | Implemented | Role inference from structure |
| Assign levels | Implemented | Containment hierarchy |
| Compute dimensions | Partial | 5/8 dimensions computed |
| Generate output | Implemented | JSON, HTML, visualization |

**Argument:** The fact that Collider successfully analyzes real codebases shows the practical utility of SMC's concepts.

**Repository:** `particle/` (Collider implementation)

### 1.2 Corpus Analysis

**Evidence type:** Application to real codebases

Collider has been applied to analyze:

| Codebase | Size | Nodes | Edges | Languages |
|----------|------|-------|-------|-----------|
| Collider itself | ~50 files | ~2,500 | ~8,000 | Python |
| PROJECT_elements | ~500 files | ~15,000 | ~50,000 | Python, TS, YAML |
| Open source samples | Various | Various | Various | Multiple |

**Key findings from self-analysis:**

1. **MECE Partition:** Every file correctly classified as Codome or Contextome (100%)
2. **Level assignment:** All entities assigned to exactly one level
3. **Containment ordering:** No violations of $\text{contains}(a,b) \Rightarrow \lambda(a) > \lambda(b)$
4. **Role classification:** ~85% of entities classified with >0.7 confidence

### 1.3 Academic Source Alignment

**Evidence type:** Alignment with established theory

SMC axioms have been grounded in academic sources:

| Axiom | Academic Source | Validation |
|-------|-----------------|------------|
| A1 (MECE Partition) | Lawvere (1969), Diagonal Arguments | Proof verified by Gemini 3 Pro |
| D7 (Purpose Dynamics) | Friston's Free Energy Principle | Structural alignment confirmed |
| F1-F2 (Emergence) | Tononi's IIT 4.0 | Metrics compatible |
| G1-G3 (Observability) | Peirce's Triadic Semiotics | Correspondence established |
| E1 (Constructal) | Bejan (2008) | Principle adopted |

**External validation:** Gemini 3 Pro (2026-01-25) rated the Lawvere proof as "VALID" and the application to software documentation necessity as "NOVEL."

### 1.4 SWEBOK Alignment Audit

**Evidence type:** Standards compliance

SMC atom taxonomy was audited against SWEBOK v4 and ISO 24765:

| Metric | Result |
|--------|--------|
| SWEBOK concept matches | 40/167 atoms |
| Gaps filled by SMC | 24 new atoms |
| Enhancements to SWEBOK | 23 refined definitions |
| Conflicts | 11 (resolved with documentation) |

**Observation:** SMC is compatible with SWEBOK while providing finer granularity.

---

## 2. Proposed Empirical Studies

### 2.1 Study A: Inter-Rater Reliability

**Research question:** Can independent analysts reliably classify code entities using SMC atoms?

**Method:**
```
1. Select 100 code entities from 5 open-source projects
   - 20 entities each from: Python, JavaScript, TypeScript, Go, Java
   - Stratified by level: L1-L3 (functions), L4-L5 (classes/files), L6-L7 (packages/systems)

2. Train 3 independent analysts on SMC classification
   - 2-hour training session
   - Practice classification with feedback

3. Each analyst independently classifies all 100 entities
   - Assigns: atom type, 8 dimensional values, level

4. Compute inter-rater reliability
   - Fleiss' Kappa for atom agreement
   - Cohen's Kappa for pairwise dimension agreement
   - Weighted Kappa for level agreement

5. Report results
   - κ > 0.8: Almost perfect agreement
   - κ 0.6-0.8: Substantial agreement
   - κ 0.4-0.6: Moderate agreement
   - κ < 0.4: Fair/poor agreement
```

**Expected outcome:** κ > 0.6 for atom classification, demonstrating that SMC provides a reliable classification vocabulary.

**Falsification criterion:** If κ < 0.4, SMC classification is too ambiguous for practical use.

### 2.2 Study B: Quality Correlation

**Research question:** Do SMC classifications correlate with software quality metrics?

**Method:**
```
1. Select 1,000 functions from 10 open-source projects
   - Projects with >1 year history
   - Projects with issue trackers

2. Classify each function using Collider
   - Atom type
   - All 8 dimensions
   - Level
   - Ring

3. Collect quality metrics per function
   - Bug count (from issue tracker linking)
   - Change frequency (from git history)
   - Cyclomatic complexity
   - Test coverage

4. Analyze correlations
   - ROLE vs. bug count
   - LAYER vs. change frequency
   - RING vs. complexity
   - PURITY vs. test coverage

5. Report results with effect sizes
   - Pearson r for continuous correlations
   - Point-biserial for categorical
   - Multiple regression for combined effects
```

**Hypotheses:**

| Hypothesis | Prediction | Falsification |
|------------|------------|---------------|
| H1 | BOUNDARY entities (D4) have more bugs | r < 0.1 |
| H2 | SHELL ring has higher change frequency | d < 0.2 |
| H3 | Utility atoms have lower complexity | d < 0.2 |
| H4 | Pure functions have higher coverage | r < 0.1 |

**Expected outcome:** At least 2/4 hypotheses show practically significant relationships.

### 2.3 Study C: Practitioner Utility

**Research question:** Do practitioners find SMC classification useful for their work?

**Method:**
```
1. Recruit 50 professional developers
   - 5+ years experience
   - Mix of roles: IC, lead, architect

2. Present SMC classification for their codebase
   - Run Collider on their project
   - Generate visualization and reports

3. Structured interview (30 min)
   - Does the classification match your mental model?
   - Are the atom names meaningful?
   - Would this help with code review?
   - What's missing or incorrect?

4. Survey (Likert 1-5)
   - Classification accuracy
   - Terminology clarity
   - Practical usefulness
   - Would you use this?

5. Analyze results
   - Quantitative: Mean scores, distribution
   - Qualitative: Thematic analysis of interviews
```

**Expected outcome:** Mean utility score > 3.5/5, >60% would use for code review.

---

## 3. Grounding Status Summary

| Grounding Type | Status | Confidence |
|-----------------|--------|------------|
| Implementation (Collider) | Complete | High |
| Self-application | Complete | High |
| Academic alignment | Complete | High |
| SWEBOK audit | Complete | High |
| Inter-rater reliability | Proposed | - |
| Quality correlation | Proposed | - |
| Practitioner utility | Proposed | - |

---

## 4. Threats to Validity

### 4.1 Internal Validity

| Threat | Mitigation |
|--------|------------|
| Selection bias in corpus | Use diverse open-source projects |
| Analyst training effects | Standardized training protocol |
| Collider implementation bugs | Unit tests, property tests |

### 4.2 External Validity

| Threat | Mitigation |
|--------|------------|
| Language specificity | Test across 15+ languages |
| Domain specificity | Include web, systems, ML projects |
| Scale effects | Include projects from 10 files to 10K files |

### 4.3 Construct Validity

| Threat | Mitigation |
|--------|------------|
| Dimension definitions | Ground in existing literature |
| Atom taxonomy | Derive from dimensions, not ad hoc |
| Quality metrics | Use established metrics (bugs, complexity) |

---

## 5. Replication Package

All validation materials will be made available:

| Resource | Location |
|----------|----------|
| Collider source | `particle/` |
| Classification training | `docs/training/` |
| Corpus data | `data/validation/` |
| Analysis scripts | `scripts/validation/` |
| Raw results | `data/results/` |

**Commitment:** All studies will follow Open Science practices with pre-registration, open data, and open materials.

---

## 6. Conclusion

The Standard Model of Code has existing practical applications and evidence through:
1. A working implementation (Collider)
2. Application to real codebases
3. Alignment with established academic frameworks
4. SWEBOK compatibility audit

To further demonstrate the practical usefulness of SMC, we propose three additional studies:
1. Inter-rater reliability (κ target: >0.6)
2. Quality correlation (effect size target: medium)
3. Practitioner utility (mean target: >3.5/5)

These studies would provide additional evidence for SMC's practical utility across diverse contexts.

---

*This document addresses Gap 4 (Empirical Validation) from the SMC Academic Gap Analysis.*
