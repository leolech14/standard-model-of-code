'use client';

import { useState, useMemo, useCallback } from 'react';
import { SERVICE_META, TOTAL_TOKENS, ecosystemNodeList } from '@/lib/nodes/registry/ecosystem';

/* ═══════════════════════════════════════════════════════════════════
   CARTOGRAPHER — Derive positions from purpose.relevance
   No hardcoded x,y. Tier assignment → row → even distribution.
   ═══════════════════════════════════════════════════════════════════ */

interface NodePosition { x: number; y: number }

function derivePositions(
  nodes: typeof ecosystemNodeList,
): Map<string, NodePosition> {
  const services = nodes.filter(n => n.representation.group === 'cloud-services');
  // Sort by relevance descending
  const sorted = [...services].sort(
    (a, b) => (b.purpose?.relevance ?? 0) - (a.purpose?.relevance ?? 0),
  );

  // Tier assignment: top 4 → row 1, next 3 → row 2, rest → row 3
  const tiers = [
    { nodes: sorted.slice(0, 4), y: 15 },
    { nodes: sorted.slice(4, 7), y: 32 },
    { nodes: sorted.slice(7),    y: 49 },
  ];

  const positions = new Map<string, NodePosition>();

  for (const tier of tiers) {
    const count = tier.nodes.length;
    tier.nodes.forEach((node, i) => {
      const x = count === 1 ? 50 :
        15 + (i * (70 / (count - 1)));
      positions.set(node.id, { x, y: tier.y });
    });
  }

  // Convergence: center, below cloud
  positions.set('ecosystem.convergence', { x: 50, y: 72 });
  return positions;
}

const CONVERGENCE_POS = { x: 50, y: 72 };

/* ═══════════════════════════════════════════════════════════════════
   PRISM — Custom View Components (all using Mint tokens)
   ═══════════════════════════════════════════════════════════════════ */

/* --- EcosystemNodeCard --- */
function EcosystemNodeCard({
  serviceId, active, onToggle,
}: {
  serviceId: string; active: boolean; onToggle: () => void;
}) {
  const meta = SERVICE_META[serviceId];
  if (!meta) return null;

  return (
    <button
      onClick={onToggle}
      className={[
        'absolute flex flex-col items-center justify-center',
        'w-20 h-20 sm:w-24 sm:h-24 rounded-2xl border',
        'cursor-pointer select-none backdrop-blur-sm',
        'transition-all duration-200 ease-out',
        active
          ? 'ring-2 ring-offset-2 ring-accent ring-offset-bg opacity-100 shadow-lg'
          : 'opacity-50 hover:opacity-70 shadow-sm',
      ].join(' ')}
      style={{
        background: 'var(--color-surface)',
        borderColor: active ? `var(--color-accent)` : 'var(--color-border)',
        transform: 'translate(-50%, -50%)',
      }}
    >
      <span className="text-2xl sm:text-3xl mb-1">{meta.icon}</span>
      <span className="text-[10px] sm:text-xs font-bold text-text leading-tight text-center px-1">
        {serviceId === 'openfinance' ? 'Finance' : meta.icon === '🔄' ? 'n8n' :
          serviceId.charAt(0).toUpperCase() + serviceId.slice(1)}
      </span>
      <span className="text-[8px] sm:text-[10px] text-text-muted leading-tight">
        {meta.sub}
      </span>
    </button>
  );
}

/* --- FlowCanvas: SVG bezier lines from nodes to convergence --- */
function FlowCanvas({
  positions, activeSet,
}: {
  positions: Map<string, NodePosition>;
  activeSet: Set<string>;
}) {
  const services = [...positions.entries()].filter(
    ([id]) => id.startsWith('ecosystem.') && id !== 'ecosystem.convergence',
  );

  return (
    <svg
      className="absolute inset-0 w-full h-full pointer-events-none"
      viewBox="0 0 100 100"
      preserveAspectRatio="none"
    >
      {services.map(([id, pos]) => {
        const active = activeSet.has(id);
        const sX = pos.x, sY = pos.y + 5;
        const eX = CONVERGENCE_POS.x, eY = CONVERGENCE_POS.y;
        const cpY = sY + (eY - sY) / 2;
        return (
          <path
            key={id}
            d={`M ${sX} ${sY} C ${sX} ${cpY}, ${eX} ${cpY}, ${eX} ${eY}`}
            fill="none"
            stroke={active ? 'var(--color-info)' : 'var(--color-border)'}
            strokeWidth={active ? 0.8 : 0.3}
            className={active ? 'data-flow' : ''}
            style={{ opacity: active ? 1 : 0.15 }}
          />
        );
      })}
    </svg>
  );
}

