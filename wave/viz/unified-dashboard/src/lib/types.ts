export interface Waybill {
    parcel_id: string;
    batch_id: string;
    merkle_root: string;
    refinery_signature: string;
    context_vector?: number[];
    route?: any[];
}

export interface RefineryChunk {
    chunk_id: string;
    file: string;
    content: string;
    type?: string;
    waybill?: Waybill;
    tokens?: number;
    semantic_hash?: string;
}

export interface ColliderNode {
    id: string;
    name: string;
    level?: number;
    atom_type?: string;
    role?: string;
    file_path?: string;
    file?: string;
    metrics?: Record<string, any>;
}

export interface ColliderEdge {
    source: string;
    target: string;
    type: string;
    weight?: number;
}

export interface ColliderGraph {
    nodes: ColliderNode[];
    edges: ColliderEdge[];
    metrics?: {
        node_count: number;
        edge_count: number;
        health_score: number;
    };
    manifest?: any;
}

export interface ProjectManifest {
    schema_version: string;
    generated_at_utc: string;
    batch_id: string;
    waybill: {
        parcel_id: string;
        batch_id: string;
        merkle_root: string;
        refinery_signature: string;
    };
}
