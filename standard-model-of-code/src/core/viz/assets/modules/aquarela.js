/**
 * AQUARELA - Dynamic Ink Background System
 *
 * Creates a subtle, animated background with organic movement
 * inspired by watercolor/ink diffusion.
 */

const AQUARELA = (function () {
    'use strict';

    let _canvas = null;
    let _ctx = null;
    let _width = 0;
    let _height = 0;
    let _particles = [];
    let _animationId = null;
    let _stopped = false;

    const CONFIG = {
        particleCount: 15,
        baseRadius: 200,
        speed: 0.15,
        opacity: 0.08,
        colors: [
            'hsla(220, 30%, 20%, 0.1)',
            'hsla(280, 20%, 15%, 0.1)',
            'hsla(180, 25%, 15%, 0.1)'
        ]
    };

    function init() {
        if (_canvas) return;

        _canvas = document.createElement('canvas');
        _canvas.id = 'aquarela-canvas';
        _canvas.style.position = 'fixed';
        _canvas.style.top = '0';
        _canvas.style.left = '0';
        _canvas.style.width = '100vw';
        _canvas.style.height = '100vh';
        _canvas.style.zIndex = '-1';
        _canvas.style.pointerEvents = 'none';
        _canvas.style.background = '#03040a';

        document.body.appendChild(_canvas);
        _ctx = _canvas.getContext('2d');

        window.addEventListener('resize', resize);
        resize();

        createParticles();
        animate();

        console.log('[AQUARELA] Background initialized');
    }

    function resize() {
        _width = window.innerWidth;
        _height = window.innerHeight;
        const dpr = window.devicePixelRatio || 1;
        _canvas.width = _width * dpr;
        _canvas.height = _height * dpr;
        _ctx.scale(dpr, dpr);
    }

    function createParticles() {
        _particles = [];
        for (let i = 0; i < CONFIG.particleCount; i++) {
            _particles.push({
                x: Math.random() * _width,
                y: Math.random() * _height,
                vx: (Math.random() - 0.5) * CONFIG.speed,
                vy: (Math.random() - 0.5) * CONFIG.speed,
                r: CONFIG.baseRadius * (0.8 + Math.random() * 0.4),
                color: CONFIG.colors[i % CONFIG.colors.length],
                phase: Math.random() * Math.PI * 2
            });
        }
    }

    function animate() {
        if (_stopped) return;

        _ctx.fillStyle = '#03040a'; // Background deep void
        _ctx.fillRect(0, 0, _width, _height);

        _ctx.globalCompositeOperation = 'screen';

        _particles.forEach(p => {
            // Update position
            p.x += p.vx;
            p.y += p.vy;

            // Simple oscillation
            p.phase += 0.005;
            const pulse = Math.sin(p.phase) * 20;
            const r = p.r + pulse;

            // Wraparound
            if (p.x < -r) p.x = _width + r;
            if (p.x > _width + r) p.x = -r;
            if (p.y < -r) p.y = _height + r;
            if (p.y > _height + r) p.y = -r;

            // Draw radial gradient
            const grad = _ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, r);
            grad.addColorStop(0, p.color);
            grad.addColorStop(1, 'transparent');

            _ctx.fillStyle = grad;
            _ctx.beginPath();
            _ctx.arc(p.x, p.y, r, 0, Math.PI * 2);
            _ctx.fill();
        });

        _animationId = requestAnimationFrame(animate);
    }

    function stop() {
        _stopped = true;
        if (_animationId) cancelAnimationFrame(_animationId);
    }

    function start() {
        if (!_stopped) return;
        _stopped = false;
        animate();
    }

    return {
        init,
        stop,
        start
    };

})();

if (typeof window !== 'undefined') {
    window.AQUARELA = AQUARELA;
}
