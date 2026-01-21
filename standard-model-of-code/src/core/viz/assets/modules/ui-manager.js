/**
 * @module ui-manager
 * @description Orchestrates the "One Dock" unified interface
 * @responsibility Manage sidebar, dock, modes, and filters UI
 * @depends_on vis-state, data-manager, refresh-throttle
 */

const UI_MANAGER = (function() {
    'use strict';

    // Private state
    let _data = null;
    let _initialized = false;

    /**
     * Initialize the UI Manager
     * @param {Object} data - Graph data object
     */
    function init(data) {
        _data = data;
        _setupSidebar();
        _setupDock();
        _setupModes();
        _populateFilters();
        _updateStatus();
        _initialized = true;
    }

    /**
     * Setup sidebar toggle and accordion behavior
     */
    function _setupSidebar() {
        const sidebar = document.getElementById('sidebar');
        const btnFilters = document.getElementById('btn-filters');
        const btnClose = document.getElementById('sidebar-close');

        const toggle = () => {
            sidebar.classList.toggle('open');
            _updateFilterBadge();
        };

        if (btnFilters) btnFilters.onclick = (e) => {
            e.stopPropagation();
            toggle();
        };
        if (btnClose) btnClose.onclick = () => sidebar.classList.remove('open');

        // Accordion Logic
        document.querySelectorAll('.accordion-header').forEach(header => {
            header.onclick = () => {
                const accordion = header.parentElement;
                accordion.classList.toggle('open');
            };
        });
    }

    /**
     * Setup dock controls
     */
    function _setupDock() {
        // Reset Layout
        const btnReset = document.getElementById('btn-reset-layout');
        if (btnReset) btnReset.onclick = () => {
            if (typeof Graph !== 'undefined' && Graph) {
                Graph.zoomToFit(1000);
            }
        };

        // Dimensions Toggle (2D/3D - stub)
        const btnDim = document.getElementById('btn-dimensions');
        if (btnDim) btnDim.onclick = () => {
            console.log("Dimension toggle requested");
        };

        // Report Button
        const btnReport = document.getElementById('btn-report');
        if (btnReport) btnReport.onclick = () => {
            const reportPanel = document.getElementById('report-panel');
            if (reportPanel) {
                const isHidden = reportPanel.style.display === 'none';
                reportPanel.style.display = isHidden ? 'block' : 'none';
                btnReport.classList.toggle('active', isHidden);
            }
        };
    }

    /**
     * Setup mode buttons (explore, files, flow)
     */
    function _setupModes() {
        const modes = ['explore', 'files', 'flow'];

        const setMode = (mode) => {
            document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
            const activeBtn = document.getElementById(`mode-${mode}`);
            if (activeBtn) activeBtn.classList.add('active');

            document.querySelectorAll('.mode-control-group').forEach(g => g.style.display = 'none');
            const group = document.getElementById(`${mode}-controls`);
            if (group) group.style.display = 'flex';
        };

        modes.forEach(mode => {
            const btn = document.getElementById(`mode-${mode}`);
            if (btn) btn.onclick = () => setMode(mode);
        });

        // Files Sub-controls wiring
        const bindToggle = (id, onClick) => {
            const el = document.getElementById(id);
            if (el) el.onclick = (e) => {
                e.target.classList.toggle('active');
                if (onClick) onClick(e.target.classList.contains('active'));
            };
        };

        bindToggle('btn-file-hulls', (_active) => {
            // Toggle hull visibility
        });
    }

    /**
     * Populate filter chips for all categories
     */
    function _populateFilters() {
        if (!_data) return;

        // Helper: Create Filter Chips
        const createChips = (containerId, counts, activeSet) => {
            const container = document.getElementById(containerId);
            if (!container) return;
            container.innerHTML = '';

            counts.forEach(([key, count]) => {
                const chip = document.createElement('div');
                const isActive = activeSet.has(key);
                chip.className = `filter-chip ${isActive ? 'active' : ''}`;
                chip.innerHTML = `${key} <span class="chip-count">${count}</span>`;
                chip.onclick = () => {
                    if (activeSet.has(key)) activeSet.delete(key);
                    else activeSet.add(key);

                    chip.classList.toggle('active');
                    _updateFilterBadge();
                    // Call refreshGraph if available
                    if (typeof refreshGraph === 'function') refreshGraph();
                };
                container.appendChild(chip);
            });

            const type = containerId.replace('filter-', '');
            const countEl = document.getElementById(`count-${type}`);
            if (countEl) countEl.innerText = activeSet.size;
        };

        // Get accessor functions
        const getNodeRing = typeof window.getNodeRing === 'function' ? window.getNodeRing :
            (typeof NODE !== 'undefined' ? NODE.getRing : (n => n.ring || 'Unknown'));
        const getNodeTier = typeof window.getNodeTier === 'function' ? window.getNodeTier :
            (typeof NODE !== 'undefined' ? NODE.getTier : (n => n.tier || 'Unknown'));
        const getNodeAtomFamily = typeof window.getNodeAtomFamily === 'function' ? window.getNodeAtomFamily :
            (typeof NODE !== 'undefined' ? NODE.getFamily : (n => n.atom_family || 'Unknown'));
        const normalizeRingValue = typeof window.normalizeRingValue === 'function' ? window.normalizeRingValue :
            (typeof NODE !== 'undefined' ? NODE.normalizeRing : (v => v));
        const collectCounts = typeof window.collectCounts === 'function' ? window.collectCounts :
            _defaultCollectCounts;

        // Get VIS_FILTERS
        const VIS_FILTERS = window.VIS_FILTERS || { rings: new Set(), tiers: new Set(), roles: new Set(), edges: new Set(), families: new Set() };

        // 1. LAYERS (Rings)
        const ringCounts = collectCounts(_data.nodes, getNodeRing);
        const rawRingDefaults = _data.controls?.filters?.rings || [];
        const ringDefaults = rawRingDefaults
            .map(v => normalizeRingValue(v))
            .filter(v => v !== null);

        if (VIS_FILTERS.rings.size === 0 && ringDefaults.length > 0) {
            const availableRings = new Set(ringCounts.map(([ring]) => ring));
            const matchedRings = ringDefaults.filter(r => availableRings.has(r));
            if (matchedRings.length > 0) {
                matchedRings.forEach(r => VIS_FILTERS.rings.add(r));
            } else {
                const familyCounts = collectCounts(_data.nodes, getNodeAtomFamily);
                const availableFamilies = new Set(familyCounts.map(([family]) => family));
                const matchedFamilies = ringDefaults.filter(f => availableFamilies.has(f));
                if (matchedFamilies.length > 0 && VIS_FILTERS.families.size === 0) {
                    matchedFamilies.forEach(f => VIS_FILTERS.families.add(f));
                    console.warn('[Filters] Ring defaults matched families; applying as family filters.');
                }
            }
        }
        createChips('filter-rings', ringCounts, VIS_FILTERS.rings);

        // 2. TIERS
        const tierCounts = collectCounts(_data.nodes, getNodeTier);
        createChips('filter-tiers', tierCounts, VIS_FILTERS.tiers);

        // 3. ROLES
        const roleCounts = collectCounts(_data.nodes, n => String(n.role || 'Unknown'));
        createChips('filter-roles', roleCounts, VIS_FILTERS.roles);

        // 4. EDGES
        const edgeCounts = collectCounts(_data.links, l => String(l.edge_type || l.type || 'default'));
        createChips('filter-edges', edgeCounts, VIS_FILTERS.edges);

        // 5. DATAMAPS
        _populateDatamaps();

        _updateFilterBadge();
    }

    /**
     * Default collectCounts implementation
     */
    function _defaultCollectCounts(items, accessor) {
        const counts = new Map();
        items.forEach(item => {
            const key = accessor(item);
            counts.set(key, (counts.get(key) || 0) + 1);
        });
        return Array.from(counts.entries()).sort((a, b) => b[1] - a[1]);
    }

    /**
     * Populate datamap chips
     */
    function _populateDatamaps() {
        const container = document.getElementById('filter-datamaps');
        if (!container) return;
        container.innerHTML = '';

        const controls = _data.controls || {};
        const resolveDatamapConfigs = typeof window.resolveDatamapConfigs === 'function'
            ? window.resolveDatamapConfigs
            : () => [];
        const configs = resolveDatamapConfigs(controls);
        const ACTIVE_DATAMAPS = window.ACTIVE_DATAMAPS || new Set();
        const setDatamap = typeof window.setDatamap === 'function' ? window.setDatamap : () => {};

        configs.forEach(cfg => {
            const chip = document.createElement('div');
            const isActive = ACTIVE_DATAMAPS.has(cfg.id);
            chip.className = `filter-chip ${isActive ? 'active' : ''}`;
            chip.style.width = '100%';
            chip.style.marginBottom = '4px';
            chip.innerHTML = `${cfg.label}`;

            chip.onclick = () => {
                setDatamap(cfg.id);
                Array.from(container.children).forEach(c => c.classList.remove('active'));
                chip.classList.add('active');
            };
            container.appendChild(chip);
        });

        const countEl = document.getElementById('count-datamaps');
        if (countEl) countEl.innerText = configs.length;
    }

    /**
     * Update filter badge count
     */
    function _updateFilterBadge() {
        const VIS_FILTERS = window.VIS_FILTERS || { rings: new Set(), tiers: new Set(), roles: new Set() };

        let total = 0;
        total += VIS_FILTERS.rings.size;
        total += VIS_FILTERS.tiers.size;
        total += VIS_FILTERS.roles.size;

        const badge = document.getElementById('filter-badge');
        const miniBadge = document.getElementById('filter-badge-mini');

        if (badge) badge.innerText = total;
        if (miniBadge) {
            miniBadge.innerText = total;
            miniBadge.classList.toggle('visible', total > 0);
        }

        const summary = document.getElementById('filter-summary');
        if (summary) {
            summary.innerText = total > 0 ? `${total} filters active` : "No filters active";
        }
    }

    /**
     * Update status display (node/edge counts)
     */
    function _updateStatus() {
        if (_data && _data.nodes) {
            const n = _data.nodes.length;
            const e = _data.links.length;
            const statusNodes = document.getElementById('status-nodes');
            const statusEdges = document.getElementById('status-edges');

            if (statusNodes) statusNodes.innerText = n;
            if (statusEdges) statusEdges.innerText = e;
        }
    }

    /**
     * Refresh filters (re-populate from current data)
     */
    function refreshFilters() {
        _populateFilters();
    }

    /**
     * Update badge count (public interface)
     */
    function updateFilterBadge() {
        _updateFilterBadge();
    }

    // Public API
    return {
        init,
        refreshFilters,
        updateFilterBadge,
        get data() { return _data; },
        get initialized() { return _initialized; }
    };
})();

// Backward compatibility - expose as UIManager
const UIManager = {
    data: null,
    init(data) {
        this.data = data;
        UI_MANAGER.init(data);
    },
    setupSidebar() { /* Now internal */ },
    setupDock() { /* Now internal */ },
    setupModes() { /* Now internal */ },
    populateFilters() { UI_MANAGER.refreshFilters(); },
    populateDatamaps() { UI_MANAGER.refreshFilters(); },
    updateFilterBadge() { UI_MANAGER.updateFilterBadge(); },
    updateStatus() { /* Now internal */ }
};

// Expose globally
window.UI_MANAGER = UI_MANAGER;
window.UIManager = UIManager;
