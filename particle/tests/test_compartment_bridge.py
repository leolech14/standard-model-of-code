"""Tests for compartment_bridge.py — Compartment → Incoherence bridge."""

import json
import tempfile
from pathlib import Path

import pytest
import yaml

from src.core.compartment_bridge import (
    compute_all_compartments,
    compute_compartment_incoherence,
    extract_subgraph_kpis,
    load_compartments,
    load_dashboard_modules,
    map_compartment_to_files,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_compartments():
    return [
        {
            "id": "integration",
            "kind": "umbrella",
            "sub_compartments": ["google"],
        },
        {
            "id": "google",
            "parent": "integration",
            "config_files": ["dashboard/google/google_api.py"],
        },
        {
            "id": "ecosync",
            "description": "No code files",
        },
    ]


@pytest.fixture
def sample_capability_files():
    return {
        "google": [
            "dashboard/google/__init__.py",
            "dashboard/google/google_api.py",
            "dashboard/google/meet.py",
        ],
        "monitoring": [
            "dashboard/monitoring/health.py",
        ],
    }


@pytest.fixture
def sample_collider_output():
    """Minimal Collider output with nodes and edges."""
    return {
        "nodes": [
            {
                "id": "dashboard/google/google_api.py::GmailService",
                "file_path": "dashboard/google/google_api.py",
                "name": "GmailService",
                "in_degree": 3,
                "out_degree": 2,
                "pi2_confidence": 0.85,
                "pi2_purpose": "SERVICE",
                "coherence_score": 0.82,
                "complexity": 0,
                "cyclomatic_complexity": 5,
                "reachable_from_entry": True,
            },
            {
                "id": "dashboard/google/google_api.py::CalendarService",
                "file_path": "dashboard/google/google_api.py",
                "name": "CalendarService",
                "in_degree": 2,
                "out_degree": 12,
                "pi2_confidence": 0.90,
                "pi2_purpose": "SERVICE",
                "coherence_score": 0.75,
                "complexity": 0,
                "cyclomatic_complexity": 8,
                "reachable_from_entry": True,
            },
            {
                "id": "dashboard/google/meet.py::MeetBridge",
                "file_path": "dashboard/google/meet.py",
                "name": "MeetBridge",
                "in_degree": 0,
                "out_degree": 0,
                "pi2_confidence": 0.70,
                "pi2_purpose": "SERVICE",
                "coherence_score": 0.60,
                "complexity": 0,
                "cyclomatic_complexity": 12,
                "reachable_from_entry": False,
            },
            {
                "id": "dashboard/google/__init__.py::init",
                "file_path": "dashboard/google/__init__.py",
                "name": "__init__",
                "in_degree": 5,
                "out_degree": 0,
                "pi2_confidence": 0.50,
                "pi2_purpose": "UNKNOWN",
                "coherence_score": 0.40,
                "complexity": 0,
                "cyclomatic_complexity": 1,
                "reachable_from_entry": True,
            },
            {
                "id": "dashboard/monitoring/health.py::check",
                "file_path": "dashboard/monitoring/health.py",
                "name": "check",
                "in_degree": 1,
                "out_degree": 1,
                "pi2_confidence": 0.95,
                "pi2_purpose": "UTILITY",
                "coherence_score": 0.90,
                "complexity": 0,
                "cyclomatic_complexity": 3,
                "reachable_from_entry": True,
            },
        ],
        "edges": [
            # 2 internal google edges
            {"source": "dashboard/google/google_api.py::GmailService", "target": "dashboard/google/__init__.py::init", "edge_type": "import"},
            {"source": "dashboard/google/google_api.py::CalendarService", "target": "dashboard/google/__init__.py::init", "edge_type": "import"},
            # 1 cross-boundary edge (google -> monitoring)
            {"source": "dashboard/google/google_api.py::GmailService", "target": "dashboard/monitoring/health.py::check", "edge_type": "calls"},
        ],
        "kpis": {
            "nodes_total": 5,
            "orphan_percent": 0,
            "avg_fanout": 1.6,
        },
    }


# ---------------------------------------------------------------------------
# Tests: Loading
# ---------------------------------------------------------------------------

class TestLoading:

    def test_load_compartments_from_list(self, tmp_path):
        data = [{"id": "a"}, {"id": "b"}]
        p = tmp_path / "comps.yaml"
        p.write_text(yaml.dump(data))
        result = load_compartments(str(p))
        assert len(result) == 2
        assert result[0]["id"] == "a"

    def test_load_compartments_from_dict(self, tmp_path):
        data = {"compartments": [{"id": "x"}]}
        p = tmp_path / "comps.yaml"
        p.write_text(yaml.dump(data))
        result = load_compartments(str(p))
        assert len(result) == 1

    def test_load_dashboard_modules(self, tmp_path):
        data = {
            "schema_version": "2.0.0",
            "files": {
                "dashboard/google/api.py": {"capability": "google", "layer": "service"},
                "dashboard/mon/health.py": {"capability": "monitoring", "layer": "service"},
            }
        }
        p = tmp_path / "modules.yaml"
        p.write_text(yaml.dump(data))
        result = load_dashboard_modules(str(p))
        assert "google" in result
        assert len(result["google"]) == 1
        assert "monitoring" in result


# ---------------------------------------------------------------------------
# Tests: Mapping
# ---------------------------------------------------------------------------

class TestMapping:

    def test_map_compartment_to_files(self, sample_capability_files):
        comp = {"id": "google", "config_files": []}
        files = map_compartment_to_files(comp, sample_capability_files)
        assert len(files) == 3
        assert "dashboard/google/google_api.py" in files

    def test_map_adds_config_py_files(self, sample_capability_files):
        comp = {
            "id": "unknown-cap",
            "config_files": ["dashboard/google/custom.py", "~/.config/token.json"],
        }
        files = map_compartment_to_files(comp, sample_capability_files)
        # Only the .py file under dashboard/ is added
        assert "dashboard/google/custom.py" in files
        assert "~/.config/token.json" not in files

    def test_map_empty_capability(self):
        comp = {"id": "ecosync"}
        files = map_compartment_to_files(comp, {})
        assert len(files) == 0

    def test_direct_match_financial_intelligence(self):
        """financial-intelligence compartment matches directly after rename."""
        cap_files = {"financial-intelligence": ["dashboard/fin_intelligence/api.py"]}
        comp = {"id": "financial-intelligence"}
        files = map_compartment_to_files(comp, cap_files)
        assert "dashboard/fin_intelligence/api.py" in files

    def test_direct_match_intelligence_pipeline(self):
        """intelligence-pipeline compartment matches directly after rename."""
        cap_files = {"intelligence-pipeline": ["dashboard/intelligence/crystal.py"]}
        comp = {"id": "intelligence-pipeline"}
        files = map_compartment_to_files(comp, cap_files)
        assert "dashboard/intelligence/crystal.py" in files

    def test_core_compartment_direct_match(self):
        """core compartment matches directly to core capability."""
        cap_files = {"core": ["dashboard/app.py", "dashboard/config.py"]}
        comp = {"id": "core"}
        files = map_compartment_to_files(comp, cap_files)
        assert "dashboard/app.py" in files
        assert "dashboard/config.py" in files

    def test_console_runtime_no_longer_inherits_core(self):
        """console-runtime does NOT get all core files (core has its own compartment)."""
        cap_files = {"core": ["dashboard/app.py", "dashboard/config.py"]}
        comp = {"id": "console-runtime"}
        files = map_compartment_to_files(comp, cap_files)
        # console-runtime has no direct capability match and no domain mapping to core
        assert len(files) == 0

    def test_domain_mapping_context_injection(self):
        """context-injection resolves through domain mapping to intelligence-pipeline."""
        cap_files = {
            "intelligence-pipeline": ["dashboard/intelligence/crystal_store.py"],
        }
        comp = {"id": "context-injection"}
        files = map_compartment_to_files(comp, cap_files)
        assert "dashboard/intelligence/crystal_store.py" in files

    def test_domain_mapping_telemetry(self):
        """telemetry resolves through domain mapping to monitoring."""
        cap_files = {
            "monitoring": ["dashboard/monitoring/health.py"],
        }
        comp = {"id": "telemetry"}
        files = map_compartment_to_files(comp, cap_files)
        assert "dashboard/monitoring/health.py" in files


# ---------------------------------------------------------------------------
# Tests: Subgraph KPIs
# ---------------------------------------------------------------------------

class TestSubgraphKPIs:

    def test_extract_google_subgraph(self, sample_collider_output, sample_capability_files):
        file_paths = set(sample_capability_files["google"])
        kpis = extract_subgraph_kpis(file_paths, sample_collider_output)

        assert kpis["nodes_total"] == 4  # 4 google nodes
        assert kpis["files"] == 3
        assert 0 <= kpis["orphan_percent"] <= 100
        assert kpis["avg_fanout"] >= 0
        assert "purpose_clarity" in kpis
        assert "cross_boundary_ratio" in kpis
        assert "avg_coherence" in kpis
        assert "purpose_entropy" in kpis

    def test_empty_files_returns_no_nodes(self, sample_collider_output):
        kpis = extract_subgraph_kpis(set(), sample_collider_output)
        assert kpis["status"] == "no_nodes"

    def test_unknown_files_returns_no_nodes(self, sample_collider_output):
        kpis = extract_subgraph_kpis({"nonexistent.py"}, sample_collider_output)
        assert kpis["status"] == "no_nodes"

    def test_cross_boundary_detection(self, sample_collider_output, sample_capability_files):
        file_paths = set(sample_capability_files["google"])
        kpis = extract_subgraph_kpis(file_paths, sample_collider_output)
        # 1 cross-boundary edge (google -> monitoring) out of 3 total
        assert kpis["cross_boundary_ratio"] > 0
        assert kpis["cross_boundary_edges"] == 1
        assert kpis["internal_edges"] == 2

    def test_orphan_detection(self, sample_collider_output, sample_capability_files):
        file_paths = set(sample_capability_files["google"])
        kpis = extract_subgraph_kpis(file_paths, sample_collider_output)
        # MeetBridge has in_degree=0, out_degree=0 → orphan
        assert kpis["orphan_percent"] > 0
        assert kpis["dead_code_percent"] > 0  # dead_code = orphans

    def test_coherence_scores(self, sample_collider_output, sample_capability_files):
        file_paths = set(sample_capability_files["google"])
        kpis = extract_subgraph_kpis(file_paths, sample_collider_output)
        # avg of 0.82, 0.75, 0.60, 0.40 = 0.6425
        assert 0.6 < kpis["avg_coherence"] < 0.7

    def test_purpose_entropy(self, sample_collider_output, sample_capability_files):
        file_paths = set(sample_capability_files["google"])
        kpis = extract_subgraph_kpis(file_paths, sample_collider_output)
        # 3 SERVICE + 1 UNKNOWN = 2 categories, some entropy
        assert kpis["purpose_entropy"] > 0


# ---------------------------------------------------------------------------
# Tests: Compartment incoherence
# ---------------------------------------------------------------------------

class TestCompartmentIncoherence:

    def test_compute_google_incoherence(self, sample_collider_output, sample_capability_files):
        comp = {"id": "google", "config_files": []}
        result = compute_compartment_incoherence(comp, sample_capability_files, sample_collider_output)

        assert result["id"] == "google"
        assert result["files"] == 3
        assert result["nodes"] == 4
        assert 0 <= result["i_struct"] <= 1
        assert 0 <= result["i_telic"] <= 1
        assert 0 <= result["i_sym"] <= 1
        assert 0 <= result["i_bound"] <= 1
        assert 0 <= result["i_flow"] <= 1
        assert 0 <= result["i_total"] <= 1
        assert 0 <= result["health_10"] <= 10

    def test_no_code_compartment(self, sample_collider_output):
        comp = {"id": "ecosync"}
        result = compute_compartment_incoherence(comp, {}, sample_collider_output)
        assert result["status"] == "no_code_files"
        assert result["files"] == 0

    def test_compartment_with_no_nodes(self, sample_collider_output, sample_capability_files):
        comp = {"id": "ghost", "config_files": ["dashboard/ghost/api.py"]}
        cap_files = {"ghost": ["dashboard/ghost/api.py"]}
        result = compute_compartment_incoherence(comp, cap_files, sample_collider_output)
        assert result["status"] == "no_nodes_in_collider"


# ---------------------------------------------------------------------------
# Tests: Umbrella derivation
# ---------------------------------------------------------------------------

class TestUmbrellas:

    def test_umbrella_worst_of_children(self, tmp_path, sample_collider_output):
        comps = [
            {"id": "integration", "kind": "umbrella", "sub_compartments": ["google"]},
            {"id": "google", "parent": "integration", "config_files": []},
        ]
        cap_files = {
            "google": [
                "dashboard/google/__init__.py",
                "dashboard/google/google_api.py",
                "dashboard/google/meet.py",
            ],
        }

        comps_path = tmp_path / "comps.yaml"
        comps_path.write_text(yaml.dump(comps))

        modules_data = {
            "files": {
                f: {"capability": "google", "layer": "service"}
                for f in cap_files["google"]
            }
        }
        modules_path = tmp_path / "modules.yaml"
        modules_path.write_text(yaml.dump(modules_data))

        collider_path = tmp_path / "collider.json"
        collider_path.write_text(json.dumps(sample_collider_output))

        result = compute_all_compartments(
            str(comps_path), str(modules_path), str(collider_path),
        )

        assert "google" in result["compartments"]
        assert "integration" in result["umbrellas"]
        umb = result["umbrellas"]["integration"]
        assert umb["derivation"] == "worst-of-children"
        # Umbrella health == child health (only one child)
        google_health = result["compartments"]["google"]["health_10"]
        assert umb["health_10"] == google_health

    def test_umbrella_no_children_code(self, tmp_path, sample_collider_output):
        comps = [
            {"id": "empty-umb", "kind": "umbrella", "sub_compartments": ["ghost"]},
            {"id": "ghost", "parent": "empty-umb"},
        ]
        comps_path = tmp_path / "comps.yaml"
        comps_path.write_text(yaml.dump(comps))
        modules_path = tmp_path / "modules.yaml"
        modules_path.write_text(yaml.dump({"modules": {}}))
        collider_path = tmp_path / "collider.json"
        collider_path.write_text(json.dumps(sample_collider_output))

        result = compute_all_compartments(
            str(comps_path), str(modules_path), str(collider_path),
        )
        umb = result["umbrellas"]["empty-umb"]
        assert umb["derivation"] == "no-children-with-code"


# ---------------------------------------------------------------------------
# Tests: Output structure
# ---------------------------------------------------------------------------

class TestOutput:

    def test_output_has_timestamp(self, tmp_path, sample_collider_output):
        comps = [{"id": "test"}]
        comps_path = tmp_path / "comps.yaml"
        comps_path.write_text(yaml.dump(comps))
        modules_path = tmp_path / "modules.yaml"
        modules_path.write_text(yaml.dump({"modules": {}}))
        collider_path = tmp_path / "collider.json"
        collider_path.write_text(json.dumps(sample_collider_output))

        result = compute_all_compartments(
            str(comps_path), str(modules_path), str(collider_path),
        )
        assert "timestamp" in result
        assert "source" in result
        assert "coverage" in result
        assert "compartments" in result
        assert "umbrellas" in result

        # Coverage structure
        cov = result["coverage"]
        assert "collider_total_nodes" in cov
        assert "mapped_to_compartments" in cov
        assert "unmapped" in cov
        assert "coverage_pct" in cov
