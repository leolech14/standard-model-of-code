# Research: Describe the main pipeline stages

> **Date:** 2026-01-30 02:44:58
> **Source:** gemini
> **Model:** gemini-2.5-flash
> **Checksum:** `sha256:2cdec59f6cfabbec4d5502da21bd761d54e68ac88341210f4472b2ff12cc1a88`
> **Raw JSON:** `raw/20260130_024458_describe_the_main_pipeline_stages.json`

---

## Query

Describe the main pipeline stages

---

## Response

The `standard-model-of-code/src/core/full_analysis.py` script orchestrates a comprehensive, multi-stage analysis pipeline for a given codebase. It processes source code through various theoretical frameworks and analytical modules to produce a rich, multi-dimensional graph model.

The main pipeline stages, as observed in the `run_full_analysis` function, are:

1.  **Stage 0: Survey (Pre-Analysis Intelligence)**
    *   **Purpose:** Initial scan of the codebase to gather high-level statistics and identify paths to exclude (e.g., vendor directories, minified files) to optimize subsequent analysis stages.
    *   **Key actions:** File scanning, identification of vendor/generated code, estimation of nodes.

2.  **Stage 1: Base Analysis**
    *   **Purpose:** The foundational step that uses the `unified_analysis.py` module to parse the codebase (files, directories) via a Tree-Sitter engine. It extracts raw code elements (functions, classes, variables) as "particles" and initial relationships.
    *   **Key actions:** AST parsing for multiple languages, initial particle (node) and basic edge extraction, raw import data collection, initial statistics generation. This stage also emits "file nodes" to represent each analyzed file as a node in the graph.

3.  **Stages 2 - 2.11: Standard Model & Deep Code Enrichment**
    *   This is a cluster of highly specialized stages that apply various Standard Model of Code theories and deep static analysis techniques to enrich the initially extracted particles with detailed metadata, classifications, and metrics.
        *   **Stage 2: Standard Model Enrichment:** Applies the core Standard Model, assigning RPBL (Responsibility, Purity, Boundary, Lifecycle) scores and flattening them for further binding. It also validates canonical roles.
        *   **Stage 2.5: Ecosystem Discovery:** Identifies unknown ecosystem patterns, attempting to classify components related to specific frameworks or platforms.
        *   **Stage 2.6: Holarchy Level Classification:** Assigns "holarchy levels" (e.g., L3..L12) to nodes and infers package levels, classifying their position in a hierarchical structure.
        *   **Stage 2.7: Octahedral Dimension Classification:** Assigns coordinates across 8 "octahedral dimensions" (e.g., D4, D5, D7), providing a multi-faceted classification of nodes.
        *   **Stage 2.8: Scope Analysis:** Analyzes code scopes to detect unused definitions and shadowed variables within files.
        *   **Stage 2.9: Control Flow Metrics:** Computes cyclomatic complexity, nesting depth, and other control flow characteristics for code elements.
        *   **Stage 2.10: Pattern-Based Atom Detection:** Uses pre-defined code patterns to identify "atoms" (fundamental units of behavior) within functions and classes.
        *   **Stage 2.11: Data Flow Analysis (D6:EFFECT):** Analyzes data flow to determine the "purity" of functions and identify side effects, contributing to the D6:EFFECT dimension.

4.  **Stages 3 - 3.7: Purpose Emergence & Coherence**
    *   These stages focus on inferring the "purpose" of code elements and assessing the coherence of those purposes.
        *   **Stage 3: Purpose Field:** Detects the overall purpose field, identifying "purpose nodes" and violations of purpose coherence.
        *   **Stage 3.5: Organelle Purpose (π₃):** Computes the "organelle purpose" for containers (e.g., classes), inferring their collective role from their children.
        *   **Stage 3.6: System Purpose (π₄):** Computes the "system purpose" for files, inferring their overall role within the codebase.
        *   **Stage 3.7: Purpose Coherence Metrics:** Enriches nodes with metrics like coherence scores, purpose entropy, and identifies "god classes" based on purpose analysis.

5.  **Stage 4: Execution Flow**
    *   **Purpose:** Analyzes the potential execution paths within the codebase.
    *   **Key actions:** Detects entry points (e.g., `main`, CLI commands), identifies truly unreachable "orphan" code, and calculates dead code percentage.

6.  **Stage 5: Markov Transition Matrix**
    *   **Purpose:** Computes the probability of transitioning between code elements, useful for understanding control flow and identifying heavily traversed paths.
    *   **Key actions:** Calculates transition probabilities between callers and callees, enriches edges with `markov_weight`.

