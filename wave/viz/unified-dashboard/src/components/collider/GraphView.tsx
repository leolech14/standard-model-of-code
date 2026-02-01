import React, { useEffect, useState, useRef } from 'react';
import dynamic from 'next/dynamic';
import { ColliderNode, ColliderEdge } from '@/lib/types';

// Dynamic import to prevent SSR issues with Three.js/ForceGraph
const ForceGraph3D = dynamic(() => import('react-force-graph-3d'), {
    ssr: false,
    loading: () => (
        <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-12 h-12 border-4 border-emerald-500/20 border-t-emerald-500 rounded-full animate-spin" />
        </div>
    )
});

interface GraphViewProps {
    onNodeClick?: (node: ColliderNode | null) => void;
}

export default function GraphView({ onNodeClick }: GraphViewProps) {
    const [graphData, setGraphData] = useState<{ nodes: ColliderNode[], links: ColliderEdge[] }>({ nodes: [], links: [] });
    const [isLoading, setIsLoading] = useState(true);
    const fgRef = useRef<any>(null);

    useEffect(() => {
        const fetchGraph = async () => {
            try {
                const res = await fetch('/api/collider/graph');
                const data = await res.json();

                // Map edges to links if needed (ForceGraph expects 'links' with 'source'/'target')
                const links = data.edges || data.links || [];
                setGraphData({
                    nodes: data.nodes || [],
                    links: links
                });
            } catch (e) {
                console.error("Failed to load graph data:", e);
            } finally {
                setIsLoading(false);
            }
        };

        fetchGraph();
    }, []);

    const getNodeColor = (node: ColliderNode) => {
        const level = node.level || 0;
        if (level <= 2) return '#10b981'; // Emerald (L1-L2)
        if (level <= 10) return '#3b82f6'; // Blue (L3-L10)
        return '#a855f7'; // Purple (L11+)
    };

    return (
        <div className="w-full h-full relative bg-black">
            {!isLoading && (
                <ForceGraph3D
                    ref={fgRef}
                    graphData={graphData}
                    nodeLabel={(node: any) => `${node.name || node.id} [L${node.level || '?'}]`}
                    nodeColor={(node: any) => getNodeColor(node as ColliderNode)}
                    nodeRelSize={4}
                    onNodeClick={(node: any) => onNodeClick && onNodeClick(node as ColliderNode)}
                    linkWidth={0.5}
                    linkColor={() => 'rgba(255,255,255,0.1)'}
                    linkDirectionalParticles={1}
                    linkDirectionalParticleSpeed={0.005}
                    backgroundColor="rgba(0,0,0,0)"
                    showNavInfo={false}
                />
            )}

            {/* Visual Overlays */}
            <div className="absolute inset-0 pointer-events-none select-none">
                <div className="absolute top-6 left-6 flex flex-col gap-1">
                    <span className="text-[10px] font-bold text-emerald-500/50 uppercase tracking-widest">Topology Monitor</span>
                    <span className="text-[8px] text-neutral-600 font-mono">ACTIVE_EMISSIVE_MODE</span>
                </div>
            </div>

            <div className="absolute bottom-6 left-6 right-6 flex items-center justify-between pointer-events-none">
                <div className="glass px-4 py-2 rounded-xl text-xs flex items-center gap-3 pointer-events-auto">
                    <div className="flex -space-x-2">
                        <div className="w-5 h-5 rounded-full bg-emerald-500 border-2 border-black" />
                        <div className="w-5 h-5 rounded-full bg-blue-500 border-2 border-black" />
                        <div className="w-5 h-5 rounded-full bg-purple-500 border-2 border-black" />
                    </div>
                    <span className="text-neutral-400 font-mono">Projectome Sync (L7 Engine)</span>
                </div>
                <div className="text-[10px] font-mono text-neutral-600 uppercase">Engine: Gemini-Flash-v2</div>
            </div>
        </div>
    );
}
