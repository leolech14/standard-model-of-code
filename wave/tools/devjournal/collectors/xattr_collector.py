"""
xattr Collector — reads ETS signature metadata from macOS extended attributes.

Scans recently modified files in PROJECTS_all for the com.ets.signature
extended attribute. This attribute contains JSON with Signature Protocol
fields stamped directly on files.

This is the READ side of the xattr Signature Protocol.
The WRITE side stamps files via: xattr -w com.ets.signature '{"model":...}' <file>
"""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

_devjournal = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_devjournal))
from schema import (
    CollectorResult, DevJournalEvent, EventKind, Signature, Source,
    PROJECTS_ROOT, FS_NOISE_DIRS, FS_NOISE_EXTENSIONS, generate_oid,
)

ETS_XATTR_KEY = "com.ets.signature"


def _read_xattr(file_path: str) -> Optional[str]:
    """Read an extended attribute value from a file."""
    try:
        result = subprocess.run(
            ["xattr", "-p", ETS_XATTR_KEY, file_path],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def _should_skip(path: Path) -> bool:
    """Check if a path should be skipped (noise dirs/extensions)."""
    for part in path.parts:
        if part in FS_NOISE_DIRS:
            return True
    if path.suffix in FS_NOISE_EXTENSIONS:
        return True
    return False


def _find_recent_files(date_str: str) -> List[Path]:
    """Find files in PROJECTS_all modified on the target date.

    Uses a targeted approach: only check files with xattrs, not all files.
    We use mdfind (Spotlight) for efficiency on macOS.
    """
    # Use mdfind to find files with our xattr that were modified on target date
    # Fallback: walk top-level project dirs for recently modified files
    recent = []

    if not PROJECTS_ROOT.is_dir():
        return recent

    for d in sorted(PROJECTS_ROOT.iterdir()):
        if not d.name.startswith("PROJECT_") or not d.is_dir():
            continue

        # Check recently modified files (top 2 levels deep for performance)
        for depth_glob in ["*", "*/*", "*/*/*"]:
            for f in d.glob(depth_glob):
                if not f.is_file():
                    continue
                if _should_skip(f):
                    continue
                try:
                    stat = f.stat()
                    mtime = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
                    if mtime.strftime("%Y-%m-%d") == date_str:
                        recent.append(f)
                except OSError:
                    continue

        # Cap per-project to avoid scanning massive repos
        if len(recent) > 5000:
            break

    return recent


def collect(date_str: str) -> CollectorResult:
    """Run the xattr collector for a target date.

    Finds recently modified files and checks for com.ets.signature xattr.
    """
    all_events: List[DevJournalEvent] = []
    files_checked = 0
    xattrs_found = 0

    recent_files = _find_recent_files(date_str)

    for file_path in recent_files:
        files_checked += 1

        xattr_value = _read_xattr(str(file_path))
        if not xattr_value:
            continue

        xattrs_found += 1

        try:
            sig_data = json.loads(xattr_value)
        except json.JSONDecodeError:
            continue

        try:
            stat = file_path.stat()
            ts = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
        except OSError:
            continue

        # Extract project name from path
        project_name = None
        for part in file_path.parts:
            if part.startswith("PROJECT_"):
                project_name = part
                break

        # Build Signature
        signature = None
        if sig_data.get("model"):
            signature = Signature(
                model=sig_data.get("model", "unknown"),
                access_point=sig_data.get("access_point", "unknown"),
                orchestration=sig_data.get("orchestration", "unknown"),
                session_id=sig_data.get("session_id"),
                hostname=sig_data.get("hostname", ""),
            )

        rel_path = str(file_path.relative_to(PROJECTS_ROOT)) if PROJECTS_ROOT in file_path.parents else str(file_path)
        oid = generate_oid(ts, "xattr", "signature_stamped", f"{rel_path}:{int(stat.st_mtime)}")

        all_events.append(DevJournalEvent(
            oid=oid,
            ts=ts,
            source=Source.XATTR,
            kind=EventKind.SIGNATURE_STAMPED,
            project=project_name,
            data={
                "file_path": str(file_path),
                "relative_path": rel_path,
                "xattr_key": ETS_XATTR_KEY,
                "signature_data": sig_data,
                "model": sig_data.get("model"),
                "size_bytes": stat.st_size,
            },
            tags=["xattr", "signature", sig_data.get("model", "unknown")],
            signature=signature,
        ))

    all_events.sort(key=lambda e: e.ts)

    return CollectorResult(
        source=Source.XATTR,
        target_date=date_str,
        events=all_events,
        stats={
            "files_checked": files_checked,
            "xattrs_found": xattrs_found,
        },
    )


if __name__ == "__main__":
    from datetime import date
    target = sys.argv[1] if len(sys.argv) > 1 else date.today().isoformat()
    result = collect(target)
    print(f"xattr collector: {len(result.events)} events")
    print(f"  Files checked: {result.stats.get('files_checked', 0)}")
    print(f"  xattrs found: {result.stats.get('xattrs_found', 0)}")
