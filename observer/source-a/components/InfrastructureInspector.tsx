import React from 'react';
import { SectionHeader, Badge } from './Common';
import {
    Database, Server, Activity, Cpu,
    Network, HardDrive, Zap, RefreshCw,
    Signal, Wifi, Box, TrendingUp, AlertTriangle
} from 'lucide-react';
import { Run, Artifact } from '../types';

interface InfraInspectorProps {
    type: 'buffer' | 'cluster' | 'network' | 'storage' | 'projects';
    data?: any;
}

export const InfrastructureInspector: React.FC<InfraInspectorProps> = ({ type, data }) => {

    // Render Buffer Inspector
    if (type === 'buffer') {
        const partitions = [
            { id: 'ingest_01', load: 85, cap: '1GB' },
            { id: 'ingest_02', load: 42, cap: '1GB' },
            { id: 'proc_main', load: 92, cap: '4GB' },
            { id: 'proc_sec', load: 12, cap: '4GB' },
            { id: 'egress_bk', load: 5, cap: '2GB' },
        ];

        return (
            <div className="flex flex-col h-full bg-neutral-950">
                <div className="p-6 border-b border-neutral-800">
                    <div className="flex items-center space-x-3 mb-2 text-indigo-500">
                        <Database className="w-6 h-6" />
                        <h2 className="text-lg font-semibold text-neutral-200">Global Buffer State</h2>
                    </div>
                    <p className="text-sm text-neutral-500">Real-time memory allocation across distributed queues.</p>
                </div>
                <div className="p-6 overflow-y-auto">
                    <div className="grid grid-cols-2 gap-4 mb-8">
                        <div className="bg-neutral-900 p-4 rounded border border-neutral-800">
                            <div className="text-[10px] uppercase text-neutral-500">Total Utilization</div>
                            <div className="text-2xl font-mono text-neutral-200 mt-1">64.2%</div>
                        </div>
                        <div className="bg-neutral-900 p-4 rounded border border-neutral-800">
                             <div className="text-[10px] uppercase text-neutral-500">Peak Rate (1m)</div>
                            <div className="text-2xl font-mono text-neutral-200 mt-1">12k <span className="text-sm text-neutral-600">ops/s</span></div>
                        </div>
                    </div>

                    <SectionHeader title="Active Partitions" />
                    <div className="space-y-4">
                        {partitions.map(p => (
                            <div key={p.id} className="space-y-1">
                                <div className="flex justify-between text-xs font-mono text-neutral-400">
                                    <span>{p.id}</span>
                                    <span>{p.load}%</span>
                                </div>
                                <div className="w-full h-2 bg-neutral-900 rounded-full overflow-hidden">
                                    <div
                                        className={`h-full rounded-full ${p.load > 90 ? 'bg-rose-500' : 'bg-indigo-500'}`}
                                        style={{ width: `${p.load}%` }}
                                    />
                                </div>
                                <div className="text-[10px] text-neutral-600 text-right">Cap: {p.cap}</div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        );
    }

    // Render Cluster Inspector
    if (type === 'cluster') {
        return (
            <div className="flex flex-col h-full bg-neutral-950">
                <div className="p-6 border-b border-neutral-800">
                    <div className="flex items-center space-x-3 mb-2 text-emerald-500">
                        <Server className="w-6 h-6" />
                        <h2 className="text-lg font-semibold text-neutral-200">Processing Cluster</h2>
                    </div>
                    <p className="text-sm text-neutral-500">Node health and task distribution.</p>
                </div>
                <div className="p-6 overflow-y-auto">
                    <div className="grid grid-cols-4 gap-2 mb-8">
                        {Array.from({length: 16}).map((_, i) => {
                            const load = Math.random() * 100;
                            const isOnline = i < 14;
                            return (
                                <div key={i} className={`aspect-square rounded border flex flex-col items-center justify-center ${isOnline ? 'bg-neutral-900 border-neutral-800' : 'bg-neutral-950 border-neutral-900 opacity-50'}`}>
                                    <Cpu className={`w-4 h-4 mb-1 ${isOnline ? (load > 80 ? 'text-amber-500' : 'text-emerald-500') : 'text-neutral-700'}`} />
                                    <span className="text-[9px] font-mono text-neutral-500">N-{i+1}</span>
                                    {isOnline && <div className="w-8 h-0.5 bg-neutral-800 mt-1"><div className="h-full bg-emerald-500" style={{ width: `${load}%` }} /></div>}
                                </div>
                            )
                        })}
                    </div>

                    <div className="space-y-4">
                        <SectionHeader title="Cluster Metrics" />
                         <div className="flex items-center justify-between p-3 bg-neutral-900/50 rounded">
                            <span className="text-sm text-neutral-400">CPU Aggregate</span>
                            <span className="font-mono text-emerald-400">42%</span>
                         </div>
                         <div className="flex items-center justify-between p-3 bg-neutral-900/50 rounded">
                            <span className="text-sm text-neutral-400">Memory Pressure</span>
                            <span className="font-mono text-amber-400">78%</span>
                         </div>
                         <div className="flex items-center justify-between p-3 bg-neutral-900/50 rounded">
                            <span className="text-sm text-neutral-400">Active Threads</span>
                            <span className="font-mono text-neutral-200">1,204</span>
                         </div>
                    </div>
                </div>
            </div>
        );
    }

    // Render Network Inspector
    if (type === 'network') {
        return (
            <div className="flex flex-col h-full bg-neutral-950">
                 <div className="p-6 border-b border-neutral-800">
                    <div className="flex items-center space-x-3 mb-2 text-blue-500">
                        <Network className="w-6 h-6" />
                        <h2 className="text-lg font-semibold text-neutral-200">Network Mesh</h2>
                    </div>
                    <p className="text-sm text-neutral-500">Ingress/Egress traffic throughput.</p>
                </div>
                <div className="p-6 overflow-y-auto">
                    <div className="h-48 bg-neutral-900/50 border border-neutral-800 rounded mb-6 relative overflow-hidden flex items-end px-2 space-x-1">
                         {Array.from({length: 40}).map((_, i) => (
                             <div
                                key={i}
                                className="flex-1 bg-blue-500/20 hover:bg-blue-500/40 transition-colors rounded-t-sm"
                                style={{ height: `${20 + Math.random() * 60}%` }}
                             />
                         ))}
                    </div>

                     <div className="grid grid-cols-2 gap-4">
                        <div className="p-4 border border-neutral-800 rounded bg-neutral-900/20">
                            <div className="flex items-center space-x-2 text-neutral-400 mb-2">
                                <Signal className="w-4 h-4" />
                                <span className="text-xs uppercase font-semibold">Inbound</span>
                            </div>
                            <div className="text-2xl font-mono text-neutral-200">420.5 <span className="text-sm text-neutral-600">MB/s</span></div>
                        </div>
                        <div className="p-4 border border-neutral-800 rounded bg-neutral-900/20">
                            <div className="flex items-center space-x-2 text-neutral-400 mb-2">
                                <Wifi className="w-4 h-4" />
                                <span className="text-xs uppercase font-semibold">Outbound</span>
                            </div>
                            <div className="text-2xl font-mono text-neutral-200">312.0 <span className="text-sm text-neutral-600">MB/s</span></div>
                        </div>
                     </div>
                </div>
            </div>
        );
    }

    // Render Project List
    if (type === 'projects') {
        const projects = data?.projects || [];
        const runs = (data?.runs || []) as Run[];
        const artifacts = (data?.artifacts || []) as Artifact[];

        // Calculate Project Stats
        const projectStats = projects.map((p: string) => {
            const pRuns = runs.filter(r => r.projectId === p).sort((a, b) => b.startTime - a.startTime);
            const pArtifacts = artifacts.filter(a => a.projectId === p);

            // Health Score: 100 - (Failure Rate * 100)
            const last10Runs = pRuns.slice(0, 10);
            const failCount = last10Runs.filter(r => r.status === 'failed').length;
            const health = Math.max(0, 100 - (failCount * 20)); // Heavy penalty for recent fails

            const lastActive = pRuns[0]?.startTime || 0;
            const timeSince = Date.now() - lastActive;
            const timeStr = timeSince < 60000 ? 'Just now' :
                            timeSince < 3600000 ? `${Math.floor(timeSince/60000)}m ago` :
                            `${Math.floor(timeSince/3600000)}h ago`;

            return {
                id: p,
                health,
                runCount: pRuns.length,
                artifactCount: pArtifacts.length,
                lastActive: timeStr,
                recentRuns: last10Runs.reverse(), // For sparkline
            };
        });

        return (
             <div className="flex flex-col h-full bg-neutral-950">
                <div className="p-6 border-b border-neutral-800 shrink-0">
                    <div className="flex items-center space-x-3 mb-2 text-neutral-200">
                        <Box className="w-6 h-6" />
                        <h2 className="text-lg font-semibold">Active Projects</h2>
                    </div>
                    <p className="text-sm text-neutral-500">Performance and resource isolation metrics.</p>
                </div>

                <div className="p-6 overflow-y-auto flex-1 space-y-4">
                    {projectStats.map((stat: any) => (
                        <div key={stat.id} className="p-4 bg-neutral-900/40 border border-neutral-800 rounded-lg hover:border-neutral-700 transition-colors group">
                            <div className="flex items-start justify-between mb-4">
                                <div>
                                    <h3 className="text-sm font-semibold text-neutral-200 group-hover:text-white transition-colors">{stat.id}</h3>
                                    <div className="flex items-center space-x-3 mt-1">
                                        <div className="flex items-center space-x-1.5">
                                            <div className={`w-1.5 h-1.5 rounded-full ${stat.health > 80 ? 'bg-emerald-500' : stat.health > 50 ? 'bg-amber-500' : 'bg-rose-500'}`} />
                                            <span className="text-[10px] text-neutral-500 font-mono">{stat.health}% Health</span>
                                        </div>
                                        <span className="text-[10px] text-neutral-600">•</span>
                                        <span className="text-[10px] text-neutral-500 font-mono">{stat.lastActive}</span>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <div className="text-xs text-neutral-400 font-mono">{stat.artifactCount} <span className="text-neutral-600">items</span></div>
                                </div>
                            </div>

                            {/* Mini Sparkline */}
                            <div className="h-8 flex items-end space-x-1 mb-2">
                                {stat.recentRuns.map((r: Run) => (
                                    <div
                                        key={r.id}
                                        className={`flex-1 rounded-t-sm ${r.status === 'success' ? 'bg-emerald-900/60' : r.status === 'failed' ? 'bg-rose-900/60' : 'bg-blue-900/60'}`}
                                        style={{ height: '100%' }}
                                    >
                                        <div className={`w-full ${r.status === 'success' ? 'bg-emerald-500' : r.status === 'failed' ? 'bg-rose-500' : 'bg-blue-500'}`} style={{ height: '20%' }} />
                                    </div>
                                ))}
                                {/* Fill empty if not enough runs */}
                                {Array.from({length: Math.max(0, 10 - stat.recentRuns.length)}).map((_, i) => (
                                    <div key={`empty-${i}`} className="flex-1 bg-neutral-800/20 rounded-t-sm h-full" />
                                ))}
                            </div>

                            <div className="flex justify-between text-[9px] text-neutral-600 uppercase tracking-wider font-semibold">
                                <span>Recent Activity</span>
                                <span>{stat.runCount} Runs Total</span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        )
    }

    return <div>Unknown Infrastructure Type</div>;
};
