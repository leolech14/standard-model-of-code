/**
 * ═══════════════════════════════════════════════════════════════════════════
 * FLOW MODULE - Flow visualization mode with presets
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * Flow mode highlights high-entropy nodes and edge transition probabilities.
 * Cycles through visual presets (EMBER, OCEAN, PLASMA, MATRIX, PULSE, AURORA).
 * Depends on: Graph, DM, THEME_CONFIG, APPEARANCE_CONFIG, FLOW_CONFIG
 *
 * @module FLOW
 * @version 1.0.0
 */

window.FLOW = (function() {
    'use strict';

    // ═══════════════════════════════════════════════════════════════════════
    // PRESET COLOR/VALUE HELPERS
    // ═══════════════════════════════════════════════════════════════════════

    function getFlowPresetColor(presetName, property, fallback) {
        const schemes = (window.THEME_CONFIG && window.THEME_CONFIG.colors && window.THEME_CONFIG.colors.schemes) || {};
        const scheme = schemes[presetName.toLowerCase()] || {};
        return scheme[property] || fallback;
    }

    function getFlowPresetValue(presetName, property, fallback) {
        const presets = (typeof window.APPEARANCE_CONFIG !== 'undefined' && window.APPEARANCE_CONFIG && window.APPEARANCE_CONFIG['flow-presets']) || {};
        const preset = presets[presetName.toLowerCase()] || {};
        const value = preset[property];
        return (value !== undefined && value !== null) ? value : fallback;
    }

    // ═══════════════════════════════════════════════════════════════════════
    // FLOW PRESETS
    // ═══════════════════════════════════════════════════════════════════════

    const PRESETS = [
        {
            name: 'EMBER',
            highlightColor: getFlowPresetColor('EMBER', 'highlightColor', getFlowPresetValue('ember', 'highlightColor', '#ff8c00')),
            particleColor: getFlowPresetColor('EMBER', 'particleColor', getFlowPresetValue('ember', 'particleColor', '#ffaa00')),
            dimColor: getFlowPresetColor('EMBER', 'dimColor', getFlowPresetValue('ember', 'dimColor', '#331100')),
            edgeColor: getFlowPresetColor('EMBER', 'edgeColor', getFlowPresetValue('ember', 'edgeColor', '#ff6600')),
            particleCount: getFlowPresetValue('ember', 'particleCount', 3),
            particleWidth: getFlowPresetValue('ember', 'particleWidth', 2.5),
            particleSpeed: getFlowPresetValue('ember', 'particleSpeed', 0.008),
            edgeWidthScale: getFlowPresetValue('ember', 'edgeWidthScale', 3.0),
            sizeMultiplier: getFlowPresetValue('ember', 'sizeMultiplier', 1.8),
            edgeOpacityMin: getFlowPresetValue('ember', 'edgeOpacityMin', 0.3),
            dimOpacity: getFlowPresetValue('ember', 'dimOpacity', 0.05)
        },
        {
            name: 'OCEAN',
            highlightColor: getFlowPresetColor('OCEAN', 'highlightColor', getFlowPresetValue('ocean', 'highlightColor', '#00d4ff')),
            particleColor: getFlowPresetColor('OCEAN', 'particleColor', getFlowPresetValue('ocean', 'particleColor', '#4df0ff')),
            dimColor: getFlowPresetColor('OCEAN', 'dimColor', getFlowPresetValue('ocean', 'dimColor', '#001122')),
            edgeColor: getFlowPresetColor('OCEAN', 'edgeColor', getFlowPresetValue('ocean', 'edgeColor', '#0088cc')),
            particleCount: getFlowPresetValue('ocean', 'particleCount', 4),
            particleWidth: getFlowPresetValue('ocean', 'particleWidth', 2.0),
            particleSpeed: getFlowPresetValue('ocean', 'particleSpeed', 0.006),
            edgeWidthScale: getFlowPresetValue('ocean', 'edgeWidthScale', 2.5),
            sizeMultiplier: getFlowPresetValue('ocean', 'sizeMultiplier', 1.6),
            edgeOpacityMin: getFlowPresetValue('ocean', 'edgeOpacityMin', 0.25),
            dimOpacity: getFlowPresetValue('ocean', 'dimOpacity', 0.03)
        },
        {
            name: 'PLASMA',
            highlightColor: getFlowPresetColor('PLASMA', 'highlightColor', getFlowPresetValue('plasma', 'highlightColor', '#ff00ff')),
            particleColor: getFlowPresetColor('PLASMA', 'particleColor', getFlowPresetValue('plasma', 'particleColor', '#ff66ff')),
            dimColor: getFlowPresetColor('PLASMA', 'dimColor', getFlowPresetValue('plasma', 'dimColor', '#110011')),
            edgeColor: getFlowPresetColor('PLASMA', 'edgeColor', getFlowPresetValue('plasma', 'edgeColor', '#cc00cc')),
            particleCount: getFlowPresetValue('plasma', 'particleCount', 5),
            particleWidth: getFlowPresetValue('plasma', 'particleWidth', 3.0),
            particleSpeed: getFlowPresetValue('plasma', 'particleSpeed', 0.012),
            edgeWidthScale: getFlowPresetValue('plasma', 'edgeWidthScale', 4.0),
            sizeMultiplier: getFlowPresetValue('plasma', 'sizeMultiplier', 2.0),
            edgeOpacityMin: getFlowPresetValue('plasma', 'edgeOpacityMin', 0.35),
            dimOpacity: getFlowPresetValue('plasma', 'dimOpacity', 0.04)
        },
        {
            name: 'MATRIX',
            highlightColor: getFlowPresetColor('MATRIX', 'highlightColor', getFlowPresetValue('matrix', 'highlightColor', '#00ff00')),
            particleColor: getFlowPresetColor('MATRIX', 'particleColor', getFlowPresetValue('matrix', 'particleColor', '#88ff88')),
            dimColor: getFlowPresetColor('MATRIX', 'dimColor', getFlowPresetValue('matrix', 'dimColor', '#001100')),
            edgeColor: getFlowPresetColor('MATRIX', 'edgeColor', getFlowPresetValue('matrix', 'edgeColor', '#00cc00')),
            particleCount: getFlowPresetValue('matrix', 'particleCount', 6),
            particleWidth: getFlowPresetValue('matrix', 'particleWidth', 1.5),
            particleSpeed: getFlowPresetValue('matrix', 'particleSpeed', 0.015),
            edgeWidthScale: getFlowPresetValue('matrix', 'edgeWidthScale', 2.0),
            sizeMultiplier: getFlowPresetValue('matrix', 'sizeMultiplier', 1.4),
            edgeOpacityMin: getFlowPresetValue('matrix', 'edgeOpacityMin', 0.2),
            dimOpacity: getFlowPresetValue('matrix', 'dimOpacity', 0.02)
        },
        {
            name: 'PULSE',
            highlightColor: getFlowPresetColor('PULSE', 'highlightColor', getFlowPresetValue('pulse', 'highlightColor', '#ff4444')),
            particleColor: getFlowPresetColor('PULSE', 'particleColor', getFlowPresetValue('pulse', 'particleColor', '#ff8888')),
            dimColor: getFlowPresetColor('PULSE', 'dimColor', getFlowPresetValue('pulse', 'dimColor', '#110000')),
            edgeColor: getFlowPresetColor('PULSE', 'edgeColor', getFlowPresetValue('pulse', 'edgeColor', '#cc2222')),
            particleCount: getFlowPresetValue('pulse', 'particleCount', 2),
            particleWidth: getFlowPresetValue('pulse', 'particleWidth', 4.0),
            particleSpeed: getFlowPresetValue('pulse', 'particleSpeed', 0.004),
            edgeWidthScale: getFlowPresetValue('pulse', 'edgeWidthScale', 5.0),
            sizeMultiplier: getFlowPresetValue('pulse', 'sizeMultiplier', 2.2),
            edgeOpacityMin: getFlowPresetValue('pulse', 'edgeOpacityMin', 0.4),
            dimOpacity: getFlowPresetValue('pulse', 'dimOpacity', 0.06)
        },
        {
            name: 'AURORA',
            highlightColor: getFlowPresetColor('AURORA', 'highlightColor', getFlowPresetValue('aurora', 'highlightColor', '#33ccbb')),
            particleColor: getFlowPresetColor('AURORA', 'particleColor', getFlowPresetValue('aurora', 'particleColor', '#66ffee')),
            dimColor: getFlowPresetColor('AURORA', 'dimColor', getFlowPresetValue('aurora', 'dimColor', '#002222')),
            edgeColor: getFlowPresetColor('AURORA', 'edgeColor', getFlowPresetValue('aurora', 'edgeColor', '#22aa99')),
            particleCount: getFlowPresetValue('aurora', 'particleCount', 4),
            particleWidth: getFlowPresetValue('aurora', 'particleWidth', 2.2),
            particleSpeed: getFlowPresetValue('aurora', 'particleSpeed', 0.007),
            edgeWidthScale: getFlowPresetValue('aurora', 'edgeWidthScale', 3.5),
            sizeMultiplier: getFlowPresetValue('aurora', 'sizeMultiplier', 1.7),
            edgeOpacityMin: getFlowPresetValue('aurora', 'edgeOpacityMin', 0.28),
            dimOpacity: getFlowPresetValue('aurora', 'dimOpacity', 0.04)
        }
    ];

    let currentPresetIndex = 0;

    // ═══════════════════════════════════════════════════════════════════════
    // TOGGLE FLOW MODE
    // ═══════════════════════════════════════════════════════════════════════

    function toggle() {
        const flowMode = window.flowMode;

        // If already in flow mode, cycle to next preset
        if (flowMode) {
            currentPresetIndex = (currentPresetIndex + 1) % PRESETS.length;
            const preset = PRESETS[currentPresetIndex];
            console.log(`[Flow] Cycling to preset: ${preset.name}`);
            applyVisualization();
            window.showModeToast(`FLOW: ${preset.name}`);
            return;
        }

        window.flowMode = true;
        currentPresetIndex = 0;
        console.log('[Flow] Toggled to:', window.flowMode);

        // Sync BOTH potential buttons (Dock vs CommandBar)
        const btnDock = document.getElementById('btn-flow');
        if (btnDock) btnDock.classList.toggle('active', window.flowMode);

        const btnCmd = document.getElementById('cmd-flow2');
        if (btnCmd) btnCmd.classList.toggle('active', window.flowMode);

        // Show/hide flow legend
        const legend = document.getElementById('flow-legend');
        if (legend) legend.classList.toggle('visible', window.flowMode);

        // EXCLUSIVE MODE: Clear other visual noise
        if (typeof window.clearAllFileModes === 'function') {
            window.clearAllFileModes();
        }
        // Ensure standard file/hull buttons are off
        document.querySelectorAll('.file-mode-btn').forEach(b => b.classList.remove('active'));

        applyVisualization();
        const preset = PRESETS[currentPresetIndex];
        window.showModeToast(`FLOW: ${preset.name}`);
    }

    // ═══════════════════════════════════════════════════════════════════════
    // DISABLE FLOW MODE
    // ═══════════════════════════════════════════════════════════════════════

    function disable() {
        if (!window.flowMode) return;
        window.flowMode = false;
        currentPresetIndex = 0;

        const btnDock = document.getElementById('btn-flow');
        if (btnDock) btnDock.classList.remove('active');

        const btnCmd = document.getElementById('cmd-flow2');
        if (btnCmd) btnCmd.classList.remove('active');

        const legend = document.getElementById('flow-legend');
        if (legend) legend.classList.remove('visible');

        clearVisualization();
        window.showModeToast('Flow mode off');
    }

    // ═══════════════════════════════════════════════════════════════════════
    // APPLY FLOW VISUALIZATION
    // ═══════════════════════════════════════════════════════════════════════

    function applyVisualization() {
        const Graph = window.Graph;
        const DM = window.DM;

        // Guard: Ensure Graph is ready
        if (!Graph || !DM) {
            console.warn('[Flow] Graph or DM not ready');
            return;
        }

        // Get current preset settings
        const preset = PRESETS[currentPresetIndex];
        const markov = DM.getMarkov ? DM.getMarkov() : {};
        const highEntropy = markov.high_entropy_nodes || [];

        // Use preset values (fallback to FLOW_CONFIG for topK/minWeight if not in preset)
        const flowCfg = window.FLOW_CONFIG || {};
        const highlightColor = preset.highlightColor;
        const particleColor = preset.particleColor;
        const sizeMult = preset.sizeMultiplier;
        const edgeScale = preset.edgeWidthScale;
        const particleCount = preset.particleCount;
        const particleWidth = preset.particleWidth;
        const particleSpeed = preset.particleSpeed;
        const edgeOpacityMin = preset.edgeOpacityMin;
        const dimOpacity = preset.dimOpacity;
        const topK = flowCfg.topKEdges || 3;
        const minWeight = flowCfg.minWeight || 0.01;

        // Build set of high entropy node names
        const highEntropyNodes = window.highEntropyNodes || new Set();
        highEntropyNodes.clear();
        highEntropy.forEach(n => highEntropyNodes.add(n.node));
        window.highEntropyNodes = highEntropyNodes;

        const graphNodes = Graph.graphData().nodes;
        const graphLinks = Graph.graphData().links;

        // THRESHOLDING: Build a map of top-K outgoing edges per source node
        const edgesBySource = new Map();
        graphLinks.forEach(link => {
            const srcId = typeof link.source === 'object' ? link.source.id : link.source;
            if (!edgesBySource.has(srcId)) {
                edgesBySource.set(srcId, []);
            }
            edgesBySource.get(srcId).push(link);
        });

        // For each source, keep only top-K by markov_weight (transition probability)
        const visibleEdges = new Set();
        edgesBySource.forEach((edges, srcId) => {
            const sorted = edges
                .filter(e => (e.markov_weight || 0) >= minWeight)
                .sort((a, b) => (b.markov_weight || 0) - (a.markov_weight || 0))
                .slice(0, topK);
            sorted.forEach(e => visibleEdges.add(e));
        });

        // Store original colors and sizes, then apply flow coloring
        const originalNodeColors = window.originalNodeColors || new Map();
        window.originalNodeColors = originalNodeColors;

        graphNodes.forEach(node => {
            if (!originalNodeColors.has(node.id)) {
                originalNodeColors.set(node.id, node.color);
            }
            // Restore original size first (in case switching presets)
            if (node._originalVal) {
                node.val = node._originalVal;
            } else {
                node._originalVal = node.val || 1;
            }
            // High entropy nodes highlighted (decision points)
            if (highEntropyNodes.has(node.name)) {
                node.color = highlightColor;
                node.val = node._originalVal * sizeMult;
            }
        });

        // Update link widths based on markov_weight (with amplification)
        const maxMarkov = Math.max(0.001, ...graphLinks.map(l => l.markov_weight || 0));
        const amplify = window.amplify || (x => x);

        Graph.linkWidth(link => {
            if (!visibleEdges.has(link)) return 0.1;
            const mw = link.markov_weight || 0;
            const normalized = mw / maxMarkov;
            const amplified = amplify(normalized);
            return 0.5 + amplified * edgeScale * 2;
        });

        // Update link opacity to emphasize important edges
        Graph.linkOpacity(link => {
            if (!visibleEdges.has(link)) return dimOpacity;
            const mw = link.markov_weight || 0;
            const normalized = mw / maxMarkov;
            const amplified = amplify(normalized);
            return edgeOpacityMin + amplified * (1.0 - edgeOpacityMin);
        });

        // Add directional particles only on visible edges
        Graph.linkDirectionalParticles(link => {
            if (!visibleEdges.has(link)) return 0;
            return particleCount;
        });
        Graph.linkDirectionalParticleWidth(particleWidth);
        Graph.linkDirectionalParticleSpeed(particleSpeed);
        Graph.linkDirectionalParticleColor(() => particleColor);

        // Update node coloring
        const toColorNumber = window.toColorNumber || (c => c);
        Graph.nodeColor(n => toColorNumber(n.color, '#888888'));

        if (typeof window.updateSelectionVisuals === 'function') {
            window.updateSelectionVisuals();
        }

        // Debug: count edges with markov weights
        const edgesWithMarkov = graphLinks.filter(l => l.markov_weight > 0).length;
        console.log(`[Flow] Preset: ${preset.name} | ${highEntropyNodes.size} high entropy nodes, ${visibleEdges.size} visible edges (top-${topK}), ${edgesWithMarkov}/${graphLinks.length} edges with markov`);
    }

    // ═══════════════════════════════════════════════════════════════════════
    // CLEAR FLOW VISUALIZATION
    // ═══════════════════════════════════════════════════════════════════════

    function clearVisualization() {
        const Graph = window.Graph;

        // Guard: Ensure Graph is ready
        if (!Graph) return;

        const graphNodes = Graph.graphData().nodes;
        const originalNodeColors = window.originalNodeColors || new Map();

        // Restore original node colors and sizes
        graphNodes.forEach(node => {
            if (originalNodeColors.has(node.id)) {
                node.color = originalNodeColors.get(node.id);
            }
            // Restore original size from saved value
            if (node._originalVal) {
                node.val = node._originalVal;
                delete node._originalVal;
            }
        });

        // Reset link widths
        Graph.linkWidth(1);

        // Reset link opacity
        Graph.linkOpacity(0.6);

        // Remove directional particles
        Graph.linkDirectionalParticles(0);

        // Update coloring
        const toColorNumber = window.toColorNumber || (c => c);
        Graph.nodeColor(n => toColorNumber(n.color, '#888888'));

        const highEntropyNodes = window.highEntropyNodes || new Set();
        highEntropyNodes.clear();

        if (typeof window.applyEdgeMode === 'function') {
            window.applyEdgeMode();
        }
        if (typeof window.updateSelectionVisuals === 'function') {
            window.updateSelectionVisuals();
        }
    }

    // ═══════════════════════════════════════════════════════════════════════
    // MODULE EXPORT
    // ═══════════════════════════════════════════════════════════════════════

    return {
        getPresetColor: getFlowPresetColor,
        getPresetValue: getFlowPresetValue,
        toggle: toggle,
        disable: disable,
        apply: applyVisualization,
        clear: clearVisualization,
        PRESETS: PRESETS,
        getCurrentPreset: () => PRESETS[currentPresetIndex],
        getCurrentPresetIndex: () => currentPresetIndex
    };
})();

// ═══════════════════════════════════════════════════════════════════════════
// BACKWARD COMPATIBILITY SHIMS
// ═══════════════════════════════════════════════════════════════════════════

window.getFlowPresetColor = FLOW.getPresetColor;
window.getFlowPresetValue = FLOW.getPresetValue;
window.toggleFlowMode = FLOW.toggle;
window.disableFlowMode = FLOW.disable;
window.applyFlowVisualization = FLOW.apply;
window.clearFlowVisualization = FLOW.clear;
window.FLOW_PRESETS = FLOW.PRESETS;

console.log('[Module] FLOW loaded - 6 functions');
