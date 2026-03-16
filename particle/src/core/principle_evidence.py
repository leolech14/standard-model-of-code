"""
Principle Evidence Collector — Collider Stage 25

Scans source code nodes for evidence of ecosystem design principles
defined in IDEOME.yaml. Produces per-node evidence dict stored in
ctx.full_output['principle_evidence'].

Runs AFTER Stage 19 (Ideome Synthesis) and Stage 20 (Data Chemistry).
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional
import re


@dataclass
class PrincipleEvidence:
    """Evidence for a single principle on a single node."""
    found: bool = False
    file: str = ""
    line: int = 0
    snippet: str = ""
    confidence: float = 0.0  # 0.0-1.0


@dataclass
class NodeEvidence:
    """All principle evidence for one source node."""
    node_id: str
    file_path: str
    a1_d6_header: PrincipleEvidence = field(default_factory=PrincipleEvidence)
    a3_longitudinal: PrincipleEvidence = field(default_factory=PrincipleEvidence)
    a5_cost_tracking: PrincipleEvidence = field(default_factory=PrincipleEvidence)
    b2_degradation: PrincipleEvidence = field(default_factory=PrincipleEvidence)
    b3_auto_feedback: PrincipleEvidence = field(default_factory=PrincipleEvidence)
    b4_error_observability: PrincipleEvidence = field(default_factory=PrincipleEvidence)

    def to_dict(self) -> dict:
        return asdict(self)


def _grep_file(path: Path, pattern: str) -> Optional[tuple]:
    """Grep a file for a pattern. Returns (line_number, snippet) or None."""
    if not path.exists():
        return None
    try:
        for i, line in enumerate(path.read_text(encoding='utf-8', errors='ignore').splitlines(), 1):
            if re.search(pattern, line):
                return (i, line.strip()[:120])
    except Exception:
        pass
    return None


def _count_pattern(path: Path, pattern: str) -> int:
    """Count occurrences of a pattern in a file."""
    if not path.exists():
        return 0
    try:
        text = path.read_text(encoding='utf-8', errors='ignore')
        return len(re.findall(pattern, text))
    except Exception:
        return 0


def collect_evidence(full_output: dict, repo_path: str = "") -> Dict[str, dict]:
    """Collect principle evidence for all source nodes.

    Args:
        full_output: Collider's accumulated analysis output
        repo_path: Root path of the analyzed repo

    Returns:
        Dict mapping node_id -> NodeEvidence.to_dict()
    """
    nodes = full_output.get("nodes", [])
    root = Path(repo_path) if repo_path else Path(".")
    evidence_map: Dict[str, dict] = {}

    for node in nodes:
        node_id = node.get("id", "")
        file_path = node.get("file", node.get("path", ""))
        if not node_id or not file_path:
            continue

        full_path = root / file_path
        if not full_path.exists() or not full_path.suffix == '.py':
            continue

        ev = NodeEvidence(node_id=node_id, file_path=file_path)

        # A1: D6 _generated header
        match = _grep_file(full_path, r'["\']_generated["\']|_generated\s*[=:]|d6_header')
        if match:
            ev.a1_d6_header = PrincipleEvidence(
                found=True, file=file_path, line=match[0],
                snippet=match[1], confidence=0.9
            )

        # A3: Longitudinal tracking (append to JSONL)
        match = _grep_file(full_path, r'open\(.*["\']a["\']\).*jsonl|\.jsonl.*["\']a["\']|run_index|meta_index|video_index')
        if match:
            ev.a3_longitudinal = PrincipleEvidence(
                found=True, file=file_path, line=match[0],
                snippet=match[1], confidence=0.85
            )

        # A5: Cost/token tracking
        match = _grep_file(full_path, r'cost|token_count|usage_metadata|estimated_usd|estimate_cost')
        if match:
            ev.a5_cost_tracking = PrincipleEvidence(
                found=True, file=file_path, line=match[0],
                snippet=match[1], confidence=0.7
            )

        # B2: LLM degradation signal
        match = _grep_file(full_path, r'[Dd]egradation|llm_failed|llm_degradation|degraded|fallback_level')
        if match:
            ev.b2_degradation = PrincipleEvidence(
                found=True, file=file_path, line=match[0],
                snippet=match[1], confidence=0.85
            )

        # B3: Auto-feedback / self-evaluation
        match = _grep_file(full_path, r'auto_feedback|self_eval|build_feedback|quality_check|_check_.*budget')
        if match:
            ev.b3_auto_feedback = PrincipleEvidence(
                found=True, file=file_path, line=match[0],
                snippet=match[1], confidence=0.75
            )

        # B4: Error observability (count except:pass vs except:log)
        pass_count = _count_pattern(full_path, r'except.*:\s*$|except.*:.*pass\b')
        log_count = _count_pattern(full_path, r'except.*:.*(?:print|log|raise|warn)')
        total = pass_count + log_count
        if total > 0:
            ratio = log_count / total
            ev.b4_error_observability = PrincipleEvidence(
                found=True, file=file_path, line=0,
                snippet=f"logged:{log_count} swallowed:{pass_count} ratio:{ratio:.0%}",
                confidence=0.8
            )

        evidence_map[node_id] = ev.to_dict()

    return evidence_map
