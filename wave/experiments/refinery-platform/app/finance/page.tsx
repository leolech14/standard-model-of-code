'use client';

import React, { useState } from 'react';
import {
  DollarSign,
  RefreshCw,
  Wifi,
  WifiOff,
  AlertTriangle,
  CreditCard,
  Building2,
  CheckCircle2,
  XCircle,
  FileText,
  Plug,
} from 'lucide-react';
import { Badge, SectionHeader, EmptyState } from '@/components/shared/Common';
import { Skeleton, Tabs, TabPanel } from '@/components/ui';
import { ActionButton } from '@/components/ui/ActionButton';
import { usePolling } from '@/lib/usePolling';
import { useMutation } from '@/lib/useMutation';
import { useToast } from '@/components/ui/Toast';

/* ─── Types ─── */

interface FinanceStatus {
  bridge_healthy?: boolean;
  pluggy_connected?: boolean;
  binance_connected?: boolean;
  pending_count?: number;
  [key: string]: unknown;
}

interface BalanceInfo {
  source?: string;
  currency?: string;
  amount?: number;
  [key: string]: unknown;
}

interface FinanceSnapshot {
  balances?: BalanceInfo[];
  total_brl?: number;
  total_usd?: number;
  [key: string]: unknown;
}

interface PendingAction {
  confirmation_id?: string;
  type?: string;
  description?: string;
  amount?: number;
  currency?: string;
  created_at?: string;
  [key: string]: unknown;
}

interface PendingActions {
  actions?: PendingAction[];
  [key: string]: unknown;
}

interface InvoiceInfo {
  vendor?: string;
  amount?: number;
  due_date?: string;
  status?: string;
  type?: string;
  [key: string]: unknown;
}

interface InvoicesData {
  invoices?: InvoiceInfo[];
  [key: string]: unknown;
}

interface CategoryBreakdown {
  category?: string;
  amount?: number;
  count?: number;
  [key: string]: unknown;
}

interface InvoiceSummary {
  total?: number;
  count?: number;
  categories?: CategoryBreakdown[];
  month?: string;
  [key: string]: unknown;
}

interface PluggyItem {
  id?: string;
  connector_name?: string;
  status?: string;
  last_updated?: string;
  [key: string]: unknown;
}

interface PluggyItems {
  items?: PluggyItem[];
  [key: string]: unknown;
}

interface PluggyOperation {
  id?: string;
  name?: string;
  tags?: string[];
  [key: string]: unknown;
}

interface PluggyOperations {
  operations?: PluggyOperation[];
  [key: string]: unknown;
}

interface ActionResult {
  success?: boolean;
  message?: string;
  [key: string]: unknown;
}

/* ─── Helpers ─── */

