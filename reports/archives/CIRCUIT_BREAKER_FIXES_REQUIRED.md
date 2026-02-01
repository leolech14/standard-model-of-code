# Circuit Breaker - Required Fixes

**Status:** 3 Critical Issues + 5 Enhancement Opportunities
**Effort:** ~2-3 hours to fix all critical issues
**Priority:** Fix these before next deployment

---

## FIX 1: toggle-arrows Validation Always Passes

**File:** `src/core/viz/assets/modules/circuit-breaker.js`
**Line Range:** 272-300
**Severity:** HIGH - Test produces false positive
**Effort:** 10 minutes

### Current Code (BROKEN)
```javascript
{
    name: 'toggle-arrows',
    type: 'toggle',
    elementId: 'cfg-toggle-arrows',
    statePath: 'APPEARANCE_STATE.showArrows',
    trigger: (el) => { el?.click(); },
    validate: (el) => {
        return {
            passed: el?.classList.contains('active') !== undefined,  // ← ALWAYS TRUE!
            expected: 'toggled',
            actual: el?.classList.contains('active') ? 'toggled' : 'not-toggled',
            stateExists: true
        };
    },
    fix: 'Ensure toggle click handler toggles .active class and calls Graph.linkDirectionalArrowLength()'
}
```

### Problem
The validation checks `!== undefined`, which is always true for any class state. The test passes even when the toggle doesn't actually toggle.

### Fix Required
Capture state BEFORE click, compare AFTER click:

```javascript
{
    name: 'toggle-arrows',
    type: 'toggle',
    elementId: 'cfg-toggle-arrows',
    statePath: 'APPEARANCE_STATE.showArrows',
    trigger: (el) => {
        window._arrowsActiveBefore = el?.classList.contains('active') ?? false;
        el?.click();
    },
    validate: (el) => {
        if (!el) return { passed: false, expected: 'element found', actual: 'element not found' };
        const isActiveNow = el.classList.contains('active');
        const toggled = isActiveNow !== window._arrowsActiveBefore;
        return {
            passed: toggled,
            expected: 'toggled',
            actual: toggled ? 'toggled' : 'no change',
            stateExists: !!window._arrowsActiveBefore !== undefined
        };
    },
    fix: 'Ensure toggle click handler toggles .active class - if failing, check app.js line 2274 for click handler'
}
```

### Verification
After fix:
```javascript
CIRCUIT.test('toggle-arrows').then(r => console.log(r.passed ? 'PASS' : 'FAIL'));
```

---

## FIX 2: physics-charge Tests Wrong State Object

**File:** `src/core/viz/assets/modules/circuit-breaker.js`
**Line Range:** 302-355
**Severity:** HIGH - Test validates non-existent state
**Effort:** 15 minutes

### Current Code (BROKEN)
```javascript
{
    name: 'physics-charge',
    type: 'slider',
    elementId: 'physics-charge',
    statePath: 'PHYSICS_STATE.charge',  // ← DOESN'T EXIST
    trigger: (el) => { el?.value = '-150'; el?.dispatchEvent(new Event('input', { bubbles: true })); },
    validate: (el) => {
        const stateResult = getStateValue('PHYSICS_STATE.charge');  // ← ALWAYS UNDEFINED
        return {
            passed: stateResult.exists && stateResult.value === '-150',
            expected: 'PHYSICS_STATE.charge = -150',
            actual: stateResult.value,
            stateExists: stateResult.exists
        };
    },
    fix: 'Ensure slider change calls window.Graph.d3Force("charge", value)'
}
```

### Problem
The app.js actually calls `Graph.d3Force()` directly (line 2235), it doesn't update `PHYSICS_STATE.charge`. The test looks for state that never gets set.

### Evidence
**In `app.js` line 2235:**
```javascript
document.getElementById('physics-charge').addEventListener('change', (e) => {
    Graph.d3Force('charge', Number(e.target.value));  // ← Direct call, no state update
});
```

**PHYSICS_STATE never updated.** Test can't detect this because it checks the wrong place.

### Fix Required

**Option A: Simple - Just call Graph API (Recommended)**
```javascript
{
    name: 'physics-charge',
    type: 'slider',
    elementId: 'physics-charge',
    graphMethod: 'Graph.d3Force',
    trigger: (el) => {
        window._chargeCallCount = 0;
        const originalMethod = Graph.d3Force;
        window._graphForceLastValue = null;
        Graph.d3Force = function(name, value) {
            if (name === 'charge') {
                window._graphForceLastValue = value;
                window._chargeCallCount++;
            }
            return originalMethod.call(this, name, value);
        };
        el?.value = '-150';
        el?.dispatchEvent(new Event('input', { bubbles: true }));
        Graph.d3Force = originalMethod; // Restore
    },
    validate: (el) => {
        return {
            passed: window._chargeCallCount > 0 && window._graphForceLastValue === -150,
            expected: 'Graph.d3Force("charge", -150) called',
            actual: window._chargeCallCount > 0 ? 'called with ' + window._graphForceLastValue : 'not called',
            stateExists: window._chargeCallCount > 0
        };
    },
    fix: 'Slider should trigger Graph.d3Force("charge", value) - check app.js line 2235'
}
```

