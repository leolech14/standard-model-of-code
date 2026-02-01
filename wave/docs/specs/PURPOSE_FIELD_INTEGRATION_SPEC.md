# PURPOSE FIELD INTEGRATION SPECIFICATION
# Connecting the Three Streams Through the Hierarchical Channel

> **Status:** DRAFT (2026-01-26)
> **Problem:** Coherence = 0.0 despite 92.5% coverage
> **Root Cause:** Three purpose systems exist but don't communicate
> **Theory Reference:** CODESPACE_ALGEBRA.md §10, THEORY_AXIOMS.md Axiom Group D

---

## 1. EXECUTIVE SUMMARY

### 1.1 The Problem

POM reports:
```yaml
purpose_field:
  coverage: 0.925    # 92.5% of nodes have purpose assigned
  coherence: 0.0     # Zero alignment between purposes
```

**Paradox:** Almost everything has purpose, but purposes form no coherent field.

### 1.2 Root Cause Diagnosis

Three independent purpose systems exist in Collider but operate as **silos**:

| System | Location | Computes | Flows |
|--------|----------|----------|-------|
| `semantic_role` | graph_framework.py | utility/orchestrator/hub/leaf | Neither ↑ nor ↓ |
| `pi2_purpose` | purpose_field.py | Role categories (Repository, Service) | Local only |
| `purpose_intelligence` | purpose_intelligence.py | Q-scores | Bottom-up only ↑ |

**Missing:** Cross-communication through the hierarchical `contains` channel.

### 1.3 The Three Fixes Needed

1. **Top-down Constraint Propagation:** Parent purpose constrains child possibilities
2. **Bottom-up Emergence Aggregation:** Child purposes synthesize into parent composite
3. **Coherence Export:** Purpose alignment metrics in unified_analysis.json

---

## 2. THEORETICAL FOUNDATION

### 2.1 Purpose Field Definition (Axiom D1)

From CODESPACE_ALGEBRA.md:

```
𝒫: N → ℝᵏ

Purpose is a vector field over nodes.
Each node has a k-dimensional purpose vector.
```

### 2.2 Purpose Propagation Rules (Axiom D3)

```
DOWNWARD (Inheritance):
  𝒫(child) ⊇ projection of 𝒫(parent)

  Children inherit purpose from parents.
  A method's purpose includes its class's purpose.

UPWARD (Aggregation):
  𝒫(parent) = Σᵢ wᵢ · 𝒫(childᵢ)  (weighted sum)

  Parent purpose is aggregate of child purposes.
  A module's purpose is the sum of its functions' purposes.
```

### 2.3 Transcendence Axiom (Axiom D3)

```
𝒫(entity) = f(role in parent)

An entity at level L has no INTRINSIC purpose.
Its purpose EMERGES from participation in level L+1.

PURPOSE IS RELATIONAL, NOT INTRINSIC.
```

### 2.4 Focusing Funnel (Axiom D4)

```
‖𝒫(L)‖ grows exponentially with L
Var(θ(L)) decreases exponentially with L

L₀: Diffuse (many weak, scattered purposes)
L₁₂: Focused (single strong unified purpose)
```

### 2.5 Emergence Signal (Axiom D5)

```
‖𝒫(parent)‖ > Σᵢ ‖𝒫(childᵢ)‖

WHEN this holds, a NEW LAYER OF ABSTRACTION has emerged.
"Whole > sum of parts" = new layer exists
```

### 2.6 Constructal Channel (Axiom E1)

```
d𝕮/dt = ∇H

Code evolves toward configurations that provide
easier access to FLOW (data, control, dependencies).

PURPOSE MUST FLOW THROUGH THE CONTAINS CHANNEL.
```

---

## 3. CURRENT IMPLEMENTATION STATE

### 3.1 System A: semantic_role (Graph Metrics)

**Location:** `particle/src/core/graph_framework.py:61-94`

```python
def classify_node_role(in_degree: int, out_degree: int) -> str:
    high_in = in_degree >= 5
    high_out = out_degree >= 5

    if high_in and not high_out:
        return "utility"      # Serves many callers
    elif high_out and not high_in:
        return "orchestrator" # Coordinates many callees
    elif high_in and high_out:
        return "hub"          # Critical junction
    else:
        return "leaf"         # Specialized/isolated
```

**Problem:** Uses call graph degree ONLY. Ignores:
- Parent's purpose (transcendence axiom)
- Hierarchy context
- Role field from classification

### 3.2 System B: pi2_purpose (Role Categories)

**Location:** `particle/src/core/purpose_field.py`

