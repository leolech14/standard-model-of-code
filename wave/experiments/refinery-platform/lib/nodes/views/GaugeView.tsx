'use client';

import React from 'react';
import {
  Cpu, Activity, HardDrive, Server,
  AlertTriangle, Database, Wifi, Clock,
} from 'lucide-react';
import { Gauge } from '@/components/ui/Gauge';
import type { NodeDefinition } from '../types';
import { extractField, interpolateTemplate } from '../helpers';

/** Map lucide icon names to components */
const ICON_MAP: Record<string, React.ComponentType<{ className?: string }>> = {
  Cpu, Activity, HardDrive, Server,
  AlertTriangle, Database, Wifi, Clock,
};

interface GaugeViewProps {
  node: NodeDefinition;
  data: unknown;
}

export function GaugeView({ node, data }: GaugeViewProps) {
  const rep = node.representation;
  const interpret = node.interpret;

  // Extract primary value (e.g., data.percent for gauge)
  const valueField = rep.valueField ?? 'percent';
  const rawValue = extractField(data, valueField);
  const pct = typeof rawValue === 'number' ? rawValue : 0;

  // Build detail text from template
  const dataObj = (typeof data === 'object' && data !== null)
    ? data as Record<string, unknown>
    : {};

  // Format load array if present
  const formattedData = { ...dataObj };
  if (Array.isArray(formattedData.load)) {
    formattedData.load = formattedData.load.map((l: number) => l.toFixed(1)).join(', ') as unknown;
  }

  const detail = rep.detailTemplate
    ? interpolateTemplate(rep.detailTemplate, formattedData as Record<string, unknown>)
    : undefined;

  const subDetail = rep.subDetailTemplate
    ? interpolateTemplate(rep.subDetailTemplate, formattedData as Record<string, unknown>)
    : undefined;

  // Resolve icon
  const IconComponent = rep.icon ? ICON_MAP[rep.icon] : null;

  // Map thresholds from interpret → Gauge props
  const thresholds = interpret?.thresholds
    ? {
        warn: interpret.thresholds.warningAbove ?? 70,
        danger: interpret.thresholds.dangerAbove ?? 90,
      }
    : undefined;

  return (
    <div className="glass-card rounded-lg p-5 flex items-center gap-5">
      <div className="relative">
        <Gauge
          value={pct}
          label=""
          size={88}
          thresholds={thresholds}
        />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          {IconComponent && (
            <span className="text-text-muted">
              <IconComponent className="w-4 h-4" />
            </span>
          )}
          <span className="text-sm font-semibold text-text">{node.title}</span>
        </div>
        {detail && <div className="text-xs text-text-secondary">{detail}</div>}
        {subDetail && <div className="text-xs text-text-muted mt-0.5">{subDetail}</div>}
        {rawValue == null && <div className="text-xs text-text-muted">No data</div>}
      </div>
    </div>
  );
}
