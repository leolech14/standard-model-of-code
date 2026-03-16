"""
FS Collector — scans key directories for file births and modifications.

Uses mtime/ctime to detect filesystem activity on the target date.
Scans: PROJECTS_all, Downloads, _inbox, music-production, 3d-workshop.
"""

import os
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Set

_devjournal = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_devjournal))
from schema import (
    CollectorResult, DevJournalEvent, EventKind, Source,
    FS_SCAN_DIRS, FS_NOISE_DIRS, FS_NOISE_EXTENSIONS, generate_oid,
)

# Max depth to scan inside directories (prevents deep traversal of node_modules etc.)
MAX_DEPTH = 4
# Max files to report per scanned directory
MAX_FILES_PER_DIR = 200


def _should_skip(name: str) -> bool:
    """Check if a file/dir name is noise."""
    return name in FS_NOISE_DIRS or name.startswith(".")


def _should_skip_ext(path: Path) -> bool:
    """Check if a file extension is noise."""
    return path.suffix.lower() in FS_NOISE_EXTENSIONS


def _get_dir_label(path: Path) -> str:
    """Get a human-readable label for a scanned directory."""
    home = Path.home()
    try:
        rel = path.relative_to(home)
        return str(rel)
    except ValueError:
        return str(path)


def _scan_dir(
    scan_root: Path,
    date_str: str,
    max_depth: int = MAX_DEPTH,
) -> List[DevJournalEvent]:
    """Scan a directory tree for files created or modified on target date."""
    events = []
    target_date = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    day_start = target_date.timestamp()
    day_end = day_start + 86_400

    if not scan_root.is_dir():
        return events

    dir_label = _get_dir_label(scan_root)
    file_count = 0

    for root, dirs, files in os.walk(scan_root):
        # Respect max depth
        depth = len(Path(root).relative_to(scan_root).parts)
        if depth > max_depth:
            dirs.clear()
            continue

        # Skip noise directories
        dirs[:] = [d for d in dirs if not _should_skip(d)]

        for fname in files:
            if file_count >= MAX_FILES_PER_DIR:
                dirs.clear()
                break

            if _should_skip(fname):
                continue

            fpath = Path(root) / fname
            if _should_skip_ext(fpath):
                continue

            try:
                stat = fpath.stat()
            except (OSError, PermissionError):
                continue

            mtime = stat.st_mtime
            # On macOS, st_birthtime is available for creation time
            ctime = getattr(stat, "st_birthtime", stat.st_ctime)

            is_created = day_start <= ctime < day_end
            is_modified = day_start <= mtime < day_end and not is_created

            if not is_created and not is_modified:
                continue

            try:
                rel_path = str(fpath.relative_to(scan_root))
            except ValueError:
                rel_path = str(fpath)

            ts = datetime.fromtimestamp(
                ctime if is_created else mtime,
                tz=timezone.utc,
            )
            kind = EventKind.FILE_CREATED if is_created else EventKind.FILE_MODIFIED

            # Determine project name if under PROJECTS_all
            project = None
            try:
                parts = fpath.relative_to(Path.home() / "PROJECTS_all").parts
                if parts and parts[0].startswith("PROJECT_"):
                    project = parts[0]
            except ValueError:
                pass

            oid = generate_oid(ts, "fs", kind.value, f"{dir_label}:{rel_path}")
            events.append(DevJournalEvent(
                oid=oid,
                ts=ts,
                source=Source.FS,
                kind=kind,
                project=project,
                data={
                    "path": rel_path,
                    "scan_root": dir_label,
                    "size_bytes": stat.st_size,
                    "extension": fpath.suffix.lower() or None,
                },
            ))
            file_count += 1

    return events


def collect(date_str: str) -> CollectorResult:
    """Run the filesystem collector for a target date.

    Args:
        date_str: Target date in YYYY-MM-DD format.

    Returns:
        CollectorResult with file_created and file_modified events.
    """
    all_events: List[DevJournalEvent] = []
    dir_stats: Dict[str, Dict[str, int]] = {}

    for scan_dir in FS_SCAN_DIRS:
        events = _scan_dir(scan_dir, date_str)
        all_events.extend(events)

        label = _get_dir_label(scan_dir)
        created = sum(1 for e in events if e.kind == EventKind.FILE_CREATED)
        modified = sum(1 for e in events if e.kind == EventKind.FILE_MODIFIED)
        dir_stats[label] = {"created": created, "modified": modified, "total": len(events)}

    # Sort by timestamp
    all_events.sort(key=lambda e: e.ts)

    # Extension distribution
    ext_counts: Dict[str, int] = defaultdict(int)
    for e in all_events:
        ext = e.data.get("extension")
        if ext:
            ext_counts[ext] += 1
    top_extensions = dict(sorted(ext_counts.items(), key=lambda x: -x[1])[:10])

    return CollectorResult(
        source=Source.FS,
        target_date=date_str,
        events=all_events,
        stats={
            "dirs_scanned": len(FS_SCAN_DIRS),
            "total_created": sum(1 for e in all_events if e.kind == EventKind.FILE_CREATED),
            "total_modified": sum(1 for e in all_events if e.kind == EventKind.FILE_MODIFIED),
            "by_directory": dir_stats,
            "top_extensions": top_extensions,
        },
    )


if __name__ == "__main__":
    from datetime import date
    target = sys.argv[1] if len(sys.argv) > 1 else date.today().isoformat()
    result = collect(target)
    print(f"FS collector: {len(result.events)} events")
    print(f"  Created: {result.stats.get('total_created', 0)}")
    print(f"  Modified: {result.stats.get('total_modified', 0)}")
    for d, s in result.stats.get("by_directory", {}).items():
        print(f"  {d}: {s}")
    print(f"  Top extensions: {result.stats.get('top_extensions', {})}")
