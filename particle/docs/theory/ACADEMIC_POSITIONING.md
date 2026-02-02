# Academic Positioning: Standard Model of Code

**Created:** 2026-02-02
**Revised:** 2026-02-02 (v2 - incorporating peer review)
**Status:** Internal Positioning Guide
**Purpose:** Claim discipline + framing consistency for academic writing

---

## Core Philosophy

### What We Are NOT Doing
- Claiming universal laws of software
- Claiming superiority over all prior work
- Claiming completeness of program understanding
- Claiming that our categories are "the true ontology"
- Seeking prestige; we seek **scrutiny and reproducible utility**

### What We ARE Doing
- Proposing a reference model
- Joining an academic conversation
- Building a tool that works
- Contributing a standardized vocabulary
- Inviting critique to improve the tool

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

## Prior Work Landscape (Three Buckets)

### Bucket A: Learned Representations (ML)
- **ASTNN** — AST-based neural representation (Zhang et al., 2019)
- **CodeBERT** — Bimodal NL-PL pretraining (Feng et al., 2020)
- **GraphCodeBERT** — Adds data-flow structure (Guo et al., 2021)
- **UniXcoder / CodeT5** — Cross-modal, identifier-aware (Wang et al., 2021; Guo et al., 2022)
- **Semantic Flow Graph** — Graph with roles/types for bug localization (Du & Yu, 2023)

*Characteristics:* Flexible, task-optimized, but representations may vary across runs/training data and are not directly human-readable.

### Bucket B: Symbolic / Graph Program-Analysis Representations
- **Code Property Graph (CPG)** — Unifies AST/CFG/PDG (Yamaguchi et al., 2014)
- **Program Dependence Graphs** — Classic control/data flow (Ferrante et al., 1987)
- **srcML** — XML representation of source code (Collard & Maletic)

*Characteristics:* Fixed structure, deterministic, but typically language-specific or analysis-task-specific.

### Bucket C: Meta-models and Interchange Standards
- **OMG KDM** — Knowledge Discovery Metamodel for software modernization (OMG)
- **FAMIX / Moose** — Language-independent software models (Ducasse et al.)
- **LSIF** — Language Server Index Format for code intelligence export (Microsoft)
- **JetBrains UAST** — Unified AST API across JVM languages

*Characteristics:* Standardized, interoperable, but not designed with LLM/agent consumption as primary goal.

---

## SMC's Unique Position

**Where SMC fits:** SMC is positioned as an **agent-actionable intermediate representation**—drawing on the interoperability goals of Bucket C, the structural rigor of Bucket B, while being explicitly designed for LLM consumption (unlike Buckets A-C).

### What SMC Contributes
- **Fixed taxonomy** — 200 atoms, 41 roles, 8 dimensions (versioned, stable)
- **Human-readable AND machine-actionable** — Dual audience by design
- **Versioned schema** — Stable contract for cross-tool interoperability
- **Agent-first design** — Explicitly structured for LLM reasoning (see evaluation criteria below)
- **Transparent classification** — Rules + evidence + confidence (auditable)

### Key Differentiator
Learned representations are flexible but unstable as interoperability contracts. Existing standards (KDM, LSIF) weren't designed for LLM consumption. SMC bridges this gap: a **fixed, versioned, agent-actionable schema** for code structure.

---

## One-Sentence Positioning

> "We propose a **versioned reference schema and taxonomy** for representing codebases as typed structural graphs, enabling interoperable analysis and agent-assisted reasoning."

Alternative framings (choose based on audience):

- **Academic-neutral:** "SMC is an engineering artifact contribution: a reproducible, versioned taxonomy and schema for representing code architecture."
- **Agent-focused:** "SMC provides a shared vocabulary so different tools and agents can reason with the *same concepts*, not incompatible embeddings."

---

## The Periodic Table Analogy (Use With Care)

**The periodic table is primarily an organizing and communication tool that also encodes useful regularities.**

