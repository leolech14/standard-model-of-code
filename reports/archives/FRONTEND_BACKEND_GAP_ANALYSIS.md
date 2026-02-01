# Frontend/Backend Gap Analysis

> **Generated:** 2026-01-19
> **Status:** Active gaps documented

---

## Summary

| Category | Count | Severity |
|----------|-------|----------|
| Missing DOM Elements | 68 | HIGH |
| Unused Python Output | 10+ | LOW |
| Graceful Function Checks | ~8 | OK |

---

## HIGH PRIORITY: Missing DOM Elements

These elements are referenced in `app.js` but don't exist in `template.html`:

### Report & Insights Panels
| Element ID | Purpose | app.js Line |
|------------|---------|-------------|
| `report-panel` | Brain Download panel | 6090, 7368 |
| `report-content` | Report text area | 6355, 6358 |
| `btn-report` | Report toggle button | 6091 |
| `insights-panel` | AI Insights panel | 6363, 7379 |
| `insights-content` | Insights text area | 6364 |
| `btn-insights` | Insights toggle | 7376, 7379 |

### File Visualization Panel
| Element ID | Purpose | app.js Line |
|------------|---------|-------------|
| `file-panel` | File info popup | 6092, 8852 |
| `file-name` | File name display | 8843 |
| `file-cohesion` | Cohesion metric | 8844 |
| `file-purpose` | File purpose | 8845 |
| `file-code` | Code preview | 8853 |
| `btn-file-cluster` | File clustering | 9752 |
| `btn-file-hulls` | Convex hulls | 9747 |
| `btn-file-spheres` | Sphere grouping | 9762 |

### Command Bar (Bottom Dock)
| Element ID | Purpose | app.js Line |
|------------|---------|-------------|
| `command-bar` | Container | - |
| `cmd-files` | Files mode | 2117, 10125 |
| `cmd-flow2` | Flow mode | 2129 |
| `cmd-3d` | 3D toggle | 2145 |
| `btn-dimensions` | Dimension toggle | 2142, 4172 |

### Color/Appearance Controls
| Element ID | Purpose | app.js Line |
|------------|---------|-------------|
| `amplifier` | Color amplification | 6241 |
| `hue-shift` | Hue adjustment | 6211 |
| `chroma-scale` | Chroma adjustment | 6212 |
| `light-shift` | Lightness | 6213 |
| `background-brightness` | BG brightness | 6214 |
| `oklch-picker` | OKLCH color picker | 3413 |

### Filter & Datamap Controls
| Element ID | Purpose | app.js Line |
|------------|---------|-------------|
| `datamap-controls` | Datamap container | 3419, 4314 |
| `filter-datamaps` | Datamap chips | 4314 |
| `count-datamaps` | Datamap count | 4345 |
| `density-slider2` | Node density | 2041, 2044 |
| `density-value2` | Density display | 2041, 2042 |
| `filter-badge` | Active filter count | 4359 |
| `filter-summary` | Filter description | 4368 |

### Layout & Preset Controls
| Element ID | Purpose | app.js Line |
|------------|---------|-------------|
| `preset-grid` | Preset buttons | 6118, 6119 |
| `dock-presets` | Preset container | 6118 |
| `dock-schemes` | Color schemes | 6129, 6169 |
| `layout-grid` | Layout buttons | 6275 |

### Sidebar Elements
| Element ID | Purpose | app.js Line |
|------------|---------|-------------|
| `side-dock` | Main sidebar | 2343, 2364 |
| `side-content` | Sidebar content | 2343, 4141 |
| `sidebar-close` | Close button | 4125 |
| `btn-filters` | Filter toggle | 4124 |

### Tooltip System
| Element ID | Purpose | app.js Line |
|------------|---------|-------------|
| `topo-tooltip` | Topology tooltip | 4655 |
| `tooltip-title` | Tooltip title | 4665 |
| `tooltip-subtitle` | Subtitle | 4666 |
| `tooltip-body` | Main content | 4667 |
| `tooltip-theory` | Theory link | 4668 |
| `tooltip-examples` | Examples | 4669 |
| `tooltip-icon` | Icon display | 4664 |

