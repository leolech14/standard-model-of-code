#!/usr/bin/env python3
"""
Mine Semgrep Rules → T2 Atoms

Extracts structural code patterns from Semgrep rules and converts them
to T2 ecosystem atoms for Collider.

Usage:
    python tools/mine_semgrep.py --input /tmp/semgrep-rules --output src/patterns/t2_mined/

What it does:
    1. Parses all YAML rules from Semgrep repository
    2. Extracts structural patterns (the code structures rules detect)
    3. Groups by ecosystem (django, flask, react, etc.)
    4. Deduplicates similar patterns
    5. Outputs T2 atom YAML files per ecosystem
"""

import yaml
import json
import re
import argparse
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field, asdict
import hashlib


@dataclass
class T2Atom:
    """A T2 ecosystem-specific atom."""
    id: str
    name: str
    ecosystem: str
    category: str
    description: str
    patterns: List[str]
    source_rules: List[str]
    tier: str = "T2"

    def to_dict(self) -> dict:
        return asdict(self)


class SemgrepMiner:
    """Mines Semgrep rules to extract T2 atoms."""

    # Ecosystem abbreviations for ID generation
    ECO_ABBREV = {
        "django": "DJANGO",
        "flask": "FLASK",
        "fastapi": "FASTAPI",
        "express": "EXPRESS",
        "react": "REACT",
        "vue": "VUE",
        "angular": "ANGULAR",
        "rails": "RAILS",
        "spring": "SPRING",
        "laravel": "LARAVEL",
        "python": "PY",
        "javascript": "JS",
        "typescript": "TS",
        "java": "JAVA",
        "go": "GO",
        "ruby": "RUBY",
        "php": "PHP",
        "rust": "RUST",
        "kotlin": "KOTLIN",
        "swift": "SWIFT",
        "terraform": "TF",
        "aws": "AWS",
        "aws-lambda": "LAMBDA",
        "gcp": "GCP",
        "azure": "AZURE",
        "docker": "DOCKER",
        "kubernetes": "K8S",
        "solidity": "SOL",
        ".net": "DOTNET",
        "csharp": "CSHARP",
    }

    # Category mappings
    CATEGORY_MAP = {
        "security": "SEC",
        "best-practice": "BEST",
        "correctness": "CORR",
        "performance": "PERF",
        "maintainability": "MAINT",
        "compatibility": "COMPAT",
    }

    def __init__(self, input_dir: Path, output_dir: Path):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Collected data
        self.raw_patterns: Dict[str, List[dict]] = defaultdict(list)
        self.atoms_by_ecosystem: Dict[str, List[T2Atom]] = defaultdict(list)
        self.stats = {
            "files_processed": 0,
            "rules_processed": 0,
            "patterns_extracted": 0,
            "atoms_created": 0,
            "ecosystems": set(),
        }

    def mine(self) -> Dict[str, List[T2Atom]]:
        """Main mining pipeline."""
        print("=" * 60)
        print("SEMGREP → T2 ATOMS MINING")
        print("=" * 60)
        print(f"Input:  {self.input_dir}")
        print(f"Output: {self.output_dir}")
        print()

        # Step 1: Parse all YAML files
        print("[1/4] Parsing YAML rules...")
        self._parse_yaml_files()
        print(f"       Processed {self.stats['files_processed']} files")
        print(f"       Found {self.stats['rules_processed']} rules")
        print(f"       Extracted {self.stats['patterns_extracted']} patterns")
        print(f"       Ecosystems: {len(self.stats['ecosystems'])}")
        print()

        # Step 2: Extract structural patterns
        print("[2/4] Extracting structural patterns...")
        self._extract_structures()
        print(f"       Grouped into {sum(len(v) for v in self.raw_patterns.values())} pattern groups")
        print()

        # Step 3: Deduplicate and create atoms
        print("[3/4] Deduplicating and creating atoms...")
        self._create_atoms()
        print(f"       Created {self.stats['atoms_created']} unique atoms")
        print()

        # Step 4: Output YAML files
        print("[4/4] Writing output files...")
        self._write_output()
        print()

        # Summary
        self._print_summary()

        return self.atoms_by_ecosystem

    def _parse_yaml_files(self):
        """Parse all YAML files in the Semgrep rules directory."""
        yaml_files = list(self.input_dir.glob("**/*.yaml"))

        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)

                if not data or 'rules' not in data:
                    continue

                self.stats['files_processed'] += 1

                for rule in data.get('rules', []):
                    self._process_rule(rule, yaml_file)

            except Exception as e:
                # Skip malformed files
                pass

    def _process_rule(self, rule: dict, source_file: Path):
        """Process a single Semgrep rule."""
        self.stats['rules_processed'] += 1

        rule_id = rule.get('id', '')
        metadata = rule.get('metadata', {})
        technologies = metadata.get('technology', [])
        category = metadata.get('category', 'unknown')
        message = rule.get('message', '')

        # Extract patterns from the rule
        patterns = self._extract_patterns_from_rule(rule)

        if not patterns or not technologies:
            return

        self.stats['patterns_extracted'] += len(patterns)

        for tech in technologies:
            tech_lower = tech.lower()
            self.stats['ecosystems'].add(tech_lower)

            for pattern in patterns:
                self.raw_patterns[tech_lower].append({
                    'pattern': pattern,
                    'rule_id': rule_id,
                    'category': category,
                    'message': message,
                    'source_file': str(source_file.relative_to(self.input_dir)),
                })

    def _extract_patterns_from_rule(self, rule: dict) -> List[str]:
        """Extract pattern strings from a rule definition."""
        patterns = []

        def _recurse(obj):
            if isinstance(obj, dict):
                for key, val in obj.items():
                    if key == 'pattern' and isinstance(val, str):
                        # Clean and normalize the pattern
                        cleaned = self._clean_pattern(val)
                        if cleaned:
                            patterns.append(cleaned)
                    elif key in ('pattern-either', 'patterns', 'pattern-inside'):
                        _recurse(val)
                    else:
                        _recurse(val)
            elif isinstance(obj, list):
                for item in obj:
                    _recurse(item)

        _recurse(rule)
        return patterns

    def _clean_pattern(self, pattern: str) -> Optional[str]:
        """Clean and normalize a pattern string."""
        # Get first line only
        pattern = pattern.strip().split('\n')[0]

        # Skip empty or comment-only patterns
        if not pattern or pattern.startswith('#'):
            return None

        # Skip patterns that are just metavariables
        if pattern.strip() in ('$...', '$X', '$_', '...'):
            return None

        # Limit length
        if len(pattern) > 200:
            pattern = pattern[:200]

        return pattern

    def _extract_structures(self):
        """Extract meaningful structural patterns from raw patterns."""
        # Patterns that indicate actual API/structure usage
        structure_patterns = [
            # Module/package patterns
            r'([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)+)',
            # Decorator patterns
            r'(@[a-zA-Z_][a-zA-Z0-9_.]*)',
            # Method call patterns
            r'\.([a-zA-Z_][a-zA-Z0-9_]*)\(',
            # Class inheritance
            r'class\s+\$?\w+\(([^)]+)\)',
        ]

        for ecosystem, patterns in self.raw_patterns.items():
            structures = defaultdict(list)

            for p in patterns:
                pattern_text = p['pattern']

                # Extract structural elements
                for regex in structure_patterns:
                    matches = re.findall(regex, pattern_text)
                    for match in matches:
                        if len(match) > 2 and not match.startswith('$'):
                            # Use the structure as a key
                            struct_key = match.lower()
                            structures[struct_key].append(p)

            # Replace raw patterns with structured groups
            self.raw_patterns[ecosystem] = dict(structures)

    def _create_atoms(self):
        """Create T2 atoms from deduplicated patterns."""
        atom_counters = defaultdict(int)

        for ecosystem, structures in self.raw_patterns.items():
            if not isinstance(structures, dict):
                continue

            eco_abbrev = self.ECO_ABBREV.get(ecosystem, ecosystem.upper()[:6])

            for structure, pattern_list in structures.items():
                if not pattern_list:
                    continue

                # Get most common category
                categories = [p.get('category', 'unknown') for p in pattern_list]
                category = max(set(categories), key=categories.count)
                cat_abbrev = self.CATEGORY_MAP.get(category, 'GEN')

                # Generate unique ID
                atom_counters[ecosystem] += 1
                counter = atom_counters[ecosystem]
                atom_id = f"EXT.{eco_abbrev}.{cat_abbrev}.{counter:03d}"

                # Generate name from structure
                name = self._structure_to_name(structure)

                # Collect unique patterns and source rules
                unique_patterns = list(set(p['pattern'] for p in pattern_list))[:5]
                source_rules = list(set(p['rule_id'] for p in pattern_list))[:10]

                # Generate description from messages
                messages = [p.get('message', '') for p in pattern_list if p.get('message')]
                description = messages[0][:200] if messages else f"Pattern: {structure}"

                atom = T2Atom(
                    id=atom_id,
                    name=name,
                    ecosystem=ecosystem,
                    category=category,
                    description=description,
                    patterns=unique_patterns,
                    source_rules=source_rules,
                )

                self.atoms_by_ecosystem[ecosystem].append(atom)
                self.stats['atoms_created'] += 1

    def _structure_to_name(self, structure: str) -> str:
        """Convert a structure pattern to a human-readable name."""
        # Remove common prefixes
        name = structure
        for prefix in ['django.', 'flask.', 'react.', 'express.', 'rails.']:
            if name.startswith(prefix):
                name = name[len(prefix):]

        # Convert to title case
        parts = re.split(r'[._]', name)
        name = ' '.join(p.title() for p in parts if p)

        return name or structure

    def _write_output(self):
        """Write T2 atoms to YAML files organized by ecosystem."""
        # Group ecosystems by category
        ecosystem_groups = {
            'python': ['python', 'django', 'flask', 'fastapi'],
            'javascript': ['javascript', 'typescript', 'express', 'node.js'],
            'frontend': ['react', 'vue', 'angular', 'svelte'],
            'java': ['java', 'spring', 'kotlin'],
            'cloud': ['aws', 'aws-lambda', 'gcp', 'azure', 'terraform'],
            'other': [],  # Catch-all
        }

        # Assign ecosystems to groups
        grouped = defaultdict(list)
        assigned = set()

        for group_name, ecosystems in ecosystem_groups.items():
            for eco in ecosystems:
                if eco in self.atoms_by_ecosystem:
                    grouped[group_name].extend(self.atoms_by_ecosystem[eco])
                    assigned.add(eco)

        # Add unassigned to 'other'
        for eco, atoms in self.atoms_by_ecosystem.items():
            if eco not in assigned:
                grouped['other'].extend(atoms)

        # Write files
        for group_name, atoms in grouped.items():
            if not atoms:
                continue

            output_file = self.output_dir / f"ATOMS_T2_{group_name.upper()}.yaml"

            # Convert to YAML-friendly format
            data = {
                'version': '1.0.0',
                'generated_by': 'mine_semgrep.py',
                'source': 'semgrep-rules',
                'atom_count': len(atoms),
                'atoms': [atom.to_dict() for atom in atoms]
            }

            with open(output_file, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

            print(f"       {output_file.name}: {len(atoms)} atoms")

    def _print_summary(self):
        """Print mining summary."""
        print("=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Files processed:    {self.stats['files_processed']}")
        print(f"Rules processed:    {self.stats['rules_processed']}")
        print(f"Patterns extracted: {self.stats['patterns_extracted']}")
        print(f"Atoms created:      {self.stats['atoms_created']}")
        print(f"Ecosystems:         {len(self.stats['ecosystems'])}")
        print()
        print("Top ecosystems by atom count:")
        sorted_eco = sorted(
            self.atoms_by_ecosystem.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:15]
        for eco, atoms in sorted_eco:
            print(f"  {eco:<20} {len(atoms):>5} atoms")
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description='Mine Semgrep rules to extract T2 atoms'
    )
    parser.add_argument(
        '--input', '-i',
        type=Path,
        default=Path('/tmp/semgrep-rules'),
        help='Path to cloned semgrep-rules repository'
    )
    parser.add_argument(
        '--output', '-o',
        type=Path,
        default=Path('src/patterns/t2_mined'),
        help='Output directory for T2 atom YAML files'
    )

    args = parser.parse_args()

    if not args.input.exists():
        print(f"ERROR: Input directory does not exist: {args.input}")
        print("Run: git clone --depth 1 https://github.com/semgrep/semgrep-rules /tmp/semgrep-rules")
        return 1

    miner = SemgrepMiner(args.input, args.output)
    miner.mine()

    return 0


if __name__ == '__main__':
    exit(main())
