# Research: GraphRAG Implementation Alignment with PROJECT_elements:

WHAT WE BUILT (validated by 120+ sources):...

> **Date:** 2026-01-27 19:17:25
> **Source:** gemini
> **Model:** gemini-2.5-flash
> **Checksum:** `sha256:8342faaa12890e0107a12e0a05ee36f3006853c9c92839bf4f568998db352463`
> **Raw JSON:** `raw/20260127_191725_graphrag_implementation_alignment_with_project_ele.json`

---

## Query

GraphRAG Implementation Alignment with PROJECT_elements:

WHAT WE BUILT (validated by 120+ sources):
- Neo4j graph: 5,284 nodes (code + chunks + papers)
- Basic queries working
- Complete code patterns from research (vector index, Leiden, subgraph extraction, ACI router)

REPOSITORY ARCHITECTURE:
- Subsystems: S1 (Collider), S3 (analyze.py), S6 (BARE), S7 (Archive), S13 (Macro)
- Butlers: 26 maintaining palace
- ACI Tiers: INSTANT, RAG, LONG_CONTEXT, PERPLEXITY (4 existing)
- Principles: Git is truth, Conventional Commits, Never leave uncommitted

INTEGRATION QUESTIONS:
1. Where does GraphRAG fit in subsystem hierarchy? (New S14 or extend S3?)
2. Should graph state be in Git (exported JSON) or ephemeral (rebuild from sources)?
3. How to integrate with analyze.py? (New --graph-query flag or new ACI tier?)
4. GraphRAG as 27th butler or enhancement to existing?
5. Incremental updates: Hook into wire.py delta detection how?
6. Commit strategy: feat(graphrag) for what exactly?
7. Performance: When use GraphRAG vs text search (SLO guidance)?

Recommend: Architecture for integrating GraphRAG that aligns with manifest.yaml, SUBSYSTEM_INTEGRATION.md, AGENT_KERNEL.md principles, and existing automation (wire/autopilot/refinery).

Specific: What subsystem number, what files to modify, what commit message, what butler pattern.

---

## Response

This is an excellent set of requirements and a well-defined new component. Integrating GraphRAG into the `PROJECT_elements` architecture requires careful consideration to maintain alignment with the established principles of `KERNEL.md`, `SUBSYSTEM_INTEGRATION.md`, and `manifest.yaml`.

Here's an architectural recommendation covering each of your integration questions, followed by specific file modifications and commit strategy.

---

### GraphRAG Architectural Integration Recommendation

#### 1. Where does GraphRAG fit in subsystem hierarchy? (New S14 or extend S3?)

GraphRAG is a new, specialized intelligence capability for knowledge retrieval and reasoning. While it will integrate closely with `analyze.py` (S3), it represents a distinct engine for processing and querying data.

**Recommendation:**
Assign GraphRAG a **new subsystem ID: S14**.

*   **Subsystem ID:** S14
*   **Subsystem Name:** GraphRAG
*   **Type:** Engine (similar to Collider S1, BARE S6, analyze.py S3)
*   **Path:** `wave/tools/ai/graph_rag/`
*   **Purpose:** Enhanced knowledge retrieval and reasoning based on structured graph data.

`analyze.py` (S3) acts as the primary AI query interface and will be extended to *orchestrate* and *route* queries to S14, similar to how it leverages S4 (Perplexity MCP). This maintains modularity and adheres to the "Concepts / Objects Duality" where `analyze.py` is a conceptual interface, and GraphRAG is a distinct object (implementation) providing specialized capabilities.

#### 2. Should graph state be in Git (exported JSON) or ephemeral (rebuild from sources)?

The "Git is truth" non-negotiable from `KERNEL.md` is critical. However, storing a 5,000+ node graph in Git as raw JSON would lead to massive repository bloat, merge conflicts, and performance issues.

**Recommendation:**
Treat the **GraphRAG database instance as an ephemeral, derived artifact** that is rebuildable from source data.

*   **Source Data (Git is Truth):** The underlying source code, chunks, and papers from which the graph is constructed *must* remain in Git. This is the canonical source of truth.
*   **Graph Schema & Configuration (Git is Truth):** The *definition* of the graph (node types, relationship types, properties, indexing strategies, build rules) is crucial for reproducibility and must be version-controlled.
    *   **New file:** `wave/tools/ai/graph_rag/schema/graph_schema.yaml`
    *   **New file:** `wave/config/graph_config.yaml` (for Neo4j connection details, source paths, chunking config, etc.)
*   **Ephemeral Database:** The running Neo4j instance or its full dump is *not* checked into Git.
*   **GCS Archiving:** To ensure recoverability and provide historical snapshots, implement mirroring of periodic Neo4j database dumps to GCS via `Archive/Mirror` (S7). This aligns with `Archive/Mirror syncs to GCS on every commit` data flow. The bucket would likely be `gs://elements-archive-2026/graph_snapshots/`.

#### 3. How to integrate with analyze.py? (New --graph-query flag or new ACI tier?)

