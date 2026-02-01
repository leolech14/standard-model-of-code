# Research: What are the 18 pipeline stages in full_analysis.py? List them all with their purpose.

> **Date:** 2026-01-30 03:02:14
> **Source:** gemini
> **Model:** gemini-2.5-flash
> **Checksum:** `sha256:6123b6b936da1337bb8b5f02fb60e963f8004cd9195280c0095a7cb1e6b82f9a`
> **Raw JSON:** `raw/20260130_030214_what_are_the_18_pipeline_stages_in_full_analysis_p.json`

---

## Query

What are the 18 pipeline stages in full_analysis.py? List them all with their purpose.

---

## Response

The `full_analysis.py` file orchestrates a comprehensive, multi-stage analysis pipeline. While the explicit numbering scheme in the `run_full_analysis` function is not a simple 1-to-18 sequence (it includes fractional stages and some out-of-order printing), I will list the 18 most distinct and significant stages based on their explicit "Stage N" labels and their described purposes within the `run_full_analysis` function.

Here are 18 pipeline stages identified in `full_analysis.py`, along with their purposes:

1.  **Stage 0: Survey (Pre-Analysis Intelligence)**
    *   **Purpose:** Performs an initial scan of the codebase to identify files for exclusion (e.g., vendor directories, minified files) and estimate overall project size, optimizing subsequent analysis.

2.  **Stage 1: Base Analysis**
    *   **Purpose:** Executes the core AST parsing and initial symbol extraction, yielding raw code particles and basic structural relationships (nodes and edges).

3.  **Stage 2: Standard Model Enrichment**
    *   **Purpose:** Enriches the extracted nodes with attributes from the "Standard Model of Code," applying conceptual frameworks like RPBL (Responsibility, Purity, Boundary, Lifecycle) scores and atom identification.

4.  **Stage 2.11: Data Flow Analysis (D6:EFFECT)**
    *   **Purpose:** Analyzes the internal data flow of individual nodes to assess their purity and potential side effects, contributing to the D6_EFFECT dimension of the 8-dimensional model.

5.  **Stage 3: Purpose Field**
    *   **Purpose:** Detects the emergent purpose of code components (e.g., "Service," "Controller") and identifies anti-patterns or violations of intended purpose through dependency analysis.

6.  **Stage 3.7: Purpose Coherence Metrics**
    *   **Purpose:** Computes metrics related to the consistency and focus of a node's purpose (coherence score, purpose entropy) and identifies "god classes" based on these metrics.

7.  **Stage 4: Execution Flow**
    *   **Purpose:** Identifies potential entry points into the codebase and analyzes code reachability, pinpointing truly orphaned or "dead" code.

8.  **Stage 5: Markov Transition Matrix**
    *   **Purpose:** Calculates probabilistic transition weights between nodes in the call graph, which can be used for flow visualization and understanding call patterns.

9.  **Stage 6: Knot/Cycle Detection**
    *   **Purpose:** Identifies dependency cycles (knots) and highly bidirectionally coupled nodes (tangles) within the graph, indicating potential architectural fragility.

10. **Stage 6.7: Semantic Purpose Analysis**
    *   **Purpose:** Performs advanced graph analytics including finding entry points, propagating context downstream, computing various centrality metrics, classifying semantic roles (utility, orchestrator, hub, leaf), and building node intent profiles from docstrings and commit history.

11. **Stage 6.8: Codome Boundary Generation**
    *   **Purpose:** Creates synthetic "codome boundary" nodes and inferred edges for disconnected nodes (e.g., test entries, framework-managed components), providing a richer understanding of external reachability.

12. **Stage 7: Data Flow Analysis**
    *   **Purpose:** Analyzes aggregate data flow patterns across the codebase to identify primary data sources (high out-degree, low in-degree) and data sinks (high in-degree, low out-degree) by type.

13. **Stage 8: Performance Prediction**
    *   **Purpose:** Predicts potential performance characteristics and bottlenecks based on the identified execution flow and node complexity.

14. **Stage 8.6: Purpose Intelligence**
    *   **Purpose:** Enriches nodes with "intelligence" or "Q-scores" that reflect their coherence, purity, and criticality, providing an overall "Codebase Intelligence" score and interpretation.

15. **Stage 9: Roadmap Evaluation**
    *   **Purpose:** Evaluates the codebase against a predefined architectural roadmap, assessing its readiness and adherence to desired patterns and goals.

16. **Stage 10: Visual Reasoning**
    *   **Purpose:** Classifies the overall structural shape and topology of the codebase's graph (e.g., "Monolith," "Microservice-like," "Spaghetti") for high-level architectural understanding.

17. **Stage 11: Semantic Cortex**
    *   **Purpose:** Extracts key domain concepts and terms from the codebase's code and documentation to infer the primary business domain and top concepts.

18. **Stage 12: Generating Consolidated Outputs**
    *   **Purpose:** Consolidates all preceding analysis results into the final output formats: an LLM-oriented JSON knowledge bundle and a human-readable HTML report (which includes an embedded "Brain Download" of the analysis).

---

## Citations

_No citations provided_
