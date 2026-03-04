/**
 * ═══════════════════════════════════════════════════════════════════════════
 * HOLARCHY MODULE — 3D Architectural Layer View
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * Renders Collider graph data as a layered holarchy:
 *   - Y axis = architectural layer (DOMAIN, APPLICATION, PRESENTATION, etc.)
 *   - Node shape = atom type (Box for structural, Sphere for behavioral)
 *   - Node size = degree (in + out connections)
 *   - Edges = calls (solid), contains (dashed)
 *
 * Uses THREE.InstancedMesh for 60fps with 5000+ nodes.
 * Shares window.GRAPH_DATA with the force-graph view.
 *
 * @module HOLARCHY
 * @version 1.0.0
 */

// ═══════════════════════════════════════════════════════════════════════
// CONSTANTS
// ═══════════════════════════════════════════════════════════════════════

const LAYER_MAP = {
    'DOMAIN':         0,
    'APPLICATION':    1,
    'PRESENTATION':   2,
    'INTERFACE':      3,
    'INFRASTRUCTURE': 4,
    'CROSS_CUTTING':  5,
    'TEST':           6,
    'UNKNOWN':        7
};

const LAYER_HEIGHT = 40;        // Y spacing between layers
const SPREAD_RADIUS = 200;      // XZ spread within a layer
const LOD_LABEL_DISTANCE = 300; // Hide labels beyond this camera distance
const INSTANCED_THRESHOLD = 200; // Use InstancedMesh above this node count

// ═══════════════════════════════════════════════════════════════════════
// STATE
// ═══════════════════════════════════════════════════════════════════════

let _scene = null;
let _camera = null;
let _renderer = null;
let _controls = null;
let _container = null;
let _animFrameId = null;
let _isActive = false;
let _nodeData = [];
let _edgeData = [];
let _labelSprites = [];
let _instancedMeshes = {};

// ═══════════════════════════════════════════════════════════════════════
// TAB UI
// ═══════════════════════════════════════════════════════════════════════

/**
 * Create tab toggle bar and holarchy container in the DOM.
 * Inserts above the graph container.
 */
function createTabUI() {
    const graphEl = document.getElementById('3d-graph');
    if (!graphEl) return;

    // Tab bar
    const tabBar = document.createElement('div');
    tabBar.id = 'view-tab-bar';
    tabBar.style.cssText = `
        position: fixed;
        top: 8px;
        right: 16px;
        z-index: 1000;
        display: flex;
        gap: 2px;
        background: var(--color-bg-panel-dark, rgba(5, 8, 12, 0.9));
        border: 1px solid var(--color-border-default, rgba(255,255,255,0.08));
        border-radius: 6px;
        padding: 3px;
        font-family: var(--typography-family-sans, Inter, sans-serif);
        font-size: var(--typography-size-sm, 11px);
    `;

    const btnForce = _createTabBtn('Force Graph', 'force', true);
    const btnHolo = _createTabBtn('Holarchy', 'holarchy', false);

    tabBar.appendChild(btnForce);
    tabBar.appendChild(btnHolo);

    // Holarchy container (hidden by default)
    _container = document.createElement('div');
    _container.id = 'holarchy-view';
    _container.style.cssText = `
        position: fixed;
        inset: 0;
        display: none;
        background: var(--color-viz-canvas-bg, #0a0b0f);
    `;

    graphEl.parentNode.insertBefore(tabBar, graphEl);
    graphEl.parentNode.insertBefore(_container, graphEl.nextSibling);

    // Tab click handlers
    btnForce.addEventListener('click', () => switchView('force'));
    btnHolo.addEventListener('click', () => switchView('holarchy'));
}

function _createTabBtn(label, viewId, active) {
    const btn = document.createElement('button');
    btn.textContent = label;
    btn.dataset.view = viewId;
    btn.className = 'view-tab-btn' + (active ? ' active' : '');
    btn.style.cssText = `
        padding: 5px 14px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: inherit;
        font-family: inherit;
        color: var(--color-text-secondary, rgba(255,255,255,0.7));
        background: transparent;
        transition: all 150ms ease;
    `;
    if (active) {
        btn.style.background = 'var(--color-accent-primary-bg, rgba(100,120,150,0.2))';
        btn.style.color = 'var(--color-text-primary, #fff)';
    }
    return btn;
}

