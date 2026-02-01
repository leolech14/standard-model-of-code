import { CanonicalStage, PipelineId, Artifact, Run, Alert, PipelineStageConfig, AppState, AppSettings, TruthStatus } from '../types';

const generateId = () => Math.random().toString(36).substring(2, 9);
const now = Date.now();
const hour = 3600000;

export const PIPELINE_CONFIGS: Record<PipelineId, PipelineStageConfig[]> = {
    [PipelineId.Refinery]: [
        { name: CanonicalStage.Capture, description: "Ingests raw telemetry from edge nodes.", status: 'success', queueDepth: 12, lastUpdated: now - 2 * hour },
        { name: CanonicalStage.Separate, description: "Splits streams into audio, video, and metadata.", status: 'running', queueDepth: 450, lastUpdated: now },
        { name: CanonicalStage.Clean, description: "Normalizes audio gain and removes video artifacts.", status: 'idle', queueDepth: 0, lastUpdated: now - 5 * hour },
        { name: CanonicalStage.Enrich, description: "Adds AI-generated tags and transcription.", status: 'success', queueDepth: 5, lastUpdated: now - 1 * hour, isLoopStart: true },
        { name: CanonicalStage.Mix, description: "Combines enriched streams for preview.", status: 'failed', queueDepth: 2, lastUpdated: now - 30 * 60000, isLoopEnd: true, loopTarget: CanonicalStage.Enrich },
        { name: CanonicalStage.Publish, description: "Pushes to CDN and archives to cold storage.", status: 'idle', queueDepth: 0, lastUpdated: now - 12 * hour }
    ],
    [PipelineId.Factory]: [
        { name: CanonicalStage.Capture, description: "Polls external partner APIs for new assets.", status: 'success', queueDepth: 0, lastUpdated: now - 4 * hour },
        { name: CanonicalStage.Clean, description: "Standardizes metadata formats.", status: 'success', queueDepth: 0, lastUpdated: now - 4 * hour },
        { name: CanonicalStage.Distill, description: "Generates summary reports and thumbnails.", status: 'running', queueDepth: 89, lastUpdated: now },
        { name: CanonicalStage.Publish, description: "Updates internal registries.", status: 'idle', queueDepth: 0, lastUpdated: now - 24 * hour }
    ]
};

const ARTIFACT_TYPES = ['json', 'mp4', 'wav', 'log', 'parquet', 'md'];
const TAGS = ['v1.2', 'prod', 'staging', 'experimental', 'deprecated', 'audit'];
const ATOM_CLASSES = ['ATOM:Spec', 'ATOM:Tool', 'ATOM:Role', 'ATOM:Doc', 'ATOM:Signal'];
const TRUTH_STATUSES: TruthStatus[] = ['VERIFIED', 'SUPPORTED', 'CONFLICTING', 'STALE', 'UNVERIFIED'];

// Helper to create clusters of identical artifacts for stacking demo
const createClones = (template: Partial<Artifact>, count: number): Artifact[] => {
    return Array.from({ length: count }).map((_, i) => ({
        id: `clone_${generateId()}_${i}`,
        name: `${template.name}_${i}`,
        pipelineId: PipelineId.Refinery,
        stage: CanonicalStage.Capture,
        type: 'file',
        size: '1KB',
        updatedAt: now,
        tags: [],
        status: 'live',
        isVaulted: false,
        atomClass: 'ATOM:Doc',
        truthStatus: 'UNVERIFIED',
        ...template // Override defaults
    } as Artifact));
};

