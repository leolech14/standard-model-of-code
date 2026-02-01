import React, { useMemo, useState } from 'react';
import { Run } from '../types';
import { Badge } from './Common';

interface ProcessedRun extends Run {
    startMs: number;
    durationMs: number;
    endMs: number;
    lane: number;
}

const parseDuration = (d: string): number => {
    const m = d.match(/(\d+)m/);
    const s = d.match(/(\d+)s/);
    const min = m ? parseInt(m[1]) : 0;
    const sec = s ? parseInt(s[1]) : 0;
    return (min * 60 + sec) * 1000;
};

interface RunsTimelineProps {
    runs: Run[];
    onSelect: (run: Run) => void;
}

export const RunsTimeline: React.FC<RunsTimelineProps> = ({ runs, onSelect }) => {
    const [hoveredRun, setHoveredRun] = useState<ProcessedRun | null>(null);

    // 1. Parse and Sort
    const { packedRuns, lanesCount, minTime, maxTime } = useMemo(() => {
        if (runs.length === 0) return { packedRuns: [], lanesCount: 0, minTime: 0, maxTime: 0 };

        const parsed = runs.map(r => {
            const durationMs = parseDuration(r.duration);
            return {
                ...r,
                startMs: r.startTime,
                durationMs,
                endMs: r.startTime + durationMs,
                lane: 0 // placeholder
            };
        }).sort((a, b) => a.startMs - b.startMs);

        const minTime = parsed.length > 0 ? parsed[0].startMs : Date.now() - 86400000;
        const maxTime = Date.now();
        const totalSpan = maxTime - minTime;

        // 2. Packing Algorithm (Greedy Lane Assignment)
        const lanes: number[] = []; // Stores the endMs of the last item in each lane

        const packed = parsed.map(run => {
            // Find a lane where this run fits (starts after the last item ended + buffer)
            // Buffer is 0.5% of total span to prevent visual touching
            const buffer = totalSpan * 0.005;

            let laneIndex = lanes.findIndex(lastEnd => lastEnd + buffer < run.startMs);

            if (laneIndex === -1) {
                // No existing lane fits, start a new one
                laneIndex = lanes.length;
                lanes.push(0);
            }

            // Update lane end time
            lanes[laneIndex] = run.endMs;

            return { ...run, lane: laneIndex };
        });

        return {
            packedRuns: packed,
            lanesCount: lanes.length,
            minTime,
            maxTime
        };
    }, [runs]);

    if (runs.length === 0) return null;

    const totalDuration = maxTime - minTime;
    const LANE_HEIGHT = 20; // px
    const GAP = 4; // px
    const totalHeight = Math.max(120, lanesCount * (LANE_HEIGHT + GAP) + 40); // Min height 120, or dynamic

    const formatTime = (ms: number) => {
        const d = new Date(ms);
        return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    return (
        <div className="w-full mb-6 select-none animate-in fade-in duration-500">
            {/* Context Header (Progressive Disclosure) */}
            <div className="flex items-center justify-between mb-2 h-6 px-1">
                <div className="text-[10px] text-neutral-500 uppercase font-bold tracking-wider">
                    Timeline Activity ({lanesCount} Tracks)
                </div>
                {hoveredRun ? (
                    <div className="flex items-center space-x-3 text-xs animate-in slide-in-from-bottom-2 fade-in duration-150">
                        <Badge status={hoveredRun.status} />
                        <span className="font-mono text-neutral-300">{hoveredRun.id}</span>
                        <span className="text-neutral-500">{hoveredRun.duration}</span>
                        <span className="text-neutral-500">@ {new Date(hoveredRun.startTime).toLocaleTimeString()}</span>
                    </div>
                ) : (
                    <div className="text-[10px] text-neutral-600">Hover for details</div>
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
                        const widthPct = Math.max(0.2, (run.durationMs / totalDuration) * 100); // Min width 0.2% visibility

                        let colorClass = 'bg-neutral-600';
                        if (run.status === 'success') colorClass = 'bg-emerald-500/80 hover:bg-emerald-400';
                        if (run.status === 'failed') colorClass = 'bg-rose-500/80 hover:bg-rose-400';
                        if (run.status === 'running') colorClass = 'bg-blue-500/80 hover:bg-blue-400 animate-pulse';

                        return (
                            <div
                                key={run.id}
                                onClick={(e) => { e.stopPropagation(); onSelect(run); }}
                                onMouseEnter={() => setHoveredRun(run)}
                                onMouseLeave={() => setHoveredRun(null)}
                                className={`
                                    absolute h-3 rounded-full cursor-pointer transition-all duration-150 z-10
                                    ${colorClass}
                                    ${hoveredRun?.id === run.id ? 'ring-1 ring-white/50 z-20 scale-y-125 shadow-lg' : 'opacity-80 hover:opacity-100'}
                                `}
                                style={{
                                    left: `${leftPct}%`,
                                    width: `${widthPct}%`,
                                    top: run.lane * (LANE_HEIGHT),
                                    minWidth: '2px'
                                }}
                            />
                        );
                    })}
                </div>

                {/* Now Indicator */}
                <div className="absolute top-0 bottom-0 right-0 w-px bg-emerald-500/20 z-0" />
            </div>
        </div>
    );
};
