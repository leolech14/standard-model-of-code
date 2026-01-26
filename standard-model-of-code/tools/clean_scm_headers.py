#!/usr/bin/env python3
"""
Clean up .scm query files - remove decorative banners, keep essential comments.

Before:
    ; =============================================================================
    ; PYTHON LAYER QUERY (D2_LAYER)
    ; Tree-sitter-based Clean Architecture layer detection
    ; =============================================================================
    ; Layers: Interface | Application | Core | Infrastructure | Test | Unknown

    ; =============================================================================
    ; INFRASTRUCTURE LAYER
    ; Database, file I/O, external services, repositories
    ; =============================================================================

After:
    ; D2_LAYER: Infrastructure | Application | Core | Interface | Test | Unknown

    ; -- INFRASTRUCTURE --

Usage:
    python tools/clean_scm_headers.py              # Preview changes
    python tools/clean_scm_headers.py --apply      # Apply changes
"""

import re
from pathlib import Path

QUERIES_DIR = Path(__file__).parent.parent / "src" / "core" / "queries"


def clean_scm_content(content: str) -> str:
    """Clean up decorative headers while preserving semantic info."""
    lines = content.split('\n')
    result = []
    skip_next_empty = False
    i = 0

    while i < len(lines):
        line = lines[i]

        # Skip decorative banner lines (only equals signs)
        if re.match(r'^;\s*=+\s*$', line):
            i += 1
            skip_next_empty = True
            continue

        # Skip empty comment lines after banners
        if skip_next_empty and line.strip() == ';':
            i += 1
            continue

        skip_next_empty = False

        # Convert section headers to compact form
        # "; INFRASTRUCTURE LAYER" -> "; -- INFRASTRUCTURE --"
        section_match = re.match(r'^;\s*([A-Z][A-Z\s/]+?)\s*(LAYER|PATTERNS?|PHASE)?\s*$', line)
        if section_match:
            section_name = section_match.group(1).strip()
            result.append(f'; -- {section_name} --')
            i += 1
            # Skip description line if it follows
            if i < len(lines) and lines[i].startswith('; ') and not lines[i].startswith('; --'):
                desc = lines[i][2:].strip()
                if desc and not re.match(r'^=+$', desc):
                    result.append(f';    {desc}')
                i += 1
            result.append('')
            continue

        # Convert main file header to single line
        # "; PYTHON LAYER QUERY (D2_LAYER)" -> keep as title comment
        title_match = re.match(r'^;\s*([A-Z]+)\s+(LAYER|BOUNDARY|STATE|LIFECYCLE|ROLES?)\s+QUERY\s*\(([^)]+)\)', line)
        if title_match:
            lang = title_match.group(1)
            query_type = title_match.group(2)
            dim = title_match.group(3)
            result.append(f'; {lang} {query_type} ({dim})')
            i += 1
            # Skip tree-sitter description line
            if i < len(lines) and 'Tree-sitter' in lines[i]:
                i += 1
            # Keep the values/options line
            if i < len(lines) and lines[i].startswith('; ') and ':' in lines[i]:
                result.append(lines[i])
                i += 1
            result.append('')
            continue

        # Keep all other lines
        result.append(line)
        i += 1

    # Clean up multiple consecutive empty lines
    cleaned = []
    prev_empty = False
    for line in result:
        is_empty = line.strip() == '' or line.strip() == ';'
        if is_empty and prev_empty:
            continue
        cleaned.append(line)
        prev_empty = is_empty

    return '\n'.join(cleaned)


def process_file(path: Path, apply: bool = False) -> tuple[int, int]:
    """Process a single .scm file. Returns (original_lines, new_lines)."""
    content = path.read_text()
    original_lines = len(content.split('\n'))

    cleaned = clean_scm_content(content)
    new_lines = len(cleaned.split('\n'))

    if apply:
        path.write_text(cleaned)

    return original_lines, new_lines


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Clean .scm query file headers")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default: preview)")
    args = parser.parse_args()

    scm_files = list(QUERIES_DIR.glob("**/*.scm"))

    if not scm_files:
        print(f"No .scm files found in {QUERIES_DIR}")
        return

    print(f"{'Applying' if args.apply else 'Previewing'} changes to {len(scm_files)} files:\n")

    total_before = 0
    total_after = 0

    for path in sorted(scm_files):
        rel_path = path.relative_to(QUERIES_DIR.parent.parent.parent)
        before, after = process_file(path, apply=args.apply)
        total_before += before
        total_after += after

        reduction = before - after
        pct = (reduction / before * 100) if before > 0 else 0

        status = "✓" if args.apply else " "
        print(f"  {status} {rel_path}: {before} -> {after} (-{reduction}, {pct:.0f}%)")

    print(f"\nTotal: {total_before} -> {total_after} lines (-{total_before - total_after})")

    if not args.apply:
        print("\nRun with --apply to make changes")


if __name__ == "__main__":
    main()
