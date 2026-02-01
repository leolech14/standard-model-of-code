import React, { useMemo } from 'react';
import { Artifact } from '../types';
import { SectionHeader } from './Common';
import { HardDrive, PieChart, File, Layers, Database } from 'lucide-react';

const parseSize = (sizeStr: string): number => {
    const num = parseFloat(sizeStr);
    if (sizeStr.includes('MB')) return num * 1024 * 1024;
    if (sizeStr.includes('KB')) return num * 1024;
    if (sizeStr.includes('GB')) return num * 1024 * 1024 * 1024;
    return num; // bytes
};

const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export const StorageAnalysis: React.FC<{ artifacts: Artifact[] }> = ({ artifacts }) => {
    const stats = useMemo(() => {
        let totalBytes = 0;
        const typeMap: Record<string, number> = {};
        const projectMap: Record<string, number> = {};

        artifacts.forEach(art => {
            const bytes = parseSize(art.size);
            totalBytes += bytes;

            // By Type
            typeMap[art.type] = (typeMap[art.type] || 0) + bytes;

            // By Project
            projectMap[art.projectId] = (projectMap[art.projectId] || 0) + bytes;
        });

        const sortedTypes = Object.entries(typeMap)
            .sort(([, a], [, b]) => b - a)
            .map(([label, bytes]) => ({ label, bytes, pct: (bytes / totalBytes) * 100 }));

        const sortedProjects = Object.entries(projectMap)
            .sort(([, a], [, b]) => b - a)
            .map(([label, bytes]) => ({ label, bytes, pct: (bytes / totalBytes) * 100 }));

        return { totalBytes, sortedTypes, sortedProjects };
    }, [artifacts]);

    return (
        <div className="flex flex-col h-full bg-neutral-950">
            <div className="p-6 border-b border-neutral-800 shrink-0">
                <div className="flex items-center space-x-3 mb-2 text-neutral-200">
                    <PieChart className="w-6 h-6 text-indigo-500" />
                    <h2 className="text-lg font-semibold">Storage Analysis</h2>
                </div>
                <p className="text-sm text-neutral-500">Repository footprint breakdown.</p>
            </div>

            <div className="flex-1 overflow-y-auto p-6 space-y-8">
                {/* Key Metrics */}
                <div className="grid grid-cols-2 gap-4">
                    <div className="p-5 bg-neutral-900/30 border border-neutral-800 rounded-lg">
                        <div className="flex items-center space-x-2 text-neutral-500 mb-2 uppercase text-[10px] font-bold tracking-wider">
                            <Database className="w-3.5 h-3.5" />
                            <span>Total Usage</span>
                        </div>
                        <div className="text-3xl font-light text-neutral-200">{formatBytes(stats.totalBytes)}</div>
                    </div>
                    <div className="p-5 bg-neutral-900/30 border border-neutral-800 rounded-lg">
                        <div className="flex items-center space-x-2 text-neutral-500 mb-2 uppercase text-[10px] font-bold tracking-wider">
                            <File className="w-3.5 h-3.5" />
                            <span>Object Count</span>
                        </div>
                        <div className="text-3xl font-light text-neutral-200">{artifacts.length.toLocaleString()}</div>
                    </div>
                </div>

                {/* Distribution by Type */}
                <div>
                    <SectionHeader title="Distribution by File Type" />
                    <div className="space-y-3 mt-4">
                        {stats.sortedTypes.map(item => (
                            <div key={item.label} className="group">
                                <div className="flex justify-between items-end mb-1">
                                    <div className="flex items-center space-x-2">
                                        <span className="text-xs font-mono uppercase bg-neutral-900 px-1.5 py-0.5 rounded text-neutral-400 border border-neutral-800">{item.label}</span>
                                    </div>
                                    <div className="text-xs text-neutral-500 font-mono">
                                        {formatBytes(item.bytes)} <span className="text-neutral-700 ml-1">({item.pct.toFixed(1)}%)</span>
                                    </div>
                                </div>
                                <div className="h-2 w-full bg-neutral-900 rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-indigo-600 rounded-full group-hover:bg-indigo-500 transition-colors"
                                        style={{ width: `${item.pct}%` }}
                                    />
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Distribution by Project */}
                <div>
                    <SectionHeader title="Usage by Project" />
                    <div className="space-y-3 mt-4">
                        {stats.sortedProjects.map(item => (
                            <div key={item.label} className="group">
                                <div className="flex justify-between items-end mb-1">
                                    <div className="flex items-center space-x-2">
                                        <Layers className="w-3 h-3 text-neutral-600" />
                                        <span className="text-sm text-neutral-300">{item.label}</span>
                                    </div>
                                    <div className="text-xs text-neutral-500 font-mono">
                                        {formatBytes(item.bytes)}
                                    </div>
                                </div>
                                <div className="h-1.5 w-full bg-neutral-900 rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-emerald-600 rounded-full group-hover:bg-emerald-500 transition-colors"
                                        style={{ width: `${item.pct}%` }}
                                    />
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};
