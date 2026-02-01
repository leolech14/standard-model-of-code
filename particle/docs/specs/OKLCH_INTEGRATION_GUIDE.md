# OKLCH Color System Integration Guide

> **Purpose:** Single source of truth for integrating OKLCH colors into UI features.
> **Generated:** 2026-01-26 | **Status:** Canonical

---

## 1. OKLCH Basics

**What is OKLCH?** A perceptually-uniform color space:

| Dimension | Range | Meaning |
|-----------|-------|---------|
| **L (Lightness)** | 0-1 (0-100%) | Perceptual brightness |
| **C (Chroma)** | 0-0.4 | Color saturation (0=gray, 0.4=vivid) |
| **H (Hue)** | 0-360° | Color identity |

**Why OKLCH?** Perceptually uniform - equal visual changes at any hue/saturation.

---

## 2. Available APIs

### JavaScript: `color-engine.js`

**Global Object:** `window.COLOR`

```javascript
// Semantic lookup
COLOR.get('tier', 'T0')              // → '#A1B2C3'
COLOR.get('family', 'LOG')           // → hex
COLOR.get('ring', 'DOMAIN')          // → hex

// Gradient position (0-1)
COLOR.getInterval('confidence', 0.75)
COLOR.getInterval('weight', 0.5)

// Raw OKLCH values
COLOR.getRaw('tier', 'T0')           // → {h: 142, c: 0.20, l: 0.68}

// Conversions
COLOR.hexToOklch('#A1B2C3')
COLOR.toHex({h: 220, c: 0.15, l: 0.65})

// Interpolation
COLOR.interpolate('#FF0000', '#0000FF', 0.5)

// Categories
COLOR.getCategories('tier')          // → ['T0', 'T1', 'T2', 'UNKNOWN']
```

**Transform API (global modifiers):**

```javascript
COLOR.setTransform('hueShift', 30)       // Rotate all hues
COLOR.setTransform('chromaScale', 1.5)   // Boost saturation
COLOR.setTransform('lightnessShift', 10) // Brighten
COLOR.resetTransforms()                   // Reset to defaults
```

**33 Named Schemes:**

```javascript
COLOR.listSchemes()                      // All available
COLOR.applyScheme('plasma')              // Set globally
COLOR.getSchemeColor('viridis', 0.7)     // Color at position
COLOR.getSchemeGradientCSS('plasma')     // CSS gradient
```

**Subscriptions:**

```javascript
COLOR.subscribe((event, data) => {
    if (event === 'transform-change') { /* re-render */ }
});
```

### JavaScript: `color-helpers.js`

```javascript
COLOR_HELPERS.getTopoColor('tiers', 'T0')    // → {l, c, h}
COLOR_HELPERS.normalizeInput('oklch(...)')   // → hex
COLOR_HELPERS.dim('#FF0000', 0.5)            // Perceptual dim
COLOR_HELPERS.getFileColor(idx, total, name) // Golden angle
COLOR_HELPERS.getFileHue(idx, total)         // 0-360
```

### Python: `appearance_engine.py`

```python
from .appearance_engine import AppearanceEngine

engine = AppearanceEngine()

# Parse OKLCH string
parsed = engine._parse_oklch('0.7 0.25 220')

# Convert OKLCH to sRGB
r, g, b = engine._oklch_to_srgb(L=0.7, C=0.25, H=220)
```

### Python: `oklch_color.py`

```python
from .oklch_color import OKLCHColorMapper

mapper = OKLCHColorMapper()

# Get color by file attributes
hex_color = mapper.get_rgb_hex('.py', recency_days=7, importance=0.8)
css_color = mapper.get_oklch_css('.py', 7, 0.8)  # 'oklch(0.70 0.25 220)'
```

### CLI: `.agent/tools/oklch_color.py`

```bash
python .agent/tools/oklch_color.py <command>
```

---

## 3. Integration Patterns

### For CSS: Design Tokens

```css
/* Use CSS variables (auto-generated from tokens) */
color: var(--color-atom-t0-core);
background: var(--color-ring-DOMAIN);
```

**Don't write OKLCH directly.** Define in Python → export to tokens → use in CSS.

### For JavaScript: Getting Colors

**Pattern 1: Semantic Lookup**
```javascript
const tierColor = COLOR.get('tier', 'T0');
node.color = new THREE.Color(tierColor);
```

