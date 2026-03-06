---
id: INFORMATION_THEORY
title: "Information Theory: Entropy and Coherence on Purpose Space"
layer: L2 (Dynamics)
prerequisites:
  - PURPOSE_SPACE
exports:
  - shannon_entropy
  - purpose_coherence
  - mutual_information
  - purpose_leakage
  - transfer_entropy
status: IMPLEMENTED
implementation:
  file: src/core/purpose_field.py
  lines: "358-375"
  coverage: "Shannon entropy, coherence = 1-H/H_max, god class detection (coherence < 0.4 AND children >= 8 AND unique >= 4)"
glossary_terms:
  - mutual_information
  - transfer_entropy
  - purpose_leakage
---

# Information Theory: Entropy and Coherence on Purpose Space

> **Navigation:** [INDEX](../INDEX.md) | [PURPOSE_SPACE](./PURPOSE_SPACE.md) > **INFORMATION_THEORY**
> **Depends on:** [PURPOSE_SPACE.md](./PURPOSE_SPACE.md) SS5 (Measure-Theoretic Structure)

---

## Abstract

Information theory provides the **quantitative dynamics** of Purpose Space M. Where graph theory measures structure and order theory classifies, information theory measures **disorder, coherence, and information flow** across purpose boundaries.

The central metric is **Shannon entropy** H = -sum p_i log_2(p_i), applied to the distribution of child purposes within a parent atom. Low entropy means focused purpose (coherent); high entropy means scattered purpose (incoherent / god class). This is extended to **mutual information** I(X;Y) for measuring purpose leakage across architectural boundaries and **transfer entropy** for detecting causal purpose influence.

**Implementation status:** Core entropy and coherence are fully implemented (`purpose_field.py:358-375`). God class detection uses coherence < 0.4. Mutual information and transfer entropy are theoretical extensions (not yet implemented).

---

## SS1. Shannon Entropy for Purpose Distribution

### 1.1 Purpose Distribution

For a parent atom v with children {c_1, ..., c_n}, the **purpose distribution** is:

```
p_i = count(children with purpose i) / n
where i ranges over distinct purposes among v's children
```

Example: A class with 3 Query methods, 2 Command methods, and 1 Factory method has:

```
p_Query   = 3/6 = 0.5
p_Command = 2/6 = 0.333
p_Factory = 1/6 = 0.167
```

### 1.2 Shannon Entropy

The **Shannon entropy** of this distribution measures purpose disorder:

```
H(v) = -sum_{i} p_i * log_2(p_i)
```

For the example above:

```
H = -(0.5 * log_2(0.5) + 0.333 * log_2(0.333) + 0.167 * log_2(0.167))
  = -(0.5 * (-1) + 0.333 * (-1.585) + 0.167 * (-2.585))
  = -(- 0.5 - 0.528 - 0.431)
  = 1.459 bits
```

**Implementation:** `purpose_field.py:358-365`

```python
entropy = 0.0
for count in purpose_counts.values():
    if count > 0:
        p = count / total
        entropy -= p * math.log2(p)
```

### 1.3 Maximum Entropy

For k distinct purposes, maximum entropy occurs when all purposes are equally represented:

```
H_max = log_2(k)
```

For k=3: H_max = log_2(3) = 1.585 bits. The example's H = 1.459 is close to maximum — nearly uniform disorder.

---

## SS2. Coherence Score

### 2.1 Definition

**Coherence** normalizes entropy to a [0, 1] scale where 1 = perfectly focused and 0 = maximally disordered:

```
coherence(v) = 1 - H(v) / H_max
where H_max = log_2(k), k = number of distinct purposes
```

**Implementation:** `purpose_field.py:367-370`

```python
max_entropy = math.log2(unique) if unique > 1 else 1
node.coherence_score = round(1 - (entropy / max_entropy) if max_entropy > 0 else 1, 3)
```

### 2.2 Interpretation Scale

| Coherence | Interpretation | Architectural Signal |
|---|---|---|
| 1.0 | Single purpose | Pure responsibility (ideal) |
| 0.8 - 1.0 | Dominant purpose | Minor supporting concerns (acceptable) |
| 0.5 - 0.8 | Mixed purposes | Growing complexity (warning) |
| 0.3 - 0.5 | Weak coherence | Approaching god class (refactor candidate) |
| 0.0 - 0.3 | No coherence | True god class (urgent refactor) |

### 2.3 God Class Detection

A god class is detected when three conditions simultaneously hold:

```
god_class(v) iff:
  coherence(v) < 0.4       AND    (low coherence)
  |children(v)| >= 8       AND    (many children)
  |unique_purposes(v)| >= 4        (many distinct purposes)
```

**Implementation:** `purpose_field.py:372-375`

```python
if node.coherence_score < 0.4 and total >= 8 and unique >= 4:
    node.is_god_class = True
```

**Connection to matroid theory:** The threshold `unique >= 4` corresponds to exceeding the matroid rank bound (see [MATROID_THEORY.md](./MATROID_THEORY.md) SS2). A class serving 4+ distinct purposes exceeds the independence threshold — no subset of its responsibilities forms a coherent independent set.

---

## SS3. Mutual Information (Purpose Leakage)

### 3.1 Definition

**Mutual information** between two purpose distributions measures how much knowing one component's purpose tells you about another's:

```
I(P_A; P_B) = H(P_A) + H(P_B) - H(P_A, P_B)
            = sum_{a,b} p(a,b) * log_2(p(a,b) / (p(a) * p(b)))
where:
  P_A = purpose distribution of component A
  P_B = purpose distribution of component B
  p(a,b) = joint probability of purpose a in A and purpose b in B
```

