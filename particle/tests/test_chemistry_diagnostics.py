"""Tests for Chemistry Diagnostics — detector trace output."""

import pytest
from src.core.data_chemistry import ChemistryLab


def _make_full_output(**overrides):
    """Create a minimal full_output dict for ChemistryLab.ingest()."""
    base = {
        "nodes": [],
        "edges": [],
        "smart_ignore": {"noise_ratio": 0.1, "total_files": 100, "ignored_count": 10},
        "classification": {"classified_percent": 90, "unclassified_percent": 10},
        "kpis": {
            "dead_code_percent": 3.0,
            "knot_score": 0.5,
            "codebase_intelligence": 0.95,
        },
        "warnings": [],
        "recommendations": [],
    }
    base.update(overrides)
    return base


class TestBuildDiagnostics:
    def test_returns_dict(self):
        lab = ChemistryLab()
        lab.ingest(_make_full_output())
        diag = lab.build_diagnostics()
        assert isinstance(diag, dict)
        assert "signal_values" in diag
        assert "signal_coverage" in diag
        assert "detector_traces" in diag

    def test_signal_coverage_present(self):
        lab = ChemistryLab()
        lab.ingest(_make_full_output())
        diag = lab.build_diagnostics()
        coverage = diag["signal_coverage"]
        # noise_ratio was provided, should be "present"
        assert coverage.get("noise_ratio") == "present"
        # boundary_ratio not in the output, should be "missing"
        assert coverage.get("boundary_ratio") == "missing"

    def test_always_extractors_present(self):
        lab = ChemistryLab()
        lab.ingest(_make_full_output())
        diag = lab.build_diagnostics()
        values = diag["signal_values"]
        # These come from _ALWAYS_EXTRACTORS
        assert "dead_code_pct" in values
        assert "knot_score" in values
        assert "codebase_intelligence" in values

    def test_five_detector_traces(self):
        lab = ChemistryLab()
        lab.ingest(_make_full_output())
        diag = lab.build_diagnostics()
        traces = diag["detector_traces"]
        assert len(traces) == 5
        names = {t["detector"] for t in traces}
        assert names == {
            "flying_blind",
            "hollow_architecture",
            "dependency_sprawl",
            "purpose_vacuum",
            "advisory_storm",
        }

    def test_healthy_codebase_no_detectors_fire(self):
        """High CI + low dead code = all detectors should report fired=False."""
        lab = ChemistryLab()
        lab.ingest(_make_full_output())
        diag = lab.build_diagnostics()
        for trace in diag["detector_traces"]:
            assert trace["fired"] is False, f"{trace['detector']} should not fire"

    def test_detector_traces_have_conditions(self):
        lab = ChemistryLab()
        lab.ingest(_make_full_output())
        diag = lab.build_diagnostics()
        for trace in diag["detector_traces"]:
            assert "conditions" in trace
            assert "reason" in trace
            assert "gate" in trace
            for cond in trace["conditions"]:
                assert "check" in cond
                assert "threshold" in cond
                assert "actual" in cond
                assert "passed" in cond

    def test_json_serializable(self):
        import json
        lab = ChemistryLab()
        lab.ingest(_make_full_output())
        diag = lab.build_diagnostics()
        # Should not raise
        json.dumps(diag)


class TestDetectorTraceLogic:
    def test_hollow_architecture_fires_with_high_dead_code(self):
        lab = ChemistryLab()
        lab.ingest(_make_full_output(
            kpis={"dead_code_percent": 25.0, "knot_score": 5.0, "codebase_intelligence": 0.3}
        ))
        diag = lab.build_diagnostics()
        hollow = next(t for t in diag["detector_traces"] if t["detector"] == "hollow_architecture")
        assert hollow["fired"] is True

    def test_advisory_storm_fires_with_many_warnings(self):
        lab = ChemistryLab()
        lab.ingest(_make_full_output(
            warnings=[{"msg": f"w{i}"} for i in range(10)],
            recommendations=[{"msg": f"r{i}"} for i in range(10)],
        ))
        diag = lab.build_diagnostics()
        storm = next(t for t in diag["detector_traces"] if t["detector"] == "advisory_storm")
        assert storm["fired"] is True
        assert "20" in storm["reason"]

    def test_purpose_vacuum_fires_with_low_ci(self):
        lab = ChemistryLab()
        lab.ingest(_make_full_output(
            kpis={"dead_code_percent": 1.0, "knot_score": 0.1, "codebase_intelligence": 0.3}
        ))
        diag = lab.build_diagnostics()
        vacuum = next(t for t in diag["detector_traces"] if t["detector"] == "purpose_vacuum")
        assert vacuum["fired"] is True
