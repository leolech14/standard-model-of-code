# Research: LOW CONFIDENCE AUDIT for consolidation tasks. Review these tasks and identify risks:

TASK-101 (80% ...

> **Date:** 2026-01-31 19:53:06
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:71c90cefa485173f3a3328c58f8c8213dd0bba418e604ee838f18e8b5e42a443`
> **Raw JSON:** `raw/20260131_195306_low_confidence_audit_for_consolidation_tasks__revi.json`

---

## Query

LOW CONFIDENCE AUDIT for consolidation tasks. Review these tasks and identify risks:

TASK-101 (80% confidence): Triage 18 untracked Python tools
- Factual: 85% (need to verify each file's purpose)
- Current: 80% (may have undocumented dependencies)

TASK-103 (85% confidence): Deduplicate intelligence directories (7 to 2)
- Current: 85% (code may reference old paths)

TASK-104 (85% confidence): Consolidate research directories  
- Onwards: 85% (may need re-split if growth)

TASK-105 (85% confidence): Unify reports directories (6 to 1)
- Current: 85% (CI/CD may depend on paths)

TASK-106 (80% confidence): Standardize archive naming
- Current: 80% (.archive hidden may be intentional)

For each: 1) Validate confidence, 2) Identify risks, 3) Actions to reach 95%+

---

## Response

Here is the **Low Confidence Audit** for the proposed consolidation tasks.

**General Assessment:** The risks identified are valid. The primary danger in consolidation is **Path Dependency Coupling**—where subsystems (especially the `pe` CLI, `analyze.py`, and `DOMAINS.yaml`) rely on hardcoded paths that you are about to change.

In `PROJECT_elements`, "Code is Law," but "Paths are Geography." changing geography breaks the maps (`DOMAINS.yaml`).

---

### TASK-101: Triage 18 untracked Python tools
**Current Confidence:** 80%
**Status:** **Valid**. The risk is high because "untracked" tools are often used by `autopilot.py` or ephemeral agent sessions.

1.  **Validate Confidence:**
    *   **Confirmed 80%.** The system uses dynamic imports and script execution (see `.agent/tools/wire.py` and `concierge.py`). A tool might look unused but be called via `subprocess` in a macro.

2.  **Specific Risks:**
    *   **Implicit Dependencies:** `context-management/tools/ai/aci/refinery.py` or `analyze.py` might invoke these tools dynamically based on strings (e.g., the `pe` router matching patterns).
    *   **Agent State Loss:** Some tools might be local state holders for `autopilot.py`.

3.  **Actions to Reach 95% (Grade A+):**
    *   **Grep Audit:** Run `grep -r "filename.py" .` for every candidate file to ensure zero references in `src/` or `.agent/`.
    *   **Import Audit:** Check `context-management/tools/__init__.py` or similar aggregators.
    *   **Quarantine Strategy:** Move them to `.agent/registry/archive/quarantine/` first. If nothing breaks in 48h, delete.

---

### TASK-103: Deduplicate intelligence directories (7 to 2)
**Current Confidence:** 85%
**Status:** **Optimistic**. Actual confidence is likely **75%**.

1.  **Validate Confidence:**
    *   **Downgrade to 75%.** `DOMAINS.yaml` specifically lists `context-management/intelligence` as a canonical path for the "Governance" domain. `SUBSYSTEMS.yaml` points "TEMPORAL_INTELLIGENCE" to `.agent/intelligence`. Merging these touches the "nervous system" of the project.

2.  **Specific Risks:**
    *   **Health Check Failure:** `DOMAINS.yaml` health checks will fail immediately if paths move.
    *   **Data Loss:** `tdj.jsonl` (Temporal Data) and `socratic_audit_pipeline_*.json` are configured in `.gitignore` at specific paths. Moving them might expose them to git or break the `.gitignore` exclusion patterns.

3.  **Actions to Reach 95% (Grade A+):**
    *   **Map Update:** You *must* update `DOMAINS.yaml` and `SUBSYSTEMS.yaml` simultaneously with the move.
    *   **Gitignore Sync:** Verify `.gitignore` rules (lines 100-110) match the new target structure exactly.
    *   **Config Check:** Grep `config/` for `intelligence_dir` or similar keys in `analyze.py`.

---

### TASK-104: Consolidate research directories
**Current Confidence:** 85%
**Status:** **Valid**.

1.  **Validate Confidence:**
    *   **Confirmed 85%.** `CODOME_MANIFEST.yaml` explicitly lists `standard-model-of-code/docs/research/perplexity/` and `gemini/`.

2.  **Specific Risks:**
    *   **Agent Write Paths:** `analyze.py` and `perplexity_mcp_server.py` likely have hardcoded default output directories. If you move the directory, agents might recreate the old one, leading to split-brain research storage.
    *   **Manifest Drift:** The `CODOME_MANIFEST.yaml` will become inaccurate immediately.

3.  **Actions to Reach 95% (Grade A+):**
    *   **Update Sources:** Modify `context-management/config/analysis_sets.yaml` or the relevant `analyze.py` constants to point to the new single location.
    *   **Update Manifest:** Task *must* include updating `CODOME_MANIFEST.yaml` "research" section.

---

### TASK-105: Unify reports directories (6 to 1)
**Current Confidence:** 85%
**Status:** **Valid**.

1.  **Validate Confidence:**
    *   **Confirmed 85%.** The `pe` script (lines 142 and 336) specifically looks for `.collider/` to run the visualization server (`cmd_viz`).

2.  **Specific Risks:**
    *   **Viz Failure:** If you consolidate to `reports/` instead of `.collider/`, `./pe viz` will fail to serve the 3D graph.
    *   **Collider Output:** `output_generator.py` in Collider defaults to specific paths. Changing the folder requires passing specific flags (`--output`) every time or refactoring the default.

3.  **Actions to Reach 95% (Grade A+):**
    *   **Select Target:** Choose `.collider/` as the winner (it is the `pe` default).
    *   **Symlink Legacy:** Create a temporary symlink from `reports/` → `.collider/` to catch lingering references.
    *   **Refactor Collider:** Ensure `full_analysis.py` defaults to this path.

---

### TASK-106: Standardize archive naming
**Current Confidence:** 80%
**Status:** **Valid**.

1.  **Validate Confidence:**
    *   **Confirmed 80%.** `SUBSYSTEMS.yaml` lists `standard-model-of-code/archive/` as a subsystem root.

2.  **Specific Risks:**
    *   **Collider Scope:** The Collider has logic to ignore hidden directories (starting with `.`). If you rename `.archive` to `archive`, the Collider might suddenly try to parse legacy code as active code, bloating node counts and causing parsing errors.
    *   **GCS Mirror:** The `archive.py` tool (`.agent/tools/archive/archive.py`) needs to know exactly where to look to sync to GCS.

3.  **Actions to Reach 95% (Grade A+):**
    *   **Exclusion Check:** If renaming to `archive` (visible), explicitly add `archive/` to `exclude_patterns` in `standard-model-of-code/src/core/full_analysis.py` or `.gitignore`.
    *   **Subsystem Update:** Update `SUBSYSTEMS.yaml` "ARCHIVE" entry to reflect the new canonical path.

---

### Summary of Prerequisites for 95% Confidence

To elevate these tasks to **Grade A+ (Ready to Execute)**, you must generate a **Configuration Migration Commit** that updates these maps *before* moving files:

1.  `DOMAINS.yaml` (Paths for Governance, Pipelines)
2.  `SUBSYSTEMS.yaml` (Roots for Intelligence, Archive)
3.  `CODOME_MANIFEST.yaml` (Research paths)
4.  `.gitignore` (Update exclusion patterns for new locations)

---

## Citations

_No citations provided_
