#!/usr/bin/env python3
"""
Documentation Node Extractor

Fragments documentation into minimal meaningful nodes with:
- ID: Unique identifier
- path: Source file
- loc: Line number range
- nature: Type of content (DEF, CLM, NUM, TBL, etc.)
- excerpt: The actual content
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass, asdict

FILE_CODES = {
    "ARCHITECTURE.md": "ARC",
    "ATOMS_REFERENCE.md": "ATM",
    "CANONICAL_SCHEMA.md": "CAN",
    "COMMANDS.md": "CMD",
    "CONSOLIDATED_UNDERSTANDING.md": "CON",
    "DISCOVERY_PROCESS.md": "DIS",
    "ERRORS.md": "ERR",
    "FORMAL_PROOF.md": "FRM",
    "GLOSSARY.md": "GLO",
    "MECHANIZED_PROOFS.md": "MEC",
    "ORIENTATION_FILES.md": "ORI",
    "PURPOSE_FIELD.md": "PUR",
    "QUICKSTART.md": "QST",
    "README.md": "RDM",
    "THE_PIVOT.md": "PIV",
    "THEORY_MAP.md": "THM",
}

@dataclass
class DocNode:
    id: str
    path: str
    loc_start: int
    loc_end: int
    nature: str
    heading: str
    excerpt: str

def classify_nature(content: str) -> str:
    """Classify the nature of content."""
    content_lower = content.lower()

    # Check for tables
    if '|' in content and content.count('|') > 4:
        return "TBL"

    # Check for code blocks
    if '```' in content:
        return "COD"

    # Check for definitions
    if any(x in content_lower for x in ['definition', 'defines', 'is defined as', '**definition']):
        return "DEF"

    # Check for numeric claims
    if re.search(r'\b\d+\s*(atoms?|roles?|levels?|stages?|dimensions?)\b', content_lower):
        return "NUM"

    # Check for claims/theorems
    if any(x in content_lower for x in ['theorem', 'claim', 'proof', 'lemma', 'axiom']):
        return "CLM"

    # Check for lists
    if re.search(r'^[-*]\s', content, re.MULTILINE):
        return "LST"

    # Check for references
    if re.search(r'\[.*\]\(.*\)', content):
        return "REF"

    # Check for instructions
    if any(x in content_lower for x in ['run', 'execute', 'install', 'usage:', 'example:']):
        return "INS"

    return "TXT"  # Default to text

def extract_nodes_from_file(filepath: Path) -> List[DocNode]:
    """Extract all meaningful nodes from a markdown file."""
    nodes = []
    filename = filepath.name
    file_code = FILE_CODES.get(filename, filename[:3].upper())

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    current_heading = ""
    current_section = ""
    section_counter = {}

    i = 0
    while i < len(lines):
        line = lines[i]

        # Track headings
        if line.startswith('#'):
            heading_match = re.match(r'^(#+)\s*(.+)', line)
            if heading_match:
                level = len(heading_match.group(1))
                heading_text = heading_match.group(2).strip()
                current_heading = heading_text
                # Create section code from heading
                section_words = re.sub(r'[^a-zA-Z0-9\s]', '', heading_text).split()[:2]
                current_section = ''.join(w[:3].upper() for w in section_words) or "HDR"

                if current_section not in section_counter:
                    section_counter[current_section] = 0
                section_counter[current_section] += 1

        # Detect tables
        if '|' in line and i + 1 < len(lines) and '|' in lines[i + 1]:
            table_start = i
            while i < len(lines) and '|' in lines[i]:
                i += 1
            table_end = i - 1

            excerpt = ''.join(lines[table_start:table_end + 1])
            node_id = f"D{file_code}.{current_section}.{section_counter.get(current_section, 1)}"

            nodes.append(DocNode(
                id=node_id,
                path=str(filepath.relative_to(filepath.parent.parent)),
                loc_start=table_start + 1,
                loc_end=table_end + 1,
                nature="TBL",
                heading=current_heading,
                excerpt=excerpt[:500] + ("..." if len(excerpt) > 500 else "")
            ))
            section_counter[current_section] = section_counter.get(current_section, 0) + 1
            continue

        # Detect code blocks
        if line.strip().startswith('```'):
            block_start = i
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                i += 1
            block_end = i

            excerpt = ''.join(lines[block_start:block_end + 1])
            node_id = f"D{file_code}.{current_section}.{section_counter.get(current_section, 1)}"

            nodes.append(DocNode(
                id=node_id,
                path=str(filepath.relative_to(filepath.parent.parent)),
                loc_start=block_start + 1,
                loc_end=block_end + 1,
                nature="COD",
                heading=current_heading,
                excerpt=excerpt[:500] + ("..." if len(excerpt) > 500 else "")
            ))
            section_counter[current_section] = section_counter.get(current_section, 0) + 1
            i += 1
            continue

        # Detect definition patterns (### Definition X.Y)
        if re.match(r'^###?\s*(Definition|Theorem|Lemma|Claim|Axiom)', line):
            def_start = i
            i += 1
            # Read until next heading or empty lines
            while i < len(lines) and not lines[i].startswith('#') and lines[i].strip():
                i += 1
            def_end = i - 1

            excerpt = ''.join(lines[def_start:def_end + 1])
            nature = classify_nature(excerpt)
            node_id = f"D{file_code}.{current_section}.{section_counter.get(current_section, 1)}"

            nodes.append(DocNode(
                id=node_id,
                path=str(filepath.relative_to(filepath.parent.parent)),
                loc_start=def_start + 1,
                loc_end=def_end + 1,
                nature=nature,
                heading=current_heading,
                excerpt=excerpt[:500] + ("..." if len(excerpt) > 500 else "")
            ))
            section_counter[current_section] = section_counter.get(current_section, 0) + 1
            continue

        # Detect numeric claims (lines with specific numbers)
        if re.search(r'\b(167|200|33|27|16|12|10)\b.*\b(atoms?|roles?|levels?|stages?|families)\b', line, re.IGNORECASE):
            node_id = f"D{file_code}.{current_section}.{section_counter.get(current_section, 1)}"

            nodes.append(DocNode(
                id=node_id,
                path=str(filepath.relative_to(filepath.parent.parent)),
                loc_start=i + 1,
                loc_end=i + 1,
                nature="NUM",
                heading=current_heading,
                excerpt=line.strip()
            ))
            section_counter[current_section] = section_counter.get(current_section, 0) + 1

        i += 1

    return nodes

def main():
    docs_dir = Path(__file__).parent.parent / "docs"
    registry_dir = docs_dir / "registry"
    registry_dir.mkdir(exist_ok=True)

    all_nodes = []

    # Process main docs (not subdirectories first)
    for md_file in sorted(docs_dir.glob("*.md")):
        print(f"Processing {md_file.name}...")
        nodes = extract_nodes_from_file(md_file)
        all_nodes.extend(nodes)
        print(f"  → Extracted {len(nodes)} nodes")

    # Save to JSON
    output = {
        "version": "1.0.0",
        "generated": "2026-01-19",
        "total_nodes": len(all_nodes),
        "nodes": [asdict(n) for n in all_nodes]
    }

    with open(registry_dir / "nodes.json", 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"\n✓ Extracted {len(all_nodes)} total nodes")
    print(f"✓ Saved to docs/registry/nodes.json")

    # Print summary by nature
    nature_counts = {}
    for n in all_nodes:
        nature_counts[n.nature] = nature_counts.get(n.nature, 0) + 1

    print("\nBy nature:")
    for nature, count in sorted(nature_counts.items(), key=lambda x: -x[1]):
        print(f"  {nature}: {count}")

if __name__ == "__main__":
    main()
