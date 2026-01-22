# AI Orchestration Protocol for Phase 2 Research

> **Classification:** Research Methodology
> **Date:** 2026-01-22
> **Status:** ACTIVE
> **Prerequisite:** Phase 2 Protocol (ATOM_COVERAGE_PHASE2_PROTOCOL.md)

---

## Overview

This protocol defines how to coordinate three AI systems for maximum research rigor:

| System | Model | Strength | Research Role |
|--------|-------|----------|---------------|
| **Gemini** | gemini-2.5-pro | Long context (1M+), code understanding | Structural analysis, pattern detection |
| **Perplexity** | sonar-pro | Real-time web research, citations | Literature validation, external evidence |
| **ChatGPT** | o3 Extended Thinking | Deep reasoning, falsification | Hypothesis critique, audit review |

---

## Core Principle: Ensemble Validation

No claim advances without agreement from multiple AI systems.

```
┌─────────────────────────────────────────────────────────────┐
│                    ENSEMBLE PROTOCOL                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Finding ──► Gemini Analysis ──┐                           │
│                                 │                           │
│   Finding ──► Perplexity Check ─┼──► Convergence ──► Claim  │
│                                 │     Test                   │
│   Finding ──► ChatGPT Falsify ──┘                           │
│                                                             │
│   If ANY system disagrees → Investigate before promotion    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## System Roles by Study

### Study A: Structural Generalization

| Task | Primary AI | Verification AI | Method |
|------|------------|-----------------|--------|
| Corpus stratification | Gemini | Perplexity | Validate repo categories against GitHub data |
| Top-4 mass computation | Deterministic code | Gemini | Spot-check 10% of runs |
| Variance explanation | Gemini | ChatGPT | Propose/falsify paradigm correlations |
| L2 promotion decision | ChatGPT | Gemini | Extended thinking critique |

### Study B: T2 Precision

| Task | Primary AI | Verification AI | Method |
|------|------------|-----------------|--------|
| Sample selection | Deterministic code | Gemini | Verify stratified sampling |
| Initial labeling | Human | Gemini | AI suggests, human decides |
| Error classification | Gemini | ChatGPT | Cross-validate error types |
| Precision calculation | Deterministic code | ChatGPT | Audit methodology |

### Study C: Functional Enrichment

| Task | Primary AI | Verification AI | Method |
|------|------------|-----------------|--------|
| Pattern mining | Gemini | Perplexity | Find official framework docs |
| Atom generation | Gemini | ChatGPT | Critique pattern precision |
| Negative examples | ChatGPT | Gemini | Adversarial case generation |
| Quality gate | Human + ChatGPT | Gemini | Triple review |

---

## Quality Gates

### Gate 1: Consistency Check

Before any claim promotion, run the same query through all three systems.

```bash
# Example: Validate Finding 1 (Pareto distribution)
.tools_venv/bin/python context-management/tools/ai/analyze.py \
  "Analyze the top-4 mass distribution in this corpus. Does it support a Pareto claim? What are the confidence bounds?" \
  --set research_full
```

**Acceptance Criteria:**
- All systems agree on direction (supports/contradicts)
- Confidence ranges overlap
- No system flags methodological issues

### Gate 2: Contradiction Check (Falsification)

Ask ChatGPT Extended Thinking specifically to find flaws.

**Prompt Template:**
```
You are an adversarial reviewer. Your goal is to find flaws in this research claim:

CLAIM: [insert claim]
EVIDENCE: [insert evidence summary]
METHOD: [insert methodology]

Tasks:
1. List all unstated assumptions
2. Identify potential confounding variables
3. Propose specific falsification tests
4. Rate confidence (0-100%) that this claim would survive peer review

Be harsh. If you cannot find flaws, explain why the methodology is sound.
```

### Gate 3: Convergence Score

For each finding, compute ensemble agreement:

| Agreement Level | Score | Action |
|-----------------|-------|--------|
| 3/3 agree | 100% | Promote claim |
| 2/3 agree, 1 uncertain | 80% | Promote with caveat |
| 2/3 agree, 1 disagrees | 60% | Investigate disagreement |
| 1/3 or fewer agree | <50% | Do not promote |

---

## Prompt Templates

### Gemini: Structural Analysis

**Use when:** Analyzing code patterns, coverage metrics, pipeline behavior

```
CONTEXT: Phase 2 Atom Coverage Research
SET: research_full

TASK: [specific analysis task]

REQUIREMENTS:
1. Cite specific file paths and line numbers
2. Provide quantitative metrics where possible
3. Flag any data quality issues
4. Distinguish between observation and interpretation

OUTPUT FORMAT:
## Observation
[What the data shows]

## Interpretation
[What this means for the hypothesis]

## Confidence
[0-100% with justification]

