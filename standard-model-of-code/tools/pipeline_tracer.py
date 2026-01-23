#!/usr/bin/env python3
"""
Pipeline Tracer - Maps the "domino effect" of running Collider.

Traces exactly which stages run, what they touch, and the data flow.
Used to validate the pipeline execution sequence.

Usage:
    python tools/pipeline_tracer.py [target_path] [--full]
"""

import sys
import json
import time
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add src/core to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src' / 'core'))


@dataclass
class StageTrace:
    """Trace of a single stage execution."""
    name: str
    stage_number: Optional[int]
    started_at: float
    completed_at: Optional[float] = None
    duration_ms: Optional[float] = None
    input_validation: Optional[bool] = None
    output_validation: Optional[bool] = None
    nodes_before: int = 0
    nodes_after: int = 0
    edges_before: int = 0
    edges_after: int = 0
    metadata_keys_added: List[str] = field(default_factory=list)
    error: Optional[str] = None
    skipped: bool = False


@dataclass
class PipelineTrace:
    """Complete trace of pipeline execution."""
    target_path: str
    started_at: str
    completed_at: Optional[str] = None
    total_duration_ms: Optional[float] = None
    stages: List[StageTrace] = field(default_factory=list)
    final_nodes: int = 0
    final_edges: int = 0
    final_metadata_keys: List[str] = field(default_factory=list)


class TracingPipelineManager:
    """Pipeline manager with built-in tracing."""

    def __init__(self, stages, trace: PipelineTrace):
        self.stages = stages
        self.trace = trace

    def run(self, state):
        """Run pipeline with tracing."""
        from data_management import CodebaseState

        for stage in self.stages:
            stage_trace = StageTrace(
                name=stage.name,
                stage_number=getattr(stage, 'stage_number', None),
                started_at=time.perf_counter(),
                nodes_before=len(state.nodes),
                edges_before=len(state.edges),
            )

            metadata_before = set(state.metadata.keys())

            try:
                # Validate input
                stage_trace.input_validation = stage.validate_input(state)
                if not stage_trace.input_validation:
                    stage_trace.skipped = True
                    stage_trace.completed_at = time.perf_counter()
                    stage_trace.duration_ms = (stage_trace.completed_at - stage_trace.started_at) * 1000
                    self.trace.stages.append(stage_trace)
                    print(f"  SKIP  {stage.name} (input validation failed)")
                    continue

                # Execute
                print(f"  RUN   {stage.name}...", end=' ', flush=True)
                state = stage.execute(state)

                # Validate output
                stage_trace.output_validation = stage.validate_output(state)

                stage_trace.completed_at = time.perf_counter()
                stage_trace.duration_ms = (stage_trace.completed_at - stage_trace.started_at) * 1000
                stage_trace.nodes_after = len(state.nodes)
                stage_trace.edges_after = len(state.edges)

                # Track new metadata keys
                metadata_after = set(state.metadata.keys())
                stage_trace.metadata_keys_added = list(metadata_after - metadata_before)

                print(f"done ({stage_trace.duration_ms:.0f}ms)")

            except Exception as e:
                stage_trace.error = str(e)
                stage_trace.completed_at = time.perf_counter()
                stage_trace.duration_ms = (stage_trace.completed_at - stage_trace.started_at) * 1000
                print(f"ERROR: {e}")

            self.trace.stages.append(stage_trace)

        return state


