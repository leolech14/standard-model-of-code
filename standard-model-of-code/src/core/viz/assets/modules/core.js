/**
 * CORE MODULE
 *
 * Foundation constants and utility functions for the visualization.
 * Zero dependencies - this is a foundation module.
 *
 * Usage:
 *   CORE.SELECTION_SIZE_MULT      // Node size multiplier when selected
 *   CORE.PENDULUM                 // OKLCH color oscillator state
 *   CORE.amplify(value, gamma)    // Power law amplification
 *   CORE.amplifyContrast(value)   // S-curve contrast expansion
 */

const CORE = (function() {
    'use strict';

    // =========================================================================
    // CONSTANTS
    // =========================================================================

    const SELECTION_SIZE_MULT = 2.2;    // Make selected nodes BIGGER

    // OKLCH PENDULUM COLOR OSCILLATOR - FULL RAINBOW EDITION
    const PENDULUM = {
        hue: {
            angle: Math.random() * Math.PI * 2,
            velocity: 0,
            damping: null,        // Set from appearance.tokens
            gravity: null,        // Set from appearance.tokens
            length: 1.0,
            rotationSpeed: null   // Set from appearance.tokens
        },
        chroma: {
            angle: Math.random() * Math.PI * 2,
            velocity: 0,
            damping: null,
            gravity: null,
            length: 1.0,
            center: null,
            amplitude: null
        },
        lightness: {
            phase: 0,
            speed: null,
            center: null,
            amplitude: null
        },
        ripple: {
            speed: null,
            scale: null
        },
        currentHue: Math.random() * 360,
        lastTime: 0,
        running: false
    };

    // =========================================================================
    // AMPLIFICATION UTILITIES
    // =========================================================================

    /**
     * Amplification function using power law: f(x) = x^(1/gamma)
     * Maps normalized [0,1] input to amplified [0,1] output
     * @param {number} value - Input value (0-1)
     * @param {number} gamma - Amplification factor (default from APPEARANCE_STATE)
     * @returns {number} Amplified value (0-1)
     */
    function amplify(value, gamma) {
        // Use global APPEARANCE_STATE if available, otherwise default to 1
        const g = gamma !== undefined ? gamma :
            (typeof APPEARANCE_STATE !== 'undefined' ? APPEARANCE_STATE.amplifier : 1);
        if (g === 1) return value;
        // Clamp to valid range
        const v = Math.max(0, Math.min(1, value));
        // Power law: v^(1/gamma) - when gamma>1, small diffs become larger
        // Using 1/gamma so that higher slider = more amplification
        return Math.pow(v, 1 / g);
    }

    /**
     * Contrast amplification: expands values away from midpoint
     * Uses S-curve (tanh) for smooth contrast expansion
     * @param {number} value - Input value (0-1)
     * @param {number} strength - Contrast strength (default from APPEARANCE_STATE)
     * @returns {number} Contrast-enhanced value (0-1)
     */
    function amplifyContrast(value, strength) {
        // Use global APPEARANCE_STATE if available, otherwise default to 1
        const s = strength !== undefined ? strength :
            (typeof APPEARANCE_STATE !== 'undefined' ? APPEARANCE_STATE.amplifier : 1);
        if (s === 1) return value;
        const v = Math.max(0, Math.min(1, value));
        // S-curve using tanh for smooth contrast expansion
        const centered = (v - 0.5) * 2;  // [-1, 1]
        const amplified = Math.tanh(centered * s) / Math.tanh(s);
        return (amplified + 1) / 2;  // Back to [0, 1]
    }

    // =========================================================================
    // PUBLIC API
    // =========================================================================

    return {
        // Constants
        SELECTION_SIZE_MULT,
        PENDULUM,

        // Utilities
        amplify,
        amplifyContrast
    };
})();

// Backward compatibility aliases - Using Object.defineProperty to avoid duplicate declarations
Object.defineProperty(window, 'SELECTION_SIZE_MULT', {
    get: () => CORE.SELECTION_SIZE_MULT,
    configurable: true
});
Object.defineProperty(window, 'PENDULUM', {
    get: () => CORE.PENDULUM,
    configurable: true
});
Object.defineProperty(window, 'amplify', {
    get: () => CORE.amplify,
    configurable: true
});
Object.defineProperty(window, 'amplifyContrast', {
    get: () => CORE.amplifyContrast,
    configurable: true
});
