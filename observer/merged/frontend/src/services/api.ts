import { CanonicalStage, PipelineId, Artifact, Run, Alert, PipelineStageConfig, AppState, AppSettings, TruthStatus } from '../types';

// Use exact same types/interfaces as mockData to ensure drop-in replacement
const PROJECTS = ['Real_Backend_Data'];

// Initial Static Config (Same as mockData)
const INITIAL_PIPELINES: Record<PipelineId, PipelineStageConfig[]> = {
    [PipelineId.Refinery]: [
        { name: CanonicalStage.Capture, description: "Ingests raw telemetry from edge nodes.", status: 'success', queueDepth: 12, lastUpdated: Date.now() },
        { name: CanonicalStage.Separate, description: "Splits streams into audio, video, and metadata.", status: 'running', queueDepth: 450, lastUpdated: Date.now() },
        { name: CanonicalStage.Clean, description: "Normalizes audio gain and removes video artifacts.", status: 'idle', queueDepth: 0, lastUpdated: Date.now() },
        { name: CanonicalStage.Enrich, description: "Adds AI-generated tags and transcription.", status: 'success', queueDepth: 5, lastUpdated: Date.now(), isLoopStart: true },
        { name: CanonicalStage.Mix, description: "Combines enriched streams for preview.", status: 'failed', queueDepth: 2, lastUpdated: Date.now(), isLoopEnd: true, loopTarget: CanonicalStage.Enrich },
        { name: CanonicalStage.Publish, description: "Pushes to CDN and archives to cold storage.", status: 'idle', queueDepth: 0, lastUpdated: Date.now() }
    ],
    [PipelineId.Factory]: [
        { name: CanonicalStage.Capture, description: "Polls external partner APIs for new assets.", status: 'success', queueDepth: 0, lastUpdated: Date.now() },
        { name: CanonicalStage.Clean, description: "Standardizes metadata formats.", status: 'success', queueDepth: 0, lastUpdated: Date.now() },
        { name: CanonicalStage.Distill, description: "Generates summary reports and thumbnails.", status: 'running', queueDepth: 89, lastUpdated: Date.now() },
        { name: CanonicalStage.Publish, description: "Updates internal registries.", status: 'idle', queueDepth: 0, lastUpdated: Date.now() }
    ]
};

const DEFAULT_SETTINGS: AppSettings = {
    pollInterval: 5000,
    showNotifications: true,
    autoPin: false,
    apiBaseUrl: ''
};

export class Repository {
    private storageKey = 'cloud_refinery_data_real';
    private stateKey = 'cloud_refinery_state_v1';

    // Cache
    private _data: any = null;

    private async fetchFiles(): Promise<any[]> {
        try {
            // Fetch root directory
            const res = await fetch('/api/list?path=.');
            if (!res.ok) return [];
            const json = await res.json();
            return json.files || [];
        } catch (e) {
            console.error("Failed to fetch files", e);
            return [];
        }
    }

    // Enrich raw file with Dashboard metadata
    private enrichFile(file: any): Artifact {
        // Deterministic hashing for consistent properties
        const hash = file.name.split('').reduce((acc: number, char: string) => acc + char.charCodeAt(0), 0);

        const pipelineId = hash % 2 === 0 ? PipelineId.Refinery : PipelineId.Factory;
        const stages = Object.values(CanonicalStage);
        const stage = stages[hash % stages.length];
        const status = hash % 10 > 8 ? 'failed' : 'live';
        const project = PROJECTS[hash % PROJECTS.length];

        return {
            id: file.path, // Use path as ID
            name: file.name,
            projectId: project,
            pipelineId: pipelineId,
            stage: stage as CanonicalStage,
            type: file.type || 'file',
            size: file.size ? `${(file.size / 1024).toFixed(1)}KB` : '0KB',
            updatedAt: file.modified * 1000,
            tags: file.is_directory ? ['dir'] : ['file'],
            status: status as any,
            isVaulted: false,
            atomClass: 'ATOM:Doc',
            truthStatus: 'VERIFIED'
        };
    }

    getData() {
        // If we have cached data, return it immediately (sync)
        // But trigger an async update
        if (this._data) {
            this.refreshData(); // Fire and forget
            return this._data;
        }

        // Return initial structure while loading
        this.refreshData();
        return {
            projects: PROJECTS,
            pipelines: INITIAL_PIPELINES,
            artifacts: [], // Will populate async
            runs: [],
            alerts: []
        };
    }

    async refreshData() {
        try {
            // Parallel fetch for speed
            const [pipelinesRes, files] = await Promise.all([
                fetch('/api/pipelines'),
                this.fetchFiles()
            ]);

            let pipelines = INITIAL_PIPELINES;
            if (pipelinesRes.ok) {
                pipelines = await pipelinesRes.json();
            }

            // Enrich artifacts using the fetched pipelines config (or default)
            // TODO: In future, fetch('/api/artifacts') directly when implemented
            const artifacts = files.map(f => this.enrichFile(f));

            this._data = {
                projects: PROJECTS,
                pipelines: pipelines,
                artifacts: artifacts,
                runs: [], // TODO: map from /api/runs
                alerts: [] // TODO: map from /api/alerts
            };

            // Save to storage for persistence across reloads if needed
            localStorage.setItem(this.storageKey, JSON.stringify(this._data));
        } catch (e) {
            console.error("Failed to refresh data", e);
        }
    }

    // Compat methods
    updateArtifact(updated: Artifact) {
        if (this._data) {
            this._data.artifacts = this._data.artifacts.map((a: any) => a.id === updated.id ? updated : a);
        }
    }

    triggerChaos(type: string) {
        return this._data || this.getData();
    }

    simulate() {
        // Just return current data, maybe slight variations
        // We'll trust the periodic refreshData calls instead
        this.refreshData();
        return this._data || { projects: PROJECTS, pipelines: INITIAL_PIPELINES, artifacts: [], runs: [], alerts: [] };
    }

    getAppState(): AppState {
        const stored = localStorage.getItem(this.stateKey);
        try {
            return JSON.parse(stored!) || { lastVisit: Date.now(), theme: 'dark', settings: DEFAULT_SETTINGS };
        } catch {
            return { lastVisit: Date.now(), theme: 'dark', settings: DEFAULT_SETTINGS };
        }
    }

    setAppState(state: AppState) {
        localStorage.setItem(this.stateKey, JSON.stringify(state));
    }

    reset() {
        this._data = null;
        localStorage.removeItem(this.storageKey);
        localStorage.removeItem(this.stateKey);
        window.location.reload();
    }
}

export const repository = new Repository();
