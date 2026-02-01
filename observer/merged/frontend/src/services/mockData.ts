import { CanonicalStage, PipelineId, Artifact, Run, Alert, PipelineStageConfig, AppState, AppSettings, TruthStatus } from '../types';

const generateId = () => Math.random().toString(36).substring(2, 9);
const now = Date.now();
const hour = 3600000;

// Projects
const PROJECTS = ['Project_Helios', 'Project_Aether', 'Project_Nyx', 'Internal_Ops'];

// Initial Static Config (Seeding)
const INITIAL_PIPELINES: Record<PipelineId, PipelineStageConfig[]> = {
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
        projectId: PROJECTS[Math.floor(Math.random() * PROJECTS.length)],
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
        projectId: PROJECTS[Math.floor(Math.random() * PROJECTS.length)],
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
        projectId: PROJECTS[Math.floor(Math.random() * PROJECTS.length)],
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
    projects: PROJECTS,
    pipelines: INITIAL_PIPELINES,
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

export interface LayoutState {
    x: number;
    y: number;
    w: number;
    h: number;
}

export class Repository {
    private storageKey = 'cloud_refinery_data_v2';
    private stateKey = 'cloud_refinery_state_v1';
    private layoutKey = 'cloud_refinery_layout_v1';

    private safeParse<T>(raw: string | null, fallback: T): T {
        if (!raw) return fallback;
        try {
            return JSON.parse(raw) as T;
        } catch {
            return fallback;
        }
    }

    getData() {
        const stored = localStorage.getItem(this.storageKey);
        const parsed = this.safeParse(stored, null as any);

        if (parsed) return parsed;

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

    // Trigger explicit chaos events for testing
    triggerChaos(type: 'latency' | 'outage' | 'traffic') {
        const data = this.getData();
        const newAlert: Alert = {
            id: `chaos_${generateId()}`,
            timestamp: Date.now(),
            acknowledged: false,
            source: 'CHAOS_MONKEY',
            severity: type === 'outage' ? 'critical' : 'warning',
            message: type === 'latency' ? 'Artificial latency injected into mesh.' :
                     type === 'outage' ? 'Simulated partial availability zone failure.' :
                     'Sudden traffic burst detected.'
        };
        data.alerts.unshift(newAlert);

        if (type === 'outage') {
            // Fail some active runs
            data.runs.forEach((r: Run) => {
                if (r.status === 'running') r.status = 'failed';
            });
        }

        if (type === 'traffic') {
            // Spike queue depths
            Object.values(data.pipelines).forEach((stages: any) => {
                stages.forEach((s: any) => s.queueDepth += 500);
            });
        }

        localStorage.setItem(this.storageKey, JSON.stringify(data));
        return data;
    }

    // Simulation Engine: Brings the dashboard to life
    simulate() {
        const data = this.getData();

        // 1. Mutate Pipelines (Queue Depth & Status)
        Object.keys(data.pipelines).forEach(key => {
            const stages = data.pipelines[key as PipelineId] as PipelineStageConfig[];
            stages.forEach(stage => {
                // Random Walk for Queue Depth
                if (Math.random() > 0.6) {
                    const change = Math.floor(Math.random() * 20) - 8; // -8 to +12
                    stage.queueDepth = Math.max(0, stage.queueDepth + change);
                }

                // Occasional Status Flip (Rare)
                if (Math.random() > 0.98) {
                   if (stage.status === 'running') stage.status = Math.random() > 0.8 ? 'success' : 'idle';
                   else if (stage.status === 'idle') stage.status = 'running';
                   stage.lastUpdated = Date.now();
                }
            });
        });

        // 2. Inject New Runs (Occasional)
        if (Math.random() > 0.8) {
            const newRun: Run = {
                id: `run_${generateId()}`,
                projectId: PROJECTS[Math.floor(Math.random() * PROJECTS.length)],
                pipelineId: Math.random() > 0.5 ? PipelineId.Refinery : PipelineId.Factory,
                status: 'running',
                startTime: Date.now(),
                duration: '0s',
                triggeredBy: 'scheduler'
            };
            data.runs.unshift(newRun);
            if (data.runs.length > 100) data.runs.pop(); // Keep list bounded
        }

        // 3. Update Active Run Durations
        data.runs.forEach((r: Run) => {
            if (r.status === 'running') {
                 // Simple increment logic simulation
                 const parts = r.duration.split(' ');
                 // Just a visual mock update, usually we'd calc from startTime
                 r.duration = `${Math.floor((Date.now() - r.startTime) / 1000)}s`;

                 // Chance to finish
                 if (Math.random() > 0.9) {
                     r.status = Math.random() > 0.9 ? 'failed' : 'success';
                 }
            }
        });

        localStorage.setItem(this.storageKey, JSON.stringify(data));
        return data;
    }

    getAppState(): AppState {
        const stored = localStorage.getItem(this.stateKey);
        let state = this.safeParse<AppState>(stored, { lastVisit: Date.now(), theme: 'dark', settings: DEFAULT_SETTINGS });

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

    // --- Layout Persistence ---

    getLayout(id: string): LayoutState | null {
        try {
            const allLayouts = this.safeParse(localStorage.getItem(this.layoutKey), {});
            return allLayouts[id] || null;
        } catch (e) {
            return null;
        }
    }

    saveLayout(id: string, layout: LayoutState) {
        try {
            const allLayouts = this.safeParse(localStorage.getItem(this.layoutKey), {});
            allLayouts[id] = layout;
            localStorage.setItem(this.layoutKey, JSON.stringify(allLayouts));
        } catch (e) {
            console.error("Failed to save layout", e);
        }
    }

    reset() {
        localStorage.removeItem(this.storageKey);
        localStorage.removeItem(this.stateKey);
        localStorage.removeItem(this.layoutKey);
        window.location.reload();
    }
}

export const repository = new Repository();
