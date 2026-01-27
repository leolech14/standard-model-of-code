#!/usr/bin/env python3
"""
COMMUNICATION FABRIC - Unified Metrics Layer
=============================================

Computes the Communication Fabric state vector by aggregating
metrics from existing engines (Collider, BARE, HSL, etc.)

State Variables:
    F       Feedback Latency (time from trigger→detect→correct→verify)
    MI      Mutual Information (code-docs alignment)
    N       Noise (orphans, phantoms, drift, complexity)
    SNR     Signal-to-Noise Ratio (closed loops / total)
    R_auto  Automated Redundancy (tests, types, schemas)
    R_manual Manual Redundancy (docs, reviews)
    ΔH      Change Entropy (structural novelty)

Usage:
    from .agent.intelligence.comms.fabric import compute_state_vector
    state = compute_state_vector()

CLI:
    ./pe comm metrics
"""

import json
import os
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List

# Project root
# fabric.py is at .agent/intelligence/comms/fabric.py
# parents[0] = comms, [1] = intelligence, [2] = .agent, [3] = PROJECT_elements
REPO_ROOT = Path(__file__).resolve().parents[3]

# Add paths for imports
sys.path.insert(0, str(REPO_ROOT / "standard-model-of-code" / "src"))
sys.path.insert(0, str(REPO_ROOT / ".agent" / "tools"))


@dataclass
class StateVector:
    """Communication Fabric state at a point in time."""
    timestamp: str

    # Core metrics
    F: float          # Feedback Latency (hours, lower is better)
    MI: float         # Mutual Information (0-1, higher is better)
    N: float          # Noise (0-1, lower is better)
    SNR: float        # Signal-to-Noise Ratio (higher is better)
    R_auto: float     # Automated Redundancy (0-1)
    R_manual: float   # Manual Redundancy (0-1)
    delta_H: float    # Change Entropy (normalized)

    # Derived
    stability_margin: float  # Distance from bifurcation
    health_tier: str         # DIAMOND/GOLD/SILVER/BRONZE/CRITICAL

    # Component breakdown
    components: Dict[str, Any]


def get_git_stats(days: int = 7) -> Dict[str, Any]:
    """Get git statistics for ΔH calculation."""
    try:
        since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        # Count commits
        result = subprocess.run(
            ["git", "rev-list", "--count", f"--since={since}", "HEAD"],
            capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=30
        )
        commit_str = result.stdout.strip()
        commits = int(commit_str) if commit_str and commit_str.isdigit() else 0

        # Unique files changed
        result2 = subprocess.run(
            ["git", "log", f"--since={since}", "--name-only", "--pretty=format:"],
            capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=30
        )
        files = set(l.strip() for l in result2.stdout.split('\n') if l.strip())

        return {
            "commits": commits,
            "files_changed": len(files),
            "period_days": days,
        }
    except Exception as e:
        return {"error": str(e), "commits": 0, "files_changed": 0, "period_days": days}


def get_test_stats() -> Dict[str, Any]:
    """Get test coverage statistics for R_auto."""
    try:
        collider_path = REPO_ROOT / "standard-model-of-code"

        # Use venv pytest
        pytest_path = REPO_ROOT / ".tools_venv" / "bin" / "pytest"
        if not pytest_path.exists():
            pytest_path = "pytest"  # Fall back to system

        # Run pytest collection only (fast)
        result = subprocess.run(
            [str(pytest_path), "--collect-only", "-q"],
            capture_output=True, text=True,
            cwd=str(collider_path),
            timeout=30
        )

        # Parse test count - each line with :: is a test
        output = result.stdout
        test_lines = [l for l in output.split('\n') if '::' in l and 'test' in l.lower()]
        test_count = len(test_lines)

        # Also check for "X items" or "X tests collected" format
        if test_count == 0:
            for line in output.split('\n'):
                if 'collected' in line.lower() or 'items' in line.lower():
                    parts = line.split()
                    for p in parts:
                        if p.isdigit():
                            test_count = int(p)
                            break

        return {
            "test_count": test_count,
            "has_tests": test_count > 0,
        }
    except Exception as e:
        return {"error": str(e), "test_count": 0, "has_tests": False}


