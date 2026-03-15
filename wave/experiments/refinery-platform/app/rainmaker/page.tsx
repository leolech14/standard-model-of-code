'use client';

import React from 'react';
import { Cloud, RefreshCw } from 'lucide-react';
import { Badge, SectionHeader } from '@/components/shared/Common';
import { Skeleton } from '@/components/ui';
import { usePolling } from '@/lib/usePolling';

interface HealthData {
  status?: string;
  uptime?: number;
  version?: string;
}

interface VoiceStatus {
  tier?: string;
  provider?: string;
  status?: string;
}

interface LlmStatus {
  mode?: string;
  provider?: string;
}

function formatUptime(seconds?: number): string {
  if (!seconds) return '--';
  const d = Math.floor(seconds / 86400);
  const h = Math.floor((seconds % 86400) / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  if (d > 0) return `${d}d ${h}h`;
  if (h > 0) return `${h}h ${m}m`;
  return `${m}m`;
}

export default function RainmakerPage() {
  const { data: health, loading: healthLoading, error: healthError, refresh: refreshHealth } =
    usePolling<HealthData>('health', { interval: 15_000 });
  const { data: voice, loading: voiceLoading, refresh: refreshVoice } =
    usePolling<VoiceStatus>('voice/gateway/status', { interval: 15_000 });
  const { data: llm, loading: llmLoading, refresh: refreshLlm } =
    usePolling<LlmStatus>('llm/mode', { interval: 15_000 });

  const loading = healthLoading && voiceLoading && llmLoading;

  const handleRefresh = () => {
    refreshHealth();
    refreshVoice();
    refreshLlm();
  };

  if (loading) {
    return (
      <div className="p-6 space-y-6 max-w-5xl">
        <div className="flex items-center gap-4">
          <Skeleton className="h-10 w-10 rounded-lg" />
          <div className="space-y-2">
            <Skeleton className="h-5 w-32" />
            <Skeleton className="h-4 w-48" />
          </div>
        </div>
        <div className="grid grid-cols-4 gap-3">
          {[...Array(4)].map((_, i) => <Skeleton key={i} className="h-16" />)}
        </div>
        <div className="grid grid-cols-2 gap-4">
          {[...Array(2)].map((_, i) => <Skeleton key={i} className="h-40" />)}
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 max-w-5xl">
      {/* Header */}
      <div className="flex items-center gap-4">
        <div className="w-10 h-10 rounded-lg bg-surface flex items-center justify-center">
          <Cloud className="w-5 h-5 text-sky" />
        </div>
        <div>
          <h1 className="text-lg font-semibold">Rainmaker</h1>
          <p className="text-sm text-text-muted">Operations Console</p>
        </div>
        <button
          onClick={handleRefresh}
          className="ml-auto p-2 rounded-md hover:bg-surface text-text-secondary hover:text-text transition-colors"
          title="Refresh"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {healthError && (
        <div className="text-sm text-danger bg-danger/10 border border-danger/20 rounded-md p-3">
          Connection error: {healthError}. Make sure OpenClaw is running on the VPS.
        </div>
      )}

      {/* Status Pills */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatusPill
          label="Status"
          value={health?.status || '--'}
          badge={health?.status === 'ok' ? 'success' : health ? 'warning' : 'idle'}
        />
        <StatusPill
          label="Uptime"
          value={formatUptime(health?.uptime)}
        />
        <StatusPill
          label="Voice Tier"
          value={voice?.tier || voice?.provider || '--'}
          badge={voice?.status === 'active' ? 'live' : 'idle'}
        />
        <StatusPill
          label="LLM Mode"
          value={llm?.mode || '--'}
          badge={llm?.mode ? 'active' : 'idle'}
        />
      </div>

      {/* Info Sections */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Voice */}
        <div className="glass-card rounded-lg p-4">
          <SectionHeader title="Voice Engine" />
          <div className="mt-3 space-y-2 text-sm">
            <InfoRow label="Provider" value={voice?.provider || '--'} />
            <InfoRow label="Tier" value={voice?.tier || '--'} />
            <InfoRow label="Status" value={voice?.status || '--'} />
          </div>
        </div>

        {/* LLM */}
        <div className="glass-card rounded-lg p-4">
          <SectionHeader title="LLM Engine" />
          <div className="mt-3 space-y-2 text-sm">
            <InfoRow label="Mode" value={llm?.mode || '--'} />
            <InfoRow label="Provider" value={llm?.provider || '--'} />
            <InfoRow label="Version" value={health?.version || '--'} />
          </div>
        </div>
      </div>

      {/* Footer note */}
      <p className="text-xs text-text-muted">
        Use the floating cloud widget (bottom-right) to chat or call Rainmaker directly.
        Full operations controls coming soon.
      </p>
    </div>
  );
}

// ── Sub-components ──

function StatusPill({ label, value, badge }: { label: string; value: string; badge?: string }) {
  return (
    <div className="glass-card rounded-lg p-3">
      <div className="text-xs text-text-muted mb-1">{label}</div>
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium text-text">{value}</span>
        {badge && <Badge status={badge as any} />}
      </div>
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between">
      <span className="text-text-muted">{label}</span>
      <span className="text-text font-mono text-xs">{value}</span>
    </div>
  );
}
