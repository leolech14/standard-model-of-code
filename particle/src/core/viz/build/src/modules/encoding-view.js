/**
 * ═══════════════════════════════════════════════════════════════════════════
 * ENCODING-VIEW MODULE - Auto-ranked top 5 OKLCH view switching
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * Python ranks all 30 views by informativeness for this dataset and sends
 * the top 5 (default + 4 data-driven) as `ranked_views` in the payload.
 * This module renders them as a flat row of dock buttons:
 *
 *   [Default] [Topo] [Risk] [Layers] [Cmplx]
 *   "Where are the highest risk areas?"
 *
 * Colors are pre-computed in Python as node.encoded_colors = { viewName: [L,C,H], ... }.
 * When a non-default view is active, getNodeColorByMode() in node-helpers.js
 * picks up the encoded color instead of computing from the JS color mode.
 *
 * @module ENCODING_VIEW
 * @version 3.0.0
 */

// Short display labels for view buttons
const VIEW_LABELS = {
    default: 'Default', architecture: 'Arch', health: 'Health', topology: 'Topo',
    files: 'Files', layers: 'Layers', boundaries: 'Bounds', scale: 'Scale',
    complexity: 'Cmplx', quality: 'Quality', convergence: 'Conv',
    influence: 'Inflnc', coupling: 'Couple', centrality: 'Central',
    file_size: 'Size', file_quality: 'FQual',
    behavior: 'Behav', intent: 'Intent', roles: 'Roles',
    purity: 'Purity', purity_by_layer: 'PLayer', isolation: 'Isolat',
    risk: 'Risk', debt: 'Debt', fragility: 'Fragile', god_class: 'God',
    confidence: 'Confid', clarity: 'Clarity',
    hotspots: 'Hotspot', signals: 'Signals',
};

// Current state
let _registry = {};
window.ENCODING_VIEW = 'default';

/**
 * Initialize the encoding view UI from payload data.
 */
function init() {
    const dock = document.getElementById('dock-encoding-view');
    if (!dock) return;

    // Load registry for signature lookups
    _registry = _loadRegistry();

    // Load ranked views from payload
    const ranked = _loadRankedViews();

    // Build UI
    _buildUI(dock, ranked);

    console.log(`[Module] ENCODING_VIEW loaded - ${ranked.length} ranked views`);
}

/**
 * Load view registry from COLLIDER_DATA payload, falling back to hardcoded.
 */
function _loadRegistry() {
    if (window.COLLIDER_DATA && window.COLLIDER_DATA.view_registry) {
        return window.COLLIDER_DATA.view_registry;
    }
    return {};
}

/**
 * Load ranked views from payload, with fallback for old payloads.
 * @returns {Array} [{ name, rank, score, domain }, ...]
 */
function _loadRankedViews() {
    if (window.COLLIDER_DATA && window.COLLIDER_DATA.ranked_views) {
        return window.COLLIDER_DATA.ranked_views;
    }
    // Fallback for old payloads
    return [
        { name: 'default', rank: 0 },
        { name: 'architecture', rank: 1 },
        { name: 'health', rank: 2 },
        { name: 'topology', rank: 3 },
        { name: 'files', rank: 4 },
    ];
}

/**
 * Build the dock UI: flat row of ranked view buttons + signature panel.
 */
function _buildUI(dock, ranked) {
    dock.innerHTML = '';

    // View button container
    const btnContainer = document.createElement('div');
    btnContainer.className = 'encoding-view-group';
    dock.appendChild(btnContainer);

    // Render buttons from ranked views
    for (const rv of ranked) {
        const btn = document.createElement('button');
        btn.className = 'dock-btn';
        if (rv.name === window.ENCODING_VIEW) btn.classList.add('active');
        btn.dataset.view = rv.name;
        btn.textContent = VIEW_LABELS[rv.name] || rv.name;

        // Tooltip: question + score
        const entry = _registry[rv.name];
        const question = entry ? (entry.question || entry.reading || rv.name) : rv.name;
        const scoreText = rv.score != null ? ` (score: ${rv.score})` : '';
        btn.title = question + scoreText;

        btn.addEventListener('click', () => {
            if (rv.name === window.ENCODING_VIEW) return;
            setView(rv.name);
        });
        btnContainer.appendChild(btn);
    }

    // Signature panel (below dock, injected as sibling)
    let sigPanel = document.getElementById('encoding-signature');
    if (!sigPanel) {
        sigPanel = document.createElement('div');
        sigPanel.id = 'encoding-signature';
        sigPanel.className = 'encoding-signature';
        // Insert after the bottom-dock
        const bottomDock = dock.closest('.bottom-dock');
        if (bottomDock && bottomDock.parentElement) {
            bottomDock.parentElement.insertBefore(sigPanel, bottomDock.nextSibling);
        }
    }

    _updateSignature();
}

/**
 * Update the semantic signature panel for the active view.
 */
function _updateSignature() {
    const sigPanel = document.getElementById('encoding-signature');
    if (!sigPanel) return;

    const entry = _registry[window.ENCODING_VIEW];
    if (!entry || (!entry.question && !entry.reading)) {
        sigPanel.style.display = 'none';
        return;
    }

    sigPanel.style.display = 'block';
    let html = '';
    if (entry.question) html += `<span class="sig-question">${entry.question}</span>`;
    if (entry.reading) html += `<span class="sig-reading">${entry.reading}</span>`;
    sigPanel.innerHTML = html;
}

/**
 * Set the active encoding view.
 * @param {string} view - View name from PRESET_VIEWS
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

    // Update signature
    _updateSignature();

    // Show toast
    const entry = _registry[view];
    if (typeof window.showToast === 'function') {
        const info = entry ? (entry.question || entry.reading || view) : view;
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

// For backward compat, expose VIEW_INFO as dynamic lookup
const VIEW_INFO = new Proxy({}, {
    get: (_, name) => {
        const entry = _registry[name];
        return entry ? (entry.reading || entry.question || name) : name;
    }
});

// Module export
const ENCODING_VIEW = { init, setView, getView, VIEW_INFO };
export { init, setView, getView, VIEW_INFO };
export { ENCODING_VIEW };
window.ENCODING_VIEW_MODULE = ENCODING_VIEW;

// Backward compat shims
window.setEncodingView = setView;
window.getEncodingView = getView;
