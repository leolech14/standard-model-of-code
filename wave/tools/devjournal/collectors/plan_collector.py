"""
Plan Collector — tracks Claude plan file creation and updates.

Scans ~/.claude/plans/ for files modified on the target date.
Extracts plan title from the first markdown heading.
Emits PLAN_CREATED or PLAN_UPDATED events.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

_devjournal = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_devjournal))
from schema import (
    CollectorResult, DevJournalEvent, EventKind, Source,
    generate_oid,
)

PLANS_DIR = Path.home() / ".claude" / "plans"


def _extract_plan_title(file_path: Path) -> str:
    """Extract the plan title from the first heading in a plan file."""
    try:
        with open(file_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("# "):
                    # Remove "# Plan: " prefix if present
                    title = line.lstrip("# ").strip()
                    if title.lower().startswith("plan:"):
                        title = title[5:].strip()
                    return title[:150]
        return file_path.stem
    except (OSError, UnicodeDecodeError):
        return file_path.stem


def _is_on_date(ts: datetime, date_str: str) -> bool:
    """Check if a timestamp falls on the target date."""
    return ts.strftime("%Y-%m-%d") == date_str


def collect(date_str: str) -> CollectorResult:
    """Run the plan collector for a target date.

    Scans ~/.claude/plans/*.md files, checking mtime against the target date.
    """
    all_events: List[DevJournalEvent] = []
    files_scanned = 0

    if not PLANS_DIR.is_dir():
        return CollectorResult(
            source=Source.PLAN,
            target_date=date_str,
            events=[],
            stats={"error": "Plans directory not found"},
        )

    for plan_file in sorted(PLANS_DIR.glob("*.md")):
        files_scanned += 1

        try:
            stat = plan_file.stat()
            mtime = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
            ctime = datetime.fromtimestamp(stat.st_birthtime, tz=timezone.utc)
        except (OSError, AttributeError):
            continue

        if not _is_on_date(mtime, date_str):
            continue

        title = _extract_plan_title(plan_file)

        # Determine if new or updated
        is_new = abs((ctime - mtime).total_seconds()) < 2
        kind = EventKind.PLAN_CREATED if is_new else EventKind.PLAN_UPDATED

        oid = generate_oid(
            mtime, "plan", kind.value,
            f"{plan_file.name}:{int(stat.st_mtime)}",
        )

        tags = ["plan"]
        if is_new:
            tags.append("new")

        all_events.append(DevJournalEvent(
            oid=oid,
            ts=mtime,
            source=Source.PLAN,
            kind=kind,
            project=None,  # Plans are ecosystem-wide
            data={
                "plan_name": title,
                "file_path": str(plan_file),
                "file_name": plan_file.name,
                "size_bytes": stat.st_size,
                "is_new": is_new,
            },
            tags=tags,
        ))

    all_events.sort(key=lambda e: e.ts)

    return CollectorResult(
        source=Source.PLAN,
        target_date=date_str,
        events=all_events,
        stats={
            "files_scanned": files_scanned,
            "plans_found": len(all_events),
            "new_plans": sum(1 for e in all_events if e.kind == EventKind.PLAN_CREATED),
            "updated_plans": sum(1 for e in all_events if e.kind == EventKind.PLAN_UPDATED),
        },
    )


if __name__ == "__main__":
    from datetime import date
    target = sys.argv[1] if len(sys.argv) > 1 else date.today().isoformat()
    result = collect(target)
    print(f"Plan collector: {len(result.events)} events from {result.stats.get('files_scanned', 0)} files")
    print(f"  New: {result.stats.get('new_plans', 0)}")
    print(f"  Updated: {result.stats.get('updated_plans', 0)}")