**Pattern 2: Gradient Mapping**
```javascript
const color = COLOR.getInterval('confidence', node.confidence);
```

**Pattern 3: Scheme-Based**
```javascript
COLOR.applyScheme('plasma');
const color = COLOR.getSchemeColor('plasma', normalized);
```

**Pattern 4: File Colors**
```javascript
const color = COLOR_HELPERS.getFileColor(fileIdx, totalFiles, fileName);
```

---

## 4. Semantic Color Mappings

### Hue Wheel (File Types)

From `.agent/config/hue_wheel.yaml`:

| Family | Extensions | Hue Range | Semantic |
|--------|------------|-----------|----------|
| Logic | .py, .js, .ts, .go | 180-300° | Computation |
| Config | .json, .yaml, .toml | 30-90° | Configuration |
| Docs | .md, .txt, .html | 90-150° | Documentation |
| Assets | .png, .jpg, .svg | 300-360° | Media |

### Semantic Dimensions

```javascript
// tier
'T0': {h: 142, c: 0.20, l: 0.68}  // Green - Foundation
'T1': {h: 220, c: 0.11, l: 0.65}  // Blue - Domain
'T2': {h: 330, c: 0.20, l: 0.68}  // Pink - Application

// family
'LOG': {h: 220, c: 0.11, l: 0.62}  // Logic (blue)
'DAT': {h: 142, c: 0.20, l: 0.68}  // Data (green)
'ORG': {h: 280, c: 0.18, l: 0.60}  // Organization (purple)

// ring
'DOMAIN': {h: 45, c: 0.22, l: 0.70}        // Amber
'APPLICATION': {h: 220, c: 0.20, l: 0.65}  // Blue
```

---

## 5. Quick Reference

### "I need a color for a new node type"

1. Add to `color-engine.js` palette:
   ```javascript
   palette.myDimension = {
       'MY_CATEGORY': {h: 200, c: 0.18, l: 0.65}
   };
   ```

2. Use it:
   ```javascript
   const color = COLOR.get('myDimension', 'MY_CATEGORY');
   ```

### "I need to add a gradient"

Add to `intervals` in `color-engine.js`:
```javascript
intervals.myMetric = {
    stops: [
        {value: 0.0, h: 220, c: 0.10, l: 0.40},
        {value: 1.0, h: 0, c: 0.20, l: 0.60}
    ]
};
```

Use: `COLOR.getInterval('myMetric', 0.5)`

### "I need accessible colors"

```javascript
COLOR.applyScheme('cividis');   // Colorblind-optimized
// Or use low chroma
{h: 220, c: 0.08, l: 0.60}      // Muted, safer
```

### "I need to modify all colors"

```javascript
COLOR.setTransform('hueShift', 180);     // Invert hues
COLOR.setTransform('chromaScale', 1.5);  // Boost saturation
```

---

## 6. File Locations

| File | Purpose | Edit? |
|------|---------|-------|
| `.agent/config/hue_wheel.yaml` | File type → hue | YES |
| `src/core/viz/assets/modules/color-engine.js` | JS palettes & schemes | YES |
| `src/core/viz/assets/modules/color-helpers.js` | JS utilities | RARELY |
| `src/core/viz/appearance_engine.py` | Python color engine | MAYBE |
| `.agent/tools/oklch_color.py` | CLI tool | MAYBE |

---

## 7. Validation

**Python & JS must produce identical hex for same OKLCH:**

```python
# Python
hex_py = OKLCHColorMapper.oklch_to_rgb(l=0.68, c=0.20, h=142)
```

```javascript
// JavaScript
const hex_js = COLOR.toHex({h: 142, c: 0.20, l: 0.68});
```

Both should match. If not, check conversion matrix.

---

## 8. Constraints

| Constraint | Reason |
|-----------|--------|
| Chroma max 0.4 | sRGB gamut safety |
| Blue needs low C (~0.11) | sRGB limits |
| Transforms are global | Single state machine |

---

## 9. Checklist for New Features

- [ ] Choose dimension or create gradient
- [ ] Add to `color-engine.js` or `hue_wheel.yaml`
- [ ] Test: `COLOR.get()` returns expected color
- [ ] Validate hex matches Python ↔ JS
- [ ] Wire to visualization
- [ ] Test with transform sliders
