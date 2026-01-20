/**
 * CONTROL BAR MODULE - Visual Mapping Command Center
 *
 * A persistent control bar (like ChatGPT/Claude input) that allows dynamic
 * mapping of any data characteristic to any visual/physics property.
 *
 * Features:
 * - Always visible at bottom of screen
 * - Works with selected nodes or node groups
 * - Dropdown to choose data source (any field)
 * - Dropdown to choose visual target (size, color, position, physics...)
 * - Group comparison with numbered badges
 * - Real-time preview as you adjust
 *
 * Depends on: DATA, COLOR, ANIM, SELECT
 */

const CONTROL_BAR = (function() {
    'use strict';

    // =========================================================================
    // AVAILABLE DATA SOURCES (what we can map FROM)
    // =========================================================================

    const DATA_SOURCES = {
        // Structural metrics
        size_bytes: { label: 'File Size (bytes)', type: 'continuous', domain: 'file' },
        token_estimate: { label: 'Token Count', type: 'continuous', domain: 'file' },
        line_count: { label: 'Line Count', type: 'continuous', domain: 'file' },
        code_lines: { label: 'Code Lines', type: 'continuous', domain: 'file' },
        complexity_density: { label: 'Complexity Density', type: 'continuous', domain: 'file' },
        cohesion: { label: 'Cohesion', type: 'continuous', domain: 'file' },
        code_ratio: { label: 'Code Ratio', type: 'continuous', domain: 'file' },

        // Temporal metrics
        age_days: { label: 'Age (days)', type: 'continuous', domain: 'file' },

        // Graph metrics
        in_degree: { label: 'In-Degree (callers)', type: 'continuous', domain: 'node' },
        out_degree: { label: 'Out-Degree (calls)', type: 'continuous', domain: 'node' },
        pagerank: { label: 'PageRank', type: 'continuous', domain: 'node' },

        // Categorical
        tier: { label: 'Tier (T0-T4)', type: 'discrete', values: ['T0', 'T1', 'T2', 'T3', 'T4'] },
        ring: { label: 'Ring', type: 'discrete', values: ['CORE', 'NEAR', 'FAR', 'OUTER'] },
        layer: { label: 'Layer', type: 'discrete', values: ['Core', 'Domain', 'Application', 'Interface', 'Infrastructure'] },
        role: { label: 'Role', type: 'discrete', domain: 'node' },
        format_category: { label: 'Format', type: 'discrete', values: ['code', 'config', 'doc', 'data', 'test', 'style', 'script', 'build'] },
        purpose: { label: 'Purpose', type: 'discrete', domain: 'file' },
        effect: { label: 'Effect', type: 'discrete', values: ['Pure', 'Read', 'Write', 'ReadWrite'] },

        // Boolean
        is_test: { label: 'Is Test?', type: 'boolean' },
        is_config: { label: 'Is Config?', type: 'boolean' },
        is_stale: { label: 'Is Stale?', type: 'boolean' },
        is_recent: { label: 'Is Recent?', type: 'boolean' }
    };

    // =========================================================================
    // AVAILABLE TARGETS (what we can map TO)
    // =========================================================================

    const VISUAL_TARGETS = {
        // Size
        nodeSize: { label: 'Node Size', category: 'appearance', range: [1, 30] },

        // Color components
        hue: { label: 'Color Hue', category: 'appearance', range: [0, 360] },
        saturation: { label: 'Saturation', category: 'appearance', range: [0, 100] },
        lightness: { label: 'Lightness', category: 'appearance', range: [20, 80] },
        opacity: { label: 'Opacity', category: 'appearance', range: [0.1, 1.0] },

        // Position
        xPosition: { label: 'X Position', category: 'position', range: [-500, 500] },
        yPosition: { label: 'Y Position', category: 'position', range: [-500, 500] },
        zPosition: { label: 'Z Position (depth)', category: 'position', range: [-300, 300] },
        radius: { label: 'Radial Distance', category: 'position', range: [50, 400] },

        // Physics
        charge: { label: 'Charge (repel)', category: 'physics', range: [-500, 0] },
        linkStrength: { label: 'Link Strength', category: 'physics', range: [0, 1] },
        mass: { label: 'Mass (inertia)', category: 'physics', range: [1, 10] },

        // Animation
        pulseSpeed: { label: 'Pulse Speed', category: 'animation', range: [0, 5] },
        rotationSpeed: { label: 'Rotation Speed', category: 'animation', range: [0, 2] }
    };

    // =========================================================================
    // SCALE FUNCTIONS
    // =========================================================================

    const SCALES = {
        linear: (v, min, max) => (v - min) / (max - min || 1),
        log: (v, min, max) => {
            const logMin = Math.log10(Math.max(1, min));
            const logMax = Math.log10(Math.max(1, max));
            const logVal = Math.log10(Math.max(1, v));
            return (logVal - logMin) / (logMax - logMin || 1);
        },
        sqrt: (v, min, max) => {
            const sqrtMin = Math.sqrt(Math.max(0, min));
            const sqrtMax = Math.sqrt(Math.max(0, max));
            const sqrtVal = Math.sqrt(Math.max(0, v));
            return (sqrtVal - sqrtMin) / (sqrtMax - sqrtMin || 1);
        },
        inverse: (v, min, max) => 1 - (v - min) / (max - min || 1)
    };

    // =========================================================================
    // STATE
    // =========================================================================

    let _visible = false;
    let _container = null;
    let _activeMapping = null;
    let _groups = [];         // [{id, name, nodeIds, color}]
    let _groupCounter = 0;

    // Current mapping configuration
    let _config = {
        source: 'token_estimate',
        target: 'nodeSize',
        scale: 'sqrt',
        scope: 'selection',   // 'selection' | 'all' | 'group:X'
        invert: false
    };

    // =========================================================================
    // UI BUILDING
    // =========================================================================

    function createUI() {
        if (_container) return _container;

        _container = document.createElement('div');
        _container.id = 'control-bar';
        _container.className = 'control-bar';
        _container.innerHTML = `
            <div class="control-bar-inner">
                <!-- Scope Selector -->
                <div class="control-section scope-section">
                    <label>SCOPE</label>
                    <select id="cb-scope" class="cb-select">
                        <option value="selection">Selected Nodes</option>
                        <option value="all">All Nodes</option>
                        <optgroup label="Groups" id="cb-groups-optgroup">
                        </optgroup>
                    </select>
                    <button id="cb-add-group" class="cb-btn cb-btn-small" title="Create group from selection">+G</button>
                    <span id="cb-node-count" class="cb-badge">0</span>
                </div>

                <!-- Source Field -->
                <div class="control-section">
                    <label>MAP</label>
                    <select id="cb-source" class="cb-select">
                        <optgroup label="Structural">
                            <option value="token_estimate">Token Count</option>
                            <option value="line_count">Line Count</option>
                            <option value="size_bytes">File Size</option>
                            <option value="code_lines">Code Lines</option>
                            <option value="complexity_density">Complexity</option>
                            <option value="cohesion">Cohesion</option>
                        </optgroup>
                        <optgroup label="Temporal">
                            <option value="age_days">Age (days)</option>
                        </optgroup>
                        <optgroup label="Graph">
                            <option value="in_degree">In-Degree</option>
                            <option value="out_degree">Out-Degree</option>
                        </optgroup>
                        <optgroup label="Categorical">
                            <option value="tier">Tier</option>
                            <option value="ring">Ring</option>
                            <option value="layer">Layer</option>
                            <option value="role">Role</option>
                            <option value="format_category">Format</option>
                            <option value="effect">Effect</option>
                        </optgroup>
                        <optgroup label="Boolean">
                            <option value="is_test">Is Test?</option>
                            <option value="is_config">Is Config?</option>
                            <option value="is_stale">Is Stale?</option>
                        </optgroup>
                    </select>
                </div>

                <!-- Arrow -->
                <div class="control-section arrow-section">
                    <span class="arrow">&#8594;</span>
                </div>

                <!-- Target Property -->
                <div class="control-section">
                    <label>TO</label>
                    <select id="cb-target" class="cb-select">
                        <optgroup label="Appearance">
                            <option value="nodeSize">Node Size</option>
                            <option value="hue">Color Hue</option>
                            <option value="saturation">Saturation</option>
                            <option value="lightness">Lightness</option>
                            <option value="opacity">Opacity</option>
                        </optgroup>
                        <optgroup label="Position">
                            <option value="xPosition">X Position</option>
                            <option value="yPosition">Y Position</option>
                            <option value="zPosition">Z Depth</option>
                            <option value="radius">Radial Distance</option>
                        </optgroup>
                        <optgroup label="Physics">
                            <option value="charge">Charge (repel)</option>
                            <option value="mass">Mass</option>
                        </optgroup>
                        <optgroup label="Animation">
                            <option value="pulseSpeed">Pulse Speed</option>
                        </optgroup>
                    </select>
                </div>

                <!-- Scale -->
                <div class="control-section">
                    <label>SCALE</label>
                    <select id="cb-scale" class="cb-select cb-select-small">
                        <option value="linear">Linear</option>
                        <option value="sqrt" selected>Sqrt</option>
                        <option value="log">Log</option>
                        <option value="inverse">Inverse</option>
                    </select>
                </div>

                <!-- Actions -->
                <div class="control-section actions-section">
                    <button id="cb-apply" class="cb-btn cb-btn-primary">APPLY</button>
                    <button id="cb-reset" class="cb-btn">Reset</button>
                </div>

                <!-- Group Comparison -->
                <div class="control-section groups-section" id="cb-groups-display">
                </div>

                <!-- Toggle -->
                <button id="cb-toggle" class="cb-toggle" title="Toggle Control Bar">
                    <span class="chevron">&#9660;</span>
                </button>
            </div>
        `;

        // Add styles
        addStyles();

        // Attach event listeners
        attachListeners();

        document.body.appendChild(_container);
        _visible = true;

        return _container;
    }

    function addStyles() {
        if (document.getElementById('control-bar-styles')) return;

        const style = document.createElement('style');
        style.id = 'control-bar-styles';
        style.textContent = `
            .control-bar {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                z-index: 9999;
                background: linear-gradient(180deg, rgba(20, 25, 35, 0.95) 0%, rgba(15, 18, 25, 0.98) 100%);
                backdrop-filter: blur(20px);
                border-top: 1px solid rgba(100, 150, 255, 0.2);
                box-shadow: 0 -4px 30px rgba(0, 0, 0, 0.5);
                transition: transform 0.3s ease;
                font-family: 'SF Mono', 'Consolas', monospace;
            }

            .control-bar.collapsed {
                transform: translateY(calc(100% - 32px));
            }

            .control-bar-inner {
                display: flex;
                align-items: center;
                gap: 16px;
                padding: 12px 20px;
                max-width: 100%;
                overflow-x: auto;
            }

            .control-section {
                display: flex;
                flex-direction: column;
                gap: 4px;
                min-width: fit-content;
            }

            .control-section label {
                font-size: 9px;
                font-weight: 600;
                color: rgba(150, 180, 255, 0.6);
                text-transform: uppercase;
                letter-spacing: 1px;
            }

            .arrow-section {
                align-self: flex-end;
                padding-bottom: 8px;
            }

            .arrow {
                font-size: 20px;
                color: rgba(100, 200, 255, 0.7);
            }

            .cb-select {
                background: rgba(30, 40, 60, 0.8);
                border: 1px solid rgba(100, 150, 255, 0.3);
                border-radius: 6px;
                color: #e0e8ff;
                padding: 8px 12px;
                font-size: 13px;
                font-family: inherit;
                cursor: pointer;
                min-width: 140px;
                transition: all 0.2s;
            }

            .cb-select:hover {
                border-color: rgba(100, 180, 255, 0.5);
                background: rgba(40, 50, 70, 0.9);
            }

            .cb-select:focus {
                outline: none;
                border-color: rgba(100, 200, 255, 0.7);
                box-shadow: 0 0 10px rgba(100, 180, 255, 0.3);
            }

            .cb-select-small {
                min-width: 90px;
            }

            .cb-btn {
                background: rgba(60, 80, 120, 0.6);
                border: 1px solid rgba(100, 150, 255, 0.3);
                border-radius: 6px;
                color: #c0d0ff;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: 600;
                font-family: inherit;
                cursor: pointer;
                transition: all 0.2s;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }

            .cb-btn:hover {
                background: rgba(80, 100, 150, 0.8);
                border-color: rgba(100, 180, 255, 0.5);
            }

            .cb-btn-primary {
                background: linear-gradient(135deg, rgba(60, 120, 200, 0.8) 0%, rgba(80, 100, 180, 0.8) 100%);
                border-color: rgba(100, 180, 255, 0.5);
            }

            .cb-btn-primary:hover {
                background: linear-gradient(135deg, rgba(80, 140, 220, 0.9) 0%, rgba(100, 120, 200, 0.9) 100%);
                box-shadow: 0 0 15px rgba(100, 180, 255, 0.4);
            }

            .cb-btn-small {
                padding: 6px 10px;
                font-size: 11px;
            }

            .cb-badge {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                background: rgba(100, 150, 255, 0.3);
                border-radius: 10px;
                padding: 2px 8px;
                font-size: 11px;
                font-weight: 600;
                color: #a0c0ff;
                min-width: 20px;
            }

            .scope-section {
                flex-direction: row;
                align-items: center;
                gap: 8px;
            }

            .scope-section label {
                align-self: center;
            }

            .actions-section {
                flex-direction: row;
                gap: 8px;
                margin-left: auto;
            }

            .groups-section {
                flex-direction: row;
                gap: 6px;
                flex-wrap: wrap;
                max-width: 300px;
            }

            .group-chip {
                display: inline-flex;
                align-items: center;
                gap: 6px;
                background: rgba(40, 50, 70, 0.8);
                border: 1px solid rgba(100, 150, 255, 0.3);
                border-radius: 14px;
                padding: 4px 10px;
                font-size: 11px;
                color: #c0d0ff;
                cursor: pointer;
                transition: all 0.2s;
            }

            .group-chip:hover {
                background: rgba(60, 70, 100, 0.9);
                border-color: rgba(100, 180, 255, 0.5);
            }

            .group-chip .group-color {
                width: 10px;
                height: 10px;
                border-radius: 50%;
            }

            .group-chip .group-count {
                font-weight: 600;
                color: #80a0ff;
            }

            .group-chip .group-remove {
                color: rgba(255, 100, 100, 0.6);
                font-weight: bold;
                margin-left: 4px;
            }

            .group-chip .group-remove:hover {
                color: rgba(255, 100, 100, 1);
            }

            .cb-toggle {
                position: absolute;
                top: -24px;
                right: 20px;
                background: rgba(30, 40, 60, 0.95);
                border: 1px solid rgba(100, 150, 255, 0.3);
                border-bottom: none;
                border-radius: 8px 8px 0 0;
                padding: 4px 12px;
                color: #80a0ff;
                cursor: pointer;
                font-size: 12px;
            }

            .cb-toggle:hover {
                background: rgba(40, 50, 70, 0.95);
            }

            .control-bar.collapsed .cb-toggle .chevron {
                transform: rotate(180deg);
            }

            .chevron {
                display: inline-block;
                transition: transform 0.3s;
            }

            /* Stats display */
            .cb-stats {
                display: flex;
                gap: 12px;
                font-size: 11px;
                color: rgba(150, 180, 255, 0.7);
            }

            .cb-stat {
                display: flex;
                gap: 4px;
            }

            .cb-stat-value {
                color: #80c0ff;
                font-weight: 600;
            }
        `;

        document.head.appendChild(style);
    }

    function attachListeners() {
        // Toggle collapse
        const toggleBtn = document.getElementById('cb-toggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', toggle);
        }

        // Scope change
        const scopeSelect = document.getElementById('cb-scope');
        if (scopeSelect) {
            scopeSelect.addEventListener('change', (e) => {
                _config.scope = e.target.value;
                updateNodeCount();
            });
        }

        // Source change
        const sourceSelect = document.getElementById('cb-source');
        if (sourceSelect) {
            sourceSelect.addEventListener('change', (e) => {
                _config.source = e.target.value;
            });
        }

        // Target change
        const targetSelect = document.getElementById('cb-target');
        if (targetSelect) {
            targetSelect.addEventListener('change', (e) => {
                _config.target = e.target.value;
            });
        }

        // Scale change
        const scaleSelect = document.getElementById('cb-scale');
        if (scaleSelect) {
            scaleSelect.addEventListener('change', (e) => {
                _config.scale = e.target.value;
            });
        }

        // Apply button
        const applyBtn = document.getElementById('cb-apply');
        if (applyBtn) {
            applyBtn.addEventListener('click', applyMapping);
        }

        // Reset button
        const resetBtn = document.getElementById('cb-reset');
        if (resetBtn) {
            resetBtn.addEventListener('click', resetMapping);
        }

        // Add group button
        const addGroupBtn = document.getElementById('cb-add-group');
        if (addGroupBtn) {
            addGroupBtn.addEventListener('click', createGroupFromSelection);
        }

        // Update node count periodically
        setInterval(updateNodeCount, 1000);
    }

    // =========================================================================
    // GROUP MANAGEMENT
    // =========================================================================

    const GROUP_COLORS = [
        '#4a9eff', '#ff6b6b', '#51cf66', '#ffd43b',
        '#cc5de8', '#20c997', '#ff922b', '#748ffc'
    ];

    function createGroupFromSelection() {
        const selectedIds = getSelectedNodeIds();
        if (selectedIds.length === 0) {
            showToast('Select nodes first to create a group');
            return;
        }

        _groupCounter++;
        const groupId = `group-${_groupCounter}`;
        const color = GROUP_COLORS[(_groupCounter - 1) % GROUP_COLORS.length];

        const group = {
            id: groupId,
            name: `Group ${_groupCounter}`,
            nodeIds: [...selectedIds],
            color: color
        };

        _groups.push(group);
        updateGroupsUI();
        showToast(`Created ${group.name} with ${selectedIds.length} nodes`);
    }

    function removeGroup(groupId) {
        _groups = _groups.filter(g => g.id !== groupId);
        updateGroupsUI();
    }

    function updateGroupsUI() {
        // Update dropdown
        const optgroup = document.getElementById('cb-groups-optgroup');
        if (optgroup) {
            optgroup.innerHTML = _groups.map(g =>
                `<option value="group:${g.id}">${g.name} (${g.nodeIds.length})</option>`
            ).join('');
        }

        // Update chips display
        const display = document.getElementById('cb-groups-display');
        if (display) {
            display.innerHTML = _groups.map(g => `
                <div class="group-chip" data-group="${g.id}">
                    <span class="group-color" style="background: ${g.color}"></span>
                    <span class="group-name">${g.name}</span>
                    <span class="group-count">${g.nodeIds.length}</span>
                    <span class="group-remove" onclick="CONTROL_BAR.removeGroup('${g.id}')">&times;</span>
                </div>
            `).join('');
        }
    }

    // =========================================================================
    // MAPPING APPLICATION
    // =========================================================================

    function getTargetNodes() {
        const dm = typeof DATA !== 'undefined' ? DATA : null;
        const allNodes = dm?.getNodes ? dm.getNodes() : (typeof graphNodes !== 'undefined' ? graphNodes : []);

        if (_config.scope === 'all') {
            return allNodes;
        }

        if (_config.scope === 'selection') {
            const selectedIds = getSelectedNodeIds();
            return allNodes.filter(n => selectedIds.includes(n.id));
        }

        if (_config.scope.startsWith('group:')) {
            const groupId = _config.scope.replace('group:', '');
            const group = _groups.find(g => g.id === groupId);
            if (group) {
                return allNodes.filter(n => group.nodeIds.includes(n.id));
            }
        }

        return [];
    }

    function applyMapping() {
        const nodes = getTargetNodes();
        if (nodes.length === 0) {
            showToast('No nodes to map. Select nodes or change scope.');
            return;
        }

        const sourceKey = _config.source;
        const targetKey = _config.target;
        const scaleFn = SCALES[_config.scale] || SCALES.linear;
        const targetInfo = VISUAL_TARGETS[targetKey];

        // Get value range
        const values = nodes.map(n => getNodeValue(n, sourceKey)).filter(v => v !== null && v !== undefined);
        if (values.length === 0) {
            showToast(`No data for "${sourceKey}" on selected nodes`);
            return;
        }

        const sourceInfo = DATA_SOURCES[sourceKey];
        const isDiscrete = sourceInfo?.type === 'discrete' || sourceInfo?.type === 'boolean';

        let dataMin, dataMax;
        if (!isDiscrete) {
            dataMin = Math.min(...values);
            dataMax = Math.max(...values);
        }

        // Apply to each node
        nodes.forEach(node => {
            const rawValue = getNodeValue(node, sourceKey);
            if (rawValue === null || rawValue === undefined) return;

            let mappedValue;
            if (isDiscrete) {
                // Map discrete values to evenly spaced range
                const uniqueValues = sourceInfo.values || [...new Set(values)];
                const idx = uniqueValues.indexOf(rawValue);
                mappedValue = idx >= 0 ? idx / Math.max(1, uniqueValues.length - 1) : 0.5;
            } else {
                mappedValue = scaleFn(rawValue, dataMin, dataMax);
            }

            // Map to target range
            const [tMin, tMax] = targetInfo.range;
            const targetValue = tMin + mappedValue * (tMax - tMin);

            applyToNode(node, targetKey, targetValue);
        });

        // Refresh graph
        if (typeof REFRESH !== 'undefined') {
            REFRESH.throttled();
        } else if (typeof Graph !== 'undefined' && Graph) {
            Graph.refresh();
        }

        showToast(`Mapped ${sourceKey} -> ${targetKey} on ${nodes.length} nodes`);
        console.log(`[CONTROL_BAR] Applied: ${sourceKey} -> ${targetKey}, scale=${_config.scale}, nodes=${nodes.length}`);
    }

    function getNodeValue(node, key) {
        // Direct property
        if (node[key] !== undefined) return node[key];

        // Nested in dimensions
        if (node.dimensions && node.dimensions[key] !== undefined) {
            return node.dimensions[key];
        }

        // Check common dimension mappings
        const dimMap = {
            'tier': 'D1_TIER',
            'ring': 'D2_RING',
            'layer': 'D2_LAYER',
            'effect': 'D6_EFFECT'
        };

        if (dimMap[key] && node.dimensions) {
            return node.dimensions[dimMap[key]];
        }

        return null;
    }

    function applyToNode(node, targetKey, value) {
        switch (targetKey) {
            case 'nodeSize':
                node.val = value;
                break;

            case 'hue':
                const currentColor = node.color || 'hsl(200, 70%, 50%)';
                node.color = setHSLComponent(currentColor, 'h', value);
                break;

            case 'saturation':
                node.color = setHSLComponent(node.color || 'hsl(200, 70%, 50%)', 's', value);
                break;

            case 'lightness':
                node.color = setHSLComponent(node.color || 'hsl(200, 70%, 50%)', 'l', value);
                break;

            case 'opacity':
                node.opacity = value;
                // Update color alpha if using rgba
                if (node.color && !node.color.startsWith('hsl')) {
                    node.color = setAlpha(node.color, value);
                }
                break;

            case 'xPosition':
                node.fx = value;
                break;

            case 'yPosition':
                node.fy = value;
                break;

            case 'zPosition':
                node.fz = value;
                break;

            case 'radius':
                // Position on a circle at given radius
                const angle = (node.fileIdx || Math.random() * 100) * 0.618 * Math.PI * 2;
                node.fx = Math.cos(angle) * value;
                node.fy = Math.sin(angle) * value;
                break;

            case 'charge':
                node.__charge = value;
                break;

            case 'mass':
                node.__mass = value;
                break;

            case 'pulseSpeed':
                node.__pulseSpeed = value;
                break;

            default:
                node[targetKey] = value;
        }
    }

    function setHSLComponent(colorStr, component, value) {
        // Parse existing HSL or convert
        let h = 200, s = 70, l = 50;

        const hslMatch = colorStr.match(/hsl\((\d+),\s*(\d+)%?,\s*(\d+)%?\)/);
        if (hslMatch) {
            h = parseInt(hslMatch[1]);
            s = parseInt(hslMatch[2]);
            l = parseInt(hslMatch[3]);
        }

        switch (component) {
            case 'h': h = value; break;
            case 's': s = value; break;
            case 'l': l = value; break;
        }

        return `hsl(${Math.round(h)}, ${Math.round(s)}%, ${Math.round(l)}%)`;
    }

    function setAlpha(colorStr, alpha) {
        // Simple alpha injection
        if (colorStr.startsWith('rgba')) {
            return colorStr.replace(/[\d.]+\)$/, `${alpha})`);
        }
        if (colorStr.startsWith('rgb')) {
            return colorStr.replace('rgb', 'rgba').replace(')', `, ${alpha})`);
        }
        return colorStr;
    }

    function resetMapping() {
        // Clear fixed positions
        const nodes = getTargetNodes();
        nodes.forEach(n => {
            delete n.fx;
            delete n.fy;
            delete n.fz;
            delete n.__charge;
            delete n.__mass;
            delete n.__pulseSpeed;
        });

        // Reheat simulation
        if (typeof Graph !== 'undefined' && Graph) {
            Graph.d3ReheatSimulation();
        }

        showToast('Reset node positions and custom properties');
    }

    // =========================================================================
    // HELPERS
    // =========================================================================

    function getSelectedNodeIds() {
        if (typeof SELECT !== 'undefined' && SELECT.getSelectedNodes) {
            return SELECT.getSelectedNodes().map(n => n.id);
        }
        if (typeof SELECTED_NODE_IDS !== 'undefined') {
            return Array.from(SELECTED_NODE_IDS);
        }
        return [];
    }

    function updateNodeCount() {
        const badge = document.getElementById('cb-node-count');
        if (!badge) return;

        const nodes = getTargetNodes();
        badge.textContent = nodes.length;
    }

    function showToast(msg) {
        if (typeof window.showToast === 'function') {
            window.showToast(msg);
        } else {
            console.log(`[CONTROL_BAR] ${msg}`);
        }
    }

    function toggle() {
        if (_container) {
            _container.classList.toggle('collapsed');
            _visible = !_container.classList.contains('collapsed');
        }
    }

    function show() {
        if (_container) {
            _container.classList.remove('collapsed');
            _visible = true;
        }
    }

    function hide() {
        if (_container) {
            _container.classList.add('collapsed');
            _visible = false;
        }
    }

    // =========================================================================
    // INIT
    // =========================================================================

    function init() {
        createUI();
        updateNodeCount();
        console.log('[CONTROL_BAR] Initialized');
    }

    // =========================================================================
    // PUBLIC API
    // =========================================================================

    return {
        init,
        toggle,
        show,
        hide,
        applyMapping,
        resetMapping,
        createGroupFromSelection,
        removeGroup,
        get visible() { return _visible; },
        get config() { return _config; },
        get groups() { return _groups; },
        DATA_SOURCES,
        VISUAL_TARGETS,
        SCALES
    };

})();

// Auto-init when DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => CONTROL_BAR.init());
} else {
    // Small delay to ensure other modules are loaded
    setTimeout(() => CONTROL_BAR.init(), 100);
}
