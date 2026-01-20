/**
 * ═══════════════════════════════════════════════════════════════════════════
 * DATAMAP MODULE - Data mapping and filtering
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * Datamap configuration, matching, and UI control updates.
 * Depends on: DM, VIS_FILTERS, ACTIVE_DATAMAPS, NODE (node-accessors)
 *
 * @module DATAMAP
 * @version 1.0.0
 */

window.DATAMAP = (function() {
    'use strict';

    // ═══════════════════════════════════════════════════════════════════════
    // NORMALIZE DATAMAP CONFIG
    // ═══════════════════════════════════════════════════════════════════════

    function normalizeDatamapConfig(raw) {
        if (!raw || typeof raw !== 'object') return null;
        const id = String(raw.id || raw.key || raw.label || '').trim();
        if (!id) return null;
        const normalizeList = (value) => {
            if (!Array.isArray(value)) return [];
            return value.map(item => String(item).toUpperCase());
        };
        const normalizeTierList = (value) => {
            if (!Array.isArray(value)) return [];
            return value.map(item => window.normalizeTier(item));
        };
        const match = raw.match || {};
        return {
            id: id.toUpperCase(),
            label: String(raw.label || raw.id || id).toUpperCase(),
            match: {
                atom_families: normalizeList(match.atom_families),
                atom_prefixes: normalizeList(match.atom_prefixes),
                tiers: normalizeTierList(match.tiers),
                rings: normalizeList(match.rings),
                roles: normalizeList(match.roles)
            },
            default: Boolean(raw.default)
        };
    }

    // ═══════════════════════════════════════════════════════════════════════
    // RESOLVE DATAMAP CONFIGS
    // ═══════════════════════════════════════════════════════════════════════

    function resolveDatamapConfigs(controlsConfig) {
        const fromTokens = Array.isArray(controlsConfig.datamaps) ? controlsConfig.datamaps : [];
        const normalized = fromTokens
            .map(normalizeDatamapConfig)
            .filter(Boolean);
        if (normalized.length) return normalized;

        const fallback = controlsConfig.buttons?.datamaps || {};
        return Object.entries(fallback).map(([label, config]) => {
            const prefix = config.filter || null;
            return normalizeDatamapConfig({
                id: label.toUpperCase(),
                label: label.toUpperCase(),
                match: prefix ? { atom_prefixes: [prefix] } : {},
                default: false
            });
        }).filter(Boolean);
    }

    // ═══════════════════════════════════════════════════════════════════════
    // DATAMAP MATCHING
    // ═══════════════════════════════════════════════════════════════════════

    function datamapMatches(node, config) {
        const match = config.match || {};
        const atomId = String(node.atom || '');
        const atomFamily = window.getNodeAtomFamily(node);
        const tier = window.getNodeTier(node);
        const ring = window.getNodeRing(node);
        const role = String(node.role || 'Unknown').toUpperCase();

        if (Array.isArray(match.atom_families) && match.atom_families.length) {
            if (!match.atom_families.includes(atomFamily)) return false;
        }

        if (Array.isArray(match.atom_prefixes) && match.atom_prefixes.length) {
            const matchesFamily = match.atom_prefixes.includes(atomFamily);
            const matchesPrefix = match.atom_prefixes.some(prefix => atomId.startsWith(prefix));
            if (!matchesFamily && !matchesPrefix) return false;
        }

        if (Array.isArray(match.tiers) && match.tiers.length) {
            if (!match.tiers.includes(tier)) return false;
        }

        if (Array.isArray(match.rings) && match.rings.length) {
            if (!match.rings.includes(ring)) return false;
        }

        if (Array.isArray(match.roles) && match.roles.length) {
            if (!match.roles.includes(role)) return false;
        }
        return true;
    }

    // ═══════════════════════════════════════════════════════════════════════
    // SET DATAMAP
    // ═══════════════════════════════════════════════════════════════════════

    function setDatamap(prefix) {
        const ACTIVE_DATAMAPS = window.ACTIVE_DATAMAPS;
        const nextSet = new Set(ACTIVE_DATAMAPS);
        if (!prefix) {
            nextSet.clear();
        } else if (nextSet.has(prefix)) {
            nextSet.delete(prefix);
        } else {
            nextSet.add(prefix);
        }

        if (!window.DM) {
            window.ACTIVE_DATAMAPS = nextSet;
            updateDatamapControls();
            return;
        }

        const subset = window.filterGraph(null, window.CURRENT_DENSITY, nextSet, window.VIS_FILTERS);
        if (!subset.nodes.length) {
            window.showToast('No nodes for that datamap selection.');
            updateDatamapControls();
            return;
        }

        window.ACTIVE_DATAMAPS = nextSet;
        updateDatamapControls();
        window.refreshGraph();
    }

    // ═══════════════════════════════════════════════════════════════════════
    // SET NODE COLOR MODE
    // ═══════════════════════════════════════════════════════════════════════

    function setNodeColorMode(mode) {
        window.NODE_COLOR_MODE = mode;
        if (typeof window.renderAllLegends === 'function') {
            window.renderAllLegends();
        }
        window.refreshGraph();
        if (typeof window.refreshGradientEdgeColors === 'function') {
            window.refreshGradientEdgeColors();
        }
    }

    // ═══════════════════════════════════════════════════════════════════════
    // APPLY DATAMAP (ALIAS)
    // ═══════════════════════════════════════════════════════════════════════

    function applyDatamap(prefix) {
        setDatamap(prefix);
    }

    // ═══════════════════════════════════════════════════════════════════════
    // UPDATE DATAMAP CONTROLS UI
    // ═══════════════════════════════════════════════════════════════════════

    function updateDatamapControls() {
        const DM = window.DM;
        const ACTIVE_DATAMAPS = window.ACTIVE_DATAMAPS;
        const DATAMAP_UI = window.DATAMAP_UI;
        const DATAMAP_CONFIGS = window.DATAMAP_CONFIGS;
        const GRAPH_MODE = window.GRAPH_MODE;
        const VIS_FILTERS = window.VIS_FILTERS;

        if (!DM) return;
        const datamapEnabled = GRAPH_MODE === 'atoms';
        const base = window.filterGraph(null, window.CURRENT_DENSITY, new Set(), VIS_FILTERS);
        const nodes = base.nodes || [];
        const totalCount = nodes.length;

        const allUI = DATAMAP_UI.get('__ALL__');
        if (allUI) {
            allUI.input.checked = ACTIVE_DATAMAPS.size === 0;
            if (allUI.count) {
                allUI.count.textContent = datamapEnabled ? String(totalCount) : '--';
            }
            allUI.input.disabled = !datamapEnabled;
            allUI.wrapper.classList.toggle('disabled', !datamapEnabled);
            allUI.wrapper.classList.toggle('active', datamapEnabled && ACTIVE_DATAMAPS.size === 0);
        }

        DATAMAP_CONFIGS.forEach((config) => {
            const count = nodes.reduce((acc, node) => acc + (datamapMatches(node, config) ? 1 : 0), 0);
            const ui = DATAMAP_UI.get(config.id);
            if (!ui) return;
            if (ui.count) {
                ui.count.textContent = datamapEnabled ? String(count) : '--';
            }
            ui.input.disabled = !datamapEnabled || count === 0;
            ui.wrapper.classList.toggle('disabled', !datamapEnabled || count === 0);
            ui.input.checked = ACTIVE_DATAMAPS.has(config.id);
            ui.wrapper.classList.toggle('active', datamapEnabled && ACTIVE_DATAMAPS.has(config.id));
        });
    }

    // ═══════════════════════════════════════════════════════════════════════
    // MODULE EXPORT
    // ═══════════════════════════════════════════════════════════════════════

    return {
        normalizeConfig: normalizeDatamapConfig,
        resolveConfigs: resolveDatamapConfigs,
        matches: datamapMatches,
        set: setDatamap,
        setColorMode: setNodeColorMode,
        apply: applyDatamap,
        updateControls: updateDatamapControls
    };
})();

// ═══════════════════════════════════════════════════════════════════════════
// BACKWARD COMPATIBILITY SHIMS
// ═══════════════════════════════════════════════════════════════════════════

window.normalizeDatamapConfig = DATAMAP.normalizeConfig;
window.resolveDatamapConfigs = DATAMAP.resolveConfigs;
window.datamapMatches = DATAMAP.matches;
window.setDatamap = DATAMAP.set;
window.setNodeColorMode = DATAMAP.setColorMode;
window.applyDatamap = DATAMAP.apply;
window.updateDatamapControls = DATAMAP.updateControls;

console.log('[Module] DATAMAP loaded - 7 functions');
