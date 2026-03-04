/**
 * ═══════════════════════════════════════════════════════════════════════════
 * ENCODING-VIEW MODULE - Scientific OKLCH 3-channel view switching
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * Manages the encoding view selector in the bottom dock. Each view maps
 * data metrics to OKLCH channels (Hue=category, Lightness=metric A,
 * Chroma=metric B). Colors are pre-computed in Python and stored as
 * node.encoded_colors = { architecture: '#hex', health: '#hex', ... }.
 *
 * When a non-default view is active, getNodeColorByMode() in node-helpers.js
 * picks up the encoded color instead of computing from the JS color mode.
 *
 * @module ENCODING_VIEW
 * @version 1.0.0
 */

// View descriptions for toast notifications
const VIEW_INFO = {
    default: 'Standard coloring (uses Color Mode selector)',
    architecture: 'H=tier, L=coherence score, C=purity score',
    health: 'H=tier, L=complexity (inverted), C=coherence',
    topology: 'H=topology role, L=pagerank, C=betweenness',
    files: 'H=file (golden angle), L=coherence, C=purity'
};

// Current active view
window.ENCODING_VIEW = 'default';

/**
 * Initialize encoding view dock buttons
 */
function init() {
    const dock = document.getElementById('dock-encoding-view');
    if (!dock) return;

    const buttons = dock.querySelectorAll('.dock-btn[data-view]');
    buttons.forEach(btn => {
        btn.addEventListener('click', () => {
            const view = btn.dataset.view;
            if (!view || view === window.ENCODING_VIEW) return;
            setView(view);
        });
    });

    console.log('[Module] ENCODING_VIEW loaded - 5 views available');
}

/**
 * Set the active encoding view
 * @param {string} view - View name: 'default', 'architecture', 'health', 'topology', 'files'
 */
function setView(view) {
    window.ENCODING_VIEW = view;

    // Update button active states
    const dock = document.getElementById('dock-encoding-view');
    if (dock) {
        dock.querySelectorAll('.dock-btn').forEach(b => b.classList.remove('active'));
        const activeBtn = dock.querySelector(`[data-view="${view}"]`);
        if (activeBtn) activeBtn.classList.add('active');
    }

    // Show toast with view description
    if (typeof window.showToast === 'function') {
        const info = VIEW_INFO[view] || view;
        window.showToast(`View: ${view} — ${info}`, 3000);
    }

    // Refresh graph to apply new colors
    if (typeof window.refreshGraph === 'function') {
        window.refreshGraph();
    }

    // Also update gradient edges if available
    if (typeof window.refreshGradientEdgeColors === 'function') {
        window.refreshGradientEdgeColors();
    }
}

/**
 * Get current active view
 * @returns {string}
 */
function getView() {
    return window.ENCODING_VIEW || 'default';
}

// Module export
const ENCODING_VIEW = { init, setView, getView, VIEW_INFO };
export { init, setView, getView, VIEW_INFO };
export { ENCODING_VIEW };
window.ENCODING_VIEW_MODULE = ENCODING_VIEW;

// Backward compat shims
window.setEncodingView = setView;
window.getEncodingView = getView;
