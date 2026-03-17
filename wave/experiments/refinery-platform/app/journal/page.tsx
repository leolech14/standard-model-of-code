'use client';

import React from 'react';
import { SemanticPage } from '@/lib/nodes/SemanticPage';
import type { CustomViewComponent } from '@/lib/nodes/NodeRenderer';

/* ── Source Colors (parametric tokens, all 8 ETS sources) ── */

const SOURCE_COLORS: Record<string, string> = {
  git: 'var(--color-emerald)',
  cli: 'var(--color-blue)',
  fs: 'var(--color-amber)',
  session: 'var(--color-rose)',
  memory: 'var(--color-purple)',
  plan: 'var(--color-teal)',
  git_notes: 'var(--color-emerald-dim)',
  xattr: 'var(--color-amber-dim)',
  system: 'var(--color-text-muted)',
  collider: 'var(--color-purple)',
};

function sourceColor(source: string): string {
  return SOURCE_COLORS[source] || 'var(--color-text-muted)';
}

/* ── Custom Views (semantic escape hatches) ─── */

/**
 * Timeline Chart — renders hourly activity bars.
 * Registered as customViewId: 'timeline-chart'
 */
const TimelineChart: CustomViewComponent = ({ data }) => {
  const timeline = Array.isArray(data) ? data : [];
  const maxTotal = Math.max(...timeline.map((b: Record<string, unknown>) => (b.total as number) || 0), 1);

  return (
    <div>
      <div className="flex items-end gap-[2px]" style={{ height: 120 }}>
        {timeline.map((bucket: Record<string, unknown>) => {
          const total = (bucket.total as number) || 0;
          const height = total > 0 ? (total / maxTotal) * 100 : 0;
          const bySrc = (bucket.by_source as Record<string, number>) || {};
          const sources = Object.entries(bySrc);
          const hour = bucket.hour as number;

          return (
            <div
              key={hour}
              className="flex-1 flex flex-col justify-end group relative"
              style={{ height: '100%' }}
            >
              <div className="absolute bottom-full mb-1 left-1/2 -translate-x-1/2 hidden group-hover:block z-10">
                <div className="bg-[var(--color-bg)] border border-[var(--color-border)] rounded-[var(--radius-sm)] px-2 py-1 text-[10px] text-[var(--color-text)] whitespace-nowrap shadow-lg">
                  <div className="font-medium">{String(hour).padStart(2, '0')}:00</div>
                  {sources.map(([src, count]) => (
                    <div key={src}>{src}: {count}</div>
                  ))}
                  {total === 0 && <div>No activity</div>}
                </div>
              </div>
              <div
                className="w-full rounded-t-[2px] transition-all"
                style={{
                  height: `${height}%`,
                  minHeight: total > 0 ? 2 : 0,
                  background: sources.length === 1
                    ? sourceColor(sources[0][0])
                    : sources.length > 0
                      ? `linear-gradient(to top, ${sources.map(([src], i) => `${sourceColor(src)} ${(i / sources.length) * 100}%, ${sourceColor(src)} ${((i + 1) / sources.length) * 100}%`).join(', ')})`
                      : 'transparent',
                  opacity: total > 0 ? 0.8 : 0.1,
                }}
              />
              {hour % 3 === 0 && (
                <div className="text-[9px] text-[var(--color-text-muted)] text-center mt-1">
                  {String(hour).padStart(2, '0')}:00
                </div>
              )}
            </div>
          );
        })}
      </div>
      <div className="flex gap-3 mt-3 flex-wrap">
        {Object.entries(SOURCE_COLORS)
          .filter(([key]) => ['git', 'cli', 'fs', 'session', 'memory', 'plan'].includes(key))
          .map(([source, color]) => (
            <div key={source} className="flex items-center gap-1">
              <div className="w-2 h-2 rounded-full" style={{ background: color }} />
              <span className="text-[10px] text-[var(--color-text-muted)]">{source}</span>
            </div>
          ))}
      </div>
    </div>
  );
};

/**
 * Project Breakdown — horizontal bars by project.
 * Registered as customViewId: 'project-breakdown'
 */
const ProjectBreakdown: CustomViewComponent = ({ data }) => {
  const byProject = (data && typeof data === 'object' && !Array.isArray(data))
    ? data as Record<string, number>
    : {};
  const sorted = Object.entries(byProject)
    .filter(([k]) => k !== '_ecosystem')
    .sort((a, b) => b[1] - a[1]);
  const maxCount = Math.max(...sorted.map(([, c]) => c), 1);

  return (
    <div className="space-y-2">
      {sorted.map(([project, count]) => (
        <div key={project}>
          <div className="flex justify-between text-xs mb-0.5">
            <span className="text-[var(--color-text-secondary)] font-mono">
              {project.replace('PROJECT_', '')}
            </span>
            <span className="text-[var(--color-text-muted)]">{count}</span>
          </div>
          <div className="h-1.5 rounded-full bg-[var(--color-surface-hover)] overflow-hidden">
            <div
              className="h-full rounded-full transition-all"
              style={{
                width: `${(count / maxCount) * 100}%`,
                background: 'var(--color-accent)',
                opacity: 0.7,
              }}
            />
          </div>
        </div>
      ))}
      {sorted.length === 0 && (
        <div className="text-xs text-[var(--color-text-muted)] italic">No project data</div>
      )}
    </div>
  );
};

/**
 * Source Breakdown — horizontal bars by trace source.
 * Registered as customViewId: 'source-breakdown'
 */
