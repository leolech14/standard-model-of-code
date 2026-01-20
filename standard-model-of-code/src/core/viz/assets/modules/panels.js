/**
 * PANELS MODULE
 *
 * Manages floating panels and HUD layout for the visualization.
 * Handles panel open/close, command bar, and UI dimming.
 *
 * Usage:
 *   PANELS.open('view')       // Open a panel
 *   PANELS.close('view')      // Close a panel
 *   PANELS.toggle('view')     // Toggle panel visibility
 *   PANELS.initCommandBar()   // Wire up command bar buttons
 */

const PANELS = (function() {
    'use strict';

    // =========================================================================
    // STATE
    // =========================================================================

    let _activePanelId = null;

    // =========================================================================
    // PANEL FUNCTIONS
    // =========================================================================

    /**
     * Open a panel by ID
     */
    function open(panelId) {
        const panel = document.getElementById('panel-' + panelId);
        const btn = document.getElementById('cmd-' + panelId);

        // Close any already-open panel
        if (_activePanelId && _activePanelId !== panelId) {
            close(_activePanelId);
        }

        if (panel) {
            panel.classList.add('visible');
            setTimeout(() => { panel.style.opacity = '1'; }, 10);
        }
        if (btn) btn.classList.add('active');
        _activePanelId = panelId;

        // Dim the universe when panel opens
        document.body.classList.add('ui-active');

        // Dim starfield via JS
        if (typeof STARFIELD !== 'undefined' && STARFIELD?.material) {
            const baseOpacity = typeof STARFIELD_OPACITY !== 'undefined' ? STARFIELD_OPACITY : 0.5;
            STARFIELD.material.opacity = baseOpacity * 0.3;
        }
    }

    /**
     * Close a panel by ID
     */
    function close(panelId) {
        const panel = document.getElementById('panel-' + panelId);
        const btn = document.getElementById('cmd-' + panelId);

        if (panel) {
            panel.classList.remove('visible');
        }
        if (btn) btn.classList.remove('active');
        if (_activePanelId === panelId) _activePanelId = null;

        // Restore universe when all panels closed
        if (!_activePanelId) {
            document.body.classList.remove('ui-active');

            // Restore starfield
            if (typeof STARFIELD !== 'undefined' && STARFIELD?.material) {
                const starsBtn = document.getElementById('btn-stars');
                const starsVisible = starsBtn && starsBtn.classList.contains('active');
                const baseOpacity = typeof STARFIELD_OPACITY !== 'undefined' ? STARFIELD_OPACITY : 0.5;
                STARFIELD.material.opacity = starsVisible ? baseOpacity : 0;
            }
        }
    }

    /**
     * Toggle a panel
     */
    function toggle(panelId) {
        const panel = document.getElementById('panel-' + panelId);
        if (panel && panel.classList.contains('visible')) {
            close(panelId);
        } else {
            open(panelId);
        }
    }

    /**
     * Get active panel ID
     */
    function getActive() {
        return _activePanelId;
    }

    // =========================================================================
    // COMMAND BAR INITIALIZATION
    // =========================================================================

    function initCommandBar() {
        const cmdBtns = {
            'cmd-view': 'view',
            'cmd-filter': 'filter',
            'cmd-style': 'style',
            'cmd-settings': 'settings'
        };

        Object.entries(cmdBtns).forEach(([btnId, panelId]) => {
            const btn = document.getElementById(btnId);
            if (btn) {
                btn.addEventListener('click', () => toggle(panelId));
            }
        });

        // Settings panel: Oval margin slider
        _initOvalMarginSlider();
        _initOvalDebugToggle();
    }

    function _initOvalMarginSlider() {
        const ovalSlider = document.getElementById('oval-margin-slider');
        const ovalValue = document.getElementById('oval-margin-value');
        let ovalDebounceTimer = null;

        if (ovalSlider) {
            ovalSlider.addEventListener('input', (e) => {
                if (ovalValue) ovalValue.textContent = e.target.value + '%';
            });

            const applyOvalMargin = () => {
                clearTimeout(ovalDebounceTimer);
                ovalDebounceTimer = setTimeout(() => {
                    const val = ovalSlider.value;
                    document.documentElement.style.setProperty('--oval-margin', val + '%');
                }, 300);
            };

            ovalSlider.addEventListener('mouseup', applyOvalMargin);
            ovalSlider.addEventListener('touchend', applyOvalMargin);
            ovalSlider.addEventListener('change', applyOvalMargin);
        }
    }

    function _initOvalDebugToggle() {
        const toggleOvalDebug = document.getElementById('toggle-oval-debug');
        if (toggleOvalDebug) {
            toggleOvalDebug.addEventListener('click', () => {
                toggleOvalDebug.classList.toggle('active');
                const ovalDebug = document.querySelector('.oval-debug');
                if (ovalDebug) {
                    ovalDebug.style.display = toggleOvalDebug.classList.contains('active') ? 'block' : 'none';
                }
            });
        }
    }

    // =========================================================================
    // HUD LAYOUT MANAGER
    // =========================================================================

    const HudLayoutManager = {
        _resizeObserver: null,
        _reflowDebouncer: null,
        _previousLayout: null,

        init() {
            this._resizeObserver = new ResizeObserver(() => {
                this._scheduleReflow();
            });

            // Observe panels that affect layout
            ['selection-panel', 'legend-panel', 'kpi-panel'].forEach(id => {
                const el = document.getElementById(id);
                if (el) this._resizeObserver.observe(el);
            });

            // Initial layout
            this.reflow();
        },

        _scheduleReflow() {
            if (this._reflowDebouncer) return;
            this._reflowDebouncer = requestAnimationFrame(() => {
                this._reflowDebouncer = null;
                this.reflow();
            });
        },

        reflow() {
            // Calculate optimal positions for HUD elements
            const vh = window.innerHeight;
            const selectionPanel = document.getElementById('selection-panel');
            const legendPanel = document.getElementById('legend-panel');

            if (selectionPanel && legendPanel) {
                const selectionRect = selectionPanel.getBoundingClientRect();
                const selectionBottom = selectionRect.bottom;

                // Position legend below selection if they overlap
                if (selectionPanel.classList.contains('visible')) {
                    legendPanel.style.top = (selectionBottom + 10) + 'px';
                } else {
                    legendPanel.style.top = '';
                }
            }
        },

        destroy() {
            if (this._resizeObserver) {
                this._resizeObserver.disconnect();
            }
        }
    };

    // =========================================================================
    // PUBLIC API
    // =========================================================================

    return {
        open,
        close,
        toggle,
        getActive,
        initCommandBar,
        HudLayoutManager,

        // State access
        get activePanelId() { return _activePanelId; }
    };
})();

// Backward compatibility - _activePanelId is managed by app.js
function openPanel(panelId) { PANELS.open(panelId); }
function closePanel(panelId) { PANELS.close(panelId); }
function togglePanel(panelId) { PANELS.toggle(panelId); }
function initCommandBar() { PANELS.initCommandBar(); }
// HudLayoutManager - app.js owns this, not duplicated here
