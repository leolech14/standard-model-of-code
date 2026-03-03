# Color Audit Report

Generated: 2026-03-01

Source files:
- `particle/schema/viz/tokens/appearance.tokens.json`
- `particle/src/core/viz/assets/modules/color-engine.js`
- `particle/src/core/viz/assets/modules/edge-system.js`
- `particle/src/core/viz/assets/modules/color-helpers.js`

---

## Summary

Three critical findings across all reports:

1. **ARCHITECTURAL SPLIT — TWO PARALLEL COLOR SYSTEMS THAT DO NOT SPEAK TO EACH OTHER.**
   The token file (`appearance.tokens.json`) defines colors for the Python baking path
   (read by `APPEARANCE_CONFIG` and consumed by `color-helpers.js` → `getTopoColor`).
   The JS palette in `color-engine.js` is the runtime path used by `COLOR.get()`.
   These two systems share the same conceptual keys (tier, family, ring, edge type) but have
   COMPLETELY DIFFERENT OKLCH values — different hues, chroma, and lightness throughout.
   The engine has no code that ever reads token values into the palette object.
   Tier T0 is Blue (h=236) in tokens vs. Green (h=142) in the JS engine.

2. **EDGE COLOR SYSTEM IS DISCONNECTED FROM TOKENS AND FROM THE COLOR ENGINE.**
   `edge-system.js` defines its own `PALETTES` and `PALETTE_HEX` objects in HSL (not OKLCH),
   uses hardcoded hex strings for gradient interpolation, and does NOT call `COLOR.get()`
   for gradient modes. The `PALETTE_HEX.tier` colors (muted grays) bear no resemblance to
   the token colors or the COLOR engine palette entries. The `type` and `mono` modes do
   call `COLOR.get('edgeType', ...)` and `COLOR.get('edgeType', 'unknown')` respectively,
   making those the only two modes with any token/engine connection.

3. **DARK-CANVAS LEGIBILITY FAILURES IN SCALE PALETTE.**
   The scale palette (L-3 through L2) has entries with l=0.25-0.35, which convert to
   very dark colors on the already-near-black canvas (~l=0.07-0.09). Entries L-3, L-2,
   L-1, and L12 all have lightness below 0.35 and will be nearly invisible. The same
   problem exists in the `magma`, `inferno`, and `mako` scheme paths where stops start
   at l=0.05-0.12 — invisible on a dark canvas.

---

## Report 1: Token-Engine Divergence Map

### Methodology

- **Token path**: `appearance.tokens.json` → `APPEARANCE_CONFIG.color` → `getTopoColor()` → node rendering
- **JS engine path**: `color-engine.js` palette object → `COLOR.get()` → node rendering
- **Delta thresholds**: hue >10deg, chroma >0.03, lightness >0.05 (as specified)
- **Lightness conversion**: token uses percentage (70.25%), engine uses decimal (0.68). Converted for comparison.

### Tier / Atom Colors

| Concept | Key | appearance.tokens OKLCH | color-engine.js OKLCH | Delta H / C / L | Verdict |
|---------|-----|------------------------|----------------------|-----------------|---------|
| Atom Tier | t0-core / T0 | h=236, c=0.1364, l=0.7025 (Blue) | h=142, c=0.20, l=0.68 (Green) | dH=94, dC=0.064, dL=0.022 | **CONFLICT** |
| Atom Tier | t1-arch / T1 | h=87.78, c=0.1521, l=0.7772 (Yellow) | h=220, c=0.11, l=0.65 (Blue) | dH=132, dC=0.042, dL=0.127 | **CONFLICT** |
| Atom Tier | t2-eco / T2 | h=310.47, c=0.25, l=0.5472 (Purple) | h=330, c=0.20, l=0.68 (Pink) | dH=20, dC=0.05, dL=0.133 | **CONFLICT** |
| Atom Tier | unknown | h=89.88, c=0.00, l=0.5103 (Gray) | h=0, c=0.04, l=0.50 (Gray) | dH=90 (irrelevant at c=0), dC=0.04, dL=0.010 | DRIFT |