Similarly:

**SMC organizes code structure as an organizing index, not as a claim of natural kinds.**

| Periodic Table | Standard Model of Code |
|----------------|------------------------|
| 118 elements | 200 atoms |
| Groups & periods | Roles & dimensions |
| Atomic properties | LOCUS coordinates |
| Enables chemistry communication | Enables AI-code reasoning |

**Caution:** The periodic table is associated with scientific discovery. Use this analogy to explain the *communication function*, not to imply SMC discovered fundamental truths.

---

## Design Goals and Non-Goals

### Goals
- **Interoperability** — Tools share the same schema
- **Explainability** — Every classification has traceable evidence
- **Agent utility** — LLMs can consume and reason over structure
- **Reproducibility** — Same code produces same output
- **Human steering** — Developers can inspect and override

### Non-Goals
- Full semantic intent inference
- Dynamic runtime behavior modeling
- Universal quality thresholds
- Replacing language-specific analysis tools
- Competing with neural embeddings for ML tasks

---

## "AI-First" as Measurable Properties

Saying "AI-first" requires operational definitions. Here's what it means for SMC:

| Property | What It Means | How We Evaluate |
|----------|---------------|-----------------|
| **Reproducibility** | Same code → same labels/graph | Agreement across extraction runs |
| **Explainability** | Every label has evidence | Traceable rule + feature mapping |
| **Interoperability** | Tools share schema | Cross-tool import/export tests |
| **Agent utility** | Agents perform tasks better | A/B: agent+SMC vs agent-only |
| **Human steering** | Humans can inspect/override | Annotation workflow usability |

---

## Governance and Versioning

If calling it a "standard model," we must answer "standard according to whom?"

### Version Policy
- **Semantic versioning:** MAJOR.MINOR.PATCH
- **Backward compatibility:** Non-breaking changes in MINOR/PATCH
- **Breaking changes:** MAJOR version bump with migration guide

### Extension Mechanism
- **Core atoms:** Stable, rarely changed
- **Ecosystem atoms:** Community extensions, clearly namespaced
- **Deprecation:** 2-version warning before removal

### Authority
- SMC is a *proposed* standard, not an established one
- "Standard" is aspirational, indicating stability goals
- Formal standardization (if pursued) would require community process

---

## How to Use Prior Work

### In Introduction
```
"Prior work has shown that structured code representations
improve program understanding (Zhang et al., 2019; Du & Yu, 2023).
Meta-models like KDM (OMG) and FAMIX have established interchange
standards. We build on these foundations by proposing a fixed
reference taxonomy designed specifically for LLM-based agents..."
```

### In Related Work
```
"The Code Property Graph (Yamaguchi et al., 2014) unifies AST,
CFG, and PDG for vulnerability analysis. The Semantic Flow Graph
(Du & Yu, 2023) captures program element types and computational
roles for bug localization. Our work differs in providing a
*fixed, versioned* taxonomy explicitly designed for cross-system
interoperability and agent consumption..."
```

