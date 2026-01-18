# Vendored Assets

These files are local copies of CDN dependencies for air-gapped/offline environments.

## Files

| File | Version | Source |
|------|---------|--------|
| `three.min.js` | 0.149.0 | three.js core |
| `3d-force-graph.min.js` | 1.73.3 | 3D Force Graph library |
| `pako.min.js` | 2.1.0 | Compression library |

## Usage

By default, the visualization loads from CDN (unpkg.com) for simplicity.

For **air-gapped environments**, serve the generated HTML via a local HTTP server
and modify the script tags in template.html to use relative paths:

```html
<script src="vendor/three.min.js"></script>
<script src="vendor/3d-force-graph.min.js"></script>
<script src="vendor/pako.min.js"></script>
```

## Note

`ConvexGeometry.js` is not available as UMD in three.js 0.149.0.
The visualization will work without it - file boundary hulls will be disabled.
