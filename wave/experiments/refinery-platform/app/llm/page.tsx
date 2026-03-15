'use client';

import React, { useState, useEffect } from 'react';
import {
  Brain,
  RefreshCw,
  Wifi,
  WifiOff,
  AlertTriangle,
  Zap,
  Layers,
  Settings2,
} from 'lucide-react';
import { Badge, SectionHeader, EmptyState } from '@/components/shared/Common';
import { Skeleton, Select } from '@/components/ui';
import { ActionButton } from '@/components/ui/ActionButton';
import { usePolling } from '@/lib/usePolling';
import { useMutation } from '@/lib/useMutation';
import { useToast } from '@/components/ui/Toast';

/* ─── Types ─── */

/** GET /api/openclaw/llm/mode
 *  Tool description says: "active mode (eco/full), configured chain,
 *  loaded chain, and preset definitions."
 *  We type all fields optional — render whatever the API actually returns.
 */
interface LlmModeData {
  mode?: string;
  provider?: string;
  configured_chain?: string;
  loaded_chain?: string;
  chain?: string;
  preset_definitions?: Record<string, unknown>;
  presets?: Record<string, unknown>;
  memory_enabled?: boolean;
  memory_count?: number;
  version?: string;
  [key: string]: unknown;
}

/** POST /api/openclaw/llm/mode */
interface ModeResult {
  success: boolean;
  message?: string;
  mode?: string;
}

/* ─── Constants ─── */

const MODE_OPTIONS = [
  { value: 'eco', label: 'Eco (cheaper, slower)' },
  { value: 'full', label: 'Full (stronger, faster)' },
];

/* ─── Helpers ─── */

function modeStatusToBadge(mode: string): string {
  const map: Record<string, string> = {
    eco: 'idle',
    full: 'success',
  };
  return map[mode?.toLowerCase()] || 'idle';
}

/** Render preset/chain definitions as a compact key-value display */
function renderKvBlock(data: Record<string, unknown>): React.ReactNode {
  const entries = Object.entries(data).filter(
    ([, v]) => v != null && v !== ''
  );
  if (entries.length === 0) return null;

  return (
    <div className="space-y-1">
      {entries.map(([key, value]) => (
        <div key={key} className="flex justify-between text-sm">
          <span className="text-text-muted">{key.replace(/_/g, ' ')}</span>
          <span className="text-text font-mono text-xs truncate max-w-[60%] text-right">
            {typeof value === 'object' ? JSON.stringify(value) : String(value)}
          </span>
        </div>
      ))}
    </div>
  );
}

/* ─── Main Page ─── */

