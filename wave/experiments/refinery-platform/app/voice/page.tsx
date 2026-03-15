'use client';

import React, { useState, useEffect } from 'react';
import {
  Mic,
  RefreshCw,
  Wifi,
  WifiOff,
  AlertTriangle,
  Phone,
  PhoneOff,
  Zap,
} from 'lucide-react';
import { Badge, SectionHeader, EmptyState } from '@/components/shared/Common';
import { Skeleton, Tabs, TabPanel, DataTable, Select } from '@/components/ui';
import type { Column } from '@/components/ui';
import { ActionButton } from '@/components/ui/ActionButton';
import { usePolling } from '@/lib/usePolling';
import { useMutation } from '@/lib/useMutation';
import { useToast } from '@/components/ui/Toast';

/* ─── Types ─── */

/** GET /api/openclaw/voice/gateway/status */
interface GatewayStatus {
  tier?: string;
  provider?: string;
  status?: string;
}

/** Single provider entry from GET /api/openclaw/voice/providers */
interface ProviderInfo {
  name: string;
  tier?: string;
  status?: string;
  cause?: string;
  quota?: { used?: number; limit?: number };
  balance?: number;
  key_status?: string;
  [key: string]: unknown;
}

/** GET /api/openclaw/voice/providers */
interface ProvidersResponse {
  providers?: ProviderInfo[];
  active_tier?: string;
  active_provider?: string;
  [key: string]: unknown;
}

/** GET /api/openclaw/voice/self-knowledge */
interface SelfKnowledge {
  tiers?: Record<string, string>;
  llm_mode?: string;
  context_layers?: string[];
  warnings?: string[];
  capabilities?: string[];
}

/** GET /api/openclaw/meet/status */
interface MeetStatus {
  active?: boolean;
  duration?: number;
  connection?: string;
  call_type?: string;
  participant?: string;
}

/** POST /api/openclaw/voice/provider/switch-full */
interface SwitchResult {
  success: boolean;
  message?: string;
  new_provider?: string;
}

/** POST /api/openclaw/voice/sync-self */
interface SyncResult {
  success: boolean;
  message?: string;
}

/* ─── Constants ─── */

const PROVIDER_OPTIONS = [
  { value: 'auto', label: 'Auto (best available)' },
  { value: 'elevenlabs', label: 'ElevenLabs' },
  { value: 'openai', label: 'OpenAI' },
  { value: 'grok', label: 'Grok' },
  { value: 'gemini', label: 'Gemini' },
  { value: 'selfhosted', label: 'Self-Hosted' },
  { value: 'twilio', label: 'Twilio' },
];

/* ─── Helpers ─── */

function providerStatusToBadge(status: string): string {
  const map: Record<string, string> = {
    active: 'success',
    available: 'idle',
    unavailable: 'error',
    error: 'error',
    degraded: 'warning',
    connecting: 'running',
  };
  return map[status?.toLowerCase()] || 'idle';
}

function formatQuota(row: ProviderInfo): string {
  if (row.quota?.limit) {
    return `${row.quota.used ?? 0} / ${row.quota.limit}`;
  }
  if (row.balance != null) {
    return `$${row.balance.toFixed(2)}`;
  }
  return '--';
}

