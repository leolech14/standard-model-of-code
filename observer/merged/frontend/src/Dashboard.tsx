import React, { useState, useEffect, useRef } from 'react';
import {
    LayoutDashboard, Activity, Box, Database,
    List, AlertTriangle, Settings, Search,
    ChevronLeft, ChevronRight, CheckCircle2,
    ArrowLeft, Menu, X, PanelLeftClose, PanelLeftOpen,
    Clock, BarChart3, Zap, Command, Download, RotateCcw,
    Server, Cpu, Network, FileStack, Repeat, Lock, HardDrive,
    Layers, FolderTree, Sidebar as SidebarIcon,
    ChevronDown, Play, Settings2, Copy, SearchCode, PieChart,
    Trash2, Unlock, TrendingUp, AlertOctagon
} from 'lucide-react';
import { repository } from './services/mockData';
import { OverlayItem, ViewType, AppState, PipelineId, Artifact, AppSettings, PipelineStageConfig, ContextMenuRequest } from './types';
import { UiLink, UiRow, Badge, SectionHeader, EmptyState, ToastContainer, ToastMessage, CommandPalette, ContextMenu, KeyboardShortcuts, ContextMenuItem } from './components/Common';
import { PipelineInspector } from './components/PipelineInspector';
import { ArtifactInspector, RunInspector, AlertInspector } from './components/Inspectors';
import { InfrastructureInspector } from './components/InfrastructureInspector';
import { InventoryGrid, StackInspector, StackListInspector, CategorizedInventory, ArtifactStack, HorizontalStackInspector } from './components/Inventory';
import { FileSystemExplorer } from './components/FileSystem';
import { RunsTimeline } from './components/Timeline';
import { StorageAnalysis } from './components/StorageAnalysis';
import { PipelineMetrics } from './components/PipelineMetrics';

// --- HELPERS ---

const getOverlayTitle = (item: OverlayItem): string => {
    switch (item.kind) {
        case 'pipeline':
             if (item.data.stage) return item.data.stage.name;
             if (item.data.pipelineId) return item.data.pipelineId.replace(' Pipeline', '');
             return 'Pipeline';
        case 'artifact': return item.data.name.length > 20 ? item.data.name.substring(0, 18) + '...' : item.data.name;
        case 'run': return item.data.id;
        case 'alert': return 'Alert';
        case 'stack': return item.data.sample?.atomClass || 'Stack';
        case 'stack-list': return 'Artifacts';
        case 'infra-buffer': return 'Global Buffer';
        case 'infra-cluster': return 'Cluster Status';
        case 'infra-network': return 'Network Mesh';
        case 'project-list': return 'Projects';
        case 'storage-analysis': return 'Storage Analysis';
        case 'pipeline-metrics': return 'Pipeline Metrics';
        case 'log': return 'Log';
        default: return 'Item';
    }
};

// --- MAIN APP ---

const NAV_ITEMS = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'pipelines', label: 'Pipelines', icon: Activity },
    { id: 'metrics', label: 'Metrics', icon: BarChart3 },
    { id: 'explorer', label: 'Explorer', icon: FolderTree },
    { id: 'runs', label: 'Runs', icon: List },
    { id: 'alerts', label: 'Alerts', icon: AlertTriangle },
    { id: 'settings', label: 'Settings', icon: Settings },
];

