import React, { useState, useMemo, useEffect } from 'react';
import { Artifact, ContextMenuRequest } from '../types';
import {
    Folder, FolderOpen, File, ChevronRight,
    ChevronDown, Search, Box, Grid, List as ListIcon,
    HardDrive, CornerDownRight, Home, Lock, Layers,
    FileCode, FileVideo, FileAudio, FileJson, ArrowLeft,
    ArrowDownAZ, Calendar, HardDrive as SizeIcon, CheckCircle2, Circle
} from 'lucide-react';
import { UiRow, Badge } from './Common';

// --- TYPES ---

export interface FileSystemNode {
    id: string;
    name: string;
    type: 'folder' | 'file';
    children?: FileSystemNode[]; // Folders have children
    artifact?: Artifact;         // Files have data
    path: string;                // Full path for breadcrumbs/ID
    meta?: {
        count?: number;          // Item count for folders
        color?: string;          // Context color
        icon?: React.ElementType; // Custom icon
    }
}

// --- HELPERS ---

const parseBytes = (sizeStr: string): number => {
    const num = parseFloat(sizeStr);
    const s = sizeStr.toUpperCase();
    if (s.includes('TB')) return num * 1024 * 1024 * 1024 * 1024;
    if (s.includes('GB')) return num * 1024 * 1024 * 1024;
    if (s.includes('MB')) return num * 1024 * 1024;
    if (s.includes('KB')) return num * 1024;
    return num; // bytes
};

export const buildVirtualFileSystem = (artifacts: Artifact[]): FileSystemNode => {
    const root: FileSystemNode = {
        id: 'root',
        name: 'Root',
        type: 'folder',
        children: [],
        path: '/'
    };

    const addArtifactToPath = (parts: string[], art: Artifact, customIcon?: React.ElementType) => {
        let currentLevel = root;
        let currentPath = '';

        parts.forEach((part) => {
            currentPath += `/${part}`;

            let existingNode = currentLevel.children!.find(c => c.name === part && c.type === 'folder');

            if (!existingNode) {
                existingNode = {
                    id: currentPath,
                    name: part,
                    type: 'folder',
                    children: [],
                    path: currentPath,
                    meta: { count: 0 }
                };

                // Apply custom icons for top-level folders
                if (currentLevel.id === 'root') {
                    if (part === 'Projects') existingNode.meta!.icon = Layers;
                    if (part === 'Vault') existingNode.meta!.icon = Lock;
                }

                currentLevel.children!.push(existingNode);
            }

            existingNode.meta!.count!++;
            currentLevel = existingNode;
        });

        // Add File
        currentLevel.children!.push({
            id: `${currentPath}/${art.id}`, // Ensure unique ID even if artifact appears in multiple trees
            name: art.name,
            type: 'file',
            artifact: art,
            path: `${currentPath}/${art.name}`
        });
    };

    artifacts.forEach(art => {
        // 1. General Project Inventory
        // Structure: /Projects / <ProjectId> / <PipelineId> / <Stage> / <AtomClass>
        const projectParts = [
            'Projects',
            art.projectId || 'Unassigned',
            art.pipelineId.replace(' Pipeline', ''),
            art.stage,
            art.atomClass
        ];
        addArtifactToPath(projectParts, art);

        // 2. Vault (Secured Items)
        // Structure: /Vault / <ProjectId> / <AtomClass>
        // Flatter structure for quick access to important items
        if (art.isVaulted) {
             const vaultParts = [
                'Vault',
                art.projectId || 'Unassigned',
                art.atomClass
             ];
             addArtifactToPath(vaultParts, art);
        }
    });

    // Recursive sort: Folders first (Vault/Projects fixed order), then alphabetical
    const sortNodes = (nodes: FileSystemNode[]) => {
        nodes.sort((a, b) => {
            // Force Vault and Projects order at root
            if (a.path === '/Vault') return 1;
            if (b.path === '/Vault') return -1;
            if (a.path === '/Projects') return -1;
            if (b.path === '/Projects') return 1;

            if (a.type === b.type) return a.name.localeCompare(b.name);
            return a.type === 'folder' ? -1 : 1;
        });
        nodes.forEach(n => {
            if (n.children) sortNodes(n.children);
        });
    };

    sortNodes(root.children!);
    return root;
};