def get_symmetry_stats() -> Dict[str, Any]:
    """Get Wave-Particle symmetry for MI calculation."""
    try:
        # Check for cached unified_analysis.json
        analysis_path = REPO_ROOT / "standard-model-of-code" / ".collider" / "unified_analysis.json"
        if not analysis_path.exists():
            analysis_path = REPO_ROOT / "unified_analysis.json"

        if analysis_path.exists():
            with open(analysis_path) as f:
                data = json.load(f)

            nodes = data.get("nodes", [])
            total = len(nodes)

            # Count documented nodes
            documented = sum(1 for n in nodes if n.get("has_docstring") or n.get("docstring"))

            # Count nodes with semantic roles
            classified = sum(1 for n in nodes if n.get("semantic_role") and n.get("semantic_role") != "unknown")

            return {
                "total_nodes": total,
                "documented_nodes": documented,
                "classified_nodes": classified,
                "doc_coverage": documented / total if total > 0 else 0,
                "classification_coverage": classified / total if total > 0 else 0,
            }

        return {"error": "No unified_analysis.json found", "doc_coverage": 0}
    except Exception as e:
        return {"error": str(e), "doc_coverage": 0}


def get_loop_latencies() -> Dict[str, float]:
    """Estimate feedback loop latencies in hours."""
    # These are based on architecture analysis
    # In future: parse actual timestamps from logs
    return {
        "HSL_validation": 24.0,      # Daily cron
        "BARE_opportunity": 0.05,     # ~3 minutes (post-commit)
        "AEP_enrichment": 1.0,        # Hourly cron
        "test_suite": 0.02,           # ~1 minute
    }


def get_noise_indicators() -> Dict[str, Any]:
    """Get noise indicators (orphans, phantoms, complexity)."""
    indicators = {
        "venv_files": 0,
        "unknown_roles": 0,
        "high_complexity": 0,
        "todo_fixme": 0,
    }

    try:
        # Check venv pollution (quick estimate via ls)
        venv_path = REPO_ROOT / ".tools_venv"
        if venv_path.exists():
            result = subprocess.run(
                ["find", str(venv_path), "-type", "f", "-name", "*.py"],
                capture_output=True, text=True, timeout=10
            )
            indicators["venv_files"] = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
    except Exception:
        pass

    try:
        # Count TODO/FIXME in code (exclude venv)
        result = subprocess.run(
            ["grep", "-r", "-c", "-E", "TODO|FIXME", "--include=*.py",
             "--exclude-dir=.tools_venv", "--exclude-dir=.venv", "--exclude-dir=node_modules"],
            capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=30
        )
        if result.stdout:
            total = sum(int(l.split(':')[-1]) for l in result.stdout.strip().split('\n')
                       if ':' in l and l.split(':')[-1].isdigit())
            indicators["todo_fixme"] = total
    except Exception:
        pass

    return indicators


