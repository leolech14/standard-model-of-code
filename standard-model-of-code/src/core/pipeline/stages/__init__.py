"""
Pipeline Stages for Collider.

27 stages organized into 5 phases:

PHASE 1: EXTRACTION (Stages 0-2)
    0. SurveyStage - Pre-analysis intelligence
    1. BaseAnalysisStage - AST extraction
    2. StandardModelStage - Atom/Role classification

PHASE 2: ENRICHMENT (Stages 2.5-2.11)
    2.5. EcosystemDiscoveryStage - T2 ecosystem patterns
    2.7. DimensionClassificationStage - 8D coordinates
    2.8. ScopeAnalysisStage - Lexical scope
    2.9. ControlFlowStage - Complexity metrics
    2.10. PatternDetectionStage - Framework patterns
    2.11. DataFlowAnalysisStage - D6:EFFECT

PHASE 3: ANALYSIS (Stages 3-6.8)
    3. PurposeFieldStage - pi2 particle purpose
    3.5. OrganellePurposeStage - pi3 class purpose
    3.6. SystemPurposeStage - pi4 file purpose
    4. EdgeExtractionStage - Call relationships
    5. MarkovMatrixStage - Transition probabilities
    6. KnotDetectionStage - Cycles and tangles
    6.5. GraphAnalyticsStage - Degree, centrality
    6.6. StatisticalMetricsStage - Entropy, Halstead
    6.8. CodomeBoundaryStage - External callers

PHASE 4: INTELLIGENCE (Stages 7-8.6)
    7. DataFlowMacroStage - Sources and sinks
    8. PerformancePredictionStage - Hotspots
    8.5. ConstraintValidationStage - Architecture rules
    8.6. PurposeIntelligenceStage - Q-scores

PHASE 5: OUTPUT (Stages 9-12)
    9. RoadmapEvaluationStage - Roadmap alignment
    10. TopologyReasoningStage - Graph shape
    11. SemanticCortexStage - Concepts/themes
    11b. AIInsightsStage - LLM analysis
    12. OutputGenerationStage - JSON/HTML/MD
"""

# Phase 1: Extraction
from .stage_0_survey import SurveyStage
from .base_analysis import BaseAnalysisStage
from .standard_model import StandardModelStage

# Phase 2: Enrichment
from .ecosystem_discovery import EcosystemDiscoveryStage
from .dimension_classification import DimensionClassificationStage
from .scope_analysis import ScopeAnalysisStage
from .control_flow import ControlFlowStage
from .pattern_detection import PatternDetectionStage
from .data_flow_analysis import DataFlowAnalysisStage

# Phase 3: Analysis
from .purpose_field import PurposeFieldStage
from .organelle_purpose import OrganellePurposeStage
from .system_purpose import SystemPurposeStage
from .edge_extraction import EdgeExtractionStage
from .markov_matrix import MarkovMatrixStage
from .knot_detection import KnotDetectionStage
from .graph_analytics import GraphAnalyticsStage
from .statistical_metrics import StatisticalMetricsStage
from .codome_boundary import CodomeBoundaryStage

# Phase 4: Intelligence
from .data_flow_macro import DataFlowMacroStage
from .performance_prediction import PerformancePredictionStage
from .constraint_validation import ConstraintValidationStage
from .purpose_intelligence import PurposeIntelligenceStage

# Phase 5: Output
from .roadmap_evaluation import RoadmapEvaluationStage
from .topology_reasoning import TopologyReasoningStage
from .semantic_cortex import SemanticCortexStage
from .ai_insights import AIInsightsStage
from .output_generation import OutputGenerationStage


__all__ = [
    # Phase 1
    "SurveyStage",
    "BaseAnalysisStage",
    "StandardModelStage",
    # Phase 2
    "EcosystemDiscoveryStage",
    "DimensionClassificationStage",
    "ScopeAnalysisStage",
    "ControlFlowStage",
    "PatternDetectionStage",
    "DataFlowAnalysisStage",
    # Phase 3
    "PurposeFieldStage",
    "OrganellePurposeStage",
    "SystemPurposeStage",
    "EdgeExtractionStage",
    "MarkovMatrixStage",
    "KnotDetectionStage",
    "GraphAnalyticsStage",
    "StatisticalMetricsStage",
    "CodomeBoundaryStage",
    # Phase 4
    "DataFlowMacroStage",
    "PerformancePredictionStage",
    "ConstraintValidationStage",
    "PurposeIntelligenceStage",
    # Phase 5
    "RoadmapEvaluationStage",
    "TopologyReasoningStage",
    "SemanticCortexStage",
    "AIInsightsStage",
    "OutputGenerationStage",
]

# Stage execution order (27 stages)
STAGE_ORDER = [
    # Phase 1: Extraction
    "survey",
    "base_analysis",
    "standard_model",
    # Phase 2: Enrichment
    "ecosystem_discovery",
    "dimension_classification",
    "scope_analysis",
    "control_flow",
    "pattern_detection",
    "data_flow_analysis",
    # Phase 3: Analysis
    "purpose_field",
    "organelle_purpose",
    "system_purpose",
    "edge_extraction",
    "markov_matrix",
    "knot_detection",
    "graph_analytics",
    "statistical_metrics",
    "codome_boundary",
    # Phase 4: Intelligence
    "data_flow_macro",
    "performance_prediction",
    "constraint_validation",
    "purpose_intelligence",
    # Phase 5: Output
    "roadmap_evaluation",
    "topology_reasoning",
    "semantic_cortex",
    "ai_insights",
    "output_generation",
]
