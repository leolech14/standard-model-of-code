/**
 * @module perf-monitor
 * @description Real-time performance monitoring and FPS diagnostics
 * @responsibility Track frame delivery, detect dropped frames, display HUD
 */

// NOTE: Named _PerfMonitorImpl to avoid conflict with performance.js PERF
const _PerfMonitorImpl = (function () {
    'use strict';

    // Configuration
    const _config = {
        enabled: true,
        maxFrames: 60,
        droppedFrameThreshold: 50
    };

    // State
    const _state = {
        fps: 0,
        frameTime: 0,
        lastFrameTime: 0,
        frameTimes: [],
        renderCalls: 0,
        droppedFrames: 0,
        lastSecond: 0,
        framesThisSecond: 0,
        hudElement: null,
        monitoring: false,
        renderer: null, // Three.js renderer reference
        hardware: null
    };

    /**
     * Initialize the performance monitor
     */
    function init() {
        if (!_config.enabled) return;
        if (_state.hudElement) return; // Idempotent

        // Hardware info
        if (typeof HardwareInfo !== 'undefined') {
            _state.hardware = HardwareInfo.get();
        }

        // Create Enhanced HUD
        _state.hudElement = document.createElement('div');
        _state.hudElement.id = 'perf-hud';
        _state.hudElement.style.cssText = `
            position: fixed; top: 10px; right: 10px; z-index: 99999;
            background: rgba(10, 12, 16, 0.95); color: #eee; font-family: 'SF Mono', monospace;
            font-size: 10px; padding: 0; border-radius: 6px;
            border: 1px solid #333; min-width: 300px; /* Wider for 3 columns */
            box-shadow: 0 4px 12px rgba(0,0,0,0.5);
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0;
            overflow: hidden;
        `;
        document.body.appendChild(_state.hudElement);
        _startMonitoring();
    }

    /**
     * Link a renderer for deep stats
     */
    function setRenderer(renderer) {
        _state.renderer = renderer;
    }

    /**
     * Start the monitoring loop
     */
    function _startMonitoring() {
        if (_state.monitoring) return;
        _state.monitoring = true;

        let frameCount = 0;

        const monitor = () => {
            if (!_state.monitoring) return;

            const now = performance.now();

            // Calculate frame time
            if (_state.lastFrameTime > 0) {
                _state.frameTime = now - _state.lastFrameTime;
                _state.frameTimes.push(_state.frameTime);
                if (_state.frameTimes.length > _config.maxFrames) {
                    _state.frameTimes.shift();
                }

                // Detect dropped frames
                if (_state.frameTime > _config.droppedFrameThreshold) {
                    _state.droppedFrames++;
                }
            }
            _state.lastFrameTime = now;

            // Calculate FPS every second
            const second = Math.floor(now / 1000);
            if (second !== _state.lastSecond) {
                _state.fps = _state.framesThisSecond;
                _state.framesThisSecond = 0;
                _state.lastSecond = second;

                // Low freq updates (memory, hardware)
                if (typeof HardwareInfo !== 'undefined') HardwareInfo.refresh();
            }
            _state.framesThisSecond++;

            // Throttle HUD DOM updates to 10fps to save CPU
            if (frameCount++ % 6 === 0) {
                _updateHUD();
            }

            requestAnimationFrame(monitor);
        };
        requestAnimationFrame(monitor);
    }

    /**
     * Update the HUD display (Enhanced)
     */
    function _updateHUD() {
        if (!_state.hudElement) return;

        const avgFrameTime = _state.frameTimes.length > 0
            ? (_state.frameTimes.reduce((a, b) => a + b, 0) / _state.frameTimes.length).toFixed(1)
            : '0.0';

        // 1. Performance Colors
        let fpsColor = '#4ade80';
        if (_state.fps < 30) fpsColor = '#facc15';
        if (_state.fps < 15) fpsColor = '#f87171';

        // 2. Memory
        let memString = '--';
        if (_state.hardware && _state.hardware.memory) {
            const used = (_state.hardware.memory.usedJSHeapSize / 1048576).toFixed(0);
            const total = (_state.hardware.memory.totalJSHeapSize / 1048576).toFixed(0);
            memString = `${used} / ${total} MB`;
        }

        // 3. Renderer Stats
        let renderInfo = { calls: 0, triangles: 0, geometries: 0 };
        if (_state.renderer && _state.renderer.info) {
            renderInfo.calls = _state.renderer.info.render.calls;
            renderInfo.triangles = _state.renderer.info.render.triangles;
            renderInfo.geometries = _state.renderer.info.memory.geometries;
        }

        // 4. GPU Name
        const gpuName = _state.hardware ? _state.hardware.gpu.replace('ANGLE (', '').replace(')', '') : 'Unknown GPU';

        // TEMPLATE
        _state.hudElement.innerHTML = `
            <div style="padding: 10px; border-right: 1px solid #333;">
                <div style="color:#888; margin-bottom:4px; font-weight:600">PERFORMANCE</div>
                <div style="font-size:18px; color:${fpsColor}; font-weight:bold; letter-spacing:-0.5px">
                    ${_state.fps} <span style="font-size:10px; color:#666">FPS</span>
                </div>
                <div style="margin-top:2px">${avgFrameTime} ms</div>
                <div style="color:#f87171; margin-top:4px">Drops: ${_state.droppedFrames}</div>
                <div style="margin-top:8px; color:#aaa; font-size:9px">MEM: ${memString}</div>
            </div>
            <div style="padding: 10px;">
                <div style="color:#888; margin-bottom:4px; font-weight:600">SCENE & HARDWARE</div>
                <div style="display:flex; justify-content:space-between"><span>Draw Calls:</span> <span>${renderInfo.calls}</span></div>
                <div style="display:flex; justify-content:space-between"><span>Triangles:</span> <span>${(renderInfo.triangles / 1000).toFixed(1)}k</span></div>
                <div style="display:flex; justify-content:space-between"><span>Geometries:</span> <span>${renderInfo.geometries}</span></div>
                
                <div style="margin-top:8px; padding-top:8px; border-top:1px solid #333; color:#666; font-size:9px; line-height:1.2">
                    ${gpuName.substring(0, 40)}...
                </div>
            </div>
        `;
    }

    /**
     * Reset statistics
     */
    function reset() {
        _state.fps = 0;
        _state.frameTime = 0;
        _state.frameTimes = [];
        _state.droppedFrames = 0;
        _state.framesThisSecond = 0;
    }

    /**
     * Log a performance resistance point
     * @param {string} location - Where the resistance occurred
     * @param {number} duration - Duration in milliseconds
     */
    function logResistance(location, duration) {
        if (duration > 16) {
            console.warn(`[PERF RESISTANCE] ${location}: ${duration.toFixed(1)}ms (>${Math.floor(duration / 16.67)} frames)`);
        }
    }

    /**
     * Stop monitoring
     */
    function stop() {
        _state.monitoring = false;
        if (_state.hudElement && _state.hudElement.parentNode) {
            _state.hudElement.parentNode.removeChild(_state.hudElement);
        }
        _state.hudElement = null;
    }

    /**
     * Toggle HUD visibility
     */
    function toggle() {
        if (_state.hudElement) {
            _state.hudElement.style.display =
                _state.hudElement.style.display === 'none' ? 'block' : 'none';
        }
    }

    /**
     * Enable/disable monitoring
     * @param {boolean} enabled
     */
    function setEnabled(enabled) {
        _config.enabled = enabled;
        if (!enabled) {
            stop();
        } else if (!_state.monitoring) {
            init();
        }
    }

    // Public API
    return {
        init,
        stop,
        reset,
        toggle,
        setEnabled,
        setRenderer,
        logResistance,
        // Read-only state access
        get fps() { return _state.fps; },
        get frameTime() { return _state.frameTime; },
        get droppedFrames() { return _state.droppedFrames; },
        get enabled() { return _config.enabled; },
        get monitoring() { return _state.monitoring; }
    };
})();

// Export as PERF_MONITOR (PERF is provided by performance.js)
const PERF_MONITOR = _PerfMonitorImpl;

// Expose globally - only PERF_MONITOR, PERF comes from performance.js
window.PERF_MONITOR = PERF_MONITOR;

// BACKWARD COMPAT: Expose logResistance globally as some modules expect it
window.logResistance = PERF_MONITOR.logResistance;
