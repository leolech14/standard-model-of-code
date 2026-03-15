'use client';

import React from 'react';
import type { NodeDefinition } from '../types';

/* ─── Source Map Type ─── */

export type SourceMap = Record<
  string,
  { data: unknown; loading: boolean; error: string | null }
>;

/* ─── Props ─── */

export interface CompositeViewProps {
  node: NodeDefinition;
  data: unknown;
  sourceMap?: SourceMap;
  /** Node lookup function — avoids circular import with registry */
  getNode?: (id: string) => NodeDefinition | undefined;
  /** Render function for child nodes — avoids circular import with NodeRenderer */
  renderNode?: (props: {
    node: NodeDefinition;
    data: unknown;
    loading: boolean;
    error: string | null;
    sourceMap?: SourceMap;
    depth: number;
  }) => React.ReactNode;
  depth?: number;
}

/* ─── Layout CSS Classes ─── */

const LAYOUT_CLASSES: Record<string, string> = {
  row: 'flex gap-3',
  grid: 'grid grid-cols-3 gap-4',
  stack: 'space-y-3',
  inline: 'inline-flex gap-2',
};

/* ─── Component ─── */

export function CompositeView({
  node,
  sourceMap,
  getNode,
  renderNode,
  depth = 0,
}: CompositeViewProps) {
  const children = node.representation.children;
  const layout = node.representation.layout ?? 'stack';

  // Depth guard: prevent infinite recursion
  if (depth >= 3 || !children?.length || !getNode || !renderNode) {
    return null;
  }

  // Resolve child nodes
  const childNodes = children
    .map((id) => getNode(id))
    .filter((n): n is NodeDefinition => n != null);

  if (childNodes.length === 0) return null;

  // mini-grid: metrics in grid row, everything else stacked below
  if (layout === 'mini-grid') {
    const metrics = childNodes.filter(
      (n) => n.kind === 'metric' || n.kind === 'status',
    );
    const rest = childNodes.filter(
      (n) => n.kind !== 'metric' && n.kind !== 'status',
    );

    return (
      <div className="glass-card rounded-lg p-5 space-y-4">
        <h3 className="text-sm font-medium text-text">{node.title}</h3>
        {metrics.length > 0 && (
          <div
            className="grid gap-4"
            style={{
              gridTemplateColumns: `repeat(${Math.min(metrics.length, 4)}, 1fr)`,
            }}
          >
            {metrics.map((child) => {
              const src = sourceMap?.[child.sense.endpoint];
              return (
                <React.Fragment key={child.id}>
                  {renderNode({
                    node: child,
                    data: src?.data ?? null,
                    loading: src?.loading ?? true,
                    error: src?.error ?? null,
                    sourceMap,
                    depth: depth + 1,
                  })}
                </React.Fragment>
              );
            })}
          </div>
        )}
        {rest.map((child) => {
          const src = sourceMap?.[child.sense.endpoint];
          return (
            <React.Fragment key={child.id}>
              {renderNode({
                node: child,
                data: src?.data ?? null,
                loading: src?.loading ?? true,
                error: src?.error ?? null,
                sourceMap,
                depth: depth + 1,
              })}
            </React.Fragment>
          );
        })}
      </div>
    );
  }

  // Standard layouts: row, grid, stack, inline
  const className = LAYOUT_CLASSES[layout] ?? LAYOUT_CLASSES.stack;

  return (
    <div className={`glass-card rounded-lg p-5 space-y-3`}>
      <h3 className="text-sm font-medium text-text">{node.title}</h3>
      <div className={className}>
        {childNodes.map((child) => {
          const src = sourceMap?.[child.sense.endpoint];
          return (
            <React.Fragment key={child.id}>
              {renderNode({
                node: child,
                data: src?.data ?? null,
                loading: src?.loading ?? true,
                error: src?.error ?? null,
                sourceMap,
                depth: depth + 1,
              })}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}
