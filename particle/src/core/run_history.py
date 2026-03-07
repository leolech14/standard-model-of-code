"""
Collider Run History Manager.

Manages the full lifecycle of Collider run artifacts:
1. Indexing  -- append-only run_index.jsonl in central sink
2. Retention -- prune old feedback, snapshots, and stale outputs by count
3. Trending  -- read index and report score progression
4. Backfill  -- bootstrap index from existing feedback files

The SQLite backend (purge_old_runs) handles DB row retention.
This module handles *filesystem* artifact retention -- the part that was missing.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


_DEFAULT_RETENTION = {
    "local_feedback": 5,        # timestamped triples in <repo>/.collider/feedback/
    "central_sink": 10,         # per-repo files in central collider_feedback/
    "concordance_snapshots": 3, # .collider/concordance_history/snapshot_*.json
    "stale_outputs": 1,         # output_llm-oriented_*, output_human-readable_*
}

_INDEX_FILENAME = "run_index.jsonl"

# Feedback file prefixes (each run produces a triple)
_FEEDBACK_PREFIXES = (
    "collider_feedback_auto_",
    "ai-user-audit_",
    "collider_feedback_report_",
)

# Central sink prefixes (slug prepended)
_CENTRAL_SUFFIXES = (
    "_auto_feedback_",
    "_ai_user_audit_",
    "_feedback_report_",
)

# Stale output patterns in .collider/ root
_STALE_OUTPUT_GLOBS = (
    "output_llm-oriented_*.json",
    "output_human-readable_*.html",
)


class RunHistoryManager:
    """Manages Collider run history: index, prune, trend, backfill."""

    def __init__(
        self,
        central_sink: Path,
        retention: dict[str, int] | None = None,
    ):
        self.central_sink = Path(central_sink)
        self.retention = {**_DEFAULT_RETENTION, **(retention or {})}
        self._index_path = self.central_sink / _INDEX_FILENAME

    # ── Indexing ─────────────────────────────────────────────

    def record_run(self, auto_feedback: dict[str, Any]) -> None:
        """Append one run entry to the index from an auto_feedback payload."""
        findings = auto_feedback.get("findings_by_severity", {})
        counts = auto_feedback.get("counts", {})
        repo_raw = auto_feedback.get("repo", "")
        repo_slug = _slug(Path(repo_raw).name) if repo_raw else "unknown"

        entry = {
            "ts": auto_feedback.get("ts", _utc_iso()),
            "repo": repo_slug,
            "grade": auto_feedback.get("grade", "?"),
            "health_score": auto_feedback.get("health_score"),
            "nodes": counts.get("nodes", 0),
            "edges": counts.get("edges", 0),
            "critical": findings.get("critical", 0),
            "high": findings.get("high", 0),
            "medium": findings.get("medium", 0),
            "low": findings.get("low", 0),
            "run_mode": auto_feedback.get("run_mode", "unknown"),
        }

        self.central_sink.mkdir(parents=True, exist_ok=True)
        with open(self._index_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, separators=(",", ":")) + "\n")

    # ── Retention ────────────────────────────────────────────

    def prune_local_feedback(self, feedback_dir: Path, keep: int | None = None) -> list[str]:
        """Delete timestamped feedback files beyond keep limit in local feedback dir."""
        keep = keep if keep is not None else self.retention["local_feedback"]
        return _prune_timestamped_groups(
            directory=feedback_dir,
            prefixes=_FEEDBACK_PREFIXES,
            keep=keep,
        )

    def prune_central_sink(self, repo_slug: str, keep: int | None = None) -> list[str]:
        """Delete oldest central sink files for a repo beyond keep limit."""
        keep = keep if keep is not None else self.retention["central_sink"]
        prefixes = tuple(f"{repo_slug}{suffix}" for suffix in _CENTRAL_SUFFIXES)
        return _prune_timestamped_groups(
            directory=self.central_sink,
            prefixes=prefixes,
            keep=keep,
        )

    def prune_concordance_snapshots(self, collider_dir: Path, keep: int | None = None) -> list[str]:
        """Delete oldest concordance snapshots beyond keep limit."""
        keep = keep if keep is not None else self.retention["concordance_snapshots"]
        history_dir = collider_dir / "concordance_history"
        if not history_dir.is_dir():
            return []
        snapshots = sorted(history_dir.glob("snapshot_*.json"))
        return _delete_oldest(snapshots, keep)

    def prune_stale_outputs(self, collider_dir: Path, keep: int | None = None) -> list[str]:
        """Delete all but latest output_llm-oriented_* and output_human-readable_* files."""
        keep = keep if keep is not None else self.retention["stale_outputs"]
        deleted: list[str] = []
        for pattern in _STALE_OUTPUT_GLOBS:
            files = sorted(collider_dir.glob(pattern))
            deleted.extend(_delete_oldest(files, keep))
        return deleted

    def record_and_prune(
        self,
        auto_feedback: dict[str, Any],
        feedback_dir: Path,
        collider_dir: Path,
    ) -> dict[str, Any]:
        """Full lifecycle: record run to index + enforce all retention policies."""
        repo_raw = auto_feedback.get("repo", "")
        repo_slug = _slug(Path(repo_raw).name) if repo_raw else "unknown"

        self.record_run(auto_feedback)

        pruned: dict[str, list[str]] = {}
        pruned["local_feedback"] = self.prune_local_feedback(feedback_dir)
        pruned["central_sink"] = self.prune_central_sink(repo_slug)
        pruned["concordance"] = self.prune_concordance_snapshots(collider_dir)
        pruned["stale_outputs"] = self.prune_stale_outputs(collider_dir)

        total = sum(len(v) for v in pruned.values())
        return {"pruned_count": total, "pruned": pruned}

    # ── Trend Reporting ──────────────────────────────────────

    def get_trend(self, repo_slug: str | None = None, last_n: int = 10) -> list[dict[str, Any]]:
        """Read index and return last N runs, optionally filtered by repo."""
        if not self._index_path.is_file():
            return []

        entries: list[dict[str, Any]] = []
        with open(self._index_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    if repo_slug and entry.get("repo") != repo_slug:
                        continue
                    entries.append(entry)
                except json.JSONDecodeError:
                    continue

        return entries[-last_n:]

    def print_trend(self, repo_slug: str | None = None, last_n: int = 10) -> None:
        """Print formatted trend table to stdout."""
        entries = self.get_trend(repo_slug, last_n)
        if not entries:
            print("  No run history found.")
            if not self._index_path.is_file():
                print("  Run `collider-hub history --backfill` to index existing feedback files.")
            return

        # Header
        print(f"  {'Timestamp':<22} {'Grade':>5} {'Score':>6} {'Nodes':>6} {'Edges':>6} "
              f"{'Crit':>5} {'High':>5} {'Med':>5} {'Delta':>7}")
        print(f"  {'─' * 75}")

        prev_score = None
        for e in entries:
            ts = e.get("ts", "?")[:19]
            grade = e.get("grade", "?")
            score = e.get("health_score")
            score_str = f"{score:.2f}" if score is not None else "?"
            nodes = e.get("nodes", 0)
            edges = e.get("edges", 0)
            crit = e.get("critical", 0)
            high = e.get("high", 0)
            med = e.get("medium", 0)

            delta = ""
            if prev_score is not None and score is not None:
                d = score - prev_score
                if d > 0:
                    delta = f"+{d:.2f}"
                elif d < 0:
                    delta = f"{d:.2f}"
            prev_score = score

            print(f"  {ts:<22} {grade:>5} {score_str:>6} {nodes:>6} {edges:>6} "
                  f"{crit:>5} {high:>5} {med:>5} {delta:>7}")

    # ── Backfill ─────────────────────────────────────────────

    def backfill_index(self) -> int:
        """Scan existing central sink feedback files and populate index for any not yet indexed."""
        if not self.central_sink.is_dir():
            return 0

        # Load already-indexed timestamps to avoid duplicates
        indexed_keys: set[str] = set()
        if self._index_path.is_file():
            with open(self._index_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        indexed_keys.add(f"{entry.get('repo')}:{entry.get('ts')}")
                    except json.JSONDecodeError:
                        continue

        # Find all auto_feedback files in central sink
        feedback_files = sorted(self.central_sink.glob("*_auto_feedback_*.json"))
        added = 0

        for fpath in feedback_files:
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except (json.JSONDecodeError, OSError):
                continue

            repo_raw = data.get("repo", "")
            repo_slug = _slug(Path(repo_raw).name) if repo_raw else _slug_from_filename(fpath.name)
            ts = data.get("ts", "")
            key = f"{repo_slug}:{ts}"

            if key in indexed_keys:
                continue

            self.record_run(data)
            indexed_keys.add(key)
            added += 1

        return added


# ── Helpers ──────────────────────────────────────────────────


def _slug(name: str) -> str:
    """Convert repo/dir name to slug for filename matching."""
    return name.lower().replace(" ", "-").replace("_", "-")


def _slug_from_filename(filename: str) -> str:
    """Extract repo slug from central sink filename like 'project-openclaw_auto_feedback_...'."""
    for suffix in _CENTRAL_SUFFIXES:
        idx = filename.find(suffix)
        if idx >= 0:
            return filename[:idx]
    return filename.split("_")[0]


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _prune_timestamped_groups(
    directory: Path,
    prefixes: tuple[str, ...],
    keep: int,
) -> list[str]:
    """
    Prune timestamped file groups. Files sharing a timestamp form a group (triple).
    Keep the newest `keep` groups, delete the rest.
    """
    if not directory.is_dir() or keep <= 0:
        return []

    # Collect timestamps from the first prefix pattern
    primary_prefix = prefixes[0]
    primary_files = sorted(directory.glob(f"{primary_prefix}*"))

    if len(primary_files) <= keep:
        return []

    # Extract timestamps from filenames: prefix{TIMESTAMP}.ext
    timestamps_to_delete: list[str] = []
    for f in primary_files[:-keep]:
        # Extract timestamp portion from filename
        name = f.stem  # without extension
        ts_part = name[len(primary_prefix):]
        timestamps_to_delete.append(ts_part)

    deleted: list[str] = []
    for ts in timestamps_to_delete:
        for prefix in prefixes:
            for match in directory.glob(f"{prefix}{ts}*"):
                try:
                    match.unlink()
                    deleted.append(str(match))
                except OSError:
                    continue
    return deleted


def _delete_oldest(files: list[Path], keep: int) -> list[str]:
    """Delete all but the last `keep` files from a sorted list."""
    if len(files) <= keep or keep <= 0:
        return []
    deleted: list[str] = []
    for f in files[:-keep]:
        try:
            f.unlink()
            deleted.append(str(f))
        except OSError:
            continue
    return deleted
