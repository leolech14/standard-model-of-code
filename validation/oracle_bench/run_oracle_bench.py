#!/usr/bin/env python3
"""
Oracle Benchmark Runner for Spectrometer Validation.

This script:
1. Loads the benchmark manifest
2. Clones/updates repos (if needed)
3. Extracts ground truth from oracles
4. Runs Spectrometer analysis
5. Compares predictions vs oracle ground truth
6. Generates precision/recall/coverage reports

Usage:
    python run_oracle_bench.py                    # Run all benchmarks
    python run_oracle_bench.py --repo cosmicpython_code  # Run single repo
    python run_oracle_bench.py --extract-only     # Only extract oracle truth
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Set

import yaml

from oracles import CanonicalPathsOracle, OracleResult
try:
    from oracles.import_linter import ImportLinterOracle
except ImportError:
    ImportLinterOracle = None  # Graceful fallback

from baselines import NaiveLayerBaseline

# Root paths
BENCH_ROOT = Path(__file__).parent
REPOS_DIR = BENCH_ROOT / "repos"
REPORTS_DIR = BENCH_ROOT / "reports"
MANIFEST_PATH = BENCH_ROOT / "manifest.yaml"
MAPPINGS_DIR = BENCH_ROOT / "mappings"

# Spectrometer paths (relative to project root)
PROJECT_ROOT = BENCH_ROOT.parent.parent
SPECTROMETER_CLI = PROJECT_ROOT / "cli.py"


@dataclass
class ComparisonMetrics:
    """Metrics comparing Spectrometer predictions vs oracle ground truth."""
    
    # Component membership accuracy
    total_symbols: int = 0
    matched_symbols: int = 0  # Symbols with both oracle and predicted labels
    correct_component: int = 0
    component_accuracy: float = 0.0
    
    # Per-component precision/recall
    per_component: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    # Per-component precision/recall
    per_component: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    # Score 2: Boundary/Constraint Violations
    total_dependency_edges: int = 0
    violating_edges: int = 0
    violation_rate: float = 0.0
    documented_violations: List[Dict[str, Any]] = field(default_factory=list)
    
    # Coverage
    symbols_with_oracle_label: int = 0
    symbols_without_oracle_label: int = 0
    coverage_rate: float = 0.0
    
    # Confusion matrix
    confusion: Dict[str, Dict[str, int]] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "component_accuracy": {
                "total_symbols": self.total_symbols,
                "matched_symbols": self.matched_symbols,
                "correct_component": self.correct_component,
                "accuracy": round(self.component_accuracy, 4),
                "per_component": self.per_component,
            },
            "component_accuracy": {
                "total_symbols": self.total_symbols,
                "matched_symbols": self.matched_symbols,
                "correct_component": self.correct_component,
                "accuracy": round(self.component_accuracy, 4),
                "per_component": self.per_component,
            },
            "boundary_conformance": {
                "total_edges": self.total_dependency_edges,
                "violating_edges": self.violating_edges,
                "violation_rate": round(self.violation_rate, 4),
                "top_violations": self.documented_violations[:10],  # Top 10 for summary
            },
            "coverage": {
                "symbols_with_oracle_label": self.symbols_with_oracle_label,
                "symbols_without_oracle_label": self.symbols_without_oracle_label,
                "coverage_rate": round(self.coverage_rate, 4),
            },
            "confusion_matrix": self.confusion,
        }


def load_manifest() -> Dict[str, Any]:
    """Load the benchmark manifest."""
    with open(MANIFEST_PATH) as f:
        return yaml.safe_load(f)


def load_mapping(mapping_file: str) -> Dict[str, Any]:
    """Load a translation mapping file."""
    mapping_path = BENCH_ROOT / mapping_file
    if not mapping_path.exists():
        print(f"  Warning: Mapping file not found: {mapping_file}")
        return {}
    with open(mapping_path) as f:
        return yaml.safe_load(f)


def clone_or_update_repo(repo_config: Dict[str, Any]) -> Path:
    """Clone the repo if needed, or verify it exists."""
    repo_id = repo_config["id"]
    repo_url = repo_config["url"]
    commit = repo_config.get("commit", "master")
    
    repo_path = REPOS_DIR / repo_id
    
    if not repo_path.exists():
        print(f"  Cloning {repo_url}...")
        REPOS_DIR.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["git", "clone", "--depth", "50", repo_url, str(repo_path)],
            check=True,
            capture_output=True,
        )
    
    # Checkout specific commit if not "master"
    if commit and commit not in ("master", "main"):
        subprocess.run(
            ["git", "checkout", commit],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )
    
    return repo_path


def get_oracle(oracle_type: str):
    """Get the oracle extractor for the given type."""
    if oracle_type == "canonical_paths":
        return CanonicalPathsOracle()
    elif oracle_type == "import_linter":
        if ImportLinterOracle:
            return ImportLinterOracle({})
        else:
            raise ImportError("ImportLinterOracle not available (check imports)")
    else:
        raise ValueError(f"Unknown oracle type: {oracle_type}")


def extract_oracle_truth(repo_path: Path, repo_config: Dict[str, Any]) -> OracleResult:
    """Extract ground truth from the oracle."""
    oracle_type = repo_config["oracle_type"]
    oracle = get_oracle(oracle_type)
    
    # Validate config
    errors = oracle.validate_config(repo_config)
    if errors:
        raise ValueError(f"Invalid oracle config: {errors}")
    
    return oracle.extract(repo_path, repo_config)


def run_spectrometer(repo_path: Path) -> Dict[str, Any]:
    """Run Spectrometer on the repository and return the graph."""
    # Check if CLI exists
    if not SPECTROMETER_CLI.exists():
        print(f"  Warning: Spectrometer CLI not found at {SPECTROMETER_CLI}")
        print("  Using fallback: direct import of learning_engine")
        return run_spectrometer_direct(repo_path)
    
    # TODO: Implement CLI-based execution
    return run_spectrometer_direct(repo_path)


def run_spectrometer_direct(repo_path: Path) -> Dict[str, Any]:
    """Run Spectrometer directly via Python import."""
    # Add core directory to path (where the modules live)
    core_path = PROJECT_ROOT / "core"
    if str(core_path) not in sys.path:
        sys.path.insert(0, str(core_path))
    
    try:
        from universal_detector import UniversalPatternDetector
        
        detector = UniversalPatternDetector()
        result = detector.analyze_repository(str(repo_path))
        
        # Extract particles from comprehensive_results
        comprehensive = result.get("comprehensive_results", {})
        particles = comprehensive.get("particles", [])
        
        return {
            "particles": particles,
            "components": {p.get("name", ""): p for p in particles},
            "raw_result": result,
        }
    except ImportError as e:
        print(f"  Warning: Could not import UniversalPatternDetector: {e}")
        print("  Returning empty result for comparison.")
        return {"components": {}, "particles": []}


def run_baseline_prediction(repo_path: Path) -> Dict[str, Any]:
    """Run Naive Baseline prediction instead of Spectrometer."""
    import os
    
    baseline = NaiveLayerBaseline()
    
    # Walk repo to find all Python files
    all_files = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".py"):
                # Make relative to repo root
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, repo_path)
                # Convert to standard format
                all_files.append(rel_path.replace("\\", "/"))
    
    # Run prediction
    particles = baseline.analyze_repo(str(repo_path), all_files)
    
    return {
        "particles": particles,
        "components": {p.get("name", ""): p for p in particles},
        "raw_result": {"source": "NaiveLayerBaseline"},
    }


# Map Spectrometer types to standard layer names
TYPE_TO_LAYER = {
    # Core/Domain layer types
    "Entity": "Core", "ValueObject": "Core", "AggregateRoot": "Core",
    "DomainService": "Core", "DomainEvent": "Core", "Specification": "Core",
    "Policy": "Core", "Repository": "Core",
    # Application layer types
    "UseCase": "Application", "ApplicationService": "Application",
    "Command": "Application", "Query": "Application", "DTO": "Application",
    "EventHandler": "Application", "CommandHandler": "Application",
    # Infrastructure layer types
    "RepositoryImpl": "Infrastructure", "Gateway": "Infrastructure",
    "Adapter": "Infrastructure", "Client": "Infrastructure",
    # Interface/Presentation layer types
    "Controller": "Interface", "Mapper": "Interface",
    # Cross-cutting (map to Unknown for layer comparison)
    "Factory": "Unknown", "Service": "Unknown",
    "Observer": "Unknown", "Configuration": "Unknown",
    "Exception": "Unknown", "Utility": "Unknown",
    "Provider": "Unknown", "Builder": "Unknown",
    "Test": "Unknown", "Event": "Unknown",
    "Unknown": "Unknown",
}


def infer_layer_from_type(particle_type: str) -> str:
    """Infer architectural layer from Spectrometer particle type."""
    if particle_type == "NaiveFile":
        # Baseline implementation handles layer inference and puts it in inferred_layer field
        # So we shouldn't be calling this for baseline particles usually, 
        # but compare_predictions will need adjustment if it calls this unconditionally.
        return "Unknown"
    return TYPE_TO_LAYER.get(particle_type, "Unknown")


def translate_oracle_to_spectrometer(
    oracle_component: str, 
    mapping: Dict[str, Any]
) -> str:
    """Translate oracle component name to Spectrometer Layer."""
    layer_map = mapping.get("oracle_to_layer", {})
    return layer_map.get(oracle_component, oracle_component)


def normalize_file_path(file_path: str, repo_path: Path) -> str:
    """
    Normalize a file path to be relative to repo_path.
    
    Handles:
    - Absolute paths
    - Paths relative to cwd that include repo path
    - Already-relative paths
    """
    if not file_path:
        return ""
    
    # Normalize slashes
    file_path = file_path.replace("\\", "/")
    repo_str = str(repo_path.resolve()).replace("\\", "/")
    
    # If it's an absolute path containing repo dir, make it relative
    if repo_str in file_path:
        idx = file_path.find(repo_str)
        relative = file_path[idx + len(repo_str):]
        return relative.lstrip("/")
    
    # If path starts with repo name (as directory), strip it
    repo_name = repo_path.name
    if file_path.startswith(repo_name + "/"):
        return file_path[len(repo_name) + 1:]
    
    # Check if path is relative but includes path components leading to repo
    parts = file_path.split("/")
    for i, part in enumerate(parts):
        if part == repo_name and i < len(parts) - 1:
            return "/".join(parts[i + 1:])
    
    return file_path


def compare_predictions(
    oracle_result: OracleResult,
    spectrometer_result: Dict[str, Any],
    mapping: Dict[str, Any],
    repo_path: Path,
) -> ComparisonMetrics:
    """
    Compare Spectrometer predictions against oracle ground truth.
    
    For each symbol Spectrometer finds:
    1. Get its file path
    2. Look up oracle component for that file
    3. Translate oracle component -> expected Spectrometer label
    4. Compare expected vs actual
    """
    metrics = ComparisonMetrics()
    
    # Get predicted particles/components
    particles = spectrometer_result.get("particles", [])
    if not particles:
        particles = list(spectrometer_result.get("components", {}).values())
    
    # Counters for precision/recall calculation
    oracle_counts: Counter[str] = Counter()
    predicted_counts: Counter[str] = Counter()
    correct_counts: Counter[str] = Counter()
    
    # Confusion matrix
    confusion: Dict[str, Dict[str, int]] = {}
    
    # Debug: collect unmatched paths
    unmatched_paths: List[str] = []
    
    for particle in particles:
        metrics.total_symbols += 1
        
        # Get file path and normalize to repo-relative
        file_path_raw = particle.get("file_path", "")
        if not file_path_raw:
            continue
        
        file_path = normalize_file_path(file_path_raw, repo_path)
        
        # Try to match against oracle membership
        oracle_component = oracle_result.membership.get_component(file_path)
        
        if oracle_component:
            metrics.symbols_with_oracle_label += 1
            
            # Translate oracle component to expected Spectrometer label
            expected_label = translate_oracle_to_spectrometer(oracle_component, mapping)
            
            # Get Spectrometer's prediction
            # Since Spectrometer outputs 'type' (e.g., Entity, Command), we need to
            # infer the layer to compare against oracle's layer ground truth
            particle_type = (
                particle.get("type") or 
                particle.get("particle_type") or
                "Unknown"
            )
            
            # Convert type to layer for fair comparison
            predicted_label = infer_layer_from_type(particle_type)
            
            oracle_counts[expected_label] += 1
            predicted_counts[predicted_label] += 1
            metrics.matched_symbols += 1
            
            if predicted_label == expected_label:
                metrics.correct_component += 1
                correct_counts[expected_label] += 1
            
            # Update confusion matrix
            if expected_label not in confusion:
                confusion[expected_label] = {}
            if predicted_label not in confusion[expected_label]:
                confusion[expected_label][predicted_label] = 0
            confusion[expected_label][predicted_label] += 1
        else:
            metrics.symbols_without_oracle_label += 1
            if len(unmatched_paths) < 5:  # Collect first few for debugging
                unmatched_paths.append(file_path)
    
    # Debug output if no matches found
    if metrics.symbols_with_oracle_label == 0 and particles:
        print(f"   DEBUG: No oracle matches found!")
        print(f"   Sample spectrometer paths: {unmatched_paths[:3]}")
        oracle_sample = list(oracle_result.membership.file_to_component.keys())[:3]
        print(f"   Sample oracle paths: {oracle_sample}")
    
    # Calculate accuracy
    if metrics.matched_symbols > 0:
        metrics.component_accuracy = metrics.correct_component / metrics.matched_symbols
    
    # Calculate coverage
    if metrics.total_symbols > 0:
        metrics.coverage_rate = metrics.symbols_with_oracle_label / metrics.total_symbols
    
    # Calculate per-component precision/recall
    all_labels = set(oracle_counts.keys()) | set(predicted_counts.keys())
    for label in all_labels:
        oracle_count = oracle_counts.get(label, 0)
        predicted_count = predicted_counts.get(label, 0)
        correct_count = correct_counts.get(label, 0)
        
        precision = correct_count / predicted_count if predicted_count > 0 else 0.0
        recall = correct_count / oracle_count if oracle_count > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        
        metrics.per_component[label] = {
            "oracle_count": oracle_count,
            "predicted_count": predicted_count,
            "correct_count": correct_count,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
        }
    
    metrics.confusion = confusion
    
    # ---------------------------------------------------------
    # Score 2: Boundary/Constraint Violations
    # ---------------------------------------------------------
    oracle_constraints = oracle_result.constraints
    
    # Extract internal edges (file-to-file dependencies)
    comprehensive = spectrometer_result.get("raw_result", {}).get("comprehensive_results", {})
    dependencies = comprehensive.get("dependencies", {})
    raw_edges = dependencies.get("internal_edges", [])

    violation_count = 0
    total_edges = 0
    detected_violations = []

    # Map file path -> component for fast lookup
    file_to_comp = oracle_result.membership.file_to_component

    for edge in raw_edges:
        src_file = edge.get("from")
        tgt_file = edge.get("to")
        
        if not src_file or not tgt_file:
            continue
        
        # Normalize paths (they should already be relative from dependency_analyzer, but good to be safe)
        src_rel = normalize_file_path(src_file, repo_path)
        tgt_rel = normalize_file_path(tgt_file, repo_path)
        
        # Get components
        src_comp = file_to_comp.get(src_rel)
        tgt_comp = file_to_comp.get(tgt_rel)
        
        # Only check cross-component edges where both sides are known
        if src_comp and tgt_comp and src_comp != tgt_comp:
            total_edges += 1
            is_allowed = oracle_constraints.is_allowed(src_comp, tgt_comp)
            
            # If explicit forbid OR (allowed list exists AND not allowed)
            violation = False
            if oracle_constraints.forbidden and (src_comp, tgt_comp) in oracle_constraints.forbidden:
                violation = True
            elif oracle_constraints.allowed and (src_comp, tgt_comp) not in oracle_constraints.allowed:
                # Implicit denial if allow-list is present
                violation = True
            
            if violation:
                violation_count += 1
                detected_violations.append({
                    "from": src_comp,
                    "to": tgt_comp,
                    "from_file": src_rel,
                    "to_file": tgt_rel,
                    "count": edge.get("count", 1)
                })

    metrics.total_dependency_edges = total_edges
    metrics.violating_edges = violation_count
    metrics.violation_rate = violation_count / total_edges if total_edges > 0 else 0.0
    metrics.documented_violations = detected_violations

    return metrics


def run_single_benchmark(repo_config: Dict[str, Any], extract_only: bool = False, use_baseline: bool = False) -> Dict[str, Any]:
    """Run benchmark for a single repository."""
    repo_id = repo_config["id"]
    print(f"\n{'='*60}")
    print(f"Benchmark: {repo_config.get('name', repo_id)} {'(BASELINE)' if use_baseline else ''}")
    print(f"{'='*60}")
    
    # 1. Clone/update repo
    print("1. Setting up repository...")
    try:
        repo_path = clone_or_update_repo(repo_config)
        print(f"   Repo path: {repo_path}")
    except Exception as e:
        print(f"   ERROR cloning repo: {e}")
        return {"error": str(e), "repo_id": repo_id}
    
    # 2. Extract Oracle Truth
    print("2. Extracting oracle ground truth...")
    try:
        oracle_result = extract_oracle_truth(repo_path, repo_config)
        summary = oracle_result.summary()
        print(f"   Source: {summary['oracle_source']}")
        print(f"   Found {summary['total_files']} files with components")
        if summary['warnings']:
            print(f"   Warnings: {summary['warnings']}")
    except Exception as e:
        print(f"   ERROR extracting oracle: {e}")
        return {"error": str(e), "repo_id": repo_id}
        
    if extract_only:
        return {
            "repo_id": repo_id,
            "oracle_summary": oracle_result.summary(),
            "status": "extracted_only"
        }
    
    # 3. Load translation mapping
    print("3. Loading translation mapping...")
    mapping_file = repo_config.get("mapping_file", "")
    mapping = load_mapping(mapping_file) if mapping_file else {}
    print(f"   Mapping: {mapping.get('name', 'none')}")
    
    # 4. Run Prediction (Spectrometer or Baseline)
    tool_name = "Naive Baseline" if use_baseline else "Spectrometer"
    print(f"4. Running {tool_name} analysis...")
    try:
        if use_baseline:
            spectrometer_result = run_baseline_prediction(repo_path)
        else:
            spectrometer_result = run_spectrometer(repo_path)
        
        comp_count = len(spectrometer_result.get("components", {}))
        part_count = len(spectrometer_result.get("particles", []))
        print(f"   Found {part_count} particles")
    except Exception as e:
        print(f"   ERROR running {tool_name}: {e}")
        return {"error": str(e), "repo_id": repo_id}
    
    # 5. Compare Predictions
    print("5. Comparing predictions vs oracle...")
    metrics = compare_predictions(oracle_result, spectrometer_result, mapping, repo_path)
    
    print(f"   Component accuracy: {metrics.component_accuracy:.1%}")
    print(f"   Boundary violations: {metrics.violating_edges}/{metrics.total_dependency_edges} edges ({metrics.violation_rate:.1%})")
    print(f"   Coverage rate: {metrics.coverage_rate:.1%}")
    print(f"   Matched/Total: {metrics.matched_symbols}/{metrics.total_symbols}")
    
    # 6. Generate report
    report = {
        "repo_id": repo_id,
        "repo_name": repo_config.get("name", repo_id),
        "oracle_type": repo_config["oracle_type"],
        "tool": "naive_baseline" if use_baseline else "spectrometer_v1",
        "validated_source": repo_config.get("validated_source", ""),
        "oracle_summary": oracle_result.summary(),
        "metrics": metrics.to_dict(),
    }
    
    return report


def save_report(report: Dict[str, Any], repo_id: str) -> Path:
    """Save report to JSON file."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / f"{repo_id}_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    return report_path


