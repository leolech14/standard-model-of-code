'use client';

import React, { useState, useMemo } from 'react';
import {
  RefreshCw,
  Wifi,
  WifiOff,
  AlertTriangle,
  CheckCircle2,
} from 'lucide-react';
import { Badge } from '@/components/shared/Common';
import { Skeleton, Tabs, TabPanel, Select } from '@/components/ui';
import { useToast } from '@/components/ui/Toast';
import { useMultiPolling } from '@/lib/useMultiPolling';
import type { EndpointConfig, SourceMap } from '@/lib/useMultiPolling';
import { useNodeMutations } from '@/lib/useNodeMutations';
import { NodeRenderer } from './NodeRenderer';
import type { CustomViewComponent } from './NodeRenderer';
import { getNodesByDomain, getUniqueEndpoints } from './registry';
import { getDomainConfig } from './domainConfig';
import { statusToBadgeVariant, extractField } from './helpers';
import type { NodeDefinition } from './types';

/* ─── Props ─── */

export interface SemanticPageProps {
  domain: string;
  /** Domain-specific custom view components keyed by customViewId */
  customViews?: Record<string, CustomViewComponent>;
  /** External filter state for nodes with filterParams */
  filterState?: Record<string, string>;
  /** Callback when a filter changes */
  onFilterChange?: (key: string, value: string) => void;
}

/* ─── Component ─── */

