/**
 * @module HardwareInfo
 * @description Extracts low-level hardware and WebGL capabilities
 */
const HardwareInfo = (function () {
    'use strict';

    let _info = null;

    function getInfo() {
        if (_info) return _info;

        _info = {
            gpu: 'Unknown GPU',
            vendor: 'Unknown Vendor',
            renderer: 'Unknown Renderer',
            memory: {
                jsHeapSizeLimit: 0,
                totalJSHeapSize: 0,
                usedJSHeapSize: 0
            },
            limits: {
                maxTextureSize: 0,
                maxCubeMapSize: 0,
                maxRenderBufferSize: 0
            },
            context: 'webgl' // or webgl2
        };

        // 1. Memory (if available)
        if (performance && performance.memory) {
            _updateMemory();
        }

        // 2. WebGL / GPU Info
        try {
            const canvas = document.createElement('canvas');
            let gl = canvas.getContext('webgl');
            if (!gl) {
                gl = canvas.getContext('experimental-webgl');
                _info.context = 'experimental-webgl';
            } else {
                _info.context = 'webgl';
            }

            // Try WebGL2 if available
            const gl2 = canvas.getContext('webgl2');
            if (gl2) {
                gl = gl2;
                _info.context = 'webgl2';
            }

            if (gl) {
                const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                if (debugInfo) {
                    _info.vendor = gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL);
                    _info.renderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
                    _info.gpu = _info.renderer; // Consolidate
                } else {
                    _info.renderer = gl.getParameter(gl.RENDERER);
                    _info.vendor = gl.getParameter(gl.VENDOR);
                }

                _info.limits.maxTextureSize = gl.getParameter(gl.MAX_TEXTURE_SIZE);
                _info.limits.maxCubeMapSize = gl.getParameter(gl.MAX_CUBE_MAP_TEXTURE_SIZE);
                _info.limits.maxRenderBufferSize = gl.getParameter(gl.MAX_RENDERBUFFER_SIZE);
            }
        } catch (e) {
            console.warn('[HardwareInfo] Failed to detect GPU:', e);
        }

        return _info;
    }

    function _updateMemory() {
        if (performance && performance.memory) {
            _info.memory.jsHeapSizeLimit = performance.memory.jsHeapSizeLimit;
            _info.memory.totalJSHeapSize = performance.memory.totalJSHeapSize;
            _info.memory.usedJSHeapSize = performance.memory.usedJSHeapSize;
        }
    }

    function refresh() {
        _updateMemory();
        return _info;
    }

    return {
        get: getInfo,
        refresh: refresh
    };

})();

// Export
if (typeof window !== 'undefined') window.HardwareInfo = HardwareInfo;
if (typeof module !== 'undefined') module.exports = HardwareInfo;
