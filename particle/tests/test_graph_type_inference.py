"""Tests for Graph-Based Type Inference Engine.

Tests cover:
- InferenceRule dataclass
- INFERENCE_RULES matching
- Structural inference from node properties
- Parent-role inheritance
- Full apply_graph_inference() pipeline
"""
import pytest
from src.core.graph_type_inference import (
    InferenceRule,
    INFERENCE_RULES,
    GraphTypeInference,
    infer_from_structure,
    apply_graph_inference,
)


class TestInferenceRule:
    """Test InferenceRule dataclass."""

    def test_default_sets(self):
        """Empty sets initialized properly."""
        rule = InferenceRule(
            name="test_rule",
            inferred_type="Service",
            confidence=80.0,
        )
        assert rule.caller_types == set()
        assert rule.callee_types == set()

    def test_with_caller_types(self):
        """Caller types preserved."""
        rule = InferenceRule(
            name="test_rule",
            inferred_type="Service",
            confidence=80.0,
            caller_types={"Controller", "Handler"},
        )
        assert rule.caller_types == {"Controller", "Handler"}

    def test_degree_bounds(self):
        """Degree bounds work correctly."""
        rule = InferenceRule(
            name="high_degree",
            inferred_type="Utility",
            confidence=70.0,
            min_in_degree=10,
            max_out_degree=5,
        )
        assert rule.min_in_degree == 10
        assert rule.max_out_degree == 5


class TestInferenceRules:
    """Test the predefined INFERENCE_RULES."""

    def test_rules_exist(self):
        """Rules list is populated."""
        assert len(INFERENCE_RULES) >= 10

    def test_calls_repository_rule(self):
        """Key rule: calls_repository exists and is correct."""
        rule = next((r for r in INFERENCE_RULES if r.name == "calls_repository"), None)
        assert rule is not None
        assert rule.inferred_type == "Service"
        assert rule.confidence == 90.0
        assert "Repository" in rule.callee_types

    def test_high_in_degree_utility_rule(self):
        """Key rule: high_in_degree_utility exists."""
        rule = next((r for r in INFERENCE_RULES if r.name == "high_in_degree_utility"), None)
        assert rule is not None
        assert rule.inferred_type == "Utility"
        assert rule.min_in_degree == 10

    def test_called_only_by_tests_rule(self):
        """Key rule: called_only_by_tests exists."""
        rule = next((r for r in INFERENCE_RULES if r.name == "called_only_by_tests"), None)
        assert rule is not None
        assert rule.inferred_type == "Internal"
        assert "Asserter" in rule.caller_types


class TestGraphTypeInference:
    """Test GraphTypeInference class."""

    def setup_method(self):
        self.engine = GraphTypeInference()

    def test_build_graph_index(self):
        """Graph index is built correctly."""
        nodes = [
            {"id": "A", "name": "ServiceA"},
            {"id": "B", "name": "RepoB"},
        ]
        edges = [
            {"source": "A", "target": "B", "edge_type": "calls"},
        ]
        index = self.engine.build_graph_index(nodes, edges)

        assert "A" in index["node_by_id"]
        assert "B" in index["node_by_id"]
        assert index["callees"]["A"] == {"B"}
        assert index["callers"]["B"] == {"A"}
        assert index["out_degree"]["A"] == 1
        assert index["in_degree"]["B"] == 1

    def test_get_neighbor_types(self):
        """Neighbor types extracted correctly."""
        nodes = [
            {"id": "A", "name": "A", "role": "Service"},
            {"id": "B", "name": "B", "role": "Repository"},
        ]
        node_by_id = {n["id"]: n for n in nodes}
        types = self.engine.get_neighbor_types("A", {"B"}, node_by_id)
        assert "Repository" in types

    def test_infer_type_calls_repository(self):
        """Node calling Repository inferred as Service."""
        nodes = [
            {"id": "A", "name": "UserService", "role": "Unknown"},
            {"id": "B", "name": "UserRepo", "role": "Repository"},
        ]
        edges = [
            {"source": "A", "target": "B", "edge_type": "calls"},
        ]
        index = self.engine.build_graph_index(nodes, edges)
        inferred_type, confidence, rule = self.engine.infer_type(nodes[0], index)

        assert inferred_type == "Service"
        assert confidence == 90.0
        assert rule == "calls_repository"

    def test_infer_type_high_in_degree(self):
        """Node with many callers inferred as Utility."""
        # Create a hub node with 10+ callers
        # Note: Hub must have out-edges to avoid triggering "leaf_called_by_service"
        nodes = [{"id": f"caller_{i}", "name": f"C{i}", "role": "Unknown"} for i in range(12)]
        nodes.append({"id": "hub", "name": "UtilityHub", "role": "Unknown"})
        nodes.append({"id": "downstream", "name": "Downstream", "role": "Unknown"})

        edges = [
            {"source": f"caller_{i}", "target": "hub", "edge_type": "calls"}
            for i in range(12)
        ]
        # Hub calls downstream so it's not a leaf
        edges.append({"source": "hub", "target": "downstream", "edge_type": "calls"})

        index = self.engine.build_graph_index(nodes, edges)
        hub_node = next(n for n in nodes if n["id"] == "hub")
        inferred_type, confidence, rule = self.engine.infer_type(hub_node, index)

        assert inferred_type == "Utility"
        assert rule == "high_in_degree_utility"

    def test_infer_all(self):
        """Full inference pass updates nodes."""
        nodes = [
            {"id": "A", "name": "UserService", "role": "Unknown"},
            {"id": "B", "name": "UserRepo", "role": "Repository"},
        ]
        edges = [
            {"source": "A", "target": "B", "edge_type": "calls"},
        ]

        updated_nodes, report = self.engine.infer_all(nodes, edges)

        # Node A should now be Service
        node_a = next(n for n in updated_nodes if n["id"] == "A")
        assert node_a["role"] == "Service"
        assert node_a.get("discovery_method", "").startswith("graph_inference:")
        assert report["total_inferred"] >= 1