Note: `color-engine.js` uses `palette.tier` for `COLOR.get('tier', 'T0')`. The token file uses `color.atom` (t0-core etc.) for the same concept. The mapping exists in `color-helpers.js getTopoColor()` which maps tiers to the atom section. So both paths claim to color the same nodes but produce completely different hues.

### Atom Family Colors

| Concept | Key | appearance.tokens OKLCH | color-engine.js OKLCH | Delta H / C / L | Verdict |
|---------|-----|------------------------|----------------------|-----------------|---------|
| Family | LOG | h=201.19, c=0.1492, l=0.8771 (Cyan) | h=220, c=0.11, l=0.62 (Blue) | dH=19, dC=0.039, dL=0.257 | **CONFLICT** |
| Family | DAT | h=156.86, c=0.21, l=0.8799 (Green) | h=142, c=0.20, l=0.68 (Green) | dH=15, dC=0.01, dL=0.200 | DRIFT (L conflict) |
| Family | ORG | h=80.53, c=0.1711, l=0.8272 (Gold) | h=280, c=0.18, l=0.60 (Purple) | dH=200, dC=0.009, dL=0.227 | **CONFLICT** |
| Family | EXE | h=15.46, c=0.2541, l=0.6354 (Red) | h=15, c=0.22, l=0.62 (Red) | dH=0.5, dC=0.034, dL=0.015 | MATCH |
| Family | EXT | h=301.37, c=0.2503, l=0.5338 (Purple) | h=35, c=0.20, l=0.65 (Orange) | dH=266, dC=0.050, dL=0.116 | **CONFLICT** |
| Family | UNKNOWN | h=89.88, c=0.00, l=0.5103 (Gray) | h=0, c=0.04, l=0.50 (Gray) | dH=irrelevant, dC=0.04, dL=0.010 | DRIFT |

Critical: ORG maps to Gold in tokens (h=80) but Purple in engine (h=280) — a 200 deg hue reversal.
EXT maps to Purple in tokens (h=301) but Orange in engine (h=35) — a 266 deg hue reversal.
LOG maps to bright Cyan (l=0.877) in tokens but dim Blue (l=0.62) in engine.

### Ring Colors

| Concept | Key | appearance.tokens OKLCH | color-engine.js OKLCH | Delta H / C / L | Verdict |
|---------|-----|------------------------|----------------------|-----------------|---------|
| Ring | DOMAIN | h=80.53, c=0.1711, l=0.8272 (Gold) | h=45, c=0.22, l=0.70 (Amber) | dH=36, dC=0.049, dL=0.127 | CONFLICT |
| Ring | APPLICATION | h=201.19, c=0.1492, l=0.8771 (Cyan) | h=220, c=0.20, l=0.65 (Blue) | dH=19, dC=0.051, dL=0.227 | CONFLICT |
| Ring | PRESENTATION | h=156.86, c=0.21, l=0.8799 (Green) | h=280, c=0.20, l=0.65 (Purple) | dH=123, dC=0.01, dL=0.230 | **CONFLICT** |
| Ring | INTERFACE | h=236.02, c=0.1364, l=0.7025 (Blue) | n/a (no INTERFACE in engine ring) | — | MISSING IN ENGINE |
| Ring | INFRASTRUCTURE | h=15.46, c=0.2541, l=0.6354 (Red) | h=0, c=0.04, l=0.50 (Gray) | dH=15, dC=0.214, dL=0.135 | **CONFLICT** |
| Ring | CROSS_CUTTING | h=301.37, c=0.2503, l=0.5338 (Purple) | n/a (no CROSS_CUTTING in engine) | — | MISSING IN ENGINE |
| Ring | TEST | h=330, c=0.145, l=0.65 (Magenta) | h=165, c=0.14, l=0.60 (Teal/Green) | dH=165, dC=0.005, dL=0.05 | **CONFLICT** |
| Ring | UNKNOWN | h=89.88, c=0.00, l=0.5103 | h=0, c=0.02, l=0.40 | dH=irrelevant, dL=0.110 | DRIFT |

Note: Ring key naming also diverges. `color-helpers.js` remaps ring keys:
`KERNEL->DOMAIN, CORE->APPLICATION, SERVICE->PRESENTATION, ADAPTER->INTERFACE`.
This means the key space doesn't match between systems and some keys that exist in tokens
(INTERFACE, CROSS_CUTTING) have no counterpart in the color engine's ring palette.

