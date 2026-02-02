# GAP_REGISTER - Consolidation Contradictions

> **Purpose:** Track mismatches between declared structure and repo reality.
> **Updated:** 2026-02-02

## GAP-001: OBSERVER Realm Definition Conflict

- **Claim (SUBSYSTEMS.yaml):** OBSERVER rooted in `.agent/` (governance, deck, intelligence).
- **Claim (REPO_STRUCTURE.json):** OBSERVER rooted in `observer/` (Control Room UI).
- **Reality:** Both directories exist with different semantics.
- **Impact:** Confuses onboarding and realm mapping.
- **Status:** OPEN (needs canonical decision).

## GAP-002: Missing `models/` Directory

- **Claim (REPO_STRUCTURE.json):** `models/` exists at repo root.
- **Reality:** No `models/` directory present at repo root.
- **Impact:** Declared structure is stale or incomplete.
- **Status:** OPEN.

## GAP-003: AGENT_KERNEL Reference Mismatch

- **Claim (wave/docs/legacy_root_scatter/CLAUDE.md):** `wave/docs/operations/AGENT_KERNEL.md` exists.
- **Reality:** File does not exist; canonical kernel now in `wave/docs/agent_school/AGENT_KERNEL.md`.
- **Impact:** Broken onboarding path.
- **Status:** RESOLVED (updated reference).

## GAP-004: Concierge Command Drift

- **Claim (wave/docs/agent_school/TUTORIAL.md):** `./concierge` exists.
- **Reality:** Concierge entrypoint is `./.agent/concierge_cli`.
- **Impact:** New agents cannot run the tutorial verbatim.
- **Status:** RESOLVED (command corrected).

## GAP-005: PROJECTOME File Counts Drift

- **Claim (wave/docs/PROJECTOME.md):** ~850 total files.
- **Reality (wave/data/repo_map/repo_map_latest.json):** 3469 files mapped.
- **Impact:** Counts are stale; affects trust in metrics.
- **Status:** OPEN.
