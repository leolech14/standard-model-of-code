"""
Tests for pipeline stage validate_output() implementations.

Verifies that each stage's validate_output() correctly distinguishes:
- Valid post-execution state (stage ran and produced expected data)
- Invalid post-execution state (stage failed silently / missing data)

Covers all 12 stages with validate_output() overrides:
  Pre-existing: base_analysis, standard_model
  Added in W4.5: edge_extraction, purpose_field, graph_analytics,
    statistical_metrics, pattern_detection, purpose_intelligence,
    topology_reasoning, scope_analysis, igt_metrics, dimension_classification
"""
import sys
import os

import pytest

# Add src/core to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'core'))

from data_management import CodebaseState

# Import all 12 stages that implement validate_output()
from pipeline.stages.base_analysis import BaseAnalysisStage
from pipeline.stages.standard_model import StandardModelStage
from pipeline.stages.edge_extraction import EdgeExtractionStage
from pipeline.stages.purpose_field import PurposeFieldStage
from pipeline.stages.graph_analytics import GraphAnalyticsStage
from pipeline.stages.statistical_metrics import StatisticalMetricsStage
from pipeline.stages.pattern_detection import PatternDetectionStage
from pipeline.stages.purpose_intelligence import PurposeIntelligenceStage
from pipeline.stages.topology_reasoning import TopologyReasoningStage
from pipeline.stages.scope_analysis import ScopeAnalysisStage
from pipeline.stages.igt_metrics import IGTMetricsStage
from pipeline.stages.dimension_classification import DimensionClassificationStage


# =============================================================================
# FIXTURES
# =============================================================================

def _empty_state() -> CodebaseState:
    """Create an empty CodebaseState (no nodes, no edges, no metadata)."""
    return CodebaseState("/tmp/test_validation")


def _state_with_nodes(count: int = 3, **extra_node_keys) -> CodebaseState:
    """Create a state with N minimal nodes."""
    state = _empty_state()
    for i in range(count):
        node = {
            'id': f'node_{i}',
            'name': f'func_{i}',
            'type': 'function',
            'file': f'/tmp/test/mod_{i}.py',
        }
        node.update(extra_node_keys)
        state.nodes[f'node_{i}'] = node
    return state


def _state_with_edges(node_count: int = 3) -> CodebaseState:
    """Create a state with nodes AND edges."""
    state = _state_with_nodes(node_count)
    for i in range(node_count - 1):
        state.edges.append({
            'source': f'node_{i}',
            'target': f'node_{i+1}',
            'type': 'calls',
        })
    return state


# =============================================================================
# Stage 1: BaseAnalysisStage — validates len(state.nodes) > 0
# =============================================================================

class TestBaseAnalysisValidation:
    """BaseAnalysis: validate_output checks that nodes were extracted."""

    def setup_method(self):
        self.stage = BaseAnalysisStage()

    def test_valid_with_nodes(self):
        state = _state_with_nodes(3)
        assert self.stage.validate_output(state) is True

    def test_invalid_empty_nodes(self):
        state = _empty_state()
        assert self.stage.validate_output(state) is False

    def test_valid_with_single_node(self):
        state = _state_with_nodes(1)
        assert self.stage.validate_output(state) is True


# =============================================================================
# Stage 2: StandardModelStage — validates rpbl count > 0
# =============================================================================

class TestStandardModelValidation:
    """StandardModel: validate_output checks that nodes have rpbl enrichment."""

    def setup_method(self):
        self.stage = StandardModelStage()

    def test_valid_with_rpbl(self):
        state = _state_with_nodes(3)
        state.nodes['node_0']['rpbl'] = {'role': 'data', 'pattern': 'none',
                                          'boundary': 'internal', 'layer': 'core'}
        assert self.stage.validate_output(state) is True

    def test_invalid_no_rpbl(self):
        state = _state_with_nodes(3)
        # Nodes exist but none have rpbl
        assert self.stage.validate_output(state) is False

    def test_invalid_empty_nodes(self):
        state = _empty_state()
        assert self.stage.validate_output(state) is False


# =============================================================================
# Stage 4: EdgeExtractionStage — validates len(state.edges) > 0
# =============================================================================

class TestEdgeExtractionValidation:
    """EdgeExtraction: validate_output checks that edges were extracted."""

    def setup_method(self):
        self.stage = EdgeExtractionStage()

    def test_valid_with_edges(self):
        state = _state_with_edges(3)
        assert self.stage.validate_output(state) is True

    def test_invalid_no_edges(self):
        state = _state_with_nodes(3)
        assert self.stage.validate_output(state) is False

    def test_invalid_empty_state(self):
        state = _empty_state()
        assert self.stage.validate_output(state) is False


# =============================================================================
# Stage 3: PurposeFieldStage — validates per-node purpose + metadata key
# =============================================================================

