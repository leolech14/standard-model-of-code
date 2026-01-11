/**
 * Standard Model of Code - TypeScript Types
 * 
 * Auto-generated type definitions for the Standard Model particle schema.
 * 
 * @version 1.0.0
 * @see https://standardmodelofcode.org/schemas/
 */

// ============================================================================
// Enums
// ============================================================================

/** Holarchy levels from L-3 (Bit) to L12 (Universe) */
export type Level =
    | 'L-3' | 'L-2' | 'L-1' | 'L0' | 'L1' | 'L2' | 'L3'
    | 'L4' | 'L5' | 'L6' | 'L7' | 'L8' | 'L9' | 'L10' | 'L11' | 'L12';

/** Popper's Three Worlds */
export type Plane = 'Physical' | 'Virtual' | 'Semantic';

/** Clean Architecture layers */
export type Layer = 'Interface' | 'Application' | 'Core' | 'Infrastructure' | 'Test' | 'Unknown';

/** Information flow boundary */
export type Boundary = 'Internal' | 'Input' | 'Output' | 'I-O';

/** State management characteristic */
export type State = 'Stateful' | 'Stateless';

/** Side effect classification */
export type Effect = 'Pure' | 'Read' | 'Write' | 'ReadWrite';

/** Object lifecycle phase */
export type Lifecycle = 'Create' | 'Use' | 'Destroy';

/** Popper World 2 - Intent clarity (NEW from foundational theories) */
export type Intent = 'Documented' | 'Implicit' | 'Ambiguous' | 'Contradictory';

/** DDD tactical roles (33 roles) */
export type Role =
    | 'Query' | 'Finder' | 'Loader' | 'Getter'
    | 'Command' | 'Creator' | 'Mutator' | 'Destroyer'
    | 'Factory' | 'Builder'
    | 'Repository' | 'Store' | 'Cache'
    | 'Service' | 'Controller' | 'Manager'
    | 'Validator' | 'Guard' | 'Asserter'
    | 'Transformer' | 'Mapper' | 'Serializer'
    | 'Handler' | 'Listener' | 'Subscriber'
    | 'Utility' | 'Formatter' | 'Helper'
    | 'Internal' | 'Lifecycle'
    | 'Unknown';

/** Edge types for relationships */
export type EdgeType =
    | 'calls' | 'imports' | 'uses' | 'references'
    | 'inherits' | 'implements' | 'extends' | 'mixes_in'
    | 'contains' | 'is_part_of' | 'returns' | 'receives'
    | 'precedes' | 'follows' | 'triggers' | 'disposes'
    | 'delegates_to' | 'decorates' | 'wraps';

/** Edge family groups */
export type EdgeFamily = 'Structural' | 'Dependency' | 'Inheritance' | 'Semantic' | 'Temporal';

// ============================================================================
// Core Interfaces
// ============================================================================

/** 10-dimensional semantic classification (8 core + 2 contextual) */
export interface Dimensions {
    /** D1: Atom type - what kind of code entity */
    D1_WHAT: string;
    /** D2: Clean Architecture layer */
    D2_LAYER?: Layer;
    /** D3: DDD tactical role */
    D3_ROLE?: Role;
    /** D4: Information flow boundary */
    D4_BOUNDARY?: Boundary;
    /** D5: State management */
    D5_STATE?: State;
    /** D6: Side effects */
    D6_EFFECT?: Effect;
    /** D7: Lifecycle phase */
    D7_LIFECYCLE?: Lifecycle;
    /** D8: Classification confidence (0-100) */
    D8_TRUST?: number;
    /** D9: Popper World 2 - Intent clarity (NEW) */
    D9_INTENT?: Intent;
    /** D10: Ranganathan Matter facet - Language (NEW) */
    D10_LANGUAGE?: string;
}

/** Source code location */
export interface Location {
    /** Relative file path */
    file: string;
    /** Starting line number (1-indexed) */
    line_start: number;
    /** Ending line number (1-indexed) */
    line_end: number;
    /** Starting column (0-indexed) */
    col_start?: number;
    /** Ending column (0-indexed) */
    col_end?: number;
}

/** Additional metadata about the particle */
export interface ParticleMetadata {
    /** Function/method signature */
    signature?: string;
    /** Documentation string */
    docstring?: string;
    /** Applied decorators/annotations */
    decorators?: string[];
    /** Parameter names */
    parameters?: string[];
    /** Return type annotation */
    return_type?: string;
    /** Cyclomatic complexity */
    complexity?: number;
    /** Lines of code count */
    lines_of_code?: number;
    /** Programming language */
    language?: string;
}

/** Relationship between particles */
export interface Edge {
    /** Target particle ID */
    target: string;
    /** Specific edge type */
    type: EdgeType;
    /** Edge family (one of 5) */
    family: EdgeFamily;
    /** Edge strength (0-1) */
    weight?: number;
    /** Detection confidence (0-100) */
    confidence?: number;
    /** Where relationship is established */
    location?: {
        file: string;
        line: number;
    };
}

// ============================================================================
// Metrics and DDD (From Foundational Theories)
// ============================================================================

