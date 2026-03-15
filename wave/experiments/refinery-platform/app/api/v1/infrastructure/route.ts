import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import { readFile } from 'fs/promises';
import { promisify } from 'util';

const execAsync = promisify(exec);

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
  status: 'running' | 'completed' | 'failed';
}

interface GCSEntry {
  dir: string;
  size: string;
  action: string;
  reason: string;
}

async function runCommand(cmd: string, timeoutMs = 5000): Promise<string> {
  try {
    const { stdout } = await execAsync(cmd, { timeout: timeoutMs });
    return stdout.trim();
  } catch {
    return '';
  }
}

function parseSize(sizeStr: string): number {
  const match = sizeStr.match(/([\d.]+)\s*(B|K|M|G|T)/i);
  if (!match) return 0;
  const val = parseFloat(match[1]);
  const unit = match[2].toUpperCase();
  const multipliers: Record<string, number> = {
    B: 1, K: 1024, M: 1024 ** 2, G: 1024 ** 3, T: 1024 ** 4,
  };
  return val * (multipliers[unit] || 1);
}

async function getDiskUsage(): Promise<{ total: string; used: string; free: string; pct: number }> {
  const raw = await runCommand("df -h / | tail -1 | awk '{print $2, $3, $4, $5}'");
  const parts = raw.split(/\s+/);
  return {
    total: parts[0] || '926Gi',
    used: parts[1] || '?',
    free: parts[2] || '?',
    pct: parseInt(parts[3]) || 0,
  };
}

async function getDriveUsage(): Promise<{ total: string; used: string; free: string }> {
  const raw = await runCommand('rclone about gdrive: --json', 10000);
  try {
    const data = JSON.parse(raw);
    const toGiB = (b: number) => `${(b / 1024 ** 3).toFixed(1)}G`;
    return {
      total: toGiB(data.total || 0),
      used: toGiB(data.used || 0),
      free: toGiB(data.free || 0),
    };
  } catch {
    return { total: '2048G', used: '~102G', free: '~1946G' };
  }
}

async function getArchiveSize(): Promise<string> {
  return await runCommand('du -sh ~/\\_archive/ 2>/dev/null | cut -f1') || '~20G';
}

