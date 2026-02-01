import React, { useMemo, useRef, useEffect, useState } from 'react';
import { PipelineId, PipelineStageConfig, CanonicalStage } from '../types';
import { Badge } from './Common';
import {
    RefreshCw, Activity,
    Box, Layers, Sparkles, Tag,
    FileVideo, Globe, HardDrive, Archive,
    Zap, ArrowRight, Settings2, Play,
    GitMerge, AlertCircle, RotateCcw, X,
    Maximize2
} from 'lucide-react';

interface PipelineInspectorProps {
    pipelineId: PipelineId;
    stages: PipelineStageConfig[];
    initialStage?: string;
    hideHeader?: boolean;
    onStageSelect?: (stage: PipelineStageConfig) => void;
    onViewArtifacts?: (stage: PipelineStageConfig) => void;
}

const getStageIcon = (stageName: CanonicalStage) => {
    switch (stageName) {
        case CanonicalStage.Capture: return Box;
        case CanonicalStage.Separate: return Layers;
        case CanonicalStage.Clean: return Sparkles;
        case CanonicalStage.Enrich: return Tag;
        case CanonicalStage.Mix: return FileVideo;
        case CanonicalStage.Distill: return Archive;
        case CanonicalStage.Publish: return Globe;
        default: return HardDrive;
    }
};

// Vertical Connector Path
const getVerticalConnectorPath = (x1: number, y1: number, x2: number, y2: number) => {
    const dist = Math.abs(y2 - y1);
    const controlOffset = dist * 0.5;
    return `M ${x1} ${y1} C ${x1} ${y1 + controlOffset}, ${x2} ${y2 - controlOffset}, ${x2} ${y2}`;
};

// Vertical Loop Path (Arcs on the right side)
const getVerticalLoopPath = (x1: number, y1: number, x2: number, y2: number, width = 60) => {
    const centerY = (y1 + y2) / 2;
    return `M ${x1} ${y1} Q ${x1 + width} ${centerY} ${x2} ${y2}`;
};

// Deterministic hash to generate consistent "random" offsets for animation schedules
const getHash = (str: string) => {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        hash = ((hash << 5) - hash) + str.charCodeAt(i);
        hash |= 0;
    }
    return Math.abs(hash);
};

