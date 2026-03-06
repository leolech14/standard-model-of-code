"""
Migration v002: Add git context and delta columns to analysis_runs.

Stores git commit/branch/dirty state per run and inter-run delta summaries.
Idempotent: silently skips columns that already exist.
"""

VERSION = 2
DESCRIPTION = "Add git context and run delta tracking to analysis_runs"

_COLUMNS = [
    ("git_commit", "TEXT"),
    ("git_branch", "TEXT"),
    ("git_dirty", "INTEGER DEFAULT 0"),
    ("git_summary", "TEXT"),
    ("delta_json", "TEXT"),
]


def up(backend) -> bool:
    """Add git_commit, git_branch, git_dirty, git_summary, delta_json columns."""
    conn = backend._conn
    # Get existing columns to skip those already present
    cursor = conn.execute("PRAGMA table_info(analysis_runs)")
    existing = {row[1] for row in cursor.fetchall()}

    for col_name, col_type in _COLUMNS:
        if col_name in existing:
            continue
        try:
            conn.execute(f"ALTER TABLE analysis_runs ADD COLUMN {col_name} {col_type}")
        except Exception:
            pass  # Genuinely can't add — log but continue
    conn.commit()

    # Verify all columns were added
    cursor = conn.execute("PRAGMA table_info(analysis_runs)")
    final_cols = {row[1] for row in cursor.fetchall()}
    missing = [c for c, _ in _COLUMNS if c not in final_cols]
    if missing:
        print(f"   ⚠️ v002 migration: columns still missing after ALTER: {missing}")
        return False
    return True


def down(backend) -> bool:
    """SQLite cannot DROP COLUMN before 3.35.0; skip rollback."""
    return False
