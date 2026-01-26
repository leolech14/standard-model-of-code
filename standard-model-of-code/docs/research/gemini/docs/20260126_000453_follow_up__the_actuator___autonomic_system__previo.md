# Research: FOLLOW-UP: THE ACTUATOR / AUTONOMIC SYSTEM

Previous analysis concluded our automation system is:
- ...

> **Date:** 2026-01-26 00:04:53
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:1fc062370df4486d5589c4a2b0eaab7effb234969c258605318fb923e5279869`
> **Raw JSON:** `raw/20260126_000453_follow_up__the_actuator___autonomic_system__previo.json`

---

## Query

FOLLOW-UP: THE ACTUATOR / AUTONOMIC SYSTEM

Previous analysis concluded our automation system is:
- Ontological category: Homeostatic Regulator / Control Plane
- Location: Observer Realm (.agent/)
- Nature: Teleological execution (syntax realizing semantics)
- Name candidates: The Actuator, The Autonomic System, The Hamiltonian

NEW QUESTIONS about architecture:

1. DISTRIBUTED vs UNIFIED
   Currently scattered across:
   - .agent/tools/autopilot.py (orchestrator)
   - .agent/tools/trigger_engine.py (macro execution)
   - .agent/tools/enrichment_orchestrator.py (opportunity processing)
   - context-management/tools/maintenance/tdj.py (sensing)
   - context-management/tools/drift_guard.py (drift detection)
   - context-management/tools/ai/ (AI analysis tools)
   - context-management/tools/hsl_daemon.py (semantic validation)

   Should these be unified under a single directory? Or is the distribution intentional/correct?

2. NAMING THE DIRECTORY
   If we create a dedicated home, what should it be called?
   - .agent/actuator/
   - .agent/autonomic/
   - .agent/daemon/
   - .agent/homeostasis/
   - Keep distributed (current state)

3. RUNTIME QUESTION
   These processes can run as:
   - Post-commit hooks (synchronous, blocking)
   - Background daemons (async, polling)
   - Scheduled jobs (cron/Cloud Run)
   - Event-driven (file watchers, webhooks)

   Is 'Actuator' the right name for something that spans multiple runtimes?
   Or should we distinguish between the CONCEPT (Actuator) and the IMPLEMENTATION (distributed agents)?

4. RELATIONSHIP TO EXISTING CONCEPTS
   - How does this relate to BARE (Background Auto-Refinement Engine)?
   - Is BARE a subset of The Actuator, or a peer?
   - What about the upcoming AEP (Autonomous Enrichment Pipeline)?

Please provide architectural guidance that maintains coherence with our existing naming (Collider, Atoms, Wave/Particle/Observer).

---

## Response

This is a foundational architectural decision. You are defining the **Cybernetics of the Projectome**—how the system governs itself.

Based on the `CODESPACE_ALGEBRA.md` and the existing "Physics" metaphor, here is the architectural guidance.

---

### 1. The Core Concept: The Hamiltonian Operator

In quantum mechanics, the **Hamiltonian ($\hat{H}$)** is the operator corresponding to the total energy of the system, and it governs how the system evolves over time (the Schrödinger equation).

In **PROJECT_elements**, this automation layer is not just a "toolset." It is the **Time-Evolution Operator**. It moves the repository from State $t$ to State $t+1$.

**Recommendation:**
The conceptual name for the *entire system* is **The Autonomic System** (biological) or **The Hamiltonian** (physical).
The *directory implementation* should be **`.agent/machinery/`**.

---

### 2. Decision: Unified vs. Distributed

**Verdict: CENTRALIZED CONTROL, DISTRIBUTED PHYSICS.**

You must distinguish between the **Controller** (Observer Realm) and the **Capability** (Wave/Particle Realms).

*   **The Brain (Wave Realm)**: `context-management/tools/ai/`
    *   *Role:* Pure intelligence. Answering questions. Planning.
    *   *Status:* Keep here. The Actuator *calls* this, but this is not the Actuator.
*   **The Body (Particle Realm)**: `standard-model-of-code/src/core/`
    *   *Role:* Parsing, measuring, graphing.
    *   *Status:* Keep here. The Actuator *uses* this to see.
*   **The Hand (Observer Realm)**: **MOVE HERE.**
    *   *Role:* Taking action. Modifying files. Committing. Managing state.
    *   *Migration:* `drift_guard.py`, `autopilot.py`, `tdj.py`, and `enrichment_orchestrator.py` should all move to the Observer realm.

**Why?**
The Observer is the only realm authorized to *collapse the wave function* (make a decision/change). If `context-management` scripts start modifying the repo autonomously, you have violated the separation of concerns.

---

### 3. Directory Structure Proposal

Create a dedicated home in `.agent/` that reflects the **Control Loop** (Sense → Decide → Act).

**Proposed Structure:**

```
.agent/
├── registry/               # (Memory) Tasks, Sprints
├── machinery/              # (The Autonomic System)
│   ├── sensors/            # INPUT: drift_guard, tdj (Technical Debt Judge)
│   ├── actuators/          # OUTPUT: autopilot, claim_task, commit_work
│   └── workflows/          # LOGIC: BARE, AEP, enrichment_orchestrator
└── triggers/               # (The Nervous System)
    ├── hooks/              # Git hooks (synchronous)
    ├── daemons/            # LaunchAgents/Cron (async)
    └── events/             # Webhooks/FileWatchers
