/**
 * ═══════════════════════════════════════════════════════════════════════════
 * SETTINGS PANEL MODULE
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * Provides a comprehensive Settings Modal for:
 * 1. General: Navigation & Mouse controls
 * 2. Appearance: Theme, Density, Normalization
 * 3. Controls: Registry of all UI controls (from CIRCUIT)
 * 4. Analysis: AI/Analyzer Config
 *
 * @module SETTINGS
 */
const SETTINGS = (function () {
    'use strict';

    let _modal = null;
    let _activeTab = 'general';

    // Default configuration
    const _config = {
        theme: {
            mode: 'dark',
            density: 'compact',
            fontSize: '11px',
            fontFamily: 'SF Mono',
            blur: true
        },
        navigation: {
            mouseMapping: 'default', // default | maya | blender
            damping: 0.1,
            rotateSpeed: 1.0,
            zoomSpeed: 1.2,
            panSpeed: 1.0
        },
        analysis: {
            perplexityModel: 'sonar-pro',
            autoQuery: false
        }
    };

    /**
     * Initialize the Settings Module
     */
    function init() {
        _createModal();
        _loadConfig();
        _applyTheme();
        console.log('[Module] SETTINGS initialized');
    }

    /**
     * Open the Settings Modal
     * @param {string} tab - Optional tab to open ('general', 'appearance', 'controls', 'analysis')
     */
    function open(tab = 'general') {
        if (!_modal) _createModal();
        if (tab) _switchTab(tab);
        _modal.style.display = 'flex';
        _populateControlsTab(); // Refresh controls tab
    }

    /**
     * Close the Settings Modal
     */
    function close() {
        if (_modal) _modal.style.display = 'none';
    }

    /**
     * Create the Modal DOM structure
     */
    function _createModal() {
        if (document.getElementById('settings-modal')) return;

        const html = `
            <div id="settings-modal" class="settings-overlay" style="display: none;">
                <div class="settings-container">
                    <div class="settings-sidebar">
                        <div class="settings-title">SETTINGS</div>
                        <button class="settings-tab active" data-tab="general">General</button>
                        <button class="settings-tab" data-tab="appearance">Appearance</button>
                        <button class="settings-tab" data-tab="controls">Controls Registry</button>
                        <button class="settings-tab" data-tab="analysis">Analysis</button>
                    </div>
                    <div class="settings-content">
                        <div class="settings-header">
                            <span id="settings-header-title">General Settings</span>
                            <button class="settings-close">×</button>
                        </div>

                        <!-- TAB: GENERAL -->
                        <div class="settings-pane active" id="pane-general">
                            <div class="settings-group">
                                <div class="settings-group-title">Mouse & Navigation</div>
                                <div class="settings-row">
                                    <label>Control Scheme</label>
                                    <select id="set-mouse-map">
                                        <option value="default">Default (L: Rotate, R: Pan)</option>
                                        <option value="maya">Maya (Alt+L: Rotate, Alt+M: Pan)</option>
                                        <option value="blender">Blender (M: Rotate, Shift+M: Pan)</option>
                                    </select>
                                </div>
                                <div class="settings-row">
                                    <label>Rotation Speed</label>
                                    <input type="range" min="0.1" max="5.0" step="0.1" value="1.0" id="set-rot-speed">
                                    <span class="val" id="val-rot-speed">1.0</span>
                                </div>
                                <div class="settings-row">
                                    <label>Zoom Speed</label>
                                    <input type="range" min="0.1" max="5.0" step="0.1" value="1.2" id="set-zoom-speed">
                                    <span class="val" id="val-zoom-speed">1.2</span>
                                </div>
                                <div class="settings-row">
                                    <label>Damping Factor</label>
                                    <input type="range" min="0.01" max="0.3" step="0.01" value="0.1" id="set-damping">
                                    <span class="val" id="val-damping">0.1</span>
                                </div>
                            </div>
                        </div>

                        <!-- TAB: APPEARANCE -->
                        <div class="settings-pane" id="pane-appearance">
                            <div class="settings-group">
                                <div class="settings-group-title">Theme System</div>
                                <div class="settings-row">
                                    <label>Mode</label>
                                    <div class="btn-group">
                                        <button class="btn active" data-theme="dark">Dark</button>
                                        <button class="btn" data-theme="light">Light</button>
                                        <button class="btn" data-theme="oled">OLED</button>
                                    </div>
                                </div>
                                <div class="settings-row">
                                    <label>UI Scaler (Density)</label>
                                    <select id="set-density">
                                        <option value="comfortable">Comfortable</option>
                                        <option value="compact" selected>Compact</option>
                                        <option value="dense">Dense</option>
                                    </select>
                                </div>
                                <div class="settings-row">
                                    <label>Font Size</label>
                                    <input type="number" value="11" min="8" max="16" id="set-font-size"> px
                                </div>
                                <div class="settings-row">
                                    <label>Backdrop Blur</label>
                                    <input type="checkbox" checked id="set-blur">
                                </div>
                            </div>
                        </div>

                        <!-- TAB: CONTROLS -->
                        <div class="settings-pane" id="pane-controls">
                            <div class="settings-group">
                                <div class="settings-group-title">Control Registry (Circuit Breaker)</div>
                                <div class="settings-desc">Live status of all registered UI checkpoints.</div>
                                <div class="registry-list" id="registry-list">
                                    <!-- Populated dynamically -->
                                </div>
                            </div>
                        </div>

                        <!-- TAB: ANALYSIS -->
                        <div class="settings-pane" id="pane-analysis">
                            <div class="settings-group">
                                <div class="settings-group-title">Analysis Configuration</div>
                                <div class="settings-row">
                                    <label>Perplexity Model</label>
                                    <select id="set-ai-model">
                                        <option value="sonar-pro">Sonar Pro</option>
                                        <option value="sonar-reasoning">Sonar Reasoning</option>
                                    </select>
                                </div>
                                <div class="settings-row">
                                    <label>Auto-Run Queries</label>
                                    <input type="checkbox" id="set-auto-query">
                                </div>
                            </div>
                        </div>

                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', html);
        _modal = document.getElementById('settings-modal');
        _bindEvents();
        _injectStyles();
    }

    /**
     * Bind UI Events
     */
    function _bindEvents() {
        // Close button
        _modal.querySelector('.settings-close').addEventListener('click', close);

        // Tab switching
        _modal.querySelectorAll('.settings-tab').forEach(tab => {
            tab.addEventListener('click', (e) => _switchTab(e.target.dataset.tab));
        });

        // Theme buttons
        _modal.querySelectorAll('[data-theme]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                _modal.querySelectorAll('[data-theme]').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                _config.theme.mode = e.target.dataset.theme;
                _applyTheme();
                _saveConfig();
            });
        });

        // Sliders
        const sliderBind = (id, configPath, valId) => {
            const el = document.getElementById(id);
            if (!el) return;
            el.addEventListener('input', (e) => {
                const val = parseFloat(e.target.value);
                document.getElementById(valId).textContent = val;

                // Update config object
                const parts = configPath.split('.');
                let obj = _config;
                for (let i = 0; i < parts.length - 1; i++) obj = obj[parts[i]];
                obj[parts[parts.length - 1]] = val;

                // Live apply
                if (configPath.startsWith('navigation')) _applyNavigation();

                _saveConfig();
            });
        };

        sliderBind('set-rot-speed', 'navigation.rotateSpeed', 'val-rot-speed');
        sliderBind('set-zoom-speed', 'navigation.zoomSpeed', 'val-zoom-speed');
        sliderBind('set-damping', 'navigation.damping', 'val-damping');

        // Density
        document.getElementById('set-density').addEventListener('change', (e) => {
            _config.theme.density = e.target.value;
            _applyTheme();
            _saveConfig();
        });

        // Font Size
        document.getElementById('set-font-size').addEventListener('change', (e) => {
            _config.theme.fontSize = e.target.value + 'px';
            _applyTheme();
            _saveConfig();
        });
    }

    /**
     * Switch Tabs
     */
    function _switchTab(tabId) {
        _activeTab = tabId;

        // Update Sidebar
        _modal.querySelectorAll('.settings-tab').forEach(t => {
            t.classList.toggle('active', t.dataset.tab === tabId);
        });

        // Update Content
        _modal.querySelectorAll('.settings-pane').forEach(p => {
            p.classList.toggle('active', p.id === `pane-${tabId}`);
        });

        // Update Header
        const titles = {
            general: 'General Settings',
            appearance: 'Appearance & Theme',
            controls: 'Controls Registry',
            analysis: 'Analysis Configuration'
        };
        document.getElementById('settings-header-title').textContent = titles[tabId] || 'Settings';
    }

    /**
     * Populate Controls Registry from CIRCUIT module
     */
    function _populateControlsTab() {
        const list = document.getElementById('registry-list');
        if (!list) return;

        list.innerHTML = '';

        if (typeof CIRCUIT === 'undefined' || !CIRCUIT.getRegistry) {
            list.innerHTML = '<div class="warn">Circuit Breaker module not loaded. Registry unavailable.</div>';
            return;
        }

        const registry = CIRCUIT.getRegistry();

        // Group by section prefix (simple heuristic)
        registry.forEach(item => {
            const statusClass = document.getElementById(item.elementId) ? 'pass' : 'fail';
            const statusIcon = statusClass === 'pass' ? '✓' : '✗';

            const div = document.createElement('div');
            div.className = `registry-item ${statusClass}`;
            div.innerHTML = `
                <div class="reg-icon">${statusIcon}</div>
                <div class="reg-info">
                    <div class="reg-name">${item.name}</div>
                    <div class="reg-meta">${item.type} | #${item.elementId || 'no-id'}</div>
                </div>
                <div class="reg-act">${item.statePath || 'N/A'}</div>
            `;
            list.appendChild(div);
        });
    }

    /**
     * Apply active theme settings to CSS Variables
     */
    function _applyTheme() {
        const r = document.documentElement;

        // Density
        if (_config.theme.density === 'compact') {
            r.style.setProperty('--spacing-unit', '4px');
        } else if (_config.theme.density === 'dense') {
            r.style.setProperty('--spacing-unit', '2px');
        } else {
            r.style.setProperty('--spacing-unit', '8px');
        }

        // Font
        r.style.setProperty('--type-size-base', _config.theme.fontSize);

        // Mode
        if (_config.theme.mode === 'light') {
            document.body.classList.add('theme-light');
            document.body.classList.remove('theme-dark', 'theme-oled');
        } else if (_config.theme.mode === 'oled') {
            document.body.classList.add('theme-oled');
            document.body.classList.remove('theme-light', 'theme-dark');
        } else {
            document.body.classList.add('theme-dark');
            document.body.classList.remove('theme-light', 'theme-oled');
        }
    }

    function _applyNavigation() {
        if (typeof Graph !== 'undefined') {
            // If we had a direct Graph API for these, we'd call it.
            // For now we assume Graph reads these from a state object or we implement direct setters later.
            // Placeholder for now.
        }
    }

    function _saveConfig() {
        localStorage.setItem('collider_settings_v2', JSON.stringify(_config));
    }

    function _loadConfig() {
        const saved = localStorage.getItem('collider_settings_v2');
        if (saved) {
            try {
                const parsed = JSON.parse(saved);
                Object.assign(_config, parsed); // Deep merge would be better, but this is simple
            } catch (e) { console.error('Settings load failed', e); }
        }

        // Update UI inputs to match config
        if (document.getElementById('set-rot-speed')) {
            document.getElementById('set-rot-speed').value = _config.navigation.rotateSpeed;
            document.getElementById('val-rot-speed').textContent = _config.navigation.rotateSpeed;
        }
        // ... set other inputs
    }

    /**
     * Inject Modal Styles
     */
    function _injectStyles() {
        if (document.getElementById('settings-css')) return;
        const css = `
            .settings-overlay {
                position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                background: rgba(0,0,0,0.6); backdrop-filter: blur(4px);
                z-index: 9999;
                align-items: center; justify-content: center;
            }
            .settings-container {
                display: flex;
                width: 800px; height: 500px;
                background: var(--color-bg-elevated, #1a1a1a);
                border: 1px solid var(--color-border-default, #333);
                border-radius: 8px;
                box-shadow: 0 20px 50px rgba(0,0,0,0.5);
                overflow: hidden;
            }
            .settings-sidebar {
                width: 200px; background: rgba(0,0,0,0.2);
                border-right: 1px solid var(--color-border-default, #333);
                padding: 20px 0;
            }
            .settings-title {
                padding: 0 20px 20px; font-weight: bold; letter-spacing: 2px;
                color: var(--text-muted, #888); font-size: 12px;
            }
            .settings-tab {
                display: block; width: 100%; text-align: left;
                padding: 12px 20px; background: none; border: none;
                color: var(--text-secondary, #ccc); cursor: pointer;
                border-left: 3px solid transparent;
                transition: all 0.2s;
            }
            .settings-tab:hover { background: rgba(255,255,255,0.05); color: #fff; }
            .settings-tab.active {
                background: rgba(255,255,255,0.08);
                border-left-color: var(--accent, #4a9eff);
                color: #fff;
            }
            .settings-content { flex: 1; display: flex; flex-direction: column; }
            .settings-header {
                padding: 20px; border-bottom: 1px solid var(--color-border-default, #333);
                display: flex; justify-content: space-between; align-items: center;
                font-size: 18px; font-weight: 500;
            }
            .settings-close {
                background: none; border: none; font-size: 24px; color: #888; cursor: pointer;
            }
            .settings-close:hover { color: #fff; }
            .settings-pane { display: none; padding: 20px; overflow-y: auto; height: 100%; }
            .settings-pane.active { display: block; }

            .settings-group { margin-bottom: 30px; }
            .settings-group-title {
                font-size: 12px; text-transform: uppercase; letter-spacing: 1px;
                color: var(--accent, #4a9eff); margin-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.1);
                padding-bottom: 5px;
            }
            .settings-row {
                display: flex; align-items: center; justify-content: space-between;
                margin-bottom: 12px; font-size: 13px;
            }
            .settings-desc { font-size: 12px; color: #666; margin-bottom: 10px; }

            .registry-list { max-height: 300px; overflow-y: auto; border: 1px solid #333; }
            .registry-item {
                display: flex; padding: 8px; border-bottom: 1px solid #333;
                align-items: center; font-size: 11px;
            }
            .registry-item:last-child { border-bottom: none; }
            .reg-icon { width: 24px; text-align: center; font-weight: bold; }
            .registry-item.pass .reg-icon { color: #4ade80; }
            .registry-item.fail .reg-icon { color: #f87171; }
            .reg-info { flex: 1; }
            .reg-name { font-weight: bold; color: #eee; }
            .reg-meta { color: #666; font-size: 10px; }
            .reg-act { font-family: monospace; color: #888; }

            .btn-group { display: flex; gap: 4px; }
            .btn-group .btn { padding: 4px 12px; border: 1px solid #444; background: #222; color: #ccc; cursor: pointer; }
            .btn-group .btn.active { background: var(--accent, #4a9eff); color: #000; border-color: var(--accent, #4a9eff); }
        `;
        const style = document.createElement('style');
        style.id = 'settings-css';
        style.textContent = css;
        document.head.appendChild(style);
    }

    // Public API
    return {
        init,
        open,
        close
    };

})();

// Global Access
window.SETTINGS = SETTINGS;
