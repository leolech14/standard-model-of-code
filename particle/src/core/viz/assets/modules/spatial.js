/**
 * ═══════════════════════════════════════════════════════════════════════════
 * SPATIAL MODULE - Spatial algorithms and collision detection
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * Spatial hashing for O(n) collision detection, convex hull calculation,
 * and node sampling utilities.
 * Depends on: IS_3D, FILE_CONTAINMENT, THREE
 *
 * @module SPATIAL
 * @version 1.0.0
 */

window.SPATIAL = (function() {
    'use strict';

    // ═══════════════════════════════════════════════════════════════════════
    // NODE SAMPLING
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Sample nodes evenly if there are too many
     * @param {Array} nodes - Array of nodes
     * @param {number} maxPoints - Maximum number of points to return
     * @returns {Array} Sampled nodes
     */
    function sampleFileNodes(nodes, maxPoints) {
        if (nodes.length <= maxPoints) return nodes;
        const step = Math.ceil(nodes.length / maxPoints);
        return nodes.filter((_, idx) => idx % step === 0);
    }

    // ═══════════════════════════════════════════════════════════════════════
    // CONVEX HULL
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Build 2D convex hull using Andrew's monotone chain algorithm
     * @param {Array} points - Array of {x, y} points
     * @returns {Array|null} Hull points or null if insufficient points
     */
    function buildHull2D(points) {
        if (points.length < 3) return null;

        // Remove duplicates
        const unique = new Map();
        points.forEach(p => {
            const key = `${p.x.toFixed(4)},${p.y.toFixed(4)}`;
            if (!unique.has(key)) unique.set(key, p);
        });

        // Sort by x, then y
        const pts = Array.from(unique.values()).sort((a, b) => {
            if (a.x === b.x) return a.y - b.y;
            return a.x - b.x;
        });

        if (pts.length < 3) return null;

        // Cross product of vectors OA and OB
        const cross = (o, a, b) => (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x);

        // Build lower hull
        const lower = [];
        for (const p of pts) {
            while (lower.length >= 2 && cross(lower[lower.length - 2], lower[lower.length - 1], p) <= 0) {
                lower.pop();
            }
            lower.push(p);
        }

        // Build upper hull
        const upper = [];
        for (let i = pts.length - 1; i >= 0; i--) {
            const p = pts[i];
            while (upper.length >= 2 && cross(upper[upper.length - 2], upper[upper.length - 1], p) <= 0) {
                upper.pop();
            }
            upper.push(p);
        }

        // Remove last point of each half (it's the starting point of the other)
        upper.pop();
        lower.pop();

        return lower.concat(upper);
    }

    /**
     * Compute centroid of points
     * @param {Array} points - Array of THREE.Vector3-like objects
     * @returns {THREE.Vector3} Centroid
     */
    function computeCentroid(points) {
        const THREE = window.THREE;
        const centroid = new THREE.Vector3();
        points.forEach(p => centroid.add(p));
        return centroid.divideScalar(Math.max(1, points.length));
    }

    // ═══════════════════════════════════════════════════════════════════════
    // SPATIAL HASHING - O(n) collision detection
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Build spatial hash grid for efficient neighbor queries
     * @param {Array} nodes - Array of nodes with x, y, z coordinates
     * @param {number} cellSize - Size of each grid cell
     * @returns {Map} Grid map with cell keys to node arrays
     */
    function buildSpatialGrid(nodes, cellSize) {
        const is3D = window.IS_3D;
        const grid = new Map();

        nodes.forEach(node => {
            if (!node || !Number.isFinite(node.x)) return;
            const cellX = Math.floor(node.x / cellSize);
            const cellY = Math.floor(node.y / cellSize);
            const cellZ = is3D ? Math.floor((node.z || 0) / cellSize) : 0;
            const key = `${cellX},${cellY},${cellZ}`;

            if (!grid.has(key)) grid.set(key, []);
            grid.get(key).push(node);
        });

        // Store for file containment
        if (window.FILE_CONTAINMENT) {
            window.FILE_CONTAINMENT.spatialGrid = grid;
        }

        return grid;
    }

    /**
     * Get keys for neighboring cells (3x3x3 in 3D, 3x3 in 2D)
     * @param {number} cellX - Cell X coordinate
     * @param {number} cellY - Cell Y coordinate
     * @param {number} cellZ - Cell Z coordinate
     * @returns {Array} Array of neighbor cell keys
     */
    function getNeighborCells(cellX, cellY, cellZ) {
        const is3D = window.IS_3D;
        const neighbors = [];

        for (let dx = -1; dx <= 1; dx++) {
            for (let dy = -1; dy <= 1; dy++) {
                for (let dz = is3D ? -1 : 0; dz <= (is3D ? 1 : 0); dz++) {
                    neighbors.push(`${cellX + dx},${cellY + dy},${cellZ + dz}`);
                }
            }
        }

        return neighbors;
    }

    /**
     * Apply soft collision forces to push overlapping nodes apart
     * @param {Array} nodes - Array of nodes
     * @param {number} cellSize - Spatial grid cell size
     * @param {number} repulsionStrength - Strength of repulsion (0-1)
     */
    function applySoftCollisions(nodes, cellSize, repulsionStrength = 0.5) {
        const containment = window.FILE_CONTAINMENT;
        const is3D = window.IS_3D;

        if (!containment || !containment.collisionEnabled) return;

        const grid = buildSpatialGrid(nodes, cellSize);
        const minDist = 8;  // Minimum distance between particles
        const minDistSq = minDist * minDist;

        nodes.forEach(node => {
            if (!node || !Number.isFinite(node.x)) return;
            if (!node.__physics) {
                node.__physics = { vx: 0, vy: 0, vz: 0 };
            }

            const cellX = Math.floor(node.x / cellSize);
            const cellY = Math.floor(node.y / cellSize);
            const cellZ = is3D ? Math.floor((node.z || 0) / cellSize) : 0;
            const neighborKeys = getNeighborCells(cellX, cellY, cellZ);

            neighborKeys.forEach(key => {
                const cellNodes = grid.get(key);
                if (!cellNodes) return;

                cellNodes.forEach(other => {
                    if (other === node) return;

                    const dx = node.x - other.x;
                    const dy = node.y - other.y;
                    const dz = is3D ? ((node.z || 0) - (other.z || 0)) : 0;
                    const distSq = dx * dx + dy * dy + dz * dz;

                    if (distSq < minDistSq && distSq > 0.001) {
                        const dist = Math.sqrt(distSq);
                        const overlap = minDist - dist;
                        const force = (overlap / minDist) * repulsionStrength;

                        // Push apart along normal
                        const nx = dx / dist;
                        const ny = dy / dist;
                        const nz = is3D ? dz / dist : 0;

                        node.__physics.vx += nx * force;
                        node.__physics.vy += ny * force;
                        if (is3D) node.__physics.vz += nz * force;
                    }
                });
            });
        });
    }

    // ═══════════════════════════════════════════════════════════════════════
    // MODULE EXPORT
    // ═══════════════════════════════════════════════════════════════════════

    return {
        sampleFileNodes: sampleFileNodes,
        buildHull2D: buildHull2D,
        computeCentroid: computeCentroid,
        buildSpatialGrid: buildSpatialGrid,
        getNeighborCells: getNeighborCells,
        applySoftCollisions: applySoftCollisions
    };
})();

// ═══════════════════════════════════════════════════════════════════════════
// BACKWARD COMPATIBILITY SHIMS
// ═══════════════════════════════════════════════════════════════════════════

window.sampleFileNodes = SPATIAL.sampleFileNodes;
window.buildHull2D = SPATIAL.buildHull2D;
window.computeCentroid = SPATIAL.computeCentroid;
window.buildSpatialGrid = SPATIAL.buildSpatialGrid;
window.getNeighborCells = SPATIAL.getNeighborCells;
window.applySoftCollisions = SPATIAL.applySoftCollisions;

console.log('[Module] SPATIAL loaded - 6 functions');