Computes atomic purpose from role classification:
- Repository, Service, Controller, Validator, etc.

Has EMERGENCE_RULES (lines 149-170) for composite purpose:
```python
EMERGENCE_RULES = {
    frozenset(['Query', 'Persist']): 'Repository',
    frozenset(['Command', 'Query']): 'Service',
    # ...
}
```

**Problem:**
- Computes locally but doesn't propagate constraints
- Coherence metrics computed but NOT exported to unified_analysis.json
- Children don't consult parent purpose

### 3.3 System C: purpose_intelligence (Q-Scores)

**Location:** `particle/src/core/purpose_intelligence.py`

Bottom-up quality aggregation:
```python
Q(H) = w_parts × Avg(Q_children) + w_intrinsic × I(H)
```

Weights: 50% child quality + 50% intrinsic structural quality

**Problem:**
- Only flows UPWARD (aggregation)
- Never flows DOWNWARD (constraint propagation)
- Doesn't inform children's purpose assignment

### 3.4 The Hierarchical Channel (WORKS)

**Contains edges:** `edge_extractor.py:1124-1140`
**Hierarchy building:** `purpose_field.py:295-306`

```python
# Parent-child linking works correctly
for node_id, node in self.nodes.items():
    if '.' in node.name:
        parent_name = node.name.rsplit('.', 1)[0]
        # Find parent by name matching
        for pid, pnode in self.nodes.items():
            if pnode.name == parent_name:
                node.parent_id = pid
                pnode.children_ids.append(node_id)
```

**Status:** Channel EXISTS but purpose doesn't FLOW through it.

---

## 4. GAP ANALYSIS

### 4.1 Visual: Current State

```
┌─────────────────────────────────────────────────────────────────┐
│                    THREE DISCONNECTED STREAMS                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Stream 1: semantic_role                                      │
│   ─────────────────────                                        │
│   call_graph → degree → utility/orchestrator/hub/leaf          │
│                   ↓                                             │
│              [output]                                           │
│                   ╳ (no connection to hierarchy)               │
│                                                                 │
│   Stream 2: pi2_purpose                                        │
│   ─────────────────────                                        │
│   role_field → classification → Repository/Service/etc.        │
│                   ↓                                             │
│              [computed]                                         │
│                   ╳ (not exported, not propagated)             │
│                                                                 │
│   Stream 3: purpose_intelligence                               │
│   ─────────────────────                                        │
│   children → aggregate → Q_total                               │
│                   ↑                                             │
│              [bottom-up only]                                   │
│                   ╳ (never informs children)                   │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│   HIERARCHICAL CHANNEL (contains edges)                        │
│   ─────────────────────────────────────────────────────────────│
│   Parent ──contains──► Child ──contains──► Grandchild          │
│      │                    │                    │                │
│      └────────────────────┴────────────────────┘                │
│                    EMPTY PIPE                                   │
│              (edges exist, nothing flows)                       │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 What's Missing

| Requirement | Theory | Implementation | Status |
|-------------|--------|----------------|--------|
| Purpose assignment | 𝒫: N → ℝᵏ | semantic_role, pi2_purpose | ✅ Exists |
| Downward propagation | 𝒫(child) ⊇ proj(𝒫(parent)) | NONE | ❌ Missing |
| Upward aggregation | 𝒫(parent) = Σwᵢ𝒫(childᵢ) | purpose_intelligence (partial) | ⚠️ Partial |
| Emergence detection | ‖𝒫(parent)‖ > Σ‖𝒫(childᵢ)‖ | purpose_field (local) | ⚠️ Not exported |
| Coherence metric | Var(θ) alignment | purpose_field.coherence_score | ⚠️ Not exported |
| Channel flow | Constructal H | NONE | ❌ Missing |
| Confidence score | purpose_confidence | NONE (always 0.0) | ❌ Missing |

### 4.3 Evidence from unified_analysis.json

```json
{
  "name": "SemgrepMiner.mine",
  "parent": "SemgrepMiner",
  "pi2_purpose": "Emit",
  "semantic_role": "orchestrator",
  "purpose_intelligence": { "Q_total": 0.948 }
}

