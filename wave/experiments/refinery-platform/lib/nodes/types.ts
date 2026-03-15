/**
 * Semantic Node Architecture — Type Definitions
 *
 * Every visual unit in the platform is a NodeDefinition.
 * Nodes are sensory-motor units: sense (IN) = data polling,
 * mutations (OUT) = user-triggered actions.
 *
 * Pages compose nodes; the rendering bridge (NodeRenderer)
 * translates semantic definitions into React components.
 */

/* ─── Enums ─── */

export type DataSource = 'openclaw' | 'local';

export type NodeKind =
  | 'metric'      // single numeric/string value
  | 'status'      // health/alive indicator
  | 'list'        // array of items
  | 'feed'        // chronological stream
  | 'table'       // structured rows with columns
  | 'control'     // toggle/switch
  | 'composite';  // groups sub-nodes

export type ViewKind =
  | 'gauge'        // SVG arc (Gauge component)
  | 'stat'         // label + value card
  | 'status-pill'  // Badge + text
  | 'table'        // table with columns
  | 'feed'         // chronological list
  | 'panel'        // collapsible section
  | 'toggle'       // Toggle component
  | 'json'         // fallback raw display
  | 'composite'    // recursive child-node layout
  | 'custom';      // escape hatch

/* ─── Sense (IN) ─── */

export interface SenseDefinition {
  source: DataSource;
  /** API path segment, e.g. 'health', 'system/current' */
  endpoint: string;
  /** Polling interval in milliseconds */
  intervalMs: number;
  /** Dot-notation path to extract sub-field from response, e.g. 'cpu' */
  fieldPath?: string;
  queryParams?: Record<string, string>;
  /** Filter parameters the page should render as Select controls for this node */
  filterParams?: MutationParameter[];
  description?: string;
}

/* ─── Interpret ─── */

export interface ThresholdRule {
  warningAbove?: number;
  dangerAbove?: number;
  warningBelow?: number;
  dangerBelow?: number;
}

export interface InterpretDefinition {
  thresholds?: ThresholdRule;
  /** Display unit: '%', 'ms', 'GB' */
  unit?: string;
  format?: 'number' | 'bytes' | 'duration' | 'percent' | 'text' | 'currency' | 'count';
  /** Multiply raw value before formatting (e.g., btc_sync 0.85 × 100 = 85%) */
  scale?: number;
  /** Fixed decimal places for numeric display */
  precision?: number;
  /** Map data values to Badge variants: { WAVE_UP: 'success', CHOP: 'warning' } */
  badgeMap?: Record<string, string>;
  /** Color mode: 'pnl' applies green/red based on value sign */
  colorMode?: 'pnl' | 'default';
  /** What empty/null data means semantically */
  emptyMeans?: 'ok' | 'warning' | 'danger' | 'unknown';
  /** Data older than this is stale */
  freshnessMs?: number;
  staleAfterMs?: number;
}

/* ─── Mutations (OUT) ─── */

export interface MutationDefinition {
  id: string;
  label: string;
  /** API path segment for the mutation */
  endpoint: string;
  method: 'POST' | 'PUT' | 'DELETE';
  /** Confirm text — supports {field} interpolation from row data */
  confirm?: string;
  confirmTitle?: string;
  dangerous?: boolean;
  /** Maps mutation body keys to row field names: { service: 'name' } */
  payloadFromRow?: Record<string, string>;
  /** UI parameters for select+execute pattern (e.g., action dropdown before toggle) */
  parameters?: MutationParameter[];
  description?: string;
}

export interface MutationParameter {
  id: string;
  label: string;
  options: { value: string; label: string }[];
}

/* ─── Representation ─── */

export interface ColumnDefinition {
  key: string;
  label: string;
  align?: 'left' | 'center' | 'right';
  /** Serializable render hints — no React closures */
  render?: 'text' | 'badge' | 'mono' | 'time' | 'pnl' | 'direction';
}

export interface RepresentationHints {
  preferredView: ViewKind;
  fallbackView?: ViewKind;
  salience: 'high' | 'normal' | 'low';
  density?: 'compact' | 'normal' | 'comfortable';
  /** Grouping key for layout composition */
  group?: string;
  /** Sort order within group */
  order?: number;
  /** Lucide icon name */
  icon?: string;
  /** For gauge: which sub-field of extracted data is the primary value */
  valueField?: string;
  /** Template string: '{used} / {total}' interpolated from data */
  detailTemplate?: string;
  /** Secondary detail template */
  subDetailTemplate?: string;
  /** Column definitions for table views */
  columns?: ColumnDefinition[];
  /** Max items to display (for feeds/lists) */
  maxItems?: number;
  /** Key for custom view lookup via customViews prop on NodeRenderer */
  customViewId?: string;
  /** Data normalization hint: 'find-array' scans object values for first array */
  dataNormalize?: 'find-array';
  /** Node IDs rendered as children by CompositeView */
  children?: string[];
  /** Layout mode for CompositeView */
  layout?: 'row' | 'grid' | 'stack' | 'mini-grid' | 'inline';
}

/* ─── Reflexes (aspirational) ─── */

export interface ReflexDefinition {
  id: string;
  when: string;
  then: string;
  enabledByDefault?: boolean;
}

/* ─── Node ─── */

export interface NodeDefinition {
  /** Dot-notation ID: 'system.cpu', 'voice.gateway' */
  id: string;
  domain: string;
  title: string;
  description?: string;
  kind: NodeKind;
  sense: SenseDefinition;
  interpret?: InterpretDefinition;
  mutations?: MutationDefinition[];
  reflexes?: ReflexDefinition[];
  representation: RepresentationHints;
  tags?: string[];
}

/* ─── Owner Profile ─── */

export interface OwnerRepresentationProfile {
  id: string;
  density: 'compact' | 'normal' | 'comfortable';
  layoutFamily: 'dashboard' | 'editorial' | 'console' | 'hybrid';
  motion: 'low' | 'normal';
  defaultViews?: Partial<Record<NodeKind, ViewKind>>;
  /** Per-node overrides: { 'system.cpu': { preferredView: 'stat' } } */
  nodePins?: Record<string, Partial<RepresentationHints>>;
  renderer: 'react-tailwind';
}
