"""
Temporal Analysis Module
========================
Git-powered codebase archaeology for the Collider pipeline.

Adapted from REH (Repository Evolution History) MCP Server v2
(wave/tools/mcp/mcp_history_server.py) -- same git logic, no MCP
dependency.  Runs as a deterministic analysis pass producing temporal
metrics for ``full_output``.

Capabilities
~~~~~~~~~~~~
1. **Growth velocity** -- file births & commit frequency over time
2. **Hotspot detection** -- most-modified files / directories
3. **Capability drift** -- functions/classes added or removed recently
4. **Age distribution** -- file ages bucketed by quartile
5. **Change coupling** -- files that frequently change together

All functions are pure git wrappers.  If the target is not a git repo
the module gracefully degrades (``available=False``).
"""

from __future__ import annotations

import os
import re
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ────────────────────────────────────────────────
# Shared constants & git helpers (canonical source: reh_core.py)
# Re-exported here for backward compatibility.
# ────────────────────────────────────────────────

from src.core.reh_core import (  # noqa: F401 — re-exports
    NOISE_DIRS,
    NOISE_EXTENSIONS,
    CODE_EXTENSIONS,
    CAPABILITY_PATTERNS,
    LANG_BY_EXT,
    _run_git,
    _is_git_repo,
    _is_noise,
    _is_code_file,
)


# ────────────────────────────────────────────────
# Result dataclasses
# ────────────────────────────────────────────────

@dataclass
class GrowthSnapshot:
    """One day of repo activity."""
    date: str
    commits: int = 0
    files_born: int = 0


@dataclass
class Hotspot:
    """A frequently-modified file."""
    path: str
    change_count: int = 0
    last_changed: str = ""


@dataclass
class CapabilityDelta:
    """A function/class that was added or removed."""
    kind: str       # "function" | "class"
    name: str
    file: str
    action: str     # "added" | "removed" | "modified"


@dataclass
class ChangeCouplingPair:
    """Two files that frequently change in the same commit."""
    file_a: str
    file_b: str
    co_change_count: int


@dataclass
class TemporalAnalysisResult:
    """Complete temporal analysis output for the Collider pipeline."""
    available: bool = False
    error: Optional[str] = None

    # Growth velocity
    total_commits: int = 0
    total_files_born: int = 0
    growth_timeline: List[GrowthSnapshot] = field(default_factory=list)
    commits_per_day: float = 0.0
    active_days: int = 0
    first_commit_date: str = ""
    last_commit_date: str = ""

    # Hotspots
    hotspots: List[Hotspot] = field(default_factory=list)

    # Capability drift (recent)
    capabilities_added: List[CapabilityDelta] = field(default_factory=list)
    capabilities_removed: List[CapabilityDelta] = field(default_factory=list)
    capabilities_modified: int = 0

    # Age distribution
    age_quartiles: Dict[str, int] = field(default_factory=dict)
    median_age_days: float = 0.0

    # Change coupling
    change_coupling: List[ChangeCouplingPair] = field(default_factory=list)

    # Summary metrics
    churn_rate: float = 0.0         # lines changed / lines total (proxy)
    bus_factor: int = 0             # distinct authors
    top_contributors: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = asdict(self)
        # Compact: trim large lists for JSON output
        if len(d.get("growth_timeline", [])) > 60:
            d["growth_timeline"] = d["growth_timeline"][-60:]
        return d


# ────────────────────────────────────────────────
# Core analysis functions
# ────────────────────────────────────────────────

