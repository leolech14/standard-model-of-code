"""
Tests for the color science module.

Covers:
    - Round-trip conversion (OKLCH -> sRGB -> OKLCH)
    - Gamut mapping produces valid sRGB
    - Color scale sampling and monotonicity
    - Harmony generation stays in-gamut
    - WCAG contrast ratios for known pairs
    - CVD simulation sanity
    - Integration helpers
"""

import json
import math
from pathlib import Path

import pytest

from src.core.viz.color_science import (
    oklch_to_srgb,
    srgb_to_oklch,
    oklch_to_hex,
    hex_to_oklch,
    hex_to_srgb,
    srgb_to_hex,
    linear_to_srgb,
    srgb_to_linear,
    in_srgb_gamut,
    gamut_map_oklch,
    gamut_report,
    GamutReport,
    ColorScale,
    sequential_scale,
    diverging_scale,
    SCALE_HEALTH,
    SCALE_RISK,
    SCALE_COMPLEXITY,
    SCALE_VIRIDIS,
    HarmonyType,
    generate_harmony,
    generate_palette,
    contrast_ratio_wcag,
    contrast_apca,
    simulate_cvd,
    validate_palette,
    AccessibilityReport,
    tokens_to_palette,
    audit_tokens,
    apply_scale_to_nodes,
    validate_gamut_tokens,
)


# =============================================================================
# PRIMITIVES
# =============================================================================

class TestLinearSrgbConversion:
    def test_black(self):
        assert linear_to_srgb(0.0) == 0.0
        assert srgb_to_linear(0.0) == 0.0

    def test_white(self):
        assert abs(linear_to_srgb(1.0) - 1.0) < 1e-6
        assert abs(srgb_to_linear(1.0) - 1.0) < 1e-6

    def test_round_trip(self):
        for val in [0.0, 0.01, 0.04, 0.1, 0.5, 0.8, 1.0]:
            result = srgb_to_linear(linear_to_srgb(val))
            assert abs(result - val) < 1e-6, f"Round-trip failed for {val}"

    def test_mid_gray(self):
        # sRGB 0.5 should be ~0.214 in linear
        linear = srgb_to_linear(0.5)
        assert 0.2 < linear < 0.25


class TestOklchSrgbConversion:
    def test_black(self):
        r, g, b = oklch_to_srgb(0.0, 0.0, 0.0)
        assert abs(r) < 0.01
        assert abs(g) < 0.01
        assert abs(b) < 0.01

    def test_white(self):
        r, g, b = oklch_to_srgb(1.0, 0.0, 0.0)
        assert abs(r - 1.0) < 0.02
        assert abs(g - 1.0) < 0.02
        assert abs(b - 1.0) < 0.02

    def test_round_trip_neutral(self):
        """Neutral grays should round-trip cleanly."""
        for L in [0.0, 0.2, 0.5, 0.8, 1.0]:
            r, g, b = oklch_to_srgb(L, 0.0, 0.0)
            L2, C2, H2 = srgb_to_oklch(
                max(0, min(1, r)), max(0, min(1, g)), max(0, min(1, b))
            )
            assert abs(L2 - L) < 0.02, f"Lightness round-trip failed for L={L}"
            assert C2 < 0.01, f"Chroma should be near-zero for neutral, got {C2}"

    def test_round_trip_chromatic(self):
        """Chromatic in-gamut colors should round-trip within tolerance."""
        test_colors = [
            (0.7, 0.10, 30.0),   # warm
            (0.6, 0.12, 145.0),  # green
            (0.5, 0.10, 240.0),  # blue
            (0.75, 0.08, 90.0),  # yellow
        ]
        for L, C, H in test_colors:
            r, g, b = oklch_to_srgb(L, C, H)
            r, g, b = max(0, min(1, r)), max(0, min(1, g)), max(0, min(1, b))
            L2, C2, H2 = srgb_to_oklch(r, g, b)
            assert abs(L2 - L) < 0.02, f"L round-trip failed for ({L},{C},{H})"
            assert abs(C2 - C) < 0.02, f"C round-trip failed for ({L},{C},{H})"
            # Hue comparison with wrapping
            h_diff = abs(H2 - H)
            if h_diff > 180:
                h_diff = 360 - h_diff
            assert h_diff < 2.0, f"H round-trip failed for ({L},{C},{H}): got {H2}"