export default function Dashboard() {
    const [view, setView] = useState<ViewType>('overview');
    const [viewStack, setViewStack] = useState<ViewType[]>([]);

    const [data, setData] = useState<any>(null);
    const [appState, setAppState] = useState<AppState | null>(null);
    const [overlayStack, setOverlayStack] = useState<OverlayItem[]>([]);

    // UI State
    const [sidebarExpanded, setSidebarExpanded] = useState(false);
    const [leftSidebarCollapsed, setLeftSidebarCollapsed] = useState(false);
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
    const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);
    const [shortcutsOpen, setShortcutsOpen] = useState(false);
    const [contextMenu, setContextMenu] = useState<ContextMenuRequest | null>(null);
    const [toasts, setToasts] = useState<ToastMessage[]>([]);

    const [selectedArtifactIds, setSelectedArtifactIds] = useState<Set<string>>(new Set());

    const [lastVisitStats, setLastVisitStats] = useState<any>(null);
    const [pipelineTab, setPipelineTab] = useState<PipelineId>(PipelineId.Refinery);

    const [inspectingStack, setInspectingStack] = useState<ArtifactStack | null>(null);

    const [runsProjectTab, setRunsProjectTab] = useState<string>('All');
    const [showCompletedRuns, setShowCompletedRuns] = useState(true);

    const [searchQuery, setSearchQuery] = useState('');

    // --- TOAST MANAGER ---
    const addToast = (title: string, description?: string, type: 'info'|'error'|'success'|'warning' = 'info') => {
        const id = Math.random().toString(36).substring(7);
        setToasts(prev => [...prev, { id, title, description, type }]);
        setTimeout(() => {
            setToasts(prev => prev.filter(t => t.id !== id));
        }, 5000);
    };

    // Load Data
    useEffect(() => {
        const d = repository.getData();
        const state = repository.getAppState();

        const now = Date.now();
        const nextState = { ...state, lastVisit: now };

        setData(d);
        setAppState(nextState);

        const diff = now - state.lastVisit;
        if (diff > 5000) {
            const newRuns = d.runs.filter((r: any) => r.startTime > state.lastVisit).length;
            const newAlerts = d.alerts.filter((a: any) => a.timestamp > state.lastVisit).length;
            if (newRuns > 0 || newAlerts > 0) {
                setLastVisitStats({ newRuns, newAlerts });
            }
        }

        repository.setAppState(nextState);
    }, []);

    // Simulation Polling Loop
    useEffect(() => {
        if (!appState?.settings) return;

        const intervalMs = appState.settings.pollInterval;
        const intervalId = setInterval(() => {
            const currentData = repository.getData();
            const prevAlertsCount = currentData.alerts.length;
            const newData = repository.simulate();

            if (appState.settings.showNotifications && newData.alerts.length > prevAlertsCount) {
                const newAlert = newData.alerts[0];
                addToast("New System Alert", newAlert.message, newAlert.severity === 'critical' ? 'error' : 'info');
            }

            setData({ ...newData });
        }, intervalMs);

        return () => clearInterval(intervalId);
    }, [appState?.settings]);

    // Global Key Handlers
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.key === 'Escape') {
                if (contextMenu) setContextMenu(null);
                else if (selectedArtifactIds.size > 0) setSelectedArtifactIds(new Set());
                else if (inspectingStack) setInspectingStack(null);
                else if (commandPaletteOpen) setCommandPaletteOpen(false);
                else if (shortcutsOpen) setShortcutsOpen(false);
                else handleBack();
            }
            if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                e.preventDefault();
                setCommandPaletteOpen(prev => !prev);
            }
            if (e.key === '?' && !['INPUT', 'TEXTAREA'].includes((e.target as HTMLElement).tagName)) {
                setShortcutsOpen(true);
            }
            if (e.key === '/' && !['INPUT', 'TEXTAREA'].includes((e.target as HTMLElement).tagName)) {
                e.preventDefault();
                handleNavigate('search');
            }
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [overlayStack, viewStack, mobileMenuOpen, commandPaletteOpen, shortcutsOpen, inspectingStack, contextMenu, selectedArtifactIds]);

    const handleArtifactUpdate = (updated: Artifact) => {
        repository.updateArtifact(updated);
        setData((prev: any) => ({
            ...prev,
            artifacts: prev.artifacts.map((a: any) => a.id === updated.id ? updated : a)
        }));
        setOverlayStack(prev => prev.map(item =>
            (item.kind === 'artifact' && item.data.id === updated.id)
                ? { ...item, data: updated }
                : item
        ));
        addToast("Artifact Updated", `${updated.name} has been updated.`, "success");
    };

    const handleSettingChange = (key: keyof AppSettings, value: any) => {
        setAppState(prev => {
            if (!prev) return prev;
            const newSettings = { ...prev.settings, [key]: value };
            const newState = { ...prev, settings: newSettings };
            repository.setAppState(newState);
            return newState;
        });
    };

    const handleChaosTrigger = (type: 'latency' | 'outage' | 'traffic') => {
        const newData = repository.triggerChaos(type);
        setData({ ...newData });
        const title = type === 'latency' ? 'Latency Injected' : type === 'outage' ? 'Outage Triggered' : 'Traffic Burst';
        addToast(title, 'System state modified manually.', 'warning');
    };

    const downloadJson = (filename: string, content: any) => {
        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(content, null, 2));
        const downloadAnchorNode = document.createElement('a');
        downloadAnchorNode.setAttribute("href", dataStr);
        downloadAnchorNode.setAttribute("download", filename + ".json");
        document.body.appendChild(downloadAnchorNode);
        downloadAnchorNode.click();
        downloadAnchorNode.remove();
        addToast("Export Complete", `Downloaded ${filename}.json`, "success");
    };

    const handleNavigate = (newView: ViewType) => {
        if (view === newView) {
            setMobileMenuOpen(false);
            return;
        }
        // Clear selection on navigation to avoid confusion
        setSelectedArtifactIds(new Set());

        setViewStack(prev => [...prev, view]);
        setView(newView);
        setMobileMenuOpen(false);
        setInspectingStack(null);
    };

    const activeDrawer = overlayStack.filter(i => i.type === 'drawer').at(-1);
    const activeModal = overlayStack.filter(i => i.type === 'modal').at(-1);
    const canGoBack = overlayStack.length > 0 || viewStack.length > 0 || inspectingStack !== null;

    const getActiveEl = () =>
        document.activeElement instanceof HTMLElement ? document.activeElement : null;

    const pushOverlay = (item: Omit<OverlayItem, 'id' | 'returnFocus'>) => {
        const newItem: OverlayItem = {
            ...item,
            id: Math.random().toString(36),
            returnFocus: getActiveEl()
        };
        setOverlayStack(prev => [...prev, newItem]);
    };

    const handleBack = () => {
        if (activeModal) {
            setOverlayStack(prev => prev.filter(i => i.id !== activeModal.id));
            return;
        }
        if (activeDrawer) {
            setOverlayStack(prev => prev.filter(i => i.id !== activeDrawer.id));
            activeDrawer.returnFocus?.focus?.();
            return;
        }
        if (inspectingStack) {
            setInspectingStack(null);
            return;
        }
        if (mobileMenuOpen) {
            setMobileMenuOpen(false);
            return;
        }
        if (viewStack.length > 0) {
            const prevView = viewStack[viewStack.length - 1];
            setViewStack(prev => prev.slice(0, -1));
            setView(prevView);
            return;
        }
    };

    const handleCanvasClick = (e: React.MouseEvent) => {
        if (activeDrawer) handleBack();
        if (contextMenu) setContextMenu(null);
    };

    const drawerStack = overlayStack.filter(i => i.type === 'drawer');

    const handleBreadcrumbClick = (targetId: string) => {
        setOverlayStack(prev => {
            const index = prev.findIndex(item => item.id === targetId);
            if (index === -1) return prev;
            return prev.slice(0, index + 1);
        });
    };

    const closeAllDrawers = () => {
         setOverlayStack(prev => {
             const firstDrawer = prev.find(i => i.type === 'drawer');
             const rootFocus = firstDrawer?.returnFocus;
             const kept = prev.filter(i => i.type !== 'drawer');
             rootFocus?.focus?.();
             return kept;
         });
    };

    // --- SELECTION HANDLER ---
    const toggleSelection = (id: string) => {
        setSelectedArtifactIds(prev => {
            const next = new Set(prev);
            if (next.has(id)) next.delete(id);
            else next.add(id);
            return next;
        });
    };

    const clearSelection = () => setSelectedArtifactIds(new Set());

    const handleBulkAction = (action: 'vault' | 'unvault' | 'delete') => {
        if (!data) return;
        const updates: Artifact[] = [];
        const ids = Array.from(selectedArtifactIds);

        ids.forEach(id => {
            const art = data.artifacts.find((a: any) => a.id === id);
            if (art) {
                if (action === 'vault') updates.push({ ...art, isVaulted: true });
                if (action === 'unvault') updates.push({ ...art, isVaulted: false });
                // Delete logic would go here
            }
        });

        updates.forEach(u => repository.updateArtifact(u));
        setData((prev: any) => ({
            ...prev,
            artifacts: prev.artifacts.map((a: any) => {
                const u = updates.find(up => up.id === a.id);
                return u || a;
            })
        }));

        addToast("Bulk Action", `${updates.length} items updated.`, 'success');
        clearSelection();
    };

    // --- CONTEXT MENU HANDLER ---
    const handleContextMenu = (e: React.MouseEvent, type: 'artifact' | 'stack', data: any) => {
        e.preventDefault();
        e.stopPropagation();
        setContextMenu({
            x: e.clientX,
            y: e.clientY,
            kind: type,
            data
        });
    };

    const getContextMenuItems = (): ContextMenuItem[] => {
        if (!contextMenu) return [];
        const { kind, data } = contextMenu;

        if (kind === 'artifact') {
            const art = data as Artifact;
            return [
                { label: 'Select Item', icon: CheckCircle2, action: () => toggleSelection(art.id) },
                { label: 'Inspect Artifact', icon: SearchCode, action: () => pushOverlay({ type: 'drawer', kind: 'artifact', data: art, breadcrumb: 'Inspector' }) },
                { label: art.isVaulted ? 'Remove from Vault' : 'Save to Vault', icon: Lock, action: () => handleArtifactUpdate({ ...art, isVaulted: !art.isVaulted }) },
                { label: 'Copy ID', icon: Copy, action: () => { navigator.clipboard.writeText(art.id); addToast('Copied', art.id, 'success'); } },
                { label: 'Trace Pipeline', icon: Activity, action: () => { setPipelineTab(art.pipelineId); handleNavigate('pipelines'); addToast('Navigation', `Switched to ${art.pipelineId}`, 'info'); } },
            ];
        } else if (kind === 'stack') {
            const stack = data as ArtifactStack;
            return [
                 { label: 'Inspect Stack', icon: Layers, action: () => setInspectingStack(stack) },
                 { label: 'Export JSON', icon: Download, action: () => downloadJson(`stack_${stack.sample.atomClass}`, stack.artifacts) },
                 { label: 'Copy All IDs', icon: Copy, action: () => { const text = stack.artifacts.map(a => a.id).join('\n'); navigator.clipboard.writeText(text); addToast('Copied', `${stack.count} IDs copied`, 'success'); } }
            ]
        }
        return [];
    };

    // --- COMMAND PALETTE ---
    const commandActions = [
        ...NAV_ITEMS.map(item => ({
            id: `nav-${item.id}`,
            label: `Go to ${item.label}`,
            icon: <item.icon className="w-4 h-4" />,
            perform: () => handleNavigate(item.id as ViewType)
        })),
        // Removed duplicate metrics action as it is now in NAV_ITEMS
        { id: 'storage-analysis', label: 'View Storage Analysis', icon: <PieChart className="w-4 h-4" />, perform: () => pushOverlay({ type: 'drawer', kind: 'storage-analysis', data: data?.artifacts, breadcrumb: 'Analytics' }) },
        { id: 'infra-buffer', label: 'View Global Buffer', icon: <Database className="w-4 h-4" />, perform: () => pushOverlay({ type: 'drawer', kind: 'infra-buffer', data: null, breadcrumb: 'Infra' }) },
        { id: 'infra-cluster', label: 'View Cluster Health', icon: <Server className="w-4 h-4" />, perform: () => pushOverlay({ type: 'drawer', kind: 'infra-cluster', data: null, breadcrumb: 'Infra' }) },
        { id: 'project-list', label: 'View Active Projects', icon: <Box className="w-4 h-4" />, perform: () => pushOverlay({ type: 'drawer', kind: 'project-list', data: null, breadcrumb: 'Overview' }) },
        { id: 'export-inventory', label: 'Export Inventory JSON', icon: <Download className="w-4 h-4" />, perform: () => downloadJson('inventory_export', data?.artifacts || []) },
        { id: 'reset-cache', label: 'Reset Local Cache', icon: <RotateCcw className="w-4 h-4" />, perform: () => { repository.reset(); } },
        { id: 'help', label: 'Show Keyboard Shortcuts', icon: <Box className="w-4 h-4" />, perform: () => setShortcutsOpen(true) },
        // Chaos
        { id: 'chaos-latency', label: 'SIMULATE: Network Latency', icon: <Activity className="w-4 h-4 text-amber-500" />, perform: () => handleChaosTrigger('latency') },
        { id: 'chaos-outage', label: 'SIMULATE: Zone Outage', icon: <AlertOctagon className="w-4 h-4 text-rose-500" />, perform: () => handleChaosTrigger('outage') },
    ];

    // --- FILTERS ---
    const getFilteredArtifacts = () => {
        if (!data) return [];
        let res = data.artifacts;
        if (view === 'pipelines') res = res.filter((a: any) => a.pipelineId === pipelineTab);

        if (searchQuery) {
            const q = searchQuery.toLowerCase();
            res = res.filter((a: any) =>
                a.name.toLowerCase().includes(q) ||
                a.id.toLowerCase().includes(q) ||
                a.tags.some((t: string) => t.toLowerCase().includes(q))
            );
        }
        return res;
    };

    const getFilteredRuns = () => {
        if (!data) return [];
        let res = data.runs;
        if (runsProjectTab !== 'All') {
            res = res.filter((r: any) => r.projectId === runsProjectTab);
        }
        if (!showCompletedRuns) {
            res = res.filter((r: any) => r.status === 'running');
        }
        if (searchQuery) {
            const q = searchQuery.toLowerCase();
            res = res.filter((r: any) =>
                r.id.toLowerCase().includes(q) ||
                r.pipelineId.toLowerCase().includes(q)
            );
        }
        return res;
    };

    const getFilteredAlerts = () => {
        if (!data) return [];
        let res = data.alerts;
        if (searchQuery) {
            const q = searchQuery.toLowerCase();
            res = res.filter((a: any) =>
                a.message.toLowerCase().includes(q) ||
                a.source.toLowerCase().includes(q)
            );
        }
        return res;
    };


    // --- RENDERERS ---

    const renderMainContent = () => {
        if (!data) return <div className="p-10 text-neutral-600">Loading...</div>;

        switch (view) {
            case 'search':
                const q = searchQuery.toLowerCase();
                const foundArtifacts = data.artifacts.filter((a: any) =>
                    a.name.toLowerCase().includes(q) ||
                    a.id.toLowerCase().includes(q)
                );
                return (
                    <div className="p-4 md:p-8 h-full overflow-y-auto animate-in fade-in duration-300">
                        <SectionHeader title={`Search Results for "${searchQuery}"`} />
                        {foundArtifacts.length === 0 && <EmptyState message="No results found" />}
                        <div className="space-y-1">
                            {foundArtifacts.map((art: any) => (
                                <UiRow key={art.id} onClick={() => pushOverlay({ type: 'drawer', kind: 'artifact', data: art, breadcrumb: 'Search' })}>
                                    <div className="flex justify-between w-full text-sm text-neutral-300 truncate">
                                        <span className="truncate mr-2">{art.name}</span>
                                        <span className="text-neutral-500 shrink-0">{art.type}</span>
                                    </div>
                                </UiRow>
                            ))}
                        </div>
                    </div>
                );

            case 'pipelines':
                const currentPipelineConfig = data.pipelines[pipelineTab] as PipelineStageConfig[];
                const pipelineArtifacts = data.artifacts.filter((a: any) => a.pipelineId === pipelineTab);

                return (
                    <div className="h-full flex flex-col animate-in fade-in duration-300 overflow-hidden bg-neutral-950">
                        {/* Tab Bar */}
                        <div className="flex items-center px-4 md:px-8 border-b border-neutral-900 bg-neutral-950/50 shrink-0">
                            {[PipelineId.Refinery, PipelineId.Factory].map(pid => (
                                <button
                                    key={pid}
                                    onClick={() => { setPipelineTab(pid); setInspectingStack(null); }}
                                    className={`py-4 px-6 text-[10px] md:text-xs font-bold uppercase tracking-widest border-b-2 transition-all ${pipelineTab === pid ? 'border-neutral-200 text-neutral-100' : 'border-transparent text-neutral-600 hover:text-neutral-400'}`}
                                >
                                    {pid.replace(' Pipeline', '')}
                                </button>
                            ))}
                        </div>

                        {/* Integrated Canvas with Overlay Sidebar */}
                        <div className="flex-1 relative overflow-hidden bg-neutral-950">
                            <PipelineInspector
                                pipelineId={pipelineTab}
                                stages={currentPipelineConfig}
                                hideHeader={false}
                                onViewArtifacts={(stage) => {
                                    const stageArtifacts = pipelineArtifacts.filter((a: any) => a.stage === stage.name);
                                    pushOverlay({ type: 'drawer', kind: 'stack-list', data: stageArtifacts, breadcrumb: 'Pipeline Artifacts' });
                                }}
                            />

                            {/* Overlay Stage Summary (Integrated into Canvas) */}
                            <div className="absolute top-4 left-4 w-72 pointer-events-none hidden md:block">
                                <div className="bg-neutral-950/40 backdrop-blur-md border border-neutral-800 rounded-lg p-4 pointer-events-auto shadow-2xl">
                                    <div className="flex justify-between items-center mb-6">
                                        <div className="text-[10px] font-bold uppercase tracking-widest text-neutral-500">Stage Summary</div>
                                        <button className="text-[9px] font-bold uppercase text-neutral-600 hover:text-neutral-300 transition-colors">Show All</button>
                                    </div>
                                    <div className="space-y-5">
                                        {currentPipelineConfig.map(stage => {
                                            const stageItems = pipelineArtifacts.filter((a: any) => a.stage === stage.name);
                                            const total = stageItems.length;
                                            const failed = stageItems.filter((a: any) => a.status === 'failed').length;
                                            const success = total - failed;
                                            const successPct = total > 0 ? (success / total) * 100 : 0;
                                            const failedPct = total > 0 ? (failed / total) * 100 : 0;

                                            return (
                                                <div
                                                    key={stage.name}
                                                    className="group cursor-pointer"
                                                    onClick={() => {
                                                        const stageArtifacts = pipelineArtifacts.filter((a: any) => a.stage === stage.name);
                                                        pushOverlay({ type: 'drawer', kind: 'stack-list', data: stageArtifacts, breadcrumb: 'Pipeline Artifacts' });
                                                    }}
                                                >
                                                    <div className="flex items-center justify-between mb-1.5">
                                                        <div className="flex items-center space-x-2">
                                                            <ChevronRight className="w-3 h-3 text-neutral-600 group-hover:text-indigo-500 transition-colors" />
                                                            <span className="text-[10px] font-bold uppercase tracking-widest text-neutral-400 group-hover:text-neutral-100 transition-colors">
                                                                {stage.name}
                                                            </span>
                                                        </div>
                                                        <span className="text-[10px] font-mono text-neutral-500">{total}</span>
                                                    </div>
                                                    <div className="h-1 w-full bg-neutral-900 rounded-full overflow-hidden flex">
                                                        <div className="bg-emerald-500/60 h-full" style={{ width: `${successPct}%` }} />
                                                        <div className="bg-rose-500/60 h-full" style={{ width: `${failedPct}%` }} />
                                                    </div>
                                                </div>
                                            );
                                        })}
                                    </div>
                                </div>
                            </div>

                            {inspectingStack && (
                                <HorizontalStackInspector
                                    stack={inspectingStack}
                                    onClose={() => setInspectingStack(null)}
                                    onSelectArtifact={(art) => pushOverlay({ type: 'drawer', kind: 'artifact', data: art, breadcrumb: 'Deep Inspector' })}
                                />
                            )}
                        </div>
                    </div>
                );

            case 'metrics':
                return (
                    <div className="h-full overflow-hidden animate-in fade-in duration-300">
                        <PipelineMetrics runs={data.runs} />
                    </div>
                );

            case 'runs':
                const allProjects = ['All', ...data.projects];
                const activeRuns = getFilteredRuns();

                return (
                    <div className="h-full flex flex-col animate-in fade-in duration-300">
                        <div className="flex items-center justify-between px-4 md:px-8 border-b border-neutral-900 bg-neutral-950/50 shrink-0">
                            <div className="flex items-center overflow-x-auto hide-scrollbar flex-1">
                                {allProjects.map(proj => (
                                    <button
                                        key={proj}
                                        onClick={() => setRunsProjectTab(proj)}
                                        className={`py-3 px-4 text-[10px] md:text-xs font-medium border-b-2 transition-colors whitespace-nowrap ${runsProjectTab === proj ? 'border-neutral-500 text-neutral-200' : 'border-transparent text-neutral-600 hover:text-neutral-400'}`}
                                    >
                                        {proj}
                                    </button>
                                ))}
                            </div>
                             <div className="flex items-center space-x-2 md:space-x-3 pl-4 border-l border-neutral-900 ml-2 md:ml-4 py-2 shrink-0">
                                <span className="hidden sm:inline text-[10px] md:text-xs text-neutral-500">Show Completed</span>
                                <button
                                    onClick={() => setShowCompletedRuns(!showCompletedRuns)}
                                    className={`w-7 h-3.5 md:w-8 md:h-4 rounded-full relative transition-colors focus:outline-none ${showCompletedRuns ? 'bg-indigo-600' : 'bg-neutral-700'}`}
                                >
                                    <div className={`absolute top-0.5 left-0.5 w-2.5 h-2.5 md:w-3 md:h-3 bg-white rounded-full transition-transform ${showCompletedRuns ? 'translate-x-3.5 md:translate-x-4' : ''}`} />
                                </button>
                            </div>
                        </div>

                        <div className="p-4 md:p-8 flex-1 overflow-y-auto">
                            <div className="max-w-7xl mx-auto w-full">
                                <div className="flex justify-between items-center mb-6">
                                    <SectionHeader title={runsProjectTab === 'All' ? 'Global Execution History' : `${runsProjectTab} Runs`} />
                                    <div className="text-[10px] text-neutral-600 font-mono shrink-0 ml-4">{activeRuns.length} entries</div>
                                </div>

                                <RunsTimeline
                                    runs={activeRuns}
                                    pipelines={data.pipelines}
                                    onSelect={(run) => pushOverlay({ type: 'drawer', kind: 'run', data: run, breadcrumb: 'Runs' })}
                                />

                                <div className="mt-8 space-y-1">
                                    {activeRuns.map((run: any) => (
                                        <UiRow key={run.id} onClick={() => pushOverlay({ type: 'drawer', kind: 'run', data: run, breadcrumb: 'Runs' })}>
                                             <div className="flex flex-col sm:flex-row sm:items-center justify-between w-full text-xs md:text-sm truncate">
                                                <div className="flex items-center space-x-3 mb-1 sm:mb-0 truncate">
                                                    <Badge status={run.status} />
                                                    <span className="font-mono text-neutral-400 text-[10px] md:text-xs w-16 shrink-0">{run.id}</span>
                                                    <span className="text-neutral-300 truncate">{run.pipelineId.replace(' Pipeline', '')}</span>
                                                    <span className="hidden md:inline text-[10px] text-neutral-600 px-2 border border-neutral-800 rounded-sm bg-neutral-900">{run.projectId}</span>
                                                </div>
                                                <div className="flex items-center space-x-4 text-[10px] md:text-xs text-neutral-500 font-mono pl-6 sm:pl-0 shrink-0">
                                                    <span>{run.duration}</span>
                                                    <span className="hidden sm:inline">{run.triggeredBy}</span>
                                                </div>
                                             </div>
                                        </UiRow>
                                    ))}
                                    {activeRuns.length === 0 && <EmptyState message="No runs found" submessage={!showCompletedRuns ? "Try enabling 'Show Completed' to see past executions." : undefined} />}
                                </div>
                            </div>
                        </div>
                    </div>
                );

            case 'settings':
                return (
                    <div className="p-4 md:p-8 h-full overflow-y-auto animate-in fade-in duration-300">
                        <div className="max-w-3xl">
                            <SectionHeader title="Console Settings" />
                            <div className="space-y-8 mt-6">
                                <div className="p-4 border border-neutral-800 rounded bg-neutral-900/20">
                                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6 sm:mb-4">
                                        <div>
                                            <div className="text-sm text-neutral-200">Simulation Speed</div>
                                            <div className="text-xs text-neutral-500">Adjust the heartbeat of the mock engine.</div>
                                        </div>
                                        <div className="flex bg-neutral-900 p-1 rounded border border-neutral-800">
                                            {[1000, 5000, 10000].map(speed => (
                                                <button
                                                    key={speed}
                                                    onClick={() => handleSettingChange('pollInterval', speed)}
                                                    className={`px-3 py-1 text-[10px] rounded transition-colors ${appState?.settings?.pollInterval === speed ? 'bg-neutral-800 text-neutral-100 shadow-sm' : 'text-neutral-500 hover:text-neutral-300'}`}
                                                >
                                                    {speed === 1000 ? 'Fast' : speed === 5000 ? 'Norm' : 'Slow'}
                                                </button>
                                            ))}
                                        </div>
                                    </div>
                                    <div className="flex items-center justify-between border-t border-neutral-800 pt-4">
                                        <div>
                                            <div className="text-sm text-neutral-200">Auto-Pin to Vault</div>
                                            <div className="text-xs text-neutral-500">Automatically secure verified artifacts.</div>
                                        </div>
                                        <button
                                            className={`w-10 h-5 rounded-full relative transition-colors ${appState?.settings?.autoPin ? 'bg-emerald-600' : 'bg-neutral-700'}`}
                                            onClick={() => handleSettingChange('autoPin', !appState?.settings?.autoPin)}
                                        >
                                            <div className={`absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full transition-transform ${appState?.settings?.autoPin ? 'translate-x-5' : ''}`} />
                                        </button>
                                    </div>
                                </div>

                                <div className="p-4 border border-rose-900/30 bg-rose-900/5 rounded">
                                    <div className="flex items-center space-x-2 mb-4 text-rose-400">
                                        <AlertTriangle className="w-4 h-4" />
                                        <h4 className="text-sm font-medium">Simulation Controls (Chaos)</h4>
                                    </div>
                                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                                        <button onClick={() => handleChaosTrigger('latency')} className="px-3 py-2 border border-rose-900/50 hover:bg-rose-900/20 rounded text-xs text-rose-200 transition-colors">
                                            Inject Latency
                                        </button>
                                        <button onClick={() => handleChaosTrigger('outage')} className="px-3 py-2 border border-rose-900/50 hover:bg-rose-900/20 rounded text-xs text-rose-200 transition-colors">
                                            Trigger Outage
                                        </button>
                                        <button onClick={() => handleChaosTrigger('traffic')} className="px-3 py-2 border border-rose-900/50 hover:bg-rose-900/20 rounded text-xs text-rose-200 transition-colors">
                                            Burst Traffic
                                        </button>
                                    </div>
                                </div>

                                <div className="space-y-4">
                                    <h4 className="text-sm text-neutral-200 font-medium">Session & Data</h4>
                                    <button className="w-full p-4 border border-neutral-800 rounded text-xs text-neutral-400 hover:bg-neutral-900 text-left transition-colors flex justify-between items-center group" onClick={() => { repository.reset(); }}>
                                        <span>Reset Local Cache (Purge and Reload)</span>
                                        <RotateCcw className="w-4 h-4 group-hover:rotate-180 transition-transform duration-500" />
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                )

            case 'explorer':
                return (
                 <FileSystemExplorer
                    artifacts={getFilteredArtifacts()}
                    title="Refinery Explorer"
                    onSelectArtifact={(art) => pushOverlay({ type: 'drawer', kind: 'artifact', data: art, breadcrumb: 'Explorer' })}
                    onContextMenu={handleContextMenu}
                    selectedIds={selectedArtifactIds}
                    onToggleSelection={toggleSelection}
                 />
            );

            case 'alerts': return (
                <div className="p-4 md:p-8 h-full overflow-y-auto animate-in fade-in duration-300">
                    <div className="max-w-7xl mx-auto w-full">
                        <SectionHeader title="System Alerts" />
                        <div className="mt-4 space-y-1">
                            {getFilteredAlerts().map((alert: any) => (
                                <UiRow key={alert.id} onClick={() => pushOverlay({ type: 'drawer', kind: 'alert', data: alert, breadcrumb: 'Alerts' })}>
                                        <div className="flex items-center justify-between w-full text-xs md:text-sm truncate">
                                        <div className="flex items-center space-x-3 truncate">
                                            <AlertTriangle className={`w-4 h-4 flex-shrink-0 ${alert.severity === 'critical' ? 'text-rose-500' : 'text-amber-500'}`} />
                                            <span className="text-neutral-300 truncate">{alert.message}</span>
                                        </div>
                                        <span className="text-[10px] text-neutral-600 shrink-0 ml-4 font-mono">{new Date(alert.timestamp).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})}</span>
                                        </div>
                                </UiRow>
                            ))}
                        </div>
                    </div>
                </div>
            );

            default: // Overview
                const refineryRuns = data.runs.filter((r: any) => r.pipelineId === PipelineId.Refinery).sort((a: any, b: any) => b.startTime - a.startTime);
                const factoryRuns = data.runs.filter((r: any) => r.pipelineId === PipelineId.Factory).sort((a: any, b: any) => b.startTime - a.startTime);

                const getMetrics = (runs: any[]) => {
                    const total = runs.length;
                    if (total === 0) return { successRate: 0, avgDuration: '0s' };
                    const success = runs.filter((r: any) => r.status === 'success').length;
                    const successRate = Math.round((success / total) * 100);
                    let totalSec = 0;
                    runs.forEach(r => {
                         const m = r.duration.match(/(\d+)m/);
                         const s = r.duration.match(/(\d+)s/);
                         totalSec += (m ? parseInt(m[1])*60 : 0) + (s ? parseInt(s[1]) : 0);
                    });
                    const avgSec = Math.round(totalSec / total);
                    const avgDuration = avgSec > 60 ? `${Math.floor(avgSec/60)}m ${avgSec%60}s` : `${avgSec}s`;
                    return { successRate, avgDuration };
                }

                const refMetrics = getMetrics(refineryRuns);
                const facMetrics = getMetrics(factoryRuns);

                const totalQueueDepth = (Object.values(data.pipelines).flat() as PipelineStageConfig[]).reduce((acc, s) => acc + s.queueDepth, 0);
                const bufferPct = Math.min(100, Math.round((totalQueueDepth / 5000) * 100));

                return (
                    <div className="p-4 md:p-8 h-full overflow-y-auto animate-in fade-in duration-300">
                        <div className="max-w-7xl mx-auto w-full">
                            <div className="flex items-center justify-between mb-8">
                                <div>
                                    <h1 className="text-xl md:text-2xl font-light text-neutral-100 mb-1">Overview</h1>
                                    <p className="text-xs md:text-sm text-neutral-500">System metrics and active pipeline health.</p>
                                </div>
                                <button onClick={() => setShortcutsOpen(true)} className="p-2 rounded-full hover:bg-neutral-900 text-neutral-500 hover:text-neutral-300 transition-colors" title="Keyboard Shortcuts">
                                    <span className="sr-only">Help</span>
                                    <span className="text-sm font-bold">?</span>
                                </button>
                            </div>

                             {/* INFRA CARDS */}
                             <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 mb-8">
                                <div onClick={() => pushOverlay({ type: 'drawer', kind: 'infra-buffer', data: null, breadcrumb: 'Overview' })} className="p-4 md:p-5 border border-neutral-800 bg-neutral-900/20 rounded-lg flex flex-col justify-between group cursor-pointer hover:border-neutral-600 hover:bg-neutral-900/40 transition-all">
                                    <div className="flex justify-between items-start mb-4">
                                        <div className="text-[10px] text-neutral-500 uppercase font-semibold tracking-wider">Global Buffer</div>
                                        <Database className="w-4 h-4 text-neutral-700 group-hover:text-indigo-500 transition-colors" />
                                    </div>
                                    <div className="text-xl md:text-2xl font-light text-neutral-200 mb-4">{totalQueueDepth.toLocaleString()}</div>
                                    <div className="w-full h-1 bg-neutral-800 rounded-full overflow-hidden">
                                        <div className={`h-full rounded-full transition-all duration-1000 ${bufferPct > 90 ? 'bg-rose-500' : 'bg-indigo-500'}`} style={{ width: `${bufferPct}%` }} />
                                    </div>
                                </div>

                                <div onClick={() => pushOverlay({ type: 'drawer', kind: 'infra-cluster', data: null, breadcrumb: 'Overview' })} className="p-4 md:p-5 border border-neutral-800 bg-neutral-900/20 rounded-lg flex flex-col justify-between group cursor-pointer hover:border-neutral-600 hover:bg-neutral-900/40 transition-all">
                                    <div className="flex justify-between items-start mb-4">
                                        <div className="text-[10px] text-neutral-500 uppercase font-semibold tracking-wider">Processing Cluster</div>
                                        <Server className="w-4 h-4 text-neutral-700 group-hover:text-emerald-500 transition-colors" />
                                    </div>
                                    <div className="text-xl md:text-2xl font-light text-neutral-200">14<span className="text-sm text-neutral-600 ml-1">/16 online</span></div>
                                </div>

                                <div onClick={() => pushOverlay({ type: 'drawer', kind: 'infra-network', data: null, breadcrumb: 'Overview' })} className="p-4 md:p-5 border border-neutral-800 bg-neutral-900/20 rounded-lg flex flex-col justify-between group cursor-pointer hover:border-neutral-600 hover:bg-neutral-900/40 transition-all sm:col-span-2 md:col-span-1">
                                    <div className="flex justify-between items-start mb-4">
                                        <div className="text-[10px] text-neutral-500 uppercase font-semibold tracking-wider">Network I/O</div>
                                        <Activity className="w-4 h-4 text-neutral-700 group-hover:text-blue-500 transition-colors" />
                                    </div>
                                    <div className="text-xl md:text-2xl font-light text-neutral-200 font-mono tracking-tight">Active</div>
                                </div>
                             </div>

                             <SectionHeader title="Repository Intelligence" />
                             <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4 mb-8">
                                <div onClick={() => pushOverlay({ type: 'drawer', kind: 'project-list', data: data, breadcrumb: 'Overview' })} className="p-4 border border-neutral-800 bg-neutral-900/10 rounded group hover:border-neutral-600 transition-colors cursor-pointer">
                                    <div className="text-[10px] text-neutral-500 uppercase mb-2">Projects</div>
                                    <div className="text-xl md:text-2xl font-light text-neutral-200">{data.projects.length}</div>
                                </div>
                                <div onClick={() => { setPipelineTab(PipelineId.Refinery); handleNavigate('pipelines'); }} className="p-4 border border-neutral-800 bg-neutral-900/10 rounded group hover:border-neutral-600 transition-colors cursor-pointer">
                                    <div className="text-[10px] text-neutral-500 uppercase mb-2">Active Loops</div>
                                    <div className="text-xl md:text-2xl font-light text-neutral-200">1</div>
                                </div>
                                <div onClick={() => handleNavigate('explorer')} className="p-4 border border-neutral-800 bg-neutral-900/10 rounded group hover:border-neutral-600 transition-colors cursor-pointer">
                                    <div className="text-[10px] text-neutral-500 uppercase mb-2">Secured</div>
                                    <div className="text-xl md:text-2xl font-light text-neutral-200">{data.artifacts.filter((a: any) => a.isVaulted).length}</div>
                                </div>
                                <div className="p-4 border border-neutral-800 bg-neutral-900/10 rounded group hover:border-neutral-700 transition-colors cursor-default">
                                    <div className="text-[10px] text-neutral-500 uppercase mb-2">Footprint</div>
                                    <div className="text-xl md:text-2xl font-light text-neutral-200">4.2 <span className="text-xs text-neutral-600">GB</span></div>
                                </div>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                {/* Pipeline Sparkline Cards */}
                                <div onClick={() => { setPipelineTab(PipelineId.Refinery); handleNavigate('pipelines'); }} className="p-5 md:p-6 border border-neutral-800 rounded-lg bg-neutral-900/20 hover:border-neutral-700 hover:bg-neutral-900/40 cursor-pointer transition-all group overflow-hidden">
                                    <div className="flex justify-between items-start mb-6">
                                        <div>
                                            <h3 className="text-sm md:text-base font-medium text-neutral-200 group-hover:text-white transition-colors flex items-center gap-2 truncate">Cloud Refinery <Activity className="w-3 h-3 text-neutral-600" /></h3>
                                            <p className="text-[10px] text-neutral-500 mt-1 truncate">Ingest • Separate • Enrich • Mix</p>
                                        </div>
                                        <Badge status="running" />
                                    </div>
                                    <div className="grid grid-cols-2 gap-4 mb-6">
                                        <div className="text-lg md:text-xl font-light text-neutral-200">{refMetrics.successRate}% <span className="text-[10px] text-neutral-600 uppercase block font-semibold">Success</span></div>
                                        <div className="text-lg md:text-xl font-light text-neutral-200">{refMetrics.avgDuration} <span className="text-[10px] text-neutral-600 uppercase block font-semibold">Avg Time</span></div>
                                    </div>
                                    <div className="flex items-end space-x-[2px] h-10">
                                        {refineryRuns.slice(0, 32).reverse().map((run: any) => (
                                            <div key={run.id} className={`flex-1 rounded-t-sm transition-all origin-bottom ${run.status === 'success' ? 'bg-emerald-500/20' : run.status === 'failed' ? 'bg-rose-500/40' : 'bg-blue-500/40 animate-pulse'}`} style={{ height: `${Math.max(20, Math.random() * 80 + 20)}%` }} />
                                        ))}
                                    </div>
                                </div>

                                 <div onClick={() => { setPipelineTab(PipelineId.Factory); handleNavigate('pipelines'); }} className="p-5 md:p-6 border border-neutral-800 rounded-lg bg-neutral-900/20 hover:border-neutral-700 hover:bg-neutral-900/40 cursor-pointer transition-all group overflow-hidden">
                                    <div className="flex justify-between items-start mb-6">
                                        <div>
                                            <h3 className="text-sm md:text-base font-medium text-neutral-200 group-hover:text-white transition-colors flex items-center gap-2 truncate">Canonical Factory <Zap className="w-3 h-3 text-neutral-600" /></h3>
                                            <p className="text-[10px] text-neutral-500 mt-1 truncate">Capture • Clean • Distill • Publish</p>
                                        </div>
                                        <Badge status="success" />
                                    </div>
                                    <div className="grid grid-cols-2 gap-4 mb-6">
                                        <div className="text-lg md:text-xl font-light text-neutral-200">{facMetrics.successRate}% <span className="text-[10px] text-neutral-600 uppercase block font-semibold">Success</span></div>
                                        <div className="text-lg md:text-xl font-light text-neutral-200">{facMetrics.avgDuration} <span className="text-[10px] text-neutral-600 uppercase block font-semibold">Avg Time</span></div>
                                    </div>
                                    <div className="flex items-end space-x-[2px] h-10">
                                        {factoryRuns.slice(0, 32).reverse().map((run: any) => (
                                            <div key={run.id} className={`flex-1 rounded-t-sm transition-all origin-bottom ${run.status === 'success' ? 'bg-emerald-500/20' : run.status === 'failed' ? 'bg-rose-500/40' : 'bg-blue-500/40 animate-pulse'}`} style={{ height: `${Math.max(20, Math.random() * 80 + 20)}%` }} />
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                );
        }
    };

    const renderDrawerContent = () => {
        if (!activeDrawer) return null;
        const { kind, data: drawerData } = activeDrawer;
        if (kind.startsWith('infra-')) return <InfrastructureInspector type={kind.replace('infra-', '') as any} />;
        if (kind === 'storage-analysis') return <StorageAnalysis artifacts={drawerData || data.artifacts} />;
        if (kind === 'pipeline-metrics') return <PipelineMetrics runs={drawerData || data.runs} />;
        if (kind === 'project-list') return <InfrastructureInspector type="projects" data={data} />;
        if (kind === 'pipeline') return <PipelineInspector pipelineId={drawerData.pipelineId} stages={data.pipelines[drawerData.pipelineId]} initialStage={drawerData.stage?.name} />;
        if (kind === 'stack') return <StackInspector stack={drawerData} onSelectArtifact={(art) => pushOverlay({ type: 'drawer', kind: 'artifact', data: art, breadcrumb: `Stack: ${drawerData.sample.atomClass}` })} />;
        if (kind === 'stack-list') return <StackListInspector artifacts={drawerData} onSelectStack={(stack) => pushOverlay({ type: 'drawer', kind: 'stack', data: stack, breadcrumb: 'Stack List' })} />;
        if (kind === 'artifact') return <ArtifactInspector artifact={drawerData} onUpdate={handleArtifactUpdate} />;
        if (kind === 'run') return <RunInspector run={drawerData} pipelineConfig={data.pipelines[drawerData.pipelineId]} />;
        if (kind === 'alert') return <AlertInspector alert={drawerData} />;
        return <div className="p-6">Unknown Content</div>;
    };

    return (
        <div className="flex h-screen w-full overflow-hidden bg-neutral-950 text-neutral-400 font-sans selection:bg-neutral-800 selection:text-white" onClick={handleCanvasClick} onContextMenu={(e) => { e.preventDefault(); setContextMenu(null); }}>
            <ToastContainer toasts={toasts} onDismiss={id => setToasts(prev => prev.filter(t => t.id !== id))} />
            <CommandPalette open={commandPaletteOpen} onClose={() => setCommandPaletteOpen(false)} actions={commandActions} />
            <ContextMenu request={contextMenu} items={getContextMenuItems()} onClose={() => setContextMenu(null)} />
            <KeyboardShortcuts open={shortcutsOpen} onClose={() => setShortcutsOpen(false)} />

            {/* Desktop Sidebar */}
            <div className={`hidden lg:flex flex-col border-r border-neutral-900 bg-neutral-950 transition-all duration-300 ease-in-out ${leftSidebarCollapsed ? 'w-16' : 'w-64'}`}>
                <div className="flex-1 flex flex-col min-h-0">
                     <div className={`h-14 flex items-center border-b border-neutral-900 ${leftSidebarCollapsed ? 'justify-center px-0' : 'justify-between px-3'}`}>
                        {leftSidebarCollapsed ? (
                             <button onClick={() => setLeftSidebarCollapsed(false)} className="p-2 rounded-md text-neutral-500 hover:text-neutral-200 hover:bg-neutral-900 transition-colors"><PanelLeftOpen className="w-5 h-5" /></button>
                        ) : (
                            <>
                                <div className="flex items-center pl-2 truncate">
                                    <div className="w-3 h-3 rounded-full bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.4)] shrink-0" />
                                    <span className="ml-3 text-sm font-semibold tracking-tight text-neutral-200 truncate">Cloud Refinery</span>
                                </div>
                                <button onClick={() => setLeftSidebarCollapsed(true)} className="p-1.5 rounded-md text-neutral-600 hover:text-neutral-300 hover:bg-neutral-900 transition-colors"><PanelLeftClose className="w-4 h-4" /></button>
                            </>
                        )}
                    </div>
                    <nav className="p-2 space-y-1 mt-2">
                        {NAV_ITEMS.map(item => (
                            <div key={item.id} onClick={() => handleNavigate(item.id as ViewType)} className={`flex items-center px-3 py-2 rounded cursor-pointer text-sm transition-all ${view === item.id ? 'text-neutral-100 bg-neutral-900' : 'text-neutral-500 hover:text-neutral-300 hover:bg-neutral-900/50'} ${leftSidebarCollapsed ? 'justify-center' : ''}`}>
                                <item.icon className={`w-4 h-4 opacity-70 ${!leftSidebarCollapsed ? 'mr-3' : ''}`} />
                                {!leftSidebarCollapsed && item.label}
                            </div>
                        ))}
                    </nav>
                </div>
            </div>

            {/* Mobile Menu */}
            {mobileMenuOpen && (
                 <div className="lg:hidden absolute inset-0 z-[100] bg-black/60 backdrop-blur-sm" onClick={() => setMobileMenuOpen(false)}>
                    <div className="w-64 h-full bg-neutral-950 border-r border-neutral-900 flex flex-col shadow-2xl animate-in slide-in-from-left duration-300" onClick={e => e.stopPropagation()}>
                        <div className="h-14 flex items-center justify-between px-6 border-b border-neutral-900">
                             <span className="text-sm font-semibold tracking-tight text-neutral-200">Cloud Refinery</span>
                             <button onClick={() => setMobileMenuOpen(false)} className="text-neutral-400"><X className="w-6 h-6" /></button>
                        </div>
                        <nav className="p-4 space-y-2 flex-1">
                             {NAV_ITEMS.map(item => (
                                <div key={item.id} onClick={() => handleNavigate(item.id as ViewType)} className={`flex items-center px-4 py-3 rounded cursor-pointer text-base transition-all ${view === item.id ? 'text-neutral-100 bg-neutral-900' : 'text-neutral-500 hover:text-neutral-300 hover:bg-neutral-900/50'}`}>
                                    <item.icon className="w-5 h-5 mr-3 opacity-70" /> {item.label}
                                </div>
                            ))}
                        </nav>
                    </div>
                </div>
            )}

            <div className="flex-1 flex flex-col min-w-0">
                 <div className="h-14 flex items-center justify-between px-4 md:px-6 border-b border-neutral-900 bg-neutral-950/95 backdrop-blur z-40">
                    <div className="flex items-center w-full md:w-1/2">
                        <button className="lg:hidden mr-4 text-neutral-400 hover:text-white" onClick={() => setMobileMenuOpen(true)}><Menu className="w-5 h-5" /></button>
                        <button onClick={handleBack} disabled={!canGoBack} className={`mr-2 md:mr-4 p-1 -ml-2 rounded-full transition-all duration-200 block ${canGoBack ? 'text-neutral-500 hover:bg-neutral-800 hover:text-neutral-200 opacity-100 cursor-pointer' : 'text-neutral-800 opacity-0 cursor-default'}`}><ArrowLeft className="w-4 h-4" /></button>
                        <div className="relative w-full max-w-sm group">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-600 group-focus-within:text-neutral-400 transition-colors" />
                            <input type="text" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} onKeyDown={(e) => { if (e.key === 'Enter' && searchQuery.trim().length > 0) handleNavigate('search'); }} placeholder="Search..." className="w-full bg-transparent border-none focus:ring-0 pl-10 text-xs md:text-sm text-neutral-300 placeholder-neutral-700 h-9" />
                        </div>
                    </div>
                    <div className="flex items-center space-x-4">
                        <button onClick={() => setCommandPaletteOpen(true)} className="hidden lg:flex items-center px-2 py-1 bg-neutral-900 hover:bg-neutral-800 border border-neutral-800 rounded text-xs text-neutral-500 font-mono transition-colors"><Command className="w-3 h-3 mr-1.5" /><span className="mr-1">Cmd+K</span></button>
                    </div>
                </div>

                <div className="flex-1 flex overflow-hidden relative">
                    <main className="flex-1 relative overflow-hidden flex flex-col min-w-0 bg-neutral-950 transition-all duration-300">
                        {renderMainContent()}
                    </main>

                    {/* Floating Bulk Actions Bar */}
                    {selectedArtifactIds.size > 0 && (
                        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 z-50 flex items-center bg-neutral-900/95 border border-neutral-800 shadow-2xl rounded-full px-4 py-2 space-x-4 backdrop-blur-lg animate-in slide-in-from-bottom-6 duration-300">
                            <div className="text-sm font-semibold text-neutral-200 flex items-center">
                                <span className="bg-neutral-800 text-neutral-400 text-xs px-2 py-0.5 rounded-full mr-2">{selectedArtifactIds.size}</span>
                                Selected
                            </div>
                            <div className="h-4 w-px bg-neutral-700" />
                            <div className="flex space-x-1">
                                <button onClick={() => handleBulkAction('vault')} className="p-2 hover:bg-neutral-800 rounded-full text-emerald-500 transition-colors" title="Vault Selected">
                                    <Lock className="w-4 h-4" />
                                </button>
                                <button onClick={() => handleBulkAction('unvault')} className="p-2 hover:bg-neutral-800 rounded-full text-neutral-400 hover:text-white transition-colors" title="Unvault Selected">
                                    <Unlock className="w-4 h-4" />
                                </button>
                                <button onClick={() => handleBulkAction('delete')} className="p-2 hover:bg-neutral-800 rounded-full text-neutral-400 hover:text-rose-500 transition-colors" title="Delete Selected">
                                    <Trash2 className="w-4 h-4" />
                                </button>
                            </div>
                            <div className="h-4 w-px bg-neutral-700" />
                            <button onClick={clearSelection} className="p-1 hover:bg-neutral-800 rounded-full text-neutral-500 hover:text-white transition-colors">
                                <X className="w-4 h-4" />
                            </button>
                        </div>
                    )}

                    {activeDrawer && <div className="lg:hidden absolute inset-0 z-40 bg-black/60 backdrop-blur-[1px]" onClick={handleBack} />}

                    <div className={`
                        bg-neutral-925 flex flex-col z-50 transition-all duration-300 ease-[cubic-bezier(0.16,1,0.3,1)] absolute inset-y-0 right-0 w-full md:w-[92vw] lg:max-w-[560px] border-l border-neutral-900 shadow-2xl
                        ${activeDrawer ? 'translate-x-0' : 'translate-x-full'}
                        lg:static lg:h-auto lg:translate-x-0 lg:shadow-none lg:w-auto
                        ${activeDrawer ? (sidebarExpanded ? 'lg:w-2/3' : 'lg:w-1/3') : 'lg:w-0'}
                        ${activeDrawer ? 'lg:border-l' : 'lg:border-l-0'}
                    `} onClick={e => e.stopPropagation()}>
                        {activeDrawer && (
                            <>
                                <div className="h-10 border-b border-neutral-800 flex items-center justify-between px-4 bg-neutral-900/50 flex-shrink-0">
                                    <div className="flex items-center space-x-2 overflow-hidden mr-2">
                                        <button onClick={() => setSidebarExpanded(!sidebarExpanded)} className="hidden lg:block p-1 hover:bg-neutral-800 rounded text-neutral-500 hover:text-neutral-300 transition-colors mr-2 flex-shrink-0">{sidebarExpanded ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}</button>
                                        <div className="flex items-center text-[10px] font-mono uppercase tracking-tight overflow-hidden text-neutral-500 mask-linear-fade">
                                            <button onClick={closeAllDrawers} className="hover:text-neutral-300 transition-colors whitespace-nowrap flex-shrink-0 flex items-center truncate max-w-[80px]">{drawerStack[0]?.breadcrumb || 'Home'}</button>
                                            {drawerStack.slice(-2).map((item, idx) => (
                                                <React.Fragment key={item.id}>
                                                     <span className="mx-2 text-neutral-800 flex-shrink-0">/</span>
                                                     <button onClick={() => handleBreadcrumbClick(item.id)} className={`whitespace-nowrap flex-shrink-0 transition-colors max-w-[100px] truncate ${idx === 1 ? 'text-neutral-300 font-semibold cursor-default' : 'hover:text-neutral-300'}`} disabled={idx === 1} title={getOverlayTitle(item)}>{getOverlayTitle(item)}</button>
                                                </React.Fragment>
                                            ))}
                                        </div>
                                    </div>
                                    <button onClick={handleBack} className="text-[10px] uppercase tracking-wider text-neutral-600 hover:text-neutral-400 font-semibold px-2 py-1 flex-shrink-0">Close</button>
                                </div>
                                <div className="flex-1 overflow-hidden relative">
                                    {renderDrawerContent()}
                                </div>
                            </>
                        )}
                    </div>
                </div>

                {activeModal && (
                    <div className="fixed inset-0 z-[200] flex items-center justify-center bg-black/60 backdrop-blur-[2px]" onClick={handleBack}>
                        <div className="bg-neutral-900 border border-neutral-800 p-6 md:p-8 rounded-lg shadow-2xl max-w-lg w-full m-4 animate-in zoom-in-95 duration-200" onClick={e => e.stopPropagation()}>
                            <h3 className="text-lg font-medium text-neutral-200 mb-4">Activity Log</h3>
                            <div className="space-y-4 text-sm text-neutral-400">
                                <p>Updates since your last session:</p>
                                <ul className="list-disc pl-5 space-y-2">
                                    <li>{activeModal.data.newRuns} pipeline runs processed.</li>
                                    <li>{activeModal.data.newAlerts} system alerts generated.</li>
                                </ul>
                                <div className="pt-4 flex justify-end">
                                    <button onClick={handleBack} className="px-5 py-2 bg-neutral-800 hover:bg-neutral-700 text-neutral-200 rounded text-sm transition-colors">Dismiss</button>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
