'use client';

import React, { useEffect, useState } from 'react';
import { localGet } from '@/lib/api';
import { Skeleton } from '@/components/ui';

/* ── Types ──────────────────────────────────── */

interface TimelineBucket {
  hour: number;
  label: string;
  total: number;
  by_source: Record<string, number>;
}

interface Highlight {
  oid: string;
  ts: string;
  kind: string;
  project: string | null;
  title: string;
  detail: string;
  tags: string[];
}

interface DailyDigest {
  date: string;
  generated_at: string;
  total_events: number;
  events_by_source: Record<string, number>;
  events_by_kind: Record<string, number>;
  events_by_project: Record<string, number>;
  timeline: TimelineBucket[];
  projects_active: string[];
  milestones: Array<Record<string, unknown>>;
  velocity: Record<string, number>;
  highlights: Highlight[];
}

interface DaySummary {
  date: string;
  total_events: number;
  events_by_source: Record<string, number>;
  projects_active: string[];
  velocity: Record<string, number>;
  milestones_count: number;
}

interface JournalIndex {
  days: DaySummary[];
  total_days: number;
}

/* ── Source Colors ────────────────────────────── */

const SOURCE_COLORS: Record<string, string> = {
  git: 'var(--color-emerald)',
  cli: 'var(--color-blue)',
  fs: 'var(--color-amber)',
  session: 'var(--color-rose)',
  collider: 'var(--color-purple)',
  atlas: 'var(--color-cyan)',
  system: 'var(--color-text-muted)',
};

function sourceColor(source: string): string {
  return SOURCE_COLORS[source] || 'var(--color-text-muted)';
}

/* ── Components ──────────────────────────────── */

function StatCard({
  label,
  value,
  sub,
}: {
  label: string;
  value: string | number;
  sub?: string;
}) {
  return (
    <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-[var(--radius)] p-4">
      <div className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider mb-1">
        {label}
      </div>
      <div className="text-2xl font-bold text-[var(--color-text)]">{value}</div>
      {sub && (
        <div className="text-xs text-[var(--color-text-muted)] mt-1">{sub}</div>
      )}
    </div>
  );
}

function ActivityTimeline({ timeline }: { timeline: TimelineBucket[] }) {
  const maxTotal = Math.max(...timeline.map((b) => b.total), 1);

  return (
    <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-[var(--radius)] p-4">
      <div className="text-sm font-medium text-[var(--color-text)] mb-3">
        Activity Timeline
      </div>
      <div className="flex items-end gap-[2px]" style={{ height: 120 }}>
        {timeline.map((bucket) => {
          const height = bucket.total > 0 ? (bucket.total / maxTotal) * 100 : 0;
          const sources = Object.entries(bucket.by_source);

          return (
            <div
              key={bucket.hour}
              className="flex-1 flex flex-col justify-end group relative"
              style={{ height: '100%' }}
            >
              {/* Tooltip */}
              <div className="absolute bottom-full mb-1 left-1/2 -translate-x-1/2 hidden group-hover:block z-10">
                <div className="bg-[var(--color-bg)] border border-[var(--color-border)] rounded-[var(--radius-sm)] px-2 py-1 text-[10px] text-[var(--color-text)] whitespace-nowrap shadow-lg">
                  <div className="font-medium">{bucket.label}</div>
                  {sources.map(([src, count]) => (
                    <div key={src}>
                      {src}: {count}
                    </div>
                  ))}
                  {bucket.total === 0 && <div>No activity</div>}
                </div>
              </div>

              {/* Stacked bar */}
              <div
                className="w-full rounded-t-[2px] transition-all"
                style={{
                  height: `${height}%`,
                  minHeight: bucket.total > 0 ? 2 : 0,
                  background:
                    sources.length === 1
                      ? sourceColor(sources[0][0])
                      : sources.length > 0
                        ? `linear-gradient(to top, ${sources.map(([src], i) => `${sourceColor(src)} ${(i / sources.length) * 100}%, ${sourceColor(src)} ${((i + 1) / sources.length) * 100}%`).join(', ')})`
                        : 'transparent',
                  opacity: bucket.total > 0 ? 0.8 : 0.1,
                }}
              />
              {/* Hour label (every 3 hours) */}
              {bucket.hour % 3 === 0 && (
                <div className="text-[9px] text-[var(--color-text-muted)] text-center mt-1">
                  {bucket.label}
                </div>
              )}
            </div>
          );
        })}
      </div>
      {/* Legend */}
      <div className="flex gap-3 mt-3 flex-wrap">
        {Object.entries(SOURCE_COLORS)
          .filter(([key]) => ['git', 'cli', 'fs'].includes(key))
          .map(([source, color]) => (
            <div key={source} className="flex items-center gap-1">
              <div
                className="w-2 h-2 rounded-full"
                style={{ background: color }}
              />
              <span className="text-[10px] text-[var(--color-text-muted)]">
                {source}
              </span>
            </div>
          ))}
      </div>
    </div>
  );
}

