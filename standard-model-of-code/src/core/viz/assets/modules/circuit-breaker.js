/**
 * CIRCUIT BREAKER MODULE
 *
 * Runtime self-test system that validates all UI controls work.
 * Runs a sequence of interactions and checks if they produce effects.
 *
 * Usage:
 *   CIRCUIT.runAll()           // Run all tests
 *   CIRCUIT.test('edge-opacity') // Test specific control
 *   CIRCUIT.report()           // Get test results
 */

const CIRCUIT = (function() {
    'use strict';

    // Test results storage
    const _results = new Map();
    let _running = false;

    // =========================================================================
    // TEST DEFINITIONS
    // Each test: { name, type, trigger, validate, cleanup? }
    // =========================================================================

    const TESTS = [
        // --- EDGE CONTROLS ---
        {
            name: 'edge-opacity',
            type: 'slider',
            elementId: 'cfg-edge-opacity',
            trigger: (el) => {
                el.value = '0.8';
                el.dispatchEvent(new Event('input', { bubbles: true }));
            },
            validate: () => {
                return typeof APPEARANCE_STATE !== 'undefined' &&
                       APPEARANCE_STATE.edgeOpacity === 0.8;
            },
            cleanup: (el) => {
                el.value = '0.6';
                el.dispatchEvent(new Event('input', { bubbles: true }));
            }
        },
        {
            name: 'edge-width',
            type: 'slider',
            elementId: 'cfg-edge-width',
            trigger: (el) => {
                el.value = '3.0';
                el.dispatchEvent(new Event('input', { bubbles: true }));
            },
            validate: () => {
                return typeof APPEARANCE_STATE !== 'undefined' &&
                       APPEARANCE_STATE.edgeWidth === 3.0;
            },
            cleanup: (el) => {
                el.value = '1.5';
                el.dispatchEvent(new Event('input', { bubbles: true }));
            }
        },
        {
            name: 'edge-curvature',
            type: 'slider',
            elementId: 'cfg-edge-curve',
            trigger: (el) => {
                el.value = '0.5';
                el.dispatchEvent(new Event('input', { bubbles: true }));
            },
            validate: () => {
                return typeof APPEARANCE_STATE !== 'undefined' &&
                       APPEARANCE_STATE.edgeCurvature === 0.5;
            },
            cleanup: (el) => {
                el.value = '0';
                el.dispatchEvent(new Event('input', { bubbles: true }));
            }
        },

        // --- NODE CONTROLS ---
        {
            name: 'node-size',
            type: 'slider',
            elementId: 'cfg-node-size',
            trigger: (el) => {
                el.value = '8';
                el.dispatchEvent(new Event('input', { bubbles: true }));
            },
            validate: () => {
                return typeof APPEARANCE_STATE !== 'undefined' &&
                       APPEARANCE_STATE.nodeScale === 8;
            },
            cleanup: (el) => {
                el.value = '5';
                el.dispatchEvent(new Event('input', { bubbles: true }));
            }
        },
        {
            name: 'node-opacity',
            type: 'slider',
            elementId: 'cfg-node-opacity',
            trigger: (el) => {
                el.value = '0.5';
                el.dispatchEvent(new Event('input', { bubbles: true }));
            },
            validate: () => {
                return typeof APPEARANCE_STATE !== 'undefined' &&
                       APPEARANCE_STATE.nodeOpacity === 0.5;
            },
            cleanup: (el) => {
                el.value = '1';
                el.dispatchEvent(new Event('input', { bubbles: true }));
            }
        },

        // --- TOGGLES ---
        {
            name: 'toggle-arrows',
            type: 'toggle',
            elementId: 'cfg-toggle-arrows',
            trigger: (el) => {
                window._arrowsActiveBefore = el.classList.contains('active');
                el.click();
            },
            validate: () => {
                const el = document.getElementById('cfg-toggle-arrows');
                if (!el) return false;
                // Check if toggle state actually changed
                const isActiveNow = el.classList.contains('active');
                return isActiveNow !== window._arrowsActiveBefore;
            },
            cleanup: (el) => {
                // Toggle back to original state
                el.click();
                delete window._arrowsActiveBefore;
            }
        },

        // --- PHYSICS CONTROLS ---
        {
            name: 'physics-charge',
            type: 'slider',
            elementId: 'physics-charge',
            trigger: (el) => {
                const originalValue = el.value;
                el.value = '-200';
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el._originalValue = originalValue;
            },
            validate: () => {
                // NOTE: sidebar.js bypasses PHYSICS_STATE and calls Graph directly
                // So we validate via Graph API, not PHYSICS_STATE
                if (typeof Graph === 'undefined' || !Graph.d3Force) return false;
                const chargeForce = Graph.d3Force('charge');
                if (!chargeForce || !chargeForce.strength) return false;
                // d3 charge force stores strength as function, call it to get value
                const strength = chargeForce.strength();
                return strength === -200;
            },
            cleanup: (el) => {
                if (el._originalValue) {
                    el.value = el._originalValue;
                    el.dispatchEvent(new Event('input', { bubbles: true }));
                }
            }
        },

        // --- BUTTONS ---
        {
            name: 'btn-edge-mode',
            type: 'button',
            elementId: 'btn-edge-mode',
            trigger: (el) => {
                window._edgeModeBefore = typeof EDGE !== 'undefined' ? EDGE.mode : null;
                el.click();
            },
            validate: () => {
                if (typeof EDGE === 'undefined') return false;
                return EDGE.mode !== window._edgeModeBefore;
            },
            cleanup: () => {
                delete window._edgeModeBefore;
            }
        },
        // NOTE: btn-color-mode test REMOVED - element doesn't exist in template.html
        // Color mode is controlled via dropdown, not a button
        // See CIRCUIT_BREAKER_RECONNAISSANCE.md for details

        // --- DIMENSION TOGGLE ---
        {
            name: 'dimension-toggle',
            type: 'button',
            elementId: 'btn-2d',  // Fixed: was 'btn-dimension' which doesn't exist
            trigger: (el) => {
                window._is3dBefore = typeof IS_3D !== 'undefined' ? IS_3D : null;
                el.click();
            },
            validate: () => {
                // Check if IS_3D actually changed (may be async)
                if (typeof IS_3D === 'undefined') return false;
                return IS_3D !== window._is3dBefore;
            },
            cleanup: () => {
                // Toggle back
                const el = document.getElementById('btn-2d');
                if (el) el.click();
                delete window._is3dBefore;
            }
        },

        // --- VIEW MODE ---
        {
            name: 'view-mode-files',
            type: 'button',
            elementId: null, // Uses selector
            selector: '[data-mode="files"]',
            trigger: (el) => {
                el.click();
            },
            validate: () => {
                return typeof GRAPH_MODE !== 'undefined' && GRAPH_MODE === 'files';
            },
            cleanup: () => {
                const atomsBtn = document.querySelector('[data-mode="atoms"]');
                if (atomsBtn) atomsBtn.click();
            }
        }
    ];

    // =========================================================================
    // TEST RUNNER
    // =========================================================================

    async function runTest(testDef) {
        const result = {
            name: testDef.name,
            type: testDef.type,
            passed: false,
            error: null,
            elementFound: false
        };

        try {
            // Find element
            const el = testDef.elementId
                ? document.getElementById(testDef.elementId)
                : document.querySelector(testDef.selector);

            if (!el) {
                result.error = 'Element not found';
                return result;
            }
            result.elementFound = true;

            // Run trigger
            testDef.trigger(el);

            // Small delay for async effects
            await new Promise(r => setTimeout(r, 50));

            // Validate
            result.passed = testDef.validate();

            // Cleanup
            if (testDef.cleanup) {
                await new Promise(r => setTimeout(r, 50));
                testDef.cleanup(el);
            }

        } catch (err) {
            result.error = err.message;
            result.passed = false;
        }

        return result;
    }

    async function runAll() {
        if (_running) {
            console.warn('[CIRCUIT] Already running');
            return;
        }
        _running = true;
        _results.clear();

        console.log('%c[CIRCUIT] Starting control validation...', 'color: #4dd4ff; font-weight: bold');

        const startTime = performance.now();
        let passed = 0;
        let failed = 0;

        for (const test of TESTS) {
            const result = await runTest(test);
            _results.set(test.name, result);

            if (result.passed) {
                passed++;
                console.log(`  %c✓ ${test.name}`, 'color: #4ade80');
            } else {
                failed++;
                const reason = result.error || (!result.elementFound ? 'Element not found' : 'Validation failed');
                console.log(`  %c✗ ${test.name}: ${reason}`, 'color: #f87171');
            }

            // Small delay between tests
            await new Promise(r => setTimeout(r, 100));
        }

        const elapsed = (performance.now() - startTime).toFixed(0);
        const total = passed + failed;
        const pct = ((passed / total) * 100).toFixed(1);

        console.log('%c─────────────────────────────────────', 'color: #666');
        if (failed === 0) {
            console.log(`%c[CIRCUIT] ALL PASS: ${passed}/${total} controls (${elapsed}ms)`,
                'color: #4ade80; font-weight: bold');
        } else {
            console.log(`%c[CIRCUIT] ${passed}/${total} passed (${pct}%), ${failed} FAILED (${elapsed}ms)`,
                'color: #f87171; font-weight: bold');
        }

        _running = false;
        return { passed, failed, total, results: Object.fromEntries(_results) };
    }

    async function test(name) {
        const testDef = TESTS.find(t => t.name === name);
        if (!testDef) {
            console.error(`[CIRCUIT] Unknown test: ${name}`);
            return null;
        }
        const result = await runTest(testDef);
        _results.set(name, result);
        return result;
    }

    function report() {
        return Object.fromEntries(_results);
    }

    function listTests() {
        return TESTS.map(t => ({ name: t.name, type: t.type }));
    }

    // =========================================================================
    // PUBLIC API
    // =========================================================================

    return {
        runAll,
        test,
        report,
        listTests,
        get isRunning() { return _running; },
        TESTS
    };
})();

// Global shortcut
window.CIRCUIT = CIRCUIT;

console.log('[Module] CIRCUIT loaded - UI control validator');
