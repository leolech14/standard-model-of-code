#!/usr/bin/env python3
"""
Theory Cataloger - Complete Inventory of All Theories
======================================================

Scans entire PROJECT_elements repository to catalog:
- Axioms (primitives, not derivable)
- Theorems (derived, provable)
- Laws (empirical, observed)
- Frameworks (application patterns)
- Definitions (enumeration of concepts)
- Metrics (measurement systems)

Output: Complete theory inventory with cross-references, lineage, validation status

Usage:
    python theory_cataloger.py --scan
    python theory_cataloger.py --stats
    python theory_cataloger.py --export theory_inventory.json
"""

import re
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Any, Set

# Paths
REPO_ROOT = Path(__file__).parent.parent.parent
OUTPUT_DIR = REPO_ROOT / ".agent" / "intelligence"

# Scan patterns
THEORY_PATTERNS = {
    "axiom": [
        r"^###?\s+Axiom\s+([A-Z]?\d+):?\s+(.+)$",
        r"^###?\s+A(\d+)\.?\s+(.+)$",
        r"^\*\*Axiom\s+([A-Z]?\d+)\*\*:?\s+(.+)$",
    ],
    "theorem": [
        r"^###?\s+Theorem\s+(\d+):?\s+(.+)$",
        r"^###?\s+T(\d+)\.?\s+(.+)$",
        r"^\*\*Theorem\s+(\d+)\*\*:?\s+(.+)$",
    ],
    "law": [
        r"^###?\s+Law\s+(\d+):?\s+(.+)$",
        r"^###?\s+L(\d+)\.?\s+(.+)$",
        r"^\*\*Law\*\*:?\s+(.+)$",
        r"^###?\s+(.+)\s+Law$",  # "Constructal Law"
    ],
    "principle": [
        r"^###?\s+Principle\s+(\d+)?:?\s+(.+)$",
        r"^\*\*Principle\*\*:?\s+(.+)$",
        r"^###?\s+(.+)\s+Principle$",  # "Slaving Principle"
    ],
    "definition": [
        r"^\*\*Definition\*\*:?\s+(.+)$",
        r"^###?\s+Definition:?\s+(.+)$",
    ],
    "framework": [
        r"^###?\s+(.+)\s+Framework$",
        r"^###?\s+Framework:?\s+(.+)$",
    ],
    "metric": [
        r"^###?\s+Metric:?\s+(.+)$",
        r"^\*\*Metric\*\*:?\s+(.+)$",
    ]
}

# Theory file patterns
THEORY_FILE_PATTERNS = [
    "**/THEORY*.md",
    "**/AXIOM*.md",
    "**/LAW*.md",
    "**/PRINCIPLE*.md",
    "**/*_THEORY.md",
    "**/MODEL.md",
    "**/ONTOLOG*.md",
]

# Exclude patterns
EXCLUDE_DIRS = {".git", ".venv", ".tools_venv", "node_modules", "__pycache__", "archive"}


class TheoryEntry:
    """A cataloged theory entry."""

    def __init__(self, entry_type: str, identifier: str, title: str,
                 file_path: str, line_number: int, section: str = None):
        self.type = entry_type  # axiom, theorem, law, etc.
        self.identifier = identifier  # A1, T3, etc.
        self.title = title
        self.file_path = file_path
        self.line_number = line_number
        self.section = section
        self.content = []  # Lines of content
        self.references = []  # Cross-references to other theories
        self.validation_status = None  # VALIDATED, PROPOSED, DEPRECATED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "id": self.identifier,
            "title": self.title,
            "file": str(self.file_path),
            "line": self.line_number,
            "section": self.section,
            "content_lines": len(self.content),
            "references": self.references,
            "validation": self.validation_status
        }


