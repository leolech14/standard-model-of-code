#!/usr/bin/env python3
"""
INDUSTRIAL TRIAGE - Batch Inbox Processor

Processes ALL inbox items at scale:
1. Load all OPP-*.yaml from inbox
2. Compute confidence scores
3. Categorize by grade (A+, A, B, C, F)
4. Generate triage report
5. Identify items needing research

Usage:
    python industrial_triage.py              # Full triage report
    python industrial_triage.py --promote    # Auto-promote A+ items to TASK
    python industrial_triage.py --json       # JSON output for pipelines
"""

import os
import sys
import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# Add parent paths for shared modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "context-management" / "tools" / "ai"))

# Import Industrial UI
try:
    from industrial_ui import TriageUI, Colors
    HAS_INDUSTRIAL_UI = True
except ImportError:
    HAS_INDUSTRIAL_UI = False

# Paths
AGENT_DIR = Path(__file__).parent.parent
INBOX_DIR = AGENT_DIR / "registry" / "inbox"
ACTIVE_DIR = AGENT_DIR / "registry" / "active"
REPORTS_DIR = AGENT_DIR / "intelligence" / "triage_reports"

# Grade thresholds
GRADES = {
    "A+": 95,  # Ready to execute, high confidence
    "A": 85,   # Promotable to TASK
    "B": 70,   # Needs minor refinement
    "C": 50,   # Needs significant research
    "F": 0,    # Unvalidated, needs full workup
}

# ANSI Colors (fallback if industrial_ui not available)
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"


def load_all_opportunities() -> List[Dict]:
    """Load all OPP-*.yaml files from inbox."""
    opportunities = []

    if not INBOX_DIR.exists():
        return opportunities

    for opp_file in sorted(INBOX_DIR.glob("OPP-*.yaml")):
        try:
            with open(opp_file) as f:
                opp = yaml.safe_load(f)
                if opp:
                    opp["_file"] = opp_file.name
                    opp["_path"] = str(opp_file)
                    opportunities.append(opp)
        except Exception as e:
            print(f"Warning: Failed to load {opp_file}: {e}", file=sys.stderr)

    return opportunities


def compute_confidence(opp: Dict) -> Tuple[int, str]:
    """
    Compute overall confidence and grade for an opportunity.

    Confidence dimensions:
    - factual: Is the information accurate?
    - alignment: Does it align with project goals?
    - current: Is it actionable now?
    - onwards: Will it remain relevant?
    """
    conf = opp.get("confidence", {})

    # Extract dimensions (default to 50 if missing)
    factual = conf.get("factual", 50)
    alignment = conf.get("alignment", 50)
    current = conf.get("current", 50)
    onwards = conf.get("onwards", 50)

    # Overall = minimum of all dimensions (weakest link)
    overall = min(factual, alignment, current, onwards)

    # Determine grade
    grade = "F"
    for g, threshold in sorted(GRADES.items(), key=lambda x: -x[1]):
        if overall >= threshold:
            grade = g
            break

    return overall, grade


def categorize_opportunities(opportunities: List[Dict]) -> Dict[str, List[Dict]]:
    """Categorize opportunities by grade."""
    categories = {grade: [] for grade in GRADES.keys()}

    for opp in opportunities:
        overall, grade = compute_confidence(opp)
        opp["_overall"] = overall
        opp["_grade"] = grade
        categories[grade].append(opp)

    return categories


def identify_research_needs(opportunities: List[Dict]) -> List[Dict]:
    """Identify items that need research to raise confidence."""
    needs_research = []

    for opp in opportunities:
        conf = opp.get("confidence", {})
        overall = opp.get("_overall", 50)

        # Items below A grade need research
        if overall < 85:
            # Identify weakest dimension
            dims = {
                "factual": conf.get("factual", 50),
                "alignment": conf.get("alignment", 50),
                "current": conf.get("current", 50),
                "onwards": conf.get("onwards", 50),
            }
            weakest = min(dims, key=dims.get)

            needs_research.append({
                "id": opp.get("id", "?"),
                "title": opp.get("title", "?"),
                "overall": overall,
                "grade": opp.get("_grade", "?"),
                "weakest_dimension": weakest,
                "weakest_score": dims[weakest],
                "gap_to_A": 85 - overall,
                "refinery_needs": opp.get("refinery_needs", []),
            })

    return sorted(needs_research, key=lambda x: -x["gap_to_A"])


