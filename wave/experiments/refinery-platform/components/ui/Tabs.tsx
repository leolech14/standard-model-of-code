'use client';

import React, { useState, useRef, useCallback, KeyboardEvent } from 'react';

/**
 * Horizontal tab bar with ARIA tablist, keyboard arrow navigation.
 *
 * Usage:
 *   <Tabs
 *     tabs={['Overview', 'Services', 'Topology']}
 *     active={activeTab}
 *     onChange={setActiveTab}
 *   />
 */

interface TabsProps {
  tabs: string[];
  active: number;
  onChange: (index: number) => void;
  /** Optional className for the tab bar container */
  className?: string;
}

export function Tabs({ tabs, active, onChange, className = '' }: TabsProps) {
  const tabRefs = useRef<(HTMLButtonElement | null)[]>([]);

  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLDivElement>) => {
      let next = active;
      if (e.key === 'ArrowRight') next = (active + 1) % tabs.length;
      else if (e.key === 'ArrowLeft') next = (active - 1 + tabs.length) % tabs.length;
      else if (e.key === 'Home') next = 0;
      else if (e.key === 'End') next = tabs.length - 1;
      else return;

      e.preventDefault();
      onChange(next);
      tabRefs.current[next]?.focus();
    },
    [active, tabs.length, onChange]
  );

  return (
    <div
      role="tablist"
      aria-orientation="horizontal"
      className={`flex gap-1 border-b border-[var(--color-border)] ${className}`}
      onKeyDown={handleKeyDown}
    >
      {tabs.map((label, i) => (
        <button
          key={label}
          ref={(el) => { tabRefs.current[i] = el; }}
          role="tab"
          aria-selected={active === i}
          tabIndex={active === i ? 0 : -1}
          onClick={() => onChange(i)}
          className={`
            px-3 py-2 text-sm font-medium transition-colors relative
            focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent)]
            ${active === i
              ? 'text-[var(--color-accent)]'
              : 'text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)]'
            }
          `}
        >
          {label}
          {active === i && (
            <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-[var(--color-accent)]" />
          )}
        </button>
      ))}
    </div>
  );
}

/**
 * Wrapper for tab panels -- only renders active panel.
 * Pairs with <Tabs> for lazy-load tab content.
 */
interface TabPanelProps {
  active: number;
  index: number;
  children: React.ReactNode;
}

export function TabPanel({ active, index, children }: TabPanelProps) {
  if (active !== index) return null;

  return (
    <div role="tabpanel" tabIndex={0}>
      {children}
    </div>
  );
}
