/**
 * PANEL HANDLERS MODULE
 *
 * Binds panel controls to their respective functionality.
 * Connects the new Gridstack-based panel controls to existing state modules.
 *
 * @module PANEL_HANDLERS
 *
 * Usage:
 *   PANEL_HANDLERS.init()  // Initialize all panel bindings
 */

window.PANEL_HANDLERS = (function() {
    'use strict';

    let _bound = false;

    // =========================================================================
    // INITIALIZATION
    // =========================================================================

    function init() {
        if (_bound) return;
        _bound = true;

        _bindFilterControls();
        _bindSelectionControls();
        _bindCameraControls();
        _bindAccessibilityControls();
        _bindExportControls();
        _bindLayoutControls();
        _bindViewModeControls();
        _bindNodeAppearanceControls();
        _bindEdgeAppearanceControls();
        _bindPanelSettings();
        _bindAnalysisUpdates();

        console.log('[PANEL_HANDLERS] Panel controls bound');
    }

    // =========================================================================
    // FILTER CONTROLS
    // =========================================================================

    function _bindFilterControls() {
        // Search input
        const searchInput = document.getElementById('panel-search-nodes');
        if (searchInput) {
            searchInput.addEventListener('input', _debounce(() => {
                if (typeof FILTER_STATE !== 'undefined') {
                    FILTER_STATE.setSearch(searchInput.value);
                }
            }, 150));
        }

        // Hide orphans toggle
        _bindPanelToggle('panel-toggle-orphans', (active) => {
            if (typeof FILTER_STATE !== 'undefined') {
                FILTER_STATE.setHideOrphans(active);
            }
        });

        // Hide dead code toggle
        _bindPanelToggle('panel-toggle-dead', (active) => {
            if (typeof FILTER_STATE !== 'undefined') {
                FILTER_STATE.setHideDeadCode(active);
            }
        });

        // Min degree slider
        _bindPanelSlider('panel-filter-degree', 'panel-filter-degree-num', (val) => {
            if (typeof FILTER_STATE !== 'undefined') {
                FILTER_STATE.setMinDegree(parseInt(val));
            }
        });
    }

    // =========================================================================
    // SELECTION CONTROLS
    // =========================================================================

    function _bindSelectionControls() {
        // Selection mode buttons
        document.querySelectorAll('[data-selection-mode]').forEach(btn => {
            btn.addEventListener('click', () => {
                const mode = btn.dataset.selectionMode;
                // Update button states
                document.querySelectorAll('[data-selection-mode]').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');

                if (typeof SELECT !== 'undefined' && SELECT.setMode) {
                    SELECT.setMode(mode);
                }
            });
        });

        // K-hop slider
        _bindPanelSlider('panel-khop', 'panel-khop-num', () => {
            // Value stored for expand operation
        });

        // Expand button
        document.getElementById('panel-select-expand')?.addEventListener('click', () => {
            const kHop = parseInt(document.getElementById('panel-khop')?.value || '1');
            if (typeof SELECT !== 'undefined' && SELECT.expandToNeighbors) {
                SELECT.expandToNeighbors(kHop);
            } else if (typeof Graph !== 'undefined') {
                // Fallback: expand selection to neighbors
                _expandSelectionToNeighbors(kHop);
            }
        });

        // Isolate button
        document.getElementById('panel-select-isolate')?.addEventListener('click', () => {
            if (typeof SELECT !== 'undefined' && SELECT.isolate) {
                SELECT.isolate();
            }
        });
    }

    function _expandSelectionToNeighbors(kHop) {
        // Basic k-hop expansion using graph data
        if (typeof Graph === 'undefined' || !Graph.graphData) return;

        const data = Graph.graphData();
        const selectedIds = new Set(window.selectedNodes?.map(n => n.id) || []);
        if (selectedIds.size === 0) return;

        // Build adjacency
        const neighbors = new Map();
        data.links.forEach(link => {
            const srcId = typeof link.source === 'object' ? link.source.id : link.source;
            const tgtId = typeof link.target === 'object' ? link.target.id : link.target;
            if (!neighbors.has(srcId)) neighbors.set(srcId, new Set());
            if (!neighbors.has(tgtId)) neighbors.set(tgtId, new Set());
            neighbors.get(srcId).add(tgtId);
            neighbors.get(tgtId).add(srcId);
        });

        // BFS expansion
        let frontier = new Set(selectedIds);
        for (let k = 0; k < kHop; k++) {
            const nextFrontier = new Set();
            frontier.forEach(id => {
                (neighbors.get(id) || []).forEach(nid => {
                    if (!selectedIds.has(nid)) {
                        selectedIds.add(nid);
                        nextFrontier.add(nid);
                    }
                });
            });
            frontier = nextFrontier;
        }

        // Update selection
        window.selectedNodes = data.nodes.filter(n => selectedIds.has(n.id));
        if (typeof REFRESH !== 'undefined') REFRESH.throttled();
    }

    // =========================================================================
    // CAMERA CONTROLS
    // =========================================================================

    function _bindCameraControls() {
        // Auto-rotate toggle
        _bindPanelToggle('panel-auto-rotate', (active) => {
            if (typeof Graph !== 'undefined' && Graph.controls) {
                Graph.controls().autoRotate = active;
            }
        });

        // Rotate speed slider
        _bindPanelSlider('panel-rotate-speed', 'panel-rotate-speed-num', (val) => {
            if (typeof Graph !== 'undefined' && Graph.controls) {
                Graph.controls().autoRotateSpeed = parseFloat(val);
            }
        });

        // Reset camera
        document.getElementById('panel-cam-reset')?.addEventListener('click', () => {
            if (typeof Graph !== 'undefined') {
                Graph.cameraPosition({ x: 0, y: 0, z: 500 }, { x: 0, y: 0, z: 0 }, 1000);
            }
        });

        // Fit all nodes
        document.getElementById('panel-cam-fit')?.addEventListener('click', () => {
            if (typeof Graph !== 'undefined' && Graph.zoomToFit) {
                Graph.zoomToFit(1000, 50);
            }
        });
    }

    // =========================================================================
    // ACCESSIBILITY CONTROLS
    // =========================================================================

    function _bindAccessibilityControls() {
        // Colorblind mode select
        const colorblindSelect = document.getElementById('panel-colorblind');
        if (colorblindSelect) {
            colorblindSelect.addEventListener('change', () => {
                const mode = colorblindSelect.value;
                document.body.dataset.colorblindMode = mode;
                // Apply colorblind-safe palette if available
                if (typeof COLOR !== 'undefined' && COLOR.setColorblindMode) {
                    COLOR.setColorblindMode(mode);
                }
            });
        }

        // High contrast toggle
        _bindPanelToggle('panel-high-contrast', (active) => {
            document.body.classList.toggle('high-contrast', active);
        });

        // Reduced motion toggle
        _bindPanelToggle('panel-reduced-motion', (active) => {
            document.body.classList.toggle('reduced-motion', active);
            if (typeof FLOW !== 'undefined') {
                active ? FLOW.disable() : FLOW.enable();
            }
        });
    }

    // =========================================================================
    // EXPORT CONTROLS
    // =========================================================================

    function _bindExportControls() {
        // PNG export
        document.getElementById('panel-export-png')?.addEventListener('click', () => {
            if (typeof exportPNG === 'function') {
                exportPNG();
            } else if (typeof Graph !== 'undefined' && Graph.renderer) {
                const canvas = Graph.renderer().domElement;
                const link = document.createElement('a');
                link.download = 'collider-graph.png';
                link.href = canvas.toDataURL('image/png');
                link.click();
            }
        });

        // JSON export
        document.getElementById('panel-export-json')?.addEventListener('click', () => {
            if (typeof exportJSON === 'function') {
                exportJSON();
            } else if (typeof Graph !== 'undefined' && Graph.graphData) {
                const data = Graph.graphData();
                const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
                const link = document.createElement('a');
                link.download = 'collider-data.json';
                link.href = URL.createObjectURL(blob);
                link.click();
            }
        });

        // SVG export (placeholder)
        document.getElementById('panel-export-svg')?.addEventListener('click', () => {
            console.log('[EXPORT] SVG export not yet implemented for WebGL canvas');
            if (typeof TOAST !== 'undefined') {
                TOAST.show('SVG export coming soon');
            }
        });

        // Embed code
        document.getElementById('panel-export-embed')?.addEventListener('click', () => {
            const embedCode = `<iframe src="${window.location.href}" width="800" height="600"></iframe>`;
            navigator.clipboard?.writeText(embedCode).then(() => {
                if (typeof TOAST !== 'undefined') {
                    TOAST.show('Embed code copied to clipboard');
                }
            });
        });
    }

    // =========================================================================
    // LAYOUT CONTROLS
    // =========================================================================

    function _bindLayoutControls() {
        // Reheat simulation
        document.getElementById('panel-reheat')?.addEventListener('click', () => {
            if (typeof Graph !== 'undefined' && Graph.d3ReheatSimulation) {
                Graph.d3ReheatSimulation();
            }
        });

        // Freeze simulation
        document.getElementById('panel-freeze')?.addEventListener('click', () => {
            if (typeof Graph !== 'undefined') {
                Graph.d3Force('charge', null);
                Graph.d3Force('link', null);
            }
        });

        // Cool down simulation
        document.getElementById('panel-cool')?.addEventListener('click', () => {
            if (typeof Graph !== 'undefined' && Graph.cooldownTicks) {
                Graph.cooldownTicks(100);
            }
        });

        // Alpha decay slider
        _bindPanelSlider('panel-alpha-decay', 'panel-alpha-decay-num', (val) => {
            if (typeof Graph !== 'undefined' && Graph.d3AlphaDecay) {
                Graph.d3AlphaDecay(parseFloat(val));
            }
        });
    }

    // =========================================================================
    // VIEW MODE CONTROLS
    // =========================================================================

    function _bindViewModeControls() {
        // 3D/2D buttons
        document.getElementById('panel-view-3d')?.addEventListener('click', () => {
            document.getElementById('panel-view-3d')?.classList.add('active');
            document.getElementById('panel-view-2d')?.classList.remove('active');
            if (typeof DIMENSION !== 'undefined' && DIMENSION.setMode) {
                DIMENSION.setMode('3d');
            } else if (typeof setDimension === 'function') {
                setDimension('3d');
            }
        });

        document.getElementById('panel-view-2d')?.addEventListener('click', () => {
            document.getElementById('panel-view-2d')?.classList.add('active');
            document.getElementById('panel-view-3d')?.classList.remove('active');
            if (typeof DIMENSION !== 'undefined' && DIMENSION.setMode) {
                DIMENSION.setMode('2d');
            } else if (typeof setDimension === 'function') {
                setDimension('2d');
            }
        });

        // Atoms/Files view mode
        document.querySelectorAll('[data-panel-mode]').forEach(btn => {
            btn.addEventListener('click', () => {
                const mode = btn.dataset.panelMode;
                document.querySelectorAll('[data-panel-mode]').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');

                if (typeof FILE_VIZ !== 'undefined' && FILE_VIZ.setMode) {
                    FILE_VIZ.setMode(mode);
                } else if (typeof setGraphMode === 'function') {
                    setGraphMode(mode);
                }
            });
        });
    }

    // =========================================================================
    // PANEL SETTINGS
    // =========================================================================

    function _bindPanelSettings() {
        // Reset layout
        document.getElementById('panel-reset-layout')?.addEventListener('click', () => {
            if (typeof PANEL_SYSTEM !== 'undefined' && PANEL_SYSTEM.resetLayout) {
                PANEL_SYSTEM.resetLayout();
            }
        });

        // Toggle dock visibility
        const toggleDock = document.getElementById('panel-toggle-dock');
        if (toggleDock) {
            toggleDock.addEventListener('click', () => {
                const container = document.querySelector('.panel-container');
                if (container) {
                    const isHidden = container.classList.toggle('hidden');
                    toggleDock.textContent = isHidden ? 'Show Panels' : 'Hide Panels';
                }
            });
        }
    }

    // =========================================================================
    // ANALYSIS PANEL UPDATES
    // =========================================================================

    function _bindAnalysisUpdates() {
        // Toggle metrics overlay
        _bindPanelToggle('panel-toggle-metrics', (active) => {
            const overlay = document.getElementById('metrics-overlay');
            if (overlay) overlay.classList.toggle('hidden', !active);
        });

        // Subscribe to events for stats updates
        if (typeof EVENT_BUS !== 'undefined') {
            EVENT_BUS.on('filter:changed', _updateAnalysisStats);
            EVENT_BUS.on('selection:changed', _updateAnalysisStats);
        }

        // Initial update
        setTimeout(_updateAnalysisStats, 1000);
    }

    function _updateAnalysisStats() {
        if (typeof Graph === 'undefined' || !Graph.graphData) return;

        const data = Graph.graphData();
        const visibleNodes = data.nodes.filter(n => n.__threeObj?.visible !== false);
        const selectedCount = window.selectedNodes?.length || 0;

        const elVisible = document.getElementById('panel-stat-visible');
        const elSelected = document.getElementById('panel-stat-selected');
        const elEdges = document.getElementById('panel-stat-edges');
        const elDensity = document.getElementById('panel-stat-density');

        if (elVisible) elVisible.textContent = visibleNodes.length;
        if (elSelected) elSelected.textContent = selectedCount;
        if (elEdges) elEdges.textContent = data.links?.length || 0;

        // Density = edges / (nodes * (nodes-1) / 2)
        const n = visibleNodes.length;
        const e = data.links?.length || 0;
        const maxEdges = n * (n - 1) / 2;
        const density = maxEdges > 0 ? (e / maxEdges * 100).toFixed(1) + '%' : '--';
        if (elDensity) elDensity.textContent = density;
    }

    // =========================================================================
    // NODE APPEARANCE CONTROLS
    // =========================================================================

    function _bindNodeAppearanceControls() {
        // Size mode buttons
        document.querySelectorAll('[data-panel-size-mode]').forEach(btn => {
            btn.addEventListener('click', () => {
                const mode = btn.dataset.panelSizeMode;
                document.querySelectorAll('[data-panel-size-mode]').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');

                if (typeof APPEARANCE_STATE !== 'undefined') {
                    APPEARANCE_STATE.sizeMode = mode;
                }
                if (typeof Graph !== 'undefined' && Graph.nodeVal) {
                    const sizeMap = {
                        uniform: () => 1,
                        degree: n => Math.sqrt((n.in_degree || 0) + (n.out_degree || 0) + 1),
                        fanout: n => Math.sqrt((n.out_degree || 0) + 1),
                        complexity: n => Math.log((n.complexity || 1) + 1)
                    };
                    Graph.nodeVal(sizeMap[mode] || sizeMap.uniform);
                }
            });
        });

        // Node size slider
        _bindPanelSlider('panel-node-size', 'panel-node-size-num', (val) => {
            if (typeof APPEARANCE_STATE !== 'undefined') APPEARANCE_STATE.nodeScale = parseFloat(val);
            if (typeof Graph !== 'undefined' && Graph.nodeVal) {
                Graph.nodeVal(n => (n.val || 1) * parseFloat(val));
            }
        });

        // Node opacity slider
        _bindPanelSlider('panel-node-opacity', 'panel-node-opacity-num', (val) => {
            if (typeof APPEARANCE_STATE !== 'undefined') APPEARANCE_STATE.nodeOpacity = parseFloat(val);
        });

        // Label size slider
        _bindPanelSlider('panel-label-size', 'panel-label-size-num', (val) => {
            if (typeof APPEARANCE_STATE !== 'undefined') APPEARANCE_STATE.labelSize = parseFloat(val);
        });

        // Show labels toggle
        _bindPanelToggle('panel-toggle-labels', (active) => {
            if (typeof Graph !== 'undefined') {
                Graph.nodeLabel(n => active ? (n.name || n.id) : null);
            }
        });

        // Highlight selected toggle
        _bindPanelToggle('panel-toggle-highlight', (active) => {
            if (typeof APPEARANCE_STATE !== 'undefined') {
                APPEARANCE_STATE.highlightSelected = active;
            }
        });

        // 3D depth shading toggle
        _bindPanelToggle('panel-toggle-depth', (active) => {
            if (typeof APPEARANCE_STATE !== 'undefined') {
                APPEARANCE_STATE.depthShading = active;
            }
        });
    }

    // =========================================================================
    // EDGE APPEARANCE CONTROLS
    // =========================================================================

    function _bindEdgeAppearanceControls() {
        // Edge style buttons
        document.querySelectorAll('[data-panel-edge-style]').forEach(btn => {
            btn.addEventListener('click', () => {
                const style = btn.dataset.panelEdgeStyle;
                document.querySelectorAll('[data-panel-edge-style]').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');

                if (typeof APPEARANCE_STATE !== 'undefined') {
                    APPEARANCE_STATE.edgeStyle = style;
                }
                // Apply particle effect for particle style
                if (typeof Graph !== 'undefined') {
                    Graph.linkDirectionalParticles(style === 'particle' ? 4 : 0);
                }
            });
        });

        // Edge opacity slider
        _bindPanelSlider('panel-edge-opacity', 'panel-edge-opacity-num', (val) => {
            if (typeof APPEARANCE_STATE !== 'undefined') APPEARANCE_STATE.edgeOpacity = parseFloat(val);
            if (typeof EDGE !== 'undefined' && EDGE.apply) EDGE.apply();
        });

        // Edge width slider
        _bindPanelSlider('panel-edge-width', 'panel-edge-width-num', (val) => {
            if (typeof APPEARANCE_STATE !== 'undefined') APPEARANCE_STATE.edgeWidth = parseFloat(val);
            if (typeof Graph !== 'undefined') Graph.linkWidth(parseFloat(val));
        });

        // Edge curvature slider
        _bindPanelSlider('panel-edge-curve', 'panel-edge-curve-num', (val) => {
            if (typeof APPEARANCE_STATE !== 'undefined') APPEARANCE_STATE.edgeCurvature = parseFloat(val);
            if (typeof Graph !== 'undefined') Graph.linkCurvature(parseFloat(val));
        });

        // Particle speed slider
        _bindPanelSlider('panel-particle-speed', 'panel-particle-speed-num', (val) => {
            if (typeof Graph !== 'undefined') Graph.linkDirectionalParticleSpeed(parseFloat(val));
        });

        // Show arrows toggle
        _bindPanelToggle('panel-toggle-arrows', (active) => {
            if (typeof APPEARANCE_STATE !== 'undefined') APPEARANCE_STATE.showArrows = active;
            if (typeof Graph !== 'undefined') {
                Graph.linkDirectionalArrowLength(active ? 6 : 0);
                Graph.linkDirectionalArrowRelPos(0.9);
            }
        });

        // Gradient colors toggle
        _bindPanelToggle('panel-toggle-gradient', (active) => {
            if (typeof APPEARANCE_STATE !== 'undefined') APPEARANCE_STATE.gradientEdges = active;
            if (typeof EDGE !== 'undefined' && EDGE.apply) EDGE.apply();
        });
    }

    // =========================================================================
    // UTILITIES
    // =========================================================================

    function _bindPanelToggle(toggleId, callback) {
        const toggle = document.getElementById(toggleId);
        if (!toggle) return;

        toggle.addEventListener('click', () => {
            const isActive = toggle.classList.toggle('active');
            callback(isActive);
        });
    }

    function _bindPanelSlider(sliderId, numInputId, callback) {
        const slider = document.getElementById(sliderId);
        const numInput = document.getElementById(numInputId);

        if (slider) {
            slider.addEventListener('input', () => {
                if (numInput) numInput.value = slider.value;
                callback(slider.value);
            });
        }

        if (numInput) {
            numInput.addEventListener('change', () => {
                if (slider) slider.value = numInput.value;
                callback(numInput.value);
            });
        }
    }

    function _debounce(fn, delay) {
        let timer = null;
        return function(...args) {
            clearTimeout(timer);
            timer = setTimeout(() => fn.apply(this, args), delay);
        };
    }

    return {
        init,
        updateStats: _updateAnalysisStats
    };

})();

console.log('[Module] PANEL_HANDLERS loaded');