def print_summary(reports: List[Dict[str, Any]]) -> None:
    """Print summary of all benchmark results."""
    print("\n" + "="*70)
    print("ORACLE BENCHMARK SUMMARY")
    print("="*70)
    
    for report in reports:
        if "error" in report:
            print(f"  ❌ {report['repo_id']}: ERROR - {report['error']}")
            continue
        
        metrics = report.get("metrics", {})
        accuracy = metrics.get("component_accuracy", {}).get("accuracy", 0)
        coverage = metrics.get("coverage", {}).get("coverage_rate", 0)
        
        status = "✅" if accuracy >= 0.8 else "⚠️" if accuracy >= 0.5 else "❌"
        print(f"  {status} {report['repo_id']}: accuracy={accuracy:.1%} coverage={coverage:.1%}")
    
    print("="*70)


def main():
    parser = argparse.ArgumentParser(description="Run Oracle Benchmark Suite")
    parser.add_argument("--repo", help="Run single repo by ID")
    parser.add_argument("--extract-only", action="store_true", help="Only extract oracle truth")
    parser.add_argument("--baseline", action="store_true", help="Run Naive Baseline providing naive comparison")
    parser.add_argument("--list", action="store_true", help="List available repos")
    args = parser.parse_args()
    
    # Load manifest
    manifest = load_manifest()
    repos = manifest.get("repos", [])
    
    if args.list:
        print("Available benchmark repos:")
        for repo in repos:
             print(f"  - {repo['id']}: {repo.get('name', 'Unknown')} ({repo['oracle_type']})")
        return
    
    # Filter to single repo if specified
    if args.repo:
        repos = [r for r in repos if r["id"] == args.repo]
        if not repos:
            print(f"Error: Repo '{args.repo}' not found in manifest")
            return
    
    # Run benchmarks
    reports = []
    for repo_config in repos:
        report = run_single_benchmark(repo_config, extract_only=args.extract_only, use_baseline=args.baseline)
        reports.append(report)
        
        # Save individual report
        if "error" not in report:
            prefix = "baseline" if args.baseline else "spectrometer"
            report_path = save_report(report, f"{prefix}_{repo_config['id']}")
            print(f"   Report saved: {report_path}")
    
    # Print summary
    print_summary(reports)


if __name__ == "__main__":
    main()
