# Purpose Intelligence (Q-Scores)

> **Status:** Experimental
> **Parent:** [MODEL.md](MODEL.md)
> **Purpose:** Quantitative measurement of how well code serves the holon at each level.

---

## 1. Core Concept

**Purpose Intelligence (Q)** measures *how well* a code holon fulfills its intended purpose.

| Concept | Question | Output |
|---------|----------|--------|
| Purpose Emergence (π) | What IS the purpose? | Labels: Retrieve, Transform, Scattered |
| Purpose Intelligence (Q) | How WELL does it serve? | Score: 0.0 - 1.0 |

**Key Insight:** A component can have a clear purpose label (π = "Repository") but poor intelligence (Q = 0.4) if it violates rules, is scattered, or incomplete.

The Q-score at the top level (π₄) tells you: **Is this codebase sharp or muddy?**

```
Sharp code:   Q(π₄) = 0.85+  → parts serve wholes cleanly
Muddy code:   Q(π₄) = 0.40   → scattered, misaligned, incomplete
```

---

## 2. The Holon Quality Formula

Purpose Intelligence propagates upward through the holon hierarchy:

```
Q(H) = w_parts × Avg(Q_children) + w_intrinsic × I(H)
```

Where:
- **Q(H)**: Purpose Intelligence score for holon H (0.0 - 1.0)
- **w_parts**: Weight for child quality (default: 0.5)
- **w_intrinsic**: Weight for intrinsic quality (default: 0.5)
- **Avg(Q_children)**: Average Q-score of all direct child holons
- **I(H)**: Intrinsic quality score from the five metrics

**Why not simple averaging?**

The holon is more than the sum of its parts. A class with excellent methods but poor structural organization (wrong lifecycle, missing interface) should score lower than its methods suggest. The intrinsic term captures this.

---

## 3. The Five Intrinsic Metrics

Intrinsic quality I(H) is a weighted combination of five metrics:

```
I(H) = 0.25×Q_align + 0.25×Q_cohere + 0.20×Q_dense + 0.15×Q_complete + 0.15×Q_simple
```

### 3.1 Alignment (Q_align)

**Question:** Does this component follow the rules?

**Calculation:**
```
Q_align = 1.0 - (w_A × V_axiom) - (w_B × V_invariant) - (w_P × V_profile)
```

Where:
- V_axiom: Count of Tier A (axiom) violations → w_A = 0.5 (severe)
- V_invariant: Count of Tier B (invariant) violations → w_B = 0.2
- V_profile: Count of architecture profile violations → w_P = 0.1

**Example:**
- A Repository with `lifecycle: Transient` instead of `Singleton` → profile violation
- A pure function with side effects → axiom violation
- A Controller calling Infrastructure directly → invariant violation

### 3.2 Coherence (Q_cohere)

**Question:** Is this component focused on one thing?

**Calculation:**
```
Q_cohere = 1.0 / (1 + H(categories) + w_H × V_heuristic)
```

Where:
- H(categories): Shannon entropy of atom category distribution
- V_heuristic: Count of Tier C heuristic violations (god_class, etc.)
- w_H: Heuristic weight (default: 0.3)

**Entropy Interpretation:**
- Low entropy (< 0.5): Atoms are from one category → coherent
- High entropy (> 1.5): Atoms scattered across categories → god class

**Example:**
```python
# Coherent function (all Logic atoms)
def calculate_tax(amount, rate):
    return amount * rate

# Incoherent function (Logic + IO + Data mixed)
def process_order(order):
    validate(order)           # Logic
    db.save(order)            # IO/Execution
    send_email(order.user)    # IO/Execution
    return OrderDTO(order)    # Data
```

### 3.3 Density (Q_dense)

**Question:** How much signal vs noise?

**Calculation:**
```
Q_dense = Σ weight(atom) / count(atoms)
```

Where atoms are weighted by purpose contribution:
- **High signal (1.0):** CallExpr, BinaryExpr, ReturnStmt, Entity, ValueObject
- **Medium signal (0.5):** Parameter, Assignment, Conditional
- **Low signal (0.2):** PassStmt, Comment, TypeAnnotation, Import

**Example:**
- A 100-line function with 80 signal atoms → Q_dense = 0.8
- A 100-line function with 30 signal atoms and 70 boilerplate → Q_dense = 0.3

### 3.4 Completeness (Q_complete)

**Question:** Are all necessary parts present?

**Calculation:**
```
Q_complete = children_present / children_expected
```

**Special Cases:**
- Orphan code (no parent, no callers) → Q_complete = 0.0
- Missing expected children (Repository without save/find) → reduced score

**Role Expectations:**
| Role | Expected Children |
|------|-------------------|
| Repository | save, find, delete (at least 2) |
| Service | At least one use case method |
| Controller | At least one handler |
| Entity | At least one field |