`analyze.py` already supports multiple ACI (AI Contextual Interface) tiers. GraphRAG provides a new type of RAG capability.

**Recommendation:**
Introduce `GRAPH_RAG` as a **new ACI tier** within `analyze.py`.

*   **New ACI Tier:** Extend `analyze.py` to recognize and route queries to a `GRAPH_RAG` tier.
*   **CLI Flag:** `analyze.py` will accept a new option, e.g., `--aci-tier GRAPH_RAG` (or `--tier GRAPH_RAG`), allowing agents or users to explicitly request graph-based reasoning.
*   **Routing Logic:** `analyze.py` will implement internal routing logic:
    *   If `GRAPH_RAG` tier is specified, it calls the `GraphRagService` (S14).
    *   Consider implementing intelligent routing: If no tier is specified, `analyze.py` could analyze the query for characteristics that suggest graph-based reasoning (e.g., asking about relationships, patterns, completeness, provenance) and *propose* or *default* to the `GRAPH_RAG` tier.

#### 4. GraphRAG as 27th butler or enhancement to existing?

The term "butler" implies an autonomous agent or process. GraphRAG, as an intelligence engine, is a *capability* that other butlers (agents/processes) can leverage.

**Recommendation:**
GraphRAG is an **enhancement to existing butlers' intelligence capabilities**.

*   It's a foundational intelligence subsystem (S14) that can be utilized by `analyze.py` (S3), `BARE` (S6), or other agents to perform their work more effectively.
*   It provides a more sophisticated RAG mechanism for querying complex relationships in the codebase, which directly benefits tasks like validation (HSL) and auto-refinement (BARE).

#### 5. Incremental updates: Hook into wire.py delta detection how?

"Delta detection" for `wire.py` suggests monitoring changes to trigger actions. The graph needs to reflect the latest state of the codebase.

**Recommendation:**
Integrate graph updates into the `CODE COMMIT` data flow using a **post-commit hook** or a **scheduled job** that leverages `wire.py` (if it coordinates post-commit actions).

*   **Graph Builder Script:** Create `wave/tools/ai/graph_rag/build_graph.py`. This script will be responsible for:
    *   Detecting changes in relevant source directories (e.g., `particle/src/`, `docs/specs/`, `docs/papers/`).
    *   Incrementally updating the Neo4j graph or performing a full rebuild if necessary.
    *   Generating `unified_analysis.json`-like intermediates if needed, or consuming them.
*   **Trigger Mechanism:**
    *   Modify `.pre-commit-config.yaml` to include a `post-commit` hook that triggers `build_graph.py`. This ensures the graph is updated after every successful commit.
    *   Alternatively, if `wire.py` is part of a broader automation framework, it should be configured to call `build_graph.py` after relevant source code changes are detected.
*   **`SUBSYSTEM_INTEGRATION.md` Update:** The Data Flow diagram will be updated to show: `1. CODE COMMIT -> GraphRAG (S14) triggers graph update/rebuild`.

#### 6. Commit strategy: feat(graphrag) for what exactly?

Adhere to the Conventional Commits format enforced by `.pre-commit-config.yaml` and `commitlint.config.js`. Use `graphrag` as the scope.

**Recommendation:**

*   **Initial Integration:**
    ```
    feat(graphrag): Introduce GraphRAG subsystem (S14) for enhanced knowledge retrieval.

    This commit lays the groundwork for GraphRAG, including basic graph construction
    from code and documentation, and initial schema definitions.
    ```
*   **Adding Query Patterns:**
    ```
    feat(graphrag): Implement subgraph extraction and ACI router patterns.

    Adds core query patterns for identifying code relationships,
    Leiden community detection, and integrating with the ACI router logic.
    ```
*   **Integrating with `analyze.py`:**
    ```
    feat(analyze.py): Add GRAPH_RAG ACI tier for graph-based queries.

    Updates analyze.py to include a new ACI tier (--tier GRAPH_RAG) that
    routes queries to the GraphRAG (S14) subsystem for advanced reasoning.
    ```
*   **Schema Changes:**
    ```
    chore(graphrag): Update graph schema to include 'completion_pattern' node type.
    ```
*   **Performance Improvements:**
    ```
    perf(graphrag): Optimize vector index for faster similarity searches.
    ```

#### 7. Performance: When use GraphRAG vs text search (SLO guidance)?

This requires defining clear use cases and expected performance characteristics for GraphRAG.

**Recommendation:**
Develop routing logic and document SLO guidance within `analyze.py` (S3) and the `AI_USER_GUIDE.md`.

*   **Routing Logic:** Within `analyze.py`, develop a strategy to determine when `GRAPH_RAG` is the most appropriate tier. This could be based on:
    *   **Query Intent:** If the query explicitly asks for relationships, dependencies, impact analysis, pattern matching, or multi-hop connections (strengths of graphs).
    *   **Query Complexity:** Complex queries that would be difficult or inefficient with traditional text search.
    *   **Confidence Score:** GraphRAG may yield higher confidence for certain types of structural or relational questions.
    *   **Cost/Latency Trade-offs:** For simple keyword searches, traditional text RAG or `INSTANT` tier might be faster and cheaper.