def trace_pipeline(target_path: str, full: bool = False) -> PipelineTrace:
    """
    Trace pipeline execution on a target path.

    Args:
        target_path: Path to analyze
        full: If True, run full 27-stage pipeline; else run 5-stage default

    Returns:
        PipelineTrace with complete execution trace
    """
    from pipeline import create_default_pipeline, create_full_pipeline, STAGE_ORDER
    from data_management import CodebaseState

    trace = PipelineTrace(
        target_path=str(target_path),
        started_at=datetime.now().isoformat(),
    )

    start_time = time.perf_counter()

    print(f"\n{'='*60}")
    print(f"PIPELINE TRACER - Domino Effect Mapper")
    print(f"{'='*60}")
    print(f"Target: {target_path}")
    print(f"Mode: {'FULL (27 stages)' if full else 'DEFAULT (5 stages)'}")
    print(f"{'='*60}\n")

    # Create pipeline
    if full:
        pipeline = create_full_pipeline(skip_ai=True)
    else:
        pipeline = create_default_pipeline()

    print(f"Stages to execute: {len(pipeline.stages)}")
    for i, s in enumerate(pipeline.stages, 1):
        print(f"  {i:2}. {s.name}")
    print()

    # Create tracing manager
    tracing_manager = TracingPipelineManager(pipeline.stages, trace)

    # Initialize state
    state = CodebaseState(target_path)

    # Run with tracing
    print("Execution:")
    print("-" * 40)
    final_state = tracing_manager.run(state)
    print("-" * 40)

    # Finalize trace
    trace.completed_at = datetime.now().isoformat()
    trace.total_duration_ms = (time.perf_counter() - start_time) * 1000
    trace.final_nodes = len(final_state.nodes)
    trace.final_edges = len(final_state.edges)
    trace.final_metadata_keys = list(final_state.metadata.keys())

    return trace


def print_trace_summary(trace: PipelineTrace):
    """Print a summary of the pipeline trace."""
    print(f"\n{'='*60}")
    print("TRACE SUMMARY")
    print(f"{'='*60}")

    print(f"\nTotal Duration: {trace.total_duration_ms:.0f}ms")
    print(f"Final Nodes: {trace.final_nodes}")
    print(f"Final Edges: {trace.final_edges}")
    print(f"Metadata Keys: {len(trace.final_metadata_keys)}")

    print(f"\n{'Stage':<30} {'Duration':>10} {'Nodes':>10} {'Edges':>10} {'Status':>10}")
    print("-" * 70)

    for st in trace.stages:
        status = "SKIP" if st.skipped else ("ERROR" if st.error else "OK")
        nodes_delta = st.nodes_after - st.nodes_before
        edges_delta = st.edges_after - st.edges_before

        nodes_str = f"+{nodes_delta}" if nodes_delta > 0 else str(nodes_delta) if nodes_delta < 0 else "="
        edges_str = f"+{edges_delta}" if edges_delta > 0 else str(edges_delta) if edges_delta < 0 else "="

        print(f"{st.name:<30} {st.duration_ms:>8.0f}ms {nodes_str:>10} {edges_str:>10} {status:>10}")

    print("-" * 70)

    # Print metadata flow
    print("\nMetadata Flow (what each stage adds):")
    for st in trace.stages:
        if st.metadata_keys_added:
            print(f"  {st.name}: {', '.join(st.metadata_keys_added)}")

    # Print domino sequence
    print("\nDomino Sequence (execution order with dependencies):")
    for i, st in enumerate(trace.stages, 1):
        arrow = "→" if i < len(trace.stages) else "◆"
        status = "[SKIP]" if st.skipped else "[ERR]" if st.error else ""
        print(f"  {i:2}. {st.name} {status} {arrow}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Trace Collider pipeline execution")
    parser.add_argument("target", nargs="?", default=".", help="Path to analyze")
    parser.add_argument("--full", action="store_true", help="Run full 27-stage pipeline")
    parser.add_argument("--json", action="store_true", help="Output JSON trace")
    parser.add_argument("--output", "-o", help="Output file for JSON trace")

    args = parser.parse_args()

    target = Path(args.target).resolve()
    if not target.exists():
        print(f"Error: {target} does not exist")
        sys.exit(1)

    trace = trace_pipeline(str(target), full=args.full)

    if args.json or args.output:
        trace_dict = asdict(trace)
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(trace_dict, f, indent=2)
            print(f"\nTrace saved to: {args.output}")
        else:
            print(json.dumps(trace_dict, indent=2))
    else:
        print_trace_summary(trace)


if __name__ == "__main__":
    main()