const PipelineTopology: React.FC<{
    stages: PipelineStageConfig[];
    selectedStage: string | null;
    selectedLoop: string | null;
    onSelectStage: (s: PipelineStageConfig) => void;
    onSelectLoop: (sourceStage: string) => void;
}> = ({ stages, selectedStage, selectedLoop, onSelectStage, onSelectLoop }) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const [dimensions, setDimensions] = useState({ width: 0, height: 0 });

    useEffect(() => {
        const updateSize = () => {
            if (containerRef.current) {
                setDimensions({
                    width: containerRef.current.clientWidth,
                    height: containerRef.current.clientHeight
                });
            }
        };
        updateSize();
        const observer = new ResizeObserver(updateSize);
        if (containerRef.current) observer.observe(containerRef.current);
        return () => observer.disconnect();
    }, []);

    const layout = useMemo(() => {
        if (dimensions.height === 0) return [];
        const count = stages.length;
        const paddingY = 80;
        const availableHeight = Math.max(dimensions.height, count * 120);
        const slotHeight = (availableHeight - (paddingY * 2)) / Math.max(1, count - 1);

        const nodeWidth = 200;
        const nodeHeight = 64;
        const centerX = dimensions.width / 2;

        return stages.map((stage, i) => {
            const slotCenterY = paddingY + (slotHeight * i);
            return {
                x: centerX - (nodeWidth / 2),
                y: slotCenterY - (nodeHeight / 2),
                width: nodeWidth,
                height: nodeHeight,
                centerX: centerX,
                centerY: slotCenterY,
                stage,
                index: i,
                animationOffset: (getHash(stage.name) % 3000) / 1000 // Hash-based delay in seconds
            };
        });
    }, [stages, dimensions]);

    if (layout.length === 0) return <div ref={containerRef} className="w-full h-full" />;

    const graphHeight = Math.max(dimensions.height, stages.length * 120 + 160);

    return (
        <div ref={containerRef} className="w-full h-full overflow-y-auto overflow-x-hidden bg-neutral-950 hide-scrollbar select-none">
            <div className="relative w-full" style={{ height: graphHeight }}>
                {/* SUBTLE 3D PERSPECTIVE GRID */}
                <div className="absolute inset-0 z-0 flex items-center justify-center pointer-events-none overflow-hidden" style={{ perspective: '1200px' }}>
                    <div
                        className="absolute w-[200%] h-[200%] opacity-[0.04]"
                        style={{
                            backgroundImage: `
                                linear-gradient(to right, #ffffff 1px, transparent 1px),
                                linear-gradient(to bottom, #ffffff 1px, transparent 1px)
                            `,
                            backgroundSize: '80px 80px',
                            transform: 'rotateX(55deg) translateZ(-100px) translateY(-10%)',
                            backgroundPosition: 'center center'
                        }}
                    />
                </div>

                {/* Topology SVG */}
                <svg
                    width={dimensions.width}
                    height={graphHeight}
                    className="absolute top-0 left-0 z-10 pointer-events-none"
                >
                    <defs>
                        <marker id="v-arrowhead" markerWidth="6" markerHeight="4" refX="5" refY="2" orient="auto">
                            <polygon points="0 0, 6 2, 0 4" fill="#262626" />
                        </marker>
                        <marker id="v-arrowhead-active" markerWidth="6" markerHeight="4" refX="5" refY="2" orient="auto">
                            <polygon points="0 0, 6 2, 0 4" fill="#10b981" />
                        </marker>
                        <marker id="v-arrowhead-loop" markerWidth="6" markerHeight="4" refX="5" refY="2" orient="auto">
                            <polygon points="0 0, 6 2, 0 4" fill="#6366f1" />
                        </marker>
                    </defs>

                    {/* Vertical Connectors - Cleaned up paths without moving lights */}
                    {layout.map((node, i) => {
                        const nextNode = layout[i + 1];
                        if (!nextNode) return null;
                        const startY = node.y + node.height;
                        const endY = nextNode.y;
                        const isActive = node.stage.status === 'running';
                        return (
                            <g key={`v-conn-${i}`}>
                                <path
                                    d={getVerticalConnectorPath(node.centerX, startY, nextNode.centerX, endY)}
                                    stroke={isActive ? "#10b981" : "#1a1a1a"}
                                    strokeWidth="1.5"
                                    fill="none"
                                    markerEnd={isActive ? "url(#v-arrowhead-active)" : "url(#v-arrowhead)"}
                                    strokeOpacity={isActive ? 0.4 : 1}
                                    className="transition-all duration-700"
                                />
                            </g>
                        );
                    })}

                    {/* Vertical Loops */}
                    {layout.map((node) => {
                        if (!node.stage.isLoopEnd || !node.stage.loopTarget) return null;
                        const targetNode = layout.find(n => n.stage.name === node.stage.loopTarget);
                        if (!targetNode) return null;
                        const isSelected = selectedLoop === node.stage.name;
                        const strokeColor = isSelected ? "#818cf8" : "#262626";
                        return (
                            <g key={`v-loop-${node.stage.name}`} className="cursor-pointer group" onClick={(e) => { e.stopPropagation(); onSelectLoop(node.stage.name); }}>
                                <path
                                    d={getVerticalLoopPath(node.x + node.width, node.centerY, targetNode.x + targetNode.width, targetNode.centerY, 100)}
                                    stroke="transparent"
                                    strokeWidth="30"
                                    fill="none"
                                    className="pointer-events-auto"
                                />
                                <path
                                    d={getVerticalLoopPath(node.x + node.width, node.centerY, targetNode.x + targetNode.width, targetNode.centerY, 100)}
                                    stroke={strokeColor}
                                    strokeWidth={isSelected ? "2" : "1"}
                                    strokeDasharray={isSelected ? "none" : "6 4"}
                                    fill="none"
                                    markerEnd="url(#v-arrowhead-loop)"
                                    className="transition-all duration-500"
                                />
                            </g>
                        );
                    })}
                </svg>

                {/* Stage Nodes */}
                {layout.map((node) => {
                    const Icon = getStageIcon(node.stage.name);
                    const isSelected = selectedStage === node.stage.name;
                    const isRunning = node.stage.status === 'running';

                    return (
                        <div
                            key={node.stage.name}
                            onClick={(e) => { e.stopPropagation(); onSelectStage(node.stage); }}
                            className={`absolute z-20 flex transition-all duration-500 ease-[cubic-bezier(0.16,1,0.3,1)] ${isSelected ? 'scale-110' : 'hover:translate-y-[-4px]'}`}
                            style={{ left: node.x, top: node.y, width: node.width, height: node.height }}
                        >
                            <div className={`
                                relative w-full h-full rounded-md border flex items-center px-4 transition-all
                                ${isSelected
                                    ? 'bg-neutral-100 border-neutral-100 shadow-[0_0_30px_rgba(255,255,255,0.1)]'
                                    : 'bg-neutral-950/80 border-neutral-800 hover:border-neutral-700 backdrop-blur-md'}
                            `}>
                                <div className={`
                                    w-9 h-9 rounded-md flex items-center justify-center flex-shrink-0 mr-4 transition-colors
                                    ${isSelected ? 'bg-neutral-950 text-neutral-100' : 'bg-neutral-900 text-neutral-600 border border-neutral-800'}
                                `}>
                                    <Icon className="w-4 h-4" />
                                </div>
                                <div className="flex-1 min-w-0">
                                    <div className={`text-[10px] font-black uppercase tracking-[0.2em] truncate ${isSelected ? 'text-neutral-950' : 'text-neutral-200'}`}>
                                        {node.stage.name}
                                    </div>
                                    <div className={`text-[8px] font-mono mt-1 ${isSelected ? 'text-neutral-500' : 'text-neutral-700'}`}>
                                        BUFF_DENSITY: {node.stage.queueDepth}
                                    </div>
                                </div>

                                <div className="flex-shrink-0 ml-2">
                                    <Badge status={node.stage.status} />
                                </div>

                                {/* Live Running Bar - Desynchronized Schedule */}
                                {isRunning && (
                                    <div
                                        className="absolute inset-x-2 -bottom-1 h-[2px] bg-emerald-500/20 rounded-full blur-[1px] animate-[pulse_3s_ease-in-out_infinite]"
                                        style={{ animationDelay: `-${node.animationOffset}s` }}
                                    />
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export const PipelineInspector: React.FC<PipelineInspectorProps> = ({ pipelineId, stages, initialStage, hideHeader = false, onStageSelect, onViewArtifacts }) => {
    const [selectedStageName, setSelectedStageName] = React.useState<string | null>(initialStage || null);
    const [selectedLoopSource, setSelectedLoopSource] = React.useState<string | null>(null);

    useEffect(() => { if (initialStage) setSelectedStageName(initialStage); }, [initialStage]);

    const selectedStageConfig = stages.find(s => s.name === selectedStageName);
    const selectedLoopConfig = stages.find(s => s.name === selectedLoopSource);

    return (
        <div className="flex flex-col h-full overflow-hidden bg-neutral-950 relative">
            {!hideHeader && (
                <div className="absolute top-0 inset-x-0 h-16 px-8 border-b border-neutral-900 bg-neutral-950/50 backdrop-blur-md z-30 flex justify-between items-center shrink-0">
                    <div className="min-w-0">
                        <h2 className="text-xs font-black uppercase tracking-[0.4em] text-neutral-600">{pipelineId.replace(' Pipeline', '')}</h2>
                    </div>
                    <div className="flex items-center space-x-2">
                        <button className="p-2 text-neutral-600 hover:text-neutral-200 transition-colors"><Settings2 className="w-4 h-4" /></button>
                        <button className="p-2 text-neutral-600 hover:text-neutral-200 transition-colors"><Play className="w-4 h-4" /></button>
                    </div>
                </div>
            )}

            <div className={`flex-1 relative overflow-hidden ${hideHeader ? '' : 'pt-16'}`} onClick={() => { setSelectedStageName(null); setSelectedLoopSource(null); }}>
                 <PipelineTopology
                    stages={stages}
                    selectedStage={selectedStageName}
                    selectedLoop={selectedLoopSource}
                    onSelectStage={(s) => { setSelectedLoopSource(null); setSelectedStageName(s.name); if (onStageSelect) onStageSelect(s); }}
                    onSelectLoop={(s) => { setSelectedStageName(null); setSelectedLoopSource(s); }}
                />

                 {/* BOTTOM INSPECTOR DRAWER */}
                 {(selectedStageConfig || selectedLoopConfig) && (
                    <div onClick={(e) => e.stopPropagation()} className="absolute bottom-0 inset-x-0 h-auto max-h-[80%] bg-neutral-950/95 border-t border-neutral-800 backdrop-blur-xl shadow-[0_-20px_50px_rgba(0,0,0,0.5)] z-40 animate-in slide-in-from-bottom-6 duration-500 flex flex-col pb-safe">
                        <div className="flex items-center justify-between px-8 py-3 border-b border-neutral-900 bg-neutral-900/40 shrink-0">
                            <span className="text-[10px] font-black uppercase tracking-[0.2em] text-neutral-700">{selectedStageConfig ? 'Depth Node Intelligence' : 'Recursion Logic Feed'}</span>
                            <button onClick={() => { setSelectedStageName(null); setSelectedLoopSource(null); }} className="text-neutral-500 hover:text-white transition-colors p-1"><X className="w-4 h-4" /></button>
                        </div>

                        <div className="p-8 md:p-12 overflow-y-auto">
                            {selectedStageConfig && (
                                <div className="flex flex-col md:flex-row gap-12 items-start">
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center space-x-4 mb-4">
                                            <h3 className="text-3xl md:text-5xl font-light text-neutral-100">{selectedStageConfig.name}</h3>
                                            <Badge status={selectedStageConfig.status} />
                                        </div>
                                        <p className="text-sm md:text-base text-neutral-500 leading-relaxed max-w-xl mb-8 font-light italic">
                                            "{selectedStageConfig.description}"
                                        </p>
                                        <div className="flex space-x-4">
                                            <button
                                                onClick={(e) => { e.stopPropagation(); onViewArtifacts && onViewArtifacts(selectedStageConfig); }}
                                                className="px-8 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-sm text-[10px] font-black uppercase tracking-[0.2em] transition-all shadow-lg hover:shadow-indigo-500/20"
                                            >
                                                Inspect State
                                            </button>
                                            <button className="px-8 py-3 border border-neutral-800 hover:bg-neutral-900 text-neutral-500 rounded-sm text-[10px] font-black uppercase tracking-[0.2em] transition-all">
                                                Re-route Mesh
                                            </button>
                                        </div>
                                    </div>
                                    <div className="grid grid-cols-2 gap-4 w-full md:w-80">
                                        <div className="p-6 bg-neutral-900/40 border border-neutral-800/60 rounded-sm">
                                            <div className="text-[9px] font-black uppercase tracking-[0.2em] text-neutral-700 mb-2">Queue Depth</div>
                                            <div className="text-3xl font-mono text-neutral-200">{selectedStageConfig.queueDepth}</div>
                                        </div>
                                        <div className="p-6 bg-neutral-900/40 border border-neutral-800/60 rounded-sm">
                                            <div className="text-[9px] font-black uppercase tracking-[0.2em] text-neutral-700 mb-2">Process Latency</div>
                                            <div className="text-3xl font-mono text-neutral-200">24<span className="text-xs ml-1 opacity-50">ms</span></div>
                                        </div>
                                        <div className="p-6 bg-neutral-900/40 border border-neutral-800/60 rounded-sm col-span-2">
                                            <div className="text-[9px] font-black uppercase tracking-[0.2em] text-neutral-700 mb-2">Health Profile</div>
                                            <div className="flex items-end space-x-1 h-10">
                                                {Array.from({length: 24}).map((_, i) => (
                                                    <div key={i} className="flex-1 bg-emerald-500/10 rounded-t-sm" style={{ height: `${15 + Math.random()*85}%` }} />
                                                ))}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}
                            {selectedLoopConfig && (
                                <div className="flex flex-col gap-6 max-w-2xl">
                                    <div className="flex items-center space-x-4">
                                        <div className="p-3 bg-indigo-500/10 rounded-full border border-indigo-500/20"><GitMerge className="w-5 h-5 text-indigo-400" /></div>
                                        <h3 className="text-xl md:text-2xl font-light text-neutral-200">Refinement Logic: {selectedLoopConfig.name}</h3>
                                    </div>
                                    <div className="p-6 border border-indigo-500/10 bg-indigo-500/5 rounded-sm">
                                        <div className="text-[10px] font-black uppercase tracking-[0.2em] text-indigo-400 mb-3">Operational Directive</div>
                                        <p className="text-sm text-neutral-400 font-mono leading-relaxed">
                                            IF quality_assurance.score &lt; THRESHOLD(0.85) AND retry_count &lt; LIMIT(3)<br/>
                                            THEN ROLLBACK state TO stage("{selectedLoopConfig.loopTarget}")<br/>
                                            ELSE FLAG AS "CONSOLIDATION_FAILURE" AND ROUTE TO HUMAN_OPS.
                                        </p>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                 )}
            </div>
        </div>
    );
};