def compute_state_vector() -> StateVector:
    """
    Compute the full Communication Fabric state vector.

    Returns:
        StateVector with all metrics computed
    """
    timestamp = datetime.now().isoformat()

    # Gather component data
    git_stats = get_git_stats(7)
    test_stats = get_test_stats()
    symmetry_stats = get_symmetry_stats()
    loop_latencies = get_loop_latencies()
    noise_indicators = get_noise_indicators()

    # === COMPUTE STATE VARIABLES ===

    # F: Feedback Latency (weighted average of loops, in hours)
    # Weight by importance: HSL most important for architectural health
    weights = {"HSL_validation": 0.4, "BARE_opportunity": 0.2, "AEP_enrichment": 0.2, "test_suite": 0.2}
    F = sum(loop_latencies[k] * weights[k] for k in weights)

    # MI: Mutual Information (code-docs alignment)
    # Based on documentation coverage and classification coverage
    doc_cov = symmetry_stats.get("doc_coverage", 0)
    class_cov = symmetry_stats.get("classification_coverage", 0)
    MI = (doc_cov * 0.6 + class_cov * 0.4)  # Weight docs higher

    # N: Noise (normalized 0-1, based on pollution indicators)
    venv_noise = min(noise_indicators["venv_files"] / 5000, 1.0)  # Cap at 5000
    todo_noise = min(noise_indicators["todo_fixme"] / 100, 1.0)   # Cap at 100
    N = (venv_noise * 0.5 + todo_noise * 0.5)

    # SNR: Signal-to-Noise Ratio
    # Signal = documented + tested; Noise = N
    signal = MI * (1 if test_stats.get("has_tests") else 0.5)
    SNR = signal / (N + 0.1)  # Add 0.1 to avoid division by zero

    # R_auto: Automated Redundancy
    # Based on test count and type coverage (estimated)
    test_score = min(test_stats.get("test_count", 0) / 150, 1.0)  # Target: 150 tests
    R_auto = test_score

    # R_manual: Manual Redundancy
    # Based on documentation presence
    R_manual = doc_cov

    # ΔH: Change Entropy (normalized by baseline)
    # High file churn = high entropy change
    files_changed = git_stats.get("files_changed", 0)
    baseline_churn = 50  # Expected weekly churn
    delta_H = min(files_changed / baseline_churn, 2.0) / 2.0  # Normalize to 0-1, cap at 2x

    # === DERIVED METRICS ===

    # Stability margin: R_auto² > threshold for stability
    # Margin = how far above threshold we are
    threshold = 0.3  # Estimated (β·δ)/(γ·ε·MI)
    stability_margin = (R_auto ** 2) - threshold

    # Health tier based on composite score
    composite = (MI * 0.3 + (1 - N) * 0.2 + SNR / 10 * 0.2 + R_auto * 0.2 + (1 - delta_H) * 0.1)

    if composite >= 0.9:
        health_tier = "DIAMOND"
    elif composite >= 0.75:
        health_tier = "GOLD"
    elif composite >= 0.6:
        health_tier = "SILVER"
    elif composite >= 0.4:
        health_tier = "BRONZE"
    else:
        health_tier = "CRITICAL"

    return StateVector(
        timestamp=timestamp,
        F=round(F, 2),
        MI=round(MI, 4),
        N=round(N, 4),
        SNR=round(SNR, 4),
        R_auto=round(R_auto, 4),
        R_manual=round(R_manual, 4),
        delta_H=round(delta_H, 4),
        stability_margin=round(stability_margin, 4),
        health_tier=health_tier,
        components={
            "git": git_stats,
            "tests": test_stats,
            "symmetry": symmetry_stats,
            "latencies": loop_latencies,
            "noise": noise_indicators,
        }
    )