/** Complexity metrics (Shannon-inspired) */
export interface ComplexityMetrics {
    cyclomatic?: number;
    cognitive?: number;
    halstead_volume?: number;
    entropy?: number;
}

/** Coupling metrics (Koestler tension dynamics) */
export interface CouplingMetrics {
    afferent?: number;  // Incoming dependencies (Ca)
    efferent?: number;  // Outgoing dependencies (Ce)
    instability?: number;  // Ce / (Ca + Ce)
    tension?: number;  // Balance between autonomy and integration
}

/** Cohesion metrics */
export interface CohesionMetrics {
    lcom?: number;  // Lack of Cohesion of Methods
}

/** Combined metrics (Shannon + Koestler inspired) */
export interface Metrics {
    complexity?: ComplexityMetrics;
    coupling?: CouplingMetrics;
    cohesion?: CohesionMetrics;
}

/** DDD properties (Evans) */
export interface DDDProperties {
    is_aggregate_root?: boolean;
    aggregate_id?: string;
    bounded_context?: string;
    invariants?: string[];
    domain_events?: string[];
}

/** Antimatter law IDs */
export type AntimatterLawId = 'AM001' | 'AM002' | 'AM003' | 'AM004' | 'AM005';

/** Antimatter law names */
export type AntimatterLawName =
    | 'LayerSkipViolation'
    | 'ReverseLayerDependency'
    | 'GodClass'
    | 'AnemicModel'
    | 'BoundedContextViolation';

/** Violation severity */
export type ViolationSeverity = 'ERROR' | 'WARNING' | 'INFO';

/** Antimatter law violation (Clean Arch + Dijkstra + Koestler) */
export interface Violation {
    law_id: AntimatterLawId;
    law_name?: AntimatterLawName;
    severity: ViolationSeverity;
    message: string;
    source_theory?: string;
}

/** A single classified code entity */
export interface Particle {
    /** Unique ID: file_path::qualified_name */
    id: string;
    /** Atom type from 200-atom periodic table */
    atom: string;
    /** Canonical τ notation */
    tau?: string;
    /** Simple name */
    name?: string;
    /** Fully qualified name */
    qualified_name?: string;
    /** 8-dimensional classification */
    dimensions: Dimensions;
    /** Holarchy level */
    level: Level;
    /** Popper's world */
    plane: Plane;
    /** Source location */
    location: Location;
    /** Additional metadata */
    metadata?: ParticleMetadata;
    /** Outgoing edges */
    edges_out?: Edge[];
    /** Complexity/coupling metrics (Shannon + Koestler) */
    metrics?: Metrics;
    /** DDD properties (Evans) */
    ddd?: DDDProperties;
    /** Antimatter law violations */
    violations?: Violation[];
}

// ============================================================================
// Graph Types
// ============================================================================

/** Repository information */
export interface Repository {
    /** Repository name */
    name: string;
    /** Absolute path to root */
    root: string;
    /** Detected languages */
    languages?: string[];
    /** Git commit hash */
    commit?: string;
    /** Git branch */
    branch?: string;
}

/** Aggregate statistics */
export interface GraphStatistics {
    total_particles?: number;
    total_edges?: number;
    total_files?: number;
    total_lines?: number;
    by_level?: Record<Level, number>;
    by_layer?: Record<Layer, number>;
    by_phase?: Record<string, number>;
    by_role?: Record<Role, number>;
    by_edge_family?: Record<EdgeFamily, number>;
    by_language?: Record<string, number>;
    confidence?: {
        mean: number;
        median: number;
        min: number;
        max: number;
    };
}

/** Complete codebase graph */
export interface Graph {
    /** Schema version */
    version: string;
    /** Generation timestamp */
    generated_at: string;
    /** Generator tool info */
    generator?: {
        name: string;
        version: string;
    };
    /** Repository info */
    repository: Repository;
    /** Aggregate statistics */
    statistics?: GraphStatistics;
    /** All particles */
    particles: Particle[];
}

// ============================================================================
// Utility Types
// ============================================================================

/** Helper to construct τ notation string */
export function buildTau(d: Dimensions): string {
    const parts = [
        d.D1_WHAT || 'Unknown',
        d.D3_ROLE || 'Unknown',
        d.D2_LAYER || 'Unknown',
        d.D4_BOUNDARY?.[0] || '-',
        d.D5_STATE?.[0] || '-',
        d.D6_EFFECT?.[0] || '-',
        d.D7_LIFECYCLE?.[0] || '-',
        d.D8_TRUST?.toString() || '-'
    ];
    return `τ(${parts.join(':')})`;
}

/** Parse particle ID into components */
export function parseParticleId(id: string): { file: string; name: string } {
    const [file, name] = id.split('::');
    return { file, name };
}

/** Check if edge crosses boundary */
export function isBoundaryCrossing(particle: Particle): boolean {
    return particle.dimensions.D4_BOUNDARY === 'I-O'
        || particle.dimensions.D4_BOUNDARY === 'Input'
        || particle.dimensions.D4_BOUNDARY === 'Output';
}
