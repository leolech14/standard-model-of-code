# Research: Compare: TRELLIS.2 is registered in tool_registry.yaml as a tool. Doppler is infrastructure. analyze...

> **Date:** 2026-01-31 00:18:55
> **Source:** gemini
> **Model:** gemini-2.5-flash
> **Checksum:** `sha256:cefda0a7b8c1133b57f7d4d04050409cc633c26a2b86764fc7f5a6bdc70e9e66`
> **Raw JSON:** `raw/20260131_001855_compare__trellis_2_is_registered_in_tool_registry.json`

---

## Query

Compare: TRELLIS.2 is registered in tool_registry.yaml as a tool. Doppler is infrastructure. analyze.py is a wave tool. Where does the HuggingFace integration belong? It has: MCP (global), CLI script, token, docs. Apply existing patterns.

---

## Response

Based on the provided codebase context, the HuggingFace integration, with its components (MCP, CLI script, token, docs), should be integrated following the established patterns of **Concepts/Objects Duality**, the **Subsystem Integration Map**, and the **Agent Manifest**.

Here's a breakdown of where each component belongs:

### 1. Overall Categorization & Subsystem Registration

*   **Subsystem Type:** Similar to the existing `Perplexity MCP` (S4), the HuggingFace integration appears to be a **Utility** or **Engine**. Given its "MCP (global)" aspect, "Utility" is a strong fit, implying it provides external services or capabilities.
*   **Purpose:** To integrate external AI models, specifically from HuggingFace, for tasks such as advanced NLP, code models, or embeddings, complementing the existing Gemini and Perplexity integrations.
*   **Integration Map Entry:** A new entry should be added to `.agent/SUBSYSTEM_INTEGRATION.md` under the "Subsystem Registry" table, e.g.:
    *   **ID:** S15 (following S14 GraphRAG)
    *   **Subsystem:** **HuggingFace Integration**
    *   **Type:** Utility
    *   **Path:** `wave/tools/huggingface/` (for code), `wave/docs/HUGGINGFACE_INTEGRATION.md` (for docs)
    *   **Purpose:** External AI model integration (e.g., NLP, code generation, embeddings)

### 2. File Structure (Concepts / Objects Duality)

The project consistently separates "Concepts" (specs, definitions) from "Objects" (instances, implementations).

*   **Concepts (Documentation):**
    *   The documentation explaining the HuggingFace integration, its capabilities, usage, configuration, and API should reside in:
        *   `wave/docs/HUGGINGFACE_INTEGRATION.md`
        *   If specific schemas are needed (e.g., for model configurations, input/output formats), they would go in `wave/config/` or `.agent/schema/` if they are system-wide.

*   **Objects (Implementation):**
    *   **MCP (global):** This component, acting as a server or a core library wrapper for HuggingFace APIs, should be placed within the `wave/tools/` directory, specifically in a new `huggingface` subdirectory, mirroring the `mcp` for Perplexity.
        *   `wave/tools/huggingface/huggingface_mcp_server.py` (or a similar name for the primary integration component).
    *   **CLI script:** Any command-line interface for interacting with the HuggingFace MCP or directly with HuggingFace models should also reside within this new directory:
        *   `wave/tools/huggingface/cli.py` (if it's a specific client for this subsystem)
        *   Alternatively, if it's meant to be a general AI query interface similar to `analyze.py`, it could be `wave/tools/ai/huggingface_analyze.py`, but the former is more consistent with self-contained subsystems.

### 3. Configuration & Secrets

*   **Token:** Secrets are managed by Doppler, as indicated in `manifest.yaml` under `integrations.secrets`. The HuggingFace API token should be stored securely in Doppler, not directly in the codebase.
    *   The code would retrieve this token via the Doppler integration.

### 4. Agent Manifest (`.agent/manifest.yaml`)

This file is for machine-readable discovery of integration points.

*   **AI Tools Integration:** The primary entry point for the HuggingFace integration should be registered under `integrations.ai_tools`.
    *   `integrations:`
        *   `ai_tools:`
            *   `huggingface: wave/tools/huggingface/huggingface_mcp_server.py` (or `wave/tools/huggingface/cli.py` if the CLI is the main interaction point).

*   **Agent Capabilities (Optional):** If HuggingFace provides unique capabilities that certain agents can leverage, a new agent entry or an update to an existing agent's capabilities could be made under `agents:` (e.g., `nlp_agent`, `model_finetuner`).

### Summary of Placement:

| Component       | Location                                                | Rationale                                                                        |
| :-------------- | :------------------------------------------------------ | :------------------------------------------------------------------------------- |
| **MCP (global)**| `wave/tools/huggingface/huggingface_mcp_server.py` | Implementation (Object), mirrors `perplexity_mcp_server.py` pattern.             |
| **CLI script**  | `wave/tools/huggingface/cli.py`           | Implementation (Object), specific tool for the subsystem.                        |
| **Token**       | Managed by Doppler                                      | Secret management via `integrations.secrets` in `manifest.yaml`.               |
| **Docs**        | `wave/docs/HUGGINGFACE_INTEGRATION.md`    | Concepts, consistent with other subsystem documentation.                         |
| **Registry**    | `.agent/SUBSYSTEM_INTEGRATION.md`                       | New `S15 HuggingFace Integration` (Utility) entry.                             |
| **Manifest**    | `.agent/manifest.yaml` (`integrations.ai_tools.huggingface`) | Machine-readable discovery, similar to Gemini and Perplexity AI tools.           |

---

## Citations

_No citations provided_
