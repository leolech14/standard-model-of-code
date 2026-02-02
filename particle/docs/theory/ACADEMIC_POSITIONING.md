# Academic Positioning: Standard Model of Code

**Created:** 2026-02-02
**Status:** AUTHORITATIVE
**Purpose:** Guide for framing SMC in academic contexts

---

## Core Philosophy

### What We Are NOT Doing
- Claiming scientific discovery
- Competing with existing research
- Proving universal truths about software
- Seeking validation or attention

### What We ARE Doing
- Proposing a reference model
- Joining an academic conversation
- Building a tool that works
- Contributing a standardized vocabulary

---

## The Reframe

| Wrong Framing | Right Framing |
|---------------|---------------|
| "We discovered laws of software" | "We propose a reference model" |
| "SMC is better than X" | "SMC builds on X, extending it with Y" |
| "We invented code representation" | "We contribute a standardized vocabulary" |
| "Our approach is novel" | "Our contribution is a fixed taxonomy for AI agents" |
| "We prove..." | "We show evidence that..." |

---

## Unique Position

### What Prior Work Does
- **Learned representations** — ASTNN, SemanticFlowGraph, CodeBERT
- **Task-specific models** — Defect prediction, clone detection
- **Dynamic embeddings** — Change per training run
- **Black-box neural networks** — Not human-interpretable

### What SMC Does
- **Fixed taxonomy** — 200 atoms, 41 roles, 8 dimensions
- **Human-readable AND machine-actionable** — Dual audience
- **Versioned schema** — Stable contract for interoperability
- **AI-first design** — Built for LLM consumption
- **Transparent structure** — Every classification is explainable

---

## One-Sentence Positioning

> "We contribute not a new model, but a new *language*—a standardized vocabulary that enables diverse AI systems to reason about code architecture using shared concepts."

---

## The Periodic Table Analogy

**The periodic table doesn't explain chemistry. It organizes elements so chemists can communicate.**

Similarly:

**SMC doesn't explain why code works. It organizes code structure so AI agents can reason.**

| Periodic Table | Standard Model of Code |
|----------------|------------------------|
| 118 elements | 200 atoms |
| Groups & periods | Roles & dimensions |
| Atomic properties | LOCUS coordinates |
| Enables chemistry communication | Enables AI-code reasoning |

---

## How to Use Prior Work

### In Introduction
```
"Prior work has shown that structured code representations
improve program understanding (Zhang et al., 2019; Du et al., 2023).
We build on these foundations by proposing a fixed reference taxonomy..."
```

### In Related Work
```
"The Semantic Flow Graph (Du et al., 2023) captures program element
types and their computational roles. Our work differs in providing
a *fixed* taxonomy rather than learned representations, enabling
cross-system interoperability..."
```

### In Contribution Statement
```
"Where prior work learns representations from data, we propose a
standardized reference model. Our contribution is not a better
neural network, but a lingua franca for code structure."
```

---

## Claim Structure

| Layer | What We Say | What We DON'T Say |
|-------|-------------|-------------------|
| **Definitions** | "We define 200 atom types, 41 roles, 8 dimensions" | "These ARE the true categories" |
| **Implementation** | "We built Collider, which extracts this structure" | "Collider is complete/perfect" |
| **Evidence** | "On N codebases, this representation enabled X" | "This proves the model is correct" |
| **Invitation** | "We invite investigation of these patterns" | "We have discovered universal laws" |

---

## Language Guidelines

### Vocabulary to AVOID
- "Law" → Use "principle" or "pattern"
- "Proof" → Use "evidence" or "demonstration"
- "Discovery" → Use "proposal" or "contribution"
- "Truth" → Use "utility" or "usefulness"
- "Ontology" → Use "taxonomy" or "classification"
- "The code obeys..." → Use "We represent code as..."

### Vocabulary to USE
- "We propose..."
- "We define..."
- "We show evidence that..."
- "This model suggests..."
- "We invite investigation..."
- "Building on prior work..."

---

## The Real Test

**Pragmatic truth:** Does the tool work? Can AI use these constructs to reason better about code?

- If yes → The model is useful
- If no → We adjust

We seek utility, not universal truth.

---

## Target Audience

### Primary: AI Agents
- LLMs reasoning about code
- Automated refactoring tools
- Code search and retrieval systems
- Documentation generators

### Secondary: Human Developers
- Architecture visualization
- Codebase onboarding
- Technical debt assessment
- Code review assistance

**Key insight:** SMC is designed for AI to use *on behalf of* humans.

---

## Suggested Paper Structure

```
1. INTRODUCTION
   - AI agents need structured code understanding
   - Text-based analysis is insufficient
   - We propose a reference model

2. BACKGROUND & RELATED WORK
   - Code representation approaches (cite generously)
   - Quality models (ISO 25010)
   - Knowledge graphs for code

3. THE STANDARD MODEL OF CODE
   - Design goals (human + machine readable)
   - Atoms (200 structural types)
   - Roles (41 semantic categories)
   - Dimensions (8 orthogonal properties)
   - LOCUS coordinates

4. IMPLEMENTATION: COLLIDER
   - Architecture
   - Extraction pipeline
   - Output schema

5. EVALUATION
   - RQ1: Can AI use this for code tasks?
   - RQ2: Does structure improve over text?
   - RQ3: Consistency across codebases?

6. DISCUSSION & LIMITATIONS
   - What the model doesn't capture
   - Boundary cases
   - Future work

7. CONCLUSION
   - Summary of contribution
   - Invitation to extend
```

---

## Key Papers to Cite

### Code Representation (Related Work)
- Zhang et al., 2019 — ASTNN (AST-based neural representation)
- Du et al., 2023 — Semantic Flow Graph (program element roles)
- Feng et al., 2020 — CodeBERT (pre-trained code model)

### Foundations (Background)
- Vaswani et al., 2017 — Attention Is All You Need
- Devlin et al., 2018 — BERT

### Taxonomies (Methodology)
- Usman et al., 2017 — Taxonomies in Software Engineering
- Huang et al., 2020 — CPC (code entity classification)

### Quality Models (Context)
- ISO/IEC 25010 — Software quality model

---

## The Motivation (Personal Context)

This project exists because:

1. **Practical need** — Building apps requires understanding code
2. **AI augmentation** — LLMs need structured input to reason well
3. **Tool-first** — The goal is a working tool, not academic glory
4. **Open contribution** — Publishing invites collaboration and validation

The academic paper is not about ego. It's about:
- Formalizing ideas rigorously
- Inviting scrutiny and improvement
- Contributing to the field
- Building credibility for the tool

---

## Summary

**Don't compete. Contribute.**

Stand on the shoulders of giants. Cite generously. Carve out your specific contribution:

> A fixed, versioned, human-readable, machine-actionable taxonomy of code structure—designed for AI agents to reason about architecture.

Not better than prior work. *Different* from prior work. And useful.
