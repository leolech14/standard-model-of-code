#!/usr/bin/env python3
"""
Section Extractor for Standard Model Theory Documents
Extracts and merges sections based on @SECTION markers.

Usage:
    python extract_sections.py list                    # List all sections
    python extract_sections.py extract <section_name>  # Extract a specific section
    python extract_sections.py merge <section_name>    # Merge section into theory_v2.md
    python extract_sections.py validate                # Validate marker structure
"""

import re
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

@dataclass
class Section:
    name: str
    order: str
    depends_on: Optional[str]
    provides: list[str]
    start_line: int
    end_line: int
    content: str

def parse_sections(file_path: Path) -> list[Section]:
    """Parse all sections from a theory document."""
    content = file_path.read_text()
    lines = content.split('\n')
    
    sections = []
    current_section = None
    section_start = None
    section_meta = {}
    
    for i, line in enumerate(lines):
        # Start of section
        if match := re.search(r'<!-- @SECTION: (\w+) -->', line):
            if current_section:
                # Close previous section
                sections.append(Section(
                    name=current_section,
                    order=section_meta.get('order', ''),
                    depends_on=section_meta.get('depends_on'),
                    provides=section_meta.get('provides', []),
                    start_line=section_start,
                    end_line=i - 1,
                    content='\n'.join(lines[section_start:i])
                ))
            current_section = match.group(1)
            section_start = i
            section_meta = {}
        
        # Metadata
        if match := re.search(r'<!-- @ORDER: ([\d.]+) -->', line):
            section_meta['order'] = match.group(1)
        if match := re.search(r'<!-- @DEPENDS_ON: (\w+) -->', line):
            section_meta['depends_on'] = match.group(1)
        if match := re.search(r'<!-- @PROVIDES: (.+) -->', line):
            section_meta['provides'] = [p.strip() for p in match.group(1).split(',')]
        
        # End of section
        if match := re.search(r'<!-- @END_SECTION: (\w+) -->', line):
            if current_section == match.group(1):
                sections.append(Section(
                    name=current_section,
                    order=section_meta.get('order', ''),
                    depends_on=section_meta.get('depends_on'),
                    provides=section_meta.get('provides', []),
                    start_line=section_start,
                    end_line=i,
                    content='\n'.join(lines[section_start:i+1])
                ))
                current_section = None
                section_meta = {}
    
    # Handle unclosed sections at end
    if current_section:
        sections.append(Section(
            name=current_section,
            order=section_meta.get('order', ''),
            depends_on=section_meta.get('depends_on'),
            provides=section_meta.get('provides', []),
            start_line=section_start,
            end_line=len(lines) - 1,
            content='\n'.join(lines[section_start:])
        ))
    
    return sections

def list_sections(file_path: Path):
    """List all sections in the document."""
    sections = parse_sections(file_path)
    
    print(f"\n{'Order':<10} {'Section':<30} {'Lines':<15} {'Provides'}")
    print("─" * 80)
    
    for s in sorted(sections, key=lambda x: x.order or '99'):
        lines = f"{s.start_line}-{s.end_line}"
        provides = ', '.join(s.provides[:3]) + ('...' if len(s.provides) > 3 else '')
        print(f"{s.order:<10} {s.name:<30} {lines:<15} {provides}")
    
    print(f"\nTotal: {len(sections)} sections")

def extract_section(file_path: Path, section_name: str):
    """Extract a specific section."""
    sections = parse_sections(file_path)
    
    for s in sections:
        if s.name == section_name:
            print(f"\n# Section: {s.name}")
            print(f"# Order: {s.order}")
            print(f"# Depends on: {s.depends_on}")
            print(f"# Lines: {s.start_line}-{s.end_line}")
            print("=" * 60)
            print(s.content)
            return
    
    print(f"Section '{section_name}' not found.")
    print("Available sections:")
    for s in sections:
        print(f"  - {s.name}")

def validate_markers(file_path: Path):
    """Validate the marker structure."""
    sections = parse_sections(file_path)
    errors = []
    warnings = []
    
    section_names = {s.name for s in sections}
    
    for s in sections:
        # Check dependencies exist
        if s.depends_on and s.depends_on not in section_names:
            if s.depends_on != 'none':
                errors.append(f"Section '{s.name}' depends on non-existent '{s.depends_on}'")
        
        # Check order format
        if not s.order:
            warnings.append(f"Section '{s.name}' has no @ORDER")
        
        # Check provides
        if not s.provides:
            warnings.append(f"Section '{s.name}' has no @PROVIDES")
    
    print("\n=== Validation Results ===\n")
    
    if errors:
        print("ERRORS:")
        for e in errors:
            print(f"  ❌ {e}")
    
    if warnings:
        print("\nWARNINGS:")
        for w in warnings:
            print(f"  ⚠️  {w}")
    
    if not errors and not warnings:
        print("✅ All markers are valid!")
    
    print(f"\nTotal sections: {len(sections)}")
    print(f"Errors: {len(errors)}")
    print(f"Warnings: {len(warnings)}")
    
    return len(errors) == 0

def merge_section(source_path: Path, target_path: Path, section_name: str):
    """Merge a section from source into target (appends before footer)."""
    sections = parse_sections(source_path)
    
    section = None
    for s in sections:
        if s.name == section_name:
            section = s
            break
    
    if not section:
        print(f"Section '{section_name}' not found in source.")
        return False
    
    target_content = target_path.read_text()
    
    # Find the footer position (last '---' before the quote)
    footer_pattern = r'\n---\n\n> \*"The map grows'
    match = re.search(footer_pattern, target_content)
    
    if match:
        # Insert before footer
        new_content = (
            target_content[:match.start()] + 
            '\n\n---\n\n' + section.content + 
            target_content[match.start():]
        )
        target_path.write_text(new_content)
        print(f"✅ Merged section '{section_name}' into {target_path.name}")
        print(f"   Lines: {section.start_line}-{section.end_line}")
        print(f"   Provides: {', '.join(section.provides)}")
        return True
    else:
        print("Could not find footer position in target.")
        return False

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1]
    docs_dir = Path(__file__).parent.parent / 'docs'
    theory_path = docs_dir / 'theory.md'
    theory_v2_path = docs_dir / 'theory_v2.md'
    
    if cmd == 'list':
        list_sections(theory_path)
    elif cmd == 'extract' and len(sys.argv) > 2:
        extract_section(theory_path, sys.argv[2])
    elif cmd == 'validate':
        validate_markers(theory_path)
    elif cmd == 'merge' and len(sys.argv) > 2:
        merge_section(theory_path, theory_v2_path, sys.argv[2])
    else:
        print(__doc__)

if __name__ == '__main__':
    main()
