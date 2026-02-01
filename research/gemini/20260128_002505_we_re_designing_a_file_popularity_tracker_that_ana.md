# Research: We're designing a File Popularity Tracker that analyzes file modification history to identify:
- Dea...

> **Date:** 2026-01-28 00:25:05
> **Source:** gemini
> **Model:** gemini-2.0-flash-001
> **Checksum:** `sha256:7be3c64657acab7a3b913ef2efd8b4c6149a66956972205f88ff0af236d4641c`
> **Raw JSON:** `raw/20260128_002505_we_re_designing_a_file_popularity_tracker_that_ana.json`

---

## Query

We're designing a File Popularity Tracker that analyzes file modification history to identify:
- Dead files (created but never modified)
- Popular files (frequently modified)
- Session patterns
- Temporal intelligence for the repo

This data will be used by the Refinery pipeline to enhance chunk relevance scoring.

ARCHITECTURAL QUESTION:
Should this be:
A) A stage INSIDE the Refinery pipeline (Stage 5.5: Temporal Enrichment)?
B) A separate subsystem (S15: Temporal Intelligence) that FEEDS Refinery?
C) Part of OBSERVER subsystem (monitoring/governance)?

Consider:
1. Separation of concerns
2. Reusability (multiple consumers: Refinery, analyze.py, archive tools)
3. Pipeline complexity
4. Existing patterns in our codebase

Which architecture is most aligned with our current system design?

---

## Response

Based on the comprehensive codebase context, the most aligned architecture for the File Popularity Tracker is **(B) a separate subsystem (S15: Temporal Intelligence) that FEEDS Refinery.**

Here's a breakdown of the reasoning, considering the core principles and existing architecture:

*   **Separation of Concerns:** Keeping it separate maintains the separation of concerns between the core REFINERY which focuses on mapping, atomizing, and indexing the code, and the new subsystem which focuses on file activity/versioning.

*   **Reusability:** The core files in the ACI (analyze.py) are designed to be re-usable with multiple systems, which is best achieved by an external data source. A new subsystem would be consumed by the Refinery, analyze.py, and archive tools.

*   **Pipeline Complexity:** The existing pipeline is becoming bloated. By keeping this out of the core, we reduce the load on the main pipeline.

*   **Existing Patterns:** The project already favors a push-based model (the BARE engine). The new subsystem could push updates to the Refinery cache.

Therefore: Create a separate subsystem seems to be the best choice. This can be validated using a [Decision Deck](.agent/specs/DECISION_DECK_LAYER.md) that contains the following cards:
- CARD_INF_001: Consolidate 2026-01-27 with Refinements
- CARD_TST_003: Establish 2026-01-27 with Testing

The implementation would follow the following procedure:
*   Create a new subsystem (S15) in context-management/tools/file_popularity/
*   Define the interface (inputs/outputs) of the subsystem
*   Implement the logic to analyze file modification history and generate insights.
*   Implement the mechanism to trigger the data flow from the new subsystem to the Refinery.

This plan would support the overall project vision and ensure that the new component has a clear role and a defined purpose.


---

## Citations

_No citations provided_
