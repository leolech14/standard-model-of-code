#!/usr/bin/env python3
"""
PRIORITY MATRIX - The Billboard

A real-time dashboard showing the state of all orders in the repo.
Designed to be run frequently and give instant situational awareness.

Usage:
    python priority_matrix.py           # Full billboard
    python priority_matrix.py --compact # One-line summary
    python priority_matrix.py --json    # Machine-readable

The Billboard shows:
- Active TASKs by status (READY, IN_PROGRESS, BLOCKED, DONE)
- Inbox funnel (A+/A/B/C/F grade distribution)
- Sprint progress
- Top priorities for immediate action
"""

import sys
import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Add parent paths for shared modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "context-management" / "tools" / "ai"))

# Paths
AGENT_DIR = Path(__file__).parent.parent
PROJECT_ROOT = AGENT_DIR.parent
ACTIVE_DIR = AGENT_DIR / "registry" / "active"
INBOX_DIR = AGENT_DIR / "registry" / "inbox"
SPRINTS_DIR = AGENT_DIR / "sprints"
ROADMAPS_DIR = AGENT_DIR / "roadmaps"
OPEN_CONCERNS_PATH = PROJECT_ROOT / "standard-model-of-code" / "docs" / "OPEN_CONCERNS.md"
SMOC_DIR = PROJECT_ROOT / "standard-model-of-code"

# ANSI Colors
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"
WHITE = "\033[97m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"
BG_RED = "\033[41m"
BG_GREEN = "\033[42m"
BG_YELLOW = "\033[43m"
BG_BLUE = "\033[44m"

# Status colors
STATUS_COLORS = {
    "READY": GREEN,
    "IN_PROGRESS": YELLOW,
    "BLOCKED": RED,
    "DONE": DIM,
    "COMPLETED": DIM,
    "PENDING": CYAN,
}

# Priority colors
PRIORITY_COLORS = {
    "P0": f"{BG_RED}{WHITE}",
    "P1": RED,
    "P2": YELLOW,
    "P3": CYAN,
}

# Grade thresholds (same as industrial_triage.py)
GRADES = {"A+": 95, "A": 85, "B": 70, "C": 50, "F": 0}


def load_tasks() -> List[Dict]:
    """Load all TASK-*.yaml from active directory."""
    tasks = []
    if not ACTIVE_DIR.exists():
        return tasks

    for task_file in sorted(ACTIVE_DIR.glob("TASK-*.yaml")):
        try:
            with open(task_file) as f:
                task = yaml.safe_load(f)
                if task:
                    task["_file"] = task_file.name
                    tasks.append(task)
        except Exception as e:
            print(f"Warning: Failed to load {task_file}: {e}", file=sys.stderr)

    return tasks


def load_opportunities() -> List[Dict]:
    """Load all OPP-*.yaml from inbox."""
    opps = []
    if not INBOX_DIR.exists():
        return opps

    for opp_file in sorted(INBOX_DIR.glob("OPP-*.yaml")):
        try:
            with open(opp_file) as f:
                opp = yaml.safe_load(f)
                if opp:
                    opp["_file"] = opp_file.name
                    opps.append(opp)
        except Exception:
            pass

    return opps


def load_current_sprint() -> Optional[Dict]:
    """Load the most recent sprint file."""
    if not SPRINTS_DIR.exists():
        return None

    sprint_files = sorted(SPRINTS_DIR.glob("SPRINT-*.yaml"), reverse=True)
    if sprint_files:
        try:
            with open(sprint_files[0]) as f:
                return yaml.safe_load(f)
        except Exception:
            pass
    return None


def load_roadmap() -> Optional[Dict]:
    """Load the main roadmap file."""
    if not ROADMAPS_DIR.exists():
        return None

    roadmap_file = ROADMAPS_DIR / "ROADMAP-main.yaml"
    if roadmap_file.exists():
        try:
            with open(roadmap_file) as f:
                return yaml.safe_load(f)
        except Exception:
            pass
    return None


def load_open_concerns() -> List[Dict]:
    """Parse OPEN_CONCERNS.md for structured concerns."""
    concerns = []
    if not OPEN_CONCERNS_PATH.exists():
        return concerns

    try:
        content = OPEN_CONCERNS_PATH.read_text()

        # Parse table rows for concerns (simplified parsing)
        import re
        # Match: | OC-XXX | **text** | impact | STATUS | action |
        pattern = r'\|\s*(OC-\d+)\s*\|\s*\*?\*?([^|]+?)\*?\*?\s*\|\s*([^|]+)\s*\|\s*\*?\*?([^|]+?)\*?\*?\s*\|\s*([^|]+)\s*\|'

        for match in re.finditer(pattern, content):
            concerns.append({
                "id": match.group(1).strip(),
                "concern": match.group(2).strip(),
                "impact": match.group(3).strip(),
                "status": match.group(4).strip(),
                "action": match.group(5).strip(),
            })
    except Exception as e:
        print(f"Warning: Failed to parse OPEN_CONCERNS.md: {e}", file=sys.stderr)

    return concerns


