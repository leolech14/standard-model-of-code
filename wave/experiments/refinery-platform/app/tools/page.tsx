'use client';

import React, { useEffect, useState } from 'react';
import { localGet } from '@/lib/api';
import { Skeleton } from '@/components/ui';
import { Folder, FileCode, Clock } from 'lucide-react';

interface Tool {
  name: string;
  path: string;
  type: 'directory' | 'file';
  description: string;
  modified: string;
  fileCount?: number;
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

export default function ToolsPage() {
  const [tools, setTools] = useState<Tool[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    localGet<{ success: boolean; data: { tools: Tool[] } }>('tools')
      .then((res) => { if (res.success) setTools(res.data.tools); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="p-6 space-y-3">
        <Skeleton className="h-8 w-48" />
        {[...Array(6)].map((_, i) => <Skeleton key={i} className="h-16" />)}
      </div>
    );
  }

  const dirs = tools.filter((t) => t.type === 'directory');
  const files = tools.filter((t) => t.type === 'file');

  return (
    <div className="p-6 space-y-6 max-w-[1200px]">
      <div>
        <h1 className="text-xl font-semibold text-[var(--color-text)]">Tools</h1>
        <p className="text-xs text-[var(--color-text-muted)]">
          {tools.length} tools in wave/tools/
        </p>
      </div>

      {dirs.length > 0 && (
        <div>
          <h2 className="text-xs font-semibold tracking-wider uppercase text-[var(--color-accent)] mb-2">
            Tool Packages
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {dirs.map((tool) => (
              <div
                key={tool.path}
                className="flex items-start gap-3 p-3 rounded-[var(--radius)] border border-[var(--color-border)] bg-[var(--color-surface)] hover:bg-[var(--color-surface-hover)] transition-colors"
              >
                <div className="w-9 h-9 rounded-[var(--radius-sm)] bg-[var(--color-accent)]/10 flex items-center justify-center shrink-0">
                  <Folder className="w-4 h-4 text-[var(--color-accent)]" />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="text-sm font-medium text-[var(--color-text)]">{tool.name}</div>
                  <div className="text-xs text-[var(--color-text-muted)]">{tool.description}</div>
                  <div className="flex items-center gap-1 mt-1 text-[10px] text-[var(--color-text-muted)]">
                    <Clock className="w-3 h-3" />
                    {formatDate(tool.modified)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {files.length > 0 && (
        <div>
          <h2 className="text-xs font-semibold tracking-wider uppercase text-[var(--color-accent)] mb-2">
            Standalone Scripts
          </h2>
          <div className="space-y-1">
            {files.map((tool) => (
              <div
                key={tool.path}
                className="flex items-center gap-3 px-3 py-2 rounded-[var(--radius-sm)] hover:bg-[var(--color-surface-hover)] transition-colors"
              >
                <FileCode className="w-4 h-4 text-[var(--color-text-muted)] shrink-0" />
                <span className="flex-1 text-sm text-[var(--color-text-secondary)] font-mono">{tool.name}</span>
                <span className="text-xs text-[var(--color-text-muted)]">{tool.description}</span>
                <span className="text-xs text-[var(--color-text-muted)]">{formatDate(tool.modified)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
