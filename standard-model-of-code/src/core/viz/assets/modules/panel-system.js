/**
 * PANEL SYSTEM MODULE
 *
 * Gridstack-based draggable/resizable panel management.
 * Provides layout persistence, default layouts, and panel state management.
 *
 * @module PANEL_SYSTEM
 *
 * Usage:
 *   PANEL_SYSTEM.init()           // Initialize Gridstack
 *   PANEL_SYSTEM.saveLayout()     // Persist current layout
 *   PANEL_SYSTEM.resetLayout()    // Restore default
 *   PANEL_SYSTEM.togglePanel(id)  // Show/hide panel
 *   PANEL_SYSTEM.getGrid()        // Access Gridstack instance
 *
 * Requires: Gridstack.js CDN loaded in HTML
 */

window.PANEL_SYSTEM = (function() {
    'use strict';

    let _grid = null;
    let _initialized = false;
    const STORAGE_KEY = 'collider_panel_layout_v1';

    // Default layout: semantic proximity grouping
    // Grid is 12 columns, positioned for control panel at bottom
    // Must match gs-id attributes in template.html panel-container
    const DEFAULT_LAYOUT = [
        // Row 0: Core controls
        { id: 'filtering',      x: 0,  y: 0, w: 3, h: 2 },
        { id: 'selection',      x: 3,  y: 0, w: 2, h: 2 },
        { id: 'camera',         x: 5,  y: 0, w: 2, h: 2 },
        { id: 'accessibility',  x: 7,  y: 0, w: 2, h: 2 },
        { id: 'export',         x: 9,  y: 0, w: 3, h: 2 },
        // Row 2: Layout and analysis
        { id: 'analysis',       x: 0,  y: 2, w: 4, h: 2 },
        { id: 'layout-phys',    x: 4,  y: 2, w: 3, h: 2 },
        { id: 'view-modes',     x: 7,  y: 2, w: 2, h: 2 },
        { id: 'panel-settings', x: 9,  y: 2, w: 3, h: 2 },
        // Row 4: Appearance controls
        { id: 'node-appear',    x: 0,  y: 4, w: 3, h: 2 },
        { id: 'edge-appear',    x: 3,  y: 4, w: 3, h: 2 }
    ];

    /**
     * Initialize Gridstack on the panel container
     */
    function init() {
        if (_initialized) return;

        const container = document.querySelector('.panel-container');
        if (!container) {
            console.warn('[PANEL_SYSTEM] No .panel-container found, using legacy sidebar');
            return;
        }

        // Check if Gridstack is loaded
        if (typeof GridStack === 'undefined') {
            console.error('[PANEL_SYSTEM] GridStack not loaded - check CDN');
            return;
        }

        _grid = GridStack.init({
            column: 12,
            cellHeight: 70,
            margin: 4,
            float: true,
            resizable: { handles: 'e,se,s,sw,w' },
            animate: true,
            minRow: 1
        }, container);

        // Load saved or default layout
        const saved = _loadLayout();
        if (saved && saved.length > 0) {
            _applyLayout(saved);
        }

        // Save on any change
        _grid.on('change', () => saveLayout());

        // Bind collapse buttons
        _bindCollapseButtons();

        _initialized = true;
        console.log('[PANEL_SYSTEM] Initialized with Gridstack');

        // Emit ready event
        if (typeof EVENT_BUS !== 'undefined') {
            EVENT_BUS.emit('panel:ready', { panelCount: _grid.getGridItems().length });
        }
    }

    /**
     * Save current layout to localStorage
     */
    function saveLayout() {
        if (!_grid) return;
        try {
            const items = _grid.save(false); // Don't include content
            localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
        } catch (e) {
            console.warn('[PANEL_SYSTEM] Could not save layout:', e);
        }
    }

    /**
     * Load layout from localStorage
     */
    function _loadLayout() {
        try {
            const saved = localStorage.getItem(STORAGE_KEY);
            return saved ? JSON.parse(saved) : null;
        } catch (e) {
            console.warn('[PANEL_SYSTEM] Could not load layout:', e);
            return null;
        }
    }

    /**
     * Apply a layout configuration
     */
    function _applyLayout(layout) {
        if (!_grid) return;
        layout.forEach(item => {
            const el = document.querySelector(`[gs-id="${item.id}"]`);
            if (el) {
                _grid.update(el, { x: item.x, y: item.y, w: item.w, h: item.h });
            }
        });
    }

    /**
     * Reset to default layout
     */
    function resetLayout() {
        localStorage.removeItem(STORAGE_KEY);
        _applyLayout(DEFAULT_LAYOUT);
        saveLayout();
        console.log('[PANEL_SYSTEM] Layout reset to default');
    }

    /**
     * Toggle panel visibility
     */
    function togglePanel(panelId) {
        const el = document.querySelector(`[gs-id="${panelId}"]`);
        if (el) {
            el.classList.toggle('gs-hidden');
            saveLayout();

            if (typeof EVENT_BUS !== 'undefined') {
                EVENT_BUS.emit('panel:toggled', {
                    id: panelId,
                    visible: !el.classList.contains('gs-hidden')
                });
            }
        }
    }

    /**
     * Bind collapse buttons on panel headers
     */
    function _bindCollapseButtons() {
        document.querySelectorAll('.panel-collapse').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const panel = btn.closest('.grid-stack-item');
                const body = panel?.querySelector('.panel-body');
                if (body) {
                    const isCollapsed = body.classList.toggle('collapsed');
                    btn.textContent = isCollapsed ? '+' : '−';

                    // Update grid height
                    if (_grid && panel) {
                        const newH = isCollapsed ? 1 : 2;
                        _grid.update(panel, { h: newH });
                    }
                }
            });
        });
    }

    /**
     * Get all panel IDs
     */
    function getPanelIds() {
        if (!_grid) return [];
        return _grid.getGridItems().map(el => el.getAttribute('gs-id')).filter(Boolean);
    }

    /**
     * Get Gridstack instance for advanced operations
     */
    function getGrid() {
        return _grid;
    }

    /**
     * Check if panel system is active
     */
    function isActive() {
        return _initialized && _grid !== null;
    }

    return {
        init,
        saveLayout,
        resetLayout,
        togglePanel,
        getPanelIds,
        getGrid,
        isActive,
        DEFAULT_LAYOUT
    };

})();

console.log('[Module] PANEL_SYSTEM loaded');
