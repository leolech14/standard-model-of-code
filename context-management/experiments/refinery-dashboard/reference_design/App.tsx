import React, { useState, useEffect, useRef } from 'react';
import { 
    LayoutDashboard, Activity, Box, Database, 
    List, AlertTriangle, Settings, Search, 
    ChevronLeft, ChevronRight, CheckCircle2,
    ArrowLeft, Menu, X, PanelLeftClose, PanelLeftOpen
} from 'lucide-react';
import { repository, PIPELINE_CONFIGS } from './services/mockData';
import { OverlayItem, ViewType, AppState, PipelineId, Artifact, AppSettings, PipelineStageConfig } from './types';
import { UiLink, UiRow, Badge, SectionHeader, EmptyState } from './components/Common';
import { PipelineInspector } from './components/PipelineInspector';
import { ArtifactInspector, RunInspector, AlertInspector } from './components/Inspectors';
import { InventoryGrid, StackInspector, StackListInspector, ArtifactStack } from './components/Inventory';
import { RunsTimeline } from './components/Timeline';

// --- MAIN APP ---

const NAV_ITEMS = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'pipelines', label: 'Pipelines', icon: Activity },
    { id: 'inventory', label: 'Inventory', icon: Box },
    { id: 'vault', label: 'Vault', icon: Database },
    { id: 'runs', label: 'Runs', icon: List },
    { id: 'alerts', label: 'Alerts', icon: AlertTriangle },
    { id: 'settings', label: 'Settings', icon: Settings },
];

