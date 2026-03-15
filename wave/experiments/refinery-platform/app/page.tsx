'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Database, Activity, Box, Inbox, ArrowRight, Package } from 'lucide-react';
import { Skeleton } from '@/components/ui';
import { localGet } from '@/lib/api';
import { getAllSpecs } from '@/lib/ingestion/specs';

interface Project {
  id: string;
  name: string;
  status: string;
  health: {
    chunk_count: number;
    token_count: number;
    coverage: number;
    freshness_hours: number;
  };
}

export default function Home() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    localGet<{ success: boolean; data: Project[] }>('projects')
      .then(res => {
        if (res.success) setProjects(res.data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="p-6 space-y-6">
        <Skeleton className="h-8 w-64" />
        <div className="grid grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => <Skeleton key={i} className="h-24" />)}
        </div>
        <Skeleton className="h-48" />
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Platform Overview */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Platform Overview</h1>
        <p className="text-text-secondary">
          Multi-tenant context processing &bull; L7 &rarr; L8 evolution &bull; Independent spinoff
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        <div className="glass-card rounded-lg p-4">
          <div className="flex items-center gap-3 mb-2">
            <Database className="w-5 h-5 text-accent" />
            <span className="text-xs text-text-muted uppercase tracking-wider">Projects</span>
          </div>
          <div className="text-2xl font-bold">{projects.length}</div>
        </div>

        <div className="glass-card rounded-lg p-4">
          <div className="flex items-center gap-3 mb-2">
            <Box className="w-5 h-5 text-info" />
            <span className="text-xs text-text-muted uppercase tracking-wider">Total Chunks</span>
          </div>
          <div className="text-2xl font-bold">
            {projects.reduce((sum, p) => sum + p.health.chunk_count, 0).toLocaleString()}
          </div>
        </div>

        <div className="glass-card rounded-lg p-4">
          <div className="flex items-center gap-3 mb-2">
            <Activity className="w-5 h-5 text-purple" />
            <span className="text-xs text-text-muted uppercase tracking-wider">Total Tokens</span>
          </div>
          <div className="text-2xl font-bold">
            {(projects.reduce((sum, p) => sum + p.health.token_count, 0) / 1000).toFixed(0)}K
          </div>
        </div>

        <div className="glass-card rounded-lg p-4">
          <div className="flex items-center gap-3 mb-2">
            <Activity className="w-5 h-5 text-accent" />
            <span className="text-xs text-text-muted uppercase tracking-wider">Avg Coverage</span>
          </div>
          <div className="text-2xl font-bold">
            {(projects.reduce((sum, p) => sum + p.health.coverage, 0) / projects.length * 100).toFixed(0)}%
          </div>
        </div>
      </div>

      {/* Apps Inbox */}
      {(() => {
        const inboxApps = getAllSpecs();
        const promotable = inboxApps.reduce((s, a) => s + a.exposable.filter(e => e.confidence >= 0.75).length, 0);
        return (
          <div className="mb-8">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">Apps Inbox</h2>
              <Link href="/inbox" className="flex items-center gap-1 text-sm text-[var(--color-accent)] hover:text-[var(--color-accent-hover)] transition-colors">
                View all <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
            <div className="glass-card rounded-lg p-5 border-dashed border-[var(--color-warning)]/30">
              <div className="flex items-center gap-3 mb-4">
                <Inbox className="w-5 h-5 text-[var(--color-warning)]" />
                <span className="text-sm font-medium">{inboxApps.length} apps pending review</span>
                {promotable > 0 && (
                  <span className="text-[10px] px-2 py-0.5 rounded bg-[oklch(var(--emerald-l)_var(--emerald-c)_var(--emerald-h)/0.1)] text-[var(--color-accent)] ml-auto">
                    {promotable} nodes promotable
                  </span>
                )}
              </div>
              <div className="space-y-2">
                {inboxApps.map(app => (
                  <Link
                    key={app.meta.id}
                    href="/inbox"
                    className="flex items-center justify-between p-3 rounded bg-[var(--color-bg)] border border-[var(--color-border)] hover:border-[var(--color-accent)]/30 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <Package className="w-4 h-4 text-[var(--color-text-muted)]" />
                      <div>
                        <div className="text-sm font-medium">{app.meta.name}</div>
                        <div className="text-[10px] text-text-muted">
                          {app.meta.stack.framework} &bull; {app.meta.fileCount} files &bull; {app.exposable.length} exposable nodes
                        </div>
                      </div>
                    </div>
                    <span className={`text-[10px] px-1.5 py-0.5 rounded font-mono ${
                      app.meta.status === 'ready'
                        ? 'bg-[oklch(var(--emerald-l)_var(--emerald-c)_var(--emerald-h)/0.1)] text-[var(--color-accent)]'
                        : 'bg-[var(--color-surface)] text-[var(--color-text-muted)]'
                    }`}>
                      {app.meta.status}
                    </span>
                  </Link>
                ))}
              </div>
            </div>
          </div>
        );
      })()}

      {/* Recent Projects */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Recent Projects</h2>
        <div className="space-y-3">
          {projects.slice(0, 3).map(project => (
            <div
              key={project.id}
              className="glass-card rounded-lg p-5 hover:border-accent/50 transition-colors cursor-pointer"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-lg mb-1">{project.name}</h3>
                  <p className="text-sm text-text-secondary mb-3">
                    {project.health.chunk_count.toLocaleString()} chunks &bull;{' '}
                    {(project.health.token_count / 1000).toFixed(0)}K tokens &bull;{' '}
                    {(project.health.coverage * 100).toFixed(0)}% coverage
                  </p>
                  <div className="flex gap-2">
                    <span className={`text-xs px-2 py-1 rounded ${
                      project.status === 'active'
                        ? 'bg-accent/20 text-accent border border-accent/30'
                        : 'bg-surface text-text-secondary'
                    }`}>
                      {project.status}
                    </span>
                    <span className="text-xs px-2 py-1 rounded bg-surface text-text-secondary">
                      Updated {project.health.freshness_hours}h ago
                    </span>
                  </div>
                </div>
                <button className="px-4 py-2 bg-accent hover:bg-accent-hover text-accent-text rounded-md text-sm font-medium transition-colors">
                  Open
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Platform Status */}
      <div className="mt-8 glass-card rounded-lg p-6">
        <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wider mb-3">
          Platform Status
        </h3>
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div>
            <div className="text-text-muted mb-1">Level</div>
            <div className="font-mono text-accent">L7 System &rarr; L8 Platform</div>
          </div>
          <div>
            <div className="text-text-muted mb-1">Type</div>
            <div className="font-mono text-purple">Independent Spinoff</div>
          </div>
          <div>
            <div className="text-text-muted mb-1">Origin</div>
            <div className="font-mono text-info">PROJECT_elements</div>
          </div>
        </div>
      </div>
    </div>
  );
}
