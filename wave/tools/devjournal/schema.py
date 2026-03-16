"""
DevJournal Schema — Pydantic models for the Refinery ingestion pipeline.

Every event is a tracked object with a deterministic oid.
Append-only ledger (devjournal.jsonl) + materialized daily views.
"""

import hashlib
import json
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ── Constants ──────────────────────────────────────────────

DEVJOURNAL_DIR = Path.home() / ".devjournal"
LEDGER_PATH = DEVJOURNAL_DIR / "devjournal.jsonl"
DAYS_DIR = DEVJOURNAL_DIR / "days"
WEEKS_DIR = DEVJOURNAL_DIR / "weeks"
PROJECTS_DIR = DEVJOURNAL_DIR / "projects"
META_INDEX_PATH = DEVJOURNAL_DIR / "meta_index.jsonl"

PROJECTS_ROOT = Path.home() / "PROJECTS_all"
CLI_HISTORY_PATH = Path.home() / ".claude" / "history.jsonl"

# Directories to scan for filesystem events
FS_SCAN_DIRS = [
    PROJECTS_ROOT,
    Path.home() / "Downloads",
    Path.home() / "_inbox",
    Path.home() / "music-production",
    Path.home() / "3d-workshop",
]

# Noise patterns to skip in filesystem scanning
FS_NOISE_DIRS = {
    "node_modules", ".git", ".venv", "__pycache__", ".next", ".cache",
    "dist", "build", ".reh", ".collider", ".agent", ".superpowers",
    ".DS_Store", ".Trash", "venv", "env", ".tox", ".mypy_cache",
    ".pytest_cache", "coverage", ".nyc_output", "target",
}
FS_NOISE_EXTENSIONS = {
    ".pyc", ".pyo", ".o", ".so", ".dylib", ".class", ".jar",
    ".lock", ".log", ".tmp", ".swp", ".swo",
}


# ── Enums ──────────────────────────────────────────────────

class Source(str, Enum):
    GIT = "git"
    CLI = "cli"
    FS = "fs"
    SESSION = "session"
    COLLIDER = "collider"
    ATLAS = "atlas"
    SYSTEM = "system"


class EventKind(str, Enum):
    # Git events
    COMMIT = "commit"
    FILE_BORN = "file_born"
    FILE_DELETED = "file_deleted"
    MILESTONE = "milestone"
    # CLI events
    PROMPT = "prompt"
    SESSION_START = "session_start"
    # Filesystem events
    FILE_CREATED = "file_created"
    FILE_MODIFIED = "file_modified"
    DIR_CREATED = "dir_created"
    # Future: session, collider, atlas, system events
    CONVERSATION = "conversation"
    ANALYSIS_RUN = "analysis_run"
    COMPONENT_REGISTERED = "component_registered"
    SYNC_COMPLETE = "sync_complete"


# ── OID Generation ─────────────────────────────────────────

def generate_oid(ts: datetime, source: str, kind: str, data_key: str) -> str:
    """Generate a deterministic, time-sortable object ID.

    Format: dj-{YYYYMMDDHHMMSS}{hash8}
    - Time-sortable (lexicographic = chronological)
    - Deterministic (same event → same oid → idempotent)
    - 25 chars total
    """
    ts_str = ts.strftime("%Y%m%d%H%M%S")
    hash_input = f"{source}:{kind}:{data_key}"
    hash8 = hashlib.sha256(hash_input.encode()).hexdigest()[:8]
    return f"dj-{ts_str}{hash8}"


# ── Core Models ────────────────────────────────────────────

class DevJournalEvent(BaseModel):
    """A single tracked event in the devjournal ledger."""
    oid: str
    ts: datetime
    source: Source
    kind: EventKind
    project: Optional[str] = None  # None for ecosystem-wide events
    data: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)

    def to_jsonl(self) -> str:
        """Serialize to a single JSONL line."""
        d = self.model_dump(mode="json")
        d["ts"] = self.ts.isoformat()
        d["source"] = self.source.value
        d["kind"] = self.kind.value
        return json.dumps(d, separators=(",", ":"), default=str)

    @classmethod
    def from_jsonl(cls, line: str) -> "DevJournalEvent":
        """Deserialize from a JSONL line."""
        d = json.loads(line)
        return cls(**d)


class CollectorResult(BaseModel):
    """Output from a collector — a batch of events."""
    source: Source
    collected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    target_date: str  # YYYY-MM-DD
    events: List[DevJournalEvent] = Field(default_factory=list)
    stats: Dict[str, Any] = Field(default_factory=dict)


class DailyDigest(BaseModel):
    """Materialized daily view for the Refinery dashboard."""
    date: str  # YYYY-MM-DD
    generated_at: datetime
    total_events: int = 0
    events_by_source: Dict[str, int] = Field(default_factory=dict)
    events_by_kind: Dict[str, int] = Field(default_factory=dict)
    events_by_project: Dict[str, int] = Field(default_factory=dict)
    timeline: List[Dict[str, Any]] = Field(default_factory=list)  # Hourly buckets
    projects_active: List[str] = Field(default_factory=list)
    milestones: List[Dict[str, Any]] = Field(default_factory=list)
    velocity: Dict[str, Any] = Field(default_factory=dict)
    highlights: List[Dict[str, Any]] = Field(default_factory=list)  # Top events


class RunEnvelope(BaseModel):
    """Metadata for each pipeline run — appended to meta_index.jsonl."""
    run_id: str
    run_ts: datetime
    target_date: str
    sources_run: List[str]
    total_events: int
    events_by_source: Dict[str, int]
    duration_ms: int
    hostname: str


# ── Utilities ──────────────────────────────────────────────

def ensure_dirs():
    """Create output directories if they don't exist."""
    for d in [DEVJOURNAL_DIR, DAYS_DIR, WEEKS_DIR, PROJECTS_DIR]:
        d.mkdir(parents=True, exist_ok=True)


def append_to_ledger(events: List[DevJournalEvent]):
    """Append events to the main JSONL ledger."""
    ensure_dirs()
    with open(LEDGER_PATH, "a") as f:
        for event in events:
            f.write(event.to_jsonl() + "\n")


def read_ledger_for_date(date_str: str) -> List[DevJournalEvent]:
    """Read all events for a specific date from the ledger."""
    events = []
    if not LEDGER_PATH.exists():
        return events
    with open(LEDGER_PATH) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                evt = DevJournalEvent.from_jsonl(line)
                if evt.ts.strftime("%Y-%m-%d") == date_str:
                    events.append(evt)
            except Exception:
                continue
    return events
