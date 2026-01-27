# Modular Architecture Synthesis: Seamless Plug-and-Play System

> **Purpose:** Architecture blueprint for truly modular, AI-integrable system
> **Research:** 5 Perplexity deep-research queries (2026-01-27)
> **Goal:** Anyone can airdrop hub + modules into any project

---

## Executive Summary

| Component | Solution |
|-----------|----------|
| **Central Hub** | Minimal registry + event bus (<500 lines) |
| **Module Contract** | `plugin.json` manifest + lifecycle hooks |
| **AI Integration** | MCP (Model Context Protocol) servers |
| **Data Schemas** | JSON Schema + TypeScript types |
| **Distribution** | Multi-channel (copy, npm, git, URL) |
| **Architecture** | Hexagonal (ports and adapters) |

---

## 1. The Minimal Hub (~300 lines)

### Core Components

```
┌─────────────────────────────────────────────┐
│                    HUB                       │
├─────────────────────────────────────────────┤
│  Registry      │ Module registration        │
│  DI Container  │ Dependency injection       │
│  Event Bus     │ Cross-module communication │
│  Loader        │ Lazy module loading        │
│  Circuit Breaker│ Failure isolation         │
└─────────────────────────────────────────────┘
```

### JavaScript Implementation

```javascript
// hub.js (~150 lines)
class ElementsHub {
  constructor() {
    this.modules = new Map();      // name → config
    this.instances = new Map();    // name → instance (singletons)
    this.events = new Map();       // event → handlers[]
  }

  // Registration
  register(name, factory, options = {}) {
    this.modules.set(name, { factory, ...options });
  }

  // Dependency Resolution
  get(name) {
    const config = this.modules.get(name);
    if (!config) throw new Error(`Module "${name}" not registered`);

    if (config.singleton && this.instances.has(name)) {
      return this.instances.get(name);
    }

    const deps = (config.dependencies || []).map(d => this.get(d));
    const instance = config.factory(this, ...deps);

    if (config.singleton) this.instances.set(name, instance);
    return instance;
  }

  // Event Bus
  on(event, handler) {
    if (!this.events.has(event)) this.events.set(event, []);
    this.events.get(event).push(handler);
  }

  emit(event, data) {
    (this.events.get(event) || []).forEach(h => h(data));
  }

  // Interface Registration
  registerInterface(name, implementation) {
    this.modules.set(`interface:${name}`, {
      factory: () => implementation,
      singleton: true
    });
  }

  getInterface(name) {
    return this.get(`interface:${name}`);
  }
}

// Global singleton
window.ELEMENTS_HUB = new ElementsHub();
```

### Python Implementation

```python
# hub.py (~150 lines)
class ElementsHub:
    def __init__(self):
        self.modules = {}      # name → config
        self.instances = {}    # name → instance
        self.events = {}       # event → handlers[]

    def register(self, name, factory, **options):
        self.modules[name] = {'factory': factory, **options}

    def get(self, name):
        config = self.modules.get(name)
        if not config:
            raise ValueError(f'Module "{name}" not registered')

        if config.get('singleton') and name in self.instances:
            return self.instances[name]

        deps = [self.get(d) for d in config.get('dependencies', [])]
        instance = config['factory'](self, *deps)

        if config.get('singleton'):
            self.instances[name] = instance
        return instance

    def on(self, event, handler):
        if event not in self.events:
            self.events[event] = []
        self.events[event].append(handler)

    def emit(self, event, data=None):
        for handler in self.events.get(event, []):
            handler(data)

    def register_interface(self, name, implementation):
        self.modules[f'interface:{name}'] = {
            'factory': lambda _: implementation,
            'singleton': True
        }

    def get_interface(self, name):
        return self.get(f'interface:{name}')

# Global singleton
ELEMENTS_HUB = ElementsHub()
```

---

## 2. Module Contract (plugin.json)

Every module MUST have a `plugin.json` manifest:

```json
{
  "$schema": "https://elements.dev/schemas/plugin-v1.json",
  "id": "color-engine",
  "name": "OKLCH Color Engine",
  "version": "1.2.0",
  "description": "Perceptually uniform color system for visualization",

  "author": "Elements Team",
  "license": "MIT",

  "engine": "^1.0.0",
  "dependencies": {},

  "interfaces": ["color-provider", "theme-manager"],

  "entrypoint": {
    "javascript": "src/color-engine.js",
    "python": "src/color_engine.py"
  },

  "exports": {
    "COLOR": "Global color API object",
    "getColor": "Get color by dimension and category",
    "interpolate": "Interpolate between colors"
  },

  "events": {
    "emits": ["color:transform-changed", "color:scheme-changed"],
    "listens": ["theme:changed", "accessibility:mode-changed"]
  },

  "config": {
    "schema": "config.schema.json",
    "defaults": {
      "hueShift": 0,
      "chromaScale": 1.0
    }
  },

  "ai": {
    "description": "Use when you need colors for visualization elements",
    "examples": [
      "COLOR.get('tier', 'T0') → hex color for tier T0",
      "COLOR.getInterval('confidence', 0.8) → color at 80% confidence"
    ],
    "whenToUse": [
      "Assigning colors to graph nodes",
      "Creating color gradients",
      "Theming UI components"
    ]
  }
}
```

