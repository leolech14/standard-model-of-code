'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  Database,
  Search,
  Activity,
  Settings,
  Box
} from 'lucide-react';

const NAV_ITEMS = [
  { id: '/', label: 'Overview', icon: LayoutDashboard },
  { id: '/projects', label: 'Projects', icon: Database },
  { id: '/search', label: 'Search', icon: Search },
  { id: '/activity', label: 'Activity', icon: Activity },
  { id: '/chunks', label: 'Chunks', icon: Box },
  { id: '/settings', label: 'Settings', icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-56 border-r border-neutral-800 bg-neutral-900/30 flex flex-col">
      {/* Logo */}
      <div className="h-14 border-b border-neutral-800 flex items-center px-4">
        <div className="w-7 h-7 rounded bg-emerald-500 flex items-center justify-center text-black font-bold text-sm">
          R
        </div>
        <span className="ml-2 font-semibold text-sm">Refinery</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3 space-y-1">
        {NAV_ITEMS.map(item => {
          const Icon = item.icon;
          const isActive = pathname === item.id;

          return (
            <Link
              key={item.id}
              href={item.id}
              className={`
                flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium
                transition-colors duration-150
                ${isActive
                  ? 'bg-neutral-800 text-white'
                  : 'text-neutral-400 hover:text-neutral-200 hover:bg-neutral-800/50'
                }
              `}
            >
              <Icon className="w-4 h-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-neutral-800">
        <div className="text-xs text-neutral-600">
          <div className="mb-1">Level: <span className="text-emerald-500 font-mono">L7 → L8</span></div>
          <div>Status: <span className="text-emerald-500">Spinoff</span></div>
        </div>
      </div>
    </aside>
  );
}