def print_state_report(state: StateVector) -> None:
    """Print human-readable state report."""
    print("=" * 60)
    print("COMMUNICATION FABRIC - STATE VECTOR")
    print("=" * 60)
    print(f"Timestamp: {state.timestamp}")
    print(f"Health Tier: {state.health_tier}")
    print()

    print("STATE VARIABLES:")
    print(f"  F (Feedback Latency):    {state.F:>8.2f} hours")
    print(f"  MI (Mutual Information): {state.MI:>8.4f} (0-1)")
    print(f"  N (Noise):               {state.N:>8.4f} (0-1, lower=better)")
    print(f"  SNR (Signal-to-Noise):   {state.SNR:>8.4f}")
    print(f"  R_auto (Auto Redundancy):{state.R_auto:>8.4f}")
    print(f"  R_manual (Manual):       {state.R_manual:>8.4f}")
    print(f"  ΔH (Change Entropy):     {state.delta_H:>8.4f}")
    print()

    print("STABILITY:")
    print(f"  Margin: {state.stability_margin:+.4f}", end="")
    if state.stability_margin > 0:
        print(" (STABLE)")
    else:
        print(" (UNSTABLE - RISK)")
    print()

    print("COMPONENT SUMMARY:")
    print(f"  Git: {state.components['git'].get('commits', 0)} commits, {state.components['git'].get('files_changed', 0)} files (7 days)")
    print(f"  Tests: {state.components['tests'].get('test_count', 0)} collected")
    print(f"  Nodes: {state.components['symmetry'].get('total_nodes', 0)} total, {state.components['symmetry'].get('documented_nodes', 0)} documented")
    print(f"  Noise: {state.components['noise'].get('venv_files', 0)} venv files, {state.components['noise'].get('todo_fixme', 0)} TODOs")
    print()

    # Recommendations
    print("RECOMMENDATIONS:")
    if state.F > 12:
        print("  [!] F too high - Consider moving HSL to post-commit for critical domains")
    if state.MI < 0.7:
        print("  [!] MI low - Increase documentation coverage")
    if state.N > 0.3:
        print("  [!] N high - Clean up venv pollution and TODOs")
    if state.R_auto < 0.5:
        print("  [!] R_auto low - Add more automated tests")
    if state.delta_H > 0.7:
        print("  [!] ΔH high - System in flux, increase damping")
    if state.stability_margin < 0:
        print("  [!!!] STABILITY MARGIN NEGATIVE - System at risk of death spiral")

    if state.stability_margin > 0.1 and state.MI > 0.7:
        print("  [OK] System appears healthy")

    print("=" * 60)


# =============================================================================
# TIME-SERIES STORAGE
# =============================================================================

HISTORY_FILE = REPO_ROOT / ".agent" / "intelligence" / "comms" / "state_history.jsonl"


def append_to_history(state: StateVector) -> None:
    """Append state vector to history file (JSONL format)."""
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Compact format for history (no components, just core metrics)
    record = {
        "ts": state.timestamp,
        "F": state.F,
        "MI": state.MI,
        "N": state.N,
        "SNR": state.SNR,
        "R_auto": state.R_auto,
        "R_manual": state.R_manual,
        "dH": state.delta_H,
        "margin": state.stability_margin,
        "tier": state.health_tier,
    }

    with open(HISTORY_FILE, 'a') as f:
        f.write(json.dumps(record) + '\n')


def load_history(days: int = 7) -> List[Dict]:
    """Load recent history from JSONL file."""
    if not HISTORY_FILE.exists():
        return []

    cutoff = datetime.now() - timedelta(days=days)
    records = []

    with open(HISTORY_FILE) as f:
        for line in f:
            if line.strip():
                try:
                    record = json.loads(line)
                    ts = datetime.fromisoformat(record["ts"])
                    if ts >= cutoff:
                        records.append(record)
                except (json.JSONDecodeError, KeyError, ValueError):
                    continue

    return records


def compute_trends(history: List[Dict]) -> Dict[str, Any]:
    """Compute trends from historical data."""
    if len(history) < 2:
        return {"status": "insufficient_data", "records": len(history)}

    # Get first and last records
    first = history[0]
    last = history[-1]

    # Compute deltas
    trends = {
        "period_hours": (datetime.fromisoformat(last["ts"]) -
                        datetime.fromisoformat(first["ts"])).total_seconds() / 3600,
        "records": len(history),
        "deltas": {},
        "alerts": [],
    }

    for key in ["F", "MI", "N", "SNR", "R_auto", "dH", "margin"]:
        if key in first and key in last:
            delta = last[key] - first[key]
            trends["deltas"][key] = round(delta, 4)

            # Check for concerning trends
            if key == "margin" and delta < -0.1:
                trends["alerts"].append(f"Stability margin declining: {delta:+.4f}")
            if key == "N" and delta > 0.1:
                trends["alerts"].append(f"Noise increasing: {delta:+.4f}")
            if key == "MI" and delta < -0.05:
                trends["alerts"].append(f"Mutual Information declining: {delta:+.4f}")

    # Compute averages
    trends["averages"] = {}
    for key in ["F", "MI", "N", "SNR", "R_auto", "dH", "margin"]:
        values = [r.get(key, 0) for r in history if key in r]
        if values:
            trends["averages"][key] = round(sum(values) / len(values), 4)

    return trends