export function SemanticPage({
  domain,
  customViews,
  filterState,
  onFilterChange,
}: SemanticPageProps) {
  const toast = useToast();
  const [activeTab, setActiveTab] = useState(0);

  // 1. Get domain config + nodes
  const config = getDomainConfig(domain);
  const nodes = useMemo(() => getNodesByDomain(domain), [domain]);

  // 2. Find nodes with filterParams and build adjusted endpoints
  const filterNodes = useMemo(
    () => nodes.filter((n) => n.sense.filterParams && n.sense.filterParams.length > 0),
    [nodes],
  );

  // 3. Compute unique endpoints with filter adjustments
  const endpoints: EndpointConfig[] = useMemo(() => {
    const epMap = getUniqueEndpoints(nodes);
    const configs: EndpointConfig[] = [];

    for (const [path, epInfo] of epMap) {
      const { intervalMs, source } = epInfo;
      // Check if any filter node uses this endpoint
      const filterNode = filterNodes.find((n) => n.sense.endpoint === path);
      if (filterNode && filterState) {
        const params = new URLSearchParams();
        for (const fp of filterNode.sense.filterParams ?? []) {
          const val = filterState[fp.id];
          if (val) params.set(fp.id, val);
        }
        const qs = params.toString();
        configs.push({ path: qs ? `${path}?${qs}` : path, intervalMs, source });
      } else {
        configs.push({ path, intervalMs, source });
      }
    }

    return configs;
  }, [nodes, filterNodes, filterState]);

  // 4. Poll all endpoints
  const { sourceMap, refreshAll } = useMultiPolling(endpoints);

  // 5. Resolve mutations
  const { handlers, loading: mutationLoading } = useNodeMutations(
    nodes,
    toast,
    refreshAll,
  );

  // 6. Build extended sourceMap that maps base paths to polled data
  //    (filter-adjusted paths like "trading/ranking?tf=4h" must resolve
  //     for nodes that declare "trading/ranking" as their endpoint)
  const resolvedSourceMap: SourceMap = useMemo(() => {
    const map: SourceMap = { ...sourceMap };
    // For each filter-adjusted endpoint, also register under the base path
    for (const ep of endpoints) {
      const basePath = ep.path.split('?')[0];
      if (basePath !== ep.path && !map[basePath]) {
        map[basePath] = map[ep.path] ?? { data: null, loading: true, error: null };
      }
    }
    return map;
  }, [sourceMap, endpoints]);

  const sourceFor = (endpoint: string) =>
    resolvedSourceMap[endpoint] ?? { data: null, loading: true, error: null };

  // 7. Derived state for page chrome
  const allLoading = nodes.length > 0 &&
    nodes.every((n) => sourceFor(n.sense.endpoint).loading);

  const firstError = nodes
    .map((n) => sourceFor(n.sense.endpoint).error)
    .find((e) => e != null) ?? null;

  // Header extraction
  const headerStatus = config?.headerExtract?.statusEndpoint
    ? extractField(
        sourceFor(config.headerExtract.statusEndpoint).data,
        config.headerExtract.statusField,
      ) as string | undefined
    : undefined;

  const subtitle = config?.headerExtract?.subtitleFields
    ?.map((sf) => {
      const val = extractField(sourceFor(sf.endpoint).data, sf.field);
      if (val == null) return null;
      // Array → show count
      if (Array.isArray(val)) return `${val.length} position${val.length !== 1 ? 's' : ''}`;
      return String(val);
    })
    .filter(Boolean)
    .join(' · ') ?? '';

  const Icon = config?.icon;

  // 8. Group + sort nodes for rendering
  //    Compass→Cartographer: purpose.relevance drives sort when available,
  //    falls back to representation.order for nodes without purpose.
  const nodesByGroup = useMemo(() => {
    const groups = new Map<string, NodeDefinition[]>();
    for (const node of nodes) {
      const g = node.purpose?.narrativeRole ?? node.representation.group ?? 'default';
      const arr = groups.get(g) ?? [];
      arr.push(node);
      groups.set(g, arr);
    }
    for (const [, arr] of groups) {
      arr.sort((a, b) => {
        const relA = a.purpose?.relevance;
        const relB = b.purpose?.relevance;
        // If both have relevance, sort descending (higher = first)
        if (relA != null && relB != null) return relB - relA;
        // If only one has relevance, it wins
        if (relA != null) return -1;
        if (relB != null) return 1;
        // Fallback to manual order
        return (a.representation.order ?? 0) - (b.representation.order ?? 0);
      });
    }
    return groups;
  }, [nodes]);

  // ── Loading ──
  if (allLoading && nodes.length > 0) {
    return (
      <div className="p-6 max-w-6xl space-y-6">
        <div className="flex items-center gap-4">
          <Skeleton className="h-10 w-10 rounded-lg" />
          <div className="space-y-2">
            <Skeleton className="h-6 w-40" />
            <Skeleton className="h-4 w-56" />
          </div>
        </div>
        <div className="grid grid-cols-3 gap-6">
          {[...Array(3)].map((_, i) => (
            <Skeleton key={i} className="h-28 rounded-lg" />
          ))}
        </div>
        <Skeleton className="h-48 rounded-lg" />
      </div>
    );
  }

  // ── Render nodes for a set of groups ──
  const renderGroups = (groups: string[]) => {
    const rendered: React.ReactNode[] = [];

    for (const groupName of groups) {
      const groupNodes = nodesByGroup.get(groupName);
      if (!groupNodes || groupNodes.length === 0) continue;

      // Separate by salience for layout
      const highNodes = groupNodes.filter((n) => n.representation.salience === 'high');
      const normalNodes = groupNodes.filter((n) => n.representation.salience === 'normal');
      const lowNodes = groupNodes.filter((n) => n.representation.salience === 'low');

      // High salience: metric nodes go in a responsive grid, others full-width
      const highMetrics = highNodes.filter((n) => n.kind === 'metric');
      const highOther = highNodes.filter((n) => n.kind !== 'metric');

      if (highMetrics.length > 0) {
        const cols = highMetrics.length <= 3 ? `grid-cols-${highMetrics.length}` : 'grid-cols-2 md:grid-cols-4';
        rendered.push(
          <div key={`${groupName}-high-metrics`} className={`grid ${cols} gap-4`}>
            {highMetrics.map((node) => renderNode(node))}
          </div>,
        );
      }

      for (const node of highOther) {
        rendered.push(renderNode(node));
      }

      // Normal salience: full-width
      for (const node of normalNodes) {
        rendered.push(renderNode(node));
      }

      // Low salience: compact grid
      if (lowNodes.length > 0) {
        rendered.push(
          <div key={`${groupName}-low`} className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {lowNodes.map((node) => renderNode(node))}
          </div>,
        );
      }
    }

    return rendered;
  };

  const renderNode = (node: NodeDefinition) => {
    const src = sourceFor(node.sense.endpoint);
    return (
      <NodeRenderer
        key={node.id}
        node={node}
        data={src.data}
        loading={src.loading}
        error={src.error ?? undefined}
        sourceMap={resolvedSourceMap}
        onMutation={handlers}
        mutationLoading={mutationLoading}
        customViews={customViews}
      />
    );
  };

  // ── Determine which groups exist (for tabs or flat rendering) ──
  const allGroupNames = [...nodesByGroup.keys()];
  const tabs = config?.tabs;

  // Filter controls for nodes with filterParams
  const filterControls = filterNodes.length > 0 && onFilterChange ? (
    <div className="flex items-end gap-3">
      {filterNodes.flatMap((node) =>
        (node.sense.filterParams ?? []).map((fp) => (
          <Select
            key={fp.id}
            value={filterState?.[fp.id] ?? ''}
            onChange={(v: string) => onFilterChange(fp.id, v)}
            options={fp.options}
            label={fp.label}
          />
        )),
      )}
    </div>
  ) : null;

  return (
    <div className="p-6 max-w-6xl space-y-6">
      {/* ── Header ── */}
      <div className="flex items-center gap-4">
        <div className="w-10 h-10 rounded-lg bg-surface flex items-center justify-center">
          {Icon && <Icon className="w-5 h-5 text-accent" />}
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="text-lg font-semibold">{config?.title ?? domain}</h1>
            {headerStatus != null && (
              <>
                <Badge
                  status={
                    headerStatus === 'ok'
                      ? 'success'
                      : statusToBadgeVariant(headerStatus)
                  }
                />
                <span className="text-xs text-text-muted capitalize">
                  {headerStatus}
                </span>
              </>
            )}
          </div>
          {subtitle && (
            <p className="text-sm text-text-muted">{subtitle}</p>
          )}
        </div>
        <div className="flex items-center gap-2">
          {!firstError ? (
            <Wifi className="w-4 h-4 text-accent" />
          ) : (
            <WifiOff className="w-4 h-4 text-danger" />
          )}
          <button
            onClick={refreshAll}
            className="p-2 rounded-md hover:bg-surface text-text-secondary hover:text-text transition-colors"
            title="Refresh all"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* ── Error Banner ── */}
      {firstError && (
        <div className="flex items-center gap-3 p-3 rounded-lg bg-danger/10 border border-danger/20 text-sm">
          <AlertTriangle className="w-4 h-4 text-danger shrink-0" />
          <span className="text-text">{firstError}</span>
        </div>
      )}

      {/* ── Content: Tabs or Flat ── */}
      {tabs && tabs.length > 1 ? (
        <>
          <Tabs
            tabs={tabs.map((t) => t.label)}
            active={activeTab}
            onChange={setActiveTab}
          />
          {tabs.map((tab, idx) => (
            <TabPanel key={tab.id} active={activeTab} index={idx}>
              <div className="space-y-6">
                {/* Show filter controls in the tab that has filtered nodes */}
                {filterNodes.some((n) =>
                  tab.groups.includes(n.representation.group ?? ''),
                ) && filterControls}
                {renderGroups(tab.groups)}
              </div>
            </TabPanel>
          ))}
        </>
      ) : (
        <div className="space-y-6">
          {filterControls}
          {renderGroups(allGroupNames)}
        </div>
      )}

      {/* ── Empty State ── */}
      {nodes.length > 0 && !firstError && allGroupNames.every(
        (g) => {
          const gNodes = nodesByGroup.get(g) ?? [];
          return gNodes.every((n) => {
            const src = sourceFor(n.sense.endpoint);
            return src.data == null && !src.loading;
          });
        },
      ) && (
        <div className="glass-card rounded-lg p-6 text-center">
          <CheckCircle2 className="w-8 h-8 text-accent mx-auto mb-3" />
          <p className="text-sm text-text">{config?.title ?? domain} operational</p>
          <p className="text-xs text-text-muted mt-1">
            Details will appear when available from the API.
          </p>
        </div>
      )}

      {/* ── Footer ── */}
      {config?.pollingFooter && (
        <div className="text-xs text-text-muted text-right">
          Polling: {config.pollingFooter}
        </div>
      )}
    </div>
  );
}
