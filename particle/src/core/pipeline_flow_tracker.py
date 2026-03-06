"""Pipeline Data Flow Tracker — field-level lineage across stages.

Tracks which node/edge fields are born, updated, and emptied at each
pipeline stage.  Produces a JSON-serializable report that answers
cascade visibility questions like "why is field X empty at stage Y?"

Usage::

    tracker = PipelineFlowTracker()
    tracker.snapshot("After Stage 1", nodes, edges)
    tracker.snapshot("After Stage 2", nodes, edges)
    report = tracker.to_dict()
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Static dependency map: field -> stage that produces it
# ---------------------------------------------------------------------------

FIELD_PRODUCERS: Dict[str, str] = {
    "rpbl":                 "Stage 2: Standard Model Enrichment",
    "role":                 "Stage 2: Standard Model Enrichment",
    "ring":                 "Stage 2: Standard Model Enrichment",
    "atom":                 "Stage 2: Standard Model Enrichment",
    "atom_family":          "Stage 2: Standard Model Enrichment",
    "tier":                 "Stage 2: Standard Model Enrichment",
    "dimensions":           "Stage 2: Standard Model Enrichment",
    "rpbl_responsibility":  "Stage 2: Standard Model Enrichment",
    "rpbl_purity":          "Stage 2: Standard Model Enrichment",
    "rpbl_boundary":        "Stage 2: Standard Model Enrichment",
    "rpbl_lifecycle":       "Stage 2: Standard Model Enrichment",
    "level":                "Stage 2.6: Level Classification",
    "level_zone":           "Stage 2.6: Level Classification",
    "scope_analysis":       "Stage 2.8: Scope Analysis",
    "cyclomatic_complexity": "Stage 2.9: Control Flow Metrics",
    "control_flow":         "Stage 2.9: Control Flow Metrics",
    "detected_atoms":       "Stage 2.10: Pattern Detection",
    "data_flow":            "Stage 2.11: Data Flow Analysis",
    "D6_EFFECT":            "Stage 2.11: Data Flow Analysis",
    "purpose_vector":       "Stage 3: Purpose Field",
    "reachable_from_entry":  "Stage 4: Execution Flow",
    "community_id":         "Stage 6.5: Graph Analytics",
    "is_bridge":            "Stage 6.5: Graph Analytics",
    "is_coordinator":       "Stage 6.5: Graph Analytics",
    "is_influential":       "Stage 6.5: Graph Analytics",
    "weight":               "normalize_output",
}

# Field -> stages that consume (read) it.  Used for ordering warnings.
FIELD_CONSUMERS: Dict[str, List[str]] = {
    "role": [
        "Stage 5 (graph_inference inside unified_analysis)",
        "Stage 3: Purpose Field",
        "Stage 6.5: Graph Analytics",
    ],
    "rpbl": [
        "Stage 20: Data Chemistry",
        "Post-Stage 20: Color Encoding",
    ],
    "ring": [
        "Post-Stage 20: Color Encoding",
    ],
    "atom": [
        "Stage 13: Manifest Writer",
        "Stage 20: Data Chemistry",
    ],
    "community_id": [
        "Stage 20: Data Chemistry (node convergence)",
    ],
    "cyclomatic_complexity": [
        "Stage 6.6: Statistical Metrics",
    ],
}


@dataclass
class FieldEvent:
    """Record of a field's lifecycle change at a specific stage."""
    stage: str
    field: str
    action: str          # "born" | "grew" | "shrunk" | "emptied"
    sample_count: int    # how many nodes/edges have this field
    total_count: int     # total nodes/edges at this point
    entity: str          # "node" or "edge"


@dataclass
class FlowSnapshot:
    """Snapshot of node/edge field coverage at a pipeline checkpoint."""
    stage: str
    node_fields: Dict[str, int]
    edge_fields: Dict[str, int]
    node_count: int
    edge_count: int


def _count_fields(items: list) -> Dict[str, int]:
    """Count how many items have each field set (non-None, non-empty)."""
    counts: Dict[str, int] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        for key, value in item.items():
            if value is None:
                continue
            # Skip internal/large fields
            if key in ("body_source", "body_bytes", "_raw"):
                continue
            counts[key] = counts.get(key, 0) + 1
    return counts


