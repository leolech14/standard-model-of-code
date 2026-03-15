'use client';

import React, { useState } from 'react';
import {
  Settings,
  RefreshCw,
  Wifi,
  WifiOff,
  AlertTriangle,
  Save,
  TrendingUp,
  Brain,
  Mic,
  Server,
} from 'lucide-react';
import { Badge, SectionHeader, EmptyState } from '@/components/shared/Common';
import { Skeleton, Tabs, TabPanel, Select } from '@/components/ui';
import { ActionButton } from '@/components/ui/ActionButton';
import { usePolling } from '@/lib/usePolling';
import { useMutation } from '@/lib/useMutation';
import { useToast } from '@/components/ui/Toast';

/* ─── Types ─── */

/** Config responses are dynamic key-value maps. We don't know the exact shape
 *  per domain, so we type loosely and render whatever comes back. */
interface ConfigData {
  [key: string]: unknown;
}

/** GET /api/openclaw/thresholds */
interface ThresholdsData {
  [key: string]: unknown;
}

/** POST /api/openclaw/voice/config/set */
interface ConfigResult {
  success: boolean;
  message?: string;
}

/* ─── Constants ─── */

const CONFIG_DOMAINS = [
  { value: 'trading', label: 'Trading', icon: TrendingUp },
  { value: 'llm', label: 'LLM', icon: Brain },
  { value: 'voice', label: 'Voice', icon: Mic },
  { value: 'system', label: 'System', icon: Server },
] as const;

const DOMAIN_OPTIONS = CONFIG_DOMAINS.map((d) => ({
  value: d.value,
  label: d.label,
}));

/* ─── Helpers ─── */

/** Flatten a value for display */
function displayValue(v: unknown): string {
  if (v == null) return '--';
  if (typeof v === 'boolean') return v ? 'true' : 'false';
  if (typeof v === 'number') return String(v);
  if (typeof v === 'string') return v || '--';
  if (typeof v === 'object') return JSON.stringify(v);
  return String(v);
}

/** Count non-null entries in a config object */
function countKeys(data: ConfigData | null): number {
  if (!data) return 0;
  return Object.keys(data).filter((k) => data[k] != null).length;
}

/* ─── Main Page ─── */

