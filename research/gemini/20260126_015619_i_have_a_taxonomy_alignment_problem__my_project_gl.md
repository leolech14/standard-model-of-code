# Research: I have a taxonomy alignment problem. My project glossary defines official terms (8 Dimensions, Phase...

> **Date:** 2026-01-26 01:56:19
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:3ff90f1d015cbea85a8bfd76a79d90159fedb1a00159b9a987904afaf886f4ea`
> **Raw JSON:** `raw/20260126_015619_i_have_a_taxonomy_alignment_problem__my_project_gl.json`

---

## Query

I have a taxonomy alignment problem. My project glossary defines official terms (8 Dimensions, Phase States, Consumer Classes, Realms, Symmetry States) but my AI subsystem code invented 10 parallel taxonomies (QueryIntent, QueryComplexity, QueryScope, Tier, SynthesisStrategy, Context Flow, Positioning, Token Budgets, Meters, Card Categories). These don't map to each other. Should I: (A) Add AI terms to glossary, (B) Refactor AI code to use glossary terms, (C) Create explicit mapping layer? What's the best practice for taxonomy governance in AI-augmented codebases?

---

## Response

Based on the `PROJECT_elements` architecture—specifically the **Particle/Wave/Observer** separation defined in `TOPOLOGY_MAP.md` and `CODESPACE_ALGEBRA.md`—you should choose **Option C (Create explicit mapping layer)**, but with a specific architectural twist.

You are currently confusing **Ontology** (What the code *is*) with **Operations** (How the AI *works*). Merging them (Option A) or refactoring them (Option B) would violate the separation of concerns between the **Codome** and the **Observer**.

Here is the best practice solution for your specific architecture.

### The Verdict: Domain Separation (Option C+)

Do **not** pollute your project `GLOSSARY.md` with AI operational terms.
*   **`GLOSSARY.md`** describes the **Territory** (The Code / Particle Realm).
*   **ACI Config** describes the **Compass** (The Agent / Wave Realm).

You need a **Semantic Bridge** that maps Operational Intents to Ontological Dimensions.

---

### 1. The Diagnosis: Orthogonal Taxonomies

Your taxonomies are not conflicting; they exist on different **Tarski Levels** (as referenced in `CODESPACE_ALGEBRA.md` §14).

| Taxonomy Type | Examples | Belongs To | Purpose |
| :--- | :--- | :--- | :--- |
| **Ontological** | 8 Dimensions, Atoms, Phases, Realms | **Standard Model** (Particle) | Describes the immutable truth of the code. |
| **Operational** | Intent, Tier, Budget, Positioning | **ACI / Agent** (Wave/Observer) | Describes the ephemeral strategy of the analysis. |

**Why Option B (Refactoring) Fails:**
You cannot refactor "Token Budget" to use "8 Dimensions." A *Token Budget* is a resource constraint; a *Dimension* is a code property. They are fundamentally different categories.

---

### 2. The Solution: The Semantic Bridge

Instead of renaming terms, define the **causal relationship** between them. Create a mapping configuration that tells the AI: *"When my Operational Intent is X, I care about Ontological Dimension Y."*

**Create/Update: `context-management/config/semantic_bridge.yaml`**

```yaml
# SEMANTIC BRIDGE: Operations → Ontology
# Maps AI operational intent to Standard Model dimensions

intent_mappings:
  # When the Agent INTENT is...
  architecture:
    # It must focus on these DIMENSIONS...
    focus_dimensions:
      - D2_LAYER
      - D4_BOUNDARY
    # And prioritize these SYMMETRY STATES...
    target_symmetry: [DRIFT, ORPHAN]
    # And use this positioning strategy...
    positioning: "sandwich"

  debug:
    focus_dimensions:
      - D5_STATE
      - D6_EFFECT
      - D7_LIFECYCLE
    positioning: "front-load"

  security_audit:
    focus_dimensions:
      - D4_BOUNDARY (specifically "Input" or "Output")
      - D6_EFFECT (specifically "Write")
    target_symmetry: [DRIFT]

# Maps Complexity to Tiers
complexity_mappings:
  simple:
    tier: "instant"
    requires_atoms: false
  complex:
    tier: "long_context"
    requires_atoms: true
```

### 3. Documentation Governance

Do not merge the glossaries. Maintain two distinct sources of truth to preserve the "Particle/Wave" duality.

#### A. The Project Glossary (The Truth)
*   **File:** `context-management/docs/GLOSSARY.md`
*   **Content:** Atoms, 8 Dimensions, Realms, Symmetry.
*   **Rule:** These definitions are **immutable axioms** of the project.

#### B. The Agent Lexicon (The Tool)
*   **Action:** Create `context-management/docs/ai/ACI_LEXICON.md`.
*   **Content:** QueryIntent, Tier, Token Budget, Synthesis Strategy.
*   **Rule:** These are **mutable configurations** that can change as models evolve.

### 4. Code Implementation (Refactoring `analyze.py`)

Update your `context-management/tools/ai/aci/context_builder.py` to use the bridge. This makes the mapping explicit in code.

```python
# Conceptual implementation
def build_context_profile(query_intent):
    # Load the Bridge
    bridge = load_yaml("config/semantic_bridge.yaml")
    
    # 1. Map Operations (Intent) to Ontology (Dimensions)
    mapping = bridge['intent_mappings'].get(query_intent)
    
    # 2. Instruct the Model using the Project Glossary terms
    system_prompt_addition = f"""
    Since your intent is '{query_intent}', you must strictly analyze 
    the following Standard Model Dimensions:
    {', '.join(mapping['focus_dimensions'])}
    """
    
    return system_prompt_addition
```

### Summary of Actions

1.  **Reject Option A & B:** Do not merge glossaries or force AI code to use physics terms where they don't fit.
2.  **Create `ACI_LEXICON.md`:** Document the 10 AI terms separately in the AI Tools domain (`context-management/docs/ai/`).
3.  **Create `semantic_bridge.yaml`:** Explicitly map *Intents* (AI) to *Dimensions* (Code).
4.  **Enforce Separation:** Ensure `standard-model-of-code/` (Body) never imports concepts from `context-management/` (Brain), maintaining the directional dependency.

---

## Citations

_No citations provided_