## Limitations
[What this analysis cannot tell us]
```

**Command:**
```bash
.tools_venv/bin/python context-management/tools/ai/analyze.py \
  "[TASK]" \
  --set research_full \
  --mode forensic
```

### Perplexity: External Validation

**Use when:** Checking claims against literature, finding prior art, validating methodology

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a research methodology validator. Find external evidence supporting or contradicting claims. Always cite sources with URLs."
    },
    {
      "role": "user",
      "content": "CLAIM: [insert claim]\n\nTasks:\n1. Find academic papers supporting/contradicting this claim\n2. Find industry reports with similar findings\n3. Identify standard methodologies for this type of research\n4. Flag if the claim is novel or well-established\n\nProvide URLs for all citations."
    }
  ]
}
```

**MCP Tool:**
```
mcp__perplexity__perplexity_research
```

### ChatGPT: Falsification Audit

**Use when:** Critiquing methodology, finding edge cases, preparing for peer review

```
ROLE: Adversarial Research Auditor

CONTEXT:
- Project: Standard Model of Code / Collider
- Phase: Phase 2 Atom Coverage Research
- Goal: Validate claims before promotion to L2

FINDING:
[paste finding with evidence]

AUDIT TASKS:
1. ASSUMPTIONS: List all implicit assumptions. Which are testable?
2. METHODOLOGY: What could bias these results?
3. STATISTICS: Are the sample sizes adequate? Is the analysis appropriate?
4. REPRODUCIBILITY: What would prevent another team from replicating?
5. SCOPE: What does this finding NOT tell us?
6. FALSIFICATION: Design 3 specific tests that would disprove this claim
7. VERDICT: Would this survive peer review? (Yes/Probably/Unlikely/No)

Be direct. Excessive praise is unhelpful.
```

---

## Workflow: Claim Promotion

### Step 1: Generate Finding

1. Run deterministic analysis (Mode A)
2. Compute metrics with `atom_coverage.py`
3. Document in evidence ledger

### Step 2: Gemini Analysis

```bash
.tools_venv/bin/python context-management/tools/ai/analyze.py \
  "Review Finding [N]: [summary]. Validate the evidence chain. Identify any gaps." \
  --set research_validation \
  --mode forensic
```

Store response in `artifacts/ai-audit/gemini_finding_N.md`

### Step 3: Perplexity Validation

Query for external validation:
- Similar research methodologies
- Industry benchmarks
- Contradicting evidence

Store response in `artifacts/ai-audit/perplexity_finding_N.md`

### Step 4: ChatGPT Falsification

Use Extended Thinking for deep critique.

Store response in `artifacts/ai-audit/chatgpt_finding_N.md`

### Step 5: Convergence Decision

| Gemini | Perplexity | ChatGPT | Action |
|--------|------------|---------|--------|
| Supports | Supports | Supports | Promote to L2 |
| Supports | Supports | Uncertain | Promote with caveat |
| Supports | Uncertain | Supports | Additional external validation |
| Mixed | Mixed | Mixed | Do not promote |

Document decision in `artifacts/ai-audit/decision_finding_N.md`

---

## Artifact Layout

```
artifacts/
├── atom-research/
│   └── 2026-01-22/
│       ├── ...existing...
│       └── ai-audit/
│           ├── gemini_finding_1.md
│           ├── perplexity_finding_1.md
│           ├── chatgpt_finding_1.md
│           ├── decision_finding_1.md
│           ├── ...
│           └── ensemble_summary.md
```

---

## Anti-Patterns

### DO NOT:

1. **Accept single-AI validation** - All claims need ensemble check
2. **Skip falsification** - ChatGPT must attempt to break every finding
3. **Ignore disagreement** - If AIs disagree, investigate before proceeding
4. **Use AI for raw metrics** - Deterministic code computes numbers; AI interprets
5. **Trust without citation** - Perplexity must provide URLs; Gemini must cite lines

### DO:

1. **Run deterministic baseline first** - AI validates, doesn't generate numbers
2. **Document all AI outputs** - Full transcripts in `ai-audit/`
3. **Use forensic mode** - Require line-level evidence from Gemini
4. **Cross-check claims** - Each finding gets 3 AI reviews
5. **Update decision log** - Every promotion decision is recorded

---

## Quick Reference

### Analyze Coverage (Gemini)
```bash
.tools_venv/bin/python context-management/tools/ai/analyze.py \
  "[query]" --set research_full --mode forensic
```

### External Validation (Perplexity)
```
Use MCP: mcp__perplexity__perplexity_research
```

### Falsification Audit (ChatGPT)
```
Use Extended Thinking with adversarial prompt template
```

### Convergence Check
```
Compare all 3 outputs → Score agreement → Document decision
```

---

## Version History

| Date | Change | Author |
|------|--------|--------|
| 2026-01-22 | Initial protocol | Claude Opus 4.5 |
