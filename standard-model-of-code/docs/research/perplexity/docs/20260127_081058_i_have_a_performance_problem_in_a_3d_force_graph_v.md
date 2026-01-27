# Research: I have a performance problem in a 3d-force-graph visualization:

- 3248 nodes, 9493 edges
- Running ...

> **Date:** 2026-01-27 08:10:58
> **Source:** perplexity-mcp
> **Model:** sonar-pro
> **Checksum:** `sha256:9cfdbf82c099457f8b173600fcb7e32c4d23152c5fcd5ab9d345b2221ff1da56`
> **Raw JSON:** `raw/20260127_081058_i_have_a_performance_problem_in_a_3d_force_graph_v.json`

---

## Query

I have a performance problem in a 3d-force-graph visualization:

- 3248 nodes, 9493 edges
- Running at 12-20 FPS (should be 60 FPS)
- Multiple requestAnimationFrame loops running concurrently
- One loop calls Graph.refresh() indirectly via REFRESH.throttled() every frame
- Another loop updates node colors via Graph.nodeColor() accessor
- Material.transparent is set to true on 3500+ Three.js meshes

What are the proven fixes for:
1. Preventing multiple RAF loops from stacking?
2. Efficient material opacity updates without traverse() every frame?
3. Should materials ALWAYS have transparent:true or only when opacity < 1?
4. How to batch Graph accessor updates (nodeColor, nodeVal, linkOpacity)?
5. Is there a better pattern than calling REFRESH every frame?

Looking for WebGL/Three.js best practices, ideally from production graph visualization libraries.

---

## Response

**Use `pauseAnimation()` and `resumeAnimation()` from 3d-force-graph to consolidate RAF loops into a single render cycle, eliminating concurrent loops.** This freezes the simulation when static views suffice and resumes only when needed, directly addressing stacked RAF calls including `Graph.refresh()` and node color updates.[1][4]

**For efficient material opacity updates, avoid `traverse()` every frame; instead, use instanced rendering or uniform buffers in Three.js, and batch accessor changes like `nodeColor()`, `nodeVal()`, and `linkOpacity()` via a single throttled update before `refresh()`.** Custom shaders with uniforms for opacity/color avoid per-mesh updates on 3500+ transparent meshes, while 3d-force-graph accessors should be set once per tick rather than per-frame to minimize rebuilds.[1][6]

**Set `material.transparent = true` only when opacity < 1; otherwise, use `opacity = 1` without transparency to skip expensive alpha blending.** Transparency enables sorting/blending but incurs high GPU cost—reserve it for semi-transparent nodes/links only.[5][6]

**Batch graph accessor updates by queuing changes in simulation callbacks like `onEngineTick()` and applying them throttled (e.g., every 100-500ms) via a single `Graph.nodeColor(fn)` or `refresh()` call, avoiding per-frame refreshes.** Replace constant `REFRESH.throttled()` with cooldown-based ticks using `cooldownTime()` or `d3ReheatSimulation()` for physics-driven updates only when layout changes.[1]

**Core WebGL/Three.js best practices from graph viz libraries:**
- **LOD (Level of Detail):** Simplify distant nodes/links (e.g., lower `linkResolution`, point sprites vs. meshes).[2]
- **Disable interactions:** Set `enablePointerInteraction(false)` for max perf on large graphs (3248 nodes).[1]
- **Physics tuning:** Increase `d3VelocityDecay` (e.g., 0.6+), use `ngraphPhysics` for faster sims, or `pauseAnimation()` post-cooldown.[1]
- **Instancing:** Migrate to `InstancedMesh` for nodes/links to handle 10k+ edges at 60 FPS without per-object draw calls.[6]
- **No per-frame refreshes:** Use `onEngineStop` callback for final layout freeze, avoiding constant RAF overload.[1]

---

## Citations

1. https://github.com/vasturiano/3d-force-graph
2. https://blog.tomsawyer.com/advanced-techniques-in-threejs-graph-visualization
3. https://forum.babylonjs.com/t/force-directed-graph-for-large-particle-simulation/18892
4. https://vasturiano.github.io/3d-force-graph/
5. https://discourse.threejs.org/t/how-to-optimize-performance-in-threejs/42769
6. https://dev.to/didof/optimizing-threejs-4-key-techniques-4lad
7. https://discourse.threejs.org/t/want-to-increase-my-page-speed-by-optimizing-three-js-code/86976

---

## Usage Stats

- Prompt tokens: 188
- Completion tokens: 503
- Total tokens: 691
