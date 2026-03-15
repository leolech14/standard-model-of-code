/**
 * Inbox App Specs — Hand-crafted code-to-spec output.
 *
 * These represent what an automated analyzer would produce
 * after reverse-engineering incoming app code. They serve as
 * both example data and format documentation.
 */

import type { AppSpec } from './types';

export const inboxSpecs: Record<string, AppSpec> = {
  'app-1': {
    specVersion: '1.0',
    meta: {
      id: 'app-1',
      name: 'cloud-refinery-console',
      description: 'Dark-mode internal dashboard for monitoring cloud pipelines with typographic aesthetics and deep inspection capabilities.',
      origin: 'zip-upload',
      originRef: 'cloud-refinery-console.zip',
      ingestedAt: Date.now() - 1_200_000,
      sizeBytes: 253_743,
      fileCount: 26,
      stack: {
        framework: 'react',
        bundler: 'vite',
        language: 'typescript',
        styling: 'tailwind',
        target: 'browser',
      },
      status: 'ready',
    },

    architecture: {
      pattern: 'spa',
      entryPoint: 'App.tsx',
      stateManagement: {
        pattern: 'hooks',
        persisted: true,
        persistenceLayer: 'localStorage (Repository class)',
      },
      componentTree: [
        { name: 'App', path: 'App.tsx', loc: 1060, props: {}, children: ['PipelineInspector', 'ArtifactInspector', 'RunInspector', 'AlertInspector', 'InfrastructureInspector', 'InventoryGrid', 'FileSystemExplorer', 'RunsTimeline', 'StorageAnalysis', 'PipelineMetrics', 'FloatingPanel'], role: 'Root shell with sidebar, overlay stack, and view router', complexity: 'root' },
        { name: 'PipelineInspector', path: 'components/PipelineInspector.tsx', loc: 380, props: { pipelineId: 'PipelineId', stages: 'PipelineStageConfig[]', initialStage: 'string?' }, children: [], role: 'Pipeline stage detail viewer with loop indicators', complexity: 'branch' },
        { name: 'InventoryGrid', path: 'components/Inventory.tsx', loc: 520, props: { artifacts: 'Artifact[]' }, children: ['StackInspector'], role: 'Artifact inventory with stack grouping and categorized views', complexity: 'branch' },
        { name: 'FileSystemExplorer', path: 'components/FileSystem.tsx', loc: 600, props: { artifacts: 'Artifact[]' }, children: [], role: 'Virtual filesystem tree with path-based navigation', complexity: 'branch' },
        { name: 'RunsTimeline', path: 'components/Timeline.tsx', loc: 230, props: { runs: 'Run[]' }, children: [], role: 'Chronological run history with status badges', complexity: 'leaf' },
        { name: 'StorageAnalysis', path: 'components/StorageAnalysis.tsx', loc: 150, props: { artifacts: 'Artifact[]' }, children: [], role: 'Storage breakdown by type, pipeline, and status', complexity: 'leaf' },
        { name: 'PipelineMetrics', path: 'components/PipelineMetrics.tsx', loc: 210, props: { runs: 'Run[]' }, children: [], role: 'Pipeline performance metrics and success rates', complexity: 'leaf' },
        { name: 'InfrastructureInspector', path: 'components/InfrastructureInspector.tsx', loc: 310, props: { type: 'string' }, children: [], role: 'Infrastructure views: buffer, cluster, network, projects', complexity: 'branch' },
        { name: 'FloatingPanel', path: 'components/FloatingPanel.tsx', loc: 150, props: { title: 'string', children: 'ReactNode' }, children: [], role: 'Draggable floating overlay panel', complexity: 'leaf' },
        { name: 'Common', path: 'components/Common.tsx', loc: 310, props: {}, children: [], role: 'Shared primitives: Badge, UiRow, SectionHeader, Toast, CommandPalette, ContextMenu', complexity: 'leaf' },
      ],
      dataFlow: 'unidirectional',
      directories: [
        { path: 'components/', role: 'React UI components', fileCount: 9 },
        { path: 'services/', role: 'Data layer (Repository, mock data)', fileCount: 1 },
        { path: 'docs/', role: 'Documentation', fileCount: 1 },
      ],
    },

    sense: {
      apis: [],
      browserApis: [
        { api: 'localStorage', purpose: 'Persist pipeline data, app state, and panel layouts across sessions', complexity: 'basic' },
      ],
      lifecycle: 'polling',
      localSources: [
        { type: 'localStorage', key: 'cloud_refinery_data_v2', holds: 'Pipelines, artifacts, runs, alerts' },
        { type: 'localStorage', key: 'cloud_refinery_state_v1', holds: 'App state (theme, settings, last visit)' },
        { type: 'localStorage', key: 'cloud_refinery_layout_v1', holds: 'Panel position/size state' },
        { type: 'generated', key: 'mockData.ts', holds: '200+ artifacts, 45 runs, 8 alerts, 4 projects, 2 pipelines' },
      ],
    },

    interpret: {
      typeSystem: [
        { name: 'Artifact', file: 'types.ts', fieldCount: 12, purpose: 'Core data unit with pipeline stage, truth status, atom class' },
        { name: 'PipelineStageConfig', file: 'types.ts', fieldCount: 7, purpose: 'Pipeline stage with queue depth, loop markers, status' },
        { name: 'Run', file: 'types.ts', fieldCount: 7, purpose: 'Pipeline execution record with timing and trigger source' },
        { name: 'Alert', file: 'types.ts', fieldCount: 6, purpose: 'System alert with severity and acknowledgment state' },
        { name: 'OverlayItem', file: 'types.ts', fieldCount: 6, purpose: 'Overlay stack entry for drawer/modal navigation' },
        { name: 'CanonicalStage', file: 'types.ts', fieldCount: 7, purpose: 'Enum: Capture, Separate, Clean, Enrich, Mix, Distill, Publish' },
        { name: 'PipelineId', file: 'types.ts', fieldCount: 2, purpose: 'Enum: Refinery, Factory' },
        { name: 'TruthStatus', file: 'types.ts', fieldCount: 5, purpose: 'Union: VERIFIED, SUPPORTED, CONFLICTING, STALE, UNVERIFIED' },
      ],
      transforms: [
        { name: 'Artifact Stacking', input: 'Artifact[]', output: 'ArtifactStack[]', location: 'components/Inventory.tsx' },
        { name: 'Pipeline Metrics', input: 'Run[]', output: '{ successRate, avgDuration }', location: 'App.tsx (overview)' },
        { name: 'Filesystem Tree', input: 'Artifact[]', output: 'TreeNode hierarchy', location: 'components/FileSystem.tsx' },
        { name: 'Simulation Engine', input: 'Repository state', output: 'Mutated state (queue walk, run injection)', location: 'services/mockData.ts' },
      ],
      algorithms: [
        { name: 'Simulation Engine', description: 'Random walk on queue depths, probabilistic status flips, run injection with bounded list', complexity: 'linear', location: 'services/mockData.ts:simulate()' },
        { name: 'Chaos Monkey', description: 'Injects latency/outage/traffic events into live simulation', complexity: 'trivial', location: 'services/mockData.ts:triggerChaos()' },
        { name: 'Stack Grouping', description: 'Groups artifacts by atomClass+stage+pipeline into visual stacks with count', complexity: 'linear', location: 'components/Inventory.tsx' },
      ],
    },

    represent: {
      layoutSystem: 'css-grid',
      layoutConfigurable: false,
      views: [
        { name: 'Overview', renders: 'Infrastructure cards, stats, pipeline sparklines', renderTech: 'dom', realtime: false, component: 'App (renderContent overview)' },
        { name: 'Pipelines', renders: 'Tabbed pipeline inspector with stage details and loop indicators', renderTech: 'dom', realtime: false, component: 'PipelineInspector' },
        { name: 'Explorer', renders: 'Virtual filesystem tree with path navigation', renderTech: 'dom', realtime: false, component: 'FileSystemExplorer' },
        { name: 'Runs', renders: 'Chronological timeline of pipeline executions', renderTech: 'dom', realtime: false, component: 'RunsTimeline' },
        { name: 'Metrics', renders: 'Pipeline performance charts and storage analysis', renderTech: 'dom', realtime: false, component: 'PipelineMetrics' },
        { name: 'Alerts', renders: 'Severity-coded alert feed with acknowledgment', renderTech: 'dom', realtime: false, component: 'App (renderContent alerts)' },
      ],
      theming: { approach: 'tailwind', themeCount: 1, colorModel: 'hex' },
      iconLibrary: 'lucide-react',
    },

    dependencies: {
      runtime: [
        { name: 'react', version: '^19.2.4', purpose: 'UI framework', weight: 'heavy' },
        { name: 'react-dom', version: '^19.2.4', purpose: 'DOM rendering', weight: 'heavy' },
        { name: 'lucide-react', version: '^0.563.0', purpose: 'Icon library', weight: 'medium' },
      ],
      dev: [
        { name: 'vite', version: '^6.2.0', purpose: 'Build tool and dev server', weight: 'heavy' },
        { name: '@vitejs/plugin-react', version: '^5.0.0', purpose: 'React refresh and JSX transform', weight: 'medium' },
        { name: 'typescript', version: '~5.8.2', purpose: 'Type checking', weight: 'heavy' },
      ],
    },

    exposable: [
      { suggestedId: 'inbox.refinery-console.pipelines', title: 'Pipeline Health', nodeKind: 'composite', senseStrategy: 'Proxy localStorage Repository.getData().pipelines through local API route', viewKind: 'composite', confidence: 0.85 },
      { suggestedId: 'inbox.refinery-console.artifacts', title: 'Artifact Inventory', nodeKind: 'table', senseStrategy: 'Proxy Repository.getData().artifacts with stacking transform', viewKind: 'table', confidence: 0.75 },
      { suggestedId: 'inbox.refinery-console.runs', title: 'Run Timeline', nodeKind: 'feed', senseStrategy: 'Proxy Repository.getData().runs sorted by startTime', viewKind: 'feed', confidence: 0.80 },
      { suggestedId: 'inbox.refinery-console.alerts', title: 'Active Alerts', nodeKind: 'feed', senseStrategy: 'Proxy Repository.getData().alerts filtered by !acknowledged', viewKind: 'feed', confidence: 0.90 },
    ],

    risks: [
      { category: 'performance', severity: 'warning', message: 'App.tsx is 1060 lines — monolithic root component', location: 'App.tsx' },
      { category: 'compatibility', severity: 'info', message: 'Uses React 19 — verify peer dependency compatibility', location: 'package.json' },
      { category: 'maintenance', severity: 'info', message: 'All data is mock-generated on first load — no real API integration', location: 'services/mockData.ts' },
      { category: 'missing', severity: 'info', message: 'No test files detected', location: '/' },
      { category: 'compatibility', severity: 'info', message: 'Color system uses raw Tailwind hex — incompatible with Algebra-UI without migration', location: 'App.tsx' },
    ],
  },

  'app-2': {
    specVersion: '1.0',
    meta: {
      id: 'app-2',
      name: 'audio-analyzer-pro',
      description: 'Professional audio analysis tool with real-time spectrogram, waveform, vectorscope, and LUFS metering.',
      origin: 'zip-upload',
      originRef: 'audio-analyzer-pro.zip',
      ingestedAt: Date.now() - 2_400_000,
      sizeBytes: 278_714,
      fileCount: 28,
      stack: {
        framework: 'react',
        bundler: 'vite',
        language: 'typescript',
        styling: 'tailwind',
        target: 'browser',
      },
      status: 'ready',
    },

    architecture: {
      pattern: 'spa',
      entryPoint: 'src/App.tsx',
      stateManagement: { pattern: 'hooks', persisted: false },
      componentTree: [
        { name: 'App', path: 'src/App.tsx', loc: 350, props: {}, children: ['DropZone', 'Transport', 'Spectrogram', 'Waveform', 'SpectrumAnalyzer', 'Vectorscope', 'LUFSMeter', 'Lyrics'], role: 'Root shell with drag-to-resize grid layout and preset system', complexity: 'root' },
        { name: 'DropZone', path: 'src/components/DropZone.tsx', loc: 65, props: { onLoad: '(buffer, file) => void' }, children: [], role: 'Drag-and-drop audio file upload with visual feedback', complexity: 'leaf' },
        { name: 'Transport', path: 'src/components/Transport.tsx', loc: 80, props: { buffer: 'AudioBuffer' }, children: [], role: 'Play/pause/stop/seek controls with time display', complexity: 'leaf' },
        { name: 'Spectrogram', path: 'src/components/Spectrogram.tsx', loc: 210, props: { buffer: 'AudioBuffer' }, children: [], role: 'Canvas-based real-time spectrogram with scrolling time axis', complexity: 'leaf' },
        { name: 'ThreeSpectrogram', path: 'src/components/ThreeSpectrogram.tsx', loc: 185, props: { buffer: 'AudioBuffer' }, children: [], role: '3D WebGL spectrogram using Three.js with camera orbit', complexity: 'leaf' },
        { name: 'Waveform', path: 'src/components/Waveform.tsx', loc: 200, props: { buffer: 'AudioBuffer' }, children: [], role: 'Canvas waveform with playhead, click-to-seek, zoom', complexity: 'leaf' },
        { name: 'SpectrumAnalyzer', path: 'src/components/SpectrumAnalyzer.tsx', loc: 105, props: {}, children: [], role: 'Real-time frequency spectrum bar chart with peak hold', complexity: 'leaf' },
        { name: 'Vectorscope', path: 'src/components/Vectorscope.tsx', loc: 130, props: {}, children: [], role: 'Stereo field vectorscope (L/R phase correlation display)', complexity: 'leaf' },
        { name: 'LUFSMeter', path: 'src/components/LUFSMeter.tsx', loc: 125, props: {}, children: [], role: 'Loudness metering with K-weighted filtering per ITU-R BS.1770', complexity: 'leaf' },
        { name: 'Lyrics', path: 'src/components/Lyrics.tsx', loc: 160, props: { transcription: 'TranscriptionItem[]' }, children: [], role: 'Synced lyrics display with auto-scroll and active line highlighting', complexity: 'leaf' },
      ],
      dataFlow: 'event-driven',
      directories: [
        { path: 'src/components/', role: 'React visualization components', fileCount: 9 },
        { path: 'src/utils/', role: 'Audio engine and waveform processing', fileCount: 2 },
        { path: 'src/services/', role: 'Transcription service (external API)', fileCount: 1 },
      ],
    },

    sense: {
      apis: [
        { endpoint: 'Whisper-compatible transcription API', method: 'POST', returns: 'TranscriptionItem[] (timestamped segments)', usedBy: ['Lyrics'] },
      ],
      browserApis: [
        { api: 'Web Audio API', purpose: 'Audio decoding, playback, FFT analysis, K-weighted LUFS filtering, stereo channel splitting', complexity: 'advanced' },
        { api: 'Canvas 2D', purpose: 'Real-time rendering of spectrogram, waveform, spectrum analyzer, vectorscope', complexity: 'advanced' },
        { api: 'WebGL (Three.js)', purpose: '3D spectrogram visualization with orbit controls', complexity: 'advanced' },
        { api: 'Drag and Drop API', purpose: 'Audio file upload via drag-and-drop', complexity: 'basic' },
        { api: 'File API', purpose: 'Reading uploaded audio files as ArrayBuffer for decoding', complexity: 'basic' },
      ],
      lifecycle: 'raf',
      localSources: [
        { type: 'file-input', key: 'user-uploaded audio', holds: 'Audio file (wav, mp3, etc.) decoded to AudioBuffer' },
      ],
    },

    interpret: {
      typeSystem: [
        { name: 'AudioEngine', file: 'src/utils/AudioEngine.ts', fieldCount: 12, purpose: 'Singleton audio graph: context, analysers, splitter, LUFS filters, playback state' },
        { name: 'TranscriptionItem', file: 'src/services/transcriptionService.ts', fieldCount: 3, purpose: 'Timestamped text segment from speech-to-text' },
        { name: 'Layout (react-grid-layout)', file: 'src/App.tsx', fieldCount: 6, purpose: 'Grid panel positions: i, x, y, w, h per view' },
      ],
      transforms: [
        { name: 'Audio Decode', input: 'File (binary)', output: 'AudioBuffer (PCM samples)', location: 'AudioEngine.loadAudio()' },
        { name: 'FFT Analysis', input: 'Time-domain audio signal', output: 'Frequency-domain magnitudes (Uint8Array)', location: 'AudioEngine.analyser (AnalyserNode)' },
        { name: 'K-Weight Filtering', input: 'Raw audio signal', output: 'K-weighted signal for LUFS measurement', location: 'AudioEngine.lufsFilter*' },
        { name: 'Stereo Split', input: 'Stereo AudioBuffer', output: 'Independent L/R channel analysers', location: 'AudioEngine.splitter' },
        { name: 'Waveform Processing', input: 'AudioBuffer', output: 'Downsampled peak data for display', location: 'src/utils/waveformProcessor.ts' },
        { name: 'BPM Detection', input: 'AudioBuffer', output: 'Estimated BPM (number)', location: 'src/App.tsx' },
      ],
      algorithms: [
        { name: 'K-Weighted LUFS', description: 'ITU-R BS.1770 loudness measurement via high-shelf (+4dB@1.5kHz) and high-pass (38Hz) filters into RMS calculation', complexity: 'nontrivial', location: 'AudioEngine constructor + LUFSMeter' },
        { name: 'Vectorscope Rendering', description: 'L/R phase correlation displayed as Lissajous figure on canvas', complexity: 'nontrivial', location: 'Vectorscope.tsx' },
        { name: 'Spectrogram Scrolling', description: 'Column-shift canvas rendering with color-mapped FFT magnitudes per time slice', complexity: 'nontrivial', location: 'Spectrogram.tsx' },
        { name: 'Peak Hold', description: 'Spectrum analyzer retains peak values with gradual decay for visual reference', complexity: 'trivial', location: 'SpectrumAnalyzer.tsx' },
      ],
    },

    represent: {
      layoutSystem: 'react-grid-layout',
      layoutConfigurable: true,
      views: [
        { name: 'Spectrogram', renders: 'Scrolling frequency-vs-time heatmap', renderTech: 'canvas-2d', realtime: true, component: 'Spectrogram' },
        { name: '3D Spectrogram', renders: '3D frequency terrain with orbit camera', renderTech: 'three.js', realtime: true, component: 'ThreeSpectrogram' },
        { name: 'Waveform', renders: 'Audio amplitude over time with playhead', renderTech: 'canvas-2d', realtime: true, component: 'Waveform' },
        { name: 'Spectrum Analyzer', renders: 'Real-time frequency bars with peak hold', renderTech: 'canvas-2d', realtime: true, component: 'SpectrumAnalyzer' },
        { name: 'Vectorscope', renders: 'Stereo field Lissajous figure (L/R correlation)', renderTech: 'canvas-2d', realtime: true, component: 'Vectorscope' },
        { name: 'LUFS Meter', renders: 'K-weighted loudness meter with target range', renderTech: 'dom', realtime: true, component: 'LUFSMeter' },
        { name: 'Lyrics', renders: 'Synced transcript with active line tracking', renderTech: 'dom', realtime: true, component: 'Lyrics' },
      ],
      theming: { approach: 'css-vars', themeCount: 2, colorModel: 'hex' },
      iconLibrary: 'lucide-react',
    },

    dependencies: {
      runtime: [
        { name: 'react', version: '^19.2.4', purpose: 'UI framework', weight: 'heavy' },
        { name: 'react-dom', version: '^19.2.4', purpose: 'DOM rendering', weight: 'heavy' },
        { name: 'react-grid-layout', version: '*', purpose: 'Draggable/resizable panel grid', weight: 'medium' },
        { name: 'three', version: '*', purpose: '3D WebGL rendering for spectrogram', weight: 'heavy' },
        { name: 'lucide-react', version: '*', purpose: 'Icon library', weight: 'medium' },
      ],
      dev: [
        { name: 'vite', version: '^6.2.0', purpose: 'Build tool and dev server', weight: 'heavy' },
        { name: '@vitejs/plugin-react', version: '^5.0.0', purpose: 'React refresh and JSX transform', weight: 'medium' },
        { name: 'typescript', version: '~5.8.2', purpose: 'Type checking', weight: 'heavy' },
      ],
    },

    exposable: [
      { suggestedId: 'inbox.audio-analyzer.lufs', title: 'Audio Loudness', nodeKind: 'metric', senseStrategy: 'Embed AudioEngine as iframe/web-worker, expose LUFS reading via postMessage', viewKind: 'gauge', confidence: 0.60 },
      { suggestedId: 'inbox.audio-analyzer.spectrum', title: 'Frequency Spectrum', nodeKind: 'composite', senseStrategy: 'Custom view embedding canvas-based spectrum analyzer', viewKind: 'custom', confidence: 0.45 },
    ],

    risks: [
      { category: 'compatibility', severity: 'warning', message: 'Depends on Three.js — heavy dependency (>500KB), may conflict with existing bundle', location: 'package.json' },
      { category: 'security', severity: 'warning', message: 'Transcription service expects API key in .env — must not be committed', location: '.env.example' },
      { category: 'compatibility', severity: 'info', message: 'Uses react-grid-layout which expects specific CSS imports', location: 'src/App.tsx' },
      { category: 'performance', severity: 'info', message: '5 real-time RAF loops running simultaneously — high CPU usage when all panels visible', location: 'src/components/*' },
      { category: 'compatibility', severity: 'info', message: 'Color system uses raw hex/CSS vars, not parametric OKLCH', location: 'src/index.css' },
      { category: 'missing', severity: 'info', message: 'No test files detected' },
    ],
  },
};

export function getAllSpecs(): AppSpec[] {
  return Object.values(inboxSpecs);
}

export function getSpecById(id: string): AppSpec | undefined {
  return inboxSpecs[id];
}
