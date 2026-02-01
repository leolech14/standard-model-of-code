# Research: I'm building a 3D code visualization using Three.js and 3d-force-graph library. I need to implement ...

> **Date:** 2026-01-27 06:19:16
> **Source:** perplexity-mcp
> **Model:** sonar-pro
> **Checksum:** `sha256:9a7b111129140a91d83e482d4d7e4b2ccb95c66d246c8b77c13ef89946ec8b92`
> **Raw JSON:** `raw/20260127_061916_i_m_building_a_3d_code_visualization_using_three_j.json`

---

## Query

I'm building a 3D code visualization using Three.js and 3d-force-graph library. I need to implement a smooth animated transition between two visualization modes in ONE unified graph:

Mode A (Atoms): Shows ~3000 nodes (functions, classes) with call/import edges
Mode B (Files): Shows ~266 file nodes connected to folder nodes

The atoms LIVE INSIDE files. I want:
1. File nodes always visible as container/parent nodes
2. Atom nodes fade in/out with opacity animation
3. When atoms fade out, file-to-file edges appear (cross-file dependencies)
4. Force layout should handle both layers (files as clusters, atoms inside)
5. Smooth 500-1000ms transition with easing

What are the best techniques for:
- Animated node opacity in 3d-force-graph?
- Maintaining force layout stability during transitions?
- Hierarchical/nested force layouts (atoms clustered inside file nodes)?
- Edge opacity animation synchronized with node transitions?

Specifically for the 3d-force-graph library (https://github.com/vasturiano/3d-force-graph), what APIs support this? nodeOpacity? nodeVisibility? Custom Three.js materials?

---

## Response

To implement smooth animated transitions between Mode A (atoms) and Mode B (files) in a unified 3d-force-graph, use the library's built-in opacity APIs combined with timed updates to `nodeVisibility`, `nodeOpacity`, and `linkOpacity`. Maintain layout stability via force simulation controls and hierarchical positioning.[1][2]

### Animated Node Opacity
Set `nodeOpacity(val)` (0-1 range) for global atom node fading, or use per-node opacity via `nodeThreeObject(fn)` returning custom Three.js materials (e.g., `MeshBasicMaterial` with animated `transparent: true` and `opacity` tweened via `TWEEN.js` or `gsap`). For Mode A→B:
```javascript
// Fade atoms out
graph.nodeOpacity(0); // Global fade (500ms internal refresh)
```
Synchronize with `requestAnimationFrame` loop for 500-1000ms easing (use `d3.easeCubicOut`). Custom materials enable individual atom opacity tied to `node.isAtom` flag.[1][2]

### Force Layout Stability During Transitions
Pause/reduce simulation velocity with `d3VelocityDecay(0.9)` (high decay stabilizes) and `d3AlphaTarget(0)` to halt cooling, preventing jitter. Pre-position atoms inside file clusters before visibility toggle:
```javascript
graph.d3VelocityDecay(0.85); // Stabilize
graph.d3AlphaTarget(0.01);   // Slow decay
```
After transition, reset `d3AlphaTarget(0)` and `d3VelocityDecay(0.6)` for resumed clustering. Use `nodePositionUpdate(fn)` to enforce atom positions relative to parent files during sim.[1][2]

### Hierarchical/Nested Force Layouts (Atoms in Files)
- **Position atoms inside files**: On init, set atom `x/y/z` offsets relative to parent file (e.g., `atom.x = file.x + random(-r, r)` where `r` is file radius). Use `nodeVal(fn)` to size files larger (`val: file.atomCount * scale`).[1]
- **Clustering forces**: Enable `dagMode: 'radial'` or custom forces via `forceEngine` (d3 sim), adding `collide` force to keep atoms within file bounds. Treat files as fixed "super-nodes" with higher `nodeVal` for repulsion dominance.[2][6]
- **Always-visible files**: Set `graph.nodeVisibility(node => !node.isAtom || mode === 'B')` so files persist.[1]

### Edge Opacity Animation (Synchronized)
Animate `linkOpacity(0→1)` for file-file edges as atoms fade:
```javascript
const duration = 750;
const start = Date.now();
function animate() {
  const progress = Math.min(1, (Date.now() - start) / duration);
  const eased = d3.easeCubicOut(progress); // Easing
  graph.nodeOpacity(1 - eased);     // Atoms out
  graph.linkOpacity(eased * 0.8);   // File edges in (filter via link.isFileEdge)
  if (progress < 1) requestAnimationFrame(animate);
}
```
Filter edges with `linkVisibility(fn)` (e.g., `link => link.isFileEdge || mode === 'A'`). Sync via shared `progress` value.[1][2]

### Complete Transition Function
```javascript
async function transitionToMode(newMode) {
  graph.pauseAnimation(); // Freeze sim
  await new Promise(resolve => {
    const start = Date.now();
    const animate = () => {
      const t = Math.min(1, (Date.now() - start) / 800);
      const opacity = 1 - d3.easeCubicInOut(t);
      graph.nodeOpacity(newMode === 'atoms' ? opacity : 1 - opacity);
      graph.linkOpacity(newMode === 'files' ? t * 0.3 : 1 - t);
      if (t < 1) requestAnimationFrame(animate);
      else resolve();
    };
    animate();
  });
  graph.nodeVisibility(node => 
    newMode === 'atoms' || node.isFile // Toggle atoms
  );
  graph.resumeAnimation();
  graph.zoomToFit(400); // Refit view
}
```
**Tips**: Precompute hierarchies (`node.parentFileId`). For perf with 3000+ atoms, use `nodeResolution(6)` and LOD (custom `nodeThreeObject` with instanced meshes). Test on demo at vasturiano.github.io/3d-force-graph.[1][4]

---

## Citations

1. https://github.com/vasturiano/3d-force-graph
2. https://github.com/vasturiano/three-forcegraph
3. https://www.youtube.com/watch?v=cJ6NdluzEG8
4. https://vasturiano.github.io/3d-force-graph/
5. https://dev.to/gilfink/creating-a-force-graph-using-react-d3-and-pixijs-182n
6. https://d3js.org/d3-force/simulation
7. https://g6.antv.antgroup.com/en/manual/layout/d3-force-layout
8. https://www.youtube.com/watch?v=QGJbJAopX-s

---

## Usage Stats

- Prompt tokens: 242
- Completion tokens: 963
- Total tokens: 1205