### 3.5 Simplicity (Q_simple)

**Question:** Is this the minimum necessary complexity?

**Calculation:**
```
Q_simple = 1.0 / (1 + log(1 + complexity_score))
```

Where complexity_score combines:
- Cyclomatic complexity
- Nesting depth
- Number of dependencies
- Lines of code (normalized)

**Interpretation:**
- Q_simple = 0.9: Clean, minimal complexity
- Q_simple = 0.5: Moderate complexity, acceptable
- Q_simple = 0.2: Over-complex, needs refactoring

---

## 4. Propagation Example

### Example: BadRepository Class

```
π₃: BadRepository (class)
├── π₂: save(entity)     - has business logic inside (bad)
└── π₂: findById(id)     - clean query (good)
```

**Step 1: Calculate Q for π₂ methods**

```
findById():
  Q_align    = 1.0  (no violations)
  Q_cohere   = 0.95 (focused query)
  Q_dense    = 0.9  (clean code)
  Q_complete = 1.0  (returns result)
  Q_simple   = 0.95 (simple logic)
  I(findById) = 0.96
  Q(findById) = 0.5 × 1.0 + 0.5 × 0.96 = 0.98

save():
  Q_align    = 0.5  (business logic in repository = violation)
  Q_cohere   = 0.4  (mixed IO + Logic atoms)
  Q_dense    = 0.6  (some boilerplate)
  Q_complete = 1.0  (saves entity)
  Q_simple   = 0.7  (moderate complexity)
  I(save) = 0.58
  Q(save) = 0.5 × 1.0 + 0.5 × 0.58 = 0.79
```

**Step 2: Calculate Q for π₃ class**

```
Avg(Q_children) = (0.98 + 0.79) / 2 = 0.885

BadRepository intrinsic:
  Q_align    = 0.6  (wrong lifecycle: Transient instead of Singleton)
  Q_cohere   = 1.0  (focused role: data access only)
  Q_dense    = 0.8  (standard implementation)
  Q_complete = 1.0  (has both save and find)
  Q_simple   = 0.9  (normal method count)
  I(BadRepository) = 0.84

Q(BadRepository) = 0.5 × 0.885 + 0.5 × 0.84 = 0.86
```

**Result:** Q = 0.86 - Good but not excellent. The poor `save()` method and wrong lifecycle drag down the score.

---

## 5. Codebase Intelligence Score

At the system level (π₄), the aggregated Q-score becomes the **Codebase Intelligence Score**:

```
CODEBASE INTELLIGENCE: 0.72

Breakdown by file:
  user_repository.py    Q = 0.86  ✓
  order_service.py      Q = 0.45  ⚠ (scattered)
  utils.py              Q = 0.32  ✗ (god module)
  auth_controller.py    Q = 0.91  ✓
```

**Interpretation:**
| Score | Quality | Action |
|-------|---------|--------|
| 0.85+ | Sharp | Maintain |
| 0.70-0.84 | Good | Minor improvements |
| 0.50-0.69 | Muddy | Refactoring needed |
| < 0.50 | Poor | Significant rework |

---

## 6. Pipeline Integration

Purpose Intelligence is computed as **Stage 8.5** in the Collider pipeline:

```
Stage 8:   Performance Prediction (complexity scores)
Stage 8.5: Purpose Intelligence (Q-scores)  ← NEW
Stage 9:   Roadmap Evaluation
```

**Dependencies:**
- Requires: atom classification, role detection, violation analysis, complexity metrics
- Produces: Q-score fields on every node

---

## 7. Output Schema

Each node in `unified_analysis.json` receives:

```json
{
  "id": "UserRepository.save",
  "pi2_purpose": "Persist",
  "purpose_intelligence": {
    "Q_total": 0.79,
    "Q_alignment": 0.5,
    "Q_coherence": 0.4,
    "Q_density": 0.6,
    "Q_completeness": 1.0,
    "Q_simplicity": 0.7,
    "Q_intrinsic": 0.58
  }
}
```

---

## 8. Relationship to Other Concepts

| Concept | Relationship |
|---------|--------------|
| Purpose Emergence (π) | Q measures quality OF the π label |
| Purpose Field | Field detects problems; Q quantifies severity |
| Antimatter Laws | Violations directly reduce Q_alignment |
| Coherence Score | Existing coherence → Q_coherence |
| God Class Detection | God class → low Q_coherence |

---

## 9. Future Work

1. **Calibration:** Tune weights (w_parts, w_intrinsic, metric weights) based on real-world validation
2. **Visualization:** Color nodes by Q-score in the 3D graph
3. **Recommendations:** Generate specific improvement suggestions based on lowest Q sub-metric
4. **Trends:** Track Q-score over time to detect architectural decay
