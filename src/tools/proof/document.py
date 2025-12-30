"""
Proof Document Builder
======================

Builds the final proof document from stage results.
"""

from datetime import datetime
from typing import Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class ProofDocument:
    """The final proof document structure."""

    metadata: Dict[str, Any] = field(default_factory=dict)
    classification: Dict[str, Any] = field(default_factory=dict)
    antimatter: Dict[str, Any] = field(default_factory=dict)
    predictions: List[str] = field(default_factory=list)
    insights: Dict[str, Any] = field(default_factory=dict)
    purpose_field: Dict[str, Any] = field(default_factory=dict)
    execution_flow: Dict[str, Any] = field(default_factory=dict)
    performance: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "metadata": self.metadata,
            "classification": self.classification,
            "antimatter": self.antimatter,
            "predictions": self.predictions,
            "insights": self.insights,
            "purpose_field": self.purpose_field,
            "execution_flow": self.execution_flow,
            "performance": self.performance,
            "metrics": self.metrics
        }


class ProofDocumentBuilder:
    """Builder for constructing proof documents from stage results."""

    def __init__(self, target_path: str):
        self._target_path = target_path
        self._doc = ProofDocument()
        self._init_metadata()

    def _init_metadata(self):
        """Initialize metadata section."""
        self._doc.metadata = {
            "target": str(self._target_path),
            "timestamp": datetime.now().isoformat(),
            "version": "2.3.0",
            "model": "Standard Model of Code",
            "tool": "Collider",
            "pipeline_stages": 10
        }

    def with_classification(
        self,
        nodes: List[Dict],
        edges: List[Dict],
        role_counts: Dict[str, int],
        coverage: float,
        avg_confidence: float,
        classification_time: float
    ) -> 'ProofDocumentBuilder':
        """Add classification results."""
        self._doc.classification = {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "role_distribution": role_counts,
            "coverage_percent": round(coverage, 2),
            "average_confidence": round(avg_confidence, 2),
            "classification_time_seconds": round(classification_time, 2)
        }
        return self

    def with_antimatter(
        self,
        violations: List,
        violation_count: int
    ) -> 'ProofDocumentBuilder':
        """Add antimatter violation results."""
        violations_data = []
        for v in (violations or [])[:10]:
            if hasattr(v, 'law_name'):
                violations_data.append({
                    "law": v.law_name,
                    "particle": v.particle_name
                })

        self._doc.antimatter = {
            "violations_count": violation_count,
            "violations": violations_data
        }
        return self

    def with_predictions(self, predictions: List[str]) -> 'ProofDocumentBuilder':
        """Add prediction results."""
        self._doc.predictions = predictions or []
        return self

    def with_insights(
        self,
        insights_count: int,
        insights_summary: List[Dict]
    ) -> 'ProofDocumentBuilder':
        """Add insights results."""
        self._doc.insights = {
            "count": insights_count,
            "items": insights_summary or []
        }
        return self

    def with_purpose_field(
        self,
        field_summary: Dict,
        violations: List
    ) -> 'ProofDocumentBuilder':
        """Add purpose field results."""
        self._doc.purpose_field = {
            "layers": field_summary.get('layers', {}),
            "layer_purposes": field_summary.get('layer_purposes', {}),
            "violations_count": len(violations) if violations else 0,
            "violations": (violations or [])[:5]
        }
        return self

    def with_execution_flow(
        self,
        flow_summary: Dict,
        orphans: List[str]
    ) -> 'ProofDocumentBuilder':
        """Add execution flow results."""
        self._doc.execution_flow = {
            "entry_points": flow_summary.get('entry_points', 0) if flow_summary else 0,
            "reachable_nodes": flow_summary.get('reachable_nodes', 0) if flow_summary else 0,
            "orphan_count": flow_summary.get('orphan_count', 0) if flow_summary else 0,
            "dead_code_percent": flow_summary.get('dead_code_percent', 0) if flow_summary else 0,
            "chains_count": flow_summary.get('chains_count', 0) if flow_summary else 0,
            "orphans": (orphans or [])[:10]
        }
        return self

    def with_performance(
        self,
        perf_summary: Dict,
        hotspots: List[str]
    ) -> 'ProofDocumentBuilder':
        """Add performance prediction results."""
        self._doc.performance = {
            "total_estimated_cost": perf_summary.get('total_estimated_cost', 0) if perf_summary else 0,
            "critical_path_cost": perf_summary.get('critical_path_cost', 0) if perf_summary else 0,
            "critical_path_length": perf_summary.get('critical_path_length', 0) if perf_summary else 0,
            "hotspot_count": perf_summary.get('hotspot_count', 0) if perf_summary else 0,
            "time_by_type": perf_summary.get('time_by_type', {}) if perf_summary else {},
            "hotspots": (hotspots or [])[:5]
        }
        return self

    def with_metrics(
        self,
        entities: int,
        repositories: int,
        services: int,
        controllers: int,
        tests: int
    ) -> 'ProofDocumentBuilder':
        """Add summary metrics."""
        self._doc.metrics = {
            "entities": entities,
            "repositories": repositories,
            "services": services,
            "controllers": controllers,
            "tests": tests
        }
        return self

    def build(self) -> ProofDocument:
        """Build and return the final proof document."""
        return self._doc
