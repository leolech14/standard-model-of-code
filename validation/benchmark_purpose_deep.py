#!/usr/bin/env python3
"""
Deep Purpose Layer Benchmark

Runs the full 7-stage Collider pipeline on repos with detailed purpose layer analysis.
Captures layer distribution, purpose flow, composite emergence, and violations.

Usage:
    python benchmark_purpose_deep.py [--phase 1|2] [--repo NAME]
"""

import argparse
import json
import sys
import time
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict

# Configuration
SPECTROMETER_ROOT = Path(__file__).parent.parent
REPOS_DIR = SPECTROMETER_ROOT / "validation" / "benchmarks" / "repos"
OUTPUT_DIR = SPECTROMETER_ROOT / "validation" / "purpose_analysis"

sys.path.insert(0, str(SPECTROMETER_ROOT / 'core'))

from unified_analysis import analyze
from purpose_field import detect_purpose_field, Layer

# Phase 1: First 11 repos (DDD/Architecture focused - locally available)
PHASE_1_REPOS = [
    "cosmicpython__code",
    "pgorecki__python-ddd",
    "ledmonster__ddd-python-inject",
    "koei-kaji__ddd-clean-architecture-python",
    "dry-python__returns",
    "dry-python__classes",
    "python-injector__injector",
    "pydantic__pydantic",
    "pallets__click",
    "tiangolo__typer",
    "tiangolo__sqlmodel",
]

# Phase 2: All locally available repos
def get_all_repos():
    """Get all repo directories"""
    if not REPOS_DIR.exists():
        return []
    return [d.name for d in REPOS_DIR.iterdir() if d.is_dir() and not d.name.startswith('.')]


def analyze_repo_deep(repo_path: Path, repo_name: str) -> dict:
    """
    Run deep purpose layer analysis on a repo.
    
    Returns detailed metrics on:
    - Layer distribution
    - Purpose flow matrix
    - Composite emergence
    - Violations
    """
    print(f"\n{'='*60}")
    print(f"🔬 Analyzing: {repo_name}")
    print(f"   Path: {repo_path}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        # Run unified analysis
        result = analyze(str(repo_path))
        nodes = result.nodes if hasattr(result, 'nodes') else result.get('nodes', [])
        edges = result.edges if hasattr(result, 'edges') else result.get('edges', [])
        
        analysis_time = time.time() - start_time
        
        print(f"   ✓ Nodes: {len(nodes)}, Edges: {len(edges)} ({analysis_time:.1f}s)")
        
        # Detect purpose field
        purpose_field = detect_purpose_field(nodes, edges)
        field_summary = purpose_field.summary()
        
        # Compute layer distribution
        layer_counts = defaultdict(int)
        for node in purpose_field.nodes.values():
            layer_counts[node.layer.value] += 1
        
        # Compute purpose flow matrix (layer-to-layer)
        flow_matrix = defaultdict(lambda: defaultdict(int))
        for (source, target, flow) in purpose_field.purpose_flow:
            parts = flow.split(" → ")
            if len(parts) == 2:
                flow_matrix[parts[0]][parts[1]] += 1
        
        # Compute composite emergence stats
        composite_counts = Counter()
        for node in purpose_field.nodes.values():
            if node.composite_purpose:
                composite_counts[node.composite_purpose] += 1
        
        # Role distribution
        role_counts = Counter()
        for node in purpose_field.nodes.values():
            role_counts[node.atomic_purpose] += 1
        
        unknown_count = role_counts.get('Unknown', 0)
        coverage = (len(nodes) - unknown_count) / len(nodes) * 100 if nodes else 0
        
        # Print summary
        print(f"\n   📊 Layer Distribution:")
        for layer in ['presentation', 'application', 'domain', 'infrastructure', 'unknown']:
            count = layer_counts.get(layer, 0)
            pct = count / len(nodes) * 100 if nodes else 0
            bar = "█" * int(pct / 5)
            print(f"      {layer:15} {count:5} ({pct:5.1f}%) {bar}")
        
        print(f"\n   🔄 Purpose Flow (top 5):")
        flow_list = []
        for src, targets in flow_matrix.items():
            for tgt, count in targets.items():
                flow_list.append((src, tgt, count))
        for src, tgt, count in sorted(flow_list, key=lambda x: -x[2])[:5]:
            print(f"      {src} → {tgt}: {count}")
        
        print(f"\n   🧬 Composite Emergence (top 5):")
        for comp, count in composite_counts.most_common(5):
            print(f"      {comp}: {count}")
        
        if purpose_field.violations:
            print(f"\n   ⚠️  Violations: {len(purpose_field.violations)}")
            for v in purpose_field.violations[:3]:
                print(f"      - {v[:80]}...")
        else:
            print(f"\n   ✅ No layer violations detected")
        
        return {
            "repo": repo_name,
            "path": str(repo_path),
            "status": "success",
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "coverage": round(coverage, 2),
            "analysis_time": round(analysis_time, 2),
            "layers": dict(layer_counts),
            "layer_percentages": {
                k: round(v / len(nodes) * 100, 1) if nodes else 0 
                for k, v in layer_counts.items()
            },
            "flow_matrix": {k: dict(v) for k, v in flow_matrix.items()},
            "composite_emergence": dict(composite_counts.most_common(10)),
            "role_distribution": dict(role_counts.most_common(10)),
            "violations": purpose_field.violations,
            "violation_count": len(purpose_field.violations)
        }
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:100]}")
        return {
            "repo": repo_name,
            "path": str(repo_path),
            "status": "error",
            "error": str(e),
            "total_nodes": 0,
            "coverage": 0
        }


