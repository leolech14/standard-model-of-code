# Research: Audit the refinery subsystem: check wave/tools/refinery/ for broken imports, missing i...

> **Date:** 2026-01-31 06:23:49
> **Source:** gemini
> **Model:** gemini-2.5-flash
> **Checksum:** `sha256:c1cad3e220561361753b83ccd888314ff59108869dc9696ffd680e1baa4ab78c`
> **Raw JSON:** `raw/20260131_062349_audit_the_refinery_subsystem__check_context_manage.json`

---

## Query

Audit the refinery subsystem: check wave/tools/refinery/ for broken imports, missing integrations, incomplete implementations, dead code. What is architecturally wrong?

---

## Response

The `refinery` subsystem, particularly focusing on the `wave/tools/refinery/` directory, exhibits several critical architectural and implementation issues. While some core "refinery pipeline" logic is documented in `wave/tools/ai/aci/refinery.py`, the `tools/refinery` directory contains fragmented, incomplete, and deprecated components that significantly hinder the system's intended functionality and overall architectural coherence.

Here's an audit of the `refinery` subsystem:

### 1. Broken Imports, Missing Integrations & Consolidations

*   **Missing Semantic Bridge (Critical Integration Failure)**: The most severe architectural flaw is the **bypassing of the "Attention Mechanism"** designed for "Laminar vs. Turbulent Flow." The logic in `aci/semantic_finder.py:287` is intended to filter data blobs (preventing "Contextome Pollution"), but it is explicitly noted as *not being called* by `analyze.py` or the `refinery.py` in `aci`. This leads to low-signal noise in LLM context windows and `D4_BOUNDARY Violations` according to `DEEP_TRUTH_AUDIT_REPORT.md`.
    *   **Source**: `DEEP_TRUTH_AUDIT_REPORT.md` ("The Attention Mechanism Failure")
*   **Missing Indexer Integration**: The `querier` (`query_chunks.py`) and `reference_analyzer` explicitly declare `indexer` as a dependency. Since `indexer.py` is currently `missing`, any semantic search or detailed reference analysis functionality is implicitly broken or severely limited, relying on brute-force methods.
    *   **Source**: `wave/config/registries/REFINERY_INTERNAL.yaml` (`querier`, `reference_analyzer` dependencies)
*   **Fragmented Scanner Integration**: The `scanner` subsystem is explicitly noted as "Currently split across 3 files (`corpus_inventory`, `boundary_mapper`, `delta_detector`)" and requires consolidation.
    *   **Source**: `wave/config/registries/REFINERY_INTERNAL.yaml` (`scanner` issues)
*   **Synthesizer Integration Gap**: The `synthesizer`'s issues mention it "Should absorb `atom_generator.py` (currently separate)," indicating a missing integration.
    *   **Source**: `wave/config/registries/REFINERY_INTERNAL.yaml` (`synthesizer` issues)

### 2. Incomplete Implementations

*   **Missing Indexer Subsystem**: The `indexer` (`wave/tools/refinery/indexer.py`) is entirely `missing` and has `0 lines_of_code`. Its absence is a fundamental blocker, forcing inefficient brute-force search through JSON files for `querier` operations.
    *   **Source**: `wave/config/registries/REFINERY_INTERNAL.yaml` (`indexer` status and issues), `DEEP_TRUTH_AUDIT_REPORT.md` ("Missing Indexer")
*   **Partial Querier Functionality**: The `querier` (`query_chunks.py`) is marked as `partial` because "semantic search not implemented" due to the missing `indexer`.
    *   **Source**: `wave/config/registries/REFINERY_INTERNAL.yaml` (`querier` status and issues)
*   **Incomplete Reference Analyzer**: The `reference_analyzer` is `partial`, with "Holon extraction not yet implemented" and "56/65 refs still need LLM analysis." It also depends on the missing `indexer`.
    *   **Source**: `wave/config/registries/REFINERY_INTERNAL.yaml` (`reference_analyzer` status and issues)
*   **Partial Scanner Implementation**: The `scanner` subsystem is `partial` and fragmented, needing further development to unify its components.
    *   **Source**: `wave/config/registries/REFINERY_INTERNAL.yaml` (`scanner` status)

### 3. Dead Code / Redundant Components

*   **Deprecated Scanner Sub-modules**: `boundary_mapper.py` and `delta_detector.py` are explicitly listed as `deprecated_subsystems` with the reason "Should merge into scanner.py." These are effectively redundant or dead as standalone modules and should be absorbed.
    *   **Source**: `wave/config/registries/REFINERY_INTERNAL.yaml` (`deprecated_subsystems`)
*   **Deprecated Atom Generator**: `atom_generator.py` is also listed as `deprecated_subsystems` because it is "Redundant - atoms are just boundary aggregations," indicating its functionality is no longer needed as a separate component.
    *   **Source**: `wave/config/registries/REFINERY_INTERNAL.yaml` (`deprecated_subsystems`)

### 4. What is Architecturally Wrong?

The architectural problems stem from a combination of incomplete implementation, fragmentation, and a critical disconnect between theoretical design and practical execution:

1.  **Fundamental "Attention Mechanism" Disconnect**: The *most critical* architectural failure is the **non-integration of the semantic filtering mechanism (`aci/semantic_finder.py`) into the `Refinery`'s data processing**. This directly violates the core principles of Adaptive Context Intelligence (ACI) by allowing "Turbulent Flow" (low-quality, noisy data) to pollute the contextome, degrading AI reasoning. This is a severe conceptual-to-implementation gap.
    *   **Source**: `DEEP_TRUTH_AUDIT_REPORT.md` (Executive Summary, "The Attention Mechanism Failure")
2.  **Missing Central Indexing Layer**: The complete absence of the `indexer` indicates a significant architectural gap. An effective content-management system relies on robust indexing for fast, semantic retrieval, which is currently non-existent, forcing inefficient workarounds.
    *   **Source**: `wave/config/registries/REFINERY_INTERNAL.yaml` (`indexer` status), `DEEP_TRUTH_AUDIT_REPORT.md` ("Implement Indexer")
3.  **Lack of Cohesion and Fragmentation**: The `scanner` and `synthesizer` subsystems within `tools/refinery/` are fragmented into multiple modules (`boundary_mapper`, `delta_detector`, `atom_generator`) that are explicitly identified as needing consolidation. This indicates poor design cohesion and a lack of refactoring to align with a unified architectural vision.
    *   **Source**: `wave/config/registries/REFINERY_INTERNAL.yaml` (`scanner` and `synthesizer` issues, `deprecated_subsystems`)
4.  **Inconsistent Localization of "Refinery" Logic**: The user's query focuses on `wave/tools/refinery/`. However, core `Refinery` pipeline components (like chunking and relevance scoring) are documented to reside in `wave/tools/ai/aci/refinery.py`. This split could lead to confusion about where the "Refinery" architecture truly resides and which team/module is responsible for its central evolution. The `tools/refinery/` directory appears to house support components that are themselves in a state of disrepair.
    *   **Source**: `wave/config/registries/DOMAINS.yaml` (`Refinery_Pipeline` codome path), `wave/docs/ACI_DATASET_MANAGEMENT.md` (Refinery tool path)

In summary, the `refinery` subsystem, particularly `wave/tools/refinery/`, suffers from critical missing core components (`indexer`), significant fragmentation (`scanner`, `synthesizer`), and a fundamental architectural oversight in connecting its data processing to the semantic filtering mechanism. These issues directly undermine the goal of adaptive context intelligence and efficient knowledge retrieval.

---

## Citations

_No citations provided_
