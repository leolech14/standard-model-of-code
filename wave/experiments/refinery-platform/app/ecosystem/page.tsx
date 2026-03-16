'use client';

import { useState } from 'react';
import { Globe, Zap, Server, Database, Key, GitBranch, Bot, Cloud, BarChart3, RefreshCw } from 'lucide-react';

const SERVICES = [
  { id: 'notion', label: 'Notion', sub: 'docs', icon: Globe, tokens: 1200, color: 'text-slate-600' },
  { id: 'chatgpt', label: 'ChatGPT', sub: 'research', icon: Bot, tokens: 850, color: 'text-emerald-600' },
  { id: 'google', label: 'Google', sub: 'cloud', icon: Cloud, tokens: 2100, color: 'text-blue-600' },
  { id: 'github', label: 'GitHub', sub: 'code', icon: GitBranch, tokens: 3400, color: 'text-slate-700' },
  { id: 'anthropic', label: 'Anthropic', sub: 'LLMs', icon: Bot, tokens: 1500, color: 'text-amber-600' },
  { id: 'supabase', label: 'Supabase', sub: 'data', icon: Database, tokens: 900, color: 'text-green-600' },
  { id: 'doppler', label: 'Doppler', sub: 'secrets', icon: Key, tokens: 150, color: 'text-yellow-600' },
  { id: 'openfinance', label: 'Open Finance', sub: 'data', icon: BarChart3, tokens: 600, color: 'text-indigo-600' },
  { id: 'cerebras', label: 'Cerebras', sub: 'inference', icon: Zap, tokens: 4500, color: 'text-rose-600' },
  { id: 'n8n', label: 'n8n', sub: 'flows', icon: RefreshCw, tokens: 400, color: 'text-red-600' },
];

const TOTAL_TOKENS = SERVICES.reduce((s, n) => s + n.tokens, 0);

export default function EcosystemPage() {
  const [showInteractive, setShowInteractive] = useState(false);

  return (
    <div className="p-6 max-w-7xl">

      {/* Header */}
      <div className="flex items-start justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">Ecosystem Atlas</h1>
          <p className="text-text-secondary">
            10 cloud services · {TOTAL_TOKENS.toLocaleString()} context tokens · always-on
          </p>
        </div>
        <button
          onClick={() => setShowInteractive(!showInteractive)}
          className="flex items-center gap-2 px-4 py-2 bg-surface hover:bg-elevated rounded-md text-sm transition-colors"
        >
          <Server className="w-4 h-4" />
          {showInteractive ? 'Show Summary' : 'Interactive Mode'}
        </button>
      </div>

      {!showInteractive ? (
        <>
          {/* Service Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-4 mb-8">
            {SERVICES.map((svc) => {
              const Icon = svc.icon;
              return (
                <div key={svc.id} className="glass-card rounded-lg p-4 flex flex-col items-center text-center">
                  <Icon className={`w-6 h-6 mb-2 ${svc.color}`} />
                  <div className="text-sm font-semibold">{svc.label}</div>
                  <div className="text-xs text-text-muted">{svc.sub}</div>

                  <div className="mt-2 text-lg font-bold font-mono text-text">
                    {svc.tokens.toLocaleString()}
                  </div>
                  <div className="text-[10px] text-text-muted">tokens</div>
                </div>
              );
            })}
          </div>

          {/* Stats Row */}
          <div className="grid grid-cols-4 gap-4 mb-8">
            <div className="glass-card rounded-lg p-4">
              <div className="text-xs text-text-muted uppercase tracking-wider mb-1">Total Context</div>
              <div className="text-2xl font-bold text-accent">{TOTAL_TOKENS.toLocaleString()}</div>
              <div className="text-xs text-text-muted mt-1">tokens compiled</div>
            </div>
            <div className="glass-card rounded-lg p-4">
              <div className="text-xs text-text-muted uppercase tracking-wider mb-1">Services</div>
              <div className="text-2xl font-bold text-info">{SERVICES.length}</div>
              <div className="text-xs text-text-muted mt-1">cloud providers</div>
            </div>
            <div className="glass-card rounded-lg p-4">
              <div className="text-xs text-text-muted uppercase tracking-wider mb-1">Atlas Entities</div>
              <div className="text-2xl font-bold text-purple">66</div>
              <div className="text-xs text-text-muted mt-1">CMP + AGT + CON + RES + EXT</div>
            </div>
            <div className="glass-card rounded-lg p-4">
              <div className="text-xs text-text-muted uppercase tracking-wider mb-1">Coverage</div>
              <div className="text-2xl font-bold text-warning">16%</div>
              <div className="text-xs text-text-muted mt-1">34 of 209 registered</div>
            </div>
          </div>

          {/* Architecture Overview */}
          <div className="glass-card rounded-lg p-6 mb-8">
            <h2 className="text-xl font-semibold mb-4">Architecture</h2>
            <div className="grid grid-cols-3 gap-6 text-sm">
              <div>
                <div className="font-semibold text-accent mb-1">Cloud Layer</div>
                <p className="text-text-secondary">10 services (Notion, ChatGPT, Google, GitHub, Anthropic, Supabase, Doppler, OpenFinance, Cerebras, n8n) connected via MCP, REST, and filesystem protocols.</p>
              </div>
              <div>
                <div className="font-semibold text-info mb-1">Ecosystem Cloudpoint</div>
                <p className="text-text-secondary">ATLAS.yaml — 7,676 tokens of pre-computed context. Stage-gated, typed entity graph loaded by every agent at session start.</p>
              </div>
              <div>
                <div className="font-semibold text-purple mb-1">Local Development</div>
                <p className="text-text-secondary">MacBook Pro running Claude Code (Opus 4.6, 1M context). PROJECT_openclaw VPS infrastructure behind Cloudflare tunnel + Authelia 2FA.</p>
              </div>
            </div>
          </div>
        </>
      ) : (
        /* Interactive Ecosystem Context Builder */
        <div className="glass-card rounded-lg overflow-hidden" style={{ height: '820px' }}>
          <iframe
            src="/ecosystem-context-builder.html"
            className="w-full h-full border-0"
            title="Ecosystem Context Builder"
          />
        </div>
      )}
    </div>
  );
}
