/**
 * NODE ACCESSORS MODULE
 *
 * Provides standardized access to node properties across the visualization.
 * Zero dependencies - this is a foundation module.
 *
 * Usage:
 *   NODE.getTier(node)       // Returns 'T0', 'T1', 'T2', or 'UNKNOWN'
 *   NODE.getFamily(node)     // Returns 'LOG', 'DAT', 'ORG', 'EXE', 'EXT', or 'UNKNOWN'
 *   NODE.getRing(node)       // Returns ring/layer value
 *   NODE.getLayer(node)      // Returns D2_LAYER value
 *   NODE.getEffect(node)     // Returns D6_EFFECT value
 */

const NODE = (function() {
    'use strict';

    // =========================================================================
    // TIER SYSTEM
    // =========================================================================

    // Tier aliases: legacy names -> canonical T0/T1/T2
    const TIER_ALIASES = {
        'CORE': 'T0', 'T0': 'T0',
        'ARCH': 'T1', 'T1': 'T1',
        'EXT': 'T2', 'T2': 'T2',
        'DISCOVERED': 'T2',  // EXT.DISCOVERED -> T2
        'UNKNOWN': 'UNKNOWN'
    };

    function normalizeTier(tier) {
        if (!tier) return 'UNKNOWN';
        const upper = String(tier).toUpperCase();
        return TIER_ALIASES[upper] || upper;
    }

    // Prefer canonical node.tier field; fallback to atom prefix inference
    function getTier(node) {
        // If node is a string (backward compat: called with atomId), infer from prefix
        if (typeof node === 'string') {
            const atomId = node;
            if (!atomId) return 'UNKNOWN';
            if (atomId.startsWith('CORE.')) return 'T0';
            if (atomId.startsWith('ARCH.')) return 'T1';
            if (atomId.startsWith('EXT.')) return 'T2';
            return 'UNKNOWN';
        }
        // Prefer canonical field
        if (node.tier) {
            return normalizeTier(node.tier);
        }
        // Fallback: infer from atom prefix
        const atomId = String(node.atom || '');
        if (atomId.startsWith('CORE.')) return 'T0';
        if (atomId.startsWith('ARCH.')) return 'T1';
        if (atomId.startsWith('EXT.')) return 'T2';
        return 'UNKNOWN';
    }

    // =========================================================================
    // FAMILY SYSTEM
    // =========================================================================

    // Get atom family from canonical field or infer from atom prefix
    function getFamily(node) {
        // Prefer canonical field
        if (node.atom_family) {
            return String(node.atom_family).toUpperCase();
        }
        // Fallback: infer from atom (e.g., "LOG.FNC.M" -> "LOG")
        const atomId = String(node.atom || '');
        const dotIdx = atomId.indexOf('.');
        if (dotIdx > 0) {
            return atomId.substring(0, dotIdx).toUpperCase();
        }
        return 'UNKNOWN';
    }

    // =========================================================================
    // RING SYSTEM
    // =========================================================================

    function normalizeRing(value) {
        if (value === null || value === undefined) return null;
        const ring = String(value).trim().toUpperCase();
        if (!ring) return null;
        const aliases = {
            TEST: 'TESTING'
        };
        return aliases[ring] || ring;
    }

    function getRing(node) {
        const ring = node.ring || node.layer || 'UNKNOWN';
        return normalizeRing(ring) || 'UNKNOWN';
    }

    // =========================================================================
    // LAYER SYSTEM (D2_LAYER)
    // =========================================================================

    function getLayer(node) {
        if (!node) return 'Unknown';
        return node.layer || node.dimensions?.D2_LAYER || 'Unknown';
    }

    // =========================================================================
    // EFFECT SYSTEM (D6_EFFECT)
    // =========================================================================

    function getEffect(node) {
        if (!node) return 'Unknown';
        return node.effect || node.dimensions?.D6_EFFECT || 'Unknown';
    }

    // =========================================================================
    // PUBLIC API
    // =========================================================================

    return {
        // Tier
        getTier,
        normalizeTier,
        TIER_ALIASES,

        // Family
        getFamily,

        // Ring
        getRing,
        normalizeRing,

        // Layer
        getLayer,

        // Effect
        getEffect
    };
})();

// Backward compatibility aliases - Using Object.defineProperty to avoid duplicate declarations
Object.defineProperty(window, 'getNodeTier', { get: () => NODE.getTier, configurable: true });
Object.defineProperty(window, 'getNodeAtomFamily', { get: () => NODE.getFamily, configurable: true });
Object.defineProperty(window, 'getNodeRing', { get: () => NODE.getRing, configurable: true });
Object.defineProperty(window, 'getNodeLayer', { get: () => NODE.getLayer, configurable: true });
Object.defineProperty(window, 'getNodeEffect', { get: () => NODE.getEffect, configurable: true });
Object.defineProperty(window, 'normalizeTier', { get: () => NODE.normalizeTier, configurable: true });
Object.defineProperty(window, 'normalizeRingValue', { get: () => NODE.normalizeRing, configurable: true });
Object.defineProperty(window, 'TIER_ALIASES', { get: () => NODE.TIER_ALIASES, configurable: true });
