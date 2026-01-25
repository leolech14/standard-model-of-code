/**
 * MAIN.JS - MODULE INTEGRATION ENTRY POINT
 *
 * This file wires up all modules and provides backward compatibility
 * for HTML onclick handlers and global function calls.
 *
 * Module Loading Order (already handled by visualize_graph_webgl.py):
 * 1. performance.js       - Performance subsystem
 * 2. core.js              - Constants & utilities
 * 3. node-accessors.js    - Node property functions
 * 4. color-engine.js      - OKLCH color system
 * 5. refresh-throttle.js  - Throttled graph updates
 * 6. legend-manager.js    - Legend system
 * 7. data-manager.js      - Data access layer
 * 8. animation.js         - Layout & animation controller
 * 9. selection.js         - Selection system
 * 10. panels.js           - Panel management
 * 11. sidebar.js          - Sidebar controls
 * 12. edge-system.js      - Edge coloring & modes
 * 13. file-viz.js         - File visualization modes
 * 14. control-bar.js      - Visual mapping command bar
 * 15. main.js             - This file (wiring)
 * 16. app.js              - Legacy monolith (shrinking)
 */

;(function() {
    'use strict';

    // =========================================================================
    // VERIFY MODULE LOADING
    // =========================================================================

    const REQUIRED_MODULES = [
        { name: 'CORE', module: typeof CORE !== 'undefined' ? CORE : null },
        { name: 'NODE', module: typeof NODE !== 'undefined' ? NODE : null },
        { name: 'COLOR', module: typeof COLOR !== 'undefined' ? COLOR : null },
        { name: 'REFRESH', module: typeof REFRESH !== 'undefined' ? REFRESH : null },
        { name: 'LEGEND', module: typeof LEGEND !== 'undefined' ? LEGEND : null },
        { name: 'DATA', module: typeof DATA !== 'undefined' ? DATA : null },
        { name: 'LAYOUT', module: typeof LAYOUT !== 'undefined' ? LAYOUT : null },  // UI Layout Engine
        { name: 'ANIM', module: typeof ANIM !== 'undefined' ? ANIM : null },
        { name: 'SELECT', module: typeof SELECT !== 'undefined' ? SELECT : null },
        { name: 'PANELS', module: typeof PANELS !== 'undefined' ? PANELS : null },
        { name: 'SIDEBAR', module: typeof SIDEBAR !== 'undefined' ? SIDEBAR : null },
        { name: 'EDGE', module: typeof EDGE !== 'undefined' ? EDGE : null },
        { name: 'FILE_VIZ', module: typeof FILE_VIZ !== 'undefined' ? FILE_VIZ : null },
        { name: 'CONTROL_BAR', module: typeof CONTROL_BAR !== 'undefined' ? CONTROL_BAR : null },
        // STARS module removed - nodes ARE the stars
        { name: 'HUD', module: typeof HUD !== 'undefined' ? HUD : null },
        { name: 'DIMENSION', module: typeof DIMENSION !== 'undefined' ? DIMENSION : null },
        // Modular panel system
        { name: 'EVENT_BUS', module: typeof EVENT_BUS !== 'undefined' ? EVENT_BUS : null },
        { name: 'FILTER_STATE', module: typeof FILTER_STATE !== 'undefined' ? FILTER_STATE : null },
        { name: 'PANEL_SYSTEM', module: typeof PANEL_SYSTEM !== 'undefined' ? PANEL_SYSTEM : null },
        { name: 'PANEL_HANDLERS', module: typeof PANEL_HANDLERS !== 'undefined' ? PANEL_HANDLERS : null }
    ];

    const loaded = REQUIRED_MODULES.filter(m => m.module !== null);
    const missing = REQUIRED_MODULES.filter(m => m.module === null);

    console.log(`[MAIN] Modules loaded: ${loaded.length}/${REQUIRED_MODULES.length}`);
    if (missing.length > 0) {
        console.warn('[MAIN] Missing modules:', missing.map(m => m.name).join(', '));
    }

    // =========================================================================
    // WINDOW-LEVEL EXPORTS FOR HTML ONCLICK HANDLERS
    // =========================================================================

    // Selection functions
    if (typeof SELECT !== 'undefined') {
        window.clearSelection = SELECT.clear;
        window.setSelection = SELECT.set;
        window.toggleSelection = SELECT.toggle;
        window.getSelectedNodes = SELECT.getSelectedNodes;
    }

    // Animation functions
    if (typeof ANIM !== 'undefined') {
        window.applyLayoutPreset = ANIM.applyLayout;
        window.stopAnimation = ANIM.stop;
    }

    // Edge functions
    if (typeof EDGE !== 'undefined') {
        window.setEdgeMode = EDGE.setMode;
        window.cycleEdgeMode = EDGE.cycleMode;
        window.applyEdgeMode = EDGE.apply;
    }

    // File visualization functions
    if (typeof FILE_VIZ !== 'undefined') {
        window.setFileVizMode = FILE_VIZ.setMode;
        window.toggleFileMode = FILE_VIZ.toggle;
    }

    // Panel functions
    if (typeof PANELS !== 'undefined') {
        window.openPanel = PANELS.open;
        window.closePanel = PANELS.close;
        window.togglePanel = PANELS.toggle;
    }

    // Sidebar functions
    if (typeof SIDEBAR !== 'undefined') {
        window.setColorMode = SIDEBAR.setColorMode;
        window.setLayout = SIDEBAR.setLayout;
    }

    // Refresh function
    if (typeof REFRESH !== 'undefined') {
        window.throttledRefresh = REFRESH.throttled;
    }

    // Control bar functions
    if (typeof CONTROL_BAR !== 'undefined') {
        window.toggleControlBar = CONTROL_BAR.toggle;
        window.showControlBar = CONTROL_BAR.show;
        window.hideControlBar = CONTROL_BAR.hide;
        window.applyVisualMapping = CONTROL_BAR.applyMapping;
    }

    // =========================================================================
    // CROSS-MODULE INTEGRATION
    // =========================================================================

    /**
     * Initialize all modules with data
     * NOTE: Currently unused - app.js calls module inits directly in setupControls()
     * Kept for potential future centralization
     * @deprecated Use direct module init calls instead
     */
    window.initializeModules = function(data) {
        console.log('[MAIN] Initializing modules with data...');

        // Initialize DATA module
        if (typeof DATA !== 'undefined' && DATA.init) {
            DATA.init(data);
            console.log('[MAIN] DATA module initialized');
        }

        // Initialize LEGEND module
        if (typeof LEGEND !== 'undefined' && LEGEND.init) {
            LEGEND.init(data.nodes, data.links || data.edges);
            console.log('[MAIN] LEGEND module initialized');
        }

        // Initialize SIDEBAR
        if (typeof SIDEBAR !== 'undefined' && SIDEBAR.init) {
            SIDEBAR.init();
            console.log('[MAIN] SIDEBAR module initialized');
        }

        // Initialize PANELS command bar
        if (typeof PANELS !== 'undefined' && PANELS.initCommandBar) {
            PANELS.initCommandBar();
            console.log('[MAIN] PANELS module initialized');
        }

        // Initialize LAYOUT (replaces HudLayoutManager from app.js)
        if (typeof LAYOUT !== 'undefined' && LAYOUT.init) {
            LAYOUT.init();
            console.log('[MAIN] LAYOUT module initialized (Ctrl+Shift+L for debug overlay)');
        }

        // STARS module removed - nodes ARE the stars

        // Initialize HUD (fade behavior)
        if (typeof HUD !== 'undefined' && HUD.setupFade) {
            HUD.setupFade();
            console.log('[MAIN] HUD module initialized');
        }

        // Initialize DIMENSION toggle
        if (typeof DIMENSION !== 'undefined' && DIMENSION.setup) {
            DIMENSION.setup();
            console.log('[MAIN] DIMENSION module initialized');
        }

        // Initialize PANEL_SYSTEM (Gridstack-based modular panels)
        if (typeof PANEL_SYSTEM !== 'undefined' && PANEL_SYSTEM.init) {
            PANEL_SYSTEM.init();
            console.log('[MAIN] PANEL_SYSTEM module initialized');
        }

        // Load saved FILTER_STATE
        if (typeof FILTER_STATE !== 'undefined' && FILTER_STATE.load) {
            FILTER_STATE.load();
            console.log('[MAIN] FILTER_STATE loaded from localStorage');
        }

        console.log('[MAIN] Module initialization complete');
    };

    /**
     * Global refresh function that uses the throttled refresher
     */
    window.moduleRefresh = function() {
        if (typeof REFRESH !== 'undefined') {
            REFRESH.throttled();
        } else if (typeof Graph !== 'undefined' && Graph) {
            REFRESH.throttled();
        }
    };

    // =========================================================================
    // MODULE HEALTH CHECK
    // =========================================================================

    window.checkModuleHealth = function() {
        console.log('=== MODULE HEALTH CHECK ===');
        REQUIRED_MODULES.forEach(({ name, module }) => {
            const status = module ? 'OK' : 'MISSING';
            const color = module ? 'color: green' : 'color: red';
            console.log(`%c[${status}] ${name}`, color);
        });

        if (typeof REFRESH !== 'undefined') {
            console.log('REFRESH stats:', REFRESH.stats);
        }

        console.log('===========================');
    };

    // =========================================================================
    // INITIALIZATION MESSAGE
    // =========================================================================

    console.log('[MAIN] Entry point loaded. Modules ready for initialization.');

})();