const SourceBreakdown: CustomViewComponent = ({ data }) => {
  const bySource = (data && typeof data === 'object' && !Array.isArray(data))
    ? data as Record<string, number>
    : {};
  const sorted = Object.entries(bySource).sort((a, b) => b[1] - a[1]);
  const maxCount = Math.max(...sorted.map(([, c]) => c), 1);
  const total = sorted.reduce((sum, [, c]) => sum + c, 0);

  return (
    <div className="space-y-2">
      {sorted.map(([source, count]) => {
        const pct = total > 0 ? ((count / total) * 100).toFixed(0) : '0';
        return (
          <div key={source}>
            <div className="flex justify-between text-xs mb-0.5">
              <div className="flex items-center gap-1.5">
                <div
                  className="w-2 h-2 rounded-full"
                  style={{ background: sourceColor(source) }}
                />
                <span className="text-[var(--color-text-secondary)] font-mono">{source}</span>
              </div>
              <span className="text-[var(--color-text-muted)]">
                {count} <span className="text-[10px]">({pct}%)</span>
              </span>
            </div>
            <div className="h-1.5 rounded-full bg-[var(--color-surface-hover)] overflow-hidden">
              <div
                className="h-full rounded-full transition-all"
                style={{
                  width: `${(count / maxCount) * 100}%`,
                  background: sourceColor(source),
                  opacity: 0.7,
                }}
              />
            </div>
          </div>
        );
      })}
      {sorted.length === 0 && (
        <div className="text-xs text-[var(--color-text-muted)] italic">No source data</div>
      )}
    </div>
  );
};

/**
 * Signature Panel — shows AI model attribution from highlights.
 * Filters highlights for ai_session entries and shows model + token usage.
 * Registered as customViewId: 'signature-panel'
 */
const SignaturePanel: CustomViewComponent = ({ data }) => {
  const highlights = Array.isArray(data) ? data : [];
  const aiSessions = highlights.filter(
    (h: Record<string, unknown>) => h.kind === 'ai_session'
  );
  const memoryEvents = highlights.filter(
    (h: Record<string, unknown>) =>
      h.kind === 'memory_written' || h.kind === 'memory_updated'
  );

  if (aiSessions.length === 0 && memoryEvents.length === 0) {
    return (
      <div className="text-xs text-[var(--color-text-muted)] italic">
        No AI attribution data for this day
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {aiSessions.length > 0 && (
        <div>
          <div className="text-[10px] text-[var(--color-text-muted)] uppercase tracking-wider mb-1.5">
            AI Sessions
          </div>
          <div className="space-y-1.5">
            {aiSessions.map((session: Record<string, unknown>, i: number) => (
              <div
                key={i}
                className="flex items-center justify-between text-xs bg-[var(--color-surface)] rounded-[var(--radius-sm)] px-2.5 py-1.5"
              >
                <div className="flex items-center gap-2">
                  <div
                    className="w-1.5 h-1.5 rounded-full"
                    style={{ background: 'var(--color-rose)' }}
                  />
                  <span className="text-[var(--color-text)] font-mono text-[11px]">
                    {String(session.title || '')}
                  </span>
                </div>
                <span className="text-[var(--color-text-muted)] text-[10px]">
                  {String(session.detail || '')}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
      {memoryEvents.length > 0 && (
        <div>
          <div className="text-[10px] text-[var(--color-text-muted)] uppercase tracking-wider mb-1.5">
            Memory Activity
          </div>
          <div className="space-y-1">
            {memoryEvents.map((mem: Record<string, unknown>, i: number) => (
              <div
                key={i}
                className="text-xs text-[var(--color-text-secondary)] flex items-center gap-1.5"
              >
                <div
                  className="w-1.5 h-1.5 rounded-full"
                  style={{ background: 'var(--color-purple)' }}
                />
                <span>{String(mem.title || '')}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

/**
 * Correlation View — shows corroborated work sessions.
 * Filters highlights for work_session entries.
 * Registered as customViewId: 'correlation-view'
 */
const CorrelationView: CustomViewComponent = ({ data }) => {
  const highlights = Array.isArray(data) ? data : [];
  const sessions = highlights.filter(
    (h: Record<string, unknown>) => h.kind === 'work_session'
  );

  if (sessions.length === 0) {
    return (
      <div className="text-xs text-[var(--color-text-muted)] italic">
        No correlated work sessions detected
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {sessions.map((session: Record<string, unknown>, i: number) => {
        const tags = (session.tags as string[]) || [];
        const sourceTags = tags.filter((t: string) => t !== 'corroborated');
        return (
          <div
            key={i}
            className="bg-[var(--color-surface)] rounded-[var(--radius-sm)] px-3 py-2 border border-[var(--color-border)]"
          >
            <div className="text-xs text-[var(--color-text)] mb-1">
              {String(session.title || '')}
            </div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] text-[var(--color-text-muted)]">
                {String(session.detail || '')}
              </span>
              <div className="flex gap-1 ml-auto">
                {sourceTags.map((tag: string) => (
                  <div
                    key={tag}
                    className="w-2 h-2 rounded-full"
                    style={{ background: sourceColor(tag) }}
                    title={tag}
                  />
                ))}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

/* ── Custom views registry ───────────────────── */

const JOURNAL_CUSTOM_VIEWS: Record<string, CustomViewComponent> = {
  'timeline-chart': TimelineChart,
  'project-breakdown': ProjectBreakdown,
  'source-breakdown': SourceBreakdown,
  'signature-panel': SignaturePanel,
  'correlation-view': CorrelationView,
};

/* ── Page ─────────────────────────────────────── */

export default function JournalPage() {
  return (
    <SemanticPage
      domain="journal"
      customViews={JOURNAL_CUSTOM_VIEWS}
    />
  );
}
