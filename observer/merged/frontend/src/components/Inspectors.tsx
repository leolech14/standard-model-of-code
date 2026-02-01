import React, { useMemo, useState } from 'react';
import { Artifact, Run, Alert, PipelineStageConfig } from '../types';
import { UiLink, Badge } from './Common';
import {
    FileCode, FileVideo, FileAudio, Archive,
    Clock, Terminal, Star, CheckCircle2,
    XCircle, Circle, PlayCircle, AlertCircle, ArrowRight,
    Search, Filter, Eye
} from 'lucide-react';

export const ArtifactInspector: React.FC<{ artifact: Artifact; onUpdate: (a: Artifact) => void }> = ({ artifact, onUpdate }) => {
    const toggleVault = () => {
        onUpdate({ ...artifact, isVaulted: !artifact.isVaulted });
    };

    return (
        <div className="flex flex-col h-full">
            <div className="p-6 border-b border-neutral-800">
                <div className="flex items-center space-x-2 text-xs text-neutral-500 font-mono mb-2">
                    <Archive className="w-3 h-3" />
                    <span>{artifact.id}</span>
                </div>
                <div className="flex items-start justify-between">
                    <h2 className="text-xl font-semibold text-neutral-200 mb-1 truncate flex-1 mr-4">{artifact.name}</h2>
                    {artifact.isVaulted && <Star className="w-5 h-5 text-emerald-500 fill-emerald-500/20" />}
                </div>
                <div className="flex items-center space-x-3 text-xs text-neutral-500">
                    <Badge status={artifact.status} />
                    <span>{artifact.stage}</span>
                    <span className="w-1 h-1 bg-neutral-700 rounded-full" />
                    <span>{artifact.size}</span>
                </div>
            </div>

            <div className="flex border-b border-neutral-800 px-6">
                {['Summary', 'Stats', 'Snippets', 'Provenance'].map((tab, i) => (
                    <button key={tab} className={`px-4 py-3 text-xs font-medium border-b-2 transition-colors ${i === 0 ? 'border-neutral-500 text-neutral-200' : 'border-transparent text-neutral-600 hover:text-neutral-400'}`}>
                        {tab}
                    </button>
                ))}
            </div>

            <div className="p-6 space-y-6 flex-1 overflow-y-auto">
                <div className="space-y-1">
                    <label className="text-[10px] uppercase text-neutral-600 font-semibold tracking-wider">Type</label>
                    <div className="flex items-center space-x-2 text-sm text-neutral-400">
                        {artifact.type === 'mp4' ? <FileVideo className="w-4 h-4" /> : artifact.type === 'wav' ? <FileAudio className="w-4 h-4" /> : <FileCode className="w-4 h-4" />}
                        <span className="uppercase">{artifact.type}</span>
                    </div>
                </div>

                <div className="space-y-1">
                    <label className="text-[10px] uppercase text-neutral-600 font-semibold tracking-wider">Tags</label>
                    <div className="flex flex-wrap gap-2">
                        {artifact.tags.map(tag => (
                            <span key={tag} className="px-1.5 py-0.5 bg-neutral-900 border border-neutral-800 rounded text-[10px] text-neutral-400 font-mono">
                                {tag}
                            </span>
                        ))}
                    </div>
                </div>

                <div className="p-4 bg-neutral-900/50 border border-neutral-800/50 rounded text-xs font-mono text-neutral-500 whitespace-pre-wrap">
{`{
  "checksum": "sha256:8f43...",
  "created_by": "service_worker_04",
  "dependencies": []
}`}
                </div>
            </div>

            <div className="p-6 border-t border-neutral-800 bg-neutral-925">
                 <UiLink
                    onClick={toggleVault}
                    className={`w-full py-2 border text-center transition-colors ${artifact.isVaulted ? 'border-emerald-900 text-emerald-500 hover:bg-emerald-900/10' : 'border-neutral-700 hover:bg-neutral-800'}`}
                 >
                    {artifact.isVaulted ? 'Remove from Vault' : 'Save to Vault'}
                 </UiLink>
            </div>
        </div>
    );
};

// Log Generator Helper
const generateLogs = (run: Run): string[] => {
    const logs = [
        `[INFO] ${new Date(run.startTime).toISOString()} - Run initiated by ${run.triggeredBy}`,
        `[INFO] Allocating resources (worker_pool_a)...`,
        `[INFO] Pulling container image v2.4.1...`,
        `[INFO] Validating input parameters...`,
        `[INFO] Ingesting telemetry stream...`,
    ];

    if (run.status === 'success') {
        logs.push(
            `[INFO] Processing chunk 1/450...`,
            `[INFO] Processing chunk 50/450...`,
            `[INFO] Processing chunk 128/450...`,
            `[INFO] Processing chunk 450/450...`,
            `[INFO] Pipeline completed successfully.`,
            `[INFO] Releasing worker resources.`
        );
    } else if (run.status === 'failed') {
        logs.push(
            `[INFO] Processing chunk 12/450...`,
            `[WARN] High latency detected in sector 7`,
            `[ERR] Connection reset by peer`,
            `[FATAL] Max retries exceeded. Aborting.`
        );
    } else {
        logs.push(
            `[INFO] Processing chunk 24/450...`,
            `[WARN] Memory pressure climbing (78%)...`,
            `[INFO] Processing active...`
        );
    }
    return logs;
};

