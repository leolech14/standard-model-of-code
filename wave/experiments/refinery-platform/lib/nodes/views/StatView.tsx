'use client';

import React from 'react';
import { Badge } from '@/components/shared/Common';
import type { NodeDefinition } from '../types';
import { formatNodeValue, pnlColorClass, resolveBadgeFromMap } from '../helpers';

interface StatViewProps {
  node: NodeDefinition;
  data: unknown;
}

export function StatView({ node, data }: StatViewProps) {
  const formatted = formatNodeValue(data, node.interpret);
  const colorMode = node.interpret?.colorMode;
  const badgeMap = node.interpret?.badgeMap;

  // Resolve value color: pnl mode uses sign-based coloring
  const valueColor =
    colorMode === 'pnl'
      ? pnlColorClass(typeof data === 'number' ? data : null)
      : 'text-text';

  // Resolve badge from map (e.g., day type → success/warning/error)
  const badgeVariant = resolveBadgeFromMap(data, badgeMap);

  return (
    <div className="glass-card rounded-lg p-4">
      <span className="text-xs text-text-muted block">{node.title}</span>
      <div className="flex items-center gap-2 mt-1">
        <span className={`text-lg font-semibold font-mono ${valueColor}`}>
          {formatted}
        </span>
        {badgeVariant && <Badge status={badgeVariant} />}
      </div>
    </div>
  );
}
