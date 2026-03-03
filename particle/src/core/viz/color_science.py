"""
Color Science Module - Canonical color authority for the Collider visualization pipeline.

Pure Python, zero external dependencies (stdlib only: math, colorsys, dataclasses, enum).

Provides:
    - OKLCH <-> sRGB conversion primitives
    - CSS Color Level 4 gamut mapping (chroma reduction)
    - Continuous color scales for data-driven visualization
    - Palette harmony generation
    - Accessibility validation (WCAG 2.1, APCA, CVD simulation)
    - Integration helpers for the token system
"""

import json
import math
import re
import warnings
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


# =============================================================================
# PRIMITIVES: OKLCH <-> sRGB Conversion
# =============================================================================

def srgb_to_linear(x: float) -> float:
    """Convert sRGB gamma-encoded channel to linear light."""
    if x <= 0.04045:
        return x / 12.92
    return ((x + 0.055) / 1.055) ** 2.4


def linear_to_srgb(x: float) -> float:
    """Convert linear light channel to sRGB gamma-encoded."""
    if x <= 0.0031308:
        return 12.92 * x
    return 1.055 * (x ** (1.0 / 2.4)) - 0.055


def oklch_to_srgb(L: float, C: float, H: float) -> Tuple[float, float, float]:
    """
    Convert OKLCH to linear sRGB (unclamped).

    Args:
        L: Lightness [0, 1]
        C: Chroma [0, ~0.4]
        H: Hue [0, 360) degrees

    Returns:
        (r, g, b) in [0, 1] range (may exceed for out-of-gamut colors)
    """
    h_rad = math.radians(H)
    a = C * math.cos(h_rad)
    b = C * math.sin(h_rad)

    # OKLab -> LMS (cube-root intermediate)
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b

    l = l_ ** 3
    m = m_ ** 3
    s = s_ ** 3

    # LMS -> linear sRGB
    r_lin = +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g_lin = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    b_lin = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s

    return (linear_to_srgb(r_lin), linear_to_srgb(g_lin), linear_to_srgb(b_lin))


def srgb_to_oklch(r: float, g: float, b: float) -> Tuple[float, float, float]:
    """
    Convert sRGB [0, 1] to OKLCH.

    Args:
        r, g, b: sRGB channels [0, 1]

    Returns:
        (L, C, H) where L in [0,1], C >= 0, H in [0, 360)
    """
    # sRGB -> linear
    r_lin = srgb_to_linear(r)
    g_lin = srgb_to_linear(g)
    b_lin = srgb_to_linear(b)

    # linear sRGB -> LMS
    l = 0.4122214708 * r_lin + 0.5363325363 * g_lin + 0.0514459929 * b_lin
    m = 0.2119034982 * r_lin + 0.6806995451 * g_lin + 0.1073969566 * b_lin
    s = 0.0883024619 * r_lin + 0.2817188376 * g_lin + 0.6299787005 * b_lin

    # LMS -> cube root
    l_ = math.copysign(abs(l) ** (1.0 / 3.0), l)
    m_ = math.copysign(abs(m) ** (1.0 / 3.0), m)
    s_ = math.copysign(abs(s) ** (1.0 / 3.0), s)

    # cube root LMS -> OKLab
    L_val = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
    a = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    b_val = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_

    # OKLab -> OKLCH (polar)
    C_val = math.sqrt(a * a + b_val * b_val)
    H_val = math.degrees(math.atan2(b_val, a)) % 360.0

    return (L_val, C_val, H_val)


def oklch_to_hex(L: float, C: float, H: float) -> str:
    """Convert OKLCH to hex string, gamut-mapping if necessary."""
    L, C, H = gamut_map_oklch(L, C, H)
    r, g, b = oklch_to_srgb(L, C, H)
    r_byte = max(0, min(255, int(round(r * 255))))
    g_byte = max(0, min(255, int(round(g * 255))))
    b_byte = max(0, min(255, int(round(b * 255))))
    return f"#{r_byte:02x}{g_byte:02x}{b_byte:02x}"