export const RunInspector: React.FC<{ run: Run; pipelineConfig: PipelineStageConfig[]; onSelectStage?: (stageName: string) => void }> = ({ run, pipelineConfig, onSelectStage }) => {
    const [searchQuery, setSearchQuery] = useState('');
    const [showOnlyMatches, setShowOnlyMatches] = useState(false);

    // Stage Breakdown based on run status
    const stages = pipelineConfig || [];

    // Deterministic pseudo-random index for failure/running state based on ID
    const runHash = run.id.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    const eventIndex = runHash % Math.max(1, stages.length);

    const getStageStatus = (index: number) => {
        if (run.status === 'success') return 'completed';
        if (run.status === 'failed') {
            if (index < eventIndex) return 'completed';
            if (index === eventIndex) return 'failed';
            return 'pending';
        }
        if (run.status === 'running') {
            if (index < eventIndex) return 'completed';
            if (index === eventIndex) return 'active';
            return 'pending';
        }
        return 'pending';
    };

    const logs = useMemo(() => generateLogs(run), [run]);

    const filteredLogs = useMemo(() => {
        if (!searchQuery) return logs;
        if (showOnlyMatches) {
            return logs.filter(l => l.toLowerCase().includes(searchQuery.toLowerCase()));
        }
        return logs;
    }, [logs, searchQuery, showOnlyMatches]);

    const renderLogLine = (line: string, idx: number) => {
        const isMatch = searchQuery && line.toLowerCase().includes(searchQuery.toLowerCase());
        const parts = searchQuery ? line.split(new RegExp(`(${searchQuery})`, 'gi')) : [line];

        return (
            <div key={idx} className={`whitespace-pre-wrap break-all ${isMatch ? 'bg-indigo-500/10 -mx-2 px-2 rounded' : 'opacity-70'}`}>
                {searchQuery ? (
                    parts.map((part, i) =>
                        part.toLowerCase() === searchQuery.toLowerCase() ? (
                            <span key={i} className="bg-indigo-500 text-white px-0.5 rounded-sm">{part}</span>
                        ) : (
                            <span key={i}>{part}</span>
                        )
                    )
                ) : (
                    <span className={line.includes('[ERR]') || line.includes('[FATAL]') ? 'text-rose-400 font-bold' : line.includes('[WARN]') ? 'text-amber-400' : line.includes('[INFO]') ? 'text-emerald-400' : ''}>{line}</span>
                )}
            </div>
        );
    };

    return (
        <div className="flex flex-col h-full">
            <div className="p-6 border-b border-neutral-800">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-lg font-semibold text-neutral-200">Run Details</h2>
                    <span className="font-mono text-xs text-neutral-600">{run.id}</span>
                </div>

                <div className="bg-neutral-900 p-4 rounded mb-6 flex items-center justify-between border border-neutral-800">
                    <div>
                         <div className="text-[10px] text-neutral-500 uppercase mb-1">Pipeline</div>
                         <div className="text-sm text-neutral-300 font-medium">{run.pipelineId}</div>
                    </div>
                    <Badge status={run.status} />
                </div>

                <div className="grid grid-cols-3 gap-2">
                    <div className="p-3 bg-neutral-900/50 border border-neutral-800/50 rounded">
                        <div className="text-[10px] text-neutral-600 uppercase mb-1">Duration</div>
                        <div className="text-xs text-neutral-300 font-mono">{run.duration}</div>
                    </div>
                    <div className="p-3 bg-neutral-900/50 border border-neutral-800/50 rounded">
                        <div className="text-[10px] text-neutral-600 uppercase mb-1">Trigger</div>
                        <div className="text-xs text-neutral-300 font-mono truncate">{run.triggeredBy}</div>
                    </div>
                     <div className="p-3 bg-neutral-900/50 border border-neutral-800/50 rounded">
                        <div className="text-[10px] text-neutral-600 uppercase mb-1">Started</div>
                        <div className="text-xs text-neutral-300 font-mono whitespace-nowrap overflow-hidden text-ellipsis">
                            {new Date(run.startTime).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                        </div>
                    </div>
                </div>
            </div>

            <div className="flex-1 overflow-y-auto">
                <div className="p-6">
                    <h3 className="text-xs text-neutral-500 uppercase font-semibold mb-4 flex items-center">
                        Stage Breakdown
                    </h3>
                    <div className="relative space-y-0">
                        {/* Connecting Line */}
                        <div className="absolute left-3.5 top-2 bottom-4 w-px bg-neutral-800" />

                        {stages.map((stage, i) => {
                            const status = getStageStatus(i);
                            return (
                                <div
                                    key={stage.name}
                                    className={`relative flex items-center py-2 group ${onSelectStage ? 'cursor-pointer' : ''}`}
                                    onClick={() => onSelectStage && onSelectStage(stage.name)}
                                >
                                    <div className="relative z-10 w-8 flex justify-center bg-neutral-925">
                                        {status === 'completed' && <CheckCircle2 className="w-4 h-4 text-emerald-500" />}
                                        {status === 'failed' && <XCircle className="w-4 h-4 text-rose-500" />}
                                        {status === 'active' && <PlayCircle className="w-4 h-4 text-blue-500 animate-pulse" />}
                                        {status === 'pending' && <Circle className="w-4 h-4 text-neutral-700" />}
                                    </div>
                                    <div className="flex-1 ml-2">
                                        <div className={`text-sm flex items-center ${status === 'pending' ? 'text-neutral-600' : 'text-neutral-300'}`}>
                                            {stage.name}
                                            {onSelectStage && (
                                                <ArrowRight className="w-3 h-3 ml-2 opacity-0 group-hover:opacity-50 transition-opacity" />
                                            )}
                                        </div>
                                        {status === 'failed' && (
                                            <div className="text-xs text-rose-500/80 mt-0.5">Error: Timeout waiting for resource allocation.</div>
                                        )}
                                        {status === 'active' && (
                                            <div className="text-xs text-blue-500/80 mt-0.5">Processing batch...</div>
                                        )}
                                    </div>
                                    <div className="text-[10px] font-mono text-neutral-600">
                                        {status === 'completed' ? 'Done' : status === 'failed' ? 'Err' : status === 'active' ? 'Run' : '-'}
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>

                <div className="p-6 border-t border-neutral-800">
                     <div className="flex items-center justify-between mb-3">
                        <h3 className="text-xs text-neutral-500 uppercase font-semibold flex items-center">
                            <Terminal className="w-3 h-3 mr-2" />
                            Execution Logs
                        </h3>
                     </div>

                     {/* Search Bar */}
                     <div className="flex items-center mb-3 space-x-2">
                        <div className="relative flex-1">
                            <Search className="absolute left-2 top-1/2 -translate-y-1/2 w-3 h-3 text-neutral-600" />
                            <input
                                type="text"
                                placeholder="Search logs..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="w-full bg-neutral-900 border border-neutral-800 rounded py-1 pl-7 pr-2 text-xs text-neutral-300 focus:outline-none focus:border-neutral-600 placeholder-neutral-600"
                            />
                        </div>
                        <button
                            onClick={() => setShowOnlyMatches(!showOnlyMatches)}
                            className={`p-1 rounded border transition-all ${showOnlyMatches ? 'bg-indigo-900/50 border-indigo-500 text-indigo-300' : 'bg-transparent border-neutral-800 text-neutral-500 hover:text-neutral-300'}`}
                            title="Show only matches"
                        >
                            <Filter className="w-3.5 h-3.5" />
                        </button>
                     </div>

                    <div className="bg-neutral-950 p-4 rounded border border-neutral-800 font-mono text-[10px] text-neutral-500 leading-relaxed overflow-x-auto min-h-[120px] max-h-[300px] overflow-y-auto">
                        {filteredLogs.length > 0 ? (
                            filteredLogs.map((line, i) => renderLogLine(line, i))
                        ) : (
                            <div className="text-center py-4 opacity-50 italic">No matching logs found.</div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export const AlertInspector: React.FC<{ alert: Alert }> = ({ alert }) => (
    <div className="p-6">
        <div className="flex items-center space-x-2 mb-4 text-rose-500">
             <AlertCircle className="w-5 h-5" />
             <span className="text-sm font-bold uppercase tracking-widest">{alert.severity} ALERT</span>
        </div>
        <h2 className="text-xl font-medium text-neutral-200 mb-2">{alert.message}</h2>
        <div className="text-xs text-neutral-500 font-mono mb-8">{alert.id} • {new Date(alert.timestamp).toLocaleString()}</div>

        <div className="space-y-4">
            <div className="bg-neutral-900 p-4 rounded border-l-2 border-neutral-700">
                <div className="text-xs text-neutral-400 mb-1">Source Component</div>
                <div className="text-sm text-neutral-200 font-mono">{alert.source}</div>
            </div>

             <div className="flex items-center justify-between pt-8">
                 <span className="text-xs text-neutral-500">Status: {alert.acknowledged ? 'Acknowledged' : 'Pending'}</span>
                 <label className="flex items-center space-x-2 cursor-pointer">
                     <div className={`w-10 h-5 rounded-full relative transition-colors ${alert.acknowledged ? 'bg-emerald-600' : 'bg-neutral-700'}`}>
                         <div className={`absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full transition-transform ${alert.acknowledged ? 'translate-x-5' : ''}`} />
                     </div>
                     <span className="text-xs text-neutral-400">Acknowledge</span>
                 </label>
             </div>
        </div>
    </div>
);