---

## 3. Module Lifecycle

Every module implements 4 lifecycle methods:

```javascript
class MyModule {
  // 1. INITIALIZE - Receive hub reference
  initialize(hub) {
    this.hub = hub;
    this.config = hub.getConfig('my-module');
  }

  // 2. REGISTER - Declare capabilities
  register() {
    this.hub.registerInterface('my-interface', this);
    this.hub.on('some:event', this.handleEvent.bind(this));
  }

  // 3. START - Begin operation
  start() {
    console.log('MyModule started');
  }

  // 4. STOP - Cleanup
  stop() {
    console.log('MyModule stopping');
  }
}
```

---

## 4. AI Integration (MCP Protocol)

For AI agents to auto-integrate modules, expose via MCP:

### MCP Server per Module

```javascript
// mcp-server.js
const server = new MCPServer({
  name: 'elements-color',
  version: '1.0.0',

  tools: [{
    name: 'get_color',
    description: 'Get a color for a visualization element',
    parameters: {
      dimension: { type: 'string', enum: ['tier', 'family', 'ring'] },
      category: { type: 'string' }
    },
    handler: async ({ dimension, category }) => {
      return COLOR.get(dimension, category);
    }
  }],

  resources: [{
    uri: 'elements://color/schemes',
    name: 'Available color schemes',
    handler: async () => COLOR.listSchemes()
  }]
});
```

### AI-Friendly Documentation (AGENTS.md)

```markdown
# Color Engine - AI Integration Guide

## When to Use This Module
- Assigning colors to graph nodes based on semantic categories
- Creating gradients for numeric data visualization
- Ensuring accessible color contrast

## Quick Start
```javascript
const color = COLOR.get('tier', 'T0');  // Returns hex like '#A1B2C3'
```

## Common Patterns

### Pattern 1: Node Coloring
```javascript
nodes.forEach(node => {
  node.color = COLOR.get('tier', node.tier);
});
```

### Pattern 2: Gradient Mapping
```javascript
const normalizedValue = value / maxValue;
const color = COLOR.getInterval('confidence', normalizedValue);
```

## Error Recovery
- "Unknown dimension" → Check COLOR.getDimensions() for valid options
- "Unknown category" → Check COLOR.getCategories(dimension)
```

---

## 5. Distribution Channels

Support ALL channels for maximum reach:

| Channel | Files | Use Case |
|---------|-------|----------|
| **Copy/Paste** | `dist/bundle.js` | Quick integration |
| **npm** | `npm install @elements/color` | Node.js projects |
| **CDN** | `https://cdn.elements.dev/color/1.2.0/bundle.js` | Browser |
| **Git Submodule** | `git submodule add ...` | Version control |
| **Python** | `pip install elements-color` | Python projects |

### Self-Contained Bundle

```bash
# Generate self-contained bundle
esbuild src/index.js --bundle --outfile=dist/bundle.js --format=iife --global-name=COLOR
```

### Package Structure

```
color-engine/
├── plugin.json           # Manifest (required)
├── AGENTS.md             # AI integration guide
├── README.md             # Human docs
├── dist/
│   ├── bundle.js         # Browser bundle (copy-paste ready)
│   ├── bundle.min.js     # Minified
│   └── index.d.ts        # TypeScript types
├── src/
│   ├── index.js          # Entry point
│   └── color-engine.js   # Implementation
├── config.schema.json    # Config validation schema
└── package.json          # npm package
```

---

## 6. Hexagonal Architecture (Ports & Adapters)

Keep business logic isolated from integration details:

```
                    ┌─────────────────────┐
                    │                     │
    ┌───────────────┤   BUSINESS LOGIC    ├───────────────┐
    │               │   (Pure functions)  │               │
    │               └─────────────────────┘               │
    │                         │                           │
    ▼                         ▼                           ▼
┌─────────┐           ┌─────────────┐           ┌─────────────┐
│ REST    │           │   EVENT     │           │   CLI       │
│ Adapter │           │   Adapter   │           │   Adapter   │
└─────────┘           └─────────────┘           └─────────────┘
    │                         │                           │
    ▼                         ▼                           ▼
 HTTP API              Message Queue              Terminal
```

### Port Definition (Interface)

```typescript
// ports/color-provider.ts
interface ColorProvider {
  get(dimension: string, category: string): string;
  getInterval(name: string, value: number): string;
  listDimensions(): string[];
  listCategories(dimension: string): string[];
}
```

