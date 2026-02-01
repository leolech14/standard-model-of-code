import React, { useMemo, useState } from 'react';
import { Run, PipelineStageConfig, CanonicalStage } from '../types';
import { Badge } from './Common';

interface ProcessedRun extends Run {
    startMs: number;
    durationMs: number;
    endMs: number;
    lane: number;
    segmentConfig: Segment[];
}

interface Segment {
    stage: CanonicalStage;
    widthPct: number;
    status: 'completed' | 'active' | 'failed' | 'pending';
    colorClass: string;
}

const parseDuration = (d: string): number => {
    const m = d.match(/(\d+)m/);
    const s = d.match(/(\d+)s/);
    const min = m ? parseInt(m[1]) : 0;
    const sec = s ? parseInt(s[1]) : 0;
    return (min * 60 + sec) * 1000;
};

// Standardized color mapping for stages
const STAGE_COLORS: Record<string, string> = {
    [CanonicalStage.Capture]: 'bg-neutral-500',
    [CanonicalStage.Separate]: 'bg-orange-600', // Special styling handled in render
    [CanonicalStage.Clean]: 'bg-cyan-600',
    [CanonicalStage.Enrich]: 'bg-violet-600',
    [CanonicalStage.Mix]: 'bg-indigo-600',
    [CanonicalStage.Distill]: 'bg-amber-600',
    [CanonicalStage.Publish]: 'bg-emerald-600',
};

const getStageColor = (stage: CanonicalStage, status: 'completed'|'active'|'failed'|'pending'): string => {
   if (status === 'failed') return 'bg-rose-500';
   if (status === 'pending') return 'bg-neutral-800/40';

   return STAGE_COLORS[stage] || 'bg-neutral-600';
};

interface RunsTimelineProps {
    runs: Run[];
    pipelines: Record<string, PipelineStageConfig[]>;
    onSelect: (run: Run) => void;
}