### In Contribution Statement
```
"Where prior work learns task-specific representations (CodeBERT,
GraphCodeBERT) or provides analysis-focused graphs (CPG), we
propose a standardized reference schema. Our contribution is not
a better neural network, but an agent-actionable lingua franca
for code structure."
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
- "The code obeys..." → Use "We represent code as..."

### Vocabulary to USE
- "We propose..."
- "We define..."
- "We show evidence that..."
- "This model suggests..."
- "We invite investigation..."
- "Building on prior work..."

### On "Ontology"
- Use only if formalized (e.g., OWL/RDF serialization)
- Otherwise prefer "taxonomy" or "schema"
- "Ontology" is legitimate in SE/semantic web contexts but triggers expectations

---

## Evaluation Framework

SMC validity is **empirical and task-dependent**. We evaluate as an engineering artifact:

### Research Questions (Paper)
- **RQ1:** Extraction reproducibility — Does Collider produce consistent output?
- **RQ2:** Cross-codebase applicability — Does the taxonomy cover diverse projects?
- **RQ3:** Agent utility — Do LLMs perform code tasks better with SMC structure?
- **RQ4:** Human interpretability — Can developers understand and correct classifications?

### Metrics
- Cohen's kappa for classification agreement
- Coverage percentage across atom/role types
- Task accuracy delta (with/without SMC)
- Time-to-understanding for human onboarding

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
   - Learned representations (ASTNN, CodeBERT, SFG)
   - Symbolic representations (CPG, PDG)
   - Meta-models and standards (KDM, FAMIX, LSIF)
   - Quality models (ISO 25010)

3. DESIGN GOALS & NON-GOALS
   - What SMC aims to provide
   - What SMC explicitly doesn't attempt

4. THE STANDARD MODEL OF CODE
   - Schema overview
   - Atoms (200 structural types)
   - Roles (41 semantic categories)
   - Dimensions (8 orthogonal properties)
   - LOCUS coordinates

5. IMPLEMENTATION: COLLIDER
   - Architecture
   - Extraction pipeline
   - Output schema (JSON)

6. EVALUATION
   - RQ1: Reproducibility
   - RQ2: Coverage
   - RQ3: Agent utility
   - RQ4: Human interpretability

7. DISCUSSION & LIMITATIONS
   - What the model doesn't capture
   - Threats to validity
   - Future work

8. CONCLUSION
   - Summary of contribution
   - Invitation to extend
```

---

## Key Papers to Cite

### Learned Representations
- Zhang et al., 2019 — ASTNN (AST-based neural representation)
- Feng et al., 2020 — CodeBERT (bimodal pre-trained model)
- Guo et al., 2021 — GraphCodeBERT (data flow structure)
- Du & Yu, 2023 — Semantic Flow Graph (ESEC/FSE)

### Symbolic/Graph Representations
- Yamaguchi et al., 2014 — Code Property Graph
- Ferrante et al., 1987 — Program Dependence Graph

### Meta-models and Standards
- OMG KDM — Knowledge Discovery Metamodel
- Ducasse et al. — FAMIX/Moose ecosystem
- Microsoft — LSIF specification

### Taxonomies (Methodology)
- Usman et al., 2017 — Taxonomies in Software Engineering
- Zhai et al., 2020 — CPC (comment classification and propagation)

### Surveys
- Allamanis et al., 2018 — Survey of ML for Big Code
- Casey et al., 2024 — Survey of Source Code Representations

### Quality Models
- ISO/IEC 25010 — Software quality model

---

## The Motivation (Personal Context)

This project exists because:

1. **Practical need** — Building apps requires understanding code
2. **AI augmentation** — LLMs need structured input to reason well
3. **Tool-first** — The goal is a working tool, not academic prestige
4. **Open contribution** — Publishing invites collaboration and scrutiny

The academic paper is about:
- Formalizing ideas rigorously
- Inviting scrutiny and improvement
- Contributing to the field
- Building credibility for the tool

---

## Reviewer-Proof Summary

> SMC is positioned as an engineering contribution: a versioned reference schema and taxonomy that represents codebases as typed structural graphs with derived roles and dimensions. Our goal is not to assert universal laws of software, but to provide a reproducible, human-auditable, and agent-actionable contract for interoperable tooling. We evaluate SMC by extraction stability, cross-codebase applicability, and task utility for both automated agents and human developers, and we explicitly scope non-goals such as full intent inference and universal thresholds.

---

## Bottom Line

**Don't compete. Contribute.**

Stand on the shoulders of giants. Cite generously. Carve out your specific contribution:

> A fixed, versioned, human-readable, machine-actionable taxonomy of code structure—designed for AI agents to reason about architecture.

Not better than prior work. *Different* from prior work. Filling a specific gap. And useful.
