/**
 * COLLIDER VIZ - MAIN ENTRY POINT
 *
 * Imports all modules in dependency order (mirrors MODULE_ORDER from Python).
 * Vite bundles this into a single collider-viz.js IIFE.
 *
 * Import order matches the 18-phase loading sequence from visualize_graph_webgl.py.
 */

// === GLOBALS SETUP ===
import './globals.js';

// === PHASE 0: Vendor & Performance ===
import './modules/performance.js';

// === PHASE 1: Foundation (zero deps) ===
import './modules/utils.js';
import './modules/aquarela.js';
import './modules/event-bus.js';
import './modules/registry.js';
import './modules/perf-monitor.js';
import './modules/core.js';
import './modules/theory.js';

// === PHASE 2: Property Access ===
import './modules/node-accessors.js';
import './modules/node-helpers.js';
import './modules/color-helpers.js';

// === PHASE 3: Color System ===
import './modules/color-telemetry.js';
import './modules/color-engine.js';
import './modules/refresh-throttle.js';

// === PHASE 4: Data Layer ===
import './modules/legend-manager.js';
import './modules/data-manager.js';
import './modules/vis-state.js';
import './modules/ui-manager.js';

// === PHASE 5: Physics & Interaction ===
import './modules/physics.js';
import './modules/datamap.js';
import './modules/groups.js';
import './modules/hover.js';

// === PHASE 6: Visualization Modes ===
import './modules/flow.js';
import './modules/ui-builders.js';
import './modules/layout-helpers.js';
import './modules/spatial.js';

// === PHASE 7: Layout ===
import './modules/layout.js';

// === PHASE 8: HUD & Display ===
import './modules/hud.js';
import './modules/dimension.js';
import './modules/report.js';
import './modules/visibility.js';

// === PHASE 9: Animation & Selection ===
import './modules/animation.js';
import './modules/selection.js';

// === PHASE 10: Panels & Filtering ===
import './modules/panels.js';
import './modules/sidebar.js';
import './modules/filter-state.js';
import './modules/panel-system.js';
import './modules/panel-handlers.js';

// === PHASE 11: Edge & File Visualization ===
import './modules/edge-system.js';
import './modules/file-color-model.js';
import './modules/layout-forces.js';
import './modules/hull-visualizer.js';
import './modules/file-viz.js';

// === PHASE 12: UI Polish ===
import './modules/tooltips.js';
import './modules/theme.js';
import './modules/holarchy.js';
import './modules/encoding-view.js';

// === PHASE 13: UPB System ===
import './modules/upb/scales.js';
import './modules/upb/endpoints.js';
import './modules/upb/blenders.js';
import './modules/upb/bindings.js';
import './modules/upb/index.js';

// === PHASE 14: Property Query System ===
import './modules/vis-schema.js';
import './modules/upb-defaults.js';
import './modules/property-query.js';
import './modules/property-query-init.js';

// === PHASE 15: Commands ===
import './modules/control-bar.js';

// === PHASE 16: Entry Point ===
import './modules/main-module.js';

// === PHASE 17: Self-Tests ===
import './modules/circuit-breaker.js';
import './modules/color-contract-test.js';

// === PHASE 18: Inlined lib modules ===
import './lib/hardware-info.js';
import './lib/control-registry.js';
import './lib/settings-panel.js';

// === PHASE 19: Application ===
import './modules/app.js';

// === CSS ===
import './styles.css';
// cmd-btn.css removed -- hardcoded colors overrode token-based styles
