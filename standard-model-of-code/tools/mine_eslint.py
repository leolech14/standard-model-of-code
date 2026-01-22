#!/usr/bin/env python3
"""
Mine ESLint Plugins → T2 Atoms

Extracts frontend patterns from ESLint plugins (React, Vue, Angular)
and converts them to T2 ecosystem atoms for Collider.

Usage:
    python tools/mine_eslint.py --input-react /tmp/eslint-react \
                                --input-vue /tmp/eslint-vue \
                                --input-angular /tmp/angular-eslint \
                                --output src/patterns/t2_mined/

What it does:
    1. Parses JS/TS rule files from ESLint plugins
    2. Extracts rule metadata (description, category)
    3. Converts to T2 atom format
    4. Merges with existing frontend atoms
    5. Outputs updated ATOMS_T2_FRONTEND.yaml
"""

import re
import yaml
import argparse
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


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


class ESLintMiner:
    """Mines ESLint plugins to extract T2 atoms."""

    # Ecosystem abbreviations
    ECO_ABBREV = {
        "react": "REACT",
        "vue": "VUE",
        "angular": "ANGULAR",
    }

    # Category mappings
    CATEGORY_MAP = {
        "best practices": "BEST",
        "best-practices": "BEST",
        "stylistic issues": "STYLE",
        "possible errors": "ERR",
        "variables": "VAR",
        "ecmascript 6": "ES6",
        "suggestion": "SUGG",
        "problem": "PROB",
        "layout": "LAYOUT",
        "security": "SEC",
        "accessibility": "A11Y",
        "performance": "PERF",
    }

    def __init__(self, react_dir: Optional[Path], vue_dir: Optional[Path],
                 angular_dir: Optional[Path], output_dir: Path):
        self.react_dir = react_dir
        self.vue_dir = vue_dir
        self.angular_dir = angular_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.atoms: List[T2Atom] = []
        self.stats = {
            "react_rules": 0,
            "vue_rules": 0,
            "angular_rules": 0,
            "atoms_created": 0,
        }

    def mine(self) -> List[T2Atom]:
        """Main mining pipeline."""
        print("=" * 60)
        print("ESLINT PLUGINS → T2 ATOMS MINING")
        print("=" * 60)
        print()

        # Mine each plugin
        if self.react_dir and self.react_dir.exists():
            print("[1/3] Mining React rules...")
            self._mine_react()
            print(f"      Found {self.stats['react_rules']} rules")
        else:
            print("[1/3] Skipping React (not found)")

        if self.vue_dir and self.vue_dir.exists():
            print("[2/3] Mining Vue rules...")
            self._mine_vue()
            print(f"      Found {self.stats['vue_rules']} rules")
        else:
            print("[2/3] Skipping Vue (not found)")

        if self.angular_dir and self.angular_dir.exists():
            print("[3/3] Mining Angular rules...")
            self._mine_angular()
            print(f"      Found {self.stats['angular_rules']} rules")
        else:
            print("[3/3] Skipping Angular (not found)")

        print()
        print(f"Total atoms created: {len(self.atoms)}")
        print()

        # Write output
        self._write_output()

        return self.atoms

    def _mine_react(self):
        """Mine React ESLint plugin rules."""
        rules_dir = self.react_dir / "lib" / "rules"
        if not rules_dir.exists():
            return

        counter = 0
        for js_file in sorted(rules_dir.glob("*.js")):
            if js_file.name == "index.js":
                continue

            rule_data = self._parse_js_rule(js_file)
            if rule_data:
                counter += 1
                atom = self._create_atom("react", rule_data, counter)
                self.atoms.append(atom)
                self.stats["react_rules"] += 1

    def _mine_vue(self):
        """Mine Vue ESLint plugin rules."""
        rules_dir = self.vue_dir / "lib" / "rules"
        if not rules_dir.exists():
            return

        counter = 0
        for js_file in sorted(rules_dir.glob("*.js")):
            # Skip wrapper files (very small files that just re-export)
            if js_file.stat().st_size < 500:
                continue

            rule_data = self._parse_js_rule(js_file)
            if rule_data:
                counter += 1
                atom = self._create_atom("vue", rule_data, counter)
                self.atoms.append(atom)
                self.stats["vue_rules"] += 1

    def _mine_angular(self):
        """Mine Angular ESLint plugin rules."""
        # Angular has rules in multiple packages
        for package_dir in self.angular_dir.glob("packages/eslint-plugin-*/src/rules"):
            counter = 0
            for ts_file in sorted(package_dir.glob("*.ts")):
                # Skip index files and spec files
                if ts_file.name in ("index.ts",) or ts_file.name.endswith(".spec.ts"):
                    continue

                rule_data = self._parse_ts_rule(ts_file)
                if rule_data:
                    counter += 1
                    atom = self._create_atom("angular", rule_data, counter)
                    self.atoms.append(atom)
                    self.stats["angular_rules"] += 1

    def _parse_js_rule(self, file_path: Path) -> Optional[dict]:
        """Parse a JavaScript ESLint rule file."""
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception:
            return None

        rule_name = file_path.stem  # e.g., "hook-use-state"

        # Extract description from meta.docs.description
        desc_match = re.search(
            r"description:\s*['\"](.+?)['\"]",
            content,
            re.DOTALL
        )
        description = desc_match.group(1).strip() if desc_match else f"Rule: {rule_name}"

        # Extract category from meta.docs.category
        cat_match = re.search(
            r"category:\s*['\"](.+?)['\"]",
            content
        )
        category = cat_match.group(1).lower() if cat_match else "general"

        # Extract from @fileoverview if no description found
        if not desc_match:
            fileoverview = re.search(r"@fileoverview\s+(.+?)(?:\n|\*)", content)
            if fileoverview:
                description = fileoverview.group(1).strip()

        return {
            "name": rule_name,
            "description": description,
            "category": category,
            "source": f"eslint:{file_path.name}",
        }

    def _parse_ts_rule(self, file_path: Path) -> Optional[dict]:
        """Parse a TypeScript ESLint rule file (Angular)."""
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception:
            return None

        rule_name = file_path.stem  # e.g., "no-inline-styles"

        # Extract RULE_NAME if present
        name_match = re.search(r"RULE_NAME\s*=\s*['\"](.+?)['\"]", content)
        if name_match:
            rule_name = name_match.group(1)

        # Extract description from meta.docs.description
        desc_match = re.search(
            r"description:\s*['\"](.+?)['\"]",
            content,
            re.DOTALL
        )
        description = desc_match.group(1).strip() if desc_match else f"Rule: {rule_name}"

        # Infer category from rule name patterns
        category = "general"
        if "accessibility" in rule_name.lower() or "a11y" in rule_name.lower():
            category = "accessibility"
        elif "no-" in rule_name:
            category = "problem"
        elif "prefer-" in rule_name:
            category = "suggestion"

        return {
            "name": rule_name,
            "description": description,
            "category": category,
            "source": f"angular-eslint:{file_path.name}",
        }

    def _create_atom(self, ecosystem: str, rule_data: dict, counter: int) -> T2Atom:
        """Create a T2 atom from rule data."""
        eco_abbrev = self.ECO_ABBREV.get(ecosystem, ecosystem.upper())
        cat_abbrev = self.CATEGORY_MAP.get(rule_data["category"].lower(), "GEN")

        atom_id = f"EXT.{eco_abbrev}.{cat_abbrev}.{counter:03d}"

        # Convert rule name to human-readable
        name = self._rule_name_to_display(rule_data["name"])

        # Generate pattern hints from rule name
        patterns = self._generate_patterns(ecosystem, rule_data["name"])

        return T2Atom(
            id=atom_id,
            name=name,
            ecosystem=ecosystem,
            category=rule_data["category"],
            description=rule_data["description"][:200],
            patterns=patterns,
            source_rules=[rule_data["source"]],
        )

    def _rule_name_to_display(self, rule_name: str) -> str:
        """Convert kebab-case rule name to display name."""
        # "hook-use-state" -> "Hook Use State"
        parts = rule_name.replace("-", " ").replace("_", " ").split()
        return " ".join(p.capitalize() for p in parts)

    def _generate_patterns(self, ecosystem: str, rule_name: str) -> List[str]:
        """Generate pattern hints based on ecosystem and rule name."""
        patterns = []

        if ecosystem == "react":
            if "hook" in rule_name:
                patterns.append("useState")
                patterns.append("useEffect")
            if "jsx" in rule_name:
                patterns.append("<Component")
                patterns.append("className=")
            if "prop" in rule_name:
                patterns.append("props.")
                patterns.append("PropTypes")

        elif ecosystem == "vue":
            if "component" in rule_name:
                patterns.append("Vue.component")
                patterns.append("defineComponent")
            if "directive" in rule_name:
                patterns.append("v-if")
                patterns.append("v-for")
            if "composition" in rule_name:
                patterns.append("setup()")
                patterns.append("ref(")

        elif ecosystem == "angular":
            if "component" in rule_name.lower():
                patterns.append("@Component")
            if "directive" in rule_name.lower():
                patterns.append("@Directive")
            if "template" in rule_name.lower():
                patterns.append("*ngIf")
                patterns.append("*ngFor")

        # Add rule name as pattern hint
        patterns.append(rule_name)

        return patterns[:5]  # Limit to 5 patterns

    def _write_output(self):
        """Write atoms to YAML file, merging with existing."""
        output_file = self.output_dir / "ATOMS_T2_FRONTEND.yaml"

        # Load existing atoms if file exists
        existing_atoms = []
        if output_file.exists():
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    existing_atoms = data.get('atoms', [])
            except Exception:
                pass

        # Create ID set for deduplication
        existing_ids = {a.get('id') for a in existing_atoms}

        # Add new atoms that don't exist
        new_atoms = [a.to_dict() for a in self.atoms if a.id not in existing_ids]

        # Merge
        all_atoms = existing_atoms + new_atoms

        # Write output
        data = {
            'version': '1.0.0',
            'generated_by': 'mine_eslint.py',
            'source': 'eslint-plugins',
            'atom_count': len(all_atoms),
            'atoms': all_atoms
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

        print(f"Written {len(new_atoms)} new atoms to {output_file.name}")
        print(f"Total atoms in file: {len(all_atoms)}")

        # Also print by ecosystem
        by_eco = defaultdict(int)
        for a in all_atoms:
            by_eco[a.get('ecosystem', 'unknown')] += 1
        print("\nBy ecosystem:")
        for eco, count in sorted(by_eco.items()):
            print(f"  {eco}: {count}")


def main():
    parser = argparse.ArgumentParser(
        description='Mine ESLint plugins to extract T2 atoms'
    )
    parser.add_argument(
        '--input-react',
        type=Path,
        default=Path('/tmp/eslint-react'),
        help='Path to eslint-plugin-react clone'
    )
    parser.add_argument(
        '--input-vue',
        type=Path,
        default=Path('/tmp/eslint-vue'),
        help='Path to eslint-plugin-vue clone'
    )
    parser.add_argument(
        '--input-angular',
        type=Path,
        default=Path('/tmp/angular-eslint'),
        help='Path to angular-eslint clone'
    )
    parser.add_argument(
        '--output', '-o',
        type=Path,
        default=Path('src/patterns/t2_mined'),
        help='Output directory for T2 atom YAML files'
    )

    args = parser.parse_args()

    miner = ESLintMiner(
        react_dir=args.input_react,
        vue_dir=args.input_vue,
        angular_dir=args.input_angular,
        output_dir=args.output
    )
    miner.mine()

    return 0


if __name__ == '__main__':
    exit(main())
