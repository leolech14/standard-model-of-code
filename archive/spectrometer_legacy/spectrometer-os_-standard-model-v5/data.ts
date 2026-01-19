import { Hadron, Link, CategoryType, LayerType, ColorPalette } from './types';

// Default Palette
export const COLORS: ColorPalette = {
  data: 0x06b6d4,        // Cyan (Data Foundations)
  logic: 0xd946ef,       // Magenta (Logic & Flow)
  org: 0x22c55e,         // Green (Organization)
  exec: 0xf59e0b,        // Amber (Execution)
  chargeIn: 0x3b82f6,    // Blue Electric
  chargeOut: 0xef4444,   // Red Electric
  chargeMix: 0xa855f7,   // Purple Plasma
};

export const PALETTES: Record<string, ColorPalette = {
    'Standard': COLORS,
    'Cyberpunk': {
        data: 0x00f3ff,      // Neon Cyan
        logic: 0xff00ff,     // Neon Magenta
        org: 0xccff00,       // Neon Lime
        exec: 0xffaa00,      // Neon Orange
        chargeIn: 0x0066ff,
        chargeOut: 0xff0044,
        chargeMix: 0xaa00ff
    },
    'Monochrome': {
        data: 0xd4d4d4,
        logic: 0xa3a3a3,
        org: 0x737373,
        exec: 0x404040,
        chargeIn: 0xffffff,
        chargeOut: 0x000000,
        chargeMix: 0x888888
    },
    'Sunset': {
        data: 0x3b82f6,      // Blue
        logic: 0x8b5cf6,     // Violet
        org: 0xf43f5e,       // Rose
        exec: 0xf97316,      // Orange
        chargeIn: 0x6366f1,
        chargeOut: 0xec4899,
        chargeMix: 0xa855f7
    },
    'Forest': {
        data: 0x2dd4bf,      // Teal
        logic: 0x818cf8,     // Indigo
        org: 0x4ade80,       // Green
        exec: 0xa16207,      // Brown/Gold
        chargeIn: 0x60a5fa,
        chargeOut: 0xf87171,
        chargeMix: 0xc084fc
    }
};

export const THEME_CONFIG = {
    light: {
        background: 0xffffff,
        grid1: 0xe5e5e5,
        grid2: 0xffffff,
        ambientIntensity: 0.9,
        dirLightIntensity: 1.5,
        particleEmissive: 0.2,
        lineOpacity: 0.8,
        higgsColor: 0xe0e0e0,
        higgsOpacity: 0.15
    },
    dark: {
        background: 0x050505,
        grid1: 0x262626,
        grid2: 0x0a0a0a,
        ambientIntensity: 0.4,
        dirLightIntensity: 1.0,
        particleEmissive: 0.8, // Neon look
        lineOpacity: 0.9,
        higgsColor: 0x333333,
        higgsOpacity: 0.1
    }
};

export const PHYSICS_DEFAULTS = {
  brownianStrength: 0.04,
  drag: 0.98,
  restitution: 0.8,
  gravity: 0,
  layerPull: 0.002,
  kickStrength: 120.0,
  blastRadius: 200,
  higgsField: true,
  showForces: true,
  darkEnergy: 0,       // Default: 0
  latticeStrength: 0,  // Default: 0
  quantumFlux: 0       // Default: 0
};

export const recolorHadrons = (hadrons: Hadron[], palette: ColorPalette): Hadron[] => {
    return hadrons.map(h => {
        let color = palette.data;
        if (h.cat === 'Logic') color = palette.logic;
        if (h.cat === 'Org') color = palette.org;
        if (h.cat === 'Exec') color = palette.exec;
        return { ...h, color };
    });
};