### Edge Type Colors

| Concept | Key | appearance.tokens OKLCH | color-engine.js OKLCH | Delta H / C / L | Verdict |
|---------|-----|------------------------|----------------------|-----------------|---------|
| Edge | calls | h=209, c=0.08, l=0.45 | h=220, c=0.12, l=0.55 | dH=11, dC=0.04, dL=0.10 | DRIFT |
| Edge | contains | h=162, c=0.07, l=0.40 | h=142, c=0.12, l=0.55 | dH=20, dC=0.05, dL=0.15 | CONFLICT |
| Edge | uses | h=85, c=0.09, l=0.45 | h=45, c=0.12, l=0.55 | dH=40, dC=0.03, dL=0.10 | CONFLICT |
| Edge | imports | h=90, c=0.00, l=0.35 | h=280, c=0.12, l=0.50 | dH=190, dC=0.12, dL=0.15 | **CONFLICT** |
| Edge | inherits | h=57, c=0.10, l=0.45 | h=330, c=0.12, l=0.55 | dH=273, dC=0.02, dL=0.10 | **CONFLICT** |
| Edge | default/unknown | h=242, c=0.01, l=0.25 | h=0, c=0.02, l=0.35 | dH=irrelevant, dL=0.10 | DRIFT |
| Edge | implements | n/a in tokens | h=165, c=0.12, l=0.55 | — | TOKEN MISSING |

Critical divergences:
- `imports`: tokens=gray (c=0, h=90), engine=purple (h=280, c=0.12) — completely different character
- `inherits`: tokens=orange (h=57), engine=pink (h=330) — 273 deg apart

### Interval Ranges (color-engine.js lines 209-311)

These have NO counterpart in `appearance.tokens.json` at all, except partial overlap with edge-modes weight/confidence configs:

| Interval | Token analog | Verdict |
|----------|-------------|---------|
| markov | none | TOKEN ABSENT |
| weight | edge-modes.weight (hue-min=210, hue-max=50, c=0.10, l=0.38) | PARTIAL — token l=0.38 vs engine range 0.35-0.65. Token hue range 210->50 vs engine 220->0 (similar intent, different endpoint) |
| confidence | edge-modes.confidence (hue-min=20, hue-max=120, c=0.10, l=0.40) | PARTIAL — token l=0.40 vs engine range 0.30-0.65 |
| complexity, churn, loc, trust, etc. | none | TOKEN ABSENT |

### Summary Score

- **MATCH**: 1 (EXE family)
- **DRIFT**: 4 (UNKNOWN entries where hue irrelevant, weight/confidence partial)
- **CONFLICT**: 17+ (most tier, family, ring, and edge type entries)
- **MISSING IN ENGINE**: 2 ring keys (INTERFACE, CROSS_CUTTING)
- **MISSING IN TOKEN**: 1 edge type (implements), 12+ intervals

**The two systems agree on almost nothing.** The Python baking path and the JS runtime path produce fundamentally different visual outputs for the same data.

---

## Report 2: Edge Color Mode Coverage

### The 8 Modes