# =============================================================================
# STABILITY ALERTING
# =============================================================================

ALERTS_FILE = REPO_ROOT / ".agent" / "intelligence" / "comms" / "alerts.jsonl"

# Alert thresholds
STABILITY_WARNING_THRESHOLD = 0.3
STABILITY_CRITICAL_THRESHOLD = 0.1
NOISE_WARNING_THRESHOLD = 0.5
MI_WARNING_THRESHOLD = 0.5


def check_stability_alerts(state: StateVector) -> List[Dict[str, Any]]:
    """
    Check for stability alerts based on state vector.

    Returns list of alert dicts with severity, message, and metric.
    """
    alerts = []
    ts = datetime.now().isoformat()

    # Stability margin alerts (most critical)
    if state.stability_margin < 0:
        alerts.append({
            "timestamp": ts,
            "severity": "CRITICAL",
            "type": "stability_negative",
            "message": f"SYSTEM UNSTABLE: Stability margin negative ({state.stability_margin:.4f})",
            "metric": "stability_margin",
            "value": state.stability_margin,
            "threshold": 0,
        })
    elif state.stability_margin < STABILITY_CRITICAL_THRESHOLD:
        alerts.append({
            "timestamp": ts,
            "severity": "CRITICAL",
            "type": "stability_critical",
            "message": f"Stability margin critically low ({state.stability_margin:.4f} < {STABILITY_CRITICAL_THRESHOLD})",
            "metric": "stability_margin",
            "value": state.stability_margin,
            "threshold": STABILITY_CRITICAL_THRESHOLD,
        })
    elif state.stability_margin < STABILITY_WARNING_THRESHOLD:
        alerts.append({
            "timestamp": ts,
            "severity": "WARNING",
            "type": "stability_warning",
            "message": f"Stability margin low ({state.stability_margin:.4f} < {STABILITY_WARNING_THRESHOLD})",
            "metric": "stability_margin",
            "value": state.stability_margin,
            "threshold": STABILITY_WARNING_THRESHOLD,
        })

    # Noise alerts
    if state.N > NOISE_WARNING_THRESHOLD:
        alerts.append({
            "timestamp": ts,
            "severity": "WARNING",
            "type": "noise_high",
            "message": f"Noise level high ({state.N:.4f} > {NOISE_WARNING_THRESHOLD})",
            "metric": "N",
            "value": state.N,
            "threshold": NOISE_WARNING_THRESHOLD,
        })

    # MI alerts
    if state.MI < MI_WARNING_THRESHOLD:
        alerts.append({
            "timestamp": ts,
            "severity": "WARNING",
            "type": "mi_low",
            "message": f"Mutual Information low ({state.MI:.4f} < {MI_WARNING_THRESHOLD})",
            "metric": "MI",
            "value": state.MI,
            "threshold": MI_WARNING_THRESHOLD,
        })

    # Feedback latency alerts
    if state.F > 24:
        alerts.append({
            "timestamp": ts,
            "severity": "WARNING",
            "type": "latency_high",
            "message": f"Feedback latency high ({state.F:.2f}h > 24h)",
            "metric": "F",
            "value": state.F,
            "threshold": 24,
        })

    return alerts


def log_alerts(alerts: List[Dict[str, Any]]) -> None:
    """Log alerts to alerts file."""
    if not alerts:
        return

    ALERTS_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(ALERTS_FILE, 'a') as f:
        for alert in alerts:
            f.write(json.dumps(alert) + '\n')