function formatDuration(seconds?: number): string {
  if (!seconds || seconds <= 0) return '--';
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, '0')}`;
}

/* ─── DataTable columns ─── */

const providerColumns: Column<ProviderInfo>[] = [
  {
    key: 'name',
    label: 'Provider',
    render: (v) => <span className="font-medium capitalize">{String(v)}</span>,
  },
  { key: 'tier', label: 'Tier', width: 'w-20' },
  {
    key: 'status',
    label: 'Status',
    align: 'center',
    render: (v) => (
      <span className="inline-flex items-center gap-1.5">
        <Badge status={providerStatusToBadge(String(v ?? ''))} />
        <span className="text-xs capitalize">{String(v ?? '--')}</span>
      </span>
    ),
  },
  {
    key: 'cause',
    label: 'Cause',
    render: (v) => (
      <span className="text-text-secondary">{v ? String(v) : '--'}</span>
    ),
  },
  {
    key: 'key_status',
    label: 'Quota',
    sortable: false,
    align: 'right',
    render: (_v, row) => (
      <span className="font-mono text-xs">{formatQuota(row)}</span>
    ),
  },
];

/* ─── Main Page ─── */

export default function VoicePage() {
  const toast = useToast();
  const [activeTab, setActiveTab] = useState(0);
  const [selectedProvider, setSelectedProvider] = useState('');

  // ── Sensory: 4 polling hooks ──
  const {
    data: gateway,
    loading: gatewayLoading,
    error: gatewayError,
    refresh: refreshGateway,
  } = usePolling<GatewayStatus>('voice/gateway/status', { interval: 15_000 });

  const {
    data: providersData,
    loading: providersLoading,
    error: providersError,
    refresh: refreshProviders,
  } = usePolling<ProvidersResponse>('voice/providers', { interval: 15_000 });

  const {
    data: selfKnowledge,
    loading: knowledgeLoading,
    refresh: refreshKnowledge,
  } = usePolling<SelfKnowledge>('voice/self-knowledge', { interval: 30_000 });

  const {
    data: meetData,
    loading: meetLoading,
    refresh: refreshMeet,
  } = usePolling<MeetStatus>('meet/status', { interval: 15_000 });

  // ── Motor: 2 mutation hooks ──
  const { mutate: switchProvider, loading: switching } = useMutation<SwitchResult>(
    'voice/provider/switch-full',
    {
      onSuccess: (data) => {
        toast.success(data?.message || `Switched to ${data?.new_provider || 'new provider'}`);
        setTimeout(() => { refreshGateway(); refreshProviders(); }, 2000);
      },
      onError: (err) => toast.error(`Provider switch failed: ${err}`),
    }
  );

  const { mutate: syncSelf, loading: syncing } = useMutation<SyncResult>(
    'voice/sync-self',
    {
      onSuccess: (data) => toast.success(data?.message || 'Voice identity synced'),
      onError: (err) => toast.error(`Sync failed: ${err}`),
    }
  );

  // ── Derived state ──
  const allLoading = gatewayLoading && providersLoading && knowledgeLoading && meetLoading;
  const isConnected = !gatewayError && !providersError;

  // Normalize providers — handle bare array or wrapped object
  const providers: ProviderInfo[] = Array.isArray(providersData)
    ? (providersData as unknown as ProviderInfo[])
    : (providersData?.providers ?? []);

  // Sync select value when gateway data first arrives
  useEffect(() => {
    if (gateway?.provider && !selectedProvider) {
      setSelectedProvider(gateway.provider);
    }
  }, [gateway?.provider, selectedProvider]);

  const handleRefreshAll = () => {
    refreshGateway();
    refreshProviders();
    refreshKnowledge();
    refreshMeet();
  };

  const handleSwitch = async () => {
    if (!selectedProvider) return;
    await switchProvider({ provider: selectedProvider });
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
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[...Array(4)].map((_, i) => <Skeleton key={i} className="h-16 rounded-lg" />)}
        </div>
        <Skeleton className="h-32 rounded-lg" />
        <Skeleton className="h-48 rounded-lg" />
      </div>
    );
  }

  return (
    <div className="p-6 max-w-6xl space-y-6">
      {/* ── Header ── */}
      <div className="flex items-center gap-4">
        <div className="w-10 h-10 rounded-lg bg-surface flex items-center justify-center">
          <Mic className="w-5 h-5 text-accent" />
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="text-lg font-semibold">Voice Engine</h1>
            <Badge status={gateway?.status === 'active' ? 'success' : gateway?.status ? 'warning' : 'idle'} />
            <span className="text-xs text-text-muted capitalize">
              {gateway?.status || 'unknown'}
            </span>
          </div>
          <p className="text-sm text-text-muted">
            {gateway?.provider || '--'} &middot; {gateway?.tier || '--'}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {isConnected ? (
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

      {/* ── Connection Error Banner ── */}
      {(gatewayError || providersError) && (
        <div className="flex items-center gap-3 p-3 rounded-lg bg-danger/10 border border-danger/20 text-sm">
          <AlertTriangle className="w-4 h-4 text-danger shrink-0" />
          <span className="text-text">
            {gatewayError || providersError}
          </span>
        </div>
      )}

      {/* ── Tabs ── */}
      <Tabs tabs={['Status', 'Providers']} active={activeTab} onChange={setActiveTab} />

      {/* ── Status Tab ── */}
      <TabPanel active={activeTab} index={0}>
        <div className="space-y-6">
          {/* Gateway Info Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <InfoTile label="Current Tier" value={gateway?.tier || '--'} />
            <InfoTile
              label="Provider"
              value={gateway?.provider || '--'}
            />
            <InfoTile
              label="Status"
              value={gateway?.status || '--'}
              badge={gateway?.status === 'active' ? 'success' : gateway?.status ? 'warning' : undefined}
            />
            <InfoTile
              label="Active Call"
              value={
                meetData?.active
                  ? `${formatDuration(meetData.duration)} (${meetData.call_type || 'call'})`
                  : 'None'
              }
              badge={meetData?.active ? 'live' : undefined}
            />
          </div>

          {/* Provider Switcher */}
          <div className="glass-card rounded-lg p-5">
            <SectionHeader title="Switch Provider" />
            <div className="mt-3 flex items-end gap-3">
              <Select
                value={selectedProvider}
                onChange={setSelectedProvider}
                options={PROVIDER_OPTIONS}
                placeholder="Select provider..."
                label="Voice Provider"
                className="flex-1 max-w-xs"
              />
              <ActionButton
                onClick={handleSwitch}
                confirm={`Switch voice provider to "${selectedProvider}"? This will end any active call and restart the voice engine with the new provider.`}
                confirmTitle="Switch Voice Provider"
                variant="primary"
                loading={switching}
                disabled={!selectedProvider || selectedProvider === gateway?.provider}
              >
                <Zap className="w-3.5 h-3.5" />
                Switch
              </ActionButton>
            </div>
          </div>

          {/* Active Call Card */}
          {meetData?.active && (
            <div className="glass-card rounded-lg p-5">
              <div className="flex items-center gap-2 mb-3">
                <Phone className="w-4 h-4 text-accent" />
                <SectionHeader title="Active Call" />
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <InfoTile label="Type" value={meetData.call_type || '--'} />
                <InfoTile label="Participant" value={meetData.participant || '--'} />
                <InfoTile label="Duration" value={formatDuration(meetData.duration)} />
                <InfoTile
                  label="Connection"
                  value={meetData.connection || '--'}
                  badge={meetData.connection === 'connected' ? 'success' : 'warning'}
                />
              </div>
            </div>
          )}

          {/* Self-Knowledge Card */}
          {selfKnowledge && (selfKnowledge.llm_mode || selfKnowledge.context_layers?.length || selfKnowledge.warnings?.length) && (
            <div className="glass-card rounded-lg p-5">
              <SectionHeader title="System Knowledge" />
              <div className="mt-3 space-y-2 text-sm">
                {selfKnowledge.llm_mode && (
                  <div className="flex justify-between">
                    <span className="text-text-muted">LLM Mode</span>
                    <span className="text-text font-mono text-xs">{selfKnowledge.llm_mode}</span>
                  </div>
                )}
                {selfKnowledge.context_layers && selfKnowledge.context_layers.length > 0 && (
                  <div className="flex justify-between">
                    <span className="text-text-muted">Context Layers</span>
                    <span className="text-text text-xs">{selfKnowledge.context_layers.join(', ')}</span>
                  </div>
                )}
                {selfKnowledge.capabilities && selfKnowledge.capabilities.length > 0 && (
                  <div className="flex justify-between">
                    <span className="text-text-muted">Capabilities</span>
                    <span className="text-text text-xs">{selfKnowledge.capabilities.length} active</span>
                  </div>
                )}
                {selfKnowledge.warnings && selfKnowledge.warnings.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-border/50 space-y-1">
                    {selfKnowledge.warnings.map((w, i) => (
                      <WarningRow key={i} message={w} />
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Sync Action Card */}
          <div className="glass-card rounded-lg p-5">
            <SectionHeader title="Voice Sync" />
            <p className="mt-2 text-sm text-text-secondary">
              Re-sync the voice engine with current workspace files. Reloads the system prompt, tool definitions, and sound profile.
            </p>
            <div className="mt-3">
              <ActionButton
                onClick={async () => { await syncSelf(); }}
                confirm="Re-sync voice identity? This reloads the system prompt and tool sounds from workspace files. The voice engine will briefly restart."
                confirmTitle="Sync Voice Identity"
                variant="secondary"
                loading={syncing}
              >
                <RefreshCw className="w-3 h-3" />
                Sync Now
              </ActionButton>
            </div>
          </div>
        </div>
      </TabPanel>

      {/* ── Providers Tab ── */}
      <TabPanel active={activeTab} index={1}>
        <div className="space-y-6">
          {providers.length > 0 ? (
            <DataTable<ProviderInfo>
              columns={providerColumns}
              data={providers}
              emptyMessage="No providers available"
            />
          ) : (
            <EmptyState
              message="No providers available"
              submessage="Provider data will appear when the voice engine reports status."
            />
          )}
        </div>
      </TabPanel>

      {/* ── Footer ── */}
      <div className="text-xs text-text-muted text-right">
        Polling: gateway 15s &middot; providers 15s &middot; knowledge 30s &middot; call 15s
      </div>
    </div>
  );
}

/* ─── Sub-Components ─── */

function InfoTile({ label, value, badge }: { label: string; value: string; badge?: string }) {
  return (
    <div className="glass-card rounded-lg p-3">
      <div className="text-xs text-text-muted mb-1">{label}</div>
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium text-text font-mono">{value}</span>
        {badge && <Badge status={badge as 'success' | 'warning' | 'error' | 'idle' | 'live' | 'running'} />}
      </div>
    </div>
  );
}

function WarningRow({ message }: { message: string }) {
  return (
    <div className="flex items-center gap-2 text-xs py-1">
      <AlertTriangle className="w-3 h-3 text-warning shrink-0" />
      <span className="text-text">{message}</span>
    </div>
  );
}
