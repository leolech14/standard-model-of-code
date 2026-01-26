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
        _bindNumericDisplayMirrors();
        _bindMiscControls();

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

        // === ORPHANED FILTER CONTROLS ===

        // Hide orphans (alternate ID)
        _bindPanelToggle('filter-hide-orphans', (active) => {
            if (typeof FILTER_STATE !== 'undefined') {
                FILTER_STATE.setHideOrphans(active);
            }
        });

        // Hide dead code (alternate ID)
        _bindPanelToggle('filter-hide-dead', (active) => {
            if (typeof FILTER_STATE !== 'undefined') {
                FILTER_STATE.setHideDeadCode(active);
            }
        });

        // Degree range filters
        _bindPanelSlider('filter-min-degree', 'filter-min-degree-val', (val) => {
            if (typeof FILTER_STATE !== 'undefined') {
                FILTER_STATE.setMinDegree(parseInt(val));
            }
        });

        _bindPanelSlider('filter-max-degree', 'filter-max-degree-val', (val) => {
            if (typeof FILTER_STATE !== 'undefined') {
                FILTER_STATE.setMaxDegree(parseInt(val));
            }
        });

        // Filter chip containers (dynamic population)
        _bindFilterChips('filter-tier-chips', 'tier');
        _bindFilterChips('filter-family-chips', 'family');
        _bindFilterChips('filter-role-chips', 'role');

        // Active filter chips display
        if (typeof EVENT_BUS !== 'undefined') {
            EVENT_BUS.on('filter:changed', _updateFilterChipsDisplay);
        }
    }

    function _bindFilterChips(containerId, filterType) {
        const container = document.getElementById(containerId);
        if (!container) return;

        // Populate chips based on available data
        if (typeof Graph !== 'undefined' && Graph.graphData) {
            const data = Graph.graphData();
            const values = new Set();

            data.nodes.forEach(node => {
                if (filterType === 'tier' && node.tier) values.add(node.tier);
                if (filterType === 'family' && node.family) values.add(node.family);
                if (filterType === 'role' && node.semantic_role) values.add(node.semantic_role);
            });

            // Create chip elements
            Array.from(values).sort().forEach(value => {
                const chip = document.createElement('div');
                chip.className = 'chip';
                chip.textContent = value;
                chip.dataset.value = value;
                chip.dataset.type = filterType;

                chip.addEventListener('click', () => {
                    chip.classList.toggle('active');
                    if (typeof FILTER_STATE !== 'undefined') {
                        const activeChips = Array.from(container.querySelectorAll('.chip.active'))
                            .map(c => c.dataset.value);
                        FILTER_STATE.setFilter(filterType, activeChips);
                    }
                });

                container.appendChild(chip);
            });
        }
    }

    function _updateFilterChipsDisplay() {
        const display = document.getElementById('panel-filter-chips');
        if (!display || typeof FILTER_STATE === 'undefined') return;

        // Get active filters
        const activeFilters = FILTER_STATE.getActiveFilters?.() || {};
        display.innerHTML = '';

        Object.entries(activeFilters).forEach(([type, values]) => {
            if (Array.isArray(values) && values.length > 0) {
                values.forEach(value => {
                    const chip = document.createElement('div');
                    chip.className = 'chip active';
                    chip.textContent = `${type}: ${value}`;
                    chip.addEventListener('click', () => {
                        if (typeof FILTER_STATE !== 'undefined') {
                            FILTER_STATE.removeFilter(type, value);
                        }
                    });
                    display.appendChild(chip);
                });
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

        // === ORPHANED SELECTION CONTROLS ===

        // Clear selection
        document.getElementById('panel-select-clear')?.addEventListener('click', () => {
            window.selectedNodes = [];
            if (typeof Graph !== 'undefined' && Graph.graphData) {
                const data = Graph.graphData();
                // Reset node colors/visibility
                data.nodes.forEach(node => {
                    if (node.__threeObj) {
                        node.__threeObj.material.opacity = 1.0;
                    }
                });
            }
            if (typeof REFRESH !== 'undefined') REFRESH.throttled();
            if (typeof EVENT_BUS !== 'undefined') EVENT_BUS.emit('selection:changed');
        });

        // Invert selection
        document.getElementById('panel-select-invert')?.addEventListener('click', () => {
            if (typeof Graph !== 'undefined' && Graph.graphData) {
                const data = Graph.graphData();
                const currentSelected = new Set((window.selectedNodes || []).map(n => n.id));

                // Invert: select all nodes NOT currently selected
                window.selectedNodes = data.nodes.filter(n => !currentSelected.has(n.id));

                if (typeof REFRESH !== 'undefined') REFRESH.throttled();
                if (typeof EVENT_BUS !== 'undefined') EVENT_BUS.emit('selection:changed');
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

        // === ORPHANED CAMERA CONTROLS ===

        // Auto-rotate (alternate ID)
        _bindPanelToggle('camera-auto-rotate', (active) => {
            if (typeof Graph !== 'undefined' && Graph.controls) {
                Graph.controls().autoRotate = active;
            }
        });

        // Rotate speed (alternate ID)
        _bindPanelSlider('camera-rotate-speed', 'camera-rotate-speed-val', (val) => {
            if (typeof Graph !== 'undefined' && Graph.controls) {
                Graph.controls().autoRotateSpeed = parseFloat(val);
            }
        });

        // Camera reset (alternate ID)
        document.getElementById('camera-reset')?.addEventListener('click', () => {
            if (typeof Graph !== 'undefined') {
                Graph.cameraPosition({ x: 0, y: 0, z: 500 }, { x: 0, y: 0, z: 0 }, 1000);
            }
        });

        // Zoom controls
        document.getElementById('camera-zoom-in')?.addEventListener('click', () => {
            if (typeof Graph !== 'undefined' && Graph.camera) {
                const cam = Graph.camera();
                const direction = new window.THREE.Vector3();
                cam.getWorldDirection(direction);
                cam.position.add(direction.multiplyScalar(50));
            }
        });

        document.getElementById('camera-zoom-out')?.addEventListener('click', () => {
            if (typeof Graph !== 'undefined' && Graph.camera) {
                const cam = Graph.camera();
                const direction = new window.THREE.Vector3();
                cam.getWorldDirection(direction);
                cam.position.add(direction.multiplyScalar(-50));
            }
        });

        document.getElementById('camera-zoom-fit')?.addEventListener('click', () => {
            if (typeof Graph !== 'undefined' && Graph.zoomToFit) {
                Graph.zoomToFit(1000, 50);
            }
        });

        // Camera bookmarks (basic implementation)
        const bookmarkSelect = document.getElementById('camera-bookmarks');
        const saveBookmarkBtn = document.getElementById('camera-save-bookmark');

        if (saveBookmarkBtn) {
            saveBookmarkBtn.addEventListener('click', () => {
                if (typeof Graph !== 'undefined' && Graph.camera) {
                    const cam = Graph.camera();
                    const bookmark = {
                        position: { x: cam.position.x, y: cam.position.y, z: cam.position.z },
                        rotation: { x: cam.rotation.x, y: cam.rotation.y, z: cam.rotation.z },
                        timestamp: Date.now()
                    };

                    // Store in localStorage
                    const bookmarks = JSON.parse(localStorage.getItem('cameraBookmarks') || '[]');
                    bookmarks.push(bookmark);
                    localStorage.setItem('cameraBookmarks', JSON.stringify(bookmarks));

                    // Update select dropdown
                    _updateCameraBookmarksList();

                    if (typeof TOAST !== 'undefined') {
                        TOAST.show('Camera view saved');
                    }
                }
            });
        }

        if (bookmarkSelect) {
            bookmarkSelect.addEventListener('change', () => {
                const index = parseInt(bookmarkSelect.value);
                if (isNaN(index)) return;

                const bookmarks = JSON.parse(localStorage.getItem('cameraBookmarks') || '[]');
                const bookmark = bookmarks[index];
                if (bookmark && typeof Graph !== 'undefined') {
                    Graph.cameraPosition(bookmark.position, { x: 0, y: 0, z: 0 }, 1000);
                }
            });

            // Load existing bookmarks
            _updateCameraBookmarksList();
        }
    }

    function _updateCameraBookmarksList() {
        const select = document.getElementById('camera-bookmarks');
        if (!select) return;

        const bookmarks = JSON.parse(localStorage.getItem('cameraBookmarks') || '[]');
        select.innerHTML = '<option value="">Select saved view...</option>';

        bookmarks.forEach((bookmark, index) => {
            const option = document.createElement('option');
            option.value = index;
            option.textContent = `View ${index + 1} (${new Date(bookmark.timestamp).toLocaleTimeString()})`;
            select.appendChild(option);
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

        // === ORPHANED A11Y CONTROLS (CRITICAL) ===

        // Large text toggle
        _bindPanelToggle('a11y-large-text', (active) => {
            document.body.classList.toggle('large-text', active);
            const scale = active ? 1.2 : 1.0;
            document.documentElement.style.fontSize = (14 * scale) + 'px';
        });

        // Focus indicators toggle
        _bindPanelToggle('a11y-focus-indicators', (active) => {
            document.body.classList.toggle('show-focus-indicators', active);
            if (active) {
                document.body.style.setProperty('--focus-ring', '2px solid var(--accent)');
            } else {
                document.body.style.setProperty('--focus-ring', 'none');
            }
        });

        // Screen reader support toggle
        _bindPanelToggle('a11y-screen-reader', (active) => {
            document.body.setAttribute('aria-live', active ? 'polite' : 'off');
            // Enable additional ARIA labels on graph elements
            if (typeof Graph !== 'undefined' && Graph.nodeLabel) {
                if (active) {
                    // Force label visibility for screen readers
                    document.body.classList.add('sr-mode');
                } else {
                    document.body.classList.remove('sr-mode');
                }
            }
        });

        // Font size slider
        _bindPanelSlider('a11y-font-size', 'a11y-font-size-val', (val) => {
            document.documentElement.style.fontSize = val + 'px';
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

        // === ORPHANED STATS DISPLAYS ===

        // Stats in header
        const statsNodes = document.getElementById('stats-nodes');
        const statsEdges = document.getElementById('stats-edges');
        const statsFiles = document.getElementById('stats-files');
        const statsDensity = document.getElementById('stats-density');

        if (statsNodes) statsNodes.textContent = data.nodes.length;
        if (statsEdges) statsEdges.textContent = data.links?.length || 0;
        if (statsDensity) statsDensity.textContent = density;

        // Count unique files
        if (statsFiles) {
            const uniqueFiles = new Set(data.nodes.map(n => n.file_path).filter(Boolean));
            statsFiles.textContent = uniqueFiles.size;
        }
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

    // =========================================================================
    // NUMERIC DISPLAY MIRRORS - Wire -num displays to sync with sliders
    // =========================================================================

    function _bindNumericDisplayMirrors() {
        // Map slider IDs to their numeric display counterparts
        const mirrorPairs = [
            ['cfg-edge-opacity', 'cfg-edge-opacity-num'],
            ['cfg-edge-width', 'cfg-edge-width-num'],
            ['cfg-edge-curve', 'cfg-edge-curve-num'],
            ['cfg-node-size', 'cfg-node-size-num'],
            ['cfg-node-opacity', 'cfg-node-opacity-num'],
            ['cfg-label-size', 'cfg-label-size-num'],
            ['cfg-particle-speed', 'cfg-particle-speed-num'],
            ['cfg-particle-count', 'cfg-particle-count-num'],
            ['node-size', 'node-size-num'],
            ['edge-opacity', 'edge-opacity-num'],
            ['physics-charge', 'physics-charge-num'],
            ['physics-link-distance', 'physics-link-num'],
            ['cfg-node-res', 'cfg-node-res-num']
        ];

        mirrorPairs.forEach(([sliderId, numId]) => {
            const slider = document.getElementById(sliderId);
            const numDisplay = document.getElementById(numId);

            if (slider && numDisplay) {
                // Sync on slider input
                slider.addEventListener('input', () => {
                    numDisplay.textContent = slider.value;
                });

                // Initialize display
                numDisplay.textContent = slider.value;
            }
        });

        // Physics center (special case - may not have a main slider)
        const physicsCenterNum = document.getElementById('physics-center-num');
        if (physicsCenterNum && typeof PHYSICS_STATE !== 'undefined') {
            physicsCenterNum.textContent = PHYSICS_STATE.centerStrength || '0';
        }
    }

    // =========================================================================
    // MISCELLANEOUS ORPHANED CONTROLS
    // =========================================================================

    function _bindMiscControls() {
        // Toggle labels (legacy control)
        _bindPanelToggle('toggle-labels', (active) => {
            if (typeof Graph !== 'undefined') {
                Graph.nodeLabel(n => active ? (n.name || n.id) : null);
            }
        });

        // Performance frame counter
        const perfFrame = document.getElementById('perf-frame');
        if (perfFrame && typeof Graph !== 'undefined') {
            // Update perf counter on render
            let lastTime = performance.now();
            setInterval(() => {
                const now = performance.now();
                const delta = now - lastTime;
                lastTime = now;
                perfFrame.textContent = delta.toFixed(1) + 'ms';
            }, 100);
        }

        // Section appearance toggle (if it's meant to be collapsible)
        const sectionAppearance = document.getElementById('section-appearance');
        if (sectionAppearance) {
            sectionAppearance.addEventListener('click', () => {
                sectionAppearance.classList.toggle('collapsed');
                const content = sectionAppearance.nextElementSibling;
                if (content) {
                    content.style.display = sectionAppearance.classList.contains('collapsed') ? 'none' : 'block';
                }
            });
        }
    }

    return {
        init,
        updateStats: _updateAnalysisStats
    };

})();

console.log('[Module] PANEL_HANDLERS loaded');
