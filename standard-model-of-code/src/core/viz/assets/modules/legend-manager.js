/**
 * LEGEND MANAGER MODULE
 *
 * Manages legend data, counts, and visibility for all visualization dimensions.
 * Delegates all color operations to the COLOR module.
 *
 * Depends on: COLOR, NODE
 *
 * Usage:
 *   LEGEND.init(nodes, links)           // Initialize with graph data
 *   LEGEND.getLegendData('tier')        // Get legend items for a dimension
 *   LEGEND.getColor('tier', 'T0')       // Get color (delegates to COLOR)
 *   LEGEND.subscribe(callback)          // React to legend changes
 */

const LEGEND = (function() {
    'use strict';

    // =========================================================================
    // DIMENSION METADATA
    // =========================================================================

    const dimensions = {
        tier: {
            name: 'TIERS',
            icon: '◐',
            extract: (node) => NODE.getTier(node)
        },
        family: {
            name: 'FAMILIES',
            icon: '⬡',
            extract: (node) => NODE.getFamily(node)
        },
        ring: {
            name: 'RINGS',
            icon: '◎',
            extract: (node) => NODE.getRing(node)
        },
        layer: {
            name: 'LAYERS',
            icon: '☰',
            extract: (node) => NODE.getLayer(node).toUpperCase()
        },
        effect: {
            name: 'EFFECTS',
            icon: '⚡',
            extract: (node) => NODE.getEffect(node)
        },
        edgeType: {
            name: 'EDGE TYPES',
            icon: '→',
            extract: (link) => (link.edge_type || link.type || 'unknown').toLowerCase()
        },
        edgeFamily: {
            name: 'EDGE FAMILIES',
            icon: '⇢',
            extract: (link) => (link.family || 'Dependency')
        }
    };

    // =========================================================================
    // STATE
    // =========================================================================

    let _counts = {};
    let _subscribers = [];

    // =========================================================================
    // CORE FUNCTIONS
    // =========================================================================

    /**
     * Initialize legend with nodes and links data
     */
    function init(nodes, links) {
        _computeCounts(nodes, links);
        return LEGEND;
    }

    /**
     * Compute counts for all dimensions
     */
    function _computeCounts(nodes, links) {
        _counts = {};

        // Node dimensions
        ['tier', 'family', 'ring', 'layer', 'effect'].forEach(dim => {
            const extract = dimensions[dim]?.extract;
            if (!extract) return;

            _counts[dim] = {};
            (nodes || []).forEach(node => {
                const cat = extract(node);
                _counts[dim][cat] = (_counts[dim][cat] || 0) + 1;
            });
        });

        // Edge dimensions
        ['edgeType', 'edgeFamily'].forEach(dim => {
            const extract = dimensions[dim]?.extract;
            if (!extract) return;

            _counts[dim] = {};
            (links || []).forEach(link => {
                const cat = extract(link);
                _counts[dim][cat] = (_counts[dim][cat] || 0) + 1;
            });
        });

        console.log('[LEGEND] Counts computed:', Object.keys(_counts));
        _notifySubscribers('counts-updated', _counts);
    }

    /**
     * Get legend data for a dimension
     * Returns array of { id, label, color, count, dimension }
     */
    function getLegendData(dimension) {
        const counts = _counts[dimension] || {};

        return Object.keys(counts)
            .filter(cat => counts[cat] > 0)
            .sort((a, b) => (counts[b] || 0) - (counts[a] || 0))
            .map(cat => ({
                id: cat,
                label: COLOR.getLabel(dimension, cat),
                color: COLOR.get(dimension, cat),
                count: counts[cat] || 0,
                dimension: dimension
            }));
    }

    /**
     * Get color for a dimension/category (delegates to COLOR)
     */
    function getColor(dimension, category) {
        return COLOR.get(dimension, category);
    }

    /**
     * Get counts for a dimension
     */
    function getCounts(dimension) {
        return _counts[dimension] || {};
    }

    /**
     * Get all available dimensions
     */
    function getDimensions() {
        return Object.keys(dimensions);
    }

    /**
     * Get dimension metadata
     */
    function getDimensionMeta(dimension) {
        return dimensions[dimension] || null;
    }

    // =========================================================================
    // SUBSCRIPTIONS
    // =========================================================================

    function subscribe(callback) {
        _subscribers.push(callback);
        return () => {
            _subscribers = _subscribers.filter(cb => cb !== callback);
        };
    }

    function _notifySubscribers(event, data) {
        _subscribers.forEach(cb => cb(event, data));
    }

    // =========================================================================
    // PUBLIC API
    // =========================================================================

    return {
        init,
        getLegendData,
        getColor,
        getCounts,
        getDimensions,
        getDimensionMeta,
        subscribe,

        // Direct access to dimensions (for migration)
        dimensions,

        // Computed counts
        get counts() { return _counts; }
    };
})();

// Backward compatibility - LegendManager class wrapper
class LegendManager {
    constructor() {
        this.dimensions = LEGEND.dimensions;
        this.counts = {};
        this._subscribers = [];
    }

    init(nodes, links) {
        LEGEND.init(nodes, links);
        this.counts = LEGEND.counts;
        return this;
    }

    _computeCounts(nodes, links) {
        LEGEND.init(nodes, links);
        this.counts = LEGEND.counts;
    }

    getLegendData(dimension) {
        return LEGEND.getLegendData(dimension);
    }

    getColor(dimension, category) {
        return LEGEND.getColor(dimension, category);
    }

    subscribe(callback) {
        this._subscribers.push(callback);
        return () => {
            this._subscribers = this._subscribers.filter(cb => cb !== callback);
        };
    }

    _notifySubscribers(event, data) {
        this._subscribers.forEach(cb => cb(event, data));
    }
}

// Global Legend instance - defined by app.js (not duplicated here to avoid redeclaration)
// Legend is accessed as a global variable provided by app.js
