# Research: What are the core principles, best practices, and architectural patterns of this repository? How doe...

> **Date:** 2026-01-31 05:58:37
> **Source:** gemini
> **Model:** gemini-2.5-flash
> **Checksum:** `sha256:28254978d6396cc4b0af00d86f20a70be1934bed2ab0d7c8052da692286b8bce`
> **Raw JSON:** `raw/20260131_055837_what_are_the_core_principles__best_practices__and.json`

---

## Query

What are the core principles, best practices, and architectural patterns of this repository? How does the codebase structure relate to the Standard Model of Code theory? What naming conventions, organizational rules, and design decisions should I follow when making changes? Give me the essential knowledge to work correctly in this codebase.

---

## Response

Based on the provided codebase context, here is an essential overview of the core principles, best practices, architectural patterns, codebase structure, naming conventions, organizational rules, and design decisions for the `PROJECT_elements` repository.

### Project Identity and Mission

*   **Project:** `PROJECT_elements`
*   **Core Product:** Standard Model of Code + Collider
*   **Mission:** Find the basic constituents of computer programs.
*   **Owner:** Leonardo Lech
*   **Overall Goal:** To enable AI agents to perform semantic code analysis, refinement, and task management effectively and reliably.

---

### Core Principles

1.  **Git is Truth:** All project state resides in files within the Git repository. Commits are the atomic transactions that represent changes and progress. There is no external database or hidden state.
2.  **Log Before Doing:** Announce your intent (e.g., in a RUN record step log) *before* executing an action. This provides transparency and traceability.
3.  **Handoff Explicitly:** Any agent ending a session must leave a clear `handoff.summary`, `handoff.next_steps`, and `handoff.artifacts` in the RUN record. The next agent should be able to pick up work without extensive code review.
4.  **Conservative Confidence:** When uncertain about any aspect (factual, alignment, current, onwards), score confidence lower. This prioritizes caution and re-evaluation.
5.  **Macro System Philosophy:** "If you do it twice manually, record it as a macro." This promotes automation and repeatable processes.
6.  **Atomic Reservation:** Tasks must be explicitly claimed using `claim_task.sh` before work begins to prevent multi-agent race conditions. The `claimed/` directory is the single source of truth for active claims.

---

### Architectural Patterns & Codebase Structure

The project employs a "fractal duality pattern" known as **Particle/Wave Architecture**, where every level consists of **Concepts** (Types, Schemas, Specs) and **Objects** (Instances, Records, Data, Implementations).

1.  **Concepts / Objects Duality:**
    *   **Concepts:** Documentation, schemas, specs (`task.schema.yaml`, `MODEL.md`).
    *   **Objects:** Implementations, actual data instances (`TASK-001.yaml`, source code).

2.  **Particle/Wave Architecture Mapping:**
    *   `particle/` (The "Body"): **PARTICLE** (measurement, collapse)
        *   Contains the `Collider` engine, which performs semantic code analysis (ground truth). This is where the code itself and its immediate analysis live.
        *   Concepts: `particle/docs/specs/`
        *   Objects: `particle/src/`
    *   `wave/` (The "Brain"): **WAVE** (potential, field)
        *   Contains AI tools, context management, and the `Intelligence Layer` (e.g., `analyze.py`, HSL, Perplexity MCP). This is where the broader intelligence, context, and potential actions are managed.
        *   Concepts: `wave/docs/`
        *   Objects: `wave/tools/`
    *   `.agent/` (The "Observer"): Decides what to measure and orchestrates work.
        *   Contains agent-specific schemas (`task.schema`, `run.schema`), task registry, and run history.
        *   Concepts: `.agent/schema/`
        *   Objects: `.agent/registry/`, `.agent/runs/`

3.  **Task / Run Separation:**
    *   **TASK:** Strategic, persistent work item (e.g., `registry/active/TASK-XXX.yaml`). Describes *what* should be true.
    *   **RUN:** Tactical, per-session attempt to advance a task (e.g., `runs/RUN-{timestamp}-{agent}.yaml`). Documents *what happened* in one session.

4.  **Subsystem Integration:** The `SUBSYSTEM_INTEGRATION.md` provides a canonical map of how various components like Collider (S1), HSL (S2), analyze.py (S3), Task Registry (S5), BARE (S6), and others connect. This diagram is critical for understanding data flow and dependencies.

---

### Best Practices for AI Agent Interaction & Context Engineering

These principles are designed to mitigate LLM limitations, especially the "Lost-in-the-Middle" effect:

1.  **Sandwich Method:** Position critical instructions at the **beginning** and **end** of the context window, with supporting context in the middle.
2.  **Token Budget Discipline:**
    *   Prioritize `Guru` (<50k tokens) for focused analysis.
    *   Avoid `Perilous` (>200k tokens) contexts, as lost-in-middle effects dominate.
    *   Treat tokens as a budget with ROI: if it doesn't change the decision, remove it.
3.  **Token Quality > Quantity:**
    *   **High-value tokens:** Directly relevant facts, canonical excerpts, disambiguating identifiers, clean structure.
    *   **Negative-value tokens (remove):** Irrelevant background, redundant paraphrases, contradictory instructions, confusable near-misses, unfiltered logs.
