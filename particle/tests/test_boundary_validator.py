"""
Tests for the boundary validator (Feature 1).

Validates:
- YAML loading and structural validation
- Node-to-compartment assignment
- Edge-based boundary violation detection
- Compliance score computation
- Edge cases (unmapped nodes, multi-mapped nodes, empty inputs)
"""

import pytest
import sys
from pathlib import Path

# Add src/core to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "core"))

from boundary_validator import (
    load_boundaries,
    assign_compartments,
    validate_boundaries,
    compute_boundary_compliance_score,
    format_boundary_summary,
)


# =============================================================================
# FIXTURES
# =============================================================================

VALID_YAML = """\
compartments:
  api:
    globs: ["src/api/**", "src/routes/**"]
    allowed_deps: [core, models]
  core:
    globs: ["src/core/**"]
    allowed_deps: [models]
  models:
    globs: ["src/models/**"]
    allowed_deps: []
  tests:
    globs: ["tests/**"]
    allowed_deps: [api, core, models]
"""


def _make_boundaries():
    """Create a boundaries dict matching VALID_YAML without file I/O."""
    return {
        "compartments": {
            "api": {
                "globs": ["src/api/**", "src/routes/**"],
                "allowed_deps": ["core", "models"],
            },
            "core": {
                "globs": ["src/core/**"],
                "allowed_deps": ["models"],
            },
            "models": {
                "globs": ["src/models/**"],
                "allowed_deps": [],
            },
            "tests": {
                "globs": ["tests/**"],
                "allowed_deps": ["api", "core", "models"],
            },
        }
    }


def _make_nodes():
    """Create a set of nodes spanning multiple compartments."""
    return [
        {"id": "src/api/routes.py:function:get_users", "file_path": "src/api/routes.py", "kind": "function"},
        {"id": "src/api/auth.py:function:check_token", "file_path": "src/api/auth.py", "kind": "function"},
        {"id": "src/core/engine.py:function:process", "file_path": "src/core/engine.py", "kind": "function"},
        {"id": "src/core/parser.py:function:parse", "file_path": "src/core/parser.py", "kind": "function"},
        {"id": "src/models/user.py:class:User", "file_path": "src/models/user.py", "kind": "class"},
        {"id": "tests/test_api.py:function:test_get", "file_path": "tests/test_api.py", "kind": "function"},
        {"id": "lib/external.py:function:helper", "file_path": "lib/external.py", "kind": "function"},
    ]


# =============================================================================
# LOADING
# =============================================================================

class TestLoadBoundaries:
    """Test YAML boundary file loading and validation."""

    def test_load_valid(self, tmp_path):
        f = tmp_path / "compartments.yaml"
        f.write_text(VALID_YAML)
        result = load_boundaries(str(f))
        assert "compartments" in result
        assert "api" in result["compartments"]
        assert result["compartments"]["api"]["globs"] == ["src/api/**", "src/routes/**"]
        assert result["compartments"]["api"]["allowed_deps"] == ["core", "models"]

    def test_load_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            load_boundaries("/nonexistent/path.yaml")

    def test_load_missing_compartments_key(self, tmp_path):
        f = tmp_path / "bad.yaml"
        f.write_text("something: true\n")
        with pytest.raises(ValueError, match="must contain a 'compartments' key"):
            load_boundaries(str(f))

    def test_load_missing_globs(self, tmp_path):
        f = tmp_path / "bad.yaml"
        f.write_text(
            "compartments:\n"
            "  api:\n"
            "    allowed_deps: [core]\n"
        )
        with pytest.raises(ValueError, match="non-empty 'globs' list"):
            load_boundaries(str(f))

    def test_load_empty_globs(self, tmp_path):
        f = tmp_path / "bad.yaml"
        f.write_text(
            "compartments:\n"
            "  api:\n"
            "    globs: []\n"
            "    allowed_deps: []\n"
        )
        with pytest.raises(ValueError, match="non-empty 'globs' list"):
            load_boundaries(str(f))

    def test_load_unknown_dependency(self, tmp_path):
        f = tmp_path / "bad.yaml"
        f.write_text(
            "compartments:\n"
            "  api:\n"
            "    globs: ['src/api/**']\n"
            "    allowed_deps: [nonexistent]\n"
        )
        with pytest.raises(ValueError, match="unknown dependency 'nonexistent'"):
            load_boundaries(str(f))

    def test_load_allowed_deps_defaults_to_empty(self, tmp_path):
        """When allowed_deps is omitted, treat as empty list (leaf node)."""
        f = tmp_path / "leaf.yaml"
        f.write_text(
            "compartments:\n"
            "  models:\n"
            "    globs: ['src/models/**']\n"
        )
        result = load_boundaries(str(f))
        # Should not raise — allowed_deps defaults to []
        assert "models" in result["compartments"]

    def test_load_compartment_not_mapping(self, tmp_path):
        f = tmp_path / "bad.yaml"
        f.write_text(
            "compartments:\n"
            "  api: just_a_string\n"
        )
        with pytest.raises(ValueError, match="must be a mapping"):
            load_boundaries(str(f))


