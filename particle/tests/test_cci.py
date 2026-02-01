"""Tests for Codome Completeness Index (CCI) calculation.

Tests the CCIMetrics dataclass and calculate_cci function from survey.py.
"""
import pytest
from src.core.survey import CCIMetrics, calculate_cci, run_survey


class TestCCIMetrics:
    """Tests for CCIMetrics dataclass."""

    def test_default_values(self):
        """Verify CCIMetrics has sensible defaults."""
        metrics = CCIMetrics()
        assert metrics.true_positives == 0
        assert metrics.false_positives == 0
        assert metrics.true_negatives == 0
        assert metrics.false_negatives == 0
        assert metrics.cci == 0.0
        assert metrics.verdict == "UNKNOWN"


class TestCalculateCCI:
    """Tests for calculate_cci function."""

    def test_perfect_score(self):
        """Perfect classification should give 100% CCI."""
        # All source analyzed, no vendor analyzed
        metrics = calculate_cci(
            total_source_files=100,
            analyzed_source_files=100,  # TP = 100
            total_vendor_files=50,
            analyzed_vendor_files=0,     # FP = 0
        )

        assert metrics.sensitivity == 1.0  # 100% recall
        assert metrics.specificity == 1.0  # 100% exclusion
        assert metrics.precision == 1.0    # 100% precision
        assert metrics.cci == 100.0
        assert metrics.verdict == "EXCELLENT"

    def test_all_missed(self):
        """Missing all source should give 0% sensitivity."""
        metrics = calculate_cci(
            total_source_files=100,
            analyzed_source_files=0,   # TP = 0, FN = 100
            total_vendor_files=50,
            analyzed_vendor_files=0,
        )

        assert metrics.sensitivity == 0.0  # Missed everything
        assert metrics.specificity == 1.0  # But excluded vendor correctly
        assert metrics.cci == 0.0
        assert metrics.verdict == "POOR"

    def test_vendor_leakage(self):
        """Analyzing vendor code should reduce specificity."""
        metrics = calculate_cci(
            total_source_files=100,
            analyzed_source_files=100,
            total_vendor_files=100,
            analyzed_vendor_files=50,  # FP = 50, half the vendor leaked through
        )

        assert metrics.sensitivity == 1.0     # Got all source
        assert metrics.specificity == 0.5     # Only excluded half vendor
        assert metrics.precision == pytest.approx(0.667, rel=0.01)  # 100/(100+50)
        assert metrics.verdict in ["GOOD", "FAIR"]  # Should be penalized

    def test_partial_coverage(self):
        """Partial source coverage should be reflected in sensitivity."""
        metrics = calculate_cci(
            total_source_files=100,
            analyzed_source_files=80,  # Only 80% captured
            total_vendor_files=50,
            analyzed_vendor_files=0,
        )

        assert metrics.sensitivity == 0.8
        assert metrics.specificity == 1.0
        assert metrics.precision == 1.0
        # F2 weights recall, 80% recall with perfect precision = 83% CCI = FAIR
        assert metrics.verdict == "FAIR"

    def test_f2_weights_recall(self):
        """F2 should weight recall higher than precision."""
        # Same F1 but different precision/recall
        high_recall = calculate_cci(
            total_source_files=100,
            analyzed_source_files=90,   # High recall
            total_vendor_files=100,
            analyzed_vendor_files=30,   # Lower precision
        )

        low_recall = calculate_cci(
            total_source_files=100,
            analyzed_source_files=60,   # Low recall
            total_vendor_files=100,
            analyzed_vendor_files=0,    # High precision
        )

        # F2 should favor high recall scenario
        assert high_recall.f2_score > low_recall.f2_score

    def test_verdict_thresholds(self):
        """Verify verdict thresholds are correct."""
        # EXCELLENT: >= 95
        excellent = calculate_cci(100, 98, 10, 0)
        assert excellent.verdict == "EXCELLENT"

        # GOOD: >= 85, < 95
        good = calculate_cci(100, 90, 50, 5)
        assert good.verdict == "GOOD"

        # FAIR: >= 70, < 85
        fair = calculate_cci(100, 75, 100, 10)
        assert fair.verdict == "FAIR"

        # POOR: < 70
        poor = calculate_cci(100, 50, 100, 20)
        assert poor.verdict == "POOR"

    def test_zero_division_safety(self):
        """Should handle edge cases without division errors."""
        # No source files
        metrics = calculate_cci(0, 0, 100, 0)
        assert metrics.sensitivity == 0.0  # 0/(0+0) handled

        # No vendor files
        metrics = calculate_cci(100, 100, 0, 0)
        assert metrics.specificity == 0.0  # 0/(0+0) handled


class TestSurveyWithCCI:
    """Integration tests for CCI in survey results."""

    def test_survey_includes_cci(self, tmp_path):
        """Survey result should include CCI metrics."""
        # Create a minimal directory structure
        src = tmp_path / "src"
        src.mkdir()
        (src / "main.py").write_text("print('hello')")
        (src / "utils.py").write_text("def helper(): pass")

        result = run_survey(str(tmp_path))

        assert result.cci is not None
        assert isinstance(result.cci, CCIMetrics)
        assert result.cci.cci >= 0
        assert result.cci.cci <= 100

    def test_survey_cci_with_vendor(self, tmp_path):
        """CCI should reflect vendor exclusion."""
        # Create source
        src = tmp_path / "src"
        src.mkdir()
        (src / "app.py").write_text("import flask")

        # Create vendor (should be excluded)
        vendor = tmp_path / "node_modules"
        vendor.mkdir()
        (vendor / "lodash.js").write_text("// lodash")
        (vendor / "react.js").write_text("// react")

        result = run_survey(str(tmp_path))

        assert result.cci is not None
        # Should have high specificity (vendor excluded)
        assert result.cci.specificity > 0.5
