/**
 * ═══════════════════════════════════════════════════════════════════════════
 * ENCODING-VIEW MODULE - Dynamic domain-grouped OKLCH view switching
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * Reads view_registry from the payload and builds a domain-grouped UI:
 *   [Domain: Architecture ▾] [Default] [Arch] [Layers] [Boundaries] [Scale]
 *   "Which architectural layers have the most coherent code?"
 *
 * Colors are pre-computed in Python as node.encoded_colors = { viewName: [L,C,H], ... }.
 * When a non-default view is active, getNodeColorByMode() in node-helpers.js
 * picks up the encoded color instead of computing from the JS color mode.
 *
 * @module ENCODING_VIEW
 * @version 2.0.0
 */

// Fallback VIEW_INFO for when view_registry is not in payload (backward compat)
const FALLBACK_VIEW_INFO = {
    default: { name: 'default', domain: 'general', question: '', reading: 'Standard coloring (uses Color Mode selector)' },
    architecture: { name: 'architecture', domain: 'general', question: '', reading: 'H=tier, L=coherence score, C=purity score' },
    health: { name: 'health', domain: 'general', question: '', reading: 'H=tier, L=complexity (inverted), C=coherence' },
    topology: { name: 'topology', domain: 'general', question: '', reading: 'H=topology role, L=pagerank, C=betweenness' },
    files: { name: 'files', domain: 'general', question: '', reading: 'H=file (golden angle), L=coherence, C=purity' },
};

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

// Domain display labels
const DOMAIN_LABELS = {
    general: 'General', architecture: 'Architecture', health: 'Health',
    topology: 'Topology', files: 'Files', behavior: 'Behavior',
    purity: 'Purity', risk: 'Risk', confidence: 'Confidence',
    convergence: 'Convergence',
};

// Current state
let _registry = {};
let _activeDomain = 'general';
window.ENCODING_VIEW = 'default';

/**
 * Initialize the encoding view UI from payload data.
 */
function init() {
    const dock = document.getElementById('dock-encoding-view');
    if (!dock) return;

    // Load registry from payload
    _registry = _loadRegistry();

    // Group views by domain
    const domains = _groupByDomain(_registry);

    // Build UI
    _buildUI(dock, domains);

    const viewCount = Object.keys(_registry).length;
    console.log(`[Module] ENCODING_VIEW loaded - ${viewCount} views across ${Object.keys(domains).length} domains`);
}

/**
 * Load view registry from COLLIDER_DATA payload, falling back to hardcoded.
 */
function _loadRegistry() {
    if (window.COLLIDER_DATA && window.COLLIDER_DATA.view_registry) {
        return window.COLLIDER_DATA.view_registry;
    }
    return FALLBACK_VIEW_INFO;
}

/**
 * Group registry entries by domain.
 * @returns {Object} { domainName: [viewEntry, ...], ... }
 */
function _groupByDomain(registry) {
    const groups = {};
    for (const [name, entry] of Object.entries(registry)) {
        const domain = entry.domain || 'general';
        if (!groups[domain]) groups[domain] = [];
        groups[domain].push(entry);
    }
    // Ensure 'general' is first
    const ordered = {};
    if (groups.general) { ordered.general = groups.general; }
    for (const [d, views] of Object.entries(groups)) {
        if (d !== 'general') ordered[d] = views;
    }
    return ordered;
}

/**
 * Build the dynamic dock UI: domain selector + view buttons + signature panel.
 */
function _buildUI(dock, domains) {
    dock.innerHTML = '';

    // Domain dropdown
    const select = document.createElement('select');
    select.className = 'encoding-domain-select';
    select.title = 'Filter views by analytical domain';
    for (const domain of Object.keys(domains)) {
        const opt = document.createElement('option');
        opt.value = domain;
        opt.textContent = DOMAIN_LABELS[domain] || domain;
        select.appendChild(opt);
    }
    select.value = _activeDomain;
    select.addEventListener('change', () => {
        _activeDomain = select.value;
        _renderViewButtons(btnContainer, domains[_activeDomain] || []);
        _updateSignature();
    });
    dock.appendChild(select);

    // View button container
    const btnContainer = document.createElement('div');
    btnContainer.className = 'encoding-view-group';
    dock.appendChild(btnContainer);

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

    // Render initial domain
    _renderViewButtons(btnContainer, domains[_activeDomain] || []);
    _updateSignature();
}

/**
 * Render view buttons for the currently selected domain.
 */
function _renderViewButtons(container, views) {
    container.innerHTML = '';
    for (const view of views) {
        const btn = document.createElement('button');
        btn.className = 'dock-btn';
        if (view.name === window.ENCODING_VIEW) btn.classList.add('active');
        btn.dataset.view = view.name;
        btn.textContent = VIEW_LABELS[view.name] || view.name;
        btn.title = view.question || view.reading || view.name;
        btn.addEventListener('click', () => {
            if (view.name === window.ENCODING_VIEW) return;
            setView(view.name);
        });
        container.appendChild(btn);
    }
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

    // Switch domain if the view belongs to a different one
    const entry = _registry[view];
    if (entry && entry.domain && entry.domain !== _activeDomain) {
        _activeDomain = entry.domain;
        const select = document.querySelector('.encoding-domain-select');
        if (select) select.value = _activeDomain;
        const dock = document.getElementById('dock-encoding-view');
        if (dock) {
            const btnContainer = dock.querySelector('.encoding-view-group');
            if (btnContainer) {
                const domains = _groupByDomain(_registry);
                _renderViewButtons(btnContainer, domains[_activeDomain] || []);
            }
        }
    }

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
