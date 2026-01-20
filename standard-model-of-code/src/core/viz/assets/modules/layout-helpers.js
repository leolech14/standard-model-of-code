/**
 * ═══════════════════════════════════════════════════════════════════════════
 * LAYOUT-HELPERS MODULE - Layout stability and position utilities
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * Functions for saving/restoring node positions, freezing/unfreezing layout,
 * and calculating file positions.
 * Depends on: Graph, NODE_POSITION_CACHE, LAYOUT_FROZEN, IS_3D
 *
 * @module LAYOUT_HELPERS
 * @version 1.0.0
 */

window.LAYOUT_HELPERS = (function() {
    'use strict';

    // ═══════════════════════════════════════════════════════════════════════
    // POSITION PERSISTENCE
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Save current node positions to cache
     */
    function saveNodePositions() {
        const Graph = window.Graph;
        const cache = window.NODE_POSITION_CACHE;
        if (!Graph || !cache) return;

        const nodes = Graph.graphData().nodes || [];
        nodes.forEach(node => {
            if (node.x !== undefined && node.y !== undefined) {
                cache.set(node.id, {
                    x: node.x, y: node.y, z: node.z || 0,
                    vx: node.vx || 0, vy: node.vy || 0, vz: node.vz || 0,
                    fx: node.fx, fy: node.fy, fz: node.fz
                });
            }
        });
    }

    /**
     * Restore node positions from cache
     * @param {Array} nodes - Nodes to restore positions for
     */
    function restoreNodePositions(nodes) {
        const cache = window.NODE_POSITION_CACHE;
        const frozen = window.LAYOUT_FROZEN;
        if (!cache) return;

        nodes.forEach(node => {
            const cached = cache.get(node.id);
            if (cached) {
                node.x = cached.x;
                node.y = cached.y;
                node.z = cached.z;
                node.vx = cached.vx;
                node.vy = cached.vy;
                node.vz = cached.vz;
                // Pin nodes in place when layout is frozen
                if (frozen) {
                    node.fx = cached.x;
                    node.fy = cached.y;
                    node.fz = cached.z;
                }
            }
        });
    }

    // ═══════════════════════════════════════════════════════════════════════
    // LAYOUT FREEZE/UNFREEZE
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Freeze layout by pinning all nodes in place
     */
    function freezeLayout() {
        window.LAYOUT_FROZEN = true;
        const Graph = window.Graph;
        if (!Graph) return;

        const nodes = Graph.graphData().nodes || [];
        nodes.forEach(node => {
            if (node.x !== undefined) {
                node.fx = node.x;
                node.fy = node.y;
                node.fz = node.z;
            }
        });
        Graph.cooldownTicks(0);  // Stop simulation immediately
    }

    /**
     * Unfreeze layout by unpinning all nodes
     */
    function unfreezeLayout() {
        window.LAYOUT_FROZEN = false;
        const Graph = window.Graph;
        if (!Graph) return;

        const nodes = Graph.graphData().nodes || [];
        nodes.forEach(node => {
            node.fx = undefined;
            node.fy = undefined;
            node.fz = undefined;
        });
    }

    /**
     * Reset layout - clear cache and reheat simulation
     */
    function resetLayout() {
        const Graph = window.Graph;
        const cache = window.NODE_POSITION_CACHE;

        // Clear position cache
        if (cache) cache.clear();

        // Unfreeze and restart simulation
        unfreezeLayout();

        if (Graph) {
            Graph.cooldownTicks(200);  // Allow simulation to run
            Graph.d3ReheatSimulation();
        }

        if (typeof window.showModeToast === 'function') {
            window.showModeToast('Layout reset - physics running');
        }
    }

    // ═══════════════════════════════════════════════════════════════════════
    // LINK/FILE HELPERS
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Get the ID of a link endpoint (source or target)
     * @param {Object} link - The link object
     * @param {string} side - 'source' or 'target'
     * @returns {string|undefined} The endpoint ID
     */
    function getLinkEndpointId(link, side) {
        const endpoint = link?.[side];
        if (endpoint && typeof endpoint === 'object') {
            return endpoint.id || endpoint;
        }
        return endpoint;
    }

    /**
     * Calculate target position for a file node in radial layout
     * @param {number} fileIdx - Index of the file
     * @param {number} totalFiles - Total number of files
     * @param {number} radius - Radius of the circle
     * @param {number} zSpacing - Z-axis spacing between files
     * @returns {Object} Position {x, y, z}
     */
    function getFileTarget(fileIdx, totalFiles, radius, zSpacing) {
        if (totalFiles <= 0) {
            return { x: 0, y: 0, z: 0 };
        }
        const angle = (fileIdx / totalFiles) * Math.PI * 2;
        const is3D = window.IS_3D;
        return {
            x: Math.cos(angle) * radius,
            y: Math.sin(angle) * radius,
            z: is3D ? (fileIdx - totalFiles / 2) * zSpacing : 0
        };
    }

    // ═══════════════════════════════════════════════════════════════════════
    // MODULE EXPORT
    // ═══════════════════════════════════════════════════════════════════════

    return {
        savePositions: saveNodePositions,
        restorePositions: restoreNodePositions,
        freeze: freezeLayout,
        unfreeze: unfreezeLayout,
        reset: resetLayout,
        getLinkEndpointId: getLinkEndpointId,
        getFileTarget: getFileTarget
    };
})();

// ═══════════════════════════════════════════════════════════════════════════
// BACKWARD COMPATIBILITY SHIMS
// ═══════════════════════════════════════════════════════════════════════════

window.saveNodePositions = LAYOUT_HELPERS.savePositions;
window.restoreNodePositions = LAYOUT_HELPERS.restorePositions;
window.freezeLayout = LAYOUT_HELPERS.freeze;
window.unfreezeLayout = LAYOUT_HELPERS.unfreeze;
window.resetLayout = LAYOUT_HELPERS.reset;
window.getLinkEndpointId = LAYOUT_HELPERS.getLinkEndpointId;
window.getFileTarget = LAYOUT_HELPERS.getFileTarget;

console.log('[Module] LAYOUT_HELPERS loaded - 7 functions');
