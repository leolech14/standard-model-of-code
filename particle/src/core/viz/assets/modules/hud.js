/**
 * ═══════════════════════════════════════════════════════════════════════════
 * HUD MODULE - Heads-up display management
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * Handles HUD fade behavior and stats panel updates.
 * Depends on: DOM elements (stat-nodes, stat-edges, stat-entropy, etc.)
 *
 * @module HUD
 * @version 1.0.0
 */

window.HUD = (function() {
    'use strict';

    // ═══════════════════════════════════════════════════════════════════════
    // HUD FADE BEHAVIOR
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Setup HUD auto-fade on idle
     * Fades HUD elements after period of inactivity
     */
    function setupFade() {
        const idleDelay = 2200;
        let timer = null;

        const activate = () => {
            document.body.classList.remove('hud-quiet');
            if (timer) {
                clearTimeout(timer);
            }
            timer = setTimeout(() => {
                document.body.classList.add('hud-quiet');
            }, idleDelay);
        };

        ['mousemove', 'mousedown', 'keydown', 'touchstart'].forEach((evt) => {
            window.addEventListener(evt, activate, { passive: true });
        });

        activate();
    }

    // ═══════════════════════════════════════════════════════════════════════
    // STATS UPDATES
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Update all HUD stats elements
     * @param {Object} data - Graph data with nodes, links, meta
     */
    function updateStats(data) {
        if (!data) return;

        // Stats panel: NODES, EDGES, ENTROPY
        const nodeCount = (data.nodes || []).length;
        const edgeCount = (data.links || []).length;

        const statNodes = document.getElementById('stat-nodes');
        const statEdges = document.getElementById('stat-edges');
        const statEntropy = document.getElementById('stat-entropy');

        if (statNodes) statNodes.textContent = nodeCount.toLocaleString();
        if (statEdges) statEdges.textContent = edgeCount.toLocaleString();
        if (statEntropy) {
            const entropy = data.meta?.entropy ?? data.entropy ?? '--';
            statEntropy.textContent = typeof entropy === 'number' ? entropy.toFixed(2) : entropy;
        }

        // Header panel: target name and timestamp
        const targetName = document.getElementById('target-name');
        const timestamp = document.getElementById('timestamp');

        if (targetName) {
            const target = data.meta?.target || data.target || 'Unknown';
            // Show just the last part of the path
            const shortTarget = target.split('/').pop() || target;
            targetName.textContent = shortTarget;
        }

        if (timestamp) {
            const ts = data.meta?.timestamp || data.timestamp || '';
            // Format: 2024-01-15T10:30:00 -> 2024-01-15 10:30
            const formatted = ts.replace('T', ' ').substring(0, 16);
            timestamp.textContent = formatted || 'Live';
        }
    }

    // ═══════════════════════════════════════════════════════════════════════
    // MODULE EXPORT
    // ═══════════════════════════════════════════════════════════════════════

    return {
        setupFade: setupFade,
        updateStats: updateStats
    };
})();

// ═══════════════════════════════════════════════════════════════════════════
// BACKWARD COMPATIBILITY SHIMS
// ═══════════════════════════════════════════════════════════════════════════

window.setupHudFade = HUD.setupFade;
window.updateHudStats = HUD.updateStats;

console.log('[Module] HUD loaded - 2 functions');
