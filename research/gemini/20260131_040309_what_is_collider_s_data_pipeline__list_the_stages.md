# Research: What is Collider's data pipeline? List the stages and intermediate data structures.

> **Date:** 2026-01-31 04:03:09
> **Source:** gemini
> **Model:** gemini-2.5-flash
> **Checksum:** `sha256:0d8b28af25b9c710ab7ef4b9af1bc97e1d8ca494fa880935c96f133eaf8e13b0`
> **Raw JSON:** `raw/20260131_040309_what_is_collider_s_data_pipeline__list_the_stages.json`

---

## Query

What is Collider's data pipeline? List the stages and intermediate data structures.

---

## Response

Collider's data pipeline, as orchestrated by the `run_full_analysis` function in `full_analysis.py`, is a comprehensive multi-stage process designed to deeply analyze a codebase and produce a rich, multi-faceted graph representation. It involves several theoretical frameworks, heuristic detections, and advanced graph analytics.

The core intermediate data structures that are passed and modified throughout the pipeline are:

1.  **`nodes` (List[Dict])**: A list of dictionaries, where each dictionary represents a "particle" or code element (e.g., a function, class, module, or even a synthetic boundary). Each node accumulates various attributes, classifications, and metrics throughout the pipeline.
2.  **`edges` (List[Dict])**: A list of dictionaries, where each dictionary represents a relationship between two nodes (e.g., "calls", "imports", "contains", "inherits"). Edges are extracted and then resolved to point to canonical node IDs.
3.  **`full_output` (Dict)**: The final aggregated dictionary that collects all analysis results, statistics, metrics, and reports, destined for JSON and HTML output.

Here's a breakdown of the pipeline's major stages and their intermediate data:

---

### Collider Data Pipeline Stages

The `run_full_analysis` function orchestrates approximately 30 distinct stages, which iteratively enrich and analyze the `nodes` and `edges` data structures.

**Phase 0: Initialization & Pre-Analysis**
*   **Logistics Setup**: Initializes `PerformanceManager` for timing, generates a unique `batch_id` and `refinery_signature` for provenance.
*   **Stage 0: Survey**:
    *   **Purpose**: Scans the codebase to identify file types, vendor directories, minified files, and suggests paths to exclude from analysis.
    *   **Input**: `target_path`
    *   **Intermediate Data**: `survey_result` (object containing file counts, exclusions, warnings). `exclude_paths` list for subsequent stages.

**Phase 1: Core Graph Extraction & Classification (via `unified_analysis.analyze`)**
This is a critical sub-pipeline that performs the initial parsing, node/edge extraction, and core classification.

*   **Stage 1: Base Analysis (Delegates to `unified_analysis.analyze`)**:
    *   **Purpose**: Extracts raw code particles, performs initial classification, and builds the foundational call graph.
    *   **Input**: `target_path`, `exclude_paths` (from survey), `options`.
    *   **Intermediate Data (from `unified_analysis.analyze` output)**:
        *   `nodes` (list of raw and initially classified particles).
        *   `edges` (list of `calls`, `imports`, `contains`, `inherits` relationships).
        *   `unified_stats`, `unified_classification`, `unified_auto_discovery`, `unified_dependencies`, `unified_architecture`, `unified_llm_enrichment`, `unified_warnings`, `unified_recommendations` (initial metrics and reports).
    *   **Internal Sub-Stages of `unified_analysis.analyze`**:
        1.  **AST Parse**: `TreeSitterUniversalEngine` parses files into raw particles (`results` list).
        2.  **Auto Pattern Discovery**: `StatsGenerator` applies heuristics to classify `particles`.
        3.  **LLM Enrichment (Optional)**: `LLMClassifier` refines `Unknown` or low-confidence `particles`.
        4.  **Emit File Nodes**: Adds synthetic "module" nodes for each analyzed file to `particles`.
        5.  **Edge Extraction**: `edge_extractor` finds `calls`, `contains`, `inherits`, and `exposes` edges from `particles` and `results`, then `resolve_edges` maps them to canonical node IDs.
        6.  **Graph Inference**: `graph_type_inference` infers node types based on graph structure.
        7.  **Purpose Field (Initial)**: `detect_purpose_field` assigns initial architectural layers to `particles`.
        8.  **Standard Model Enrichment (Initial)**: `standard_model_enricher` adds initial RPBL scores, Atom IDs, and `dimensions`.
        9.  **Create Unified Output**: Consolidates all internal results into a `UnifiedAnalysisOutput` object.

**Phase 2: Deep Enrichment & Advanced Analysis (within `run_full_analysis`)**
This phase takes the `nodes` and `edges` from the `Base Analysis` and applies a myriad of theoretical frameworks and analytical tools.

*   **Stage 2: Standard Model Enrichment (Re-apply)**:
    *   **Purpose**: Re-applies the Standard Model theory (RPBL, Atom IDs, Dimensions) to `nodes`, potentially refining previous classifications.
    *   **Input**: `nodes`
    *   **Intermediate Data**: `nodes` (enriched with `rpbl_responsibility`, `rpbl_purity`, etc.).

