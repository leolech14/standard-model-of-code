# Research: What are the architectural gaps in the wave/tools/ai/ toolkit and what should be consolidated before...

> **Date:** 2026-02-07 19:26:53
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:02eb27712388aa4fa2f1616dcef2f0929d954ce4399b06e842d34fd8d5c4c35e`
> **Raw JSON:** `raw/20260207_192653_what_are_the_architectural_gaps_in_the_wave_tools.json`

---

## Query

What are the architectural gaps in the wave/tools/ai/ toolkit and what should be consolidated before MCP wrapping?

---

## Response

Based on the analysis of the `wave/tools/ai/aci` codebase, the system implements a sophisticated "Adaptive Context Intelligence" (ACI) subsystem. It features advanced tier routing (Instant vs. RAG vs. Long Context), graph-based semantic search, and multi-step research orchestration.

However, to prepare this for **MCP (Model Context Protocol)** wrapping—where these tools will be exposed to an LLM client (like Claude Desktop or an IDE extension)—there are specific architectural gaps regarding state management, configuration redundancy, and logic fragmentation.

Here is the architectural analysis and consolidation plan.

---

### 1. Architectural Gaps

#### A. The "Split Brain" of Intent Detection
There is a significant overlap in how the system understands a user query across three different files. This makes the system brittle; changing a keyword in one place doesn't propagate to others.
*   **`intent_parser.py`**: Uses regex/keywords to determine `QueryIntent` (Architecture, Debug, etc.).
*   **`tier_orchestrator.py`**: Contains a hardcoded `ROUTING_MATRIX` and triggers (`CEREBRAS_TRIGGERS`, `FLASH_DEEP_TRIGGERS`) that effectively re-evaluate intent.
*   **`semantic_finder.py`**: Contains its own dictionaries (`QUERY_PURPOSE_KEYWORDS`, `QUERY_LAYER_KEYWORDS`) to map queries to the Standard Model of Code.

**Gap:** Logic is duplicated. An MCP tool needs a single source of truth for "What is the user asking?" to deterministically route requests.

#### B. Context Assembly Fragmentation (Refinery vs. RepoPack)
The system has two completely separate pipelines for reading code, leading to I/O inefficiency and potential inconsistency.
*   **`refinery.py`**: A "Smart" chunker. It parses ASTs (Python), splits Markdown headers, and calculates relevance scores. It generates `RefineryNodes`.
*   **`repopack.py`**: A "Dumb" packer. It walks the file system and concatenates strings for the Long-Context tier. It ignores the intelligent chunking logic of Refinery.

**Gap:** `RepoPack` should effectively be a serializer for `RefineryNodes`, not a separate file reader. The "Flash Deep" tier receives raw text rather than the semantically scored/filtered context that `Refinery` produces.

#### C. Hardcoded Configuration vs. `aci_config.yaml`
While `aci_config.yaml` exists, huge chunks of logic are hardcoded in Python.
*   **`tier_orchestrator.py`**: The `ROUTING_MATRIX` (mapping Intent/Complexity/Scope to Tier) is a Python dictionary, making it impossible to tune routing logic without a code deploy.
*   **`context_builder.py`**: Contains `_DEFAULT_TOKEN_BUDGETS` which might conflict with config overrides.

**Gap:** MCP servers often require dynamic configuration. The routing logic needs to be fully lifted into the YAML configuration so the "Assistant" behavior can be tuned independently of the code.

---

### 2. Consolidation Strategy (Pre-MCP)

Before wrapping these tools in MCP, perform the following refactors to ensure the tools are atomic, stateless, and consistent.

#### Step 1: Unify The "Brain" (Intent & Semantics)
Merge the logic from `intent_parser.py` and `semantic_finder.py`.
*   **Action:** Create a `QueryUnderstandingService`.
*   **Result:** A single analysis pass that outputs a `QueryContext` object containing Intent, Scope, Complexity, *and* Semantic Targets ($\pi$ levels, layers).
*   **Why:** MCP tools often receive vague instructions. You need the strongest possible signal extraction in one place to prevent the "Router" and the "Context Builder" from disagreeing on what the user wants.

#### Step 2: Unify The "Hand" (Context Pipeline)
Refactor `repopack.py` to consume `Refinery` output.
*   **Action:** Modify `repopack.py` to accept a list of `RefineryNode` objects instead of a raw directory path.
*   **Logic:**
    1.  `Refinery` scans and chunks the code.
    2.  `Refinery` filters noise (imports, low-value chunks) based on `context_depth`.
    3.  `RepoPack` formats those high-value chunks into the cacheable XML/Markdown string.
*   **Why:** This ensures the "Flash Deep" (2M context) tier doesn't waste tokens on low-value code that the Refinery already knows how to filter out.

#### Step 3: Extract the Routing Matrix
Move the `ROUTING_MATRIX` from `tier_orchestrator.py` to `aci_config.yaml`.
*   **Action:** Define a rule engine in YAML.
    ```yaml
    routing_rules:
      - if: { intent: "DEBUG", complexity: "MODERATE" }
        use: "LONG_CONTEXT"
        reason: "Multi-file reasoning required"
    ```
*   **Why:** This allows the MCP server behavior to be tweaked by the user (via config) without altering the server source code.

---

### 3. MCP Wrapping Strategy

Once consolidated, you should expose three distinct MCP Tools. The `research_orchestrator.py` is already close to being an MCP-ready architecture; the others need adaptation.

#### Tool 1: `analyze_codebase` (The Router)
*   **Source:** `tier_orchestrator.py` + `aci_config.yaml`
*   **Input:** `query` (string)
*   **Behavior:** Runs the unified `QueryUnderstandingService`. Determines if the answer exists in `repo_truths` (Tier 0), requires a specific file lookup (Tier 1), or full reasoning (Tier 2).
*   **Output:** A structured plan (JSON) telling the LLM client *which* tool to call next (or providing the answer immediately if Tier 0).

#### Tool 2: `fetch_context` (The Builder)
*   **Source:** `context_builder.py` + `refinery.py` + `repopack.py`
*   **Input:** `sets` (list of strings), `mode` (focused | broad)
*   **Behavior:**
    1.  Resolves "sets" to file paths.
    2.  Runs `Refinery` to get chunks.
    3.  Runs `RepoPack` (if mode=broad) or selects specific chunks (if mode=focused).
    4.  Checks `context_cache` to see if a valid Snapshot ID exists.
*   **Output:** Either the actual text context (for RAG) or a Cache ID (for Gemini context caching).

#### Tool 3: `run_research` (The Agent)
*   **Source:** `research_orchestrator.py`
*   **Input:** `schema_name` (string), `query` (string), `overrides` (dict)
*   **Behavior:** The "Joystick Interface" described in the file is perfect for MCP. It allows the LLM to trigger complex, multi-step workflows (like "validation_trio") as a single function call.
*   **Consolidation Note:** Ensure `research_orchestrator` uses the *new* Unified Context Pipeline (Step 2 above) instead of spawning subprocesses to `analyze.py`.

### Summary of Priority Actions

1.  **Refactor:** Rewrite `repopack.py` to import and use `Refinery` classes.
2.  **Refactor:** Merge `INTENT_KEYWORDS` (parser) and `ROUTING_MATRIX` (orchestrator) into `aci_config.yaml`.
3.  **Define:** Create `tools/mcp_server.py` that maps the three tools above to the internal Python API.

---

## Citations

_No citations provided_
