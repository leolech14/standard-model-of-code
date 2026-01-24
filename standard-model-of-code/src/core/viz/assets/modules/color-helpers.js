/**
 * ═══════════════════════════════════════════════════════════════════════════
 * COLOR-HELPERS MODULE - Color utilities and conversions
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * Topology colors, color normalization, file hue generation.
 * Depends on: UTILS (parseOklchString, hashToUnit, clampValue), COLOR (oklchColor)
 *
 * @module COLOR_HELPERS
 * @version 1.0.0
 */

window.COLOR_HELPERS = (function() {
    'use strict';

    // ═══════════════════════════════════════════════════════════════════════
    // TOPOLOGY COLOR LOOKUP
    // ═══════════════════════════════════════════════════════════════════════

    function getTopoColor(category, key) {
        const APPEARANCE_CONFIG = window.APPEARANCE_CONFIG;
        if (!APPEARANCE_CONFIG || !APPEARANCE_CONFIG.color) return { l: 50, c: 0, h: 0 };

        let tokenKey = key;
        let section = 'atom-family'; // Default

        // Map legacy/UI keys to Token keys
        if (category === 'tiers') {
            section = 'atom';
            if (key === 'T0') tokenKey = 't0-core';
            else if (key === 'T1') tokenKey = 't1-arch';
            else if (key === 'T2') tokenKey = 't2-eco';
            else if (key === 'UNKNOWN') tokenKey = 'unknown';
        } else if (category === 'rings') {
            section = 'ring';
            if (key === 'KERNEL') tokenKey = 'DOMAIN';
            if (key === 'CORE') tokenKey = 'APPLICATION';
            if (key === 'SERVICE') tokenKey = 'PRESENTATION';
            if (key === 'ADAPTER') tokenKey = 'INTERFACE';
        } else if (category === 'families') {
            section = 'atom-family';
        }

        // Lookup token
        const tokenStr = APPEARANCE_CONFIG.color[section]?.[tokenKey] || APPEARANCE_CONFIG.color[section]?.['UNKNOWN'];

        // Parse OKLCH
        const parsed = window.parseOklchString(tokenStr);
        if (!parsed) return { l: 50, c: 0, h: 0 }; // Fallback gray

        // Normalize to internal l,c,h format (lowercase)
        return { l: parsed.L * 100, c: parsed.C, h: parsed.H };
    }

    // ═══════════════════════════════════════════════════════════════════════
    // COLOR NORMALIZATION
    // ═══════════════════════════════════════════════════════════════════════

    function normalizeColorInput(color, fallback = 'rgb(128, 128, 128)') {
        if (color === null || color === undefined) {
            return fallback;
        }
        if (typeof color !== 'string') {
            return color;
        }
        const parsed = window.parseOklchString(color);
        if (parsed) {
            return window.oklchColor(parsed.L, parsed.C, parsed.H, parsed.A);
        }
        return color;
    }

    function toColorNumber(color, fallback = '#777777') {
        // Returns CSS hex string (polished-compatible) instead of JS hex int
        if (typeof color === 'number') {
            return '#' + color.toString(16).padStart(6, '0');
        }
        if (typeof color !== 'string') {
            return fallback;
        }
        const normalized = normalizeColorInput(color);
        if (typeof normalized === 'string') {
            color = normalized;
        }
        if (color.startsWith('#') || color.startsWith('rgb') || color.startsWith('hsl')) {
            return color;  // Already valid CSS color
        }
        try {
            const hex = new THREE.Color(color).getHex();
            return '#' + hex.toString(16).padStart(6, '0');
        } catch (err) {
            return fallback;
        }
    }

    function dimColor(hexColor, factor = 0.33) {
        // OKLCH: Delegate to COLOR engine for perceptually uniform dimming
        if (typeof COLOR !== 'undefined' && COLOR.interpolate) {
            return COLOR.interpolate(hexColor, '#000000', factor);
        }
        // Fallback: raw RGB dimming when COLOR not available
        const hex = hexColor.replace('#', '');
        const r = Math.round(parseInt(hex.substr(0, 2), 16) * (1 - factor));
        const g = Math.round(parseInt(hex.substr(2, 2), 16) * (1 - factor));
        const b = Math.round(parseInt(hex.substr(4, 2), 16) * (1 - factor));
        return '#' + [r, g, b].map(x => Math.max(0, Math.min(255, x)).toString(16).padStart(2, '0')).join('');
    }

    // ═══════════════════════════════════════════════════════════════════════
    // FILE COLOR GENERATION
    // ═══════════════════════════════════════════════════════════════════════

    function getFileHue(fileIdx, totalFiles, fileName) {
        const FILE_COLOR_CONFIG = window.FILE_COLOR_CONFIG || {};
        const strategy = FILE_COLOR_CONFIG.strategy || 'golden-angle';
        if (strategy === 'sequential') {
            const denom = Math.max(1, totalFiles);
            return (fileIdx / denom) * 360;
        }
        if (strategy === 'hash') {
            const seed = fileName || String(fileIdx);
            return window.hashToUnit(seed) * 360;
        }
        const angle = FILE_COLOR_CONFIG.angle ?? 137.5;
        return (fileIdx * angle) % 360;
    }

    function getFileColor(fileIdx, totalFiles, fileName, lightnessOverride = null) {
        const FILE_COLOR_CONFIG = window.FILE_COLOR_CONFIG || {};
        const COLOR_TWEAKS = window.COLOR_TWEAKS || {};
        const saturation = FILE_COLOR_CONFIG.saturation ?? 70;
        const lightness = (lightnessOverride !== null)
            ? lightnessOverride
            : (FILE_COLOR_CONFIG.lightness ?? 50);
        const hue = getFileHue(fileIdx, totalFiles, fileName);
        if (typeof FILE_COLOR_CONFIG.chroma === 'number') {
            return window.oklchColor(lightness, FILE_COLOR_CONFIG.chroma, hue);
        }
        const adjustedHue = hue + (COLOR_TWEAKS.hueShift || 0);
        const adjustedLightness = window.clampValue(lightness + (COLOR_TWEAKS.lightnessShift || 0), 0, 100);
        // OKLCH: Route through COLOR engine for perceptually uniform output
        if (typeof COLOR !== 'undefined' && COLOR.toHex) {
            return COLOR.toHex({ h: adjustedHue, c: 0.18, l: adjustedLightness / 100 });
        }
        // Strict fallback: neutral gray
        return '#888888';
    }

    // ═══════════════════════════════════════════════════════════════════════
    // MODULE EXPORT
    // ═══════════════════════════════════════════════════════════════════════

    return {
        getTopoColor: getTopoColor,
        normalizeInput: normalizeColorInput,
        toNumber: toColorNumber,
        dim: dimColor,
        getFileHue: getFileHue,
        getFileColor: getFileColor
    };
})();

// ═══════════════════════════════════════════════════════════════════════════
// BACKWARD COMPATIBILITY SHIMS
// ═══════════════════════════════════════════════════════════════════════════

window.getTopoColor = COLOR_HELPERS.getTopoColor;
window.normalizeColorInput = COLOR_HELPERS.normalizeInput;
window.toColorNumber = COLOR_HELPERS.toNumber;
window.dimColor = COLOR_HELPERS.dim;
window.getFileHue = COLOR_HELPERS.getFileHue;
window.getFileColor = COLOR_HELPERS.getFileColor;

console.log('[Module] COLOR_HELPERS loaded - 6 functions');
