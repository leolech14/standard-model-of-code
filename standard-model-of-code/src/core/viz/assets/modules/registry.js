/**
 * @module registry
 * @description Centralized UI and command registration system
 * @responsibility Manage DOM element and command handler registration
 */

const REGISTRY = (function() {
    'use strict';

    // Private state
    const _items = new Map();
    const _commands = new Map();

    /**
     * Register a command handler or DOM element
     * @param {string} id - The identifier
     * @param {Function|Element} item - Handler function or DOM element
     * @param {Object} options - Additional options
     */
    function register(id, item, options = {}) {
        // CASE 1: Registering a Command Identifier + Handler Function
        // e.g. REGISTRY.register('cmd-files', () => toggleFiles(), { desc: '...' })
        if (typeof item === 'function') {
            _commands.set(id, { handler: item, options });

            // Auto-wire if DOM element exists with this ID
            const btn = document.getElementById(id);
            if (btn) {
                btn.onclick = (e) => {
                    item(e);
                };
                btn.setAttribute('data-command-id', id);
            }
            return;
        }

        // CASE 2: Registering a DOM Element directly
        let element = item;
        let elementId = id;

        // Overload: register(element) -> id comes from element.id
        if ((item instanceof Element) && arguments.length === 1) {
            element = item;
            elementId = element.id;
        }
        // Overload: register(id, element)
        else if (item instanceof Element) {
            element = item;
        }
        // Fallback: mismatched args
        else if (!element && (typeof id === 'object' && id instanceof Element)) {
            element = id;
            elementId = element.id;
        }

        if (!element || !element.setAttribute) {
            return;
        }

        if (!elementId) {
            return;
        }

        _items.set(elementId, element);
        element.setAttribute('data-registry-id', elementId);
    }

    /**
     * Get a registered element by ID (falls back to document.getElementById)
     * @param {string} id - The element ID
     * @returns {Element|null}
     */
    function get(id) {
        return _items.get(id) || document.getElementById(id);
    }

    /**
     * Get a registered command handler
     * @param {string} id - The command ID
     * @returns {Object|undefined} - { handler, options }
     */
    function getCommand(id) {
        return _commands.get(id);
    }

    /**
     * Execute a registered command
     * @param {string} id - The command ID
     * @param {Event} event - Optional event object
     * @returns {*} - Result of handler execution
     */
    function execute(id, event) {
        const cmd = _commands.get(id);
        if (cmd && typeof cmd.handler === 'function') {
            return cmd.handler(event);
        }
        console.warn(`[Registry] Command not found: ${id}`);
        return undefined;
    }

    /**
     * Check if a command is registered
     * @param {string} id - The command ID
     * @returns {boolean}
     */
    function hasCommand(id) {
        return _commands.has(id);
    }

    /**
     * Check if an element is registered
     * @param {string} id - The element ID
     * @returns {boolean}
     */
    function hasElement(id) {
        return _items.has(id);
    }

    /**
     * Get all registered command IDs
     * @returns {string[]}
     */
    function listCommands() {
        return Array.from(_commands.keys());
    }

    /**
     * Get all registered element IDs
     * @returns {string[]}
     */
    function listElements() {
        return Array.from(_items.keys());
    }

    // Public API
    return {
        register,
        get,
        getCommand,
        execute,
        hasCommand,
        hasElement,
        listCommands,
        listElements,
        // Expose maps for backward compatibility (read-only access pattern)
        get items() { return _items; },
        get commands() { return _commands; }
    };
})();

// Expose globally for backward compatibility
window.REGISTRY = REGISTRY;