def print_alerts(alerts: List[Dict[str, Any]]) -> None:
    """Print alerts to stdout."""
    if not alerts:
        return

    print()
    print("=" * 60)
    print("STABILITY ALERTS")
    print("=" * 60)

    critical = [a for a in alerts if a["severity"] == "CRITICAL"]
    warnings = [a for a in alerts if a["severity"] == "WARNING"]

    if critical:
        print("\n[CRITICAL]")
        for alert in critical:
            print(f"  !!! {alert['message']}")

    if warnings:
        print("\n[WARNING]")
        for alert in warnings:
            print(f"  [!] {alert['message']}")

    print("=" * 60)


def print_trends_report(trends: Dict[str, Any]) -> None:
    """Print trends analysis."""
    print("=" * 60)
    print("COMMUNICATION FABRIC - TREND ANALYSIS")
    print("=" * 60)

    if trends.get("status") == "insufficient_data":
        print(f"Insufficient data for trends ({trends['records']} records)")
        print("Run './pe comm metrics --record' periodically to build history")
        return

    print(f"Period: {trends['period_hours']:.1f} hours ({trends['records']} samples)")
    print()

    print("DELTAS (change over period):")
    for key, delta in trends.get("deltas", {}).items():
        direction = "↑" if delta > 0 else "↓" if delta < 0 else "→"
        print(f"  {key:>8}: {delta:+.4f} {direction}")
    print()

    print("AVERAGES:")
    for key, avg in trends.get("averages", {}).items():
        print(f"  {key:>8}: {avg:.4f}")
    print()

    if trends.get("alerts"):
        print("ALERTS:")
        for alert in trends["alerts"]:
            print(f"  [!] {alert}")
    else:
        print("No concerning trends detected.")

    print("=" * 60)


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Communication Fabric Metrics")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--save", type=str, help="Save to file")
    parser.add_argument("--record", action="store_true", help="Record to history")
    parser.add_argument("--trends", action="store_true", help="Show trend analysis")
    parser.add_argument("--alerts-only", action="store_true", help="Only check and output alerts")
    parser.add_argument("--history-days", type=int, default=7, help="Days of history for trends")
    args = parser.parse_args()

    # Handle trends-only request
    if args.trends:
        history = load_history(args.history_days)
        trends = compute_trends(history)
        if args.json:
            print(json.dumps(trends, indent=2))
        else:
            print_trends_report(trends)
        return

    # Compute current state
    state = compute_state_vector()

    # Check for alerts
    alerts = check_stability_alerts(state)
    has_critical = any(a["severity"] == "CRITICAL" for a in alerts)

    # Record to history if requested
    if args.record:
        append_to_history(state)
        if alerts:
            log_alerts(alerts)

    # Alerts-only mode (for monitoring scripts)
    if args.alerts_only:
        if args.json:
            print(json.dumps(alerts, indent=2))
        else:
            if alerts:
                print_alerts(alerts)
            else:
                print("No alerts.")
        # Exit with code 2 for critical, 1 for warnings, 0 for clean
        if has_critical:
            sys.exit(2)
        elif alerts:
            sys.exit(1)
        sys.exit(0)

    # Output
    if args.json:
        output = asdict(state)
        output["alerts"] = alerts
        print(json.dumps(output, indent=2))
    else:
        print_state_report(state)

        # Print alerts if any
        if alerts:
            print_alerts(alerts)

        # Show mini-trends if we have history
        history = load_history(1)  # Last 24 hours
        if len(history) >= 2:
            print()
            trends = compute_trends(history)
            if trends.get("alerts"):
                print("TREND ALERTS:")
                for alert in trends["alerts"]:
                    print(f"  [!] {alert}")

    if args.save:
        with open(args.save, 'w') as f:
            json.dump(asdict(state), f, indent=2)
        print(f"\nSaved to: {args.save}")

    # Record automatically when --record is set
    # (don't double-record, already done above)

    # Exit with appropriate code for monitoring
    if has_critical:
        sys.exit(2)


if __name__ == "__main__":
    main()
