'use client';

import { useEffect, useState } from 'react';
import { Database, Activity, Box, Settings } from 'lucide-react';

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
        <div className="animate-pulse text-emerald-500">Loading Platform...</div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Platform Overview */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Platform Overview</h1>
        <p className="text-neutral-400">
          Multi-tenant context processing • L7 → L8 evolution • Independent spinoff
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        <div className="glass-card rounded-lg p-4">
          <div className="flex items-center gap-3 mb-2">
            <Database className="w-5 h-5 text-emerald-500" />
            <span className="text-xs text-neutral-500 uppercase tracking-wider">Projects</span>
          </div>
          <div className="text-2xl font-bold">{projects.length}</div>
        </div>

        <div className="glass-card rounded-lg p-4">
          <div className="flex items-center gap-3 mb-2">
            <Box className="w-5 h-5 text-blue-500" />
            <span className="text-xs text-neutral-500 uppercase tracking-wider">Total Chunks</span>
          </div>
          <div className="text-2xl font-bold">
            {projects.reduce((sum, p) => sum + p.health.chunk_count, 0).toLocaleString()}
          </div>
        </div>

        <div className="glass-card rounded-lg p-4">
          <div className="flex items-center gap-3 mb-2">
            <Activity className="w-5 h-5 text-purple-500" />
            <span className="text-xs text-neutral-500 uppercase tracking-wider">Total Tokens</span>
          </div>
          <div className="text-2xl font-bold">
            {(projects.reduce((sum, p) => sum + p.health.token_count, 0) / 1000).toFixed(0)}K
          </div>
        </div>

        <div className="glass-card rounded-lg p-4">
          <div className="flex items-center gap-3 mb-2">
            <Activity className="w-5 h-5 text-emerald-500" />
            <span className="text-xs text-neutral-500 uppercase tracking-wider">Avg Coverage</span>
          </div>
          <div className="text-2xl font-bold">
            {(projects.reduce((sum, p) => sum + p.health.coverage, 0) / projects.length * 100).toFixed(0)}%
          </div>
        </div>
      </div>

      {/* Recent Projects */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Recent Projects</h2>
        <div className="space-y-3">
          {projects.slice(0, 3).map(project => (
            <div
              key={project.id}
              className="glass-card rounded-lg p-5 hover:border-emerald-500/50 transition-colors cursor-pointer"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-lg mb-1">{project.name}</h3>
                  <p className="text-sm text-neutral-400 mb-3">
                    {project.health.chunk_count.toLocaleString()} chunks • {' '}
                    {(project.health.token_count / 1000).toFixed(0)}K tokens • {' '}
                    {(project.health.coverage * 100).toFixed(0)}% coverage
                  </p>
                  <div className="flex gap-2">
                    <span className={`text-xs px-2 py-1 rounded ${
                      project.status === 'active'
                        ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                        : 'bg-neutral-800 text-neutral-400'
                    }`}>
                      {project.status}
                    </span>
                    <span className="text-xs px-2 py-1 rounded bg-neutral-800 text-neutral-400">
                      Updated {project.health.freshness_hours}h ago
                    </span>
                  </div>
                </div>
                <button className="px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-black rounded-md text-sm font-medium transition-colors">
                  Open
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Platform Status */}
      <div className="mt-8 glass-card rounded-lg p-6">
        <h3 className="text-sm font-semibold text-neutral-400 uppercase tracking-wider mb-3">
          Platform Status
        </h3>
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div>
            <div className="text-neutral-500 mb-1">Level</div>
            <div className="font-mono text-emerald-400">L7 System → L8 Platform</div>
          </div>
          <div>
            <div className="text-neutral-500 mb-1">Type</div>
            <div className="font-mono text-purple-400">Independent Spinoff</div>
          </div>
          <div>
            <div className="text-neutral-500 mb-1">Origin</div>
            <div className="font-mono text-blue-400">PROJECT_elements</div>
          </div>
        </div>
      </div>
    </div>
  );
}
