"""
REH Meta Envelope — longitudinal tracking for evolution analysis.

Mirrors Collider's meta_envelope.py pattern. Produces a standard identity
block embedded in every output tier, enabling cross-run joins.

Storage: <repo>/.reh/meta_index.jsonl (append-only, one JSON line per run)
"""

import hashlib
import json
import socket
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


SCHEMA_VERSION = "1.0.0"
REH_VERSION = "1.0.0"


def build_reh_envelope(
    repo_path: str,
    date_range: Dict[str, str],
    commit_count: int = 0,
    file_count: int = 0,
    capability_count: int = 0,
    velocity_cpw: float = 0.0,
    trajectory: str = "unknown",
    analysis_time_ms: int = 0,
) -> Dict[str, Any]:
    """Build identity + provenance envelope for REH output."""
    target = Path(repo_path).resolve()
    repo_id = hashlib.sha256(str(target).encode()).hexdigest()[:12]

    return {
        "repo_id": repo_id,
        "run_id": str(uuid.uuid4()),
        "run_ts": datetime.now(timezone.utc).isoformat(),
        "reh_version": REH_VERSION,
        "schema_version": SCHEMA_VERSION,
        "target": target.name,
        "target_path": str(target),
        "date_range": date_range,
        "commit_count": commit_count,
        "file_count": file_count,
        "capability_count": capability_count,
        "velocity_commits_per_week": round(velocity_cpw, 2),
        "trajectory": trajectory,
        "analysis_time_ms": analysis_time_ms,
        "hostname": socket.gethostname(),
    }


def append_to_reh_index(
    envelope: Dict[str, Any],
    output_dir: Path,
) -> Path:
    """Append envelope as one JSON line to .reh/meta_index.jsonl."""
    output_dir.mkdir(parents=True, exist_ok=True)
    index_path = output_dir / "meta_index.jsonl"
    line = json.dumps(envelope, default=str, sort_keys=True)
    with open(index_path, "a") as f:
        f.write(line + "\n")
    return index_path