*   **Stage 2.5: Ecosystem Discovery**:
    *   **Purpose**: Identifies unknown ecosystem patterns within nodes.
    *   **Input**: `nodes`
    *   **Intermediate Data**: `ecosystem_discovery` (dict).

*   **Stage 2.6: Holarchy Level Classification**:
    *   **Purpose**: Classifies nodes into holarchy levels (L-3 to L12) and infers package levels.
    *   **Input**: `nodes`
    *   **Intermediate Data**: `nodes` (with `level`, `level_zone`), `level_stats`.

*   **Stage 2.7: Octahedral Dimension Classification**:
    *   **Purpose**: Assigns nodes full 8-dimension coordinates.
    *   **Input**: `nodes`
    *   **Intermediate Data**: `nodes` (with `dimensions` updated).

*   **Stage 2.8: Scope Analysis**:
    *   **Purpose**: Identifies unused definitions and shadowed variables within code bodies using Tree-sitter.
    *   **Input**: `nodes` (`body_source`), `tree_sitter` parsers.
    *   **Intermediate Data**: `nodes` (with `scope_analysis` metadata).

*   **Stage 2.9: Control Flow Metrics**:
    *   **Purpose**: Calculates cyclomatic complexity and nesting depth using Tree-sitter.
    *   **Input**: `nodes` (`body_source`), `tree_sitter` parsers.
    *   **Intermediate Data**: `nodes` (with `control_flow`, `cyclomatic_complexity`, `max_nesting_depth`).

*   **Stage 2.10: Pattern-Based Atom Detection**:
    *   **Purpose**: Detects fine-grained "atoms" (e.g., data types, domain concepts) within code bodies using Tree-sitter patterns.
    *   **Input**: `nodes` (`body_source`), `tree_sitter` parsers.
    *   **Intermediate Data**: `nodes` (with `detected_atoms`, `atom_type`).

*   **Stage 2.11: Data Flow Analysis (D6:EFFECT)**:
    *   **Purpose**: Analyzes data flow for side effects and purity, contributing to the D6:EFFECT dimension.
    *   **Input**: `nodes` (`body_source`), `tree_sitter` parsers.
    *   **Intermediate Data**: `nodes` (with `data_flow`, `D6_EFFECT`).

*   **Stage 3: Purpose Field (Re-apply)**:
    *   **Purpose**: Builds a rich purpose field, refining architectural layers and identifying violations like "God Classes."
    *   **Input**: `nodes`, `edges`.
    *   **Intermediate Data**: `purpose_field` (object with detailed node purpose info, violations).

*   **Stage 3.5: Organelle Purpose (π₃)**:
    *   **Purpose**: Infers the aggregate purpose of composite nodes (e.g., classes from their methods).
    *   **Input**: `nodes`.
    *   **Intermediate Data**: `nodes` (with `pi3_purpose`, `pi3_confidence`).

*   **Stage 3.6: System Purpose (π₄)**:
    *   **Purpose**: Infers the purpose of files/modules based on their contained nodes.
    *   **Input**: `nodes`.
    *   **Intermediate Data**: `nodes` (with `pi4_purpose`, `pi4_confidence`), `file_purposes`.

*   **Stage 3.7: Purpose Coherence Metrics**:
    *   **Purpose**: Calculates metrics like coherence score and purpose entropy based on `purpose_field`.
    *   **Input**: `nodes`, `purpose_field`.
    *   **Intermediate Data**: `nodes` (with `purpose_coherence`, `coherence_score`).

*   **Stage 4: Execution Flow**:
    *   **Purpose**: Identifies entry points, unreachable code (orphans), and estimates dead code percentage.
    *   **Input**: `nodes`, `edges`, `purpose_field`.
    *   **Intermediate Data**: `exec_flow` (object containing entry points, orphans).

*   **Stage 5: Markov Transition Matrix**:
    *   **Purpose**: Computes transition probabilities between nodes, enriching edges with `markov_weight`.
    *   **Input**: `nodes`, `edges`.
    *   **Intermediate Data**: `edges` (with `markov_weight`), `markov` (dict).

*   **Stage 6: Knot/Cycle Detection**:
    *   **Purpose**: Detects dependency cycles and bidirectional edges.
    *   **Input**: `nodes`, `edges`.
    *   **Intermediate Data**: `knots` (dict with cycle counts, bidirectional edges, knot score).

*   **Stage 6.5: Graph Analytics (Nerd Layer)**:
    *   **Purpose**: Computes graph metrics like in/out degree, betweenness centrality, PageRank, and community detection using NetworkX.
    *   **Input**: `nodes`, `edges`.
    *   **Intermediate Data**: `nodes` (with `in_degree`, `out_degree`, `betweenness_centrality`, `pagerank`, `topology_role`, `disconnection`, `pi2_purpose`), `graph_analytics` (dict for bottlenecks, top PageRank, communities).

