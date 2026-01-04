"""
Proof Stages
============

Individual stage handlers for the Standard Model proof pipeline.
Each stage is a pure function that takes input and returns results.
"""

import time
from typing import Dict, Any, List, Tuple
from collections import Counter
from dataclasses import dataclass, field


@dataclass
class StageResult:
    """Result from a single stage."""
    name: str
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    error: str = ""
    duration_ms: float = 0


def stage_classification(
    target_path: str,
    analyze_func,
    **kwargs
) -> StageResult:
    """
    Stage 1: CLASSIFICATION
    Extract nodes and edges from the codebase.
    """
    start = time.time()

    try:
        result = analyze_func(target_path, **kwargs)
        nodes = result.nodes if hasattr(result, 'nodes') else result.get('nodes', [])
        edges = result.edges if hasattr(result, 'edges') else result.get('edges', [])

        return StageResult(
            name="classification",
            success=True,
            data={
                "nodes": nodes,
                "edges": edges,
                "classification_time": time.time() - start
            },
            duration_ms=(time.time() - start) * 1000
        )
    except Exception as e:
        return StageResult(
            name="classification",
            success=False,
            error=str(e),
            duration_ms=(time.time() - start) * 1000
        )


def stage_role_distribution(nodes: List[Dict]) -> StageResult:
    """
    Stage 2: ROLE DISTRIBUTION
    Analyze role distribution and coverage.
    """
    start = time.time()

    role_counts = Counter()
    confidence_sum = 0
    confidence_count = 0

    for node in nodes:
        if hasattr(node, 'role'):
            role = node.role
            conf = node.role_confidence
        else:
            role = node.get('role', 'Unknown')
            conf = node.get('role_confidence', 0)

        role_counts[role] += 1
        if conf:
            confidence_sum += conf
            confidence_count += 1

    avg_confidence = confidence_sum / confidence_count if confidence_count else 0
    unknown_count = role_counts.get('Unknown', 0)
    coverage = (len(nodes) - unknown_count) / len(nodes) * 100 if nodes else 0

    return StageResult(
        name="role_distribution",
        success=True,
        data={
            "role_counts": dict(role_counts),
            "coverage": coverage,
            "average_confidence": avg_confidence,
            "entities": role_counts.get('Entity', 0) + role_counts.get('AggregateRoot', 0),
            "repositories": role_counts.get('Repository', 0),
            "services": role_counts.get('Service', 0) + role_counts.get('ApplicationService', 0),
            "controllers": role_counts.get('Controller', 0),
            "tests": role_counts.get('Test', 0)
        },
        duration_ms=(time.time() - start) * 1000
    )


def stage_antimatter(nodes: List[Dict], evaluator_class) -> StageResult:
    """
    Stage 3: ANTIMATTER VIOLATIONS
    Detect architectural violations.
    """
    start = time.time()

    try:
        evaluator = evaluator_class()
        particles = []
        for node in nodes:
            if hasattr(node, '__dict__'):
                particles.append(vars(node))
            elif hasattr(node, 'to_dict'):
                particles.append(node.to_dict())
            else:
                particles.append(node)

        result = evaluator.evaluate(particles)
        violations = result.violations

        return StageResult(
            name="antimatter",
            success=True,
            data={
                "violations": violations,
                "violation_count": len(violations)
            },
            duration_ms=(time.time() - start) * 1000
        )
    except Exception as e:
        return StageResult(
            name="antimatter",
            success=False,
            data={"violations": [], "violation_count": 0},
            error=str(e),
            duration_ms=(time.time() - start) * 1000
        )


def stage_predictions(role_data: Dict) -> StageResult:
    """
    Stage 4: PREDICTIONS
    Predict missing components based on role distribution.
    """
    start = time.time()

    entities = role_data.get('entities', 0)
    repositories = role_data.get('repositories', 0)
    services = role_data.get('services', 0)
    controllers = role_data.get('controllers', 0)
    tests = role_data.get('tests', 0)
    role_counts = role_data.get('role_counts', {})

    predictions = []

    # Missing repositories
    if entities > 0 and repositories < entities:
        missing = entities - repositories
        predictions.append(f"Missing ~{missing} Repositories for {entities} Entities")

    # Missing tests
    total_logic = services + controllers + role_counts.get('UseCase', 0)
    if total_logic > 0 and tests < total_logic:
        missing = total_logic - tests
        predictions.append(f"Missing ~{missing} Tests for {total_logic} logic components")

    # Missing services
    if entities > 3 and services == 0:
        predictions.append(f"Missing Services layer for {entities} Entities")

    return StageResult(
        name="predictions",
        success=True,
        data={"predictions": predictions},
        duration_ms=(time.time() - start) * 1000
    )


