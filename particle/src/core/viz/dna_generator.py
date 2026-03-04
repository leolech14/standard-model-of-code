"""
DNA Generator — Derive design tokens from 12 atomic variables.

PURPOSE: Generate design tokens mathematically from 12 foundational "DNA"
variables, making theme creation a matter of tweaking 12 numbers instead
of hand-authoring values.

ARCHITECTURE:
    12 DNA Variables → DNAGenerator.generate() → Full token dict with $extensions
                    → DNAGenerator.validate()  → WCAG + range constraint warnings

Based on Vector UI's DESIGN_SYSTEM_DNA.md derivation formulas.

COVERAGE (vs DESIGN_SYSTEM_DNA.md spec: 12 atomic → 87 derivable = 99 total):

    Family              Spec    Impl    Status
    ─────────────────────────────────────────────
    Colors              20      20      COMPLETE
    Typography          27      17      PARTIAL — see below
    Spacing             13      12      PARTIAL — missing space-24
    Border Radius        8       7      PARTIAL — missing radius-2xl
    Shadows              8       3      PARTIAL — see below
    Transitions          4       4      COMPLETE
    Z-Index              8       0      DEFERRED — hardcoded, not derivable from DNA
    ─────────────────────────────────────────────
    TOTAL               88      63      72% coverage

    Deferred tokens (25):
    - Typography: font-display family, text-4xl/5xl sizes, weight-black,
      leading-none/loose, tracking-tight/normal/wide/wider (10 tokens)
      Reason: Collider HTML uses only xs–3xl sizes and 4 weights.
      Letter-spacing is unused in the current token system.
    - Spacing: space-24 (1 token)
      Reason: Collider panels never exceed space-20 (80px).
    - Radius: radius-2xl (1 token)
      Reason: Collider uses radius-lg as max.
    - Shadows: shadow-xs/base/xl/glow/glow-lg (5 tokens)
      Reason: Collider dark theme uses none/sm/md/lg only.
      Glow shadows were explicitly removed from the design language.
    - Z-Index: all 8 (z-base through z-tooltip)
      Reason: Not derivable from DNA variables. Fixed stacking order
      is defined in layout.tokens.json, not generated.

    Note: Spec says "87 derivable" but lists 88 in detail sections
    (minor counting discrepancy in the spec itself).

PRECEDENCE RULE (encoded_color vs wireframe):
    When apply_to_nodes() is called with wireframe=True AND a node has
    'encoded_color' (from color_encoding.py's non-default view), the
    encoded_color wins for the 'color' field, but wireframe properties
    (fillOpacity, strokeOpacity, strokeWidth) are still applied.
    This is intentional: data encoding determines WHAT color, wireframe
    determines HOW it renders (filled vs stroke-only).
"""

import math
from typing import Any, Dict, List, Optional


