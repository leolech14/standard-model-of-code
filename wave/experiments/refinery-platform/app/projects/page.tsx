'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Database, ExternalLink } from 'lucide-react';
import { Badge } from '@/components/shared/Common';
import { Skeleton } from '@/components/ui';
import { localGet } from '@/lib/api';

interface Project {
  id: string;
  name: string;
  path: string;
  status: string;
  last_processed: string;
  health: {
    chunk_count: number;
    token_count: number;
    file_count: number;
    coverage: number;
    freshness_hours: number;
    error_count: number;
  };
}

export default function ProjectsPage() {
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
        <Skeleton className="h-8 w-48" />
        <div className="grid grid-cols-2 gap-4">
          {[...Array(4)].map((_, i) => <Skeleton key={i} className="h-48" />)}
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold mb-2">Projects</h1>
        <p className="text-text-secondary text-sm">
          {projects.length} registered {projects.length === 1 ? 'project' : 'projects'} &bull; Multi-tenant platform
        </p>
      </div>

      {/* Projects Grid */}
      <div className="grid grid-cols-2 gap-4">
        {projects.map(project => (
          <Link
            key={project.id}
            href={`/projects/${project.id}`}
            className="glass-card rounded-lg p-5 hover:border-accent/50 transition-all group"
          >
            {/* Header */}
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-accent/10 border border-accent/30 flex items-center justify-center">
                  <Database className="w-5 h-5 text-accent" />
                </div>
                <div>
                  <h3 className="font-semibold text-lg group-hover:text-accent transition-colors">
                    {project.name}
                  </h3>
                  <p className="text-xs text-text-muted font-mono">{project.id}</p>
                </div>
              </div>
              <ExternalLink className="w-4 h-4 text-text-muted group-hover:text-accent transition-colors" />
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-3 mb-4">
              <div>
                <div className="text-xs text-text-muted mb-1">Chunks</div>
                <div className="text-sm font-semibold">{project.health.chunk_count.toLocaleString()}</div>
              </div>
              <div>
                <div className="text-xs text-text-muted mb-1">Tokens</div>
                <div className="text-sm font-semibold">{(project.health.token_count / 1000).toFixed(0)}K</div>
              </div>
              <div>
                <div className="text-xs text-text-muted mb-1">Coverage</div>
                <div className="text-sm font-semibold">{(project.health.coverage * 100).toFixed(0)}%</div>
              </div>
            </div>

            {/* Status Bar */}
            <div className="flex items-center gap-2 text-xs">
              <Badge status={project.status} />
              <span className={`${project.status === 'active' ? 'text-accent' : 'text-text-muted'}`}>
                {project.status}
              </span>
              <span className="text-text-muted">&bull;</span>
              <span className="text-text-muted">
                Updated {project.health.freshness_hours}h ago
              </span>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