7.  **Stage 6: Knot/Cycle Detection**
    *   **Purpose:** Identifies structural problems in the dependency graph, such as cycles (A -> B -> C -> A) and bidirectional edges (tangles).
    *   **Key actions:** Finds strongly connected components, lists bidirectional edges, and calculates a "knot score."

8.  **Stages 6.5 - 6.8: Graph & Semantic Analytics**
    *   A group of stages for in-depth graph theory and semantic interpretation.
        *   **Stage 6.5: Graph Analytics:** Computes fundamental graph metrics like in-degree, out-degree, centrality (betweenness, pagerank), and classifies topological roles (orphan, root, leaf, hub). It also computes π₂ (Molecular Purpose).
        *   **Stage 6.6: Statistical Metrics:** Applies general software metrics such as Halstead complexity measures, entropy, and calculates estimated bugs.
        *   **Stage 6.7: Semantic Purpose Analysis:** Builds a NetworkX graph, finds entry points, propagates context downstream, and computes closeness centrality. It also identifies critical nodes (bridges, influential) and builds intent profiles (docstrings, commit history).
        *   **Stage 6.8: Codome Boundary Generation:** Creates synthetic "codome boundary" nodes (e.g., for test frameworks, external APIs) and infers edges to disconnected code elements, preventing misclassification as dead code.

9.  **Stage 7: Data Flow Analysis**
    *   **Purpose:** Analyzes how data flows through the system.
    *   **Key actions:** Identifies "data sources" (high out-degree, low in-degree) and "data sinks" (high in-degree, low out-degree).

10. **Stages 8 - 11: Advanced Evaluation & Intelligence**
    *   These stages apply higher-level reasoning and evaluation frameworks.
        *   **Stage 8: Performance Prediction:** Analyzes the graph for potential performance bottlenecks based on execution flow.
        *   **Stage 8.5: Constraint Field Validation:** Validates the codebase against a "Constraint Field," identifying "antimatter" (severe violations), policy violations, and architectural signals. It also attempts architecture detection (e.g., layered).
        *   **Stage 8.6: Purpose Intelligence (Q-Scores):** Computes a "Codebase Intelligence" score (Q-score) and provides an interpretation of the codebase's health based on purpose.
        *   **Stage 9: Roadmap Evaluation:** If a roadmap is provided, evaluates the codebase's readiness against it.
        *   **Stage 10: Visual Topology Analysis:** Classifies the overall architectural "shape" or topology of the codebase (e.g., monolithic, microservices).
        *   **Stage 11: Semantic Cortex (Concept Extraction):** Extracts key domain concepts and infers the overall domain of the codebase.

11. **Stage 11b: AI Insights Generation (Optional)**
    *   **Purpose:** Leverages external AI models (e.g., Vertex AI Gemini) to generate high-level insights about the codebase.
    *   **Key actions:** Formats the analysis output into a prompt and calls an external AI tool to get summarized insights.

12. **Stage 11.5: Manifest Writer (Provenance & Integrity)**
    *   **Purpose:** Ensures cryptographic integrity and provenance for the analysis output.
    *   **Key actions:** Calculates a Merkle root for all nodes, generates a refinery signature, and creates a detailed manifest including input, pipeline, and environment information. It also attaches "waybills" to individual nodes for traceability.

13. **Stage 13: Information Graph Theory (IGT) Metrics**
    *   **Purpose:** Applies advanced information theory concepts to evaluate codebase properties.
    *   **Key actions:** Analyzes directory stability, classifies the severity of "orphan" nodes (true dead code vs. framework entry points), and provides overall stability and orphan metrics.

14. **File Index Building** (implicit stage before output generation)
    *   **Purpose:** Creates a file-centric view of the codebase, linking atoms back to their source files for easier navigation and reporting.
    *   **Key actions:** Groups nodes by file, computes internal/external edge counts per file, and infers file purpose.

15. **Stage 12: Generating Consolidated Outputs**
    *   **Purpose:** Final output generation in two primary formats.
    *   **Key actions:** Creates a machine-readable, LLM-oriented JSON knowledge bundle (`output_llm-oriented_*.json`) and a human-readable HTML report with interactive visualizations (`output_human-readable_*.html`). It embeds a "brain download" (summary markdown) into the HTML.

This elaborate pipeline ensures a deep, multi-faceted understanding of the codebase, from low-level code elements to high-level architectural patterns and semantic insights.

---

## Citations

_No citations provided_
