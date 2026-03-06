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
    for col_name, col_type in _COLUMNS:
        try:
            conn.execute(f"ALTER TABLE analysis_runs ADD COLUMN {col_name} {col_type}")
        except Exception:
            pass  # Column already exists
    conn.commit()
    return True


def down(backend) -> bool:
    """SQLite cannot DROP COLUMN before 3.35.0; skip rollback."""
    return False