class TestPurposeFieldValidation:
    """PurposeField: validate_output checks purpose on nodes AND metadata key."""

    def setup_method(self):
        self.stage = PurposeFieldStage()

    def test_valid_with_purpose(self):
        state = _state_with_nodes(3)
        state.nodes['node_0']['purpose'] = 'data_transformation'
        state.nodes['node_0']['purpose_confidence'] = 0.85
        state.metadata['purpose_field'] = {'scored_nodes': 1}
        assert self.stage.validate_output(state) is True

    def test_invalid_no_purpose_on_nodes(self):
        state = _state_with_nodes(3)
        state.metadata['purpose_field'] = {'scored_nodes': 0}
        # Metadata present but no node has 'purpose' key
        assert self.stage.validate_output(state) is False

    def test_invalid_no_metadata_key(self):
        state = _state_with_nodes(3)
        state.nodes['node_0']['purpose'] = 'data_transformation'
        # Node has purpose but metadata key missing
        assert self.stage.validate_output(state) is False

    def test_invalid_both_missing(self):
        state = _state_with_nodes(3)
        assert self.stage.validate_output(state) is False


# =============================================================================
# Stage 6.5: GraphAnalyticsStage — validates metadata dict with total_nodes > 0
# =============================================================================

class TestGraphAnalyticsValidation:
    """GraphAnalytics: validate_output checks graph_analytics metadata."""

    def setup_method(self):
        self.stage = GraphAnalyticsStage()

    def test_valid_with_analytics(self):
        state = _state_with_edges(3)
        state.metadata['graph_analytics'] = {
            'total_nodes': 3,
            'total_edges': 2,
            'orphan_nodes': 0,
            'hub_nodes': 1,
            'avg_degree': 1.33,
        }
        assert self.stage.validate_output(state) is True

    def test_invalid_missing_metadata(self):
        state = _state_with_edges(3)
        # No graph_analytics in metadata
        assert self.stage.validate_output(state) is False

    def test_invalid_not_a_dict(self):
        state = _state_with_edges(3)
        state.metadata['graph_analytics'] = "not a dict"
        assert self.stage.validate_output(state) is False

    def test_invalid_zero_nodes(self):
        state = _state_with_edges(3)
        state.metadata['graph_analytics'] = {'total_nodes': 0, 'total_edges': 0}
        assert self.stage.validate_output(state) is False


# =============================================================================
# Stage 6.6: StatisticalMetricsStage — validates stats is non-empty dict
# =============================================================================

class TestStatisticalMetricsValidation:
    """StatisticalMetrics: validate_output checks stats metadata exists."""

    def setup_method(self):
        self.stage = StatisticalMetricsStage()

    def test_valid_with_stats(self):
        state = _state_with_nodes(3)
        state.metadata['stats'] = {
            'avg_complexity': 3.2,
            'max_complexity': 12,
            'entropy': 0.87,
        }
        assert self.stage.validate_output(state) is True

    def test_invalid_missing_stats(self):
        state = _state_with_nodes(3)
        assert self.stage.validate_output(state) is False

    def test_invalid_empty_dict(self):
        state = _state_with_nodes(3)
        state.metadata['stats'] = {}
        assert self.stage.validate_output(state) is False

    def test_invalid_not_a_dict(self):
        state = _state_with_nodes(3)
        state.metadata['stats'] = [1, 2, 3]
        assert self.stage.validate_output(state) is False


# =============================================================================
# Stage 2.10: PatternDetectionStage — validates patterns dict with 'counts' key
# =============================================================================

class TestPatternDetectionValidation:
    """PatternDetection: validate_output checks patterns.counts exists."""

    def setup_method(self):
        self.stage = PatternDetectionStage()

    def test_valid_with_patterns(self):
        state = _state_with_nodes(3)
        state.metadata['patterns'] = {
            'counts': {'decorator': 5, 'factory': 2, 'singleton': 1},
            'total': 8,
        }
        assert self.stage.validate_output(state) is True

    def test_invalid_missing_patterns(self):
        state = _state_with_nodes(3)
        assert self.stage.validate_output(state) is False

    def test_invalid_no_counts_key(self):
        state = _state_with_nodes(3)
        state.metadata['patterns'] = {'total': 5}
        assert self.stage.validate_output(state) is False

    def test_invalid_not_a_dict(self):
        state = _state_with_nodes(3)
        state.metadata['patterns'] = 42
        assert self.stage.validate_output(state) is False


# =============================================================================
# Stage 8.6: PurposeIntelligenceStage — validates intelligence.avg_q_score
# =============================================================================

class TestPurposeIntelligenceValidation:
    """PurposeIntelligence: validate_output checks intelligence.avg_q_score."""

    def setup_method(self):
        self.stage = PurposeIntelligenceStage()

    def test_valid_with_intelligence(self):
        state = _state_with_nodes(3)
        state.metadata['intelligence'] = {
            'avg_q_score': 0.72,
            'total_scored': 3,
        }
        assert self.stage.validate_output(state) is True

    def test_invalid_missing_intelligence(self):
        state = _state_with_nodes(3)
        assert self.stage.validate_output(state) is False

    def test_invalid_no_q_score_key(self):
        state = _state_with_nodes(3)
        state.metadata['intelligence'] = {'total_scored': 3}
        assert self.stage.validate_output(state) is False

    def test_invalid_not_a_dict(self):
        state = _state_with_nodes(3)
        state.metadata['intelligence'] = None
        assert self.stage.validate_output(state) is False