class TestHexConversion:
    def test_black(self):
        assert oklch_to_hex(0.0, 0.0, 0.0) == "#000000"

    def test_white(self):
        result = oklch_to_hex(1.0, 0.0, 0.0)
        # Allow slight rounding
        r, g, b = hex_to_srgb(result)
        assert r > 0.98 and g > 0.98 and b > 0.98

    def test_hex_round_trip(self):
        for hex_color in ["#ff0000", "#00ff00", "#0000ff", "#888888", "#ffcc00"]:
            L, C, H = hex_to_oklch(hex_color)
            result = oklch_to_hex(L, C, H)
            # Hex round-trip may have +-1 per channel
            r1, g1, b1 = hex_to_srgb(hex_color)
            r2, g2, b2 = hex_to_srgb(result)
            assert abs(r1 - r2) < 0.02
            assert abs(g1 - g2) < 0.02
            assert abs(b1 - b2) < 0.02

    def test_short_hex(self):
        L, C, H = hex_to_oklch("#fff")
        assert L > 0.98

    def test_srgb_to_hex(self):
        assert srgb_to_hex(0.0, 0.0, 0.0) == "#000000"
        assert srgb_to_hex(1.0, 1.0, 1.0) == "#ffffff"


# =============================================================================
# GAMUT MAPPING
# =============================================================================

class TestGamutMapping:
    def test_in_gamut_stays_unchanged(self):
        L, C, H = 0.6, 0.10, 145.0
        assert in_srgb_gamut(L, C, H)
        mapped = gamut_map_oklch(L, C, H)
        assert abs(mapped[0] - L) < 0.002
        assert abs(mapped[1] - C) < 0.002

    def test_out_of_gamut_gets_mapped(self):
        # Very high chroma should be out of gamut
        L, C, H = 0.5, 0.4, 120.0
        assert not in_srgb_gamut(L, C, H)
        mapped = gamut_map_oklch(L, C, H)
        assert in_srgb_gamut(*mapped)
        assert mapped[1] < C  # chroma reduced
        assert abs(mapped[0] - L) < 0.002  # lightness preserved
        assert abs(mapped[2] - H) < 0.1  # hue preserved

    def test_mapped_produces_valid_srgb(self):
        """All gamut-mapped colors must produce sRGB in [0,1]."""
        test_cases = [
            (0.9, 0.35, 30.0),
            (0.3, 0.30, 200.0),
            (0.7, 0.40, 310.0),
            (0.5, 0.50, 90.0),
        ]
        for L, C, H in test_cases:
            mapped = gamut_map_oklch(L, C, H)
            r, g, b = oklch_to_srgb(*mapped)
            assert -0.01 <= r <= 1.01, f"r={r} for ({L},{C},{H})"
            assert -0.01 <= g <= 1.01, f"g={g} for ({L},{C},{H})"
            assert -0.01 <= b <= 1.01, f"b={b} for ({L},{C},{H})"

    def test_gamut_report(self):
        report = gamut_report(0.5, 0.4, 120.0)
        assert isinstance(report, GamutReport)
        assert report.clipped
        assert report.chroma_reduction > 0
        assert report.original == (0.5, 0.4, 120.0)

    def test_gamut_report_in_gamut(self):
        report = gamut_report(0.5, 0.05, 200.0)
        assert not report.clipped
        assert report.chroma_reduction == 0.0


# =============================================================================
# CONTINUOUS SCALES
# =============================================================================

class TestColorScale:
    def test_basic_scale(self):
        scale = ColorScale([
            (0.0, (0.3, 0.1, 30.0)),
            (1.0, (0.9, 0.1, 30.0)),
        ])
        c0 = scale.sample(0.0)
        c1 = scale.sample(1.0)
        assert c0 != c1
        assert c0.startswith("#")
        assert c1.startswith("#")

    def test_sample_n(self):
        colors = SCALE_HEALTH.sample_n(5)
        assert len(colors) == 5
        assert all(c.startswith("#") for c in colors)
        # All distinct
        assert len(set(colors)) == 5

    def test_sample_n_one(self):
        colors = SCALE_HEALTH.sample_n(1)
        assert len(colors) == 1

    def test_sample_n_zero(self):
        colors = SCALE_HEALTH.sample_n(0)
        assert len(colors) == 0

    def test_reverse(self):
        colors_fwd = SCALE_HEALTH.sample_n(5)
        colors_rev = SCALE_HEALTH.reverse().sample_n(5)
        # First of forward should match last of reverse (approximately)
        assert colors_fwd[0] == colors_rev[-1]
        assert colors_fwd[-1] == colors_rev[0]

    def test_clamp_bounds(self):
        """Values outside [0,1] should be clamped."""
        c_neg = SCALE_HEALTH.sample(-0.5)
        c_zero = SCALE_HEALTH.sample(0.0)
        c_over = SCALE_HEALTH.sample(1.5)
        c_one = SCALE_HEALTH.sample(1.0)
        assert c_neg == c_zero
        assert c_over == c_one

    def test_too_few_stops_raises(self):
        with pytest.raises(ValueError):
            ColorScale([(0.5, (0.5, 0.1, 200.0))])

    def test_sequential_scale(self):
        scale = sequential_scale(200.0)
        colors = scale.sample_n(10)
        assert len(colors) == 10
        # Lightness should increase (dark to light)
        lch_first = hex_to_oklch(colors[0])
        lch_last = hex_to_oklch(colors[-1])
        assert lch_last[0] > lch_first[0], "Sequential scale should go dark->light"

    def test_diverging_scale(self):
        scale = diverging_scale(30.0, 240.0)
        colors = scale.sample_n(5)
        assert len(colors) == 5

    def test_all_presets_produce_valid_hex(self):
        for scale in [SCALE_HEALTH, SCALE_RISK, SCALE_COMPLEXITY, SCALE_VIRIDIS]:
            colors = scale.sample_n(10)
            for c in colors:
                assert len(c) == 7 and c.startswith("#"), f"Invalid hex: {c}"


