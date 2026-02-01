# Research: Summarize the high-level repository file structure and key subsystems

> **Date:** 2026-01-27 19:33:25
> **Source:** gemini
> **Model:** gemini-2.5-flash
> **Checksum:** `sha256:57a24944527f2c94d3896f24e0fe5401f84923d2765377d2578cf0a600a0eca2`
> **Raw JSON:** `raw/20260127_193325_summarize_the_high_level_repository_file_structure.json`

---

## Query

Summarize the high-level repository file structure and key subsystems

---

## Response

The repository is structured around two primary, high-level subsystems, each residing in its own top-level directory:

### High-Level Repository File Structure

*   **`standard-model-of-code/`**: Contains the core code parsing engine ("Collider"), its associated schemas, and documentation.
*   **`context-management/`**: Houses AI tools, cloud integration, and data logistics components.

### Key Subsystems

1.  **Standard Model of Code (The Body)**
    *   **Purpose:** This is the "Collider engine" responsible for parsing code and identifying its "basic constituents." It acts as the core code analysis component.
    *   **Key Locations:**
        *   `standard-model-of-code/src/core/`: The heart of the Collider engine.
        *   `standard-model-of-code/schema/*.yaml`: Defines the "Atom schemas" or structures for parsed code elements.
        *   `standard-model-of-code/docs/`: Contains "Theory docs" related to the code model.

2.  **Context Management (The Brain)**
    *   **Purpose:** Manages AI capabilities, cloud interactions ("cloud mirror"), and the broader data/context pipeline.
    *   **Key Locations:**
        *   **AI Tools (`context-management/tools/ai/`):** Contains utilities for AI queries and "Socratic Verification" (an "Antimatter Law Check" for detecting documentation/implementation drift).
        *   **Refinery (Logistics) (`context-management/tools/refinery/`):** Handles data ingestion, provenance tracking, and "Physics" within a "Logistics Pipeline." It has its own theoretical documentation (`context-management/intelligence/concepts/THEORY_DATA_LOGISTICS.md`).
        *   **Holographic-Socratic Layer:** An AI-powered guardian (utilizing AI tools from `context-management/tools/ai/` and configurations from `context-management/config/semantic_models.yaml`) that continuously detects drift between documentation and implementation.

In essence, `standard-model-of-code` is the engine that understands the code's structure, while `context-management` leverages AI to derive insights, manage data flow, and ensure consistency across the project.

---

## Citations

_No citations provided_
