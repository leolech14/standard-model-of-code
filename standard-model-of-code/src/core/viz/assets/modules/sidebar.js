/**
 * SIDEBAR MODULE
 *
 * Manages sidebar controls including color presets, layout presets,
 * physics controls, appearance controls, filters, and panel updates.
 *
 * Depends on: ANIM (for layouts), REFRESH (for throttled updates)
 *
 * Usage:
 *   SIDEBAR.init()                         // Initialize after DOM ready
 *   SIDEBAR.setColorMode('tier')           // Change color mode
 *   SIDEBAR.setLayout('force')             // Change layout
 *   SIDEBAR.setPhysicsPreset('tight')      // Apply physics preset
 *   SIDEBAR.updateStats(nodes, edges)      // Update stat displays
 */

// Note: Using window assignment instead of const to avoid duplicate declaration with app.js
window.SIDEBAR = (function () {
    'use strict';

    // =========================================================================
    // STATE
    // =========================================================================

    let _refreshTimer = null;
    let _bound = false;

    // =========================================================================
    // INITIALIZATION
    // =========================================================================

    /**
     * Initialize sidebar - call after DOM is ready
     */
    function init() {
        if (_bound) return;
        _bound = true;

        _bindSectionHeaders();
        _bindColorPresets();
        _bindLayoutPresets();
        _bindPhysicsControls();
        _bindAppearanceControls();
        _bindActionButtons();

        console.log('[SIDEBAR] Initialized');
    }

    // =========================================================================
    // SECTION COLLAPSE/EXPAND
    // =========================================================================

    function _bindSectionHeaders() {
        document.querySelectorAll('.section-header[data-section]').forEach(header => {
            header.addEventListener('click', () => {
                const sectionId = header.dataset.section;
                const content = document.getElementById(`section-${sectionId}`);
                if (!content) return;

                const isCollapsed = header.classList.toggle('collapsed');
                content.classList.toggle('collapsed', isCollapsed);
            });
        });
    }

    // =========================================================================
    // COLOR PRESETS (TIER, FAMILY, LAYER, RING, FILE, FLOW)
    // =========================================================================

    // =========================================================================
    // COLOR PRESETS: SMART SIDEBAR CONFIGURATION
    // =========================================================================

    const PRESET_CONFIG = [
        {
            category: 'Architecture',
            presets: [
                { id: 'tier', label: 'Tier', desc: 'Auto-detected architectural height' },
                { id: 'layer', label: 'Layer', desc: 'Business logic strata' },
                { id: 'subsystem', label: 'Subsystem', desc: 'Functional domain grouping' },
                { id: 'boundary_score', label: 'Boundary', desc: 'Internal vs External (1-9)' },
                { id: 'phase', label: 'Phase', desc: 'Data-Logic-Org-Exec (MIPO)' }
            ]
        },
        {
            category: 'Taxonomy',
            presets: [
                { id: 'atom', label: 'Atom', desc: 'Function, Class, Module types' },
                { id: 'family', label: 'Family', desc: 'Logic, Data, Execution' },
                { id: 'role', label: 'Role', desc: 'Service, Repo, Controller' },
                { id: 'roleCategory', label: 'Role Cat', desc: 'Query, Command, Event' },
                { id: 'fileType', label: 'File Type', desc: 'Extension-based coloring' }
            ]
        },
        {
            category: 'Metrics',
            presets: [
                { id: 'complexity', label: 'Complexity', desc: 'Cyclomatic complexity' },
                { id: 'loc', label: 'LOC', desc: 'Lines of Code' },
                { id: 'fan_in', label: 'Fan-In', desc: 'Incoming dependencies' },
                { id: 'fan_out', label: 'Fan-Out', desc: 'Outgoing dependencies' },
                { id: 'trust', label: 'Trust', desc: 'Detection confidence' }
            ]
        },
        {
            category: 'RPBL DNA',
            presets: [
                { id: 'responsibility', label: 'Responsibility', desc: 'SRP alignment (1-9)' },
                { id: 'purity', label: 'Purity', desc: 'Side-effect profile (1-9)' },
                { id: 'lifecycle_score', label: 'Lifecycle', desc: 'Static vs Dynamic (1-9)' },
                { id: 'state', label: 'State', desc: 'Stateful vs Stateless' },
                { id: 'visibility', label: 'Visibility', desc: 'Public vs Private' }
            ]
        },
        {
            category: 'Topology',
            presets: [
                { id: 'centrality', label: 'Centrality', desc: 'Graph importance' },
                { id: 'rank', label: 'PageRank', desc: 'Algorithmic influence' }, // mapped to centrality logic or similar
                { id: 'ring', label: 'Ring', desc: 'Concentric architecture rings' },
                { id: 'flow', label: 'Flow', desc: 'Dependency direction' }
            ]
        },
        {
            category: 'Evolution',
            presets: [
                { id: 'churn', label: 'Churn', desc: 'Change frequency (Simulated)' },
                { id: 'age', label: 'Age', desc: 'Time since creation (Simulated)' }
            ]
        }
    ];

    function _bindColorPresets() {
        // Init Smart Sidebar
        const container = document.getElementById('section-color');
        if (!container) return;

        // Clear existing static buttons if any (except header)
        const contentDiv = container.querySelector('.section-content');
        if (contentDiv) {
            contentDiv.innerHTML = ''; // Rebuild from scratch
            renderSmartSidebar(contentDiv);
        }
    }

    function renderSmartSidebar(container) {
        // Search bar
        const searchContainer = document.createElement('div');
        searchContainer.style.cssText = 'padding-bottom: 8px; margin-bottom: 8px; border-bottom: 1px solid var(--border);';
        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.placeholder = 'Filter Presets...';
        searchInput.style.cssText = 'width: 100%; background: rgba(0,0,0,0.2); border: 1px solid var(--border); padding: 4px 8px; color: var(--text); border-radius: 4px; font-size: 10px;';

        searchInput.addEventListener('input', (e) => {
            const term = e.target.value.toLowerCase();
            document.querySelectorAll('.preset-category').forEach(cat => {
                let hasMatch = false;
                cat.querySelectorAll('.btn').forEach(btn => {
                    const match = btn.textContent.toLowerCase().includes(term) || btn.title.toLowerCase().includes(term);
                    btn.style.display = match ? 'block' : 'none';
                    if (match) hasMatch = true;
                });
                cat.style.display = hasMatch ? 'block' : 'none';
            });
        });

        searchContainer.appendChild(searchInput);
        container.appendChild(searchContainer);

        // Render Categories
        PRESET_CONFIG.forEach(section => {
            const catDiv = document.createElement('div');
            catDiv.className = 'preset-category';
            catDiv.style.marginBottom = '12px';

            const catTitle = document.createElement('div');
            catTitle.textContent = section.category;
            catTitle.style.cssText = 'font-size: 9px; opacity: 0.5; text-transform: uppercase; margin-bottom: 6px; letter-spacing: 0.5px;';
            catDiv.appendChild(catTitle);

            const grid = document.createElement('div');
            grid.className = 'btn-grid btn-grid-3'; // Default to 3-col

            section.presets.forEach(p => {
                const btn = document.createElement('button');
                btn.className = 'btn color-btn';
                btn.textContent = p.label;
                btn.title = p.desc;
                btn.dataset.preset = p.id;

                // Add color indicator logic if needed (dot)
                // For now relying on CSS ::before using data-preset, OR we can inject style

                btn.addEventListener('click', () => {
                    setColorMode(p.id);
                    // Update UI active state
                    document.querySelectorAll('#section-color .btn').forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                });

                grid.appendChild(btn);
            });

            catDiv.appendChild(grid);
            container.appendChild(catDiv);
        });
    }

    function setColorMode(mode) {
        if (typeof APPEARANCE_STATE !== 'undefined') {
            APPEARANCE_STATE.colorMode = mode;
            APPEARANCE_STATE.currentPreset = mode;
        }

        // Call existing function if available
        if (typeof setNodeColorMode === 'function') {
            setNodeColorMode(mode);
        }

        // Handle flow mode specially
        if (mode === 'flow') {
            if (typeof flowMode !== 'undefined' && !flowMode && typeof toggleFlowMode === 'function') {
                toggleFlowMode();
            }
        } else if (typeof flowMode !== 'undefined' && flowMode && typeof disableFlowMode === 'function') {
            disableFlowMode();
        }

        // Refresh gradient edges
        if (typeof window !== 'undefined' && typeof window.refreshGradientEdgeColors === 'function') {
            window.refreshGradientEdgeColors();
        }

        // Re-render legends
        if (typeof renderAllLegends === 'function') {
            renderAllLegends();
        }

        console.log('[SIDEBAR] Color mode:', mode);
    }

    // =========================================================================
    // LAYOUT PRESETS (FORCE, RADIAL, ORBITAL, SPHERE, GRID, SPIRAL)
    // =========================================================================

    function _bindLayoutPresets() {
        const container = document.getElementById('section-layout');
        if (!container) return;

        container.querySelectorAll('.btn[data-layout]').forEach(btn => {
            btn.addEventListener('click', () => {
                const layout = btn.dataset.layout;
                setLayout(layout);

                // Update active state
                container.querySelectorAll('.btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            });
        });
    }

    function setLayout(layout) {
        // Prefer ANIM module if available
        if (typeof ANIM !== 'undefined' && ANIM.applyLayout) {
            ANIM.applyLayout(layout, true);
        } else if (typeof applyLayoutPreset === 'function') {
            applyLayoutPreset(layout, true);
        }
        console.log('[SIDEBAR] Layout:', layout);
    }

    // =========================================================================
    // PHYSICS CONTROLS
    // =========================================================================

    const PHYSICS_PRESETS = {
        default: { charge: -120, link: 50, center: 0.05, damping: 0.4 },
        tight: { charge: -80, link: 30, center: 0.1, damping: 0.5 },
        loose: { charge: -200, link: 80, center: 0.02, damping: 0.3 },
        explosive: { charge: -400, link: 120, center: 0.01, damping: 0.2 }
    };

    function _bindPhysicsControls() {
        // Charge (repulsion)
        _bindSlider('physics-charge', (val) => {
            if (typeof Graph !== 'undefined' && Graph) {
                Graph.d3Force('charge').strength(val);
                Graph.d3ReheatSimulation();
            }
        });

        // Link distance
        _bindSlider('physics-link', (val) => {
            if (typeof Graph !== 'undefined' && Graph) {
                Graph.d3Force('link').distance(val);
                Graph.d3ReheatSimulation();
            }
        });

        // Center pull
        _bindSlider('physics-center', (val) => {
            if (typeof Graph !== 'undefined' && Graph) {
                const center = Graph.d3Force('center');
                if (center && center.strength) center.strength(val);
                Graph.d3ReheatSimulation();
            }
        });

        // Damping (velocity decay)
        _bindSlider('physics-damping', (val) => {
            if (typeof Graph !== 'undefined' && Graph) {
                Graph.d3VelocityDecay(val);
                Graph.d3ReheatSimulation();
            }
        });

        // Physics presets
        const container = document.getElementById('section-physics');
        if (container) {
            container.querySelectorAll('.btn[data-physics]').forEach(btn => {
                btn.addEventListener('click', () => {
                    const preset = btn.dataset.physics;
                    setPhysicsPreset(preset);
                });
            });
        }
    }

    function setPhysicsPreset(preset) {
        const p = PHYSICS_PRESETS[preset];
        if (!p) return;

        // Update sliders
        _setSliderValue('physics-charge', p.charge);
        _setSliderValue('physics-link', p.link);
        _setSliderValue('physics-center', p.center);
        _setSliderValue('physics-damping', p.damping);

        // Apply to graph
        if (typeof Graph !== 'undefined' && Graph) {
            Graph.d3Force('charge').strength(p.charge);
            Graph.d3Force('link').distance(p.link);
            const center = Graph.d3Force('center');
            if (center && center.strength) center.strength(p.center);
            Graph.d3VelocityDecay(p.damping);
            Graph.d3ReheatSimulation();
        }

        console.log('[SIDEBAR] Physics preset:', preset);
    }

    // =========================================================================
    // APPEARANCE CONTROLS
    // =========================================================================

    function _bindAppearanceControls() {
        // Node size
        _bindSlider('node-size', (val) => {
            if (typeof APPEARANCE_STATE !== 'undefined') {
                APPEARANCE_STATE.nodeScale = val;
            }
            if (typeof Graph !== 'undefined' && Graph) {
                Graph.nodeVal(n => (n.val || 1) * val);
            }
        });

        // Edge opacity
        _bindSlider('edge-opacity', (val) => {
            if (typeof APPEARANCE_STATE !== 'undefined') {
                APPEARANCE_STATE.edgeOpacity = val;
            }
            if (typeof applyEdgeMode === 'function') applyEdgeMode();
        });

        // Label size
        _bindSlider('label-size', (val) => {
            if (typeof Graph !== 'undefined' && Graph) {
                Graph.nodeLabel(n => val > 0.3 ? n.name : null);
            }
        });

        // Toggles
        _bindToggle('toggle-labels', (active) => {
            if (typeof VIS_FILTERS !== 'undefined' && VIS_FILTERS.metadata) {
                VIS_FILTERS.metadata.showLabels = active;
            }
            if (typeof Graph !== 'undefined' && Graph) {
                Graph.nodeLabel(n => active ? n.name : null);
            }
        });

        _bindToggle('toggle-stars', (active) => {
            // Toggle starfield visibility
            if (typeof Graph !== 'undefined' && Graph) {
                const scene = Graph.scene();
                if (scene) {
                    scene.children.forEach(child => {
                        if (child.type === 'Points' && child.geometry?.attributes?.position?.count > 1000) {
                            child.visible = active;
                        }
                    });
                }
            }
        });
    }

    // =========================================================================
    // ACTION BUTTONS
    // =========================================================================

    function _bindActionButtons() {
        // Reset view
        const resetBtn = document.getElementById('btn-reset');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                if (typeof Graph !== 'undefined' && Graph) {
                    Graph.cameraPosition({ x: 0, y: 0, z: 500 }, { x: 0, y: 0, z: 0 }, 1000);
                }
            });
        }

        // Screenshot
        const screenshotBtn = document.getElementById('btn-screenshot');
        if (screenshotBtn) {
            screenshotBtn.addEventListener('click', () => {
                if (typeof takeScreenshot === 'function') {
                    takeScreenshot();
                } else if (typeof Graph !== 'undefined' && Graph) {
                    const link = document.createElement('a');
                    link.download = 'collider-screenshot.png';
                    link.href = Graph.renderer().domElement.toDataURL('image/png');
                    link.click();
                }
            });
        }

        // Toggle 2D
        const toggle2dBtn = document.getElementById('btn-2d');
        if (toggle2dBtn) {
            toggle2dBtn.addEventListener('click', () => {
                if (typeof toggle2DMode === 'function') toggle2DMode();
            });
        }

        // Freeze simulation
        const freezeBtn = document.getElementById('btn-freeze');
        if (freezeBtn) {
            freezeBtn.addEventListener('click', () => {
                if (typeof toggleFreeze === 'function') {
                    toggleFreeze();
                } else if (typeof Graph !== 'undefined' && Graph) {
                    // Simple freeze toggle
                    const alpha = Graph.d3AlphaTarget();
                    Graph.d3AlphaTarget(alpha === 0 ? 0.3 : 0);
                    freezeBtn.classList.toggle('active', alpha !== 0);
                }
            });
        }
    }

    // =========================================================================
    // FILTER CHIPS
    // =========================================================================

    function populateFilterChips(data) {
        if (!data || !data.nodes) return;

        // Tiers
        const tiers = [...new Set(data.nodes.map(n => n.tier).filter(Boolean))].sort();
        _populateChipGroup('filter-tiers', tiers, 'tiers');

        // Rings
        const rings = [...new Set(data.nodes.map(n => n.ring).filter(Boolean))].sort();
        _populateChipGroup('filter-rings', rings, 'rings');

        // Edge types
        const edgeTypes = [...new Set(data.links?.map(e => e.type).filter(Boolean) || [])].sort();
        _populateChipGroup('filter-edges', edgeTypes, 'edges');
    }

    function _populateChipGroup(containerId, items, filterKey) {
        const container = document.getElementById(containerId);
        if (!container) return;

        container.innerHTML = '';
        items.forEach(item => {
            const chip = document.createElement('div');
            chip.className = 'chip';
            chip.textContent = item;
            chip.addEventListener('click', () => {
                const isActive = chip.classList.toggle('active');
                setFilter(filterKey, item, !isActive); // active = filtered OUT
                _scheduleRefresh();
            });
            container.appendChild(chip);
        });
    }

    function setFilter(dimension, value, visible) {
        if (typeof VIS_FILTERS === 'undefined') return;
        const set = VIS_FILTERS[dimension];
        if (!set) return;

        if (visible) {
            set.delete(value); // Remove from filter = show
        } else {
            set.add(value);    // Add to filter = hide
        }
    }

    // =========================================================================
    // HOVER PANEL
    // =========================================================================

    function showHoverPanel(node) {
        const panel = document.getElementById('hover-panel');
        if (!panel || !node) return;

        const setField = (id, value) => {
            const el = document.getElementById(id);
            if (el) el.textContent = value || '--';
        };

        setField('hover-name', node.name);
        setField('hover-kind', node.kind || node.type || 'unknown');
        setField('hover-atom', node.atom);
        setField('hover-family', node.family || (node.atom ? node.atom.split('.')[0] : null));
        setField('hover-ring', node.ring);
        setField('hover-tier', node.tier);
        setField('hover-role', node.role);

        const fileEl = document.getElementById('hover-file');
        if (fileEl) fileEl.textContent = node.file_path || node.file || '';

        panel.classList.add('visible');
    }

    function hideHoverPanel() {
        const panel = document.getElementById('hover-panel');
        if (panel) panel.classList.remove('visible');
    }

    // =========================================================================
    // SELECTION PANEL
    // =========================================================================

    function updateSelectionPanel(selectedNodes) {
        const panel = document.getElementById('selection-panel');
        const title = document.getElementById('selection-title');
        const list = document.getElementById('selection-list');
        const clearBtn = document.getElementById('selection-clear');

        if (!panel || !list) return;

        if (!selectedNodes || selectedNodes.length === 0) {
            panel.classList.remove('visible');
            return;
        }

        if (title) title.textContent = `SELECTED (${selectedNodes.length})`;

        list.innerHTML = selectedNodes.slice(0, 20).map(n =>
            `<div class="selection-item">${n.name || n.id}</div>`
        ).join('');

        if (selectedNodes.length > 20) {
            list.innerHTML += `<div class="selection-item" style="opacity:0.5">...and ${selectedNodes.length - 20} more</div>`;
        }

        panel.classList.add('visible');

        // Bind clear button
        if (clearBtn) {
            clearBtn.onclick = () => {
                if (typeof SELECT !== 'undefined') {
                    SELECT.clear();
                } else if (typeof clearSelection === 'function') {
                    clearSelection();
                }
                panel.classList.remove('visible');
            };
        }
    }

    // =========================================================================
    // STATS DISPLAY
    // =========================================================================

    function updateStats(nodes, edges, entropy) {
        const nodeEl = document.getElementById('stat-nodes');
        const edgeEl = document.getElementById('stat-edges');
        const entropyEl = document.getElementById('stat-entropy');

        if (nodeEl) nodeEl.textContent = nodes?.toLocaleString() || '0';
        if (edgeEl) edgeEl.textContent = edges?.toLocaleString() || '0';
        if (entropyEl) entropyEl.textContent = entropy?.toFixed(2) || '--';
    }

    // =========================================================================
    // HELPER: SLIDERS
    // =========================================================================

    function _bindSlider(id, callback) {
        const slider = document.getElementById(id);
        const valueEl = document.getElementById(`${id}-val`);
        if (!slider) return;

        slider.addEventListener('input', () => {
            const val = parseFloat(slider.value);
            if (valueEl) valueEl.textContent = val;
            callback(val);
        });
    }

    function _setSliderValue(id, value) {
        const slider = document.getElementById(id);
        const valueEl = document.getElementById(`${id}-val`);
        if (slider) slider.value = value;
        if (valueEl) valueEl.textContent = value;
    }

    // =========================================================================
    // HELPER: TOGGLES
    // =========================================================================

    function _bindToggle(id, callback) {
        const toggle = document.getElementById(id);
        if (!toggle) return;

        toggle.addEventListener('click', () => {
            const isActive = toggle.classList.toggle('active');
            callback(isActive);
        });
    }

    // =========================================================================
    // DEBOUNCED REFRESH
    // =========================================================================

    function _scheduleRefresh() {
        clearTimeout(_refreshTimer);
        _refreshTimer = setTimeout(() => {
            if (typeof REFRESH !== 'undefined') {
                REFRESH.throttled();
            } else if (typeof refreshGraph === 'function') {
                refreshGraph();
            }
        }, 16); // ~1 frame
    }

    // =========================================================================
    // PUBLIC API
    // =========================================================================

    return {
        // Initialization
        init,

        // Color modes
        setColorMode,

        // Layouts
        setLayout,

        // Physics
        setPhysicsPreset,
        PHYSICS_PRESETS,

        // Filters
        // Filters
        populateFilterChips,
        setFilter,
        renderSmartSidebar, // Export for debug/manual re-render

        // Panels
        showHoverPanel,
        hideHoverPanel,
        updateSelectionPanel,

        // Stats
        updateStats
    };
})();

// Backward compatibility - SidebarManager class is defined in app.js, not duplicated here
// The SIDEBAR module provides all functionality via SIDEBAR.* calls
