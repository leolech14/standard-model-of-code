---
id: nav_consumers
title: "Consumers - Who Uses the Output?"
category: nav
theory_refs: [L0_AXIOMS.md H1-H5]
consumer_classes: 3
---

# CONSUMERS - Who Uses the Output?

> Three consumer classes. The Stone Tool Principle. AI as universal consumer.

<!-- T1:END -->

---

## The 3 Consumer Classes

Every output of the SMoC system is consumed by one of three audiences:

| Consumer | Needs | Format | Example |
|----------|-------|--------|---------|
| **END_USER** | Usability | Dashboards, summaries | "Your codebase has 3 critical issues" |
| **DEVELOPER** | Clarity | Code, structured reports | Architecture diagrams, role distributions |
| **AI_AGENT** | Parseability | JSON, YAML, structured data | `unified_analysis.json` (5,000+ lines) |

---

## The Stone Tool Principle

> Tools MAY be designed that humans cannot directly use. AI mediates.

The `unified_analysis.json` output is a **stone tool**: a 5,000+ line structured graph that is useful only through AI interpretation. No human reads it directly. An AI agent queries it.

This is a **valid design choice**, not a limitation. Just as a microscope mediates between human eyes and bacteria, AI mediates between humans and complex structured data.

---

<!-- T2:END -->

## Why This Matters

Traditional software tools optimize for DEVELOPER as the primary consumer. The SMoC recognizes that:

1. **AI agents are first-class consumers** -- they need structured, machine-parseable output
2. **Humans need mediated access** -- AI translates stone tools into dashboards
3. **Output format follows consumer** -- don't force JSON on developers or prose on AI

---

## AI as Universal Consumer

From L0_AXIOMS.md (Axiom H4): AI acts as a **universal consumer** that can engage at any Tarski meta-level:

| Level | What AI Does |
|-------|-------------|
| **Object level** | Read the code directly |
| **Meta level** | Read the Collider's analysis of the code |
| **Meta-meta level** | Reason about the analysis methodology itself |

Human consumers typically operate at one level. AI fluidly crosses levels. This makes AI the ideal mediator between stone tools and human understanding.

---

## Collaboration at L1

From Axiom H5: Effective human-AI collaboration requires both operating at the same abstraction level. The classification system (atoms, roles, layers) provides a **shared vocabulary** that both humans and AI understand.

Instead of:
- Human: "That function is kind of important"
- AI: "Node has betweenness centrality 0.847"

With shared vocabulary:
- Both: "This is a Service role in the Application layer with high coupling"

---

## Consumer-Aware Design

| Design Decision | END_USER | DEVELOPER | AI_AGENT |
|-----------------|----------|-----------|----------|
| Show raw graph? | No | Maybe | Yes |
| Show health score? | Yes (color) | Yes (number) | Yes (float) |
| Show antimatter? | "3 issues found" | Location + fix | JSON pattern match |
| Show purpose drift? | "Outdated docs" | Diff view | Cosine distance |

---

*Source: L0_AXIOMS.md (Axioms H1-H5)*
*See also: [../essentials/THEORY_WINS.md](../essentials/THEORY_WINS.md) (Idea #12), [../essentials/ARCHITECTURE.md](../essentials/ARCHITECTURE.md) for system outputs*