# =============================================================================
# COMPARTMENT ASSIGNMENT
# =============================================================================

class TestAssignCompartments:
    """Test node-to-compartment assignment."""

    def test_all_mapped(self):
        nodes = [
            {"id": "a", "file_path": "src/api/x.py"},
            {"id": "b", "file_path": "src/core/y.py"},
            {"id": "c", "file_path": "src/models/z.py"},
        ]
        boundaries = _make_boundaries()
        result = assign_compartments(nodes, boundaries)
        assert result["mapped_count"] == 3
        assert len(result["unmapped_nodes"]) == 0
        assert result["assignments"]["a"] == "api"
        assert result["assignments"]["b"] == "core"
        assert result["assignments"]["c"] == "models"

    def test_unmapped_nodes(self):
        nodes = [
            {"id": "a", "file_path": "src/api/x.py"},
            {"id": "b", "file_path": "lib/external.py"},  # No compartment matches
        ]
        boundaries = _make_boundaries()
        result = assign_compartments(nodes, boundaries)
        assert result["mapped_count"] == 1
        assert "b" in result["unmapped_nodes"]

    def test_multi_mapped(self):
        """When globs from multiple compartments match the same file."""
        boundaries = {
            "compartments": {
                "api": {
                    "globs": ["src/**"],
                    "allowed_deps": [],
                },
                "core": {
                    "globs": ["src/core/**"],
                    "allowed_deps": [],
                },
            }
        }
        nodes = [
            {"id": "a", "file_path": "src/core/engine.py"},
        ]
        result = assign_compartments(nodes, boundaries)
        assert "a" in result["multi_mapped"]
        # First match wins
        assert result["assignments"]["a"] == "api"

    def test_mutates_nodes_in_place(self):
        nodes = [{"id": "a", "file_path": "src/api/x.py"}]
        boundaries = _make_boundaries()
        assign_compartments(nodes, boundaries)
        assert nodes[0]["compartment"] == "api"

    def test_no_file_path_is_unmapped(self):
        nodes = [{"id": "a", "kind": "function"}]
        boundaries = _make_boundaries()
        result = assign_compartments(nodes, boundaries)
        assert "a" in result["unmapped_nodes"]

    def test_empty_nodes(self):
        result = assign_compartments([], _make_boundaries())
        assert result["mapped_count"] == 0
        assert result["unmapped_nodes"] == []

    def test_multiple_globs_per_compartment(self):
        """API compartment has two globs: src/api/** and src/routes/**."""
        nodes = [
            {"id": "a", "file_path": "src/api/x.py"},
            {"id": "b", "file_path": "src/routes/y.py"},
        ]
        boundaries = _make_boundaries()
        result = assign_compartments(nodes, boundaries)
        assert result["assignments"]["a"] == "api"
        assert result["assignments"]["b"] == "api"