/**
 * Switch between force-graph and holarchy views.
 * @param {string} viewId - 'force' or 'holarchy'
 */
function switchView(viewId) {
    const graphEl = document.getElementById('3d-graph');
    const holoEl = document.getElementById('holarchy-view');
    if (!graphEl || !holoEl) return;

    // Toggle visibility
    graphEl.style.display = viewId === 'force' ? 'block' : 'none';
    holoEl.style.display = viewId === 'holarchy' ? 'block' : 'none';

    // Update tab buttons
    document.querySelectorAll('.view-tab-btn').forEach(btn => {
        const isActive = btn.dataset.view === viewId;
        btn.classList.toggle('active', isActive);
        btn.style.background = isActive
            ? 'var(--color-accent-primary-bg, rgba(100,120,150,0.2))'
            : 'transparent';
        btn.style.color = isActive
            ? 'var(--color-text-primary, #fff)'
            : 'var(--color-text-secondary, rgba(255,255,255,0.7))';
    });

    if (viewId === 'holarchy') {
        if (!_scene) {
            initScene();
            loadData();
        }
        _isActive = true;
        animate();
    } else {
        _isActive = false;
        if (_animFrameId) {
            cancelAnimationFrame(_animFrameId);
            _animFrameId = null;
        }
    }

    // Pause/resume force graph
    const Graph = window.Graph;
    if (Graph) {
        if (viewId === 'force' && typeof Graph.resumeAnimation === 'function') {
            Graph.resumeAnimation();
        } else if (viewId === 'holarchy' && typeof Graph.pauseAnimation === 'function') {
            Graph.pauseAnimation();
        }
    }
}

// ═══════════════════════════════════════════════════════════════════════
// THREE.js SCENE
// ═══════════════════════════════════════════════════════════════════════

function initScene() {
    if (!_container || typeof THREE === 'undefined') return;

    // Renderer
    _renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
    _renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    _renderer.setSize(window.innerWidth, window.innerHeight);
    _container.appendChild(_renderer.domElement);

    // Scene
    _scene = new THREE.Scene();
    _updateSceneBackground();

    // Camera (perspective for depth)
    _camera = new THREE.PerspectiveCamera(
        50, window.innerWidth / window.innerHeight, 1, 5000
    );
    _camera.position.set(0, LAYER_HEIGHT * 4, SPREAD_RADIUS * 1.5);
    _camera.lookAt(0, LAYER_HEIGHT * 3, 0);

    // OrbitControls
    _controls = new THREE.OrbitControls(_camera, _renderer.domElement);
    _controls.enableDamping = true;
    _controls.dampingFactor = 0.08;
    _controls.target.set(0, LAYER_HEIGHT * 3, 0);

    // Lighting
    const ambient = new THREE.AmbientLight(0xffffff, 0.6);
    _scene.add(ambient);
    const directional = new THREE.DirectionalLight(0xffffff, 0.8);
    directional.position.set(100, 200, 100);
    _scene.add(directional);

    // Grid planes per layer
    _addLayerGrids();

    // Handle resize
    window.addEventListener('resize', _onResize);
}

function _updateSceneBackground() {
    if (!_scene) return;
    const bg = getComputedStyle(document.documentElement)
        .getPropertyValue('--color-viz-canvas-bg')?.trim() || '#0a0b0f';
    _scene.background = new THREE.Color(bg);
}

function _addLayerGrids() {
    const layerNames = Object.keys(LAYER_MAP);
    for (const name of layerNames) {
        const y = LAYER_MAP[name] * LAYER_HEIGHT;
        const grid = new THREE.GridHelper(SPREAD_RADIUS * 2, 20, 0x333340, 0x222230);
        grid.position.y = y;
        grid.material.opacity = 0.15;
        grid.material.transparent = true;
        _scene.add(grid);

        // Layer label
        const sprite = _makeTextSprite(name, { fontSize: 14, color: '#888898' });
        sprite.position.set(-SPREAD_RADIUS - 20, y + 5, 0);
        sprite.scale.set(60, 15, 1);
        _scene.add(sprite);
    }
}

