# Research: Where should we store research findings and theoretical discoveries in this repository? We have:\n- ...

> **Date:** 2026-01-28 07:49:48
> **Source:** gemini
> **Model:** gemini-2.5-flash
> **Checksum:** `sha256:ce572e442cd97059ff1a2f0751d4b5d09d51f418d0e2c55ab22e86384f9f1499`
> **Raw JSON:** `raw/20260128_074948_where_should_we_store_research_findings_and_theore.json`

---

## Query

Where should we store research findings and theoretical discoveries in this repository? We have:\n- EPR entanglement theory for dependencies (validated 78%)\n- API scale-emergence theory (validated 78%)\n- Compositional alignment theory (validated 95%)\n- Dual navigation space theory (validated 75%)\n- Task prioritization principles\n\nWhat's the proper location for: theory additions, research reports, hypothesis validations, and implementation specifications?

---

## Response

Based on the `KERNEL.md`, `SUBSYSTEM_INTEGRATION.md`, and `manifest.yaml` files, here's where research findings, theoretical discoveries, hypothesis validations, and implementation specifications should be stored:

The project utilizes a **Concepts / Objects Duality** pattern, where:
*   **Concepts** (Types, Schemas, Specs, Definitions) live in `docs/` or `schema/` directories.
*   **Objects** (Instances, Records, Data, Implementations) live in `src/`, `registry/`, `runs/` etc.

This pattern applies at every level, meaning that theoretical foundations (`Concepts`) are distinct from their implementations (`Objects`).

---

### 1. Research Findings and Hypothesis Validations

**Location:** `docs/research/`
*   This directory is explicitly identified in `SUBSYSTEM_INTEGRATION.md` as an auto-save target for output from `analyze.py` and is also where Perplexity MCP output is found (`docs/research/perplexity/`). It serves as the general landing zone for raw or processed research output, experimental results, and reports detailing hypothesis validations.
*   **Rationale:** The validated theories (EPR entanglement, API scale-emergence, compositional alignment, dual navigation space) each have a validation percentage. This suggests they are currently "findings" or "reports" of research and experimental validation.

**Recommendation for your specific items:**
*   **EPR entanglement theory for dependencies (validated 78%)**
*   **API scale-emergence theory (validated 78%)**
*   **Compositional alignment theory (validated 95%)**
*   **Dual navigation space theory (validated 75%)**

These should initially be documented as separate files or in a dedicated subdirectory within `docs/research/`. For example:
*   `docs/research/theories/epr_entanglement_report.md`
*   `docs/research/theories/api_scale_emergence_report.md`
*   `docs/research/theories/compositional_alignment_report.md`
*   `docs/research/theories/dual_navigation_space_report.md`

Each document would detail the theory, the methodology of validation, and the confidence score.

---

### 2. Core Theoretical Additions

**Location:**
*   **For theories contributing to the core "Standard Model of Code" (i.e., the "Particle" side, how code itself is understood):**
    *   `particle/docs/`
    *   **Rationale:** `manifest.yaml` defines `particle/docs/` as the `concepts` path for the `body` (Collider engine). `particle/docs/MODEL.md` is a key example of a core theoretical document. If, after rigorous review and higher confidence (e.g., >95% acceptance), these theories are integrated as fundamental contributions to the project's understanding of code, they should be formalized here. You might create a `particle/docs/theories/` subdirectory if there are many.
*   **For theories or conceptual frameworks related to AI tools, context management, or the "Wave" intelligence layer:**
    *   `wave/docs/`
    *   **Rationale:** `manifest.yaml` defines `wave/docs/` as the `concepts` path for the `brain` (AI tools and context management). `wave/docs/HOLOGRAPHIC_SOCRATIC_LAYER.md` is an example of a conceptual framework living here.

**Recommendation:** Given your theories ("dependencies," "API scale-emergence," "compositional alignment," "dual navigation space") seem deeply tied to understanding code structure and its emergent properties, they would likely eventually be formalized within `particle/docs/` if they become part of the core "Standard Model of Code."

---

### 3. Implementation Specifications

**Location:**
*   **For specifications related to the Collider engine or the "Particle" world:**
    *   `particle/docs/specs/`
*   **For specifications related to AI tools, context management, or the "Wave" world:**
    *   `wave/docs/specs/`
*   **For agent-specific specifications (e.g., BARE engine):**
    *   `.agent/specs/`

**Recommendation:** Place implementation specifications in the `docs/specs/` directory of the relevant subsystem they describe.

---

### 4. Task Prioritization Principles

**Location:** `.agent/docs/`
*   **Rationale:** These principles directly pertain to the operation and responsibilities of the AI agents. The `.agent/` directory is dedicated to the Observer layer, including agent schemas, registry, and runs. Operational guidelines for agents naturally fit into `.agent/docs/`.
*   **Recommendation:** A new file like `.agent/docs/TASK_PRIORITIZATION_PRINCIPLES.md` would be appropriate.

---

### Summary of Recommended Locations:

| Document Type                                  | Recommended Path(s)                                   |
| :--------------------------------------------- | :---------------------------------------------------- |
| **Initial Research Findings & Hypothesis Validations** <br> (e.g., your 4 validated theories with scores) | `docs/research/` (e.g., `docs/research/theories/your_theory_report.md`) |
| **Core Theoretical Additions** <br> (fundamental, high-confidence, integrated concepts) | `particle/docs/` (for core code models) <br> `wave/docs/` (for AI/context frameworks) |
| **Implementation Specifications**              | `particle/docs/specs/` <br> `wave/docs/specs/` <br> `.agent/specs/` |
| **Task Prioritization Principles**             | `.agent/docs/` (e.g., `.agent/docs/TASK_PRIORITIZATION_PRINCIPLES.md`) |

---

## Citations

_No citations provided_
