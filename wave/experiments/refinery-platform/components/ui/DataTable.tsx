'use client';

import React, { useState, useMemo, useCallback } from 'react';

/**
 * Sortable data table with glass-card style, row click, empty state.
 *
 * Usage:
 *   <DataTable
 *     columns={[
 *       { key: 'name', label: 'Name' },
 *       { key: 'status', label: 'Status', render: (v) => <Badge status={v} /> },
 *     ]}
 *     data={services}
 *     onRowClick={(row) => setSelected(row)}
 *     emptyMessage="No services found"
 *   />
 */

export interface Column<T> {
  key: keyof T & string;
  label: string;
  /** Custom cell renderer. Falls back to String(value). */
  render?: (value: T[keyof T], row: T) => React.ReactNode;
  /** Enable sorting for this column. Default true. */
  sortable?: boolean;
  /** Column width class, e.g. 'w-32' */
  width?: string;
  /** Text alignment */
  align?: 'left' | 'center' | 'right';
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  /** Callback when a row is clicked */
  onRowClick?: (row: T) => void;
  /** Message shown when data is empty */
  emptyMessage?: string;
  /** Optional className for the container */
  className?: string;
}

type SortDir = 'asc' | 'desc';

export function DataTable<T extends Record<string, unknown>>({
  columns,
  data,
  onRowClick,
  emptyMessage = 'No data',
  className = '',
}: DataTableProps<T>) {
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortDir, setSortDir] = useState<SortDir>('asc');

  const handleSort = useCallback(
    (key: string) => {
      if (sortKey === key) {
        setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
      } else {
        setSortKey(key);
        setSortDir('asc');
      }
    },
    [sortKey]
  );

  const sorted = useMemo(() => {
    if (!sortKey) return data;
    return [...data].sort((a, b) => {
      const av = a[sortKey];
      const bv = b[sortKey];
      if (av == null && bv == null) return 0;
      if (av == null) return 1;
      if (bv == null) return -1;

      let cmp: number;
      if (typeof av === 'number' && typeof bv === 'number') {
        cmp = av - bv;
      } else {
        cmp = String(av).localeCompare(String(bv));
      }
      return sortDir === 'desc' ? -cmp : cmp;
    });
  }, [data, sortKey, sortDir]);

  if (data.length === 0) {
    return (
      <div className={`glass-card rounded-lg p-8 text-center text-[var(--color-text-muted)] text-sm ${className}`}>
        {emptyMessage}
      </div>
    );
  }

  return (
    <div className={`glass-card rounded-lg overflow-hidden ${className}`}>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-[var(--color-border)]">
              {columns.map((col) => {
                const canSort = col.sortable !== false;
                const isSorted = sortKey === col.key;
                const alignClass =
                  col.align === 'right'
                    ? 'text-right'
                    : col.align === 'center'
                    ? 'text-center'
                    : 'text-left';

                return (
                  <th
                    key={col.key}
                    className={`
                      px-4 py-3 font-medium text-[var(--color-text-muted)]
                      ${alignClass} ${col.width || ''}
                      ${canSort ? 'cursor-pointer select-none hover:text-[var(--color-text-secondary)]' : ''}
                    `}
                    onClick={canSort ? () => handleSort(col.key) : undefined}
                  >
                    <span className="inline-flex items-center gap-1">
                      {col.label}
                      {isSorted && (
                        <span className="text-[var(--color-accent)] text-xs">
                          {sortDir === 'asc' ? '\u2191' : '\u2193'}
                        </span>
                      )}
                    </span>
                  </th>
                );
              })}
            </tr>
          </thead>
          <tbody>
            {sorted.map((row, i) => (
              <tr
                key={i}
                onClick={onRowClick ? () => onRowClick(row) : undefined}
                className={`
                  border-b border-[var(--color-border-subtle)] last:border-b-0
                  transition-colors
                  ${onRowClick ? 'cursor-pointer hover:bg-[var(--color-surface-hover)]' : ''}
                `}
              >
                {columns.map((col) => {
                  const val = row[col.key];
                  const alignClass =
                    col.align === 'right'
                      ? 'text-right'
                      : col.align === 'center'
                      ? 'text-center'
                      : 'text-left';

                  return (
                    <td
                      key={col.key}
                      className={`px-4 py-3 text-[var(--color-text)] ${alignClass}`}
                    >
                      {col.render ? col.render(val, row) : String(val ?? '--')}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