# =============================================================================
# BOUNDARY VALIDATION
# =============================================================================

class TestValidateBoundaries:
    """Test edge-based boundary violation detection."""

    def test_no_violations(self):
        """All cross-compartment edges follow allowed_deps."""
        assignments = {"a": "api", "b": "core", "c": "models"}
        edges = [
            {"source": "a", "target": "b", "edge_type": "calls"},  # api -> core: allowed
            {"source": "a", "target": "c", "edge_type": "imports"},  # api -> models: allowed
            {"source": "b", "target": "c", "edge_type": "calls"},  # core -> models: allowed
        ]
        result = validate_boundaries([], edges, assignments, _make_boundaries())
        assert result["violation_count"] == 0
        assert result["compliant_edges"] == 3
        assert result["compliance_rate"] == 1.0

    def test_single_violation(self):
        """models -> api is not allowed (models has no allowed_deps)."""
        assignments = {"a": "api", "c": "models"}
        edges = [
            {"source": "c", "target": "a", "edge_type": "imports"},  # models -> api: VIOLATION
        ]
        result = validate_boundaries([], edges, assignments, _make_boundaries())
        assert result["violation_count"] == 1
        assert result["compliant_edges"] == 0
        assert result["compliance_rate"] == 0.0
        v = result["violations"][0]
        assert v["source_compartment"] == "models"
        assert v["target_compartment"] == "api"

    def test_multiple_violations(self):
        assignments = {"a": "api", "b": "core", "c": "models"}
        edges = [
            {"source": "c", "target": "a", "edge_type": "calls"},   # models -> api: VIOLATION
            {"source": "c", "target": "b", "edge_type": "calls"},   # models -> core: VIOLATION
            {"source": "b", "target": "a", "edge_type": "calls"},   # core -> api: VIOLATION
        ]
        result = validate_boundaries([], edges, assignments, _make_boundaries())
        assert result["violation_count"] == 3
        assert result["compliance_rate"] == 0.0

    def test_intra_compartment_edges_ignored(self):
        """Edges within the same compartment don't count as cross-compartment."""
        assignments = {"a": "api", "b": "api"}
        edges = [
            {"source": "a", "target": "b", "edge_type": "calls"},  # api -> api: always OK
        ]
        result = validate_boundaries([], edges, assignments, _make_boundaries())
        assert result["violation_count"] == 0
        assert result["total_cross_compartment_edges"] == 0

    def test_unmapped_nodes_skipped(self):
        """Edges involving unmapped nodes are not validated."""
        assignments = {"a": "api"}  # b is unmapped
        edges = [
            {"source": "a", "target": "b", "edge_type": "calls"},
        ]
        result = validate_boundaries([], edges, assignments, _make_boundaries())
        assert result["violation_count"] == 0
        assert result["total_cross_compartment_edges"] == 0

    def test_mixed_compliance(self):
        """Some compliant, some violating."""
        assignments = {"a": "api", "b": "core", "c": "models"}
        edges = [
            {"source": "a", "target": "b", "edge_type": "calls"},  # api -> core: OK
            {"source": "c", "target": "a", "edge_type": "calls"},  # models -> api: VIOLATION
        ]
        result = validate_boundaries([], edges, assignments, _make_boundaries())
        assert result["violation_count"] == 1
        assert result["compliant_edges"] == 1
        assert result["total_cross_compartment_edges"] == 2
        assert result["compliance_rate"] == 0.5

    def test_per_compartment_stats(self):
        assignments = {"a": "api", "b": "core", "c": "models"}
        edges = [
            {"source": "a", "target": "b", "edge_type": "calls"},  # OK
            {"source": "c", "target": "a", "edge_type": "calls"},  # VIOLATION
        ]
        result = validate_boundaries([], edges, assignments, _make_boundaries())
        # api has 1 compliant outbound cross-compartment edge
        assert result["per_compartment"]["api"]["compliant"] == 1
        assert result["per_compartment"]["api"]["violations"] == 0
        # models has 1 violating outbound
        assert result["per_compartment"]["models"]["violations"] == 1
        assert result["per_compartment"]["models"]["compliant"] == 0

    def test_tests_compartment_can_reach_everything(self):
        """Tests compartment is allowed to depend on all others."""
        assignments = {"t": "tests", "a": "api", "b": "core", "c": "models"}
        edges = [
            {"source": "t", "target": "a", "edge_type": "imports"},
            {"source": "t", "target": "b", "edge_type": "imports"},
            {"source": "t", "target": "c", "edge_type": "imports"},
        ]
        result = validate_boundaries([], edges, assignments, _make_boundaries())
        assert result["violation_count"] == 0
        assert result["compliant_edges"] == 3

    def test_empty_edges(self):
        assignments = {"a": "api"}
        result = validate_boundaries([], [], assignments, _make_boundaries())
        assert result["violation_count"] == 0
        assert result["total_cross_compartment_edges"] == 0
        assert result["compliance_rate"] == 1.0

    def test_edge_type_fallback(self):
        """Support both 'edge_type' and 'type' field names."""
        assignments = {"a": "api", "c": "models"}
        edges = [
            {"source": "c", "target": "a", "type": "imports"},  # 'type' not 'edge_type'
        ]
        result = validate_boundaries([], edges, assignments, _make_boundaries())
        assert result["violation_count"] == 1
        assert result["violations"][0]["edge_type"] == "imports"