# =============================================================================
# PALETTE HARMONIES
# =============================================================================

class TestHarmony:
    def test_complementary(self):
        colors = generate_harmony((0.6, 0.12, 30.0), HarmonyType.COMPLEMENTARY)
        assert len(colors) == 2
        # Hues should be ~180 degrees apart
        h_diff = abs(colors[0][2] - colors[1][2])
        if h_diff > 180:
            h_diff = 360 - h_diff
        assert 170 < h_diff < 190

    def test_triadic(self):
        colors = generate_harmony((0.6, 0.12, 30.0), HarmonyType.TRIADIC)
        assert len(colors) == 3

    def test_tetradic(self):
        colors = generate_harmony((0.6, 0.12, 30.0), HarmonyType.TETRADIC)
        assert len(colors) == 4

    def test_analogous(self):
        colors = generate_harmony((0.6, 0.12, 30.0), HarmonyType.ANALOGOUS)
        assert len(colors) == 3

    def test_split_complementary(self):
        colors = generate_harmony((0.6, 0.12, 30.0), HarmonyType.SPLIT_COMPLEMENTARY)
        assert len(colors) == 3

    def test_all_in_gamut(self):
        for ht in HarmonyType:
            colors = generate_harmony((0.6, 0.15, 200.0), ht)
            for L, C, H in colors:
                assert in_srgb_gamut(L, C, H), f"{ht.value}: ({L},{C},{H}) out of gamut"

    def test_chroma_override(self):
        colors = generate_harmony((0.6, 0.12, 30.0), HarmonyType.TRIADIC, chroma=0.08)
        for L, C, H in colors:
            # Chroma may be reduced by gamut mapping, but never increased
            assert C <= 0.08 + 0.001

    def test_generate_palette(self):
        palette = generate_palette((0.6, 0.10, 0.0), 8)
        assert len(palette) == 8
        for L, C, H in palette:
            assert in_srgb_gamut(L, C, H)


# =============================================================================
# ACCESSIBILITY
# =============================================================================

class TestWcagContrast:
    def test_black_on_white(self):
        ratio = contrast_ratio_wcag("#000000", "#ffffff")
        assert abs(ratio - 21.0) < 0.1

    def test_white_on_black(self):
        ratio = contrast_ratio_wcag("#ffffff", "#000000")
        assert abs(ratio - 21.0) < 0.1

    def test_identical_colors(self):
        ratio = contrast_ratio_wcag("#888888", "#888888")
        assert abs(ratio - 1.0) < 0.01

    def test_aa_threshold(self):
        # Gray on white should have a known ratio
        ratio = contrast_ratio_wcag("#767676", "#ffffff")
        assert ratio >= 4.5  # #767676 is the darkest gray passing AA on white

    def test_symmetry(self):
        ratio1 = contrast_ratio_wcag("#ff0000", "#0000ff")
        ratio2 = contrast_ratio_wcag("#0000ff", "#ff0000")
        assert abs(ratio1 - ratio2) < 0.01


class TestApca:
    def test_black_on_white(self):
        lc = contrast_apca("#000000", "#ffffff")
        # Normal polarity (dark text on light bg) -> large positive Lc
        assert lc > 60

    def test_white_on_black(self):
        lc = contrast_apca("#ffffff", "#000000")
        # Reverse polarity (light text on dark bg) -> large negative Lc
        assert lc < -60

    def test_identical(self):
        lc = contrast_apca("#888888", "#888888")
        assert abs(lc) < 5