// --- COMPONENTS ---

const TreeNode: React.FC<{
    node: FileSystemNode;
    level: number;
    expandedPaths: Set<string>;
    selectedPath: string | null;
    onToggle: (node: FileSystemNode) => void;
    onSelect: (node: FileSystemNode) => void;
}> = ({ node, level, expandedPaths, selectedPath, onToggle, onSelect }) => {
    const isExpanded = expandedPaths.has(node.path);
    const isSelected = selectedPath === node.path;
    const hasChildren = node.children && node.children.length > 0;

    // Icon Selection
    const CustomIcon = node.meta?.icon;
    let Icon = isExpanded ? FolderOpen : Folder;
    if (CustomIcon) Icon = CustomIcon;

    if (node.type === 'file') return null;

    return (
        <div className="select-none">
            <div
                className={`
                    flex items-center py-1 pr-2 cursor-pointer transition-colors border-l-2
                    ${isSelected ? 'bg-neutral-900 border-indigo-500 text-indigo-400' : 'border-transparent text-neutral-500 hover:text-neutral-300 hover:bg-neutral-900/30'}
                `}
                style={{ paddingLeft: `${level * 12 + 8}px` }}
                onClick={(e) => {
                    e.stopPropagation();
                    onSelect(node);
                    if (!isExpanded) onToggle(node); // Auto-expand on click
                }}
            >
                <div
                    className="p-0.5 mr-1 rounded hover:bg-neutral-800 text-neutral-600"
                    onClick={(e) => { e.stopPropagation(); onToggle(node); }}
                >
                    {hasChildren ? (
                        <ChevronRight className={`w-3 h-3 transition-transform ${isExpanded ? 'rotate-90' : ''}`} />
                    ) : (
                        <div className="w-3 h-3" />
                    )}
                </div>

                <Icon className={`w-3.5 h-3.5 mr-2 ${isSelected ? 'text-indigo-400' : (CustomIcon ? 'text-neutral-400' : 'text-neutral-600')}`} />

                <span className="text-xs truncate font-medium">{node.name}</span>
                {node.meta?.count !== undefined && (
                    <span className="ml-auto text-[9px] text-neutral-700 font-mono">{node.meta.count}</span>
                )}
            </div>

            {isExpanded && node.children && (
                <div>
                    {node.children.map(child => (
                        <TreeNode
                            key={child.id}
                            node={child}
                            level={level + 1}
                            expandedPaths={expandedPaths}
                            selectedPath={selectedPath}
                            onToggle={onToggle}
                            onSelect={onSelect}
                        />
                    ))}
                </div>
            )}
        </div>
    );
};

