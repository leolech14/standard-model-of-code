"""
Proof Package
=============

The Standard Model of Code proof pipeline.

This package provides a modular, stage-based approach to analyzing
codebases using the Standard Model classification system.

Usage:
    from proof import ProofPipeline

    pipeline = ProofPipeline("/path/to/code")
    result = pipeline.run()

Or use the legacy function:
    from proof import run_proof

    result = run_proof("/path/to/code")
"""

from .pipeline import ProofPipeline
from .document import ProofDocument, ProofDocumentBuilder
from .stages import (
    StageResult,
    stage_classification,
    stage_role_distribution,
    stage_antimatter,
    stage_predictions,
    stage_insights,
    stage_purpose_field,
    stage_execution_flow,
    stage_performance,
)
from .visualization import VisualizationGenerator, enrich_state_with_results


def run_proof(target_path: str, **kwargs) -> dict:
    """
    Legacy entry point for backward compatibility.

    Use ProofPipeline directly for more control.
    """
    pipeline = ProofPipeline(target_path)
    return pipeline.run(**kwargs)


__all__ = [
    # Main entry points
    'ProofPipeline',
    'run_proof',

    # Document building
    'ProofDocument',
    'ProofDocumentBuilder',

    # Individual stages
    'StageResult',
    'stage_classification',
    'stage_role_distribution',
    'stage_antimatter',
    'stage_predictions',
    'stage_insights',
    'stage_purpose_field',
    'stage_execution_flow',
    'stage_performance',

    # Visualization
    'VisualizationGenerator',
    'enrich_state_with_results',
]