const generateArtifacts = (count: number): Artifact[] => {
    const randomArtifacts: Artifact[] = Array.from({ length: count }).map((_, i) => ({
        id: `art_${generateId()}`,
        name: `element_${generateId()}_${i}`,
        pipelineId: i % 2 === 0 ? PipelineId.Refinery : PipelineId.Factory,
        stage: Object.values(CanonicalStage)[Math.floor(Math.random() * Object.values(CanonicalStage).length)],
        type: ARTIFACT_TYPES[Math.floor(Math.random() * ARTIFACT_TYPES.length)],
        size: `${(Math.random() * 500).toFixed(1)}MB`,
        updatedAt: now - Math.floor(Math.random() * 48 * hour),
        tags: [TAGS[Math.floor(Math.random() * TAGS.length)]],
        status: (Math.random() > 0.9 ? 'failed' : 'live') as Artifact['status'],
        isVaulted: Math.random() > 0.95,
        atomClass: ATOM_CLASSES[Math.floor(Math.random() * ATOM_CLASSES.length)],
        truthStatus: TRUTH_STATUSES[Math.floor(Math.random() * TRUTH_STATUSES.length)]
    }));

    // Inject Large Stacks for Inventory Demo
    const bigStacks: Artifact[] = [
        // Stack 1: 523 Verified Specs (Refinery Publish)
        ...createClones({
            pipelineId: PipelineId.Refinery,
            stage: CanonicalStage.Publish,
            type: 'json',
            atomClass: 'ATOM:Spec',
            truthStatus: 'VERIFIED',
            name: 'Canonical_Schema_V2',
            size: '12KB',
            tags: ['prod']
        }, 523),

        // Stack 2: 840 Raw Signals (Refinery Capture)
        ...createClones({
            pipelineId: PipelineId.Refinery,
            stage: CanonicalStage.Capture,
            type: 'log',
            atomClass: 'ATOM:Signal',
            truthStatus: 'UNVERIFIED',
            name: 'Edge_Telemetry_Raw',
            size: '2MB',
            tags: ['audit']
        }, 840),

        // Stack 3: 105 Archived Tools (Factory Clean)
        ...createClones({
            pipelineId: PipelineId.Factory,
            stage: CanonicalStage.Clean,
            type: 'py',
            atomClass: 'ATOM:Tool',
            truthStatus: 'STALE',
            name: 'Legacy_Parser_Script',
            size: '45KB',
            tags: ['deprecated'],
            status: 'archived'
        }, 105)
    ];

    return [...randomArtifacts, ...bigStacks];
};

const generateRuns = (count: number): Run[] => {
    return Array.from({ length: count }).map((_, i) => ({
        id: `run_${generateId()}`,
        pipelineId: Math.random() > 0.5 ? PipelineId.Refinery : PipelineId.Factory,
        status: (Math.random() > 0.8 ? 'failed' : (Math.random() > 0.9 ? 'running' : 'success')) as Run['status'],
        startTime: now - Math.floor(Math.random() * 72 * hour),
        duration: `${Math.floor(Math.random() * 60)}m ${Math.floor(Math.random() * 60)}s`,
        triggeredBy: Math.random() > 0.7 ? 'scheduler' : 'webhook'
    }));
};

const generateAlerts = (count: number): Alert[] => {
    return Array.from({ length: count }).map((_, i) => ({
        id: `alt_${generateId()}`,
        severity: (Math.random() > 0.8 ? 'critical' : (Math.random() > 0.5 ? 'warning' : 'info')) as Alert['severity'],
        message: `Drift detected in ${Math.random() > 0.5 ? 'audio' : 'metadata'} normalization layer.`,
        timestamp: now - Math.floor(Math.random() * 24 * hour),
        acknowledged: Math.random() > 0.7,
        source: 'Monitor_Daemon_01'
    }));
};

// Initial Seed
const INITIAL_DATA = {
    artifacts: generateArtifacts(200), // Base random noise + big stacks injected above
    runs: generateRuns(45),
    alerts: generateAlerts(8)
};

const DEFAULT_SETTINGS: AppSettings = {
    pollInterval: 5000,
    showNotifications: true,
    autoPin: false,
    apiBaseUrl: ''
};

export class Repository {
    private storageKey = 'cloud_refinery_data_v1';
    private stateKey = 'cloud_refinery_state_v1';

    getData() {
        const stored = localStorage.getItem(this.storageKey);
        if (stored) return JSON.parse(stored);

        localStorage.setItem(this.storageKey, JSON.stringify(INITIAL_DATA));
        return INITIAL_DATA;
    }

    updateArtifact(updated: Artifact) {
        const data = this.getData();
        const index = data.artifacts.findIndex((a: any) => a.id === updated.id);
        if (index !== -1) {
            data.artifacts[index] = updated;
            localStorage.setItem(this.storageKey, JSON.stringify(data));
        }
    }

    getAppState(): AppState {
        const stored = localStorage.getItem(this.stateKey);
        let state: AppState;

        if (stored) {
            state = JSON.parse(stored);
        } else {
            state = { lastVisit: Date.now(), theme: 'dark', settings: DEFAULT_SETTINGS };
        }

        // Merge defaults for new settings fields if missing
        if (!state.settings) {
            state.settings = DEFAULT_SETTINGS;
        } else {
            state.settings = { ...DEFAULT_SETTINGS, ...state.settings };
        }

        return state;
    }

    setAppState(state: AppState) {
        localStorage.setItem(this.stateKey, JSON.stringify(state));
    }

    reset() {
        localStorage.removeItem(this.storageKey);
        localStorage.removeItem(this.stateKey);
        window.location.reload();
    }
}

export const repository = new Repository();