const FolderThumbnail: React.FC<{ node: FileSystemNode }> = ({ node }) => {
    const children = node.children || [];
    const folderCount = children.filter(c => c.type === 'folder').length;
    const fileCount = children.filter(c => c.type === 'file').length;

    // Empty state or Special top-level folders (Project/Vault) which may want an Icon
    if (children.length === 0) {
         const CustomIcon = node.meta?.icon || Folder;
         return (
             <div className="w-24 h-24 mb-3 flex items-center justify-center bg-neutral-900/20 rounded-xl border border-neutral-800 group-hover:border-neutral-700 transition-all">
                 <CustomIcon
                    className={`w-10 h-10 transition-colors ${node.name === 'Vault' ? 'text-emerald-900 group-hover:text-emerald-500' : 'text-neutral-700 group-hover:text-neutral-500'}`}
                    strokeWidth={1}
                />
             </div>
         );
    }

    // Grid Preview Logic: 3x3 Grid
    const maxItems = 9;
    const previewItems = children.slice(0, maxItems);

    return (
        <div className="w-24 h-24 mb-3 bg-neutral-950/50 rounded-xl border border-neutral-800 p-2 flex flex-col gap-1.5 group-hover:border-neutral-600 transition-all shadow-sm relative overflow-hidden">
            {/* 3x3 Grid for Visual Preview */}
            <div className="grid grid-cols-3 gap-1 w-full h-full auto-rows-fr">
                {previewItems.map((child, i) => {
                    const isFolder = child.type === 'folder';
                    // Folders = Indigo, Files = Emerald
                    return (
                        <div
                            key={i}
                            className={`
                                rounded-[2px] transition-colors
                                ${isFolder
                                    ? 'bg-indigo-500/40 border border-indigo-400/20 group-hover:bg-indigo-500/60'
                                    : 'bg-emerald-500/40 border border-emerald-400/20 group-hover:bg-emerald-500/60'
                                }
                            `}
                            title={child.name}
                        />
                    );
                })}
                {/* Fill empty slots with subtle placeholders to maintain grid structure */}
                {Array.from({ length: Math.max(0, maxItems - previewItems.length) }).map((_, i) => (
                    <div key={`empty-${i}`} className="rounded-[2px] bg-neutral-900/50" />
                ))}
            </div>

            {/* Content Distribution Bar */}
            <div className="h-1.5 w-full flex rounded-full overflow-hidden bg-neutral-900 border border-neutral-800/50 shrink-0">
                {/* Folders Portion (Indigo) */}
                <div
                    className="bg-indigo-500"
                    style={{ width: `${(folderCount / (folderCount + fileCount || 1)) * 100}%` }}
                />
                {/* Files Portion (Emerald) */}
                <div
                    className="bg-emerald-500"
                    style={{ width: `${(fileCount / (folderCount + fileCount || 1)) * 100}%` }}
                />
            </div>
        </div>
    );
};