# =============================================================================
# COMPLIANCE SCORE
# =============================================================================

class TestComplianceScore:
    """Test health score computation from compliance data."""

    def test_perfect_compliance(self):
        result = {
            "total_cross_compartment_edges": 10,
            "compliance_rate": 1.0,
        }
        assert compute_boundary_compliance_score(result) == 10.0

    def test_zero_compliance(self):
        result = {
            "total_cross_compartment_edges": 10,
            "compliance_rate": 0.0,
        }
        assert compute_boundary_compliance_score(result) == 0.0

    def test_partial_compliance(self):
        result = {
            "total_cross_compartment_edges": 10,
            "compliance_rate": 0.75,
        }
        assert compute_boundary_compliance_score(result) == 7.5

    def test_no_cross_compartment_edges(self):
        """No edges to violate → perfect score."""
        result = {
            "total_cross_compartment_edges": 0,
            "compliance_rate": 1.0,
        }
        assert compute_boundary_compliance_score(result) == 10.0

    def test_empty_input(self):
        assert compute_boundary_compliance_score({}) == 10.0


# =============================================================================
# SUMMARY FORMAT
# =============================================================================

class TestFormatSummary:
    """Test human-readable summary output."""

    def test_summary_is_string(self):
        assignment_result = {
            "mapped_count": 5,
            "unmapped_nodes": ["x"],
            "multi_mapped": [],
        }
        validation_result = {
            "violations": [],
            "violation_count": 0,
            "compliant_edges": 10,
            "total_cross_compartment_edges": 10,
            "compliance_rate": 1.0,
            "per_compartment": {},
        }
        summary = format_boundary_summary(assignment_result, validation_result)
        assert isinstance(summary, str)
        assert "Compliance rate: 100.0%" in summary

    def test_summary_shows_violations(self):
        assignment_result = {
            "mapped_count": 3,
            "unmapped_nodes": [],
            "multi_mapped": [],
        }
        validation_result = {
            "violations": [{
                "source_node": "c",
                "target_node": "a",
                "source_compartment": "models",
                "target_compartment": "api",
                "edge_type": "imports",
            }],
            "violation_count": 1,
            "compliant_edges": 2,
            "total_cross_compartment_edges": 3,
            "compliance_rate": 0.6667,
            "per_compartment": {},
        }
        summary = format_boundary_summary(assignment_result, validation_result)
        assert "Violations: 1" in summary
        assert "models -> api" in summary