async function getRcloneProcesses(): Promise<RcloneProcess[]> {
  const raw = await runCommand("ps aux | grep 'rclone copy' | grep -v grep");
  if (!raw) return [];

  const processes: RcloneProcess[] = [];
  for (const line of raw.split('\n')) {
    const parts = line.split(/\s+/);
    const pid = parseInt(parts[1]);
    // Extract source and destination from the command
    const cmdIdx = parts.findIndex(p => p === 'copy');
    if (cmdIdx === -1) continue;
    const source = parts[cmdIdx + 1] || '';
    const dest = parts[cmdIdx + 2] || '';
    // Get runtime from ps
    const elapsed = parts[9] || '?';

    processes.push({
      pid,
      source: source.replace(/.*\//, '').replace(/\/$/, '') || source,
      destination: dest.replace('gdrive:', '').replace(/\/$/, '') || dest,
      runtime: elapsed,
      status: 'running',
    });
  }
  return processes;
}

function parseManifest(content: string): {
  archives: ArchiveEntry[];
  gcsEntries: GCSEntry[];
  totalOffloaded: string;
  gcsMigrated: string;
  gcsSkipped: string;
  timeline: Array<{ date: string; action: string; impact: string }>;
} {
  const archives: ArchiveEntry[] = [];
  const gcsEntries: GCSEntry[] = [];
  const timeline: Array<{ date: string; action: string; impact: string }> = [];

  const lines = content.split('\n');

  // Parse offloaded directories table
  let inOffloadTable = false;
  let inGCSTable = false;
  let inTimeline = false;
  let headerSkipped = false;

  for (const line of lines) {
    // Detect offloaded directories section
    if (line.includes('## Offloaded Directories')) {
      inOffloadTable = true;
      inGCSTable = false;
      inTimeline = false;
      headerSkipped = false;
      continue;
    }

    // Detect GCS Bucket Inventory section
    if (line.includes('### GCS Bucket Inventory')) {
      inGCSTable = true;
      inOffloadTable = false;
      inTimeline = false;
      headerSkipped = false;
      continue;
    }

    // Detect timeline section
    if (line.includes('## Timeline')) {
      inTimeline = true;
      inOffloadTable = false;
      inGCSTable = false;
      headerSkipped = false;
      continue;
    }

    // End sections on new ## headers
    if (line.startsWith('## ') && !line.includes('Offloaded') && !line.includes('Timeline')) {
      if (inOffloadTable) inOffloadTable = false;
    }
    if (line.startsWith('### ') && !line.includes('GCS Bucket Inventory')) {
      if (inGCSTable) inGCSTable = false;
    }

    if (line.startsWith('|') && line.includes('---')) {
      headerSkipped = true;
      continue;
    }

    if (inOffloadTable && headerSkipped && line.startsWith('|')) {
      const cols = line.split('|').map(c => c.trim()).filter(Boolean);
      if (cols.length >= 5) {
        archives.push({
          source: cols[0].replace(/`/g, ''),
          destination: cols[1].replace(/`/g, ''),
          size: cols[2],
          files: cols[3],
          status: cols[4] as ArchiveEntry['status'],
        });
      }
    }

    if (inGCSTable && headerSkipped && line.startsWith('|')) {
      const cols = line.split('|').map(c => c.trim()).filter(Boolean);
      if (cols.length >= 4) {
        gcsEntries.push({
          dir: cols[0].replace(/`/g, ''),
          size: cols[1],
          action: cols[2].replace(/\*\*/g, ''),
          reason: cols[3],
        });
      }
    }

    if (inTimeline && headerSkipped && line.startsWith('|')) {
      const cols = line.split('|').map(c => c.trim()).filter(Boolean);
      if (cols.length >= 3) {
        timeline.push({
          date: cols[0],
          action: cols[1],
          impact: cols[2],
        });
      }
    }
  }

  // Extract totals
  const totalMatch = content.match(/Total offloaded:\s*~?([\d.]+G)/);
  const migratedMatch = content.match(/Migrated\*\*:\s*~?([\d.]+G)/);
  const skippedMatch = content.match(/Skipped\*\*:\s*~?([\d.]+G)/);

  return {
    archives,
    gcsEntries,
    totalOffloaded: totalMatch?.[1] || '102G',
    gcsMigrated: migratedMatch?.[1] || '12G',
    gcsSkipped: skippedMatch?.[1] || '43G',
    timeline,
  };
}

export async function GET() {
  try {
    // Run queries in parallel
    const [disk, drive, archiveSize, rcloneProcs, manifestRaw] = await Promise.all([
      getDiskUsage(),
      getDriveUsage(),
      getArchiveSize(),
      getRcloneProcesses(),
      readFile(
        `${process.env.HOME}/_archive/OFFLOAD_MANIFEST.md`,
        'utf-8'
      ).catch(() => ''),
    ]);

    const manifest = parseManifest(manifestRaw);

    // Detect environment
    const hostname = await runCommand('hostname');
    const isMac = process.platform === 'darwin';
    const hostLabel = isMac ? 'Mac SSD' : `VPS (${hostname || 'rainmaker'})`;

    // Build storage tiers
    const tiers: StorageTier[] = [
      {
        id: 't1',
        name: 'T1 Hot',
        service: hostLabel,
        capacity: disk.total,
        used: disk.used,
        usedBytes: parseSize(disk.used),
        capacityBytes: parseSize(disk.total),
        purpose: 'Active projects, current work',
        status: 'online',
      },
      {
        id: 't2',
        name: 'T2 Warm',
        service: 'Google Drive (rclone)',
        capacity: drive.total,
        used: drive.used,
        usedBytes: parseSize(drive.used),
        capacityBytes: parseSize(drive.total),
        purpose: 'Archives, backups, offloaded data',
        status: rcloneProcs.length > 0 ? 'uploading' : 'online',
      },
      {
        id: 't3',
        name: 'T3 Quick',
        service: 'iCloud Drive',
        capacity: '200G',
        used: '7.3G',
        usedBytes: parseSize('7.3G'),
        capacityBytes: parseSize('200G'),
        purpose: 'Cross-device access (phone/iPad)',
        status: 'online',
      },
      {
        id: 't4',
        name: 'T4 Cold',
        service: 'GCS (elements-archive-2026)',
        capacity: '55.2G',
        used: '55.2G',
        usedBytes: parseSize('55.2G'),
        capacityBytes: parseSize('55.2G'),
        purpose: 'Frozen cold storage (billing disabled)',
        status: 'offline',
      },
    ];

    const data = {
      tiers,
      disk: { ...disk },
      drive,
      archiveLocalSize: archiveSize,
      rcloneProcesses: rcloneProcs,
      manifest: {
        archives: manifest.archives,
        gcsEntries: manifest.gcsEntries,
        totalOffloaded: manifest.totalOffloaded,
        gcsMigrated: manifest.gcsMigrated,
        gcsSkipped: manifest.gcsSkipped,
        timeline: manifest.timeline,
      },
      lastUpdated: new Date().toISOString(),
    };

    return NextResponse.json({ success: true, data });
  } catch (error) {
    return NextResponse.json(
      { success: false, error: String(error) },
      { status: 500 }
    );
  }
}