/* --- ConvergencePoint: dot strip + token counter + progress bar --- */
function ConvergencePoint({
  activeTokens, activeCount, totalCount,
}: {
  activeTokens: number; activeCount: number; totalCount: number;
}) {
  const pct = (activeTokens / TOTAL_TOKENS) * 100;
  return (
    <div className="flex flex-col items-center w-64">
      {/* Dot strip — one per service */}
      <div className="flex gap-1 mb-2">
        {Array.from({ length: totalCount }, (_, i) => (
          <div
            key={i}
            className="w-1.5 h-1.5 rounded-full transition-colors duration-300"
            style={{
              background: i < activeCount ? 'var(--color-info)' : 'var(--color-border)',
              boxShadow: i < activeCount ? '0 0 8px var(--color-info)' : 'none',
            }}
          />
        ))}
      </div>
      <h2 className="text-xl font-semibold tracking-tight text-text">Ecosystem Cloudpoint</h2>
      <div className="text-sm text-text-muted font-medium tracking-wide mb-2 flex items-center gap-2">
        <span className="font-mono">{activeTokens.toLocaleString()}</span> tokens
        <span className="w-1 h-1 rounded-full" style={{ background: 'var(--color-text-muted)' }} />
        <span style={{ color: activeTokens > 0 ? 'var(--color-info)' : undefined }}>
          {activeTokens > 0 ? 'always-on' : 'standby'}
        </span>
      </div>
      {/* Progress bar */}
      <div className="w-48 h-2 rounded-full overflow-hidden border"
           style={{ background: 'var(--color-surface)', borderColor: 'var(--color-border)' }}>
        <div
          className="h-full rounded-full transition-all duration-500 ease-out"
          style={{ width: `${pct}%`, background: 'var(--color-accent)' }}
        />
      </div>
    </div>
  );
}

