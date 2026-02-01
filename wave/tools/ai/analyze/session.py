"""
Session Module - Turn Logging and Session Management
=====================================================

Standard Model Classification:
-----------------------------
D1_KIND:     LOG.FNC.M (Logic Function Module)
D2_LAYER:    Infrastructure (persistence)
D3_ROLE:     Utility (logging helper)
D4_BOUNDARY: Output (writes to disk)
D5_STATE:    Stateful (accumulates session turns)
D6_EFFECT:   Impure (file writes)
D7_LIFECYCLE: Use (called during analysis)
D8_TRUST:    90 (simple logging)

RPBL: (2, 5, 3, 3)
    R=2: Two responsibilities (log turns, save session)
    P=5: File I/O with state accumulation
    B=3: Output boundary (writes logs)
    L=3: Session-lifetime state

Communication Theory:
    This module implements the AUDIT TRAIL - recording all
    interactions for later analysis and debugging.

    Source:   User/model turns
    Channel:  Memory buffer -> File
    Message:  Timestamped turn records
    Receiver: Future debugging sessions
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from .config import PROJECT_ROOT, GEMINI_RESEARCH_PATH


# Module-level state for session tracking
_session_turns: List[Dict[str, Any]] = []
_session_start_time: Optional[datetime] = None
_session_model: Optional[str] = None

# Environment variable for session logging
SESSION_LOG = os.environ.get('SESSION_LOG') == '1'


def log_turn(
    role: str,
    content: str,
    truncate: int = 500,
    tokens_in: int = 0,
    tokens_out: int = 0
) -> None:
    """
    Log a conversation turn.

    In Communication Theory terms, this captures each message
    in the user<->model channel for later analysis.

    Args:
        role: "user" or "assistant"
        content: Turn content
        truncate: Max chars to show in stderr log
        tokens_in: Input token count (if known)
        tokens_out: Output token count (if known)
    """
    global _session_start_time

    if _session_start_time is None:
        _session_start_time = datetime.utcnow()

    timestamp = datetime.utcnow().isoformat()
    turn = {
        "timestamp": timestamp,
        "role": role,
        "content": content,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
    }
    _session_turns.append(turn)

    # Print to stderr if SESSION_LOG is enabled
    if SESSION_LOG:
        truncated = content[:truncate] + "..." if len(content) > truncate else content
        # Replace newlines for single-line log
        truncated = truncated.replace("\n", " \\n ")
        print(f"[{timestamp}] {role.upper()}: {truncated}", file=sys.stderr)


def save_session_log(
    model: str = None,
    total_tokens_in: int = 0,
    total_tokens_out: int = 0,
    output_dir: Path = None
) -> Optional[str]:
    """
    Save the accumulated session log to a file.

    Creates a JSON file with all turns and metadata.
    This enables:
    - Session replay
    - Cost analysis
    - Quality review
    - Training data collection

    Args:
        model: Model used for the session
        total_tokens_in: Total input tokens
        total_tokens_out: Total output tokens
        output_dir: Directory to save to (default: GEMINI_RESEARCH_PATH/sessions)

    Returns:
        Path to saved file, or None if no turns to save
    """
    global _session_turns, _session_start_time, _session_model

    if not _session_turns:
        return None

    # Determine output directory
    if output_dir is None:
        output_dir = GEMINI_RESEARCH_PATH / "sessions"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Build session metadata
    session_data = {
        "session_id": _session_start_time.strftime("%Y%m%d_%H%M%S") if _session_start_time else "unknown",
        "start_time": _session_start_time.isoformat() if _session_start_time else None,
        "end_time": datetime.utcnow().isoformat(),
        "model": model or _session_model,
        "total_turns": len(_session_turns),
        "total_tokens_in": total_tokens_in,
        "total_tokens_out": total_tokens_out,
        "turns": _session_turns,
    }

    # Generate filename
    session_id = session_data["session_id"]
    filename = f"{session_id}_session.json"
    filepath = output_dir / filename

    # Write file
    try:
        with open(filepath, 'w') as f:
            json.dump(session_data, f, indent=2, default=str)
        print(f"  [Session saved: {filename}]", file=sys.stderr)
        return str(filepath)
    except Exception as e:
        print(f"  [Session save failed: {e}]", file=sys.stderr)
        return None


def clear_session() -> None:
    """Clear the current session state."""
    global _session_turns, _session_start_time, _session_model
    _session_turns = []
    _session_start_time = None
    _session_model = None


def set_session_model(model: str) -> None:
    """Set the model for the current session."""
    global _session_model
    _session_model = model


def get_session_stats() -> Dict[str, Any]:
    """
    Get statistics about the current session.

    Returns:
        Dict with turn count, duration, etc.
    """
    if not _session_turns:
        return {"turns": 0, "duration_seconds": 0}

    user_turns = sum(1 for t in _session_turns if t["role"] == "user")
    assistant_turns = sum(1 for t in _session_turns if t["role"] == "assistant")

    duration = 0
    if _session_start_time:
        duration = (datetime.utcnow() - _session_start_time).total_seconds()

    total_tokens_in = sum(t.get("tokens_in", 0) for t in _session_turns)
    total_tokens_out = sum(t.get("tokens_out", 0) for t in _session_turns)

    return {
        "turns": len(_session_turns),
        "user_turns": user_turns,
        "assistant_turns": assistant_turns,
        "duration_seconds": duration,
        "total_tokens_in": total_tokens_in,
        "total_tokens_out": total_tokens_out,
        "model": _session_model,
    }


def format_session_summary() -> str:
    """
    Format a human-readable session summary.

    Returns:
        Formatted string summary
    """
    stats = get_session_stats()

    if stats["turns"] == 0:
        return "No session active."

    duration_min = stats["duration_seconds"] / 60
    return (
        f"Session Summary:\n"
        f"  Turns: {stats['turns']} ({stats['user_turns']} user, {stats['assistant_turns']} assistant)\n"
        f"  Duration: {duration_min:.1f} minutes\n"
        f"  Tokens: {stats['total_tokens_in']:,} in, {stats['total_tokens_out']:,} out\n"
        f"  Model: {stats['model'] or 'unknown'}"
    )