def run_benchmark(phase: int = 1, single_repo: str = None):
    """Run the deep purpose benchmark"""
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Determine repos to analyze
    if single_repo:
        repos = [single_repo]
        phase_name = f"single_{single_repo}"
    elif phase == 1:
        repos = PHASE_1_REPOS
        phase_name = "phase1_11repos"
    else:
        repos = get_all_repos()
        phase_name = f"phase2_{len(repos)}repos"
    
    # Filter to locally available repos
    available_repos = []
    for repo in repos:
        repo_path = REPOS_DIR / repo
        if repo_path.exists():
            available_repos.append((repo, repo_path))
        else:
            print(f"⚠️  Repo not found locally: {repo}")
    
    print("=" * 70)
    print("🔬 DEEP PURPOSE LAYER BENCHMARK")
    print("=" * 70)
    print(f"Phase:      {phase_name}")
    print(f"Repos:      {len(available_repos)} available")
    print(f"Output:     {OUTPUT_DIR}")
    print(f"Started:    {datetime.now().isoformat()}")
    print()
    
    # Run analysis
    results = []
    total_nodes = 0
    total_violations = 0
    
    for i, (repo_name, repo_path) in enumerate(available_repos, 1):
        print(f"\n[{i}/{len(available_repos)}]", end="")
        result = analyze_repo_deep(repo_path, repo_name)
        results.append(result)
        
        if result["status"] == "success":
            total_nodes += result["total_nodes"]
            total_violations += result["violation_count"]
    
    # Aggregate analysis
    print("\n")
    print("=" * 70)
    print("📊 CONSOLIDATED RESULTS")
    print("=" * 70)
    
    # Success rate
    success = [r for r in results if r["status"] == "success"]
    print(f"\nSuccess Rate: {len(success)}/{len(results)}")
    print(f"Total Nodes: {total_nodes:,}")
    print(f"Total Violations: {total_violations}")
    
    # Aggregate layer distribution
    agg_layers = defaultdict(int)
    for r in success:
        for layer, count in r.get("layers", {}).items():
            agg_layers[layer] += count
    
    print(f"\nAggregate Layer Distribution:")
    for layer in ['presentation', 'application', 'domain', 'infrastructure', 'unknown']:
        count = agg_layers.get(layer, 0)
        pct = count / total_nodes * 100 if total_nodes else 0
        bar = "█" * int(pct / 2)
        print(f"  {layer:15} {count:6} ({pct:5.1f}%) {bar}")
    
    # Repos with most violations
    print(f"\nRepos by Violation Count:")
    for r in sorted(success, key=lambda x: -x["violation_count"])[:5]:
        print(f"  {r['repo']:40} {r['violation_count']:3} violations")
    
    # Repos with cleanest architecture
    print(f"\nCleanest Architecture (0 violations):")
    clean = [r for r in success if r["violation_count"] == 0]
    for r in clean:
        print(f"  ✓ {r['repo']}")
    
    # Save results
    output_file = OUTPUT_DIR / f"purpose_deep_{phase_name}_{timestamp}.json"
    with open(output_file, "w") as f:
        json.dump({
            "metadata": {
                "phase": phase_name,
                "timestamp": datetime.now().isoformat(),
                "repos_analyzed": len(results),
                "repos_success": len(success),
                "total_nodes": total_nodes,
                "total_violations": total_violations
            },
            "aggregate_layers": dict(agg_layers),
            "results": results
        }, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    
    # Generate markdown report
    report_file = OUTPUT_DIR / f"PURPOSE_DEEP_REPORT_{phase_name}_{timestamp}.md"
    with open(report_file, "w") as f:
        f.write(f"# Deep Purpose Layer Analysis\n\n")
        f.write(f"**Phase:** {phase_name}  \n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  \n")
        f.write(f"**Repos:** {len(success)}/{len(results)} successful  \n\n")
        
        f.write(f"## Aggregate Layer Distribution\n\n")
        f.write(f"| Layer | Count | % |\n")
        f.write(f"|-------|------:|---:|\n")
        for layer in ['presentation', 'application', 'domain', 'infrastructure', 'unknown']:
            count = agg_layers.get(layer, 0)
            pct = count / total_nodes * 100 if total_nodes else 0
            f.write(f"| {layer} | {count:,} | {pct:.1f}% |\n")
        
        f.write(f"\n## Per-Repo Results\n\n")
        f.write(f"| Repo | Nodes | Coverage | Violations |\n")
        f.write(f"|------|------:|---------:|-----------:|\n")
        for r in sorted(success, key=lambda x: -x["coverage"]):
            f.write(f"| {r['repo']} | {r['total_nodes']:,} | {r['coverage']:.1f}% | {r['violation_count']} |\n")
    
    print(f"📄 Report saved to: {report_file}")
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Deep Purpose Layer Benchmark")
    parser.add_argument("--phase", type=int, default=1, choices=[1, 2],
                        help="Phase 1 (11 repos) or Phase 2 (all repos)")
    parser.add_argument("--repo", type=str, default=None,
                        help="Analyze a single repo by name")
    args = parser.parse_args()
    
    run_benchmark(phase=args.phase, single_repo=args.repo)


if __name__ == "__main__":
    main()
