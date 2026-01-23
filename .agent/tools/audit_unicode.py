#!/usr/bin/env python3
"""
Unicode Health Audit Tool
Scans codebase for emoji and special characters, reports potential issues.
"""

import os
import re
import sys
from pathlib import Path
from collections import defaultdict

# Character classifications
SAFE_SINGLE_WIDTH = {
    '✓': ('U+2713', 'CHECK MARK', 'success'),
    '✔': ('U+2714', 'HEAVY CHECK MARK', 'success'),
    '✗': ('U+2717', 'BALLOT X', 'failure'),
    '✘': ('U+2718', 'HEAVY BALLOT X', 'failure'),
    '●': ('U+25CF', 'BLACK CIRCLE', 'status'),
    '○': ('U+25CB', 'WHITE CIRCLE', 'status'),
    '■': ('U+25A0', 'BLACK SQUARE', 'status'),
    '□': ('U+25A1', 'WHITE SQUARE', 'status'),
    '▶': ('U+25B6', 'RIGHT TRIANGLE', 'action'),
    '◀': ('U+25C0', 'LEFT TRIANGLE', 'action'),
    '▲': ('U+25B2', 'UP TRIANGLE', 'action'),
    '▼': ('U+25BC', 'DOWN TRIANGLE', 'action'),
    '→': ('U+2192', 'RIGHTWARDS ARROW', 'flow'),
    '←': ('U+2190', 'LEFTWARDS ARROW', 'flow'),
    '↑': ('U+2191', 'UPWARDS ARROW', 'flow'),
    '↓': ('U+2193', 'DOWNWARDS ARROW', 'flow'),
    '─': ('U+2500', 'BOX HORIZONTAL', 'box'),
    '│': ('U+2502', 'BOX VERTICAL', 'box'),
    '┌': ('U+250C', 'BOX DOWN RIGHT', 'box'),
    '┐': ('U+2510', 'BOX DOWN LEFT', 'box'),
    '└': ('U+2514', 'BOX UP RIGHT', 'box'),
    '┘': ('U+2518', 'BOX UP LEFT', 'box'),
    '├': ('U+251C', 'BOX VERTICAL RIGHT', 'box'),
    '┤': ('U+2524', 'BOX VERTICAL LEFT', 'box'),
    '┬': ('U+252C', 'BOX DOWN HORIZONTAL', 'box'),
    '┴': ('U+2534', 'BOX UP HORIZONTAL', 'box'),
    '┼': ('U+253C', 'BOX CROSS', 'box'),
    '█': ('U+2588', 'FULL BLOCK', 'progress'),
    '░': ('U+2591', 'LIGHT SHADE', 'progress'),
    '▒': ('U+2592', 'MEDIUM SHADE', 'progress'),
    '▓': ('U+2593', 'DARK SHADE', 'progress'),
    '•': ('U+2022', 'BULLET', 'list'),
    '◆': ('U+25C6', 'BLACK DIAMOND', 'marker'),
    '★': ('U+2605', 'BLACK STAR', 'rating'),
    '☆': ('U+2606', 'WHITE STAR', 'rating'),
}

PROBLEMATIC_EMOJI = {
    '✅': ('U+2705', 'WHITE HEAVY CHECK MARK', 'width varies 1-2'),
    '❌': ('U+274C', 'CROSS MARK', 'width 2'),
    '☑️': ('U+2611+FE0F', 'BALLOT BOX WITH CHECK', 'compound, width varies'),
    '🟢': ('U+1F7E2', 'GREEN CIRCLE', 'emoji width 2'),
    '🟡': ('U+1F7E1', 'YELLOW CIRCLE', 'emoji width 2'),
    '🔴': ('U+1F534', 'RED CIRCLE', 'emoji width 2'),
    '🚧': ('U+1F6A7', 'CONSTRUCTION', 'emoji width 2'),
    '💤': ('U+1F4A4', 'SLEEPING', 'emoji width 2'),
    '⛔': ('U+26D4', 'NO ENTRY', 'width varies'),
    '⚠️': ('U+26A0+FE0F', 'WARNING SIGN', 'dual presentation, width 1.5-2'),
    '🛠️': ('U+1F6E0+FE0F', 'HAMMER AND WRENCH', 'ZWJ, width varies'),
    '⚙️': ('U+2699+FE0F', 'GEAR', 'compound, width varies'),
    '🔄': ('U+1F504', 'ANTICLOCKWISE ARROWS', 'emoji width 2'),
}

# Variation selectors that cause issues
VARIATION_SELECTORS = {
    '\uFE0E': 'VS15 (text)',
    '\uFE0F': 'VS16 (emoji)',
}


