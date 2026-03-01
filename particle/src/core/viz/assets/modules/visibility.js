/**
 * ═══════════════════════════════════════════════════════════════════════════
 * VISIBILITY MODULE - UI visibility controls and filter utilities
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * Handles background brightness, metadata visibility, filter clearing,
 * and collapsible section management.
 * Depends on: Graph, APPEARANCE_STATE, VIS_FILTERS, THREE
 *
 * @module VISIBILITY
 * @version 1.0.0
 */

window.VISIBILITY = (function() {
    'use strict';

    // ═══════════════════════════════════════════════════════════════════════
    // BACKGROUND CONTROLS
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Update background brightness based on APPEARANCE_STATE
     */
    function updateBackgroundBrightness() {
        const Graph = window.Graph;
        const APPEARANCE_STATE = window.APPEARANCE_STATE;
        const THREE = window.THREE;

        if (!Graph || !APPEARANCE_STATE.backgroundBase) return;
        const baseColor = new THREE.Color(APPEARANCE_STATE.backgroundBase);
        const brightness = APPEARANCE_STATE.backgroundBrightness ?? 1;
        const adjusted = baseColor.clone().multiplyScalar(brightness);
        Graph.backgroundColor(`#${adjusted.getHexString()}`);
    }

    // ═══════════════════════════════════════════════════════════════════════
    // METADATA VISIBILITY
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Apply metadata visibility settings (report panel, file panel, etc.)
     */
    function applyMetadataVisibility() {
        const VIS_FILTERS = window.VIS_FILTERS;

        const reportPanel = document.getElementById('report-panel');
        const reportButton = document.getElementById('btn-report');
        const filePanel = document.getElementById('file-panel');

        // Guard: elements may not exist in minimal template
        if (!reportPanel && !reportButton) return;

        if (!VIS_FILTERS.metadata.showReportPanel) {
            if (reportPanel) reportPanel.style.display = 'none';
            if (reportButton) {
                reportButton.classList.remove('active');
                reportButton.style.display = 'none';
            }
        } else {
            if (reportButton) reportButton.style.display = 'inline-flex';
        }
        if (!VIS_FILTERS.metadata.showFilePanel && filePanel) {
            filePanel.classList.remove('visible');
        }
    }

    // ═══════════════════════════════════════════════════════════════════════
    // FILTER CONTROLS
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Clear all dimension filters (tier, ring, family, role, file, edge)
     * Used for zero-node recovery and manual reset
     */
    function clearAllFilters() {
        const VIS_FILTERS = window.VIS_FILTERS;

        VIS_FILTERS.tiers.clear();
        VIS_FILTERS.rings.clear();
        VIS_FILTERS.families.clear();
        VIS_FILTERS.roles.clear();
        VIS_FILTERS.files.clear();
        VIS_FILTERS.edges.clear();
        VIS_FILTERS.layers.clear();
        VIS_FILTERS.effects.clear();
        VIS_FILTERS.edgeFamilies.clear();

        // Update legend UI
        document.querySelectorAll('.topo-legend-item.filtered').forEach(el => el.classList.remove('filtered'));

        // Update chip UI
        document.querySelectorAll('.filter-chip.active').forEach(el => el.classList.remove('active'));

        console.log('[Filters] All filters cleared');
    }

    // ═══════════════════════════════════════════════════════════════════════
    // COLLAPSIBLE SECTIONS
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Setup collapsible sections in sidebar and panels
     */
    function setupCollapsibleSections() {
        // Standard sidebar sections
        const titles = document.querySelectorAll('.side-title.collapsible');
        titles.forEach(title => {
            title.onclick = () => {
                const targetId = title.dataset.target;
                const content = document.getElementById(targetId);
                const icon = title.querySelector('.collapse-icon');
                if (content) {
                    const isCollapsed = content.classList.toggle('collapsed');
                    title.classList.toggle('collapsed', isCollapsed);
                    if (icon) icon.textContent = isCollapsed ? '>' : 'v';
                }
            };
        });

        // Topology section collapsibles (GEOMETRY panel)
        const topoTitles = document.querySelectorAll('.topo-section-title.collapsible');
        topoTitles.forEach(title => {
            title.onclick = () => {
                const targetId = title.dataset.target;
                const content = document.getElementById(targetId);
                const icon = title.querySelector('.collapse-icon');
                if (content) {
                    const isCollapsed = content.classList.toggle('collapsed');
                    title.classList.toggle('expanded', !isCollapsed);
                    if (icon) icon.textContent = isCollapsed ? '>' : 'v';
                }
            };
        });
    }

    // ═══════════════════════════════════════════════════════════════════════
    // MODULE EXPORT
    // ═══════════════════════════════════════════════════════════════════════

    return {
        updateBackgroundBrightness: updateBackgroundBrightness,
        applyMetadataVisibility: applyMetadataVisibility,
        clearAllFilters: clearAllFilters,
        setupCollapsibleSections: setupCollapsibleSections
    };
})();

// ═══════════════════════════════════════════════════════════════════════════
// BACKWARD COMPATIBILITY SHIMS
// ═══════════════════════════════════════════════════════════════════════════

window.updateBackgroundBrightness = VISIBILITY.updateBackgroundBrightness;
window.applyMetadataVisibility = VISIBILITY.applyMetadataVisibility;
window.clearAllFilters = VISIBILITY.clearAllFilters;
window.setupCollapsibleSections = VISIBILITY.setupCollapsibleSections;

console.log('[Module] VISIBILITY loaded - 4 functions');