function formatCurrency(v?: number, currency?: string): string {
  if (v == null) return '--';
  const sym = currency === 'USD' ? '$' : 'R$';
  return `${sym} ${v.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

function statusBadge(s?: string): 'success' | 'warning' | 'error' {
  if (!s) return 'warning';
  const good = ['connected', 'active', 'healthy', 'ok', 'updated', 'paid'];
  const bad = ['error', 'failed', 'disconnected', 'expired', 'overdue'];
  if (good.includes(s.toLowerCase())) return 'success';
  if (bad.includes(s.toLowerCase())) return 'error';
  return 'warning';
}

function normalizeArray<T>(data: unknown, key: string): T[] {
  if (!data) return [];
  if (Array.isArray(data)) return data as T[];
  if (typeof data === 'object' && data !== null) {
    const obj = data as Record<string, unknown>;
    if (obj[key] && Array.isArray(obj[key])) return obj[key] as T[];
    for (const v of Object.values(obj)) {
      if (Array.isArray(v)) return v as T[];
    }
  }
  return [];
}

function displayValue(v: unknown): string {
  if (v == null) return '--';
  if (typeof v === 'number') return v.toFixed(2);
  if (typeof v === 'boolean') return v ? 'Yes' : 'No';
  if (typeof v === 'string') return v || '--';
  if (typeof v === 'object') return JSON.stringify(v);
  return String(v);
}

/* ─── Main Page ─── */

export default function FinancePage() {
  const toast = useToast();
  const [activeTab, setActiveTab] = useState(0);

  // ── Sensory: 5 eager polls ──
  const {
    data: finStatus,
    loading: statusLoading,
    error: statusError,
    refresh: refreshStatus,
  } = usePolling<FinanceStatus>('voice/finance/status', { interval: 30_000 });

  const {
    data: snapshot,
    loading: snapshotLoading,
    refresh: refreshSnapshot,
  } = usePolling<FinanceSnapshot>('voice/finance/snapshot', { interval: 30_000 });

  const {
    data: pending,
    loading: pendingLoading,
    refresh: refreshPending,
  } = usePolling<PendingActions>('voice/finance/pending', { interval: 30_000 });

  const {
    data: invoices,
    loading: invoicesLoading,
    refresh: refreshInvoices,
  } = usePolling<InvoicesData>('voice/invoices/check', { interval: 30_000 });

  const {
    data: summary,
    loading: summaryLoading,
    refresh: refreshSummary,
  } = usePolling<InvoiceSummary>('voice/invoices/summary', { interval: 30_000 });

  // ── Sensory: 2 tab-gated polls (Pluggy tab only) ──
  const {
    data: pluggyItems,
    loading: pluggyItemsLoading,
    refresh: refreshPluggyItems,
  } = usePolling<PluggyItems>('voice/finance/pluggy/items/known', {
    interval: 30_000,
    enabled: activeTab === 2,
  });

  const {
    data: pluggyOps,
    loading: pluggyOpsLoading,
    refresh: refreshPluggyOps,
  } = usePolling<PluggyOperations>('voice/finance/pluggy/operations', {
    interval: 30_000,
    enabled: activeTab === 2,
  });

  // ── Motor: 3 mutations ──
  const { mutate: confirmAction, loading: confirming } =
    useMutation<ActionResult>('voice/finance/confirm', {
      onSuccess: (data) => {
        toast.success(data?.message || 'Action confirmed');
        setTimeout(refreshPending, 1500);
      },
      onError: (err) => toast.error(`Confirm failed: ${err}`),
    });

  const { mutate: cancelAction, loading: cancelling } =
    useMutation<ActionResult>('voice/finance/cancel', {
      onSuccess: (data) => {
        toast.success(data?.message || 'Action cancelled');
        setTimeout(refreshPending, 1500);
      },
      onError: (err) => toast.error(`Cancel failed: ${err}`),
    });

  const { mutate: refreshItem, loading: refreshingItem } =
    useMutation<ActionResult>('voice/finance/pluggy/item/refresh', {
      onSuccess: (data) => {
        toast.success(data?.message || 'Item refresh triggered');
        setTimeout(refreshPluggyItems, 2000);
      },
      onError: (err) => toast.error(`Refresh failed: ${err}`),
    });

  // ── Derived state ──
  const allLoading =
    statusLoading && snapshotLoading && pendingLoading && invoicesLoading && summaryLoading;
  const hasError = !!statusError;

  const pendingActions = normalizeArray<PendingAction>(pending, 'actions');
  const balances = normalizeArray<BalanceInfo>(snapshot, 'balances');
  const invoiceList = normalizeArray<InvoiceInfo>(invoices, 'invoices');
  const categories = normalizeArray<CategoryBreakdown>(summary, 'categories');
  const items = normalizeArray<PluggyItem>(pluggyItems, 'items');
  const operations = normalizeArray<PluggyOperation>(pluggyOps, 'operations');

  const handleRefreshAll = () => {
    refreshStatus();
    refreshSnapshot();
    refreshPending();
    refreshInvoices();
    refreshSummary();
    if (activeTab === 2) {
      refreshPluggyItems();
      refreshPluggyOps();
    }
  };

  // ── Loading State ──
  if (allLoading) {
    return (
      <div className="p-6 max-w-6xl space-y-6">
        <div className="flex items-center gap-4">
          <Skeleton className="h-10 w-10 rounded-lg" />
          <div className="space-y-2">
            <Skeleton className="h-6 w-40" />
            <Skeleton className="h-4 w-56" />
          </div>
        </div>
        <Skeleton className="h-10 w-80" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} className="h-24 rounded-lg" />
          ))}
        </div>
        <Skeleton className="h-48 rounded-lg" />
      </div>
    );
  }

  return (
    <div className="p-6 max-w-6xl space-y-6">
      {/* ── Header ── */}
      <div className="flex items-center gap-4">
        <div className="w-10 h-10 rounded-lg bg-surface flex items-center justify-center">
          <DollarSign className="w-5 h-5 text-accent" />
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="text-lg font-semibold">Finance</h1>
            <Badge status={hasError ? 'warning' : 'success'} />
            <span className="text-xs text-text-muted">
              {hasError ? 'partial' : 'connected'}
            </span>
            {(finStatus?.pending_count ?? 0) > 0 && (
              <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-warning/20 text-warning">
                {finStatus?.pending_count} pending
              </span>
            )}
          </div>
          <p className="text-sm text-text-muted">
            Balances, invoices &middot; {balances.length} sources &middot; {invoiceList.length} invoices
          </p>
        </div>
        <div className="flex items-center gap-2">
          {!hasError ? (
            <Wifi className="w-4 h-4 text-accent" />
          ) : (
            <WifiOff className="w-4 h-4 text-danger" />
          )}
          <button
            onClick={handleRefreshAll}
            className="p-2 rounded-md hover:bg-surface text-text-secondary hover:text-text transition-colors"
            title="Refresh all"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* ── Error Banner ── */}
      {hasError && (
        <div className="flex items-center gap-3 p-3 rounded-lg bg-danger/10 border border-danger/20 text-sm">
          <AlertTriangle className="w-4 h-4 text-danger shrink-0" />
          <span className="text-text">{statusError}</span>
        </div>
      )}

      {/* ── Tabs ── */}
      <Tabs
        tabs={['Overview', 'Invoices', 'Pluggy']}
        active={activeTab}
        onChange={setActiveTab}
      />

      {/* ── Overview Tab ── */}
      <TabPanel active={activeTab} index={0}>
        <div className="space-y-6">
          {/* Info Tiles */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <InfoTile
              label="Total BRL"
              value={formatCurrency(snapshot?.total_brl, 'BRL')}
            />
            <InfoTile
              label="Total USD"
              value={formatCurrency(snapshot?.total_usd, 'USD')}
            />
            <InfoTile
              label="Pending Actions"
              value={String(pendingActions.length)}
              badge={pendingActions.length > 0 ? 'warning' : 'success'}
            />
            <InfoTile
              label="Bridge"
              value={finStatus?.bridge_healthy ? 'Healthy' : 'Unknown'}
              badge={finStatus?.bridge_healthy ? 'success' : 'warning'}
            />
          </div>

          {/* Balances Card */}
          <div className="glass-card rounded-lg p-5">
            <SectionHeader title="Balances" />
            {balances.length > 0 ? (
              <div className="mt-3 space-y-1">
                {balances.map((b, i) => (
                  <div
                    key={i}
                    className="flex justify-between items-center py-1.5 border-b border-border-subtle last:border-b-0"
                  >
                    <div className="flex items-center gap-2">
                      <Building2 className="w-3.5 h-3.5 text-text-muted" />
                      <span className="text-sm text-text">
                        {b.source || 'Unknown'}
                      </span>
                      <span className="text-xs text-text-muted">
                        {b.currency || ''}
                      </span>
                    </div>
                    <span className="text-sm font-mono text-text">
                      {formatCurrency(b.amount, b.currency)}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState
                message="No balance data"
                submessage="Balance information will appear when finance sources report."
              />
            )}
          </div>

          {/* Pending Actions Card */}
          <div className="glass-card rounded-lg p-5">
            <SectionHeader title="Pending Confirmations" />
            {pendingActions.length > 0 ? (
              <div className="mt-3 space-y-3">
                {pendingActions.map((action, i) => (
                  <PendingActionRow
                    key={action.confirmation_id || i}
                    action={action}
                    onConfirm={(id) => confirmAction({ confirmation_id: id })}
                    onCancel={(id) => cancelAction({ confirmation_id: id })}
                    confirming={confirming}
                    cancelling={cancelling}
                  />
                ))}
              </div>
            ) : (
              <EmptyState
                message="No pending actions"
                submessage="Staged finance operations requiring confirmation will appear here."
              />
            )}
          </div>

          {/* Discovery Fields from Status */}
          {finStatus && (
            <DiscoveryFields
              data={finStatus}
              exclude={['bridge_healthy', 'pluggy_connected', 'binance_connected', 'pending_count']}
              title="Status Details"
            />
          )}
        </div>
      </TabPanel>

      {/* ── Invoices Tab ── */}
      <TabPanel active={activeTab} index={1}>
        <div className="space-y-6">
          {/* Invoice Summary */}
          <div className="glass-card rounded-lg p-5">
            <SectionHeader title={`Invoice Summary${summary?.month ? ` — ${summary.month}` : ''}`} />
            <div className="mt-3 grid grid-cols-2 gap-4">
              <div>
                <span className="text-xs text-text-muted">Total</span>
                <p className="text-lg font-semibold text-text font-mono">
                  {formatCurrency(summary?.total, 'BRL')}
                </p>
              </div>
              <div>
                <span className="text-xs text-text-muted">Count</span>
                <p className="text-lg font-semibold text-text">
                  {summary?.count ?? '--'}
                </p>
              </div>
            </div>
            {categories.length > 0 && (
              <div className="mt-4 space-y-1">
                <span className="text-xs font-medium text-text-muted">By Category</span>
                {categories.map((cat, i) => (
                  <div
                    key={i}
                    className="flex justify-between items-center py-1.5 border-b border-border-subtle last:border-b-0"
                  >
                    <span className="text-sm text-text">
                      {cat.category || 'Uncategorized'}
                    </span>
                    <div className="flex items-center gap-3">
                      <span className="text-xs text-text-muted">
                        {cat.count ?? 0} items
                      </span>
                      <span className="text-sm font-mono text-text">
                        {formatCurrency(cat.amount, 'BRL')}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Pending Invoices */}
          <div className="glass-card rounded-lg p-5">
            <SectionHeader title="Invoices" />
            {invoiceList.length > 0 ? (
              <div className="mt-3 space-y-2">
                {invoiceList.map((inv, i) => (
                  <InvoiceRow key={i} invoice={inv} />
                ))}
              </div>
            ) : (
              <EmptyState
                message="No invoices found"
                submessage="Invoice and boleto data will appear when the finance engine reports."
              />
            )}
          </div>
        </div>
      </TabPanel>

      {/* ── Pluggy Tab ── */}
      <TabPanel active={activeTab} index={2}>
        <div className="space-y-6">
          {/* Connected Items */}
          <div className="glass-card rounded-lg p-5">
            <SectionHeader title="Connected Items" />
            {pluggyItemsLoading && !pluggyItems ? (
              <div className="mt-3 space-y-3">
                {[...Array(3)].map((_, i) => (
                  <Skeleton key={i} className="h-16 rounded-lg" />
                ))}
              </div>
            ) : items.length > 0 ? (
              <div className="mt-3 space-y-3">
                {items.map((item, i) => (
                  <PluggyItemCard
                    key={item.id || i}
                    item={item}
                    onRefresh={(id) => refreshItem({ item_id: id })}
                    refreshing={refreshingItem}
                  />
                ))}
              </div>
            ) : (
              <EmptyState
                message="No Pluggy items"
                submessage="Connected bank accounts and financial sources will appear here."
              />
            )}
          </div>

          {/* Available Operations */}
          <div className="glass-card rounded-lg p-5">
            <SectionHeader title="Available Operations" />
            {pluggyOpsLoading && !pluggyOps ? (
              <div className="mt-3 space-y-2">
                {[...Array(3)].map((_, i) => (
                  <Skeleton key={i} className="h-8 rounded" />
                ))}
              </div>
            ) : operations.length > 0 ? (
              <div className="mt-3 space-y-1">
                {operations.map((op, i) => (
                  <div
                    key={op.id || i}
                    className="flex justify-between items-center py-1.5 border-b border-border-subtle last:border-b-0"
                  >
                    <span className="text-sm text-text">
                      {op.name || op.id || '--'}
                    </span>
                    {op.tags && op.tags.length > 0 && (
                      <div className="flex gap-1">
                        {op.tags.map((tag) => (
                          <span
                            key={tag}
                            className="px-1.5 py-0.5 rounded text-[10px] bg-surface text-text-muted"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState
                message="No operations available"
                submessage="Pluggy operations will appear when configured."
              />
            )}
          </div>
        </div>
      </TabPanel>

      {/* ── Footer ── */}
      <div className="text-xs text-text-muted text-right">
        Polling: status/snapshot/pending/invoices/summary 30s &times; 5 &middot; pluggy 30s &times; 2 (tab-gated)
      </div>
    </div>
  );
}

/* ─── Sub-Components ─── */

function InfoTile({
  label,
  value,
  badge,
}: {
  label: string;
  value: string;
  badge?: 'success' | 'warning' | 'error';
}) {
  return (
    <div className="glass-card rounded-lg p-4">
      <span className="text-xs text-text-muted">{label}</span>
      <div className="mt-1 flex items-center gap-2">
        <span className="text-lg font-semibold text-text font-mono">{value}</span>
        {badge && <Badge status={badge} />}
      </div>
    </div>
  );
}

function PendingActionRow({
  action,
  onConfirm,
  onCancel,
  confirming,
  cancelling,
}: {
  action: PendingAction;
  onConfirm: (id: string) => void;
  onCancel: (id: string) => void;
  confirming: boolean;
  cancelling: boolean;
}) {
  const id = action.confirmation_id || '';

  return (
    <div className="flex items-center gap-3 p-3 rounded-lg bg-surface border border-border-subtle">
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <Badge status={statusBadge(action.type)} />
          <span className="text-sm font-medium text-text truncate">
            {action.type || 'Action'}
          </span>
          {action.amount != null && (
            <span className="text-sm font-mono text-text-secondary">
              {formatCurrency(action.amount, action.currency)}
            </span>
          )}
        </div>
        <p className="text-xs text-text-muted mt-0.5 truncate">
          {action.description || id || '--'}
        </p>
        {action.created_at && (
          <span className="text-[10px] text-text-muted">{action.created_at}</span>
        )}
      </div>
      <div className="flex items-center gap-2 shrink-0">
        <ActionButton
          onClick={() => onConfirm(id)}
          confirm={`Confirm action: ${action.description || id}?`}
          confirmTitle="Confirm Finance Action"
          variant="primary"
          loading={confirming}
          disabled={!id}
          size="sm"
        >
          <CheckCircle2 className="w-3.5 h-3.5" />
          Confirm
        </ActionButton>
        <ActionButton
          onClick={() => onCancel(id)}
          confirm={`Cancel action: ${action.description || id}? This cannot be undone.`}
          confirmTitle="Cancel Finance Action"
          variant="danger"
          loading={cancelling}
          disabled={!id}
          size="sm"
        >
          <XCircle className="w-3.5 h-3.5" />
          Cancel
        </ActionButton>
      </div>
    </div>
  );
}

function InvoiceRow({ invoice }: { invoice: InvoiceInfo }) {
  return (
    <div className="flex items-center gap-3 py-2 border-b border-border-subtle last:border-b-0">
      <FileText className="w-4 h-4 text-text-muted shrink-0" />
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="text-sm text-text truncate">
            {invoice.vendor || 'Unknown vendor'}
          </span>
          {invoice.type && (
            <span className="px-1.5 py-0.5 rounded text-[10px] bg-surface text-text-muted">
              {invoice.type}
            </span>
          )}
        </div>
        {invoice.due_date && (
          <span className="text-[10px] text-text-muted">Due: {invoice.due_date}</span>
        )}
      </div>
      <div className="flex items-center gap-2 shrink-0">
        <Badge status={statusBadge(invoice.status)} />
        <span className="text-xs text-text-muted">{invoice.status || '--'}</span>
        <span className="text-sm font-mono text-text">
          {formatCurrency(invoice.amount, 'BRL')}
        </span>
      </div>
    </div>
  );
}

function PluggyItemCard({
  item,
  onRefresh,
  refreshing,
}: {
  item: PluggyItem;
  onRefresh: (id: string) => void;
  refreshing: boolean;
}) {
  const id = item.id || '';

  return (
    <div className="flex items-center gap-3 p-3 rounded-lg bg-surface border border-border-subtle">
      <Plug className="w-4 h-4 text-accent shrink-0" />
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-text truncate">
            {item.connector_name || id || 'Unknown'}
          </span>
          <Badge status={statusBadge(item.status)} />
          <span className="text-xs text-text-muted">{item.status || '--'}</span>
        </div>
        {item.last_updated && (
          <span className="text-[10px] text-text-muted">
            Last updated: {item.last_updated}
          </span>
        )}
      </div>
      <ActionButton
        onClick={() => onRefresh(id)}
        confirm={`Refresh Pluggy item: ${item.connector_name || id}?`}
        confirmTitle="Refresh Item"
        variant="secondary"
        loading={refreshing}
        disabled={!id}
        size="sm"
      >
        <RefreshCw className="w-3.5 h-3.5" />
        Refresh
      </ActionButton>
    </div>
  );
}

function DiscoveryFields({
  data,
  exclude,
  title,
}: {
  data: Record<string, unknown>;
  exclude: string[];
  title: string;
}) {
  const extra = Object.entries(data).filter(
    ([k, v]) => !exclude.includes(k) && v != null
  );
  if (extra.length === 0) return null;

  return (
    <div className="glass-card rounded-lg p-5">
      <SectionHeader title={title} />
      <div className="mt-3 space-y-1">
        {extra.map(([key, value]) => (
          <div
            key={key}
            className="flex justify-between items-center py-1.5 border-b border-border-subtle last:border-b-0"
          >
            <span className="text-sm text-text-muted">
              {key.replace(/_/g, ' ')}
            </span>
            <span className="text-sm text-text font-mono truncate max-w-[50%] text-right">
              {displayValue(value)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