*   **SLO Guidance:**
    *   Document the expected performance of GraphRAG for different query types (e.g., "N-hop relationship queries typically complete in X seconds with Y% recall").
    *   Clearly define when GraphRAG should be preferred over other tiers in `wave/docs/AI_USER_GUIDE.md`.
    *   Instrument GraphRAG and `analyze.py` to collect metrics (latency, success rate, confidence) to validate and refine SLOs.

---

### Specific Files to Modify

**New Files (for S14: GraphRAG subsystem)**

*   `wave/tools/ai/graph_rag/__init__.py`: Python package initialization.
*   `wave/tools/ai/graph_rag/graph_rag_service.py`: Core service for interacting with Neo4j (queries, subgraph extraction, etc.). This is what `analyze.py` will import.
*   `wave/tools/ai/graph_rag/build_graph.py`: Script to build/update the Neo4j graph from code, chunks, papers.
*   `wave/tools/ai/graph_rag/schema/graph_schema.yaml`: Defines the schema for the Neo4j graph (node labels, relationship types, properties).
*   `wave/tools/ai/graph_rag/docs/GRAPH_RAG_DESIGN.md`: Detailed design and usage instructions for the GraphRAG subsystem.
*   `wave/config/graph_config.yaml`: Configuration for Neo4j connection, source data paths, chunking strategies, vector index parameters.

**Existing Files to Modify**

1.  **`.agent/SUBSYSTEM_INTEGRATION.md`**:
    *   **Subsystem Registry:** Add S14 entry.
        ```
        | S14 | **GraphRAG** | Engine | `wave/tools/ai/graph_rag/` | Enhanced knowledge retrieval and reasoning via graph structures |
        ```
    *   **Architecture Overview Diagram:** Update the diagram to include S14 within the `INTELLIGENCE LAYER (Wave)`, showing `analyze.py` connecting to it.
    *   **Data Flow:** Update "1. CODE COMMIT" flow.
        ```
        1. CODE COMMIT
           └─► Collider generates unified_analysis.json
           └─► Archive/Mirror syncs to GCS
           └─► BARE TruthValidator updates repo_truths.yaml
           └─► **GraphRAG (S14) triggers graph update/rebuild**
        ```
    *   **Cross-Reference Index:** Add S14 entry.
        ```
        ### GraphRAG (S14)
        - Service: `wave/tools/ai/graph_rag/graph_rag_service.py`
        - Builder: `wave/tools/ai/graph_rag/build_graph.py`
        - Schema: `wave/tools/ai/graph_rag/schema/graph_schema.yaml`
        - Config: `wave/config/graph_config.yaml`
        - Docs: `wave/tools/ai/graph_rag/docs/GRAPH_RAG_DESIGN.md`
        ```

2.  **`.agent/manifest.yaml`**:
    *   Under `integrations.ai_tools`:
        ```yaml
          ai_tools:
            gemini: wave/tools/ai/analyze.py
            perplexity: wave/tools/mcp/perplexity_mcp_server.py
            graphrag: wave/tools/ai/graph_rag/graph_rag_service.py # New
        ```
    *   Under `agents.gemini.capabilities`: Add `graph_reasoning` or `relational_query`.
        ```yaml
          gemini:
            capabilities: [research, validation, exploration, graph_reasoning] # Updated
            config: wave/tools/ai/analyze.py
        ```

3.  **`wave/tools/ai/analyze.py`**:
    *   Import `graph_rag_service.py`.
    *   Add a new argument for ACI tier selection, e.g., `--tier GRAPH_RAG`.
    *   Implement routing logic to call `graph_rag_service.py` functions when `GRAPH_RAG` tier is active.
    *   Potentially add heuristic-based routing for queries without an explicit tier.

4.  **`wave/docs/AI_USER_GUIDE.md`**:
    *   Document the new `GRAPH_RAG` ACI tier.
    *   Provide guidance on when to use GraphRAG, including examples and expected performance/SLO characteristics.
    *   Explain the types of queries best suited for GraphRAG vs. other tiers.

5.  **`.pre-commit-config.yaml`**:
    *   Add a new `post-commit` hook definition to trigger `wave/tools/ai/graph_rag/build_graph.py` after a commit, potentially conditionally based on changed files.
        ```yaml
        - id: graphrag-update
          name: GraphRAG Update
          entry: bash -c 'wave/tools/ai/graph_rag/build_graph.py --delta "$@"' --
          language: system
          types: [file] # Adjust if specific file types are needed
          files: '^(particle/src/|docs/specs/|docs/papers/).*' # Only run if relevant sources change
          stages: [post-commit]
        ```
        *(Note: The exact `entry` and `files` regex might need refinement based on the `build_graph.py` implementation and relevant source paths.)*

This structured approach ensures GraphRAG is deeply integrated while respecting `PROJECT_elements`'s architectural principles and automation ecosystem.

---

## Citations

_No citations provided_
