import { NextResponse } from 'next/server';
import { readdir, stat } from 'fs/promises';
import { resolve, join, basename, extname, relative } from 'path';
import { homedir } from 'os';

/* ── Types ──────────────────────────────────── */

interface FileSystemNode {
  name: string;
  path: string;
  type: 'file' | 'directory';
  size: number;
  modified: string;
  children?: FileSystemNode[];
  childCount?: number;
  extension?: string;
}

interface ScanStats {
  totalDirs: number;
  totalFiles: number;
  scanDurationMs: number;
}

/* ── Constants ──────────────────────────────── */

const HOME = homedir();
const IS_VPS = HOME === '/root';
const MAC_TAILSCALE_IP = '100.111.18.33';
const MAC_API_PORT = 3001;
const MAC_API_TIMEOUT = 3000; // 3s — fail fast if Mac is offline

// Roots available on THIS machine
const LOCAL_ROOTS: Record<string, string> = {
  PROJECTS_all: join(HOME, 'PROJECTS_all'),
  Downloads: join(HOME, 'Downloads'),
  _inbox: join(HOME, '_inbox'),
  '.devjournal': join(HOME, '.devjournal'),
  'music-production': join(HOME, 'music-production'),
  '3d-workshop': join(HOME, '3d-workshop'),
};

// On VPS, some roots only exist on Mac — proxy via Tailscale
const MAC_ONLY_ROOTS = new Set(['Downloads', '_inbox', 'music-production', '3d-workshop']);

const ROOTS = LOCAL_ROOTS;

const EXCLUDED = new Set([
  '.git', 'node_modules', '.venv', '__pycache__', '.next', '.cache',
  'dist', 'build', '.DS_Store', '.Trash', 'venv', 'env', '.tox',
  '.mypy_cache', '.pytest_cache', '.nyc_output', 'target', '.parcel-cache',
  '.turbo', '.svelte-kit', '.nuxt', '.output', 'coverage',
]);

const MAX_DEPTH = 6;
const DEFAULT_DEPTH = 2;

/* ── Scanner ────────────────────────────────── */

async function scanDirectory(
  dirPath: string,
  rootPath: string,
  currentDepth: number,
  maxDepth: number,
  stats: ScanStats,
): Promise<FileSystemNode> {
  const name = basename(dirPath);
  const relPath = relative(rootPath, dirPath) || '.';

  if (currentDepth >= maxDepth) {
    // At max depth — return folder with childCount but no children (lazy load)
    try {
      const entries = await readdir(dirPath);
      const count = entries.filter((e) => !e.startsWith('.') && !EXCLUDED.has(e)).length;
      stats.totalDirs++;
      return { name, path: relPath, type: 'directory', size: 0, modified: '', childCount: count };
    } catch {
      stats.totalDirs++;
      return { name, path: relPath, type: 'directory', size: 0, modified: '', childCount: 0 };
    }
  }

  let entries;
  try {
    entries = await readdir(dirPath, { withFileTypes: true });
  } catch {
    stats.totalDirs++;
    return { name, path: relPath, type: 'directory', size: 0, modified: '', children: [] };
  }

  const children: FileSystemNode[] = [];

  // Sort: directories first, then alphabetical
  const sorted = [...entries].sort((a, b) => {
    if (a.isDirectory() !== b.isDirectory()) return a.isDirectory() ? -1 : 1;
    return a.name.localeCompare(b.name);
  });

  for (const entry of sorted) {
    if (EXCLUDED.has(entry.name)) continue;
    if (entry.name.startsWith('.') && entry.name !== '.devjournal') continue;

    const fullPath = join(dirPath, entry.name);
    const entryRelPath = relative(rootPath, fullPath);

    if (entry.isDirectory()) {
      const child = await scanDirectory(fullPath, rootPath, currentDepth + 1, maxDepth, stats);
      children.push(child);
    } else if (entry.isFile()) {
      try {
        const s = await stat(fullPath);
        stats.totalFiles++;
        children.push({
          name: entry.name,
          path: entryRelPath,
          type: 'file',
          size: s.size,
          modified: s.mtime.toISOString(),
          extension: extname(entry.name).toLowerCase() || undefined,
        });
      } catch {
        // Skip files we can't stat
      }
    }
  }

  stats.totalDirs++;

  let dirModified = '';
  try {
    const s = await stat(dirPath);
    dirModified = s.mtime.toISOString();
  } catch { /* empty */ }

  return { name, path: relPath, type: 'directory', size: 0, modified: dirModified, children };
}

/* ── Route Handler ──────────────────────────── */

/** Try to proxy a filesystem request to the Mac via Tailscale */
async function proxyToMac(rootKey: string, subPath: string, depth: number): Promise<NextResponse | null> {
  // Only proxy on VPS for Mac-only roots
  if (HOME !== '/root') return null;
  if (!MAC_ONLY_ROOTS.has(rootKey)) return null;

  const params = new URLSearchParams({ root: rootKey, depth: String(depth) });
  if (subPath) params.set('path', subPath);
  const url = `http://${MAC_TAILSCALE_IP}:${MAC_API_PORT}/api/v1/filesystem?${params}`;

  try {
    const res = await fetch(url, {
      signal: AbortSignal.timeout(MAC_API_TIMEOUT),
      cache: 'no-store',
    });

    if (!res.ok) return null;

    const data = await res.json();
    if (data?.data) data.data.source = 'mac';
    return NextResponse.json(data);
  } catch {
    // Mac offline or Refinery not running — fall back to local
    return null;
  }
}

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const rootKey = searchParams.get('root') || 'PROJECTS_all';
    const subPath = searchParams.get('path') || '';
    const depth = Math.min(Math.max(parseInt(searchParams.get('depth') || String(DEFAULT_DEPTH)), 1), MAX_DEPTH);

    // On VPS: try Mac proxy for Mac-only roots
    const macResponse = await proxyToMac(rootKey, subPath, depth);
    if (macResponse) return macResponse;

    // Validate root
    const rootDir = ROOTS[rootKey];
    if (!rootDir) {
      return NextResponse.json(
        { success: false, error: `Unknown root: ${rootKey}. Available: ${Object.keys(ROOTS).join(', ')}` },
        { status: 400 },
      );
    }

    // Resolve and validate path (prevent traversal)
    const targetDir = subPath ? resolve(rootDir, subPath) : rootDir;
    if (!targetDir.startsWith(rootDir)) {
      return NextResponse.json(
        { success: false, error: 'Path traversal not allowed' },
        { status: 403 },
      );
    }

    const startMs = Date.now();
    const stats: ScanStats = { totalDirs: 0, totalFiles: 0, scanDurationMs: 0 };

    const tree = await scanDirectory(targetDir, rootDir, 0, depth, stats);
    stats.scanDurationMs = Date.now() - startMs;

    return NextResponse.json({
      success: true,
      data: {
        tree,
        stats,
        rootKey,
        rootPath: rootDir,
        roots: Object.keys(ROOTS),
        source: 'local',
      },
    });
  } catch (err) {
    return NextResponse.json(
      { success: false, error: String(err) },
      { status: 500 },
    );
  }
}