| Mode | Data Source | Color Source | OKLCH Range (approx) | Default Opacity | Token-Connected? |
|------|------------|--------------|----------------------|----------------|-----------------|
| gradient-tier | `node.tier` (via `getNodeTierValue()`) | `PALETTE_HEX.tier` hardcoded hex: T0=#6a7a8a, T1=#7a6a8a, T2=#8a7a6a; cross-tier gets `COLOR.toHex({h:45,c:0.05,l:0.45})` | l~0.48-0.52, c~0.04-0.06, muted gray family | 0.08 | **No** — PALETTE_HEX values are hardcoded muted grays, not from tokens |
| gradient-file | `node.fileIdx` (file boundary index) | `COLOR.toHex()` — same-file: {h: goldenAngle*fileIdx, c:0.20, l:0.48}; cross-file: midpoint hue, c:0.12, l:0.50 | h=0-360 (golden angle dist), c=0.12-0.20, l=0.48-0.50 | 0.08 x 0.25 for cross-file (interfile_factor) | **Partial** — uses `COLOR.toHex()` (engine), not tokens. Default mode on startup. |
| gradient-flow | `link.markov_weight` or `link.weight` | `PALETTE_HEX.flow` hardcoded: cold=#5a6a7a, warm=#7a7a5a, hot=#8a5a5a; interpolated via `COLOR.interpolate()` | l~0.40-0.50, c~0.04-0.06, very muted | 0.08 | **No** — PALETTE_HEX.flow bypasses both tokens and `COLOR.get()` |
| gradient-depth | `node.depth` (via `getNodeDepth()`) | `PALETTE_HEX.depth` hardcoded: shallow=#66b3b3, mid=#7733cc, deep=#b3267a; interpolated | h=180-320 (cyan->purple->magenta), l~0.40-0.65, c~0.14-0.22 | 0.08 | **No** — PALETTE_HEX.depth is hardcoded |
| gradient-semantic | `getSemanticSimilarity(srcNode, tgtNode)` | `PALETTE_HEX.semantic` hardcoded: similar=#5a7a6a, related=#5a6a7a, different=#7a5a6a; interpolated | l~0.42-0.48, c~0.03-0.05, very muted grays | 0.08 | **No** — PALETTE_HEX.semantic bypasses both systems |
| type | `link.edge_type` or `link.type` (string key) | `COLOR.get('edgeType', key)` — reads from `palette.edgeType` in `color-engine.js` | h varies by type (220=calls, 142=contains, 45=uses, 280=imports, 330=inherits), c=0.12, l=0.50-0.55 | 0.08 | **Partial** — reads from color-engine.js palette (not tokens) |
| weight | `link.weight` (normalized) | `COLOR.getInterval('weight', t)` — reads from `intervals.weight`: {h:220->180->142, c:0.08->0.16, l:0.40->0.60} | h=142-220, c=0.08-0.16, l=0.40-0.60 | 0.08 | **Partial** — reads engine intervals, not tokens. Token edge-modes.weight parameters exist but are NOT read. |
| mono | `'unknown'` constant | `COLOR.get('edgeType', 'unknown')` -> palette.edgeType.unknown: {h:0, c:0.02, l:0.35} | h=0, c=0.02, l=0.35 (very dark, near black) | 0.08 | **Partial** — reads engine palette, not tokens |

### Opacity Details

- **Master opacity**: `DEFAULT_OPACITY = 0.08` (constant in edge-system.js line 115). This matches `appearance.tokens.json` opacity.edge = 0.08 — the only thing that does match!
- **Inferred edges**: `INFERRED_OPACITY = 0.04` (hardcoded line 116)
- **Cross-file edges** (gradient-file mode): opacity x `_config.dim.interfile_factor` = 0.08 x 0.25 = 0.02
- **Particle style**: opacity x 0.3 (minimum 0.1) — applied when `APPEARANCE_STATE.edgeStyle === 'particle'`
- **Layer crossfade**: multiplied by `link._viewOpacity` (0-1 runtime value)
- **APPEARANCE_STATE.edgeOpacity**: Runtime override that replaces DEFAULT_OPACITY if set

### Key Architecture Observations

1. **gradient-tier** has a logic bug: the first `if` branch (avgTier < 0.5) and the second `else if` branch (avgTier < 1.5) both interpolate between T0 and T1, making the second branch a duplicate. The T2 branch is only reached for avgTier >= 1.5. Additionally, the cross-tier early return (`if srcTier !== tgtTier return amber`) fires before the interpolation is used, so the expensive interpolation computed above is thrown away for cross-tier edges.

2. **PALETTE_HEX values** are described as "Pre-computed hex colors for OKLCH interpolation" (comment line 90) but are actually HSL-approximate muted grays — far darker and less saturated than the corresponding `PALETTES` HSL entries (e.g., `PALETTES.tier.T0 = {h:210, s:70, l:55}` but `PALETTE_HEX.tier.T0 = '#6a7a8a'` ~ {h:210, s:10, l:49}). The saturation has been crushed from 70% to ~10%.

