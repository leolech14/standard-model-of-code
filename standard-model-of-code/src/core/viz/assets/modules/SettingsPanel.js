/**
 * @module SettingsPanel
 * @description UI Component for configuring application settings, starting with inputs.
 * Toggles via a gear icon or menu item.
 */

const SettingsPanel = (function () {
    'use strict';

    let container = null;
    let isVisible = false;


    function init() {
        if (container) {
            console.log('[SettingsPanel] Already initialized.');
            return;
        }

        console.log('[SettingsPanel] Initializing...');
        createPanel();
        createToggleButton();

        // Listen for external updates to refresh UI if open
        window.addEventListener('controls-updated', () => {
            if (isVisible) refreshUI();
        });
    }

    function createToggleButton() {
        const actionsSection = document.getElementById('section-actions');
        if (!actionsSection) {
            console.warn('[SettingsPanel] Could not find #section-actions to append toggle button');
            return;
        }

        const btn = document.createElement('button');
        btn.className = 'nav-btn'; // Re-use existing styling
        btn.innerHTML = `<span class="icon">⚙️</span> Settings`;
        btn.onclick = togglePanel;
        btn.title = 'Configure Controls & Settings';

        // Append to the actions area
        actionsSection.appendChild(btn);
    }

    function createPanel() {
        // Create modal container
        container = document.createElement('div');
        container.id = 'settings-panel';
        container.style.display = 'none';
        container.style.position = 'fixed';
        container.style.top = '50%';
        container.style.left = '50%';
        container.style.transform = 'translate(-50%, -50%)';
        container.style.backgroundColor = 'rgba(20, 20, 25, 0.95)';
        container.style.border = '1px solid #444';
        container.style.borderRadius = '8px';
        container.style.padding = '20px';
        container.style.zIndex = '100000';
        container.style.width = '400px';
        container.style.boxShadow = '0 10px 30px rgba(0,0,0,0.5)';
        container.style.color = '#eee';
        container.style.fontFamily = 'sans-serif';

        // Header
        const header = document.createElement('div');
        header.style.display = 'flex';
        header.style.justifyContent = 'space-between';
        header.style.alignItems = 'center';
        header.style.marginBottom = '20px';
        header.style.borderBottom = '1px solid #444';
        header.style.paddingBottom = '10px';

        const title = document.createElement('h2');
        title.innerText = 'Settings';
        title.style.margin = '0';
        title.style.fontSize = '18px';

        const closeBtn = document.createElement('button');
        closeBtn.innerText = '×';
        closeBtn.style.background = 'none';
        closeBtn.style.border = 'none';
        closeBtn.style.color = '#fff';
        closeBtn.style.fontSize = '24px';
        closeBtn.style.cursor = 'pointer';
        closeBtn.onclick = hidePanel;

        header.appendChild(title);
        header.appendChild(closeBtn);
        container.appendChild(header);

        // Content Area
        const content = document.createElement('div');
        content.id = 'settings-content';
        container.appendChild(content);

        // Footer
        const footer = document.createElement('div');
        footer.style.marginTop = '20px';
        footer.style.display = 'flex';
        footer.style.justifyContent = 'flex-end';
        footer.style.gap = '10px';

        const resetBtn = document.createElement('button');
        resetBtn.innerText = 'Reset Defaults';
        resetBtn.style.padding = '8px 12px';
        resetBtn.style.background = '#444';
        resetBtn.style.color = '#fff';
        resetBtn.style.border = 'none';
        resetBtn.style.borderRadius = '4px';
        resetBtn.style.cursor = 'pointer';
        resetBtn.onclick = () => {
            if (confirm('Reset all navigation controls to default?')) {
                ControlRegistry.resetDefaults();
                refreshUI();
            }
        };

        const saveBtn = document.createElement('button');
        saveBtn.innerText = 'Done';
        saveBtn.style.padding = '8px 16px';
        saveBtn.style.background = '#2196F3';
        saveBtn.style.color = '#fff';
        saveBtn.style.border = 'none';
        saveBtn.style.borderRadius = '4px';
        saveBtn.style.cursor = 'pointer';
        saveBtn.onclick = hidePanel;

        footer.appendChild(resetBtn);
        footer.appendChild(saveBtn);
        container.appendChild(footer);

        document.body.appendChild(container);
    }

    function refreshUI() {
        const content = document.getElementById('settings-content');
        content.innerHTML = ''; // Clear

        // -- Controls Section --
        const section = document.createElement('div');
        section.innerHTML = '<h3 style="margin-top:0; font-size:14px; color:#aaa; text-transform:uppercase;">Navigation Controls</h3>';

        const config = ControlRegistry.getConfig();
        const { ACTIONS, ACTION_LABELS } = ControlRegistry.CONSTANTS;

        // Render Dropdown for each Mouse Button
        ['LEFT', 'MIDDLE', 'RIGHT'].forEach(btn => {
            const row = document.createElement('div');
            row.style.display = 'flex';
            row.style.justifyContent = 'space-between';
            row.style.alignItems = 'center';
            row.style.marginBottom = '10px';

            const label = document.createElement('label');
            label.innerText = `${btn} Mouse Button:`;
            label.style.fontSize = '14px';

            const select = document.createElement('select');
            select.style.padding = '4px';
            select.style.background = '#222';
            select.style.color = '#ddd';
            select.style.border = '1px solid #555';
            select.style.borderRadius = '4px';

            // Populate Options (Rotate, Zoom, Pan)
            Object.keys(ACTIONS).forEach(actionKey => {
                const actionId = ACTIONS[actionKey];
                const opt = document.createElement('option');
                opt.value = actionId;
                opt.innerText = ACTION_LABELS[actionId];
                if (config.mouse[btn] === actionId) {
                    opt.selected = true;
                }
                select.appendChild(opt);
            });

            // Handle Change
            select.onchange = (e) => {
                ControlRegistry.updateMapping(btn, parseInt(e.target.value));
            };

            row.appendChild(label);
            row.appendChild(select);
            section.appendChild(row);
        });

        content.appendChild(section);

        // Hints
        const hint = document.createElement('div');
        hint.style.fontSize = '12px';
        hint.style.color = '#888';
        hint.style.marginTop = '10px';
        hint.innerText = 'Tip: Changes apply immediately.';
        content.appendChild(hint);
    }

    function togglePanel() {
        if (isVisible) hidePanel();
        else showPanel();
    }

    function showPanel() {
        refreshUI();
        container.style.display = 'block';
        isVisible = true;
    }

    function hidePanel() {
        container.style.display = 'none';
        isVisible = false;
    }

    return {
        init,
        toggle: togglePanel
    };
})();

// Export
if (typeof window !== 'undefined') window.SettingsPanel = SettingsPanel;
if (typeof module !== 'undefined') module.exports = SettingsPanel;
