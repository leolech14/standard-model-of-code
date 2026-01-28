#!/usr/bin/env python3
"""
Active Docs Audit - Quality Gates G3, G4, G5
=============================================

Scans active documentation for:
- G3: Broken internal links
- G4: Unresolved placeholders ({...}, TODO, FIXME)
- G5: validated_* file integrity (missing PASS/FAIL headers)

Saves persistent results to refinery output.

Usage:
    python docs_audit.py              # Full audit
    python docs_audit.py --gate G3    # Specific gate only
    python docs_audit.py --fix        # Auto-fix what's possible
"""

import re
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Set
from dataclasses import dataclass, asdict
from collections import defaultdict

# Paths
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
DOCS_ROOT = PROJECT_ROOT / "context-management" / "docs"
OUTPUT_DIR = PROJECT_ROOT / ".agent" / "intelligence" / "chunks"
REFINERY_REPORTS_DIR = PROJECT_ROOT / "context-management" / "reports" / "refinery"

# Active doc patterns (exclude these)
INACTIVE_PATTERNS = [
    "**/archive/**",
    "**/legacy_root_scatter/**",
    "**/legacy_schema_2025/**",
]


@dataclass
class LinkIssue:
    """Broken link finding."""
    file: str
    line: int
    link_text: str
    target: str
    issue: str


@dataclass
class PlaceholderIssue:
    """Unresolved placeholder finding."""
    file: str
    line: int
    pattern: str
    context: str


@dataclass
class ValidationIssue:
    """validated_* file integrity issue."""
    file: str
    issue: str
    suggestion: str


@dataclass
class AuditReport:
    """Complete audit results."""
    timestamp: str
    git_sha: str
    files_scanned: int
    active_files: int

    # G3: Links
    g3_broken_links: List[LinkIssue]
    g3_status: str

    # G4: Placeholders
    g4_placeholders: List[PlaceholderIssue]
    g4_status: str

    # G5: Validation files
    g5_validation_issues: List[ValidationIssue]
    g5_status: str

    overall_status: str


def get_git_sha() -> str:
    """Get current git SHA."""
    import subprocess
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()[:8]
    except Exception:
        return "unknown"


def is_active_doc(filepath: Path) -> bool:
    """Check if doc is active (not archived/legacy)."""
    rel_path = str(filepath.relative_to(PROJECT_ROOT))

    for pattern in INACTIVE_PATTERNS:
        if filepath.match(pattern):
            return False

    return True


def scan_markdown_files() -> List[Path]:
    """Find all markdown files in context-management/docs."""
    all_docs = list(DOCS_ROOT.rglob("*.md"))
    active_docs = [doc for doc in all_docs if is_active_doc(doc)]
    return active_docs


def check_broken_links(files: List[Path]) -> List[LinkIssue]:
    """G3: Check for broken internal links."""
    issues = []

    # Pattern for markdown links: [text](path)
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

    for filepath in files:
        try:
            content = filepath.read_text()
            lines = content.split('\n')

            for line_num, line in enumerate(lines, 1):
                for match in link_pattern.finditer(line):
                    link_text = match.group(1)
                    target = match.group(2)

                    # Skip external links, anchors, mailto
                    if target.startswith(('http://', 'https://', 'mailto:', '#')):
                        continue

                    # Resolve relative path
                    if target.startswith('/'):
                        # Root-relative
                        target_path = PROJECT_ROOT / target.lstrip('/')
                    else:
                        # Relative to current file
                        target_path = (filepath.parent / target).resolve()

                    # Remove anchor
                    if '#' in str(target_path):
                        target_path = Path(str(target_path).split('#')[0])

                    # Check if target exists
                    if not target_path.exists():
                        issues.append(LinkIssue(
                            file=str(filepath.relative_to(PROJECT_ROOT)),
                            line=line_num,
                            link_text=link_text,
                            target=target,
                            issue=f"Target does not exist: {target_path}"
                        ))

        except Exception as e:
            print(f"Error scanning {filepath}: {e}")

    return issues


def check_placeholders(files: List[Path]) -> List[PlaceholderIssue]:
    """G4: Check for unresolved placeholders."""
    issues = []

    # Patterns to detect
    placeholder_patterns = [
        (r'\{[^}|]+\}', 'curly_brace'),  # {variable} but not {var|default}
        (r'\bTODO(?!\(#\d+\))', 'todo_unlinked'),  # TODO without issue link
        (r'\bFIXME(?!\(#\d+\))', 'fixme_unlinked'),
        (r'\bXXX\b', 'xxx_marker'),
    ]

    for filepath in files:
        try:
            content = filepath.read_text()
            lines = content.split('\n')

            for line_num, line in enumerate(lines, 1):
                for pattern, pattern_type in placeholder_patterns:
                    for match in re.finditer(pattern, line):
                        # Skip code blocks (lines starting with 4 spaces or tab)
                        if line.startswith(('    ', '\t')):
                            continue

                        # Extract context (30 chars around match)
                        start = max(0, match.start() - 15)
                        end = min(len(line), match.end() + 15)
                        context = line[start:end].strip()

                        issues.append(PlaceholderIssue(
                            file=str(filepath.relative_to(PROJECT_ROOT)),
                            line=line_num,
                            pattern=pattern_type,
                            context=context
                        ))

        except Exception as e:
            print(f"Error scanning {filepath}: {e}")

    return issues


