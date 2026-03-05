#!/usr/bin/env python3
"""
Tests for the three-tier output system:
    - Meta-envelope builder
    - Tier 2 AI briefing
    - Tier 3 HTML report
    - Meta-index JSONL append
    - Output generator tier integration
    - Backward compatibility (symlinks, key names)
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict
from unittest.mock import patch

import pytest


# ── Fixtures ──────────────────────────────────────────────────────────


def _make_full_output(**overrides) -> Dict[str, Any]:
    """Build a minimal but complete full_output dict for testing."""
    base = {
        "meta": {
            "target": "/tmp/test-repo",
            "timestamp": "2026-03-05T14:30:00+00:00",
            "analysis_time_ms": 12340,
            "version": "4.0.0",
            "schema_version": "1.0.0",
        },
        "counts": {
            "nodes": 100,
            "edges": 200,
            "files": 42,
            "entry_points": 5,
            "orphans": 2,
            "cycles": 1,
        },
        "stats": {
            "language_distribution": {"python": 0.85, "yaml": 0.10, "json": 0.05},
        },
        "kpis": {
            "avg_complexity": 3.2,
            "test_coverage_ratio": 0.65,
        },
        "nodes": [{"id": f"n{i}", "name": f"node_{i}", "type": "function"} for i in range(5)],
        "edges": [{"source": "n0", "target": "n1", "edge_type": "calls"}],
        "compiled_insights": _make_compiled_insights(),
    }
    base.update(overrides)
    return base


def _make_compiled_insights(**overrides) -> Dict[str, Any]:
    """Minimal compiled_insights for testing."""
    base = {
        "grade": "B+",
        "health_score": 7.2,
        "health_components": {
            "architecture": 8.1,
            "complexity": 6.5,
            "maintainability": 7.0,
            "reliability": 7.5,
            "testability": 6.0,
            "documentation": 5.5,
            "security": 8.0,
        },
        "executive_summary": "The codebase shows solid architecture with room for improvement in documentation and testability.",
        "findings_count": 3,
        "findings": [
            {
                "severity": "high",
                "category": "complexity",
                "title": "High cyclomatic complexity in core module",
                "description": "The core processing module has functions exceeding complexity threshold of 10.",
                "recommendation": "Refactor complex functions into smaller, focused units.",
                "confidence": 0.85,
                "related_nodes": ["n1", "n2", "n3"],
            },
            {
                "severity": "medium",
                "category": "documentation",
                "title": "Missing docstrings in public API",
                "description": "Several public functions lack documentation.",
                "recommendation": "Add docstrings to all public API functions.",
                "confidence": 0.92,
                "related_nodes": ["n4"],
            },
            {
                "severity": "low",
                "category": "style",
                "title": "Inconsistent naming conventions",
                "description": "Mix of snake_case and camelCase detected.",
                "recommendation": "Standardize on snake_case per PEP 8.",
                "confidence": 0.78,
                "related_nodes": [],
            },
        ],
        "mission_matrix": {
            "execution": 85,
            "performance": 72,
            "reliability": 78,
            "security": 90,
        },
        "navigation": {
            "start_here": ["src/core/main.py", "src/core/config.py"],
            "critical_path": ["src/core/processor.py", "src/core/pipeline.py"],
            "top_risks": ["src/legacy/old_handler.py"],
        },
    }
    base.update(overrides)
    return base


@pytest.fixture
def full_output():
    return _make_full_output()


@pytest.fixture
def compiled_insights():
    return _make_compiled_insights()


@pytest.fixture
def target_path(tmp_path):
    repo = tmp_path / "test-repo"
    repo.mkdir()
    return repo


@pytest.fixture
def options():
    return {"skip_html": False, "verbose_output": False}


# ── Meta-Envelope Tests ──────────────────────────────────────────────


class TestMetaEnvelope:
    """Tests for src.core.meta_envelope.build_meta_envelope."""

    def test_all_fields_present(self, full_output, target_path, options):
        from src.core.meta_envelope import build_meta_envelope

        env = build_meta_envelope(full_output, target_path, options)
        required_fields = {
            "repo_id", "run_id", "run_ts", "collider_version",
            "schema_version", "target", "target_path", "node_count",
            "edge_count", "file_count", "language_mix",
            "analysis_time_ms", "config_hash", "hostname",
            "grade", "health_score",
        }
        assert required_fields.issubset(set(env.keys())), (
            f"Missing fields: {required_fields - set(env.keys())}"
        )

    def test_repo_id_is_stable(self, full_output, target_path, options):
        from src.core.meta_envelope import build_meta_envelope

        env1 = build_meta_envelope(full_output, target_path, options)
        env2 = build_meta_envelope(full_output, target_path, options)
        assert env1["repo_id"] == env2["repo_id"], "repo_id should be stable across runs"

    def test_run_id_is_unique(self, full_output, target_path, options):
        from src.core.meta_envelope import build_meta_envelope

        env1 = build_meta_envelope(full_output, target_path, options)
        env2 = build_meta_envelope(full_output, target_path, options)
        assert env1["run_id"] != env2["run_id"], "run_id should be unique per run"

    def test_field_types(self, full_output, target_path, options):
        from src.core.meta_envelope import build_meta_envelope

        env = build_meta_envelope(full_output, target_path, options)
        assert isinstance(env["repo_id"], str) and len(env["repo_id"]) == 12
        assert isinstance(env["run_id"], str) and len(env["run_id"]) == 36  # UUID4
        assert isinstance(env["run_ts"], str) and "T" in env["run_ts"]
        assert isinstance(env["node_count"], int)
        assert isinstance(env["edge_count"], int)
        assert isinstance(env["language_mix"], dict)
        assert isinstance(env["health_score"], (int, float))
        assert isinstance(env["config_hash"], str) and len(env["config_hash"]) == 8

    def test_grade_from_insights(self, full_output, target_path, options):
        from src.core.meta_envelope import build_meta_envelope

        env = build_meta_envelope(full_output, target_path, options)
        assert env["grade"] == "B+"
        assert env["health_score"] == 7.2

    def test_schema_version(self, full_output, target_path, options):
        from src.core.meta_envelope import build_meta_envelope

        env = build_meta_envelope(full_output, target_path, options)
        assert env["schema_version"] == "1.0.0"


class TestMetaIndex:
    """Tests for append_to_meta_index JSONL functionality."""

    def test_append_creates_file(self, full_output, target_path, options):
        from src.core.meta_envelope import build_meta_envelope, append_to_meta_index

        env = build_meta_envelope(full_output, target_path, options)
        with tempfile.TemporaryDirectory() as tmpdir:
            idx = append_to_meta_index(env, Path(tmpdir))
            assert idx.exists()
            lines = idx.read_text().strip().split("\n")
            assert len(lines) == 1
            parsed = json.loads(lines[0])
            assert parsed["repo_id"] == env["repo_id"]

    def test_append_is_additive(self, full_output, target_path, options):
        from src.core.meta_envelope import build_meta_envelope, append_to_meta_index

        with tempfile.TemporaryDirectory() as tmpdir:
            for _ in range(3):
                env = build_meta_envelope(full_output, target_path, options)
                append_to_meta_index(env, Path(tmpdir))

            lines = (Path(tmpdir) / "meta_index.jsonl").read_text().strip().split("\n")
            assert len(lines) == 3
            # Each line must be valid JSON
            for line in lines:
                parsed = json.loads(line)
                assert "run_id" in parsed

    def test_different_run_ids_same_repo_id(self, full_output, target_path, options):
        from src.core.meta_envelope import build_meta_envelope, append_to_meta_index

        with tempfile.TemporaryDirectory() as tmpdir:
            envs = []
            for _ in range(2):
                env = build_meta_envelope(full_output, target_path, options)
                append_to_meta_index(env, Path(tmpdir))
                envs.append(env)

            assert envs[0]["repo_id"] == envs[1]["repo_id"]
            assert envs[0]["run_id"] != envs[1]["run_id"]


# ── Tier 2: AI Briefing Tests ────────────────────────────────────────


class TestTier2Briefing:
    """Tests for src.core.tier2_briefing.build_briefing."""

    def test_briefing_structure(self, compiled_insights, full_output):
        from src.core.tier2_briefing import build_briefing
        from src.core.meta_envelope import build_meta_envelope

        env = build_meta_envelope(full_output, Path("/tmp/test"), {})
        briefing = build_briefing(compiled_insights, full_output, env)

        required_keys = {
            "meta_envelope", "executive_summary", "grade", "health_score",
            "health_components", "mission_matrix", "top_findings",
            "stats_summary", "navigation",
        }
        assert required_keys.issubset(set(briefing.keys()))

    def test_finding_limit(self, full_output):
        """Briefing should contain at most 5 findings."""
        from src.core.tier2_briefing import build_briefing
        from src.core.meta_envelope import build_meta_envelope

        # Create insights with 10 findings
        insights = _make_compiled_insights()
        insights["findings"] = [
            {
                "severity": "medium",
                "category": f"cat_{i}",
                "title": f"Finding {i}",
                "description": f"Description for finding {i}",
                "recommendation": f"Fix finding {i}",
                "confidence": 0.5 + i * 0.04,
                "related_nodes": [f"n{i}"],
            }
            for i in range(10)
        ]

        env = build_meta_envelope(full_output, Path("/tmp/test"), {})
        briefing = build_briefing(insights, full_output, env)
        assert len(briefing["top_findings"]) <= 5

    def test_text_truncation(self, full_output):
        """Long text fields should be truncated."""
        from src.core.tier2_briefing import build_briefing
        from src.core.meta_envelope import build_meta_envelope

        insights = _make_compiled_insights()
        insights["findings"] = [{
            "severity": "high",
            "category": "test",
            "title": "A" * 200,          # Over 80 limit
            "description": "B" * 500,     # Over 200 limit
            "recommendation": "C" * 500,  # Over 200 limit
            "confidence": 0.9,
            "related_nodes": [],
        }]

        env = build_meta_envelope(full_output, Path("/tmp/test"), {})
        briefing = build_briefing(insights, full_output, env)
        finding = briefing["top_findings"][0]
        assert len(finding["title"]) <= 80
        assert len(finding["description"]) <= 200
        assert len(finding["recommendation"]) <= 200

    def test_severity_sort_order(self, full_output):
        """Findings should be sorted by severity (critical first)."""
        from src.core.tier2_briefing import build_briefing
        from src.core.meta_envelope import build_meta_envelope

        insights = _make_compiled_insights()
        insights["findings"] = [
            {"severity": "low", "category": "a", "title": "Low", "description": "", "recommendation": "", "confidence": 0.9, "related_nodes": []},
            {"severity": "critical", "category": "b", "title": "Critical", "description": "", "recommendation": "", "confidence": 0.8, "related_nodes": []},
            {"severity": "high", "category": "c", "title": "High", "description": "", "recommendation": "", "confidence": 0.7, "related_nodes": []},
        ]

        env = build_meta_envelope(full_output, Path("/tmp/test"), {})
        briefing = build_briefing(insights, full_output, env)
        severities = [f["severity"] for f in briefing["top_findings"]]
        assert severities == ["critical", "high", "low"]

    def test_stats_summary_keys(self, compiled_insights, full_output):
        """Stats summary should have expected KPI keys."""
        from src.core.tier2_briefing import build_briefing
        from src.core.meta_envelope import build_meta_envelope

        env = build_meta_envelope(full_output, Path("/tmp/test"), {})
        briefing = build_briefing(compiled_insights, full_output, env)
        stats = briefing["stats_summary"]
        for key in ("files", "nodes", "edges", "avg_complexity", "test_coverage_ratio", "entry_points", "orphan_ratio", "cycle_count"):
            assert key in stats, f"Missing KPI: {key}"

    def test_related_nodes_flattened(self, compiled_insights, full_output):
        """related_nodes should be flattened to count."""
        from src.core.tier2_briefing import build_briefing
        from src.core.meta_envelope import build_meta_envelope

        env = build_meta_envelope(full_output, Path("/tmp/test"), {})
        briefing = build_briefing(compiled_insights, full_output, env)
        for finding in briefing["top_findings"]:
            assert "related_node_count" in finding
            assert isinstance(finding["related_node_count"], int)
            assert "related_nodes" not in finding


# ── Tier 3: HTML Report Tests ────────────────────────────────────────


class TestTier3HtmlReport:
    """Tests for src.core.tier3_html_report.build_html_report."""

    def test_returns_valid_html(self, compiled_insights, full_output):
        from src.core.tier3_html_report import build_html_report
        from src.core.meta_envelope import build_meta_envelope

        env = build_meta_envelope(full_output, Path("/tmp/test"), {})
        html = build_html_report(compiled_insights, full_output, env)
        assert html.startswith("<!DOCTYPE html>")
        assert "</html>" in html

    def test_self_contained_no_external_refs(self, compiled_insights, full_output):
        """HTML should have no external stylesheet or script references."""
        from src.core.tier3_html_report import build_html_report
        from src.core.meta_envelope import build_meta_envelope

        env = build_meta_envelope(full_output, Path("/tmp/test"), {})
        html = build_html_report(compiled_insights, full_output, env)
        # No external CSS links
        assert 'rel="stylesheet"' not in html or "href=" not in html
        # No external script srcs (inline is OK)
        assert '<script src=' not in html

    def test_contains_all_sections(self, compiled_insights, full_output):
        from src.core.tier3_html_report import build_html_report
        from src.core.meta_envelope import build_meta_envelope

        env = build_meta_envelope(full_output, Path("/tmp/test"), {})
        html = build_html_report(compiled_insights, full_output, env)
        # Check key section identifiers
        assert "Executive Summary" in html
        assert "Health Dashboard" in html
        assert "Architecture Overview" in html
        assert "Generated by Collider" in html

    def test_grade_badge_present(self, compiled_insights, full_output):
        from src.core.tier3_html_report import build_html_report
        from src.core.meta_envelope import build_meta_envelope

        env = build_meta_envelope(full_output, Path("/tmp/test"), {})
        html = build_html_report(compiled_insights, full_output, env)
        assert "B+" in html  # Grade badge

    def test_inline_svg_charts(self, compiled_insights, full_output):
        """Should contain inline SVG elements for charts."""
        from src.core.tier3_html_report import build_html_report
        from src.core.meta_envelope import build_meta_envelope

        env = build_meta_envelope(full_output, Path("/tmp/test"), {})
        html = build_html_report(compiled_insights, full_output, env)
        assert "<svg" in html
        assert "</svg>" in html


# ── Output Generator Integration Tests ───────────────────────────────


class TestOutputGeneratorTiers:
    """Integration tests for generate_outputs tier system."""

    def test_tier1_raw_created(self, full_output):
        from src.core.output_generator import generate_outputs
        from src.core.meta_envelope import build_meta_envelope

        env = build_meta_envelope(full_output, Path("/tmp/test"), {})

        with tempfile.TemporaryDirectory() as tmpdir:
            result = generate_outputs(
                full_output, tmpdir,
                target_name="test",
                skip_html=True,
                meta_envelope=env,
            )
            raw_path = Path(tmpdir) / "collider_raw.json"
            assert raw_path.exists()
            assert result["raw"] == raw_path
            # Verify meta_envelope embedded
            with open(raw_path) as f:
                data = json.load(f)
            assert "meta_envelope" in data
            assert data["meta_envelope"]["repo_id"] == env["repo_id"]

    def test_tier2_briefing_created(self, full_output):
        from src.core.output_generator import generate_outputs
        from src.core.meta_envelope import build_meta_envelope

        env = build_meta_envelope(full_output, Path("/tmp/test"), {})

        with tempfile.TemporaryDirectory() as tmpdir:
            result = generate_outputs(
                full_output, tmpdir,
                target_name="test",
                skip_html=True,
                meta_envelope=env,
            )
            briefing_path = Path(tmpdir) / "collider_briefing.json"
            assert briefing_path.exists()
            assert result["briefing"] == briefing_path

    def test_tier3_report_created(self, full_output):
        from src.core.output_generator import generate_outputs
        from src.core.meta_envelope import build_meta_envelope

        env = build_meta_envelope(full_output, Path("/tmp/test"), {})

        with tempfile.TemporaryDirectory() as tmpdir:
            result = generate_outputs(
                full_output, tmpdir,
                target_name="test",
                skip_html=False,
                meta_envelope=env,
            )
            report_path = Path(tmpdir) / "collider_report.html"
            assert report_path.exists()
            assert result["report_html"] == report_path

    def test_backward_compat_symlinks(self, full_output):
        from src.core.output_generator import generate_outputs
        from src.core.meta_envelope import build_meta_envelope

        env = build_meta_envelope(full_output, Path("/tmp/test"), {})

        with tempfile.TemporaryDirectory() as tmpdir:
            generate_outputs(
                full_output, tmpdir,
                target_name="test",
                skip_html=True,
                meta_envelope=env,
            )
            # Both symlinks should exist and point to collider_raw.json
            for name in ("collider_output.json", "unified_analysis.json"):
                sym = Path(tmpdir) / name
                assert sym.is_symlink(), f"{name} should be a symlink"
                assert os.readlink(str(sym)) == "collider_raw.json"

    def test_llm_key_backward_compat(self, full_output):
        from src.core.output_generator import generate_outputs
        from src.core.meta_envelope import build_meta_envelope

        env = build_meta_envelope(full_output, Path("/tmp/test"), {})

        with tempfile.TemporaryDirectory() as tmpdir:
            result = generate_outputs(
                full_output, tmpdir,
                target_name="test",
                skip_html=True,
                meta_envelope=env,
            )
            # "llm" key should still exist, pointing to Tier 1
            assert "llm" in result
            assert result["llm"] == result["raw"]

    def test_meta_index_created(self, full_output):
        from src.core.output_generator import generate_outputs
        from src.core.meta_envelope import build_meta_envelope

        env = build_meta_envelope(full_output, Path("/tmp/test"), {})

        with tempfile.TemporaryDirectory() as tmpdir:
            result = generate_outputs(
                full_output, tmpdir,
                target_name="test",
                skip_html=True,
                meta_envelope=env,
            )
            idx = Path(tmpdir) / "meta_index.jsonl"
            assert idx.exists()
            lines = idx.read_text().strip().split("\n")
            assert len(lines) == 1
            parsed = json.loads(lines[0])
            assert parsed["run_id"] == env["run_id"]

    def test_insights_files_still_emitted(self, full_output):
        from src.core.output_generator import generate_outputs
        from src.core.meta_envelope import build_meta_envelope

        env = build_meta_envelope(full_output, Path("/tmp/test"), {})

        with tempfile.TemporaryDirectory() as tmpdir:
            result = generate_outputs(
                full_output, tmpdir,
                target_name="test",
                skip_html=True,
                meta_envelope=env,
            )
            assert (Path(tmpdir) / "collider_insights.json").exists()

    def test_webgl_off_by_default(self, full_output):
        from src.core.output_generator import generate_outputs
        from src.core.meta_envelope import build_meta_envelope

        env = build_meta_envelope(full_output, Path("/tmp/test"), {})

        with tempfile.TemporaryDirectory() as tmpdir:
            result = generate_outputs(
                full_output, tmpdir,
                target_name="test",
                skip_html=False,
                meta_envelope=env,
            )
            # WebGL HTML should NOT be created by default (no --webgl flag)
            assert "html" not in result

    def test_skip_html_skips_tier3(self, full_output):
        from src.core.output_generator import generate_outputs
        from src.core.meta_envelope import build_meta_envelope

        env = build_meta_envelope(full_output, Path("/tmp/test"), {})

        with tempfile.TemporaryDirectory() as tmpdir:
            result = generate_outputs(
                full_output, tmpdir,
                target_name="test",
                skip_html=True,
                meta_envelope=env,
            )
            assert "report_html" not in result
            assert not (Path(tmpdir) / "collider_report.html").exists()


# ── Normalize Output Tests ───────────────────────────────────────────


class TestNormalizeSchemaVersion:
    """Tests for schema_version in normalize_output."""

    def test_schema_version_default(self):
        from src.core.normalize_output import normalize_meta

        data = {"meta": {"target": "test", "timestamp": "now", "version": "4.0.0"}}
        meta = normalize_meta(data)
        assert meta["schema_version"] == "1.0.0"

    def test_schema_version_preserved(self):
        from src.core.normalize_output import normalize_meta

        data = {"meta": {"target": "test", "timestamp": "now", "version": "4.0.0", "schema_version": "2.0.0"}}
        meta = normalize_meta(data)
        assert meta["schema_version"] == "2.0.0"
