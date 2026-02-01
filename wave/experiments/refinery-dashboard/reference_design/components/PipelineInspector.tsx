import React, { useEffect } from 'react';
import { PipelineId, PipelineStageConfig } from '../types';
import { PIPELINE_CONFIGS } from '../services/mockData';
import { UiRow, Badge, UiLink } from './Common';
import { RefreshCw, Database, Activity } from 'lucide-react';

interface PipelineInspectorProps {
    pipelineId: PipelineId;
    initialStage?: string;
    onStageSelect?: (stage: PipelineStageConfig) => void;
    onViewArtifacts?: (stage: PipelineStageConfig) => void;
}

export const PipelineInspector: React.FC<PipelineInspectorProps> = ({
    pipelineId,
    initialStage,
    onStageSelect,
    onViewArtifacts
}) => {
    const stages = PIPELINE_CONFIGS[pipelineId];
    const [selectedStageName, setSelectedStageName] = React.useState<string | null>(null);

    // Auto-select stage if provided via deep link
    useEffect(() => {
        if (initialStage && stages.some(s => s.name === initialStage)) {
            setSelectedStageName(initialStage);
        }
    }, [initialStage, stages]);

    const handleSelect = (stage: PipelineStageConfig) => {
        // Toggle if already selected? No, strictly select for inspection context.
        setSelectedStageName(stage.name);
        if (onStageSelect) onStageSelect(stage);
    };

    return (
        <div className="flex flex-col h-full overflow-hidden">
            <div className="p-6 border-b border-neutral-800">
                <h2 className="text-lg font-semibold text-neutral-200">{pipelineId}</h2>
                <div className="mt-2 flex items-center space-x-4 text-xs text-neutral-500 font-mono">
                    <span className="flex items-center"><Activity className="w-3 h-3 mr-1" /> ONLINE</span>
                    <span className="flex items-center"><RefreshCw className="w-3 h-3 mr-1" /> AUTO</span>
                </div>
            </div>

            <div className="flex-1 overflow-y-auto p-6 relative">
                <div className="absolute left-9 top-6 bottom-6 w-px bg-neutral-800" />

                <div className="space-y-8 relative">
                    {stages.map((stage, idx) => {
                        const isLoopStart = stage.isLoopStart;
                        const isLoopEnd = stage.isLoopEnd;

                        // Dynamic Loop Calculation
                        let loopHeightStyle = {};
                        if (isLoopEnd && stage.loopTarget) {
                            const targetIdx = stages.findIndex(s => s.name === stage.loopTarget);
                            if (targetIdx !== -1) {
                                const distance = idx - targetIdx;
                                loopHeightStyle = {
                                    height: `calc(100% * ${distance} + ${distance * 32}px)`, // 32px accounts for margin/padding gaps
                                    top: '50%',
                                    transform: 'translateY(-100%)'
                                };
                            }
                        }

                        return (
                            <div key={stage.name} className="relative group">
                                {/* Connector Node */}
                                <div className="absolute left-3 top-3 w-3 h-3 -ml-1.5 z-10 flex items-center justify-center bg-neutral-900">
                                    <div className={`w-1.5 h-1.5 rounded-full ${selectedStageName === stage.name ? 'bg-neutral-200' : 'bg-neutral-600 group-hover:bg-neutral-400'}`} />
                                </div>

                                {/* Main Row */}
                                <div
                                    onClick={() => handleSelect(stage)}
                                    tabIndex={0}
                                    role="button"
                                    onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); handleSelect(stage); } }}
                                    className={`
                                        ml-8 p-3 rounded border border-transparent cursor-pointer transition-all outline-none
                                        ${selectedStageName === stage.name
                                            ? 'bg-neutral-900 border-neutral-800 shadow-sm'
                                            : 'hover:bg-neutral-900/50 hover:border-neutral-800/50 focus-visible:bg-neutral-900/30 focus-visible:border-neutral-800/50'
                                        }
                                    `}
                                >
                                    <div className="flex justify-between items-center mb-1">
                                        <span className={`text-sm font-medium ${selectedStageName === stage.name ? 'text-white' : 'text-neutral-400'}`}>
                                            {stage.name}
                                        </span>
                                        <Badge status={stage.status} />
                                    </div>
                                    <div className="flex justify-between text-xs text-neutral-600 font-mono">
                                        <span>Q: {stage.queueDepth}</span>
                                        <span>{(Date.now() - stage.lastUpdated) / 60000 < 60 ? 'Just now' : '1h ago'}</span>
                                    </div>
                                </div>

                                {/* Loop Visualization */}
                                {isLoopEnd && stage.loopTarget && (
                                    <div
                                        className="absolute -left-2 w-4 pointer-events-none opacity-50 border-l border-b border-t border-dashed border-neutral-600 rounded-l-lg"
                                        style={loopHeightStyle}
                                    >
                                        <div className="absolute -right-2 top-0 mt-2 text-[10px] text-neutral-600 rotate-90 origin-left whitespace-nowrap">LOOP</div>
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>
            </div>

            {selectedStageName && (
                <div className="border-t border-neutral-800 bg-neutral-925 p-6 animate-in slide-in-from-bottom-4 duration-200">
                   <StageDetail
                        stage={stages.find(s => s.name === selectedStageName)!}
                        onViewArtifacts={onViewArtifacts}
                   />
                </div>
            )}
        </div>
    );
};

const StageDetail: React.FC<{ stage: PipelineStageConfig; onViewArtifacts?: (s: PipelineStageConfig) => void }> = ({ stage, onViewArtifacts }) => (
    <div className="space-y-4">
        <div>
            <h4 className="text-sm font-semibold text-neutral-300 mb-1">Function</h4>
            <p className="text-xs text-neutral-500 leading-relaxed">{stage.description}</p>
        </div>

        <div className="grid grid-cols-2 gap-4">
            <div className="bg-neutral-900 p-3 rounded">
                <div className="text-[10px] uppercase text-neutral-600 mb-1">Current Load</div>
                <div className="text-lg font-mono text-neutral-300">{stage.queueDepth} <span className="text-xs text-neutral-600">items</span></div>
            </div>
            <div className="bg-neutral-900 p-3 rounded">
                 <div className="text-[10px] uppercase text-neutral-600 mb-1">Throughput</div>
                 <div className="text-lg font-mono text-neutral-300">~450 <span className="text-xs text-neutral-600">/min</span></div>
            </div>
        </div>

        <div className="pt-2 flex justify-end">
            <UiLink onClick={() => onViewArtifacts && onViewArtifacts(stage)}>
                View produced artifacts &rarr;
            </UiLink>
        </div>
    </div>
);