3. **Token `edge-modes.weight`** and **`edge-modes.confidence`** sub-schemas define hue ranges and chroma values that are NEVER read by the edge system. The engine uses its own hardcoded `intervals.weight` object instead.

4. **gradient-file** is the default startup mode (`let _mode = 'gradient-file'` line 128), which means by default, edges are colored by file membership at chroma=0.12-0.20, NOT by any type or topology information.

---

## Report 3: Color Accessibility and Perceptual Quality

### 1. Perceptual Uniformity Within Categories

**tier** (palette.tier, 3+1 entries):
- T0: l=0.68, T1: l=0.65, T2: l=0.68, UNKNOWN: l=0.50
- Lightness range: 0.50-0.68. T0 and T2 are at the same lightness; T1 is 0.03 lower (negligible).
- The three tier entries are perceptually even. UNKNOWN (l=0.50) is noticeably darker.
- **Verdict: GOOD** uniformity among active tiers.

**family** (palette.family, 6 entries):
- LOG: l=0.62, DAT: l=0.68, ORG: l=0.60, EXE: l=0.62, EXT: l=0.65, UNKNOWN: l=0.50
- Lightness spread: 0.50-0.68 (0.18 range). DAT and ORG are 0.08 apart. Noticeable pop.
- **Verdict: MODERATE** uniformity. DAT pops slightly brighter.

**ring** (palette.ring, 5+1 entries):
- DOMAIN: l=0.70, APPLICATION: l=0.65, INFRASTRUCTURE: l=0.50, PRESENTATION: l=0.65, TESTING: l=0.60
- Lightness spread: 0.50-0.70 (0.20 range). INFRASTRUCTURE is 0.20 below DOMAIN — a strong perceptual step.
- Chroma: DOMAIN=0.22, APPLICATION=0.20, INFRASTRUCTURE=0.04, PRESENTATION=0.20, TESTING=0.14
- INFRASTRUCTURE is both darker AND less chromatic — nearly invisible relative to DOMAIN.
- **Verdict: POOR** uniformity. INFRASTRUCTURE will appear as a dark gray stub next to vivid amber/blue/purple entries.

**atom** (palette.atom, 11 entries):
- Lightness range: 0.60 (class, struct, field) to 0.70 (module). Spread=0.10.
- Chroma range: 0.18 (variable/field) to 0.24 (package). Spread=0.06.
- **Verdict: GOOD** — relatively tight cluster.

**scale** (palette.scale, 16 entries, L-3 to L12):
- Physical zone (L-3 to L-1): l=0.28, 0.35, 0.42 — very dark
- Syntactic zone (L0): l=0.55
- Semantic zone (L1-L3): l=0.78, 0.85, 0.92 — very bright
- Systemic zone (L4-L7): l=0.40-0.52
- Cosmological zone (L8-L12): l=0.45 down to 0.25
- Lightness spread: 0.25 (L12, UNIVERSE) to 0.92 (L3, NODE) — a 0.67 range!
- **Verdict: EXTREMELY non-uniform** by design (encodes scale metaphor), but problematic for rendering.

**levelZone** (5+1 entries):
- PHYSICAL: l=0.35, SYNTACTIC: l=0.55, SEMANTIC: l=0.85, SYSTEMIC: l=0.45, COSMOLOGICAL: l=0.30
- Spread: 0.30-0.85. Again by design but extreme.

**fileType** (15 entries):
- Lightness range: 0.50 (cpp) to 0.75 (json). Spread=0.25.
- Chroma range: 0.02 (md, unknown) to 0.25 (html). Spread=0.23.
- **Verdict: MODERATE**. json (l=0.75) and md (l=0.70, c=0.04) pop differently from cpp (l=0.55, c=0.20).

**subsystem** (11 entries):
- Lightness range: 0.50 (Security, h=0 red) to 0.75 (Observability, h=60 yellow).
- Chroma range: 0.00 (Unknown) to 0.26 (Security).
- **Verdict: MODERATE**. Observability (l=0.75) and Delivery (l=0.70) are distinctly brighter than Domain (l=0.55) and Security (l=0.55).

