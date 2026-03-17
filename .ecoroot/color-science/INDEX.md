# Color Science & Beauty Laws — Consolidated Index

> All correlated knowledge across PROJECT_vector-ui, PROJECT_elements, and the parametric UI engine.
> This directory is the SINGLE READING POINT for any agent working on color, beauty, or parametric constraints.

---

## The 5 Universal Laws of UI Beauty

Discovered from 149,695 Android UIs (513K total dataset). Correlations r > 0.90.

| # | Law | Parameter | Safe Zone | Optimal | Extended | Source |
|---|-----|-----------|-----------|---------|----------|--------|
| 1 | Complexity | total_atoms | 28-125 | 41 | 9-281 | vector-ui |
| 2 | Entropy | spacing_shannon_entropy | 2.10-3.00 | 2.70 | 1.90-3.20 | vector-ui |
| 3 | Color Contrast | oklch_delta_e_mean | 2.0-3.5 | 2.75 | 1.5-4.5 | vector-ui |
| 4 | Grid Adherence | spacing_grid_adherence | 0.5-1.0 | 0.64 | 0.3-1.0 | vector-ui |
| 5 | Grid Error | spacing_grid_error_mean | 0.0-2.0px | 1.0px | 0.0-3.0px | vector-ui |

### Counterweight Laws (Trade-offs)
- **Harmony Counterweight** (r = -0.8508): analogous ↑ = triadic ↓
- **Diversity Counterweight** (r = -0.8414): can't maximize all dimensions

### Key Discovery
Beauty = Controlled Variation, NOT consistency. Higher entropy → more beautiful (r = +0.899).

---

## Source Files (by location)

### PROJECT_vector-ui (research origin)

| File | Content | Priority |
|------|---------|----------|
| `UI_ALGEBRA_SAFE_ZONES.md` | The 5 safe zones with counterweight formula, scoring system | READ FIRST |
| `docs/SESSION_PHASE_2_COMPLETE_BEAUTY_LAWS_DISCOVERED.md` | Discovery narrative, methodology, 5 laws with evidence | READ SECOND |
| `03_ANALYSIS/reports/analysis_summary_oklch.json` | Raw data: 149K UIs, 36 metrics, 72 correlations, 5 laws | DATA |
| `02_DATASETS/processed/ui_beauty_dataset.db` | SQLite: beauty scores per UI | DATA |
| `02_DATASETS/universal_dataset.db` | SQLite: full 513K UI dataset | DATA |
| `04_PIPELINE/scripts/04_universal_laws.py` | Python: law discovery pipeline | CODE |
| `SCIENTIFIC_PAPER_FIGURES/Figure1_Universal_Laws.png` | Publication-ready figure | VISUAL |
| `EDUCATIONAL_FIGURES/EDUCATIONAL_2_All_Laws_Complete_Guide.png` | All 5 laws visual guide | VISUAL |
| `DESIGN_SYSTEM_UNIVERSALITY_ANALYSIS.md` | Design system analysis | ANALYSIS |

### PROJECT_elements (implementation)

| File | Content | Priority |
|------|---------|----------|
| `particle/src/core/viz/color_science.py` | OKLCH ↔ sRGB conversion, gamut mapping, WCAG/APCA, palettes | CANONICAL CODE |
| `particle/tests/test_color_science.py` | Tests for color science module | TESTS |
| `particle/docs/theory/whitepapers/COLOR_ENGINE_THEORY.md` | Full theory: 72 data fields, combinatorial analysis | THEORY |
| `particle/docs/theory/whitepapers/COLOR_THEORY_PSYCHOLOGY_TEXTBOOK.md` | Color perception research | THEORY |
| `particle/docs/theory/whitepapers/COLOR_THEORY_INTEL_TEXTBOOK.md` | Color intelligence for AI | THEORY |
| `particle/docs/research/perplexity/20260314_211356_what_are_the_established_color_schemas_and_color_w.md` | Perplexity research on color schemas | RESEARCH |
| `wave/experiments/refinery-platform/app/globals.css` | Algebra-UI: 644 lines, OKLCH parametric engine | PRODUCTION CSS |
| `wave/experiments/refinery-platform/lib/engine/beauty.ts` | Beauty constraints (8 rules) for parametric control panel | PRODUCTION TS |
| `wave/experiments/refinery-platform/lib/engine/parameters.ts` | 28 tunable parameters with beauty region bounds | PRODUCTION TS |