*   **Stage 6.6: Statistical Metrics**:
    *   **Purpose**: Calculates code complexity, Halstead metrics, and entropy.
    *   **Input**: `nodes`.
    *   **Intermediate Data**: `statistical_metrics` (dict).

*   **Stage 6.7: Semantic Purpose Analysis**:
    *   **Purpose**: Infers semantic roles, propagates context from entry points, identifies critical nodes, and builds node intent profiles.
    *   **Input**: `nodes`, `edges`, `target_path`.
    *   **Intermediate Data**: `nodes` (with `semantic_role`, `is_bridge`, `depth_from_entry`, `intent_profile`), `semantic_analysis` (dict).

*   **Stage 6.8: Codome Boundary Generation**:
    *   **Purpose**: Creates synthetic boundary nodes and inferred edges to represent external interactions (e.g., test frameworks, web calls).
    *   **Input**: `nodes`, `edges`.
    *   **Intermediate Data**: `nodes` (extended with boundary nodes), `edges` (extended with inferred edges), `codome_result` (dict).

*   **Stage 7: Data Flow Analysis**:
    *   **Purpose**: Identifies data sources and sinks within the codebase based on flow patterns.
    *   **Input**: `nodes`, `edges`.
    *   **Intermediate Data**: `data_flow` (dict).

*   **Stage 8: Performance Prediction**:
    *   **Purpose**: Predicts performance characteristics based on code structure and execution flow.
    *   **Input**: `nodes`, `exec_flow`.
    *   **Intermediate Data**: `perf_summary` (dict).

*   **Stage 8.5: Constraint Field Validation**:
    *   **Purpose**: Validates the codebase against architectural constraints, identifying "antimatter," policy violations, and architectural patterns.
    *   **Input**: `nodes`, `edges`.
    *   **Intermediate Data**: `constraint_report` (dict).

*   **Stage 8.6: Purpose Intelligence (Q-Scores)**:
    *   **Purpose**: Computes an overall "codebase intelligence" score based on various metrics.
    *   **Input**: `nodes`, `edges`.
    *   **Intermediate Data**: `nodes` (enriched with intelligence scores), `codebase_intelligence` (dict).

*   **File-Centric View**:
    *   **Purpose**: Creates an index of atoms grouped by file for hybrid navigation and enriches file metadata.
    *   **Input**: `nodes`, `edges`, `target_path`.
    *   **Intermediate Data**: `files_index`, `file_boundaries` (added to `full_output`).

*   **Stage 9: Roadmap Evaluation**:
    *   **Purpose**: Evaluates the codebase's readiness against a defined architectural roadmap.
    *   **Input**: `target_path`, `options['roadmap']`.
    *   **Intermediate Data**: `roadmap_result` (dict).

*   **Stage 10: Visual Topology Analysis**:
    *   **Purpose**: Classifies the overall visual shape and structure of the graph.
    *   **Input**: `nodes`, `edges`.
    *   **Intermediate Data**: `topology_result` (dict).

*   **Stage 11: Semantic Cortex (Concept Extraction)**:
    *   **Purpose**: Extracts key concepts and infers domain from node content.
    *   **Input**: `nodes`.
    *   **Intermediate Data**: `semantics` (dict).

*   **Stage 11b: AI Insights Generation (Optional)**:
    *   **Purpose**: Uses an LLM (e.g., Vertex AI Gemini) to generate high-level insights from the `full_output`.
    *   **Input**: `full_output`.
    *   **Intermediate Data**: `ai_insights` (dict).

*   **Stage 11.5: Manifest Writer (Provenance & Integrity)**:
    *   **Purpose**: Calculates a cryptographic Merkle root for `nodes` and generates a manifest for provenance tracking.
    *   **Input**: `nodes`.
    *   **Intermediate Data**: `merkle_root`, `manifest` (dict).

*   **Stage 13: Information Graph Theory (IGT) Metrics**:
    *   **Purpose**: Computes metrics like directory stability and classifies true "orphan" nodes.
    *   **Input**: `file_boundaries`, `exec_flow.orphans`, `nodes`.
    *   **Intermediate Data**: `igt_results` (dict).

**Phase 3: Output Consolidation**

*   **Stage 12: Generating Consolidated Outputs**:
    *   **Purpose**: Finalizes the `full_output` structure, attaches `waybill` metadata to individual nodes for atom-level provenance, and generates the final LLM-oriented JSON and human-readable HTML reports.
    *   **Input**: `full_output`, `output_dir`.
    *   **Output**: `output_llm-oriented_<project>_<timestamp>.json` and `output_human-readable_<project>_<timestamp>.html`.

---

This extensive pipeline ensures that Collider generates a highly detailed, multi-dimensional, and theoretically rich analysis of a codebase, covering structural, behavioral, semantic, and architectural aspects.

---

## Citations

_No citations provided_
