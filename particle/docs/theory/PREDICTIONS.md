# Falsifiable Predictions of the Standard Model of Code

**Status:** Academic Draft
**Version:** 1.0.0
**Date:** 2026-02-01

---

## Abstract

A scientific theory must make predictions that can be proven wrong. This document enumerates the falsifiable predictions of the Standard Model of Code (SMC), specifying for each prediction: the claim, the test, and the falsification criterion. These predictions transform SMC from a descriptive framework into a testable reference model.

---

## 1. Classification Predictions

### P1: Complete Classification

**Claim:** Every syntactically valid code entity can be classified into exactly one of 167 atom types.

**Test:**
```
1. Collect corpus of 10,000 entities from diverse projects
2. Attempt classification of each entity
3. Count entities with 0 classifications
4. Count entities with 2+ classifications
```

**Falsification criterion:**
- If >5% of entities fit 0 atom types: Taxonomy is incomplete
- If >5% of entities fit 2+ atom types: Atoms are not mutually exclusive

**Current status:** Preliminary testing shows <2% unclassifiable, <1% ambiguous

---

### P2: Dimensional Orthogonality

**Claim:** The 8 classification dimensions are statistically independent (orthogonal).

**Test:**
```
1. Classify 10,000 entities on all 8 dimensions
2. Compute pairwise Pearson correlation for all 28 dimension pairs
3. Compute variance inflation factors (VIF) for regression
```

**Falsification criterion:**
- If any |r| > 0.7: Those dimensions are not independent
- If any VIF > 10: Multicollinearity indicates redundancy

**Current status:** Theoretical independence claimed, empirical test pending

---

### P3: Level Ordering

**Claim:** Containment relationships follow strict level ordering.

$$\text{contains}(a, b) \Rightarrow \lambda(a) > \lambda(b)$$

**Test:**
```
1. Extract all containment edges from 100 projects
2. For each edge, verify λ(container) > λ(contained)
3. Count violations
```

**Falsification criterion:**
- If any containment edge has λ(container) ≤ λ(contained): Axiom violated

**Current status:** 0 violations in Collider self-analysis

---

### P4: MECE Partition

**Claim:** Every project artifact belongs to exactly one of {Codome, Contextome}.

$$\forall f \in \mathcal{P}: f \in \mathcal{C} \oplus f \in \mathcal{X}$$

**Test:**
```
1. Enumerate all files in 100 projects
2. Classify each as Codome or Contextome
3. Count files in neither (0 classifications)
4. Count files in both (2 classifications)
```

**Falsification criterion:**
- If any file is neither executable nor non-executable: Partition incomplete
- If any file is both executable and non-executable: Contradiction

**Current status:** 100% classification achieved in all tested projects

---

## 2. Structural Predictions

### P5: Atom Derivability

**Claim:** Every atom can be derived from the 8 dimensions. No atom is primitive.

**Test:**
```
1. For each of 167 atoms, express as dimensional conjunction
2. Verify that dimensional values uniquely identify the atom
3. Check for atoms requiring extra information
```

**Falsification criterion:**
- If any atom cannot be expressed as dimensional conjunction: Atoms not derived from dimensions

**Current status:** Derivability proven by construction

---

### P6: Containment Transitivity

**Claim:** Containment is transitive.

$$\text{contains}(a, b) \land \text{contains}(b, c) \Rightarrow \text{contains}(a, c)$$

**Test:**
```
1. Build containment graph for 100 projects
2. Compute transitive closure
3. Verify all implied containments exist
```

**Falsification criterion:**
- If transitive closure adds edges not implied by hierarchy: Structure is not a proper hierarchy

**Current status:** Verified in AST-derived containment

---

### P7: Ring Balance in Healthy Codebases

**Claim:** Healthy, well-maintained codebases have balanced ring distribution.

$$\forall r \in \{CORE, INNER, OUTER, SHELL\}: 0.1 \leq \frac{|r|}{|N|} \leq 0.4$$

**Test:**
```
1. Select 50 "healthy" projects (active, low bug count, good reviews)
2. Select 50 "unhealthy" projects (abandoned, high bugs, complaints)
3. Compute ring distribution for each
4. Compare distributions
```

**Falsification criterion:**
- If healthy projects have imbalanced rings: Ring balance is not a health indicator
- If unhealthy projects have balanced rings: Ring balance is not a health indicator

**Current status:** Hypothesis, empirical test pending

---

## 3. Quality Predictions

### P8: Boundary-Bug Correlation

**Claim:** Entities with high BOUNDARY dimension (D4) have more defects.

**Test:**
```
1. Classify 5,000 functions by LAYER dimension
2. Collect bug counts per function from issue trackers
3. Compute correlation between LAYER=boundary and bug count
```

**Falsification criterion:**
- If r < 0.15 (small effect): No meaningful correlation
- If boundary functions have fewer bugs: Prediction reversed

**Current status:** Hypothesis based on integration point complexity

---

### P9: Utility Simplicity

**Claim:** Utility atoms (pure helper functions) have lower complexity than Service atoms.

**Test:**
```
1. Identify all Utility and Service atoms in 50 projects
2. Compute cyclomatic complexity for each
3. Compare distributions
```

**Falsification criterion:**
- If mean complexity(Utility) ≥ mean complexity(Service): Prediction falsified
- If Cohen's d < 0.3 (small effect): Difference not meaningful

**Current status:** Hypothesis based on architectural expectations

---

### P10: Purity-Coverage Correlation

**Claim:** Pure functions (PURITY=Pure) have higher test coverage than impure functions.

**Test:**
```
1. Classify 2,000 functions by PURITY dimension
2. Measure test coverage per function
3. Compute correlation
```

