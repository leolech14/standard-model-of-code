# UI Refactor Vision

> Captured: 2026-01-20
> Status: Planning Phase

## Design Philosophy

**Core Principle:** The UI should be invisible. Its function is to convey information, not to be noticed. No glowy, futuristic, neon aesthetics. Just boring, functional, discreet interfaces that get out of the way.

---

## Change Request #1: Bottom Component (Footer → Floating Mapper)

### Current State
- Fixed footer at bottom of page
- Full-width, glued to bottom edge
- Contains: Scope selector (Selected Nodes / All Nodes)
- Style: Part of the sidebar system, feels like a footer

### Desired State
- **Floating component** in bottom-center of canvas
- NOT full-width - compact, centered
- Like ChatGPT input bar / "Higgs Field" input bar style
- **Purpose:** Visual Mapping Interface
  - Simple UI to map: `[Visual Attribute]` ↔ `[Data Parameter]`
  - Example: "Size of nodes" ↔ "File size in bytes"
  - Make it obvious: "You matched these two values, now they correlate visually"
- Give users full data visualization power in an intuitive way

### Files Involved
| File | Current Role | Changes Needed |
|------|--------------|----------------|
| `template.html` | Contains footer markup | Restructure to floating component |
| `styles.css` | Footer styles | New floating styles, centered positioning |
| `modules/control-bar.js` | Visual mapping logic | May need to integrate with new component |
| `modules/sidebar.js` | Currently manages this? | Remove footer responsibility |

### Legacy to Handle
- Current footer markup in template.html
- Footer-related CSS classes
- Any JS that expects footer to be part of sidebar

### Confidence: 85%
### Complexity: Medium

---

## Change Request #2: UI Color Palette - De-glamorize

### Current State
- Bright light blue accent colors
- Glowy, futuristic aesthetic
- Neon-replacement colors that still attract attention
- Interface "wants to be seen"

### Desired State
- Boring, muted colors
- Discreet, unnoticeable
- Functional over aesthetic
- "You don't even notice it's there"
- Interface that delivers information invisibly

### Files Involved
| File | Current Role | Changes Needed |
|------|--------------|----------------|
| `styles.css` | All UI colors defined here | Mute all accent colors |
| `template.html` | Inline styles? | Remove any inline glowy styles |
| `modules/theme.js` | Theme configuration | Update color palette |

### Color Direction
- Replace bright blues with muted grays
- Remove glow effects (box-shadow with color)
- Reduce contrast between UI and background
- Make borders subtle, not prominent

### Legacy to Handle
- Current color variables in CSS
- Any hardcoded colors in JS

### Confidence: 90%
### Complexity: Low-Medium

---

## Change Request #3: Remove Star Field Feature

### Current State
- Star field exists in codebase
- Toggle in sidebar (shows "deactivated")
- **BUG:** Stars appear on canvas even when toggle is off
- Only disappears after toggle on→off cycle

### Desired State
- **Remove entirely** - not just hide
- Rationale: Nodes ARE the stars. Adding more dots creates confusion.
- Meaningless visual elements that look strikingly similar to actual data

### Files Involved
| File | Current Role | Changes Needed |
|------|--------------|----------------|
| `modules/stars.js` | Star field implementation | DELETE or archive |
| `template.html` | Star toggle in sidebar | Remove toggle |
| `styles.css` | Star-related styles | Remove |
| `modules/main.js` | STARS module wiring | Remove references |
| `app.js` | Any star initialization | Remove |

### Legacy to Handle
- `modules/stars.js` - archive to `archive/` folder
- STARS_STORAGE_KEY in localStorage
- Any references in other modules

### Confidence: 95%
### Complexity: Low

---

## Change Request #4: Resizable Sidebar Sections (Vertical)

### Current State
- Fixed-height sections within sidebars
- No ability to resize individual sections
- Some sections have empty space (right sidebar bottom)
- Cannot compact or expand sections

### Desired State
- **Drag borders** between sections to resize vertically
- Each section independently resizable
- **Constraints:**
  - Minimum height: ~66-100px (keeps section visible but compact)
  - Maximum height: Slightly more than content needs
  - Scrollable when compacted below content height
- Smart behavior: respect element count in section

### Files Involved
| File | Current Role | Changes Needed |
|------|--------------|----------------|
| `template.html` | Section structure | Add resize handles |
| `styles.css` | Section styles | resize cursor, min/max heights |
| `modules/sidebar.js` | Sidebar logic | Add resize drag handlers |

### Implementation Notes
- Use CSS `resize: vertical` or custom drag handlers
- Store user preferences in localStorage
- Sections: filters, schemes, controls, etc.

### Legacy to Handle
- Current fixed-height CSS
- Any hardcoded height values

### Confidence: 75%
### Complexity: Medium-High

---

