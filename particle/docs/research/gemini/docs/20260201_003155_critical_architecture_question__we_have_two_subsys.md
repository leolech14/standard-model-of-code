# Research: CRITICAL ARCHITECTURE QUESTION: We have TWO SUBSYSTEMS.yaml files:

1. ./SUBSYSTEMS.yaml (ROOT)
2. ....

> **Date:** 2026-02-01 00:31:55
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:02f54e53defef9658815c85e431ae1ebe4bba785d97c1e68fadb5e2d3815cd82`
> **Raw JSON:** `raw/20260201_003155_critical_architecture_question__we_have_two_subsys.json`

---

## Query

CRITICAL ARCHITECTURE QUESTION: We have TWO SUBSYSTEMS.yaml files:

1. ./SUBSYSTEMS.yaml (ROOT)
2. ./wave/config/registries/SUBSYSTEMS.yaml (NESTED)

They have DIFFERENT content (diff shows divergence in paths).

Questions:
1. Which is the CANONICAL locus for SUBSYSTEMS.yaml?
2. What code/configs IMPORT or READ from each location?
3. Should we consolidate to ONE location? Which one?
4. What is the architectural principle - should registries live at root or in subsystem?

Check: DOMAINS.yaml location, REPO_STRUCTURE.md references, any Python imports of these files.

---

## Response

Based on the codebase analysis, here is the architectural ruling regarding the `SUBSYSTEMS.yaml` conflict.

### 1. Which is the CANONICAL locus?

**The Canonical Locus is: `./SUBSYSTEMS.yaml` (ROOT)**

**Evidence:**
1.  **Freshness:** The Root file header states `Updated: 2026-01-27`. The `META_REGISTRY.yaml` (which points to the nested file) was last updated `2026-01-23`. The Root file is the most recent intent.
2.  **Symmetry:** `DOMAINS.yaml` (Code↔Context symmetry) lives at the Root. `SUBSYSTEMS.yaml` (Architecture definition) belongs at the same level of hierarchy.
3.  **Content Authority:** The Root file explicitly contains the header: `# SUBSYSTEMS REGISTRY - Single Source of Truth`.

**The Conflict:**
`.agent/META_REGISTRY.yaml` is currently **out of date**. It points to the nested file:
```yaml
subsystems: "wave/config/registries/SUBSYSTEMS.yaml"
```
This is a "pointer drift" issue—the registry moved, but the pointer wasn't updated.

### 2. Who reads what?

Currently, the system is in a **Fractured State**:

*   **The Agent/Human (Governance):** Looks at `./SUBSYSTEMS.yaml` (Root) because it's visible and claims to be the source of truth.
*   **The Tools (`refinery`, `analyze.py`):** Likely read the **NESTED** file because they rely on `.agent/META_REGISTRY.yaml` to resolve paths.
    *   Specifically, `wave/tools/refinery/subsystem_registry.py` (invoked by `./pe refinery subsystems`) likely loads the path defined in `META_REGISTRY.yaml`.
*   **The CLI (`./pe`):** Is agnostic, but routes commands to tools that are reading the stale file.

### 3. Consolidation Strategy

**Consolidate to ONE location: `./SUBSYSTEMS.yaml` (ROOT).**

**Migration Steps:**
1.  **Merge Data:** Ensure any specific details (like specific config paths) in the *Nested* file are preserved in the *Root* file.
2.  **Update Pointer:** Modify `.agent/META_REGISTRY.yaml` to point `meta.subsystems` to `./SUBSYSTEMS.yaml`.
3.  **Refactor Paths:** Grep `wave/` for hardcoded paths to `config/registries/SUBSYSTEMS.yaml` and replace them with a lookup via `META_REGISTRY` or a relative path to Root.
4.  **Delete:** Remove `wave/config/registries/SUBSYSTEMS.yaml`.

### 4. The Architectural Principle

**Principle: Topological Hierarchy**

A registry cannot be strictly *contained* by the thing it defines if it also defines that thing's siblings.

*   **Bad Topology:** `wave` (The Brain) contains `SUBSYSTEMS.yaml`.
    *   *Why:* `SUBSYSTEMS.yaml` defines `particle` (The Body). The Body should not depend on a config file buried inside The Brain.
*   **Good Topology:** `PROJECT_elements/SUBSYSTEMS.yaml` (Root).
    *   *Why:* The Root (Governance Layer) sits *above* both Particle (Body) and Wave (Brain). It defines the boundaries for both.

### Summary of Action Required

You should run the following immediately to align the system:

```bash
# 1. Update META_REGISTRY to point to the correct source of truth
sed -i '' 's|wave/config/registries/SUBSYSTEMS.yaml|SUBSYSTEMS.yaml|' .agent/META_REGISTRY.yaml

# 2. (Manual Step) Compare content and merge unique fields from nested to root
# diff wave/config/registries/SUBSYSTEMS.yaml SUBSYSTEMS.yaml

# 3. Delete the phantom file
# rm wave/config/registries/SUBSYSTEMS.yaml
```

---

## Citations

_No citations provided_
