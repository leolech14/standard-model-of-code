import React, { useMemo, useState } from 'react';
import { Artifact, TruthStatus } from '../types';
import { UiRow, UiLink, Badge, SectionHeader } from './Common';
import {
    FileCode, FileText, FileJson, File,
    Box, Wrench, Tag, Scroll, Activity,
    Search, Copy, Layers, Clock, Hash,
    Download, Check, X, ArrowUpRight, Filter,
    ChevronRight, ChevronDown, Maximize2, Minimize2
} from 'lucide-react';

export interface ArtifactStack {
    key: string;
    artifacts: Artifact[];
    count: number;
    sample: Artifact;
}

const STACK_CAPACITY = 100;

// --- HELPERS ---

const getStackKey = (a: Artifact) => `${a.pipelineId}:${a.stage}:${a.type}:${a.atomClass}:${a.truthStatus}`;

export const groupArtifacts = (artifacts: Artifact[]): ArtifactStack[] => {
    const map = new Map<string, ArtifactStack>();

    artifacts.forEach(a => {
        const key = getStackKey(a);
        if (!map.has(key)) {
            map.set(key, { key, artifacts: [], count: 0, sample: a });
        }
        const entry = map.get(key)!;
        entry.artifacts.push(a);
        entry.count++;
    });

    // Sort items within stacks by recency (newest first)
    for (const stack of map.values()) {
        stack.artifacts.sort((a, b) => b.updatedAt - a.updatedAt);
    }

    return Array.from(map.values()).sort((a, b) => b.count - a.count);
};

const downloadStackJson = (stack: ArtifactStack) => {
    const filename = `stack_${stack.sample.type}_${stack.sample.atomClass.replace(':', '_')}`;
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(stack.artifacts, null, 2));
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", filename + ".json");
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
};

const copyStackIds = (stack: ArtifactStack) => {
    const text = stack.artifacts.map(a => a.id).join('\n');
    navigator.clipboard.writeText(text);
};

// --- VISUALS ---

const getAtomIcon = (atomClass: string) => {
    if (atomClass === 'ATOM:Spec') return Scroll;
    if (atomClass === 'ATOM:Tool') return Wrench;
    if (atomClass === 'ATOM:Role') return Tag;
    if (atomClass === 'ATOM:Signal') return Activity;
    return Box;
};

const getStatusColor = (status: TruthStatus) => {
    switch (status) {
        case 'VERIFIED': return 'text-emerald-500';
        case 'SUPPORTED': return 'text-blue-500';
        case 'CONFLICTING': return 'text-rose-500';
        case 'STALE': return 'text-amber-500';
        default: return 'text-neutral-600';
    }
};

// --- COMPONENTS ---

interface InventoryGridProps {
    artifacts: Artifact[];
    onSelectStack: (stack: ArtifactStack) => void;
    onViewAll?: () => void;
    className?: string;
    limit?: number;
    onContextMenu?: (e: React.MouseEvent, type: 'stack', data: ArtifactStack) => void;
}