class DNAGenerator:
    """Generate design tokens from 12 atomic DNA variables.

    The 12 variables are the minimum information set needed to fully define
    a coherent design system. Everything else is derived mathematically.
    """

    # Default DNA signature — matches Collider's muted dark theme
    DNA_SIGNATURE: Dict[str, Any] = {
        "primaryHue": 250,        # Blue-gray (Collider default)
        "successHue": 145,        # Green
        "warningHue": 85,         # Yellow
        "dangerHue": 25,          # Red-orange
        "chroma": 0.04,           # Very low — Collider's muted palette
        "fontFamily": "Inter",    # Sans-serif default
        "baseFontSize": 12,       # px — compact UI
        "spacingBase": 8,         # px — 8px grid
        "bgLightness": 8,         # Dark theme default (0-100)
        "textLightness": 100,     # White text on dark bg
        "radiusBase": 6,          # px — subtle rounding
        "transitionBase": 200,    # ms — animation speed
    }

    # Scientific paper DNA preset — white bg, serif, hairline
    SCIENTIFIC_PAPER_DNA: Dict[str, Any] = {
        "primaryHue": 250,
        "successHue": 145,
        "warningHue": 85,
        "dangerHue": 25,
        "chroma": 0.08,           # Slightly more saturated accents
        "fontFamily": "Libre Baskerville",
        "baseFontSize": 13,
        "spacingBase": 8,
        "bgLightness": 99,        # Near-white
        "textLightness": 10,      # Near-black text
        "radiusBase": 2,          # Minimal rounding
        "transitionBase": 150,    # Snappier transitions
    }

    # Modular scale ratio (minor third)
    _SCALE_RATIO = 1.143

    def generate(self, dna: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate full token dict from DNA variables.

        Args:
            dna: Optional DNA variable overrides. Missing keys use defaults.

        Returns:
            Complete token dictionary with $value and $extensions per DTCG spec.
        """
        d = {**self.DNA_SIGNATURE, **(dna or {})}
        tokens: Dict[str, Any] = {}

        tokens["color"] = self._derive_colors(d)
        tokens["typography"] = self._derive_typography(d)
        tokens["spacing"] = self._derive_spacing(d)
        tokens["radius"] = self._derive_radius(d)
        tokens["shadow"] = self._derive_shadows(d)
        tokens["transition"] = self._derive_transitions(d)

        return tokens

    def to_theme_tokens(self, dna: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Convert generated tokens to theme.tokens.json format.

        Returns a dict structured like a theme entry in theme.tokens.json,
        suitable for insertion into the themes object.
        """
        tokens = self.generate(dna)
        d = {**self.DNA_SIGNATURE, **(dna or {})}

        theme = {
            "$description": f"Generated from DNA: primaryHue={d['primaryHue']}, "
                           f"bgLightness={d['bgLightness']}, chroma={d['chroma']}",
            "color": {},
            "typography": {},
            "shadow": {},
        }

        # Map generated color tokens to theme.tokens.json structure
        colors = tokens["color"]
        theme["color"]["bg"] = {
            "base": self._dtcg_token(
                colors["bg-base"]["$value"], "oklch({bgLightness}% 0.04 250)",
                ["bgLightness"], f"bgLightness in [0, 100]"
            ),
            "surface": self._dtcg_token(
                colors["bg-raised"]["$value"], "oklch({bgLightness+4}% 0.04 250)",
                ["bgLightness"]
            ),
            "elevated": self._dtcg_token(
                colors["bg-overlay"]["$value"], "oklch({bgLightness-6}% 0.03 250)",
                ["bgLightness"]
            ),
            "sunken": self._dtcg_token(
                colors["bg-sunken"]["$value"], "oklch({bgLightness-10}% 0.02 250)",
                ["bgLightness"]
            ),
        }

        theme["color"]["text"] = {
            "primary": self._dtcg_token(
                colors["text-primary"]["$value"],
                "oklch({textLightness}% 0.01 {primaryHue})",
                ["textLightness", "primaryHue"],
                "textLightness in [0, 100]"
            ),
            "secondary": self._dtcg_token(
                colors["text-secondary"]["$value"],
                "oklch({textLightness-27}% 0.02 {primaryHue})",
                ["textLightness", "primaryHue"]
            ),
            "muted": self._dtcg_token(
                colors["text-disabled"]["$value"],
                "oklch({textLightness-57}% 0.02 {primaryHue})",
                ["textLightness", "primaryHue"]
            ),
        }

        theme["color"]["accent"] = {
            "primary": self._dtcg_token(
                colors["primary-500"]["$value"],
                "oklch({bgLightness+37}% {chroma} {primaryHue})",
                ["bgLightness", "chroma", "primaryHue"]
            ),
        }

        # Typography
        typo = tokens["typography"]
        theme["typography"]["family"] = {
            "sans": {"$value": typo["font-sans"]["$value"]},
        }
        theme["typography"]["size"] = {
            "base": self._dtcg_token(
                typo["text-base"]["$value"],
                "{baseFontSize}px",
                ["baseFontSize"],
                "baseFontSize in [10, 24]"
            ),
        }

        # Shadows
        shadow = tokens["shadow"]
        theme["shadow"] = {
            "sm": {"$value": shadow["shadow-sm"]["$value"]},
            "md": {"$value": shadow["shadow-md"]["$value"]},
            "lg": {"$value": shadow["shadow-lg"]["$value"]},
        }

        return theme

    def validate(self, tokens: Optional[Dict[str, Any]] = None,
                 dna: Optional[Dict[str, Any]] = None) -> List[str]:
        """Run WCAG + touch-target + range constraints. Return warnings.

        Args:
            tokens: Pre-generated token dict (or None to generate from dna).
            dna: DNA variables to generate from (used if tokens is None).

        Returns:
            List of warning strings. Empty list means all constraints pass.
        """
        if tokens is None:
            tokens = self.generate(dna)

        d = {**self.DNA_SIGNATURE, **(dna or {})}
        warnings: List[str] = []

        # 1. OKLCH range constraints
        if not (0 <= d["bgLightness"] <= 100):
            warnings.append(
                f"bgLightness={d['bgLightness']} out of range [0, 100]"
            )
        if not (0 <= d["textLightness"] <= 100):
            warnings.append(
                f"textLightness={d['textLightness']} out of range [0, 100]"
            )
        if not (0.0 <= d["chroma"] <= 0.4):
            warnings.append(
                f"chroma={d['chroma']} out of range [0.0, 0.4]"
            )

        # 2. WCAG AA contrast check (text on background)
        bg_luminance = self._oklch_approx_luminance(d["bgLightness"] / 100.0)
        text_luminance = self._oklch_approx_luminance(d["textLightness"] / 100.0)
        contrast = self._contrast_ratio(bg_luminance, text_luminance)
        if contrast < 4.5:
            warnings.append(
                f"WCAG AA fail: text/bg contrast ratio {contrast:.2f} < 4.5:1 "
                f"(bgL={d['bgLightness']}, textL={d['textLightness']})"
            )

        # 3. Touch target minimum (44px)
        min_interactive = d["spacingBase"] * 5.5  # 44px at base=8
        if min_interactive < 44:
            warnings.append(
                f"Touch target {min_interactive:.0f}px < 44px minimum "
                f"(spacingBase={d['spacingBase']})"
            )

        # 4. Font size minimum for readability
        if d["baseFontSize"] < 10:
            warnings.append(
                f"baseFontSize={d['baseFontSize']}px below 10px minimum"
            )

        # 5. Hue range validation
        for hue_name in ("primaryHue", "successHue", "warningHue", "dangerHue"):
            hue = d[hue_name]
            if not (0 <= hue <= 360):
                warnings.append(f"{hue_name}={hue} out of range [0, 360]")

        return warnings

    # ─── Color derivation ────────────────────────────────────────────

    def _derive_colors(self, d: Dict[str, Any]) -> Dict[str, Any]:
        """Derive 20 color tokens from 5 DNA variables."""
        bg = d["bgLightness"]
        text = d["textLightness"]
        c = d["chroma"]
        hue = d["primaryHue"]

        colors = {}

        # Primary scale (5) — vary lightness around bg
        for name, offset in [
            ("primary-900", 17), ("primary-700", 27), ("primary-500", 37),
            ("primary-300", 47), ("primary-100", 57),
        ]:
            L = self._clamp(bg + offset, 0, 100)
            colors[name] = self._color_token(
                L, c, hue,
                f"oklch({{bgLightness+{offset}}}% {{chroma}} {{primaryHue}})",
                ["bgLightness", "chroma", "primaryHue"]
            )

        # Background scale (4)
        bg_tokens = [
            ("bg-base", bg, 0.04, 250, "oklch({bgLightness}% 0.04 250)", ["bgLightness"]),
            ("bg-raised", bg + 4, 0.04, 250, "oklch({bgLightness+4}% 0.04 250)", ["bgLightness"]),
            ("bg-overlay", max(0, bg - 6), 0.03, 250,
             "oklch({bgLightness-6}% 0.03 250)", ["bgLightness"]),
            ("bg-sunken", max(0, bg - 10), 0.02, 250,
             "oklch({bgLightness-10}% 0.02 250)", ["bgLightness"]),
        ]
        for name, L, ch, h, formula, inputs in bg_tokens:
            colors[name] = self._color_token(
                self._clamp(L, 0, 100), ch, h, formula, inputs
            )

        # Text scale (4)
        text_tokens = [
            ("text-primary", text, 0.01, "oklch({textLightness}% 0.01 {primaryHue})",
             ["textLightness", "primaryHue"]),
            ("text-secondary", text - 27, 0.02,
             "oklch({textLightness-27}% 0.02 {primaryHue})", ["textLightness", "primaryHue"]),
            ("text-tertiary", text - 42, 0.02,
             "oklch({textLightness-42}% 0.02 {primaryHue})", ["textLightness", "primaryHue"]),
            ("text-disabled", text - 57, 0.02,
             "oklch({textLightness-57}% 0.02 {primaryHue})", ["textLightness", "primaryHue"]),
        ]
        for name, L, ch, formula, inputs in text_tokens:
            colors[name] = self._color_token(
                self._clamp(L, 0, 100), ch, hue, formula, inputs
            )

        # Borders (3)
        colors["border-base"] = self._color_token(30, 0.03, hue,
            "oklch(30% 0.03 {primaryHue})", ["primaryHue"])
        colors["border-hover"] = self._color_token(40, 0.08, hue,
            "oklch(40% 0.08 {primaryHue})", ["primaryHue"])
        colors["border-focus"] = self._color_token(50, 0.12, hue,
            "oklch(50% 0.12 {primaryHue})", ["primaryHue"])

        # Semantic colors (4)
        colors["success"] = self._color_token(65, c, d["successHue"],
            "oklch(65% {chroma} {successHue})", ["chroma", "successHue"])
        colors["warning"] = self._color_token(75, c, d["warningHue"],
            "oklch(75% {chroma} {warningHue})", ["chroma", "warningHue"])
        colors["danger"] = self._color_token(55, c, d["dangerHue"],
            "oklch(55% {chroma} {dangerHue})", ["chroma", "dangerHue"])
        colors["info"] = self._color_token(60, c, 230,
            "oklch(60% {chroma} 230)", ["chroma"])

        return colors

    # ─── Typography derivation ───────────────────────────────────────

    def _derive_typography(self, d: Dict[str, Any]) -> Dict[str, Any]:
        """Derive typography tokens from baseFontSize and fontFamily."""
        base = d["baseFontSize"]
        r = self._SCALE_RATIO
        family = d["fontFamily"]

        tokens = {}

        # Font families
        tokens["font-sans"] = self._ext_token(
            f"'{family}', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
            "'{fontFamily}', -apple-system, ...", ["fontFamily"]
        )
        tokens["font-mono"] = self._ext_token(
            "'JetBrains Mono', 'SF Mono', Monaco, Consolas, monospace",
            "fixed", []
        )

        # Font sizes (modular scale)
        size_map = {
            "text-xs": 0.786, "text-sm": 0.929, "text-base": 1.0,
            "text-md": r, "text-lg": r**2, "text-xl": r**3,
            "text-2xl": r**4, "text-3xl": r**5,
        }
        for name, multiplier in size_map.items():
            px = round(base * multiplier, 1)
            tokens[name] = self._ext_token(
                f"{px}px",
                f"{{baseFontSize}} * {multiplier:.3f}",
                ["baseFontSize"],
                f"baseFontSize in [10, 24]"
            )

        # Font weights
        for name, value in [
            ("weight-normal", 400), ("weight-medium", 500),
            ("weight-semibold", 600), ("weight-bold", 700),
        ]:
            tokens[name] = {"$value": value}

        # Line heights
        for name, value in [
            ("leading-tight", 1.2), ("leading-normal", 1.5), ("leading-relaxed", 1.6),
        ]:
            tokens[name] = {"$value": value}

        return tokens

    # ─── Spacing derivation ──────────────────────────────────────────

    def _derive_spacing(self, d: Dict[str, Any]) -> Dict[str, Any]:
        """Derive spacing tokens from spacingBase."""
        base = d["spacingBase"]
        tokens = {}

        multipliers = {
            "space-0": 0, "space-1": 0.5, "space-2": 1, "space-3": 1.5,
            "space-4": 2, "space-5": 2.5, "space-6": 3, "space-8": 4,
            "space-10": 5, "space-12": 6, "space-16": 8, "space-20": 10,
        }
        for name, mult in multipliers.items():
            px = round(base * mult, 1)
            tokens[name] = self._ext_token(
                f"{px}px",
                f"{{spacingBase}} * {mult}",
                ["spacingBase"]
            )

        return tokens

    # ─── Radius derivation ───────────────────────────────────────────

    def _derive_radius(self, d: Dict[str, Any]) -> Dict[str, Any]:
        """Derive border radius tokens from radiusBase."""
        base = d["radiusBase"]
        tokens = {}

        multipliers = {
            "radius-none": 0, "radius-sm": 0.5, "radius-base": 0.75,
            "radius-md": 1.0, "radius-lg": 1.5, "radius-xl": 2.0,
            "radius-full": None,  # special case
        }
        for name, mult in multipliers.items():
            if mult is None:
                tokens[name] = {"$value": "9999px"}
            else:
                px = round(base * mult, 1)
                tokens[name] = self._ext_token(
                    f"{px}px",
                    f"{{radiusBase}} * {mult}",
                    ["radiusBase"]
                )

        return tokens

    # ─── Shadow derivation ───────────────────────────────────────────

    def _derive_shadows(self, d: Dict[str, Any]) -> Dict[str, Any]:
        """Derive shadow tokens (formulaic elevation-based)."""
        is_dark = d["bgLightness"] < 50
        alpha_base = 0.25 if is_dark else 0.1

        return {
            "shadow-sm": self._ext_token(
                f"0 2px 4px rgba(0, 0, 0, {alpha_base:.2f})",
                "elevation-based", ["bgLightness"]
            ),
            "shadow-md": self._ext_token(
                f"0 4px 12px rgba(0, 0, 0, {alpha_base + 0.1:.2f})",
                "elevation-based", ["bgLightness"]
            ),
            "shadow-lg": self._ext_token(
                f"0 8px 24px rgba(0, 0, 0, {alpha_base + 0.15:.2f})",
                "elevation-based", ["bgLightness"]
            ),
        }

    # ─── Transition derivation ───────────────────────────────────────

    def _derive_transitions(self, d: Dict[str, Any]) -> Dict[str, Any]:
        """Derive transition tokens from transitionBase."""
        base = d["transitionBase"]
        return {
            "duration-fast": self._ext_token(
                f"{round(base * 0.75)}ms",
                "{transitionBase} * 0.75", ["transitionBase"]
            ),
            "duration-base": self._ext_token(
                f"{base}ms",
                "{transitionBase}", ["transitionBase"]
            ),
            "duration-slow": self._ext_token(
                f"{round(base * 1.5)}ms",
                "{transitionBase} * 1.5", ["transitionBase"]
            ),
            "easing-standard": {
                "$value": "cubic-bezier(0.4, 0, 0.2, 1)"
            },
        }

    # ─── Token construction helpers ──────────────────────────────────

    @staticmethod
    def _color_token(L: float, C: float, H: float,
                     formula: str, inputs: List[str],
                     constraint: Optional[str] = None) -> Dict[str, Any]:
        """Create a color token with DTCG $extensions."""
        token: Dict[str, Any] = {
            "$value": f"oklch({L}% {C} {H})",
            "$extensions": {
                "com.vectorui": {
                    "formula": formula,
                    "inputs": inputs,
                }
            }
        }
        if constraint:
            token["$extensions"]["com.vectorui"]["constraint"] = constraint
        return token

    @staticmethod
    def _ext_token(value: Any, formula: str,
                   inputs: List[str],
                   constraint: Optional[str] = None) -> Dict[str, Any]:
        """Create a token with DTCG $extensions metadata."""
        token: Dict[str, Any] = {
            "$value": value,
            "$extensions": {
                "com.vectorui": {
                    "formula": formula,
                    "inputs": inputs,
                }
            }
        }
        if constraint:
            token["$extensions"]["com.vectorui"]["constraint"] = constraint
        return token

    @staticmethod
    def _dtcg_token(value: Any, formula: str,
                    inputs: List[str],
                    constraint: Optional[str] = None) -> Dict[str, Any]:
        """Create a DTCG-formatted token for theme.tokens.json output."""
        token: Dict[str, Any] = {
            "$value": value,
            "$extensions": {
                "com.vectorui": {
                    "formula": formula,
                    "inputs": inputs,
                }
            }
        }
        if constraint:
            token["$extensions"]["com.vectorui"]["constraint"] = constraint
        return token

    # ─── Validation helpers ──────────────────────────────────────────

    @staticmethod
    def _clamp(value: float, lo: float, hi: float) -> float:
        """Clamp value to [lo, hi] range."""
        return max(lo, min(hi, value))

    @staticmethod
    def _oklch_approx_luminance(L: float) -> float:
        """Approximate relative luminance from OKLCH lightness (0-1 range).

        OKLCH L is perceptual lightness, not luminance. This approximation
        converts using the cube relationship: Y ≈ L^3 (OKLab definition).
        """
        return L ** 3

    @staticmethod
    def _contrast_ratio(lum1: float, lum2: float) -> float:
        """Calculate WCAG contrast ratio between two relative luminances."""
        lighter = max(lum1, lum2)
        darker = min(lum1, lum2)
        return (lighter + 0.05) / (darker + 0.05)
