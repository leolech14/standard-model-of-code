#!/usr/bin/env python3
"""
Contract tests for output normalization.
Ensures canonical meta/id/confidence after normalization.
"""

from src.core.normalize_output import normalize_output, validate_contract


def _sample_output(target_path: str):
    return {
        "target": target_path,
        "timestamp": "2026-01-01T00:00:00",
        "version": "0.0.1",
        "nodes": [
            {
                "id": f"{target_path}/app/main.py:Main.run",
                "name": "Main.run",
                "file_path": f"{target_path}/app/main.py",
                "atom": "LOG.FNC.M",
                "ring": "LOG",
                "confidence": 80,
                "role_confidence": 80,
            },
            {
                "id": f"{target_path}/app/utils.py:Helper",
                "name": "Helper",
                "file_path": f"{target_path}/app/utils.py",
                "atom": "ORG.AGG.M",
                "ring": "ORG",
                "confidence": 1.0,
            },
        ],
        "edges": [
            {
                "source": f"{target_path}/app/main.py:Main.run",
                "target": f"{target_path}/app/utils.py:Helper",
                "edge_type": "calls",
                "confidence": 50,
            }
        ],
    }


def test_normalize_output_contract():
    target_path = "/tmp/project"
    data = _sample_output(target_path)
    normalized = normalize_output(data)

    # Meta must be present
    meta = normalized.get("meta", {})
    assert meta.get("target") == target_path
    assert meta.get("timestamp")
    assert meta.get("version")

    # Confidence must be canonical 0..1 with raw preserved
    node_conf = normalized["nodes"][0]["confidence"]
    assert 0.0 <= node_conf <= 1.0
    assert normalized["nodes"][0]["confidence_raw"] == 80
    assert normalized["nodes"][0]["role_confidence"] == 0.8
    assert normalized["nodes"][0]["role_confidence_raw"] == 80
    assert normalized["nodes"][0]["atom_family"] == "LOG"

    edge_conf = normalized["edges"][0]["confidence"]
    assert 0.0 <= edge_conf <= 1.0
    assert normalized["edges"][0]["confidence_raw"] == 50

    # IDs must be canonical (double-colon) and file paths relative
    assert "::" in normalized["nodes"][0]["id"]
    assert normalized["nodes"][0]["file_path"] == "app/main.py"
    assert normalized["nodes"][1]["file_path"] == "app/utils.py"

    errors, warnings = validate_contract(normalized)
    assert errors == []
    assert warnings == []


def test_normalize_output_idempotent():
    target_path = "/tmp/project"
    data = _sample_output(target_path)
    once = normalize_output(data)
    twice = normalize_output(once)
    assert once == twice


def test_normalize_output_file_paths_consistent():
    target_path = "/tmp/project"
    data = _sample_output(target_path)

    # Simulate mixed absolute/relative inputs.
    data["nodes"][0]["file_path"] = "app/main.py"
    data["nodes"][1]["file_path"] = "app/utils.py"
    data["file_boundaries"] = [
        {"file": f"{target_path}/app/main.py", "file_name": "main.py", "atom_count": 1},
        {"file": f"{target_path}/app/utils.py", "file_name": "utils.py", "atom_count": 1},
    ]
    data["files"] = {
        f"{target_path}/app/main.py": {"atom_names": ["Main.run"]},
        f"{target_path}/app/utils.py": {"atom_names": ["Helper"]},
    }

    normalized = normalize_output(data)
    boundary_files = {b.get("file") for b in normalized.get("file_boundaries", [])}
    assert boundary_files == {"app/main.py", "app/utils.py"}

    files_index = normalized.get("files", {})
    assert "app/main.py" in files_index
    assert "app/utils.py" in files_index
    assert f"{target_path}/app/main.py" not in files_index
    assert f"{target_path}/app/utils.py" not in files_index


# ---------------------------------------------------------------------------
# Locus tests
# ---------------------------------------------------------------------------

LOCUS_DIMS = ("physical", "architectural", "scale", "identity", "topological", "address")


def _rich_node():
    """A fully-populated node with all locus source fields."""
    return {
        "id": "core_auth.py::validate_token",
        "name": "validate_token",
        "file_path": "core_auth.py",
        "start_line": 149,
        "end_line": 160,
        "atom": "EXT.CTL.M",
        "layer": "Interface",
        "ring": "presentation",
        "tier": "T2",
        "level": "L3",
        "level_zone": "SYSTEMIC",
        "atom_family": "EXT",
        "role": "Controller",
        "kind": "function",
        "community_id": 1,
        "topology_role": "hub",
        "depth_from_entry": 1,
    }


def test_locus_stamped_after_normalize():
    """Full node gets all 6 locus dimensions."""
    target_path = "/tmp/project"
    data = {
        "target": target_path,
        "timestamp": "2026-01-01T00:00:00",
        "version": "0.0.1",
        "nodes": [_rich_node()],
        "edges": [],
    }
    normalized = normalize_output(data)
    node = normalized["nodes"][0]
    assert "locus" in node

    locus = node["locus"]
    for dim in LOCUS_DIMS:
        assert dim in locus, f"locus missing dimension: {dim}"

    assert locus["physical"] == "core_auth.py:149-160"
    assert locus["architectural"] == "Interface.presentation.T2"
    assert locus["scale"] == "L3.SYSTEMIC"
    assert locus["identity"] == "EXT.Controller.function"
    assert locus["topological"] == "C1.hub.d1"
    assert "Interface" in locus["address"]
    assert "core_auth.py" in locus["address"]


def test_locus_idempotent():
    """Normalizing twice produces identical locus."""
    target_path = "/tmp/project"
    data = {
        "target": target_path,
        "timestamp": "2026-01-01T00:00:00",
        "version": "0.0.1",
        "nodes": [_rich_node()],
        "edges": [],
    }
    once = normalize_output(data)
    locus_1 = once["nodes"][0]["locus"].copy()
    twice = normalize_output(once)
    locus_2 = twice["nodes"][0]["locus"]
    assert locus_1 == locus_2


def test_locus_partial_fields():
    """Sparse node gets '?' fallbacks, never crashes."""
    target_path = "/tmp/project"
    sparse_node = {
        "id": "bare.py::foo",
        "name": "foo",
        "file_path": "bare.py",
        "atom": "LOG.FNC.M",
    }
    data = {
        "target": target_path,
        "timestamp": "2026-01-01T00:00:00",
        "version": "0.0.1",
        "nodes": [sparse_node],
        "edges": [],
    }
    normalized = normalize_output(data)
    locus = normalized["nodes"][0]["locus"]

    for dim in LOCUS_DIMS:
        assert dim in locus, f"locus missing dimension: {dim}"
        assert isinstance(locus[dim], str)

    # Physical should have file but no line range
    assert "bare.py" in locus["physical"]
    # Missing fields should show "?"
    assert "?" in locus["architectural"]
    assert "?" in locus["topological"]


def test_validate_contract_locus_warning():
    """Missing locus produces a validation warning (not error)."""
    target_path = "/tmp/project"
    data = _sample_output(target_path)
    normalized = normalize_output(data)

    # Strip locus to simulate a pre-locus output
    for node in normalized["nodes"]:
        del node["locus"]

    errors, warnings = validate_contract(normalized)
    locus_warnings = [w for w in warnings if "locus" in w]
    assert len(locus_warnings) >= 1