// ═══════════════════════════════════════════════════════════════════════
// DATA LOADING
// ═══════════════════════════════════════════════════════════════════════

function loadData() {
    const data = window.GRAPH_DATA;
    if (!data || !data.nodes) {
        console.warn('[Holarchy] No GRAPH_DATA available');
        return;
    }

    _nodeData = data.nodes || [];
    _edgeData = data.links || data.edges || [];

    const nodeCount = _nodeData.length;
    console.log(`[Holarchy] Loading ${nodeCount} nodes, ${_edgeData.length} edges`);

    if (nodeCount > INSTANCED_THRESHOLD) {
        _buildInstanced();
    } else {
        _buildIndividual();
    }

    _buildEdges();
}

// ═══════════════════════════════════════════════════════════════════════
// INSTANCED RENDERING (1000+ nodes)
// ═══════════════════════════════════════════════════════════════════════

function _buildInstanced() {
    const boxGeom = new THREE.BoxGeometry(2, 2, 2);
    const sphereGeom = new THREE.SphereGeometry(1.2, 8, 6);

    // Separate nodes by shape type
    const structural = []; // Box
    const behavioral = []; // Sphere

    _nodeData.forEach((node, i) => {
        const atom = (node.atom || '').toUpperCase();
        // Structural atoms: ORG, DAT, EXT categories → Box
        // Behavioral atoms: LOG, EXE categories → Sphere
        const isStructural = atom.startsWith('CORE.') || atom.startsWith('ARCH.') ||
                             atom.startsWith('EXT.') || !atom;
        const pos = _nodePosition(node, i);
        const size = _nodeSize(node);
        const color = new THREE.Color(node.color || '#707080');

        if (isStructural) {
            structural.push({ pos, size, color, index: i });
        } else {
            behavioral.push({ pos, size, color, index: i });
        }
    });

    // Create instanced meshes
    if (structural.length > 0) {
        _instancedMeshes.box = _createInstancedMesh(boxGeom, structural);
        _scene.add(_instancedMeshes.box);
    }
    if (behavioral.length > 0) {
        _instancedMeshes.sphere = _createInstancedMesh(sphereGeom, behavioral);
        _scene.add(_instancedMeshes.sphere);
    }

    // Add labels for high-degree nodes only (LOD)
    const degreeThreshold = _nodeData.length > 1000 ? 10 : 3;
    _nodeData.forEach((node, i) => {
        const degree = (node.in_degree || 0) + (node.out_degree || 0);
        if (degree >= degreeThreshold && node.label) {
            const pos = _nodePosition(node, i);
            const sprite = _makeTextSprite(node.label, { fontSize: 10, color: '#aaaaaa' });
            sprite.position.set(pos.x, pos.y + 3, pos.z);
            sprite.scale.set(30, 8, 1);
            sprite.userData = { isLabel: true };
            _labelSprites.push(sprite);
            _scene.add(sprite);
        }
    });
}

function _createInstancedMesh(geometry, items) {
    const material = new THREE.MeshPhongMaterial({
        vertexColors: false,
        transparent: true,
        opacity: 0.85,
    });

    const mesh = new THREE.InstancedMesh(geometry, material, items.length);
    const dummy = new THREE.Object3D();
    const colorAttr = new Float32Array(items.length * 3);

    items.forEach((item, i) => {
        dummy.position.copy(item.pos);
        const s = item.size;
        dummy.scale.set(s, s, s);
        dummy.updateMatrix();
        mesh.setMatrixAt(i, dummy.matrix);

        colorAttr[i * 3] = item.color.r;
        colorAttr[i * 3 + 1] = item.color.g;
        colorAttr[i * 3 + 2] = item.color.b;
    });

    mesh.instanceMatrix.needsUpdate = true;

    // Per-instance color
    mesh.instanceColor = new THREE.InstancedBufferAttribute(colorAttr, 3);
    mesh.material.vertexColors = false; // Use instanceColor

    return mesh;
}

