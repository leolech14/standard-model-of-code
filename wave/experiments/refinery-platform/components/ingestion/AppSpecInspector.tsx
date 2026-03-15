'use client';

import React, { useState } from 'react';
import {
  Box, Code, Layers, Package, Eye,
  ChevronDown, ChevronRight, FileCode, Cpu, Globe,
  Gauge, Shield, Workflow,
} from 'lucide-react';
import type { AppSpec, ComponentNode, AppRisk, ExposableNode } from '@/lib/ingestion/types';

/* ─── Shared Primitives ─── */

const Section = ({ title, icon: Icon, count, children, defaultOpen = false }: {
  title: string; icon: React.ComponentType<{ className?: string }>; count?: number; children: React.ReactNode; defaultOpen?: boolean;
}) => {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="border-b border-[var(--color-border)] last:border-b-0">
      <button onClick={() => setOpen(!open)} className="w-full flex items-center justify-between px-5 py-3 hover:bg-[var(--color-surface-hover)] transition-colors text-left">
        <div className="flex items-center gap-2.5">
          <Icon className="w-3.5 h-3.5 text-[var(--color-text-muted)]" />
          <span className="text-xs font-medium text-[var(--color-text-secondary)] uppercase tracking-wider">{title}</span>
          {count != null && <span className="text-[10px] px-1.5 py-0.5 rounded bg-[var(--color-surface)] text-[var(--color-text-muted)]">{count}</span>}
        </div>
        {open ? <ChevronDown className="w-3 h-3 text-[var(--color-text-muted)]" /> : <ChevronRight className="w-3 h-3 text-[var(--color-text-muted)]" />}
      </button>
      {open && <div className="px-5 pb-4">{children}</div>}
    </div>
  );
};

const Tag = ({ children, color = 'neutral' }: { children: React.ReactNode; color?: 'neutral' | 'amber' | 'emerald' | 'rose' | 'blue' }) => {
  const colors = {
    neutral: 'bg-[var(--color-surface)] text-[var(--color-text-secondary)] border-[var(--color-border)]',
    amber: 'bg-[oklch(var(--amber-l)_var(--amber-c)_var(--amber-h)/0.1)] text-[var(--color-warning)] border-[oklch(var(--amber-l)_var(--amber-c)_var(--amber-h)/0.2)]',
    emerald: 'bg-[oklch(var(--emerald-l)_var(--emerald-c)_var(--emerald-h)/0.1)] text-[var(--color-accent)] border-[oklch(var(--emerald-l)_var(--emerald-c)_var(--emerald-h)/0.2)]',
    rose: 'bg-[oklch(var(--rose-l)_var(--rose-c)_var(--rose-h)/0.1)] text-[var(--color-danger)] border-[oklch(var(--rose-l)_var(--rose-c)_var(--rose-h)/0.2)]',
    blue: 'bg-[oklch(var(--blue-l)_var(--blue-c)_var(--blue-h)/0.1)] text-[var(--color-info)] border-[oklch(var(--blue-l)_var(--blue-c)_var(--blue-h)/0.2)]',
  };
  return <span className={`text-[10px] px-1.5 py-0.5 rounded border ${colors[color]}`}>{children}</span>;
};

const KV = ({ label, value }: { label: string; value: React.ReactNode }) => (
  <div className="flex justify-between items-baseline py-1">
    <span className="text-[10px] text-[var(--color-text-muted)] uppercase tracking-wider">{label}</span>
    <span className="text-xs text-[var(--color-text-secondary)] text-right max-w-[60%] truncate">{value}</span>
  </div>
);

/* ─── Risk Badge ─── */

const RiskBadge = ({ risk }: { risk: AppRisk }) => {
  const colors = {
    critical: 'border-[var(--color-danger)] bg-[oklch(var(--rose-l)_var(--rose-c)_var(--rose-h)/0.05)] text-[var(--color-danger)]',
    warning: 'border-[var(--color-warning)] bg-[oklch(var(--amber-l)_var(--amber-c)_var(--amber-h)/0.05)] text-[var(--color-warning)]',
    info: 'border-[var(--color-border)] bg-[var(--color-bg)] text-[var(--color-text-secondary)]',
  };
  const icons = { critical: '!', warning: '!', info: 'i' };
  return (
    <div className={`p-2.5 rounded border ${colors[risk.severity]} text-[11px] leading-relaxed`}>
      <div className="flex items-start gap-2">
        <span className="font-mono font-bold text-[10px] mt-0.5 shrink-0">{icons[risk.severity]}</span>
        <div>
          <span>{risk.message}</span>
          {risk.location && <span className="text-[10px] opacity-50 ml-1.5 font-mono">{risk.location}</span>}
        </div>
      </div>
    </div>
  );
};

