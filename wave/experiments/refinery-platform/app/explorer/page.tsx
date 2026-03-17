'use client';

import React, { useEffect, useState, useMemo, useCallback } from 'react';
import { localGet } from '@/lib/api';
import { Skeleton } from '@/components/ui';
import {
  FolderTree, Folder, FolderOpen, File, FileText, FileCode,
  FileJson, ChevronRight, Home, Grid3X3, List,
  ArrowDownAZ, HardDrive, Calendar, RefreshCw, Search,
} from 'lucide-react';

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

interface BrowseData {
  tree: FileSystemNode;
  stats: { totalDirs: number; totalFiles: number; scanDurationMs: number };
  rootKey: string;
  roots: string[];
}

/* ── Helpers ─────────────────────────────────── */

const FILE_ICONS: Record<string, typeof File> = {
  '.ts': FileCode, '.tsx': FileCode, '.js': FileCode, '.jsx': FileCode,
  '.py': FileCode, '.rs': FileCode, '.go': FileCode, '.sh': FileCode,
  '.md': FileText, '.txt': FileText, '.mdx': FileText,
  '.json': FileJson, '.yaml': FileJson, '.yml': FileJson, '.toml': FileJson,
};

function getFileIcon(ext?: string) {
  return (ext && FILE_ICONS[ext]) || File;
}