export const InventoryGrid: React.FC<InventoryGridProps> = ({ artifacts, onSelectStack, onViewAll, className, limit = 9, onContextMenu }) => {
    const stacks = useMemo(() => groupArtifacts(artifacts), [artifacts]);
    const topStacks = stacks.slice(0, limit);

    return (
        <div className={`grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-2 ${className || ''}`}>
            {topStacks.map(stack => {
                const AtomIcon = getAtomIcon(stack.sample.atomClass);
                const truthColor = getStatusColor(stack.sample.truthStatus);

                // Tibia-style Stacking Logic
                const count = stack.count;
                const fullStacks = Math.floor(count / STACK_CAPACITY);
                const remainder = count % STACK_CAPACITY;
                const layers = fullStacks >= 5 ? 3 : fullStacks >= 3 ? 2 : fullStacks >= 1 ? 1 : 0;

                const showPlusRemainder = fullStacks >= 1 && remainder > 0;

                return (
                    <div
                        key={stack.key}
                        onClick={(e) => { e.stopPropagation(); onSelectStack(stack); }}
                        onContextMenu={(e) => {
                             if (onContextMenu) {
                                 e.preventDefault();
                                 e.stopPropagation();
                                 onContextMenu(e, 'stack', stack);
                             }
                        }}
                        tabIndex={0}
                        onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); e.stopPropagation(); onSelectStack(stack); } }}
                        className="
                            aspect-square relative group
                            bg-neutral-900/15 hover:bg-neutral-900/30
                            rounded-sm cursor-pointer transition-colors duration-150
                            flex flex-col items-center justify-center overflow-hidden
                            outline-none focus-visible:ring-1 focus-visible:ring-neutral-700 focus-visible:bg-neutral-900/30
                        "
                        title={`${stack.count} total — ${fullStacks}×${STACK_CAPACITY} + ${remainder}`}
                    >
                        {/* Status Dot */}
                        <div className={`absolute top-1.5 left-1.5 w-1.5 h-1.5 rounded-full ${truthColor} opacity-60 shadow-[0_0_5px_rgba(0,0,0,0.5)]`} />

                        {/* Count Display (Top Right) */}
                        <div className="absolute top-1 right-1 text-[9px] font-mono text-neutral-500 text-right leading-none z-20 pointer-events-none">
                            {fullStacks > 0 ? (
                                <>
                                    <div className="text-neutral-400 font-semibold">{fullStacks}×{STACK_CAPACITY}</div>
                                    {showPlusRemainder && <div className="text-[8px] opacity-75">+{remainder}</div>}
                                </>
                            ) : (
                                <span>{count}/{STACK_CAPACITY}</span>
                            )}
                        </div>

                        {/* Stacking Visual Layers */}
                        <div className="relative w-8 h-8 flex items-center justify-center mt-2 pointer-events-none">
                             {/* Layer -3 (Deepest) */}
                             {layers >= 3 && (
                                <AtomIcon
                                    strokeWidth={1.5}
                                    className="absolute w-5 h-5 text-neutral-800 transform -translate-y-1.5 -translate-x-1.5"
                                />
                             )}
                             {/* Layer -2 */}
                             {layers >= 2 && (
                                <AtomIcon
                                    strokeWidth={1.5}
                                    className="absolute w-5 h-5 text-neutral-700 transform -translate-y-1 -translate-x-1"
                                />
                             )}
                             {/* Layer -1 */}
                             {layers >= 1 && (
                                <AtomIcon
                                    strokeWidth={1.5}
                                    className="absolute w-5 h-5 text-neutral-600 transform -translate-y-0.5 -translate-x-0.5"
                                />
                             )}

                            {/* Main Icon */}
                            <AtomIcon
                                strokeWidth={1.5}
                                className="relative z-10 w-5 h-5 text-neutral-400 group-hover:text-neutral-300 transition-colors"
                            />
                        </div>

                        {/* Label */}
                        <div className="mt-1 text-[8px] font-mono text-neutral-600 uppercase tracking-tight text-center px-1 truncate w-full z-20 pointer-events-none">
                            {stack.sample.type}
                        </div>
                    </div>
                );
            })}

            {/* Empty slots filler (Game Inventory Style: Empty slots exist but are dim) */}
            {topStacks.length < limit && Array.from({ length: limit - topStacks.length }).map((_, i) => (
                <div key={`empty-${i}`} className="aspect-square bg-neutral-900/5 rounded-sm" />
            ))}

            {stacks.length > limit && (
                <div className="col-span-3 sm:col-span-4 md:col-span-6 lg:col-span-8 text-center mt-1">
                    <span
                        className="text-[10px] text-neutral-600 cursor-pointer hover:text-neutral-400 focus:outline-none focus:underline"
                        role="button"
                        tabIndex={0}
                        onClick={(e) => { e.stopPropagation(); onViewAll && onViewAll(); }}
                        onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); e.stopPropagation(); onViewAll && onViewAll(); } }}
                    >
                        + {stacks.length - limit} more stacks
                    </span>
                </div>
            )}
        </div>
    );
};