# =============================================================================
# INTEGRATION-STYLE TESTS
# =============================================================================

class TestIntegration:
    """End-to-end tests using realistic node/edge structures."""

    def test_full_pipeline(self):
        """Load → Assign → Validate → Score."""
        nodes = _make_nodes()
        boundaries = _make_boundaries()

        # Assign
        assignment = assign_compartments(nodes, boundaries)
        assert assignment["mapped_count"] == 6  # 7 nodes, 1 unmapped (lib/external.py)
        assert len(assignment["unmapped_nodes"]) == 1

        # Create edges — some valid, some violations
        edges = [
            # api -> core: allowed
            {"source": "src/api/routes.py:function:get_users",
             "target": "src/core/engine.py:function:process",
             "edge_type": "calls"},
            # api -> models: allowed
            {"source": "src/api/routes.py:function:get_users",
             "target": "src/models/user.py:class:User",
             "edge_type": "imports"},
            # core -> models: allowed
            {"source": "src/core/engine.py:function:process",
             "target": "src/models/user.py:class:User",
             "edge_type": "calls"},
            # models -> core: VIOLATION (models has no allowed_deps)
            {"source": "src/models/user.py:class:User",
             "target": "src/core/parser.py:function:parse",
             "edge_type": "imports"},
            # tests -> api: allowed
            {"source": "tests/test_api.py:function:test_get",
             "target": "src/api/routes.py:function:get_users",
             "edge_type": "calls"},
        ]

        # Validate
        validation = validate_boundaries(
            nodes, edges, assignment["assignments"], boundaries
        )
        assert validation["violation_count"] == 1
        assert validation["total_cross_compartment_edges"] == 5
        assert validation["compliant_edges"] == 4
        assert validation["compliance_rate"] == 0.8

        # Score
        score = compute_boundary_compliance_score(validation)
        assert score == 8.0

    def test_fully_compliant_codebase(self):
        """Zero violations → perfect score."""
        boundaries = _make_boundaries()
        nodes = [
            {"id": "a", "file_path": "src/api/x.py"},
            {"id": "b", "file_path": "src/core/y.py"},
            {"id": "c", "file_path": "src/models/z.py"},
        ]
        assignment = assign_compartments(nodes, boundaries)

        edges = [
            {"source": "a", "target": "b", "edge_type": "calls"},  # api -> core: OK
            {"source": "b", "target": "c", "edge_type": "calls"},  # core -> models: OK
        ]
        validation = validate_boundaries(nodes, edges, assignment["assignments"], boundaries)
        assert validation["violation_count"] == 0
        assert compute_boundary_compliance_score(validation) == 10.0

    def test_chaotic_codebase(self):
        """Everything talks to everything → many violations."""
        boundaries = _make_boundaries()
        nodes = [
            {"id": "a", "file_path": "src/api/x.py"},
            {"id": "b", "file_path": "src/core/y.py"},
            {"id": "c", "file_path": "src/models/z.py"},
        ]
        assignment = assign_compartments(nodes, boundaries)

        # All directions
        edges = [
            {"source": "a", "target": "b", "edge_type": "calls"},  # api->core: OK
            {"source": "a", "target": "c", "edge_type": "calls"},  # api->models: OK
            {"source": "b", "target": "a", "edge_type": "calls"},  # core->api: VIOLATION
            {"source": "b", "target": "c", "edge_type": "calls"},  # core->models: OK
            {"source": "c", "target": "a", "edge_type": "calls"},  # models->api: VIOLATION
            {"source": "c", "target": "b", "edge_type": "calls"},  # models->core: VIOLATION
        ]
        validation = validate_boundaries(nodes, edges, assignment["assignments"], boundaries)
        assert validation["violation_count"] == 3
        assert validation["compliant_edges"] == 3
        assert validation["compliance_rate"] == 0.5
        assert compute_boundary_compliance_score(validation) == 5.0
