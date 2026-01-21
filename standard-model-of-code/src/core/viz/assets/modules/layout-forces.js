/**
 * LAYOUT FORCES
 * 
 * D3 force simulation manipulation for file visualization.
 * Extracted from file-viz.js God Object decomposition.
 * 
 * KEY DESIGN: Takes graph instance as argument - NO GLOBALS.
 * 
 * @usage
 *   LayoutForces.applyClusterForce(Graph, nodes, targets);
 *   LayoutForces.applyCohesionForce(Graph, nodes, config);
 *   LayoutForces.clearForces(Graph, ['cluster', 'fileCohesion']);
 */

const LayoutForces = (function () {
    'use strict';

    // =========================================================================
    // CONSTANTS
    // =========================================================================

    const FORCE_NAMES = {
        CLUSTER: 'cluster',
        COHESION: 'fileCohesion',
        RADIAL: 'fileRadial'
    };

    const DEFAULT_COHESION_CONFIG = {
        strength: 0.3,
        radiusFactor: 1.2,
        minRadius: 15,
        maxRadius: 100,
        centerPull: 0.5
    };

    const DEFAULT_CLUSTER_CONFIG = {
        strength: 0.15,
        decay: 0.02
    };

    // =========================================================================
    // CORE FORCE FUNCTIONS
    // =========================================================================

    /**
     * Create a clustering force that pulls nodes toward target positions
     * @param {Object} graphInstance - The ForceGraph3D instance
     * @param {Array} nodes - Nodes to apply force to (must have x, y, z)
     * @param {Map|Object} targets - Map of nodeId -> { x, y, z } target positions
     * @param {Object} config - Force configuration
     */
    function applyClusterForce(graphInstance, nodes, targets, config = {}) {
        const { strength, decay } = { ...DEFAULT_CLUSTER_CONFIG, ...config };

        if (!graphInstance || !graphInstance.d3Force) {
            console.warn('[LayoutForces] No graph instance or d3Force not available');
            return false;
        }

        // Convert targets to Map if needed
        const targetMap = targets instanceof Map ? targets : new Map(Object.entries(targets));

        // Create custom force
        const clusterForce = (alpha) => {
            const effectiveStrength = strength * alpha;

            nodes.forEach(node => {
                const target = targetMap.get(node.id);
                if (!target) return;

                // Pull toward target
                const dx = target.x - (node.x || 0);
                const dy = target.y - (node.y || 0);
                const dz = target.z - (node.z || 0);

                node.vx = (node.vx || 0) + dx * effectiveStrength;
                node.vy = (node.vy || 0) + dy * effectiveStrength;
                node.vz = (node.vz || 0) + dz * effectiveStrength;
            });
        };

        graphInstance.d3Force(FORCE_NAMES.CLUSTER, clusterForce);
        graphInstance.d3ReheatSimulation();

        return true;
    }

    /**
     * Apply file cohesion force - pulls nodes together within file groups
     * @param {Object} graphInstance - The ForceGraph3D instance
     * @param {Array} nodes - All graph nodes
     * @param {Object} config - Force configuration and physics settings
     */
    function applyCohesionForce(graphInstance, nodes, config = {}) {
        const settings = { ...DEFAULT_COHESION_CONFIG, ...config };

        if (!graphInstance || !graphInstance.d3Force) {
            console.warn('[LayoutForces] No graph instance or d3Force not available');
            return false;
        }

        // Group nodes by file
        const fileGroups = new Map();
        nodes.forEach(node => {
            const fileIdx = node.fileIdx;
            if (fileIdx === undefined || fileIdx < 0) return;

            if (!fileGroups.has(fileIdx)) {
                fileGroups.set(fileIdx, []);
            }
            fileGroups.get(fileIdx).push(node);
        });

        // Precompute centroids
        const centroids = new Map();
        fileGroups.forEach((group, fileIdx) => {
            if (group.length === 0) return;

            const centroid = { x: 0, y: 0, z: 0 };
            group.forEach(n => {
                centroid.x += n.x || 0;
                centroid.y += n.y || 0;
                centroid.z += n.z || 0;
            });
            centroid.x /= group.length;
            centroid.y /= group.length;
            centroid.z /= group.length;

            centroids.set(fileIdx, centroid);
        });

        // Create cohesion force
        const cohesionForce = (alpha) => {
            const effectiveStrength = settings.strength * alpha;

            fileGroups.forEach((group, fileIdx) => {
                if (group.length < 2) return;

                const centroid = centroids.get(fileIdx);
                if (!centroid) return;

                // Compute group radius
                let maxDist = 0;
                group.forEach(n => {
                    const dx = (n.x || 0) - centroid.x;
                    const dy = (n.y || 0) - centroid.y;
                    const dz = (n.z || 0) - centroid.z;
                    const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);
                    if (dist > maxDist) maxDist = dist;
                });

                const targetRadius = Math.min(
                    settings.maxRadius,
                    Math.max(settings.minRadius, maxDist * settings.radiusFactor)
                );

                // Apply force toward centroid with boundary constraint
                group.forEach(n => {
                    const dx = (n.x || 0) - centroid.x;
                    const dy = (n.y || 0) - centroid.y;
                    const dz = (n.z || 0) - centroid.z;
                    const dist = Math.sqrt(dx * dx + dy * dy + dz * dz) || 1;

                    // Pull toward centroid
                    const pullStrength = effectiveStrength * settings.centerPull;
                    n.vx = (n.vx || 0) - dx * pullStrength / dist;
                    n.vy = (n.vy || 0) - dy * pullStrength / dist;
                    n.vz = (n.vz || 0) - dz * pullStrength / dist;

                    // Boundary constraint if outside target radius
                    if (dist > targetRadius) {
                        const overshoot = (dist - targetRadius) / dist;
                        n.vx = (n.vx || 0) - dx * overshoot * effectiveStrength;
                        n.vy = (n.vy || 0) - dy * overshoot * effectiveStrength;
                        n.vz = (n.vz || 0) - dz * overshoot * effectiveStrength;
                    }
                });

                // Update centroid for next iteration
                let newCentroid = { x: 0, y: 0, z: 0 };
                group.forEach(n => {
                    newCentroid.x += n.x || 0;
                    newCentroid.y += n.y || 0;
                    newCentroid.z += n.z || 0;
                });
                newCentroid.x /= group.length;
                newCentroid.y /= group.length;
                newCentroid.z /= group.length;
                centroids.set(fileIdx, newCentroid);
            });
        };

        graphInstance.d3Force(FORCE_NAMES.COHESION, cohesionForce);
        graphInstance.d3ReheatSimulation();

        console.log(`[LayoutForces] Cohesion force applied to ${fileGroups.size} file groups`);
        return true;
    }

    /**
     * Clear specific forces from the simulation
     * @param {Object} graphInstance - The ForceGraph3D instance
     * @param {Array<string>} forceNames - Names of forces to clear
     */
    function clearForces(graphInstance, forceNames = [FORCE_NAMES.CLUSTER, FORCE_NAMES.COHESION]) {
        if (!graphInstance || !graphInstance.d3Force) {
            return false;
        }

        forceNames.forEach(name => {
            graphInstance.d3Force(name, null);
        });

        return true;
    }

    /**
     * Apply radial force - arranges nodes in a ring
     * @param {Object} graphInstance - The ForceGraph3D instance
     * @param {Array} nodes - Nodes to arrange
     * @param {Object} config - { radius, strength, center: {x, y, z} }
     */
    function applyRadialForce(graphInstance, nodes, config = {}) {
        const { radius = 100, strength = 0.3, center = { x: 0, y: 0, z: 0 } } = config;

        if (!graphInstance || !graphInstance.d3Force) {
            return false;
        }

        const radialForce = (alpha) => {
            const effectiveStrength = strength * alpha;

            nodes.forEach((node, i) => {
                const angle = (i / nodes.length) * Math.PI * 2;
                const targetX = center.x + Math.cos(angle) * radius;
                const targetY = center.y + Math.sin(angle) * radius;
                const targetZ = center.z;

                node.vx = (node.vx || 0) + (targetX - (node.x || 0)) * effectiveStrength;
                node.vy = (node.vy || 0) + (targetY - (node.y || 0)) * effectiveStrength;
                node.vz = (node.vz || 0) + (targetZ - (node.z || 0)) * effectiveStrength;
            });
        };

        graphInstance.d3Force(FORCE_NAMES.RADIAL, radialForce);
        graphInstance.d3ReheatSimulation();

        return true;
    }

    // =========================================================================
    // PUBLIC API
    // =========================================================================

    return {
        // Force application
        applyClusterForce,
        applyCohesionForce,
        applyRadialForce,
        clearForces,

        // Constants
        FORCE_NAMES,
        DEFAULT_COHESION_CONFIG,
        DEFAULT_CLUSTER_CONFIG
    };
})();

// Export for both browser and module contexts
if (typeof window !== 'undefined') {
    window.LayoutForces = LayoutForces;
}
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LayoutForces;
}