def hex_to_oklch(hex_color: str) -> Tuple[float, float, float]:
    """Convert hex color string to OKLCH."""
    hex_color = hex_color.strip().lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    return srgb_to_oklch(r, g, b)


def hex_to_srgb(hex_color: str) -> Tuple[float, float, float]:
    """Convert hex color string to sRGB [0, 1]."""
    hex_color = hex_color.strip().lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    return (
        int(hex_color[0:2], 16) / 255.0,
        int(hex_color[2:4], 16) / 255.0,
        int(hex_color[4:6], 16) / 255.0,
    )


def srgb_to_hex(r: float, g: float, b: float) -> str:
    """Convert sRGB [0, 1] to hex string."""
    r_byte = max(0, min(255, int(round(r * 255))))
    g_byte = max(0, min(255, int(round(g * 255))))
    b_byte = max(0, min(255, int(round(b * 255))))
    return f"#{r_byte:02x}{g_byte:02x}{b_byte:02x}"


# =============================================================================
# GAMUT MAPPING: CSS Color Level 4 Algorithm
# =============================================================================

def in_srgb_gamut(L: float, C: float, H: float, epsilon: float = 0.001) -> bool:
    """Check if an OKLCH color is within the sRGB gamut."""
    r, g, b = oklch_to_srgb(L, C, H)
    return (
        -epsilon <= r <= 1.0 + epsilon
        and -epsilon <= g <= 1.0 + epsilon
        and -epsilon <= b <= 1.0 + epsilon
    )


def gamut_map_oklch(
    L: float, C: float, H: float, epsilon: float = 0.001, max_iter: int = 32
) -> Tuple[float, float, float]:
    """
    Map an OKLCH color into sRGB gamut via CSS Color Level 4 binary search.

    Preserves hue and lightness, reduces chroma until in-gamut.

    Args:
        L: Lightness [0, 1]
        C: Chroma
        H: Hue degrees
        epsilon: Tolerance for gamut boundary
        max_iter: Maximum binary search iterations

    Returns:
        (L, C, H) with C reduced to fit sRGB gamut
    """
    # Clamp lightness to valid range
    L = max(0.0, min(1.0, L))

    # Already in gamut
    if in_srgb_gamut(L, C, H, epsilon):
        return (L, C, H)

    # Binary search: reduce chroma
    lo, hi = 0.0, C
    for _ in range(max_iter):
        mid = (lo + hi) / 2.0
        if in_srgb_gamut(L, mid, H, epsilon):
            lo = mid
        else:
            hi = mid
        if hi - lo < epsilon / 100:
            break

    return (L, lo, H)


@dataclass
class GamutReport:
    """Report on gamut mapping applied to a color."""
    original: Tuple[float, float, float]
    mapped: Tuple[float, float, float]
    clipped: bool
    chroma_reduction: float


def gamut_report(L: float, C: float, H: float) -> GamutReport:
    """Generate a detailed gamut mapping report for an OKLCH color."""
    mapped_L, mapped_C, mapped_H = gamut_map_oklch(L, C, H)
    return GamutReport(
        original=(L, C, H),
        mapped=(mapped_L, mapped_C, mapped_H),
        clipped=mapped_C < C,
        chroma_reduction=C - mapped_C if mapped_C < C else 0.0,
    )


def modulate_oklch(
    L: float, C: float, H: float,
    l_target: Optional[float] = None,
    c_target: Optional[float] = None,
) -> Tuple[float, float, float]:
    """Shift lightness and/or chroma while preserving hue. Gamut-mapped.

    Args:
        L, C, H: base OKLCH color
        l_target: if set, replace L with this value (None = keep original)
        c_target: if set, replace C with this value (None = keep original)

    Returns:
        (L, C, H) gamut-mapped tuple
    """
    return gamut_map_oklch(
        l_target if l_target is not None else L,
        c_target if c_target is not None else C,
        H,
    )


# =============================================================================
# CONTINUOUS SCALES
# =============================================================================

