# Research: Why doesn't our BARE system automatically boost task confidence? Looking at TASK-120 (Autonomous Con...

> **Date:** 2026-01-23 06:31:23
> **Source:** gemini
> **Model:** gemini-2.5-pro
> **Checksum:** `sha256:3c975f31ad0dd92677e8fc795d269c190443af9e1cc03fc965d988a3e48b1a28`
> **Raw JSON:** `raw/20260123_063123_why_doesn_t_our_bare_system_automatically_boost_ta.json`

---

## Query

Why doesn't our BARE system automatically boost task confidence? Looking at TASK-120 (Autonomous Confidence Booster) and TASK-121 (Task Opportunity Explorer) - these are supposed to auto-boost confidence but they're not implemented yet. What's the gap between our current TruthValidator (which runs on post-commit) and a full confidence boosting system? What minimal changes would enable automatic confidence boosting?

---

## Response

As a senior software engineer, I've analyzed the provided context. Here’s a breakdown of why our BARE system doesn't automatically boost task confidence yet, the architectural gap that exists, and the minimal path to implementing this capability.

### Executive Summary

You've hit on a critical point. The system currently lacks an *autonomous confidence booster* because our existing `TruthValidator` is designed for **post-commit verification**, not **pre-execution validation**.

*   **Verification (Current State):** "Does the code I just committed align with our established rules?" This is a backward-looking, rule-based check for drift.
*   **Validation (Desired State):** "Is the plan for this new task correct, complete, and likely to succeed?" This is a forward-looking, reasoning-based assessment of a proposed change.

The gap is between a simple rule-checker and a complex reasoning engine. We have the manual process for this reasoning documented in `WORKFLOW_FACTORY.md` as the "Socratic Research Loop," but we haven't automated it yet.

---

### Analysis: The Gap Between `TruthValidator` and `ConfidenceBooster`

The `TruthValidator` you mentioned, which is part of the Holographic-Socratic Layer (`HOLOGRAPHIC_SOCRATIC_LAYER.md`), is excellent at its job, but its job is narrowly defined. Let's compare it to the requirements of the unimplemented `TASK-120` (Autonomous Confidence Booster).

| Feature | `TruthValidator` (Current System) | `ConfidenceBooster` (Desired System) |
| :--- | :--- | :--- |
| **Purpose** | **Verification**: Detect drift from established truths. | **Validation**: Assess the feasibility and risk of a new plan. |
| **Trigger** | Post-commit, scheduled, or file-change. | Pre-execution, on-demand for a specific task. |
| **Scope** | Backward-looking: "Does this code violate our `semantic_models.yaml`?" | Forward-looking: "Will this plan achieve its goal without causing new issues?" |
| **Mechanism** | Rule-based checks and invariant enforcement (e.g., Antimatter Laws). | Multi-modal reasoning: using LLMs, external search, and full-context analysis. |
| **Core Input** | Committed code diff + `semantic_models.yaml`. | Task description + proposed plan + relevant codebase context (`analysis_sets.yaml`). |
| **Output** | A binary pass/fail or a drift report. | A 4D confidence score (Factual, Vision, Current, Onwards) with evidence, as seen in `DOCS_REORG_TASK_REGISTRY.md`. |
| **Key File(s)** | `semantic_models.yaml`, `documentation_map.yaml` | `analysis_prompts.yaml`, `aci_config.yaml`, `WORKFLOW_FACTORY.md` |

The `TruthValidator` answers, "Is the map of our territory still accurate?" The `ConfidenceBooster` needs to answer, "Is this new route on the map a good idea?" These are fundamentally different questions requiring different tools and context.

The manual process for this is already well-defined in **`context-management/docs/WORKFLOW_FACTORY.md`** under the "Socratic Research Loop." It describes exactly what `TASK-120` should automate: using Gemini for internal validation, Perplexity for external validation, and file reads for ground truth to boost the 4D confidence scores.

---

### Minimal Changes to Enable Automatic Confidence Boosting

We can implement this incrementally. We don't need to build the fully autonomous `TASK-120` in one step. Here is a practical, phased approach.

#### Phase 1: Create a "Confidence-Boosting" Script

The first step is to automate the manual Socratic Research Loop. We can create a new tool, `boost_confidence.py`, that takes a task ID as input and generates a confidence report.

1.  **Create a New Analysis Prompt:**
    We would add a new prompt to `prompts.yaml` specifically for this task, synthesizing the ideas from `plan_validation` and `role_validation` into a general-purpose task assessor.

    ```yaml
    # In prompts.yaml
    task_assessment: |
      You are a Staff Engineer reviewing a proposed task.
      CONTEXT:
      - Task Description: {task_description}
      - Proposed Plan: {task_plan}
      - Relevant Code: {code_context}

      TASK:
      1. Analyze the Factual Correctness of the plan against the code.
      2. Assess Alignment with project vision (is this a good idea?).
      3. Evaluate impact on the Current codebase (what will this break?).
      4. Predict if this aligns with our Onwards trajectory (see roadmap).
      5. Output a JSON object with a confidence score (0.0-1.0) and rationale for each of the 4D dimensions.
    ```

2.  **Develop `boost_confidence.py`:**
    This script would orchestrate the process:
    *   **Input:** `python tools/ai/boost_confidence.py --task TASK-123`
    *   **Steps:**
        1.  Parse the task's YAML file (e.g., from `.agent/registry/active/TASK-123.yaml`).
        2.  Extract the task description and any proposed plan/diff.
        3.  Use keywords from the task to select the appropriate `analysis_sets.yaml` (e.g., a "schema" task loads the `schema` set). The `set_mappings` in `aci_config.yaml` can help here.
        4.  Load the relevant code into the context.
        5.  Invoke the new `task_assessment` prompt.
        6.  Check for `external_indicators` in `aci_config.yaml` (e.g., "best practice," "2026") to decide if a query to the `perplexity` tier is needed for external validation.
    *   **Output:** A structured JSON or markdown report with the 4D confidence scores and rationale.

This script doesn't *set* the confidence, but it does the heavy lifting and presents a complete report for a human or a primary agent to consume.

#### Phase 2: Integrate into the Agent Workflow

Once the script from Phase 1 is reliable, we can integrate it into the core agent logic.

1.  **Modify Agent Kernel Logic:**
    The `.agent/KERNEL.md` implies a boot sequence. We can add a step to the agent's main loop: "If a task's confidence is below a threshold (e.g., 90%), run `boost_confidence.py`."
2.  **Decision Making:**
    The agent would then parse the report from the script.
    *   If the boosted confidence meets the execution threshold (defined in `WORKFLOW_FACTORY.md`), the agent proceeds with the task.
    *   If not, the agent flags the task for human review, attaching the confidence report as evidence.

This achieves semi-autonomy and makes the agent significantly more robust without granting it the permission to modify its own confidence scores directly. This is the crucial step to building trust in the system before full automation. `TASK-121` (Task Opportunity Explorer) would likely be a consumer of this, using it to evaluate potential tasks it discovers.

---

## Citations

_No citations provided_
