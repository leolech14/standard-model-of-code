# Research: Audit the ACI tier routing system: How does it decide which tier to use? What are the failure modes?

> **Date:** 2026-01-30 03:01:27
> **Source:** gemini
> **Model:** gemini-2.5-flash
> **Checksum:** `sha256:838b3a1d6764b44774f4f7d95ec556d463a4d01644240e03bebd7dd07a2a2992`
> **Raw JSON:** `raw/20260130_030127_audit_the_aci_tier_routing_system__how_does_it_dec.json`

---

## Query

Audit the ACI tier routing system: How does it decide which tier to use? What are the failure modes?

---

## Response

The ACI (Adaptive Context Intelligence) system aims to automatically select the optimal context tier for AI queries. This involves a sophisticated routing mechanism that analyzes the query, consults semantic graphs, and adheres to configured budgets and strategies.

Let's audit its tier routing system, how it decides which tier to use, and its potential failure modes.

### ACI Tier Routing System: How it Decides Which Tier to Use

The core of the ACI tier routing system is encapsulated in `tier_orchestrator.py` and heavily relies on input from `intent_parser.py`, `semantic_finder.py`, and `aci_config.yaml`. The `route_query` function orchestrates this decision-making process:

1.  **Query Analysis (`intent_parser.py`):**
    *   The `analyze_query` function categorizes the user's input into a `QueryProfile`, which includes:
        *   **Intent:** What is the user trying to achieve (e.g., `ARCHITECTURE`, `DEBUG`, `RESEARCH`, `COUNT`, `TASK`). This is detected using keywords and phrases, which are configurable in `aci_config.yaml` (`intent_keywords`).
        *   **Complexity:** How deep or broad is the query (`SIMPLE`, `MODERATE`, `COMPLEX`). This is determined by keywords like "all", "entire", "single", etc., also configurable in `aci_config.yaml` (`complexity`).
        *   **Scope:** Does the answer primarily reside within the codebase (`INTERNAL`), require external knowledge (`EXTERNAL`), or both (`HYBRID`)? (`external_indicators` in `aci_config.yaml` are key here).
        *   **Needs Agent Context:** Is the query related to agent tasks or internal operations (checked against `agent_context/trigger_keywords` in `aci_config.yaml`).
        *   **Suggested Sets:** Initial suggestions for analysis sets based on intent and keywords.

2.  **Semantic Matching (`semantic_finder.py`):**
    *   The `semantic_match` function leverages the "Standard Model relationship graph" to enrich the context selection. It maps keywords to:
        *   **Purpose (π₂):** The functional intent (e.g., Retrieve, Transform, Validate).
        *   **Architecture Layer:** (e.g., Interface, Application, Core, Infrastructure).
        *   **Roles:** Domain-Driven Design roles.
        *   **Traversal Direction:** For graph exploration (`UPSTREAM`, `DOWNSTREAM`, `BOTH`).
    *   This matching provides additional `suggested_sets` and `suggested_files` to ensure coherent context loading and determines `context_flow` ("laminar" for coherent, "turbulent" for mixed) and `traversal_strategy`.

3.  **Routing Overrides (`aci_config.yaml`):**
    *   `aci_config.yaml` contains a `routing_overrides` section. If a query matches specific patterns defined here, it can *force* a specific tier (e.g., "how many * files" always goes to `instant` tier). These overrides take precedence.

4.  **FLASH_DEEP Tier Triggers (`tier_orchestrator.py`):**
    *   Before consulting the main routing matrix, `_is_flash_deep_query` checks for keywords like "comprehensive", "entire codebase", or requests for multiple domains (e.g., "pipeline" and "architecture" and "agent"). If these are present and the scope is internal, the query is immediately routed to `Tier.FLASH_DEEP` (2M context).