export const generateHadrons = (code?: string, palette: ColorPalette = COLORS): Hadron[] => {
  const hadrons: Hadron[] = [];
  let idCounter = 1;
  
  // Helper to create hadron
  const create = (cat: any, sub: string, shape: string, name: string, desc: string, extraProps: Partial<Hadron> = {}) => {
      // 1. COLOR (Quarks)
      let color = palette.data;
      if (cat === 'Logic') color = palette.logic;
      if (cat === 'Org') color = palette.org;
      if (cat === 'Exec') color = palette.exec;

      // 2. CHARGE (Boundary)
      let boundary: any = 'Internal';
      const inKeywords = ['Listener', 'Consumer', 'Param', 'Import', 'Subscriber', 'Worker', 'Input', 'Req', 'Args'];
      const outKeywords = ['Service', 'Func', 'Return', 'Export', 'Publisher', 'Output', 'Emitter', 'Res', 'Result'];
      const mixKeywords = ['Handler', 'Controller', 'API', 'Repo', 'Gateway', 'Middle', 'Proxy', 'Hook'];

      if (mixKeywords.some(k => name.includes(k))) boundary = 'In&Out';
      else if (outKeywords.some(k => name.includes(k))) boundary = 'Out';
      else if (inKeywords.some(k => name.includes(k))) boundary = 'In';
      
      // 3. MASS (Lifetime)
      let lifetime: any = 'Session';
      const transientSub = ['Bit', 'Var', 'Expr', 'Primitive'];
      const globalSub = ['Aggregate', 'Module', 'Infra', 'File', 'Port', 'Class'];
      
      if (cat === 'Data' && transientSub.includes(sub)) lifetime = 'Transient';
      if (cat === 'Logic' && sub === 'Expr') lifetime = 'Transient';
      if (cat === 'Org' && globalSub.includes(sub)) lifetime = 'Global';
      if (name.includes('Singleton') || name.includes('Global') || name.includes('Container') || name.includes('Registry') || name.includes('Context') || name.includes('App')) lifetime = 'Global';

      // 4. DECAY (State)
      let state: any = 'Stateful';
      if (cat === 'Logic' || (cat === 'Exec' && !name.includes('Service') && !name.includes('Job'))) state = 'Stateless';
      if (cat === 'Data' && sub === 'Bit') state = 'Stateless';

      // 5. GENERATION (Layer)
      let layer: any = 'Core';
      let targetY = 100;
      if (cat === 'Exec') { layer = 'Interface'; targetY = 180; }
      if (cat === 'Logic') { layer = 'Application'; targetY = 120; }
      if (cat === 'Org') { layer = 'Domain'; targetY = 50; }
      if (cat === 'Data' || name.includes('Infra') || name.includes('Repo') || name.includes('File')) { layer = 'Infra'; targetY = -20; }

      // 6. SPIN (Activation)
      let activation: any = 'Direct';
      if (name.includes('Event') || name.includes('Async') || name.includes('Listener') || name.includes('Queue') || name.includes('Job') || name.includes('Promise')) activation = 'Event';
      if (lifetime === 'Global') activation = 'Time';

      // Overrides from extraProps
      if (extraProps.cat) cat = extraProps.cat;
      if (extraProps.layer) layer = extraProps.layer;
      if (extraProps.targetY) targetY = extraProps.targetY;
      
      // Recalculate color if cat changed
      if (cat === 'Logic') color = palette.logic;
      if (cat === 'Org') color = palette.org;
      if (cat === 'Exec') color = palette.exec;
      if (cat === 'Data') color = palette.data;

      hadrons.push({ id: idCounter++, cat, sub, shape, name, desc, color, boundary, lifetime, state, layer, targetY, activation, ...extraProps });
  };

  if (code && code.trim().length > 0) {
      const isMermaid = code.match(/^\s*(graph|flowchart)\s+[A-Za-z]+/);

      if (isMermaid) {
          // --- MERMAID PARSER ---
          const lines = code.split('\n');
          let currentCategory: CategoryType = 'Org';
          let currentLayer: LayerType = 'Domain';
          let currentTargetY = 50;

          // Regex patterns
          const subgraphPattern = /subgraph\s+"?([^"]+)"?/i;
          const nodePattern = /([A-Za-z0-9_]+)\s*(\[|\(|\{\{|\(\[)([^\]\)\}]+)(\]|\)|\}\}|\)\])/;
          // shape mapping: [ ]=cube, ( )=sphere, (( ))=sphere, {{ }}=icosahedron, ([ ])=torus
          
          lines.forEach(line => {
              const l = line.trim();
              if (!l || l.startsWith('%%')) return;

              // Subgraph detection (Maps to Categories/Layers)
              const sgMatch = l.match(subgraphPattern);
              if (sgMatch) {
                  const title = sgMatch[1].toLowerCase();
                  if (title.includes('domain') || title.includes('core')) { currentCategory = 'Org'; currentLayer = 'Domain'; currentTargetY = 50; }
                  else if (title.includes('application') || title.includes('logic')) { currentCategory = 'Logic'; currentLayer = 'Application'; currentTargetY = 120; }
                  else if (title.includes('infrastructure') || title.includes('data')) { currentCategory = 'Data'; currentLayer = 'Infra'; currentTargetY = -20; }
                  else if (title.includes('interface') || title.includes('api') || title.includes('presentation')) { currentCategory = 'Exec'; currentLayer = 'Interface'; currentTargetY = 180; }
                  else if (title.includes('deployment')) { currentCategory = 'Exec'; currentLayer = 'Infra'; currentTargetY = 220; }
              }

              if (l.startsWith('end')) {
                   // Reset or keep? Usually mermaid subgraphs are nested or sequential. 
              }

              // Node detection
              const nodeMatch = l.match(nodePattern);
              if (nodeMatch) {
                  const rawId = nodeMatch[1]; 
                  
                  const shapeSymbol = nodeMatch[2];
                  let shape = 'cube';
                  if (shapeSymbol.startsWith('(')) shape = 'sphere';
                  if (shapeSymbol.startsWith('{{')) shape = 'icosahedron';
                  if (shapeSymbol.startsWith('([')) shape = 'torus';
                  
                  const rawLabel = nodeMatch[3];
                  // Handle "Name<br/>Desc"
                  const parts = rawLabel.split('<br/>');
                  const name = parts[0];
                  const desc = parts.length > 1 ? parts[1] : 'Defined in diagram';

                  // Heuristics for Sub-type based on name
                  let sub = 'Component';
                  if (name.includes('Entity')) sub = 'Entity';
                  if (name.includes('Value')) sub = 'ValueObject';
                  if (name.includes('Service')) sub = 'Service';
                  if (name.includes('Repository')) sub = 'Repository';
                  if (name.includes('Event')) sub = 'Event';

                  create(currentCategory, sub, shape, name, desc, { 
                      layer: currentLayer, 
                      targetY: currentTargetY,
                  } as any);
                  
                  // Store mermaid ID on the last added hadron
                  (hadrons[hadrons.length - 1] as any)._mermaidId = rawId;
              }
          });

      } else {
          // --- TYPESCRIPT/CODE PARSER ---
          const lines = code.split('\n');
          
          lines.forEach(line => {
              const l = line.trim();
              if (!l || l.startsWith('//') || l.startsWith('/*')) return;

              // ORG: Classes, Interfaces, Imports
              if (l.match(/^import\s+/)) {
                  const parts = l.split(/\s+/);
                  const name = parts[parts.length-1].replace(/['";]/g, '');
                  create('Org', 'File', 'cube', name, `Imported module dependency: ${name}`);
              }
              else if (l.match(/^(export\s+)?(class|interface|type)\s+(\w+)/)) {
                  const match = l.match(/^(export\s+)?(class|interface|type)\s+(\w+)/);
                  if (match) {
                      const type = match[2];
                      const name = match[3];
                      if (type === 'class') create('Org', 'Aggregate', 'sphere', name, 'Class definition structure.');
                      else create('Data', 'Structure', 'dodecahedron', name, 'Type definition schema.');
                  }
              }
              // LOGIC: Functions
              else if (l.match(/^(export\s+)?(async\s+)?function\s+(\w+)/) || l.match(/^(const|let|var)\s+(\w+)\s*=\s*(\(.*\)|async)/)) {
                  let name = 'Anonymous';
                  if (l.includes('function')) {
                      const match = l.match(/function\s+(\w+)/);
                      if (match) name = match[1];
                  } else {
                      const match = l.match(/(const|let|var)\s+(\w+)/);
                      if (match) name = match[2];
                  }
                  const isAsync = l.includes('async') || l.includes('Promise');
                  create('Logic', 'Func', 'octahedron', name, isAsync ? 'Asynchronous logic routine.' : 'Synchronous logic routine.');
              }
              // DATA: Variables
              else if (l.match(/^(const|let|var)\s+(\w+)/)) {
                  const match = l.match(/^(const|let|var)\s+(\w+)/);
                  if (match) {
                      create('Data', 'Var', 'cylinder', match[2], 'Local variable memory allocation.');
                  }
              }
              // EXEC: Hooks, Effects, Console
              else if (l.includes('useEffect') || l.includes('useState') || l.includes('useMemo')) {
                  create('Exec', 'Handler', 'torus', 'ReactHook', 'Component lifecycle trigger.');
              }
              else if (l.includes('console.') || l.includes('print(')) {
                  create('Exec', 'Entry', 'cone', 'Logger', 'Output stream write.');
              }
              else if (l.includes('return')) {
                  create('Logic', 'Stmt', 'tetrahedron', 'Return', 'Flow exit control.');
              }
          });
      }

      // If code was too short or parsed nothing, sprinkle some randomness
      if (hadrons.length === 0) {
           create('Exec', 'Entry', 'icosahedron', 'Main', 'Inferred entry point.');
      }

  } else {
      // --- DEFAULT RANDOM MODE ---
      // Re-use existing random logic logic inside this block
      // 1. DATA
      create('Data', 'Bit', 'tetrahedron', 'BitFlag', 'Atomic unit of logic.');
      create('Data', 'Bit', 'tetrahedron', 'ParityBit', 'Error detection unit.');
      create('Data', 'Bit', 'tetrahedron', 'SignBit', 'Positive/Negative indicator.');
      create('Data', 'Bit', 'tetrahedron', 'OverflowBit', 'Capacity exceeded marker.');
      create('Data', 'Byte', 'cube', 'ByteArray', 'Raw memory buffer.');
      create('Data', 'Byte', 'cube', 'MagicBytes', 'File signature header.');
      create('Data', 'Byte', 'cube', 'PaddingBytes', 'Memory alignment spacer.');
      create('Data', 'Primitive', 'icosahedron', 'Boolean', 'True/False logic gate.');
      create('Data', 'Primitive', 'icosahedron', 'Integer', 'Whole number scalar.');
      create('Data', 'Primitive', 'icosahedron', 'Float', 'Floating point precision.');
      create('Data', 'Primitive', 'icosahedron', 'StringLiteral', 'Immutable text sequence.');
      create('Data', 'Primitive', 'icosahedron', 'EnumValue', 'Defined constant option.');
      create('Data', 'Var', 'cylinder', 'LocalVar', 'Stack-allocated reference.');
      create('Data', 'Var', 'cylinder', 'Parameter', 'Function input vector.');
      create('Data', 'Var', 'cylinder', 'InstanceField', 'Object property slot.');
      create('Data', 'Var', 'cylinder', 'StaticField', 'Class-level state.');
      create('Data', 'Var', 'cylinder', 'GlobalVar', 'Heap-allocated singleton.');

      // 2. LOGIC
      create('Logic', 'Expr', 'cone', 'ArithmeticExpr', 'Mathematical operation.');
      create('Logic', 'Expr', 'cone', 'CallExpr', 'Execution invocation.');
      create('Logic', 'Expr', 'cone', 'LiteralExpr', 'Fixed value declaration.');
      create('Logic', 'Stmt', 'cube', 'Assignment', 'State mutation.');
      create('Logic', 'Stmt', 'cube', 'ReturnStmt', 'Control flow exit.');
      create('Logic', 'Stmt', 'cube', 'ExpressionStmt', 'Side-effect execution.');
      create('Logic', 'Control', 'torus', 'IfBranch', 'Conditional fork.');
      create('Logic', 'Control', 'torus', 'LoopFor', 'Iterative cycle.');
      create('Logic', 'Control', 'torus', 'LoopWhile', 'Condition-bound cycle.');
      create('Logic', 'Control', 'torus', 'SwitchCase', 'Multi-branch selector.');
      create('Logic', 'Control', 'torus', 'TryCatch', 'Error boundary ring.');
      create('Logic', 'Control', 'torus', 'GuardClause', 'Early exit protection.');
      create('Logic', 'Func', 'octahedron', 'PureFunction', 'Deterministic output.');
      create('Logic', 'Func', 'octahedron', 'ImpureFunction', 'Side-effect wrapper.');
      create('Logic', 'Func', 'octahedron', 'AsyncFunction', 'Promise-returning routine.');
      create('Logic', 'Func', 'octahedron', 'Generator', 'Yielding iterator.');
      create('Logic', 'Func', 'octahedron', 'Closure', 'Scope-capturing unit.');
      create('Logic', 'Func', 'octahedron', 'CommandHandler', 'Write-model logic.');
      create('Logic', 'Func', 'octahedron', 'QueryHandler', 'Read-model logic.');
      create('Logic', 'Func', 'octahedron', 'EventHandler', 'Reactive responder.');
      create('Logic', 'Func', 'octahedron', 'SagaStep', 'Distributed transaction step.');
      create('Logic', 'Func', 'octahedron', 'Middleware', 'Pipeline interceptor.');
      create('Logic', 'Func', 'octahedron', 'Validator', 'Constraint checker.');
      create('Logic', 'Func', 'octahedron', 'Mapper', 'Data transformer.');
      create('Logic', 'Func', 'octahedron', 'Reducer', 'Accumulation logic.');

      // 3. ORG
      create('Org', 'Aggregate', 'sphere', 'ValueObject', 'Immutable attribute set.');
      create('Org', 'Aggregate', 'sphere', 'Entity', 'Identity-based object.');
      create('Org', 'Aggregate', 'sphere', 'AggregateRoot', 'Consistency boundary.');
      create('Org', 'Aggregate', 'sphere', 'ReadModel', 'Optimized query view.');
      create('Org', 'Aggregate', 'sphere', 'Projection', 'Event-driven view builder.');
      create('Org', 'Aggregate', 'sphere', 'DTO', 'Data Transfer Object.');
      create('Org', 'Aggregate', 'sphere', 'Factory', 'Object creator.');
      create('Org', 'Module', 'dodecahedron', 'BoundedContext', 'Autonomous domain boundary.');
      create('Org', 'Module', 'dodecahedron', 'FeatureModule', 'Functional vertical slice.');
      create('Org', 'Module', 'dodecahedron', 'InfraAdapter', 'Technology gateway.');
      create('Org', 'Module', 'dodecahedron', 'DomainPort', 'Interface definition.');
      create('Org', 'Module', 'dodecahedron', 'ApplicationPort', 'Use-case interface.');
      create('Org', 'File', 'cube', 'SourceFile', 'Code container.');
      create('Org', 'File', 'cube', 'ConfigFile', 'Runtime parameters.');
      create('Org', 'File', 'cube', 'MigrationFile', 'Database evolution.');
      create('Org', 'File', 'cube', 'TestFile', 'Verification suite.');

      // 4. EXEC
      create('Exec', 'Entry', 'icosahedron', 'MainEntry', 'Process start point.');
      create('Exec', 'Entry', 'icosahedron', 'CLIEntry', 'Command line interface.');
      create('Exec', 'Entry', 'icosahedron', 'LambdaEntry', 'Serverless handler.');
      create('Exec', 'Entry', 'icosahedron', 'WorkerEntry', 'Background process.');
      create('Exec', 'Handler', 'icosahedron', 'APIHandler', 'HTTP route controller.');
      create('Exec', 'Handler', 'icosahedron', 'GraphQLResolver', 'Graph query solver.');
      create('Exec', 'Handler', 'icosahedron', 'WebSocketHandler', 'Real-time channel.');
      create('Exec', 'Executables', 'icosahedron', 'ContainerEntry', 'Docker entrypoint.');
      create('Exec', 'Executables', 'icosahedron', 'KubernetesJob', 'Orchestrated task.');
      create('Exec', 'Executables', 'icosahedron', 'CronJob', 'Time-triggered task.');
      create('Exec', 'Executables', 'icosahedron', 'MessageConsumer', 'Queue listener.');
      create('Exec', 'Executables', 'icosahedron', 'QueueWorker', 'Job processor.');
      create('Exec', 'Executables', 'icosahedron', 'BackgroundThread', 'Parallel execution unit.');
      create('Exec', 'Executables', 'icosahedron', 'Actor', 'Stateful concurrent unit.');
      create('Exec', 'Executables', 'icosahedron', 'Coroutine', 'Cooperative multitasking.');
      create('Exec', 'Executables', 'icosahedron', 'Fiber', 'Lightweight thread.');
      create('Exec', 'Executables', 'icosahedron', 'WebWorker', 'Browser background thread.');
      create('Exec', 'Executables', 'icosahedron', 'ServiceWorker', 'Proxy & Cache controller.');
      create('Exec', 'Executables', 'icosahedron', 'ServerlessColdStart', 'Initialization latency.');
      create('Exec', 'Executables', 'icosahedron', 'HealthCheck', 'Status probe.');
      create('Exec', 'Executables', 'icosahedron', 'MetricsExporter', 'Telemetry emitter.');
      create('Exec', 'Executables', 'icosahedron', 'TracerProvider', 'Distributed trace context.');
      create('Exec', 'Executables', 'icosahedron', 'LoggerInit', 'Output stream setup.');
      create('Exec', 'Executables', 'icosahedron', 'ConfigLoader', 'Environment reader.');
      create('Exec', 'Executables', 'icosahedron', 'DIContainer', 'Dependency resolver.');
      create('Exec', 'Executables', 'icosahedron', 'PluginLoader', 'Dynamic extension.');
      create('Exec', 'Executables', 'icosahedron', 'MigrationRunner', 'Schema upgrade exec.');
      create('Exec', 'Executables', 'icosahedron', 'SeedData', 'Initial state population.');
      create('Exec', 'Executables', 'icosahedron', 'GracefulShutdown', 'Cleanup sequence.');
      create('Exec', 'Executables', 'icosahedron', 'PanicRecover', 'Crash safety net.');
      create('Exec', 'Executables', 'icosahedron', 'CircuitBreakerInit', 'Fault tolerance guard.');
      create('Exec', 'Executables', 'icosahedron', 'RateLimiter', 'Traffic controller.');
      create('Exec', 'Executables', 'icosahedron', 'CacheWarmer', 'Pre-emptive loader.');
      create('Exec', 'Executables', 'icosahedron', 'FeatureFlagCheck', 'Toggle evaluator.');
      create('Exec', 'Executables', 'icosahedron', 'ABTestRouter', 'Variant distributor.');
      create('Exec', 'Executables', 'icosahedron', 'CanaryDeployTrigger', 'Rollout controller.');
      create('Exec', 'Executables', 'icosahedron', 'ChaosMonkey', 'Random failure injector.');
      create('Exec', 'Executables', 'icosahedron', 'SelfHealingProbe', 'Auto-recovery unit.');
  }

  return hadrons;
};

