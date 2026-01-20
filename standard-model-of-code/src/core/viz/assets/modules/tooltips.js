/**
 * ═══════════════════════════════════════════════════════════════════════════
 * TOOLTIPS MODULE - Tooltip and Toast Notifications
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * Handles topology tooltips and toast notifications.
 * Depends on: TOOLTIP_STATE, HINTS_ENABLED, SMC_THEORY (globals)
 *
 * @module TOOLTIPS
 * @version 1.0.0
 * @confidence 99%
 */

window.TOOLTIPS = (function() {
    'use strict';

    // Module-local timeout reference
    let _toastTimeout = null;

    // ═══════════════════════════════════════════════════════════════════════
    // TOOLTIP OPERATIONS
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Initialize tooltip elements
     */
    function initTooltips() {
        const state = window.TOOLTIP_STATE;
        if (state) {
            state.element = document.getElementById('topo-tooltip');
        }
    }

    /**
     * Show topology tooltip with theory content
     * @param {string} category - Theory category (tiers, rings, families, etc.)
     * @param {string} key - Item key within category
     * @param {number} x - Screen X position
     * @param {number} y - Screen Y position
     */
    function showTopoTooltip(category, key, x, y) {
        const state = window.TOOLTIP_STATE;
        if (!state) return;

        if (!state.element) initTooltips();
        if (!state.element) return;

        const theory = window.SMC_THEORY;
        const content = theory?.[category]?.[key];
        if (!content) return;

        clearTimeout(state.hideTimeout);

        // Populate tooltip content
        const iconEl = document.getElementById('tooltip-icon');
        const titleEl = document.getElementById('tooltip-title');
        const subtitleEl = document.getElementById('tooltip-subtitle');
        const bodyEl = document.getElementById('tooltip-body');
        const theoryEl = document.getElementById('tooltip-theory');
        const examplesEl = document.getElementById('tooltip-examples');

        if (iconEl) iconEl.textContent = content.icon || '';
        if (titleEl) titleEl.textContent = content.title || key;
        if (subtitleEl) subtitleEl.textContent = content.subtitle || '';
        if (bodyEl) bodyEl.textContent = content.body || '';
        if (theoryEl) theoryEl.textContent = content.theory || '';
        if (examplesEl) {
            examplesEl.innerHTML = (content.examples || [])
                .map(ex => `<span class="topo-tooltip-example">${ex}</span>`)
                .join('');
        }

        // Position tooltip
        const tooltip = state.element;
        let left = x + 15, top = y + 15;
        if (left + 280 > window.innerWidth) left = x - 295;
        if (top + 200 > window.innerHeight) top = y - 215;
        if (left < 0) left = 15;
        if (top < 0) top = 15;

        tooltip.style.left = left + 'px';
        tooltip.style.top = top + 'px';
        tooltip.classList.add('visible');

        state.visible = true;
        state.currentKey = `${category}:${key}`;
    }

    /**
     * Hide topology tooltip
     * @param {boolean} immediate - Hide immediately without delay
     */
    function hideTopoTooltip(immediate = false) {
        const state = window.TOOLTIP_STATE;
        if (!state || !state.element) return;

        if (immediate) {
            state.element.classList.remove('visible');
            state.visible = false;
        } else {
            state.hideTimeout = setTimeout(() => {
                state.element.classList.remove('visible');
                state.visible = false;
            }, 150);
        }
    }

    // ═══════════════════════════════════════════════════════════════════════
    // TOAST OPERATIONS
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Show a toast notification
     * @param {string} message - Message to display
     */
    function showToast(message) {
        const toast = document.getElementById('hud-toast');
        if (!toast) return;

        toast.textContent = message;
        toast.classList.add('visible');

        clearTimeout(toast._timer);
        toast._timer = setTimeout(() => {
            toast.classList.remove('visible');
        }, 2200);
    }

    /**
     * Show mode change toast (respects hints setting)
     * @param {string} message - Message to display
     */
    function showModeToast(message) {
        if (!window.HINTS_ENABLED) return;

        let toast = document.getElementById('mode-toast');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'mode-toast';
            toast.className = 'mode-toast';
            document.body.appendChild(toast);
        }

        toast.textContent = message;
        toast.classList.add('visible');

        if (_toastTimeout) clearTimeout(_toastTimeout);
        _toastTimeout = setTimeout(() => {
            toast.classList.remove('visible');
        }, 1200);
    }

    // ═══════════════════════════════════════════════════════════════════════
    // MODULE EXPORT
    // ═══════════════════════════════════════════════════════════════════════

    return {
        init: initTooltips,
        showTopo: showTopoTooltip,
        hideTopo: hideTopoTooltip,
        toast: showToast,
        modeToast: showModeToast
    };
})();

// ═══════════════════════════════════════════════════════════════════════════
// BACKWARD COMPATIBILITY SHIMS
// ═══════════════════════════════════════════════════════════════════════════

window.initTooltips = TOOLTIPS.init;
window.showTopoTooltip = TOOLTIPS.showTopo;
window.hideTopoTooltip = TOOLTIPS.hideTopo;
window.showToast = TOOLTIPS.toast;
window.showModeToast = TOOLTIPS.modeToast;

console.log('[Module] TOOLTIPS loaded - 5 functions');
