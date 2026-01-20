/**
 * ═══════════════════════════════════════════════════════════════════════════
 * PHYSICS MODULE - Force simulation controls
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * Physics presets, sliders, and force parameter management.
 * Depends on: Graph, PHYSICS_STATE, PHYSICS_PRESETS (globals)
 *
 * @module PHYSICS
 * @version 1.0.0
 */

window.PHYSICS = (function() {
    'use strict';

    // ═══════════════════════════════════════════════════════════════════════
    // APPLY PHYSICS STATE
    // ═══════════════════════════════════════════════════════════════════════

    function applyPhysicsState() {
        const Graph = window.Graph;
        const PHYSICS_STATE = window.PHYSICS_STATE;
        if (!Graph) return;
        try {
            Graph.d3Force('charge')?.strength(PHYSICS_STATE.charge);
            Graph.d3Force('link')?.distance(PHYSICS_STATE.linkDistance);
            Graph.d3Force('center')?.strength(PHYSICS_STATE.centerStrength);
            Graph.d3VelocityDecay?.(PHYSICS_STATE.velocityDecay);
            Graph.d3ReheatSimulation();
        } catch (e) {
            console.warn('[Physics] Could not apply:', e.message);
        }
    }

    // ═══════════════════════════════════════════════════════════════════════
    // APPLY PHYSICS PRESET
    // ═══════════════════════════════════════════════════════════════════════

    function applyPhysicsPreset(presetName) {
        const PHYSICS_STATE = window.PHYSICS_STATE;
        const PHYSICS_PRESETS = window.PHYSICS_PRESETS;
        const preset = PHYSICS_PRESETS[presetName];
        if (!preset) return;
        Object.assign(PHYSICS_STATE, {
            charge: preset.charge,
            linkDistance: preset.linkDistance,
            centerStrength: preset.centerStrength,
            velocityDecay: preset.velocityDecay
        });
        applyPhysicsState();
        updatePhysicsSliders();
        window.showModeToast(`Physics: ${preset.label}`);
    }

    // ═══════════════════════════════════════════════════════════════════════
    // UPDATE PHYSICS SLIDERS
    // ═══════════════════════════════════════════════════════════════════════

    function updatePhysicsSliders() {
        const PHYSICS_STATE = window.PHYSICS_STATE;
        const sliders = {
            'physics-charge': PHYSICS_STATE.charge,
            'physics-link-distance': PHYSICS_STATE.linkDistance,
            'physics-center': PHYSICS_STATE.centerStrength,
            'physics-damping': PHYSICS_STATE.velocityDecay
        };
        for (const [id, value] of Object.entries(sliders)) {
            const input = document.getElementById(id);
            const display = document.getElementById(id + '-value');
            if (input) input.value = value;
            if (display) display.textContent = typeof value === 'number' && value % 1 !== 0 ? value.toFixed(2) : value;
        }
    }

    // ═══════════════════════════════════════════════════════════════════════
    // BUILD PHYSICS CONTROLS UI
    // ═══════════════════════════════════════════════════════════════════════

    function buildPhysicsControls(containerId) {
        const PHYSICS_STATE = window.PHYSICS_STATE;
        const PHYSICS_PRESETS = window.PHYSICS_PRESETS;
        const container = document.getElementById(containerId);
        if (!container) return;

        // Preset buttons
        const presetRow = document.createElement('div');
        presetRow.className = 'physics-presets';
        presetRow.style.cssText = 'display:flex;gap:4px;margin-bottom:8px;flex-wrap:wrap;';
        Object.entries(PHYSICS_PRESETS).forEach(([key, preset]) => {
            const btn = document.createElement('button');
            btn.className = 'preset-btn physics-preset-btn';
            btn.textContent = preset.label;
            btn.style.cssText = 'font-size:9px;padding:2px 6px;';
            btn.onclick = () => applyPhysicsPreset(key);
            presetRow.appendChild(btn);
        });
        container.appendChild(presetRow);

        // Sliders
        const sliderDefs = [
            {
                id: 'physics-charge',
                label: 'REPULSION',
                min: -500,
                max: 50,
                step: 10,
                value: PHYSICS_STATE.charge,
                onChange: (val) => { PHYSICS_STATE.charge = val; applyPhysicsState(); }
            },
            {
                id: 'physics-link-distance',
                label: 'LINK DIST',
                min: 10,
                max: 200,
                step: 5,
                value: PHYSICS_STATE.linkDistance,
                onChange: (val) => { PHYSICS_STATE.linkDistance = val; applyPhysicsState(); }
            },
            {
                id: 'physics-center',
                label: 'CENTER PULL',
                min: 0,
                max: 0.3,
                step: 0.01,
                value: PHYSICS_STATE.centerStrength,
                onChange: (val) => { PHYSICS_STATE.centerStrength = val; applyPhysicsState(); }
            },
            {
                id: 'physics-damping',
                label: 'DAMPING',
                min: 0,
                max: 1,
                step: 0.05,
                value: PHYSICS_STATE.velocityDecay,
                onChange: (val) => { PHYSICS_STATE.velocityDecay = val; applyPhysicsState(); }
            }
        ];

        sliderDefs.forEach(def => {
            const wrapper = document.createElement('div');
            wrapper.className = 'slider-row';

            const header = document.createElement('div');
            header.className = 'slider-header';
            const label = document.createElement('span');
            label.className = 'slider-label';
            label.textContent = def.label;
            const valueDisplay = document.createElement('span');
            valueDisplay.className = 'slider-value';
            valueDisplay.id = def.id + '-value';
            valueDisplay.textContent = def.step < 1 ? def.value.toFixed(2) : def.value;
            header.appendChild(label);
            header.appendChild(valueDisplay);

            const input = document.createElement('input');
            input.type = 'range';
            input.className = 'slider-input';
            input.id = def.id;
            input.min = def.min;
            input.max = def.max;
            input.step = def.step;
            input.value = def.value;
            input.oninput = () => {
                const val = parseFloat(input.value);
                valueDisplay.textContent = def.step < 1 ? val.toFixed(2) : val;
                def.onChange(val);
            };

            wrapper.appendChild(header);
            wrapper.appendChild(input);
            container.appendChild(wrapper);
        });

        console.log('[Physics] Controls initialized');
    }

    // ═══════════════════════════════════════════════════════════════════════
    // MODULE EXPORT
    // ═══════════════════════════════════════════════════════════════════════

    return {
        applyState: applyPhysicsState,
        applyPreset: applyPhysicsPreset,
        updateSliders: updatePhysicsSliders,
        buildControls: buildPhysicsControls
    };
})();

// ═══════════════════════════════════════════════════════════════════════════
// BACKWARD COMPATIBILITY SHIMS
// ═══════════════════════════════════════════════════════════════════════════

window.applyPhysicsState = PHYSICS.applyState;
window.applyPhysicsPreset = PHYSICS.applyPreset;
window.updatePhysicsSliders = PHYSICS.updateSliders;
window.buildPhysicsControls = PHYSICS.buildControls;

console.log('[Module] PHYSICS loaded - 4 functions');