export const CategorizedInventory: React.FC<{
    artifacts: Artifact[];
    groupBy: (a: Artifact) => string;
    onSelectStack: (stack: ArtifactStack) => void;
    className?: string;
    onContextMenu?: (e: React.MouseEvent, type: 'stack', data: ArtifactStack) => void;
}> = ({ artifacts, groupBy, onSelectStack, className, onContextMenu }) => {
    // Default to collapsed state, using a Set to track open categories
    const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set());
    const [allExpanded, setAllExpanded] = useState(false);

    const groups = useMemo(() => {
        const g = new Map<string, Artifact[]>();
        artifacts.forEach(a => {
            const key = groupBy(a);
            if (!g.has(key)) g.set(key, []);
            g.get(key)!.push(a);
        });

        // Define sorting order for stages to keep them logical
        const stageOrder = ['Capture', 'Separate', 'Clean', 'Enrich', 'Mix', 'Distill', 'Publish'];

        return Array.from(g.entries()).sort((a, b) => {
             const idxA = stageOrder.indexOf(a[0]);
             const idxB = stageOrder.indexOf(b[0]);
             if (idxA !== -1 && idxB !== -1) return idxA - idxB;
             return a[0].localeCompare(b[0]);
        });
    }, [artifacts, groupBy]);

    const toggleCategory = (category: string) => {
        const newSet = new Set(expandedCategories);
        if (newSet.has(category)) {
            newSet.delete(category);
        } else {
            newSet.add(category);
        }
        setExpandedCategories(newSet);
        setAllExpanded(false); // Break "all expanded" sync if user toggles manually
    };

    const toggleAll = () => {
        if (allExpanded) {
            setExpandedCategories(new Set());
        } else {
            setExpandedCategories(new Set(groups.map(g => g[0])));
        }
        setAllExpanded(!allExpanded);
    };

    return (
        <div className={`space-y-2 ${className || ''}`}>
            {/* Global Controls */}
            <div className="flex justify-end mb-4 border-b border-neutral-900 pb-2">
                <button
                    onClick={toggleAll}
                    className="flex items-center space-x-1.5 text-[10px] uppercase font-semibold text-neutral-500 hover:text-neutral-300 transition-colors"
                >
                    {allExpanded ? <Minimize2 className="w-3 h-3" /> : <Maximize2 className="w-3 h-3" />}
                    <span>{allExpanded ? 'Collapse All' : 'Show All'}</span>
                </button>
            </div>

            {groups.map(([category, items]) => {
                const isExpanded = allExpanded || expandedCategories.has(category);

                // Contextual Stats for Header
                const liveCount = items.filter(i => i.status === 'live').length;
                const failedCount = items.filter(i => i.status === 'failed').length;
                // const total = items.length;
                const livePct = (liveCount / items.length) * 100;
                const failedPct = (failedCount / items.length) * 100;

                return (
                    <div key={category} className="bg-neutral-900/10 border border-neutral-900 rounded overflow-hidden">
                        {/* Interactive Header */}
                        <div
                            onClick={() => toggleCategory(category)}
                            className={`
                                flex items-center justify-between px-3 py-2 cursor-pointer select-none transition-colors
                                ${isExpanded ? 'bg-neutral-900/30' : 'hover:bg-neutral-900/20'}
                            `}
                        >
                            <div className="flex items-center space-x-2">
                                <ChevronRight className={`w-3.5 h-3.5 text-neutral-500 transition-transform duration-200 ${isExpanded ? 'rotate-90' : ''}`} />
                                <span className="text-[10px] uppercase font-bold text-neutral-400 tracking-wider">{category}</span>
                            </div>

                            <div className="flex items-center space-x-3">
                                {/* Contextual Mini-Viz (Visible when collapsed OR expanded) */}
                                <div className="flex flex-col items-end space-y-0.5">
                                    <div className="flex space-x-0.5 h-1.5 w-16 bg-neutral-900 rounded-sm overflow-hidden">
                                        <div className="bg-emerald-500/50" style={{ width: `${livePct}%` }} />
                                        <div className="bg-rose-500/50" style={{ width: `${failedPct}%` }} />
                                    </div>
                                    {failedCount > 0 && !isExpanded && (
                                        <span className="text-[9px] text-rose-500 font-mono leading-none">{failedCount} failed</span>
                                    )}
                                </div>

                                <span className="text-[10px] font-mono text-neutral-600 min-w-[24px] text-right">
                                    {items.length}
                                </span>
                            </div>
                        </div>

                        {/* Content Body */}
                        {isExpanded && (
                            <div className="p-3 border-t border-neutral-900 animate-in slide-in-from-top-1 duration-200">
                                <InventoryGrid
                                    artifacts={items}
                                    onSelectStack={onSelectStack}
                                    onContextMenu={onContextMenu}
                                    className="!gap-1.5"
                                    limit={16}
                                />
                            </div>
                        )}
                    </div>
                );
            })}
        </div>
    );
};

