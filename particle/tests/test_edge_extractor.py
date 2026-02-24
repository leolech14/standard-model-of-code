"""Unit tests for edge_extractor core helpers and resolution logic."""

from pathlib import Path

import pytest

from src.core import edge_extractor as ee


def test_file_node_name_and_id_handle_collisions(tmp_path):
    file_path = str(tmp_path / "pkg" / "main.py")
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    Path(file_path).write_text("def f():\n    return 1\n")

    normalized = str(Path(file_path).resolve())
    existing = {
        ee._make_node_id(normalized, "main"),
        ee._make_node_id(normalized, "main.__file__"),
    }

    name = ee.file_node_name(file_path, existing)
    node_id = ee.file_node_id(file_path, existing)

    assert name == "main.__file__2"
    assert node_id == f"{normalized}:main.__file__2"


def test_find_target_particle_prefers_same_file_then_imports_then_first():
    particle_by_name = {
        "helper": [
            {"name": "helper", "file_path": "/tmp/a.py"},
            {"name": "helper", "file_path": "/tmp/b.py"},
        ]
    }

    same_file = ee._find_target_particle("helper", "/tmp/b.py", particle_by_name)
    assert same_file["file_path"] == "/tmp/b.py"

    import_based = ee._find_target_particle(
        "helper",
        "/tmp/c.py",
        {
            "helper": [
                {"name": "helper", "file_path": "/tmp/math.py"},
                {"name": "helper", "file_path": "/tmp/other.py"},
            ]
        },
        caller_imports=[{"module": "pkg.math"}],
    )
    assert import_based["file_path"] == "/tmp/math.py"

    fallback = ee._find_target_particle(
        "helper",
        "/tmp/c.py",
        {
            "helper": [
                {"name": "helper", "file_path": "/tmp/first.py"},
                {"name": "helper", "file_path": "/tmp/second.py"},
            ]
        },
        caller_imports=[{"module": "pkg.unknown"}],
    )
    assert fallback["file_path"] == "/tmp/first.py"


def test_extract_exposure_edges_from_body_supports_js_and_python_patterns():
    body = """
module.exports = CoreApi
module.exports.Named = NamedApi
exports.Alias = AliasApi
export function fnA() {}
export class Thing {}
export default MainSymbol
export { localX as X, localY }
__all__ = ["py_a", "py_b"]
"""
    exposures = ee._extract_exposure_edges_from_body(body, "/tmp/mod.js", {})

    assert ("CoreApi", "commonjs") in exposures
    assert ("Named", "commonjs") in exposures
    assert ("Alias", "commonjs") in exposures
    assert ("fnA", "named") in exposures
    assert ("Thing", "named") in exposures
    assert ("MainSymbol", "default") in exposures
    assert ("localX", "named") in exposures
    assert ("localY", "named") in exposures
    assert ("py_a", "python_all") in exposures
    assert ("py_b", "python_all") in exposures


def test_extract_exposure_edges_prefers_module_level_results(tmp_path):
    file_path = tmp_path / "mod.js"
    file_path.write_text("module.exports = exportedSym\n")
    file_path_str = str(file_path)
    source_module_id = ee._make_node_id(file_path_str, "__module__")

    particles = [
        {
            "id": ee._make_node_id(file_path_str, "exportedSym"),
            "name": "exportedSym",
            "file_path": file_path_str,
            "body_source": "module.exports = exportedSym",  # Would duplicate if module-level not preferred.
            "line": 3,
        }
    ]
    results = [
        {
            "file_path": file_path_str,
            "raw_content": "module.exports = exportedSym",
        }
    ]

    edges = ee.extract_exposure_edges(particles, results=results)

    assert len(edges) == 1
    assert edges[0]["source"] == source_module_id
    assert edges[0]["target"] == ee._make_node_id(file_path_str, "exportedSym")
    assert edges[0]["edge_type"] == "exposes"
    assert edges[0]["metadata"]["export_type"] == "commonjs"


def test_resolve_import_target_to_file_handles_success_and_ambiguity(tmp_path):
    root = tmp_path / "repo"
    (root / "pkg").mkdir(parents=True)
    (root / "pkg" / "mod.py").write_text("X = 1\n")
    resolved, ambiguous = ee.resolve_import_target_to_file("pkg.mod", str(root))
    assert ambiguous is False
    assert resolved == str((root / "pkg" / "mod.py").resolve())

    # Ambiguous when both pkg.py and pkg/__init__.py exist.
    (root / "pkg.py").write_text("Y = 1\n")
    (root / "pkg" / "__init__.py").write_text("Z = 1\n")
    resolved2, ambiguous2 = ee.resolve_import_target_to_file("pkg", str(root))
    assert resolved2 is None
    assert ambiguous2 is True