class PipelineFlowTracker:
    """Tracks field births, deaths, and coverage across pipeline stages."""

    def __init__(self) -> None:
        self._snapshots: List[FlowSnapshot] = []
        self._events: List[FieldEvent] = []

    def snapshot(self, stage: str, nodes: list, edges: list) -> None:
        """Take a field-coverage snapshot and diff against previous."""
        node_fields = _count_fields(nodes)
        edge_fields = _count_fields(edges)

        snap = FlowSnapshot(
            stage=stage,
            node_fields=node_fields,
            edge_fields=edge_fields,
            node_count=len(nodes),
            edge_count=len(edges),
        )

        # Diff against previous snapshot
        if self._snapshots:
            prev = self._snapshots[-1]
            self._diff_fields(prev.node_fields, node_fields, len(nodes), stage, "node")
            self._diff_fields(prev.edge_fields, edge_fields, len(edges), stage, "edge")
        else:
            # First snapshot: every field is "born"
            for f, count in node_fields.items():
                self._events.append(FieldEvent(stage, f, "born", count, len(nodes), "node"))
            for f, count in edge_fields.items():
                self._events.append(FieldEvent(stage, f, "born", count, len(edges), "edge"))

        self._snapshots.append(snap)

    def _diff_fields(
        self,
        prev: Dict[str, int],
        curr: Dict[str, int],
        total: int,
        stage: str,
        entity: str,
    ) -> None:
        """Emit events for fields that changed between snapshots."""
        all_fields = set(prev) | set(curr)
        for f in all_fields:
            old_count = prev.get(f, 0)
            new_count = curr.get(f, 0)

            if old_count == 0 and new_count > 0:
                action = "born"
            elif old_count > 0 and new_count == 0:
                action = "emptied"
            elif new_count > old_count:
                action = "grew"
            elif new_count < old_count:
                action = "shrunk"
            else:
                continue  # no change

            self._events.append(FieldEvent(stage, f, action, new_count, total, entity))

    def get_ordering_warnings(self) -> List[str]:
        """Detect fields consumed before they are produced.

        Uses the static FIELD_PRODUCERS/FIELD_CONSUMERS maps and the
        actual snapshot timeline to flag ordering violations.
        """
        warnings: List[str] = []

        # Determine when each field was first born from snapshots
        field_birth_stage: Dict[str, str] = {}
        for event in self._events:
            if event.action == "born" and event.field not in field_birth_stage:
                field_birth_stage[event.field] = event.stage

        # Check known consumer->producer ordering issues
        for consumer_field, consumers in FIELD_CONSUMERS.items():
            producer_stage = FIELD_PRODUCERS.get(consumer_field)
            if not producer_stage:
                continue

            for consumer in consumers:
                # Special case: graph_inference runs INSIDE Stage 1,
                # before Stage 2 enrichment produces role/ring/rpbl
                if "inside unified_analysis" in consumer.lower():
                    if consumer_field in ("role", "ring", "rpbl", "atom"):
                        warnings.append(
                            f"{consumer} consumes '{consumer_field}' but it is "
                            f"produced by {producer_stage} — graph_inference runs "
                            f"INSIDE Stage 1 before Stage 2"
                        )

        # Check for fields that are still empty after their expected producer
        snapshot_stages = [s.stage for s in self._snapshots]
        for f, producer in FIELD_PRODUCERS.items():
            if f not in field_birth_stage and len(self._snapshots) >= 2:
                warnings.append(
                    f"Field '{f}' expected from {producer} but never appeared "
                    f"in {len(self._snapshots)} snapshots"
                )

        return warnings

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the full tracker state for JSON output."""
        # Compact snapshots: only include fields with interesting counts
        compact_snapshots = []
        for snap in self._snapshots:
            compact_snapshots.append({
                "stage": snap.stage,
                "node_count": snap.node_count,
                "edge_count": snap.edge_count,
                "node_fields": {k: v for k, v in sorted(snap.node_fields.items())
                                if v > 0 or k in FIELD_PRODUCERS},
                "edge_fields": {k: v for k, v in sorted(snap.edge_fields.items())
                                if v > 0 or k in FIELD_PRODUCERS},
            })

        # Compact events: group by stage, only show births/empties
        significant_events = [
            {
                "stage": e.stage,
                "field": e.field,
                "action": e.action,
                "count": e.sample_count,
                "total": e.total_count,
                "entity": e.entity,
            }
            for e in self._events
            if e.action in ("born", "emptied") or e.field in FIELD_PRODUCERS
        ]

        return {
            "snapshots": compact_snapshots,
            "field_events": significant_events,
            "ordering_warnings": self.get_ordering_warnings(),
            "total_snapshots": len(self._snapshots),
            "total_events": len(self._events),
        }