**Option B: Create PHYSICS_STATE bridge (Architectural fix)**
Add this to app.js after physics-charge slider binding:
```javascript
document.getElementById('physics-charge').addEventListener('change', (e) => {
    const value = Number(e.target.value);
    PHYSICS_STATE.charge = value;  // ← ADD THIS LINE
    Graph.d3Force('charge', value);
});
```

Then revert circuit-breaker.js to simple state check.

### Recommendation
Use **Option A** immediately (doesn't require app.js changes). Option B is architectural cleanup for next refactoring.

---

## FIX 3: dimension-toggle Tests Phantom Element ID

**File:** `src/core/viz/assets/modules/circuit-breaker.js`
**Line Range:** 356-387
**Severity:** MEDIUM - Test reports false negative
**Effort:** 5 minutes

### Current Code (BROKEN)
```javascript
{
    name: 'dimension-toggle',
    type: 'button',
    elementId: 'btn-dimension',  // ← DOESN'T EXIST
    statePath: 'IS_3D',
    trigger: (el) => { el?.click(); },
    validate: (el) => {
        return {
            passed: el !== null && el !== undefined,
            expected: 'active',
            actual: el?.classList.contains('active') ? 'active' : 'inactive',
            stateExists: true
        };
    },
    fix: 'Check template.html for actual button ID'
}
```

### Problem
Actual button ID in template.html:1316 is `btn-2d`, not `btn-dimension`.

### Evidence
**In `template.html` line 1316:**
```html
<button id="btn-2d" class="dim-toggle" data-dimension="2d">
```

Test searches for phantom ID and always fails.

### Fix Required
Change one line:

```javascript
{
    name: 'dimension-toggle',
    type: 'button',
    elementId: 'btn-2d',  // ← CORRECTED
    statePath: 'IS_3D',
    trigger: (el) => { el?.click(); },
    validate: (el) => {
        if (!el) return { passed: false, expected: 'element found', actual: 'element not found', stateExists: false };
        const isActive = el.classList.contains('active');
        return {
            passed: isActive,
            expected: 'active',
            actual: isActive ? 'active' : 'inactive',
            stateExists: true
        };
    },
    fix: 'Dimension toggle is #btn-2d - switches IS_3D between true/false'
}
```

---

## ENHANCEMENTS: 5 Quick Wins

### Enhancement 1: Add Overall Test Suite Runner
**Location:** End of CIRCUIT IIFE
**Time:** 10 minutes
**Value:** Better debugging output

```javascript
// Add to public API:
function status() {
    const results = report();
    const passed = Array.from(results.values()).filter(r => r.passed).length;
    const total = results.size;
    return {
        summary: `${passed}/${total} tests passing`,
        passRate: (passed / total * 100).toFixed(1) + '%',
        details: Array.from(results.entries())
            .filter(([_, r]) => !r.passed)
            .map(([name, r]) => ({ name, error: r.error, fix: r.fix }))
    };
}
```

### Enhancement 2: Add Control Discovery
**Location:** Near `inventory()` function
**Time:** 15 minutes
**Value:** Auto-detect controls from template instead of hardcoding

```javascript
function discoverControls() {
    const template = document.querySelector('template');
    if (!template) return [];

    const controls = [];
    template.content.querySelectorAll('[id^="cfg-"], [id^="btn-"], [id^="physics-"], [id^="layout-"], [id^="color-"]')
        .forEach(el => {
            controls.push({
                id: el.id,
                type: el.tagName.toLowerCase(),
                inputType: el.type || el.className,
                dataAttributes: Object.fromEntries([...el.attributes]
                    .filter(a => a.name.startsWith('data-'))
                    .map(a => [a.name, a.value]))
            });
        });
    return controls;
}
```

### Enhancement 3: Add Timing Enforcement
**Location:** `runTest()` function
**Time:** 10 minutes
**Value:** Prevent hanging tests

```javascript
async function runTest(testDef) {
    const timeout = testDef.timeout || 500;
    try {
        return await Promise.race([
            executeTest(testDef),
            new Promise((_, reject) =>
                setTimeout(() => reject({
                    passed: false,
                    error: 'TIMEOUT after ' + timeout + 'ms',
                    fix: 'Test took too long - check for async issues in trigger or validate'
                }), timeout)
            )
        ]);
    } catch (e) {
        return {
            passed: false,
            error: e.message || e,
            trace: [e.stack]
        };
    }
}
```

### Enhancement 4: Add Graph Method Spying
**Location:** Module initialization
**Time:** 20 minutes
**Value:** Verify visual effects, not just state changes

```javascript
function spyOnGraphMethods() {
    if (!window.Graph) return null;
    const originalMethods = {};
    const callLog = {};

    const methodsToSpy = [
        'linkOpacity', 'linkWidth', 'nodeColor', 'nodeSize', 'nodeMaterial',
        'd3Force', 'postProcessing', 'cameraPosition'
    ];

    methodsToSpy.forEach(method => {
        if (typeof Graph[method] === 'function') {
            originalMethods[method] = Graph[method];
            callLog[method] = [];
            Graph[method] = function(...args) {
                callLog[method].push({
                    timestamp: Date.now(),
                    args: args,
                    caller: arguments.callee.caller?.name || 'unknown'
                });
                return originalMethods[method].apply(this, args);
            };
        }
    });

    return { originalMethods, callLog, restore: () => {
        methodsToSpy.forEach(m => { Graph[m] = originalMethods[m]; });
    }};
}

window._graphSpy = spyOnGraphMethods();
```

### Enhancement 5: Add Browser Console Quick Commands
**Location:** Module initialization or global scope
**Time:** 10 minutes
**Value:** Better CLI experience

```javascript
// At module load
window.CIRCUIT_CLI = {
    'test-all': () => CIRCUIT.runAll(),
    'status': () => {
        const r = CIRCUIT.report();
        const failures = [...r.entries()].filter(([_, v]) => !v.passed);
        return failures.length > 0
            ? failures.map(([n, v]) => `✗ ${n}: ${v.error}`).join('\n')
            : 'All tests passing!';
    },
    'controls': () => CIRCUIT.inventoryJSON(),
    'help': () => Object.keys(window.CIRCUIT_CLI).join(', ')
};

// Type in console:
// CIRCUIT_CLI['test-all']()
// CIRCUIT_CLI.status()
```

---

## Testing the Fixes

### Before Fixes
```javascript
// Run all tests
CIRCUIT.runAll();
// Expected: 3 failures (toggle-arrows false positive, physics-charge missing, dimension-toggle not found)
```

### After Fixes
```javascript
// Run all tests
CIRCUIT.runAll();
// Expected: all pass (if you fixed the 3 issues)

// Verify specific tests
CIRCUIT.test('toggle-arrows').then(r => console.log(r.passed));
CIRCUIT.test('physics-charge').then(r => console.log(r.passed));
CIRCUIT.test('dimension-toggle').then(r => console.log(r.passed));
```

### Regression Test
After fixing:
```bash
# Run validation from command line
python tools/validate_ui.py collider_report.html --verbose
```

---

## Implementation Checklist

### Critical (MUST FIX)
- [ ] Fix toggle-arrows validation (line 272) - 10 min
- [ ] Fix physics-charge state path (line 302) - 15 min
- [ ] Fix dimension-toggle element ID (line 356) - 5 min
- [ ] Test all 3 fixes in browser console - 10 min

### Quick Wins (SHOULD DO THIS SPRINT)
- [ ] Add Enhancement 1: Test status runner - 10 min
- [ ] Add Enhancement 2: Control discovery - 15 min
- [ ] Add Enhancement 4: Graph method spying - 20 min
- [ ] Update docs/OPEN_CONCERNS.md with fixes applied

### Later (Next Sprint)
- [ ] Enhancement 3: Timing enforcement - 10 min
- [ ] Enhancement 5: CLI shortcuts - 10 min
- [ ] Add P0 control tests (node-color, edge-mode, layouts)
- [ ] Archive this document to docs/CLOSED/

---

## Time Estimate

| Task | Time |
|------|------|
| Fix 3 critical bugs | 30 min |
| Test & verify | 15 min |
| Add Enhancement 1 | 10 min |
| Add Enhancement 2 | 15 min |
| Add Enhancement 4 | 20 min |
| Commit & document | 10 min |
| **TOTAL** | **100 min (1.7 hours)** |

**Can be done in single focused session.**

---

## Success Criteria

- [ ] CIRCUIT.runAll() returns 100% pass rate (87/87 tests)
- [ ] CIRCUIT.diagnose() returns empty array
- [ ] CIRCUIT.inventory() shows all 87 controls
- [ ] python tools/validate_ui.py runs without errors
- [ ] Browser console commands execute successfully
- [ ] No regression in module-loaded tests

---

Generated: 2026-01-25 by Claude Code CLI
