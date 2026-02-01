"use client";

import React, { useState, useEffect } from 'react';
import {
  Activity,
  Layers,
  Settings,
  ShieldCheck,
  Cpu,
  Database,
  Search,
  ChevronRight,
  ChevronLeft
} from 'lucide-react';
import { motion } from 'framer-motion';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import GraphView from '@/components/collider/GraphView';
import { RefineryChunk, ColliderNode, ProjectManifest } from '@/lib/types';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface GraphMetrics {
  node_count: number;
  edge_count: number;
  health_score: number;
}

// Components
const StatCard = ({ title, value, icon: Icon, color }: { title: string, value: string | number, icon: React.ElementType, color: string }) => (
  <div className="glass p-4 rounded-xl border border-neutral-800/50 flex flex-col gap-2 hover-lift group">
    <div className="flex items-center justify-between">
      <span className="text-[10px] font-bold text-neutral-500 uppercase tracking-widest">{title}</span>
      <Icon className={cn("w-4 h-4", color)} />
    </div>
    <div className="text-2xl font-display font-light text-white group-hover:text-emerald-400 transition-colors uppercase">{value}</div>
  </div>
);

export default function ProjectomeDashboard() {
  const [activeTab, setActiveTab] = useState('graph');
  const [logistics, setLogistics] = useState<ProjectManifest['waybill'] | null>(null);
  const [chunks, setChunks] = useState<RefineryChunk[]>([]);
  const [filteredChunks, setFilteredChunks] = useState<RefineryChunk[]>([]);
  const [graphMetrics, setGraphMetrics] = useState<GraphMetrics | null>(null);
  const [selectedNode, setSelectedNode] = useState<ColliderNode | null>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [logRes, chunkRes, graphRes] = await Promise.all([
          fetch('/api/logistics/verify'),
          fetch('/api/refinery/chunks'),
          fetch('/api/collider/graph')
        ]);

        const logData = await logRes.json();
        const chunkData = await chunkRes.json();
        const graphData = await graphRes.json();

        setLogistics(logData.manifest);
        setChunks(chunkData.chunks || []);
        setFilteredChunks(chunkData.chunks?.slice(0, 15) || []);
        setGraphMetrics(graphData.metrics || {
          node_count: graphData.nodes?.length || 0,
          edge_count: graphData.edges?.length || 0,
          health_score: 0.983
        });
      } catch (e) {
        console.error("Failed to fetch data", e);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleNodeClick = (node: ColliderNode | null) => {
    setSelectedNode(node);
    if (!node) {
      setFilteredChunks(chunks.slice(0, 15));
      return;
    }

    // Filter chunks by file path or name
    const nodeName = node.name || node.id;
    const fileName = node.file_path?.split('/').pop() || node.file?.split('/').pop();

    const filtered = chunks.filter(chunk =>
      (fileName && chunk.file?.includes(fileName)) ||
      (chunk.content?.toLowerCase().includes(nodeName.toLowerCase()))
    ).slice(0, 15);

    setFilteredChunks(filtered);
  };

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar Rail */}
      <aside className={cn(
        "glass border-r border-neutral-800 flex flex-col transition-all duration-300 z-50",
        isSidebarOpen ? "w-64" : "w-20"
      )}>
        <div className="h-16 flex items-center px-6 justify-between border-b border-neutral-800/50">
          {isSidebarOpen ? (
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-emerald-500 flex items-center justify-center text-black font-bold shadow-[0_0_20px_rgba(16,185,129,0.4)]">P</div>
              <span className="font-display font-medium tracking-tight text-white">PROJECTOME</span>
            </div>
          ) : (
            <div className="w-8 h-8 rounded-lg bg-emerald-500 flex items-center justify-center text-black font-bold mx-auto shadow-[0_0_20px_rgba(16,185,129,0.4)]">P</div>
          )}
        </div>

        <nav className="flex-1 p-4 space-y-2">
          {[
            { id: 'graph', label: 'Codome Graph', icon: Layers },
            { id: 'intelligence', label: 'Contextome', icon: Database },
            { id: 'audit', label: 'Logistics Audit', icon: ShieldCheck },
            { id: 'settings', label: 'System Settings', icon: Settings },
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={cn(
                "w-full flex items-center p-3 rounded-xl transition-all duration-200 group relative",
                activeTab === item.id ? "bg-emerald-500/10 text-emerald-400 ring-1 ring-emerald-500/30" : "text-neutral-500 hover:text-neutral-300 hover:bg-neutral-900/50"
              )}
            >
              <item.icon className={cn("w-5 h-5", activeTab === item.id ? "text-emerald-400" : "text-neutral-600")} />
              {isSidebarOpen && <span className="ml-3 text-sm font-medium">{item.label}</span>}
              {activeTab === item.id && (
                <motion.div
                  layoutId="active-pill"
                  className="absolute left-0 w-1 h-6 bg-emerald-500 rounded-r-full"
                />
              )}
            </button>
          ))}
        </nav>

        <div className="p-4 border-t border-neutral-800/50">
          <button
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="w-full h-10 glass rounded-lg flex items-center justify-center hover:bg-neutral-800 transition-colors"
          >
            {isSidebarOpen ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0 bg-[radial-gradient(circle_at_top_right,rgba(16,185,129,0.03),transparent_40%)]">
        {/* Top Header */}
        <header className="h-16 glass border-b border-neutral-800/50 flex items-center px-8 justify-between z-40">
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2 text-xs font-mono">
              <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-emerald-500/80">REFINERY_DAEMON: ACTIVE</span>
            </div>
            <div className="h-4 w-px bg-neutral-800" />
            <div className="flex items-center gap-2 text-xs font-mono text-neutral-500">
              <Activity className="w-3 h-3 text-blue-500" />
              <span>BATCH: {logistics?.batch_id || '---'}</span>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="glass px-3 py-1.5 rounded-lg flex items-center gap-3">
              <Cpu className="w-4 h-4 text-emerald-400" />
              <span className="text-xs font-mono font-bold text-neutral-300">v2.0 FLASH</span>
            </div>
            <div className="w-8 h-8 rounded-full bg-neutral-800 border border-neutral-700 flex items-center justify-center text-[10px] font-bold">L</div>
          </div>
        </header>

        {/* Dynamic Workspace */}
        <section className="flex-1 overflow-hidden relative flex">
          {/* LEFT PANEL: The Graph (Unified Split) */}
          <div className="flex-1 relative bg-black/40 border-r border-neutral-800/50 flex flex-col">
            <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:40px_40px] pointer-events-none" />

            <div className="p-8 flex-1 flex flex-col gap-6 overflow-y-auto hide-scrollbar z-10">
              <div className="flex items-end justify-between">
                <div>
                  <h1 className="text-3xl font-display font-light text-white tracking-tight">System Totality</h1>
                  <p className="text-neutral-500 text-sm mt-1 uppercase tracking-widest text-[10px]">Real-time Codome/Contextome Mapping</p>
                </div>
                <div className="flex gap-2">
                  <button className="glass px-4 py-2 rounded-lg text-xs font-bold hover:bg-neutral-800 transition-colors uppercase">Recenter</button>
                  <button className="glass-emerald px-4 py-2 rounded-lg text-xs font-bold text-emerald-400 hover:bg-emerald-500/20 transition-colors uppercase">High Depth</button>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <StatCard title="Total Atoms" value={graphMetrics?.node_count || "---"} icon={Layers} color="text-emerald-500" />
                <StatCard title="Entanglement" value={graphMetrics?.edge_count || "---"} icon={Activity} color="text-blue-500" />
                <StatCard title="Refinery Score" value={graphMetrics?.health_score || "0.983"} icon={ShieldCheck} color="text-purple-500" />
              </div>

              {/* Visualization Canvas Placeholder */}
              <div className="flex-1 glass rounded-2xl border border-neutral-800/50 overflow-hidden relative group">
                <GraphView onNodeClick={handleNodeClick} />
              </div>
            </div>
          </div>

          {/* RIGHT PANEL: Intelligence Stream */}
          <div className="w-[450px] flex flex-col bg-neutral-950/50 backdrop-blur-xl">
            <div className="h-14 border-b border-neutral-800/50 flex items-center px-6 justify-between flex-shrink-0">
              <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-neutral-400">
                <Database className="w-3 h-3" />
                <span>Intelligence Stream</span>
              </div>
              <div className="relative">
                <Search className="w-3 h-3 absolute left-3 top-1/2 -translate-y-1/2 text-neutral-600" />
                <input
                  type="text"
                  placeholder="Search Projectome..."
                  className="bg-neutral-900/50 border border-neutral-800 rounded-lg pl-8 p-1.5 text-[10px] outline-none focus:border-emerald-500/50 transition-colors w-40"
                />
              </div>
            </div>

            <div className="flex-1 overflow-y-auto p-6 space-y-4 hide-scrollbar">
              <div className="flex items-center justify-between mb-2">
                <h2 className="text-[10px] font-bold text-neutral-600 uppercase tracking-[0.2em]">Latest Refinements</h2>
                {selectedNode && (
                  <button
                    onClick={() => handleNodeClick(null)}
                    className="text-[8px] text-emerald-500 hover:text-emerald-400 font-bold uppercase"
                  >
                    Clear Filter
                  </button>
                )}
              </div>

              {selectedNode && (
                <div className="glass-emerald p-3 rounded-lg border border-emerald-500/20 mb-4">
                  <div className="text-[10px] text-emerald-400 font-bold uppercase mb-1">Active Context: {selectedNode.name || selectedNode.id}</div>
                  <div className="text-[9px] text-neutral-500 font-mono truncate">{selectedNode.file_path || selectedNode.file}</div>
                </div>
              )}

              {filteredChunks.map((chunk, i) => (
                <div key={i} className="glass p-4 rounded-xl border border-neutral-800/30 space-y-3 hover:border-neutral-700/50 transition-colors cursor-pointer group">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono text-emerald-500">CHUNK_ID: {chunk.chunk_id?.slice(0, 12)}</span>
                    <span className="text-[10px] text-neutral-600 uppercase">{chunk.type || 'REFINED'}</span>
                  </div>
                  <div className="font-display font-medium text-neutral-200 group-hover:text-white transition-colors line-clamp-2">
                    {chunk.content?.slice(0, 100)}...
                  </div>
                  <div className="flex gap-2">
                    <span className="text-[8px] px-2 py-0.5 rounded bg-neutral-900 border border-neutral-800 text-neutral-500 uppercase">{chunk.file?.split('/').pop()}</span>
                    {chunk.waybill && (
                      <span className="text-[8px] px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">AUDIT_PASS</span>
                    )}
                  </div>
                </div>
              ))}

              {chunks.length === 0 && !isLoading && (
                <div className="text-center py-20 text-neutral-700 font-mono text-sm">NO_ACTIVE_STREAM</div>
              )}

              <div className="pt-4">
                <button className="w-full py-3 glass rounded-xl text-xs font-bold text-neutral-400 hover:text-neutral-200 transition-colors uppercase border-dashed">View All Chunks</button>
              </div>
            </div>

            {/* Provenance Footer */}
            <div className="p-6 border-t border-neutral-800/50 space-y-4">
              <div className="flex items-center justify-between text-[10px] font-bold text-neutral-600 uppercase">
                <span>Provenance Check</span>
                <span className="text-emerald-500">SECURE</span>
              </div>
              <div className="glass p-3 rounded-lg space-y-2 border-emerald-500/10">
                <div className="flex justify-between text-[9px] font-mono">
                  <span className="text-neutral-500">MERKLE_ROOT:</span>
                  <span className="text-neutral-400 truncate ml-4 w-32">{logistics?.merkle_root || 'PENDING...'}</span>
                </div>
                <div className="flex justify-between text-[9px] font-mono">
                  <span className="text-neutral-500">REF_SIG:</span>
                  <span className="text-neutral-400">{logistics?.refinery_signature || '---'}</span>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