**roleCategory** (11 entries):
- Lightness range: 0.50 (Unknown, c=0) to 0.70 (Validation, Utility).
- Chroma range: 0.00 (Internal, Unknown) to 0.24 (Command, Validation).
- Internal (l=0.60, c=0.00) and Unknown (l=0.50, c=0.00) are neutral grays — intentional.
- **Verdict: MODERATE**, by design.

### 2. Distinguishability (Colorblind Hue Separation)

Pairs with <20 deg hue separation at similar lightness — candidates for confusion:

**tier:**
- T0 (h=142) vs T1 (h=220): 78 deg — fine.
- T1 (h=220) vs T2 (h=330): 110 deg — fine.
- T0 (h=142) vs T2 (h=330): 188 deg — fine.
- **Verdict: GOOD** for colorblind users.

**family:**
- LOG (h=220) vs ORG (h=280): 60 deg at similar lightness — borderline for deuteranopia.
- LOG (h=220) vs EXT (h=35): 175 deg — fine.
- DAT (h=142) vs EXT (h=35): 107 deg — fine.
- **Verdict:** LOG/ORG pair (blue vs purple, 60 deg) may merge for blue-purple blind users.

**ring:**
- APPLICATION (h=220) vs PRESENTATION (h=280): 60 deg — same LOG/ORG issue, blue vs purple.
- **Verdict: FLAGGED** — APPLICATION and PRESENTATION will appear similar to tritanopes and some deuteranopes.

**atom (CRITICAL):**
- function (h=160) vs method (h=175): **15 deg apart**, same lightness 0.65/0.62. **CRITICAL FLAG.**
- method (h=175) vs closure (h=190): **15 deg apart**, l=0.62/0.60. **CRITICAL FLAG.**
- function/method/closure form a 30 deg cluster (h=160-190) — nearly indistinguishable to anyone with reduced color acuity.
- class (h=260) vs struct (h=240): **20 deg apart**, l=0.60 both. **FLAGGED.**
- class (h=260) vs interface (h=280): **20 deg apart**, l=0.60/0.65. **FLAGGED.**
- module (h=45) vs package (h=30): **15 deg apart**, l=0.70/0.65. **CRITICAL FLAG.**
- variable (h=340) vs field (h=350): **10 deg apart**, l=0.65/0.62. **CRITICAL FLAG.**
- **Verdict: POOR.** The atom palette has 5 pairs with <20 deg hue separation. For a visualization where atoms are the primary node type, this is a serious usability problem.

**roleCategory:**
- Query (h=190) vs Utility (h=200): **10 deg apart**, l=0.65/0.70. **CRITICAL FLAG.**
- Command (h=25) vs Factory (h=280): 255 deg — fine.
- Orchestration (h=240) vs Event (h=260): **20 deg** — FLAGGED.
- **Verdict: POOR** for fine atom-type discrimination.

**subsystem:**
- Config (h=290) vs Async (h=300): **10 deg apart**, l=0.65/0.60. **FLAGGED.**
- Ingress (h=220) vs Persistence (h=142): 78 deg — fine.
- Delivery (h=30) vs Egress (h=20): **10 deg apart**, l=0.70/0.60. **FLAGGED.**
- **Verdict: MODERATE** issues.

**edgeType:**
- ALL edge types have identical chroma c=0.12. Only hue varies.
- calls (h=220) vs contains (h=142): 78 deg — fine.
- uses (h=45) vs inherits (h=330): 75 deg — fine.
- implements (h=165) vs contains (h=142): **23 deg** at same lightness. **FLAGGED.**
- **Verdict: MODERATE.**

### 3. Dark-Background Legibility

Canvas background is approximately `oklch(7-9% 0.02 250)`. Entries with l < 0.35 will be nearly invisible.

**Entries with l < 0.35 (INVISIBLE on dark canvas):**

| Category | Key | l value | Status |
|----------|-----|---------|--------|
| scale | L-3 (BIT) | 0.28 | **INVISIBLE** |
| scale | L-2 (BYTE) | 0.35 | BORDERLINE |
| scale | L12 (UNIVERSE) | 0.25 | **INVISIBLE** |
| scale | L11 (DOMAIN) | 0.30 | **INVISIBLE** |
| scale | L10 (ORGANIZATION) | 0.35 | BORDERLINE |
| levelZone | COSMOLOGICAL | 0.30 | **INVISIBLE** |
| levelZone | PHYSICAL | 0.35 | BORDERLINE |
| edgeType | unknown | 0.35 | BORDERLINE for edges |

