"""
Repository Evolution History (REH) MCP Server v2
=================================================
Git-powered codebase archaeology. Five tools for investigating how a repo
evolved, when specific code appeared/disappeared, and what capabilities
were gained or lost across refactors.

Tools:
    get_repo_history        — Chronological timeline (file births + commits)
    search_code_changes     — Pickaxe search (when was string X added/removed?)
    get_file_history        — Full evolution of a single file
    detect_capability_changes — What functions/classes were added/removed between refs
    get_directory_activity  — Scoped view of all activity in a directory + date range

All tools are pure git wrappers. No API keys, no external deps, no TDJ dependency.

Usage:
    uv run python wave/tools/mcp/mcp_history_server.py
"""
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

# Import shared REH core (D9: single canonical source for constants + git utilities)
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "particle" / "src"))
from core.reh_core import (  # noqa: E402
    NOISE_DIRS,
    NOISE_EXTENSIONS,
    CODE_EXTENSIONS,
    CAPABILITY_PATTERNS,
    LANG_BY_EXT,
    _run_git,
    _is_noise,
    _is_code_file,
)

from mcp.server.fastmcp import FastMCP  # noqa: E402

mcp = FastMCP(
    "Repository Evolution History",
    instructions=(
        "Git-powered codebase archaeology. Use search_code_changes to find when "
        "specific code was introduced or removed (pickaxe). Use get_file_history "
        "to trace a file's full evolution. Use detect_capability_changes to find "
        "regressions (functions/classes lost between two commits). Use "
        "get_directory_activity for scoped activity in a path + date window. "
        "Use get_repo_history for a broad chronological overview."
    ),
)

# ========== MCP-specific Utilities ==========

def _validate_repo(path: str) -> tuple[bool, str]:
    """Check that path exists and is a git repo."""
    if not os.path.isdir(path):
        return False, f"Directory not found: {path}"
    if not os.path.isdir(os.path.join(path, ".git")):
        return False, f"Not a git repository: {path}"
    return True, ""


def _check_file_status(relative_path: str, repo_root: str) -> str:
    """Return a status badge for a file: ACTIVE, ARCHIVED, or DELETED."""
    full_path = os.path.join(repo_root, relative_path)
    if os.path.exists(full_path):
        if "archive/" in relative_path or "legacy" in relative_path.lower():
            return "ARCHIVED"
        return "ACTIVE"
    # Check common archive locations
    for arc_dir in ("archive", "archive/zombie_code"):
        arc_path = os.path.join(repo_root, arc_dir, os.path.basename(relative_path))
        if os.path.exists(arc_path):
            return "ARCHIVED"
    return "DELETED"


# ========== Tool 1: Repository History ==========

@mcp.tool()
def get_repo_history(
    repo_path: str,
    path_filter: str = "",
    since: str = "",
    until: str = "",
    limit: int = 50,
) -> str:
    """Chronological timeline of a repository: commits + files born per day.

    Args:
        repo_path: Absolute path to the git repository root.
        path_filter: Optional directory/file filter (e.g. "dashboard/" or "src/api").
        since: Start date (YYYY-MM-DD). Omit for no lower bound.
        until: End date (YYYY-MM-DD). Omit for no upper bound.
        limit: Max days to return (default 50).
    """
    valid, err = _validate_repo(repo_path)
    if not valid:
        return json.dumps({"error": err})

    # Get commits
    cmd = ["log", "--date=short", "--format=%ad|%s"]
    if since:
        cmd += [f"--since={since}"]
    if until:
        cmd += [f"--until={until}"]
    if path_filter:
        cmd += ["--", path_filter]
    ok, output = _run_git(repo_path, cmd)
    if not ok:
        return json.dumps({"error": f"git log failed: {output}"})

    commits_by_day = defaultdict(list)
    for line in output.strip().split("\n"):
        if "|" in line:
            date, msg = line.split("|", 1)
            date = date.strip()
            msg = msg.strip()
            if "Merge pull request" not in msg and "Merge branch" not in msg:
                commits_by_day[date].append(msg)

    # Get file births (files first added)
    birth_cmd = ["log", "--diff-filter=A", "--date=short", "--format=%ad", "--name-only"]
    if since:
        birth_cmd += [f"--since={since}"]
    if until:
        birth_cmd += [f"--until={until}"]
    if path_filter:
        birth_cmd += ["--", path_filter]
    ok, birth_output = _run_git(repo_path, birth_cmd)

    births_by_day = defaultdict(list)
    current_date = None
    if ok:
        for line in birth_output.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            # Date lines are YYYY-MM-DD format
            if re.match(r"^\d{4}-\d{2}-\d{2}$", line):
                current_date = line
            elif current_date and not _is_noise(line) and _is_code_file(line):
                births_by_day[current_date].append(line)

    # Merge all dates
    all_dates = sorted(set(list(commits_by_day.keys()) + list(births_by_day.keys())))
    if limit:
        all_dates = all_dates[-limit:]

    days = []
    for date in all_dates:
        commits = list(dict.fromkeys(commits_by_day.get(date, [])))[:10]
        born = births_by_day.get(date, [])
        born_with_status = []
        for f in sorted(set(born))[:20]:
            status = _check_file_status(f, repo_path)
            born_with_status.append({"file": f, "status": status})

        if commits or born_with_status:
            days.append({
                "date": date,
                "commits": commits,
                "files_born": born_with_status,
                "files_born_count": len(born),
            })

    return json.dumps({
        "repo": repo_path,
        "path_filter": path_filter or "(all)",
        "date_range": f"{since or 'start'} to {until or 'now'}",
        "total_days": len(days),
        "days": days,
    }, indent=2)