// ═══════════════════════════════════════════════════════════════════════
// INDIVIDUAL RENDERING (<200 nodes)
// ═══════════════════════════════════════════════════════════════════════

function _buildIndividual() {
    _nodeData.forEach((node, i) => {
        const pos = _nodePosition(node, i);
        const size = _nodeSize(node);
        const color = new THREE.Color(node.color || '#707080');

        const atom = (node.atom || '').toUpperCase();
        const isStructural = atom.startsWith('CORE.') || atom.startsWith('ARCH.') ||
                             atom.startsWith('EXT.') || !atom;

        let geometry;
        if (isStructural) {
            geometry = new THREE.BoxGeometry(size * 2, size * 2, size * 2);
        } else {
            geometry = new THREE.SphereGeometry(size * 1.2, 8, 6);
        }

        const material = new THREE.MeshPhongMaterial({
            color: color,
            transparent: true,
            opacity: 0.85,
        });

        const mesh = new THREE.Mesh(geometry, material);
        mesh.position.copy(pos);
        _scene.add(mesh);

        // Label
        if (node.label) {
            const sprite = _makeTextSprite(node.label, { fontSize: 10, color: '#aaaaaa' });
            sprite.position.set(pos.x, pos.y + size + 2, pos.z);
            sprite.scale.set(30, 8, 1);
            sprite.userData = { isLabel: true };
            _labelSprites.push(sprite);
            _scene.add(sprite);
        }
    });
}

// ═══════════════════════════════════════════════════════════════════════
// EDGE RENDERING
// ═══════════════════════════════════════════════════════════════════════

function _buildEdges() {
    // Build node index for edge lookups
    const nodeIndex = {};
    _nodeData.forEach((node, i) => {
        const id = node.id || node.name || i;
        nodeIndex[id] = i;
    });

    const positions = [];
    const colors = [];

    _edgeData.forEach(edge => {
        const srcIdx = nodeIndex[edge.source] ?? nodeIndex[edge.source?.id];
        const tgtIdx = nodeIndex[edge.target] ?? nodeIndex[edge.target?.id];
        if (srcIdx === undefined || tgtIdx === undefined) return;

        const srcPos = _nodePosition(_nodeData[srcIdx], srcIdx);
        const tgtPos = _nodePosition(_nodeData[tgtIdx], tgtIdx);

        positions.push(srcPos.x, srcPos.y, srcPos.z);
        positions.push(tgtPos.x, tgtPos.y, tgtPos.z);

        // Edge color — use encoded or fallback
        const edgeColor = new THREE.Color(edge.color || '#404050');
        colors.push(edgeColor.r, edgeColor.g, edgeColor.b);
        colors.push(edgeColor.r, edgeColor.g, edgeColor.b);
    });

    if (positions.length === 0) return;

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));

    const material = new THREE.LineBasicMaterial({
        vertexColors: true,
        transparent: true,
        opacity: 0.12,
        linewidth: 1,
    });

    const lines = new THREE.LineSegments(geometry, material);
    _scene.add(lines);
}

// ═══════════════════════════════════════════════════════════════════════
// NODE POSITIONING
// ═══════════════════════════════════════════════════════════════════════

function _nodePosition(node, index) {
    // Y = architectural layer
    const layerName = (node.ring || node.layer || 'UNKNOWN').toUpperCase();
    const layerIdx = LAYER_MAP[layerName] ?? LAYER_MAP['UNKNOWN'];
    const y = layerIdx * LAYER_HEIGHT;

    // XZ = golden angle spiral within each layer
    const angle = index * 2.399963; // Golden angle in radians
    const radius = Math.sqrt(index + 1) * 8;
    const x = Math.cos(angle) * Math.min(radius, SPREAD_RADIUS);
    const z = Math.sin(angle) * Math.min(radius, SPREAD_RADIUS);

    return new THREE.Vector3(x, y, z);
}

