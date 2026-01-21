/**
 * HULL VISUALIZER - SDF-Based Organic Membranes
 * 
 * Renders file group boundaries using Signed Distance Functions.
 * GPU-accelerated via WebGL shaders for smooth, organic membrane look.
 * 
 * Advantages over Metaballs/Marching Cubes:
 * - Implicit smooth blending between overlapping groups
 * - Real-time performance with 100+ groups
 * - Distance queries for hit testing
 * - Smooth normals for lighting
 * 
 * @usage
 *   const hulls = new HullVisualizer(scene, renderer);
 *   hulls.update(nodesByFile, colorProvider);
 *   hulls.setBlendFactor(0.5); // Membrane smoothness
 *   hulls.dispose();
 */

const HullVisualizer = (function () {
    'use strict';

    // =========================================================================
    // SHADER CODE
    // =========================================================================

    const VERTEX_SHADER = `
        varying vec3 vWorldPos;
        varying vec3 vNormal;
        
        void main() {
            vWorldPos = (modelMatrix * vec4(position, 1.0)).xyz;
            vNormal = normalize(normalMatrix * normal);
            gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
    `;

    // Fragment shader with SDF smooth union
    const FRAGMENT_SHADER = `
        precision highp float;
        
        uniform vec3 uCenters[64];      // Up to 64 group centers
        uniform float uRadii[64];       // Corresponding radii
        uniform vec3 uColors[64];       // Group colors
        uniform int uGroupCount;        // Active group count
        uniform float uBlendFactor;     // Smooth union factor (higher = more blending)
        uniform float uOpacity;         // Overall opacity
        uniform vec3 uCameraPos;        // Camera position for fresnel
        
        varying vec3 vWorldPos;
        varying vec3 vNormal;
        
        // Smooth minimum (for organic blending)
        float smin(float a, float b, float k) {
            float h = clamp(0.5 + 0.5 * (b - a) / k, 0.0, 1.0);
            return mix(b, a, h) - k * h * (1.0 - h);
        }
        
        // SDF for a sphere
        float sdSphere(vec3 p, vec3 center, float radius) {
            return length(p - center) - radius;
        }
        
        // Compute combined SDF for all groups
        float sceneSDF(vec3 p) {
            if (uGroupCount == 0) return 1000.0;
            
            float d = sdSphere(p, uCenters[0], uRadii[0]);
            
            for (int i = 1; i < 64; i++) {
                if (i >= uGroupCount) break;
                float di = sdSphere(p, uCenters[i], uRadii[i]);
                d = smin(d, di, uBlendFactor);
            }
            
            return d;
        }
        
        // Get blended color based on distance to each group
        vec3 getBlendedColor(vec3 p) {
            if (uGroupCount == 0) return vec3(0.5);
            
            vec3 colorSum = vec3(0.0);
            float weightSum = 0.0;
            
            for (int i = 0; i < 64; i++) {
                if (i >= uGroupCount) break;
                float d = length(p - uCenters[i]);
                float weight = 1.0 / (d * d + 0.01);
                colorSum += uColors[i] * weight;
                weightSum += weight;
            }
            
            return colorSum / max(weightSum, 0.001);
        }
        
        void main() {
            float sdf = sceneSDF(vWorldPos);
            
            // Only render near the surface (within membrane thickness)
            float thickness = uBlendFactor * 0.5;
            if (abs(sdf) > thickness) discard;
            
            // Compute normal from SDF gradient
            vec3 eps = vec3(0.01, 0.0, 0.0);
            vec3 sdfNormal = normalize(vec3(
                sceneSDF(vWorldPos + eps.xyy) - sceneSDF(vWorldPos - eps.xyy),
                sceneSDF(vWorldPos + eps.yxy) - sceneSDF(vWorldPos - eps.yxy),
                sceneSDF(vWorldPos + eps.yyx) - sceneSDF(vWorldPos - eps.yyx)
            ));
            
            // Fresnel effect for glass-like appearance
            vec3 viewDir = normalize(uCameraPos - vWorldPos);
            float fresnel = pow(1.0 - abs(dot(viewDir, sdfNormal)), 2.0);
            
            // Get blended color
            vec3 color = getBlendedColor(vWorldPos);
            
            // Edge fade based on SDF distance
            float edgeFade = 1.0 - smoothstep(0.0, thickness, abs(sdf));
            
            // Final color with fresnel rim lighting
            vec3 finalColor = color + fresnel * 0.3;
            float finalOpacity = uOpacity * edgeFade * (0.3 + fresnel * 0.5);
            
            gl_FragColor = vec4(finalColor, finalOpacity);
        }
    `;

    // =========================================================================
    // FALLBACK: Simple sphere-based visualization (when shaders unavailable)
    // =========================================================================

    function createFallbackMesh(center, radius, color, THREE) {
        const geometry = new THREE.SphereGeometry(radius, 24, 24);
        const material = new THREE.MeshPhysicalMaterial({
            color: color,
            transparent: true,
            opacity: 0.15,
            roughness: 0.1,
            metalness: 0.0,
            clearcoat: 0.3,
            side: THREE.DoubleSide,
            depthWrite: false
        });

        const mesh = new THREE.Mesh(geometry, material);
        mesh.position.copy(center);
        mesh.renderOrder = -1; // Render behind nodes

        return mesh;
    }

    // =========================================================================
    // MAIN CLASS
    // =========================================================================

    class HullVisualizer {
        constructor(scene, renderer, options = {}) {
            this.scene = scene;
            this.renderer = renderer;
            this.options = {
                maxGroups: 64,
                blendFactor: 2.0,
                opacity: 0.25,
                paddingFactor: 1.3,
                minRadius: 5,
                useShaders: options.useShaders !== false,
                ...options
            };

            this.meshes = [];
            this.shaderMaterial = null;
            this.uniforms = null;
            this.boundingMesh = null;

            this._initShaderMaterial();
        }

        _initShaderMaterial() {
            if (!this.options.useShaders || typeof THREE === 'undefined') {
                console.log('[HullVisualizer] Using fallback sphere rendering');
                return;
            }

            try {
                this.uniforms = {
                    uCenters: { value: new Array(this.options.maxGroups).fill(new THREE.Vector3()) },
                    uRadii: { value: new Float32Array(this.options.maxGroups) },
                    uColors: { value: new Array(this.options.maxGroups).fill(new THREE.Vector3(0.5, 0.5, 0.5)) },
                    uGroupCount: { value: 0 },
                    uBlendFactor: { value: this.options.blendFactor },
                    uOpacity: { value: this.options.opacity },
                    uCameraPos: { value: new THREE.Vector3() }
                };

                this.shaderMaterial = new THREE.ShaderMaterial({
                    vertexShader: VERTEX_SHADER,
                    fragmentShader: FRAGMENT_SHADER,
                    uniforms: this.uniforms,
                    transparent: true,
                    side: THREE.DoubleSide,
                    depthWrite: false
                });

                console.log('[HullVisualizer] SDF shader initialized');
            } catch (e) {
                console.warn('[HullVisualizer] Shader init failed, using fallback:', e.message);
                this.shaderMaterial = null;
            }
        }

        /**
         * Update visualization with new node groups
         * @param {Map|Object} nodesByFile - Map of fileIdx -> [nodes]
         * @param {Function} colorProvider - (fileIdx, total) -> color string or number
         */
        update(nodesByFile, colorProvider) {
            this.clear();

            // Convert to Map if needed
            const groups = nodesByFile instanceof Map ?
                nodesByFile :
                new Map(Object.entries(nodesByFile));

            if (groups.size === 0) return;

            const groupData = [];

            // Compute centroids and radii
            groups.forEach((nodes, fileIdx) => {
                if (!nodes || nodes.length === 0) return;

                // Compute centroid
                const centroid = { x: 0, y: 0, z: 0 };
                nodes.forEach(n => {
                    centroid.x += n.x || 0;
                    centroid.y += n.y || 0;
                    centroid.z += n.z || 0;
                });
                centroid.x /= nodes.length;
                centroid.y /= nodes.length;
                centroid.z /= nodes.length;

                // Compute radius (max distance from centroid + padding)
                let maxDist = 0;
                nodes.forEach(n => {
                    const dx = (n.x || 0) - centroid.x;
                    const dy = (n.y || 0) - centroid.y;
                    const dz = (n.z || 0) - centroid.z;
                    const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);
                    if (dist > maxDist) maxDist = dist;
                });

                const radius = Math.max(
                    this.options.minRadius,
                    maxDist * this.options.paddingFactor
                );

                // Get color
                const color = colorProvider ?
                    colorProvider(parseInt(fileIdx), groups.size) :
                    '#888888';

                groupData.push({
                    fileIdx,
                    center: new THREE.Vector3(centroid.x, centroid.y, centroid.z),
                    radius,
                    color: this._parseColor(color)
                });
            });

            // Limit to max groups
            const activeGroups = groupData.slice(0, this.options.maxGroups);

            if (this.shaderMaterial && this.uniforms) {
                this._updateShaderUniforms(activeGroups);
                this._createBoundingMesh(activeGroups);
            } else {
                this._createFallbackMeshes(activeGroups);
            }

            console.log(`[HullVisualizer] Updated ${activeGroups.length} group boundaries`);
        }

        _parseColor(color) {
            if (typeof color === 'number') {
                return new THREE.Color(color);
            }
            if (typeof color === 'string') {
                return new THREE.Color(color);
            }
            if (color instanceof THREE.Color) {
                return color;
            }
            return new THREE.Color(0x888888);
        }

        _updateShaderUniforms(groups) {
            groups.forEach((g, i) => {
                this.uniforms.uCenters.value[i] = g.center;
                this.uniforms.uRadii.value[i] = g.radius;
                this.uniforms.uColors.value[i] = new THREE.Vector3(g.color.r, g.color.g, g.color.b);
            });
            this.uniforms.uGroupCount.value = groups.length;
        }

        _createBoundingMesh(groups) {
            // Create a large bounding box that contains all groups
            let minX = Infinity, minY = Infinity, minZ = Infinity;
            let maxX = -Infinity, maxY = -Infinity, maxZ = -Infinity;

            groups.forEach(g => {
                minX = Math.min(minX, g.center.x - g.radius);
                minY = Math.min(minY, g.center.y - g.radius);
                minZ = Math.min(minZ, g.center.z - g.radius);
                maxX = Math.max(maxX, g.center.x + g.radius);
                maxY = Math.max(maxY, g.center.y + g.radius);
                maxZ = Math.max(maxZ, g.center.z + g.radius);
            });

            const width = maxX - minX + this.options.blendFactor * 2;
            const height = maxY - minY + this.options.blendFactor * 2;
            const depth = maxZ - minZ + this.options.blendFactor * 2;

            const geometry = new THREE.BoxGeometry(width, height, depth, 32, 32, 32);
            this.boundingMesh = new THREE.Mesh(geometry, this.shaderMaterial);
            this.boundingMesh.position.set(
                (minX + maxX) / 2,
                (minY + maxY) / 2,
                (minZ + maxZ) / 2
            );
            this.boundingMesh.renderOrder = -1;

            this.scene.add(this.boundingMesh);
            this.meshes.push(this.boundingMesh);
        }

        _createFallbackMeshes(groups) {
            groups.forEach(g => {
                const mesh = createFallbackMesh(g.center, g.radius, g.color, THREE);
                this.scene.add(mesh);
                this.meshes.push(mesh);
            });
        }

        /**
         * Update camera position for fresnel effect
         */
        updateCamera(cameraPosition) {
            if (this.uniforms && this.uniforms.uCameraPos) {
                this.uniforms.uCameraPos.value.copy(cameraPosition);
            }
        }

        /**
         * Set blend factor (higher = more organic blending)
         */
        setBlendFactor(factor) {
            this.options.blendFactor = factor;
            if (this.uniforms) {
                this.uniforms.uBlendFactor.value = factor;
            }
        }

        /**
         * Set opacity
         */
        setOpacity(opacity) {
            this.options.opacity = opacity;
            if (this.uniforms) {
                this.uniforms.uOpacity.value = opacity;
            }
            // Update fallback meshes
            this.meshes.forEach(m => {
                if (m.material && m.material.opacity !== undefined) {
                    m.material.opacity = opacity;
                }
            });
        }

        /**
         * Clear all rendered hulls
         */
        clear() {
            this.meshes.forEach(mesh => {
                this.scene.remove(mesh);
                if (mesh.geometry) mesh.geometry.dispose();
                if (mesh.material && mesh.material !== this.shaderMaterial) {
                    mesh.material.dispose();
                }
            });
            this.meshes = [];
            this.boundingMesh = null;
        }

        /**
         * Dispose of all resources
         */
        dispose() {
            this.clear();
            if (this.shaderMaterial) {
                this.shaderMaterial.dispose();
                this.shaderMaterial = null;
            }
        }

        /**
         * Check if a point is inside any hull
         * @returns {number|null} fileIdx if inside, null otherwise
         */
        hitTest(point) {
            if (!this.uniforms) return null;

            const count = this.uniforms.uGroupCount.value;
            for (let i = 0; i < count; i++) {
                const center = this.uniforms.uCenters.value[i];
                const radius = this.uniforms.uRadii.value[i];
                const dist = point.distanceTo(center);
                if (dist < radius) {
                    return i; // Return group index
                }
            }
            return null;
        }
    }

    // =========================================================================
    // STATIC FACTORY
    // =========================================================================

    HullVisualizer.create = function (scene, renderer, options) {
        return new HullVisualizer(scene, renderer, options);
    };

    return HullVisualizer;
})();

// Export for both browser and module contexts
if (typeof window !== 'undefined') {
    window.HullVisualizer = HullVisualizer;
}
if (typeof module !== 'undefined' && module.exports) {
    module.exports = HullVisualizer;
}