const FileItem: React.FC<{
    node: FileSystemNode;
    selected: boolean;
    onClick: () => void;
    onToggleSelect: () => void;
    onContextMenu: (e: React.MouseEvent) => void;
}> = ({ node, selected, onClick, onToggleSelect, onContextMenu }) => {
    if (node.type === 'folder') {
        const childrenCount = node.children ? node.children.length : 0;
        return (
            <div
                onClick={onClick}
                onDoubleClick={onClick}
                onContextMenu={onContextMenu}
                className="group flex flex-col items-center p-3 rounded-xl border border-transparent hover:border-neutral-800 hover:bg-neutral-900/40 cursor-pointer transition-all h-48 justify-start relative"
            >
                <FolderThumbnail node={node} />
                <div className="flex flex-col items-center w-full px-1">
                    <span className="text-xs text-neutral-300 font-medium text-center truncate w-full">{node.name}</span>
                    <span className="text-[10px] text-neutral-500 mt-1 font-mono">{childrenCount} items</span>
                </div>
            </div>
        );
    }

    // It's a file
    const art = node.artifact!;
    return (
        <div
            onClick={onClick}
            onContextMenu={onContextMenu}
            className={`
                group relative flex flex-col p-3 rounded-xl border transition-all h-48 cursor-pointer
                ${selected
                    ? 'bg-indigo-900/10 border-indigo-500/50 hover:bg-indigo-900/20'
                    : 'bg-neutral-900/20 border-neutral-800 hover:bg-neutral-900/60 hover:border-neutral-700'
                }
            `}
        >
            <div className="flex items-start justify-between mb-4">
                <button
                    onClick={(e) => { e.stopPropagation(); onToggleSelect(); }}
                    className={`
                        w-5 h-5 rounded-full flex items-center justify-center transition-all z-10
                        ${selected
                            ? 'bg-indigo-500 text-white shadow-sm scale-100 opacity-100'
                            : 'bg-neutral-800/50 border border-neutral-600 text-transparent hover:border-neutral-400 group-hover:scale-100 scale-90 opacity-0 group-hover:opacity-100'
                        }
                    `}
                >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                </button>
                <Badge status={art.status} />
            </div>

            {/* File Icon Center */}
            <div className="flex-1 flex items-center justify-center mb-2 opacity-50 group-hover:opacity-80 transition-opacity pointer-events-none">
                 {['mp4', 'wav', 'mov'].includes(art.type) ? <FileVideo className="w-8 h-8 text-neutral-600" strokeWidth={1}/> :
                  ['json', 'xml', 'yaml'].includes(art.type) ? <FileCode className="w-8 h-8 text-neutral-600" strokeWidth={1}/> :
                  <File className="w-8 h-8 text-neutral-600" strokeWidth={1}/>
                 }
            </div>

            <div className="min-w-0 flex flex-col justify-end">
                <div className="text-xs font-medium text-neutral-300 truncate mb-1">{art.name}</div>
                <div className="text-[10px] font-mono text-neutral-600 uppercase flex items-center justify-between">
                    <span>{art.type}</span>
                    <span className="opacity-50">|</span>
                    <span>{art.size}</span>
                </div>
            </div>
            {/* Tag overlay on hover */}
            <div className="absolute inset-x-0 bottom-0 p-2 opacity-0 group-hover:opacity-100 transition-opacity bg-neutral-900/95 border-t border-neutral-800 rounded-b-xl backdrop-blur-sm pointer-events-none">
                <div className="flex flex-wrap gap-1 justify-center">
                    {art.tags.slice(0, 3).map(t => (
                        <span key={t} className="text-[9px] bg-neutral-800 px-1.5 py-0.5 rounded text-neutral-400">{t}</span>
                    ))}
                </div>
            </div>
        </div>
    );
};

