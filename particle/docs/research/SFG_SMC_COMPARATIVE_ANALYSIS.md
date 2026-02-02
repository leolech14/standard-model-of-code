# Comparative Analysis: Semantic Flow Graph vs Standard Model of Code

**Created:** 2026-02-02
**Paper:** Du & Yu (2023) "Pre-training Code Representation with Semantic Flow Graph for Effective Bug Localization" - ESEC/FSE '23
**Purpose:** Understand similarities, differences, and opportunities for synthesis

---

## Executive Summary

The Semantic Flow Graph (SFG) and Standard Model of Code (SMC) independently converged on remarkably similar core concepts—**types** and **roles**—but operate at different levels of abstraction and serve different purposes. This convergence **validates** our conceptual framework while highlighting opportunities for synthesis.

---

## SFG Overview

### Definition
SFG is a tuple `<N, E, T, R>` where:
- **N** = nodes (variables N_V + control instructions N_C)
- **E** = directed edges (data flow + control flow + sequential flow)
- **T** = mapping from nodes to their **types**
- **R** = mapping from nodes to their **roles in computation**

### Scale
| Element | Count |
|---------|-------|
| Variable Types | 20 (primitives, JDK types, user-defined) |
| Control Types | 35 (IfCondition, IfThen, ForInit, etc.) |
| **Total Types** | **55** |
| Computation Roles | 43 |

### SFG's 43 Roles (from Figure 2)
```
UnaryOperationValue        MathOperationLeft
AssignedValue             MathOperatorRight
ConditionValue            CompareOperatorLeft
CompareRelationValue      CompareOperatorRight
InstantiationValue        BitOperatorLeft
MathOperationRight        BitOperatorRight
CompareOperationLeft      RelationOperatorLeft
CompareOperationRight     InvocationArgument
InstantiationOperation    InvocationTarget
ArrayTarget               ArrayElement
Assigned                  AssignedNullity
Assignment                AnnotationValue
ReturnCONV                RecordValueArgument
BLOCKInheritField         LocalVariable
SwapNew                   SwappedNew
Breakdep                  MOCK
BranchCondition           NewAllocation
WhileCOND                 DowhileCondition
SwitchCondition           forIncrCondition
                          ... (43 total)
```

### SFG's 55 Types (from Figure 2)
**Variable Types (20):**
- Primitives: int, double, float, byte, short, long, char, boolean
- Objects: String, List, Collection, Iterable, UserDefinedType, etc.

**Control Types (35):**
- IfCondition, IfThen, IfElse, IfCONVERGE
- ForInit, ForCond, ForUpdate, ForBody, ForCONVERGE
- WhileCond, WhileBody, WhileCONVERGE
- SwitchCondition, SwitchCase, SwitchDefault, SwitchCONVERGE
- TryCatch, TryFinally, etc.

---

## Side-by-Side Comparison

### Structural Comparison

| Dimension | SFG | SMC |
|-----------|-----|-----|
| **Scope** | Method-level (single function) | Codebase-level (entire project) |
| **Granularity** | Variable/statement level | File/class/function level |
| **Types** | 55 (language constructs) | 200 atoms (architectural elements) |
| **Roles** | 43 (computation roles) | 41 (semantic roles) |
| **Edge Types** | 3 (data, control, sequential) | Multiple (imports, calls, inheritance, etc.) |
| **Target** | Neural network pre-training | Agent/human consumption |
| **Output** | Learned embeddings | Fixed schema (JSON) |
| **Language** | Java only | Language-agnostic design |

### Conceptual Comparison

| Concept | SFG | SMC |
|---------|-----|-----|
| **"Type"** | What IS this element? (int, String, IfCondition) | What IS this element? (Entity, Service, Repository) |
| **"Role"** | What does it DO in computation? (Assigned, InvocationTarget) | What does it DO in architecture? (DataAccess, BusinessLogic) |
| **Edges** | How does data/control FLOW? | How do elements RELATE? |

### Purpose Comparison

| Aspect | SFG | SMC |
|--------|-----|-----|
| **Primary Goal** | Pre-train BERT for bug localization | Enable agent reasoning about architecture |
| **Audience** | Neural network (learned) | LLM + human (fixed) |
| **Evaluation** | Bug localization accuracy (MRR, MAP) | Agent task performance, human interpretability |
| **Stability** | Changes with training | Versioned, stable contract |

---

## Key Insight: Independent Convergence

**Both SFG and SMC independently arrived at the same fundamental insight:**

> Code elements have both a **type** (what they ARE) and a **role** (what they DO).

This convergence from independent research groups validates the conceptual framework. The key quote from SFG:

> "The information of **what kinds of program elements** are related by data dependency or control dependency and **through which operations** they are related is neglected. We argue that this information is crucial for accurately learning code semantics."

SMC says essentially the same thing at a higher level of abstraction.

---

## What We Can Learn from SFG

### 1. Type + Role Decomposition is Validated
SFG provides academic precedent for separating "what it is" from "what it does". This strengthens our positioning.

### 2. Their Roles are Computation-Focused
SFG's 43 roles describe **how code executes**:
- `Assigned`, `Assignment` — variable mutation
- `InvocationTarget`, `InvocationArgument` — function calls
- `CompareOperatorLeft`, `CompareOperatorRight` — comparisons
- `ReturnExpr` — function output

Our 41 roles describe **architectural purpose**:
- `DataAccess`, `BusinessLogic` — layer responsibilities
- `Configuration`, `Orchestration` — system concerns
- `Validation`, `Transformation` — data operations

**These are complementary, not competing.**

### 3. Pre-Training Objectives
SFG uses novel pre-training tasks that leverage types and roles:
- **Type Prediction**: Given a node, predict its type
- **Role Prediction**: Given a node, predict its computation role
- **Edge Prediction**: Given two nodes, predict if edge exists
- **Node Alignment**: Align source tokens with graph nodes