def stage_insights(nodes: List[Dict], edges: List[Dict], generate_func) -> StageResult:
    """
    Stage 5: ACTIONABLE INSIGHTS
    Generate actionable architectural insights.
    """
    start = time.time()

    try:
        insights, insights_report = generate_func(nodes, edges)

        insights_summary = []
        for insight in (insights or [])[:10]:
            insights_summary.append({
                "type": insight.type.value,
                "priority": insight.priority.value,
                "title": insight.title,
                "description": insight.description,
                "recommendation": insight.recommendation,
                "schema": insight.schema
            })

        return StageResult(
            name="insights",
            success=True,
            data={
                "insights": insights or [],
                "insights_summary": insights_summary,
                "insights_report": insights_report
            },
            duration_ms=(time.time() - start) * 1000
        )
    except Exception as e:
        return StageResult(
            name="insights",
            success=False,
            data={"insights": [], "insights_summary": [], "insights_report": ""},
            error=str(e),
            duration_ms=(time.time() - start) * 1000
        )


def stage_purpose_field(nodes: List[Dict], edges: List[Dict], detect_func) -> StageResult:
    """
    Stage 6: PURPOSE FIELD
    Detect architectural layers and purpose flow.
    """
    start = time.time()

    try:
        purpose_field = detect_func(nodes, edges)
        field_summary = purpose_field.summary()
        violations = purpose_field.violations if hasattr(purpose_field, 'violations') else []

        return StageResult(
            name="purpose_field",
            success=True,
            data={
                "purpose_field": purpose_field,
                "summary": field_summary,
                "violations": violations
            },
            duration_ms=(time.time() - start) * 1000
        )
    except Exception as e:
        return StageResult(
            name="purpose_field",
            success=False,
            data={"purpose_field": None, "summary": {}, "violations": []},
            error=str(e),
            duration_ms=(time.time() - start) * 1000
        )


def stage_execution_flow(
    nodes: List[Dict],
    edges: List[Dict],
    purpose_field,
    detect_func
) -> StageResult:
    """
    Stage 7: EXECUTION FLOW
    Analyze execution flow and dead code.
    """
    start = time.time()

    try:
        exec_flow = detect_func(nodes, edges, purpose_field)
        flow_summary = exec_flow.summary()

        return StageResult(
            name="execution_flow",
            success=True,
            data={
                "exec_flow": exec_flow,
                "summary": flow_summary,
                "orphans": exec_flow.orphans if hasattr(exec_flow, 'orphans') else []
            },
            duration_ms=(time.time() - start) * 1000
        )
    except Exception as e:
        return StageResult(
            name="execution_flow",
            success=False,
            data={"exec_flow": None, "summary": {}, "orphans": []},
            error=str(e),
            duration_ms=(time.time() - start) * 1000
        )


def stage_performance(nodes: List[Dict], exec_flow, predict_func) -> StageResult:
    """
    Stage 8: PERFORMANCE PREDICTION
    Predict performance hotspots.
    """
    start = time.time()

    try:
        perf_profile = predict_func(nodes, exec_flow)
        perf_summary = perf_profile.summary()

        return StageResult(
            name="performance",
            success=True,
            data={
                "perf_profile": perf_profile,
                "summary": perf_summary,
                "hotspots": perf_profile.hotspots if hasattr(perf_profile, 'hotspots') else []
            },
            duration_ms=(time.time() - start) * 1000
        )
    except Exception as e:
        return StageResult(
            name="performance",
            success=False,
            data={"perf_profile": None, "summary": {}, "hotspots": []},
            error=str(e),
            duration_ms=(time.time() - start) * 1000
        )