export const generateLinks = (hadrons: Hadron[], code?: string): Link[] => {
    // ... existing link logic unchanged ...
    const links: Link[] = [];
    
    // MERMAID LINK PARSING
    if (code && code.match(/^\s*(graph|flowchart)\s+[A-Za-z]+/)) {
        const lines = code.split('\n');
        // Map mermaidId to real ID
        const idMap = new Map<string, number>();
        hadrons.forEach(h => {
            if ((h as any)._mermaidId) {
                idMap.set((h as any)._mermaidId, h.id);
            }
        });

        const linkPattern = /([A-Za-z0-9_]+)\s*(-+\>|==\>|-\.-\>)\s*([A-Za-z0-9_]+)/;
        
        lines.forEach(line => {
            const match = line.match(linkPattern);
            if (match) {
                const sourceRaw = match[1];
                const operator = match[2];
                const targetRaw = match[3];

                const sId = idMap.get(sourceRaw);
                const tId = idMap.get(targetRaw);

                if (sId && tId) {
                    let type: any = 'Weak';
                    if (operator.includes('==')) type = 'Strong';
                    if (operator.includes('.-')) type = 'Electromagnetic'; // Dotted line often events/async
                    
                    links.push({ source: sId, target: tId, type });
                }
            }
        });

        // Add some random entanglement for flavor if graph is dense
        if (links.length > 20) {
             hadrons.forEach(h => {
                 if (h.lifetime === 'Global' && Math.random() > 0.95) {
                    const target = hadrons[Math.floor(Math.random() * hadrons.length)];
                    if (target.id !== h.id) links.push({ source: h.id, target: target.id, type: 'Entanglement' });
                 }
             })
        }

        return links;
    }

    // Helper to find ID by name approx
    const findIds = (term: string) => hadrons.filter(h => h.name.includes(term)).map(h => h.id);

    // If we have very few hadrons (e.g. from code parse), just fully connect them loosely
    if (hadrons.length < 20 && hadrons.length > 1) {
        for(let i=0; i<hadrons.length; i++) {
            for(let j=i+1; j<hadrons.length; j++) {
                if (Math.random() > 0.5) {
                    const type = ['Strong', 'Electromagnetic', 'Weak', 'Gravity'][Math.floor(Math.random()*4)] as any;
                    links.push({ source: hadrons[i].id, target: hadrons[j].id, type });
                }
            }
        }
        return links;
    }

    // Default Random Logic
    // 1. STRONG FORCE (Direct Calls) - Logic <-> Exec
    // Services call Repositories
    const services = findIds('Service');
    const repos = findIds('Repo');
    services.forEach(s => {
        repos.forEach(r => {
            if (Math.random() > 0.85) links.push({ source: s, target: r, type: 'Strong' });
        });
    });

    // 2. ELECTROMAGNETIC FORCE (Events)
    // Handlers trigger Events, Listeners consume Events
    const handlers = findIds('Handler');
    const listeners = findIds('Listener');
    handlers.forEach(h => {
        listeners.forEach(l => {
            if (Math.random() > 0.9) links.push({ source: h, target: l, type: 'Electromagnetic' });
        });
    });

    // 3. WEAK FORCE (Dependency Injection / Config)
    // Config/DI connected to randomly scattered components
    const configs = [...findIds('Config'), ...findIds('DI')];
    const targets = [...findIds('Service'), ...findIds('Controller')];
    configs.forEach(c => {
        targets.forEach(t => {
            if (Math.random() > 0.9) links.push({ source: c, target: t, type: 'Weak' });
        });
    });

    // 4. GRAVITY (Inheritance / Global coupling)
    // Heavy objects (Modules/Aggregates) attract smaller related ones
    const modules = findIds('Module');
    const domainEntities = findIds('Entity');
    modules.forEach(m => {
        domainEntities.forEach(e => {
            if (Math.random() > 0.7) links.push({ source: m, target: e, type: 'Gravity' });
        });
    });
    
    // 5. QUANTUM ENTANGLEMENT (Shared State without direct link)
    // Singletons or GlobalVars entangled with users
    const globals = findIds('Global');
    const consumers = findIds('Worker');
    globals.forEach(g => {
        consumers.forEach(c => {
            if (Math.random() > 0.9) links.push({ source: g, target: c, type: 'Entanglement' });
        });
    });

    // Fallback: If no links generated (sparse custom code), link random things in same category
    if (links.length === 0 && hadrons.length > 5) {
        hadrons.forEach((h, i) => {
            if (i < hadrons.length - 1 && h.cat === hadrons[i+1].cat && Math.random() > 0.5) {
                links.push({ source: h.id, target: hadrons[i+1].id, type: 'Weak' });
            }
        });
    }

    return links;
};