/* ─── Component Tree Item ─── */

const ComponentItem = ({ node }: { node: ComponentNode }) => {
  const complexityColor = { leaf: 'emerald', branch: 'blue', root: 'amber' } as const;
  return (
    <div className="p-2 rounded bg-[var(--color-bg)] border border-[var(--color-border)] hover:border-[var(--color-border-subtle)] transition-colors">
      <div className="flex items-center justify-between mb-1">
        <div className="flex items-center gap-2">
          <FileCode className="w-3 h-3 text-[var(--color-text-muted)]" />
          <span className="text-xs text-[var(--color-text)] font-mono">{node.name}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <Tag color={complexityColor[node.complexity]}>{node.complexity}</Tag>
          <span className="text-[10px] text-[var(--color-text-muted)] font-mono">{node.loc}L</span>
        </div>
      </div>
      <p className="text-[10px] text-[var(--color-text-muted)] pl-5">{node.role}</p>
    </div>
  );
};

/* ─── Exposable Node Card ─── */

const ExposableCard = ({ node }: { node: ExposableNode }) => {
  const conf = Math.round(node.confidence * 100);
  const confColor = conf >= 80 ? 'text-[var(--color-accent)]' : conf >= 60 ? 'text-[var(--color-warning)]' : 'text-[var(--color-text-muted)]';
  return (
    <div className="p-3 rounded border border-dashed border-[oklch(var(--emerald-l)_var(--emerald-c)_var(--emerald-h)/0.2)] bg-[oklch(var(--emerald-l)_var(--emerald-c)_var(--emerald-h)/0.05)] hover:border-[oklch(var(--emerald-l)_var(--emerald-c)_var(--emerald-h)/0.4)] transition-colors">
      <div className="flex items-center justify-between mb-1.5">
        <span className="text-xs text-[var(--color-text)] font-mono">{node.suggestedId}</span>
        <span className={`text-[10px] font-mono ${confColor}`}>{conf}%</span>
      </div>
      <div className="flex items-center gap-2 mb-1.5">
        <Tag color="emerald">{node.nodeKind}</Tag>
        <Tag>{node.viewKind}</Tag>
      </div>
      <p className="text-[10px] text-[var(--color-text-muted)]">{node.senseStrategy}</p>
    </div>
  );
};

/* ─── Main Inspector ─── */

