/**
 * REFRESH THROTTLE MODULE
 *
 * Prevents excessive Graph.refresh() calls that can cause performance issues.
 * Implements frame-budget-aware throttling at 60fps max.
 *
 * Fixes ARCH-003: Unthrottled Graph.refresh() calls
 *
 * Usage:
 *   REFRESH.throttled()     // Request a throttled refresh
 *   REFRESH.force()         // Force immediate refresh (use sparingly)
 *   REFRESH.stats           // Get refresh statistics
 */

const REFRESH = (function() {
    'use strict';

    // =========================================================================
    // CONFIGURATION
    // =========================================================================

    const CONFIG = {
        minInterval: 16,      // 60fps max (1000ms / 60 = 16.67ms)
        maxPending: 3,        // Max queued refresh requests before forcing
        logThreshold: 100     // Log warning if more than N refreshes/second
    };

    // =========================================================================
    // STATE
    // =========================================================================

    let _pending = false;
    let _lastRefresh = 0;
    let _rafId = null;
    let _pendingCount = 0;

    // Statistics
    let _stats = {
        totalCalls: 0,
        throttledCalls: 0,
        actualRefreshes: 0,
        lastSecondRefreshes: 0,
        currentSecondRefreshes: 0,
        lastSecond: 0
    };

    // =========================================================================
    // CORE FUNCTIONS
    // =========================================================================

    /**
     * Request a throttled graph refresh.
     * Multiple calls within the same frame are coalesced into one refresh.
     */
    function throttled() {
        _stats.totalCalls++;
        _pendingCount++;

        // Track calls per second for diagnostics
        const now = performance.now();
        const currentSecond = Math.floor(now / 1000);
        if (currentSecond !== _stats.lastSecond) {
            _stats.lastSecondRefreshes = _stats.currentSecondRefreshes;
            _stats.currentSecondRefreshes = 0;
            _stats.lastSecond = currentSecond;

            // Warn if too many refreshes
            if (_stats.lastSecondRefreshes > CONFIG.logThreshold) {
                console.warn(`[REFRESH] High refresh rate: ${_stats.lastSecondRefreshes}/s`);
            }
        }

        // If already pending, don't queue another
        if (_pending) {
            _stats.throttledCalls++;

            // Force refresh if too many pending
            if (_pendingCount >= CONFIG.maxPending) {
                _doRefresh();
            }
            return;
        }

        // Check if enough time has passed since last refresh
        const elapsed = now - _lastRefresh;
        if (elapsed >= CONFIG.minInterval) {
            // Enough time passed, refresh immediately
            _doRefresh();
        } else {
            // Schedule refresh for next frame
            _pending = true;
            _rafId = requestAnimationFrame(() => {
                _pending = false;
                _doRefresh();
            });
        }
    }

    /**
     * Force an immediate refresh, bypassing throttle.
     * Use sparingly - for critical updates only.
     */
    function force() {
        // Cancel any pending throttled refresh
        if (_rafId) {
            cancelAnimationFrame(_rafId);
            _rafId = null;
        }
        _pending = false;
        _doRefresh();
    }

    /**
     * Internal: Perform the actual refresh
     */
    function _doRefresh() {
        _lastRefresh = performance.now();
        _pendingCount = 0;
        _stats.actualRefreshes++;
        _stats.currentSecondRefreshes++;

        // Call the global Graph.refresh() if available
        if (typeof Graph !== 'undefined' && Graph && Graph.refresh) {
            Graph.refresh();
        }
    }

    /**
     * Cancel any pending refresh
     */
    function cancel() {
        if (_rafId) {
            cancelAnimationFrame(_rafId);
            _rafId = null;
        }
        _pending = false;
        _pendingCount = 0;
    }

    /**
     * Reset statistics
     */
    function resetStats() {
        _stats = {
            totalCalls: 0,
            throttledCalls: 0,
            actualRefreshes: 0,
            lastSecondRefreshes: 0,
            currentSecondRefreshes: 0,
            lastSecond: 0
        };
    }

    // =========================================================================
    // PUBLIC API
    // =========================================================================

    return {
        throttled,
        force,
        cancel,
        resetStats,

        // Config (read-only access, can be modified via setConfig)
        get config() { return { ...CONFIG }; },
        setConfig(key, value) {
            if (key in CONFIG) {
                CONFIG[key] = value;
            }
        },

        // Statistics
        get stats() {
            return {
                ..._stats,
                throttleRatio: _stats.totalCalls > 0
                    ? (_stats.throttledCalls / _stats.totalCalls * 100).toFixed(1) + '%'
                    : '0%',
                pending: _pending,
                pendingCount: _pendingCount
            };
        },

        // Debug
        debug() {
            console.log('[REFRESH] Stats:', this.stats);
            console.log('[REFRESH] Config:', CONFIG);
        }
    };
})();