def check_validation_files(files: List[Path]) -> List[ValidationIssue]:
    """G5: Check validated_* files for PASS/FAIL headers."""
    issues = []

    for filepath in files:
        if not filepath.name.startswith('validated_'):
            continue

        try:
            content = filepath.read_text()

            # Check for status header in first 20 lines
            header_section = '\n'.join(content.split('\n')[:20])

            has_status = bool(re.search(
                r'(?:Status|Result):\s*(PASS|FAIL|PARTIAL)',
                header_section,
                re.IGNORECASE
            ))

            if not has_status:
                # Check if it looks like a stack trace or error log
                if 'Traceback' in content or 'Error:' in content[:500]:
                    issues.append(ValidationIssue(
                        file=str(filepath.relative_to(PROJECT_ROOT)),
                        issue="Contains stack trace/errors without status header",
                        suggestion=f"Rename to: FAILED_{filepath.name.replace('validated_', '')}"
                    ))
                else:
                    issues.append(ValidationIssue(
                        file=str(filepath.relative_to(PROJECT_ROOT)),
                        issue="Missing Status: PASS/FAIL/PARTIAL header",
                        suggestion="Add header in first 20 lines"
                    ))

        except Exception as e:
            print(f"Error scanning {filepath}: {e}")

    return issues


def generate_report(
    files: List[Path],
    link_issues: List[LinkIssue],
    placeholder_issues: List[PlaceholderIssue],
    validation_issues: List[ValidationIssue]
) -> AuditReport:
    """Generate complete audit report."""

    all_files = list(DOCS_ROOT.rglob("*.md"))

    # Determine gate statuses
    g3_status = "PASS" if len(link_issues) == 0 else "FAIL"
    g4_status = "PASS" if len(placeholder_issues) == 0 else "FAIL"
    g5_status = "PASS" if len(validation_issues) == 0 else "FAIL"

    passing = [g3_status, g4_status, g5_status].count("PASS")
    overall = "PASS" if passing == 3 else f"FAIL ({passing}/3 gates pass)"

    return AuditReport(
        timestamp=datetime.now().isoformat(),
        git_sha=get_git_sha(),
        files_scanned=len(all_files),
        active_files=len(files),
        g3_broken_links=link_issues,
        g3_status=g3_status,
        g4_placeholders=placeholder_issues,
        g4_status=g4_status,
        g5_validation_issues=validation_issues,
        g5_status=g5_status,
        overall_status=overall
    )


def save_report(report: AuditReport):
    """Save report to refinery output."""

    # Create reports directory
    REFINERY_REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save as JSON (machine-readable)
    json_file = REFINERY_REPORTS_DIR / f"docs_audit_{timestamp}.json"
    with open(json_file, 'w') as f:
        json.dump(asdict(report), f, indent=2, default=str)

    # Save as Markdown (human-readable)
    md_file = REFINERY_REPORTS_DIR / f"docs_audit_{timestamp}.md"
    with open(md_file, 'w') as f:
        f.write(format_markdown_report(report))

    # Update latest symlink
    latest_json = REFINERY_REPORTS_DIR / "docs_audit_latest.json"
    latest_md = REFINERY_REPORTS_DIR / "docs_audit_latest.md"

    if latest_json.exists():
        latest_json.unlink()
    if latest_md.exists():
        latest_md.unlink()

    latest_json.symlink_to(json_file.name)
    latest_md.symlink_to(md_file.name)

    print(f"\n✅ Report saved:")
    print(f"   JSON: {json_file}")
    print(f"   MD:   {md_file}")
    print(f"   Latest: {latest_md}")