def _lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation."""
    return a + (b - a) * t


def _lerp_oklch(
    lch1: Tuple[float, float, float], lch2: Tuple[float, float, float], t: float
) -> Tuple[float, float, float]:
    """Interpolate between two OKLCH colors, handling hue wrapping."""
    L = _lerp(lch1[0], lch2[0], t)
    C = _lerp(lch1[1], lch2[1], t)

    # Shortest-arc hue interpolation
    h1, h2 = lch1[2], lch2[2]
    diff = h2 - h1
    if diff > 180:
        diff -= 360
    elif diff < -180:
        diff += 360
    H = (h1 + diff * t) % 360.0

    return (L, C, H)


class ColorScale:
    """
    Continuous color scale defined by OKLCH stops.

    Each stop is (position, (L, C, H)) where position is in [0, 1].
    """

    def __init__(self, stops: List[Tuple[float, Tuple[float, float, float]]]):
        if len(stops) < 2:
            raise ValueError("ColorScale requires at least 2 stops")
        self._stops = sorted(stops, key=lambda s: s[0])

    @property
    def stops(self) -> List[Tuple[float, Tuple[float, float, float]]]:
        return list(self._stops)

    def sample(self, t: float) -> str:
        """Sample the scale at position t in [0, 1], returns hex."""
        t = max(0.0, min(1.0, t))

        # Find surrounding stops
        if t <= self._stops[0][0]:
            lch = self._stops[0][1]
        elif t >= self._stops[-1][0]:
            lch = self._stops[-1][1]
        else:
            for i in range(len(self._stops) - 1):
                t0, lch0 = self._stops[i]
                t1, lch1 = self._stops[i + 1]
                if t0 <= t <= t1:
                    local_t = (t - t0) / (t1 - t0) if t1 > t0 else 0.0
                    lch = _lerp_oklch(lch0, lch1, local_t)
                    break
            else:
                lch = self._stops[-1][1]

        return oklch_to_hex(*lch)

    def sample_n(self, n: int) -> List[str]:
        """Sample n evenly-spaced colors from the scale."""
        if n < 1:
            return []
        if n == 1:
            return [self.sample(0.5)]
        return [self.sample(i / (n - 1)) for i in range(n)]

    def reverse(self) -> "ColorScale":
        """Return a reversed copy of this scale."""
        return ColorScale([(1.0 - pos, lch) for pos, lch in reversed(self._stops)])


def sequential_scale(hue: float, n: int = 256) -> ColorScale:
    """
    Create a single-hue sequential scale (lightness ramp).

    Dark (L=0.25) at t=0 to bright (L=0.90) at t=1, with moderate chroma.
    """
    return ColorScale([
        (0.0, (0.25, 0.05, hue)),
        (0.5, (0.55, 0.12, hue)),
        (1.0, (0.90, 0.08, hue)),
    ])


def diverging_scale(hue_low: float, hue_high: float, n: int = 256) -> ColorScale:
    """
    Create a diverging scale through a neutral midpoint.

    Low values map to hue_low, high values to hue_high, center is neutral.
    """
    return ColorScale([
        (0.0, (0.55, 0.15, hue_low)),
        (0.5, (0.85, 0.01, 0.0)),     # near-neutral midpoint
        (1.0, (0.55, 0.15, hue_high)),
    ])


# Presets
SCALE_HEALTH = ColorScale([
    (0.0,  (0.55, 0.18, 30.0)),   # red (poor health)
    (0.5,  (0.80, 0.16, 90.0)),   # yellow (moderate)
    (1.0,  (0.75, 0.17, 145.0)),  # green (good health)
])

SCALE_RISK = ColorScale([
    (0.0,  (0.60, 0.12, 240.0)),  # blue (low risk)
    (0.5,  (0.75, 0.16, 60.0)),   # orange (medium)
    (1.0,  (0.55, 0.18, 25.0)),   # red (high risk)
])

SCALE_COMPLEXITY = ColorScale([
    (0.0,  (0.65, 0.10, 230.0)),  # cool blue (low complexity)
    (0.5,  (0.55, 0.18, 280.0)),  # purple (medium)
    (1.0,  (0.50, 0.22, 330.0)),  # hot magenta (high complexity)
])

SCALE_VIRIDIS = ColorScale([
    (0.00, (0.35, 0.15, 300.0)),  # dark purple
    (0.25, (0.45, 0.12, 260.0)),  # blue-purple
    (0.50, (0.60, 0.12, 180.0)),  # teal
    (0.75, (0.78, 0.15, 120.0)),  # green-yellow
    (1.00, (0.93, 0.10, 100.0)),  # bright yellow
])


# =============================================================================
# PALETTE HARMONIES
# =============================================================================

class HarmonyType(Enum):
    COMPLEMENTARY = "complementary"
    TRIADIC = "triadic"
    TETRADIC = "tetradic"
    ANALOGOUS = "analogous"
    SPLIT_COMPLEMENTARY = "split_complementary"


def generate_harmony(
    seed: Tuple[float, float, float],
    harmony_type: HarmonyType,
    chroma: Optional[float] = None,
) -> List[Tuple[float, float, float]]:
    """
    Generate a harmonious palette from a seed OKLCH color.

    Args:
        seed: (L, C, H) seed color
        harmony_type: Type of color harmony
        chroma: Override chroma for all generated colors (None = use seed's)

    Returns:
        List of OKLCH tuples, all gamut-mapped.
    """
    L, C, H = seed
    c = chroma if chroma is not None else C

    if harmony_type == HarmonyType.COMPLEMENTARY:
        hues = [H, (H + 180) % 360]
    elif harmony_type == HarmonyType.TRIADIC:
        hues = [H, (H + 120) % 360, (H + 240) % 360]
    elif harmony_type == HarmonyType.TETRADIC:
        hues = [H, (H + 90) % 360, (H + 180) % 360, (H + 270) % 360]
    elif harmony_type == HarmonyType.ANALOGOUS:
        hues = [(H - 30) % 360, H, (H + 30) % 360]
    elif harmony_type == HarmonyType.SPLIT_COMPLEMENTARY:
        hues = [H, (H + 150) % 360, (H + 210) % 360]
    else:
        hues = [H]

    return [gamut_map_oklch(L, c, h) for h in hues]


def generate_palette(
    seed: Tuple[float, float, float],
    n: int,
    lightness_spread: float = 0.15,
) -> List[Tuple[float, float, float]]:
    """
    Generate n visually distinct colors from a seed, using golden-angle hue spacing.

    Args:
        seed: (L, C, H) seed color
        n: Number of colors to generate
        lightness_spread: Variation in lightness across the palette

    Returns:
        List of n gamut-mapped OKLCH tuples.
    """
    L, C, H = seed
    colors = []
    golden_angle = 137.50776405  # degrees

    for i in range(n):
        hue = (H + i * golden_angle) % 360.0
        # Alternate lightness slightly for better distinction
        l_offset = lightness_spread * (0.5 - (i % 3) / 2.0)
        lightness = max(0.2, min(0.9, L + l_offset))
        colors.append(gamut_map_oklch(lightness, C, hue))

    return colors


# =============================================================================
# ACCESSIBILITY
# =============================================================================

def _relative_luminance(r: float, g: float, b: float) -> float:
    """WCAG 2.1 relative luminance from sRGB [0, 1] channels."""
    r_lin = srgb_to_linear(r)
    g_lin = srgb_to_linear(g)
    b_lin = srgb_to_linear(b)
    return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin


def contrast_ratio_wcag(fg_hex: str, bg_hex: str) -> float:
    """
    WCAG 2.1 contrast ratio between two hex colors.

    Returns a value between 1.0 (identical) and 21.0 (black on white).
    """
    fg = hex_to_srgb(fg_hex)
    bg = hex_to_srgb(bg_hex)
    lum_fg = _relative_luminance(*fg)
    lum_bg = _relative_luminance(*bg)

    lighter = max(lum_fg, lum_bg)
    darker = min(lum_fg, lum_bg)

    return (lighter + 0.05) / (darker + 0.05)


def contrast_apca(fg_hex: str, bg_hex: str) -> float:
    """
    Simplified APCA (Accessible Perceptual Contrast Algorithm) Lc value.

    Based on Myndex APCA-W3. Returns Lc contrast value.
    Positive = light text on dark, negative = dark text on light.
    Magnitude > 60 is generally readable for body text.
    """
    fg = hex_to_srgb(fg_hex)
    bg = hex_to_srgb(bg_hex)

    # Linearize
    fg_lin = [srgb_to_linear(c) for c in fg]
    bg_lin = [srgb_to_linear(c) for c in bg]

    # APCA luminance coefficients (sRGB)
    coeffs = (0.2126729, 0.7151522, 0.0721750)

    y_fg = sum(c * k for c, k in zip(fg_lin, coeffs))
    y_bg = sum(c * k for c, k in zip(bg_lin, coeffs))

    # Soft clamp
    y_fg = max(y_fg, 0.0)
    y_bg = max(y_bg, 0.0)

    # APCA exponents
    norm_bg = 0.56
    norm_fg = 0.57
    rev_bg = 0.65
    rev_fg = 0.62

    # Scale
    scale = 1.14

    if y_bg > y_fg:
        # Normal polarity (dark text on light bg) -> positive Lc
        sapc = (y_bg ** norm_bg - y_fg ** norm_fg) * scale
        if sapc < 0.001:
            return 0.0
        return (sapc - 0.027) * 100.0
    else:
        # Reverse polarity (light text on dark bg) -> negative Lc
        sapc = (y_bg ** rev_bg - y_fg ** rev_fg) * scale
        if sapc > -0.001:
            return 0.0
        return (sapc + 0.027) * 100.0


# --- CVD Simulation (Color Vision Deficiency) ---

# Brettel/Vienot 3x3 matrices for simulating color blindness in linear sRGB space.
# Each matrix transforms linear sRGB to simulate how a person with the
# given deficiency perceives color.

_CVD_MATRICES = {
    "deuteranopia": [
        # Reduced green-sensitive (M) cones
        [0.625, 0.375, 0.0],
        [0.700, 0.300, 0.0],
        [0.000, 0.300, 0.700],
    ],
    "protanopia": [
        # Reduced red-sensitive (L) cones
        [0.152286, 1.052583, -0.204868],
        [0.114503, 0.786281, 0.099216],
        [-0.003882, -0.048116, 1.051998],
    ],
    "tritanopia": [
        # Reduced blue-sensitive (S) cones
        [1.255528, -0.076749, -0.178779],
        [-0.078411, 0.930809, 0.147602],
        [0.004733, 0.691367, 0.303900],
    ],
}


def simulate_cvd(hex_color: str, deficiency: str) -> str:
    """
    Simulate how a color appears under a color vision deficiency.

    Args:
        hex_color: Input hex color
        deficiency: "deuteranopia", "protanopia", or "tritanopia"

    Returns:
        Hex color as perceived under the deficiency.
    """
    if deficiency not in _CVD_MATRICES:
        raise ValueError(f"Unknown deficiency: {deficiency}. Use: {list(_CVD_MATRICES.keys())}")

    r, g, b = hex_to_srgb(hex_color)

    # Convert to linear space for matrix transform
    r_lin = srgb_to_linear(r)
    g_lin = srgb_to_linear(g)
    b_lin = srgb_to_linear(b)

    mat = _CVD_MATRICES[deficiency]
    sim_r = mat[0][0] * r_lin + mat[0][1] * g_lin + mat[0][2] * b_lin
    sim_g = mat[1][0] * r_lin + mat[1][1] * g_lin + mat[1][2] * b_lin
    sim_b = mat[2][0] * r_lin + mat[2][1] * g_lin + mat[2][2] * b_lin

    # Back to sRGB, clamp
    out_r = max(0.0, min(1.0, linear_to_srgb(sim_r)))
    out_g = max(0.0, min(1.0, linear_to_srgb(sim_g)))
    out_b = max(0.0, min(1.0, linear_to_srgb(sim_b)))

    return srgb_to_hex(out_r, out_g, out_b)


def _hex_distance(hex1: str, hex2: str) -> float:
    """Euclidean distance in OKLCH space between two hex colors."""
    l1, c1, h1 = hex_to_oklch(hex1)
    l2, c2, h2 = hex_to_oklch(hex2)
    # Convert to Cartesian for distance
    a1, b1 = c1 * math.cos(math.radians(h1)), c1 * math.sin(math.radians(h1))
    a2, b2 = c2 * math.cos(math.radians(h2)), c2 * math.sin(math.radians(h2))
    return math.sqrt((l1 - l2) ** 2 + (a1 - a2) ** 2 + (b1 - b2) ** 2)


@dataclass
class AccessibilityReport:
    """Results from accessibility validation of a color palette."""
    wcag_aa_pass: bool
    wcag_aaa_pass: bool
    apca_scores: List[float]
    cvd_distinguishable: Dict[str, bool]
    failures: List[str] = field(default_factory=list)


def validate_palette(
    colors: List[str],
    bg_hex: str,
    min_cvd_distance: float = 0.04,
) -> AccessibilityReport:
    """
    Validate a list of hex colors against accessibility criteria.

    Args:
        colors: List of foreground hex colors
        bg_hex: Background hex color
        min_cvd_distance: Minimum OKLCH distance between CVD-simulated colors
                          to consider them distinguishable (default 0.04)

    Returns:
        AccessibilityReport with pass/fail results.
    """
    failures: List[str] = []
    wcag_ratios = []
    apca_scores = []

    for i, color in enumerate(colors):
        ratio = contrast_ratio_wcag(color, bg_hex)
        wcag_ratios.append(ratio)
        apca_val = contrast_apca(color, bg_hex)
        apca_scores.append(apca_val)

        if ratio < 4.5:
            failures.append(f"Color {i} ({color}): WCAG AA fail (ratio={ratio:.2f}, need 4.5)")
        if ratio < 3.0:
            failures.append(f"Color {i} ({color}): WCAG AA large text fail (ratio={ratio:.2f}, need 3.0)")

    # WCAG thresholds
    wcag_aa = all(r >= 4.5 for r in wcag_ratios)
    wcag_aaa = all(r >= 7.0 for r in wcag_ratios)

    # CVD distinguishability
    cvd_results: Dict[str, bool] = {}
    for deficiency in _CVD_MATRICES:
        simulated = [simulate_cvd(c, deficiency) for c in colors]
        distinguishable = True
        for i in range(len(simulated)):
            for j in range(i + 1, len(simulated)):
                dist = _hex_distance(simulated[i], simulated[j])
                if dist < min_cvd_distance:
                    distinguishable = False
                    failures.append(
                        f"Colors {i},{j} indistinguishable under {deficiency} "
                        f"(distance={dist:.4f})"
                    )
        cvd_results[deficiency] = distinguishable

    return AccessibilityReport(
        wcag_aa_pass=wcag_aa,
        wcag_aaa_pass=wcag_aaa,
        apca_scores=apca_scores,
        cvd_distinguishable=cvd_results,
        failures=failures,
    )


# =============================================================================
# INTEGRATION HELPERS
# =============================================================================

_OKLCH_PATTERN = re.compile(r"^oklch\((.+)\)$", re.IGNORECASE)


def _parse_oklch_string(value: str) -> Optional[Tuple[float, float, float]]:
    """Parse an oklch(...) CSS string into (L, C, H). Returns None if not OKLCH."""
    match = _OKLCH_PATTERN.match(value.strip())
    if not match:
        return None

    content = match.group(1)
    # Strip alpha channel
    if "/" in content:
        content = content.split("/")[0]

    tokens = re.split(r"[ ,]+", content.strip())
    if len(tokens) < 3:
        return None

    try:
        # L: percentage or decimal
        l_tok = tokens[0].strip().rstrip("%")
        L = float(l_tok)
        if tokens[0].strip().endswith("%") or L > 1.0:
            L /= 100.0

        # C: number
        C = float(tokens[1].strip().rstrip("%"))
        if tokens[1].strip().endswith("%"):
            C /= 100.0

        # H: degrees
        H = float(tokens[2].strip().replace("deg", "")) % 360.0

        return (L, C, H)
    except (ValueError, IndexError):
        return None


def tokens_to_palette(token_dict: dict) -> List[Tuple[float, float, float]]:
    """
    Extract OKLCH colors from a flat or nested token dict.

    Walks the token tree, finds all $value entries that are oklch() strings,
    and returns them as OKLCH tuples.

    Args:
        token_dict: Loaded appearance.tokens.json (or subset)

    Returns:
        List of (L, C, H) tuples found in the tokens.
    """
    colors: List[Tuple[float, float, float]] = []

    def _walk(obj: Any) -> None:
        if isinstance(obj, dict):
            if "$value" in obj:
                val = obj["$value"]
                if isinstance(val, str):
                    parsed = _parse_oklch_string(val)
                    if parsed:
                        colors.append(parsed)
            else:
                for v in obj.values():
                    _walk(v)
        elif isinstance(obj, list):
            for item in obj:
                _walk(item)

    _walk(token_dict)
    return colors


def audit_tokens(
    token_path: str,
    bg_hex: str = "#000000",
) -> AccessibilityReport:
    """
    Load a token file and run a full accessibility audit on all OKLCH colors.

    Args:
        token_path: Path to appearance.tokens.json
        bg_hex: Background color to test contrast against

    Returns:
        AccessibilityReport for all token colors.
    """
    with open(token_path, "r") as f:
        token_dict = json.load(f)

    oklch_colors = tokens_to_palette(token_dict)
    hex_colors = [oklch_to_hex(*lch) for lch in oklch_colors]

    if not hex_colors:
        return AccessibilityReport(
            wcag_aa_pass=True,
            wcag_aaa_pass=True,
            apca_scores=[],
            cvd_distinguishable={d: True for d in _CVD_MATRICES},
            failures=["No OKLCH colors found in token file"],
        )

    return validate_palette(hex_colors, bg_hex)


def apply_scale_to_nodes(
    nodes: List[Dict[str, Any]],
    metric_key: str,
    scale: ColorScale,
    output_key: str = "metric_color",
) -> None:
    """
    Apply a color scale to nodes based on a numeric metric, in-place.

    Normalizes the metric across all nodes to [0, 1], then samples the scale.
    Nodes missing the metric are skipped.

    Args:
        nodes: List of node dicts
        metric_key: Key to read the numeric value from
        scale: ColorScale to sample
        output_key: Key to write the resulting hex color to
    """
    # Collect valid values for normalization
    values = []
    for node in nodes:
        val = node.get(metric_key)
        if val is not None:
            try:
                values.append(float(val))
            except (TypeError, ValueError):
                pass

    if not values:
        return

    v_min = min(values)
    v_max = max(values)
    v_range = v_max - v_min

    for node in nodes:
        val = node.get(metric_key)
        if val is None:
            continue
        try:
            fval = float(val)
        except (TypeError, ValueError):
            continue

        t = (fval - v_min) / v_range if v_range > 0 else 0.5
        node[output_key] = scale.sample(t)


def validate_gamut_tokens(token_dict: dict, threshold: float = 0.01) -> List[str]:
    """
    Validate that all OKLCH token colors are within sRGB gamut.

    Args:
        token_dict: Loaded token dictionary
        threshold: Minimum chroma reduction to report (avoids noise from
                   near-gamut colors). Default 0.01.

    Returns:
        List of warning strings for out-of-gamut tokens (empty if all OK).
    """
    warnings_list: List[str] = []
    oklch_colors = tokens_to_palette(token_dict)

    for L, C, H in oklch_colors:
        if not in_srgb_gamut(L, C, H):
            mapped = gamut_map_oklch(L, C, H)
            chroma_reduction = C - mapped[1]
            if chroma_reduction >= threshold:
                warnings_list.append(
                    f"Out-of-gamut: oklch({L:.4f} {C:.4f} {H:.1f}) "
                    f"-> mapped to oklch({mapped[0]:.4f} {mapped[1]:.4f} {mapped[2]:.1f}) "
                    f"(chroma reduced by {chroma_reduction:.4f})"
                )

    return warnings_list