**Falsification criterion:**
- If r < 0.2: No meaningful correlation
- If impure functions have higher coverage: Prediction reversed

**Current status:** Hypothesis based on testability theory

---

## 4. Architectural Predictions

### P11: Layer Violation Bugs

**Claim:** Layer violations (lower layer calling higher layer) correlate with bugs.

**Test:**
```
1. Detect all layer violations in 50 projects
2. For each violation, measure bug frequency in involved components
3. Compare to components without violations
```

**Falsification criterion:**
- If violations show no bug increase: Layer ordering is not predictive

**Current status:** Hypothesis based on coupling theory

---

### P12: Level-Complexity Correlation

**Claim:** Higher-level entities have lower inherent complexity per entity.

$$\text{Complexity}(e) / \text{LOC}(e) \text{ decreases with } \lambda(e)$$

**Test:**
```
1. Compute complexity density for entities at each level
2. Regress against level
3. Test for negative slope
```

**Falsification criterion:**
- If slope ≥ 0: Higher levels are not simpler per line

**Current status:** Hypothesis based on abstraction theory

---

### P13: Purpose Focusing

**Claim:** Purpose variance decreases with level (focusing funnel).

$$\text{Var}[\pi(e) \mid \lambda(e) = L] \text{ decreases with } L$$

**Test:**
```
1. Compute purpose vectors for entities at each level
2. Measure variance of purpose direction at each level
3. Test for monotonic decrease
```

**Falsification criterion:**
- If variance increases with level: Focusing funnel hypothesis falsified

**Current status:** Theoretical prediction from Axiom D4

---

## 5. Emergence Predictions

### P14: Emergence at Composition

**Claim:** Emergent properties appear when composing entities.

$$\|\pi(\text{parent})\| > \sum_i \|\pi(\text{child}_i)\|$$

**Test:**
```
1. For 1,000 composite entities (classes, modules)
2. Compute purpose magnitude for composite
3. Compute sum of child purpose magnitudes
4. Compare
```

**Falsification criterion:**
- If parent magnitude ≤ child sum: No emergence

**Current status:** Theoretical prediction from Axiom D5

---

### P15: Information Gain at Composition

**Claim:** Higher-level descriptions provide predictive power.

$$I(\text{class type}; \text{behavior}) > \sum I(\text{method}; \text{behavior})$$

**Test:**
```
1. Select 500 classes with known behaviors (e.g., bug patterns)
2. Train predictor on class-level features
3. Train predictor on method-level features
4. Compare predictive accuracy
```

**Falsification criterion:**
- If method-level predicts better: Higher abstraction adds no information

**Current status:** Hypothesis based on emergence theory

---

## 6. Observability Predictions

### P16: Triad Completeness

**Claim:** All three observers (Structural, Operational, Generative) are necessary for complete observability.

**Test:**
```
1. Define "complete observability" operationally
2. Attempt to achieve completeness with only 2 observers
3. Identify blind spots
```

**Falsification criterion:**
- If any 2 observers achieve completeness: Third observer is redundant

**Current status:** Theoretical proof from Axiom G3

---

## 7. Summary Table

| ID | Prediction | Falsification Criterion | Status |
|----|------------|------------------------|--------|
| P1 | Complete Classification | >5% unclassifiable | Preliminary pass |
| P2 | Dimensional Orthogonality | \|r\| > 0.7 | Pending |
| P3 | Level Ordering | Any violation | Verified |
| P4 | MECE Partition | Any overlap/gap | Verified |
| P5 | Atom Derivability | Any primitive atom | Verified |
| P6 | Containment Transitivity | Non-transitive | Verified |
| P7 | Ring Balance | No health correlation | Pending |
| P8 | Boundary-Bug Correlation | r < 0.15 | Pending |
| P9 | Utility Simplicity | d < 0.3 | Pending |
| P10 | Purity-Coverage | r < 0.2 | Pending |
| P11 | Layer Violations | No bug correlation | Pending |
| P12 | Level-Complexity | Positive slope | Pending |
| P13 | Purpose Focusing | Increasing variance | Pending |
| P14 | Emergence at Composition | No magnitude gain | Pending |
| P15 | Information Gain | Method-level wins | Pending |
| P16 | Triad Completeness | 2 observers suffice | Theoretical |

---

## 8. Implications of Falsification

If predictions are falsified:

| Prediction | If Falsified, Then |
|------------|-------------------|
| P1 (Classification) | Add atoms or accept incompleteness |
| P2 (Orthogonality) | Merge correlated dimensions |
| P3 (Level Ordering) | Revise level definitions |
| P4 (MECE) | Add intermediate category |
| P7 (Ring Balance) | Ring is descriptive, not normative |
| P8-P10 (Quality) | Revise quality hypotheses |
| P11-P15 (Architecture) | Revise architectural hypotheses |
| P16 (Observability) | Reduce to 2 observers |

**Key insight:** Falsification would not invalidate SMC entirely, but would require revising specific axioms or predictions. This is how science progresses.

---

## 9. Conclusion

The Standard Model of Code makes 16 explicit, falsifiable predictions. These predictions span:

- **Classification** (P1-P4): Can we reliably classify entities?
- **Structure** (P5-P7): Does the structure hold mathematically?
- **Quality** (P8-P10): Does classification predict quality?
- **Architecture** (P11-P15): Does hierarchy predict behavior?
- **Observability** (P16): Is the triad minimal?

Current verification status:
- 5 predictions verified (P3, P4, P5, P6, one aspect of P1)
- 10 predictions pending empirical test
- 1 prediction with theoretical proof (P16)

These predictions distinguish SMC from untestable frameworks and position it as a testable reference model subject to empirical evaluation.

---

*This document addresses Gap 6 (Falsifiable Predictions) from the SMC Academic Gap Analysis.*
