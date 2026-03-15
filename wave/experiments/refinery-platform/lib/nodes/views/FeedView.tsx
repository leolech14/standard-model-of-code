'use client';

import React from 'react';
import { AlertTriangle } from 'lucide-react';
import { Badge, SectionHeader } from '@/components/shared/Common';
import type { NodeDefinition } from '../types';
import { severityColorClass } from '../helpers';

interface FeedViewProps {
  node: NodeDefinition;
  data: unknown;
}

export function FeedView({ node, data }: FeedViewProps) {
  // Normalize: accept string[] (trading alerts) or Record<string, unknown>[]
  const rawItems = Array.isArray(data) ? data : [];
  const items = rawItems.map((item) =>
    typeof item === 'string' ? { message: item } : item,
  ) as Record<string, unknown>[];
  const maxItems = node.representation.maxItems ?? 50;
  const sliced = items.slice(0, maxItems);

  if (sliced.length === 0) return null;

  // Determine if this is an anomaly/alert feed
  const isAlert = node.kind === 'list' && node.representation.icon === 'AlertTriangle';

  return (
    <div className="glass-card rounded-lg overflow-hidden">
      <div className="px-5 py-3 border-b border-border">
        <div className="flex items-center gap-2">
          {isAlert && <AlertTriangle className="w-4 h-4 text-warning" />}
          <SectionHeader title={node.title} />
        </div>
      </div>
      <div className={`divide-y divide-border/30 ${!isAlert ? 'max-h-64 overflow-y-auto' : ''}`}>
        {sliced.map((item, i) => (
          isAlert
            ? <AnomalyRow key={i} item={item} />
            : <EventRow key={i} item={item} />
        ))}
      </div>
    </div>
  );
}

/* ─── Event Row (system.events pattern) ─── */

function EventRow({ item }: { item: Record<string, unknown> }) {
  const timestamp = item.timestamp ? new Date(String(item.timestamp)).toLocaleTimeString() : '';
  const type = String(item.type ?? '');
  const message = String(item.message ?? '');
  const severity = item.severity as string | undefined;

  return (
    <div className="px-5 py-2.5 flex items-start gap-3 text-xs hover:bg-surface-hover transition-colors">
      <span className="text-text-muted whitespace-nowrap font-mono w-20 shrink-0">
        {timestamp}
      </span>
      <span className={`shrink-0 uppercase font-medium tracking-wider w-16 ${severityColorClass(severity)}`}>
        {type}
      </span>
      <span className="text-text flex-1">{message}</span>
    </div>
  );
}

/* ─── Anomaly Row (system.anomalies pattern) ─── */

function AnomalyRow({ item }: { item: Record<string, unknown> }) {
  const metric = String(item.metric ?? '');
  const value = item.value;
  const threshold = item.threshold;
  const message = item.message as string | undefined;
  const timestamp = item.timestamp
    ? new Date(String(item.timestamp)).toLocaleTimeString()
    : '';

  return (
    <div className="px-5 py-3 flex items-center gap-4 text-sm">
      <Badge status="warning" />
      <div className="flex-1">
        <span className="font-medium text-text">{metric}</span>
        <span className="text-text-muted ml-2">
          {value != null ? String(value) : '--'} / {threshold != null ? String(threshold) : '--'} threshold
        </span>
        {message && (
          <p className="text-xs text-text-secondary mt-0.5">{message}</p>
        )}
      </div>
      <span className="text-xs text-text-muted font-mono">{timestamp}</span>
    </div>
  );
}