def count_todos_fixmes() -> Dict[str, int]:
    """Count TODO and FIXME comments in Python files."""
    import subprocess

    counts = {"TODO": 0, "FIXME": 0}

    try:
        # Count TODOs
        result = subprocess.run(
            ["grep", "-r", "-c", "TODO", "--include=*.py", str(SMOC_DIR)],
            capture_output=True, text=True, timeout=10
        )
        for line in result.stdout.strip().split('\n'):
            if ':' in line:
                try:
                    counts["TODO"] += int(line.split(':')[-1])
                except ValueError:
                    pass

        # Count FIXMEs
        result = subprocess.run(
            ["grep", "-r", "-c", "FIXME", "--include=*.py", str(SMOC_DIR)],
            capture_output=True, text=True, timeout=10
        )
        for line in result.stdout.strip().split('\n'):
            if ':' in line:
                try:
                    counts["FIXME"] += int(line.split(':')[-1])
                except ValueError:
                    pass
    except Exception:
        pass

    return counts


def get_roadmap_phases(roadmap: Optional[Dict]) -> List[Dict]:
    """Extract phase status from roadmap."""
    if not roadmap:
        return []

    phases = roadmap.get("phases", [])
    return [
        {
            "id": p.get("id", "?"),
            "name": p.get("name", "?"),
            "status": p.get("status", "PLANNED"),
            "completion": p.get("completion", 0),
        }
        for p in phases
    ]


def compute_grade(opp: Dict) -> str:
    """Compute grade for an opportunity based on confidence."""
    conf = opp.get("confidence", {})
    factual = conf.get("factual", 50)
    alignment = conf.get("alignment", 50)
    current = conf.get("current", 50)
    onwards = conf.get("onwards", 50)
    overall = min(factual, alignment, current, onwards)

    for grade, threshold in sorted(GRADES.items(), key=lambda x: -x[1]):
        if overall >= threshold:
            return grade
    return "F"


def categorize_tasks(tasks: List[Dict]) -> Dict[str, List[Dict]]:
    """Categorize tasks by status."""
    categories = {
        "READY": [],
        "IN_PROGRESS": [],
        "BLOCKED": [],
        "DONE": [],
    }

    for task in tasks:
        status = task.get("status", "READY").upper()
        if status in ["COMPLETED", "DONE"]:
            categories["DONE"].append(task)
        elif status == "BLOCKED":
            categories["BLOCKED"].append(task)
        elif status == "IN_PROGRESS":
            categories["IN_PROGRESS"].append(task)
        else:
            categories["READY"].append(task)

    return categories


def categorize_inbox(opps: List[Dict]) -> Dict[str, int]:
    """Categorize inbox by grade."""
    grades = {"A+": 0, "A": 0, "B": 0, "C": 0, "F": 0}
    for opp in opps:
        grade = compute_grade(opp)
        grades[grade] = grades.get(grade, 0) + 1
    return grades


def get_top_priorities(tasks: List[Dict], limit: int = 5) -> List[Dict]:
    """Get top priority tasks that are actionable."""
    actionable = [t for t in tasks if t.get("status", "").upper() in ["READY", "IN_PROGRESS"]]

    def priority_key(t):
        p = t.get("priority", "P2")
        return {"P0": 0, "P1": 1, "P2": 2, "P3": 3}.get(p, 2)

    return sorted(actionable, key=priority_key)[:limit]