export default function App() {
    const [view, setView] = useState<ViewType>('overview');
    const [viewStack, setViewStack] = useState<ViewType[]>([]);
    
    const [data, setData] = useState<any>(null);
    const [appState, setAppState] = useState<AppState | null>(null);
    const [overlayStack, setOverlayStack] = useState<OverlayItem[]>([]);
    
    // UI State
    const [sidebarExpanded, setSidebarExpanded] = useState(false); // Right sidebar expansion (Super Sidebar)
    const [leftSidebarCollapsed, setLeftSidebarCollapsed] = useState(false); // Desktop left sidebar (Rail mode)
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false); // Mobile left sidebar (Overlay)
    
    const [lastVisitStats, setLastVisitStats] = useState<any>(null);
    const [pipelineTab, setPipelineTab] = useState<PipelineId>(PipelineId.Refinery);
    const [pipelineSubTab, setPipelineSubTab] = useState<'Map' | 'Stream'>('Map');
    const [searchQuery, setSearchQuery] = useState('');

    // Focus Management Refs
    const previousFocusStack = useRef<HTMLElement[]>([]);

    // Load Data
    useEffect(() => {
        const d = repository.getData();
        const state = repository.getAppState();
        
        setData(d);
        setAppState(state);

        // While you were away logic
        const now = Date.now();
        const diff = now - state.lastVisit;
        if (diff > 5000) { 
            const newRuns = d.runs.filter((r: any) => r.startTime > state.lastVisit).length;
            const newAlerts = d.alerts.filter((a: any) => a.timestamp > state.lastVisit).length;
            if (newRuns > 0 || newAlerts > 0) {
                setLastVisitStats({ newRuns, newAlerts });
            }
        }
        
        repository.setAppState({ ...state, lastVisit: now });
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    // Global Key Handlers (ESC)
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.key === 'Escape') {
                handleBack();
            }
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [overlayStack, viewStack, mobileMenuOpen]);

    // Data Actions
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
    };

    const handleSettingChange = (key: keyof AppSettings, value: any) => {
        if (!appState) return;
        const newSettings = { ...appState.settings, [key]: value };
        const newState = { ...appState, settings: newSettings };
        setAppState(newState);
        repository.setAppState(newState);
    };

    const downloadJson = (filename: string, content: any) => {
        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(content, null, 2));
        const downloadAnchorNode = document.createElement('a');
        downloadAnchorNode.setAttribute("href", dataStr);
        downloadAnchorNode.setAttribute("download", filename + ".json");
        document.body.appendChild(downloadAnchorNode);
        downloadAnchorNode.click();
        downloadAnchorNode.remove();
    };

    const handleNavigate = (newView: ViewType) => {
        if (view === newView) {
            setMobileMenuOpen(false);
            return;
        }
        setViewStack(prev => [...prev, view]);
        setView(newView);
        setMobileMenuOpen(false); 
    };

    const navigateToPipeline = (id: PipelineId) => {
        setViewStack(prev => [...prev, view]);
        setView('pipelines');
        setPipelineTab(id);
    };

    const activeDrawer = overlayStack.filter(i => i.type === 'drawer').at(-1);
    const activeModal = overlayStack.filter(i => i.type === 'modal').at(-1);
    const canGoBack = overlayStack.length > 0 || viewStack.length > 0;

    // --- CLOSING LOGIC (Layered Dismissal) ---
    const handleBack = () => {
        // 1. Close Modal (Topmost)
        if (activeModal) {
            setOverlayStack(prev => prev.filter(i => i.id !== activeModal.id));
            return;
        }
        // 2. Close Right Drawer
        if (activeDrawer) {
            setOverlayStack(prev => prev.filter(i => i.id !== activeDrawer.id));
            const prevFocus = previousFocusStack.current.pop();
            if (prevFocus) prevFocus.focus();
            return;
        }
        // 3. Close Mobile Menu
        if (mobileMenuOpen) {
            setMobileMenuOpen(false);
            return;
        }
        // 4. Pop Navigation History
        if (viewStack.length > 0) {
            const prevView = viewStack[viewStack.length - 1];
            setViewStack(prev => prev.slice(0, -1));
            setView(prevView);
            return;
        }
    };

    // Click outside handler for docked right sidebar
    const handleCanvasClick = (e: React.MouseEvent) => {
        // If drawer is open and we click the main canvas (backdrop), close it.
        // This is acceptable behavior even for docked mode as per requirements.
        if (activeDrawer) {
            handleBack();
        }
    };

    const pushOverlay = (item: Omit<OverlayItem, 'id'>) => {
        if (document.activeElement instanceof HTMLElement) {
            previousFocusStack.current.push(document.activeElement);
        }
        const newItem = { ...item, id: Math.random().toString(36) };
        setOverlayStack(prev => [...prev, newItem]);
    };

    // --- FILTERS & DATA FETCHING ---
    const getFilteredArtifacts = () => {
        if (!data) return [];
        let res = data.artifacts;
        if (view === 'pipelines') res = res.filter((a: any) => a.pipelineId === pipelineTab);
        if (view === 'vault') res = res.filter((a: any) => a.isVaulted);
        
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
            case 'pipelines':
                return (
                    <div className="h-full flex flex-col animate-in fade-in duration-300">
                        <div className="flex items-center px-4 md:px-8 border-b border-neutral-900 overflow-x-auto hide-scrollbar">
                            {[PipelineId.Refinery, PipelineId.Factory].map(pid => (
                                <button 
                                    key={pid}
                                    onClick={() => setPipelineTab(pid)}
                                    className={`py-4 px-6 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${pipelineTab === pid ? 'border-neutral-500 text-neutral-200' : 'border-transparent text-neutral-600 hover:text-neutral-400'}`}
                                >
                                    {pid}
                                </button>
                            ))}
                        </div>
                        <div className="flex-1 p-4 md:p-8 overflow-y-auto">
                            <div className="flex space-x-4 mb-6">
                                <UiLink active={pipelineSubTab === 'Map'} onClick={() => setPipelineSubTab('Map')}>Map</UiLink>
                                <UiLink active={pipelineSubTab === 'Stream'} onClick={() => setPipelineSubTab('Stream')}>Stream</UiLink>
                            </div>
                            
                            {pipelineSubTab === 'Map' ? (
                                <div className="max-w-2xl">
                                    <h3 className="text-xs uppercase text-neutral-500 font-semibold mb-4">Pipeline Topology</h3>
                                    <div className="space-y-2">
                                        {PIPELINE_CONFIGS[pipelineTab].map((stage) => (
                                            <UiRow 
                                                key={stage.name} 
                                                onClick={() => pushOverlay({ 
                                                    type: 'drawer', 
                                                    kind: 'pipeline', 
                                                    data: { stage, pipelineId: pipelineTab }, 
                                                    breadcrumb: `Pipelines › ${pipelineTab}`
                                                })}
                                            >
                                                <div className="flex items-center w-full">
                                                    <div className={`w-2 h-2 rounded-full mr-4 ${stage.status === 'success' ? 'bg-emerald-500' : 'bg-neutral-600'}`} />
                                                    <span className="flex-1 text-sm text-neutral-300 font-medium">{stage.name}</span>
                                                    <span className="text-xs text-neutral-600 font-mono">{stage.queueDepth} queued</span>
                                                </div>
                                            </UiRow>
                                        ))}
                                    </div>
                                </div>
                            ) : (
                                <div>
                                    <div className="flex items-end justify-between mb-4">
                                        <h3 className="text-xs uppercase text-neutral-500 font-semibold">Live Stacks</h3>
                                    </div>
                                    <div className="mb-8">
                                        <InventoryGrid 
                                            artifacts={getFilteredArtifacts()} 
                                            onSelectStack={(stack) => pushOverlay({ type: 'drawer', kind: 'stack', data: stack, breadcrumb: 'Pipelines › Stream' })}
                                            onViewAll={() => pushOverlay({ type: 'drawer', kind: 'stack-list', data: getFilteredArtifacts(), breadcrumb: 'Pipelines' })}
                                        />
                                    </div>
                                    
                                    <h3 className="text-xs uppercase text-neutral-500 font-semibold mb-4">Live Artifact Stream</h3>
                                    {getFilteredArtifacts().slice(0, 20).map((art: any) => (
                                        <UiRow key={art.id} onClick={() => pushOverlay({ type: 'drawer', kind: 'artifact', data: art, breadcrumb: 'Pipelines › Stream' })}>
                                             <div className="grid grid-cols-12 gap-4 w-full text-sm">
                                                <span className="col-span-3 md:col-span-2 text-neutral-500 font-mono text-xs truncate">{art.stage}</span>
                                                <span className="col-span-6 md:col-span-6 text-neutral-300 truncate">{art.name}</span>
                                                <span className="col-span-3 md:col-span-2 text-neutral-600 text-xs text-right md:text-left">{art.type}</span>
                                                <span className="hidden md:block col-span-2 text-right text-neutral-600 font-mono text-xs">{art.size}</span>
                                             </div>
                                        </UiRow>
                                    ))}
                                    {getFilteredArtifacts().length === 0 && <EmptyState message="No artifacts match your filter" submessage="Try adjusting your search query." />}
                                </div>
                            )}
                        </div>
                    </div>
                );
            case 'inventory':
                return (
                    <div className="p-4 md:p-8 h-full overflow-y-auto animate-in fade-in duration-300">
                        <SectionHeader title="Global Inventory" action={<UiLink onClick={() => downloadJson('inventory_export', getFilteredArtifacts())}>Export JSON</UiLink>} />
                        
                        <div className="mb-8">
                            <h4 className="text-xs text-neutral-600 uppercase mb-3 px-1">Top Stacks</h4>
                            <InventoryGrid 
                                artifacts={getFilteredArtifacts()} 
                                onSelectStack={(stack) => pushOverlay({ type: 'drawer', kind: 'stack', data: stack, breadcrumb: 'Inventory' })}
                                onViewAll={() => pushOverlay({ type: 'drawer', kind: 'stack-list', data: getFilteredArtifacts(), breadcrumb: 'Inventory' })}
                                className="max-w-md"
                            />
                        </div>

                        <div className="mt-4 space-y-1">
                             <div className="hidden md:grid grid-cols-12 gap-4 px-3 py-2 text-xs font-semibold text-neutral-600 uppercase tracking-wider">
                                <span className="col-span-4">Name</span>
                                <span className="col-span-3">Pipeline</span>
                                <span className="col-span-2">Stage</span>
                                <span className="col-span-1">Type</span>
                                <span className="col-span-2 text-right">Updated</span>
                            </div>
                            {getFilteredArtifacts().map((art: any) => (
                                <UiRow key={art.id} onClick={() => pushOverlay({ type: 'drawer', kind: 'artifact', data: art, breadcrumb: 'Inventory' })}>
                                    <div className="grid grid-cols-1 md:grid-cols-12 gap-1 md:gap-4 w-full text-sm items-center">
                                        <div className="col-span-1 md:col-span-4 text-neutral-300 truncate font-mono text-xs flex justify-between">
                                            <span>{art.name}</span>
                                            <span className="md:hidden text-neutral-600">{art.type}</span>
                                        </div>
                                        <span className="hidden md:block col-span-3 text-neutral-500 text-xs truncate">{art.pipelineId.split(' ')[0]}</span>
                                        <span className="col-span-1 md:col-span-2 text-neutral-500 text-xs flex items-center">
                                            <span className="md:hidden w-1.5 h-1.5 bg-neutral-600 rounded-full mr-2"></span>
                                            {art.stage}
                                        </span>
                                        <span className="hidden md:block col-span-1 text-neutral-600 text-xs">{art.type}</span>
                                        <span className="hidden md:block col-span-2 text-right text-neutral-600 text-xs">{(Date.now() - art.updatedAt) < 3600000 ? 'Just now' : 'Older'}</span>
                                    </div>
                                </UiRow>
                            ))}
                             {getFilteredArtifacts().length === 0 && <EmptyState message="Inventory empty" submessage="No items match your current filter." />}
                        </div>
                    </div>
                );
            case 'runs':
                return (
                    <div className="p-4 md:p-8 h-full overflow-y-auto animate-in fade-in duration-300">
                        <SectionHeader title="Execution History" />
                        
                        {/* Interactive Gantt Timeline */}
                        <RunsTimeline runs={getFilteredRuns()} onSelect={(run) => pushOverlay({ type: 'drawer', kind: 'run', data: run, breadcrumb: 'Runs' })} />

                        <div className="mt-4 space-y-1">
                            {getFilteredRuns().map((run: any) => (
                                <UiRow key={run.id} onClick={() => pushOverlay({ type: 'drawer', kind: 'run', data: run, breadcrumb: 'Runs' })}>
                                     <div className="flex flex-col md:flex-row md:items-center justify-between w-full text-sm">
                                        <div className="flex items-center space-x-3 mb-1 md:mb-0">
                                            <Badge status={run.status} />
                                            <span className="font-mono text-neutral-400 text-xs">{run.id}</span>
                                            <span className="text-neutral-300 truncate">{run.pipelineId}</span>
                                        </div>
                                        <div className="flex items-center space-x-6 text-xs text-neutral-500 font-mono pl-6 md:pl-0">
                                            <span>{run.duration}</span>
                                            <span>{run.triggeredBy}</span>
                                        </div>
                                     </div>
                                </UiRow>
                            ))}
                             {getFilteredRuns().length === 0 && <EmptyState message="No runs found" submessage="Adjust filters or check pipeline health." />}
                        </div>
                    </div>
                );
             case 'alerts':
                return (
                    <div className="p-4 md:p-8 h-full overflow-y-auto animate-in fade-in duration-300">
                        <SectionHeader title="System Alerts" />
                        <div className="mt-4 space-y-1">
                            {getFilteredAlerts().map((alert: any) => (
                                <UiRow key={alert.id} onClick={() => pushOverlay({ type: 'drawer', kind: 'alert', data: alert, breadcrumb: 'Alerts' })}>
                                     <div className="flex items-center justify-between w-full text-sm">
                                        <div className="flex items-center space-x-3">
                                            <AlertTriangle className={`w-4 h-4 flex-shrink-0 ${alert.severity === 'critical' ? 'text-rose-500' : 'text-amber-500'}`} />
                                            <span className="text-neutral-300 truncate max-w-xs md:max-w-md">{alert.message}</span>
                                        </div>
                                        <span className="text-xs text-neutral-600 flex-shrink-0 ml-2">{new Date(alert.timestamp).toLocaleTimeString()}</span>
                                     </div>
                                </UiRow>
                            ))}
                             {getFilteredAlerts().length === 0 && <EmptyState message="No active alerts" submessage="System is operating normally." />}
                        </div>
                    </div>
                );
             case 'vault':
                return (
                     <div className="p-4 md:p-8 h-full overflow-y-auto animate-in fade-in duration-300">
                        <SectionHeader title="The Vault" action={<UiLink onClick={() => downloadJson('vault_bundle', getFilteredArtifacts())}>Export Bundle</UiLink>} />
                        <p className="text-sm text-neutral-600 mb-6 max-w-lg">
                            Secure, immutable storage for high-value refined artifacts. Items here are pinned and replicated across 3 zones.
                        </p>
                         <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                            {getFilteredArtifacts().map((art: any) => (
                                <div key={art.id} onClick={() => pushOverlay({ type: 'drawer', kind: 'artifact', data: art, breadcrumb: 'Vault' })} className="p-4 border border-neutral-800 rounded bg-neutral-900/20 hover:bg-neutral-900/50 cursor-pointer transition-colors group">
                                    <div className="flex justify-between items-start mb-2">
                                        <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                                        <span className="text-[10px] text-neutral-600 font-mono uppercase">{art.type}</span>
                                    </div>
                                    <div className="font-mono text-xs text-neutral-300 truncate mb-1">{art.name}</div>
                                    <div className="text-[10px] text-neutral-500">{art.size}</div>
                                </div>
                            ))}
                         </div>
                         {getFilteredArtifacts().length === 0 && <EmptyState message="Vault is empty" submessage="Pin artifacts from the inventory to see them here." />}
                     </div>
                );
             case 'settings':
                return (
                    <div className="p-4 md:p-8 h-full overflow-y-auto max-w-3xl animate-in fade-in duration-300">
                        <SectionHeader title="Console Settings" />
                        <div className="space-y-8 mt-6">
                            <div className="space-y-4">
                                <h4 className="text-sm text-neutral-200 font-medium">Data Source</h4>
                                <div className="flex flex-col md:flex-row items-start md:items-center space-y-4 md:space-y-0 md:space-x-4 p-4 border border-neutral-800 rounded bg-neutral-900/30">
                                    <div className="flex-1">
                                        <div className="text-sm text-neutral-300">Operation Mode</div>
                                        <div className="text-xs text-neutral-500">
                                            {appState?.settings?.apiBaseUrl ? `API: ${appState.settings.apiBaseUrl}` : 'Using in-memory mock repository.'}
                                        </div>
                                    </div>
                                    <div className="flex bg-neutral-950 rounded p-1 border border-neutral-800">
                                        <button className="px-3 py-1 text-xs text-neutral-200 bg-neutral-800 rounded shadow-sm">Mock</button>
                                        <button className="px-3 py-1 text-xs text-neutral-600" disabled>API</button>
                                    </div>
                                </div>
                            </div>
                            
                            <div className="space-y-4">
                                <h4 className="text-sm text-neutral-200 font-medium">Configuration</h4>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div className="p-4 border border-neutral-800 rounded bg-neutral-900/20">
                                        <label className="block text-xs text-neutral-500 mb-2">Poll Interval (ms)</label>
                                        <input 
                                            type="number" 
                                            className="w-full bg-neutral-900 border border-neutral-700 rounded px-2 py-1 text-sm text-neutral-200 focus:border-neutral-500 outline-none"
                                            value={appState?.settings?.pollInterval || 5000}
                                            onChange={(e) => handleSettingChange('pollInterval', parseInt(e.target.value))}
                                        />
                                    </div>
                                    <div className="p-4 border border-neutral-800 rounded bg-neutral-900/20">
                                        <label className="block text-xs text-neutral-500 mb-2">API Base URL</label>
                                        <input 
                                            type="text" 
                                            className="w-full bg-neutral-900 border border-neutral-700 rounded px-2 py-1 text-sm text-neutral-200 focus:border-neutral-500 outline-none"
                                            value={appState?.settings?.apiBaseUrl || ''}
                                            placeholder="https://api.internal..."
                                            onChange={(e) => handleSettingChange('apiBaseUrl', e.target.value)}
                                        />
                                    </div>
                                    <div className="p-4 border border-neutral-800 rounded bg-neutral-900/20 flex items-center justify-between">
                                        <span className="text-sm text-neutral-400">Notifications</span>
                                        <div 
                                            className={`w-10 h-5 rounded-full relative transition-colors cursor-pointer ${appState?.settings?.showNotifications ? 'bg-emerald-600' : 'bg-neutral-700'}`}
                                            onClick={() => handleSettingChange('showNotifications', !appState?.settings?.showNotifications)}
                                        >
                                            <div className={`absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full transition-transform ${appState?.settings?.showNotifications ? 'translate-x-5' : ''}`} />
                                        </div>
                                    </div>
                                    <div className="p-4 border border-neutral-800 rounded bg-neutral-900/20 flex items-center justify-between">
                                        <span className="text-sm text-neutral-400">Auto-Pin Verified</span>
                                        <div 
                                            className={`w-10 h-5 rounded-full relative transition-colors cursor-pointer ${appState?.settings?.autoPin ? 'bg-emerald-600' : 'bg-neutral-700'}`}
                                            onClick={() => handleSettingChange('autoPin', !appState?.settings?.autoPin)}
                                        >
                                            <div className={`absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full transition-transform ${appState?.settings?.autoPin ? 'translate-x-5' : ''}`} />
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="space-y-4">
                                <h4 className="text-sm text-neutral-200 font-medium">Session</h4>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                     <button className="p-3 border border-neutral-800 rounded text-xs text-neutral-400 hover:bg-neutral-900 text-left" onClick={() => { repository.reset(); }}>
                                         Reset Local Cache
                                     </button>
                                     <button onClick={() => downloadJson('refinery_diagnostic', data)} className="p-3 border border-neutral-800 rounded text-xs text-neutral-400 hover:bg-neutral-900 text-left">
                                         Export Diagnostic JSON
                                     </button>
                                </div>
                            </div>
                        </div>
                    </div>
                )
            default: // Overview
                return (
                    <div className="p-4 md:p-8 h-full overflow-y-auto animate-in fade-in duration-300">
                        <div className="flex items-center justify-between mb-8">
                            <div>
                                <h1 className="text-2xl font-light text-neutral-100 mb-1">Overview</h1>
                                <p className="text-sm text-neutral-500">System metrics and active pipeline health.</p>
                            </div>
                            <div className="text-right hidden md:block">
                                <div className="text-xs text-neutral-600 uppercase tracking-wider mb-1">Queue Depth</div>
                                <div className="text-xl font-mono text-neutral-300">557 <span className="text-sm text-neutral-600">items</span></div>
                            </div>
                        </div>

                        {lastVisitStats && (
                            <div onClick={() => pushOverlay({ type: 'modal', kind: 'log', data: lastVisitStats })} className="mb-8 p-3 border border-neutral-800 bg-neutral-925 rounded flex items-center justify-between cursor-pointer hover:border-neutral-700 transition-colors">
                                <span className="text-sm text-neutral-400">
                                    Since your last visit: <span className="text-white">{lastVisitStats.newRuns} new runs</span>, <span className="text-white">{lastVisitStats.newAlerts} alerts</span>.
                                </span>
                                <span className="text-xs text-neutral-500">View Log &rarr;</span>
                            </div>
                        )}

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div 
                                onClick={() => pushOverlay({ 
                                    type: 'drawer', 
                                    kind: 'pipeline', 
                                    data: { pipelineId: PipelineId.Refinery },
                                    breadcrumb: 'Overview'
                                })}
                                className="p-5 border border-neutral-800 rounded bg-neutral-900/10 cursor-pointer hover:border-neutral-600 hover:bg-neutral-900/30 transition-all group"
                            >
                                <div className="flex justify-between items-center mb-4">
                                    <h3 className="text-sm font-medium text-neutral-300 group-hover:text-white transition-colors">Cloud Refinery</h3>
                                    <Badge status="running" />
                                </div>
                                <div className="h-32 flex items-end justify-between space-x-1">
                                    {Array.from({length: 20}).map((_, i) => (
                                        <div key={i} style={{height: `${Math.random() * 100}%`}} className="w-full bg-neutral-800 rounded-t-sm opacity-60 group-hover:opacity-80 transition-opacity" />
                                    ))}
                                </div>
                                <div className="mt-3 flex justify-between text-xs text-neutral-600 font-mono">
                                    <span>Throughput</span>
                                    <span>24h</span>
                                </div>
                            </div>

                             <div 
                                onClick={() => pushOverlay({ 
                                    type: 'drawer', 
                                    kind: 'pipeline', 
                                    data: { pipelineId: PipelineId.Factory },
                                    breadcrumb: 'Overview'
                                })}
                                className="p-5 border border-neutral-800 rounded bg-neutral-900/10 cursor-pointer hover:border-neutral-600 hover:bg-neutral-900/30 transition-all group"
                            >
                                <div className="flex justify-between items-center mb-4">
                                    <h3 className="text-sm font-medium text-neutral-300 group-hover:text-white transition-colors">Canonical Factory</h3>
                                    <Badge status="success" />
                                </div>
                                <div className="h-32 flex items-end justify-between space-x-1">
                                     {Array.from({length: 20}).map((_, i) => (
                                        <div key={i} style={{height: `${Math.random() * 80 + 10}%`}} className="w-full bg-neutral-800 rounded-t-sm opacity-60 group-hover:opacity-80 transition-opacity" />
                                    ))}
                                </div>
                                <div className="mt-3 flex justify-between text-xs text-neutral-600 font-mono">
                                    <span>Throughput</span>
                                    <span>24h</span>
                                </div>
                            </div>
                        </div>

                        <div className="mt-8">
                             <SectionHeader title="Recent Alerts" />
                             {data.alerts.slice(0, 3).map((alert: any) => (
                                <UiRow key={alert.id} onClick={() => pushOverlay({ type: 'drawer', kind: 'alert', data: alert, breadcrumb: 'Overview' })}>
                                    <div className="flex items-center space-x-3 text-sm text-neutral-400">
                                        <AlertTriangle className="w-3 h-3 text-amber-500" />
                                        <span>{alert.message}</span>
                                    </div>
                                </UiRow>
                             ))}
                        </div>
                    </div>
                );
        }
    };

    const renderDrawerContent = () => {
        if (!activeDrawer) return null;
        const { kind, data } = activeDrawer;

        if (kind === 'pipeline') {
             const pipelineId = data.pipelineId || PipelineId.Refinery;
             const initialStage = data.stage?.name;
             
             return (
                <PipelineInspector 
                    pipelineId={pipelineId} 
                    initialStage={initialStage}
                    onStageSelect={(stage) => { /* Selection handled internally for visual cue, no generic action needed yet */ }}
                    onViewArtifacts={(stage) => {
                         // Filter artifacts for this stage and show them in a layered stack list
                         const stageArtifacts = data.artifacts ? data.artifacts : repository.getData().artifacts.filter((a: any) => a.pipelineId === pipelineId && a.stage === stage.name);
                         pushOverlay({ 
                             type: 'drawer', 
                             kind: 'stack-list', 
                             data: stageArtifacts,
                             breadcrumb: `${pipelineId} › ${stage.name}`
                         });
                    }}
                />
             );
        }
        if (kind === 'stack') return <StackInspector stack={data} onSelectArtifact={(art) => pushOverlay({ type: 'drawer', kind: 'artifact', data: art, breadcrumb: `Stack: ${data.sample.atomClass}` })} />;
        if (kind === 'stack-list') return <StackListInspector artifacts={data} onSelectStack={(stack) => pushOverlay({ type: 'drawer', kind: 'stack', data: stack, breadcrumb: 'Stack List' })} />;
        if (kind === 'artifact') return <ArtifactInspector artifact={data} onUpdate={handleArtifactUpdate} />;
        if (kind === 'run') return <RunInspector run={data} />;
        if (kind === 'alert') return <AlertInspector alert={data} />;
        return <div className="p-6">Unknown Content</div>;
    };

    return (
        <div className="flex h-screen w-full overflow-hidden bg-neutral-950 text-neutral-400 font-sans selection:bg-neutral-800 selection:text-white">
            
            {/* DESKTOP LEFT SIDEBAR (Collapsible) */}
            <div 
                className={`hidden lg:flex flex-col border-r border-neutral-900 bg-neutral-950 transition-all duration-300 ease-in-out
                ${leftSidebarCollapsed ? 'w-16' : 'w-64'}
                `}
            >
                <div>
                    <div className={`h-14 flex items-center border-b border-neutral-900 ${leftSidebarCollapsed ? 'justify-center px-0' : 'justify-between px-6'}`}>
                        <div className="flex items-center">
                            <div className="w-3 h-3 rounded-full bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.4)]" />
                            {!leftSidebarCollapsed && <span className="ml-3 text-sm font-semibold tracking-tight text-neutral-200">Cloud Refinery</span>}
                        </div>
                    </div>
                    <nav className="p-2 space-y-1 mt-2">
                        {NAV_ITEMS.map(item => (
                            <div 
                                key={item.id}
                                onClick={() => handleNavigate(item.id as ViewType)}
                                title={leftSidebarCollapsed ? item.label : undefined}
                                className={`
                                    flex items-center px-3 py-2 rounded cursor-pointer text-sm transition-all
                                    ${view === item.id ? 'text-neutral-100 bg-neutral-900' : 'text-neutral-500 hover:text-neutral-300 hover:bg-neutral-900/50'}
                                    ${leftSidebarCollapsed ? 'justify-center' : ''}
                                `}
                            >
                                <item.icon className={`w-4 h-4 opacity-70 ${!leftSidebarCollapsed ? 'mr-3' : ''}`} />
                                {!leftSidebarCollapsed && item.label}
                            </div>
                        ))}
                    </nav>
                </div>
                <div className="p-4 flex justify-center">
                     <button 
                        onClick={() => setLeftSidebarCollapsed(!leftSidebarCollapsed)}
                        className="p-1.5 rounded-md text-neutral-600 hover:text-neutral-300 hover:bg-neutral-900 transition-colors"
                     >
                         {leftSidebarCollapsed ? <PanelLeftOpen className="w-4 h-4" /> : <PanelLeftClose className="w-4 h-4" />}
                     </button>
                </div>
            </div>

            {/* MOBILE SIDEBAR (OFF-CANVAS OVERLAY) */}
            {mobileMenuOpen && (
                <div className="lg:hidden absolute inset-0 z-40 bg-black/60 backdrop-blur-sm" onClick={() => setMobileMenuOpen(false)}>
                    <div className="w-64 h-full bg-neutral-950 border-r border-neutral-900 flex flex-col shadow-2xl" onClick={e => e.stopPropagation()}>
                        <div className="h-14 flex items-center justify-between px-6 border-b border-neutral-900">
                             <div className="flex items-center">
                                <div className="w-3 h-3 rounded-full bg-emerald-500 mr-3 shadow-[0_0_10px_rgba(16,185,129,0.4)]" />
                                <span className="text-sm font-semibold tracking-tight text-neutral-200">Cloud Refinery</span>
                             </div>
                             <button onClick={() => setMobileMenuOpen(false)} className="text-neutral-400">
                                 <X className="w-6 h-6" />
                             </button>
                        </div>
                        <nav className="p-4 space-y-2 flex-1">
                             {NAV_ITEMS.map(item => (
                                <div 
                                    key={item.id}
                                    onClick={() => handleNavigate(item.id as ViewType)}
                                    className={`
                                        flex items-center px-4 py-3 rounded cursor-pointer text-base transition-all
                                        ${view === item.id ? 'text-neutral-100 bg-neutral-900' : 'text-neutral-500 hover:text-neutral-300 hover:bg-neutral-900/50'}
                                    `}
                                >
                                    <item.icon className="w-5 h-5 mr-3 opacity-70" />
                                    {item.label}
                                </div>
                            ))}
                        </nav>
                    </div>
                </div>
            )}

            {/* MAIN AREA */}
            <div className="flex-1 flex flex-col min-w-0">
                {/* TOP BAR */}
                <div className="h-14 flex items-center justify-between px-4 md:px-6 border-b border-neutral-900 bg-neutral-950/95 backdrop-blur z-10">
                    <div className="flex items-center w-full md:w-1/2">
                        {/* Mobile Menu Button */}
                        <button 
                            className="lg:hidden mr-4 text-neutral-400 hover:text-white"
                            onClick={() => setMobileMenuOpen(true)}
                        >
                            <Menu className="w-5 h-5" />
                        </button>

                        <button 
                            onClick={handleBack} 
                            disabled={!canGoBack}
                            className={`
                                mr-4 p-1 -ml-2 rounded-full transition-all duration-200 block
                                ${canGoBack 
                                    ? 'text-neutral-500 hover:bg-neutral-800 hover:text-neutral-200 opacity-100 cursor-pointer' 
                                    : 'text-neutral-800 opacity-0 cursor-default'}
                            `}
                            title="Go Back (Esc)"
                        >
                            <ArrowLeft className="w-4 h-4" />
                        </button>
                        <div className="relative w-full max-w-sm group">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-600 group-focus-within:text-neutral-400 transition-colors" />
                            <input 
                                type="text" 
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                placeholder="Search..." 
                                className="w-full bg-transparent border-none focus:ring-0 pl-10 text-sm text-neutral-300 placeholder-neutral-700 h-9"
                            />
                        </div>
                    </div>
                    <div className="flex items-center space-x-4 hidden md:flex">
                        {lastVisitStats && <UiLink onClick={() => pushOverlay({ type: 'modal', kind: 'log', data: lastVisitStats })} className="hidden md:inline-flex">While you were away...</UiLink>}
                        <div className="w-2 h-2 rounded-full bg-emerald-500/50" title="System Online" />
                    </div>
                </div>

                {/* CONTENT WRAPPER (Horizontal Flex for Docked Layout) */}
                <div className="flex-1 flex overflow-hidden relative">
                    {/* CANVAS */}
                    <main 
                        className="flex-1 relative overflow-hidden flex flex-col min-w-0 bg-neutral-950 transition-all duration-300" 
                        onClick={handleCanvasClick} // Click outside handler
                    >
                        {renderMainContent()}
                    </main>

                    {/* Mobile Drawer Backdrop */}
                    {activeDrawer && (
                        <div className="lg:hidden absolute inset-0 z-20 bg-black/60 backdrop-blur-[1px]" onClick={handleBack} />
                    )}

                    {/* RIGHT SIDEBAR (DRAWER) */}
                    {/* Desktop: Docked Flex Item. Mobile: Absolute Overlay with Backdrpo support */}
                    <div 
                        className={`
                            bg-neutral-925 flex flex-col z-30 
                            transition-all duration-300 ease-[cubic-bezier(0.16,1,0.3,1)]
                            
                            /* Mobile Behavior (Default) */
                            absolute inset-y-0 right-0 w-[92vw] max-w-[560px] border-l border-neutral-900 shadow-2xl
                            ${activeDrawer ? 'translate-x-0' : 'translate-x-full'}

                            /* Desktop Behavior (>= lg) */
                            lg:static lg:h-auto lg:translate-x-0 lg:shadow-none lg:w-auto
                            ${activeDrawer ? (sidebarExpanded ? 'lg:w-2/3' : 'lg:w-1/3') : 'lg:w-0'}
                            ${activeDrawer ? 'lg:border-l' : 'lg:border-l-0'}
                        `}
                        onClick={e => e.stopPropagation()} // Prevent clicks inside drawer closing it
                    >
                        {activeDrawer && (
                            <>
                                <div className="h-10 border-b border-neutral-800 flex items-center justify-between px-4 bg-neutral-900/50 flex-shrink-0">
                                    <div className="flex items-center space-x-2">
                                        <button 
                                            onClick={() => setSidebarExpanded(!sidebarExpanded)} 
                                            className="hidden md:block p-1 hover:bg-neutral-800 rounded text-neutral-500 hover:text-neutral-300 transition-colors mr-2"
                                            title={sidebarExpanded ? "Collapse" : "Expand"}
                                        >
                                            {sidebarExpanded ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
                                        </button>
                                        {/* Context Anchor Breadcrumb */}
                                        <span className="text-[10px] font-mono text-neutral-500 uppercase tracking-tight truncate max-w-[200px]">
                                            {activeDrawer.breadcrumb || 'Inspector'}
                                        </span>
                                    </div>
                                    <button onClick={handleBack} className="text-[10px] uppercase tracking-wider text-neutral-600 hover:text-neutral-400 font-semibold px-2 py-1">Close</button>
                                </div>
                                <div className="flex-1 overflow-hidden relative">
                                    {renderDrawerContent()}
                                </div>
                            </>
                        )}
                    </div>
                </div>

                {/* MODAL OVERLAY */}
                {activeModal && (
                    <div className="absolute inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-[2px]" onClick={handleBack}>
                        <div className="bg-neutral-900 border border-neutral-800 p-8 rounded-lg shadow-2xl max-w-lg w-full m-4" onClick={e => e.stopPropagation()}>
                            <h3 className="text-lg font-medium text-neutral-200 mb-4">Activity Log</h3>
                            <div className="space-y-4 text-sm text-neutral-400">
                                <p>Since your last visit:</p>
                                <ul className="list-disc pl-5 space-y-1">
                                    <li>{activeModal.data.newRuns} pipelines executed.</li>
                                    <li>{activeModal.data.newAlerts} new system alerts triggered.</li>
                                    <li>Vault integrity check completed successfully.</li>
                                </ul>
                                <div className="pt-4 flex justify-end">
                                    <button onClick={handleBack} className="px-4 py-2 bg-neutral-800 hover:bg-neutral-700 text-neutral-200 rounded text-sm transition-colors">Dismiss</button>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}