export const FileSystemExplorer: React.FC<{
    artifacts: Artifact[];
    title?: string;
    onSelectArtifact?: (art: Artifact) => void;
    onContextMenu?: (e: React.MouseEvent, type: 'artifact' | 'stack', data: any) => void;
    selectedIds?: Set<string>;
    onToggleSelection?: (id: string) => void;
}> = ({ artifacts, title = "File System", onSelectArtifact, onContextMenu, selectedIds = new Set(), onToggleSelection }) => {
    // 1. Build Virtual Tree
    const root = useMemo(() => buildVirtualFileSystem(artifacts), [artifacts]);

    // 2. State
    const [currentFolder, setCurrentFolder] = useState<FileSystemNode>(root);
    const [expandedPaths, setExpandedPaths] = useState<Set<string>>(new Set(['/']));
    const [searchQuery, setSearchQuery] = useState('');
    const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
    const [sortBy, setSortBy] = useState<'name' | 'size' | 'date'>('name');

    // 3. Navigation
    const handleToggle = (node: FileSystemNode) => {
        const next = new Set(expandedPaths);
        if (next.has(node.path)) next.delete(node.path);
        else next.add(node.path);
        setExpandedPaths(next);
    };

    const navigateTo = (node: FileSystemNode) => {
        if (node.type === 'folder') {
            setCurrentFolder(node);
            // Ensure path to this folder is expanded in tree
            const parts = node.path.split('/').filter(Boolean);
            const nextExpanded = new Set(expandedPaths);
            let p = '';
            parts.forEach(part => {
                p += `/${part}`;
                nextExpanded.add(p);
            });
            setExpandedPaths(nextExpanded);
        } else {
             if (onSelectArtifact && node.artifact) onSelectArtifact(node.artifact);
        }
    };

    const handleBreadcrumbClick = (index: number) => {
        if (index === -1) {
            navigateTo(root);
            return;
        }
        // Reconstruct path to navigate up
        const parts = currentFolder.path.split('/').filter(Boolean).slice(0, index + 1);
        let target = root;
        for (const part of parts) {
            const next = target.children?.find(c => c.name === part);
            if (next) target = next;
        }
        navigateTo(target);
    };

    const handleNavigateUp = () => {
        const parts = currentFolder.path.split('/').filter(Boolean);
        if (parts.length === 0) return; // At root

        handleBreadcrumbClick(parts.length - 2);
    };

    // Filter contents for main view
    const folderContents = useMemo(() => {
        let contents = currentFolder.children || [];
        if (searchQuery) {
            contents = contents.filter(c => c.name.toLowerCase().includes(searchQuery.toLowerCase()));
        }

        // Sorting
        return [...contents].sort((a, b) => {
            if (a.type !== b.type) return a.type === 'folder' ? -1 : 1; // Folders always first

            if (sortBy === 'name') return a.name.localeCompare(b.name);
            if (sortBy === 'size') {
                const sizeA = a.artifact ? parseBytes(a.artifact.size) : 0;
                const sizeB = b.artifact ? parseBytes(b.artifact.size) : 0;
                return sizeB - sizeA;
            }
            if (sortBy === 'date') {
                const dateA = a.artifact ? a.artifact.updatedAt : 0;
                const dateB = b.artifact ? b.artifact.updatedAt : 0;
                return dateB - dateA;
            }
            return 0;
        });

    }, [currentFolder, searchQuery, sortBy]);

    const breadcrumbs = currentFolder.path.split('/').filter(Boolean);

    return (
        <div className="flex h-full w-full bg-neutral-950 text-neutral-400 overflow-hidden animate-in fade-in duration-300">
            {/* SIDEBAR: Directory Tree */}
            <div className="w-64 flex flex-col border-r border-neutral-900 bg-neutral-925/30 shrink-0">
                <div className="h-10 flex items-center px-4 border-b border-neutral-900 shrink-0">
                    <span className="text-xs font-semibold uppercase tracking-wider text-neutral-500">{title}</span>
                </div>
                {/*
                   Crucial Feature: "Scroll left and right when hovering"
                   overflow-x-hidden by default, overflow-x-auto on hover
                */}
                <div className="flex-1 overflow-y-auto overflow-x-hidden hover:overflow-x-auto py-2 group/tree">
                    <div className="min-w-fit pr-4">
                        {root.children?.map(child => (
                            <TreeNode
                                key={child.id}
                                node={child}
                                level={0}
                                expandedPaths={expandedPaths}
                                selectedPath={currentFolder.path}
                                onToggle={handleToggle}
                                onSelect={navigateTo}
                            />
                        ))}
                    </div>
                </div>

                {/* Tree Stats Footer */}
                <div className="p-3 border-t border-neutral-900 text-[10px] text-neutral-600 font-mono flex justify-between">
                    <span>{artifacts.length} Objects</span>
                    <span>{Math.round(artifacts.reduce((acc, a) => acc + parseBytes(a.size), 0) / 1024 / 1024)} MB</span>
                </div>
            </div>

            {/* MAIN CONTENT: File Browser */}
            <div className="flex-1 flex flex-col min-w-0 bg-neutral-950">
                {/* Toolbar / Breadcrumbs */}
                <div className="h-12 border-b border-neutral-900 flex items-center justify-between px-4 shrink-0">
                    <div className="flex items-center space-x-1 text-sm overflow-hidden mask-linear-fade pr-4">
                        {/* Back Button */}
                        <button
                            onClick={handleNavigateUp}
                            disabled={breadcrumbs.length === 0}
                            className={`p-1 mr-1 rounded hover:bg-neutral-900 transition-colors ${breadcrumbs.length === 0 ? 'text-neutral-800 cursor-default' : 'text-neutral-500 hover:text-neutral-200'}`}
                            title="Go Up"
                        >
                            <ArrowLeft className="w-4 h-4" />
                        </button>

                        <div className="h-4 w-px bg-neutral-800 mx-1" />

                        <button
                            onClick={() => handleBreadcrumbClick(-1)}
                            className={`p-1 rounded hover:bg-neutral-900 transition-colors ${breadcrumbs.length === 0 ? 'text-neutral-200' : 'text-neutral-500'}`}
                        >
                            <Home className="w-4 h-4" />
                        </button>
                        {breadcrumbs.map((part, i) => (
                            <React.Fragment key={i}>
                                <ChevronRight className="w-3 h-3 text-neutral-700 shrink-0" />
                                <button
                                    onClick={() => handleBreadcrumbClick(i)}
                                    className={`
                                        px-2 py-0.5 rounded transition-colors whitespace-nowrap
                                        ${i === breadcrumbs.length - 1 ? 'bg-neutral-900 text-neutral-200 font-medium' : 'text-neutral-500 hover:text-neutral-300 hover:bg-neutral-900'}
                                    `}
                                >
                                    {part}
                                </button>
                            </React.Fragment>
                        ))}
                    </div>

                    <div className="flex items-center space-x-2 pl-2 border-l border-neutral-900 ml-2">
                        {/* SORTING BUTTONS */}
                         <div className="flex bg-neutral-900 rounded border border-neutral-800 p-0.5 mr-2">
                            <button
                                onClick={() => setSortBy('name')}
                                className={`p-1 rounded ${sortBy === 'name' ? 'bg-neutral-800 text-neutral-200 shadow-sm' : 'text-neutral-500 hover:text-neutral-300'}`}
                                title="Sort by Name"
                            >
                                <ArrowDownAZ className="w-3.5 h-3.5" />
                            </button>
                            <button
                                onClick={() => setSortBy('size')}
                                className={`p-1 rounded ${sortBy === 'size' ? 'bg-neutral-800 text-neutral-200 shadow-sm' : 'text-neutral-500 hover:text-neutral-300'}`}
                                title="Sort by Size"
                            >
                                <SizeIcon className="w-3.5 h-3.5" />
                            </button>
                            <button
                                onClick={() => setSortBy('date')}
                                className={`p-1 rounded ${sortBy === 'date' ? 'bg-neutral-800 text-neutral-200 shadow-sm' : 'text-neutral-500 hover:text-neutral-300'}`}
                                title="Sort by Date"
                            >
                                <Calendar className="w-3.5 h-3.5" />
                            </button>
                        </div>

                         <div className="relative group">
                            <Search className="absolute left-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-neutral-600 group-focus-within:text-neutral-400" />
                            <input
                                type="text"
                                placeholder="Filter folder..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="w-32 focus:w-48 transition-all bg-neutral-900 border border-neutral-800 rounded h-7 pl-7 text-xs text-neutral-300 focus:outline-none focus:border-neutral-600 placeholder-neutral-700"
                            />
                        </div>
                        <div className="flex bg-neutral-900 rounded border border-neutral-800 p-0.5">
                            <button
                                onClick={() => setViewMode('grid')}
                                className={`p-1 rounded ${viewMode === 'grid' ? 'bg-neutral-800 text-neutral-200 shadow-sm' : 'text-neutral-500 hover:text-neutral-300'}`}
                            >
                                <Grid className="w-3.5 h-3.5" />
                            </button>
                            <button
                                onClick={() => setViewMode('list')}
                                className={`p-1 rounded ${viewMode === 'list' ? 'bg-neutral-800 text-neutral-200 shadow-sm' : 'text-neutral-500 hover:text-neutral-300'}`}
                            >
                                <ListIcon className="w-3.5 h-3.5" />
                            </button>
                        </div>
                    </div>
                </div>

                {/* Content Grid/List */}
                <div className="flex-1 overflow-y-auto p-4" onClick={() => { /* Deselect logic handled by app or buttons */ }}>
                    {folderContents.length === 0 ? (
                         <div className="h-full flex flex-col items-center justify-center opacity-40">
                             <FolderOpen className="w-12 h-12 text-neutral-700 mb-2" strokeWidth={1} />
                             <span className="text-sm text-neutral-500">Folder is empty</span>
                         </div>
                    ) : (
                        <div className={`
                            ${viewMode === 'grid' ? 'grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3' : 'flex flex-col space-y-1'}
                        `}>
                            {folderContents.map(node => (
                                viewMode === 'grid' ? (
                                    <FileItem
                                        key={node.id}
                                        node={node}
                                        selected={node.artifact ? selectedIds.has(node.artifact.id) : false}
                                        onClick={() => navigateTo(node)}
                                        onToggleSelect={() => node.artifact && onToggleSelection && onToggleSelection(node.artifact.id)}
                                        onContextMenu={(e) => {
                                            if (node.artifact && onContextMenu) {
                                                e.preventDefault();
                                                e.stopPropagation();
                                                onContextMenu(e, 'artifact', node.artifact);
                                            }
                                        }}
                                    />
                                ) : (
                                    <UiRow
                                        key={node.id}
                                        selected={node.artifact ? selectedIds.has(node.artifact.id) : false}
                                        onClick={() => navigateTo(node)}
                                        onContextMenu={(e) => {
                                             if (node.artifact && onContextMenu) {
                                                e.preventDefault();
                                                e.stopPropagation();
                                                onContextMenu(e as any, 'artifact', node.artifact);
                                            }
                                        }}
                                        className="group !py-1.5"
                                    >
                                        <div className="flex items-center w-full text-sm">
                                            {/* List Checkbox */}
                                            {node.artifact && (
                                                <button
                                                    onClick={(e) => { e.stopPropagation(); onToggleSelection && onToggleSelection(node.artifact!.id); }}
                                                    className={`
                                                        w-4 h-4 rounded border mr-3 flex items-center justify-center transition-colors
                                                        ${selectedIds.has(node.artifact.id)
                                                            ? 'bg-indigo-500 border-indigo-500 text-white'
                                                            : 'border-neutral-700 hover:border-neutral-500 bg-transparent text-transparent'
                                                        }
                                                    `}
                                                >
                                                    <CheckCircle2 className="w-3 h-3" />
                                                </button>
                                            )}

                                            {node.type === 'folder' ? <Folder className="w-4 h-4 text-neutral-600 mr-3" /> : <File className="w-4 h-4 text-neutral-500 mr-3" />}
                                            <span className="flex-1 truncate text-neutral-300">{node.name}</span>

                                            {/* List Columns for Details */}
                                            {node.artifact && (
                                                <div className="flex items-center space-x-6 text-xs text-neutral-600 font-mono w-64 justify-end">
                                                    <span className="w-20 text-right truncate">{new Date(node.artifact.updatedAt).toLocaleDateString()}</span>
                                                    <span className="w-16 text-right uppercase">{node.artifact.type}</span>
                                                    <span className="w-16 text-right">{node.artifact.size}</span>
                                                </div>
                                            )}
                                            {node.type === 'folder' && (
                                                <span className="text-xs text-neutral-600 font-mono w-64 text-right">
                                                    {node.meta?.count} items
                                                </span>
                                            )}
                                        </div>
                                    </UiRow>
                                )
                            ))}
                        </div>
                    )}
                </div>

                {/* Status Bar */}
                <div className="h-6 bg-neutral-900 border-t border-neutral-800 flex items-center px-4 justify-between text-[9px] text-neutral-500 select-none">
                     <div className="flex items-center space-x-4">
                         <span>path: {currentFolder.path}</span>
                         <span>selected: {selectedIds.size}</span>
                     </div>
                     <div className="flex items-center space-x-2">
                        <HardDrive className="w-3 h-3" />
                        <span>Ready</span>
                     </div>
                </div>
            </div>
        </div>
    );
};