function _nodeSize(node) {
    const degree = (node.in_degree || 0) + (node.out_degree || 0);
    return Math.max(0.8, Math.min(4, 0.8 + degree * 0.15));
}

// ═══════════════════════════════════════════════════════════════════════
// TEXT SPRITES
// ═══════════════════════════════════════════════════════════════════════

function _makeTextSprite(text, opts = {}) {
    const fontSize = opts.fontSize || 12;
    const color = opts.color || '#ffffff';

    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = 256;
    canvas.height = 64;

    ctx.font = `${fontSize}px ${getComputedStyle(document.documentElement)
        .getPropertyValue('--typography-family-sans')?.trim() || 'Inter, sans-serif'}`;
    ctx.fillStyle = color;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    // Truncate long labels
    const maxChars = 24;
    const label = text.length > maxChars ? text.slice(0, maxChars - 1) + '\u2026' : text;
    ctx.fillText(label, 128, 32);

    const texture = new THREE.CanvasTexture(canvas);
    texture.minFilter = THREE.LinearFilter;

    const material = new THREE.SpriteMaterial({
        map: texture,
        transparent: true,
        depthWrite: false,
    });

    return new THREE.Sprite(material);
}

// ═══════════════════════════════════════════════════════════════════════
// ANIMATION LOOP
// ═══════════════════════════════════════════════════════════════════════

function animate() {
    if (!_isActive) return;
    _animFrameId = requestAnimationFrame(animate);

    _controls.update();

    // LOD: hide labels when camera is far
    const camDist = _camera.position.length();
    _labelSprites.forEach(sprite => {
        sprite.visible = camDist < LOD_LABEL_DISTANCE;
    });

    _renderer.render(_scene, _camera);
}

function _onResize() {
    if (!_camera || !_renderer) return;
    _camera.aspect = window.innerWidth / window.innerHeight;
    _camera.updateProjectionMatrix();
    _renderer.setSize(window.innerWidth, window.innerHeight);
}

// ═══════════════════════════════════════════════════════════════════════
// THEME UPDATE
// ═══════════════════════════════════════════════════════════════════════

/**
 * Update holarchy view when theme changes.
 * Called by THEME.set() when the holarchy tab is present.
 * @param {string} themeName - New theme name
 */
function updateTheme(themeName) {
    _updateSceneBackground();

    // Update grid and label colors based on theme lightness
    if (!_scene) return;
    const isLight = ['light', 'aquarela', 'scientific-paper'].includes(themeName);
    const gridColor = isLight ? 0xcccccc : 0x333340;
    const gridSubColor = isLight ? 0xdddddd : 0x222230;

    _scene.traverse(obj => {
        if (obj instanceof THREE.GridHelper) {
            obj.material.color.setHex(gridColor);
            if (obj.material.length > 1) {
                obj.material[1].color.setHex(gridSubColor);
            }
        }
    });
}

// ═══════════════════════════════════════════════════════════════════════
// CLEANUP
// ═══════════════════════════════════════════════════════════════════════

function dispose() {
    _isActive = false;
    if (_animFrameId) cancelAnimationFrame(_animFrameId);
    if (_renderer) {
        _renderer.dispose();
        _renderer.domElement.remove();
    }
    if (_controls) _controls.dispose();
    _scene = null;
    _camera = null;
    _renderer = null;
    _controls = null;
    _labelSprites = [];
    _instancedMeshes = {};
    window.removeEventListener('resize', _onResize);
}

// ═══════════════════════════════════════════════════════════════════════
// MODULE EXPORT
// ═══════════════════════════════════════════════════════════════════════

export const HOLARCHY = {
    createTabUI,
    switchView,
    updateTheme,
    dispose,
    get isActive() { return _isActive; }
};

export {
    createTabUI,
    switchView,
    updateTheme,
    dispose
};

window.HOLARCHY = HOLARCHY;

console.log('[Module] HOLARCHY loaded - holarchy 3D view');
