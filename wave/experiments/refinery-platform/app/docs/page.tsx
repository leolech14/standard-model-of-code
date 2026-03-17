'use client';

import React, { useEffect, useState } from 'react';
import { localGet } from '@/lib/api';
import { Skeleton } from '@/components/ui';

interface DocEntry {
  id: string;
  title: string;
  relativePath: string;
  type: 'html' | 'markdown';
  category: string;
  size: number;
  modified: string;
}

interface DocsData {
  total: number;
  categories: Record<string, DocEntry[]>;
}

const TYPE_COLORS: Record<string, string> = {
  html: 'var(--color-emerald)',
  markdown: 'var(--color-blue)',
};

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes}B`;
  if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)}KB`;
  return `${(bytes / 1048576).toFixed(1)}MB`;
}

function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

export default function DocsPage() {
  const [data, setData] = useState<DocsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('');

  useEffect(() => {
    localGet<{ success: boolean; data: DocsData }>('docs')
      .then((res) => {
        if (res.success) setData(res.data);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="p-6 space-y-4">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-64" />
      </div>
    );
  }

  if (!data || data.total === 0) {
    return (
      <div className="p-6">
        <h1 className="text-xl font-semibold text-[var(--color-text)]">Knowledge Base</h1>
        <p className="text-sm text-[var(--color-text-muted)] mt-2">No documents found.</p>
      </div>
    );
  }

  const filtered = filter
    ? Object.fromEntries(
        Object.entries(data.categories).map(([cat, docs]) => [
          cat,
          docs.filter(
            (d) =>
              d.title.toLowerCase().includes(filter.toLowerCase()) ||
              d.relativePath.toLowerCase().includes(filter.toLowerCase())
          ),
        ]).filter(([, docs]) => (docs as DocEntry[]).length > 0)
      )
    : data.categories;

  return (
    <div className="p-6 space-y-6 max-w-[1200px]">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-[var(--color-text)]">Knowledge Base</h1>
          <p className="text-xs text-[var(--color-text-muted)]">
            {data.total} documents across {Object.keys(data.categories).length} categories
          </p>
        </div>
        <input
          type="text"
          placeholder="Filter..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="text-sm px-3 py-1.5 rounded-[var(--radius)] border border-[var(--color-border)] bg-[var(--color-surface)] text-[var(--color-text)] placeholder:text-[var(--color-text-muted)] focus:outline-none focus:border-[var(--color-accent)] w-48"
        />
      </div>

      {Object.entries(filtered).map(([category, docs]) => (
        <div key={category}>
          <div className="flex items-center gap-2 mb-2">
            <h2 className="text-xs font-semibold tracking-wider uppercase text-[var(--color-accent)]">
              {category}
            </h2>
            <span className="text-[10px] text-[var(--color-text-muted)]">
              {(docs as DocEntry[]).length}
            </span>
          </div>
          <div className="space-y-1">
            {(docs as DocEntry[]).map((doc) => (
              <div
                key={doc.id}
                className="flex items-center gap-3 p-2.5 rounded-[var(--radius)] bg-[var(--color-surface)] border border-[var(--color-border)] hover:bg-[var(--color-surface-hover)] transition-colors group"
              >
                <div
                  className="w-2 h-2 rounded-full shrink-0"
                  style={{ background: TYPE_COLORS[doc.type] || 'var(--color-text-muted)' }}
                />
                <div className="flex-1 min-w-0">
                  <div className="text-sm text-[var(--color-text)] truncate font-medium">
                    {doc.title}
                  </div>
                  <div className="text-[10px] text-[var(--color-text-muted)] font-mono truncate">
                    {doc.relativePath}
                  </div>
                </div>
                <div className="flex items-center gap-3 shrink-0">
                  <span className="text-[10px] text-[var(--color-text-muted)]">
                    {formatSize(doc.size)}
                  </span>
                  <span className="text-[10px] text-[var(--color-text-muted)]">
                    {formatDate(doc.modified)}
                  </span>
                  <span
                    className="text-[9px] px-1.5 py-0.5 rounded-full font-mono"
                    style={{
                      background: `color-mix(in oklch, ${TYPE_COLORS[doc.type] || 'var(--color-text-muted)'} 12%, transparent)`,
                      color: TYPE_COLORS[doc.type] || 'var(--color-text-muted)',
                    }}
                  >
                    {doc.type}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
