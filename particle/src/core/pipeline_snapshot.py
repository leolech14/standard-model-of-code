"""
Pipeline snapshot builder for Pipeline Navigator UI.

Converts observability data from PerformanceManager into the format
expected by pipeline-navigator.js.

Extracted from full_analysis.py during audit refactoring (2026-02-24).
"""
import re
from typing import Dict, List, Any


def build_pipeline_snapshot(perf_manager, nodes: List[Dict], edges: List[Dict], target_path: str) -> Dict[str, Any]:
    """
    Build pipeline_snapshot from PerformanceManager for Pipeline Navigator UI.

    Converts the observability data to the format expected by pipeline-navigator.js:
    - stages: array of stage snapshots with timing/status
    - total_duration_ms: total pipeline time
    - stages_succeeded/failed: counts
    - final_nodes/edges: final counts
    """
    perf_data = perf_manager.to_dict()

    def normalize_stage_name(name: str) -> str:
        """Convert 'Stage 1: Base Analysis' to 'stage_1'."""
        match = re.match(r'Stage\s+(\d+(?:\.\d+)?)', name)
        if match:
            num = match.group(1).replace('.', '_')
            return f'stage_{num}'
        return name.lower().replace(' ', '_').replace(':', '')

    stages = []
    for stage in perf_data.get('stages', []):
        stage_name = normalize_stage_name(stage.get('stage_name', ''))
        status = stage.get('status', 'OK')
        is_error = status == 'FAIL'
        is_skipped = status == 'SKIP'

        stage_snapshot = {
            'stage_name': stage_name,
            'stage_number': None,
            'duration_ms': stage.get('latency_ms', 0),
            'error': stage.get('error') if is_error else None,
            'skipped': is_skipped,
            'input_valid': True,
            'output_valid': not is_error,
            'nodes_before': 0,
            'nodes_after': 0,
            'edges_before': 0,
            'edges_after': 0,
            'nodes_added': 0,
            'nodes_removed': 0,
            'edges_added': 0,
            'edges_removed': 0,
            'fields_added': [],
            'metadata_keys_added': [],
            'sample_node_before': None,
            'sample_node_after': None,
        }
        stages.append(stage_snapshot)

    summary = perf_data.get('summary', {})

    return {
        'target_path': target_path,
        'started_at': None,
        'completed_at': None,
        'total_duration_ms': summary.get('total_latency_ms', 0),
        'stages': stages,
        'final_nodes': len(nodes),
        'final_edges': len(edges),
        'final_metadata_keys': [],
        'stages_succeeded': summary.get('ok_count', 0),
        'stages_failed': summary.get('fail_count', 0),
        'stages_skipped': 0,
    }