```

**Migration Map:**

| Current File | New Location | Component Type |
| :--- | :--- | :--- |
| `context-management/tools/drift_guard.py` | `.agent/machinery/sensors/drift_guard.py` | **Sensor** (Detects $\Delta$) |
| `context-management/tools/maintenance/tdj.py` | `.agent/machinery/sensors/tdj.py` | **Sensor** (Measures Quality) |
| `.agent/tools/autopilot.py` | `.agent/machinery/actuators/autopilot.py` | **Actuator** (Executes Change) |
| `.agent/tools/enrichment_orchestrator.py` | `.agent/machinery/workflows/aep.py` | **Workflow** (Orchestrates) |
| `context-management/tools/hsl_daemon.py` | `.agent/machinery/workflows/hsl.py` | **Workflow** (Validates) |

---

### 4. Relationship to BARE and AEP

This solves the confusion between "Engine" vs "Tool".

*   **BARE** (Background Auto-Refinement Engine) is a **Workflow**.
    *   It is a specific *policy* that uses Sensors (TruthValidator) and Actuators (GitCommit) to refine the repo.
*   **AEP** (Autonomous Enrichment Pipeline) is a **Workflow**.
    *   It uses Sensors (ComplexityAnalyzer) and Actuators (TaskPromoter) to mature tasks.

**The Hierarchy:**

1.  **The Autonomic System** (`.agent/machinery/`)
    *   The container for all automated evolution.
2.  **Workflows** (The "Engines")
    *   high-level logic scripts (BARE, AEP, HSL).
    *   They typically run in loops or sequences.
3.  **Actuators & Sensors** (The "Organs")
    *   Atomic capabilities used by the Workflows.

---

### 5. Runtime Architecture (The "Triggers")

You asked if "Actuator" is the right name for something that spans runtimes.
**Answer:** The Actuator is the code *being run*. The Trigger is *how it runs*.

**The decoupling rule:**
An Actuator (e.g., `clean_logs.py`) should not know if it is running inside a Cron job, a Git Hook, or a Cloud Run container.

**Directory: `.agent/triggers/`**
This directory contains the *wrappers* that invoke the Machinery.

*   `.agent/triggers/post-commit` -> calls `machinery/workflows/bare.py --quick`
*   `.agent/triggers/daily_cron` -> calls `machinery/workflows/hsl.py --full`
*   `.agent/triggers/cloud_entrypoint.sh` -> calls `machinery/workflows/aep.py`

---

### Summary of Recommendations

1.  **Move** all sensing, guarding, and acting scripts into `.agent/`.
2.  **Rename** the container to **`.agent/machinery/`** (to represent the physics of the Hamiltonian).
3.  **Structure** internal folders as `sensors/`, `actuators/`, and `workflows/`.
4.  **Define BARE and AEP** as **Workflows** that orchestrate sensors and actuators.
5.  **Isolate Runtimes** into `.agent/triggers/` to keep the logic pure.

This aligns perfectly with the **Observer Realm** definition: *The Observer decides what to measure and how to interact with the system.*

---

## Citations

_No citations provided_