5.  **Routing Matrix Lookup (`tier_orchestrator.py`):**
    *   The system then uses a predefined `ROUTING_MATRIX` (a dictionary) to map the `(QueryIntent, QueryComplexity, QueryScope)` tuple from the `QueryProfile` to a specific `Tier` and a `reasoning` string. For example:
        *   `(COUNT, SIMPLE, INTERNAL)` -> `Tier.INSTANT`
        *   `(LOCATE, SIMPLE, INTERNAL)` -> `Tier.RAG`
        *   `(ARCHITECTURE, ANY, INTERNAL)` -> `Tier.LONG_CONTEXT`
        *   `(RESEARCH, ANY, EXTERNAL)` -> `Tier.PERPLEXITY`

6.  **Default Routing (`tier_orchestrator.py`):**
    *   If no match is found in the `ROUTING_MATRIX`, a default tier is chosen based on scope: `PERPLEXITY` for external, `HYBRID` for hybrid, and `LONG_CONTEXT` for internal queries.

7.  **Context Set Consolidation and Sanitization (`tier_orchestrator.py`):**
    *   The `_determine_sets` function (based on the `QueryProfile` and chosen tier) and `_merge_sets_ordered` (integrating semantic suggestions) combine to form `primary_sets`.
    *   Tier-specific logic exists, e.g., `TASK` queries on `LONG_CONTEXT` automatically include `agent_full`, and `FLASH_DEEP` attempts to include all major analysis sets.
    *   `inject_agent_context` (from `context_builder.py`, called by `optimize_context` after routing) is used if `profile.needs_agent_context` is true, ensuring agent-specific sets are positioned favorably.
    *   Finally, `sanitize_sets` (in `tier_orchestrator.py`) applies `SET_ALIASES` (from `aci_config.yaml` indirectly) to map invalid semantic matcher outputs to valid analysis sets, dedupes, and caps the number of sets to `max_sets` (default 5) to prevent invalid sets from crowding out valid ones.

8.  **`use_truths` Flag (`tier_orchestrator.py`):**
    *   `_should_use_truths` determines if `repo_truths.yaml` should be checked first (e.g., always for `COUNT` queries, or simple `LOCATE`/`EXPLAIN`).

9.  **Fallback Tier Determination (`tier_orchestrator.py`):**
    *   `_get_fallback_tier` defines a progression (e.g., `INSTANT` -> `RAG` -> `LONG_CONTEXT` -> `FLASH_DEEP`), providing a plan B if the primary tier fails.

The entire process generates a `RoutingDecision` object containing the chosen tier, primary sets, fallback tier, and reasoning.

### Failure Modes of ACI Tier Routing

Despite its comprehensive design, the ACI tier routing system has several potential failure modes:

1.  **Incorrect Query Analysis (Source: `intent_parser.py`, `aci_config.yaml`):**
    *   **Misclassification:** If `analyze_query` incorrectly identifies the `intent`, `complexity`, or `scope` due to ambiguous phrasing in the query or an incomplete/outdated keyword configuration in `aci_config.yaml`, the query will be routed to an inappropriate tier.
    *   **Inaccurate Suggested Sets:** Poor keyword extraction or mapping in `_suggest_sets` can lead to the selection of irrelevant `primary_sets`, even if the tier is correct.

2.  **Suboptimal Semantic Matching (Source: `semantic_finder.py`):**
    *   **Stale Graph Data:** The Standard Model relationship graph (which `semantic_finder` queries) might be out-of-date or incomplete, leading to `semantic_match` returning irrelevant `SemanticTarget`s, `suggested_sets`, or `suggested_files`. This would result in suboptimal context flow (`turbulent` instead of `laminar`) or incorrect traversal strategies.
    *   **Circular Import Fallback:** If `semantic_finder` cannot properly import `compute_semantic_distance`, its ability to score nodes for attention gating will be impaired, affecting context relevance.

