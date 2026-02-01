# Archived Dead Code - 2026-01-25

Files archived during loose ends audit.

## history_loader.py

**Original location:** `wave/tools/ai/aci/history_loader.py`
**LOC:** 469
**Reason:** Never imported or called anywhere in codebase. Designed for Claude Code conversation mining but no consumer code was ever written.

**Exports that were never used:**
- `HistoryLoader` class
- `HistoryConfig` dataclass
- `ConversationTurn` dataclass
- `SessionSummary` dataclass

**Recovery:** If needed, move back to original location and add import to `aci/__init__.py`

## task_v2.schema.yaml

**Original location:** `.agent/schema/task_v2.schema.yaml`
**Reason:** Orphaned schema with no consumers. `task.schema.yaml` is the actual schema used by task registry code.

**Recovery:** If this was intended as an upgrade path, document the migration plan and restore.

---

*Archived by: Claude Opus 4.5*
*Audit: SKEPTICAL_AUDIT_REPORT_20260125.md*
