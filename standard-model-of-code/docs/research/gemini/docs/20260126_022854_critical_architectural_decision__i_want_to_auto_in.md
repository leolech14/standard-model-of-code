# Research: Critical architectural decision: I want to AUTO-INJECT context into Claude's workflow WITHOUT requir...

> **Date:** 2026-01-26 02:28:54
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:6dc2a6ae176cbe1be5898dc650a2960fe9c558b8e1f3528d0c54a566faf2cf24`
> **Raw JSON:** `raw/20260126_022854_critical_architectural_decision__i_want_to_auto_in.json`

---

## Query

Critical architectural decision: I want to AUTO-INJECT context into Claude's workflow WITHOUT requiring tool calls. Options: 1) Pre-hook injection (user-prompt-submit-hook), 2) MCP resource auto-loading, 3) System prompt dynamic refresh, 4) CLAUDE.md @imports. Which is best for: a terminal-based intel feed that provides meters, available cards, session state, alerts BEFORE the LLM starts thinking. The goal is zero agentic overhead - context is ALREADY THERE like a pilot's instrument panel. What are the tradeoffs? What's the recommended pattern?

---

## Response

Based on the `PROJECT_elements` architecture—specifically the **ACI (Adaptive Context Intelligence)** system and the **Observer Realm (.agent/)**—here is the architectural recommendation.

### Executive Decision: Option 1 (Pre-hook Injection via CLI Wrapper)

For a "pilot's instrument panel" (zero latency, zero tool use, always visible), **Pre-hook Injection via the `./pe` CLI wrapper** is the only viable architecture.

**Why:**
1.  **Zero-Shot Awareness:** The LLM sees the state *before* it generates the first token.
2.  **No Tool Loop:** Options 2 (MCP) often require the model to *decide* to look at a resource, or rely on client-specific auto-attach implementations that are flaky.
3.  **Dynamic vs. Static:** `CLAUDE.md` is for *policy* (static). The Instrument Panel is for *state* (dynamic).
4.  **Codome/Contextome Alignment:** This effectively creates a transient "Session Contextome" that exists only for the duration of the turn.

---

### The Tradeoff Analysis

| Pattern | Latency | Agency Cost | Best For | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **1. Pre-hook Injection** | **Zero** | **Zero** | **State, Meters, Alerts** | **🏆 WINNER** |
| **2. MCP Auto-load** | Low | Low/Med | Large Ref Docs, Logs | Good for "Library", not "HUD" |
| **3. System Prompt** | Zero | High (Reset) | Personality, Core Laws | Too rigid for changing state |
| **4. CLAUDE.md** | Zero | None | Static Policy, Formatting | Impossible for real-time state |

### The "Context HUD" Pattern

You should implement a **Context Compositor** inside your `./pe` entry point. When a user runs `./pe ask "fix the bug"`, the system does not send "fix the bug" to the LLM. It sends:

```xml
<instrument_panel>
  <meters>
    <focus>5/10</focus>
    <rigor>8/10</rigor>
    <drift>CRITICAL (Doc/Code mismatch)</drift>
  </meters>
  <session>
    <active_task>TASK-124: Refactor Auth</active_task>
    <sprint_status>EXECUTING</sprint_status>
  </session>
  <deck>
    <available_cards>
      <card id="CARD-ANA-001">Deep Analysis</card>
      <card id="CARD-REF-002">Safe Refactor</card>
    </available_cards>
  </deck>
  <alerts>
    <alert level="high">AM002 Violation detected in src/core/pipeline.py</alert>
  </alerts>
</instrument_panel>

<user_query>
fix the bug
</user_query>
```

### Implementation Plan

This fits directly into your **ACI (Adaptive Context Intelligence)** system defined in `context-management/config/aci_config.yaml`.

#### 1. Define the HUD Source
Create a lightweight aggregator in `context-management/tools/ai/aci/hud_builder.py` that pulls strictly from `.agent/` (Observer realm).

*   **Input:** `.agent/state/meters.yaml`, `.agent/registry/active/*.yaml`, `.agent/state/play_log.yaml`
*   **Output:** Compact XML string.

#### 2. Modify the CLI Entry Point (`./pe`)
Update your `./pe` wrapper (Layer 1 abstraction) to invoke the HUD builder before constructing the payload.

```python
# Pseudo-code for ./pe or context-management/tools/ai/analyze.py

def construct_final_prompt(user_query):
    hud = aci.hud_builder.build(
        include_meters=True,
        include_deck=True, 
        verbosity="compact" # Keep token cost low
    )
    return f"{hud}\n\nUser Query: {user_query}"
```

#### 3. Update `aci_config.yaml`
Add a section to control HUD density to manage token costs.

```yaml
# context-management/config/aci_config.yaml

instrument_panel:
  enabled: true
  format: "xml"
  elements:
    meters: true
    active_task: true
    deck_hand: true    # Only show playable cards
    full_registry: false # Too large, force tool use
  injection_strategy: "prepend_user_message"
```

### Why this fits PROJECT_elements

1.  **Observability (Axiom G):** The HUD satisfies the "Complete Observability" axiom in `CODESPACE_ALGEBRA.md`. It forces the "Secondness" (actual brute facts of the session) into the "Thirdness" (interpretation) of the LLM.
2.  **Symmetry:** It prevents the **AMNESIAC** state defined in your glossary (Code exists, Intent recorded, but Human/Agent has no structural memory). The HUD bridges the memory gap instantly.
3.  **Cost:** It uses the **Instant Tier** (cached truths) logic from ACI to build the string, incurring $0 computation cost and minimal token cost.

### Recommendation

**Do not use MCP for the Instrument Panel.** Use MCP for the *Library* (looking up docs/code). Use **Pre-hook Injection** for the *Cockpit* (meters/state).

**Action Item:** Create `context-management/tools/ai/aci/hud_builder.py` and wire it into the `analyze.py` prompt construction flow immediately.

---

## Citations

_No citations provided_
