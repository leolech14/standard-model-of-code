/**
 * ═══════════════════════════════════════════════════════════════════════════
 * UTILS MODULE - Pure Utility Functions
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * Zero-dependency pure functions for math, string, and data operations.
 * These functions have NO external state dependencies and can be used anywhere.
 *
 * @module UTILS
 * @version 1.0.0
 * @confidence 99%
 */

window.UTILS = (function() {
    'use strict';

    // ═══════════════════════════════════════════════════════════════════════
    // MATH UTILITIES
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Clamp value to [0, 1] range
     * @param {number} value - Value to clamp
     * @returns {number} Clamped value
     */
    function clamp01(value) {
        return Math.max(0, Math.min(1, value));
    }

    /**
     * Clamp value to [min, max] range
     * @param {number} value - Value to clamp
     * @param {number} min - Minimum bound
     * @param {number} max - Maximum bound
     * @returns {number} Clamped value
     */
    function clampValue(value, min, max) {
        return Math.max(min, Math.min(max, value));
    }

    /**
     * Normalize value to [0, 1] based on max.
     * NOW DELEGATES TO UPB_SCALES when available.
     *
     * @param {number} val - Value to normalize
     * @param {number} max - Maximum value
     * @param {string} [scaleName] - Optional scale name (linear, log, sqrt)
     * @returns {number} Normalized value
     */
    function normalize(val, max, scaleName) {
        // === UPB INTEGRATION ===
        if (window.UPB_SCALES) {
            return window.UPB_SCALES.applyScale(scaleName || 'linear', val, 0, max);
        }
        // Fallback
        return Math.min(1, Math.max(0, val / max));
    }

    /**
     * Normalize metric value based on range.
     * NOW DELEGATES TO UPB_SCALES when available.
     *
     * @param {number} value - Value to normalize
     * @param {{min: number, max: number}} range - Range object
     * @param {string} [scaleName] - Optional scale name (linear, log, sqrt)
     * @returns {number} Normalized value in [0, 1]
     */
    function normalizeMetric(value, range, scaleName) {
        if (!range || range.max <= range.min) {
            return clamp01(value);
        }
        // === UPB INTEGRATION ===
        if (window.UPB_SCALES) {
            return window.UPB_SCALES.applyScale(scaleName || 'linear', value, range.min, range.max);
        }
        // Fallback
        return clamp01((value - range.min) / (range.max - range.min));
    }

    /**
     * Calculate quantile from sorted values
     * @param {number[]} values - Array of numbers
     * @param {number} q - Quantile (0-1)
     * @returns {number} Quantile value
     */
    function quantile(values, q) {
        if (!values.length) return 0;
        const sorted = values.slice().sort((a, b) => a - b);
        const pos = (sorted.length - 1) * q;
        const base = Math.floor(pos);
        const rest = pos - base;
        if (sorted[base + 1] !== undefined) {
            return sorted[base] + rest * (sorted[base + 1] - sorted[base]);
        }
        return sorted[base];
    }

    // ═══════════════════════════════════════════════════════════════════════
    // HASH & SEED UTILITIES
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Convert any value to a unit float [0, 1] via hashing
     * @param {*} value - Any value to hash
     * @returns {number} Hash as unit float
     */
    function hashToUnit(value) {
        const str = String(value || '');
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            hash = ((hash << 5) - hash) + str.charCodeAt(i);
            hash |= 0;
        }
        return (hash >>> 0) / 0xffffffff;
    }

    /**
     * Generate stable seed from node and salt
     * @param {Object} node - Node object with id/name
     * @param {string} salt - Salt string
     * @returns {number} Stable seed in [0, 1]
     */
    function stableSeed(node, salt) {
        const id = String(node.id || node.name || '');
        const combined = `${id}|${salt}`;
        let hash = 0;
        for (let i = 0; i < combined.length; i++) {
            hash = ((hash << 5) - hash + combined.charCodeAt(i)) | 0;
        }
        return ((hash >>> 0) % 1000) / 1000;
    }

    /**
     * Generate stable Z offset for node
     * @param {Object} node - Node object
     * @returns {number} Z offset
     */
    function stableZ(node) {
        const normalized = stableSeed(node, 'z');
        return (normalized - 0.5) * 60;
    }

    /**
     * Generate stable offset vector for node positioning
     * @param {Object} node - Node object
     * @param {string} salt - Salt string
     * @param {number} radius - Base radius
     * @returns {{x: number, y: number, z: number}} Offset vector
     */
    function stableOffset(node, salt, radius) {
        const angle = stableSeed(node, `${salt}:angle`) * Math.PI * 2;
        const spread = 0.3 + stableSeed(node, `${salt}:radius`) * 0.7;
        const zJitter = (stableSeed(node, `${salt}:z`) - 0.5) * radius * 0.6;
        const dist = radius * spread;
        return {
            x: Math.cos(angle) * dist,
            y: Math.sin(angle) * dist,
            z: zJitter
        };
    }

    // ═══════════════════════════════════════════════════════════════════════
    // STRING UTILITIES
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Escape HTML special characters
     * @param {string} text - Text to escape
     * @returns {string} Escaped HTML
     */
    function escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Parse OKLCH color string
     * @param {string} value - OKLCH color string
     * @returns {{L: number, C: number, H: number, A: number}|null} Parsed values or null
     */
    function parseOklchString(value) {
        if (typeof value !== 'string') return null;
        const match = value.trim().match(/^oklch\(\s*([\d.]+)%\s+([\d.]+)\s+([\d.]+)(?:\s*\/\s*([\d.]+))?\s*\)$/i);
        if (!match) return null;
        return {
            L: parseFloat(match[1]),
            C: parseFloat(match[2]),
            H: parseFloat(match[3]),
            A: match[4] !== undefined ? parseFloat(match[4]) : 1
        };
    }

    // ═══════════════════════════════════════════════════════════════════════
    // DATA UTILITIES
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Resolve defaults against available values
     * @param {Array} defaults - Preferred defaults
     * @param {Array} available - Available values
     * @returns {Array} Resolved values
     */
    function resolveDefaults(defaults, available) {
        if (!Array.isArray(defaults) || defaults.length === 0) {
            return available;
        }
        const availableSet = new Set(available);
        const intersection = defaults.filter(value => availableSet.has(value));
        return intersection.length ? intersection : available;
    }

    /**
     * Build dataset key from data object
     * @param {Object} data - Data object with meta, nodes, links
     * @returns {string} Dataset key
     */
    function buildDatasetKey(data) {
        const meta = (data && data.meta) ? data.meta : {};
        const target = meta.target || meta.project || 'dataset';
        const version = meta.version || '';
        const nodeCount = Array.isArray(data?.nodes) ? data.nodes.length : 0;
        const edgeCount = Array.isArray(data?.links)
            ? data.links.length
            : (Array.isArray(data?.edges) ? data.edges.length : 0);
        const raw = `${target}|${nodeCount}|${edgeCount}|${version}`;
        return raw.replace(/[^a-zA-Z0-9_.-]/g, '_').slice(0, 180);
    }

    // ═══════════════════════════════════════════════════════════════════════
    // GEOMETRY UTILITIES
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Calculate bounding box from two points
     * @param {{x: number, y: number}} start - Start point
     * @param {{x: number, y: number}} end - End point
     * @returns {{left: number, top: number, width: number, height: number, right: number, bottom: number}} Box rect
     */
    function getBoxRect(start, end) {
        const left = Math.min(start.x, end.x);
        const top = Math.min(start.y, end.y);
        const width = Math.abs(start.x - end.x);
        const height = Math.abs(start.y - end.y);
        return {
            left,
            top,
            width,
            height,
            right: left + width,
            bottom: top + height
        };
    }

    // ═══════════════════════════════════════════════════════════════════════
    // MODULE EXPORT
    // ═══════════════════════════════════════════════════════════════════════

    return {
        // Math
        clamp01,
        clampValue,
        normalize,
        normalizeMetric,
        quantile,

        // Hash & Seed
        hashToUnit,
        stableSeed,
        stableZ,
        stableOffset,

        // String
        escapeHtml,
        parseOklchString,

        // Data
        resolveDefaults,
        buildDatasetKey,

        // Geometry
        getBoxRect
    };
})();

// ═══════════════════════════════════════════════════════════════════════════
// BACKWARD COMPATIBILITY SHIMS
// ═══════════════════════════════════════════════════════════════════════════
// These ensure existing code continues to work without modification

window.clamp01 = UTILS.clamp01;
window.clampValue = UTILS.clampValue;
window.normalize = UTILS.normalize;
window.normalizeMetric = UTILS.normalizeMetric;
window.quantile = UTILS.quantile;
window.hashToUnit = UTILS.hashToUnit;
window.stableSeed = UTILS.stableSeed;
window.stableZ = UTILS.stableZ;
window.stableOffset = UTILS.stableOffset;
window.escapeHtml = UTILS.escapeHtml;
window.parseOklchString = UTILS.parseOklchString;
window.resolveDefaults = UTILS.resolveDefaults;
window.buildDatasetKey = UTILS.buildDatasetKey;
window.getBoxRect = UTILS.getBoxRect;

console.log('[Module] UTILS loaded - 14 pure functions');