def render_report(categories: Dict[str, List[Dict]], research_needs: List[Dict]):
    """Render industrial triage report to terminal."""
    total = sum(len(items) for items in categories.values())

    print()
    print(f"{YELLOW}{'═' * 70}{RESET}")
    print(f"{YELLOW}  INDUSTRIAL TRIAGE REPORT{RESET}")
    print(f"{YELLOW}{'═' * 70}{RESET}")
    print()
    print(f"  {DIM}Generated:{RESET} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  {DIM}Total Inbox:{RESET} {BOLD}{total}{RESET} opportunities")
    print()

    # Grade distribution
    print(f"  {CYAN}GRADE DISTRIBUTION{RESET}")
    print(f"  {DIM}{'─' * 50}{RESET}")

    grade_colors = {"A+": GREEN, "A": GREEN, "B": YELLOW, "C": YELLOW, "F": RED}

    for grade in ["A+", "A", "B", "C", "F"]:
        items = categories[grade]
        count = len(items)
        bar_len = int((count / max(total, 1)) * 30)
        bar = "█" * bar_len + "░" * (30 - bar_len)
        color = grade_colors[grade]

        print(f"  {color}{grade:3}{RESET} {bar} {BOLD}{count:3}{RESET} ({count/max(total,1)*100:5.1f}%)")

    print()

    # Ready to promote (A+/A)
    promotable = categories["A+"] + categories["A"]
    if promotable:
        print(f"  {GREEN}READY TO PROMOTE ({len(promotable)}){RESET}")
        print(f"  {DIM}{'─' * 50}{RESET}")
        for opp in promotable[:10]:  # Show top 10
            print(f"    {GREEN}✓{RESET} {opp.get('id', '?'):10} {opp.get('_overall', 0):3}% {opp.get('title', '?')[:40]}")
        if len(promotable) > 10:
            print(f"    {DIM}... and {len(promotable) - 10} more{RESET}")
        print()

    # Needs research
    if research_needs:
        print(f"  {YELLOW}NEEDS RESEARCH ({len(research_needs)}){RESET}")
        print(f"  {DIM}{'─' * 50}{RESET}")
        for item in research_needs[:10]:
            gap = item["gap_to_A"]
            weak = item["weakest_dimension"][:3]
            print(f"    {YELLOW}?{RESET} {item['id']:10} {item['overall']:3}% (+{gap} needed) [{weak}] {item['title'][:30]}")
        if len(research_needs) > 10:
            print(f"    {DIM}... and {len(research_needs) - 10} more{RESET}")
        print()

    # Summary stats
    promotable_count = len(categories["A+"]) + len(categories["A"])
    needs_work_count = len(categories["B"]) + len(categories["C"]) + len(categories["F"])

    print(f"  {DIM}{'─' * 50}{RESET}")
    print(f"  {GREEN}▸ Promotable:{RESET} {promotable_count}  {YELLOW}▸ Needs work:{RESET} {needs_work_count}")
    print()
    print(f"{YELLOW}{'═' * 70}{RESET}")
    print()


def save_report(categories: Dict[str, List[Dict]], research_needs: List[Dict]) -> Path:
    """Save triage report as JSON."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = REPORTS_DIR / f"{timestamp}_triage.json"

    report = {
        "timestamp": datetime.now().isoformat(),
        "total": sum(len(items) for items in categories.values()),
        "distribution": {grade: len(items) for grade, items in categories.items()},
        "promotable": [
            {"id": o.get("id"), "title": o.get("title"), "confidence": o.get("_overall")}
            for o in categories["A+"] + categories["A"]
        ],
        "needs_research": research_needs,
    }

    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    return report_path


def auto_promote(categories: Dict[str, List[Dict]]) -> int:
    """Auto-promote A+ items to TASK status."""
    promoted = 0

    for opp in categories["A+"]:
        opp_id = opp.get("id", "")
        if not opp_id.startswith("OPP-"):
            continue

        # Generate TASK ID
        task_num = opp_id.replace("OPP-", "")
        task_id = f"TASK-{task_num}"
        task_path = ACTIVE_DIR / f"{task_id}.yaml"

        if task_path.exists():
            continue  # Already promoted

        # Create TASK from OPP
        task = {
            "id": task_id,
            "title": opp.get("title"),
            "status": "READY",
            "priority": opp.get("priority", "P2"),
            "domain": opp.get("category", "unknown").lower(),
            "description": opp.get("description", ""),
            "confidence": opp.get("confidence", {}),
            "source_opp": opp_id,
            "promoted_at": datetime.now().isoformat(),
            "steps": opp.get("steps", []),
        }

        ACTIVE_DIR.mkdir(parents=True, exist_ok=True)
        with open(task_path, "w") as f:
            yaml.dump(task, f, default_flow_style=False, sort_keys=False)

        promoted += 1
        print(f"  {GREEN}✓ Promoted:{RESET} {opp_id} → {task_id}")

    return promoted


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Industrial-scale inbox triage")
    parser.add_argument("--promote", action="store_true", help="Auto-promote A+ items")
    parser.add_argument("--json", action="store_true", help="JSON output only")
    args = parser.parse_args()

    # Load and categorize
    opportunities = load_all_opportunities()
    categories = categorize_opportunities(opportunities)
    research_needs = identify_research_needs(opportunities)

    if args.json:
        report = {
            "total": len(opportunities),
            "distribution": {g: len(items) for g, items in categories.items()},
            "promotable": len(categories["A+"]) + len(categories["A"]),
            "needs_research": len(research_needs),
        }
        print(json.dumps(report, indent=2))
        return

    # Render report
    render_report(categories, research_needs)

    # Save report
    report_path = save_report(categories, research_needs)
    print(f"  {DIM}Report saved: {report_path}{RESET}")
    print()

    # Auto-promote if requested
    if args.promote:
        print(f"  {CYAN}AUTO-PROMOTING A+ ITEMS...{RESET}")
        promoted = auto_promote(categories)
        print(f"  {GREEN}Promoted {promoted} items{RESET}")
        print()


if __name__ == "__main__":
    main()