class TheoryCatalog:
    """Complete theory inventory."""

    def __init__(self):
        self.entries: List[TheoryEntry] = []
        self.files_scanned = 0
        self.by_type: Dict[str, List[TheoryEntry]] = defaultdict(list)
        self.by_file: Dict[str, List[TheoryEntry]] = defaultdict(list)

    def scan_repository(self):
        """Scan entire repository for theory files."""
        print("Scanning repository for theories...")

        # Find all theory files
        theory_files = set()
        for pattern in THEORY_FILE_PATTERNS:
            for path in REPO_ROOT.rglob(pattern):
                # Skip excluded directories
                if any(excl in str(path) for excl in EXCLUDE_DIRS):
                    continue
                if path.is_file():
                    theory_files.add(path)

        print(f"Found {len(theory_files)} theory files")

        # Scan each file
        for filepath in sorted(theory_files):
            self._scan_file(filepath)

        print(f"Scanned {self.files_scanned} files")
        print(f"Found {len(self.entries)} theory entries")

    def _scan_file(self, filepath: Path):
        """Scan single file for theory entries."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()

            self.files_scanned += 1
            current_section = None

            for line_num, line in enumerate(lines, 1):
                # Track section headers
                if line.startswith('#'):
                    current_section = line.strip('#').strip()

                # Check each pattern type
                for entry_type, patterns in THEORY_PATTERNS.items():
                    for pattern in patterns:
                        match = re.match(pattern, line.strip())
                        if match:
                            # Extract identifier and title
                            groups = match.groups()
                            if len(groups) == 2:
                                identifier, title = groups
                            elif len(groups) == 1:
                                identifier = ""
                                title = groups[0]
                            else:
                                continue

                            # Create entry
                            entry = TheoryEntry(
                                entry_type=entry_type,
                                identifier=identifier.strip() if identifier else "",
                                title=title.strip(),
                                file_path=str(filepath.relative_to(REPO_ROOT)),
                                line_number=line_num,
                                section=current_section
                            )

                            self.entries.append(entry)
                            self.by_type[entry_type].append(entry)
                            self.by_file[entry.file_path].append(entry)
                            break  # Found match, don't check other patterns

        except Exception as e:
            print(f"Error scanning {filepath}: {e}")

    def generate_statistics(self) -> Dict[str, Any]:
        """Generate statistics about cataloged theories."""
        stats = {
            "timestamp": datetime.now().isoformat(),
            "total_entries": len(self.entries),
            "files_scanned": self.files_scanned,
            "by_type": {k: len(v) for k, v in self.by_type.items()},
            "top_files": []
        }

        # Top files by theory count
        sorted_files = sorted(self.by_file.items(), key=lambda x: len(x[1]), reverse=True)
        for filepath, entries in sorted_files[:20]:
            stats["top_files"].append({
                "file": filepath,
                "count": len(entries),
                "types": {t: sum(1 for e in entries if e.type == t)
                         for t in set(e.type for e in entries)}
            })

        return stats

    def export_inventory(self, output_path: Path):
        """Export complete inventory to JSON."""
        inventory = {
            "meta": {
                "generated": datetime.now().isoformat(),
                "total_entries": len(self.entries),
                "files_scanned": self.files_scanned
            },
            "statistics": self.generate_statistics(),
            "entries": [e.to_dict() for e in self.entries],
            "by_type": {k: [e.to_dict() for e in v] for k, v in self.by_type.items()},
            "by_file": {k: [e.to_dict() for e in v] for k, v in self.by_file.items()}
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(inventory, f, indent=2)

        print(f"Exported inventory to: {output_path}")

    def print_report(self):
        """Print summary report."""
        stats = self.generate_statistics()

        print("\n" + "=" * 70)
        print("THEORY CATALOG - COMPLETE INVENTORY")
        print("=" * 70)
        print()

        print(f"Files Scanned: {stats['files_scanned']}")
        print(f"Total Entries: {stats['total_entries']}")
        print()

        print("By Type:")
        for entry_type, count in sorted(stats['by_type'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {entry_type:15} {count:>5}")
        print()

        print("Top 10 Files by Theory Count:")
        for i, file_info in enumerate(stats['top_files'][:10], 1):
            print(f"  {i:2}. {file_info['file']}")
            print(f"      Total: {file_info['count']}")
            type_summary = ", ".join(f"{count} {t}" for t, count in file_info['types'].items())
            print(f"      Types: {type_summary}")
            print()

        print("=" * 70)


def main():
    """CLI interface."""
    import argparse

    parser = argparse.ArgumentParser(description="Theory Cataloger - Complete Inventory")
    parser.add_argument("--scan", action="store_true", help="Scan repository")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--export", type=str, help="Export to JSON file")

    args = parser.parse_args()

    catalog = TheoryCatalog()

    if args.scan or args.export or not args.stats:
        catalog.scan_repository()

    if args.export:
        output_path = Path(args.export)
        catalog.export_inventory(output_path)

    if args.stats or not args.export:
        catalog.print_report()


if __name__ == "__main__":
    main()
