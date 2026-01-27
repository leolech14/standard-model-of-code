/**
 * EVENT BUS V2 - Decoupled Module Communication
 * ==============================================
 * SMoC Role: Infrastructure | Domain: Coordination
 *
 * Minimal pub/sub event system matching Python implementation.
 * Enables loose coupling between modules via events instead of direct dependencies.
 *
 * Usage:
 *   const bus = new EventBus();
 *
 *   // Subscribe
 *   bus.on('user:created', (data) => console.log(`User ${data.id} created`));
 *
 *   // Publish
 *   bus.emit('user:created', {id: 123, name: 'Alice'});
 *
 *   // Unsubscribe
 *   bus.off('user:created', handler);
 *
 * Features:
 * - Wildcard subscriptions ('user:*')
 * - Error isolation (one failing handler doesn't crash others)
 * - once() for one-time subscriptions
 * - disable/enable for testing
 *
 * Part of: Elements Hub Architecture (MODULAR_ARCHITECTURE_SYNTHESIS.md)
 */

const EventBus = (function() {
    'use strict';

    class EventBus {
        constructor() {
            this._handlers = new Map();        // event → handlers[]
            this._wildcardHandlers = [];      // [{prefix, handler}]
            this._enabled = true;
        }

        /**
         * Subscribe to an event.
         * @param {string} event - Event name (e.g., 'user:created', 'data:*')
         * @param {function} handler - Callback receiving event data
         */
        on(event, handler) {
            if (event.endsWith(':*')) {
                // Wildcard subscription
                const prefix = event.slice(0, -2);
                this._wildcardHandlers.push({prefix, handler});
            } else {
                if (!this._handlers.has(event)) {
                    this._handlers.set(event, []);
                }
                this._handlers.get(event).push(handler);
            }
        }

        /**
         * Publish an event to all subscribers.
         * @param {string} event - Event name
         * @param {*} data - Optional payload
         * @returns {number} Number of handlers successfully executed
         */
        emit(event, data = null) {
            if (!this._enabled) return 0;

            let handlersExecuted = 0;

            // Direct handlers
            const directHandlers = this._handlers.get(event) || [];
            for (const handler of directHandlers) {
                try {
                    handler(data);
                    handlersExecuted++;
                } catch (error) {
                    console.error(`Event handler failed for '${event}':`, error);
                }
            }

            // Wildcard handlers
            for (const {prefix, handler} of this._wildcardHandlers) {
                if (event.startsWith(prefix + ':')) {
                    try {
                        handler(data);
                        handlersExecuted++;
                    } catch (error) {
                        console.error(`Wildcard handler failed for '${event}':`, error);
                    }
                }
            }

            return handlersExecuted;
        }

        /**
         * Unsubscribe a specific handler from an event.
         * @param {string} event - Event name
         * @param {function} handler - The exact handler to remove
         * @returns {boolean} True if handler was found and removed
         */
        off(event, handler) {
            if (event.endsWith(':*')) {
                const prefix = event.slice(0, -2);
                const originalLen = this._wildcardHandlers.length;
                this._wildcardHandlers = this._wildcardHandlers.filter(
                    item => !(item.prefix === prefix && item.handler === handler)
                );
                return this._wildcardHandlers.length < originalLen;
            } else {
                const handlers = this._handlers.get(event);
                if (!handlers) return false;

                const index = handlers.indexOf(handler);
                if (index !== -1) {
                    handlers.splice(index, 1);
                    return true;
                }
                return false;
            }
        }

        /**
         * Clear all handlers for an event, or all events if null.
         * @param {string|null} event - Event name or null for all
         */
        clear(event = null) {
            if (event === null) {
                this._handlers.clear();
                this._wildcardHandlers = [];
            } else if (event.endsWith(':*')) {
                const prefix = event.slice(0, -2);
                // Clear exact event handlers
                const keysToDelete = [];
                for (const key of this._handlers.keys()) {
                    if (key.startsWith(prefix + ':')) {
                        keysToDelete.push(key);
                    }
                }
                keysToDelete.forEach(k => this._handlers.delete(k));
                // Clear wildcard handlers
                this._wildcardHandlers = this._wildcardHandlers.filter(
                    item => item.prefix !== prefix
                );
            } else {
                this._handlers.delete(event);
            }
        }

        /**
         * Subscribe to event, auto-unsubscribe after first emission.
         * @param {string} event - Event name
         * @param {function} handler - Callback
         */
        once(event, handler) {
            const wrapper = (data) => {
                handler(data);
                this.off(event, wrapper);
            };
            this.on(event, wrapper);
        }

        /**
         * Temporarily disable all event emission (for testing).
         */
        disable() {
            this._enabled = false;
        }

        /**
         * Re-enable event emission after disable().
         */
        enable() {
            this._enabled = true;
        }

        /**
         * List all registered event names.
         * @returns {string[]} Sorted list of event names
         */
        getEvents() {
            const events = new Set([...this._handlers.keys()]);
            this._wildcardHandlers.forEach(({prefix}) => {
                events.add(`${prefix}:*`);
            });
            return Array.from(events).sort();
        }

        /**
         * Count handlers registered for an event.
         * @param {string} event - Event name
         * @returns {number} Handler count
         */
        getHandlerCount(event) {
            let count = (this._handlers.get(event) || []).length;

            // Count wildcard handlers that match
            if (event.includes(':')) {
                const prefix = event.split(':')[0];
                count += this._wildcardHandlers.filter(
                    item => item.prefix === prefix
                ).length;
            }

            return count;
        }
    }

    return EventBus;
})();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EventBus;
}

// Global singleton for convenience
if (typeof window !== 'undefined') {
    window.EventBus = EventBus;
    window.EVENT_BUS = new EventBus();
}