// Parent node:
{
  "name": "SemgrepMiner",
  "pi2_purpose": "Initiate",
  "semantic_role": "leaf"
}
```

**Violations observed:**
1. Child purpose (Emit) differs from parent (Initiate) - no coherence check
2. Child role (orchestrator) differs from parent (leaf) - hierarchy ignored
3. No `purpose_from_parent` field
4. No `coherence_score` exported
5. No `composite_purpose` on parent

---

## 5. PROPOSED SOLUTION

### 5.1 Architecture: Unified Purpose Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    UNIFIED PURPOSE FLOW                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   PHASE 1: BOTTOM-UP AGGREGATION                               │
│   ─────────────────────────────────                             │
│                                                                 │
│   L3 Functions ───► aggregate ───► L5 Module composite_purpose │
│   L5 Modules   ───► aggregate ───► L7 System composite_purpose │
│                                                                 │
│   composite_purpose = EMERGENCE_RULES(child_purposes)          │
│   If no rule matches: weighted_centroid(child_purposes)        │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   PHASE 2: TOP-DOWN CONSTRAINT PROPAGATION                     │
│   ─────────────────────────────────                             │
│                                                                 │
│   L7 System purpose ───► constrain ───► L5 allowed_purposes    │
│   L5 Module purpose ───► constrain ───► L3 allowed_purposes    │
│                                                                 │
│   CONSTRAINT_RULES:                                             │
│     Repository: children ∈ {Query, Persist, Transform}         │
│     Service: children ∈ {Command, Query, Validate}             │
│     Controller: children ∈ {Handle, Route, Respond}            │
│                                                                 │
│   purpose_from_parent = project(parent.purpose, child.level)   │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   PHASE 3: COHERENCE VALIDATION                                │
│   ─────────────────────────────────                             │
│                                                                 │
│   For each parent:                                              │
│     child_purposes = [c.purpose for c in children]             │
│     entropy = -Σ p(purpose) × log₂(p(purpose))                 │
│     coherence = 1 - (entropy / max_entropy)                    │
│                                                                 │
│   VIOLATIONS:                                                   │
│     coherence < 0.5 AND children >= 5 → GOD_CLASS              │
│     child.purpose ∉ allowed_purposes → MISPLACED_CHILD         │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   PHASE 4: CONFIDENCE SCORING                                  │
│   ─────────────────────────────────                             │
│                                                                 │
│   purpose_confidence = f(                                       │
│     has_docstring,         # Intent declared                   │
│     role_match,            # Role matches purpose              │
│     parent_coherence,      # Parent is coherent                │
│     child_alignment        # Children align with us            │
│   )                                                             │
│                                                                 │
│   Final coherence = avg(purpose_confidence) across all nodes   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 New Fields in unified_analysis.json

```json
{
  "name": "SemgrepMiner",
  "pi2_purpose": "Initiate",
  "semantic_role": "orchestrator",

  // NEW: Purpose Flow Fields
  "purpose_flow": {
    "composite_purpose": "DataProcessor",
    "purpose_from_parent": null,
    "allowed_child_purposes": ["Extract", "Transform", "Emit"],
    "coherence_score": 0.85,
    "purpose_entropy": 0.42,
    "emergence_detected": true,
    "purpose_confidence": 0.78,
    "violations": []
  },

  // Children now include constraint info
  "children": [
    {
      "name": "SemgrepMiner.__init__",
      "pi2_purpose": "Initiate",
      "purpose_from_parent": "Initiate",
      "purpose_aligned": true
    },
    {
      "name": "SemgrepMiner.mine",
      "pi2_purpose": "Emit",
      "purpose_from_parent": "Extract",
      "purpose_aligned": false,
      "alignment_issue": "Emit not in allowed set"
    }
  ]
}
```

### 5.3 Implementation Changes

| File | Change |
|------|--------|
| `purpose_field.py` | Export coherence_score, entropy to node dict |
| `purpose_field.py` | Add top-down constraint propagation |
| `purpose_field.py` | Add CONSTRAINT_RULES dictionary |
| `purpose_intelligence.py` | Compute purpose_confidence |
| `full_analysis.py` | Wire purpose_flow into node output |
| `graph_framework.py` | semantic_role consults parent context |
| POM | Read purpose_flow for coherence metric |

---

## 6. MATHEMATICAL FORMALIZATION

### 6.1 Purpose Vector Space

```
Let 𝒫 = ℝᵏ where k = |PurposeCategories|

Purpose categories (k=12):
  {Query, Command, Persist, Transform, Validate,
   Produce, Consume, Route, Handle, Initiate,
   Compute, Orchestrate}

Each node n has purpose vector:
  𝒫(n) ∈ ℝ¹² with ‖𝒫(n)‖₁ = 1 (probability distribution)
```

### 6.2 Aggregation Function

```
𝒫(parent) = normalize(Σᵢ wᵢ × 𝒫(childᵢ))

WHERE:
  wᵢ = complexity(childᵢ) / Σⱼ complexity(childⱼ)
  complexity = lines_of_code × cyclomatic_complexity
