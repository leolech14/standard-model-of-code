"""
REH Evolution Compiler — aggregates temporal data into unified analysis.

Deterministic: no LLM, no external APIs. Pure git queries + computation.
Produces Tier 1 output (reh_evolution.json).
"""

import json
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Import shared REH core (needs both particle/src and particle on path)
_particle = Path(__file__).resolve().parents[3] / "particle"
sys.path.insert(0, str(_particle / "src"))
sys.path.insert(0, str(_particle))
from core.reh_core import (  # noqa: E402
    CAPABILITY_PATTERNS,
    LANG_BY_EXT,
    _run_git,
    _is_noise,
    _is_code_file,
)

from reh_meta_envelope import build_reh_envelope  # noqa: E402


def _d6_header() -> Dict[str, Any]:
    import subprocess
    sha = "unknown"
    try:
        sha = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(Path(__file__).resolve().parents[3]),
            stderr=subprocess.DEVNULL,
        ).decode().strip()
    except Exception:
        pass
    return {
        "source": "reh",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "git_sha": sha,
    }


class EvolutionCompiler:
    """Compiles unified temporal analysis from git history."""

    def compile(
        self,
        repo_path: str,
        since: str = "",
        until: str = "",
    ) -> Dict[str, Any]:
        start_ms = time.time()

        timeline = self._build_timeline(repo_path, since, until)
        velocity = self._compute_velocity(timeline)
        activity = self._compute_activity_heatmap(repo_path, since, until)
        capability_changes = self._track_capabilities(repo_path, since, until)
        milestones = self._detect_milestones(timeline)

        # Trajectory classification
        trajectory = self._classify_trajectory(velocity)

        elapsed_ms = int((time.time() - start_ms) * 1000)

        # Count unique files and capabilities
        all_files = set()
        for day in timeline:
            for fb in day.get("files_born", []):
                all_files.add(fb["file"])
        cap_count = capability_changes.get("total_current", 0)

        dev_commits = sum(len(d.get("commits", [])) for d in timeline)
        raw_commits = getattr(self, "_total_raw_commits", dev_commits)

        envelope = build_reh_envelope(
            repo_path=repo_path,
            date_range={"since": since or "repo_start", "until": until or "now"},
            commit_count=dev_commits,
            file_count=len(all_files),
            capability_count=cap_count,
            velocity_cpw=velocity.get("commits_per_week_avg", 0),
            trajectory=trajectory,
            analysis_time_ms=elapsed_ms,
        )
        envelope["commit_count_raw"] = raw_commits

        return {
            "_generated": _d6_header(),
            "meta_envelope": envelope,
            "repo_path": repo_path,
            "date_range": {"since": since or "repo_start", "until": until or "now"},
            "trajectory": trajectory,
            "timeline": timeline,
            "velocity": velocity,
            "activity_heatmap": activity,
            "capability_changes": capability_changes,
            "milestones": milestones,
        }

    def _build_timeline(
        self, repo_path: str, since: str, until: str
    ) -> List[Dict[str, Any]]:
        """Build per-day timeline: commits + files born."""
        args = ["log", "--date=short", "--format=%ad|%s"]
        if since:
            args.append(f"--since={since}")
        if until:
            args.append(f"--until={until}")

        ok, output = _run_git(repo_path, args)
        if not ok:
            return []

        # Group commits by date (merge commits filtered for dev-only count)
        by_date: Dict[str, List[str]] = defaultdict(list)
        total_raw_commits = 0
        for line in output.strip().split("\n"):
            if "|" not in line:
                continue
            total_raw_commits += 1
            date, msg = line.split("|", 1)
            msg = msg.strip()
            if msg.lower().startswith("merge"):
                continue
            by_date[date.strip()].append(msg)

        # Get file births
        birth_args = ["log", "--diff-filter=A", "--date=short", "--format=%ad", "--name-only"]
        if since:
            birth_args.append(f"--since={since}")
        if until:
            birth_args.append(f"--until={until}")

        ok2, birth_output = _run_git(repo_path, birth_args)
        births_by_date: Dict[str, List[str]] = defaultdict(list)
        if ok2:
            current_date = ""
            for line in birth_output.strip().split("\n"):
                line = line.strip()
                if not line:
                    continue
                # Date lines are YYYY-MM-DD format
                if len(line) == 10 and line[4] == "-" and line[7] == "-":
                    current_date = line
                elif current_date and not _is_noise(line):
                    births_by_date[current_date].append(line)

        # Merge into timeline
        all_dates = sorted(set(list(by_date.keys()) + list(births_by_date.keys())))
        self._total_raw_commits = total_raw_commits

        timeline = []
        for date in all_dates[-50:]:  # Last 50 days max
            commits = by_date.get(date, [])[:10]  # Max 10 per day
            files = births_by_date.get(date, [])[:20]  # Max 20 per day

            # Check file status
            file_entries = []
            for f in files:
                status = "ACTIVE" if (Path(repo_path) / f).exists() else "DELETED"
                file_entries.append({"file": f, "status": status})

            timeline.append({
                "date": date,
                "commits": commits,
                "commit_count": len(by_date.get(date, [])),
                "files_born": file_entries,
                "files_born_count": len(births_by_date.get(date, [])),
            })

        return timeline

    def _compute_velocity(self, timeline: List[Dict]) -> Dict[str, Any]:
        """Compute development velocity from timeline."""
        if not timeline:
            return {
                "commits_per_week_avg": 0,
                "trend": "unknown",
                "weekly_commits": [],
                "most_active_dirs": [],
            }

        # Group by ISO week
        weekly: Dict[str, int] = defaultdict(int)
        for day in timeline:
            try:
                dt = datetime.strptime(day["date"], "%Y-%m-%d")
                week_key = dt.strftime("%Y-W%W")
                weekly[week_key] += day["commit_count"]
            except (ValueError, KeyError):
                continue

        weeks_sorted = sorted(weekly.items())
        values = [v for _, v in weeks_sorted]

        if not values:
            return {"commits_per_week_avg": 0, "trend": "unknown", "weekly_commits": [], "most_active_dirs": []}

        avg = sum(values) / len(values)

        # Trend: compare recent half vs older half
        mid = len(values) // 2
        if mid > 0 and len(values) > 2:
            old_avg = sum(values[:mid]) / mid
            new_avg = sum(values[mid:]) / (len(values) - mid)
            if new_avg > old_avg * 1.3:
                trend = "accelerating"
            elif new_avg < old_avg * 0.7:
                trend = "decelerating"
            else:
                trend = "steady"
        else:
            trend = "steady"

        # Most active directories from file births
        dir_counts: Dict[str, int] = defaultdict(int)
        for day in timeline:
            for fb in day.get("files_born", []):
                parts = fb["file"].split("/")
                if len(parts) > 1:
                    dir_counts[parts[0] + "/"] += 1

        most_active = sorted(dir_counts.items(), key=lambda x: -x[1])[:5]

        return {
            "commits_per_week_avg": round(avg, 1),
            "trend": trend,
            "weekly_commits": [{"week": w, "commits": c} for w, c in weeks_sorted[-8:]],
            "most_active_dirs": [f"{d} ({c} files)" for d, c in most_active],
        }

    def _compute_activity_heatmap(
        self, repo_path: str, since: str, until: str
    ) -> Dict[str, Any]:
        """Compute directory activity heatmap (dirs x weeks)."""
        args = ["log", "--date=short", "--format=%ad", "--name-only"]
        if since:
            args.append(f"--since={since}")
        if until:
            args.append(f"--until={until}")

        ok, output = _run_git(repo_path, args)
        if not ok:
            return {"directories": [], "weeks": [], "matrix": []}

        # Parse: date lines followed by file paths
        dir_week_counts: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        current_date = ""
        for line in output.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            if len(line) == 10 and line[4] == "-" and line[7] == "-":
                current_date = line
            elif current_date and not _is_noise(line):
                parts = line.split("/")
                top_dir = parts[0] + "/" if len(parts) > 1 else "(root)"
                try:
                    dt = datetime.strptime(current_date, "%Y-%m-%d")
                    week = dt.strftime("%Y-W%W")
                    dir_week_counts[top_dir][week] += 1
                except ValueError:
                    pass

        # Top 10 most active directories
        dir_totals = {d: sum(weeks.values()) for d, weeks in dir_week_counts.items()}
        top_dirs = sorted(dir_totals.items(), key=lambda x: -x[1])[:10]
        top_dir_names = [d for d, _ in top_dirs]

        # All weeks seen
        all_weeks = sorted(set(w for weeks in dir_week_counts.values() for w in weeks))
        recent_weeks = all_weeks[-8:]  # Last 8 weeks

        # Build matrix
        matrix = []
        for d in top_dir_names:
            row = [dir_week_counts[d].get(w, 0) for w in recent_weeks]
            matrix.append({"directory": d, "total": dir_totals[d], "weekly": row})

        return {
            "directories": top_dir_names,
            "weeks": recent_weeks,
            "matrix": matrix,
        }

    def _track_capabilities(
        self, repo_path: str, since: str, until: str
    ) -> Dict[str, Any]:
        """Track capability evolution (functions/classes added/removed)."""
        # Get HEAD capability count
        args_head = ["diff", "--name-only", "HEAD~10..HEAD"]
        ok, changed = _run_git(repo_path, args_head)
        changed_files = changed.strip().split("\n") if ok else []

        # Count current capabilities in changed files
        added = []
        for fpath in changed_files[:20]:  # Cap at 20 files
            if not _is_code_file(fpath):
                continue
            ext = Path(fpath).suffix
            lang = LANG_BY_EXT.get(ext)
            if not lang or lang not in CAPABILITY_PATTERNS:
                continue
            pattern = CAPABILITY_PATTERNS[lang]
            full_path = Path(repo_path) / fpath
            if not full_path.exists():
                continue
            try:
                for line in full_path.read_text(errors="ignore").split("\n"):
                    m = pattern.match(line)
                    if m:
                        name = next((g for g in m.groups() if g), None)
                        if name and not name.startswith("_"):
                            added.append({"name": name, "file": fpath, "type": "function" if "def " in line or "func " in line else "class"})
            except Exception:
                pass

        # Count total current capabilities (sample: first 50 code files)
        total_caps = 0
        args_files = ["ls-files"]
        ok, all_files = _run_git(repo_path, args_files)
        if ok:
            code_files = [f for f in all_files.strip().split("\n") if _is_code_file(f)][:50]
            for fpath in code_files:
                ext = Path(fpath).suffix
                lang = LANG_BY_EXT.get(ext)
                if not lang or lang not in CAPABILITY_PATTERNS:
                    continue
                full_path = Path(repo_path) / fpath
                if not full_path.exists():
                    continue
                try:
                    for line in full_path.read_text(errors="ignore").split("\n"):
                        if CAPABILITY_PATTERNS[lang].match(line):
                            total_caps += 1
                except Exception:
                    pass

        return {
            "total_current": total_caps,
            "recently_changed": added[:15],
            "recently_changed_count": len(added),
        }

    def _detect_milestones(self, timeline: List[Dict]) -> List[Dict[str, Any]]:
        """Detect high-impact commits (milestones)."""
        milestones = []
        for day in timeline:
            # Milestone criteria: >5 files born OR >5 commits in one day
            if day["files_born_count"] > 5 or day["commit_count"] > 5:
                # Determine type from commit messages
                msgs = " ".join(day["commits"]).lower()
                if "refactor" in msgs or "rename" in msgs or "move" in msgs:
                    milestone_type = "refactor"
                elif "feat" in msgs or "add" in msgs or "new" in msgs:
                    milestone_type = "capability_added"
                elif "fix" in msgs or "bug" in msgs:
                    milestone_type = "bugfix_wave"
                else:
                    milestone_type = "major_change"

                impact = "high" if day["files_born_count"] > 10 or day["commit_count"] > 10 else "medium"

                milestones.append({
                    "date": day["date"],
                    "type": milestone_type,
                    "title": day["commits"][0] if day["commits"] else "Multiple changes",
                    "description": f"{day['commit_count']} commits, {day['files_born_count']} new files",
                    "impact": impact,
                    "commit_count": day["commit_count"],
                    "files_born_count": day["files_born_count"],
                })

        # Sort by impact then date
        milestones.sort(key=lambda m: (0 if m["impact"] == "high" else 1, m["date"]))
        return milestones[:10]  # Top 10

    def _classify_trajectory(self, velocity: Dict) -> str:
        """Classify overall trajectory from velocity metrics."""
        trend = velocity.get("trend", "unknown")
        avg = velocity.get("commits_per_week_avg", 0)

        if avg == 0:
            return "dormant"
        if trend == "accelerating":
            return "growing"
        if trend == "decelerating" and avg < 3:
            return "declining"
        if trend == "decelerating":
            return "stabilizing"
        return "stable"