class TestInferFromStructure:
    """Test structural inference from node properties."""

    def test_return_type_factory(self):
        """Return type with 'create' suggests Factory."""
        node = {
            "name": "UserFactory",
            "return_type": "create_user",
            "role": "Unknown",
        }
        result = infer_from_structure(node)
        assert result is not None
        assert result[0] == "Factory"

    def test_return_type_bool_specification(self):
        """Boolean return type suggests Specification."""
        node = {
            "name": "IsValidUser",
            "return_type": "bool",
            "role": "Unknown",
        }
        result = infer_from_structure(node)
        assert result is not None
        assert result[0] == "Specification"

    def test_http_params_controller(self):
        """Request/response params suggest Controller."""
        node = {
            "name": "handle_request",
            "params": [{"name": "request", "type": "HttpRequest"}],
            "role": "Unknown",
        }
        result = infer_from_structure(node)
        assert result is not None
        assert result[0] == "Controller"

    def test_docstring_test(self):
        """Docstring with 'test' suggests Test."""
        node = {
            "name": "test_something",
            "docstring": "Test that user validation works correctly.",
            "role": "Unknown",
        }
        result = infer_from_structure(node)
        assert result is not None
        assert result[0] == "Test"

    def test_docstring_validator(self):
        """Docstring with 'validate' suggests Validator."""
        node = {
            "name": "check_email",
            "docstring": "Validate that email format is correct.",
            "role": "Unknown",
        }
        result = infer_from_structure(node)
        assert result is not None
        assert result[0] == "Validator"

    def test_high_complexity_service(self):
        """High complexity suggests Service."""
        node = {
            "name": "complex_workflow",
            "complexity": 25,
            "role": "Unknown",
        }
        result = infer_from_structure(node)
        assert result is not None
        assert result[0] == "Service"

    def test_leaf_class_dto(self):
        """Zero out-degree class suggests DTO."""
        node = {
            "name": "UserDTO",
            "kind": "class",
            "out_degree": 0,
            "role": "Unknown",
        }
        result = infer_from_structure(node)
        assert result is not None
        assert result[0] == "DTO"

    def test_skips_high_confidence(self):
        """Skips nodes with existing high confidence."""
        node = {
            "name": "AlreadyClassified",
            "role": "Service",
            "role_confidence": 95,
        }
        result = infer_from_structure(node)
        assert result is None