// --- NEW HORIZONTAL INSPECTOR ---

export const HorizontalStackInspector: React.FC<{
    stack: ArtifactStack;
    onClose: () => void;
    onSelectArtifact: (a: Artifact) => void;
}> = ({ stack, onClose, onSelectArtifact }) => {
    const AtomIcon = getAtomIcon(stack.sample.atomClass);
    const uniqueTags = useMemo(() => Array.from(new Set(stack.artifacts.flatMap(a => a.tags))), [stack.artifacts]);

    return (
        <div className="absolute top-0 inset-x-0 z-30 bg-neutral-950/90 border-b border-neutral-800 backdrop-blur-md shadow-2xl animate-in slide-in-from-top-4 fade-in duration-300 h-72 flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-2 border-b border-neutral-800/50 bg-neutral-900/20 shrink-0">
                 <div className="flex items-center space-x-3">
                    <div className="p-1.5 bg-neutral-900 rounded border border-neutral-800 text-neutral-400">
                        <AtomIcon className="w-4 h-4" />
                    </div>
                    <div>
                        <div className="flex items-center space-x-2">
                             <span className="text-sm font-semibold text-neutral-200">{stack.sample.atomClass}</span>
                             <span className={`text-[10px] font-mono uppercase px-1.5 py-0.5 rounded-sm bg-neutral-900 border border-neutral-800 ${getStatusColor(stack.sample.truthStatus)}`}>
                                {stack.sample.truthStatus}
                             </span>
                        </div>
                    </div>
                 </div>
                 <div className="flex items-center space-x-4">
                     <span className="text-[10px] text-neutral-500 uppercase tracking-widest">{stack.count} Items</span>
                     <button onClick={onClose} className="text-neutral-500 hover:text-neutral-200 hover:bg-neutral-800 rounded p-1 transition-colors">
                        <X className="w-4 h-4" />
                     </button>
                 </div>
            </div>

            {/* Body */}
            <div className="flex flex-1 min-h-0">
                {/* Left: Metadata Column */}
                <div className="w-64 p-4 border-r border-neutral-800 bg-neutral-900/10 flex flex-col space-y-4 shrink-0 overflow-y-auto">
                     <div>
                        <div className="text-[10px] uppercase text-neutral-600 font-semibold mb-1">Pipeline Context</div>
                        <div className="text-xs text-neutral-300 font-mono space-y-0.5">
                             <div className="flex items-center"><ArrowUpRight className="w-3 h-3 mr-2 text-neutral-600"/>{stack.sample.pipelineId.split(' ')[0]}</div>
                             <div className="flex items-center"><ArrowUpRight className="w-3 h-3 mr-2 text-neutral-600"/>{stack.sample.stage}</div>
                        </div>
                     </div>

                     {uniqueTags.length > 0 && (
                        <div>
                            <div className="text-[10px] uppercase text-neutral-600 font-semibold mb-1">Tags</div>
                            <div className="flex flex-wrap gap-1">
                                {uniqueTags.map(tag => (
                                    <span key={tag} className="px-1.5 py-0.5 bg-neutral-900 border border-neutral-800 rounded text-[10px] text-neutral-500 font-mono">
                                        {tag}
                                    </span>
                                ))}
                            </div>
                        </div>
                     )}

                     <div className="mt-auto pt-4 flex flex-col gap-2">
                        <UiLink onClick={() => copyStackIds(stack)} className="justify-start">
                            <Copy className="w-3 h-3 mr-2" /> Copy All IDs
                        </UiLink>
                        <UiLink onClick={() => downloadStackJson(stack)} className="justify-start">
                            <Download className="w-3 h-3 mr-2" /> Export JSON
                        </UiLink>
                     </div>
                </div>

                {/* Right: Grid of Artifacts */}
                <div className="flex-1 p-4 overflow-y-auto bg-neutral-950/30">
                    <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-2">
                        {stack.artifacts.map(art => (
                            <div
                                key={art.id}
                                onClick={() => onSelectArtifact(art)}
                                className="group flex items-center p-2 rounded border border-neutral-800 bg-neutral-900/20 hover:bg-neutral-800/80 hover:border-neutral-700 cursor-pointer transition-all"
                            >
                                <div className={`w-1 h-8 rounded-full mr-3 ${art.status === 'live' ? 'bg-emerald-500/50' : art.status === 'failed' ? 'bg-rose-500/50' : 'bg-neutral-700'}`} />
                                <div className="min-w-0 flex-1">
                                    <div className="flex justify-between items-center mb-0.5">
                                        <span className="text-[10px] font-mono text-neutral-500 uppercase">{art.type}</span>
                                        <span className="text-[9px] text-neutral-600">{art.size}</span>
                                    </div>
                                    <div className="text-xs text-neutral-300 font-medium truncate group-hover:text-white transition-colors">{art.name}</div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export const StackInspector: React.FC<{
    stack: ArtifactStack;
    onSelectArtifact: (art: Artifact) => void;
}> = ({ stack, onSelectArtifact }) => {
    const AtomIcon = getAtomIcon(stack.sample.atomClass);
    return (
        <div className="flex flex-col h-full bg-neutral-950">
            <div className="p-6 border-b border-neutral-800 shrink-0">
                <div className="flex items-center space-x-3 mb-2">
                    <div className="p-2 bg-neutral-900 rounded border border-neutral-800">
                        <AtomIcon className="w-5 h-5 text-neutral-400" />
                    </div>
                    <div>
                        <h2 className="text-lg font-semibold text-neutral-200">{stack.sample.atomClass}</h2>
                        <div className="text-xs text-neutral-500 font-mono">{stack.count} items • {stack.sample.truthStatus}</div>
                    </div>
                </div>
                <div className="flex gap-2 mt-4">
                     <button onClick={() => copyStackIds(stack)} className="flex-1 py-2 border border-neutral-800 hover:bg-neutral-900 rounded text-xs text-neutral-400 flex items-center justify-center transition-colors">
                        <Copy className="w-3 h-3 mr-2" /> IDs
                     </button>
                     <button onClick={() => downloadStackJson(stack)} className="flex-1 py-2 border border-neutral-800 hover:bg-neutral-900 rounded text-xs text-neutral-400 flex items-center justify-center transition-colors">
                        <Download className="w-3 h-3 mr-2" /> JSON
                     </button>
                </div>
            </div>
            <div className="flex-1 overflow-y-auto p-2">
                {stack.artifacts.map(art => (
                    <UiRow key={art.id} onClick={() => onSelectArtifact(art)}>
                        <div className="flex flex-col w-full py-1">
                             <div className="flex justify-between items-center mb-1">
                                <span className="text-sm text-neutral-300 truncate">{art.name}</span>
                                <Badge status={art.status} />
                             </div>
                             <div className="flex justify-between items-center text-[10px] text-neutral-600 font-mono">
                                <span>{art.id}</span>
                                <span>{art.size}</span>
                             </div>
                        </div>
                    </UiRow>
                ))}
            </div>
        </div>
    );
};

export const StackListInspector: React.FC<{
    artifacts: Artifact[];
    onSelectStack: (stack: ArtifactStack) => void;
}> = ({ artifacts, onSelectStack }) => {
    return (
        <div className="flex flex-col h-full bg-neutral-950">
            <div className="p-6 border-b border-neutral-800 shrink-0">
                <SectionHeader title="Artifact Stacks" />
                <p className="text-xs text-neutral-500 mt-2">Grouped by atom class and type.</p>
            </div>
            <div className="p-4 overflow-y-auto flex-1">
                <InventoryGrid
                    artifacts={artifacts}
                    onSelectStack={onSelectStack}
                    limit={200}
                    className="gap-3"
                />
            </div>
        </div>
    );
};
