"""Integration tests for end-to-end default Collider pipeline execution."""

import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

# Support legacy absolute imports used by core modules (e.g., `import unified_analysis`).
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "core"))

from src.core.data_management import CodebaseState
from src.core.pipeline import create_default_pipeline


class _PurposeNode:
    def __init__(self, purpose: str, confidence: float, coherence: float):
        self.atomic_purpose = purpose
        self.atomic_confidence = confidence
        self.coherence_score = coherence


class _PurposeField:
    def __init__(self, node_ids):
        self.nodes = {
            node_id: _PurposeNode("Process", 0.88, 0.73)
            for node_id in node_ids
        }

    def summary(self):
        return {
            "coverage": 1.0,
            "coherence": 0.73,
            "god_class_count": 0,
        }


def test_default_pipeline_end_to_end_with_stubs(monkeypatch, tmp_path):
    target = tmp_path / "app.py"
    target.write_text("def foo():\n    return helper()\n")

    foo_id = f"{target}::foo"
    helper_id = f"{target}::helper"

    base_nodes = [
        {
            "id": foo_id,
            "name": "foo",
            "file_path": str(target),
            "kind": "function",
            "body_source": "helper()",
            "line": 1,
        },
        {
            "id": helper_id,
            "name": "helper",
            "file_path": str(target),
            "kind": "function",
            "body_source": "return 1",
            "line": 2,
        },
    ]
    base_edges = [
        {
            "source": foo_id,
            "target": helper_id,
            "edge_type": "calls",
            "family": "Dependency",
            "confidence": 1.0,
        }
    ]

    def fake_analyze(*args, **kwargs):
        return SimpleNamespace(
            nodes=[dict(node) for node in base_nodes],
            edges=[dict(edge) for edge in base_edges],
            stats={"files_analyzed": 1},
            classification={"ok": True},
            auto_discovery={"enabled": True},
            dependencies={"count": 1},
            architecture={"shape": "toy"},
        )

    def fake_enrich(nodes):
        enriched = []
        for node in nodes:
            node_copy = dict(node)
            node_copy["atom"] = "LOG.FNC.M"
            node_copy["role"] = "Service"
            node_copy["rpbl"] = {
                "responsibility": 0.8,
                "purity": 0.7,
                "boundary": 0.9,
                "lifecycle": 0.6,
            }
            enriched.append(node_copy)
        return enriched

    def fake_detect_purpose_field(nodes, edges):
        return _PurposeField([node["id"] for node in nodes])

    def fake_extract_call_edges(nodes, edges):
        return [
            {
                "source": helper_id,
                "target": foo_id,
                "edge_type": "calls",
                "family": "Dependency",
                "file_path": str(target),
                "line": 2,
                "confidence": 0.95,
            }
        ]

    unified_analysis = ModuleType("unified_analysis")
    unified_analysis.analyze = fake_analyze
    monkeypatch.setitem(sys.modules, "unified_analysis", unified_analysis)

    standard_model_enricher = ModuleType("standard_model_enricher")
    standard_model_enricher.enrich_with_standard_model = fake_enrich
    monkeypatch.setitem(sys.modules, "standard_model_enricher", standard_model_enricher)

    purpose_field = ModuleType("purpose_field")
    purpose_field.detect_purpose_field = fake_detect_purpose_field
    monkeypatch.setitem(sys.modules, "purpose_field", purpose_field)

    edge_extractor = ModuleType("edge_extractor")
    edge_extractor.extract_call_edges = fake_extract_call_edges
    monkeypatch.setitem(sys.modules, "edge_extractor", edge_extractor)

    state = CodebaseState(str(target))
    pipeline = create_default_pipeline()
    final_state = pipeline.run(state)

    assert pipeline.list_stages() == [
        "base_analysis",
        "standard_model",
        "purpose_field",
        "edge_extraction",
        "graph_analytics",
    ]

    assert len(final_state.nodes) == 2
    assert len(final_state.edges) == 2
    assert any(edge["source"] == helper_id and edge["target"] == foo_id for edge in final_state.edges)

    for node in final_state.nodes.values():
        assert node["atom"] == "LOG.FNC.M"
        assert node["role"] == "Service"
        assert node["rpbl_responsibility"] == 0.8
        assert node["purpose"] == "Process"
        assert node["purpose_confidence"] == 0.88
        assert node["coherence_score"] == 0.73
        assert "in_degree" in node
        assert "out_degree" in node
        assert "total_degree" in node

    assert final_state.metadata["stats"]["files_analyzed"] == 1
    assert final_state.metadata["purpose_field"]["coverage"] == 1.0
    assert final_state.metadata["graph_analytics"]["total_nodes"] == 2
    assert final_state.metadata["graph_analytics"]["total_edges"] == 2