### Adapter Implementation

```typescript
// adapters/rest-adapter.ts
class RestColorAdapter {
  constructor(private colorProvider: ColorProvider) {}

  async handleRequest(req, res) {
    const { dimension, category } = req.params;
    const color = this.colorProvider.get(dimension, category);
    res.json({ color });
  }
}
```

---

## 7. Schema Validation

Use JSON Schema for all data contracts:

### Config Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "hueShift": {
      "type": "number",
      "minimum": -180,
      "maximum": 180,
      "default": 0,
      "description": "Rotate all hues by this amount (degrees)"
    },
    "chromaScale": {
      "type": "number",
      "minimum": 0,
      "maximum": 2,
      "default": 1.0,
      "description": "Scale all chroma values"
    }
  }
}
```

### Event Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "color:transform-changed",
  "type": "object",
  "properties": {
    "transform": {
      "type": "object",
      "properties": {
        "hueShift": { "type": "number" },
        "chromaScale": { "type": "number" },
        "lightnessShift": { "type": "number" }
      }
    },
    "source": { "type": "string" }
  },
  "required": ["transform"]
}
```

---

## 8. Versioning Strategy

### Semantic Versioning

```
MAJOR.MINOR.PATCH
  │     │     └── Bug fixes (safe to upgrade)
  │     └──────── New features (safe to upgrade)
  └────────────── Breaking changes (review required)
```

### Additive-Only Changes

```javascript
// v1.0.0
{ tier: 'T0', color: '#abc123' }

// v1.1.0 - SAFE (added field)
{ tier: 'T0', color: '#abc123', label: 'Foundation' }

// v2.0.0 - BREAKING (removed field)
{ tier: 'T0', label: 'Foundation' }  // color removed!
```

### Deprecation Process

1. Mark deprecated in docs and code comments
2. Log deprecation warning when used
3. Keep working for 2 minor versions
4. Remove in next major version

---

## 9. Integration Checklist

When integrating a module:

- [ ] Copy `plugin.json` to understand the module
- [ ] Check `dependencies` - are they available?
- [ ] Check `engine` version compatibility
- [ ] Load entrypoint (JS or Python)
- [ ] Call `initialize(hub)` with hub reference
- [ ] Call `register()` to wire up interfaces
- [ ] Call `start()` to begin operation
- [ ] Subscribe to emitted events if needed

### AI Agent Auto-Integration

```javascript
async function autoIntegrateModule(modulePath) {
  // 1. Read manifest
  const manifest = JSON.parse(fs.readFileSync(`${modulePath}/plugin.json`));

  // 2. Check compatibility
  if (!semver.satisfies(HUB_VERSION, manifest.engine)) {
    throw new Error(`Incompatible engine: requires ${manifest.engine}`);
  }

  // 3. Check dependencies
  for (const [dep, version] of Object.entries(manifest.dependencies)) {
    if (!hub.has(dep)) {
      await autoIntegrateModule(findModule(dep));
    }
  }

  // 4. Load module
  const Module = require(`${modulePath}/${manifest.entrypoint.javascript}`);
  const instance = new Module();

  // 5. Lifecycle
  instance.initialize(hub);
  instance.register();
  instance.start();

  // 6. Register
  hub.register(manifest.id, () => instance, { singleton: true });

  return instance;
}
```

---

## 10. File Structure (Final)

```
elements-hub/
├── hub.js                    # JavaScript hub (~150 lines)
├── hub.py                    # Python hub (~150 lines)
├── plugin.schema.json        # Manifest schema
└── README.md

elements-modules/
├── color-engine/
│   ├── plugin.json
│   ├── AGENTS.md
│   ├── src/
│   └── dist/
├── event-bus/
│   ├── plugin.json
│   └── src/
├── graph-metrics/
│   ├── plugin.json
│   └── src/
└── ...
```

---

## Summary: What to Build

| Priority | Component | Effort |
|----------|-----------|--------|
| P0 | `hub.js` / `hub.py` | 2 hours |
| P0 | `plugin.schema.json` | 1 hour |
| P0 | Convert color-engine to plugin format | 2 hours |
| P1 | Add plugin.json to all 6 portable modules | 3 hours |
| P1 | Create AGENTS.md for AI integration | 2 hours |
| P2 | MCP server wrapper | 4 hours |
| P2 | Bundle generation scripts | 2 hours |

**Total: ~16 hours to full plug-and-play system**

---

## Research Sources

1. Plugin Architecture Patterns (VSCode, WordPress, Backstage)
2. AI-Agent-Friendly Module Design (MCP Protocol)
3. Central Hub / Service Locator Patterns
4. Zero-Friction Distribution Strategies
5. Interface Contracts and Schema-Driven Integration

Full research: `docs/research/perplexity/docs/20260127_*`