export const RunsTimeline: React.FC<RunsTimelineProps> = ({ runs, pipelines, onSelect }) => {
    const [hoveredRun, setHoveredRun] = useState<ProcessedRun | null>(null);

    // 1. Parse, Sort, and Calculate Segments
    const { packedRuns, lanesCount, minTime, maxTime } = useMemo(() => {
        if (runs.length === 0) return { packedRuns: [], lanesCount: 0, minTime: 0, maxTime: 0 };

        const parsed: ProcessedRun[] = runs.map(r => {
            const durationMs = parseDuration(r.duration);

            // Calculate Segments Logic (Deterministic)
            const stages = pipelines[r.pipelineId] || [];
            const segmentCount = stages.length;

            // Replicate deterministic status logic from RunInspector to match visuals
            const runHash = r.id.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
            const stopIndex = r.status === 'success' ? segmentCount - 1 : (runHash % Math.max(1, segmentCount));

            // Distribute duration roughly equally among executed stages
            // Note: If Failed/Running, the total duration represents time elapsed so far.
            // So we divide current duration by (stopIndex + 1)
            const activeStageCount = stopIndex + 1;
            const segmentWidth = 100 / activeStageCount; // Percentage width for active segments

            const segments: Segment[] = stages.map((stage, i) => {
                let status: Segment['status'] = 'pending';
                if (i < stopIndex) status = 'completed';
                else if (i === stopIndex) {
                    if (r.status === 'success') status = 'completed';
                    else if (r.status === 'failed') status = 'failed';
                    else status = 'active';
                }

                // If status is pending, it has 0 width in the "elapsed time" bar
                // unless we wanted to project future time, but here we show actuals.
                // However, for visualization consistency, we only generate segments that have "happened"
                // or are "happening". Pending stages are implicitly not shown in the bar duration.

                return {
                    stage: stage.name,
                    widthPct: status === 'pending' ? 0 : segmentWidth,
                    status,
                    colorClass: getStageColor(stage.name, status)
                };
            }).filter(s => s.status !== 'pending'); // Only keep visible segments

            return {
                ...r,
                startMs: r.startTime,
                durationMs,
                endMs: r.startTime + durationMs,
                lane: 0, // placeholder
                segmentConfig: segments
            };
        }).sort((a, b) => a.startMs - b.startMs);

        const minTime = parsed.length > 0 ? parsed[0].startMs : Date.now() - 86400000;
        const lastRunEnd = parsed.length > 0 ? Math.max(...parsed.map(r => r.endMs)) : Date.now();
        const rawSpan = lastRunEnd - minTime;
        const maxTime = lastRunEnd + (Math.max(rawSpan, 1000) * 0.05); // 5% buffer

        const totalSpan = maxTime - minTime;

        // 2. Packing Algorithm
        const lanes: number[] = [];

        const packed = parsed.map(run => {
            const buffer = totalSpan * 0.005;
            let laneIndex = lanes.findIndex(lastEnd => lastEnd + buffer < run.startMs);

            if (laneIndex === -1) {
                laneIndex = lanes.length;
                lanes.push(0);
            }
            lanes[laneIndex] = run.endMs;
            return { ...run, lane: laneIndex };
        });

        return {
            packedRuns: packed,
            lanesCount: lanes.length,
            minTime,
            maxTime
        };
    }, [runs, pipelines]);

    if (runs.length === 0) return null;

    const totalDuration = maxTime - minTime;
    const LANE_HEIGHT = 24; // px
    const BAR_HEIGHT = 14; // px
    const totalHeight = Math.max(140, lanesCount * LANE_HEIGHT + 40);

    const formatTime = (ms: number) => {
        const d = new Date(ms);
        return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    return (
        <div className="w-full mb-6 select-none animate-in fade-in duration-500">
            {/* Context Header */}
            <div className="flex items-center justify-between mb-2 h-6 px-1">
                <div className="text-[10px] text-neutral-500 uppercase font-bold tracking-wider">
                    Pipeline Activity ({lanesCount} Tracks)
                </div>
                {hoveredRun ? (
                    <div className="flex items-center space-x-3 text-xs animate-in slide-in-from-bottom-2 fade-in duration-150">
                        <Badge status={hoveredRun.status} />
                        <span className="font-mono text-neutral-300">{hoveredRun.id}</span>
                        <span className="text-neutral-500">{hoveredRun.duration}</span>
                        <div className="flex space-x-1">
                            {hoveredRun.segmentConfig.map((s, i) => (
                                <div key={i} className={`w-1.5 h-1.5 rounded-full ${s.colorClass}`} />
                            ))}
                        </div>
                    </div>
                ) : (
                    <div className="text-[10px] text-neutral-600">Hover for stage details</div>
                )}
            </div>

            {/* Timeline Canvas */}
            <div
                className="relative w-full bg-neutral-900/40 border border-neutral-800 rounded-lg overflow-hidden"
                style={{ height: totalHeight }}
            >
                {/* Time Grid Lines */}
                {Array.from({ length: 5 }).map((_, i) => {
                    const left = (i / 4) * 100;
                    const time = minTime + (totalDuration * (i / 4));
                    return (
                        <div key={i} className="absolute top-0 bottom-0 border-l border-neutral-800/30 flex flex-col justify-end pointer-events-none" style={{ left: `${left}%` }}>
                            <span className="text-[9px] font-mono text-neutral-700 ml-1 mb-1">{formatTime(time)}</span>
                        </div>
                    );
                })}

                {/* Bars */}
                <div className="absolute inset-0 top-4 bottom-6 overflow-y-auto hide-scrollbar">
                    {packedRuns.map(run => {
                        const leftPct = ((run.startMs - minTime) / totalDuration) * 100;
                        const widthPct = Math.max(0.2, (run.durationMs / totalDuration) * 100);

                        return (
                            <div
                                key={run.id}
                                onClick={(e) => { e.stopPropagation(); onSelect(run); }}
                                onMouseEnter={() => setHoveredRun(run)}
                                onMouseLeave={() => setHoveredRun(null)}
                                className={`
                                    absolute rounded-sm cursor-pointer transition-all duration-150 z-10 flex overflow-hidden
                                    ${hoveredRun?.id === run.id ? 'ring-1 ring-white/50 z-20 scale-y-110 shadow-lg' : 'opacity-90 hover:opacity-100'}
                                `}
                                style={{
                                    left: `${leftPct}%`,
                                    width: `${widthPct}%`,
                                    top: run.lane * LANE_HEIGHT + (LANE_HEIGHT - BAR_HEIGHT) / 2,
                                    height: BAR_HEIGHT,
                                    minWidth: '4px'
                                }}
                            >
                                {/* Render Segments */}
                                {run.segmentConfig.map((seg, i) => (
                                    <div
                                        key={i}
                                        style={{ width: `${seg.widthPct}%` }}
                                        className={`h-full relative ${seg.status === 'active' ? 'animate-pulse brightness-110' : ''}`}
                                    >
                                        {/* "Branching" Visual for Separate Stage */}
                                        {seg.stage === CanonicalStage.Separate ? (
                                            <div className="h-full w-full flex flex-col justify-between py-[2px] bg-neutral-900/50">
                                                <div className={`h-[3px] w-full ${seg.colorClass} opacity-80`} />
                                                <div className={`h-[3px] w-full ${seg.colorClass} opacity-80`} />
                                            </div>
                                        ) : (
                                            <div className={`h-full w-full ${seg.colorClass} border-r border-black/20`} />
                                        )}
                                    </div>
                                ))}
                            </div>
                        );
                    })}
                </div>

                {/* Now Indicator */}
                <div className="absolute top-0 bottom-0 right-0 w-px bg-emerald-500/20 z-0 pointer-events-none" />
            </div>
        </div>
    );
};