# ========== Tool 2: Pickaxe Search ==========

@mcp.tool()
def search_code_changes(
    repo_path: str,
    search_string: str,
    is_regex: bool = False,
    file_pattern: str = "",
    max_results: int = 20,
) -> str:
    """Find commits where a specific string was added or removed (git pickaxe).

    Use this to answer: "when was send_whatsapp introduced?" or
    "when was the audio capability removed?"

    Args:
        repo_path: Absolute path to the git repository root.
        search_string: The string or regex to search for in diffs.
        is_regex: If true, treat search_string as regex (-G). Default false uses literal (-S).
        file_pattern: Optional file/dir filter (e.g. "dashboard/*.py" or "src/").
        max_results: Max commits to return (default 20).
    """
    valid, err = _validate_repo(repo_path)
    if not valid:
        return json.dumps({"error": err})

    flag = "-G" if is_regex else "-S"
    cmd = ["log", flag, search_string, f"--format=%H|%ad|%an|%s", "--date=short"]
    if file_pattern:
        cmd += ["--", file_pattern]
    ok, output = _run_git(repo_path, cmd)
    if not ok:
        return json.dumps({"error": f"git log pickaxe failed: {output}"})

    matches = []
    for line in output.strip().split("\n"):
        if not line or "|" not in line:
            continue
        parts = line.split("|", 3)
        if len(parts) < 4:
            continue
        commit_hash, date, author, message = parts
        matches.append({
            "commit": commit_hash.strip(),
            "date": date.strip(),
            "author": author.strip(),
            "message": message.strip(),
        })

    matches = matches[:max_results]

    # For each match, get the specific changed lines containing the search string
    for m in matches[:10]:  # detail for first 10 only
        diff_cmd = ["diff", f"{m['commit']}~1..{m['commit']}", "-U0"]
        if file_pattern:
            diff_cmd += ["--", file_pattern]
        ok, diff_out = _run_git(repo_path, diff_cmd, max_output=50_000)
        if not ok:
            continue

        added = []
        removed = []
        current_file = ""
        for dline in diff_out.split("\n"):
            if dline.startswith("diff --git"):
                parts = dline.split(" b/")
                current_file = parts[-1] if len(parts) > 1 else ""
            elif dline.startswith("+") and not dline.startswith("+++"):
                if search_string.lower() in dline.lower():
                    added.append({"file": current_file, "line": dline[1:].strip()})
            elif dline.startswith("-") and not dline.startswith("---"):
                if search_string.lower() in dline.lower():
                    removed.append({"file": current_file, "line": dline[1:].strip()})

        if added or removed:
            m["added_lines"] = added[:10]
            m["removed_lines"] = removed[:10]

    return json.dumps({
        "query": search_string,
        "mode": "regex" if is_regex else "literal",
        "file_pattern": file_pattern or "(all)",
        "total_matches": len(matches),
        "matches": matches,
    }, indent=2)


# ========== Tool 3: File History ==========

