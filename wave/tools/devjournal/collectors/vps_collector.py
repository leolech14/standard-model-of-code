"""
VPS Collector — tracks OpenClaw activity on the VPS via SSH.

Connects to the VPS over Tailscale and reads:
  - /root/.openclaw/cron/runs/ — cron job execution logs
  - /root/.openclaw/voice-calls/ — voice call transcripts
  - /root/.claude/history.jsonl — VPS Claude CLI activity

Falls back gracefully if SSH is unavailable (VPS offline, no Tailscale).
"""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

_devjournal = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_devjournal))
from schema import (
    CollectorResult, DevJournalEvent, EventKind, Signature, Source,
    generate_oid,
)

VPS_HOST = "100.119.234.42"  # Tailscale IP
VPS_USER = "root"
SSH_TIMEOUT = 10

CRON_RUNS_PATH = "/root/.openclaw/cron/runs"
VOICE_CALLS_PATH = "/root/.openclaw/voice-calls"
VPS_CLI_HISTORY = "/root/.claude/history.jsonl"


def _ssh_cmd(cmd: str) -> Optional[str]:
    """Run a command on the VPS via SSH. Returns stdout or None."""
    try:
        result = subprocess.run(
            [
                "ssh", "-o", "ConnectTimeout=5",
                "-o", "StrictHostKeyChecking=no",
                "-o", "BatchMode=yes",
                f"{VPS_USER}@{VPS_HOST}",
                cmd,
            ],
            capture_output=True,
            text=True,
            timeout=SSH_TIMEOUT,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None


def _check_connectivity() -> bool:
    """Quick check if VPS is reachable via SSH."""
    return _ssh_cmd("echo ok") == "ok"


def _collect_cron_runs(date_str: str) -> List[DevJournalEvent]:
    """Collect cron job execution events from the VPS."""
    events = []

    # List run files for the target date
    out = _ssh_cmd(f"ls {CRON_RUNS_PATH}/ 2>/dev/null | grep {date_str}")
    if not out:
        # Try reading a runs.jsonl or similar aggregate
        out = _ssh_cmd(
            f"cat {CRON_RUNS_PATH}/runs.jsonl 2>/dev/null | grep {date_str}"
        )
        if not out:
            return events

        for line in out.split("\n"):
            line = line.strip()
            if not line:
                continue
            try:
                run = json.loads(line)
            except json.JSONDecodeError:
                continue

            ts_str = run.get("ts") or run.get("timestamp") or run.get("startedAt", "")
            try:
                ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            except (ValueError, TypeError):
                continue

            if ts.strftime("%Y-%m-%d") != date_str:
                continue

            oid = generate_oid(
                ts, "openclaw", "cron_executed",
                f"cron-{run.get('jobId', 'unknown')}-{ts_str}",
            )

            events.append(DevJournalEvent(
                oid=oid,
                ts=ts,
                source=Source.OPENCLAW,
                kind=EventKind.CRON_EXECUTED,
                project="PROJECT_openclaw",
                data={
                    "job_id": run.get("jobId", "unknown"),
                    "action": run.get("action", ""),
                    "status": run.get("status", ""),
                    "summary": str(run.get("summary", ""))[:200],
                    "duration_ms": run.get("durationMs", 0),
                },
                tags=["cron", "openclaw", run.get("status", "unknown")],
                signature=Signature(
                    model="cron",
                    access_point="vps-ssh",
                    orchestration="automated",
                    hostname="vps",
                ),
            ))
        return events

    # Individual run files
    for filename in out.split("\n"):
        filename = filename.strip()
        if not filename:
            continue
        content = _ssh_cmd(f"cat {CRON_RUNS_PATH}/{filename} 2>/dev/null")
        if not content:
            continue
        try:
            run = json.loads(content)
        except json.JSONDecodeError:
            continue

        ts_str = run.get("ts") or run.get("timestamp", "")
        try:
            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            continue

        oid = generate_oid(
            ts, "openclaw", "cron_executed",
            f"cron-{run.get('jobId', 'unknown')}-{filename}",
        )

        events.append(DevJournalEvent(
            oid=oid,
            ts=ts,
            source=Source.OPENCLAW,
            kind=EventKind.CRON_EXECUTED,
            project="PROJECT_openclaw",
            data={
                "job_id": run.get("jobId", "unknown"),
                "action": run.get("action", ""),
                "status": run.get("status", ""),
                "summary": str(run.get("summary", ""))[:200],
                "duration_ms": run.get("durationMs", 0),
            },
            tags=["cron", "openclaw"],
            signature=Signature(
                model="cron",
                access_point="vps-ssh",
                orchestration="automated",
                hostname="vps",
            ),
        ))

    return events


def _collect_voice_calls(date_str: str) -> List[DevJournalEvent]:
    """Collect voice call events from the VPS."""
    events = []

    out = _ssh_cmd(
        f"find {VOICE_CALLS_PATH} -name '*.json' -newer /tmp/ets-{date_str}-start "
        f"-not -newer /tmp/ets-{date_str}-end 2>/dev/null"
    )
    # Simpler approach: list and grep
    out = _ssh_cmd(f"ls {VOICE_CALLS_PATH}/ 2>/dev/null | grep {date_str}")
    if not out:
        return events

    for filename in out.split("\n"):
        filename = filename.strip()
        if not filename:
            continue
        content = _ssh_cmd(f"cat {VOICE_CALLS_PATH}/{filename} 2>/dev/null")
        if not content:
            continue
        try:
            call = json.loads(content)
        except json.JSONDecodeError:
            continue

        ts_str = call.get("timestamp") or call.get("startedAt", "")
        try:
            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            continue

        oid = generate_oid(
            ts, "openclaw", "voice_call",
            f"call-{call.get('callId', filename)}",
        )

        events.append(DevJournalEvent(
            oid=oid,
            ts=ts,
            source=Source.OPENCLAW,
            kind=EventKind.VOICE_CALL,
            project="PROJECT_openclaw",
            data={
                "call_id": call.get("callId", ""),
                "provider": call.get("provider", ""),
                "direction": call.get("direction", ""),
                "state": call.get("state", ""),
                "from": call.get("from", ""),
                "to": call.get("to", ""),
                "duration_seconds": call.get("durationSeconds", 0),
                "transcript": str(call.get("transcript", ""))[:500],
            },
            tags=["voice", "openclaw", call.get("direction", "unknown")],
        ))

    return events


def _collect_vps_cli(date_str: str) -> List[DevJournalEvent]:
    """Collect VPS Claude CLI history entries."""
    events = []

    # Read history.jsonl from VPS, filter to target date
    target_date = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    day_start_ms = int(target_date.timestamp() * 1000)
    day_end_ms = day_start_ms + 86_400_000

    out = _ssh_cmd(f"cat {VPS_CLI_HISTORY} 2>/dev/null")
    if not out:
        return events

    for line in out.split("\n"):
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue

        ts_ms = entry.get("timestamp", 0)
        if not (day_start_ms <= ts_ms < day_end_ms):
            continue

        ts = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
        display = entry.get("display", "")
        if not display:
            continue

        session_id = entry.get("sessionId", "")
        data_key = f"vps:{ts_ms}:{display[:50]}"
        oid = generate_oid(ts, "vps", "prompt", data_key)

        events.append(DevJournalEvent(
            oid=oid,
            ts=ts,
            source=Source.VPS,
            kind=EventKind.PROMPT,
            project="PROJECT_openclaw",
            data={
                "display": display[:500],
                "char_count": len(display),
                "session_id": session_id,
                "hostname": "vps",
            },
            tags=["vps", "cli"],
        ))

    return events


def collect(date_str: str) -> CollectorResult:
    """Run the VPS collector for a target date.

    Connects via SSH to the VPS and collects cron runs, voice calls,
    and CLI history. Fails gracefully if VPS is unreachable.
    """
    all_events: List[DevJournalEvent] = []
    stats: Dict[str, Any] = {"vps_reachable": False}

    if not _check_connectivity():
        stats["error"] = "VPS unreachable (SSH timeout)"
        return CollectorResult(
            source=Source.VPS,
            target_date=date_str,
            events=[],
            stats=stats,
        )

    stats["vps_reachable"] = True

    # Collect from all three sources
    cron_events = _collect_cron_runs(date_str)
    voice_events = _collect_voice_calls(date_str)
    cli_events = _collect_vps_cli(date_str)

    all_events.extend(cron_events)
    all_events.extend(voice_events)
    all_events.extend(cli_events)
    all_events.sort(key=lambda e: e.ts)

    stats.update({
        "cron_events": len(cron_events),
        "voice_events": len(voice_events),
        "cli_events": len(cli_events),
        "total_events": len(all_events),
    })

    return CollectorResult(
        source=Source.VPS,
        target_date=date_str,
        events=all_events,
        stats=stats,
    )


if __name__ == "__main__":
    from datetime import date
    target = sys.argv[1] if len(sys.argv) > 1 else date.today().isoformat()
    result = collect(target)
    print(f"VPS collector: {len(result.events)} events")
    print(f"  Reachable: {result.stats.get('vps_reachable', False)}")
    print(f"  Cron: {result.stats.get('cron_events', 0)}")
    print(f"  Voice: {result.stats.get('voice_events', 0)}")
    print(f"  CLI: {result.stats.get('cli_events', 0)}")
    if result.stats.get("error"):
        print(f"  Error: {result.stats['error']}")