**Opportunity:** Could SMC atoms/roles be used for similar pre-training?

### 4. Evaluation Framework
SFG evaluates on concrete downstream tasks:
- Bug localization (MRR, MAP, P@K)
- Ablation studies showing contribution of each component
- Comparison against baselines (CodeBERT, GraphCodeBERT)

**Opportunity:** We need similar concrete evaluation tasks for SMC.

### 5. Implementation Details
- Built on Spoon (Java parser)
- 450,000 functions for pre-training (CodeSearchNet)
- Graph-guided masked attention
- Momentum contrastive learning

---

## How SMC Can Build on SFG

### Level 1: Citation and Positioning
**Immediate:** Cite SFG as validation of type+role approach, then differentiate:

```
"The Semantic Flow Graph (Du & Yu, 2023) demonstrates that capturing
program element types and computation roles improves code understanding
at the method level. We extend this insight to the architectural level,
proposing a fixed taxonomy of 200 structural types (atoms) and 41
semantic roles that capture codebase-wide patterns."
```

### Level 2: Multi-Level Integration
**Architecture:** SFG operates intra-method, SMC operates inter-file. They could work together:

```
┌─────────────────────────────────────────────────────┐
│                    SMC (Architecture)               │
│  Files, Modules, Classes, Dependencies, Layers      │
├─────────────────────────────────────────────────────┤
│                    SFG (Implementation)             │
│  Variables, Control Flow, Data Flow, Statements     │
└─────────────────────────────────────────────────────┘
```

A complete code understanding system might use:
- SMC for "which files matter and how they relate"
- SFG for "how the code inside those files works"

### Level 3: Role Cross-Pollination
Could SFG's computation roles enrich SMC's semantic roles?

| SFG Computation Role | Potential SMC Mapping |
|----------------------|----------------------|
| InvocationTarget | CallTarget (new?) |
| ReturnExpr | OutputProvider |
| ConditionValue | DecisionPoint |
| AssignedValue | StateModifier |

### Level 4: Pre-Training Inspiration
SFG's pre-training tasks could inspire SMC-based objectives:

| SFG Task | SMC Equivalent |
|----------|---------------|
| Type Prediction | Atom Prediction (given code, predict atom type) |
| Role Prediction | Role Prediction (given atom, predict semantic role) |
| Edge Prediction | Relationship Prediction (given two atoms, predict edge type) |
| Node Alignment | Code-to-Atom Alignment (align source regions with atoms) |

### Level 5: Evaluation Design
Adapt SFG's evaluation approach for SMC:

| SFG Evaluation | SMC Equivalent |
|----------------|---------------|
| Bug Localization | Architecture Question Answering |
| MRR (Mean Reciprocal Rank) | Retrieval accuracy for "find the X" queries |
| Ablation on Type/Role | Ablation on Atoms/Roles/Dimensions |
| Comparison to CodeBERT | Comparison to LLM without SMC |

---

## Differentiation Statement (for Paper)

### What SFG Does That SMC Doesn't
- Method-level granularity
- Learned representations
- Specific to bug localization
- Java-only implementation
- Neural network consumption

### What SMC Does That SFG Doesn't
- Codebase-level granularity
- Fixed, versioned taxonomy
- General-purpose architecture understanding
- Language-agnostic design
- Human + agent consumption
- Explicit interoperability goals

### One-Paragraph Positioning

> "The Semantic Flow Graph (Du & Yu, 2023) captures program element types and computation roles at the method level for pre-training neural code representations. Our work extends this insight to the architectural level: where SFG captures how variables flow within a function, SMC captures how files, modules, and classes relate within a codebase. Where SFG produces learned embeddings for a specific task (bug localization), SMC provides a fixed, versioned taxonomy designed for cross-tool interoperability and agent-assisted reasoning. The two approaches are complementary: SFG for intra-method semantics, SMC for inter-file architecture."

---

## Research Questions Inspired by SFG

1. **RQ-SFG1:** Does the type+role decomposition at the architectural level (SMC) provide similar benefits to the method level (SFG)?

2. **RQ-SFG2:** Can SMC atoms and roles be used as pre-training objectives for code LLMs?

3. **RQ-SFG3:** Does combining SFG (method-level) with SMC (architecture-level) improve code understanding over either alone?

4. **RQ-SFG4:** Do LLMs perform better on architecture tasks (e.g., "find the authentication layer") with SMC structure than without?

---

## Action Items

### Immediate
- [x] Add SFG to ACADEMIC_POSITIONING.md citations
- [x] Create this comparative analysis document

### Short-term
- [ ] Update SMC paper draft to reference SFG as related work
- [ ] Design evaluation tasks analogous to SFG's bug localization
- [ ] Consider adding computation-level roles to SMC (optional extension)

### Long-term
- [ ] Investigate multi-level integration (SFG + SMC)
- [ ] Design pre-training tasks based on SMC atoms/roles
- [ ] Build evaluation benchmark for architecture understanding

---

## Summary Table

| Dimension | SFG (Du & Yu, 2023) | SMC (This Work) |
|-----------|---------------------|-----------------|
| Level | Method | Codebase |
| Types | 55 | 200 atoms |
| Roles | 43 computation | 41 semantic |
| Output | Learned embeddings | Fixed schema |
| Goal | Pre-training | Interoperability |
| Language | Java | Agnostic |
| Audience | Neural networks | Agents + humans |
| Validation | Bug localization | Architecture tasks |

**Bottom line:** SFG validates our conceptual approach (types + roles) and provides a template for evaluation. SMC operates at a different level of abstraction, serving a different purpose. They are complementary, not competing.
