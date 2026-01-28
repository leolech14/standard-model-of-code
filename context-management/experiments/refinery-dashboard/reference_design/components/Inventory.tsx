import React, { useMemo, useState } from 'react';
import { Artifact, TruthStatus } from '../types';
import { UiRow, UiLink } from './Common';
import { 
    FileCode, FileText, FileJson, File, 
    Box, Wrench, Tag, Scroll, Activity, 
    Search, Copy, Layers
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
}

export const InventoryGrid: React.FC<InventoryGridProps> = ({ artifacts, onSelectStack, onViewAll, className, limit = 9 }) => {
    const stacks = useMemo(() => groupArtifacts(artifacts), [artifacts]);
    const topStacks = stacks.slice(0, limit);

    return (
        <div className={`grid grid-cols-3 gap-2 ${className || ''}`}>
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
                        className="
                            aspect-square relative group 
                            bg-neutral-900/15 hover:bg-neutral-900/30 
                            rounded-sm cursor-pointer transition-colors duration-100 
                            flex flex-col items-center justify-center overflow-hidden
                        "
                        title={`${stack.count} total — ${fullStacks}×${STACK_CAPACITY} + ${remainder}`}
                    >
                        {/* Status Dot */}
                        <div className={`absolute top-1.5 left-1.5 w-1 h-1 rounded-full ${truthColor} opacity-40`} />

                        {/* Count Display (Top Right) */}
                        <div className="absolute top-1 right-1 text-[9px] font-mono text-neutral-500 text-right leading-none z-20">
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
                        <div className="relative w-8 h-8 flex items-center justify-center mt-2">
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
                        <div className="mt-1 text-[8px] font-mono text-neutral-600 uppercase tracking-tight text-center px-1 truncate w-full z-20">
                            {stack.sample.type}
                        </div>
                    </div>
                );
            })}
            
            {/* Empty slots filler (Game Inventory Style: Empty slots exist but are dim) */}
            {topStacks.length < 9 && Array.from({ length: 9 - topStacks.length }).map((_, i) => (
                <div key={`empty-${i}`} className="aspect-square bg-neutral-900/5 rounded-sm" />
            ))}
            
            {stacks.length > limit && (
                <div className="col-span-3 text-center mt-1">
                    <span 
                        className="text-[10px] text-neutral-600 cursor-pointer hover:text-neutral-400"
                        onClick={(e) => { e.stopPropagation(); onViewAll && onViewAll(); }}
                    >
                        + {stacks.length - limit} more stacks
                    </span>
                </div>
            )}
        </div>
    );
};

interface StackInspectorProps {
    stack: ArtifactStack;
    onSelectArtifact: (artifact: Artifact) => void;
}

export const StackInspector: React.FC<StackInspectorProps> = ({ stack, onSelectArtifact }) => {
    const AtomIcon = getAtomIcon(stack.sample.atomClass);
    const [copied, setCopied] = useState(false);

    const handleCopy = () => {
        copyStackIds(stack);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="flex flex-col h-full">
            <div className="p-6 border-b border-neutral-800 bg-neutral-925">
                <div className="flex items-center space-x-3 mb-2">
                    <div className="p-2 bg-neutral-900 rounded border border-neutral-800">
                        <AtomIcon className="w-5 h-5 text-neutral-300" />
                    </div>
                    <div>
                        <h2 className="text-sm font-semibold text-neutral-200">{stack.sample.atomClass}</h2>
                        <div className="text-xs text-neutral-500 font-mono flex items-center space-x-2">
                             <span>{stack.sample.pipelineId.split(' ')[0]}</span>
                             <span>•</span>
                             <span>{stack.sample.stage}</span>
                        </div>
                    </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4 mt-4">
                     <div className="p-2 bg-neutral-900/50 rounded border border-neutral-800/50">
                        <div className="text-[10px] uppercase text-neutral-600">Count</div>
                        <div className="text-sm font-mono text-neutral-300">{stack.count}</div>
                     </div>
                     <div className="p-2 bg-neutral-900/50 rounded border border-neutral-800/50">
                        <div className="text-[10px] uppercase text-neutral-600">Truth Status</div>
                        <div className={`text-sm font-mono ${getStatusColor(stack.sample.truthStatus)}`}>
                            {stack.sample.truthStatus}
                        </div>
                     </div>
                </div>

                <div className="flex space-x-4 mt-4">
                    <UiLink onClick={handleCopy}>
                        {copied ? 'Copied!' : 'Copy IDs'}
                    </UiLink>
                    <UiLink onClick={() => downloadStackJson(stack)}>
                        Export Stack JSON
                    </UiLink>
                </div>
            </div>

            <div className="flex-1 overflow-y-auto p-2">
                {stack.artifacts.map(art => (
                    <UiRow key={art.id} onClick={() => onSelectArtifact(art)}>
                        <div className="flex items-center w-full text-sm py-1">
                            <span className="font-mono text-neutral-500 text-xs mr-3">{art.type}</span>
                            <span className="text-neutral-300 flex-1 truncate mr-2">{art.name}</span>
                            <span className="text-neutral-600 text-xs">{art.size}</span>
                        </div>
                    </UiRow>
                ))}
            </div>
        </div>
    );
};

