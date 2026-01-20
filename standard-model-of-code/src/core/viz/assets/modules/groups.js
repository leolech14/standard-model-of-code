/**
 * ═══════════════════════════════════════════════════════════════════════════
 * GROUPS MODULE - Node grouping functionality
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * Group creation, storage, rendering, and management.
 * Depends on: GROUPS, ACTIVE_GROUP_ID, SELECTED_NODE_IDS, GROUPS_STORAGE_KEY
 *
 * @module GROUPS_MODULE
 * @version 1.0.0
 */

window.GROUPS_MODULE = (function() {
    'use strict';

    // ═══════════════════════════════════════════════════════════════════════
    // GROUP PERSISTENCE
    // ═══════════════════════════════════════════════════════════════════════

    function loadGroups() {
        window.GROUPS = [];
        try {
            const stored = localStorage.getItem(window.GROUPS_STORAGE_KEY);
            if (stored) {
                const parsed = JSON.parse(stored);
                if (Array.isArray(parsed)) {
                    window.GROUPS = parsed;
                }
            }
        } catch (e) {
            // localStorage unavailable
        }
        window.GROUPS = window.GROUPS.filter(group => group && group.id && Array.isArray(group.node_ids));
        window.GROUPS.forEach(group => {
            if (group.visible === undefined) group.visible = true;
        });
    }

    function saveGroups() {
        try {
            localStorage.setItem(window.GROUPS_STORAGE_KEY, JSON.stringify(window.GROUPS));
        } catch (e) {
            // localStorage unavailable
        }
    }

    // ═══════════════════════════════════════════════════════════════════════
    // GROUP HELPERS
    // ═══════════════════════════════════════════════════════════════════════

    function getNextGroupColor() {
        const hue = (window.GROUPS.length * 137.5) % 360;
        return window.hslColor(hue, 65, 55);
    }

    function getGroupById(groupId) {
        return window.GROUPS.find(group => group.id === groupId) || null;
    }

    function getPrimaryGroupForNode(nodeId) {
        const visibleGroups = window.GROUPS.filter(group =>
            group.visible !== false && Array.isArray(group.node_ids) && group.node_ids.includes(nodeId)
        );
        if (!visibleGroups.length) return null;
        if (window.ACTIVE_GROUP_ID) {
            const active = visibleGroups.find(group => group.id === window.ACTIVE_GROUP_ID);
            if (active) return active;
        }
        return visibleGroups[0];
    }

    // ═══════════════════════════════════════════════════════════════════════
    // GROUP LIST RENDERING
    // ═══════════════════════════════════════════════════════════════════════

    function renderGroupList() {
        const container = document.getElementById('group-list');
        if (!container) return;
        container.innerHTML = '';

        if (!window.GROUPS.length) {
            const empty = document.createElement('div');
            empty.style.fontSize = '9px';
            empty.style.color = 'rgba(255,255,255,0.4)';
            empty.textContent = 'No groups yet';
            container.appendChild(empty);
            return;
        }

        window.GROUPS.forEach(group => {
            const row = document.createElement('div');
            row.className = 'group-item';
            row.classList.toggle('active', group.id === window.ACTIVE_GROUP_ID);

            const dot = document.createElement('span');
            dot.className = 'group-color';
            dot.style.background = group.color || '#6fe8ff';

            const name = document.createElement('span');
            name.className = 'group-name';
            name.textContent = group.name || 'Group';

            const count = document.createElement('span');
            count.className = 'group-count';
            count.textContent = String((group.node_ids || []).length);

            const toggle = document.createElement('input');
            toggle.type = 'checkbox';
            toggle.className = 'group-toggle';
            toggle.checked = group.visible !== false;
            toggle.onchange = (e) => {
                e.stopPropagation();
                group.visible = toggle.checked;
                saveGroups();
                window.updateSelectionVisuals();
                renderGroupList();
            };

            row.onclick = (e) => {
                if (e.target === toggle) return;
                window.ACTIVE_GROUP_ID = group.id;
                renderGroupList();
                window.setSelection(group.node_ids || []);
                window.updateSelectionVisuals();
            };

            row.appendChild(dot);
            row.appendChild(name);
            row.appendChild(count);
            row.appendChild(toggle);
            container.appendChild(row);
        });
    }

    // ═══════════════════════════════════════════════════════════════════════
    // GROUP BUTTON STATE
    // ═══════════════════════════════════════════════════════════════════════

    function updateGroupButtonState() {
        const btn = document.getElementById('btn-create-group');
        if (!btn) return;
        const hasSelection = window.SELECTED_NODE_IDS.size > 0;
        btn.classList.toggle('disabled', !hasSelection);
        btn.disabled = !hasSelection;
    }

    // ═══════════════════════════════════════════════════════════════════════
    // CREATE GROUP FROM SELECTION
    // ═══════════════════════════════════════════════════════════════════════

    function createGroupFromSelection() {
        if (window.SELECTED_NODE_IDS.size === 0) return;
        const nodeIds = Array.from(window.SELECTED_NODE_IDS);
        const groupId = `group_${Date.now().toString(36)}`;
        const groupName = `Group ${window.GROUPS.length + 1}`;
        const groupColor = getNextGroupColor();
        window.GROUPS.push({
            id: groupId,
            name: groupName,
            color: groupColor,
            node_ids: nodeIds,
            visible: true
        });
        window.ACTIVE_GROUP_ID = groupId;
        saveGroups();
        renderGroupList();
        window.updateSelectionVisuals();
        window.showToast(`Created ${groupName} (${nodeIds.length})`);
    }

    // ═══════════════════════════════════════════════════════════════════════
    // MODULE EXPORT
    // ═══════════════════════════════════════════════════════════════════════

    return {
        load: loadGroups,
        save: saveGroups,
        getNextColor: getNextGroupColor,
        getById: getGroupById,
        getPrimaryForNode: getPrimaryGroupForNode,
        renderList: renderGroupList,
        updateButtonState: updateGroupButtonState,
        createFromSelection: createGroupFromSelection
    };
})();

// ═══════════════════════════════════════════════════════════════════════════
// BACKWARD COMPATIBILITY SHIMS
// ═══════════════════════════════════════════════════════════════════════════

window.loadGroups = GROUPS_MODULE.load;
window.saveGroups = GROUPS_MODULE.save;
window.getNextGroupColor = GROUPS_MODULE.getNextColor;
window.getGroupById = GROUPS_MODULE.getById;
window.getPrimaryGroupForNode = GROUPS_MODULE.getPrimaryForNode;
window.renderGroupList = GROUPS_MODULE.renderList;
window.updateGroupButtonState = GROUPS_MODULE.updateButtonState;
window.createGroupFromSelection = GROUPS_MODULE.createFromSelection;

console.log('[Module] GROUPS_MODULE loaded - 8 functions');
