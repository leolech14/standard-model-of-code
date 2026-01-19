import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { Hadron, PhysicsSettings, Link, Theme, ColorPalette } from '../types';
import { THEME_CONFIG } from '../data';

interface LabSceneProps {
    hadrons: Hadron[];
    links: Link[];
    settings: PhysicsSettings;
    selectedId: number | null;
    theme: Theme;
    palette: ColorPalette;
    onSelect: (id: number | null) => void;
    onKick: (id: number | null, position: THREE.Vector3) => void;
}

export const LabScene: React.FC<LabSceneProps> = ({ hadrons, links, settings, selectedId, theme, palette, onSelect, onKick }) => {
    const mountRef = useRef<HTMLDivElement>(null);
    const sceneRef = useRef<THREE.Scene | null>(null);
    const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
    const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
    const particlesRef = useRef<THREE.Group | null>(null);
    const linesRef = useRef<THREE.Group | null>(null);
    const higgsRef = useRef<THREE.Mesh | null>(null);
    const gridRef = useRef<THREE.GridHelper | null>(null);
    const controlsRef = useRef<OrbitControls | null>(null);
    const mouseRef = useRef(new THREE.Vector2());
    const raycasterRef = useRef(new THREE.Raycaster());
    const ambientLightRef = useRef<THREE.AmbientLight | null>(null);
    const dirLightRef = useRef<THREE.DirectionalLight | null>(null);
    
    // Cache geometries to reuse
    const geomsRef = useRef<Record<string, THREE.BufferGeometry> | null>(null);

    // Loop state
    const stateRef = useRef({
        hadrons,
        links,
        settings,
        selectedId,
        theme
    });

    useEffect(() => {
        stateRef.current = { hadrons, links, settings, selectedId, theme };
    }, [hadrons, links, settings, selectedId, theme]);

    const createGlowTexture = (colorHex: number) => {
        const canvas = document.createElement('canvas');
        canvas.width = 64; canvas.height = 64;
        const ctx = canvas.getContext('2d');
        if (!ctx) return new THREE.Texture();
        
        const grad = ctx.createRadialGradient(32, 32, 0, 32, 32, 32);
        const col = new THREE.Color(colorHex);
        grad.addColorStop(0, `rgba(${col.r*255}, ${col.g*255}, ${col.b*255}, 0.8)`);
        grad.addColorStop(0.4, `rgba(${col.r*255}, ${col.g*255}, ${col.b*255}, 0.2)`);
        grad.addColorStop(1, `rgba(${col.r*255}, ${col.g*255}, ${col.b*255}, 0)`);
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, 64, 64);
        return new THREE.CanvasTexture(canvas);
    };

    // 1. INITIAL SCENE SETUP (Run Once)
    useEffect(() => {
        if (!mountRef.current) return;

        const config = THEME_CONFIG[theme];

        // Init Scene
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(config.background);
        sceneRef.current = scene;

        // Init Camera
        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 2000);
        camera.position.set(0, 140, 240);
        cameraRef.current = camera;

        // Init Renderer
        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.2;
        mountRef.current.appendChild(renderer.domElement);
        rendererRef.current = renderer;

        // Controls
        const controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.maxDistance = 1000;
        controlsRef.current = controls;

        // Lighting
        const ambientLight = new THREE.AmbientLight(0xffffff, config.ambientIntensity);
        ambientLightRef.current = ambientLight;
        scene.add(ambientLight);
        
        const dirLight = new THREE.DirectionalLight(0xffffff, config.dirLightIntensity);
        dirLight.position.set(100, 300, 100);
        dirLight.castShadow = true;
        dirLight.shadow.mapSize.width = 2048;
        dirLight.shadow.mapSize.height = 2048;
        dirLight.shadow.bias = -0.0001;
        dirLightRef.current = dirLight;
        scene.add(dirLight);

        // Grid
        const gridHelper = new THREE.GridHelper(1200, 80, config.grid1, config.grid1);
        gridHelper.position.y = -20;
        gridRef.current = gridHelper;
        scene.add(gridHelper);

        // Higgs Field
        const higgsGeo = new THREE.PlaneGeometry(1200, 1200, 48, 48); 
        const higgsMat = new THREE.MeshStandardMaterial({ 
            color: config.higgsColor, 
            wireframe: true, 
            transparent: true, 
            opacity: config.higgsOpacity,
            side: THREE.DoubleSide
        });
        const higgsMesh = new THREE.Mesh(higgsGeo, higgsMat);
        higgsMesh.rotation.x = -Math.PI / 2;
        higgsMesh.position.y = -20;
        higgsMesh.receiveShadow = true;
        scene.add(higgsMesh);
        higgsRef.current = higgsMesh;

        // Groups
        const particlesGroup = new THREE.Group();
        particlesRef.current = particlesGroup;
        scene.add(particlesGroup);

        const linesGroup = new THREE.Group();
        linesRef.current = linesGroup;
        scene.add(linesGroup);

        // Init Geometries
        geomsRef.current = {
            tetrahedron: new THREE.TetrahedronGeometry(1),
            cube: new THREE.BoxGeometry(1, 1, 1),
            icosahedron: new THREE.IcosahedronGeometry(1, 0),
            cylinder: new THREE.CylinderGeometry(0.5, 0.5, 2, 16),
            cone: new THREE.ConeGeometry(0.7, 2, 16),
            torus: new THREE.TorusGeometry(0.7, 0.3, 16, 32),
            octahedron: new THREE.OctahedronGeometry(1),
            sphere: new THREE.SphereGeometry(1, 16, 16),
            dodecahedron: new THREE.DodecahedronGeometry(1)
        };

        // Initialize Lines Buffers (Max 2000 lines)
        const initLines = () => {
             const lineGeoStrong = new THREE.BufferGeometry();
             const lineGeoEM = new THREE.BufferGeometry();
             const lineGeoWeak = new THREE.BufferGeometry();
             const lineGeoGravity = new THREE.BufferGeometry();
             const lineGeoEntangle = new THREE.BufferGeometry();
     
             const maxLinks = 2000;
             const initBuffers = (geo: THREE.BufferGeometry) => {
                 geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(maxLinks * 6), 3));
                 geo.setDrawRange(0, 0);
             };
             [lineGeoStrong, lineGeoEM, lineGeoWeak, lineGeoGravity, lineGeoEntangle].forEach(initBuffers);
     
             const matStrong = new THREE.LineBasicMaterial({ color: 0xff0044, linewidth: 2, transparent: true, opacity: config.lineOpacity });
             const matEM = new THREE.LineBasicMaterial({ color: 0x0088ff, linewidth: 1, transparent: true, opacity: config.lineOpacity * 0.8 });
             const matWeak = new THREE.LineBasicMaterial({ color: 0x00ff44, linewidth: 1, transparent: true, opacity: config.lineOpacity * 0.4 });
             const matGravity = new THREE.LineBasicMaterial({ color: 0xaa00ff, linewidth: 1, transparent: true, opacity: config.lineOpacity * 0.5 });
             const matEntangle = new THREE.LineBasicMaterial({ color: 0xffd700, linewidth: 1, transparent: true, opacity: config.lineOpacity, blending: THREE.AdditiveBlending });
     
             linesGroup.add(new THREE.LineSegments(lineGeoStrong, matStrong));
             linesGroup.add(new THREE.LineSegments(lineGeoEM, matEM));
             linesGroup.add(new THREE.LineSegments(lineGeoWeak, matWeak));
             linesGroup.add(new THREE.LineSegments(lineGeoGravity, matGravity));
             linesGroup.add(new THREE.LineSegments(lineGeoEntangle, matEntangle));
        };
        initLines();

        // Helper to safely get velocity
        const getVelocity = (obj: THREE.Object3D): THREE.Vector3 | null => {
            if (obj && obj.userData && obj.userData.velocity) {
                return obj.userData.velocity as THREE.Vector3;
            }
            return null;
        };

        // Animation Loop
        let animationId: number;
        let time = 0;

        const animate = () => {
            animationId = requestAnimationFrame(animate);
            time += 0.01;
            
            const { settings, selectedId, links } = stateRef.current;
            const boundaryLimit = 450;
            
            const heavyParticles: THREE.Vector3[] = [];
            
            // Update Physics
            particlesGroup.children.forEach((child) => {
                const mesh = child as THREE.Mesh;
                const h = mesh.userData.props as Hadron;
                const v = getVelocity(mesh);
                
                if (!v) return;

                const isSelected = h.id === selectedId;

                // Physics Calculation
                if (!isSelected) {
                    // 1. STANDARD GRAVITY / LAYER PULL
                    const dy = h.targetY - mesh.position.y;
                    v.y += dy * settings.layerPull;
                    v.y -= settings.gravity * 0.1;

                    // 2. EXOTIC FORCE: DARK ENERGY (Global Expansion)
                    if (settings.darkEnergy > 0) {
                        const repulsion = mesh.position.clone().normalize().multiplyScalar(settings.darkEnergy * 0.2);
                        v.add(repulsion);
                    }

                    // 3. EXOTIC FORCE: LATTICE FIELD (Crystallization)
                    if (settings.latticeStrength > 0) {
                        const gridSize = 40;
                        const snapX = Math.round(mesh.position.x / gridSize) * gridSize;
                        const snapY = Math.round(mesh.position.y / gridSize) * gridSize;
                        const snapZ = Math.round(mesh.position.z / gridSize) * gridSize;
                        
                        const snapVec = new THREE.Vector3(snapX, snapY, snapZ).sub(mesh.position);
                        v.add(snapVec.multiplyScalar(settings.latticeStrength * 0.05));
                    }

                    // 4. EXOTIC FORCE: QUANTUM FLUX (Wave Motion)
                    if (settings.quantumFlux > 0) {
                        // Create a wave that travels along X and Z
                        const wave = Math.sin(mesh.position.x * 0.02 + mesh.position.z * 0.02 + time * 2) * settings.quantumFlux * 0.2;
                        v.y += wave;
                    }
                    
                    if (settings.higgsField) {
                         if (h.lifetime === 'Global') {
                            v.multiplyScalar(0.92); 
                            if (mesh.position.y > -5) v.y -= 0.03;
                            heavyParticles.push(mesh.position);
                         } else if (h.lifetime === 'Transient') {
                             v.multiplyScalar(0.99); 
                         } else {
                             v.multiplyScalar(0.96);
                         }
                    } else {
                        v.multiplyScalar(settings.drag);
                    }

                    v.x += (Math.random()-0.5) * settings.brownianStrength;
                    v.z += (Math.random()-0.5) * settings.brownianStrength;
                    v.y += (Math.random()-0.5) * settings.brownianStrength;
                } else {
                    v.multiplyScalar(0.8);
                }

                mesh.position.add(v);

                // Boundary Constraints
                if (mesh.position.x > boundaryLimit) { mesh.position.x = boundaryLimit; v.x *= -settings.restitution; }
                else if (mesh.position.x < -boundaryLimit) { mesh.position.x = -boundaryLimit; v.x *= -settings.restitution; }
                if (mesh.position.z > boundaryLimit) { mesh.position.z = boundaryLimit; v.z *= -settings.restitution; }
                else if (mesh.position.z < -boundaryLimit) { mesh.position.z = -boundaryLimit; v.z *= -settings.restitution; }
                
                const floorY = -18;
                if (mesh.position.y < floorY) { mesh.position.y = floorY; v.y = Math.abs(v.y) * settings.restitution; }
                if (mesh.position.y > 400) { mesh.position.y = 400; v.y *= -settings.restitution; }

                // Visual Updates
                if (h.activation === 'Direct') mesh.rotation.y += 0.03;
                else if (h.activation === 'Event') { mesh.rotation.x += 0.01; mesh.rotation.z += 0.015; }

                // SCALE EFFECT FOR QUANTUM FLUX
                if (settings.quantumFlux > 0) {
                    const waveScale = 1 + Math.sin(time * 3 + mesh.position.x * 0.05) * 0.1 * settings.quantumFlux;
                    const base = mesh.userData.baseScale || 3;
                    mesh.scale.set(base * waveScale, base * waveScale, base * waveScale);
                } else {
                    const base = mesh.userData.baseScale || 3;
                    mesh.scale.set(base, base, base);
                }

                if (h.state === 'Stateless') {
                    const alpha = Math.sin(time * 4 + mesh.userData.blinkPhase) * 0.3 + 0.7; 
                    (mesh.material as THREE.MeshStandardMaterial).opacity = alpha;
                    if (mesh.userData.halo) mesh.userData.halo.material.opacity = alpha * 0.5;
                }
            });

            // Higgs Field
            if (settings.higgsField && higgsRef.current) {
                higgsRef.current.visible = true;
                const geo = higgsRef.current.geometry;
                const pos = geo.attributes.position;
                
                for (let i = 0; i < pos.count; i++) {
                    const localX = pos.getX(i);
                    const localY = pos.getY(i);
                    let zHeight = Math.sin(localX * 0.02 + time) * 2 + Math.cos(localY * 0.02 + time * 0.8) * 2;
                    
                    if (heavyParticles.length > 0) {
                        for (let j = 0; j < heavyParticles.length; j++) {
                            const p = heavyParticles[j];
                            const dx = localX - p.x;
                            const dy = localY - p.z;
                            const distSq = dx*dx + dy*dy;
                            if (distSq < 3600) {
                                const force = (1 - distSq / 3600); 
                                zHeight -= force * 25; 
                            }
                        }
                    }
                    pos.setZ(i, zHeight);
                }
                pos.needsUpdate = true;
            } else if (higgsRef.current) {
                higgsRef.current.visible = false;
            }

            // Update Force Lines
            if (settings.showForces) {
                linesGroup.visible = true;
                const positionsStrong: number[] = [];
                const positionsEM: number[] = [];
                const positionsWeak: number[] = [];
                const positionsGravity: number[] = [];
                const positionsEntangle: number[] = [];

                const meshMap = new Map<number, THREE.Mesh>();
                particlesGroup.children.forEach(c => meshMap.set(c.userData.id, c as THREE.Mesh));

                links.forEach(l => {
                    const m1 = meshMap.get(l.source);
                    const m2 = meshMap.get(l.target);
                    if (m1 && m2) {
                        const p1 = m1.position;
                        const p2 = m2.position;
                        
                        let arr;
                        if (l.type === 'Strong') arr = positionsStrong;
                        else if (l.type === 'Electromagnetic') arr = positionsEM;
                        else if (l.type === 'Weak') arr = positionsWeak;
                        else if (l.type === 'Gravity') arr = positionsGravity;
                        else if (l.type === 'Entanglement') {
                            if (Math.sin(time * 15 + m1.id) > 0.5) arr = positionsEntangle;
                        }

                        if (arr) {
                            arr.push(p1.x, p1.y, p1.z);
                            arr.push(p2.x, p2.y, p2.z);
                        }
                    }
                });

                const updateGeo = (meshIdx: number, positions: number[]) => {
                    const lineMesh = linesGroup.children[meshIdx] as THREE.LineSegments;
                    if (!lineMesh) return;
                    const attr = lineMesh.geometry.attributes.position as THREE.BufferAttribute;
                    
                    // Safe set buffer data directly
                    const count = Math.min(positions.length, attr.array.length);
                    (attr.array as Float32Array).set(positions.slice(0, count));
                    
                    lineMesh.geometry.setDrawRange(0, count / 3);
                    attr.needsUpdate = true;
                };

                updateGeo(0, positionsStrong);
                updateGeo(1, positionsEM);
                updateGeo(2, positionsWeak);
                updateGeo(3, positionsGravity);
                updateGeo(4, positionsEntangle);

            } else {
                linesGroup.visible = false;
            }

            controls.update();
            renderer.render(scene, camera);
        };

        animate();

        // Resize
        const onResize = () => {
            if (!cameraRef.current || !rendererRef.current) return;
            cameraRef.current.aspect = window.innerWidth / window.innerHeight;
            cameraRef.current.updateProjectionMatrix();
            rendererRef.current.setSize(window.innerWidth, window.innerHeight);
        };
        window.addEventListener('resize', onResize);

        // Cleanup
        return () => {
            window.removeEventListener('resize', onResize);
            cancelAnimationFrame(animationId);
            if (mountRef.current) mountRef.current.innerHTML = '';
        };
    }, []);

    // 2. THEME UPDATES
    useEffect(() => {
        if (!sceneRef.current) return;
        const config = THEME_CONFIG[theme];
        
        sceneRef.current.background = new THREE.Color(config.background);
        if (ambientLightRef.current) ambientLightRef.current.intensity = config.ambientIntensity;
        if (dirLightRef.current) dirLightRef.current.intensity = config.dirLightIntensity;

        if (gridRef.current) {
            sceneRef.current.remove(gridRef.current);
            const gridHelper = new THREE.GridHelper(1200, 80, config.grid1, config.grid1);
            gridHelper.position.y = -20;
            gridRef.current = gridHelper;
            sceneRef.current.add(gridHelper);
        }

        if (higgsRef.current) {
             const mat = higgsRef.current.material as THREE.MeshStandardMaterial;
             mat.color.setHex(config.higgsColor);
             mat.opacity = config.higgsOpacity;
             mat.needsUpdate = true;
        }

        if (particlesRef.current) {
            particlesRef.current.children.forEach(child => {
                const mesh = child as THREE.Mesh;
                const mat = mesh.material as THREE.MeshStandardMaterial;
                mat.emissiveIntensity = config.particleEmissive;
                // Re-create halo if needed or just let it be
            });
        }
        
        if (linesRef.current) {
            linesRef.current.children.forEach(child => {
                 const line = child as THREE.LineSegments;
                 const mat = line.material as THREE.LineBasicMaterial;
                 mat.opacity = config.lineOpacity;
            });
        }
    }, [theme]);

    // 3. HADRONS UPDATE (Rebuild Particles)
    useEffect(() => {
        if (!particlesRef.current || !geomsRef.current) return;
        const config = THEME_CONFIG[theme];

        // Cleanup existing
        const group = particlesRef.current;
        while(group.children.length > 0) {
            const mesh = group.children[0] as THREE.Mesh;
            // Optional: Dispose materials if we wanted to be strict
            if (mesh.userData.halo) {
                 mesh.userData.halo.material.dispose();
            }
            if (mesh.material instanceof THREE.Material) {
                mesh.material.dispose();
            }
            group.remove(mesh);
        }

        // Build New
        hadrons.forEach((h) => {
            let scale = 3; 
            if (h.lifetime === 'Global') scale = 6.0;   
            if (h.lifetime === 'Session') scale = 3.5;  
            if (h.lifetime === 'Transient') scale = 1.8;

            const geometry = geomsRef.current![h.shape] || geomsRef.current!.cube;
            const material = new THREE.MeshStandardMaterial({ 
                color: h.color, 
                roughness: 0.2, 
                metalness: 0.1,
                emissive: h.color,
                emissiveIntensity: config.particleEmissive
            });
            
            const mesh = new THREE.Mesh(geometry, material);
            mesh.scale.set(scale, scale, scale);
            mesh.castShadow = true;
            mesh.receiveShadow = true;

            const spread = 250;
            mesh.position.set(
                (Math.random() - 0.5) * spread,
                h.targetY + (Math.random() - 0.5) * 50, 
                (Math.random() - 0.5) * spread
            );

            // Halo (Charge) - Use Palette
            if (h.boundary !== 'Internal') {
                let haloColor = 0xffffff;
                if (h.boundary === 'In') haloColor = palette.chargeIn;
                if (h.boundary === 'Out') haloColor = palette.chargeOut;
                if (h.boundary === 'In&Out') haloColor = palette.chargeMix;

                const spriteMat = new THREE.SpriteMaterial({ 
                    map: createGlowTexture(haloColor), 
                    color: haloColor, 
                    transparent: true, 
                    opacity: 0.6, 
                    blending: THREE.AdditiveBlending,
                    depthWrite: false
                });
                const sprite = new THREE.Sprite(spriteMat);
                sprite.scale.set(scale * 4, scale * 4, 1);
                mesh.add(sprite);
                mesh.userData.halo = sprite; 
            }

            mesh.userData = {
                id: h.id,
                props: h,
                velocity: new THREE.Vector3((Math.random()-0.5)*0.2, (Math.random()-0.5)*0.2, (Math.random()-0.5)*0.2),
                spinAxis: h.activation === 'Direct' ? new THREE.Vector3(0, 1, 0) : new THREE.Vector3(Math.random(), Math.random(), Math.random()).normalize(),
                blinkPhase: Math.random() * Math.PI * 2,
                baseScale: scale
            };

            group.add(mesh);
        });

    }, [hadrons, theme, palette]); // Added palette dependency

    // Interaction Handlers (Setup once, references refs)
    // ... (rest of interaction code unchanged) ...
    useEffect(() => {
        if (!rendererRef.current) return;
        const canvasEl = rendererRef.current.domElement;

        const getIntersects = (e: MouseEvent) => {
            const rect = canvasEl.getBoundingClientRect();
            mouseRef.current.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
            mouseRef.current.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
            raycasterRef.current.setFromCamera(mouseRef.current, cameraRef.current!);
            return raycasterRef.current.intersectObjects(particlesRef.current!.children);
        };

        const onClick = (e: MouseEvent) => {
            const intersects = getIntersects(e);
            if (intersects.length > 0) onSelect(intersects[0].object.userData.id);
            else onSelect(null);
        };

        const onDblClick = (e: MouseEvent) => {
            const intersects = getIntersects(e);
            if (intersects.length > 0) {
                onSelect(null);
                const hit = intersects[0].object;
                const v = hit.userData.velocity; 
                if (!v) return;

                const kickDir = new THREE.Vector3().subVectors(hit.position, cameraRef.current!.position).normalize();
                v.add(kickDir.multiplyScalar(stateRef.current.settings.kickStrength));
                
                particlesRef.current!.children.forEach((other) => {
                    if (other !== hit) {
                         const dist = other.position.distanceTo(hit.position);
                         if (dist < stateRef.current.settings.blastRadius) {
                            const away = new THREE.Vector3().subVectors(other.position, hit.position).normalize();
                            const force = (1 - dist / stateRef.current.settings.blastRadius) * 20;
                            const ov = other.userData.velocity;
                            if (ov) ov.add(away.multiplyScalar(force));
                        }
                    }
                });
            }
        };

        canvasEl.addEventListener('click', onClick);
        canvasEl.addEventListener('dblclick', onDblClick);
        
        return () => {
            canvasEl.removeEventListener('click', onClick);
            canvasEl.removeEventListener('dblclick', onDblClick);
        };
    }, []);

    return <div ref={mountRef} className={`absolute inset-0 z-0 cursor-crosshair ${theme === 'light' ? 'bg-white' : 'bg-[#050505]'}`} />;
};