```

### 6.3 Constraint Function

```
allowed_purposes(parent) → Set[Purpose]

Given parent.purpose, return valid child purposes.

CONSTRAINT_MATRIX C ∈ {0,1}^(k×k):
  C[i,j] = 1 iff purpose j is valid child of purpose i

𝒫(child) must satisfy:
  𝒫(child) · C[parent.purpose] > 0
```

### 6.4 Coherence Metric

```
coherence(parent) = 1 - H(children) / H_max

WHERE:
  H(children) = -Σᵢ p(purposeᵢ) × log₂(p(purposeᵢ))
  H_max = log₂(k)  # Maximum entropy for k categories
  p(purposeᵢ) = count(children with purposeᵢ) / |children|
```

### 6.5 Emergence Condition

```
emergence(parent) = true IFF:
  ‖𝒫(parent)‖ > α × Σᵢ ‖𝒫(childᵢ)‖

WHERE α = 1.2 (emergence threshold, configurable)
```

### 6.6 Confidence Computation

```
confidence(n) = w₁×has_intent + w₂×role_match + w₃×parent_coherent + w₄×children_aligned

WHERE:
  has_intent = 1 if docstring exists else 0.5
  role_match = 1 if role ∈ purpose_category else 0
  parent_coherent = parent.coherence_score if parent else 1.0
  children_aligned = Σ aligned_children / |children| if children else 1.0

Weights: w₁=0.2, w₂=0.3, w₃=0.25, w₄=0.25
```

---

## 7. CHANNEL VERIFICATION

### 7.1 Channel Continuity Check

```
CHANNEL_CONTINUOUS(L_bottom, L_top) = true IFF:
  ∀ level L in [L_bottom, L_top]:
    ∃ node n at level L with:
      purpose_confidence(n) > 0 AND
      (parent.purpose → n.purpose edge exists) AND
      (n.purpose → child.purpose edge exists for some child)
```

### 7.2 Flow Resistance

```
R(channel) = Σ (1 - coherence(level)) for each level

Low R = smooth purpose flow (healthy)
High R = blocked purpose flow (incoherent)
```

### 7.3 Health Index Integration

```
H_purpose = 1 / (1 + R)

Add to Constructal Health:
  H_total = w₁×H_flow + w₂×H_symmetry + w₃×H_purpose
```

---

## 8. VALIDATION CRITERIA

### 8.1 Success Metrics

| Metric | Current | Target | Meaning |
|--------|---------|--------|---------|
| Coverage | 92.5% | 95%+ | Nodes with purpose |
| Coherence | 0.0 | 0.7+ | Purpose alignment |
| Emergence | Unknown | Measured | Layers detected |
| Violations | Unknown | <5% | Misaligned children |

### 8.2 Test Cases

1. **Repository pattern:** All children should be Query/Persist
2. **Service pattern:** All children should be Command/Query
3. **God class detection:** coherence < 0.5 with 5+ children
4. **Emergence detection:** Module purpose > sum of function purposes

---

## 9. IMPLEMENTATION ROADMAP

### Phase 1: Export Existing Metrics
- Export coherence_score from purpose_field.py
- Export entropy from purpose_field.py
- Add to unified_analysis.json

### Phase 2: Bottom-Up Aggregation
- Implement composite_purpose calculation
- Wire EMERGENCE_RULES into output
- Detect emergence events

### Phase 3: Top-Down Constraints
- Define CONSTRAINT_RULES matrix
- Propagate allowed_purposes down hierarchy
- Detect MISPLACED_CHILD violations

### Phase 4: Confidence Scoring
- Implement purpose_confidence formula
- Update POM to read confidence
- Verify coherence > 0

### Phase 5: Channel Verification
- Implement continuity check
- Compute flow resistance
- Add to health index

---

## 10. REFERENCES

### Internal

- `CODESPACE_ALGEBRA.md` §10 - Purpose Field formalization
- `THEORY_AXIOMS.md` Axiom Group D - Purpose axioms
- `THEORY_AXIOMS.md` Axiom Group E - Constructal Law
- `purpose_field.py` - Existing implementation
- `purpose_intelligence.py` - Q-score aggregation

### External

- Friston, K. - Free Energy Principle (purpose as gradient descent)
- Bejan, A. - Constructal Law (flow optimization)
- Category Theory - Functors as purpose-preserving maps

---

## CHANGELOG

| Date | Change |
|------|--------|
| 2026-01-26 | Initial specification based on gap analysis |

---

*"Purpose is not what you have. Purpose is what flows through you."*
