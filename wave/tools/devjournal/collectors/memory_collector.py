"""
Memory Collector — tracks Claude memory file creation and updates.

Scans ~/.claude/projects/*/memory/ directories for files modified on the
target date. Parses YAML frontmatter to extract name, type, and description.
Emits MEMORY_WRITTEN (new) or MEMORY_UPDATED events.

Distinguishes new vs updated by comparing file ctime to mtime:
- ctime == mtime (within 2s) → newly written
- ctime < mtime → updated
"""

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_devjournal = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_devjournal))
from schema import (
    CollectorResult, DevJournalEvent, EventKind, Source,
    generate_oid,
)

CLAUDE_PROJECTS_DIR = Path.home() / ".claude" / "projects"


def _parse_frontmatter(file_path: Path) -> Dict[str, str]:
    """Parse YAML frontmatter from a memory file.

    Expects files starting with --- delimiters containing key: value pairs.
    Returns dict of frontmatter fields.
    """
    fields = {}
    try:
        text = file_path.read_text(errors="replace")
        lines = text.split("\n")
        if not lines or lines[0].strip() != "---":
            return fields

        for line in lines[1:]:
            line = line.strip()
            if line == "---":
                break
            if ":" in line:
                key, _, value = line.partition(":")
                fields[key.strip()] = value.strip()
    except (OSError, UnicodeDecodeError):
        pass

    return fields


def _extract_project_from_dir(dir_name: str) -> Optional[str]:
    """Extract project name from a Claude projects directory name."""
    parts = dir_name.split("-")
    for i, part in enumerate(parts):
        if part == "PROJECT" and i + 1 < len(parts):
            return f"PROJECT_{parts[i + 1]}"
    return None


def _is_on_date(ts: datetime, date_str: str) -> bool:
    """Check if a timestamp falls on the target date."""
    return ts.strftime("%Y-%m-%d") == date_str


def collect(date_str: str) -> CollectorResult:
    """Run the memory collector for a target date.

    Scans all ~/.claude/projects/*/memory/*.md files, checking mtime
    against the target date. Parses frontmatter for metadata.
    """
    all_events: List[DevJournalEvent] = []
    files_scanned = 0
    memories_found = 0
    by_type: Dict[str, int] = {}

    if not CLAUDE_PROJECTS_DIR.is_dir():
        return CollectorResult(
            source=Source.MEMORY,
            target_date=date_str,
            events=[],
            stats={"error": "Claude projects directory not found"},
        )

    for project_dir in sorted(CLAUDE_PROJECTS_DIR.iterdir()):
        if not project_dir.is_dir():
            continue

        memory_dir = project_dir / "memory"
        if not memory_dir.is_dir():
            continue

        project_name = _extract_project_from_dir(project_dir.name)

        for md_file in sorted(memory_dir.glob("*.md")):
            # Skip the index file
            if md_file.name == "MEMORY.md":
                continue

            files_scanned += 1

            try:
                stat = md_file.stat()
                mtime = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
                ctime = datetime.fromtimestamp(stat.st_birthtime, tz=timezone.utc)
            except (OSError, AttributeError):
                continue

            if not _is_on_date(mtime, date_str):
                continue

            memories_found += 1

            # Parse frontmatter
            fm = _parse_frontmatter(md_file)
            mem_name = fm.get("name", md_file.stem)
            mem_type = fm.get("type", "unknown")
            mem_desc = fm.get("description", "")

            by_type[mem_type] = by_type.get(mem_type, 0) + 1

            # Determine if new or updated
            is_new = abs((ctime - mtime).total_seconds()) < 2
            kind = EventKind.MEMORY_WRITTEN if is_new else EventKind.MEMORY_UPDATED

            oid = generate_oid(
                mtime, "memory", kind.value,
                f"{project_dir.name}:{md_file.name}",
            )

            tags = ["memory", mem_type]
            if is_new:
                tags.append("new")

            all_events.append(DevJournalEvent(
                oid=oid,
                ts=mtime,
                source=Source.MEMORY,
                kind=kind,
                project=project_name,
                data={
                    "name": mem_name,
                    "type": mem_type,
                    "description": mem_desc[:200],
                    "file_path": str(md_file),
                    "file_name": md_file.name,
                    "size_bytes": stat.st_size,
                    "is_new": is_new,
                },
                tags=tags,
            ))

    all_events.sort(key=lambda e: e.ts)

    return CollectorResult(
        source=Source.MEMORY,
        target_date=date_str,
        events=all_events,
        stats={
            "files_scanned": files_scanned,
            "memories_found": memories_found,
            "new_memories": sum(1 for e in all_events if e.kind == EventKind.MEMORY_WRITTEN),
            "updated_memories": sum(1 for e in all_events if e.kind == EventKind.MEMORY_UPDATED),
            "by_type": by_type,
        },
    )


if __name__ == "__main__":
    from datetime import date
    target = sys.argv[1] if len(sys.argv) > 1 else date.today().isoformat()
    result = collect(target)
    print(f"Memory collector: {len(result.events)} events from {result.stats.get('files_scanned', 0)} files")
    print(f"  New: {result.stats.get('new_memories', 0)}")
    print(f"  Updated: {result.stats.get('updated_memories', 0)}")
    print(f"  By type: {result.stats.get('by_type', {})}")
