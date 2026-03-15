/**
 * AppSpec — Code-to-Spec Ingestion Format
 *
 * Mirrors the Semantic Node Architecture's philosophy:
 *   Sense (IN) → Interpret (transform) → Represent (OUT)
 * but applied to entire code artifacts rather than live data nodes.
 *
 * An AppSpec is what a code-to-spec analyzer produces after
 * reverse-engineering an incoming application. It answers:
 *   - What IS this? (meta, architecture)
 *   - What does it CONSUME? (sense)
 *   - How does it TRANSFORM data? (interpret)
 *   - What does it RENDER? (represent)
 *   - What can Refinery DO with it? (exposable)
 *   - What should we WORRY about? (risks)
 */

/* ─── Meta ─── */

export interface AppSpecMeta {
  id: string;
  name: string;
  description: string;
  origin: 'zip-upload' | 'git-clone' | 'npm-registry' | 'manual';
  originRef: string;
  ingestedAt: number;
  sizeBytes: number;
  fileCount: number;
  stack: StackSignature;
  status: 'pending' | 'analyzing' | 'ready' | 'failed';
}

export interface StackSignature {
  framework: string;
  bundler: string;
  language: string;
  styling: string;
  target: 'browser' | 'node' | 'edge' | 'hybrid';
}

/* ─── Architecture ─── */

export interface AppArchitecture {
  pattern: string;
  entryPoint: string;
  stateManagement: StateManagement;
  componentTree: ComponentNode[];
  dataFlow: 'unidirectional' | 'bidirectional' | 'event-driven' | 'mixed';
  directories: DirectoryRole[];
}

export interface StateManagement {
  pattern: string;
  persisted: boolean;
  persistenceLayer?: string;
}

export interface ComponentNode {
  name: string;
  path: string;
  loc: number;
  props: Record<string, string>;
  children: string[];
  role: string;
  complexity: 'leaf' | 'branch' | 'root';
}

export interface DirectoryRole {
  path: string;
  role: string;
  fileCount: number;
}

/* ─── Sense (IN) ─── */

export interface AppSense {
  apis: ApiConsumption[];
  browserApis: BrowserApiUsage[];
  lifecycle: 'polling' | 'event-driven' | 'raf' | 'manual' | 'static' | 'mixed';
  localSources: LocalSource[];
}

export interface ApiConsumption {
  endpoint: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  returns: string;
  usedBy: string[];
}

export interface BrowserApiUsage {
  api: string;
  purpose: string;
  complexity: 'basic' | 'advanced';
}

export interface LocalSource {
  type: string;
  key: string;
  holds: string;
}

/* ─── Interpret ─── */

export interface AppInterpret {
  typeSystem: TypeDef[];
  transforms: DataTransform[];
  algorithms: Algorithm[];
}

export interface TypeDef {
  name: string;
  file: string;
  fieldCount: number;
  purpose: string;
}

export interface DataTransform {
  name: string;
  input: string;
  output: string;
  location: string;
}

export interface Algorithm {
  name: string;
  description: string;
  complexity: 'trivial' | 'linear' | 'nontrivial';
  location: string;
}

/* ─── Represent ─── */

export interface AppRepresent {
  layoutSystem: string;
  layoutConfigurable: boolean;
  views: AppView[];
  theming: ThemingInfo;
  iconLibrary?: string;
}

export interface AppView {
  name: string;
  renders: string;
  renderTech: 'dom' | 'canvas-2d' | 'webgl' | 'svg' | 'three.js';
  realtime: boolean;
  component: string;
}

export interface ThemingInfo {
  approach: string;
  themeCount: number;
  colorModel: string;
}

/* ─── Dependencies ─── */

export interface AppDependencies {
  runtime: Dependency[];
  dev: Dependency[];
}

export interface Dependency {
  name: string;
  version: string;
  purpose: string;
  weight: 'light' | 'medium' | 'heavy';
}

/* ─── Exposable ─── */

export interface ExposableNode {
  suggestedId: string;
  title: string;
  nodeKind: 'metric' | 'status' | 'list' | 'feed' | 'table' | 'control' | 'composite';
  senseStrategy: string;
  viewKind: string;
  confidence: number;
}

/* ─── Risks ─── */

export interface AppRisk {
  category: 'security' | 'compatibility' | 'performance' | 'maintenance' | 'missing';
  severity: 'critical' | 'warning' | 'info';
  message: string;
  location?: string;
}

/* ─── Complete Spec ─── */

export interface AppSpec {
  specVersion: '1.0';
  meta: AppSpecMeta;
  architecture: AppArchitecture;
  sense: AppSense;
  interpret: AppInterpret;
  represent: AppRepresent;
  dependencies: AppDependencies;
  exposable: ExposableNode[];
  risks: AppRisk[];
}
