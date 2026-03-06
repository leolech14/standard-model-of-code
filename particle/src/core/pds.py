"""
PDS: Progressive Discovery System for Collider.

Incremental, findings-aware gate that evaluates structural damage
from code changes using graph topology and compiled insights.

Instead of a blind health threshold, PDS:
1. Identifies changed files via git diff
2. Computes blast radius using the dependency graph (ancestors + descendants)
3. Gates on critical/high findings in structural categories
"""

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set

import networkx as nx

# Extensions Collider can analyze
ANALYZABLE_EXTENSIONS = {
    '.py', '.js', '.ts', '.tsx', '.jsx', '.go', '.rs', '.java',
    '.rb', '.c', '.cpp', '.h', '.hpp', '.cs', '.swift', '.kt',
}

# Categories that indicate structural problems (block push)
BLOCKING_CATEGORIES = {
    "purpose_decomposition", "incoherence", "gap_detection",
    "topology", "entanglement", "constraints",
}

# Categories that are informational (warn only)
WARN_CATEGORIES = {
    "bus_factor", "stale_data", "temporal", "performance", "contextome",
}

# Severities that trigger blocking (within blocking categories)
BLOCKING_SEVERITIES = {"critical", "high"}


@dataclass
class GateResult:
    """Result of PDS gate evaluation."""
    passed: bool
    blocking_findings: List[Dict] = field(default_factory=list)
    warnings: List[Dict] = field(default_factory=list)
    summary: str = ""

    def to_dict(self) -> Dict:
        return {
            "passed": self.passed,
            "blocking_findings": self.blocking_findings,
            "warnings": self.warnings,
            "summary": self.summary,
        }


def get_changed_files(repo_path: str, base_ref: str = "HEAD~1") -> Set[str]:
    """Get files changed since base_ref via git diff.

    Args:
        repo_path: Root of the git repository.
        base_ref: Git ref to diff against (default: previous commit).

    Returns:
        Set of relative file paths that were added, copied, modified, or renamed.
        Filtered to Collider-analyzable extensions.
    """
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=ACMR", base_ref],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return _fallback_changed_files(repo_path)

        files = set()
        for line in result.stdout.strip().splitlines():
            line = line.strip()
            if not line:
                continue
            if Path(line).suffix in ANALYZABLE_EXTENSIONS:
                files.add(line)
        return files

    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return _fallback_changed_files(repo_path)


def _fallback_changed_files(repo_path: str) -> Set[str]:
    """Fallback: use git status for unstaged/staged changes when diff fails."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return set()

        files = set()
        for line in result.stdout.strip().splitlines():
            # porcelain format: XY filename
            if len(line) < 4:
                continue
            path = line[3:].strip()
            if Path(path).suffix in ANALYZABLE_EXTENSIONS:
                files.add(path)
        return files

    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return set()


def compute_blast_radius(G: nx.DiGraph, changed_nodes: Set[str]) -> Set[str]:
    """Compute the full blast radius of changed nodes in the dependency graph.

    For each changed node, includes:
    - The node itself
    - All ancestors (upstream callers that depend on this node)
    - All descendants (downstream dependencies)

    Args:
        G: NetworkX directed graph from Collider analysis.
        changed_nodes: Set of node IDs that correspond to changed files.

    Returns:
        Union of all affected node IDs.
    """
    blast_radius = set()

    for node in changed_nodes:
        if node not in G:
            continue
        blast_radius.add(node)
        blast_radius.update(nx.ancestors(G, node))
        blast_radius.update(nx.descendants(G, node))

    return blast_radius


def _node_in_changed_files(node_id: str, changed_files: Set[str]) -> bool:
    """Check if a graph node belongs to one of the changed files.

    Node IDs have the form '/full/path/to/file.py:function_name'.
    Changed files are relative paths like 'particle/src/core/pds.py'.
    We match by checking if the node's file path ends with any changed file.
    """
    file_part = node_id.split(":")[0] if ":" in node_id else node_id
    return any(file_part.endswith(cf) for cf in changed_files)


def evaluate_gate(
    findings: List[Dict],
    blast_radius: Set[str],
    changed_files: Set[str],
    changed_nodes: Optional[Set[str]] = None,
) -> GateResult:
    """Evaluate whether findings in the blast radius should block a push.

    Filters findings to those whose related_nodes intersect with the blast
    radius, then classifies them based on proximity to actual changes:

    - Findings directly in changed files/nodes → blocking (if critical/high
      in structural categories)
    - Findings only reachable via blast radius (pre-existing) → downgraded
      to warnings with annotation

    This prevents pre-existing findings from blocking unrelated pushes.

    Args:
        findings: List of compiled insight dicts from baseline.
        blast_radius: Set of node IDs in the blast radius.
        changed_files: Set of changed file paths (relative).
        changed_nodes: Optional set of node IDs directly in changed files.
            If provided, used for precise matching; otherwise falls back
            to file-path matching via changed_files.

    Returns:
        GateResult with pass/fail decision and categorized findings.
    """
    blocking = []
    warnings = []

    for finding in findings:
        related = set(finding.get("related_nodes", []))

        # Check if this finding touches the blast radius
        if not related.intersection(blast_radius):
            continue

        category = finding.get("category", "")
        severity = finding.get("severity", "").lower()

        # Determine if finding is directly in changed code
        if changed_nodes is not None:
            directly_changed = bool(related.intersection(changed_nodes))
        else:
            directly_changed = any(
                _node_in_changed_files(n, changed_files) for n in related
            )

        if category in BLOCKING_CATEGORIES and severity in BLOCKING_SEVERITIES:
            if directly_changed:
                blocking.append(finding)
            else:
                # Pre-existing finding in blast radius — downgrade to warning
                downgraded = dict(finding)
                downgraded["downgraded_from"] = "blocking"
                downgraded["downgrade_reason"] = (
                    "pre-existing finding (not in changed files)"
                )
                warnings.append(downgraded)
        elif category in WARN_CATEGORIES or severity not in BLOCKING_SEVERITIES:
            warnings.append(finding)

    passed = len(blocking) == 0
    n_downgraded = sum(
        1 for w in warnings if w.get("downgraded_from") == "blocking"
    )
    summary = (
        f"{len(changed_files)} file(s) changed, "
        f"{len(blast_radius)} node(s) in blast radius, "
        f"{len(blocking)} blocking finding(s), "
        f"{len(warnings)} warning(s)"
    )
    if n_downgraded:
        summary += f" ({n_downgraded} pre-existing downgraded)"

    return GateResult(
        passed=passed,
        blocking_findings=blocking,
        warnings=warnings,
        summary=summary,
    )
