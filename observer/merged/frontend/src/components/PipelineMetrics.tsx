import React, { useMemo } from 'react';
import { Run, PipelineId } from '../types';
import { SectionHeader } from './Common';
import { Activity, TrendingUp, AlertOctagon, Clock } from 'lucide-react';

interface PipelineMetricsProps {
    runs: Run[];
}

const parseDuration = (d: string): number => {
    const m = d.match(/(\d+)m/);
    const s = d.match(/(\d+)s/);
    const min = m ? parseInt(m[1]) : 0;
    const sec = s ? parseInt(s[1]) : 0;
    return min * 60 + sec; // seconds
};

export const PipelineMetrics: React.FC<PipelineMetricsProps> = ({ runs }) => {
    // Process Data
    const metrics = useMemo(() => {
        const sortedRuns = [...runs].sort((a, b) => a.startTime - b.startTime);

        // 1. Durations over time (Moving Average)
        const durationPoints = sortedRuns.map((r, i) => {
            return {
                index: i,
                value: parseDuration(r.duration),
                pipeline: r.pipelineId,
                status: r.status
            };
        });

        // 2. Failure Rates per Pipeline
        const failures: Record<string, { total: number, failed: number }> = {};
        Object.values(PipelineId).forEach(pid => failures[pid] = { total: 0, failed: 0 });

        sortedRuns.forEach(r => {
            if (failures[r.pipelineId]) {
                failures[r.pipelineId].total++;
                if (r.status === 'failed') failures[r.pipelineId].failed++;
            }
        });

        // 3. Avg Duration Calculation
        const avgDuration = durationPoints.reduce((acc, curr) => acc + curr.value, 0) / (durationPoints.length || 1);

        return { durationPoints, failures, avgDuration };
    }, [runs]);

    // Chart Dimensions
    const height = 150;
    const width = 100; // Percent
    const maxDuration = Math.max(...metrics.durationPoints.map(p => p.value), 60);

    // Generate Polyline Points
    const getPolyline = (pid: PipelineId) => {
        const relevantRuns = metrics.durationPoints.filter(p => p.pipeline === pid);
        if (relevantRuns.length < 2) return '';

        // Normalize X across the global timeline to show relative frequency
        // We map the global index to X to preserve temporal spacing between pipelines
        const totalPoints = metrics.durationPoints.length;

        return relevantRuns.map(p => {
            const x = (p.index / (totalPoints - 1)) * 100; // %
            const y = height - ((p.value / maxDuration) * height);
            return `${x},${y}`;
        }).join(' ');
    };

    return (
        <div className="flex flex-col h-full bg-neutral-950">
            <div className="p-6 border-b border-neutral-800 shrink-0">
                <div className="flex items-center space-x-3 mb-2 text-indigo-400">
                    <TrendingUp className="w-6 h-6" />
                    <h2 className="text-lg font-semibold text-neutral-200">Pipeline Analytics</h2>
                </div>
                <p className="text-sm text-neutral-500">Historical performance and reliability trends.</p>
            </div>

            <div className="flex-1 overflow-y-auto p-6 space-y-8">
                {/* 1. Duration Trend Chart */}
                <div className="bg-neutral-900/30 border border-neutral-800 rounded-lg p-4">
                    <div className="flex justify-between items-center mb-6">
                        <SectionHeader title="Execution Duration Trend" />
                        <div className="flex items-center space-x-4 text-[10px] font-mono">
                            <div className="flex items-center"><span className="w-2 h-2 rounded-full bg-blue-500 mr-2" /> Refinery</div>
                            <div className="flex items-center"><span className="w-2 h-2 rounded-full bg-emerald-500 mr-2" /> Factory</div>
                        </div>
                    </div>

                    <div className="relative h-[150px] w-full">
                        {/* Grid Lines */}
                        <div className="absolute inset-0 flex flex-col justify-between pointer-events-none opacity-20">
                            {[100, 75, 50, 25, 0].map((pct, i) => (
                                <div key={i} className="w-full border-t border-neutral-600 h-0 text-[9px] text-neutral-500 pl-1 pt-0.5">
                                    {Math.round((maxDuration * (pct/100)))}s
                                </div>
                            ))}
                        </div>

                        <svg className="absolute inset-0 w-full h-full overflow-visible" preserveAspectRatio="none" viewBox={`0 0 100 ${height}`}>
                            <polyline
                                points={getPolyline(PipelineId.Refinery)}
                                fill="none"
                                stroke="#3b82f6"
                                strokeWidth="1.5"
                                vectorEffect="non-scaling-stroke"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                className="opacity-80"
                            />
                            <polyline
                                points={getPolyline(PipelineId.Factory)}
                                fill="none"
                                stroke="#10b981"
                                strokeWidth="1.5"
                                vectorEffect="non-scaling-stroke"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                className="opacity-80"
                            />
                        </svg>
                    </div>
                </div>

                {/* 2. Key Metrics Cards */}
                <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 bg-neutral-900/30 border border-neutral-800 rounded-lg">
                        <div className="flex items-center space-x-2 text-neutral-500 mb-2 uppercase text-[10px] font-bold tracking-wider">
                            <Clock className="w-3.5 h-3.5" />
                            <span>Avg Duration</span>
                        </div>
                        <div className="text-3xl font-light text-neutral-200">
                            {Math.round(metrics.avgDuration)}<span className="text-sm font-normal text-neutral-600 ml-1">sec</span>
                        </div>
                    </div>
                    <div className="p-4 bg-neutral-900/30 border border-neutral-800 rounded-lg">
                        <div className="flex items-center space-x-2 text-neutral-500 mb-2 uppercase text-[10px] font-bold tracking-wider">
                            <Activity className="w-3.5 h-3.5" />
                            <span>Total Runs</span>
                        </div>
                        <div className="text-3xl font-light text-neutral-200">
                            {runs.length}
                        </div>
                    </div>
                </div>

                {/* 3. Reliability Breakdown */}
                <div>
                    <SectionHeader title="Reliability Profile" />
                    <div className="space-y-4 mt-4">
                        {Object.entries(metrics.failures).map(([pid, stats]) => {
                            const s = stats as { total: number, failed: number };
                            const failRate = s.total > 0 ? (s.failed / s.total) * 100 : 0;
                            const successRate = 100 - failRate;

                            return (
                                <div key={pid} className="group">
                                    <div className="flex justify-between items-end mb-2">
                                        <div className="flex items-center space-x-2">
                                            {failRate > 15 ? <AlertOctagon className="w-3.5 h-3.5 text-rose-500" /> : <div className="w-3.5" />}
                                            <span className="text-xs font-medium text-neutral-300">{pid.replace(' Pipeline', '')}</span>
                                        </div>
                                        <div className="text-xs font-mono text-neutral-500">
                                            <span className={failRate > 0 ? 'text-rose-400' : 'text-neutral-600'}>{s.failed} fails</span>
                                            <span className="mx-1">/</span>
                                            <span>{s.total} runs</span>
                                        </div>
                                    </div>
                                    <div className="h-2 w-full bg-neutral-900 rounded-full overflow-hidden flex">
                                        <div
                                            className="h-full bg-emerald-600 group-hover:bg-emerald-500 transition-colors"
                                            style={{ width: `${successRate}%` }}
                                        />
                                        <div
                                            className="h-full bg-rose-600 group-hover:bg-rose-500 transition-colors"
                                            style={{ width: `${failRate}%` }}
                                        />
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>
        </div>
    );
};