### 3.2 Purpose Leakage

**Purpose leakage** is high mutual information between components that should be independent:

```
leakage(A, B) = I(P_A; P_B)   when A and B are in DIFFERENT architectural layers
```

If two components in different layers share mutual information about their purposes, purpose is "leaking" across the boundary. This violates separation of concerns.

**Example:** If a presentation-layer controller's purpose distribution is highly correlated with an infrastructure-layer repository's distribution, the controller likely contains business logic that should be in the domain layer.

### 3.3 Conditional Entropy

**Conditional entropy** H(Purpose|Layer) measures remaining uncertainty about purpose after knowing the layer:

```
H(Purpose|Layer) = sum_l p(l) * H(Purpose|Layer=l)
                 = H(Purpose, Layer) - H(Layer)
```

**Low conditional entropy** means layer strongly determines purpose (good architecture). **High conditional entropy** means knowing the layer doesn't tell you much about purpose (poor separation of concerns).

This connects to [L0_AXIOMS.md](../foundations/L0_AXIOMS.md) Axiom F2: "Purpose emerges from relationships through mutual information."

**Implementation status:** THEORETICAL. Not yet implemented. Requires computing joint purpose distributions across layer boundaries, which the current pipeline does not perform.

---

## SS4. Transfer Entropy (Causal Purpose Influence)

### 4.1 Definition

**Transfer entropy** from process X to process Y measures the directed information flow:

```
T_{X->Y} = sum p(y_{t+1}, y_t, x_t) * log_2(p(y_{t+1}|y_t, x_t) / p(y_{t+1}|y_t))
```

### 4.2 Application to Purpose Evolution

In the context of codebase evolution (git history), transfer entropy measures how changes in one component's purpose causally influence another's:

```
T_{A->B} = information gained about B's next purpose state
           by knowing A's current purpose state,
           beyond what B's own history provides
```

**High transfer entropy** T_{A->B} means A's purpose changes drive B's purpose changes — indicating tight coupling that may violate architectural boundaries.

**Implementation status:** THEORETICAL. Requires temporal purpose data (purpose vectors at multiple git commits), which is future work.

---

## SS5. Information-Theoretic View of Architecture

### 5.1 Shannon's M-I-P-O Model

[L2_PRINCIPLES.md](../foundations/L2_PRINCIPLES.md) SS6 applies Shannon's communication model to software architecture:

```
Message (intent) -> Input (code) -> Processing (compilation/runtime) -> Output (behavior)
```

Each stage adds noise and loses information. The purpose field captures the **channel capacity** of code to transmit architectural intent: high coherence = low noise = high fidelity transmission of design intent.

### 5.2 Architecture as Information Channel

The entire codebase can be modeled as an information channel:

```
Source: Developer's architectural intent (purpose assignments)
Channel: Code structure (imports, patterns, naming)
Receiver: Downstream developer understanding the architecture

Channel capacity C = max I(Intent; Understanding)
```

Good architecture maximizes this channel capacity by making purpose **readable from structure** (Axiom A2). Information theory quantifies how much of the original architectural intent survives in the code structure.

---

## SS6. Connections to Other Frameworks

| Framework | Connection |
|---|---|
| [PURPOSE_SPACE](./PURPOSE_SPACE.md) | Entropy provides the measure mu on M = (S, d, **mu**, tau, A) |
| [GRAPH_THEORY](./GRAPH_THEORY.md) | High modularity Q correlates with low cross-community entropy |
| [ORDER_THEORY](./ORDER_THEORY.md) | Entropy measures disorder within a concept's extent |
| [CATEGORY_THEORY](./CATEGORY_THEORY.md) | Mutual information is a natural transformation between entropy functors |
| [TOPOLOGY](./TOPOLOGY.md) | Entropy gradient reveals boundaries between purpose zones |
| [MATROID_THEORY](./MATROID_THEORY.md) | God class threshold = matroid rank bound violation |

---

## Appendix A: Entropy Properties

Shannon entropy satisfies four key axioms:

1. **Non-negativity:** H(X) >= 0
2. **Maximum at uniformity:** H(X) <= log_2(|X|), equality iff uniform distribution
3. **Additivity:** H(X, Y) = H(X) + H(Y) if X, Y independent
4. **Chain rule:** H(X, Y) = H(X) + H(Y|X)

These properties ensure coherence is well-defined and comparable across atoms with different numbers of children.

## Appendix B: Citations

- Shannon, C. E. (1948). "A mathematical theory of communication." Bell System Technical Journal 27: 379-423, 623-656.
- PMC (2023). "Entropy as a Measure of Consistency in Software Architecture." Entropy 25(2): 313.
- ACM ICSM (2001). "Entropies as Measures of Software Information." International Conference on Software Maintenance.
- Allen, E. B. & Khoshgoftaar, T. M. (1999). "Measuring coupling and cohesion: An information-entropy approach." Proc. METRICS'99.
- Schreiber, T. (2000). "Measuring information transfer." Physical Review Letters 85(2): 461.

---

*This document defines information-theoretic tools on Purpose Space. For the space itself, see [PURPOSE_SPACE.md](./PURPOSE_SPACE.md). For categorical abstraction, see [CATEGORY_THEORY.md](./CATEGORY_THEORY.md). For topological structure, see [TOPOLOGY.md](./TOPOLOGY.md).*
