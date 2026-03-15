'use client';

import React, { useState } from 'react';
import { Badge, SectionHeader } from '@/components/shared/Common';
import { Select } from '@/components/ui';
import { ActionButton } from '@/components/ui/ActionButton';
import type { NodeDefinition, MutationDefinition } from '../types';
import { interpolateTemplate } from '../helpers';

interface ControlViewProps {
  node: NodeDefinition;
  data: unknown;
  onMutation?: Record<string, (payload: Record<string, unknown>) => void>;
  mutationLoading?: Record<string, boolean>;
}

export function ControlView({ node, data, onMutation, mutationLoading }: ControlViewProps) {
  const mutations = node.mutations ?? [];
  const dataObj = (typeof data === 'object' && data !== null ? data : {}) as Record<string, unknown>;

  return (
    <div className="glass-card rounded-lg p-5">
      <SectionHeader title={node.title} />

      {/* Auto-discover data fields */}
      <div className="mt-3 flex items-center gap-3 flex-wrap">
        {Object.entries(dataObj).map(([key, value]) => {
          if (value == null) return null;

          // Booleans → Badge + label
          if (typeof value === 'boolean') {
            return (
              <React.Fragment key={key}>
                <Badge status={value ? 'success' : 'warning'} />
                <span className="text-xs font-medium text-text">
                  {value ? 'Enabled' : 'Disabled'}
                </span>
              </React.Fragment>
            );
          }

          // Strings → labeled pill
          if (typeof value === 'string' && value) {
            // Special: mode field gets its own badge
            if (key === 'mode') {
              return (
                <React.Fragment key={key}>
                  <Badge status={value === 'live' ? 'error' : 'success'} />
                  <span className="text-xs text-text-muted">{value}</span>
                </React.Fragment>
              );
            }
            return (
              <span key={key} className="text-xs text-text-muted">
                {key.replace(/_/g, ' ')}: <span className="text-text">{value}</span>
              </span>
            );
          }

          // Numbers → labeled value
          if (typeof value === 'number') {
            return (
              <span key={key} className="text-xs text-text-muted">
                {key.replace(/_/g, ' ')}: <span className="text-text">{value}</span>
                {key.endsWith('_pct') ? '%' : ''}
              </span>
            );
          }

          return null;
        })}
      </div>

      {/* Mutation actions with parameter selects */}
      {mutations.map((mut) => {
        const handler = onMutation?.[mut.id];
        if (!handler) return null;

        return (
          <MutationControl
            key={mut.id}
            mutation={mut}
            data={dataObj}
            handler={handler}
            loading={mutationLoading?.[mut.id] ?? false}
          />
        );
      })}
    </div>
  );
}

/* ─── Mutation Control (with parameter selects) ─── */

function MutationControl({
  mutation,
  data,
  handler,
  loading,
}: {
  mutation: MutationDefinition;
  data: Record<string, unknown>;
  handler: (payload: Record<string, unknown>) => void;
  loading: boolean;
}) {
  const params = mutation.parameters ?? [];
  const [paramValues, setParamValues] = useState<Record<string, string>>(() => {
    const init: Record<string, string> = {};
    for (const p of params) {
      init[p.id] = p.options[0]?.value ?? '';
    }
    return init;
  });

  const confirmText = mutation.confirm
    ? interpolateTemplate(mutation.confirm, { ...data, ...paramValues })
    : undefined;
  const confirmTitle = mutation.confirmTitle
    ? interpolateTemplate(mutation.confirmTitle, { ...data, ...paramValues })
    : undefined;

  return (
    <div className="mt-4 flex items-end gap-3">
      {params.map((p) => (
        <Select
          key={p.id}
          value={paramValues[p.id] ?? ''}
          onChange={(v: string) => setParamValues((prev) => ({ ...prev, [p.id]: v }))}
          options={p.options}
          label={p.label}
        />
      ))}
      <ActionButton
        onClick={() => handler(paramValues)}
        confirm={confirmText}
        confirmTitle={confirmTitle}
        variant="primary"
        loading={loading}
      >
        {mutation.label}
      </ActionButton>
    </div>
  );
}
