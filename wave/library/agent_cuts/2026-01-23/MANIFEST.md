# Archive Manifest: CUT-2026-01-23-001

> Human-readable inventory of archived files from Bulk-to-Lean transition.

**Date:** 2026-01-23
**Operator:** claude-opus-4-5-20251101
**Machine-readable:** See `PROVENANCE.yaml`

---

## Summary

| Category | Count | Reason |
|----------|-------|--------|
| Dead Weight | 2 | Historical snapshots with no consumer |
| Misplaced | 1 | Experiment docs in wrong location |
| Superseded | 1 | Content migrated to new system |
| **Total** | **4** | |

---

## Archived Files

### 1. Truths History (DEAD_WEIGHT)

Two historical truth snapshots that were never consumed by any system:

| Original | Archive |
|----------|---------|
| `.agent/intelligence/truths/history/truths_20260123_052327.yaml` | `truths_history/truths_20260123_052327.yaml` |
| `.agent/intelligence/truths/history/truths_20260123_052436.yaml` | `truths_history/truths_20260123_052436.yaml` |

**Rationale:** The BARE TruthValidator doesn't use historical snapshots. These accumulate without purpose.

**Restore:**
```bash
cp archive/agent_cuts/2026-01-23/truths_history/*.yaml .agent/intelligence/truths/history/
```

### 2. Testing Suite (MISPLACED)

| Original | Archive |
|----------|---------|
| `.agent/workflows/testing_suite.md` | `workflows/testing_suite.md` |

**Rationale:** Describes 100+ repo experiment methodology, not core agent workflow. Belongs in research docs, not agent workflows.

**Restore:**
```bash
cp archive/agent_cuts/2026-01-23/workflows/testing_suite.md .agent/workflows/
```

### 3. Open Concerns (SUPERSEDED)

| Original | Archive |
|----------|---------|
| `.agent/OPEN_CONCERNS.md` | `OPEN_CONCERNS.md` |

**Rationale:** Content migrated to sprint system. Sprint discipline now active via:
- `.agent/sprints/SPRINT-001.yaml`
- `.agent/specs/BACKGROUND_AUTO_REFINEMENT_ENGINE.md`

**Restore:**
```bash
cp archive/agent_cuts/2026-01-23/OPEN_CONCERNS.md .agent/
```

---

## Restoration Protocol

To restore any file:

1. Verify it's needed (check `PROVENANCE.yaml` for why it was archived)
2. Run the restore command from repo root
3. Update relevant registries if applicable
4. Document the restoration decision

---

## Related

- **Plan:** `.agent/specs/CUTTING_PLAN.md`
- **Task:** `.agent/registry/active/TASK-004.yaml`
- **Provenance:** `archive/agent_cuts/2026-01-23/PROVENANCE.yaml`