def _analyze_growth(repo_path: str, limit: int = 90) -> Tuple[
    List[GrowthSnapshot], int, int, str, str
]:
    """Build a day-by-day growth timeline.

    Returns (timeline, total_commits, total_births, first_date, last_date).
    """
    # Commits per day
    ok, output = _run_git(repo_path, [
        "log", "--date=short", "--format=%ad",
    ])
    if not ok:
        return [], 0, 0, "", ""

    commit_counts: Counter = Counter()
    all_dates: list[str] = []
    for line in output.strip().split("\n"):
        line = line.strip()
        if re.match(r"^\d{4}-\d{2}-\d{2}$", line):
            commit_counts[line] += 1
            all_dates.append(line)

    if not all_dates:
        return [], 0, 0, "", ""

    total_commits = len(all_dates)
    first_date = min(all_dates)
    last_date = max(all_dates)

    # File births per day
    ok, birth_output = _run_git(repo_path, [
        "log", "--diff-filter=A", "--date=short",
        "--format=%ad", "--name-only",
    ])
    births_by_day: Counter = Counter()
    current_date = None
    total_births = 0
    if ok:
        for line in birth_output.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            if re.match(r"^\d{4}-\d{2}-\d{2}$", line):
                current_date = line
            elif current_date and not _is_noise(line) and _is_code_file(line):
                births_by_day[current_date] += 1
                total_births += 1

    # Build unified timeline (recent N days only)
    all_unique_dates = sorted(
        set(list(commit_counts.keys()) + list(births_by_day.keys()))
    )
    if limit and len(all_unique_dates) > limit:
        all_unique_dates = all_unique_dates[-limit:]

    timeline = [
        GrowthSnapshot(
            date=d,
            commits=commit_counts.get(d, 0),
            files_born=births_by_day.get(d, 0),
        )
        for d in all_unique_dates
    ]

    return timeline, total_commits, total_births, first_date, last_date


def _analyze_hotspots(repo_path: str, top_n: int = 20) -> List[Hotspot]:
    """Find the most frequently modified files."""
    ok, output = _run_git(repo_path, [
        "log", "--name-only", "--format=",
    ], max_output=1_000_000, timeout=60)
    if not ok:
        return []

    change_counts: Counter = Counter()
    for line in output.strip().split("\n"):
        line = line.strip()
        if line and not _is_noise(line) and _is_code_file(line):
            change_counts[line] += 1

    if not change_counts:
        return []

    # Get last-changed date for top files
    hotspots = []
    for path, count in change_counts.most_common(top_n):
        ok, date_out = _run_git(repo_path, [
            "log", "-1", "--format=%ad", "--date=short", "--", path,
        ])
        last_changed = date_out.strip() if ok else ""
        hotspots.append(Hotspot(
            path=path,
            change_count=count,
            last_changed=last_changed,
        ))

    return hotspots


def _analyze_capability_drift(
    repo_path: str,
    before_ref: str = "HEAD~10",
    after_ref: str = "HEAD",
) -> Tuple[List[CapabilityDelta], List[CapabilityDelta], int]:
    """Detect functions/classes added or removed between two refs.

    Returns (added, removed, modified_count).
    """
    ok, output = _run_git(repo_path, [
        "diff", f"{before_ref}..{after_ref}", "-U0",
    ])
    if not ok:
        # If before_ref doesn't exist (shallow clone, young repo), try HEAD~3
        for fallback in ["HEAD~5", "HEAD~3", "HEAD~1"]:
            ok, output = _run_git(repo_path, [
                "diff", f"{fallback}..{after_ref}", "-U0",
            ])
            if ok:
                before_ref = fallback
                break
        if not ok:
            return [], [], 0

    added_caps: list[dict] = []
    removed_caps: list[dict] = []
    current_file = ""

    for line in output.split("\n"):
        if line.startswith("diff --git"):
            parts = line.split(" b/")
            current_file = parts[-1] if len(parts) > 1 else ""
            continue

        is_add = line.startswith("+") and not line.startswith("+++")
        is_rem = line.startswith("-") and not line.startswith("---")
        if not is_add and not is_rem:
            continue

        stripped = line[1:].strip()
        if stripped.startswith("#") or stripped.startswith("//"):
            continue
        if stripped.startswith('"""') or stripped.startswith("'''"):
            continue

        _, ext = os.path.splitext(current_file)
        lang = LANG_BY_EXT.get(ext, "python")
        pattern = CAPABILITY_PATTERNS.get(lang)
        if not pattern:
            continue

        match = pattern.match(stripped)
        if not match:
            continue

        name = next((g for g in match.groups() if g), None)
        if not name:
            continue

        cap_type = "class" if "class " in stripped else "function"
        entry = {"kind": cap_type, "name": name, "file": current_file}

        if is_add:
            added_caps.append(entry)
        else:
            removed_caps.append(entry)

    # Deduplicate: modified = in both added and removed
    added_keys = {(c["name"], c["file"]) for c in added_caps}
    removed_keys = {(c["name"], c["file"]) for c in removed_caps}
    truly_added = [
        CapabilityDelta(**c, action="added")
        for c in added_caps if (c["name"], c["file"]) not in removed_keys
    ]
    truly_removed = [
        CapabilityDelta(**c, action="removed")
        for c in removed_caps if (c["name"], c["file"]) not in added_keys
    ]
    modified_count = len(added_keys & removed_keys)

    return truly_added, truly_removed, modified_count


