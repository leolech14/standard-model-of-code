/**
 * EVENT BUS MODULE
 *
 * Decoupled communication between panels and UI components.
 * Simple publish/subscribe pattern for loose coupling.
 *
 * @module EVENT_BUS
 *
 * Usage:
 *   EVENT_BUS.on('filter:changed', data => console.log(data))
 *   EVENT_BUS.emit('filter:changed', { search: 'test' })
 *   EVENT_BUS.off('filter:changed', handler)
 *
 * Standard Events:
 *   - filter:changed      - Filter state updated
 *   - selection:changed   - Node selection changed
 *   - colorBy:changed     - Color mode changed
 *   - palette:changed     - Color palette changed
 *   - layout:changed      - Layout preset changed
 *   - panel:collapsed     - Panel collapsed/expanded
 *   - panel:moved         - Panel position changed
 *   - graph:updated       - Graph data changed
 */

window.EVENT_BUS = (function() {
    'use strict';

    const _listeners = new Map();
    const _onceListeners = new Map();

    function on(event, callback) {
        if (typeof callback !== 'function') return () => {};
        if (!_listeners.has(event)) _listeners.set(event, []);
        _listeners.get(event).push(callback);
        return () => off(event, callback);
    }

    function once(event, callback) {
        if (typeof callback !== 'function') return () => {};
        if (!_onceListeners.has(event)) _onceListeners.set(event, []);
        _onceListeners.get(event).push(callback);
        return () => {
            const cbs = _onceListeners.get(event);
            if (cbs) _onceListeners.set(event, cbs.filter(cb => cb !== callback));
        };
    }

    function off(event, callback) {
        const cbs = _listeners.get(event);
        if (cbs) _listeners.set(event, cbs.filter(cb => cb !== callback));
        const onceCbs = _onceListeners.get(event);
        if (onceCbs) _onceListeners.set(event, onceCbs.filter(cb => cb !== callback));
    }

    function emit(event, data) {
        (_listeners.get(event) || []).forEach(cb => {
            try { cb(data); } catch (e) { console.error(`[EVENT_BUS] ${event}:`, e); }
        });
        const onceCbs = _onceListeners.get(event) || [];
        if (onceCbs.length > 0) {
            onceCbs.forEach(cb => {
                try { cb(data); } catch (e) { console.error(`[EVENT_BUS] ${event}:`, e); }
            });
            _onceListeners.set(event, []);
        }
    }

    function clear(event) {
        if (event) {
            _listeners.delete(event);
            _onceListeners.delete(event);
        } else {
            _listeners.clear();
            _onceListeners.clear();
        }
    }

    return { on, once, off, emit, clear };
})();

console.log('[Module] EVENT_BUS loaded');
