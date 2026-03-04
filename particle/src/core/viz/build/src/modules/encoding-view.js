/**
 * ═══════════════════════════════════════════════════════════════════════════
 * ENCODING-VIEW MODULE - Auto-ranked top 5 OKLCH view switching
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * Reads view_registry from the payload. Each entry has rank/score fields
 * set by Python's rank_views(). Entries with rank != null are shown as
 * dock buttons (default at rank 0, top 4 data-driven at ranks 1-4):
 *
 *   [Default] [Topo] [Risk] [Layers] [Cmplx]
 *   "Where are the highest risk areas?"
 *
 * Single data source: view_registry carries both metadata (question, reading,
 * domain) and ranking (rank, score). No separate ranked_views field needed.
 *
 * @module ENCODING_VIEW
 * @version 3.1.0
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

    // Load registry — single source for metadata + ranking
    _registry = _loadRegistry();

    // Extract ranked views from registry
    const ranked = _getRankedViews(_registry);

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
    // Fallback for old payloads without view_registry
    return {
        default: { name: 'default', domain: 'general', question: '', reading: 'Standard coloring (uses Color Mode selector)', rank: 0, score: null },
        architecture: { name: 'architecture', domain: 'general', question: '', reading: 'H=tier, L=coherence score, C=purity score', rank: 1, score: null },
        health: { name: 'health', domain: 'general', question: '', reading: 'H=tier, L=complexity (inverted), C=coherence', rank: 2, score: null },
        topology: { name: 'topology', domain: 'general', question: '', reading: 'H=topology role, L=pagerank, C=betweenness', rank: 3, score: null },
        files: { name: 'files', domain: 'general', question: '', reading: 'H=file (golden angle), L=coherence, C=purity', rank: 4, score: null },
    };
}

/**
 * Extract ranked views from registry, sorted by rank.
 * @returns {Array} entries with rank != null, sorted ascending
 */
function _getRankedViews(registry) {
    return Object.values(registry)
        .filter(e => e.rank != null)
        .sort((a, b) => a.rank - b.rank);
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
    for (const entry of ranked) {
        const btn = document.createElement('button');
        btn.className = 'dock-btn';
        if (entry.name === window.ENCODING_VIEW) btn.classList.add('active');
        btn.dataset.view = entry.name;
        btn.textContent = VIEW_LABELS[entry.name] || entry.name;

        // Tooltip: question + score (all from same entry)
        const question = entry.question || entry.reading || entry.name;
        const scoreText = entry.score != null ? ` (score: ${entry.score})` : '';
        btn.title = question + scoreText;

        btn.addEventListener('click', () => {
            if (entry.name === window.ENCODING_VIEW) return;
            setView(entry.name);
        });
        btnContainer.appendChild(btn);
    }

    // Signature panel (below dock, injected as sibling)
    let sigPanel = document.getElementById('encoding-signature');
    if (!sigPanel) {
        sigPanel = document.createElement('div');
        sigPanel.id = 'encoding-signature';
        sigPanel.className = 'encoding-signature';
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