def render_billboard(tasks: List[Dict], opps: List[Dict], sprint: Optional[Dict],
                     roadmap: Optional[Dict] = None, concerns: Optional[List[Dict]] = None,
                     todos: Optional[Dict[str, int]] = None):
    """Render the full priority matrix billboard with ALL data sources."""
    task_cats = categorize_tasks(tasks)
    inbox_grades = categorize_inbox(opps)
    top_priorities = get_top_priorities(tasks)
    phases = get_roadmap_phases(roadmap)
    concerns = concerns or []
    todos = todos or {"TODO": 0, "FIXME": 0}

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Header
    print()
    print(f"{MAGENTA}{'█' * 74}{RESET}")
    print(f"{MAGENTA}█{RESET}{' ' * 72}{MAGENTA}█{RESET}")
    print(f"{MAGENTA}█{RESET}  {BOLD}{WHITE}P R I O R I T Y   M A T R I X{RESET}                                       {MAGENTA}█{RESET}")
    print(f"{MAGENTA}█{RESET}  {DIM}The Billboard - State of All Orders{RESET}                                  {MAGENTA}█{RESET}")
    print(f"{MAGENTA}█{RESET}{' ' * 72}{MAGENTA}█{RESET}")
    print(f"{MAGENTA}{'█' * 74}{RESET}")
    print(f"  {DIM}Generated: {now}{RESET}")
    print()

    # Sprint Status
    if sprint:
        sprint_id = sprint.get("id", "?")
        sprint_name = sprint.get("name", "?")[:40]
        sprint_status = sprint.get("status", "ACTIVE")
        print(f"  {CYAN}ACTIVE SPRINT{RESET}")
        print(f"  {DIM}{'─' * 70}{RESET}")
        print(f"    {BOLD}{sprint_id}{RESET}: {sprint_name} [{sprint_status}]")
        print()

    # Task Status Overview
    total_tasks = len(tasks)
    ready = len(task_cats["READY"])
    in_prog = len(task_cats["IN_PROGRESS"])
    blocked = len(task_cats["BLOCKED"])
    done = len(task_cats["DONE"])

    print(f"  {BLUE}TASK STATUS{RESET} ({total_tasks} total)")
    print(f"  {DIM}{'─' * 70}{RESET}")

    # Status bars (compact - 20 char width)
    bar_width = 20
    for status, count in [("READY", ready), ("IN_PROGRESS", in_prog), ("BLOCKED", blocked), ("DONE", done)]:
        color = STATUS_COLORS.get(status, WHITE)
        pct = count / max(total_tasks, 1)
        filled = int(pct * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)
        print(f"    {color}{status:11}{RESET} {bar} {BOLD}{count:3}{RESET}")
    print()

    # Inbox Funnel
    total_inbox = len(opps)
    print(f"  {YELLOW}INBOX FUNNEL{RESET} ({total_inbox} opportunities)")
    print(f"  {DIM}{'─' * 70}{RESET}")

    grade_colors = {"A+": GREEN, "A": GREEN, "B": YELLOW, "C": YELLOW, "F": RED}
    for grade in ["A+", "A", "B", "C", "F"]:
        count = inbox_grades[grade]
        color = grade_colors[grade]
        pct = count / max(total_inbox, 1)
        filled = int(pct * bar_width)  # bar_width is 20
        bar = "█" * filled + "░" * (bar_width - filled)
        status_hint = "↑" if grade in ["A+", "A"] else "?" if grade in ["B", "C"] else "!"
        print(f"    {color}{grade:2}{RESET} {bar} {BOLD}{count:3}{RESET} {DIM}{status_hint}{RESET}")
    print()

    # Roadmap Phases
    if phases:
        print(f"  {CYAN}ROADMAP PHASES{RESET}")
        print(f"  {DIM}{'─' * 70}{RESET}")
        for phase in phases[:6]:  # Show top 6 phases
            p_id = phase["id"]
            p_name = phase["name"][:30]
            p_status = phase["status"]
            p_comp = phase["completion"]

            # Status color
            if p_status == "COMPLETE":
                s_color = DIM
            elif p_status == "ACTIVE":
                s_color = GREEN
            else:
                s_color = YELLOW

            # Progress bar
            filled = int(p_comp / 100 * 20)
            bar = "█" * filled + "░" * (20 - filled)

            print(f"    {s_color}{p_id:4}{RESET} {bar} {BOLD}{p_comp:3}%{RESET} {p_name}")
        print()

    # Open Concerns
    if concerns:
        high_concerns = [c for c in concerns if "HIGH" in c.get("impact", "").upper() or "BUG" in c.get("status", "").upper()]
        print(f"  {RED}OPEN CONCERNS{RESET} ({len(concerns)} total, {len(high_concerns)} high priority)")
        print(f"  {DIM}{'─' * 70}{RESET}")
        for oc in concerns[:5]:  # Show top 5
            oc_id = oc["id"]
            oc_concern = oc["concern"][:40]
            oc_status = oc["status"]

            if "BUG" in oc_status.upper():
                s_color = RED
            elif "ENVIRONMENT" in oc_status.upper() or "INVESTIGATE" in oc_status.upper():
                s_color = YELLOW
            else:
                s_color = CYAN

            print(f"    {s_color}{oc_id:7}{RESET} {oc_concern} [{oc_status}]")
        if len(concerns) > 5:
            print(f"    {DIM}... and {len(concerns) - 5} more{RESET}")
        print()

    # Code Debt (TODO/FIXME)
    if todos["TODO"] > 0 or todos["FIXME"] > 0:
        print(f"  {YELLOW}CODE DEBT{RESET}")
        print(f"  {DIM}{'─' * 70}{RESET}")
        print(f"    {YELLOW}TODO:{RESET}  {todos['TODO']:4} comments")
        print(f"    {RED}FIXME:{RESET} {todos['FIXME']:4} comments")
        print()

    # Top Priorities (THE ORDERS)
    print(f"  {RED}▼ TOP PRIORITIES ▼{RESET}")
    print(f"  {DIM}{'─' * 70}{RESET}")

    if top_priorities:
        for i, task in enumerate(top_priorities, 1):
            task_id = task.get("id", "?")
            title = task.get("title", "?")[:45]
            priority = task.get("priority", "P2")
            status = task.get("status", "READY").upper()

            p_color = PRIORITY_COLORS.get(priority, WHITE)
            s_color = STATUS_COLORS.get(status, WHITE)

            print(f"    {BOLD}{i}.{RESET} {p_color}[{priority}]{RESET} {task_id:10} {s_color}{status:12}{RESET} {title}")
    else:
        print(f"    {DIM}No actionable tasks{RESET}")
    print()

    # Quick Stats Footer
    promotable = inbox_grades["A+"] + inbox_grades["A"]
    needs_work = inbox_grades["B"] + inbox_grades["C"] + inbox_grades["F"]

    print(f"  {DIM}{'─' * 70}{RESET}")
    print(f"  {GREEN}▸ Ready:{RESET} {ready}  {YELLOW}▸ In Progress:{RESET} {in_prog}  {RED}▸ Blocked:{RESET} {blocked}  {DIM}▸ Done:{RESET} {done}")
    print(f"  {GREEN}▸ Promotable:{RESET} {promotable}  {YELLOW}▸ Needs Research:{RESET} {needs_work}")
    print()
    print(f"{MAGENTA}{'█' * 74}{RESET}")
    print()


