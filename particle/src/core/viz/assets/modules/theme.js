/**
 * ═══════════════════════════════════════════════════════════════════════════
 * THEME MODULE - Runtime Theme Management
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * Handles theme switching, persistence, and initialization.
 * Depends on: THEME_CONFIG (global), Graph (global), THREE (global)
 *
 * @module THEME
 * @version 1.0.0
 * @confidence 99%
 */

window.THEME = (function() {
    'use strict';

    // ═══════════════════════════════════════════════════════════════════════
    // THEME OPERATIONS
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Set the active theme by name.
     * Updates document data-theme attribute and stores preference.
     * @param {string} themeName - Theme name: 'dark', 'light', or 'high-contrast'
     */
    function setTheme(themeName) {
        const config = window.THEME_CONFIG;
        if (!config || !config.available.includes(themeName)) {
            console.warn(`[Theme] Unknown theme: ${themeName}. Available: ${config?.available?.join(', ') || 'none'}`);
            return;
        }

        // Update document attribute for CSS variable switching
        document.documentElement.setAttribute('data-theme', themeName);

        // Update global state
        config.current = themeName;

        // Store preference in localStorage
        try {
            localStorage.setItem('collider-theme', themeName);
        } catch (e) {
            console.warn('[Theme] Could not save preference:', e);
        }

        // Update canvas background if WebGL renderer is active
        const Graph = window.Graph;
        if (Graph && Graph.scene && Graph.scene()) {
            const scene = Graph.scene();
            if (scene.background) {
                const vizColors = window.VIZ_COLORS || {};
                const bgColor = getComputedStyle(document.documentElement)
                    .getPropertyValue('--color-viz-canvas-bg')?.trim() || vizColors.canvasBg || '#0a0a0f';
                scene.background = new THREE.Color(bgColor);
            }
        }

        // Update theme toggle buttons
        document.querySelectorAll('.theme-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.theme === themeName);
        });

        const consoleColors = window.CONSOLE_COLORS || { success: '#4caf50' };
        console.log(`%c[Theme] Switched to: ${themeName}`, `color: ${consoleColors.success}; font-weight: bold`);

        // Show toast if available
        if (typeof window.showToast === 'function') {
            window.showToast(`Theme: ${themeName}`);
        }
    }

    /**
     * Get the current theme name.
     * @returns {string} Current theme name
     */
    function getTheme() {
        const config = window.THEME_CONFIG;
        return config ? config.current : 'dark';
    }

    /**
     * Get list of available themes.
     * @returns {string[]} Array of theme names
     */
    function getAvailableThemes() {
        const config = window.THEME_CONFIG;
        return config ? config.available : ['dark'];
    }

    /**
     * Cycle to the next theme in the list.
     */
    function cycleTheme() {
        const config = window.THEME_CONFIG;
        if (!config) return;

        const current = config.current;
        const themes = config.available;
        const currentIndex = themes.indexOf(current);
        const nextIndex = (currentIndex + 1) % themes.length;
        setTheme(themes[nextIndex]);
    }

    /**
     * Initialize theme from saved preference or default.
     */
    function initTheme() {
        const config = window.THEME_CONFIG;
        if (!config) {
            console.warn('[Theme] THEME_CONFIG not available');
            return;
        }

        // Check for saved preference
        let savedTheme = null;
        try {
            savedTheme = localStorage.getItem('collider-theme');
        } catch (e) {
            // Ignore storage errors
        }

        // Use saved preference if valid
        if (savedTheme && config.available.includes(savedTheme)) {
            setTheme(savedTheme);
            return;
        }

        // Fall back to default theme
        setTheme(config.default || 'dark');
    }

    // ═══════════════════════════════════════════════════════════════════════
    // MODULE EXPORT
    // ═══════════════════════════════════════════════════════════════════════

    return {
        set: setTheme,
        get: getTheme,
        available: getAvailableThemes,
        cycle: cycleTheme,
        init: initTheme
    };
})();

// ═══════════════════════════════════════════════════════════════════════════
// BACKWARD COMPATIBILITY SHIMS
// ═══════════════════════════════════════════════════════════════════════════

window.setTheme = THEME.set;
window.getTheme = THEME.get;
window.getAvailableThemes = THEME.available;
window.cycleTheme = THEME.cycle;
window.initTheme = THEME.init;

console.log('[Module] THEME loaded - 5 functions');
