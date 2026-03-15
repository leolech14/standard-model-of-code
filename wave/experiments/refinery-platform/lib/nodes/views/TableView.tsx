'use client';

import React from 'react';
import { RotateCcw } from 'lucide-react';
import { Badge, SectionHeader } from '@/components/shared/Common';
import { ActionButton } from '@/components/ui/ActionButton';
import type { NodeDefinition, MutationDefinition } from '../types';
import { statusToBadgeVariant, interpolateTemplate, pnlColorClass } from '../helpers';

interface TableViewProps {
  node: NodeDefinition;
  data: unknown;
  onMutation?: Record<string, (row: Record<string, unknown>) => void>;
  mutationLoading?: Record<string, boolean>;
}

export function TableView({ node, data, onMutation, mutationLoading }: TableViewProps) {
  const columns = node.representation.columns ?? [];
  const mutations = node.mutations ?? [];
  const rows = Array.isArray(data) ? data as Record<string, unknown>[] : [];

  if (rows.length === 0) return null;

  const hasMutations = mutations.length > 0 && onMutation;

  return (
    <div className="glass-card rounded-lg overflow-hidden">
      <div className="px-5 py-3 border-b border-border">
        <SectionHeader title={`${node.title} (${rows.length})`} />
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-text-muted text-xs uppercase tracking-wider border-b border-border/50">
              {columns.map((col) => (
                <th
                  key={col.key}
                  className={`px-${col.align === 'left' ? '5' : '3'} py-2 font-medium ${
                    col.align === 'right' ? 'text-right'
                    : col.align === 'center' ? 'text-center'
                    : 'text-left'
                  }`}
                >
                  {col.label}
                </th>
              ))}
              {hasMutations && (
                <th className="text-right px-5 py-2 font-medium">Actions</th>
              )}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr
                key={String(row[columns[0]?.key] ?? i)}
                className="border-b border-border/30 hover:bg-surface-hover transition-colors"
              >
                {columns.map((col) => (
                  <td
                    key={col.key}
                    className={`${col.align === 'left' ? 'px-5' : 'px-3'} py-2.5 ${
                      col.align === 'right' ? 'text-right'
                      : col.align === 'center' ? 'text-center'
                      : ''
                    } ${renderCellClass(col.render)}`}
                  >
                    {renderCell(col.render, row[col.key], row)}
                  </td>
                ))}
                {hasMutations && (
                  <td className="px-5 py-2.5 text-right">
                    <MutationActions
                      mutations={mutations}
                      row={row}
                      onMutation={onMutation}
                      mutationLoading={mutationLoading}
                    />
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

/* ─── Cell Rendering ─── */

function renderCellClass(render?: string): string {
  switch (render) {
    case 'mono': return 'font-mono text-xs text-text-muted';
    case 'badge': return '';
    case 'time': return 'text-xs text-text-secondary';
    case 'pnl': return 'font-mono font-medium';
    case 'direction': return '';
    default: return 'font-medium text-text';
  }
}

function renderCell(
  render: string | undefined,
  value: unknown,
  _row: Record<string, unknown>,
): React.ReactNode {
  if (value == null) return <span className="text-text-muted">--</span>;

  switch (render) {
    case 'badge': {
      const statusStr = String(value);
      return (
        <span className="inline-flex items-center gap-1.5">
          <Badge status={statusToBadgeVariant(statusStr)} />
          <span className="text-xs text-text-secondary capitalize">{statusStr}</span>
        </span>
      );
    }
    case 'pnl': {
      const num = Number(value);
      if (isNaN(num)) return <span className="text-text-muted">--</span>;
      const sign = num > 0 ? '+' : '';
      return (
        <span className={pnlColorClass(num)}>
          {sign}${num.toFixed(2)}
        </span>
      );
    }
    case 'direction': {
      const dir = String(value).toUpperCase();
      const variant = dir === 'LONG' ? 'success' : dir === 'SHORT' ? 'error' : 'warning';
      return (
        <span className="inline-flex items-center gap-1.5">
          <Badge status={variant} />
          <span className="text-xs font-medium text-text">{dir}</span>
        </span>
      );
    }
    case 'mono':
      return <span>{String(value)}</span>;
    case 'time':
      return <span>{String(value)}</span>;
    default:
      return <span>{String(value)}</span>;
  }
}

/* ─── Mutation Actions ─── */

function MutationActions({
  mutations,
  row,
  onMutation,
  mutationLoading,
}: {
  mutations: MutationDefinition[];
  row: Record<string, unknown>;
  onMutation: Record<string, (row: Record<string, unknown>) => void>;
  mutationLoading?: Record<string, boolean>;
}) {
  // Check if row supports restart (restartable !== false)
  if (row.restartable === false) return null;

  return (
    <div className="flex items-center gap-1 justify-end">
      {mutations.map((mut) => {
        const handler = onMutation[mut.id];
        if (!handler) return null;

        const confirmText = mut.confirm
          ? interpolateTemplate(mut.confirm, row)
          : undefined;
        const confirmTitle = mut.confirmTitle
          ? interpolateTemplate(mut.confirmTitle, row)
          : undefined;

        return (
          <ActionButton
            key={mut.id}
            onClick={() => handler(row)}
            confirm={confirmText}
            confirmTitle={confirmTitle}
            variant="ghost"
            size="sm"
            loading={mutationLoading?.[mut.id] ?? false}
          >
            <RotateCcw className="w-3 h-3" />
            {mut.label}
          </ActionButton>
        );
      })}
    </div>
  );
}