**Entries with 0.35 <= l < 0.45 (dim but functional):**
- markov interval stop at v=0: l=0.35
- weight interval stop at v=0: l=0.40
- scale L-1 (CHARACTER): l=0.42
- scale L4 (CONTAINER): l=0.40
- scale L5 (FILE): l=0.44
- ring INFRASTRUCTURE: l=0.50 — OK but low chroma makes it gray

### 4. Chroma Consistency

**tier:** c=0.20, 0.11, 0.20 + UNKNOWN=0.04. T1 (Blue, h=220) has c=0.11 due to sRGB gamut constraint for blue hues. This is visually correct (blue at high chroma clips in sRGB) but T1 will appear slightly less vivid than T0 and T2. The comment in the code ("Blue (c=0.11 max for sRGB)") acknowledges this.

**family:** c range = 0.04-0.22. LOG (blue, h=220) is limited to c=0.11 by gamut. EXE (red) has c=0.22. Cross-family chroma consistency is MODERATE.

**ring:** c range = 0.02-0.22. APPLICATION (h=220, c=0.20) — notably higher than expected given the gamut constraint noted for tier T1 at the same hue. This is a MINOR INCONSISTENCY: tier.T1 uses c=0.11 for h=220 but ring.APPLICATION uses c=0.20 for h=220. ring.APPLICATION will clip in sRGB.

**edgeType:** All entries have c=0.12 exactly — perfectly consistent by design.

**scale (physical zone, L-3 to L-1):** c descends 0.18->0.16->0.14 as l descends 0.28->0.35->0.42. Low chroma reinforces the "deep" metaphor but makes these entries look very gray at already-dark lightness.

**scale (semantic zone, L1-L3):** c=0.10, 0.12, 0.08 — low chroma at high lightness. L3 (NODE, l=0.92, c=0.08) will appear almost white, distinguishable only from the background.

### 5. Named Scheme Analysis (33 schemes)

**Perceptual types:**

- **Sequential** (monotonic lightness): viridis, plasma, magma, inferno, cividis, mako, rocket, ocean, nightvision, query, finder, command, creator, destroyer, factory, repository, cache, service, orchestrator, validator, guard, transformer, parser, handler, emitter, utility, lifecycle, ramp-lightness (~27 schemes)
- **Diverging** (center-outward, two-tailed): coolwarm, spectral (~2 schemes)
- **Mathematical paths** (generator functions): rainbow-loop, rainbow-bright, rainbow-dark, arc-warm, arc-cool, arc-nature, spiral-up, spiral-down, spiral-chroma, wave-lightness, wave-chroma, pulse, ramp-hue, ramp-chroma, helix, convergent, divergent, bicone (~18 schemes)

**Schemes with problematic lightness ranges on dark canvas:**

- **magma**: starts at l=0.08 (near black) — the bottom 25% is invisible
- **inferno**: starts at l=0.05 — the bottom 20% is invisible
- **mako**: starts at l=0.12 — the bottom 25% is very dim
- **rocket**: starts at l=0.10 — same issue
- **destroyer**: ends at l=0.25 (dark destruction) — the top 30% goes dark
- **helix** generator: starts at l=0.30 — low end is borderline
- **rainbow-dark**: constant l=0.45 — acceptable but dim, chroma=0.18 helps
- **spiral-up** generator: starts at l=0.30 — low values dim
- **viridis**: starts at l=0.25 — the zero-end anchor is borderline
- **lifecycle**: ends at l=0.35 (death/purple) — the high-value end goes dark

**Summary:**
- 27 of 33 schemes are sequential in structure
- 2 are diverging (coolwarm, spectral)
- 4 are oscillating/geometric (bicone, wave-lightness, wave-chroma, pulse)
- At least 10 schemes have anchors below l=0.35 that will be invisible on the dark canvas
- The generator-based schemes are unconstrained by any token system
- No scheme enforces a minimum lightness for dark-canvas safety
