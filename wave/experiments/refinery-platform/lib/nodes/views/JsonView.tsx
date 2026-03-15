'use client';

import React from 'react';
import type { NodeDefinition } from '../types';

interface JsonViewProps {
  node: NodeDefinition;
  data: unknown;
}

export function JsonView({ node, data }: JsonViewProps) {
  return (
    <div className="glass-card rounded-lg p-4">
      <div className="text-xs text-text-muted mb-2">{node.title}</div>
      <pre className="text-xs text-text font-mono overflow-x-auto max-h-48 overflow-y-auto">
        {JSON.stringify(data, null, 2) ?? 'null'}
      </pre>
    </div>
  );
}
