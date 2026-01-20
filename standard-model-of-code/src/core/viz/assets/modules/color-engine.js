/**
 * COLOR ENGINE MODULE
 *
 * Centralized Color Intelligence System using OKLCH color space.
 * Single source of truth for ALL colors in the visualization.
 * Everything reads from here. OKLCH transforms apply here.
 *
 * Usage:
 *   COLOR.get('tier', 'T0')              // Get hex color for tier T0
 *   COLOR.getInterval('markov', 0.5)     // Get interpolated color
 *   COLOR.setTransform('hueShift', 30)   // Shift all hues by 30 degrees
 *   COLOR.subscribe(callback)            // React to transform changes
 */

const COLOR = (function () {
    'use strict';

    // =========================================================================
    // BASE PALETTE: Semantic color definitions (before OKLCH transforms)
    // =========================================================================

    const palette = {
        // NODE DIMENSIONS - VIVID BASE COLORS (high chroma for bold schemes)
        tier: {
            'T0': { h: 142, c: 0.22, l: 0.68, label: 'Foundation', semantic: 'stable' },      // Green
            'T1': { h: 220, c: 0.22, l: 0.68, label: 'Domain', semantic: 'structure' },       // Blue
            'T2': { h: 330, c: 0.22, l: 0.68, label: 'Application', semantic: 'active' },     // Pink
            'UNKNOWN': { h: 0, c: 0.04, l: 0.50, label: 'Unknown', semantic: 'neutral' }      // Gray
        },
        family: {
            'LOG': { h: 220, c: 0.24, l: 0.65, label: 'Logic', semantic: 'computation' },     // Blue
            'DAT': { h: 142, c: 0.22, l: 0.68, label: 'Data', semantic: 'storage' },          // Green
            'ORG': { h: 280, c: 0.24, l: 0.62, label: 'Organization', semantic: 'structure' },// Purple
            'EXE': { h: 15, c: 0.26, l: 0.62, label: 'Execution', semantic: 'action' },       // Red
            'EXT': { h: 35, c: 0.22, l: 0.65, label: 'External', semantic: 'boundary' },      // Orange
            'UNKNOWN': { h: 0, c: 0.04, l: 0.50, label: 'Unknown', semantic: 'neutral' }
        },
        ring: {
            'DOMAIN': { h: 45, c: 0.22, l: 0.70, label: 'Domain', semantic: 'core' },         // Amber
            'APPLICATION': { h: 220, c: 0.20, l: 0.65, label: 'Application', semantic: 'logic' },
            'INFRASTRUCTURE': { h: 0, c: 0.04, l: 0.50, label: 'Infrastructure', semantic: 'foundation' },
            'PRESENTATION': { h: 280, c: 0.20, l: 0.65, label: 'Presentation', semantic: 'interface' },
            'TESTING': { h: 165, c: 0.14, l: 0.60, label: 'Testing', semantic: 'validation' },
            'UNKNOWN': { h: 0, c: 0.02, l: 0.40, label: 'Unknown', semantic: 'neutral' }
        },
        layer: {
            'PHYSICAL': { h: 220, c: 0.14, l: 0.62, label: 'Physical', semantic: 'concrete' },
            'VIRTUAL': { h: 142, c: 0.14, l: 0.65, label: 'Virtual', semantic: 'runtime' },
            'SEMANTIC': { h: 330, c: 0.14, l: 0.65, label: 'Semantic', semantic: 'meaning' }
        },
        atom: {
            // Function-like (Green-Cyan)
            'function': { h: 160, c: 0.20, l: 0.65, label: 'Function', semantic: 'logic' },
            'method': { h: 175, c: 0.20, l: 0.62, label: 'Method', semantic: 'logic' },
            'closure': { h: 190, c: 0.20, l: 0.60, label: 'Closure', semantic: 'logic' },
            // Class-like (Blue-Purple)
            'class': { h: 260, c: 0.22, l: 0.60, label: 'Class', semantic: 'structure' },
            'interface': { h: 280, c: 0.20, l: 0.65, label: 'Interface', semantic: 'abstraction' },
            'struct': { h: 240, c: 0.20, l: 0.60, label: 'Struct', semantic: 'data' },
            // Module/Package (Orange-Yellow)
            'module': { h: 45, c: 0.22, l: 0.70, label: 'Module', semantic: 'container' },
            'package': { h: 30, c: 0.24, l: 0.65, label: 'Package', semantic: 'container' },
            // Variables/Fields (Pink-Red)
            'variable': { h: 340, c: 0.18, l: 0.65, label: 'Variable', semantic: 'state' },
            'field': { h: 350, c: 0.18, l: 0.62, label: 'Field', semantic: 'state' },
            // Unknown
            'unknown': { h: 0, c: 0.04, l: 0.50, label: 'Unknown', semantic: 'neutral' }
        },
        family: {
            'LOG': { h: 220, c: 0.24, l: 0.65, label: 'Logic', semantic: 'computation' },
            'DAT': { h: 142, c: 0.22, l: 0.68, label: 'Data', semantic: 'storage' },
            'ORG': { h: 280, c: 0.24, l: 0.62, label: 'Organization', semantic: 'structure' },
            'EXE': { h: 15, c: 0.26, l: 0.62, label: 'Execution', semantic: 'action' },
            'EXT': { h: 35, c: 0.22, l: 0.65, label: 'External', semantic: 'boundary' },
            'UNKNOWN': { h: 0, c: 0.04, l: 0.50, label: 'Unknown', semantic: 'neutral' }
        },
        roleCategory: {
            'Query': { h: 190, c: 0.20, l: 0.65, label: 'Query', semantic: 'read' },         // Cyan
            'Command': { h: 25, c: 0.24, l: 0.60, label: 'Command', semantic: 'write' },     // Orange/Red
            'Factory': { h: 280, c: 0.22, l: 0.60, label: 'Factory', semantic: 'create' },   // Purple
            'Storage': { h: 140, c: 0.20, l: 0.65, label: 'Storage', semantic: 'persist' },  // Green
            'Orchestration': { h: 240, c: 0.22, l: 0.60, label: 'Orchestration', semantic: 'manage' }, // Blue
            'Validation': { h: 45, c: 0.24, l: 0.70, label: 'Validation', semantic: 'check' }, // Yellow
            'Transform': { h: 320, c: 0.20, l: 0.60, label: 'Transform', semantic: 'change' }, // Pink
            'Event': { h: 260, c: 0.22, l: 0.65, label: 'Event', semantic: 'async' },        // Violet
            'Utility': { h: 200, c: 0.10, l: 0.70, label: 'Utility', semantic: 'helper' },   // Light Blue
            'Internal': { h: 0, c: 0.00, l: 0.60, label: 'Internal', semantic: 'private' },  // Gray
            'Unknown': { h: 0, c: 0.00, l: 0.50, label: 'Unknown', semantic: 'neutral' }
        },
        subsystem: {
            'Ingress': { h: 220, c: 0.24, l: 0.60, label: 'Ingress', semantic: 'entry' },
            'Egress': { h: 20, c: 0.24, l: 0.60, label: 'Egress', semantic: 'exit' },
            'Domain': { h: 260, c: 0.24, l: 0.55, label: 'Domain Core', semantic: 'core' },
            'Persistence': { h: 142, c: 0.22, l: 0.65, label: 'Persistence', semantic: 'store' },
            'Async': { h: 300, c: 0.22, l: 0.60, label: 'Async', semantic: 'bg' },
            'Presentation': { h: 190, c: 0.20, l: 0.65, label: 'Presentation', semantic: 'ui' },
            'Security': { h: 0, c: 0.26, l: 0.55, label: 'Security', semantic: 'guard' },
            'Observability': { h: 60, c: 0.22, l: 0.75, label: 'Observability', semantic: 'monitor' },
            'Config': { h: 290, c: 0.18, l: 0.65, label: 'config', semantic: 'setup' },
            'Delivery': { h: 30, c: 0.20, l: 0.70, label: 'Delivery', semantic: 'ops' },
            'Unknown': { h: 0, c: 0.00, l: 0.50, label: 'Unknown', semantic: 'neutral' }
        },
        phase: {
            'DATA': { h: 142, c: 0.22, l: 0.65, label: 'Data', semantic: 'structure' },
            'LOGIC': { h: 240, c: 0.24, l: 0.60, label: 'Logic', semantic: 'flow' },
            'ORGANIZATION': { h: 280, c: 0.22, l: 0.60, label: 'Organization', semantic: 'arch' },
            'EXECUTION': { h: 20, c: 0.26, l: 0.60, label: 'Execution', semantic: 'run' }
        },
        state: {
            'Stateless': { h: 220, c: 0.20, l: 0.70, label: 'Stateless', semantic: 'pure' }, // Light Blue
            'Stateful': { h: 20, c: 0.24, l: 0.60, label: 'Stateful', semantic: 'impure' }   // Orange
        },
        effect: {
            'Pure': { h: 142, c: 0.22, l: 0.70, label: 'Pure', semantic: 'safe' },          // Green
            'SideEffect': { h: 340, c: 0.22, l: 0.60, label: 'Side Effect', semantic: 'risk' } // Pink/Red
        },
        visibility: {
            'Public': { h: 220, c: 0.20, l: 0.65, label: 'Public', semantic: 'open' },
            'Private': { h: 0, c: 0.05, l: 0.55, label: 'Private', semantic: 'closed' },
            'Internal': { h: 280, c: 0.15, l: 0.60, label: 'Internal', semantic: 'module' }
        },
        fileType: {
            'js': { h: 60, c: 0.24, l: 0.70, label: 'JavaScript', semantic: 'code' },    // Yellow
            'ts': { h: 240, c: 0.22, l: 0.60, label: 'TypeScript', semantic: 'code' },    // Blue
            'py': { h: 220, c: 0.20, l: 0.62, label: 'Python', semantic: 'code' },        // Blue
            'go': { h: 190, c: 0.22, l: 0.68, label: 'Go', semantic: 'code' },            // Cyan
            'rs': { h: 30, c: 0.24, l: 0.60, label: 'Rust', semantic: 'code' },           // Orange
            'java': { h: 40, c: 0.24, l: 0.62, label: 'Java', semantic: 'code' },         // Orange/Red
            'c': { h: 210, c: 0.18, l: 0.60, label: 'C', semantic: 'code' },             // Blue
            'cpp': { h: 210, c: 0.20, l: 0.55, label: 'C++', semantic: 'code' },          // Blue
            'h': { h: 280, c: 0.16, l: 0.60, label: 'Header', semantic: 'code' },         // Purple
            'html': { h: 20, c: 0.25, l: 0.60, label: 'HTML', semantic: 'markup' },       // Orange
            'css': { h: 230, c: 0.24, l: 0.60, label: 'CSS', semantic: 'style' },         // Blue
            'json': { h: 60, c: 0.18, l: 0.75, label: 'JSON', semantic: 'data' },         // Yellow
            'yaml': { h: 300, c: 0.18, l: 0.65, label: 'YAML', semantic: 'config' },      // Magenta
            'md': { h: 0, c: 0.04, l: 0.70, label: 'Markdown', semantic: 'doc' },         // Gray
            'unknown': { h: 0, c: 0.02, l: 0.50, label: 'Unknown', semantic: 'neutral' }
        },
        // EDGE DIMENSIONS
        edgeType: {
            'calls': { h: 220, c: 0.12, l: 0.55, label: 'Calls', semantic: 'flow' },
            'contains': { h: 142, c: 0.12, l: 0.55, label: 'Contains', semantic: 'structure' },
            'uses': { h: 45, c: 0.12, l: 0.55, label: 'Uses', semantic: 'dependency' },
            'imports': { h: 280, c: 0.12, l: 0.50, label: 'Imports', semantic: 'external' },
            'inherits': { h: 330, c: 0.12, l: 0.55, label: 'Inherits', semantic: 'hierarchy' },
            'implements': { h: 165, c: 0.12, l: 0.55, label: 'Implements', semantic: 'contract' },
            'unknown': { h: 0, c: 0.02, l: 0.35, label: 'Unknown', semantic: 'neutral' }
        }
    };

    // =========================================================================
    // OKLCH TRANSFORM STATE: Applied to all colors
    // =========================================================================

    const transform = {
        hueShift: 0,        // -180 to 180
        chromaScale: 1.0,   // 0 to 2
        lightnessShift: 0,  // -20 to 20 (percentage points)
        amplifier: 1.0      // Gamma for contrast
    };

    // =========================================================================
    // INTERVAL MAPPINGS: For numeric data -> color gradients
    // =========================================================================

    const intervals = {
        markov: {
            stops: [
                { value: 0.0, h: 220, c: 0.05, l: 0.35 },  // Low probability - dim blue
                { value: 0.3, h: 45, c: 0.12, l: 0.55 },   // Medium - amber
                { value: 0.7, h: 15, c: 0.18, l: 0.60 },   // High - orange
                { value: 1.0, h: 0, c: 0.22, l: 0.65 }     // Max - red hot
            ]
        },
        weight: {
            stops: [
                { value: 0.0, h: 220, c: 0.08, l: 0.40 },
                { value: 0.5, h: 180, c: 0.12, l: 0.50 },
                { value: 1.0, h: 142, c: 0.16, l: 0.60 }
            ]
        },
        confidence: {
            stops: [
                { value: 0.0, h: 0, c: 0.02, l: 0.30 },    // Low confidence - gray
                { value: 0.5, h: 45, c: 0.10, l: 0.50 },   // Medium - amber
                { value: 1.0, h: 142, c: 0.16, l: 0.65 }   // High - green
            ]
        },
        complexity: {
            stops: [
                { value: 0.0, h: 142, c: 0.18, l: 0.70 },  // Low complexity (0) - Green
                { value: 0.3, h: 100, c: 0.18, l: 0.75 },  // Moderate (5-10) - Yellow-Green
                { value: 0.6, h: 50, c: 0.20, l: 0.70 },   // High (10-20) - Orange
                { value: 1.0, h: 15, c: 0.24, l: 0.60 }    // Very High (20+) - Red
            ]
        },
        churn: {
            stops: [
                { value: 0.0, h: 230, c: 0.10, l: 0.45 },  // Stale/Cold - Blue
                { value: 0.5, h: 300, c: 0.14, l: 0.60 },  // Active - Purple
                { value: 1.0, h: 30, c: 0.24, l: 0.65 }    // Hot - Orange/Red
            ]
        },
        loc: {
            stops: [
                { value: 0.0, h: 200, c: 0.10, l: 0.75 },  // Small - Light Blue
                { value: 0.3, h: 240, c: 0.18, l: 0.60 },  // Medium - Blue
                { value: 0.7, h: 280, c: 0.20, l: 0.50 },  // Large - Purple
                { value: 1.0, h: 320, c: 0.22, l: 0.40 }   // Massive - Dark Purple
            ]
        },
        trust: {
            stops: [
                { value: 0.0, h: 0, c: 0.24, l: 0.50 },    // Untrusted - Red
                { value: 0.5, h: 60, c: 0.20, l: 0.70 },   // Warning - Yellow
                { value: 1.0, h: 142, c: 0.22, l: 0.65 }   // Trusted - Green
            ]
        },
        responsibility: {
            stops: [
                { value: 0.0, h: 142, c: 0.20, l: 0.70 },  // Single Purpose (1) - Green
                { value: 0.5, h: 60, c: 0.18, l: 0.75 },   // Moderate (5) - Yellow
                { value: 1.0, h: 0, c: 0.24, l: 0.60 }     // God Object (9) - Red
            ]
        },
        purity: {
            stops: [
                { value: 0.0, h: 142, c: 0.20, l: 0.70 },  // Pure (1) - Green
                { value: 0.5, h: 220, c: 0.18, l: 0.65 },  // Mixed (5) - Blue
                { value: 1.0, h: 320, c: 0.24, l: 0.55 }   // I/O Heavy (9) - Purple/Red
            ]
        },
        boundary_score: {
            stops: [
                { value: 0.0, h: 240, c: 0.15, l: 0.65 },  // Internal (1) - Blue
                { value: 0.5, h: 280, c: 0.18, l: 0.60 },  // Module (5) - Purple
                { value: 1.0, h: 20, c: 0.24, l: 0.60 }    // External API (9) - Orange
            ]
        },
        lifecycle_score: {
            stops: [
                { value: 0.0, h: 180, c: 0.15, l: 0.70 },  // Ephemeral (1) - Cyan
                { value: 0.5, h: 220, c: 0.18, l: 0.60 },  // Managed (5) - Blue
                { value: 1.0, h: 280, c: 0.22, l: 0.50 }   // Singleton (9) - Purple
            ]
        },
        centrality: {
            stops: [
                { value: 0.0, h: 240, c: 0.05, l: 0.40 },  // Periphery - Gray/Blue
                { value: 0.5, h: 280, c: 0.20, l: 0.60 },  // Bridge - Purple
                { value: 1.0, h: 340, c: 0.25, l: 0.65 }   // Core - Pink/Red
            ]
        },
        fan_in: {
            stops: [
                { value: 0.0, h: 220, c: 0.10, l: 0.65 },  // Low - Blue
                { value: 0.5, h: 300, c: 0.18, l: 0.60 },  // Med - Purple
                { value: 1.0, h: 30, c: 0.24, l: 0.65 }    // High - Orange
            ]
        },
        fan_out: {
            stops: [
                { value: 0.0, h: 142, c: 0.15, l: 0.65 },  // Low - Green
                { value: 0.5, h: 60, c: 0.18, l: 0.70 },   // Med - Yellow
                { value: 1.0, h: 0, c: 0.24, l: 0.60 }     // High - Red
            ]
        }
};

// =========================================================================
// SUBSCRIBERS: Reactive notifications
// =========================================================================

let _subscribers = [];

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
// OKLCH -> HEX CONVERSION
// =========================================================================

function _toHex(oklch) {
    const { h, c, l } = oklch;

    // Convert OKLCH to approximate RGB
    const hRad = h * Math.PI / 180;
    const a = c * Math.cos(hRad);
    const b = c * Math.sin(hRad);

    // Simplified OKLab to linear RGB (approximate)
    const L = l;
    const l_ = L + 0.3963377774 * a + 0.2158037573 * b;
    const m_ = L - 0.1055613458 * a - 0.0638541728 * b;
    const s_ = L - 0.0894841775 * a - 1.2914855480 * b;

    const l3 = l_ * l_ * l_;
    const m3 = m_ * m_ * m_;
    const s3 = s_ * s_ * s_;

    let r = +4.0767416621 * l3 - 3.3077115913 * m3 + 0.2309699292 * s3;
    let g = -1.2684380046 * l3 + 2.6097574011 * m3 - 0.3413193965 * s3;
    let bl = -0.0041960863 * l3 - 0.7034186147 * m3 + 1.7076147010 * s3;

    // Clamp and convert to sRGB
    const toSRGB = (x) => {
        x = Math.max(0, Math.min(1, x));
        return x <= 0.0031308 ? 12.92 * x : 1.055 * Math.pow(x, 1 / 2.4) - 0.055;
    };

    r = Math.round(toSRGB(r) * 255);
    g = Math.round(toSRGB(g) * 255);
    bl = Math.round(toSRGB(bl) * 255);

    r = Math.max(0, Math.min(255, r));
    g = Math.max(0, Math.min(255, g));
    bl = Math.max(0, Math.min(255, bl));

    return '#' + [r, g, bl].map(x => x.toString(16).padStart(2, '0')).join('');
}

function _applyTransform(oklch) {
    const t = transform;

    // Apply transforms
    let h = (oklch.h + t.hueShift + 360) % 360;
    let c = Math.max(0, Math.min(0.4, oklch.c * t.chromaScale));
    let l = Math.max(0, Math.min(1, oklch.l + t.lightnessShift / 100));

    // Apply amplifier to chroma for contrast
    if (t.amplifier !== 1) {
        c = Math.pow(c / 0.4, 1 / t.amplifier) * 0.4;
    }

    return _toHex({ h, c, l });
}

// =========================================================================
// CORE API
// =========================================================================

/**
 * Get color with transforms applied
 * @param {string} dimension - Palette dimension (tier, family, ring, layer, edgeType)
 * @param {string} category - Category within dimension
 * @returns {string} Hex color string
 */
function get(dimension, category) {
    const base = palette[dimension]?.[category];
    if (!base) return _toHex({ h: 0, c: 0.02, l: 0.40 }); // Fallback gray
    return _applyTransform(base);
}

/**
 * Get color for a numeric value using interval mapping
 * @param {string} intervalName - Interval name (markov, weight, confidence)
 * @param {number} value - Value (0-1)
 * @returns {string} Hex color string
 */
function getInterval(intervalName, value) {
    const interval = intervals[intervalName];
    if (!interval) return _toHex({ h: 0, c: 0.02, l: 0.40 });

    const stops = interval.stops;
    const v = Math.max(0, Math.min(1, value));

    // Find surrounding stops
    let lower = stops[0];
    let upper = stops[stops.length - 1];

    for (let i = 0; i < stops.length - 1; i++) {
        if (v >= stops[i].value && v <= stops[i + 1].value) {
            lower = stops[i];
            upper = stops[i + 1];
            break;
        }
    }

    // Interpolate between stops
    const range = upper.value - lower.value;
    const t = range > 0 ? (v - lower.value) / range : 0;

    const interpolated = {
        h: lower.h + (upper.h - lower.h) * t,
        c: lower.c + (upper.c - lower.c) * t,
        l: lower.l + (upper.l - lower.l) * t
    };

    return _applyTransform(interpolated);
}

/**
 * Interpolate between two hex colors in OKLCH space
 * @param {string} color1 - Hex color 1
 * @param {string} color2 - Hex color 2
 * @param {number} t - Interpolation factor (0-1)
 * @returns {string} Hex result
 */
function interpolate(color1, color2, t) {
    // We assume input hexes can be approximated back to OKLCH or treated as sRGB->OKLCH
    // For simplicity in this engine which mostly generates from OKLCH, we'll assume
    // specific OKLCH-derived palettes unless provided raw hex.
    // If we really need robust hex->oklch, we need a converter.
    // BUT, for edge gradients in app.js, we often have raw HSL or OKLCH objects.
    // Let's support passing Objects {h,c,l} or hex strings (naive interpolation for hex if needed).
    // Best approach: app.js should use COLOR.get() to get objects if possible, or we expose a helper
    // that takes our internal palette objects.

    // Actually, let's keep it simple: assume app.js will partial refactoring.
    // We will accept object {h,c,l} inputs for maximum precision.
    const c1 = (typeof color1 === 'string') ? parseOklchString(color1) || { h: 0, c: 0, l: 0.5 } : color1;
    const c2 = (typeof color2 === 'string') ? parseOklchString(color2) || { h: 0, c: 0, l: 0.5 } : color2;

    t = Math.max(0, Math.min(1, t));

    // Shortest path hue interpolation
    let h1 = c1.h || c1.H || 0;
    let h2 = c2.h || c2.H || 0;
    let dh = h2 - h1;
    if (Math.abs(dh) > 180) {
        if (dh > 0) h1 += 360;
        else h2 += 360;
    }

    const h = (h1 + (h2 - h1) * t) % 360;
    const c = (c1.c !== undefined ? c1.c : c1.C) + ((c2.c !== undefined ? c2.c : c2.C) - (c1.c !== undefined ? c1.c : c1.C)) * t;
    const l = (c1.l !== undefined ? c1.l : c1.L) + ((c2.l !== undefined ? c2.l : c2.L) - (c1.l !== undefined ? c1.l : c1.L)) * t;

    return _applyTransform({ h, c, l });
}

/**
 * Get raw OKLCH values (for advanced use)
 */
function getRaw(dimension, category) {
    return palette[dimension]?.[category] || { h: 0, c: 0.02, l: 0.40 };
}

/**
 * Get all categories for a dimension
 */
function getCategories(dimension) {
    return Object.keys(palette[dimension] || {});
}

/**
 * Get label for a category
 */
function getLabel(dimension, category) {
    return palette[dimension]?.[category]?.label || category;
}

// =========================================================================
// TRANSFORM CONTROLS
// =========================================================================

function setTransform(key, value) {
    if (key in transform) {
        transform[key] = value;
        _notifySubscribers('transform-change', { key, value });
    }
}

function setAllTransforms(transforms) {
    Object.assign(transform, transforms);
    _notifySubscribers('transform-change', transforms);
}

function resetTransforms() {
    transform.hueShift = 0;
    transform.chromaScale = 1.0;
    transform.lightnessShift = 0;
    transform.amplifier = 1.0;
    _notifySubscribers('transform-change', transform);
}

function getTransform() {
    return { ...transform };
}

// =========================================================================
// DEBUG
// =========================================================================

function debug() {
    console.log('[COLOR] Transform state:', transform);
    console.log('[COLOR] Palette dimensions:', Object.keys(palette));
    console.log('[COLOR] Interval mappings:', Object.keys(intervals));
}

// =========================================================================
// PUBLIC API
// =========================================================================

return {
    // Core API
    get,
    getInterval,
    getRaw,
    getCategories,
    getLabel,
    interpolate,

    // Transform controls
    setTransform,
    setAllTransforms,
    resetTransforms,
    getTransform,

    // Subscriptions
    subscribe,

    // Internal access (for migration)
    palette,
    intervals,
    transform,

    // Debug
    debug
};
}) ();

// Backward compatibility aliases - Using Object.defineProperty to avoid duplicate declarations
Object.defineProperty(window, 'ColorOrchestrator', { get: () => COLOR, configurable: true });
Object.defineProperty(window, 'Color', { get: () => COLOR, configurable: true });
