'use client';

import React from 'react';
import { Badge, EmptyState } from '@/components/shared/Common';
import type { CustomViewComponent } from '@/lib/nodes/NodeRenderer';

/**
 * OpportunityList — custom view for trading.ranking node.
 * Renders ranked trade cards with confidence bars + discovery fields.
 *
 * Justified custom escape hatch: confidence progress bar with inline
 * style widths, rank numbers, dynamic extra-field discovery (iterating
 * unknown object keys) — cannot decompose into child nodes.
 */
export const OpportunityList: CustomViewComponent = ({ node, data }) => {
  const trades = Array.isArray(data) ? data as Record<string, unknown>[] : [];

  if (trades.length === 0) {
    return (
      <EmptyState
        message="No trade opportunities"
        submessage="Adjust filters or wait for the next scan cycle."
      />
    );
  }

  return (
    <div className="space-y-3">
      {trades.map((trade, i) => (
        <OpportunityCard key={(trade.symbol as string) || i} trade={trade} rank={i + 1} />
      ))}
    </div>
  );
};

function OpportunityCard({ trade, rank }: { trade: Record<string, unknown>; rank: number }) {
  const symbol = trade.symbol as string | undefined;
  const dir = trade.direction as string | undefined;
  const confidence = trade.confidence as number | undefined;
  const timeframe = trade.timeframe as string | undefined;
  const entry = trade.entry as number | undefined;
  const target = trade.target as number | undefined;
  const stop = trade.stop as number | undefined;
  const rr = trade.rr as number | undefined;

  const knownKeys = new Set([
    'symbol', 'direction', 'confidence', 'timeframe', 'entry', 'target', 'stop', 'rr',
  ]);
  const extraFields: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(trade)) {
    if (!knownKeys.has(k) && v != null && v !== '') {
      extraFields[k] = v;
    }
  }

  return (
    <div className="glass-card rounded-lg p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-xs text-text-muted w-6">#{rank}</span>
          <span className="text-sm font-medium text-text">{symbol || '--'}</span>
          <Badge
            status={dir === 'LONG' || dir === 'long' ? 'success' : 'error'}
          />
          <span className="text-xs font-medium text-text">
            {dir || '?'}
          </span>
          {timeframe && (
            <span className="text-xs text-text-muted">{timeframe}</span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {confidence != null && (
            <div className="flex items-center gap-2">
              <div className="w-16 h-1.5 bg-surface rounded-full overflow-hidden">
                <div
                  className="h-full bg-accent rounded-full transition-all"
                  style={{ width: `${Math.min(100, Math.max(0, confidence))}%` }}
                />
              </div>
              <span className="text-xs font-mono text-accent">
                {confidence.toFixed(0)}%
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Price levels */}
      <div className="mt-2 flex gap-4 text-xs text-text-muted">
        {entry != null && (
          <span>Entry: <span className="text-text font-mono">{entry.toFixed(2)}</span></span>
        )}
        {target != null && (
          <span>Target: <span className="text-emerald font-mono">{target.toFixed(2)}</span></span>
        )}
        {stop != null && (
          <span>Stop: <span className="text-danger font-mono">{stop.toFixed(2)}</span></span>
        )}
        {rr != null && (
          <span>R:R <span className="text-text font-mono">{rr.toFixed(1)}</span></span>
        )}
      </div>

      {/* Discovery: extra fields */}
      {Object.keys(extraFields).length > 0 && (
        <div className="mt-2 flex flex-wrap gap-x-3 gap-y-1 text-xs">
          {Object.entries(extraFields).map(([k, v]) => (
            <span key={k} className="text-text-muted">
              {k.replace(/_/g, ' ')}: <span className="text-text font-mono">{displayValue(v)}</span>
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

function displayValue(v: unknown): string {
  if (v == null) return '--';
  if (typeof v === 'number') return v.toFixed(2);
  if (typeof v === 'boolean') return v ? 'Yes' : 'No';
  if (typeof v === 'string') return v || '--';
  if (typeof v === 'object') return JSON.stringify(v);
  return String(v);
}