export function AppSpecInspector({ spec }: { spec: AppSpec }) {
  const { meta, architecture, sense, interpret, represent, dependencies, exposable, risks } = spec;

  const criticalRisks = risks.filter(r => r.severity === 'critical').length;
  const warningRisks = risks.filter(r => r.severity === 'warning').length;

  return (
    <div className="h-full overflow-y-auto">
      {/* Header */}
      <div className="px-5 pt-5 pb-4 border-b border-[var(--color-border)]">
        <div className="flex items-center gap-2.5 mb-3">
          <div className="w-8 h-8 rounded-lg bg-[var(--color-surface)] flex items-center justify-center">
            <Package className="w-4 h-4 text-[var(--color-text-secondary)]" />
          </div>
          <div>
            <h2 className="text-sm font-medium text-[var(--color-text)]">{meta.name}</h2>
            <p className="text-[10px] text-[var(--color-text-muted)]">{meta.description}</p>
          </div>
        </div>

        {/* Stack chips */}
        <div className="flex flex-wrap gap-1.5 mb-3">
          <Tag color="blue">{meta.stack.framework}</Tag>
          <Tag>{meta.stack.bundler}</Tag>
          <Tag>{meta.stack.language}</Tag>
          <Tag>{meta.stack.styling}</Tag>
          <Tag>{meta.stack.target}</Tag>
        </div>

        {/* Quick stats */}
        <div className="grid grid-cols-4 gap-2">
          {[
            { value: meta.fileCount, label: 'Files' },
            { value: `${(meta.sizeBytes / 1024).toFixed(0)}`, unit: 'KB', label: 'Size' },
            { value: architecture.componentTree.length, label: 'Comps' },
            { value: exposable.length, label: 'Nodes' },
          ].map(s => (
            <div key={s.label} className="text-center p-1.5 rounded bg-[var(--color-bg)]">
              <div className="text-sm font-light text-[var(--color-text)]">
                {s.value}{s.unit && <span className="text-[9px] text-[var(--color-text-muted)] ml-0.5">{s.unit}</span>}
              </div>
              <div className="text-[9px] text-[var(--color-text-muted)] uppercase">{s.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Sections */}
      <Section title="Architecture" icon={Layers} defaultOpen>
        <div className="space-y-1 mb-3">
          <KV label="Pattern" value={architecture.pattern.toUpperCase()} />
          <KV label="Entry" value={<span className="font-mono">{architecture.entryPoint}</span>} />
          <KV label="State" value={architecture.stateManagement.pattern} />
          {architecture.stateManagement.persisted && (
            <KV label="Persistence" value={architecture.stateManagement.persistenceLayer || 'yes'} />
          )}
          <KV label="Data Flow" value={architecture.dataFlow} />
        </div>
        <div className="text-[10px] text-[var(--color-text-muted)] uppercase tracking-wider mb-2 mt-3">Directories</div>
        <div className="space-y-1">
          {architecture.directories.map(d => (
            <div key={d.path} className="flex items-center justify-between text-[11px]">
              <span className="text-[var(--color-text-secondary)] font-mono">{d.path}</span>
              <span className="text-[var(--color-text-muted)]">{d.role} ({d.fileCount})</span>
            </div>
          ))}
        </div>
      </Section>

      <Section title="Components" icon={Box} count={architecture.componentTree.length}>
        <div className="space-y-1.5">
          {architecture.componentTree.map(node => (
            <ComponentItem key={node.name} node={node} />
          ))}
        </div>
      </Section>

      <Section title="Sense (Data In)" icon={Globe} count={sense.apis.length + sense.browserApis.length}>
        {sense.apis.length > 0 && (
          <>
            <div className="text-[10px] text-[var(--color-text-muted)] uppercase tracking-wider mb-2">APIs</div>
            {sense.apis.map((api, i) => (
              <div key={i} className="p-2 rounded bg-[var(--color-bg)] border border-[var(--color-border)] mb-1.5 text-[11px]">
                <span className="font-mono text-[var(--color-info)]">{api.method}</span>
                <span className="text-[var(--color-text-secondary)] ml-1.5">{api.endpoint}</span>
                <p className="text-[var(--color-text-muted)] mt-0.5">{api.returns}</p>
              </div>
            ))}
          </>
        )}
        {sense.browserApis.length > 0 && (
          <>
            <div className="text-[10px] text-[var(--color-text-muted)] uppercase tracking-wider mb-2 mt-3">Browser APIs</div>
            <div className="space-y-1.5">
              {sense.browserApis.map((b, i) => (
                <div key={i} className="flex items-center justify-between text-[11px]">
                  <div className="flex items-center gap-2">
                    <Cpu className="w-3 h-3 text-[var(--color-text-muted)]" />
                    <span className="text-[var(--color-text-secondary)]">{b.api}</span>
                  </div>
                  <Tag color={b.complexity === 'advanced' ? 'amber' : 'neutral'}>{b.complexity}</Tag>
                </div>
              ))}
            </div>
          </>
        )}
        <div className="mt-3">
          <KV label="Lifecycle" value={sense.lifecycle} />
          <KV label="Local Sources" value={sense.localSources.length} />
        </div>
      </Section>

      <Section title="Interpret (Transforms)" icon={Workflow} count={interpret.transforms.length}>
        <div className="text-[10px] text-[var(--color-text-muted)] uppercase tracking-wider mb-2">Type System ({interpret.typeSystem.length} types)</div>
        <div className="space-y-1 mb-3">
          {interpret.typeSystem.map(t => (
            <div key={t.name} className="flex items-center justify-between text-[11px]">
              <span className="text-[var(--color-text-secondary)] font-mono">{t.name}</span>
              <span className="text-[var(--color-text-muted)]">{t.fieldCount} fields</span>
            </div>
          ))}
        </div>

        <div className="text-[10px] text-[var(--color-text-muted)] uppercase tracking-wider mb-2">Transforms</div>
        <div className="space-y-1.5">
          {interpret.transforms.map((t, i) => (
            <div key={i} className="text-[11px] p-2 rounded bg-[var(--color-bg)] border border-[var(--color-border)]">
              <span className="text-[var(--color-text-secondary)]">{t.name}</span>
              <div className="text-[var(--color-text-muted)] font-mono text-[10px] mt-0.5">{t.input} → {t.output}</div>
            </div>
          ))}
        </div>

        {interpret.algorithms.length > 0 && (
          <>
            <div className="text-[10px] text-[var(--color-text-muted)] uppercase tracking-wider mb-2 mt-3">Algorithms</div>
            <div className="space-y-1.5">
              {interpret.algorithms.map((a, i) => (
                <div key={i} className="text-[11px] p-2 rounded bg-[var(--color-bg)] border border-[var(--color-border)]">
                  <div className="flex items-center justify-between mb-0.5">
                    <span className="text-[var(--color-text-secondary)]">{a.name}</span>
                    <Tag color={a.complexity === 'nontrivial' ? 'amber' : 'neutral'}>{a.complexity}</Tag>
                  </div>
                  <p className="text-[var(--color-text-muted)] text-[10px]">{a.description}</p>
                </div>
              ))}
            </div>
          </>
        )}
      </Section>

      <Section title="Represent (Views)" icon={Eye} count={represent.views.length}>
        <div className="space-y-1 mb-3">
          <KV label="Layout" value={represent.layoutSystem} />
          <KV label="Configurable" value={represent.layoutConfigurable ? 'Yes (drag/resize)' : 'No'} />
          <KV label="Theming" value={`${represent.theming.approach} (${represent.theming.themeCount} theme${represent.theming.themeCount > 1 ? 's' : ''})`} />
          <KV label="Colors" value={represent.theming.colorModel.toUpperCase()} />
          {represent.iconLibrary && <KV label="Icons" value={represent.iconLibrary} />}
        </div>
        <div className="space-y-1.5">
          {represent.views.map(v => (
            <div key={v.name} className="flex items-center justify-between p-2 rounded bg-[var(--color-bg)] border border-[var(--color-border)] text-[11px]">
              <div>
                <span className="text-[var(--color-text-secondary)]">{v.name}</span>
                <p className="text-[var(--color-text-muted)] text-[10px]">{v.renders}</p>
              </div>
              <div className="flex items-center gap-1.5 shrink-0">
                <Tag>{v.renderTech}</Tag>
                {v.realtime && <Tag color="amber">RT</Tag>}
              </div>
            </div>
          ))}
        </div>
      </Section>

      <Section title="Dependencies" icon={Code} count={dependencies.runtime.length + dependencies.dev.length}>
        <div className="text-[10px] text-[var(--color-text-muted)] uppercase tracking-wider mb-2">Runtime</div>
        <div className="space-y-1 mb-3">
          {dependencies.runtime.map(d => (
            <div key={d.name} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-2">
                <span className="text-[var(--color-text-secondary)] font-mono">{d.name}</span>
                <span className="text-[var(--color-text-muted)] font-mono text-[10px]">{d.version}</span>
              </div>
              <Tag color={d.weight === 'heavy' ? 'rose' : d.weight === 'medium' ? 'amber' : 'neutral'}>{d.weight}</Tag>
            </div>
          ))}
        </div>
        <div className="text-[10px] text-[var(--color-text-muted)] uppercase tracking-wider mb-2">Dev</div>
        <div className="space-y-1">
          {dependencies.dev.map(d => (
            <div key={d.name} className="flex items-center justify-between text-[11px]">
              <span className="text-[var(--color-text-secondary)] font-mono">{d.name}</span>
              <span className="text-[var(--color-text-muted)] font-mono text-[10px]">{d.version}</span>
            </div>
          ))}
        </div>
      </Section>

      <Section title="Exposable Nodes" icon={Gauge} count={exposable.length} defaultOpen>
        {exposable.length === 0 ? (
          <p className="text-[11px] text-[var(--color-text-muted)] italic">No extractable nodes identified</p>
        ) : (
          <div className="space-y-2">
            {exposable.map(node => (
              <ExposableCard key={node.suggestedId} node={node} />
            ))}
          </div>
        )}
      </Section>

      <Section title="Risks" icon={Shield} count={risks.length} defaultOpen={criticalRisks > 0 || warningRisks > 0}>
        <div className="space-y-1.5">
          {[...risks].sort((a, b) => {
            const order = { critical: 0, warning: 1, info: 2 };
            return order[a.severity] - order[b.severity];
          }).map((risk, i) => (
            <RiskBadge key={i} risk={risk} />
          ))}
        </div>
      </Section>
    </div>
  );
}
