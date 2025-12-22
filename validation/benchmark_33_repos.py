#!/usr/bin/env python3
"""
33-Repo Benchmark Script
Clone, analyze, and consolidate results for 33 diverse Python repos.
"""

import subprocess
import json
import sys
import time
from pathlib import Path
from datetime import datetime
from collections import Counter

# Configuration
REPOS_DIR = Path("/tmp/benchmark_33")
SPECTROMETER_ROOT = Path("/Users/lech/PROJECTS_all/PROJECT_elements/standard-model-of-code")

# 33 repos organized by architecture type
REPOS = [
    # DDD / Clean Architecture (3)
    ("cosmicpython/code", "https://github.com/cosmicpython/code.git"),
    ("python-injector/injector", "https://github.com/python-injector/injector.git"),
    ("dry-python/returns", "https://github.com/dry-python/returns.git"),
    
    # Web Frameworks (6)
    ("django/django", "https://github.com/django/django.git"),
    ("encode/starlette", "https://github.com/encode/starlette.git"),
    ("sanic-org/sanic", "https://github.com/sanic-org/sanic.git"),
    ("encode/django-rest-framework", "https://github.com/encode/django-rest-framework.git"),
    ("graphql-python/graphene", "https://github.com/graphql-python/graphene.git"),
    ("strawberry-graphql/strawberry", "https://github.com/strawberry-graphql/strawberry.git"),
    
    # CLI Tools (5)
    ("python-poetry/poetry", "https://github.com/python-poetry/poetry.git"),
    ("pypa/pipenv", "https://github.com/pypa/pipenv.git"),
    ("psf/black", "https://github.com/psf/black.git"),
    ("tiangolo/typer", "https://github.com/tiangolo/typer.git"),
    ("tqdm/tqdm", "https://github.com/tqdm/tqdm.git"),
    
    # Data Science (5)
    ("streamlit/streamlit", "https://github.com/streamlit/streamlit.git"),
    ("optuna/optuna", "https://github.com/optuna/optuna.git"),
    ("mlflow/mlflow", "https://github.com/mlflow/mlflow.git"),
    ("dask/dask", "https://github.com/dask/dask.git"),
    ("great-expectations/great_expectations", "https://github.com/great-expectations/great_expectations.git"),
    
    # DevOps (5)
    ("apache/airflow", "https://github.com/apache/airflow.git"),
    ("prefecthq/prefect", "https://github.com/prefecthq/prefect.git"),
    ("locustio/locust", "https://github.com/locustio/locust.git"),
    ("pre-commit/pre-commit", "https://github.com/pre-commit/pre-commit.git"),
    ("fabric/fabric", "https://github.com/fabric/fabric.git"),
    
    # Libraries (7)
    ("sqlalchemy/sqlalchemy", "https://github.com/sqlalchemy/sqlalchemy.git"),
    ("marshmallow-code/marshmallow", "https://github.com/marshmallow-code/marshmallow.git"),
    ("pallets/werkzeug", "https://github.com/pallets/werkzeug.git"),
    ("pallets/jinja", "https://github.com/pallets/jinja.git"),
    ("scrapy/scrapy", "https://github.com/scrapy/scrapy.git"),
    ("joke2k/faker", "https://github.com/joke2k/faker.git"),
    ("Delgan/loguru", "https://github.com/Delgan/loguru.git"),
    
    # Enterprise (2)
    ("getsentry/sentry", "https://github.com/getsentry/sentry.git"),
    ("PostHog/posthog", "https://github.com/PostHog/posthog.git"),
]

def clone_repo(name, url, repos_dir, index, total):
    """Clone a repo if not already present."""
    safe_name = name.replace("/", "__")
    repo_path = repos_dir / safe_name
    
    print(f"\n[{index}/{total}] {name}")
    print(f"    URL: {url}")
    
    if repo_path.exists():
        # Count files
        py_files = list(repo_path.rglob("*.py"))
        print(f"    ⏭️  Already cloned ({len(py_files)} .py files)")
        return repo_path
    
    print(f"    📥 Cloning...", end=" ", flush=True)
    start = time.time()
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", url, str(repo_path)],
            capture_output=True,
            timeout=180,
            check=True
        )
        elapsed = time.time() - start
        py_files = list(repo_path.rglob("*.py"))
        print(f"✅ Done in {elapsed:.1f}s ({len(py_files)} .py files)")
        return repo_path
    except subprocess.TimeoutExpired:
        print(f"❌ Timeout after 180s")
        return None
    except Exception as e:
        print(f"❌ Failed: {str(e)[:50]}")
        return None

