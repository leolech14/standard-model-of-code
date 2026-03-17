'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  Server,
  Mic,
  Brain,
  Zap,
  MessageSquare,
  TrendingUp,
  Wallet,
  Database,
  Wrench,
  Box,
  HardDrive,
  Mail,
  Settings,
  Inbox,
  BookOpen,
  FileText,
  FolderTree,
  ChevronRight,
  Globe,
} from 'lucide-react';

/**
 * Sidebar with 5 navigation groups + 14 items.
 * Groups collapsible via localStorage. Active state uses pathname.startsWith().
 *
 * Group structure from the plan:
 *   Overview (/)
 *   OPERATIONS:      System, Voice, LLM, Automations
 *   COMMUNICATIONS:  Comms
 *   FINANCE:         Trading, Finance
 *   INTELLIGENCE:    Memory, Tools
 *   PLATFORM:        Projects, Chunks, Infrastructure, Google, Settings
 */

interface NavItem {
  path: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
}

interface NavGroup {
  label: string;
  items: NavItem[];
}

const NAV_GROUPS: NavGroup[] = [
  {
    label: 'OPERATIONS',
    items: [
      { path: '/system', label: 'System', icon: Server },
      { path: '/voice', label: 'Voice', icon: Mic },
      { path: '/llm', label: 'LLM', icon: Brain },
      { path: '/automations', label: 'Automations', icon: Zap },
    ],
  },
  {
    label: 'COMMUNICATIONS',
    items: [
      { path: '/comms', label: 'Comms', icon: MessageSquare },
    ],
  },
  {
    label: 'FINANCE',
    items: [
      { path: '/trading', label: 'Trading', icon: TrendingUp },
      { path: '/finance', label: 'Finance', icon: Wallet },
    ],
  },
  {
    label: 'INTELLIGENCE',
    items: [
      { path: '/journal', label: 'Journal', icon: BookOpen },
      { path: '/docs', label: 'Knowledge Base', icon: FileText },
      { path: '/inbox', label: 'Inbox', icon: Inbox },
      { path: '/memory', label: 'Memory', icon: Database },
      { path: '/tools', label: 'Tools', icon: Wrench },
    ],
  },
  {
    label: 'PLATFORM',
    items: [
      { path: '/projects', label: 'Projects', icon: Box },
      { path: '/explorer', label: 'Explorer', icon: FolderTree },
      { path: '/ecosystem', label: 'Ecosystem', icon: Globe },
      { path: '/chunks', label: 'Chunks', icon: Box },
      { path: '/infra', label: 'Infrastructure', icon: HardDrive },
      { path: '/google', label: 'Google', icon: Mail },
      { path: '/settings', label: 'Settings', icon: Settings },
    ],
  },
];

const STORAGE_KEY = 'refinery-sidebar-collapsed';

function loadCollapsed(): Record<string, boolean> {
  if (typeof window === 'undefined') return {};
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
  } catch {
    return {};
  }
}

function saveCollapsed(collapsed: Record<string, boolean>) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(collapsed));
  } catch { /* noop */ }
}

export function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>({});

  // Load persisted state on mount
  useEffect(() => {
    setCollapsed(loadCollapsed());
  }, []);

  const toggleGroup = (label: string) => {
    setCollapsed((prev) => {
      const next = { ...prev, [label]: !prev[label] };
      saveCollapsed(next);
      return next;
    });
  };

  const isActive = (path: string) =>
    path === '/' ? pathname === '/' : pathname.startsWith(path);

  return (
    <aside
      className="flex flex-col border-r border-[var(--color-border)] bg-[var(--color-surface)]"
      style={{ width: 'var(--sidebar-width)' }}
    >
      {/* Logo */}
      <div
        className="border-b border-[var(--color-border)] flex items-center px-4"
        style={{ height: 'var(--header-height)' }}
      >
        <div className="w-7 h-7 rounded-[var(--radius-sm)] bg-[var(--color-accent)] flex items-center justify-center text-[var(--color-accent-text)] font-bold text-sm">
          R
        </div>
        <span className="ml-2 font-semibold text-sm text-[var(--color-text)]">Refinery</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto p-3 space-y-1">
        {/* Overview -- standalone */}
        <Link
          href="/"
          className={`
            flex items-center gap-3 px-3 py-2 rounded-[var(--radius)] text-sm font-medium
            transition-colors
            ${isActive('/')
              ? 'bg-[var(--color-surface-hover)] text-[var(--color-text)]'
              : 'text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-hover)]'
            }
          `}
        >
          <LayoutDashboard className="w-4 h-4" />
          Overview
        </Link>

        {/* Grouped navigation */}
        {NAV_GROUPS.map((group) => {
          const isGroupCollapsed = collapsed[group.label];
          const hasActiveItem = group.items.some((item) => isActive(item.path));

          return (
            <div key={group.label} className="pt-3">
              {/* Group header */}
              <button
                onClick={() => toggleGroup(group.label)}
                className="flex items-center gap-1 w-full px-3 py-1 text-[10px] font-semibold tracking-[var(--tracking-widest)] uppercase text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)] transition-colors"
              >
                <ChevronRight
                  className={`w-3 h-3 transition-transform ${isGroupCollapsed ? '' : 'rotate-90'}`}
                />
                {group.label}
                {hasActiveItem && isGroupCollapsed && (
                  <span className="ml-auto w-1.5 h-1.5 rounded-full bg-[var(--color-accent)]" />
                )}
              </button>

              {/* Items */}
              {!isGroupCollapsed && (
                <div className="mt-1 space-y-0.5">
                  {group.items.map((item) => {
                    const Icon = item.icon;
                    const active = isActive(item.path);

                    return (
                      <Link
                        key={item.path}
                        href={item.path}
                        className={`
                          flex items-center gap-3 px-3 py-1.5 rounded-[var(--radius)] text-sm
                          transition-colors
                          ${active
                            ? 'bg-[var(--color-surface-hover)] text-[var(--color-text)] font-medium'
                            : 'text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-hover)]'
                          }
                        `}
                      >
                        <Icon className="w-4 h-4 shrink-0" />
                        {item.label}
                      </Link>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-[var(--color-border)]">
        <div className="text-xs text-[var(--color-text-muted)]">
          <div className="mb-1">
            Level: <span className="text-[var(--color-accent)] font-mono">L7 &rarr; L8</span>
          </div>
          <div>
            Type: <span className="text-[var(--color-accent)]">Spinoff</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