def test_resolve_edges_classifies_internal_external_and_unresolved(tmp_path):
    root = tmp_path / "repo"
    pkg = root / "pkg"
    pkg.mkdir(parents=True)
    mod = pkg / "mod.py"
    mod.write_text("VALUE = 1\n")
    mod_resolved = str(mod.resolve())

    source = f"{mod_resolved}:caller"
    internal_target = f"{mod_resolved}:callee"
    file_node_target = f"{mod_resolved}:mod.__file__"

    node_ids = {source, internal_target, file_node_target}
    file_node_ids = {mod_resolved: file_node_target}
    edges = [
        {"source": source, "target": internal_target, "edge_type": "calls"},
        {"source": source, "target": "pkg.mod", "edge_type": "imports"},
        {"source": source, "target": "json", "edge_type": "imports"},
        {"source": source, "target": "unknown_pkg.alpha", "edge_type": "imports"},
    ]

    resolved = ee.resolve_edges(edges, node_ids, target_root=str(root), file_node_ids=file_node_ids)
    by_target = {edge["target"]: edge for edge in resolved}

    assert by_target[internal_target]["resolution"] == "resolved_internal"
    assert by_target[file_node_target]["resolution"] == "resolved_internal"
    assert by_target["json"]["resolution"] == "external"
    assert by_target["unknown_pkg.alpha"]["resolution"] == "unresolved"


def test_proof_edge_and_resolution_diagnostics():
    edges = [
        {"source": "a", "target": "b", "edge_type": "calls", "resolution": "resolved_internal"},
        {"source": "a", "target": "json", "edge_type": "imports", "resolution": "external"},
        {
            "source": "a",
            "target": "mystery.pkg",
            "edge_type": "imports",
            "resolution": "unresolved",
            "metadata": {"import_resolution": "resolved_to_file_no_node"},
        },
        {
            "source": "a",
            "target": "ambiguous.pkg",
            "edge_type": "imports",
            "resolution": "unresolved",
            "metadata": {"import_resolution": "ambiguous"},
        },
    ]

    proof = ee.get_proof_edges(edges)
    summary = ee.get_edge_resolution_summary(edges)
    counts, unresolved_roots = ee.get_import_resolution_diagnostics(edges)

    assert proof == [edges[0]]
    assert summary["calls"]["resolved_internal"] == 1
    assert summary["imports"]["external"] == 1
    assert summary["imports"]["unresolved"] == 2

    assert counts["attempted"] == 3
    assert counts["resolved_internal"] == 0
    assert counts["external"] == 1
    assert counts["unresolved"] == 2
    assert counts["resolved_to_file_no_node"] == 1
    assert counts["ambiguous"] == 1
    assert "mystery" in unresolved_roots


def test_get_strategy_for_file_falls_back_when_tree_sitter_disabled(monkeypatch):
    monkeypatch.setattr(ee, "TREE_SITTER_AVAILABLE", False)

    assert isinstance(ee.get_strategy_for_file("x.py"), ee.PythonEdgeStrategy)
    assert isinstance(ee.get_strategy_for_file("x.js"), ee.JavascriptEdgeStrategy)
    assert isinstance(ee.get_strategy_for_file("x.ts"), ee.TypeScriptEdgeStrategy)
    assert isinstance(ee.get_strategy_for_file("x.go"), ee.GoEdgeStrategy)
    assert isinstance(ee.get_strategy_for_file("x.rs"), ee.RustEdgeStrategy)
    assert isinstance(ee.get_strategy_for_file("x.unknown"), ee.DefaultEdgeStrategy)


def test_extract_call_edges_builds_import_contains_inherits_and_calls(monkeypatch, tmp_path):
    monkeypatch.setattr(ee, "TREE_SITTER_AVAILABLE", False)

    file_path = str((tmp_path / "a.py").resolve())
    particles = [
        {
            "id": ee._make_node_id(file_path, "a.__file__"),
            "name": "a.__file__",
            "file_path": file_path,
            "metadata": {"file_node": True},
            "body_source": "",
            "line": 0,
        },
        {
            "id": ee._make_node_id(file_path, "Base"),
            "name": "Base",
            "file_path": file_path,
            "base_classes": [],
            "body_source": "",
            "line": 1,
        },
        {
            "id": ee._make_node_id(file_path, "Child"),
            "name": "Child",
            "file_path": file_path,
            "base_classes": ["Base"],
            "body_source": "",
            "line": 2,
        },
        {
            "id": ee._make_node_id(file_path, "helper"),
            "name": "helper",
            "file_path": file_path,
            "parent": "Child",
            "base_classes": [],
            "body_source": "",
            "line": 3,
        },
        {
            "id": ee._make_node_id(file_path, "foo"),
            "name": "foo",
            "file_path": file_path,
            "base_classes": [],
            "body_source": "helper()",
            "line": 4,
        },
    ]
    results = [
        {
            "file_path": file_path,
            "raw_imports": [{"module": "json", "line": 1}],
            "raw_content": "",
        }
    ]

    edges = ee.extract_call_edges(particles, results, target_path=str(tmp_path))

    assert any(
        edge["edge_type"] == "imports" and edge["target"] == "json" and edge["resolution"] == "external"
        for edge in edges
    )
    assert any(
        edge["edge_type"] == "contains"
        and edge["source"] == ee._make_node_id(file_path, "Child")
        and edge["target"] == ee._make_node_id(file_path, "helper")
        and edge["resolution"] == "resolved_internal"
        for edge in edges
    )
    assert any(
        edge["edge_type"] == "inherits"
        and edge["source"] == ee._make_node_id(file_path, "Child")
        and edge["target"] == ee._make_node_id(file_path, "Base")
        and edge["resolution"] == "resolved_internal"
        for edge in edges
    )
    assert any(
        edge["edge_type"] == "calls"
        and edge["source"] == ee._make_node_id(file_path, "foo")
        and edge["target"] == ee._make_node_id(file_path, "helper")
        and edge["resolution"] == "resolved_internal"
        for edge in edges
    )