function formatSize(bytes: number): string {
  if (bytes === 0) return '--';
  if (bytes < 1024) return `${bytes}B`;
  if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)}KB`;
  if (bytes < 1073741824) return `${(bytes / 1048576).toFixed(1)}MB`;
  return `${(bytes / 1073741824).toFixed(1)}GB`;
}

function formatDate(iso: string): string {
  if (!iso) return '--';
  const d = new Date(iso);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function findNode(tree: FileSystemNode, path: string): FileSystemNode | null {
  if (tree.path === path) return tree;
  if (!tree.children) return null;
  for (const child of tree.children) {
    const found = findNode(child, path);
    if (found) return found;
  }
  return null;
}

/* ── Tree Sidebar ────────────────────────────── */

function TreeNode({
  node, level, expandedPaths, activePath, onToggle, onNavigate,
}: {
  node: FileSystemNode;
  level: number;
  expandedPaths: Set<string>;
  activePath: string;
  onToggle: (path: string) => void;
  onNavigate: (path: string) => void;
}) {
  if (node.type !== 'directory') return null;
  const isExpanded = expandedPaths.has(node.path);
  const isActive = activePath === node.path;
  const hasChildren = (node.children && node.children.length > 0) || (node.childCount && node.childCount > 0);
  const FolderIcon = isExpanded ? FolderOpen : Folder;

  return (
    <div>
      <div
        className={`
          flex items-center py-1 pr-2 cursor-pointer transition-colors border-l-2
          ${isActive
            ? 'bg-[var(--color-surface-hover)] border-[var(--color-accent)] text-[var(--color-accent)]'
            : 'border-transparent text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-hover)]/30'
          }
        `}
        style={{ paddingLeft: `${level * 12 + 8}px` }}
        onClick={() => { onNavigate(node.path); if (!isExpanded) onToggle(node.path); }}
      >
        <div
          className="p-0.5 mr-1 rounded-[var(--radius-sm)] hover:bg-[var(--color-surface-hover)] text-[var(--color-text-muted)]"
          onClick={(e) => { e.stopPropagation(); onToggle(node.path); }}
        >
          {hasChildren ? (
            <ChevronRight className={`w-3 h-3 transition-transform ${isExpanded ? 'rotate-90' : ''}`} />
          ) : (
            <div className="w-3 h-3" />
          )}
        </div>
        <FolderIcon className={`w-3.5 h-3.5 mr-2 ${isActive ? 'text-[var(--color-accent)]' : 'text-[var(--color-text-muted)]'}`} />
        <span className="text-xs truncate font-medium">{node.name}</span>
        {(node.childCount ?? node.children?.length) != null && (
          <span className="ml-auto text-[9px] text-[var(--color-text-muted)] font-mono">
            {node.childCount ?? node.children?.filter((c) => c.type === 'directory').length}
          </span>
        )}
      </div>
      {isExpanded && node.children && (
        <div>
          {node.children
            .filter((c) => c.type === 'directory')
            .map((child) => (
              <TreeNode
                key={child.path}
                node={child}
                level={level + 1}
                expandedPaths={expandedPaths}
                activePath={activePath}
                onToggle={onToggle}
                onNavigate={onNavigate}
              />
            ))}
        </div>
      )}
    </div>
  );
}

/* ── Content Items (rich preview cards) ──────── */

function FolderThumbnail({ node }: { node: FileSystemNode }) {
  const children = node.children || [];
  const dirCount = children.filter((c) => c.type === 'directory').length;
  const fileCount = children.filter((c) => c.type === 'file').length;
  const maxItems = 9;
  const preview = children.slice(0, maxItems);

  if (children.length === 0) {
    return (
      <div className="w-20 h-20 mb-2 flex items-center justify-center bg-[var(--color-surface)]/20 rounded-[var(--radius)] border border-[var(--color-border)] group-hover:border-[var(--color-text-muted)] transition-all">
        <Folder className="w-8 h-8 text-[var(--color-text-muted)] group-hover:text-[var(--color-text-secondary)]" strokeWidth={1} />
      </div>
    );
  }

  return (
    <div className="w-20 h-20 mb-2 bg-[var(--color-bg)]/50 rounded-[var(--radius)] border border-[var(--color-border)] p-1.5 flex flex-col gap-1 group-hover:border-[var(--color-text-muted)] transition-all overflow-hidden shadow-sm">
      <div className="grid grid-cols-3 gap-0.5 w-full flex-1 auto-rows-fr">
        {preview.map((child, i) => (
          <div
            key={i}
            title={child.name}
            className={`rounded-[2px] transition-colors ${
              child.type === 'directory'
                ? 'bg-[var(--color-accent)]/40 border border-[var(--color-accent)]/20 group-hover:bg-[var(--color-accent)]/60'
                : 'bg-[var(--color-emerald)]/40 border border-[var(--color-emerald)]/20 group-hover:bg-[var(--color-emerald)]/60'
            }`}
          />
        ))}
        {Array.from({ length: Math.max(0, maxItems - preview.length) }).map((_, i) => (
          <div key={`e-${i}`} className="rounded-[2px] bg-[var(--color-surface)]/50" />
        ))}
      </div>
      <div className="h-1 w-full flex rounded-full overflow-hidden bg-[var(--color-surface)] shrink-0">
        <div className="bg-[var(--color-accent)]" style={{ width: `${(dirCount / (dirCount + fileCount || 1)) * 100}%` }} />
        <div className="bg-[var(--color-emerald)]" style={{ width: `${(fileCount / (dirCount + fileCount || 1)) * 100}%` }} />
      </div>
    </div>
  );
}

function FolderCard({ node, onClick }: { node: FileSystemNode; onClick: () => void }) {
  const total = node.childCount ?? (node.children?.length ?? 0);
  return (
    <div
      onClick={onClick}
      className="group flex flex-col items-center p-3 rounded-[var(--radius-lg)] border border-transparent hover:border-[var(--color-border)] hover:bg-[var(--color-surface-hover)]/40 cursor-pointer transition-all h-44 justify-start"
    >
      <FolderThumbnail node={node} />
      <span className="text-xs text-[var(--color-text-secondary)] font-medium text-center truncate w-full">{node.name}</span>
      <span className="text-[10px] text-[var(--color-text-muted)] mt-0.5 font-mono">{total} items</span>
    </div>
  );
}

function FileCard({ node }: { node: FileSystemNode }) {
  const Icon = getFileIcon(node.extension);
  return (
    <div className="group relative flex flex-col p-3 rounded-[var(--radius-lg)] border border-[var(--color-border)] bg-[var(--color-surface)]/20 hover:bg-[var(--color-surface-hover)]/60 hover:border-[var(--color-text-muted)] cursor-pointer transition-all h-44">
      <div className="flex justify-end">
        <span className="text-[9px] font-mono uppercase text-[var(--color-text-muted)] bg-[var(--color-surface)]/60 px-1.5 py-0.5 rounded-[var(--radius-sm)]">
          {node.extension?.replace('.', '') || '?'}
        </span>
      </div>
      <div className="flex-1 flex items-center justify-center opacity-40 group-hover:opacity-70 transition-opacity">
        <Icon className="w-10 h-10 text-[var(--color-text-muted)]" strokeWidth={1} />
      </div>
      <div className="min-w-0">
        <div className="text-xs font-medium text-[var(--color-text-secondary)] truncate">{node.name}</div>
        <div className="text-[10px] font-mono text-[var(--color-text-muted)] mt-0.5">
          {formatSize(node.size)}{node.modified && ` · ${formatDate(node.modified)}`}
        </div>
      </div>
    </div>
  );
}

function FileRow({ node }: { node: FileSystemNode }) {
  const Icon = node.type === 'directory' ? Folder : getFileIcon(node.extension);
  return (
    <div className="flex items-center gap-3 px-3 py-1.5 rounded-[var(--radius-sm)] hover:bg-[var(--color-surface-hover)] transition-colors cursor-pointer">
      <Icon className="w-4 h-4 text-[var(--color-text-muted)] shrink-0" />
      <span className="flex-1 text-sm text-[var(--color-text-secondary)] truncate">{node.name}</span>
      <span className="text-xs text-[var(--color-text-muted)] font-mono w-20 text-right">{formatDate(node.modified)}</span>
      <span className="text-xs text-[var(--color-text-muted)] font-mono w-12 text-right uppercase">{node.extension?.replace('.', '') || (node.type === 'directory' ? 'dir' : '')}</span>
      <span className="text-xs text-[var(--color-text-muted)] font-mono w-16 text-right">{node.type === 'file' ? formatSize(node.size) : `${node.childCount ?? node.children?.length ?? 0}`}</span>
    </div>
  );
}

/* ── Main Page ───────────────────────────────── */

export default function ExplorerPage() {
  const [data, setData] = useState<BrowseData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activePath, setActivePath] = useState('.');
  const [expandedPaths, setExpandedPaths] = useState<Set<string>>(new Set(['.']));
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<'name' | 'size' | 'date'>('name');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [selectedRoot, setSelectedRoot] = useState('PROJECTS_all');
  const [refreshKey, setRefreshKey] = useState(0);

  // Fetch tree
  const fetchTree = useCallback((root: string, path?: string, depth?: number) => {
    setLoading(true);
    setError('');
    const params = new URLSearchParams({ root, depth: String(depth ?? 2) });
    if (path) params.set('path', path);
    localGet<{ success: boolean; data: BrowseData }>(`filesystem?${params}`)
      .then((res) => { if (res.success) { setData(res.data); setActivePath('.'); } })
      .catch((err) => setError(String(err)))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { fetchTree(selectedRoot); }, [selectedRoot, refreshKey, fetchTree]);

  // Current folder contents
  const currentNode = useMemo(() => {
    if (!data) return null;
    return findNode(data.tree, activePath);
  }, [data, activePath]);

  const contents = useMemo(() => {
    if (!currentNode?.children) return [];
    let items = [...currentNode.children];

    // Search filter
    if (searchQuery) {
      items = items.filter((c) => c.name.toLowerCase().includes(searchQuery.toLowerCase()));
    }

    // Sort (directories always first)
    items.sort((a, b) => {
      if (a.type !== b.type) return a.type === 'directory' ? -1 : 1;
      if (sortBy === 'name') return a.name.localeCompare(b.name);
      if (sortBy === 'size') return b.size - a.size;
      if (sortBy === 'date') return (b.modified || '').localeCompare(a.modified || '');
      return 0;
    });

    return items;
  }, [currentNode, searchQuery, sortBy]);

  // Breadcrumbs
  const breadcrumbs = activePath === '.' ? [] : activePath.split('/').filter(Boolean);

  const navigateToBreadcrumb = (index: number) => {
    if (index === -1) { setActivePath('.'); return; }
    const path = breadcrumbs.slice(0, index + 1).join('/');
    setActivePath(path);
  };

  const toggleExpand = (path: string) => {
    setExpandedPaths((prev) => {
      const next = new Set(prev);
      if (next.has(path)) next.delete(path); else next.add(path);
      return next;
    });
  };

  const navigateTo = (path: string) => {
    setActivePath(path);
    // Auto-expand path in tree
    const parts = path.split('/');
    setExpandedPaths((prev) => {
      const next = new Set(prev);
      let p = '';
      for (const part of parts) {
        p = p ? `${p}/${part}` : part;
        next.add(p);
      }
      return next;
    });
  };

  // Loading
  if (loading && !data) {
    return (
      <div className="flex h-full">
        <div className="w-64 border-r border-[var(--color-border)] p-3 space-y-2">
          {[...Array(8)].map((_, i) => <Skeleton key={i} className="h-6" />)}
        </div>
        <div className="flex-1 p-6">
          <Skeleton className="h-8 w-48 mb-4" />
          <div className="grid grid-cols-4 gap-3">
            {[...Array(12)].map((_, i) => <Skeleton key={i} className="h-24" />)}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <h1 className="text-xl font-semibold text-[var(--color-text)]">Explorer</h1>
        <div className="mt-4 p-4 rounded-[var(--radius)] border border-[var(--color-danger)]/30 bg-[var(--color-danger)]/5 text-sm text-[var(--color-text)]">
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-[var(--color-bg)] text-[var(--color-text-muted)]">
      {/* Toolbar */}
      <div className="h-11 border-b border-[var(--color-border)] flex items-center justify-between px-4 shrink-0">
        <div className="flex items-center gap-1 text-sm overflow-hidden">
          {/* Root selector */}
          <select
            value={selectedRoot}
            onChange={(e) => setSelectedRoot(e.target.value)}
            className="text-xs bg-[var(--color-surface)] border border-[var(--color-border)] rounded-[var(--radius-sm)] px-2 py-1 text-[var(--color-text-secondary)] focus:outline-none mr-2"
          >
            {data?.roots.map((r) => <option key={r} value={r}>{r}</option>)}
          </select>

          <div className="h-4 w-px bg-[var(--color-border)] mx-1" />

          {/* Breadcrumbs */}
          <button onClick={() => navigateToBreadcrumb(-1)} className="p-1 rounded-[var(--radius-sm)] hover:bg-[var(--color-surface-hover)] text-[var(--color-text-muted)]">
            <Home className="w-4 h-4" />
          </button>
          {breadcrumbs.map((part, i) => (
            <React.Fragment key={i}>
              <ChevronRight className="w-3 h-3 text-[var(--color-text-muted)] shrink-0" />
              <button
                onClick={() => navigateToBreadcrumb(i)}
                className={`px-2 py-0.5 rounded-[var(--radius-sm)] transition-colors whitespace-nowrap text-xs ${
                  i === breadcrumbs.length - 1
                    ? 'bg-[var(--color-surface-hover)] text-[var(--color-text)] font-medium'
                    : 'text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-hover)]'
                }`}
              >
                {part}
              </button>
            </React.Fragment>
          ))}
        </div>

        <div className="flex items-center gap-2 pl-2 border-l border-[var(--color-border)] ml-2">
          {/* Sort buttons */}
          <div className="flex bg-[var(--color-surface)] rounded-[var(--radius-sm)] border border-[var(--color-border)] p-0.5">
            {([['name', ArrowDownAZ], ['size', HardDrive], ['date', Calendar]] as const).map(([key, Icon]) => (
              <button
                key={key}
                onClick={() => setSortBy(key as typeof sortBy)}
                className={`p-1 rounded-[var(--radius-sm)] ${sortBy === key ? 'bg-[var(--color-surface-hover)] text-[var(--color-text)] shadow-sm' : 'text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)]'}`}
                title={`Sort by ${key}`}
              >
                <Icon className="w-3.5 h-3.5" />
              </button>
            ))}
          </div>

          {/* Search */}
          <div className="relative">
            <Search className="absolute left-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[var(--color-text-muted)]" />
            <input
              type="text"
              placeholder="Filter..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-28 focus:w-40 transition-all bg-[var(--color-surface)] border border-[var(--color-border)] rounded-[var(--radius-sm)] h-7 pl-7 text-xs text-[var(--color-text-secondary)] focus:outline-none focus:border-[var(--color-text-muted)] placeholder:text-[var(--color-text-muted)]"
            />
          </div>

          {/* View toggle */}
          <div className="flex bg-[var(--color-surface)] rounded-[var(--radius-sm)] border border-[var(--color-border)] p-0.5">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-1 rounded-[var(--radius-sm)] ${viewMode === 'grid' ? 'bg-[var(--color-surface-hover)] text-[var(--color-text)] shadow-sm' : 'text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)]'}`}
            >
              <Grid3X3 className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-1 rounded-[var(--radius-sm)] ${viewMode === 'list' ? 'bg-[var(--color-surface-hover)] text-[var(--color-text)] shadow-sm' : 'text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)]'}`}
            >
              <List className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Refresh */}
          <button
            onClick={() => setRefreshKey((k) => k + 1)}
            className="p-1.5 rounded-[var(--radius-sm)] text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-hover)]"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Main area */}
      <div className="flex flex-1 min-h-0">
        {/* Tree sidebar */}
        <div className="w-64 flex flex-col border-r border-[var(--color-border)] bg-[var(--color-surface)]/30 shrink-0">
          <div className="h-9 flex items-center px-4 border-b border-[var(--color-border)]">
            <FolderTree className="w-3.5 h-3.5 text-[var(--color-text-muted)] mr-2" />
            <span className="text-xs font-semibold uppercase tracking-wider text-[var(--color-text-muted)]">{selectedRoot}</span>
          </div>
          <div className="flex-1 overflow-y-auto overflow-x-hidden hover:overflow-x-auto py-1">
            {data?.tree.children?.map((child) => (
              <TreeNode
                key={child.path}
                node={child}
                level={0}
                expandedPaths={expandedPaths}
                activePath={activePath}
                onToggle={toggleExpand}
                onNavigate={navigateTo}
              />
            ))}
          </div>
          <div className="p-2 border-t border-[var(--color-border)] text-[10px] text-[var(--color-text-muted)] font-mono flex justify-between">
            <span>{data?.stats.totalDirs ?? 0} dirs</span>
            <span>{data?.stats.totalFiles ?? 0} files</span>
            <span>{data?.stats.scanDurationMs ?? 0}ms</span>
          </div>
        </div>

        {/* Content area */}
        <div className="flex-1 flex flex-col min-w-0">
          <div className="flex-1 overflow-y-auto p-4">
            {contents.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center opacity-40">
                <FolderOpen className="w-12 h-12 text-[var(--color-text-muted)] mb-2" strokeWidth={1} />
                <span className="text-sm text-[var(--color-text-muted)]">
                  {searchQuery ? 'No matches' : 'Empty folder'}
                </span>
              </div>
            ) : viewMode === 'grid' ? (
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-2">
                {contents.map((node) =>
                  node.type === 'directory' ? (
                    <FolderCard key={node.path} node={node} onClick={() => navigateTo(node.path)} />
                  ) : (
                    <FileCard key={node.path} node={node} />
                  )
                )}
              </div>
            ) : (
              <div className="space-y-0.5">
                {contents.map((node) => (
                  <div key={node.path} onClick={() => node.type === 'directory' && navigateTo(node.path)}>
                    <FileRow node={node} />
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Status bar */}
          <div className="h-6 bg-[var(--color-surface)] border-t border-[var(--color-border)] flex items-center px-4 justify-between text-[9px] text-[var(--color-text-muted)] select-none">
            <span className="font-mono">/{selectedRoot}/{activePath === '.' ? '' : activePath}</span>
            <div className="flex items-center gap-3">
              <span>{contents.filter((c) => c.type === 'directory').length} folders</span>
              <span>{contents.filter((c) => c.type === 'file').length} files</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