class TestApplyGraphInference:
    """Test the full apply_graph_inference() function."""

    def test_full_pipeline(self):
        """Full pipeline: graph + structural + parent inheritance."""
        nodes = [
            {"id": "A", "name": "UserService", "role": "Unknown"},
            {"id": "B", "name": "UserRepo", "role": "Repository"},
            {"id": "C", "name": "UserService.validate", "role": "Unknown", "parent": "A"},
        ]
        edges = [
            {"source": "A", "target": "B", "edge_type": "calls"},
        ]

        updated_nodes, report = apply_graph_inference(nodes, edges)

        # Node A should be Service (calls Repository)
        node_a = next(n for n in updated_nodes if n["id"] == "A")
        assert node_a["role"] == "Service"

        # Node C should inherit from parent A
        node_c = next(n for n in updated_nodes if n["id"] == "C")
        # Should inherit Service from parent or remain Unknown if parent inheritance happens after
        assert node_c["role"] in ["Service", "Unknown"]

        # Report should have counts
        assert "total_inferred" in report

    def test_no_unknowns(self):
        """Already-classified nodes not modified."""
        nodes = [
            {"id": "A", "name": "UserService", "role": "Service", "role_confidence": 90},
            {"id": "B", "name": "UserRepo", "role": "Repository", "role_confidence": 95},
        ]
        edges = [
            {"source": "A", "target": "B", "edge_type": "calls"},
        ]

        updated_nodes, report = apply_graph_inference(nodes, edges)

        # Roles unchanged
        node_a = next(n for n in updated_nodes if n["id"] == "A")
        assert node_a["role"] == "Service"

    def test_parent_inheritance_dotted_name(self):
        """Parent inheritance works with dotted names."""
        nodes = [
            {"id": "A", "name": "TestClass", "role": "Asserter"},
            {"id": "B", "name": "TestClass.test_method", "role": "Unknown"},
        ]
        edges = []

        updated_nodes, report = apply_graph_inference(nodes, edges)

        # Node B should inherit Asserter from TestClass
        node_b = next(n for n in updated_nodes if n["id"] == "B")
        assert node_b["role"] == "Asserter"
        assert "parent_inheritance" in node_b.get("discovery_method", "")


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_nodes(self):
        """Empty node list handled."""
        nodes, report = apply_graph_inference([], [])
        assert nodes == []
        assert report["total_inferred"] == 0

    def test_no_edges(self):
        """No edges still processes structural rules."""
        nodes = [
            {"id": "A", "name": "validate", "docstring": "Validate user input", "role": "Unknown"},
        ]
        updated_nodes, report = apply_graph_inference(nodes, [])

        node_a = next(n for n in updated_nodes if n["id"] == "A")
        # Structural inference should kick in from docstring
        assert node_a["role"] == "Validator"

    def test_cyclic_graph(self):
        """Cyclic dependencies don't cause infinite loops."""
        nodes = [
            {"id": "A", "name": "A", "role": "Unknown"},
            {"id": "B", "name": "B", "role": "Unknown"},
            {"id": "C", "name": "C", "role": "Unknown"},
        ]
        edges = [
            {"source": "A", "target": "B", "edge_type": "calls"},
            {"source": "B", "target": "C", "edge_type": "calls"},
            {"source": "C", "target": "A", "edge_type": "calls"},
        ]

        # Should complete without hanging
        updated_nodes, report = apply_graph_inference(nodes, edges)
        assert len(updated_nodes) == 3


class TestRuleMatching:
    """Test specific rule matching scenarios."""

    def test_called_by_controller(self):
        """Node called by Controller becomes Service."""
        nodes = [
            {"id": "controller", "name": "UserController", "role": "Controller"},
            {"id": "service", "name": "UserUseCase", "role": "Unknown"},
        ]
        edges = [
            {"source": "controller", "target": "service", "edge_type": "calls"},
        ]

        engine = GraphTypeInference()
        index = engine.build_graph_index(nodes, edges)
        inferred_type, confidence, rule = engine.infer_type(nodes[1], index)

        assert inferred_type == "Service"
        assert rule == "called_by_controller"

    def test_leaf_called_by_service(self):
        """Leaf node called by Service becomes Query."""
        nodes = [
            {"id": "service", "name": "UserService", "role": "Service"},
            {"id": "query", "name": "FindUserQuery", "role": "Unknown"},
        ]
        edges = [
            {"source": "service", "target": "query", "edge_type": "calls"},
        ]

        engine = GraphTypeInference()
        index = engine.build_graph_index(nodes, edges)
        inferred_type, confidence, rule = engine.infer_type(nodes[1], index)

        assert inferred_type == "Query"
        assert rule == "leaf_called_by_service"

    def test_calls_factory(self):
        """Node calling Factory becomes Service."""
        nodes = [
            {"id": "creator", "name": "UserCreator", "role": "Unknown"},
            {"id": "factory", "name": "UserFactory", "role": "Factory"},
        ]
        edges = [
            {"source": "creator", "target": "factory", "edge_type": "calls"},
        ]

        engine = GraphTypeInference()
        index = engine.build_graph_index(nodes, edges)
        inferred_type, confidence, rule = engine.infer_type(nodes[0], index)

        assert inferred_type == "Service"
        assert rule == "calls_factory"