def _analyze_age_distribution(repo_path: str) -> Tuple[Dict[str, int], float]:
    """Compute file age quartiles and median age.

    Returns ({quartile_label: count}, median_age_days).
    """
    ok, output = _run_git(repo_path, [
        "log", "--diff-filter=A", "--date=unix",
        "--format=%ad", "--name-only",
    ], max_output=1_000_000, timeout=60)
    if not ok:
        return {}, 0.0

    import time as _time
    now = _time.time()

    file_birth: dict[str, float] = {}
    current_epoch: Optional[float] = None
    for line in output.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.isdigit() or (line.startswith("-") and line[1:].isdigit()):
            current_epoch = float(line)
        elif current_epoch and not _is_noise(line) and _is_code_file(line):
            # Keep earliest birth
            if line not in file_birth or current_epoch < file_birth[line]:
                file_birth[line] = current_epoch

    if not file_birth:
        return {}, 0.0

    ages_days = sorted([(now - epoch) / 86400 for epoch in file_birth.values()])
    n = len(ages_days)
    median = ages_days[n // 2] if n else 0.0

    # Quartile buckets
    buckets: Dict[str, int] = {
        "< 7 days": 0,
        "7-30 days": 0,
        "30-90 days": 0,
        "90-180 days": 0,
        "180-365 days": 0,
        "> 365 days": 0,
    }
    for age in ages_days:
        if age < 7:
            buckets["< 7 days"] += 1
        elif age < 30:
            buckets["7-30 days"] += 1
        elif age < 90:
            buckets["30-90 days"] += 1
        elif age < 180:
            buckets["90-180 days"] += 1
        elif age < 365:
            buckets["180-365 days"] += 1
        else:
            buckets["> 365 days"] += 1

    return buckets, round(median, 1)


def _analyze_change_coupling(
    repo_path: str,
    min_co_changes: int = 3,
    top_n: int = 15,
) -> List[ChangeCouplingPair]:
    """Find files that frequently change together in the same commit."""
    ok, output = _run_git(repo_path, [
        "log", "--name-only", "--format=COMMIT_SEP",
    ], max_output=2_000_000, timeout=60)
    if not ok:
        return []

    pair_counts: Counter = Counter()
    current_files: list[str] = []

    for line in output.split("\n"):
        line = line.strip()
        if line == "COMMIT_SEP":
            # Process previous commit's files
            code_files = [
                f for f in current_files
                if f and not _is_noise(f) and _is_code_file(f)
            ]
            # Only consider commits with 2-15 files (avoid merge bombs)
            if 2 <= len(code_files) <= 15:
                code_files.sort()
                for i in range(len(code_files)):
                    for j in range(i + 1, len(code_files)):
                        pair_counts[(code_files[i], code_files[j])] += 1
            current_files = []
        elif line:
            current_files.append(line)

    # Process last commit
    code_files = [
        f for f in current_files
        if f and not _is_noise(f) and _is_code_file(f)
    ]
    if 2 <= len(code_files) <= 15:
        code_files.sort()
        for i in range(len(code_files)):
            for j in range(i + 1, len(code_files)):
                pair_counts[(code_files[i], code_files[j])] += 1

    result = [
        ChangeCouplingPair(
            file_a=pair[0],
            file_b=pair[1],
            co_change_count=count,
        )
        for pair, count in pair_counts.most_common(top_n)
        if count >= min_co_changes
    ]
    return result


def _analyze_contributors(repo_path: str) -> Tuple[int, List[Dict[str, Any]]]:
    """Get bus factor (distinct authors) and top contributors.

    Returns (bus_factor, top_contributors_list).
    """
    ok, output = _run_git(repo_path, [
        "shortlog", "-sn", "--no-merges", "HEAD",
    ])
    if not ok:
        return 0, []

    contributors = []
    for line in output.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t", 1)
        if len(parts) == 2:
            count_str, name = parts
            try:
                contributors.append({
                    "name": name.strip(),
                    "commits": int(count_str.strip()),
                })
            except ValueError:
                pass

    bus_factor = len(contributors)
    return bus_factor, contributors[:10]


# ────────────────────────────────────────────────
# Main entry point
# ────────────────────────────────────────────────

def compute_temporal_analysis(
    full_output: dict,
    repo_path: Optional[str] = None,
) -> TemporalAnalysisResult:
    """Run all temporal analyses and return a unified result.

    Parameters
    ----------
    full_output : dict
        The Collider full_output dictionary (used to extract repo_path
        if not supplied explicitly).
    repo_path : str, optional
        Explicit path to the git repo root.  If *None*, extracted from
        ``full_output['metadata']['target_path']``.

    Returns
    -------
    TemporalAnalysisResult
        Populated result if the target is a git repo, otherwise
        a stub with ``available=False``.
    """
    result = TemporalAnalysisResult()

    # Resolve repo path
    if repo_path is None:
        metadata = full_output.get("metadata", {})
        repo_path = metadata.get("target_path", "")
    if not repo_path:
        result.error = "no repo path available"
        return result

    repo_path = str(Path(repo_path).resolve())

    if not _is_git_repo(repo_path):
        result.error = "not a git repository"
        return result

    result.available = True

    # 1. Growth velocity
    timeline, total_commits, total_births, first_date, last_date = (
        _analyze_growth(repo_path)
    )
    result.growth_timeline = timeline
    result.total_commits = total_commits
    result.total_files_born = total_births
    result.first_commit_date = first_date
    result.last_commit_date = last_date
    result.active_days = len(timeline)
    if result.active_days > 0:
        result.commits_per_day = round(total_commits / max(result.active_days, 1), 2)

    # 2. Hotspots
    result.hotspots = _analyze_hotspots(repo_path)

    # 3. Capability drift (last ~10 commits)
    added, removed, modified = _analyze_capability_drift(repo_path)
    result.capabilities_added = added
    result.capabilities_removed = removed
    result.capabilities_modified = modified

    # 4. Age distribution
    age_q, median_age = _analyze_age_distribution(repo_path)
    result.age_quartiles = age_q
    result.median_age_days = median_age

    # 5. Change coupling
    result.change_coupling = _analyze_change_coupling(repo_path)

    # 6. Contributors / bus factor
    bus_factor, top_contribs = _analyze_contributors(repo_path)
    result.bus_factor = bus_factor
    result.top_contributors = top_contribs

    # 7. Churn rate proxy: total hotspot changes / total files
    total_files = full_output.get("node_count", 0)
    if total_files > 0 and result.hotspots:
        total_changes = sum(h.change_count for h in result.hotspots)
        result.churn_rate = round(total_changes / total_files, 2)

    return result
