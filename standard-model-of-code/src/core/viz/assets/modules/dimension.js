/**
 * ═══════════════════════════════════════════════════════════════════════════
 * DIMENSION MODULE - 2D/3D dimension switching with animation
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * Handles smooth animated transitions between 2D and 3D graph views.
 * Depends on: Graph, IS_3D, DIMENSION_TRANSITION, STARFIELD, STARFIELD_OPACITY,
 *             BLOOM_PASS, BLOOM_STRENGTH, stableSeed, stableZ, fileMode,
 *             GRAPH_MODE, applyFileVizMode
 *
 * @module DIMENSION
 * @version 1.0.0
 */

window.DIMENSION = (function() {
    'use strict';

    // ═══════════════════════════════════════════════════════════════════════
    // DIMENSION TOGGLE
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Toggle between 2D and 3D dimensions
     */
    function toggle() {
        if (window.DIMENSION_TRANSITION) return;
        window.DIMENSION_TRANSITION = true;

        const target3d = !window.IS_3D;
        const button = document.getElementById('btn-dimensions');

        animateChange(target3d, () => {
            window.IS_3D = target3d;
            window.DIMENSION_TRANSITION = false;
            if (button) button.textContent = window.IS_3D ? '2D' : '3D';

            // Re-apply file viz mode if active
            if (window.fileMode && window.GRAPH_MODE === 'atoms') {
                if (typeof window.applyFileVizMode === 'function') {
                    window.applyFileVizMode();
                }
            }
        });
    }

    /**
     * Setup the dimension toggle button
     */
    function setup() {
        const button = document.getElementById('btn-dimensions');
        if (!button) return;

        const updateLabel = () => {
            button.textContent = window.IS_3D ? '2D' : '3D';
        };
        updateLabel();
        button.onclick = toggle;
    }

    // ═══════════════════════════════════════════════════════════════════════
    // ANIMATED TRANSITION
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Animate transition between 2D and 3D
     * @param {boolean} target3d - Whether transitioning to 3D
     * @param {Function} done - Callback when animation completes
     */
    function animateChange(target3d, done) {
        const Graph = window.Graph;
        const STARFIELD = window.STARFIELD;
        const STARFIELD_OPACITY = window.STARFIELD_OPACITY;
        const BLOOM_PASS = window.BLOOM_PASS;
        const BLOOM_STRENGTH = window.BLOOM_STRENGTH;
        const stableSeed = window.stableSeed;
        const stableZ = window.stableZ;

        const nodes = (Graph && Graph.graphData().nodes) ? Graph.graphData().nodes : [];
        const startTime = performance.now();
        const duration = 3000;
        const delayMin = 0;
        const delayMax = 2000;
        const lockPositionsAfterTransition = true;

        const easeInOutSine = (t) => 0.5 - 0.5 * Math.cos(Math.PI * t);

        const starStart = STARFIELD ? STARFIELD.material.opacity : 0;
        const starTarget = target3d ? STARFIELD_OPACITY : 0;
        const bloomStart = BLOOM_PASS ? BLOOM_PASS.strength : 0;
        const bloomTarget = BLOOM_PASS ? (target3d ? BLOOM_STRENGTH : 0) : 0;

        // Store previous simulation settings
        const previousVelocityDecay = (Graph && Graph.d3VelocityDecay) ? Graph.d3VelocityDecay() : null;
        const previousAlphaTarget = (Graph && Graph.d3AlphaTarget) ? Graph.d3AlphaTarget() : null;
        const previousCooldownTicks = (Graph && Graph.cooldownTicks) ? Graph.cooldownTicks() : null;
        const previousCooldownTime = (Graph && Graph.cooldownTime) ? Graph.cooldownTime() : null;

        // Freeze simulation during transition
        if (Graph && Graph.cooldownTicks) Graph.cooldownTicks(Infinity);
        if (Graph && Graph.cooldownTime) Graph.cooldownTime(Infinity);
        if (Graph && Graph.d3VelocityDecay) Graph.d3VelocityDecay(1);
        if (Graph && Graph.d3AlphaTarget) Graph.d3AlphaTarget(0);
        if (Graph && Graph.d3ReheatSimulation) Graph.d3ReheatSimulation();

        // Initialize node animation state
        nodes.forEach((node) => {
            node.__xStart = node.x || 0;
            node.__yStart = node.y || 0;
            node.__zStart = node.z || 0;
            node.__delay = delayMin + (stableSeed(node, 'delay') * (delayMax - delayMin));
            node.fx = node.__xStart;
            node.fy = node.__yStart;
            node.vx = 0;
            node.vy = 0;
            node.vz = 0;

            if (target3d) {
                if (node.__z3d === undefined || node.__z3d === null) {
                    node.__z3d = node.__zStart || stableZ(node);
                }
            } else {
                node.__z3d = node.__zStart;
            }
        });

        const maxDistance = nodes.reduce((acc, node) => Math.max(acc, Math.abs(node.__zStart || 0)), 1);

        Graph.numDimensions(3);

        const animate = (now) => {
            const elapsed = now - startTime;
            const t = Math.min(1, elapsed / duration);
            const eased = easeInOutSine(t);

            // Animate each node's Z position
            nodes.forEach((node) => {
                const startZ = node.__zStart || 0;
                const targetZ = target3d ? (node.__z3d || 0) : 0;
                const delay = node.__delay || 0;
                const localDuration = Math.max(600, duration - delay);
                const localElapsed = Math.max(0, elapsed - delay);
                const localT = Math.min(1, localElapsed / localDuration);
                const localEase = easeInOutSine(localT);
                const distanceRatio = maxDistance > 0 ? Math.abs(startZ) / maxDistance : 0;
                const distanceCurve = 0.6 + (1 - distanceRatio) * 0.6;
                const progress = Math.pow(localEase, distanceCurve);
                const nextZ = startZ + (targetZ - startZ) * progress;
                node.z = nextZ;
                node.fz = nextZ;
                node.vz = 0;
            });

            // Animate starfield and bloom
            if (STARFIELD) {
                const nextOpacity = starStart + (starTarget - starStart) * eased;
                STARFIELD.material.opacity = nextOpacity;
                STARFIELD.visible = nextOpacity > 0.02;
            }
            if (BLOOM_PASS) {
                BLOOM_PASS.strength = bloomStart + (bloomTarget - bloomStart) * eased;
            }

            if (t < 1) {
                requestAnimationFrame(animate);
            } else {
                // Animation complete - clean up
                nodes.forEach((node) => {
                    delete node.fz;
                    delete node.__zStart;
                    delete node.__xStart;
                    delete node.__yStart;
                    delete node.__delay;

                    if (!target3d) {
                        node.z = 0;
                        node.fz = 0;
                    } else if (lockPositionsAfterTransition) {
                        node.z = node.__z3d || node.z || 0;
                        node.fz = node.z;
                    } else {
                        delete node.fx;
                        delete node.fy;
                    }
                });

                Graph.numDimensions(target3d ? 3 : 2);

                if (!target3d && STARFIELD) {
                    STARFIELD.visible = false;
                }

                // Restore simulation settings
                if (Graph && Graph.d3VelocityDecay && previousVelocityDecay !== null) {
                    Graph.d3VelocityDecay(previousVelocityDecay);
                }
                if (Graph && Graph.d3AlphaTarget && previousAlphaTarget !== null) {
                    Graph.d3AlphaTarget(previousAlphaTarget);
                }
                if (Graph && Graph.cooldownTicks && previousCooldownTicks !== null) {
                    Graph.cooldownTicks(previousCooldownTicks);
                }
                if (Graph && Graph.cooldownTime && previousCooldownTime !== null) {
                    Graph.cooldownTime(previousCooldownTime);
                }

                if (done) done();
            }
        };

        requestAnimationFrame(animate);
    }

    // ═══════════════════════════════════════════════════════════════════════
    // MODULE EXPORT
    // ═══════════════════════════════════════════════════════════════════════

    return {
        toggle: toggle,
        setup: setup,
        animateChange: animateChange
    };
})();

// ═══════════════════════════════════════════════════════════════════════════
// BACKWARD COMPATIBILITY SHIMS
// ═══════════════════════════════════════════════════════════════════════════

window.toggleDimensions = DIMENSION.toggle;
window.setupDimensionToggle = DIMENSION.setup;
window.animateDimensionChange = DIMENSION.animateChange;

console.log('[Module] DIMENSION loaded - 3 functions');