3.  **Context Budget Exceedance (Source: `context_builder.py`, `aci_config.yaml`):**
    *   **Over-budget Allocation:** Even if a tier is selected, the `estimate_tokens_for_sets` function in `context_builder.py` might calculate an `estimated_tokens` count that exceeds the `hard_cap` (defined in `aci_config.yaml`). This triggers a `budget_warning` but doesn't prevent routing. Such queries are highly susceptible to "lost-in-middle" effects or API errors due to truncation. The `perilous` budget explicitly highlights this.
    *   **Misconfigured Budgets:** If `aci_config.yaml` sets `token_budgets` too low for a given role (e.g., `architect`), it might inadvertently limit the AI's ability to perform multi-file reasoning, leading to partial or incorrect answers.

4.  **API/Service Unavailability or Performance Issues (Source: `tier_orchestrator.py`, external APIs):**
    *   **Gemini API Failure:** `get_model_token_limit` relies on the Gemini API. If the API is unreachable, it falls back to `_TOKEN_LIMIT_DEFAULTS`. If these defaults are outdated or incorrect for a specific model (e.g., `gemini-2.0-flash-thinking-exp`'s actual limit changes), the system might make routing decisions based on incorrect token capacities.
    *   **External Service Failure:** If `Tier.PERPLEXITY` is chosen but the external research service (Perplexity AI) is unavailable, rate-limited, or times out, the query will fail.

5.  **Incomplete or Stale `repo_truths.yaml` (Source: `context_builder.py`):**
    *   **Data Gaps:** `Tier.INSTANT` relies entirely on `load_repo_truths`. If `repo_truths.yaml` is missing, corrupt, or contains outdated information (e.g., incorrect file counts), `answer_from_truths` will return `None`, forcing a fallback to a more expensive and slower tier for simple `COUNT` queries.

6.  **Suboptimal Context Set Selection (Source: `tier_orchestrator.py`, `context_builder.py`):**
    *   **Aliasing Issues:** While `sanitize_sets` prevents invalid sets, the `SET_ALIASES` mapping could convert a user-intended, semantically valid but non-existent set name to a different, less relevant valid set name.
    *   **Too Few or Too Many Sets:** Capping sets at 5 (in `_suggest_sets` and `sanitize_sets`) might exclude critical context for `MODERATE` or `COMPLEX` queries, especially for non-`FLASH_DEEP` tiers. Conversely, too many sets for smaller context windows (before `optimize_context`'s compaction) can lead to "lost-in-middle" effects.

7.  **Circular Dependency Handling Issues (Source: `__init__.py`, `context_builder.py`, `intent_parser.py`):**
    *   The `_get_config` functions use lazy imports to avoid circular dependencies. If `ACI_CONFIG` fails to load (e.g., malformed `aci_config.yaml`, permission issues), the system will silently fall back to hardcoded defaults. This could lead to unexpected routing behavior, incorrect budget limits, or a lack of specific intent/complexity keyword recognition, effectively bypassing configured intelligence.

8.  **Feedback Loop Deficiencies (Source: `feedback_store.py`):**
    *   **Unmonitored Performance:** If the `FeedbackLoop` is disabled or its logged `high_retry_rate` or `high_avg_tokens` are not acted upon, the system loses its ability to learn from its mistakes and self-correct. Persistent suboptimal routing decisions (e.g., always choosing a tier that leads to retries) will go unaddressed.
    *   **Inadequate Metrics:** The current feedback loop logs `tokens_input` and `tokens_output`. If these don't accurately reflect the perceived "value" or quality of the AI's output, purely quantitative metrics might not lead to truly optimal routing adjustments.

In summary, the ACI tier routing system is designed with multiple layers of intelligence and fallback mechanisms. However, its effectiveness is highly dependent on the quality and freshness of its input data (query analysis, semantic graph, `repo_truths`), the robustness of its configurations in `aci_config.yaml`, and the availability and performance of underlying AI models and external services. Vigilance in monitoring feedback and maintaining configuration and semantic graph data is crucial to prevent these failure modes.

---

## Citations

_No citations provided_
