/**
 * FILE COLOR MODEL
 * 
 * Pure color generation for file visualization.
 * ZERO external dependencies - fully testable in isolation.
 * 
 * Extracted from file-viz.js God Object decomposition.
 * 
 * @usage
 *   const colors = new FileColorModel({ strategy: 'golden-angle' });
 *   const color = colors.getColor(fileIdx, totalFiles, fileName);
 */

const FileColorModel = (function () {
    'use strict';

    // =========================================================================
    // CONSTANTS
    // =========================================================================

    const GOLDEN_RATIO = 1.618033988749895;
    const GOLDEN_ANGLE = 360 / (GOLDEN_RATIO * GOLDEN_RATIO); // ~137.5°

    const STRATEGIES = {
        'golden-angle': 'golden-angle',
        'sequential': 'sequential',
        'hash': 'hash'
    };

    const DEFAULT_CONFIG = {
        strategy: 'golden-angle',
        saturation: 0.7,
        lightness: 0.55,
        lightnessRange: { min: 0.35, max: 0.75 },
        hueOffset: 0
    };

    // =========================================================================
    // PURE UTILITY FUNCTIONS
    // =========================================================================

    /**
     * Clamp value to range
     */
    function clamp(value, min, max) {
        return Math.max(min, Math.min(max, value));
    }

    /**
     * Convert HSL to CSS color string
     */
    function hslToString(h, s, l) {
        return `hsl(${h.toFixed(1)}, ${(s * 100).toFixed(1)}%, ${(l * 100).toFixed(1)}%)`;
    }

    /**
     * Convert HSL to hex color
     */
    function hslToHex(h, s, l) {
        const c = (1 - Math.abs(2 * l - 1)) * s;
        const x = c * (1 - Math.abs((h / 60) % 2 - 1));
        const m = l - c / 2;

        let r, g, b;
        if (h < 60) { r = c; g = x; b = 0; }
        else if (h < 120) { r = x; g = c; b = 0; }
        else if (h < 180) { r = 0; g = c; b = x; }
        else if (h < 240) { r = 0; g = x; b = c; }
        else if (h < 300) { r = x; g = 0; b = c; }
        else { r = c; g = 0; b = x; }

        const toHex = (v) => Math.round((v + m) * 255).toString(16).padStart(2, '0');
        return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
    }

    /**
     * Hash string to unit value [0, 1)
     */
    function hashToUnit(str) {
        if (!str) return 0;
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            hash = ((hash << 5) - hash) + str.charCodeAt(i);
            hash = hash & hash; // Convert to 32bit integer
        }
        return Math.abs(hash % 1000) / 1000;
    }

    // =========================================================================
    // HUE CALCULATION STRATEGIES
    // =========================================================================

    /**
     * Golden angle distribution - maximally distinct colors
     */
    function hueGoldenAngle(fileIdx, totalFiles, hueOffset) {
        return (fileIdx * GOLDEN_ANGLE + hueOffset) % 360;
    }

    /**
     * Sequential distribution - linear spread across spectrum
     */
    function hueSequential(fileIdx, totalFiles, hueOffset) {
        if (totalFiles <= 1) return hueOffset;
        return ((fileIdx / totalFiles) * 360 + hueOffset) % 360;
    }

    /**
     * Hash-based distribution - deterministic based on filename
     */
    function hueFromHash(fileName, hueOffset) {
        return (hashToUnit(fileName) * 360 + hueOffset) % 360;
    }

    // =========================================================================
    // MAIN CLASS
    // =========================================================================

    class FileColorModel {
        constructor(config = {}) {
            this.config = { ...DEFAULT_CONFIG, ...config };
            this._validateConfig();
        }

        _validateConfig() {
            if (!STRATEGIES[this.config.strategy]) {
                console.warn(`[FileColorModel] Unknown strategy "${this.config.strategy}", using golden-angle`);
                this.config.strategy = 'golden-angle';
            }
        }

        /**
         * Get hue for a file based on current strategy
         * @param {number} fileIdx - Index of the file
         * @param {number} totalFiles - Total number of files
         * @param {string} fileName - Name of the file (used for hash strategy)
         * @returns {number} Hue value 0-360
         */
        getHue(fileIdx, totalFiles, fileName = '') {
            const { strategy, hueOffset } = this.config;

            switch (strategy) {
                case 'hash':
                    return hueFromHash(fileName, hueOffset);
                case 'sequential':
                    return hueSequential(fileIdx, totalFiles, hueOffset);
                case 'golden-angle':
                default:
                    return hueGoldenAngle(fileIdx, totalFiles, hueOffset);
            }
        }

        /**
         * Get color for a file
         * @param {number} fileIdx - Index of the file
         * @param {number} totalFiles - Total number of files
         * @param {string} fileName - Name of the file
         * @param {Object} overrides - Optional overrides for saturation/lightness
         * @returns {string} CSS color string
         */
        getColor(fileIdx, totalFiles, fileName = '', overrides = {}) {
            const hue = this.getHue(fileIdx, totalFiles, fileName);
            const saturation = overrides.saturation ?? this.config.saturation;
            const lightness = overrides.lightness ?? this.config.lightness;

            return hslToString(hue, saturation, lightness);
        }

        /**
         * Get color as hex string
         */
        getColorHex(fileIdx, totalFiles, fileName = '', overrides = {}) {
            const hue = this.getHue(fileIdx, totalFiles, fileName);
            const saturation = overrides.saturation ?? this.config.saturation;
            const lightness = overrides.lightness ?? this.config.lightness;

            return hslToHex(hue, saturation, lightness);
        }

        /**
         * Get color as numeric value for Three.js
         */
        getColorNumeric(fileIdx, totalFiles, fileName = '', overrides = {}) {
            const hex = this.getColorHex(fileIdx, totalFiles, fileName, overrides);
            return parseInt(hex.slice(1), 16);
        }

        /**
         * Generate a palette of N colors
         * @param {number} count - Number of colors to generate
         * @returns {Array<string>} Array of CSS color strings
         */
        generatePalette(count) {
            return Array.from({ length: count }, (_, i) =>
                this.getColor(i, count, `file_${i}`)
            );
        }

        /**
         * Update configuration
         */
        setConfig(newConfig) {
            this.config = { ...this.config, ...newConfig };
            this._validateConfig();
        }

        /**
         * Get current configuration
         */
        getConfig() {
            return { ...this.config };
        }
    }

    // =========================================================================
    // STATIC UTILITIES (for one-off use without instantiation)
    // =========================================================================

    FileColorModel.hslToHex = hslToHex;
    FileColorModel.hslToString = hslToString;
    FileColorModel.hashToUnit = hashToUnit;
    FileColorModel.GOLDEN_ANGLE = GOLDEN_ANGLE;
    FileColorModel.STRATEGIES = STRATEGIES;

    return FileColorModel;
})();

// Export for both browser and module contexts
if (typeof window !== 'undefined') {
    window.FileColorModel = FileColorModel;
}
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FileColorModel;
}
