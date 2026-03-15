'use client';

import React from 'react';
import { Badge } from '@/components/shared/Common';
import type { NodeDefinition } from '../types';
import { statusToBadgeVariant } from '../helpers';

interface StatusViewProps {
  node: NodeDefinition;
  data: unknown;
}

export function StatusView({ node, data }: StatusViewProps) {
  const statusText = typeof data === 'string' ? data
    : (typeof data === 'object' && data !== null && 'status' in data)
      ? String((data as Record<string, unknown>).status)
      : undefined;

  const variant = statusToBadgeVariant(statusText);

  return (
    <span className="inline-flex items-center gap-1.5">
      <Badge status={variant} />
      <span className="text-xs text-text-secondary capitalize">
        {statusText || node.interpret?.emptyMeans || 'unknown'}
      </span>
    </span>
  );
}