@mcp.tool()
def get_file_history(
    repo_path: str,
    file_path: str,
    follow_renames: bool = True,
    show_diffs: bool = False,
    max_results: int = 30,
) -> str:
    """Full chronological evolution of a single file.

    Shows every commit that touched the file, optionally with diffs.
    Works for deleted files too (shows when/why it was removed).

    Args:
        repo_path: Absolute path to the git repository root.
        file_path: Relative path to the file within the repo (e.g. "dashboard/voice_gateway.py").
        follow_renames: Track the file across renames (default true).
        show_diffs: Include diff snippets per commit (default false, more verbose).
        max_results: Max commits to return (default 30).
    """
    valid, err = _validate_repo(repo_path)
    if not valid:
        return json.dumps({"error": err})

    exists = os.path.exists(os.path.join(repo_path, file_path))

    cmd = ["log", f"--format=%H|%ad|%an|%s", "--date=short", f"-{max_results}"]
    if follow_renames:
        cmd.append("--follow")
    if show_diffs:
        cmd.append("-p")
    cmd += ["--", file_path]

    ok, output = _run_git(repo_path, cmd)
    if not ok:
        return json.dumps({"error": f"git log failed: {output}"})

    commits = []
    if show_diffs:
        # Parse interleaved format: commit lines + diff blocks
        current = None
        diff_lines = []
        for line in output.split("\n"):
            if "|" in line and re.match(r"^[0-9a-f]{7,40}\|", line):
                # Save previous
                if current:
                    current["diff"] = "\n".join(diff_lines[:200])
                    commits.append(current)
                    diff_lines = []
                parts = line.split("|", 3)
                if len(parts) >= 4:
                    current = {
                        "commit": parts[0].strip(),
                        "date": parts[1].strip(),
                        "author": parts[2].strip(),
                        "message": parts[3].strip(),
                    }
            elif current is not None:
                diff_lines.append(line)
        if current:
            current["diff"] = "\n".join(diff_lines[:200])
            commits.append(current)
    else:
        for line in output.strip().split("\n"):
            if not line or "|" not in line:
                continue
            parts = line.split("|", 3)
            if len(parts) >= 4:
                commits.append({
                    "commit": parts[0].strip(),
                    "date": parts[1].strip(),
                    "author": parts[2].strip(),
                    "message": parts[3].strip(),
                })

    # If file is deleted, find the deletion commit
    deleted_in = None
    if not exists and commits:
        del_cmd = ["log", "--diff-filter=D", "--format=%H|%ad|%s", "--date=short", "-1", "--", file_path]
        ok, del_out = _run_git(repo_path, del_cmd)
        if ok and del_out.strip():
            parts = del_out.strip().split("|", 2)
            if len(parts) >= 3:
                deleted_in = {"commit": parts[0], "date": parts[1], "message": parts[2]}

    return json.dumps({
        "file": file_path,
        "exists": exists,
        "deleted_in": deleted_in,
        "total_commits": len(commits),
        "commits": commits,
    }, indent=2)


# ========== Tool 4: Capability Changes ==========

@mcp.tool()
def detect_capability_changes(
    repo_path: str,
    before_ref: str = "HEAD~1",
    after_ref: str = "HEAD",
    path_filter: str = "",
) -> str:
    """Detect functions/classes added or removed between two git refs.

    Use this to find regressions: "what was lost in the refactor?"
    Compares before_ref..after_ref and extracts function/class definitions
    from the diff.

    Args:
        repo_path: Absolute path to the git repository root.
        before_ref: Git ref for the "before" state (commit hash, branch, HEAD~N). Default HEAD~1.
        after_ref: Git ref for the "after" state. Default HEAD.
        path_filter: Optional directory/file filter (e.g. "dashboard/").
    """
    valid, err = _validate_repo(repo_path)
    if not valid:
        return json.dumps({"error": err})

    cmd = ["diff", f"{before_ref}..{after_ref}", "-U0"]
    if path_filter:
        cmd += ["--", path_filter]
    ok, output = _run_git(repo_path, cmd)
    if not ok:
        return json.dumps({"error": f"git diff failed: {output}"})

    # Also get file-level summary
    stat_cmd = ["diff", f"{before_ref}..{after_ref}", "--name-status"]
    if path_filter:
        stat_cmd += ["--", path_filter]
    ok, stat_out = _run_git(repo_path, stat_cmd)

    files_created = []
    files_deleted = []
    files_modified = []
    if ok:
        for line in stat_out.strip().split("\n"):
            if not line:
                continue
            parts = line.split("\t", 1)
            if len(parts) == 2:
                status, fpath = parts
                if status == "A":
                    files_created.append(fpath)
                elif status == "D":
                    files_deleted.append(fpath)
                elif status.startswith("R"):
                    parts2 = fpath.split("\t")
                    files_modified.append(f"{parts2[0]} -> {parts2[1]}" if len(parts2) == 2 else fpath)
                else:
                    files_modified.append(fpath)

    # Parse diff for function/class definitions
    added_caps = []
    removed_caps = []
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

        content = line[1:]
        # Skip comments and docstrings
        stripped = content.strip()
        if stripped.startswith("#") or stripped.startswith("//") or stripped.startswith('"""') or stripped.startswith("'''"):
            continue

        # Detect language from file extension
        _, ext = os.path.splitext(current_file)
        lang = LANG_BY_EXT.get(ext, "python")
        pattern = CAPABILITY_PATTERNS.get(lang)
        if not pattern:
            continue

        match = pattern.match(stripped)
        if not match:
            continue

        # Extract the name from whichever group matched
        name = next((g for g in match.groups() if g), None)
        if not name:
            continue

        cap_type = "class" if "class " in stripped else "function"
        entry = {"type": cap_type, "name": name, "file": current_file, "line": stripped}

        if is_add:
            added_caps.append(entry)
        else:
            removed_caps.append(entry)

    # Identify truly removed (in removed but not in added with same name+file)
    added_keys = {(c["name"], c["file"]) for c in added_caps}
    removed_keys = {(c["name"], c["file"]) for c in removed_caps}
    truly_removed = [c for c in removed_caps if (c["name"], c["file"]) not in added_keys]
    truly_added = [c for c in added_caps if (c["name"], c["file"]) not in removed_keys]
    modified = [c for c in removed_caps if (c["name"], c["file"]) in added_keys]

    return json.dumps({
        "before": before_ref,
        "after": after_ref,
        "path_filter": path_filter or "(all)",
        "capabilities_removed": truly_removed,
        "capabilities_added": truly_added,
        "capabilities_modified": [{"name": c["name"], "file": c["file"]} for c in modified],
        "files_created": files_created[:50],
        "files_deleted": files_deleted[:50],
        "files_modified": files_modified[:50],
        "summary": (
            f"Removed {len(truly_removed)} capabilities, "
            f"added {len(truly_added)}, "
            f"modified {len(modified)}. "
            f"Files: +{len(files_created)} -{len(files_deleted)} ~{len(files_modified)}"
        ),
    }, indent=2)