def scan_file(filepath):
    """Scan a file for special Unicode characters."""
    findings = {
        'safe': defaultdict(list),
        'problematic': defaultdict(list),
        'unknown': defaultdict(list),
    }

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                for char in line:
                    if ord(char) > 127:  # Non-ASCII
                        # Skip common safe chars
                        if char in '©®™°±²³¹º¼½¾':
                            continue
                        if char in '—–''""…':  # Typography
                            continue
                        if char in 'áàâäãåéèêëíìîïóòôöõúùûüýÿñçÁÀÂÄÃÅÉÈÊËÍÌÎÏÓÒÔÖÕÚÙÛÜÝŸÑÇ':
                            continue  # Accented chars

                        if char in SAFE_SINGLE_WIDTH:
                            findings['safe'][char].append((line_num, filepath))
                        elif char in PROBLEMATIC_EMOJI:
                            findings['problematic'][char].append((line_num, filepath))
                        elif char in VARIATION_SELECTORS:
                            findings['problematic'][char].append((line_num, filepath))
                        elif ord(char) > 0x1F000:  # Emoji range
                            findings['unknown'][char].append((line_num, filepath))
                        elif 0x2500 <= ord(char) <= 0x257F:  # Box drawing
                            findings['safe'][char].append((line_num, filepath))
                        elif 0x2580 <= ord(char) <= 0x259F:  # Block elements
                            findings['safe'][char].append((line_num, filepath))
                        elif 0x25A0 <= ord(char) <= 0x25FF:  # Geometric shapes
                            findings['safe'][char].append((line_num, filepath))
                        elif 0x2190 <= ord(char) <= 0x21FF:  # Arrows
                            findings['safe'][char].append((line_num, filepath))
                        elif 0x2700 <= ord(char) <= 0x27BF:  # Dingbats
                            findings['safe'][char].append((line_num, filepath))
    except (UnicodeDecodeError, PermissionError, IsADirectoryError):
        pass

    return findings


def print_report(all_findings):
    """Print the audit report."""
    print("=" * 70)
    print("UNICODE HEALTH AUDIT REPORT")
    print("=" * 70)

    # Aggregate counts
    safe_chars = defaultdict(int)
    problem_chars = defaultdict(int)
    unknown_chars = defaultdict(int)

    for findings in all_findings:
        for char, locations in findings['safe'].items():
            safe_chars[char] += len(locations)
        for char, locations in findings['problematic'].items():
            problem_chars[char] += len(locations)
        for char, locations in findings['unknown'].items():
            unknown_chars[char] += len(locations)

    # Safe characters
    print("\n✓ SAFE CHARACTERS (single-width, consistent):")
    print("-" * 70)
    if safe_chars:
        print(f"{'Char':<4} {'Codepoint':<12} {'Count':<8} {'Category':<12} {'Name'}")
        print("-" * 70)
        for char, count in sorted(safe_chars.items(), key=lambda x: -x[1]):
            info = SAFE_SINGLE_WIDTH.get(char, (f'U+{ord(char):04X}', 'UNKNOWN', 'other'))
            print(f"{char:<4} {info[0]:<12} {count:<8} {info[2]:<12} {info[1]}")
    else:
        print("  (none found)")

    # Problematic characters
    print("\n⚠ PROBLEMATIC CHARACTERS (width issues, avoid in tables):")
    print("-" * 70)
    if problem_chars:
        print(f"{'Char':<4} {'Codepoint':<16} {'Count':<8} {'Issue'}")
        print("-" * 70)
        for char, count in sorted(problem_chars.items(), key=lambda x: -x[1]):
            if char in PROBLEMATIC_EMOJI:
                info = PROBLEMATIC_EMOJI[char]
                print(f"{char:<4} {info[0]:<16} {count:<8} {info[2]}")
            elif char in VARIATION_SELECTORS:
                print(f"(VS) {VARIATION_SELECTORS[char]:<16} {count:<8} causes width issues")
    else:
        print("  (none found)")

    # Unknown emoji
    print("\n? UNKNOWN EMOJI (needs review):")
    print("-" * 70)
    if unknown_chars:
        print(f"{'Char':<4} {'Codepoint':<12} {'Count':<8}")
        print("-" * 70)
        for char, count in sorted(unknown_chars.items(), key=lambda x: -x[1]):
            print(f"{char:<4} U+{ord(char):04X}      {count:<8}")
    else:
        print("  (none found)")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    total_safe = sum(safe_chars.values())
    total_problem = sum(problem_chars.values())
    total_unknown = sum(unknown_chars.values())

    print(f"  Safe characters:        {total_safe:>6} occurrences ({len(safe_chars)} unique)")
    print(f"  Problematic characters: {total_problem:>6} occurrences ({len(problem_chars)} unique)")
    print(f"  Unknown emoji:          {total_unknown:>6} occurrences ({len(unknown_chars)} unique)")

    health = "HEALTHY" if total_problem == 0 else "NEEDS REVIEW" if total_problem < 50 else "ISSUES FOUND"
    print(f"\n  Health Status: {health}")

    if total_problem > 0:
        print("\n  Recommendation: Replace problematic emoji with safe alternatives")
        print("  in ASCII tables. OK to use in Quick View / non-aligned contexts.")


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')

    # Directories to skip
    skip_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'venv',
                 '.tools_venv', 'archive', '.collider'}

    # Extensions to scan
    scan_extensions = {'.md', '.py', '.js', '.yaml', '.yml', '.json', '.txt', '.html', '.css'}

    all_findings = []
    file_count = 0

    print(f"Scanning {root}...")

    for path in root.rglob('*'):
        if any(skip in path.parts for skip in skip_dirs):
            continue
        if path.is_file() and path.suffix in scan_extensions:
            findings = scan_file(path)
            if any(findings[k] for k in findings):
                all_findings.append(findings)
            file_count += 1

    print(f"Scanned {file_count} files.\n")
    print_report(all_findings)


if __name__ == '__main__':
    main()
