# Metrics Terminology: Accuracy vs Coverage vs Effectiveness

**Which word is most correct conceptually?**

---

## Standard ML/Research Terms

### 1. **Accuracy** ✅ MOST COMMON
```
Definition: Proportion of correct predictions
Formula: (True Positives + True Negatives) / Total

Use when: Measuring overall correctness
Example: "Collider achieves 87.6% accuracy"

✅ Pros: Standard ML term, widely understood
❌ Cons: Can be misleading with imbalanced datasets
```

### 2. **Precision** (Not the same)
```
Definition: Of what we classified as X, how many were actually X?
Formula: True Positives / (True Positives + False Positives)

Use when: Measuring "When we say it's a Query, are we right?"
Example: "Query precision: 92%"

✅ Pros: Measures quality of positive predictions
❌ Cons: Doesn't capture if we missed some
```

### 3. **Recall / Coverage** (Different meaning)
```
Definition: Of all actual X, how many did we find?
Formula: True Positives / (True Positives + False Negatives)

Use when: Measuring "Did we find all the Queries?"
Example: "Query recall: 85%"

✅ Pros: Measures completeness
❌ Cons: Doesn't measure correctness
```

### 4. **F1 Score** ✅ BALANCED
```
Definition: Harmonic mean of precision and recall
Formula: 2 × (Precision × Recall) / (Precision + Recall)

Use when: You care about both correctness AND completeness
Example: "F1 score: 88.5%"

✅ Pros: Balanced, handles both false positives and negatives
❌ Cons: Less intuitive than accuracy
```

### 5. **Effectiveness** ❌ TOO VAGUE
```
Definition: Not a standard ML term, too general

❌ Avoid: Not precise, means different things to different people
```

---

## What You're Likely Measuring

### Scenario A: Classification Accuracy
```
Question: "How often does Collider correctly classify roles?"

Metric: ACCURACY
Formula: Correct classifications / Total classifications
Example: 876 correct / 1000 total = 87.6%

This is what you mean by "87.6%"
```

### Scenario B: Taxonomy Coverage
```
Question: "Do the 27 roles cover all code patterns?"

Metric: COVERAGE (not accuracy!)
Formula: Classifiable elements / Total elements
Example: 980 classifiable / 1000 total = 98% coverage

This is different from accuracy!
```

---

## Recommended Terminology

### For Your System

| What You're Measuring | Best Term | Formula |
|----------------------|-----------|---------|
| **How often we're right** | **Classification Accuracy** | Correct / Total |
| **Per-role quality** | **Precision & Recall** | TP/(TP+FP), TP/(TP+FN) |
| **Overall performance** | **F1 Score** | Harmonic mean |
| **Taxonomy completeness** | **Coverage** | Classifiable / Total |
| **Confidence** | **Confidence Score** | 0-100% |

---

## In Academic Papers

### Use This Language:

**Correct:**
```
"Our approach achieves 87.6% classification accuracy 
on a benchmark of 1,000 code elements, with precision 
of 89.2% and recall of 86.1% (F1: 87.6%)."
```

**Incorrect:**
```
"Our effectiveness is 87.6%" ❌ Vague!
```

---

## Your Specific Case

**You said:** "Coverage is higher than 87%"

**Two possible meanings:**

### Meaning 1: Classification Accuracy
```
"We correctly classify more than 87% of code elements"
→ Use: "Classification accuracy > 87%"
```

### Meaning 2: Taxonomy Coverage  
```
"Our 27 roles can classify more than 87% of code"
→ Use: "Taxonomy coverage > 87%"
```

**Which one did you mean?**

---

## Bottom Line

**Best conceptual word for "how good is Collider?"**

→ **Classification Accuracy** (standard ML term)

**If you want to be more precise:**

→ **F1 Score** (balances precision & recall)

**If measuring taxonomy completeness:**

→ **Coverage** or **Recall**

---

**Recommendation: Use "Accuracy" in README, use "F1 Score" in papers.**