4.  **Post-Compaction Rule:** After any context restore, **NEVER trust in-memory task state.** Always perform a live filesystem check via `claim_task.sh` as `claimed/` is the single source of truth.

---

### Workflow, State Management & Agent Responsibilities

1.  **Boot Protocol (Mandatory Steps):**
    1.  READ `KERNEL.md`
    2.  RUN `.agent/tools/check_stale.sh` (Release abandoned claims)
    3.  CHECK `git status` (Detect interrupted sessions)
    4.  READ `manifest.yaml` (Discovery pointers)
    5.  CHECK `registry/INDEX.md` (Active tasks)
    6.  **CLAIM task BEFORE starting work** (`.agent/tools/claim_task.sh`)
    7.  FIND or CREATE a `RUN` record in `runs/`
    8.  BEGIN work, logging steps to your `RUN` record

2.  **Task State Machine:**
    *   `DISCOVERY`: Opportunity identified, needs scoping (Cannot Claim)
    *   `READY`: Scoped and claimable (Can Claim)
    *   `EXECUTING`: Work in progress (has active RUN) (Cannot Claim)
    *   `COMPLETE`: Work done, verified, merged (Cannot Claim)
    *   `ARCHIVED`: Closed (success or abandoned) (Cannot Claim)
    *   *Simplification:* SCOPED+PLANNED merged into READY; VALIDATING absorbed into EXECUTING; no RETRY state (if failed, returns to READY).

3.  **Agent Session Lifecycle:**
    *   **Starting:**
        1.  Check `registry/INDEX.md` for highest-priority task.
        2.  Create `RUN-YYYYMMDD-HHMMSS-{agent}.yaml` in `runs/`.
        3.  Set `RUN` status to `STARTED`.
        4.  Read task context and previous RUNs.
    *   **During Work:**
        1.  Update `RUN` status to `IN_PROGRESS`.
        2.  Log each step in `progress.step_log`.
        3.  Create/modify files.
        4.  Commit atomically when reaching stable states.
    *   **Ending:**
        1.  Update `RUN` with `handoff.summary`, `handoff.next_steps`, `handoff.artifacts`.
        2.  Set `RUN` status to `DONE`, `HANDOFF_READY`, or `ABANDONED`.
        3.  Update task confidence if changed.
        4.  Commit all changes.

4.  **4D Confidence Model (for Tasks):** Tasks are scored on four dimensions, with `Overall = min(factual, alignment, current, onwards)`.
    *   **Factual:** Is my understanding of current state correct?
    *   **Alignment:** Does this serve the project's mission?
    *   **Current:** Does this fit codebase as it exists?
    *   **Onwards:** Does this fit where we're heading?
    *   **Verdicts:** ACCEPT (>=75%), DEFER (50-74%), REJECT (<50%).

---

### Naming Conventions, Organizational Rules & Design Decisions

1.  **Naming Conventions:**
    *   **Task IDs:** `TASK-XXX` (e.g., `TASK-001`). Must match regex `^TASK-[0-9]{3}$`.
    *   **Run IDs:** `RUN-YYYYMMDD-HHMMSS-{agent}` (e.g., `RUN-20260124-123045-claude`). Must match regex `^RUN-[0-9]{8}-[0-9]{6}-[a-z]+$`.
    *   **Conventional Commits (Non-Negotiable):** All commits must follow `<type>(<scope>): <subject>` format.
        *   **Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.
        *   **Scopes:** `collider`, `viz`, `agent`, `aci`, `hsl`, `refinery`, `archive` (optional but recommended).
        *   **Enforcement:** `.pre-commit-config.yaml` and `commitlint.config.js`.

2.  **Organizational Rules:**
    *   **`manifest.yaml`:** Machine-readable discovery file for project ID, agent system schemas/instances, project structure, integrations, and agent capabilities.
    *   **`KERNEL.md`:** The primary bootstrap context for all agents. Read this first.
    *   **`SUBSYSTEM_INTEGRATION.md`:** Canonical reference for how subsystems connect.
    *   **Integration Checklist:** When adding a new subsystem, ensure it's added to the registry, data flow is documented, cross-referenced, diagram updated, and integration tests are added.
    *   **Directory Structure:** Adhere to the Concepts/Objects duality for all new modules/features.
        *   `docs/` for concepts (schemas, specs).
        *   `src/` or `tools/` for objects (implementations, data).

3.  **Design Decisions:**
    *   **Task Registry Format:** Currently uses human-readable Markdown, but a migration path to structured YAML is proposed for machine readability and automation. BARE will eventually read from YAML.
    *   **HSL vs. `analyze.py --verify`:** This is a deliberate **Concept/Implementation** pair. HSL is the "what" and "why" (conceptual framework), while `analyze.py --verify` is the "how" (execution engine). They are not redundant but complementary.
    *   **Modularity:** The system is composed of many interacting subsystems (Collider, HSL, BARE, Task Registry, etc.) with explicit integration points and documented data flow.

---

By adhering to these principles, practices, and architectural guidelines, you will ensure your contributions are consistent, auditable, and easily integrated into the existing `PROJECT_elements` codebase. Always consult `KERNEL.md` first for the latest boot protocol and non-negotiables.

---

## Citations

_No citations provided_
