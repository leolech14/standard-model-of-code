'use client';

import React from 'react';
import { Skeleton } from '@/components/ui';
import type { NodeDefinition, OwnerRepresentationProfile, ViewKind } from './types';
import { extractField, normalizeNodeData } from './helpers';
import { DEFAULT_PROFILE } from './defaultProfile';
import { GaugeView, StatView, StatusView, TableView, FeedView, ControlView, JsonView, CompositeView } from './views';
import type { SourceMap } from './views/CompositeView';
import { getNodeById } from './registry';

/* ─── Custom View Component Type ─── */

export type CustomViewComponent = React.ComponentType<{
  node: NodeDefinition;
  data: unknown;
}>;

/* ─── Props ─── */

export interface NodeRendererProps {
  node: NodeDefinition;
  /** Raw data from usePolling — NodeRenderer extracts via fieldPath */
  data: unknown;
  loading?: boolean;
  error?: string | null;
  /** Mutation handlers keyed by mutation ID */
  onMutation?: Record<string, (row: Record<string, unknown>) => void>;
  /** Loading states keyed by mutation ID */
  mutationLoading?: Record<string, boolean>;
  /** Domain-specific custom view components keyed by customViewId */
  customViews?: Record<string, CustomViewComponent>;
  /** Full source map for composite nodes to resolve child data */
  sourceMap?: SourceMap;
  /** Nesting depth for composite recursion guard */
  depth?: number;
  /** Owner profile for view resolution overrides */
  profile?: OwnerRepresentationProfile;
}

/* ─── Component ─── */

export function NodeRenderer({
  node,
  data,
  loading = false,
  error,
  onMutation,
  mutationLoading,
  customViews,
  sourceMap,
  depth = 0,
  profile = DEFAULT_PROFILE,
}: NodeRendererProps) {
  // 1. Extract sub-field from raw data
  const raw = extractField(data, node.sense.fieldPath);

  // 2. Apply data normalization hint (e.g., 'find-array' for ranking responses)
  const extracted = normalizeNodeData(raw, node.representation.dataNormalize);

  // 3. Resolve view kind (profile pin > node preference > profile default > json fallback)
  const resolvedView: ViewKind =
    profile.nodePins?.[node.id]?.preferredView ??
    node.representation.preferredView ??
    profile.defaultViews?.[node.kind] ??
    'json';

  // 4. Loading state
  if (loading && extracted == null) {
    return <LoadingSkeleton view={resolvedView} />;
  }

  // 5. Error state
  if (error && extracted == null) {
    return (
      <div className="glass-card rounded-lg p-4 border border-danger/20">
        <div className="text-xs text-text-muted mb-1">{node.title}</div>
        <div className="text-xs text-danger">{error}</div>
      </div>
    );
  }

  // 6. Dispatch to view component
  switch (resolvedView) {
    case 'gauge':
      return <GaugeView node={node} data={extracted} />;
    case 'stat':
      return <StatView node={node} data={extracted} />;
    case 'status-pill':
      return <StatusView node={node} data={extracted} />;
    case 'table':
      return (
        <TableView
          node={node}
          data={extracted}
          onMutation={onMutation}
          mutationLoading={mutationLoading}
        />
      );
    case 'feed':
      return <FeedView node={node} data={extracted} />;
    case 'toggle':
      return (
        <ControlView
          node={node}
          data={extracted}
          onMutation={onMutation}
          mutationLoading={mutationLoading}
        />
      );
    case 'composite':
      return (
        <CompositeView
          node={node}
          data={extracted}
          sourceMap={sourceMap}
          getNode={getNodeById}
          depth={depth}
          renderNode={(childProps) => (
            <NodeRenderer
              node={childProps.node}
              data={childProps.data}
              loading={childProps.loading}
              error={childProps.error ?? undefined}
              sourceMap={childProps.sourceMap}
              depth={childProps.depth}
              onMutation={onMutation}
              mutationLoading={mutationLoading}
              customViews={customViews}
              profile={profile}
            />
          )}
        />
      );
    case 'custom': {
      const viewId = node.representation.customViewId;
      const CustomComponent = viewId ? customViews?.[viewId] : undefined;
      if (CustomComponent) {
        return <CustomComponent node={node} data={extracted} />;
      }
      return <JsonView node={node} data={extracted} />;
    }
    case 'json':
    default:
      return <JsonView node={node} data={extracted} />;
  }
}

/* ─── Loading Skeletons ─── */

function LoadingSkeleton({ view }: { view: ViewKind }) {
  switch (view) {
    case 'gauge':
      return (
        <div className="glass-card rounded-lg p-5 flex items-center gap-5">
          <Skeleton className="h-[88px] w-[88px] rounded-full" />
          <div className="flex-1 space-y-2">
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-3 w-32" />
          </div>
        </div>
      );
    case 'stat':
      return (
        <div className="glass-card rounded-lg p-4 space-y-2">
          <Skeleton className="h-3 w-16" />
          <Skeleton className="h-5 w-24" />
        </div>
      );
    case 'table':
      return <Skeleton className="h-48 rounded-lg" />;
    case 'feed':
      return <Skeleton className="h-40 rounded-lg" />;
    case 'toggle':
      return <Skeleton className="h-32 rounded-lg" />;
    case 'composite':
    case 'custom':
      return <Skeleton className="h-48 rounded-lg" />;
    case 'status-pill':
      return <Skeleton className="h-5 w-20 rounded-full" />;
    default:
      return <Skeleton className="h-24 rounded-lg" />;
  }
}
