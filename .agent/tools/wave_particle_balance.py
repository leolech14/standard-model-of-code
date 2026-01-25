#!/usr/bin/env python3
"""
Wave/Particle Balance Analyzer
==============================

Uses Collider's unified_analysis.json to measure the balance between:
- PARTICLE (standard-model-of-code/) - The product
- WAVE (context-management/) - The support
- OBSERVER (.agent/) - The meta

Usage:
    python wave_particle_balance.py                    # Use latest analysis
    python wave_particle_balance.py /path/to/analysis.json  # Use specific file
    python wave_particle_balance.py --run-collider     # Run Collider first
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
OUTPUT_DIR = PROJECT_ROOT / ".agent/intelligence"
REPORT_PATH = OUTPUT_DIR / "WAVE_PARTICLE_BALANCE.md"


def find_latest_analysis():
    """Find the most recent unified_analysis.json."""
    candidates = [
        PROJECT_ROOT / ".collider" / "unified_analysis.json",
        Path("/tmp/elements_self_analysis"),
    ]

    for path in candidates:
        if path.is_dir():
            # Find JSON files in directory
            jsons = list(path.glob("*llm-oriented*.json")) + list(path.glob("unified_analysis.json"))
            if jsons:
                return max(jsons, key=lambda p: p.stat().st_mtime)
        elif path.exists():
            return path

    return None


def analyze_balance(analysis_path: Path) -> dict:
    """Extract Wave/Particle balance from analysis."""
    with open(analysis_path) as f:
        data = json.load(f)

    nodes = data.get('nodes', [])
    edges = data.get('edges', [])

    # Categorize by realm
    realms = {
        'PARTICLE': [],
        'WAVE': [],
        'OBSERVER': [],
        'OTHER': []
    }

    for node in nodes:
        path = node.get('file_path', '') or node.get('id', '')
        if 'standard-model-of-code' in path:
            realms['PARTICLE'].append(node)
        elif 'context-management' in path:
            realms['WAVE'].append(node)
        elif '.agent' in path:
            realms['OBSERVER'].append(node)
        else:
            realms['OTHER'].append(node)

    # Calculate metrics
    def count_lines(nodes):
        total = 0
        for n in nodes:
            start = n.get('start_line', 0) or 0
            end = n.get('end_line', 0) or 0
            if end > start:
                total += (end - start)
        return total

    def unique_files(nodes):
        return len(set(n.get('file_path', '') for n in nodes if n.get('file_path')))

    total_nodes = len(nodes)

    results = {
        'timestamp': datetime.now().isoformat(),
        'source': str(analysis_path),
        'total_nodes': total_nodes,
        'total_edges': len(edges),
        'realms': {}
    }

    for name, realm_nodes in realms.items():
        results['realms'][name] = {
            'nodes': len(realm_nodes),
            'files': unique_files(realm_nodes),
            'lines': count_lines(realm_nodes),
            'percent': (len(realm_nodes) / total_nodes * 100) if total_nodes else 0
        }

    # Calculate ratios
    p = results['realms']['PARTICLE']['nodes']
    w = results['realms']['WAVE']['nodes']
    o = results['realms']['OBSERVER']['nodes']

    results['ratios'] = {
        'particle_wave': round(p / w, 2) if w else 0,
        'particle_observer': round(p / o, 2) if o else 0,
        'wave_observer': round(w / o, 2) if o else 0,
    }

    # Edge families
    families = {}
    for e in edges:
        fam = e.get('family', 'unknown')
        families[fam] = families.get(fam, 0) + 1
    results['edge_families'] = families

    return results


def print_report(results: dict):
    """Print balance report to stdout."""
    print("=" * 70)
    print("WAVE / PARTICLE / OBSERVER BALANCE")
    print("=" * 70)
    print(f"Source: {results['source']}")
    print(f"Generated: {results['timestamp']}")
    print()

    print(f"{'REALM':<20} {'NODES':>10} {'FILES':>10} {'LINES':>10} {'%':>8}")
    print("-" * 70)

    for name in ['PARTICLE', 'WAVE', 'OBSERVER', 'OTHER']:
        r = results['realms'][name]
        print(f"{name:<20} {r['nodes']:>10} {r['files']:>10} {r['lines']:>10} {r['percent']:>7.1f}%")

    print("-" * 70)
    print(f"{'TOTAL':<20} {results['total_nodes']:>10}")
    print()

    print("RATIOS:")
    print(f"  PARTICLE : WAVE     = {results['ratios']['particle_wave']:.2f} : 1")
    print(f"  PARTICLE : OBSERVER = {results['ratios']['particle_observer']:.2f} : 1")
    print(f"  WAVE : OBSERVER     = {results['ratios']['wave_observer']:.2f} : 1")
    print()

    # Assessment
    pw = results['ratios']['particle_wave']
    if pw > 10:
        print("ASSESSMENT: Wave infrastructure may need expansion")
    elif pw < 2:
        print("ASSESSMENT: Too much support infrastructure vs product")
    else:
        print("ASSESSMENT: Balanced")

    print()
    print("EDGE FAMILIES:")
    for fam, count in sorted(results['edge_families'].items(), key=lambda x: -x[1]):
        print(f"  {fam}: {count}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Wave/Particle Balance Analyzer")
    parser.add_argument('analysis_path', nargs='?', help="Path to unified_analysis.json")
    parser.add_argument('--run-collider', action='store_true', help="Run Collider first")
    parser.add_argument('--json', action='store_true', help="Output as JSON")
    args = parser.parse_args()

    if args.run_collider:
        print("Running Collider on PROJECT_elements...")
        subprocess.run([
            str(PROJECT_ROOT / "standard-model-of-code/collider"),
            "full",
            str(PROJECT_ROOT),
            "--output", "/tmp/elements_self_analysis"
        ], check=True)
        analysis_path = find_latest_analysis()
    elif args.analysis_path:
        analysis_path = Path(args.analysis_path)
    else:
        analysis_path = find_latest_analysis()

    if not analysis_path or not analysis_path.exists():
        print("ERROR: No analysis file found. Run with --run-collider or provide path.")
        sys.exit(1)

    results = analyze_balance(analysis_path)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print_report(results)


if __name__ == "__main__":
    main()
