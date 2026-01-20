/**
 * ═══════════════════════════════════════════════════════════════════════════
 * UI-BUILDERS MODULE - DOM element construction utilities
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * Factory functions for building common UI elements: checkboxes, toggles,
 * filter groups, and option selectors.
 *
 * @module UI_BUILDERS
 * @version 1.0.0
 */

window.UI_BUILDERS = (function() {
    'use strict';

    // ═══════════════════════════════════════════════════════════════════════
    // COUNT COLLECTION
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Collect counts by key from items
     * @param {Array} items - Items to count
     * @param {Function} keyFn - Function to extract key from item
     * @returns {Array} Array of [key, count] pairs sorted by count desc
     */
    function collectCounts(items, keyFn) {
        const counts = new Map();
        items.forEach(item => {
            const key = keyFn(item);
            if (!key) return;
            counts.set(key, (counts.get(key) || 0) + 1);
        });
        return Array.from(counts.entries()).sort((a, b) => b[1] - a[1]);
    }

    // ═══════════════════════════════════════════════════════════════════════
    // CHECKBOX ROW
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Build a checkbox row element
     * @param {HTMLElement} container - Parent container
     * @param {string} id - Element ID
     * @param {string} label - Display label
     * @param {number|null} count - Optional count to display
     * @param {boolean} checked - Initial checked state
     * @param {Function} onChange - Callback when checkbox changes
     * @returns {HTMLInputElement} The checkbox input element
     */
    function buildCheckboxRow(container, id, label, count, checked, onChange) {
        const row = document.createElement('div');
        row.className = 'filter-item';

        const input = document.createElement('input');
        input.type = 'checkbox';
        input.id = id;
        input.checked = checked;
        input.onchange = () => onChange(input.checked);

        const text = document.createElement('label');
        text.setAttribute('for', id);
        text.textContent = label;

        const countEl = document.createElement('span');
        countEl.className = 'filter-count';
        countEl.textContent = (typeof count === 'number') ? String(count) : '';

        row.appendChild(input);
        row.appendChild(text);
        if (countEl.textContent) {
            row.appendChild(countEl);
        }
        container.appendChild(row);

        return input;
    }

    // ═══════════════════════════════════════════════════════════════════════
    // FILTER GROUP
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Build a filter group with ALL checkbox and individual items
     * @param {string} containerId - Container element ID
     * @param {Array} items - Array of [value, count] pairs
     * @param {Set} stateSet - Set to track selected values
     * @param {Function} onUpdate - Callback when selection changes
     */
    function buildFilterGroup(containerId, items, stateSet, onUpdate) {
        const container = document.getElementById(containerId);
        if (!container) return;
        container.innerHTML = '';

        const allId = `${containerId}-all`;
        let allCheckbox = null;

        allCheckbox = buildCheckboxRow(container, allId, 'ALL', null, true, (checked) => {
            stateSet.clear();
            if (checked) {
                items.forEach(([value]) => stateSet.add(value));
            }
            container.querySelectorAll('input[type="checkbox"]').forEach(box => {
                if (box.id !== allId) box.checked = checked;
            });
            onUpdate();
        });

        items.forEach(([value, count], index) => {
            const id = `${containerId}-${index}`;
            const checked = stateSet.has(value);
            buildCheckboxRow(container, id, value, count, checked, (isChecked) => {
                if (isChecked) {
                    stateSet.add(value);
                } else {
                    stateSet.delete(value);
                }
                const allChecked = items.every(([v]) => stateSet.has(v));
                allCheckbox.checked = allChecked;
                onUpdate();
            });
        });
    }

    // ═══════════════════════════════════════════════════════════════════════
    // DATAMAP TOGGLE
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Build a datamap toggle element
     * @param {HTMLElement} container - Parent container
     * @param {string} id - Toggle ID
     * @param {string} label - Display label
     * @param {boolean} checked - Initial checked state
     * @param {number|null} count - Optional count to display
     * @param {Function} onChange - Callback when toggle changes
     * @returns {Object} Object with wrapper, input, and count elements
     */
    function buildDatamapToggle(container, id, label, checked, count, onChange) {
        const wrapper = document.createElement('label');
        wrapper.className = 'datamap-toggle';
        wrapper.setAttribute('data-id', id);

        const input = document.createElement('input');
        input.type = 'checkbox';
        input.checked = checked;
        input.onchange = () => onChange(input.checked);

        const text = document.createElement('span');
        text.textContent = label;

        const countEl = document.createElement('span');
        countEl.className = 'datamap-count';
        countEl.textContent = (typeof count === 'number') ? String(count) : '';

        wrapper.appendChild(input);
        wrapper.appendChild(text);
        wrapper.appendChild(countEl);
        container.appendChild(wrapper);

        return { wrapper, input, count: countEl };
    }

    // ═══════════════════════════════════════════════════════════════════════
    // EXCLUSIVE OPTIONS
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Build exclusive (radio-like) options using checkboxes
     * @param {string} containerId - Container element ID
     * @param {Array} options - Array of {label, value} objects
     * @param {*} activeValue - Currently active value
     * @param {Function} onSelect - Callback when option is selected
     */
    function buildExclusiveOptions(containerId, options, activeValue, onSelect) {
        const container = document.getElementById(containerId);
        if (!container) return;
        container.innerHTML = '';

        const inputs = [];
        options.forEach((option, index) => {
            const id = `${containerId}-${index}`;
            const input = buildCheckboxRow(
                container,
                id,
                option.label,
                null,
                option.value === activeValue,
                (checked) => {
                    if (!checked) {
                        input.checked = true;
                        return;
                    }
                    inputs.forEach(other => {
                        if (other !== input) other.checked = false;
                    });
                    onSelect(option.value);
                }
            );
            inputs.push(input);
        });
    }

    // ═══════════════════════════════════════════════════════════════════════
    // MODULE EXPORT
    // ═══════════════════════════════════════════════════════════════════════

    return {
        collectCounts: collectCounts,
        buildCheckboxRow: buildCheckboxRow,
        buildFilterGroup: buildFilterGroup,
        buildDatamapToggle: buildDatamapToggle,
        buildExclusiveOptions: buildExclusiveOptions
    };
})();

// ═══════════════════════════════════════════════════════════════════════════
// BACKWARD COMPATIBILITY SHIMS
// ═══════════════════════════════════════════════════════════════════════════

window.collectCounts = UI_BUILDERS.collectCounts;
window.buildCheckboxRow = UI_BUILDERS.buildCheckboxRow;
window.buildFilterGroup = UI_BUILDERS.buildFilterGroup;
window.buildDatamapToggle = UI_BUILDERS.buildDatamapToggle;
window.buildExclusiveOptions = UI_BUILDERS.buildExclusiveOptions;

console.log('[Module] UI_BUILDERS loaded - 5 functions');