interface StackListInspectorProps {
    artifacts: Artifact[];
    onSelectStack: (stack: ArtifactStack) => void;
}

export const StackListInspector: React.FC<StackListInspectorProps> = ({ artifacts, onSelectStack }) => {
    const stacks = useMemo(() => groupArtifacts(artifacts), [artifacts]);
    const [query, setQuery] = useState('');

    const filteredStacks = useMemo(() => {
        if (!query) return stacks;
        const q = query.toLowerCase();
        return stacks.filter(s => 
            s.sample.type.toLowerCase().includes(q) ||
            s.sample.atomClass.toLowerCase().includes(q) ||
            s.sample.truthStatus.toLowerCase().includes(q)
        );
    }, [stacks, query]);

    return (
        <div className="flex flex-col h-full">
            <div className="p-6 border-b border-neutral-800 bg-neutral-925">
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-2">
                        <Layers className="w-5 h-5 text-neutral-500" />
                        <h2 className="text-lg font-semibold text-neutral-200">All Stacks</h2>
                    </div>
                    <span className="text-xs text-neutral-500 font-mono">{filteredStacks.length} groups</span>
                </div>
                <div className="relative group">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-600" />
                    <input 
                        type="text" 
                        value={query}
                        onChange={e => setQuery(e.target.value)}
                        placeholder="Filter stacks..."
                        className="w-full bg-neutral-900 border border-neutral-800 rounded py-2 pl-9 pr-4 text-sm text-neutral-300 focus:outline-none focus:border-neutral-600 transition-colors"
                    />
                </div>
            </div>
            
            <div className="flex-1 overflow-y-auto p-2">
                {filteredStacks.map(stack => {
                     const AtomIcon = getAtomIcon(stack.sample.atomClass);
                     const truthColor = getStatusColor(stack.sample.truthStatus);

                     return (
                        <UiRow key={stack.key} onClick={() => onSelectStack(stack)}>
                            <div className="flex items-center w-full py-2">
                                <div className="p-1.5 bg-neutral-900 rounded border border-neutral-800 mr-3">
                                    <AtomIcon className="w-4 h-4 text-neutral-400" />
                                </div>
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center space-x-2 mb-0.5">
                                        <span className="text-sm font-medium text-neutral-300 truncate">{stack.sample.atomClass}</span>
                                        <span className={`text-[10px] font-mono uppercase ${truthColor}`}>{stack.sample.truthStatus}</span>
                                    </div>
                                    <div className="text-xs text-neutral-500 flex items-center space-x-2">
                                        <span className="uppercase font-mono">{stack.sample.type}</span>
                                        <span className="w-1 h-1 bg-neutral-700 rounded-full" />
                                        <span>{stack.sample.pipelineId.split(' ')[0]}</span>
                                    </div>
                                </div>
                                <div className="ml-4 flex flex-col items-end">
                                    <span className="text-sm font-mono text-neutral-300">{stack.count}</span>
                                    <span className="text-[10px] text-neutral-600">items</span>
                                </div>
                            </div>
                        </UiRow>
                     );
                })}
                {filteredStacks.length === 0 && (
                     <div className="p-8 text-center text-sm text-neutral-500">
                         No stacks match your filter.
                     </div>
                )}
            </div>
        </div>
    );
};