def analyze_repo(repo_path, spectrometer_root, name, index, total):
    """Run spectrometer analysis on a repo."""
    sys.path.insert(0, str(spectrometer_root / "core"))
    
    print(f"\n[{index}/{total}] Analyzing {name}")
    print(f"    Path: {repo_path}")
    
    start = time.time()
    try:
        from auto_pattern_discovery import AutoPatternDiscovery
        apd = AutoPatternDiscovery()
        
        print(f"    🔬 Running pattern discovery...", end=" ", flush=True)
        analysis = apd.analyze_codebase(str(repo_path))
        elapsed = time.time() - start
        
        particles = analysis.get("particles", [])
        if not particles:
            particles = analysis.get("nodes", [])
        
        total_p = len(particles)
        unknown = sum(1 for p in particles if p.get("role") == "Unknown")
        coverage = ((total_p - unknown) / total_p * 100) if total_p else 0
        
        # Count role distribution
        roles = Counter(p.get("role", "Unknown") for p in particles)
        top_roles = roles.most_common(5)
        
        status = "✅" if coverage >= 95 else "❌"
        print(f"{status} Done in {elapsed:.1f}s")
        print(f"    📊 {total_p} nodes, {coverage:.1f}% coverage ({unknown} unknown)")
        print(f"    🏷️  Top roles: {', '.join(f'{r}({c})' for r,c in top_roles)}")
        
        return {
            "particles": particles,
            "total": total_p,
            "unknown": unknown,
            "coverage": coverage,
            "roles": dict(roles),
            "elapsed": elapsed
        }
    except Exception as e:
        print(f"❌ Error: {str(e)[:100]}")
        return {"particles": [], "total": 0, "unknown": 0, "coverage": 0, "error": str(e)}

def calculate_coverage(analysis):
    """Calculate coverage from analysis results."""
    return analysis.get("total", 0), analysis.get("unknown", 0), analysis.get("coverage", 0)

def main():
    start_time = time.time()
    
    print("=" * 70)
    print("🔬 33-REPO BENCHMARK - SPECTROMETER COVERAGE TEST")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Output: {REPOS_DIR}")
    print()
    
    # Create repos directory
    REPOS_DIR.mkdir(parents=True, exist_ok=True)
    total_repos = len(REPOS)
    
    # Phase 1: Clone
    print("=" * 70)
    print("PHASE 1: CLONING REPOSITORIES")
    print("=" * 70)
    
    cloned = []
    for i, (name, url) in enumerate(REPOS, 1):
        path = clone_repo(name, url, REPOS_DIR, i, total_repos)
        if path:
            cloned.append((name, path))
    
    print()
    print(f"📦 Clone Summary: {len(cloned)}/{total_repos} repos ready")
    print()
    
    # Phase 2: Analyze
    print("=" * 70)
    print("PHASE 2: ANALYZING WITH SPECTROMETER")
    print("=" * 70)
    
    results = []
    running_nodes = 0
    running_unknown = 0
    
    for i, (name, path) in enumerate(cloned, 1):
        analysis = analyze_repo(path, SPECTROMETER_ROOT, name, i, len(cloned))
        total, unknown, coverage = calculate_coverage(analysis)
        
        running_nodes += total
        running_unknown += unknown
        running_coverage = ((running_nodes - running_unknown) / running_nodes * 100) if running_nodes else 0
        
        print(f"    📈 Running total: {running_nodes:,} nodes, {running_coverage:.1f}% avg coverage")
        
        results.append({
            "name": name,
            "path": str(path),
            "total": total,
            "unknown": unknown,
            "coverage": coverage,
            "passed": coverage >= 95,
            "roles": analysis.get("roles", {})
        })
    
    # Phase 3: Consolidate
    print()
    print("=" * 70)
    print("📊 CONSOLIDATED RESULTS")
    print("=" * 70)
    print()
    print(f"{'Repo':<45} {'Nodes':>8} {'Coverage':>10} {'Status':>8}")
    print("-" * 70)
    
    for r in sorted(results, key=lambda x: -x["coverage"]):
        status = "✅" if r["passed"] else "❌"
        print(f"{r['name']:<45} {r['total']:>8,} {r['coverage']:>9.1f}% {status:>8}")
    
    print("-" * 70)
    
    total_nodes = sum(r["total"] for r in results)
    total_unknown = sum(r["unknown"] for r in results)
    avg_coverage = ((total_nodes - total_unknown) / total_nodes * 100) if total_nodes else 0
    passed = sum(1 for r in results if r["passed"])
    
    print(f"{'TOTAL':<45} {total_nodes:>8,} {avg_coverage:>9.1f}%")
    print()
    
    elapsed = time.time() - start_time
    
    print("=" * 70)
    print("🎯 FINAL SUMMARY")
    print("=" * 70)
    print(f"  Repos tested:     {len(results)}")
    print(f"  Repos at 95%+:    {passed} ({passed/len(results)*100:.0f}%)")
    print(f"  Total nodes:      {total_nodes:,}")
    print(f"  Average coverage: {avg_coverage:.1f}%")
    print(f"  Time elapsed:     {elapsed/60:.1f} minutes")
    print()
    
    if passed == len(results):
        print("🎉 100% PASS RATE - ALL REPOS AT 95%+ COVERAGE!")
    elif passed / len(results) >= 0.9:
        print(f"✅ {passed}/{len(results)} repos passed (90%+ pass rate)")
    else:
        print(f"⚠️  {passed}/{len(results)} repos passed")
    
    # Save results
    output_path = REPOS_DIR / "benchmark_results.json"
    with open(output_path, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "elapsed_seconds": elapsed,
            "repos_tested": len(results),
            "repos_passed": passed,
            "pass_rate": passed / len(results) if results else 0,
            "total_nodes": total_nodes,
            "average_coverage": avg_coverage,
            "results": results
        }, f, indent=2)
    
    print()
    print(f"💾 Results saved to: {output_path}")

if __name__ == "__main__":
    main()