export default function LlmPage() {
  const toast = useToast();
  const [selectedMode, setSelectedMode] = useState('');

  // ── Sensory: 1 polling hook ──
  const {
    data: modeData,
    loading,
    error,
    refresh,
  } = usePolling<LlmModeData>('llm/mode', { interval: 15_000 });

  // ── Motor: 1 mutation hook ──
  const { mutate: switchMode, loading: switching } = useMutation<ModeResult>(
    'llm/mode',
    {
      onSuccess: (data) => {
        toast.success(
          data?.message || `Switched to ${data?.mode || selectedMode} mode`
        );
        setTimeout(() => {
          refresh();
        }, 2000);
      },
      onError: (err) => toast.error(`Mode switch failed: ${err}`),
    }
  );

  // Sync select with current mode on first load
  useEffect(() => {
    if (modeData?.mode && !selectedMode) {
      setSelectedMode(modeData.mode);
    }
  }, [modeData?.mode, selectedMode]);

  const handleSwitch = async () => {
    if (!selectedMode) return;
    await switchMode({ mode: selectedMode });
  };

  // ── Derived state ──
  const isConnected = !error;
  const currentMode = modeData?.mode || '--';
  const currentProvider = modeData?.provider || '--';

  // Detect extra fields the API may return beyond mode/provider
  const hasChainInfo = !!(
    modeData?.configured_chain ||
    modeData?.loaded_chain ||
    modeData?.chain
  );
  const hasPresets = !!(
    modeData?.preset_definitions &&
    Object.keys(modeData.preset_definitions).length > 0
  ) || !!(
    modeData?.presets &&
    Object.keys(modeData.presets).length > 0
  );
  const hasMemoryInfo = modeData?.memory_enabled != null || modeData?.memory_count != null;

  // Gather all "extra" fields beyond mode/provider for discovery rendering
  const knownKeys = new Set([
    'mode', 'provider', 'configured_chain', 'loaded_chain', 'chain',
    'preset_definitions', 'presets', 'memory_enabled', 'memory_count', 'version',
  ]);
  const extraFields: Record<string, unknown> = {};
  if (modeData) {
    for (const [k, v] of Object.entries(modeData)) {
      if (!knownKeys.has(k) && v != null && v !== '') {
        extraFields[k] = v;
      }
    }
  }
  const hasExtraFields = Object.keys(extraFields).length > 0;

  // ── Loading State ──
  if (loading) {
    return (
      <div className="p-6 max-w-6xl space-y-6">
        <div className="flex items-center gap-4">
          <Skeleton className="h-10 w-10 rounded-lg" />
          <div className="space-y-2">
            <Skeleton className="h-6 w-40" />
            <Skeleton className="h-4 w-56" />
          </div>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {[...Array(3)].map((_, i) => (
            <Skeleton key={i} className="h-16 rounded-lg" />
          ))}
        </div>
        <Skeleton className="h-28 rounded-lg" />
      </div>
    );
  }

  return (
    <div className="p-6 max-w-6xl space-y-6">
      {/* ── Header ── */}
      <div className="flex items-center gap-4">
        <div className="w-10 h-10 rounded-lg bg-surface flex items-center justify-center">
          <Brain className="w-5 h-5 text-accent" />
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="text-lg font-semibold">LLM Engine</h1>
            <Badge status={modeStatusToBadge(currentMode)} />
            <span className="text-xs text-text-muted capitalize">
              {currentMode}
            </span>
          </div>
          <p className="text-sm text-text-muted">
            {currentProvider} {modeData?.version ? `v${modeData.version}` : ''}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {isConnected ? (
            <Wifi className="w-4 h-4 text-accent" />
          ) : (
            <WifiOff className="w-4 h-4 text-danger" />
          )}
          <button
            onClick={refresh}
            className="p-2 rounded-md hover:bg-surface text-text-secondary hover:text-text transition-colors"
            title="Refresh"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* ── Connection Error Banner ── */}
      {error && (
        <div className="flex items-center gap-3 p-3 rounded-lg bg-danger/10 border border-danger/20 text-sm">
          <AlertTriangle className="w-4 h-4 text-danger shrink-0" />
          <span className="text-text">{error}</span>
        </div>
      )}

      {/* ── Status Grid ── */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        <InfoTile
          label="Mode"
          value={currentMode}
          badge={modeStatusToBadge(currentMode)}
        />
        <InfoTile label="Provider" value={currentProvider} />
        {hasMemoryInfo ? (
          <InfoTile
            label="Memory"
            value={
              modeData?.memory_count != null
                ? `${modeData.memory_count} entries`
                : modeData?.memory_enabled
                ? 'Enabled'
                : 'Disabled'
            }
            badge={modeData?.memory_enabled ? 'success' : 'idle'}
          />
        ) : (
          <InfoTile
            label="Version"
            value={modeData?.version || '--'}
          />
        )}
      </div>

      {/* ── Mode Switcher ── */}
      <div className="glass-card rounded-lg p-5">
        <SectionHeader title="Switch Mode" />
        <p className="mt-2 text-sm text-text-secondary">
          Toggle between eco (cheaper, suitable for simple tasks) and full
          (stronger model, lower latency) LLM chains.
        </p>
        <div className="mt-3 flex items-end gap-3">
          <Select
            value={selectedMode}
            onChange={setSelectedMode}
            options={MODE_OPTIONS}
            placeholder="Select mode..."
            label="LLM Mode"
            className="flex-1 max-w-xs"
          />
          <ActionButton
            onClick={handleSwitch}
            confirm={`Switch LLM mode to "${selectedMode}"? This changes the active language model chain for all voice conversations.`}
            confirmTitle="Switch LLM Mode"
            variant="primary"
            loading={switching}
            disabled={!selectedMode || selectedMode === modeData?.mode}
          >
            <Zap className="w-3.5 h-3.5" />
            Switch
          </ActionButton>
        </div>
      </div>

      {/* ── Chain Details (conditional) ── */}
      {hasChainInfo && (
        <div className="glass-card rounded-lg p-5">
          <div className="flex items-center gap-2 mb-3">
            <Layers className="w-4 h-4 text-accent" />
            <SectionHeader title="Chain Configuration" />
          </div>
          <div className="space-y-2 text-sm">
            {modeData?.configured_chain && (
              <div className="flex justify-between">
                <span className="text-text-muted">Configured Chain</span>
                <span className="text-text font-mono text-xs">
                  {modeData.configured_chain}
                </span>
              </div>
            )}
            {modeData?.loaded_chain && (
              <div className="flex justify-between">
                <span className="text-text-muted">Loaded Chain</span>
                <span className="text-text font-mono text-xs">
                  {modeData.loaded_chain}
                </span>
              </div>
            )}
            {modeData?.chain && !modeData?.configured_chain && (
              <div className="flex justify-between">
                <span className="text-text-muted">Chain</span>
                <span className="text-text font-mono text-xs">
                  {modeData.chain}
                </span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ── Preset Definitions (conditional) ── */}
      {hasPresets && (
        <div className="glass-card rounded-lg p-5">
          <div className="flex items-center gap-2 mb-3">
            <Settings2 className="w-4 h-4 text-accent" />
            <SectionHeader title="Preset Definitions" />
          </div>
          {renderKvBlock(
            (modeData?.preset_definitions || modeData?.presets) as Record<
              string,
              unknown
            >
          )}
        </div>
      )}

      {/* ── Extra Fields Discovery (conditional) ── */}
      {hasExtraFields && (
        <div className="glass-card rounded-lg p-5">
          <SectionHeader title="Additional Data" />
          <div className="mt-3">
            {renderKvBlock(extraFields)}
          </div>
        </div>
      )}

      {/* ── Footer ── */}
      <div className="text-xs text-text-muted text-right">
        Polling: mode 15s
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
  badge?: string;
}) {
  return (
    <div className="glass-card rounded-lg p-3">
      <div className="text-xs text-text-muted mb-1">{label}</div>
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium text-text font-mono">
          {value}
        </span>
        {badge && (
          <Badge
            status={
              badge as
                | 'success'
                | 'warning'
                | 'error'
                | 'idle'
                | 'live'
                | 'running'
            }
          />
        )}
      </div>
    </div>
  );
}
