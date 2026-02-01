"use client";

import React, { useState } from 'react';
import { Settings, Play, Box, Layers, Activity, Server, FileText, Cpu, Eye } from 'lucide-react';
import { motion } from 'framer-motion';

export default function RefineryDashboard() {
  const [config, setConfig] = useState({
    contextDepth: 3,
    agentCount: 4,
    attentionMode: 'laminar',
    ignoreTests: true
  });

  const [isPrinting, setIsPrinting] = useState(false);
  const [status, setStatus] = useState<string>('');
  const [executionId, setExecutionId] = useState<string | null>(null);

  const handleRefine = async () => {
    if (isPrinting) return; // Prevent double click or handle stop logic later
    setIsPrinting(true);
    setStatus('Generating G-Code...');

    try {
      const response = await fetch('/api/refine', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      });
      const data = await response.json();

      if (data.success) {
        setExecutionId(data.executionId);
        setStatus(`Printing... [${data.executionId}]`);
      } else {
        setStatus(`Error: ${data.error}`);
        setIsPrinting(false);
      }
    } catch (e: any) {
      setStatus(`Network Error: ${e.message}`);
      setIsPrinting(false);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-200 font-sans selection:bg-emerald-500/30">
      {/* Header */}
      <header className="h-14 border-b border-neutral-800 flex items-center px-4 justify-between bg-neutral-900/50 backdrop-blur-md sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded bg-emerald-500 flex items-center justify-center text-black font-bold">R</div>
          <span className="font-semibold tracking-tight text-white">Cloud Refinery v2.0</span>
          <span className="text-xs px-2 py-0.5 rounded-full bg-neutral-800 text-neutral-400 border border-neutral-700">Online</span>
        </div>
        <div className="flex items-center gap-4 text-sm">
          <div className="flex items-center gap-2 text-emerald-400">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            Neo4j Connected
          </div>
          <button className="p-2 hover:bg-neutral-800 rounded-md transition-colors"><Settings className="w-4 h-4" /></button>
        </div>
      </header>

      <main className="flex h-[calc(100vh-3.5rem)]">
        {/* LEFT: The Slicer (Configuration) */}
        <aside className="w-80 border-r border-neutral-800 bg-neutral-900/30 flex flex-col">
          <div className="p-4 border-b border-neutral-800">
            <h2 className="text-xs font-bold text-neutral-500 uppercase tracking-wider mb-4">Slicer Settings</h2>

            {/* Context Depth */}
            <div className="mb-6">
              <div className="flex justify-between mb-2">
                <label className="text-sm font-medium text-neutral-300">Context Depth</label>
                <span className="text-xs text-emerald-400 font-mono">L{config.contextDepth}</span>
              </div>
              <input
                type="range" min="1" max="5" step="1"
                value={config.contextDepth}
                onChange={(e) => setConfig({ ...config, contextDepth: parseInt(e.target.value) })}
                className="w-full h-1 bg-neutral-700 rounded-lg appearance-none cursor-pointer accent-emerald-500"
              />
              <div className="flex justify-between text-[10px] text-neutral-500 mt-1">
                <span>File</span>
                <span>AST</span>
                <span>Molecular</span>
              </div>
            </div>

            {/* Agent Allocation */}
            <div className="mb-6">
              <label className="text-sm font-medium text-neutral-300 mb-2 block">Agent Allocation</label>
              <div className="flex items-center gap-3 bg-neutral-800/50 p-2 rounded border border-neutral-700/50">
                <Cpu className="w-4 h-4 text-neutral-400" />
                <span className="text-sm font-mono flex-1">{config.agentCount} Agents</span>
                <div className="flex gap-1">
                  <button onClick={() => setConfig(c => ({ ...c, agentCount: Math.max(1, c.agentCount - 1) }))} className="w-6 h-6 flex items-center justify-center bg-neutral-700 hover:bg-neutral-600 rounded text-xs">-</button>
                  <button onClick={() => setConfig(c => ({ ...c, agentCount: Math.min(50, c.agentCount + 1) }))} className="w-6 h-6 flex items-center justify-center bg-neutral-700 hover:bg-neutral-600 rounded text-xs">+</button>
                </div>
              </div>
            </div>

            {/* Attention Mode */}
            <div className="mb-6">
              <label className="text-sm font-medium text-neutral-300 mb-2 block">Attention Mode</label>
              <div className="grid grid-cols-2 gap-2 bg-neutral-800/50 p-1 rounded border border-neutral-700/50">
                <button
                  onClick={() => setConfig({ ...config, attentionMode: 'laminar' })}
                  className={`text-xs py-1.5 rounded transition-colors ${config.attentionMode === 'laminar' ? 'bg-emerald-500/20 text-emerald-300' : 'text-neutral-500 hover:text-neutral-300'}`}
                >Laminar</button>
                <button
                  onClick={() => setConfig({ ...config, attentionMode: 'turbulent' })}
                  className={`text-xs py-1.5 rounded transition-colors ${config.attentionMode === 'turbulent' ? 'bg-purple-500/20 text-purple-300' : 'text-neutral-500 hover:text-neutral-300'}`}
                >Turbulent</button>
              </div>
            </div>

            {/* Print Button */}
            <button
              onClick={handleRefine}
              disabled={isPrinting}
              className={`w-full py-3 rounded-lg font-bold flex items-center justify-center gap-2 transition-all ${isPrinting
                  ? 'bg-neutral-800 text-neutral-400 cursor-not-allowed border border-neutral-700'
                  : 'bg-emerald-500 hover:bg-emerald-400 text-black shadow-[0_0_20px_rgba(16,185,129,0.3)]'
                }`}
            >
              {isPrinting ? <><Activity className="w-4 h-4 animate-spin" /> PROCESSING</> : <><Play className="w-4 h-4 fill-current" /> SLICE & REFINE</>}
            </button>
          </div>

          <div className="flex-1 p-4 overflow-y-auto">
            <h2 className="text-xs font-bold text-neutral-500 uppercase tracking-wider mb-2">Telemetry</h2>
            <div className="font-mono text-[10px] text-neutral-400 space-y-1">
              <div className="text-emerald-500">[SYSTEM] Connection established.</div>
              <div>[INFO] Standard Model loaded.</div>
              {status && <div className="text-blue-400">[LOG] {status}</div>}
              {isPrinting && executionId && (
                <>
                  <div className="text-yellow-400">[CLOUD] socratic-audit-job triggered.</div>
                  <div className="text-neutral-500">ID: {executionId}</div>
                </>
              )}
            </div>
          </div>
        </aside>

        {/* CENTER: The Visualization (Model View) */}
        <div className="flex-1 bg-black relative overflow-hidden flex items-center justify-center">
          {/* Grid Background */}
          <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:50px_50px]" />

          {/* Placeholder for 3D View */}
          <div className="relative z-10 text-center">
            <div className="w-64 h-64 border border-neutral-800 rounded-full flex items-center justify-center mx-auto mb-6 bg-neutral-900/50 backdrop-blur border-dashed animate-[spin_10s_linear_infinite]">
              <div className="w-48 h-48 border border-neutral-700 rounded-full flex items-center justify-center border-dashed animate-[spin_15s_linear_infinite_reverse]">
                <Layers className="w-12 h-12 text-neutral-600" />
              </div>
            </div>
            <h1 className="text-2xl font-light text-neutral-300">Awaiting Slice</h1>
            <p className="text-neutral-500 mt-2">Configure parameters and start refinement.</p>
          </div>

          {/* Floating Stats */}
          <div className="absolute bottom-6 right-6 flex gap-4">
            <div className="bg-neutral-900/80 backdrop-blur border border-neutral-800 p-3 rounded-lg w-40">
              <div className="text-xs text-neutral-500 uppercase">Nodes</div>
              <div className="text-xl font-mono text-white">12,405</div>
            </div>
            <div className="bg-neutral-900/80 backdrop-blur border border-neutral-800 p-3 rounded-lg w-40">
              <div className="text-xs text-neutral-500 uppercase">Edges</div>
              <div className="text-xl font-mono text-white">45,102</div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
