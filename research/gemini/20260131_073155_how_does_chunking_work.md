# Research: how does chunking work

> **Date:** 2026-01-31 07:31:55
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:d57ddc713d2ca74b093acf9830f23006135f11f4d0e35e65e3f79b31cab3c90b`
> **Raw JSON:** `raw/20260131_073155_how_does_chunking_work.json`

---

## Query

how does chunking work

---

## Response

Based on the provided `wave/docs/WORKFLOW_FACTORY.md`, chunking is a critical component of the **Hybrid Workflow (RAG)** and **GraphRAG** strategies. Here is an analysis of how it works in this system:

### 1. Hybrid Workflow (RAG)
In the Tier 2 (File Search) and Hybrid approaches, chunking is the mechanism used to retrieve relevant information from a large corpus without loading entire files.

*   **Retrieval Phase:** The system treats the codebase as a "Large Corpus (2M+ tokens)". It uses **Vector/BM25 Retrieval** to identify specific "Top-K chunks" (typically 5–20 documents/fragments) that match the user's query.
*   **Purpose:** This allows the system to answer "needle queries" (e.g., "Where is RPBL score calculated?") efficiently (~$0.003/query) compared to full context analysis.

### 2. Context Assembly (The "Sandwich" Strategy)
Once chunks are retrieved, they are not just dumped into the model. The system uses a specific **Positional Strategy** (implemented in `analyze.py:875-934`) to assemble the prompt:

1.  **Start:** Critical files (High signal files explicitly requested).
2.  **Middle:** **Retrieved Chunks** (The "Top-K" results from the search).
3.  **End:** Instructions + critical recap (to leverage the "recency bias" of LLMs).

This structure ensures that the retrieved chunks provide necessary context without overwhelming the "critical" instructions at the start and end.

### 3. Structural Chunking (GraphRAG)
For the GraphRAG component (analysis of code relationships), the system appears to use semantic/structural chunking rather than arbitrary text splitting:

*   **Engine:** The docs cite `TreeSitterUniversalEngine` for **Entity Extraction** (scored 10/10).
*   **Method:** This implies the code is "chunked" based on its Abstract Syntax Tree (AST)—identifying functions, classes, and definitions—rather than simple line counts.
*   **Usage:** These structural chunks are used to build nodes in the knowledge graph (`collider-brain`, `collider-schema`, etc.) and establish edges via `edge_extractor.py`.

### 4. Implementation References
The documentation points to specific implementations for these mechanisms:
*   **Gemini File Search (Vector RAG):** `analyze.py:412-625`
*   **Positional Strategy (Context Assembly):** `analyze.py:875-934`
*   **Entity/Structural Extraction:** `TreeSitterUniversalEngine` (External component integrated for GraphRAG)

---

## Citations

_No citations provided_
