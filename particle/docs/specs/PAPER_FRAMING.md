# Standard Model of Code: Paper Framing

**Status:** Canonical positioning for all documentation and agents
**Date:** 2026-02-02
**Authority:** This document overrides any conflicting framing in other docs

---

## The Core Position

**What we are doing:**
> We propose a reference model that makes code structure machine-actionable, enabling AI agents to reason about code as architecture rather than text.

**What we are NOT doing:**
> We are not claiming to have discovered fundamental laws of software. We built a tool. It works. Here's how we think about code. Does it help you too?

---

## The Value Proposition

### The Problem (2026)

```
CODEBASE SIZE          vs.        CONTEXT WINDOW
─────────────                     ──────────────
500 files                         128K-1M tokens
50,000+ lines
~2M tokens                        CAN'T FIT IT ALL
```

Current approach ("context stuffing") fails:
- Dump raw files into context
- Run out of space
- Agent hallucinates missing parts
- Breaks things

### The Solution: Context Compression

SMC compresses code into semantic structure:

| Raw Code | SMC Atom |
|----------|----------|
| 200 lines, ~800 tokens | ~50 tokens |
| Syntax | Architecture |
| Text | Graph |

**16x compression** while preserving what AI needs to reason.

### The Hook (One Sentence)

> "As AI agents move from generating functions to managing systems, they need architecture understanding, not just text. SMC compresses codebases into semantic structure that fits in context windows while preserving reasoning power."

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

All agents and documentation MUST use this vocabulary:

| Instead of... | Write... |
|---------------|----------|
| "The law states..." | "We define..." |
| "Code obeys..." | "We represent code as..." |
| "We discovered..." | "We propose..." |
| "We prove..." | "We show evidence that..." |
| "The ontology of code..." | "A taxonomy of code elements..." |
| "Truth" | "Utility" |
| "Universal" | "Context-dependent" |
| "Causes" | "Predicts / correlates with" |
| "Validated" | "Supported by evidence" |

---

## Epistemic Positioning (For Paper Introduction)

> **Epistemic Positioning:** We explicitly do not claim to have discovered fundamental laws of nature governing software. Code is a human construct, not a physical phenomenon. Instead, we propose the "Standard Model of Code" as a **heuristic reference architecture**.
>
> While we employ nomenclature from physics (e.g., "Atoms," "Collider") to describe component granularity and interaction dynamics, these are functional analogies designed to provide AI agents with a coherent, deterministic ontology for reasoning about non-deterministic systems.
>
> The success of this model is measured not by its ontological truth, but by its engineering utility in reducing context fragmentation.

---

## What This Paper Does NOT Claim

Include in Introduction (condensed) and Limitations (full):

1. **Not ontological truth** - These categories are proposals, not discoveries
2. **Not universal constants** - Thresholds are configurable, not laws of nature
3. **Not physics** - Analogies are heuristic devices, not literal claims
4. **Not complete** - The model is extensible, not final
5. **Not the only way** - Alternative taxonomies could also work

---

## Why We Publish

1. To share a mental model we found useful
2. To invite investigation, not demand agreement
3. To provide AI agents with structured code understanding
4. To learn from community feedback what works and what doesn't
5. To build better tools for ourselves and others

---

## Success Metrics

The model succeeds if:

| Metric | Question |
|--------|----------|
| **Utility** | Does it help AI reason about code? |
| **Compression** | Does it fit more meaning in less context? |
| **Consistency** | Do different codebases get comparable representations? |
| **Actionability** | Can agents use it to make correct decisions? |

The model does NOT need to:
- Be "true" in a Platonic sense
- Match some external "real" ontology
- Be accepted by all academics
- Win arguments about philosophy

---

## Paper Structure (Recommended)

```
1. INTRODUCTION
   - AI agents need structured code understanding
   - Text-based analysis is insufficient
   - We propose a reference model
   - Epistemic positioning (what we claim / don't claim)

2. DESIGN GOALS
   - Human-readable AND machine-actionable
   - Finite primitives, compositional rules
   - Language-agnostic where possible
   - Context compression for AI agents

3. THE MODEL
   - 3.1 Atoms (structural types)
   - 3.2 Roles (semantic categories)
   - 3.3 Dimensions (orthogonal properties)
   - 3.4 LOCUS coordinates
   - 3.5 Graph representation

4. IMPLEMENTATION: COLLIDER
   - Architecture
   - Extraction pipeline
   - Output schema

5. EVALUATION
   - RQ1: Can AI use this for code navigation?
   - RQ2: Does structure improve over text?
   - RQ3: Consistency across codebases?

6. LIMITATIONS & OPEN QUESTIONS
   - What the model doesn't capture
   - Where boundaries are unclear
   - What we don't claim (full version)
   - Invitation to extend

7. RELATED WORK
   - Code ontologies, AST analysis, knowledge graphs

8. CONCLUSION
   - Summary of contribution
   - The question we leave open
```

---

## The Periodic Table Analogy (Correct Usage)

**Correct:**
> "Like a periodic table for software structure, SMC doesn't claim to explain WHY code works—only to provide a consistent language for describing WHAT is there."

**Incorrect:**
> "SMC discovers the fundamental elements of code like chemistry discovered elements."

The periodic table organizes. It doesn't explain chemistry. SMC organizes. It doesn't explain software.

---

## Addressing Reviewer Concerns (Preemptively)

| Likely Critique | Our Response |
|-----------------|--------------|
| "These aren't real laws" | Correct. We propose definitions, not discoveries. |
| "Thresholds are arbitrary" | Yes. They're configurable defaults, not constants. |
| "Why not just use AST?" | AST captures syntax. SMC captures architecture and intent for AI context. |
| "Physics metaphors are pretentious" | They're heuristic devices for intuition, defined once, then we use technical terms. |
| "How do you validate this?" | By utility: does AI reason better with this structure? |

---

## For All Agents

When working on SMC documentation or code:

1. **Don't defend the theory** - It doesn't need defense. It needs testing.
2. **Don't seek validation** - Seek utility instead.
3. **Don't overclaim** - "We suggest" not "we prove"
4. **Focus on the tool** - Collider works. The viz works. That's evidence.
5. **Remember the goal** - Build apps. Make money. Stay relevant. Help others do the same.

---

## The Bottom Line

```
OLD FRAME                          NEW FRAME
─────────                          ─────────
"We discovered laws"               "We built a tool"
"Prove us right"                   "Does this help you?"
"Universal truth"                  "Useful structure"
"Academic validation"              "Engineering utility"
"Nobel Prize"                      "Working software"
```

---

*"We are not physicists discovering nature. We are toolmakers sharing blueprints."*