### Status & Metrics
| Element ID | Purpose | app.js Line |
|------------|---------|-------------|
| `status-nodes` | Node count | 4378 |
| `status-edges` | Edge count | 4379 |
| `metric-edge-resolution` | KPI | 3513 |
| `metric-call-ratio` | KPI | 3514 |
| `metric-reachability` | KPI | 3515 |
| `metric-dead-code` | KPI | 3516 |
| `metric-topology` | KPI | 3517 |

### Group Management
| Element ID | Purpose | app.js Line |
|------------|---------|-------------|
| `btn-create-group` | Create group | 8018 |
| `group-list` | Group list | 7959 |

### Selection Modal
| Element ID | Purpose | app.js Line |
|------------|---------|-------------|
| `selection-modal-overlay` | Modal backdrop | 8207, 8319 |
| `selection-modal-title` | Modal title | 8208 |
| `selection-modal-stats` | Stats display | 8209 |
| `selection-modal-body` | Modal body | 8210 |
| `selection-modal-tbody` | Table body | 8286 |
| `selection-modal-close` | Close button | 8325 |

### Miscellaneous
| Element ID | Purpose | app.js Line |
|------------|---------|-------------|
| `btn-reset-layout` | Reset layout | 7425, 4157 |
| `btn-hints` | Hints toggle | 7430 |
| `btn-edge-mode` | Edge mode cycler | 7353 |
| `toggle-oval-debug` | Debug toggle | 1999, 2001 |
| `oval-margin-slider` | Oval margin | 1977 |
| `hud-toast` | HUD notifications | 6612 |
| `mode-toast` | Mode toast | 3886 |
| `flow-legend` | Flow legend | 7581, 7606 |

---

## MEDIUM PRIORITY: Unused Python Output

These fields are computed by the Python backend but not displayed in the frontend:

| Field | Source | Why Unused |
|-------|--------|------------|
| `unified_classification` | full_analysis.py:727 | No UI panel |
| `unified_dependencies` | full_analysis.py:730 | No dependency graph |
| `unified_auto_discovery` | full_analysis.py:728 | No discovery panel |
| `theory_completeness` | full_analysis.py:735 | Not rendered anywhere |
| `warnings` | full_analysis.py:733 | No warnings panel |
| `recommendations` | full_analysis.py:734 | No recommendations |
| `semantic/domain_inference` | full_analysis.py:365 | Unused semantic data |
| `distributions` (full) | visualize_graph_webgl.py:351 | Only types used |
| `ecosystem_discovery` | full_analysis.py:729 | No ecosystem panel |
| `llm_enrichment` | full_analysis.py:732 | Inconsistent access |

---

## LOW PRIORITY: Graceful Function Checks

These functions use `typeof X === 'function'` guards, so they degrade gracefully:

- `setNodeColorMode()` - Defined
- `toggleFlowMode()` - Defined
- `disableFlowMode()` - Defined
- `renderAllLegends()` - Defined
- `applyLayoutPreset()` - Conditional
- `applyEdgeMode()` - Conditional
- `refreshGraph()` - Defined
- `window.refreshGradientEdgeColors()` - Conditional

---

## Recommended Actions

### Phase 1: Essential UI Restoration
1. Add `report-panel` with `report-content` for Brain Download
2. Add `insights-panel` with `insights-content` for AI Insights
3. Add basic `file-panel` for file hover info

### Phase 2: Enhanced Controls
4. Add `datamap-controls` for datamap filtering
5. Add `density-slider2` for node density
6. Add color adjustment sliders (amplifier, hue, chroma)

### Phase 3: Advanced Features
7. Add tooltip system for topology explanations
8. Add command bar with mode buttons
9. Add selection modal for bulk operations

### Phase 4: Cleanup
10. Remove unused Python output computations OR
11. Add UI panels to display computed data

---

## Files Reference

| File | Role |
|------|------|
| `src/core/full_analysis.py` | Python analysis pipeline |
| `tools/visualize_graph_webgl.py` | HTML/JS generator |
| `src/core/viz/assets/app.js` | Frontend JavaScript |
| `src/core/viz/assets/template.html` | HTML template |
| `src/core/viz/assets/styles.css` | CSS styles |

---

*Generated by Collider Gap Analysis*