def format_markdown_report(report: AuditReport) -> str:
    """Format report as markdown."""

    lines = [
        "# Active Docs Audit Report",
        "",
        f"**Generated:** {report.timestamp}",
        f"**Git SHA:** {report.git_sha}",
        f"**Files Scanned:** {report.files_scanned} total, {report.active_files} active",
        "",
        "---",
        "",
        "## Summary",
        "",
        f"**Overall Status:** {report.overall_status}",
        "",
        f"- **G3 Link Integrity:** {report.g3_status} ({len(report.g3_broken_links)} broken links)",
        f"- **G4 Placeholder Check:** {report.g4_status} ({len(report.g4_placeholders)} unresolved)",
        f"- **G5 Validation Naming:** {report.g5_status} ({len(report.g5_validation_issues)} issues)",
        "",
        "---",
        "",
    ]

    # G3: Broken Links
    lines.extend([
        "## G3: Broken Internal Links",
        "",
        f"**Status:** {report.g3_status}",
        f"**Count:** {len(report.g3_broken_links)}",
        "",
    ])

    if report.g3_broken_links:
        lines.append("### Issues")
        lines.append("")

        by_file = defaultdict(list)
        for issue in report.g3_broken_links:
            by_file[issue.file].append(issue)

        for filepath, issues in sorted(by_file.items()):
            lines.append(f"#### {filepath}")
            lines.append("")
            for issue in issues:
                lines.append(f"- Line {issue.line}: `[{issue.link_text}]({issue.target})`")
                lines.append(f"  - Issue: {issue.issue}")
            lines.append("")
    else:
        lines.append("✅ No broken links found.")
        lines.append("")

    lines.append("---")
    lines.append("")

    # G4: Placeholders
    lines.extend([
        "## G4: Unresolved Placeholders",
        "",
        f"**Status:** {report.g4_status}",
        f"**Count:** {len(report.g4_placeholders)}",
        "",
    ])

    if report.g4_placeholders:
        lines.append("### Issues")
        lines.append("")

        by_file = defaultdict(list)
        for issue in report.g4_placeholders:
            by_file[issue.file].append(issue)

        for filepath, issues in sorted(by_file.items()):
            lines.append(f"#### {filepath}")
            lines.append("")
            for issue in issues:
                lines.append(f"- Line {issue.line} ({issue.pattern}): `{issue.context}`")
            lines.append("")
    else:
        lines.append("✅ No unresolved placeholders found.")
        lines.append("")

    lines.append("---")
    lines.append("")

    # G5: Validation Files
    lines.extend([
        "## G5: Validation File Integrity",
        "",
        f"**Status:** {report.g5_status}",
        f"**Count:** {len(report.g5_validation_issues)}",
        "",
    ])

    if report.g5_validation_issues:
        lines.append("### Issues")
        lines.append("")

        for issue in report.g5_validation_issues:
            lines.append(f"#### {issue.file}")
            lines.append(f"- **Issue:** {issue.issue}")
            lines.append(f"- **Suggestion:** {issue.suggestion}")
            lines.append("")
    else:
        lines.append("✅ No validation file issues found.")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Next Actions")
    lines.append("")

    if report.overall_status == "PASS":
        lines.append("✅ All gates passing! No action needed.")
    else:
        lines.append("Fix gates in priority order:")
        if report.g3_status == "FAIL":
            lines.append(f"1. Fix {len(report.g3_broken_links)} broken links (G3)")
        if report.g4_status == "FAIL":
            lines.append(f"2. Resolve {len(report.g4_placeholders)} placeholders (G4)")
        if report.g5_status == "FAIL":
            lines.append(f"3. Fix {len(report.g5_validation_issues)} validation files (G5)")

    return '\n'.join(lines)


def print_summary(report: AuditReport):
    """Print console summary."""

    status_emoji = "✅" if report.overall_status == "PASS" else "❌"

    print("\n" + "=" * 70)
    print(f"{status_emoji} ACTIVE DOCS AUDIT - {report.overall_status}")
    print("=" * 70)
    print()
    print(f"Files: {report.active_files} active (of {report.files_scanned} total)")
    print(f"Git SHA: {report.git_sha}")
    print()
    print("GATE RESULTS:")
    print(f"  {'✅' if report.g3_status == 'PASS' else '❌'} G3: Link Integrity - {len(report.g3_broken_links)} broken links")
    print(f"  {'✅' if report.g4_status == 'PASS' else '❌'} G4: Placeholder Check - {len(report.g4_placeholders)} unresolved")
    print(f"  {'✅' if report.g5_status == 'PASS' else '❌'} G5: Validation Naming - {len(report.g5_validation_issues)} issues")
    print()
    print("=" * 70)


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Active Docs Audit (G3, G4, G5)")
    parser.add_argument("--gate", choices=["G3", "G4", "G5"], help="Check specific gate only")
    parser.add_argument("--fix", action="store_true", help="Auto-fix what's possible")

    args = parser.parse_args()

    print("Scanning active documentation...")
    files = scan_markdown_files()
    print(f"Found {len(files)} active markdown files")

    # Run checks
    link_issues = [] if args.gate and args.gate != "G3" else check_broken_links(files)
    placeholder_issues = [] if args.gate and args.gate != "G4" else check_placeholders(files)
    validation_issues = [] if args.gate and args.gate != "G5" else check_validation_files(files)

    # Generate report
    report = generate_report(files, link_issues, placeholder_issues, validation_issues)

    # Save to refinery
    save_report(report)

    # Print summary
    print_summary(report)

    # Exit code
    exit(0 if report.overall_status == "PASS" else 1)


if __name__ == "__main__":
    main()