/* --- TerminalLaptop: MacBook with live terminal output --- */
function TerminalLaptop({
  activeServices, activeTokens,
}: {
  activeServices: Array<{ id: string; tokens: number }>;
  activeTokens: number;
}) {
  return (
    <div className="flex flex-col items-center">
      {/* Connecting tendrils */}
      <svg className="w-32 h-16 pointer-events-none opacity-20" viewBox="0 0 100 100" preserveAspectRatio="none">
        <path d="M 25 0 C 25 50, 40 50, 42 100" fill="none" stroke="var(--color-text-muted)" strokeWidth="1" />
        <path d="M 42 0 C 42 50, 47 50, 48 100" fill="none" stroke="var(--color-text-muted)" strokeWidth="1" />
        <path d="M 58 0 C 58 50, 53 50, 52 100" fill="none" stroke="var(--color-text-muted)" strokeWidth="1" />
        <path d="M 75 0 C 75 50, 60 50, 58 100" fill="none" stroke="var(--color-text-muted)" strokeWidth="1" />
      </svg>
      {/* Screen */}
      <div className="w-[340px] sm:w-[480px] h-[200px] sm:h-[260px] rounded-t-2xl border-[5px] relative overflow-hidden flex flex-col"
           style={{ background: 'var(--color-bg)', borderColor: 'var(--color-border)' }}>
        {/* Glare */}
        <div className="absolute inset-0 bg-gradient-to-br from-white/3 to-transparent pointer-events-none" />
        {/* Title bar */}
        <div className="h-6 flex items-center px-3 gap-1.5 border-b"
             style={{ background: 'var(--color-surface)', borderColor: 'var(--color-border)' }}>
          <div className="w-2.5 h-2.5 rounded-full bg-[#f87171] opacity-70" />
          <div className="w-2.5 h-2.5 rounded-full bg-[#fbbf24] opacity-70" />
          <div className="w-2.5 h-2.5 rounded-full bg-[#34d399] opacity-70" />
          <span className="ml-2 text-[10px] text-text-muted font-mono">bash — openclaw</span>
        </div>
        {/* Terminal content */}
        <div className="flex-1 p-4 font-mono text-xs sm:text-sm overflow-y-auto flex flex-col justify-end"
             style={{ color: 'var(--color-positive)' }}>
          <div className="opacity-40 mb-2">Initializing local environment...</div>
          <div><span style={{ color: 'var(--color-positive)' }}>$</span> claude code</div>
          <div className="flex flex-col gap-1 mt-1">
            {activeServices.length === 0 ? (
              <div className="text-text-muted italic">Waiting for ecosystem connections...</div>
            ) : (
              <>
                {activeServices.map(svc => (
                  <div key={svc.id}>
                    <span className="text-text-muted">+</span>{' '}
                    ecosystem <span style={{ color: 'var(--color-info)' }}>{svc.id.replace('ecosystem.', '')}</span>{' '}
                    loaded <span className="text-text-muted text-[10px]">({svc.tokens}t)</span>
                  </div>
                ))}
                <div className="mt-2 font-bold" style={{ color: 'var(--color-info)' }}>
                  <span className="text-text-muted">&gt;</span> CONTEXT: {activeTokens.toLocaleString()} tokens active
                </div>
              </>
            )}
          </div>
          <div className="mt-2 flex items-center gap-2">
            <span style={{ color: 'var(--color-positive)' }}>$</span>
            <span className="w-2 h-4 animate-pulse" style={{ background: 'var(--color-positive)' }} />
          </div>
        </div>
      </div>

      {/* Laptop base */}
      <div className="relative w-[400px] sm:w-[560px]">
        <div className="h-4 rounded-t-sm w-full mx-auto relative z-10 border-b flex justify-center"
             style={{ background: 'var(--color-surface)', borderColor: 'var(--color-border)' }}>
          <div className="w-16 h-1 rounded-b-md" style={{ background: 'var(--color-border)' }} />
        </div>
        <div className="h-3 rounded-b-xl w-[98%] mx-auto"
             style={{ background: 'var(--color-surface)' }} />
      </div>
      <div className="mt-6 text-xs font-medium tracking-[0.2em] text-text-muted uppercase">
        Local Dev &bull; Project_openclaw
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════
   CSS: data-flow animation (injected via style tag since we're
   inside the React app, not a standalone HTML file)
   ═══════════════════════════════════════════════════════════════════ */

const FLOW_CSS = `
@keyframes flow {
  from { stroke-dashoffset: 12; }
  to { stroke-dashoffset: 0; }
}
.data-flow {
  stroke-dasharray: 4 8;
  animation: flow 1s linear infinite;
}
`;

/* ═══════════════════════════════════════════════════════════════════
   MAIN PAGE — EcosystemPage
   State: activeSet (which services are toggled on)
   Everything else is DERIVED.
   ═══════════════════════════════════════════════════════════════════ */

export default function EcosystemPage() {
  const [activeSet, setActiveSet] = useState<Set<string>>(new Set());

  const toggle = useCallback((id: string) => {
    setActiveSet(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  }, []);


  // CARTOGRAPHER: derive positions from relevance
  const positions = useMemo(() => derivePositions(ecosystemNodeList), []);

  // Derived state (MINT territory — computed, not stored)
  const serviceNodes = useMemo(
    () => ecosystemNodeList.filter(n => n.representation.group === 'cloud-services'),
    [],
  );

  const activeTokens = useMemo(() => {
    let sum = 0;
    for (const id of activeSet) {
      const key = id.replace('ecosystem.', '');
      const meta = SERVICE_META[key];
      if (meta) sum += meta.tokens;
    }
    return sum;
  }, [activeSet]);

  const activeServices = useMemo(() => {
    return [...activeSet].map(id => {
      const key = id.replace('ecosystem.', '');
      return { id, tokens: SERVICE_META[key]?.tokens ?? 0 };
    });
  }, [activeSet]);


  return (
    <div className="p-6 max-w-5xl mx-auto">
      {/* Inject flow animation CSS */}
      <style dangerouslySetInnerHTML={{ __html: FLOW_CSS }} />

      {/* Cloud atmosphere */}
      <div className="relative" style={{ minHeight: '480px' }}>
        {/* Radial glow behind cloud zone */}
        <div
          className="absolute pointer-events-none"
          style={{
            top: '-5%', left: '50%', transform: 'translateX(-50%)',
            width: '120%', height: '55%',
            background: 'radial-gradient(ellipse at center, var(--color-surface) 0%, transparent 70%)',
            opacity: 0.5,
          }}
        />

        {/* SVG flow lines layer */}
        <FlowCanvas positions={positions} activeSet={activeSet} />

        {/* Service node cards */}
        {serviceNodes.map(node => {
          const pos = positions.get(node.id);
          if (!pos) return null;
          const svcId = node.id.replace('ecosystem.', '');
          return (
            <div
              key={node.id}
              className="absolute"
              style={{ left: `${pos.x}%`, top: `${pos.y}%` }}
            >
              <EcosystemNodeCard
                serviceId={svcId}
                active={activeSet.has(node.id)}
                onToggle={() => toggle(node.id)}
              />
            </div>
          );
        })}

        {/* Convergence point */}
        <div
          className="absolute left-1/2 -translate-x-1/2"
          style={{ top: `${CONVERGENCE_POS.y}%` }}
        >
          <ConvergencePoint
            activeTokens={activeTokens}
            activeCount={activeSet.size}
            totalCount={serviceNodes.length}
          />
        </div>
      </div>

      {/* Terminal laptop */}
      <TerminalLaptop
        activeServices={activeServices}
        activeTokens={activeTokens}
      />
    </div>
  );
}