function ProjectBreakdown({
  byProject,
}: {
  byProject: Record<string, number>;
}) {
  const sorted = Object.entries(byProject)
    .filter(([k]) => k !== '_ecosystem')
    .sort((a, b) => b[1] - a[1]);
  const maxCount = Math.max(...sorted.map(([, c]) => c), 1);

  return (
    <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-[var(--radius)] p-4">
      <div className="text-sm font-medium text-[var(--color-text)] mb-3">
        Projects
      </div>
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
      </div>
    </div>
  );
}

function HighlightsFeed({ highlights }: { highlights: Highlight[] }) {
  return (
    <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-[var(--radius)] p-4">
      <div className="text-sm font-medium text-[var(--color-text)] mb-3">
        Highlights
      </div>
      <div className="space-y-2">
        {highlights.map((h) => (
          <div
            key={h.oid}
            className="flex gap-3 p-2 rounded-[var(--radius-sm)] hover:bg-[var(--color-surface-hover)] transition-colors"
          >
            <div className="text-[10px] text-[var(--color-text-muted)] font-mono whitespace-nowrap pt-0.5">
              {new Date(h.ts).toLocaleTimeString('en-US', {
                hour: '2-digit',
                minute: '2-digit',
                hour12: false,
              })}
            </div>
            <div className="min-w-0 flex-1">
              <div className="text-xs text-[var(--color-text)] truncate">
                {h.title}
              </div>
              {h.detail && (
                <div className="text-[10px] text-[var(--color-text-muted)] truncate">
                  {h.detail}
                </div>
              )}
              <div className="flex gap-1 mt-0.5">
                <span
                  className="text-[9px] px-1.5 py-0.5 rounded-full"
                  style={{
                    background: `color-mix(in oklch, ${sourceColor(h.kind === 'milestone' ? 'git' : h.kind === 'session' ? 'cli' : 'fs')} 15%, transparent)`,
                    color: sourceColor(
                      h.kind === 'milestone'
                        ? 'git'
                        : h.kind === 'session'
                          ? 'cli'
                          : 'fs'
                    ),
                  }}
                >
                  {h.kind}
                </span>
                {h.project && (
                  <span className="text-[9px] text-[var(--color-text-muted)] font-mono">
                    {h.project.replace('PROJECT_', '')}
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}
        {highlights.length === 0 && (
          <div className="text-xs text-[var(--color-text-muted)] italic">
            No highlights for this day
          </div>
        )}
      </div>
    </div>
  );
}

function DaySelector({
  days,
  selectedDate,
  onSelect,
}: {
  days: DaySummary[];
  selectedDate: string;
  onSelect: (date: string) => void;
}) {
  return (
    <div className="flex gap-2 overflow-x-auto pb-1">
      {days.map((day) => {
        const isSelected = day.date === selectedDate;
        const d = new Date(day.date + 'T12:00:00');
        const weekday = d.toLocaleDateString('en-US', { weekday: 'short' });
        const dayNum = d.getDate();

        return (
          <button
            key={day.date}
            onClick={() => onSelect(day.date)}
            className={`
              flex flex-col items-center px-3 py-2 rounded-[var(--radius)] text-xs transition-colors shrink-0
              ${
                isSelected
                  ? 'bg-[var(--color-accent)] text-[var(--color-accent-text)]'
                  : 'bg-[var(--color-surface)] border border-[var(--color-border)] text-[var(--color-text-muted)] hover:bg-[var(--color-surface-hover)]'
              }
            `}
          >
            <span className="text-[10px] uppercase">{weekday}</span>
            <span className="text-lg font-bold">{dayNum}</span>
            <span className="text-[10px]">{day.total_events} events</span>
          </button>
        );
      })}
    </div>
  );
}

/* ── Main Page ───────────────────────────────── */

export default function JournalPage() {
  const [index, setIndex] = useState<JournalIndex | null>(null);
  const [digest, setDigest] = useState<DailyDigest | null>(null);
  const [selectedDate, setSelectedDate] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load index
  useEffect(() => {
    localGet<{ success: boolean; data: JournalIndex }>('journal')
      .then((res) => {
        if (res.success && res.data.days.length > 0) {
          setIndex(res.data);
          setSelectedDate(res.data.days[0].date);
        }
      })
      .catch((err) => setError(String(err)))
      .finally(() => setLoading(false));
  }, []);

  // Load selected day's digest
  useEffect(() => {
    if (!selectedDate) return;
    localGet<{ success: boolean; data: DailyDigest }>(
      `journal?date=${selectedDate}`
    )
      .then((res) => {
        if (res.success) setDigest(res.data);
      })
      .catch(() => setDigest(null));
  }, [selectedDate]);

  if (loading) {
    return (
      <div className="p-6 space-y-4">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-32" />
        <Skeleton className="h-64" />
      </div>
    );
  }

  if (error || !index || index.days.length === 0) {
    return (
      <div className="p-6">
        <h1 className="text-xl font-semibold text-[var(--color-text)] mb-2">
          Developer Journal
        </h1>
        <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-[var(--radius)] p-8 text-center">
          <div className="text-[var(--color-text-muted)] text-sm">
            {error
              ? `Error: ${error}`
              : 'No journal data yet. Run the DevJournal pipeline:'}
          </div>
          <pre className="mt-3 text-xs font-mono text-[var(--color-accent)] bg-[var(--color-bg)] rounded-[var(--radius-sm)] p-3 inline-block">
            python wave/tools/devjournal/run.py
          </pre>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-4 max-w-[1400px]">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-[var(--color-text)]">
            Developer Journal
          </h1>
          <p className="text-xs text-[var(--color-text-muted)]">
            {index.total_days} days tracked
          </p>
        </div>
      </div>

      {/* Day selector */}
      <DaySelector
        days={index.days}
        selectedDate={selectedDate}
        onSelect={setSelectedDate}
      />

      {digest && (
        <>
          {/* Stat cards row */}
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
            <StatCard
              label="Events"
              value={digest.total_events}
              sub={`${Object.keys(digest.events_by_source).length} sources`}
            />
            <StatCard
              label="Commits"
              value={digest.velocity.commits ?? 0}
              sub={`+${digest.velocity.lines_added?.toLocaleString() ?? 0} lines`}
            />
            <StatCard
              label="Prompts"
              value={digest.velocity.prompts ?? 0}
              sub="CLI interactions"
            />
            <StatCard
              label="Files Created"
              value={digest.velocity.files_created ?? 0}
              sub={`+${digest.velocity.files_born_in_git ?? 0} in git`}
            />
            <StatCard
              label="Net Lines"
              value={
                digest.velocity.net_lines
                  ? `+${digest.velocity.net_lines.toLocaleString()}`
                  : '0'
              }
              sub={`-${digest.velocity.lines_removed?.toLocaleString() ?? 0} removed`}
            />
            <StatCard
              label="Active Hours"
              value={digest.velocity.active_hours ?? 0}
              sub="of 24h"
            />
          </div>

          {/* Main content grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Timeline - spans 2 cols */}
            <div className="lg:col-span-2">
              <ActivityTimeline timeline={digest.timeline} />
            </div>
            {/* Project breakdown */}
            <ProjectBreakdown byProject={digest.events_by_project} />
          </div>

          {/* Highlights feed */}
          <HighlightsFeed highlights={digest.highlights} />
        </>
      )}
    </div>
  );
}