export default function SettingsPage() {
  const toast = useToast();
  const [activeTab, setActiveTab] = useState(0);

  // Config editor form state
  const [editDomain, setEditDomain] = useState('trading');
  const [editKey, setEditKey] = useState('');
  const [editValue, setEditValue] = useState('');

  // ── Sensory: 4 config domain polls + 1 thresholds ──
  const {
    data: tradingConfig,
    loading: tradingLoading,
    error: tradingError,
    refresh: refreshTrading,
  } = usePolling<ConfigData>('voice/config/get?domain=trading', {
    interval: 30_000,
  });

  const {
    data: llmConfig,
    loading: llmLoading,
    refresh: refreshLlm,
  } = usePolling<ConfigData>('voice/config/get?domain=llm', {
    interval: 30_000,
  });

  const {
    data: voiceConfig,
    loading: voiceLoading,
    refresh: refreshVoice,
  } = usePolling<ConfigData>('voice/config/get?domain=voice', {
    interval: 30_000,
  });

  const {
    data: systemConfig,
    loading: systemLoading,
    refresh: refreshSystem,
  } = usePolling<ConfigData>('voice/config/get?domain=system', {
    interval: 30_000,
  });

  const {
    data: thresholds,
    loading: thresholdsLoading,
    error: thresholdsError,
    refresh: refreshThresholds,
  } = usePolling<ThresholdsData>('thresholds', { interval: 30_000 });

  // ── Motor: config update ──
  const { mutate: updateConfig, loading: updating } =
    useMutation<ConfigResult>('voice/config/set', {
      onSuccess: (data) => {
        toast.success(data?.message || `Updated ${editDomain}.${editKey}`);
        setEditKey('');
        setEditValue('');
        // Refresh the affected domain after a short delay
        setTimeout(() => {
          const refreshMap: Record<string, () => void> = {
            trading: refreshTrading,
            llm: refreshLlm,
            voice: refreshVoice,
            system: refreshSystem,
          };
          refreshMap[editDomain]?.();
        }, 1500);
      },
      onError: (err) => toast.error(`Config update failed: ${err}`),
    });

  // ── Derived state ──
  const allLoading =
    tradingLoading && llmLoading && voiceLoading && systemLoading && thresholdsLoading;
  const hasError = !!(tradingError || thresholdsError);

  const configsByDomain: { key: string; label: string; icon: typeof Settings; data: ConfigData | null; loading: boolean }[] = [
    { key: 'trading', label: 'Trading', icon: TrendingUp, data: tradingConfig, loading: tradingLoading },
    { key: 'llm', label: 'LLM', icon: Brain, data: llmConfig, loading: llmLoading },
    { key: 'voice', label: 'Voice', icon: Mic, data: voiceConfig, loading: voiceLoading },
    { key: 'system', label: 'System', icon: Server, data: systemConfig, loading: systemLoading },
  ];

  const handleRefreshAll = () => {
    refreshTrading();
    refreshLlm();
    refreshVoice();
    refreshSystem();
    refreshThresholds();
  };

  const handleUpdate = async () => {
    if (!editDomain || !editKey) return;
    await updateConfig({
      domain: editDomain,
      key: editKey,
      value: editValue,
    });
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
        <Skeleton className="h-10 w-64" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} className="h-32 rounded-lg" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-6xl space-y-6">
      {/* ── Header ── */}
      <div className="flex items-center gap-4">
        <div className="w-10 h-10 rounded-lg bg-surface flex items-center justify-center">
          <Settings className="w-5 h-5 text-accent" />
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="text-lg font-semibold">Settings</h1>
            <Badge status={hasError ? 'warning' : 'success'} />
            <span className="text-xs text-text-muted">
              {hasError ? 'partial' : 'connected'}
            </span>
          </div>
          <p className="text-sm text-text-muted">
            4 domains &middot; {countKeys(tradingConfig) + countKeys(llmConfig) + countKeys(voiceConfig) + countKeys(systemConfig)} keys loaded
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
          <span className="text-text">
            {tradingError || thresholdsError}
          </span>
        </div>
      )}

      {/* ── Tabs ── */}
      <Tabs
        tabs={['Configuration', 'Thresholds']}
        active={activeTab}
        onChange={setActiveTab}
      />

      {/* ── Configuration Tab ── */}
      <TabPanel active={activeTab} index={0}>
        <div className="space-y-6">
          {/* Domain Config Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {configsByDomain.map((domain) => (
              <ConfigCard
                key={domain.key}
                label={domain.label}
                icon={domain.icon}
                data={domain.data}
                loading={domain.loading}
              />
            ))}
          </div>

          {/* Config Editor */}
          <div className="glass-card rounded-lg p-5">
            <SectionHeader title="Update Configuration" />
            <p className="mt-2 text-sm text-text-secondary">
              Set a configuration value for any domain. Changes take effect immediately on the OpenClaw runtime.
            </p>
            <div className="mt-3 grid grid-cols-1 sm:grid-cols-4 gap-3 items-end">
              <Select
                value={editDomain}
                onChange={setEditDomain}
                options={DOMAIN_OPTIONS}
                label="Domain"
              />
              <div>
                <label className="block text-xs font-medium text-text-muted mb-1">
                  Key
                </label>
                <input
                  type="text"
                  value={editKey}
                  onChange={(e) => setEditKey(e.target.value)}
                  placeholder="config_key"
                  className="w-full px-3 py-2 text-sm rounded-[var(--radius)] bg-surface text-text border border-border focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent transition-colors font-mono"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-text-muted mb-1">
                  Value
                </label>
                <input
                  type="text"
                  value={editValue}
                  onChange={(e) => setEditValue(e.target.value)}
                  placeholder="new_value"
                  className="w-full px-3 py-2 text-sm rounded-[var(--radius)] bg-surface text-text border border-border focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent transition-colors font-mono"
                />
              </div>
              <ActionButton
                onClick={handleUpdate}
                confirm={`Set ${editDomain}.${editKey} = "${editValue}"? This changes the live runtime configuration.`}
                confirmTitle="Update Configuration"
                variant="primary"
                loading={updating}
                disabled={!editKey}
              >
                <Save className="w-3.5 h-3.5" />
                Update
              </ActionButton>
            </div>
          </div>
        </div>
      </TabPanel>

      {/* ── Thresholds Tab ── */}
      <TabPanel active={activeTab} index={1}>
        <div className="space-y-6">
          {thresholds && Object.keys(thresholds).length > 0 ? (
            <div className="glass-card rounded-lg p-5">
              <SectionHeader title="Trading Thresholds" />
              <div className="mt-3 space-y-1">
                {Object.entries(thresholds)
                  .filter(([, v]) => v != null)
                  .map(([key, value]) => (
                    <div
                      key={key}
                      className="flex justify-between items-center py-1.5 border-b border-border-subtle last:border-b-0"
                    >
                      <span className="text-sm text-text-muted">
                        {key.replace(/_/g, ' ')}
                      </span>
                      <span className="text-sm text-text font-mono">
                        {displayValue(value)}
                      </span>
                    </div>
                  ))}
              </div>
            </div>
          ) : (
            <EmptyState
              message="No threshold data"
              submessage="Threshold configuration will appear when the trading engine reports its state."
            />
          )}
        </div>
      </TabPanel>

      {/* ── Footer ── */}
      <div className="text-xs text-text-muted text-right">
        Polling: config 30s &times; 4 domains &middot; thresholds 30s
      </div>
    </div>
  );
}

/* ─── Sub-Components ─── */

function ConfigCard({
  label,
  icon: Icon,
  data,
  loading,
}: {
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  data: ConfigData | null;
  loading: boolean;
}) {
  if (loading && !data) {
    return <Skeleton className="h-32 rounded-lg" />;
  }

  const entries = data
    ? Object.entries(data).filter(([, v]) => v != null)
    : [];

  return (
    <div className="glass-card rounded-lg p-4">
      <div className="flex items-center gap-2 mb-3">
        <Icon className="w-4 h-4 text-accent" />
        <span className="text-sm font-medium text-text">{label}</span>
        <span className="text-xs text-text-muted ml-auto">
          {entries.length} keys
        </span>
      </div>
      {entries.length > 0 ? (
        <div className="space-y-1 max-h-48 overflow-y-auto">
          {entries.map(([key, value]) => (
            <div
              key={key}
              className="flex justify-between items-center text-xs py-0.5"
            >
              <span className="text-text-muted truncate mr-2">
                {key.replace(/_/g, ' ')}
              </span>
              <span className="text-text font-mono truncate max-w-[50%] text-right">
                {displayValue(value)}
              </span>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-xs text-text-muted">No configuration data</p>
      )}
    </div>
  );
}
