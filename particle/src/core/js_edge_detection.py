"""
Heuristic edge detectors for implicit dependency relationships.

Discovers edges that aren't explicitly declared in code:
- JS import edges (import { X } from './y')
- Class instantiation edges (x = MyClass())

Extracted from full_analysis.py during audit refactoring (2026-02-24).
"""
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List


def detect_js_imports(nodes: List[Dict], edges: List[Dict]) -> int:
    """
    Find edges from JS files to imported modules/functions.
    Pattern: import { Foo } from './bar' -> invokes edge
    """
    new_edges = 0

    # 1. Index potential targets by name
    targets_by_name = defaultdict(list)
    for n in nodes:
        if n.get('name'):
            targets_by_name[n.get('name')].append(n.get('id'))

    # 2. Identify unique JS files
    js_files = set()
    file_to_node_id = {}

    for n in nodes:
        fpath = n.get('file_path', '')
        if fpath.lower().endswith(('.js', '.jsx', '.ts', '.tsx')):
            js_files.add(fpath)
            if fpath not in file_to_node_id or n.get('kind') == 'module':
                file_to_node_id[fpath] = n.get('id')

    # 3. Scan files
    for fpath in js_files:
        if not fpath or fpath not in file_to_node_id:
            continue

        try:
            full_path = Path(fpath).resolve()
            if not full_path.exists():
                full_path = Path.cwd() / fpath

            if not full_path.exists():
                continue

            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            named_imports = re.findall(r'import\s*{([^}]+)}\s*from', content)
            source_id = file_to_node_id[fpath]

            for group in named_imports:
                names = [n.strip().split(' as ')[0] for n in group.split(',')]
                for name in names:
                    name = name.strip()
                    if name in targets_by_name:
                        for target_id in targets_by_name[name]:
                            if target_id == source_id:
                                continue
                            edges.append({
                                'source': source_id,
                                'target': target_id,
                                'edge_type': 'imports',
                                'family': 'Dependency',
                                'inferred': True,
                                'confidence': 0.8,
                                'description': f"JS import {name}"
                            })
                            new_edges += 1
        except Exception:
            continue

    return new_edges


def detect_class_instantiation(nodes: List[Dict], edges: List[Dict]) -> int:
    """
    Find edges from code instantiating a class to the class definition.
    Pattern: x = MyClass() -> invokes edge
    """
    new_edges = 0

    classes_by_name = defaultdict(list)
    for n in nodes:
        if n.get('kind') == 'class' or n.get('type') == 'class':
            name = n.get('name', '')
            if len(name) >= 4:
                classes_by_name[name].append(n.get('id'))

    if not classes_by_name:
        return new_edges

    # Single compiled regex: \b(Class1|Class2|...)\s*(
    # Sorted longest-first so longer names match before shorter prefixes
    sorted_names = sorted(classes_by_name.keys(), key=len, reverse=True)
    combined_pattern = re.compile(
        r'\b(' + '|'.join(re.escape(name) for name in sorted_names) + r')\s*\('
    )

    for src_node in nodes:
        body = src_node.get('body_source', '')
        if not body:
            continue

        src_id = src_node.get('id')
        for match in combined_pattern.finditer(body):
            class_name = match.group(1)
            for target_id in classes_by_name[class_name]:
                if target_id == src_id:
                    continue
                edges.append({
                    'source': src_id,
                    'target': target_id,
                    'edge_type': 'instantiates',
                    'family': 'Dependency',
                    'inferred': True,
                    'confidence': 0.6,
                    'description': f"Class instantiation {class_name}() detected"
                })
                new_edges += 1

    return new_edges
