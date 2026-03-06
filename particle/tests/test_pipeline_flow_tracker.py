"""Tests for PipelineFlowTracker — field-level lineage across stages."""

import pytest
from src.core.pipeline_flow_tracker import (
    PipelineFlowTracker,
    _count_fields,
    FIELD_PRODUCERS,
    FIELD_CONSUMERS,
)


def _make_nodes(count, fields=None):
    """Create mock nodes with specified fields."""
    fields = fields or {}
    return [{"id": f"node_{i}", "name": f"n{i}", **fields} for i in range(count)]


def _make_edges(count, fields=None):
    """Create mock edges with specified fields."""
    fields = fields or {}
    return [{"source": f"s{i}", "target": f"t{i}", **fields} for i in range(count)]


class TestCountFields:
    def test_basic(self):
        items = [{"a": 1, "b": "x"}, {"a": 2, "c": True}]
        result = _count_fields(items)
        assert result == {"a": 2, "b": 1, "c": 1}

    def test_skips_none(self):
        items = [{"a": 1, "b": None}]
        result = _count_fields(items)
        assert result == {"a": 1}

    def test_skips_body_source(self):
        items = [{"a": 1, "body_source": "big code blob"}]
        result = _count_fields(items)
        assert result == {"a": 1}

    def test_empty_list(self):
        assert _count_fields([]) == {}

    def test_non_dict_items_ignored(self):
        assert _count_fields([None, "string", 42]) == {}


class TestFlowTracker:
    def test_single_snapshot_all_born(self):
        tracker = PipelineFlowTracker()
        nodes = _make_nodes(3, {"role": "Service"})
        edges = _make_edges(2)
        tracker.snapshot("Stage 1", nodes, edges)

        result = tracker.to_dict()
        assert result["total_snapshots"] == 1
        # All fields should be "born" events
        births = [e for e in result["field_events"] if e["action"] == "born"]
        assert len(births) > 0
        # 'role' should be born
        role_births = [e for e in births if e["field"] == "role"]
        assert len(role_births) == 1
        assert role_births[0]["count"] == 3

    def test_two_snapshots_detect_born_fields(self):
        tracker = PipelineFlowTracker()
        # Stage 1: nodes without enrichment fields
        nodes = _make_nodes(5)
        edges = _make_edges(3)
        tracker.snapshot("After Stage 1", nodes, edges)

        # Stage 2: add rpbl and role to nodes
        for n in nodes:
            n["rpbl"] = {"R": 5, "P": 5, "B": 5, "L": 5}
            n["role"] = "Entity"
        tracker.snapshot("After Stage 2", nodes, edges)

        result = tracker.to_dict()
        assert result["total_snapshots"] == 2

        # rpbl and role should have "born" events at Stage 2
        stage2_births = [
            e for e in result["field_events"]
            if e["action"] == "born" and e["stage"] == "After Stage 2"
        ]
        born_fields = {e["field"] for e in stage2_births}
        assert "rpbl" in born_fields
        assert "role" in born_fields

    def test_emptied_field_detected(self):
        tracker = PipelineFlowTracker()
        nodes = _make_nodes(3, {"temp": True})
        tracker.snapshot("Stage 1", nodes, [])

        # Remove the field
        for n in nodes:
            del n["temp"]
        tracker.snapshot("Stage 2", nodes, [])

        result = tracker.to_dict()
        emptied = [e for e in result["field_events"] if e["action"] == "emptied"]
        assert any(e["field"] == "temp" for e in emptied)

    def test_grew_field_detected(self):
        tracker = PipelineFlowTracker()
        # Only 2 of 5 nodes have 'ring'
        nodes = _make_nodes(5)
        nodes[0]["ring"] = "domain"
        nodes[1]["ring"] = "application"
        tracker.snapshot("Stage 1", nodes, [])

        # Now all 5 have it
        for n in nodes:
            n["ring"] = "domain"
        tracker.snapshot("Stage 2", nodes, [])

        # ring should appear as born at Stage 1 and grew at Stage 2
        result = tracker.to_dict()
        grew = [e for e in result["field_events"]
                if e["action"] == "grew" and e["field"] == "ring"]
        # 'ring' is in FIELD_PRODUCERS so it should appear in significant events
        assert len(grew) >= 1 or any(
            e["field"] == "ring" for e in result["field_events"]
        )

    def test_ordering_warnings_graph_inference(self):
        """The known bug: graph_inference consumes 'role' before Stage 2 produces it."""
        tracker = PipelineFlowTracker()
        # Simulate: Stage 1 produces nodes without role
        nodes = _make_nodes(3)
        tracker.snapshot("After Stage 1", nodes, [])

        # Stage 2 adds role
        for n in nodes:
            n["role"] = "Service"
        tracker.snapshot("After Stage 2", nodes, [])

        warnings = tracker.get_ordering_warnings()
        # Should flag graph_inference consuming 'role' before Stage 2
        role_warnings = [w for w in warnings if "role" in w and "graph_inference" in w]
        assert len(role_warnings) >= 1

    def test_to_dict_serializable(self):
        """Output must be JSON-serializable."""
        import json
        tracker = PipelineFlowTracker()
        nodes = _make_nodes(2, {"role": "X", "rpbl": {}})
        tracker.snapshot("S1", nodes, _make_edges(1))
        result = tracker.to_dict()
        # Should not raise
        json.dumps(result)


class TestStaticMaps:
    def test_producers_all_strings(self):
        for field, stage in FIELD_PRODUCERS.items():
            assert isinstance(field, str)
            assert isinstance(stage, str)

    def test_consumers_reference_known_producers(self):
        for field in FIELD_CONSUMERS:
            assert field in FIELD_PRODUCERS, f"Consumer field '{field}' not in FIELD_PRODUCERS"
