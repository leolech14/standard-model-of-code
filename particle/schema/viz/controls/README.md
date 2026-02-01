# UI Control Registry

## Overview

This directory contains the **Single Source of Truth** for all UI controls in the Collider visualization system.

- **CONTROL_REGISTRY.yaml** - Authoritative registry of all 160 UI controls
- **README.md** - This file

## Purpose

The Control Registry enforces strict governance over UI control addition:

1. **No control may be added to template.html without FIRST being registered here**
2. **Controls must flow through the authorization workflow**
3. **Pre-commit hooks validate template.html IDs against the registry**

## Control Workflow

```
PROPOSED → REVIEW → AUTHORIZED → IMPLEMENT → WIRE → IMPLEMENTED
```

### Step-by-step

1. **PROPOSE**: Add control entry with `status: PROPOSED`
   ```yaml
   - id: my-new-control
     type: button
     status: PROPOSED
     added: "2026-01-25"
   ```

2. **REVIEW**: Validate against design system, check for duplicates

3. **AUTHORIZE**: Change status to `AUTHORIZED` (approval to implement)

4. **IMPLEMENT**: Add HTML element to `src/core/viz/assets/template.html`
   ```html
   <button id="my-new-control">Click me</button>
   ```

5. **WIRE**: Add event handlers in `src/core/viz/assets/modules/panel-handlers.js`
   ```javascript
   const myNewControl = {
     selector: '#my-new-control',
     onChange: (value) => { /* handler */ }
   };
   ```

6. **VALIDATE**: Change status to `IMPLEMENTED`

## Registry Structure

### Panel Organization

Controls are grouped by panel (functional area):

- **filtering** - Data subset selection (8 controls)
- **selection** - Interactive element selection (9 controls)
- **camera** - 3D camera controls (11 controls)
- **accessibility** - WCAG compliance (7 controls)
- **node-appear** - Node visual properties (7 controls)
- **edge-appear** - Edge visual properties (7 controls)
- **view-modes** - Graph view switching (4 controls)
- **layout-phys** - Physics simulation (3 controls)
- **export** - Export and sharing (2 controls)
- **analysis** - Metrics and insights (1 control)

### Control Fields

Each control entry has:

```yaml
- id: unique-control-id              # HTML element ID, must match template.html
  type: button|slider|toggle|etc.    # Control type (for UI library)
  status: PROPOSED|AUTHORIZED|IMPLEMENTED|DEPRECATED
  added: "YYYY-MM-DD"                # Date first registered
```

### Authorization States

| Status | Meaning |
|--------|---------|
| `PROPOSED` | Under review, not approved for implementation |
| `AUTHORIZED` | Approved, safe to add to template.html |
| `IMPLEMENTED` | In template.html and wired to handlers |
| `DEPRECATED` | Scheduled for removal |

## Governance Rule

> No control may be added to template.html without FIRST being registered here with status AUTHORIZED

**Enforcement:** Pre-commit hooks check:
1. Every control ID in template.html exists in CONTROL_REGISTRY.yaml
2. Every ID in registry matches a template.html element
3. Status is `IMPLEMENTED` for production

## Current Status

- **Version:** 1.0
- **Last Updated:** 2026-01-25
- **Total Registered:** 160 controls
- **All Status:** IMPLEMENTED (all controls are wired and production)
- **Coverage:** 100% of template.html controls registered
- **Panels:** 19 functional groups
- **Validation:** Zero discrepancies - registry is authoritative

## Validation

To verify the registry:

```bash
python3 tools/validate_ui.py src/core/viz/assets/template.html --verbose
```

## Next Steps

### Adding a New Control

1. Edit CONTROL_REGISTRY.yaml, add entry with `status: PROPOSED`
2. Get design review approval
3. Update status to `AUTHORIZED`
4. Add HTML element to template.html
5. Wire handler in panel-handlers.js
6. Update status to `IMPLEMENTED`
7. Run validation hook
8. Commit with message: `feat(ui): Add [control-id] control`

### Removing a Control

1. Set `status: DEPRECATED`
2. Remove from template.html (in separate commit)
3. Remove from handler wiring
4. Delete registry entry (in separate commit)

## Related Files

- **Template:** `src/core/viz/assets/template.html`
- **Handlers:** `src/core/viz/assets/modules/panel-handlers.js`
- **UI Spec:** `docs/specs/VISUALIZATION_UI_SPEC.md`
- **Validator:** `tools/validate_ui.py`
