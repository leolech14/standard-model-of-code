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

const ROOTS: Record<string, string> = {
  PROJECTS_all: join(HOME, 'PROJECTS_all'),
  Downloads: join(HOME, 'Downloads'),
  _inbox: join(HOME, '_inbox'),
  '.devjournal': join(HOME, '.devjournal'),
  'music-production': join(HOME, 'music-production'),
  '3d-workshop': join(HOME, '3d-workshop'),
};

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

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const rootKey = searchParams.get('root') || 'PROJECTS_all';
    const subPath = searchParams.get('path') || '';
    const depth = Math.min(Math.max(parseInt(searchParams.get('depth') || String(DEFAULT_DEPTH)), 1), MAX_DEPTH);

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
      },
    });
  } catch (err) {
    return NextResponse.json(
      { success: false, error: String(err) },
      { status: 500 },
    );
  }
}
