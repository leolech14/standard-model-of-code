#!/usr/bin/env python3
"""
33-Repo Benchmark Script - FAST VERSION
Uses already-cloned repos where available, skips massive repos.
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime
from collections import Counter
import subprocess

# Configuration
EXISTING_REPOS = Path("/Users/lech/PROJECTS_all/PROJECT_elements/standard-model-of-code/validation/benchmarks/repos")
NEW_REPOS_DIR = Path("/tmp/benchmark_33")
SPECTROMETER_ROOT = Path("/Users/lech/PROJECTS_all/PROJECT_elements/standard-model-of-code")

# Add core to path
sys.path.insert(0, str(SPECTROMETER_ROOT / "core"))

def get_repo_mapping():
    """Build mapping using existing clones where possible."""
    existing = {p.name: p for p in EXISTING_REPOS.iterdir() if p.is_dir()}
    
    # All 33 repos - (display_name, clone_name, optional_url)
    repos = [
        # Already cloned (14 confirmed)
        ("cosmicpython/code", "cosmicpython__code", None),
        ("dry-python/returns", "dry-python__returns", None),
        ("python-injector/injector", "python-injector__injector", None),
        ("python-poetry/poetry", "python-poetry__poetry", None),
        ("pypa/pipenv", "pypa__pipenv", None),
        ("psf/black", "psf__black", None),
        ("tiangolo/typer", "tiangolo__typer", None),
        ("tqdm/tqdm", "tqdm__tqdm", None),
        ("Textualize/rich", "Textualize__rich", None),
        ("Textualize/textual", "Textualize__textual", None),
        ("astral-sh/ruff", "astral-sh__ruff", None),
        ("httpie/cli", "httpie__cli", None),
        ("pallets/click", "pallets__click", None),
        ("pydantic/pydantic", "pydantic__pydantic", None),
        
        # Need to clone (15 more)
        ("encode/starlette", "encode__starlette", "https://github.com/encode/starlette.git"),
        ("sanic-org/sanic", "sanic-org__sanic", "https://github.com/sanic-org/sanic.git"),
        ("encode/django-rest-framework", "encode__django-rest-framework", "https://github.com/encode/django-rest-framework.git"),
        ("graphql-python/graphene", "graphql-python__graphene", "https://github.com/graphql-python/graphene.git"),
        ("strawberry-graphql/strawberry", "strawberry-graphql__strawberry", "https://github.com/strawberry-graphql/strawberry.git"),
        ("optuna/optuna", "optuna__optuna", "https://github.com/optuna/optuna.git"),
        ("locustio/locust", "locustio__locust", "https://github.com/locustio/locust.git"),
        ("pre-commit/pre-commit", "pre-commit__pre-commit", "https://github.com/pre-commit/pre-commit.git"),
        ("fabric/fabric", "fabric__fabric", "https://github.com/fabric/fabric.git"),
        ("marshmallow-code/marshmallow", "marshmallow-code__marshmallow", "https://github.com/marshmallow-code/marshmallow.git"),
        ("pallets/werkzeug", "pallets__werkzeug", "https://github.com/pallets/werkzeug.git"),
        ("pallets/jinja", "pallets__jinja", "https://github.com/pallets/jinja.git"),
        ("scrapy/scrapy", "scrapy__scrapy", "https://github.com/scrapy/scrapy.git"),
        ("joke2k/faker", "joke2k__faker", "https://github.com/joke2k/faker.git"),
        ("Delgan/loguru", "Delgan__loguru", "https://github.com/Delgan/loguru.git"),
        
        # 4 additional to reach 33 (3 large in order + 1 JS repo)
        ("sqlalchemy/sqlalchemy", "sqlalchemy__sqlalchemy", "https://github.com/sqlalchemy/sqlalchemy.git"),
        ("streamlit/streamlit", "streamlit__streamlit", "https://github.com/streamlit/streamlit.git"),
        ("django/django", "django__django", "https://github.com/django/django.git"),
        ("expressjs/express", "expressjs__express", "https://github.com/expressjs/express.git"),  # JS polyglot test
    ]
    
    # Skip truly massive repos (keep sqlalchemy, streamlit, django)
    SKIP = ["getsentry/sentry", "PostHog/posthog", 
            "apache/airflow", "prefecthq/prefect",
            "mlflow/mlflow", "dask/dask", "great-expectations/great_expectations"]
    
    mapping = []
    for item in repos:
        name, clone_name, url = item
        
        if name in SKIP:
            continue
            
        # Check existing repos first
        if clone_name in existing:
            mapping.append((name, existing[clone_name], None))
        elif url:
            # Will clone to /tmp
            mapping.append((name, NEW_REPOS_DIR / clone_name, url))
    
    return mapping


def clone_if_needed(name, path, url):
    """Clone repo if needed."""
    if path.exists():
        return path
    if not url:
        print(f"  ⚠️  {name} - not found, skipping")
        return None
    
    print(f"  📥 Cloning {name}...", end=" ", flush=True)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["git", "clone", "--depth", "1", url, str(path)],
            capture_output=True, timeout=120, check=True
        )
        print("✅")
        return path
    except Exception as e:
        print(f"❌ {e}")
        return None


def analyze_repo(name, path):
    """Analyze a single repo using unified_analysis.analyze()."""
    from unified_analysis import analyze
    
    print(f"  🔬 {name}...", end=" ", flush=True)
    start = time.time()
    
    try:
        result = analyze(str(path))
        
        # result.nodes could be list of UnifiedNode or list of dict
        nodes = result.nodes
        total = len(nodes)
        
        def get_role(n):
            if hasattr(n, 'role'):
                return n.role
            elif isinstance(n, dict):
                return n.get("role", "Unknown")
            return "Unknown"
        
        unknown = sum(1 for n in nodes if get_role(n) == "Unknown")
        coverage = ((total - unknown) / total * 100) if total else 0
        roles = Counter(get_role(n) for n in nodes)
        
        elapsed = time.time() - start
        status = "✅" if coverage >= 95 else "⚠️ " if coverage >= 80 else "❌"
        print(f"{status} {total:,} nodes, {coverage:.1f}% in {elapsed:.1f}s")
        
        return {
            "name": name,
            "total": total,
            "unknown": unknown,
            "coverage": coverage,
            "passed": coverage >= 95,
            "roles": dict(roles),
            "elapsed": elapsed
        }
    except Exception as e:
        elapsed = time.time() - start
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {"name": name, "total": 0, "unknown": 0, "coverage": 0, "passed": False, "error": str(e), "elapsed": elapsed}


def main():
    start = time.time()
    print("=" * 60)
    print("🚀 FAST BENCHMARK - 29 Repos")
    print("=" * 60)
    
    repos = get_repo_mapping()
    print(f"\n📦 {len(repos)} repos to analyze\n")
    
    # Phase 1: Ensure repos exist
    print("Phase 1: Checking/cloning repos")
    ready = []
    for name, path, url in repos:
        actual_path = clone_if_needed(name, path, url)
        if actual_path:
            ready.append((name, actual_path))
        else:
            print(f"  ⏭️  {name} skipped")
    
    print(f"\n✅ {len(ready)} repos ready\n")
    
    # Phase 2: Analyze
    print("Phase 2: Analyzing with Spectrometer")
    print("-" * 60)
    results = []
    for name, path in ready:
        r = analyze_repo(name, path)
        results.append(r)
    
    # Report
    print("\n" + "=" * 60)
    print("📊 RESULTS (sorted by coverage)")
    print("=" * 60)
    print(f"\n{'Repo':<40} {'Nodes':>8} {'Coverage':>10}")
    print("-" * 60)
    
    for r in sorted(results, key=lambda x: -x["coverage"]):
        status = "✅" if r["passed"] else "❌"
        print(f"{r['name']:<40} {r['total']:>8,} {r['coverage']:>9.1f}% {status}")
    
    print("-" * 60)
    total_nodes = sum(r["total"] for r in results)
    total_unknown = sum(r["unknown"] for r in results)
    avg_cov = ((total_nodes - total_unknown) / total_nodes * 100) if total_nodes else 0
    passed = sum(1 for r in results if r["passed"])
    
    print(f"{'TOTAL':<40} {total_nodes:>8,} {avg_cov:>9.1f}%")
    print(f"\n🎯 {passed}/{len(results)} repos at 95%+ coverage ({passed*100//len(results)}% pass rate)")
    print(f"⏱️  Completed in {time.time()-start:.1f}s ({(time.time()-start)/60:.1f} min)")
    
    # Save
    out = NEW_REPOS_DIR / "benchmark_results.json"
    out.parent.mkdir(exist_ok=True)
    with open(out, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "repos_tested": len(results),
            "pass_rate": passed / len(results) if results else 0,
            "total_nodes": total_nodes,
            "average_coverage": avg_cov,
            "results": results
        }, f, indent=2)
    print(f"\n💾 Saved: {out}")


if __name__ == "__main__":
    main()
