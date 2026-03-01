/**
 * THEORY MODULE - Standard Model of Code Theory Constants
 *
 * Pure data representing the Standard Model topology.
 * No dependencies. This is the canonical source of truth.
 *
 * @module THEORY
 * @version 1.0.0
 */

window.THEORY = (function() {
    'use strict';

    // =========================================================================
    // THE 16 ABSTRACTION LEVELS (vertical axis: L-3 to L12)
    // =========================================================================

    const SCALE_16_LEVELS = {
        // COSMOLOGICAL (L8-L12) - Beyond scope, shown as outer haze
        'L12': { name: 'UNIVERSE', symbol: '🌐', zone: 'COSMOLOGICAL', y: 1.4, color: { h: 260, s: 30, l: 25 } },
        'L11': { name: 'DOMAIN', symbol: '🏛️', zone: 'COSMOLOGICAL', y: 1.3, color: { h: 250, s: 35, l: 30 } },
        'L10': { name: 'ORGANIZATION', symbol: '🏢', zone: 'COSMOLOGICAL', y: 1.2, color: { h: 240, s: 40, l: 35 } },
        'L9': { name: 'PLATFORM', symbol: '☁️', zone: 'COSMOLOGICAL', y: 1.1, color: { h: 230, s: 45, l: 40 } },
        'L8': { name: 'ECOSYSTEM', symbol: '🔗', zone: 'COSMOLOGICAL', y: 1.0, color: { h: 220, s: 50, l: 45 } },
        // ARCHITECTURAL (L4-L7) - Primary visible zone (teal - virtual depths)
        'L7': { name: 'SYSTEM', symbol: '⬡', zone: 'ARCHITECTURAL', y: 0.7, color: { h: 175, s: 60, l: 52 } },
        'L6': { name: 'PACKAGE', symbol: '📦', zone: 'ARCHITECTURAL', y: 0.5, color: { h: 178, s: 62, l: 48 } },
        'L5': { name: 'FILE', symbol: '📄', zone: 'ARCHITECTURAL', y: 0.3, color: { h: 180, s: 65, l: 44 } },
        'L4': { name: 'CONTAINER', symbol: '⬢', zone: 'ARCHITECTURAL', y: 0.1, color: { h: 182, s: 68, l: 40 } },
        // SEMANTIC (L1-L3) - The operational core (silver/white - surface light)
        'L3': { name: 'NODE', symbol: '★', zone: 'SEMANTIC', y: -0.1, color: { h: 210, s: 25, l: 92 } },  // Brightest - fundamental unit
        'L2': { name: 'BLOCK', symbol: '▣', zone: 'SEMANTIC', y: -0.3, color: { h: 210, s: 30, l: 85 } },
        'L1': { name: 'STATEMENT', symbol: '─', zone: 'SEMANTIC', y: -0.5, color: { h: 210, s: 35, l: 78 } },
        // SYNTACTIC (L0) - The event horizon between meaning and data
        'L0': { name: 'TOKEN', symbol: '·', zone: 'SYNTACTIC', y: -0.7, color: { h: 60, s: 90, l: 55 } },  // Bright yellow - event horizon
        // PHYSICAL (L-1 to L-3) - The substrate (deep blue - ocean floor)
        'L-1': { name: 'CHARACTER', symbol: 'a', zone: 'PHYSICAL', y: -0.9, color: { h: 220, s: 70, l: 42 } },
        'L-2': { name: 'BYTE', symbol: '01', zone: 'PHYSICAL', y: -1.1, color: { h: 220, s: 75, l: 35 } },
        'L-3': { name: 'BIT/QUBIT', symbol: '⚡', zone: 'PHYSICAL', y: -1.3, color: { h: 220, s: 80, l: 28 } }  // Deepest
    };

    // =========================================================================
    // THE THREE PARALLEL LAYERS (shells around the structure)
    // =========================================================================

    const THREE_LAYERS = {
        'PHYSICAL': { order: 0, radius: 1.8, opacity: 0.15, color: { h: 220, s: 75, l: 35 }, description: 'Hardware, bits, memory, I/O' },
        'VIRTUAL': { order: 1, radius: 1.4, opacity: 0.25, color: { h: 175, s: 65, l: 45 }, description: 'Code, structures, algorithms' },
        'SEMANTIC': { order: 2, radius: 1.0, opacity: 0.35, color: { h: 210, s: 30, l: 88 }, description: 'Meaning, business logic, intent' }
    };

    // =========================================================================
    // STANDARD MODEL THEORY CONTENT - Semantic descriptions for tooltips
    // =========================================================================

    const SMC_THEORY = {
        // THE THREE FUNDAMENTAL LAYERS
        layers: {
            'PHYSICAL': {
                icon: '⚡',
                title: 'Physical Layer',
                subtitle: 'The Substrate',
                body: 'The hardware reality: electrons, circuits, memory cells. Everything that exists in physical space-time.',
                theory: '"Matter is the canvas upon which computation paints its patterns."',
                examples: ['CPU registers', 'RAM cells', 'disk sectors', 'network signals']
            },
            'VIRTUAL': {
                icon: '💠',
                title: 'Virtual Layer',
                subtitle: 'The Structure',
                body: 'Pure information structures: code, data, algorithms. The mathematical forms that live in computational space.',
                theory: '"Between the physical and the meaningful lies the virtual — pure form without matter or purpose."',
                examples: ['variables', 'functions', 'classes', 'data structures']
            },
            'SEMANTIC': {
                icon: '🎯',
                title: 'Semantic Layer',
                subtitle: 'The Meaning',
                body: 'Intent and purpose: business logic, user goals, system behavior. The "why" behind the code.',
                theory: '"Semantics is where computation meets human intention — the bridge between bits and understanding."',
                examples: ['user stories', 'business rules', 'API contracts', 'domain models']
            }
        },

        // ATOM FAMILIES
        families: {
            'LOG': {
                icon: '📊',
                title: 'Logic Family',
                subtitle: 'The Reasoners',
                body: 'Elements that transform data through computation: conditionals, loops, calculations.',
                theory: '"Logic atoms are the decision-makers — they take inputs and produce outputs through transformation."',
                examples: ['if/else', 'for loops', 'calculations', 'validators']
            },
            'DAT': {
                icon: '📦',
                title: 'Data Family',
                subtitle: 'The Containers',
                body: 'Elements that hold and organize information: variables, structures, databases.',
                theory: '"Data atoms store state — they are the nouns in the grammar of code."',
                examples: ['variables', 'arrays', 'objects', 'databases']
            },
            'ORG': {
                icon: '🏗️',
                title: 'Organization Family',
                subtitle: 'The Architects',
                body: 'Elements that structure code: modules, classes, packages. They create boundaries.',
                theory: '"Organization atoms create order from chaos — the folders in the file system of abstraction."',
                examples: ['modules', 'classes', 'packages', 'namespaces']
            },
            'EXE': {
                icon: '⚙️',
                title: 'Execution Family',
                subtitle: 'The Doers',
                body: 'Elements that perform actions: function calls, I/O, system operations.',
                theory: '"Execution atoms are the verbs — where potential becomes actual."',
                examples: ['function calls', 'API requests', 'file writes', 'renders']
            },
            'EXT': {
                icon: '🔌',
                title: 'External Family',
                subtitle: 'The Connectors',
                body: 'Elements that interface with the outside: APIs, imports, system calls.',
                theory: '"External atoms are portals — they connect isolated systems into larger ecosystems."',
                examples: ['imports', 'API calls', 'env vars', 'dependencies']
            }
        },

        // TIERS
        tiers: {
            'T0': {
                icon: '🔬',
                title: 'Tier 0 — Foundation',
                subtitle: 'Low-level primitives',
                body: 'The atomic building blocks: individual statements, expressions, basic operations.',
                theory: '"T0 is where code meets silicon — the ground floor of abstraction."',
                examples: ['assignments', 'operators', 'literals', 'basic types']
            },
            'T1': {
                icon: '🔧',
                title: 'Tier 1 — Components',
                subtitle: 'Functional units',
                body: 'Grouped functionality: functions, methods, small modules.',
                theory: '"T1 is the sweet spot — complex enough to be useful, simple enough to understand."',
                examples: ['functions', 'methods', 'handlers', 'utilities']
            },
            'T2': {
                icon: '🏛️',
                title: 'Tier 2 — Architecture',
                subtitle: 'System structure',
                body: 'High-level organization: classes, modules, services. The skeleton of the codebase.',
                theory: '"T2 defines the shape of software — patterns emerge that echo through every line."',
                examples: ['classes', 'modules', 'services', 'controllers']
            }
        },

        // SPECIAL ELEMENTS
        special: {
            'core': {
                icon: '✨',
                title: 'The Nexus',
                subtitle: 'Singularity Point',
                body: 'The center of the topology: where all paths converge.',
                theory: '"Every codebase has a heart — the central modules that everything depends upon."',
                examples: ['main.js', 'app.py', 'index.ts', 'core.rs']
            },
            'elevator': {
                icon: '🚀',
                title: 'Data Elevator',
                subtitle: 'Cross-tier Highway',
                body: 'Vertical connections that move data between abstraction levels.',
                theory: '"Elevators are the call stacks of architecture."',
                examples: ['API layers', 'ORMs', 'serializers', 'adapters']
            },
            'hub-star': {
                icon: '⭐',
                title: 'Hub Node',
                subtitle: 'High-connectivity Center',
                body: 'A node with many incoming connections. Often a critical dependency.',
                theory: '"Hubs are the load-bearing walls — remove them and everything collapses."',
                examples: ['utils', 'config', 'logger', 'database']
            }
        }
    };

    // =========================================================================
    // LEVEL ZONES - Which levels belong to which visual band
    // =========================================================================

    const LEVEL_ZONES = {
        'COSMOLOGICAL': { levels: ['L12', 'L11', 'L10', 'L9', 'L8'], opacity: 0.2, blur: true },
        'ARCHITECTURAL': { levels: ['L7', 'L6', 'L5', 'L4'], opacity: 0.6, blur: false },
        'SEMANTIC': { levels: ['L3', 'L2', 'L1'], opacity: 1.0, blur: false },        // Primary focus
        'SYNTACTIC': { levels: ['L0'], opacity: 0.8, blur: false },                   // Event horizon
        'PHYSICAL': { levels: ['L-1', 'L-2', 'L-3'], opacity: 0.4, blur: true }
    };

    // =========================================================================
    // VISUALIZATION PRESETS - Different ways to see the topology
    // =========================================================================

    const VIS_PRESETS = {
        'tier': {
            name: 'By Tier (T0/T1/T2)',
            description: 'Core → Architecture → External',
            colorBy: 'tier',
            sizeBy: 'fanout',
            edgeBy: 'type'
        },
        'family': {
            name: 'By Atom Family',
            description: 'LOG, DAT, ORG, EXE, EXT',
            colorBy: 'family',
            sizeBy: 'fanout',
            edgeBy: 'type'
        },
        'layer': {
            name: 'By Layer',
            description: 'Physical → Virtual → Semantic',
            colorBy: 'layer',
            sizeBy: 'uniform',
            edgeBy: 'resolution'
        },
        'ring': {
            name: 'By Ring (Domain)',
            description: 'Domain architecture layers',
            colorBy: 'ring',
            sizeBy: 'fanout',
            edgeBy: 'type'
        },
        'file': {
            name: 'By File',
            description: 'Each file gets unique hue',
            colorBy: 'file',
            sizeBy: 'uniform',
            edgeBy: 'resolution'
        },
        'flow': {
            name: 'Markov Flow',
            description: 'Edge width = transition probability',
            colorBy: 'tier',
            sizeBy: 'entropy',
            edgeBy: 'weight'
        },
        'depth': {
            name: 'By Depth (Call Distance)',
            description: 'Distance from entry points',
            colorBy: 'depth',
            sizeBy: 'fanout',
            edgeBy: 'type'
        }
        // NOTE: Color schemes (viridis, plasma, thermal, etc.) are now in color-engine.js schemePaths
        // Access via COLOR.listSchemes(), COLOR.applyScheme(), COLOR.getSchemeColor()
    };

    // =========================================================================
    // PUBLIC API
    // =========================================================================

    return {
        SCALE_16_LEVELS,
        THREE_LAYERS,
        SMC_THEORY,
        LEVEL_ZONES,
        VIS_PRESETS,

        // Convenience getters
        getLevel: (id) => SCALE_16_LEVELS[id],
        getLayer: (id) => THREE_LAYERS[id],
        getZone: (id) => LEVEL_ZONES[id],
        getPreset: (id) => VIS_PRESETS[id],

        // Theory content accessors (for tooltips)
        getTheoryContent: (category, key) => SMC_THEORY[category]?.[key],
        getLayerTheory: (key) => SMC_THEORY.layers[key],
        getFamilyTheory: (key) => SMC_THEORY.families[key],
        getTierTheory: (key) => SMC_THEORY.tiers[key],
        getSpecialTheory: (key) => SMC_THEORY.special[key]
    };
})();

// =========================================================================
// BACKWARD COMPATIBILITY SHIMS
// =========================================================================

window.SCALE_16_LEVELS = THEORY.SCALE_16_LEVELS;
window.THREE_LAYERS = THEORY.THREE_LAYERS;
window.SMC_THEORY = THEORY.SMC_THEORY;
window.LEVEL_ZONES = THEORY.LEVEL_ZONES;
window.VIS_PRESETS = THEORY.VIS_PRESETS;

console.log('[Module] THEORY loaded - 5 constants, 8 accessors');