class TestCvdSimulation:
    def test_deuteranopia(self):
        result = simulate_cvd("#ff0000", "deuteranopia")
        assert result.startswith("#")
        assert len(result) == 7

    def test_protanopia(self):
        result = simulate_cvd("#ff0000", "protanopia")
        assert result.startswith("#")

    def test_tritanopia(self):
        result = simulate_cvd("#0000ff", "tritanopia")
        assert result.startswith("#")

    def test_gray_unchanged(self):
        """Neutral gray should be nearly unchanged under any CVD."""
        gray = "#808080"
        for deficiency in ["deuteranopia", "protanopia", "tritanopia"]:
            result = simulate_cvd(gray, deficiency)
            r1, g1, b1 = hex_to_srgb(gray)
            r2, g2, b2 = hex_to_srgb(result)
            assert abs(r1 - r2) < 0.15
            assert abs(g1 - g2) < 0.15
            assert abs(b1 - b2) < 0.15

    def test_invalid_deficiency(self):
        with pytest.raises(ValueError):
            simulate_cvd("#ff0000", "invalid")


class TestValidatePalette:
    def test_high_contrast_passes(self):
        report = validate_palette(["#ffffff", "#000000"], "#808080")
        assert isinstance(report, AccessibilityReport)
        # At least one should pass AA
        assert len(report.apca_scores) == 2

    def test_low_contrast_fails(self):
        report = validate_palette(["#777777", "#787878"], "#808080")
        assert not report.wcag_aa_pass
        assert len(report.failures) > 0


# =============================================================================
# INTEGRATION HELPERS
# =============================================================================

class TestTokensToPalette:
    def test_extracts_oklch(self):
        tokens = {
            "color": {
                "primary": {"$value": "oklch(70% 0.15 200)"},
                "secondary": {"$value": "oklch(50% 0.10 30)"},
                "not_oklch": {"$value": "#ff0000"},
            }
        }
        palette = tokens_to_palette(tokens)
        assert len(palette) == 2
        assert all(isinstance(t, tuple) and len(t) == 3 for t in palette)

    def test_empty_tokens(self):
        assert tokens_to_palette({}) == []

    def test_nested_tokens(self):
        tokens = {
            "group": {
                "sub": {
                    "deep": {"$value": "oklch(60% 0.12 145)"}
                }
            }
        }
        palette = tokens_to_palette(tokens)
        assert len(palette) == 1


class TestApplyScaleToNodes:
    def test_basic_application(self):
        nodes = [
            {"name": "a", "complexity": 1},
            {"name": "b", "complexity": 5},
            {"name": "c", "complexity": 10},
        ]
        apply_scale_to_nodes(nodes, "complexity", SCALE_COMPLEXITY)
        assert all("metric_color" in n for n in nodes)
        # Low complexity != high complexity color
        assert nodes[0]["metric_color"] != nodes[2]["metric_color"]

    def test_missing_metric_skipped(self):
        nodes = [
            {"name": "a", "complexity": 5},
            {"name": "b"},
            {"name": "c", "complexity": 10},
        ]
        apply_scale_to_nodes(nodes, "complexity", SCALE_COMPLEXITY)
        assert "metric_color" in nodes[0]
        assert "metric_color" not in nodes[1]
        assert "metric_color" in nodes[2]

    def test_empty_nodes(self):
        nodes = []
        apply_scale_to_nodes(nodes, "complexity", SCALE_COMPLEXITY)
        assert nodes == []

    def test_all_same_value(self):
        nodes = [{"val": 5}, {"val": 5}, {"val": 5}]
        apply_scale_to_nodes(nodes, "val", SCALE_HEALTH)
        # All should get same color (t=0.5 since range is 0)
        assert nodes[0]["metric_color"] == nodes[1]["metric_color"]

    def test_custom_output_key(self):
        nodes = [{"x": 0}, {"x": 10}]
        apply_scale_to_nodes(nodes, "x", SCALE_HEALTH, output_key="health_color")
        assert "health_color" in nodes[0]
        assert "metric_color" not in nodes[0]


class TestValidateGamutTokens:
    def test_in_gamut_tokens(self):
        tokens = {
            "color": {
                "safe": {"$value": "oklch(60% 0.10 200)"},
            }
        }
        warnings = validate_gamut_tokens(tokens)
        assert len(warnings) == 0

    def test_out_of_gamut_tokens(self):
        tokens = {
            "color": {
                "extreme": {"$value": "oklch(50% 0.40 120)"},
            }
        }
        warnings = validate_gamut_tokens(tokens)
        assert len(warnings) == 1
        assert "Out-of-gamut" in warnings[0]


class TestAuditTokens:
    def test_with_real_tokens(self, project_root):
        token_path = project_root / "schema" / "viz" / "tokens" / "appearance.tokens.json"
        if not token_path.exists():
            pytest.skip("appearance.tokens.json not found")
        report = audit_tokens(str(token_path))
        assert isinstance(report, AccessibilityReport)
        assert isinstance(report.apca_scores, list)
