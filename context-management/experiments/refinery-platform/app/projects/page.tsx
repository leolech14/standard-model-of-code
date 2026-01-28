'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Database, ExternalLink } from 'lucide-react';
import { Badge } from '@/components/shared/Common';

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
    fetch('/api/v1/projects')
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          setProjects(data.data);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load projects:', err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-pulse text-emerald-500">Loading projects...</div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold mb-2">Projects</h1>
        <p className="text-neutral-400 text-sm">
          {projects.length} registered {projects.length === 1 ? 'project' : 'projects'} • Multi-tenant platform
        </p>
      </div>

      {/* Projects Grid */}
      <div className="grid grid-cols-2 gap-4">
        {projects.map(project => (
          <Link
            key={project.id}
            href={`/projects/${project.id}`}
            className="glass-card rounded-lg p-5 hover:border-emerald-500/50 transition-all group"
          >
            {/* Header */}
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center">
                  <Database className="w-5 h-5 text-emerald-500" />
                </div>
                <div>
                  <h3 className="font-semibold text-lg group-hover:text-emerald-400 transition-colors">
                    {project.name}
                  </h3>
                  <p className="text-xs text-neutral-500 font-mono">{project.id}</p>
                </div>
              </div>
              <ExternalLink className="w-4 h-4 text-neutral-600 group-hover:text-emerald-500 transition-colors" />
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-3 mb-4">
              <div>
                <div className="text-xs text-neutral-500 mb-1">Chunks</div>
                <div className="text-sm font-semibold">{project.health.chunk_count.toLocaleString()}</div>
              </div>
              <div>
                <div className="text-xs text-neutral-500 mb-1">Tokens</div>
                <div className="text-sm font-semibold">{(project.health.token_count / 1000).toFixed(0)}K</div>
              </div>
              <div>
                <div className="text-xs text-neutral-500 mb-1">Coverage</div>
                <div className="text-sm font-semibold">{(project.health.coverage * 100).toFixed(0)}%</div>
              </div>
            </div>

            {/* Status Bar */}
            <div className="flex items-center gap-2 text-xs">
              <Badge status={project.status} />
              <span className={`${project.status === 'active' ? 'text-emerald-400' : 'text-neutral-500'}`}>
                {project.status}
              </span>
              <span className="text-neutral-600">•</span>
              <span className="text-neutral-500">
                Updated {project.health.freshness_hours}h ago
              </span>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