# =============================================================================
# Stage 10: TopologyReasoningStage — validates topology.shape
# =============================================================================

class TestTopologyReasoningValidation:
    """TopologyReasoning: validate_output checks topology.shape exists."""

    def setup_method(self):
        self.stage = TopologyReasoningStage()

    def test_valid_with_topology(self):
        state = _state_with_nodes(3)
        state.metadata['topology'] = {
            'shape': 'star',
            'confidence': 0.85,
        }
        assert self.stage.validate_output(state) is True

    def test_invalid_missing_topology(self):
        state = _state_with_nodes(3)
        assert self.stage.validate_output(state) is False

    def test_invalid_no_shape_key(self):
        state = _state_with_nodes(3)
        state.metadata['topology'] = {'confidence': 0.85}
        assert self.stage.validate_output(state) is False

    def test_invalid_not_a_dict(self):
        state = _state_with_nodes(3)
        state.metadata['topology'] = "star"
        assert self.stage.validate_output(state) is False


# =============================================================================
# Stage 2.8: ScopeAnalysisStage — validates scope_analysis.analyzed_nodes > 0
# =============================================================================

class TestScopeAnalysisValidation:
    """ScopeAnalysis: validate_output checks scope_analysis.analyzed_nodes > 0."""

    def setup_method(self):
        self.stage = ScopeAnalysisStage()

    def test_valid_with_scope(self):
        state = _state_with_nodes(3)
        state.metadata['scope_analysis'] = {
            'analyzed_nodes': 3,
            'unused_definitions': 1,
        }
        assert self.stage.validate_output(state) is True

    def test_invalid_missing_scope(self):
        state = _state_with_nodes(3)
        assert self.stage.validate_output(state) is False

    def test_invalid_zero_analyzed(self):
        state = _state_with_nodes(3)
        state.metadata['scope_analysis'] = {
            'analyzed_nodes': 0,
            'unused_definitions': 0,
        }
        assert self.stage.validate_output(state) is False

    def test_invalid_not_a_dict(self):
        state = _state_with_nodes(3)
        state.metadata['scope_analysis'] = []
        assert self.stage.validate_output(state) is False


# =============================================================================
# Stage 14: IGTMetricsStage — validates igt_metrics is dict WITHOUT 'error'
# =============================================================================

class TestIGTMetricsValidation:
    """IGTMetrics: validate_output checks igt_metrics exists and has no error."""

    def setup_method(self):
        self.stage = IGTMetricsStage()

    def test_valid_with_metrics(self):
        state = _state_with_nodes(3)
        state.metadata['igt_metrics'] = {
            'graph_entropy': 2.31,
            'information_density': 0.78,
        }
        assert self.stage.validate_output(state) is True

    def test_invalid_missing_metrics(self):
        state = _state_with_nodes(3)
        assert self.stage.validate_output(state) is False

    def test_invalid_error_present(self):
        """Stage sets {'error': str(e)} on failure — must detect this."""
        state = _state_with_nodes(3)
        state.metadata['igt_metrics'] = {'error': 'No module named igt_core'}
        assert self.stage.validate_output(state) is False

    def test_invalid_not_a_dict(self):
        state = _state_with_nodes(3)
        state.metadata['igt_metrics'] = "crashed"
        assert self.stage.validate_output(state) is False

    def test_valid_empty_but_no_error(self):
        """An empty dict with no 'error' key is technically valid."""
        state = _state_with_nodes(3)
        state.metadata['igt_metrics'] = {}
        assert self.stage.validate_output(state) is True


# =============================================================================
# Stage 2.7: DimensionClassificationStage — validates per-node d4_boundary
# =============================================================================

class TestDimensionClassificationValidation:
    """DimensionClassification: validate_output checks d4_boundary on nodes."""

    def setup_method(self):
        self.stage = DimensionClassificationStage()

    def test_valid_with_dimensions(self):
        state = _state_with_nodes(3)
        state.nodes['node_0']['d4_boundary'] = 'internal'
        state.nodes['node_0']['d5_state'] = 'stateless'
        state.nodes['node_0']['d7_time'] = 'synchronous'
        assert self.stage.validate_output(state) is True

    def test_invalid_no_dimensions(self):
        state = _state_with_nodes(3)
        # No node has d4_boundary
        assert self.stage.validate_output(state) is False

    def test_invalid_empty_nodes(self):
        state = _empty_state()
        assert self.stage.validate_output(state) is False

    def test_valid_partial_dimensions(self):
        """Even if only one node has d4_boundary, it's valid."""
        state = _state_with_nodes(5)
        state.nodes['node_2']['d4_boundary'] = 'external'
        assert self.stage.validate_output(state) is True
