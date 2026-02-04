# Research: Create a documentation update plan for Standard Model of Code.

CONTEXT:
We have just established ne...

> **Date:** 2026-02-02 00:51:12
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:f616baa8a68792de49eedb62ad8646a5058780f68a1dbb80b1b89e8e9d04309f`
> **Raw JSON:** `raw/20260202_005112_create_a_documentation_update_plan_for_standard_mo.json`

---

## Query

Create a documentation update plan for Standard Model of Code.

CONTEXT:
We have just established new framing in particle/docs/specs/PAPER_FRAMING.md that repositions SMC from 'scientific discovery' to 'practical tool / reference model for AI context compression'.

KEY CHANGES NEEDED:
1. Language: 'discovered' → 'proposed', 'laws' → 'definitions', 'truth' → 'utility'
2. Remove overclaims about universal laws or ontological truth
3. Add epistemic positioning / disclaimers where needed
4. Emphasize AI-first use case (context compression for agents)
5. Keep physics metaphors but mark them as 'heuristic devices'

FILES TO AUDIT:
- particle/docs/theory/*.md (all theory docs)
- particle/docs/specs/*.md
- wave/docs/*.md
- README files
- CLAUDE.md files

DELIVERABLE:
Create a prioritized task list with:
1. File path
2. What needs to change
3. Priority (HIGH/MEDIUM/LOW)
4. Estimated scope (lines to change)

Focus on files that have the MOST overclaiming language that conflicts with the new framing.

---

## Response

Based on the new framing established in `particle/docs/specs/PAPER_FRAMING.md`, here is the prioritized documentation update plan.

The core strategic shift is moving from **Ontological Discovery** (finding pre-existing truths) to **Epistemic Utility** (creating a useful model for AI efficiency).

### Execution Strategy
1.  **Create Global Disclaimer:** Add a standard "Epistemic Status" block to `particle/docs/MODEL.md` to be transcluded or referenced elsewhere.
2.  **Update Agent Context First:** Fix `CLAUDE.md` and `KERNEL.md` first so AI agents stop generating "Universal Truth" content during the refactor.
3.  **Refactor Theory:** Downgrade "Laws" to "Principles" or "Heuristics".

---

### Priority 1: High (Critical Framing & Agent Context)
*These files define the project identity or are the primary reading material for the AI agents.*

| File Path | Change Required | Scope |
| :--- | :--- | :--- |
| **`particle/docs/MODEL.md`** | **Canonical Reframing.**<br>1. Add "Epistemic Status: Heuristic Model" header.<br>2. Change "Code IS physics" to "Treating code AS physics allows..."<br>3. Frame the "Standard Model" as a compression schema, not a discovery of nature. | Large<br>(~50 lines) |
| **`particle/CLAUDE.md`** | **Agent Instructions.**<br>Update project description. Explicitly instruct agents: "Do not frame SMC as a scientific discovery of natural laws. Frame it as a rigorous schema for context management." | Small<br>(~10 lines) |
| **`.agent/KERNEL.md`** | **Mission Statement.**<br>Change "Mission: Find the basic constituents of computer programs" to "Mission: Define standard constituents for AI context compression." | Small<br>(~5 lines) |
| **`particle/docs/theory/L2_LAWS`** | **Terminology Shift.**<br>Rename file/concept to `L2_PRINCIPLES` or `L2_DYNAMICS`.<br>Change "Laws of Code" to "Operational Principles".<br>Clarify that these are observed regularities, not immutable physical laws. | Medium<br>(~30 lines) |
| **`REPO_STRUCTURE.json`** | **Metadata.**<br>Change description: "Theoretical framework treating code like physics" $\to$ "Context compression framework using physics-based metaphors." | Tiny<br>(1 line) |

### Priority 2: Medium (Specs & Theory Details)
*These files contain specific "truth claims" that are now over-aggressive.*

| File Path | Change Required | Scope |
| :--- | :--- | :--- |
| **`particle/docs/theory/L0_AXIOMS`** | **Softening.**<br>Change "Axioms of Reality" to "Modeling Assumptions".<br>Clarify that these are the rules *we chose* to make the system work, not rules we found in the universe. | Medium<br>(~20 lines) |
| **`particle/docs/specs/CODOME_COMPLETENESS_INDEX.md`** | **Validation vs. Truth.**<br>Change "Proves we found all code" to "Validates coverage against the schema."<br>Remove "Ground Truth" where it implies absolute reality; use "Reference Total" instead. | Medium<br>(~15 lines) |
| **`particle/docs/specs/EXHAUSTIVE_CLASSIFICATION_MODEL.md`** | **Tone Shift.**<br>The word "Exhaustive" is fine, but frame it as "Taxonomic Completeness" (we have a bucket for everything) rather than "Physical Completeness" (we found every atom in the universe). | Medium<br>(~20 lines) |
| **`.agent/CODOME_MANIFEST.yaml`** | **Description.**<br>Update `description`: "Standard Model of Code - Finding the basic constituents..." $\to$ "Standard Model of Code - A schema for token-efficient code representation." | Tiny<br>(1 line) |
| **`particle/docs/COLLIDER.md`** | **Value Prop.**<br>Add section "AI Context Efficiency". Explain that Collider isn't just measuring code, it's *compressing* it for LLMs (Wave layer). | Medium<br>(~20 lines) |

### Priority 3: Low (Legacy & Peripheral)
*These files likely contain old framing but are less visible or strictly technical.*

| File Path | Change Required | Scope |
| :--- | :--- | :--- |
| **`wave/docs/AI_USER_GUIDE.md`** | **Integration.**<br>Ensure the "Why Collider?" section emphasizes that the rigorous model exists to save the AI tokens and reduce hallucinations, not just for the sake of "science." | Small<br>(~10 lines) |
| **`particle/docs/specs/COMPLETENESS_ATTESTATION_PROTOCOL.md`** | **Terminology.**<br>"Attestation" implies swearing to a truth. Soften to "Coverage Verification Protocol." | Small<br>(~5 lines) |
| **`DOMAINS.yaml`** | **Drift Check.**<br>Review descriptions for `Atoms` domain. Ensure it describes "Taxonomy" rather than "Nature." | Tiny<br>(~2 lines) |

---

### Implementation Task (Copy/Paste for Deck)

You can create a new Task Card (`CARD-DOC-002`) to track this refactor.

```yaml
# CARD-DOC-002: Reframing Documentation
# Align docs with PAPER_FRAMING.md (Discovery -> Utility)

id: CARD-DOC-002
title: "Reframe SMC Documentation"
description: "Update documentation to shift framing from 'scientific discovery of universal laws' to 'practical utility for AI context compression'. Replace 'truth' with 'utility' and 'laws' with 'principles'."

phase_gate: [EXECUTING]

preconditions:
  - check: "PAPER_FRAMING.md exists"
    description: "New strategic positioning is defined"

steps:
  - action: "Update particle/docs/MODEL.md with Epistemic Status"
    description: "Add disclaimer that physics metaphors are heuristic devices"
  - action: "Update CLAUDE.md and KERNEL.md"
    description: "Realign agent instructions to new mission"
  - action: "Refactor L0_AXIOMS and L2_LAWS"
    description: "Rename Laws -> Principles, Axioms -> Assumptions"
  - action: "Audit specs for 'Ground Truth' overclaims"
    description: "Replace with 'Reference Standard' or 'Schema Coverage'"

outcomes:
  success:
    state_changes:
      - "Project framed as AI Tool, not Physics Discovery"
      - "Reduced risk of overclaiming"
    meters:
      alignment: 1
      clarity: 1

tags: [docs, refactor, branding, theory]
```

---

## Citations

_No citations provided_
