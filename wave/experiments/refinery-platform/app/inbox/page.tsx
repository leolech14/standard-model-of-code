'use client';

import { useState } from 'react';
import {
  Inbox, Package, ArrowRight, Clock4, FileCode,
  ChevronLeft, Gauge, Shield, AlertTriangle,
} from 'lucide-react';
import { getAllSpecs } from '@/lib/ingestion/specs';
import { AppSpecInspector } from '@/components/ingestion/AppSpecInspector';
import type { AppSpec } from '@/lib/ingestion/types';

const specs = getAllSpecs();

function timeAgo(ms: number): string {
  const mins = Math.floor((Date.now() - ms) / 60_000);
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

export default function InboxPage() {
  const [selectedSpec, setSelectedSpec] = useState<AppSpec | null>(null);

  const totalExposable = specs.reduce((s, a) => s + a.exposable.length, 0);
  const promotable = specs.reduce((s, a) => s + a.exposable.filter(e => e.confidence >= 0.75).length, 0);
  const totalRisks = specs.reduce((s, a) => s + a.risks.filter(r => r.severity !== 'info').length, 0);

  // Drill-in view
  if (selectedSpec) {
    return (
      <div className="h-full flex flex-col">
        {/* Back bar */}
        <div className="px-6 py-3 border-b border-[var(--color-border)] bg-[var(--color-surface)] flex items-center gap-3">
          <button
            onClick={() => setSelectedSpec(null)}
            className="flex items-center gap-1.5 text-sm text-[var(--color-text-muted)] hover:text-[var(--color-text)] transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
            Back to Inbox
          </button>
          <span className="text-[var(--color-text-muted)]">/</span>
          <span className="text-sm font-medium text-[var(--color-text)]">{selectedSpec.meta.name}</span>
          <span className={`ml-auto text-[10px] px-2 py-0.5 rounded font-mono ${
            selectedSpec.meta.status === 'ready'
              ? 'bg-[oklch(var(--emerald-l)_var(--emerald-c)_var(--emerald-h)/0.1)] text-[var(--color-accent)]'
              : 'bg-[var(--color-surface)] text-[var(--color-text-muted)]'
          }`}>
            {selectedSpec.meta.status}
          </span>
        </div>

        {/* Inspector */}
        <div className="flex-1 overflow-hidden">
          <AppSpecInspector spec={selectedSpec} />
        </div>
      </div>
    );
  }

  // Listing view
  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Inbox className="w-6 h-6 text-[var(--color-warning)]" />
          <h1 className="text-3xl font-bold">Apps Inbox</h1>
        </div>
        <p className="text-text-secondary">
          Code-to-Spec ingestion pipeline &bull; Reverse-engineer incoming apps into structured specifications
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        <div className="glass-card rounded-lg p-4">
          <div className="flex items-center gap-3 mb-2">
            <Package className="w-5 h-5 text-[var(--color-warning)]" />
            <span className="text-xs text-text-muted uppercase tracking-wider">Apps</span>
          </div>
          <div className="text-2xl font-bold">{specs.length}</div>
        </div>

        <div className="glass-card rounded-lg p-4">
          <div className="flex items-center gap-3 mb-2">
            <Gauge className="w-5 h-5 text-[var(--color-accent)]" />
            <span className="text-xs text-text-muted uppercase tracking-wider">Exposable Nodes</span>
          </div>
          <div className="text-2xl font-bold">{totalExposable}</div>
        </div>

        <div className="glass-card rounded-lg p-4">
          <div className="flex items-center gap-3 mb-2">
            <ArrowRight className="w-5 h-5 text-[var(--color-info)]" />
            <span className="text-xs text-text-muted uppercase tracking-wider">Promotable</span>
          </div>
          <div className="text-2xl font-bold text-[var(--color-accent)]">{promotable}</div>
        </div>

        <div className="glass-card rounded-lg p-4">
          <div className="flex items-center gap-3 mb-2">
            <Shield className="w-5 h-5 text-[var(--color-danger)]" />
            <span className="text-xs text-text-muted uppercase tracking-wider">Risks</span>
          </div>
          <div className="text-2xl font-bold">{totalRisks}</div>
        </div>
      </div>

      {/* App cards */}
      <h2 className="text-xl font-semibold mb-4">Ingested Applications</h2>
      <div className="space-y-4">
        {specs.map(spec => {
          const highConfNodes = spec.exposable.filter(e => e.confidence >= 0.75);
          const warnings = spec.risks.filter(r => r.severity === 'warning').length;
          const criticals = spec.risks.filter(r => r.severity === 'critical').length;

          return (
            <div
              key={spec.meta.id}
              onClick={() => setSelectedSpec(spec)}
              className="glass-card rounded-lg p-5 hover:border-[var(--color-accent)]/50 transition-colors cursor-pointer group"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  {/* Title row */}
                  <div className="flex items-center gap-3 mb-2">
                    <div className="w-9 h-9 rounded-lg bg-[var(--color-surface)] flex items-center justify-center shrink-0">
                      <FileCode className="w-4.5 h-4.5 text-[var(--color-text-secondary)]" />
                    </div>
                    <div className="min-w-0">
                      <h3 className="font-semibold text-lg truncate">{spec.meta.name}</h3>
                      <p className="text-sm text-text-secondary truncate">{spec.meta.description}</p>
                    </div>
                  </div>

                  {/* Stack tags */}
                  <div className="flex flex-wrap gap-1.5 mb-3 ml-12">
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-[oklch(var(--blue-l)_var(--blue-c)_var(--blue-h)/0.1)] text-[var(--color-info)] border border-[oklch(var(--blue-l)_var(--blue-c)_var(--blue-h)/0.2)]">
                      {spec.meta.stack.framework}
                    </span>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-[var(--color-surface)] text-[var(--color-text-secondary)] border border-[var(--color-border)]">
                      {spec.meta.stack.bundler}
                    </span>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-[var(--color-surface)] text-[var(--color-text-secondary)] border border-[var(--color-border)]">
                      {spec.meta.stack.language}
                    </span>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-[var(--color-surface)] text-[var(--color-text-secondary)] border border-[var(--color-border)]">
                      {spec.meta.stack.styling}
                    </span>
                  </div>

                  {/* Metrics row */}
                  <div className="flex items-center gap-5 ml-12 text-xs text-text-muted">
                    <span>{spec.meta.fileCount} files</span>
                    <span>{(spec.meta.sizeBytes / 1024).toFixed(0)} KB</span>
                    <span>{spec.architecture.componentTree.length} components</span>
                    <span className="text-[var(--color-accent)]">{spec.exposable.length} exposable nodes</span>
                    {highConfNodes.length > 0 && (
                      <span className="text-[var(--color-accent)] font-medium">{highConfNodes.length} promotable</span>
                    )}
                    {warnings > 0 && (
                      <span className="flex items-center gap-1 text-[var(--color-warning)]">
                        <AlertTriangle className="w-3 h-3" />{warnings}
                      </span>
                    )}
                    {criticals > 0 && (
                      <span className="flex items-center gap-1 text-[var(--color-danger)]">
                        <AlertTriangle className="w-3 h-3" />{criticals}
                      </span>
                    )}
                  </div>
                </div>

                {/* Right side */}
                <div className="flex flex-col items-end gap-2 ml-4 shrink-0">
                  <span className={`text-[10px] px-2 py-0.5 rounded font-mono ${
                    spec.meta.status === 'ready'
                      ? 'bg-[oklch(var(--emerald-l)_var(--emerald-c)_var(--emerald-h)/0.1)] text-[var(--color-accent)]'
                      : 'bg-[var(--color-surface)] text-[var(--color-text-muted)]'
                  }`}>
                    {spec.meta.status}
                  </span>
                  <span className="flex items-center gap-1 text-[10px] text-[var(--color-text-muted)]">
                    <Clock4 className="w-3 h-3" />
                    {timeAgo(spec.meta.ingestedAt)}
                  </span>
                  <ArrowRight className="w-4 h-4 text-[var(--color-text-muted)] group-hover:text-[var(--color-accent)] transition-colors mt-1" />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Footer */}
      <div className="mt-8 glass-card rounded-lg p-6">
        <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wider mb-3">
          Ingestion Pipeline
        </h3>
        <div className="grid grid-cols-4 gap-4 text-sm">
          <div>
            <div className="text-text-muted mb-1">Pipeline</div>
            <div className="font-mono text-[var(--color-accent)]">Code → Spec</div>
          </div>
          <div>
            <div className="text-text-muted mb-1">Bridge</div>
            <div className="font-mono text-[var(--color-info)]">ExposableNode</div>
          </div>
          <div>
            <div className="text-text-muted mb-1">Threshold</div>
            <div className="font-mono text-[var(--color-warning)]">&ge; 75% confidence</div>
          </div>
          <div>
            <div className="text-text-muted mb-1">Target</div>
            <div className="font-mono text-[var(--color-accent)]">NodeDefinition</div>
          </div>
        </div>
      </div>
    </div>
  );
}