### Other Projects

| File | Content |
|------|---------|
| `PROJECT_rovelab/COLOR_SCHEMA_OKLCH.md` | OKLCH schema reference |
| `PROJECT_orchestra/obsidian-orchestra/scf.70_OKLCH_DESIGN.md` | OKLCH design notes |
| `PROJECT_obsidian/obsidian-vault-intelligence/OKLCHColorModes.ts` | TypeScript OKLCH modes |

---

## How Beauty Laws Map to Parametric Controls

| Beauty Law | Refinery Parameter | Beauty Constraint | Status |
|-----------|-------------------|-------------------|--------|
| Law 3 (ΔE 2.0-3.5) | `--bg-l`, `--text-l`, chromatic L seeds | `text-contrast`, `chromatic-contrast` | IMPLEMENTED (simplified) |
| Law 2 (Entropy 2.10-3.00) | `--density`, `--space-unit` | `density-bounds` | IMPLEMENTED (crude) |
| Law 4 (Grid 0.5-1.0) | `--space-unit` (→ grid base) | Not yet | MISSING |
| Law 5 (Error < 2px) | `--radius-seed` (sub-pixel precision) | Not yet | MISSING |
| Law 1 (Atoms 28-125) | Node count per page | `zone-balance` in sieve.ts (partial) | PARTIAL |
| Harmony Counterweight | Chromatic hue relationships | Not yet | MISSING |

### What's Missing in beauty.ts

The current 8 beauty constraints use estimated thresholds. They should use the EMPIRICAL thresholds from 149K UIs:

1. **Text contrast**: currently `|text-l - bg-l| >= 0.4`. Should map through OKLCH ΔE formula and validate against ΔE 2.0-3.5 safe zone.
2. **Chromatic contrast**: currently `|hue-l - bg-l| >= 0.25`. Should use the actual gamut_map_oklch from color_science.py to compute ΔE per hue.
3. **Density**: currently `0.5-2.0`. Should correlate with spacing entropy safe zone 2.10-3.00.
4. **Missing**: harmony counterweight (analogous vs triadic trade-off), grid adherence validation, atom count per zone.

---

## The Beauty Score Formula

From `UI_ALGEBRA_SAFE_ZONES.md`:

```python
BEAUTY = (
    complexity_law(atoms) * 20 +      # Law 1
    entropy_law(spacing) * 20 +        # Law 2
    color_law(delta_e) * 20 +          # Law 3
    grid_law(adherence) * 20 +         # Law 4
    error_law(deviation) * 20          # Law 5
) / 5

# Score range: 0-100
# Safe zone: 60+ (beautiful)
# Gold zone: 80+ (exceptional)
```

---

## OKLCH Quick Reference

```
L (Lightness): 0.0 (black) → 1.0 (white)
C (Chroma):    0.0 (gray) → ~0.4 (maximum saturation, gamut-dependent)
H (Hue):       0° → 360° (perceptually uniform angle)

Key: OKLCH is perceptually uniform — equal math = equal perception.
HSL has 50° error for yellow perception. OKLCH has zero.

ΔE (Delta E) = perceptual color difference:
  < 1.0: imperceptible
  1.0-2.0: just noticeable
  2.0-3.5: SAFE ZONE (clear but harmonious)
  3.5-10: strong contrast (functional but harsh)
  > 10: jarring
```

---

## Gamut Mapping (from color_science.py)

When you pick an OKLCH color, it might be outside sRGB gamut (not displayable). The `gamut_map_oklch()` function uses CSS Color Level 4 binary search to reduce chroma until the color fits sRGB — preserving hue and lightness.

This is critical for the parametric sliders: as users slide chromatic lightness seeds, some L+C+H combinations go out of gamut. The gamut mapper finds the maximum legal chroma.

---

*Index created: 2026-03-17 | Consolidates: vector-ui (research) + elements (implementation) + refinery (production)*