# ========== Tool 5: Directory Activity ==========

@mcp.tool()
def get_directory_activity(
    repo_path: str,
    directory: str,
    since: str = "",
    until: str = "",
    max_results: int = 50,
) -> str:
    """Focused view of all activity within a directory during a time window.

    Use this to answer: "what happened in dashboard/ around Feb 14-15?"

    Args:
        repo_path: Absolute path to the git repository root.
        directory: Relative directory path (e.g. "dashboard/" or "src/api").
        since: Start date (YYYY-MM-DD). Omit for no lower bound.
        until: End date (YYYY-MM-DD). Omit for no upper bound.
        max_results: Max commits to return (default 50).
    """
    valid, err = _validate_repo(repo_path)
    if not valid:
        return json.dumps({"error": err})

    cmd = ["log", f"--format=%H|%ad|%an|%s", "--date=short", "--name-status", f"-{max_results}"]
    if since:
        cmd += [f"--since={since}"]
    if until:
        cmd += [f"--until={until}"]
    cmd += ["--", directory]

    ok, output = _run_git(repo_path, cmd)
    if not ok:
        return json.dumps({"error": f"git log failed: {output}"})

    commits = []
    current = None
    totals = {"A": 0, "M": 0, "D": 0, "R": 0}

    for line in output.split("\n"):
        line = line.strip()
        if not line:
            continue
        if "|" in line and re.match(r"^[0-9a-f]{7,40}\|", line):
            if current:
                commits.append(current)
            parts = line.split("|", 3)
            if len(parts) >= 4:
                current = {
                    "commit": parts[0].strip(),
                    "date": parts[1].strip(),
                    "author": parts[2].strip(),
                    "message": parts[3].strip(),
                    "files": [],
                }
        elif current and line[0] in "AMDRC":
            parts = line.split("\t", 1)
            if len(parts) == 2:
                status = parts[0][0]
                current["files"].append({"status": status, "path": parts[1]})
                if status in totals:
                    totals[status] += 1

    if current:
        commits.append(current)

    return json.dumps({
        "directory": directory,
        "date_range": f"{since or 'start'} to {until or 'now'}",
        "total_commits": len(commits),
        "summary": {
            "files_added": totals["A"],
            "files_modified": totals["M"],
            "files_deleted": totals["D"],
            "files_renamed": totals["R"],
        },
        "commits": commits,
    }, indent=2)


# ========== Entry Point ==========

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--test" and len(sys.argv) > 2:
        repo = sys.argv[2]
        print("=== Testing REH v2 ===\n")
        print("--- get_repo_history (last 5 days) ---")
        print(get_repo_history(repo, limit=5))
        print("\n--- search_code_changes('def ') ---")
        print(search_code_changes(repo, "def ", max_results=3))
        print("\n--- detect_capability_changes (last commit) ---")
        print(detect_capability_changes(repo))
    elif len(sys.argv) > 1 and os.path.isdir(sys.argv[1]):
        print(get_repo_history(sys.argv[1]))
    else:
        mcp.run()
