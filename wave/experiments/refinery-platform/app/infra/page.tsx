'use client';

import { useEffect, useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import {
  HardDrive,
  Cloud,
  CloudOff,
  Smartphone,
  Upload,
  CheckCircle2,
  Clock,
  AlertTriangle,
  Server,
  RefreshCw,
  Database,
  ArrowUpDown,
} from 'lucide-react';
import { Badge } from '@/components/shared/Common';
import { Skeleton } from '@/components/ui';
import { localGet } from '@/lib/api';

/* ─── Types ─── */

interface StorageTier {
  id: string;
  name: string;
  service: string;
  capacity: string;
  used: string;
  usedBytes: number;
  capacityBytes: number;
  purpose: string;
  status: 'online' | 'offline' | 'degraded' | 'uploading';
}

interface ArchiveEntry {
  source: string;
  destination: string;
  size: string;
  files: string;
  status: 'VERIFIED' | 'UPLOADING' | 'PENDING';
}

interface RcloneProcess {
  pid: number;
  source: string;
  destination: string;
  runtime: string;
  status: string;
}

interface GCSEntry {
  dir: string;
  size: string;
  action: string;
  reason: string;
}

interface InfraData {
  tiers: StorageTier[];
  disk: { total: string; used: string; free: string; pct: number };
  drive: { total: string; used: string; free: string };
  archiveLocalSize: string;
  rcloneProcesses: RcloneProcess[];
  manifest: {
    archives: ArchiveEntry[];
    gcsEntries: GCSEntry[];
    totalOffloaded: string;
    gcsMigrated: string;
    gcsSkipped: string;
    timeline: Array<{ date: string; action: string; impact: string }>;
  };
  lastUpdated: string;
}

/* ─── Sub-Components ─── */

function TierCard({ tier }: { tier: StorageTier }) {
  const pct = tier.capacityBytes > 0 ? (tier.usedBytes / tier.capacityBytes) * 100 : 0;

  const tierIcons: Record<string, React.ReactNode> = {
    t1: <HardDrive className="w-5 h-5" />,
    t2: <Cloud className="w-5 h-5" />,
    t3: <Smartphone className="w-5 h-5" />,
    t4: <CloudOff className="w-5 h-5" />,
  };

  const tierColors: Record<string, string> = {
    t1: 'text-accent',
    t2: 'text-info',
    t3: 'text-purple',
    t4: 'text-text-muted',
  };

  const barColors: Record<string, string> = {
    t1: 'bg-accent',
    t2: 'bg-info',
    t3: 'bg-purple',
    t4: 'bg-border-subtle',
  };

  const statusMap: Record<string, string> = {
    online: 'success',
    offline: 'idle',
    degraded: 'warning',
    uploading: 'running',
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card rounded-lg p-5"
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className={tierColors[tier.id]}>{tierIcons[tier.id]}</div>
          <div>
            <div className="font-semibold text-sm">{tier.name}</div>
            <div className="text-xs text-text-muted">{tier.service}</div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Badge status={statusMap[tier.status] || 'idle'} />
          <span className="text-xs text-text-secondary capitalize">{tier.status}</span>
        </div>
      </div>

      {/* Usage bar */}
      <div className="mb-2">
        <div className="h-2 bg-surface rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${Math.min(pct, 100)}%` }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
            className={`h-full rounded-full ${barColors[tier.id]}`}
          />
        </div>
      </div>

      <div className="flex justify-between text-xs text-text-secondary">
        <span>{tier.used} used</span>
        <span>{tier.capacity} total</span>
      </div>

      <div className="mt-3 text-xs text-text-muted">{tier.purpose}</div>
    </motion.div>
  );
}

function ArchiveTable({ archives }: { archives: ArchiveEntry[] }) {
  const statusIcon = (status: string) => {
    if (status === 'VERIFIED') return <CheckCircle2 className="w-3.5 h-3.5 text-accent" />;
    if (status === 'UPLOADING') return <Upload className="w-3.5 h-3.5 text-info animate-pulse" />;
    return <Clock className="w-3.5 h-3.5 text-text-muted" />;
  };

  return (
    <div className="glass-card rounded-lg overflow-hidden">
      <div className="px-5 py-3 border-b border-border">
        <div className="flex items-center gap-2">
          <Database className="w-4 h-4 text-accent" />
          <h3 className="text-sm font-semibold">Archive Inventory</h3>
          <span className="text-xs text-text-muted ml-auto">{archives.length} entries</span>
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="text-text-muted uppercase tracking-wider border-b border-border/50">
              <th className="text-left px-5 py-2 font-medium">Source</th>
              <th className="text-left px-3 py-2 font-medium">Remote</th>
              <th className="text-right px-3 py-2 font-medium">Size</th>
              <th className="text-right px-3 py-2 font-medium">Files</th>
              <th className="text-center px-5 py-2 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {archives.map((entry, i) => (
              <tr
                key={i}
                className="border-b border-border/30 hover:bg-surface-hover transition-colors"
              >
                <td className="px-5 py-2.5 font-mono text-text truncate max-w-[200px]">
                  {entry.source}
                </td>
                <td className="px-3 py-2.5 font-mono text-text-muted truncate max-w-[250px]">
                  {entry.destination}
                </td>
                <td className="px-3 py-2.5 text-right text-text whitespace-nowrap">
                  {entry.size}
                </td>
                <td className="px-3 py-2.5 text-right text-text-secondary whitespace-nowrap">
                  {entry.files}
                </td>
                <td className="px-5 py-2.5 text-center">
                  <span className="inline-flex items-center gap-1.5">
                    {statusIcon(entry.status)}
                    <span className={
                      entry.status === 'VERIFIED'
                        ? 'text-accent'
                        : entry.status === 'UPLOADING'
                          ? 'text-info'
                          : 'text-text-muted'
                    }>
                      {entry.status}
                    </span>
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function GCSSection({
  entries,
  migrated,
  skipped,
}: {
  entries: GCSEntry[];
  migrated: string;
  skipped: string;
}) {
  if (entries.length === 0) return null;

  return (
    <div className="glass-card rounded-lg overflow-hidden">
      <div className="px-5 py-3 border-b border-border">
        <div className="flex items-center gap-2">
          <Server className="w-4 h-4 text-warning" />
          <h3 className="text-sm font-semibold">GCS Migration (elements-archive-2026)</h3>
        </div>
        <div className="flex gap-4 mt-2 text-xs">
          <span className="text-accent">Migrated: ~{migrated}</span>
          <span className="text-text-muted">Skipped: ~{skipped} redundant</span>
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="text-text-muted uppercase tracking-wider border-b border-border/50">
              <th className="text-left px-5 py-2 font-medium">Directory</th>
              <th className="text-right px-3 py-2 font-medium">Size</th>
              <th className="text-center px-3 py-2 font-medium">Action</th>
              <th className="text-left px-5 py-2 font-medium">Reason</th>
            </tr>
          </thead>
          <tbody>
            {entries.map((entry, i) => (
              <tr
                key={i}
                className="border-b border-border/30 hover:bg-surface-hover transition-colors"
              >
                <td className="px-5 py-2 font-mono text-text">{entry.dir}</td>
                <td className="px-3 py-2 text-right text-text whitespace-nowrap">{entry.size}</td>
                <td className="px-3 py-2 text-center">
                  <span
                    className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${
                      entry.action === 'SKIPPED'
                        ? 'bg-surface text-text-secondary'
                        : entry.action === 'Migrated'
                          ? 'bg-accent/20 text-accent border border-accent/30'
                          : 'bg-info/20 text-info border border-info/30'
                    }`}
                  >
                    {entry.action}
                  </span>
                </td>
                <td className="px-5 py-2 text-text-muted">{entry.reason}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function ActiveUploads({ processes }: { processes: RcloneProcess[] }) {
  if (processes.length === 0) return null;

  return (
    <div className="glass-card rounded-lg p-5">
      <div className="flex items-center gap-2 mb-4">
        <Upload className="w-4 h-4 text-info animate-pulse" />
        <h3 className="text-sm font-semibold">Active Uploads</h3>
        <span className="text-xs px-2 py-0.5 rounded bg-info/20 text-info border border-info/30 ml-auto">
          {processes.length} running
        </span>
      </div>
      <div className="space-y-3">
        {processes.map((proc) => (
          <div key={proc.pid} className="flex items-center gap-4 text-xs">
            <span className="text-text-muted font-mono w-16">PID {proc.pid}</span>
            <div className="flex-1">
              <div className="flex items-center gap-1.5">
                <span className="text-text font-medium">{proc.source}</span>
                <ArrowUpDown className="w-3 h-3 text-text-muted" />
                <span className="text-text-secondary font-mono">{proc.destination}</span>
              </div>
            </div>
            <span className="text-text-muted">{proc.runtime}</span>
            <Badge status="running" />
          </div>
        ))}
      </div>
    </div>
  );
}

function Timeline({ events }: { events: Array<{ date: string; action: string; impact: string }> }) {
  if (events.length === 0) return null;

  return (
    <div className="glass-card rounded-lg overflow-hidden">
      <div className="px-5 py-3 border-b border-border">
        <div className="flex items-center gap-2">
          <Clock className="w-4 h-4 text-purple" />
          <h3 className="text-sm font-semibold">Migration Timeline</h3>
        </div>
      </div>
      <div className="divide-y divide-border/30">
        {events.map((event, i) => (
          <div key={i} className="px-5 py-2.5 flex items-start gap-4 text-xs hover:bg-surface-hover transition-colors">
            <span className="text-text-muted whitespace-nowrap font-mono w-20 shrink-0">
              {event.date}
            </span>
            <span className="text-text flex-1">{event.action}</span>
            <span className="text-text-muted whitespace-nowrap">{event.impact}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ─── Main Page ─── */

export default function InfrastructurePage() {
  const [data, setData] = useState<InfraData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [refreshing, setRefreshing] = useState(false);

  const fetchData = useCallback(async () => {
    try {
      const json = await localGet<{ success: boolean; data: InfraData; error?: string }>('infrastructure');
      if (json.success) {
        setData(json.data);
        setError('');
      } else {
        setError(json.error || 'Failed to load');
      }
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [fetchData]);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchData();
  };

  if (loading) {
    return (
      <div className="p-6 max-w-7xl space-y-6">
        <Skeleton className="h-10 w-64" />
        <div className="grid grid-cols-5 gap-4">
          {[...Array(5)].map((_, i) => <Skeleton key={i} className="h-24" />)}
        </div>
        <div className="grid grid-cols-2 gap-4">
          {[...Array(4)].map((_, i) => <Skeleton key={i} className="h-40" />)}
        </div>
        <Skeleton className="h-64" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="glass-card rounded-lg p-8 text-center max-w-md">
          <AlertTriangle className="w-8 h-8 text-warning mx-auto mb-4" />
          <p className="text-text mb-2">Failed to load infrastructure data</p>
          <p className="text-xs text-text-muted">{error}</p>
          <button
            onClick={() => { setLoading(true); setError(''); fetchData(); }}
            className="mt-4 px-4 py-2 bg-surface hover:bg-elevated rounded-md text-sm transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const verifiedCount = data.manifest.archives.filter(a => a.status === 'VERIFIED').length;
  const uploadingCount = data.manifest.archives.filter(a => a.status === 'UPLOADING').length;

  return (
    <div className="p-6 max-w-7xl">
      {/* Header */}
      <div className="flex items-start justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">Infrastructure</h1>
          <p className="text-text-secondary">
            Storage tiers, archive inventory, and migration status
          </p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="flex items-center gap-2 px-4 py-2 bg-surface hover:bg-elevated rounded-md text-sm transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-5 gap-4 mb-8">
        <div className="glass-card rounded-lg p-4">
          <div className="text-xs text-text-muted uppercase tracking-wider mb-1">Disk Free</div>
          <div className="text-2xl font-bold text-accent">{data.disk.free}</div>
          <div className="text-xs text-text-muted mt-1">{data.disk.pct}% used</div>
        </div>
        <div className="glass-card rounded-lg p-4">
          <div className="text-xs text-text-muted uppercase tracking-wider mb-1">Drive Used</div>
          <div className="text-2xl font-bold text-info">{data.drive.used}</div>
          <div className="text-xs text-text-muted mt-1">of {data.drive.total}</div>
        </div>
        <div className="glass-card rounded-lg p-4">
          <div className="text-xs text-text-muted uppercase tracking-wider mb-1">Offloaded</div>
          <div className="text-2xl font-bold text-purple">~{data.manifest.totalOffloaded}</div>
          <div className="text-xs text-text-muted mt-1">to Google Drive</div>
        </div>
        <div className="glass-card rounded-lg p-4">
          <div className="text-xs text-text-muted uppercase tracking-wider mb-1">Archives</div>
          <div className="text-2xl font-bold">
            <span className="text-accent">{verifiedCount}</span>
            <span className="text-text-muted text-lg"> / {data.manifest.archives.length}</span>
          </div>
          <div className="text-xs text-text-muted mt-1">
            {uploadingCount > 0 ? `${uploadingCount} uploading` : 'all verified'}
          </div>
        </div>
        <div className="glass-card rounded-lg p-4">
          <div className="text-xs text-text-muted uppercase tracking-wider mb-1">Local Archive</div>
          <div className="text-2xl font-bold text-text">{data.archiveLocalSize}</div>
          <div className="text-xs text-text-muted mt-1">~/_archive/ residual</div>
        </div>
      </div>

      {/* Storage Tiers */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4">Storage Tiers</h2>
        <div className="grid grid-cols-2 gap-4">
          {data.tiers.map((tier) => (
            <TierCard key={tier.id} tier={tier} />
          ))}
        </div>
      </div>

      {/* Active Uploads */}
      {data.rcloneProcesses.length > 0 && (
        <div className="mb-8">
          <ActiveUploads processes={data.rcloneProcesses} />
        </div>
      )}

      {/* Archive Inventory */}
      <div className="mb-8">
        <ArchiveTable archives={data.manifest.archives} />
      </div>

      {/* GCS Migration */}
      <div className="mb-8">
        <GCSSection
          entries={data.manifest.gcsEntries}
          migrated={data.manifest.gcsMigrated}
          skipped={data.manifest.gcsSkipped}
        />
      </div>

      {/* Timeline */}
      <div className="mb-8">
        <Timeline events={data.manifest.timeline} />
      </div>

      {/* Footer */}
      <div className="text-xs text-text-muted text-right">
        Last updated: {new Date(data.lastUpdated).toLocaleString()}
        {' '}&bull; Auto-refreshes every 30s
      </div>
    </div>
  );
}
