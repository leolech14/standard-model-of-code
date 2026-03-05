"""Tests for output_generator.py - stable output filename generation."""
import json
import pytest
from pathlib import Path
from src.core.output_generator import generate_outputs, write_llm_output


class TestStableOutputFilenames:
    """Tests for stable collider_output.json and unified_analysis.json symlink."""

    def test_stable_json_created(self, tmp_path):
        """Verify collider_output.json and unified_analysis.json symlink are created."""
        data = {
            "nodes": [{"id": "test"}],
            "edges": [],
            "meta": {"target": "test_project"}
        }

        outputs = generate_outputs(data, tmp_path, target_name="test")

        # Canonical and backward-compat files should exist
        assert outputs["llm"].exists()
        assert outputs["llm"].name == "collider_output.json"
        assert outputs["stable_json"].exists()
        assert outputs["stable_json"].name == "unified_analysis.json"

        # Content should be identical (symlink)
        canonical_content = outputs["llm"].read_text()
        stable_content = outputs["stable_json"].read_text()
        assert canonical_content == stable_content

    def test_html_created(self, tmp_path):
        """Verify HTML report is created when skip_html=False."""
        # app.js is a Vite build artifact, not git-tracked -- skip if absent (e.g. worktrees)
        assets_dir = Path(__file__).resolve().parent.parent / "src" / "core" / "viz" / "assets"
        if not (assets_dir / "app.js").exists():
            pytest.skip("viz/assets/app.js not built (run Vite build first)")

        data = {
            "nodes": [{"id": "test", "kind": "function"}],
            "edges": [],
            "meta": {"target": "test_project"}
        }

        outputs = generate_outputs(data, tmp_path, target_name="test", skip_html=False)

        assert outputs["html"].exists()

    def test_stable_json_content_valid(self, tmp_path):
        """Verify unified_analysis.json contains valid JSON with expected structure."""
        data = {
            "nodes": [{"id": "func1", "semantic_role": "utility"}],
            "edges": [{"source": "a", "target": "b"}],
            "semantic_analysis": {
                "entry_points": ["main"],
                "role_distribution": {"utility": 1}
            }
        }

        outputs = generate_outputs(data, tmp_path, target_name="test")

        # Load and verify structure
        loaded = json.loads(outputs["stable_json"].read_text())
        assert "nodes" in loaded
        assert "edges" in loaded

    def test_multiple_runs_overwrite_stable(self, tmp_path):
        """Verify stable files are overwritten on subsequent runs."""
        data1 = {"nodes": [{"id": "v1"}], "edges": [], "meta": {"target": "t"}}
        data2 = {"nodes": [{"id": "v2"}], "edges": [], "meta": {"target": "t"}}

        # First run
        generate_outputs(data1, tmp_path, target_name="test", timestamp="20260101_000001")

        # Second run
        outputs2 = generate_outputs(data2, tmp_path, target_name="test", timestamp="20260101_000002")
        stable_content2 = outputs2["stable_json"].read_text()

        # Stable file should have new content
        assert "v2" in stable_content2
        assert "v1" not in stable_content2


class TestWriteLlmOutput:
    """Tests for write_llm_output function."""

    def test_creates_directory(self, tmp_path):
        """Verify output directory is created if it doesn't exist."""
        nested_dir = tmp_path / "nested" / "output"
        data = {"test": "data"}

        path = write_llm_output(data, nested_dir, filename="test.json")

        assert path.exists()
        assert nested_dir.exists()

    def test_json_formatting(self, tmp_path):
        """Verify JSON is properly formatted with indentation."""
        data = {"nodes": [{"id": "test"}]}

        path = write_llm_output(data, tmp_path, filename="test.json")
        content = path.read_text()

        # Should be indented (pretty-printed)
        assert "\n" in content
        assert "  " in content  # 2-space indent