## Change Request #5: Resizable Sidebars (Horizontal)

### Current State
- Fixed-width left and right sidebars
- Vertical divider line exists but not draggable
- Cannot adjust canvas vs sidebar ratio

### Desired State
- **Drag vertical divider** to resize sidebars
- Left and right sidebars resize **independently**
- Components inside **reflow** when width changes:
  - More width → elements spread horizontally, less vertical space
  - Less width → elements stack vertically, more scrolling
- Smart responsive behavior

### Files Involved
| File | Current Role | Changes Needed |
|------|--------------|----------------|
| `template.html` | Layout structure | Add draggable dividers |
| `styles.css` | Sidebar widths | Flexbox/Grid adjustments |
| `modules/sidebar.js` | Sidebar management | Resize handlers, reflow logic |

### Implementation Notes
- CSS Grid or Flexbox with dynamic columns
- Store widths in localStorage
- Minimum sidebar width to prevent collapse
- Maximum to prevent canvas from disappearing

### Legacy to Handle
- Current fixed-width CSS
- Any layout assumptions in JS

### Confidence: 70%
### Complexity: High

---

## Summary Task List

| # | Task | Confidence | Complexity | Priority |
|---|------|------------|------------|----------|
| 1 | Remove star field feature | **98%** | Low | High |
| 2 | De-glamorize UI colors | **95%** | Low-Med | High |
| 3 | Convert footer to floating mapper | **92%** | Medium | High |
| 4 | Add vertical section resizing | **85%** | Med-High | Medium |
| 5 | Add horizontal sidebar resizing | **80%** | High | Medium |

### Confidence Justification (Updated after code review)

**#1 Stars (98%):** Code is isolated - `modules/stars.js` (89 lines), starfield creation in app.js (lines 1997-2019), MODULE_ORDER in visualize_graph_webgl.py. Clean removal.

**#2 Colors (95%):** All glowy colors are in `control-bar.js` inline styles and `styles.css`. Pattern: `rgba(100, 150, 255, ...)` everywhere. Search-and-replace friendly.

**#3 Floating Mapper (92%):** `control-bar.js` already has the EXACT UI needed (SCOPE, MAP, TO, SCALE, APPLY). Just needs CSS repositioning:
- Current: `position: fixed; bottom: 0; left: 0; right: 0;` (full-width)
- Needed: `left: 50%; transform: translateX(-50%); max-width: 900px; border-radius: 12px;`

**#4 Vertical Section Resize (85%):** Template already uses `.section` > `.section-header` + `.section-content` pattern. Add CSS `resize: vertical` or custom drag handlers. Store in localStorage.

**#5 Horizontal Sidebar Resize (80%):** Uses CSS variable `--sidebar-width: 280px`. Add draggable divider elements. More complex due to responsive reflow, but clear path.

---

## File Change Summary

### Files to DELETE/Archive
- `modules/stars.js` → `archive/stars.js`

### Files to MODIFY (Heavy)
- `styles.css` - colors, layout, resize styles
- `template.html` - structure changes
- `modules/sidebar.js` - resize logic

### Files to MODIFY (Light)
- `modules/main.js` - remove STARS wiring
- `modules/control-bar.js` - integrate with floating mapper
- `app.js` - remove star references

---

## Open Questions

1. Floating mapper: Should it have a collapse/expand state?
2. Section resizing: Should collapsed sections have a "header only" mode?
3. Color palette: Any specific reference for "boring" UI? (macOS? Windows? Material?)
4. Should sidebar widths be synced or fully independent?

---

## Architecture Coordination

### Concurrent Refactoring (Other Agent)
- Extracting UI functions (15) → `modules/ui-controls.js`
- MODULE_ORDER defined in `tools/visualize_graph_webgl.py`

### Module Assignment for UI Changes

| Change | Target Module | Notes |
|--------|---------------|-------|
| Star field removal | DELETE `stars.js` | Also remove from MODULE_ORDER |
| UI colors | `styles.css` + `theme.js` | No new module needed |
| Floating mapper | NEW `modules/visual-mapper.js` OR extend `control-bar.js` | TBD |
| Section resizing | `modules/sidebar.js` | Extend existing |
| Sidebar resizing | `modules/sidebar.js` + CSS | Extend existing |

### Functions Still in app.js (Relevant to UI)
- `buildChipGroup`, `buildMetadataControls`, `buildAppearanceSliders`
- These may move to `ui-controls.js` soon - coordinate!

---

## Next Steps

1. [ ] Review and approve this vision document
2. [ ] **Coordinate with refactoring agent** on ui-controls.js
3. [ ] Prioritize: Start with #1 (stars removal) - quick win
4. [ ] Then #2 (colors) - visual consistency
5. [ ] Then #3 (floating mapper) - UX improvement
6. [ ] Finally #4 & #5 (resizing) - polish features