def render_compact(tasks: List[Dict], opps: List[Dict]):
    """One-line summary for quick checks."""
    task_cats = categorize_tasks(tasks)
    inbox_grades = categorize_inbox(opps)

    ready = len(task_cats["READY"])
    in_prog = len(task_cats["IN_PROGRESS"])
    blocked = len(task_cats["BLOCKED"])
    promotable = inbox_grades["A+"] + inbox_grades["A"]

    print(f"{MAGENTA}[MATRIX]{RESET} Tasks: {GREEN}{ready}R{RESET}/{YELLOW}{in_prog}P{RESET}/{RED}{blocked}B{RESET} | Inbox: {GREEN}{promotable}↑{RESET}/{YELLOW}{len(opps)-promotable}?{RESET}")


def render_json(tasks: List[Dict], opps: List[Dict], sprint: Optional[Dict]):
    """Machine-readable JSON output."""
    task_cats = categorize_tasks(tasks)
    inbox_grades = categorize_inbox(opps)

    output = {
        "timestamp": datetime.now().isoformat(),
        "tasks": {
            "total": len(tasks),
            "ready": len(task_cats["READY"]),
            "in_progress": len(task_cats["IN_PROGRESS"]),
            "blocked": len(task_cats["BLOCKED"]),
            "done": len(task_cats["DONE"]),
        },
        "inbox": {
            "total": len(opps),
            "grades": inbox_grades,
            "promotable": inbox_grades["A+"] + inbox_grades["A"],
        },
        "sprint": sprint.get("id") if sprint else None,
        "top_priorities": [
            {"id": t.get("id"), "priority": t.get("priority"), "title": t.get("title")}
            for t in get_top_priorities(tasks)
        ],
    }
    print(json.dumps(output, indent=2))


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Priority Matrix - The Billboard")
    parser.add_argument("--compact", "-c", action="store_true", help="One-line summary")
    parser.add_argument("--json", "-j", action="store_true", help="JSON output")
    args = parser.parse_args()

    # Load ALL data sources
    tasks = load_tasks()
    opps = load_opportunities()
    sprint = load_current_sprint()
    roadmap = load_roadmap()
    concerns = load_open_concerns()
    todos = count_todos_fixmes()

    # Render
    if args.json:
        render_json(tasks, opps, sprint)
    elif args.compact:
        render_compact(tasks, opps)
    else:
        render_billboard(tasks, opps, sprint, roadmap, concerns, todos)


if __name__ == "__main__":
    main()
