'use client';

import { useState, useEffect, useCallback } from 'react';

/**
 * Theme hook -- the brain of the theme machine.
 *
 * Modes:
 *   'light' | 'dark' | 'system'
 *
 * System mode follows prefers-color-scheme and auto-updates on OS toggle.
 * Choice persisted in localStorage. SSR-safe (defaults to dark until hydrated).
 *
 * The hook sets `data-theme` on <html> which triggers the CSS remap
 * in globals.css. No component needs to know about themes -- they just
 * reference semantic tokens and the CSS cascade handles everything.
 */

export type ThemeMode = 'light' | 'dark' | 'system';
export type ResolvedTheme = 'light' | 'dark';

const STORAGE_KEY = 'refinery-theme-mode';

function getSystemTheme(): ResolvedTheme {
  if (typeof window === 'undefined') return 'dark';
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function getSavedMode(): ThemeMode {
  if (typeof window === 'undefined') return 'dark';
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved === 'light' || saved === 'dark' || saved === 'system') return saved;
  } catch { /* noop */ }
  return 'dark';
}

function applyTheme(resolved: ResolvedTheme) {
  if (typeof document === 'undefined') return;
  const root = document.documentElement;
  if (resolved === 'light') {
    root.setAttribute('data-theme', 'light');
  } else {
    root.removeAttribute('data-theme');
  }
}

export interface UseThemeReturn {
  /** Current user preference: light, dark, or system */
  mode: ThemeMode;
  /** Resolved effective theme after system preference */
  resolved: ResolvedTheme;
  /** Set theme mode */
  setMode: (mode: ThemeMode) => void;
  /** Convenience toggle: dark -> light -> system -> dark */
  toggle: () => void;
}

export function useTheme(): UseThemeReturn {
  const [mode, setModeState] = useState<ThemeMode>('dark');
  const [resolved, setResolved] = useState<ResolvedTheme>('dark');

  // Initialize from localStorage on mount
  useEffect(() => {
    const saved = getSavedMode();
    setModeState(saved);
    const effective = saved === 'system' ? getSystemTheme() : saved;
    setResolved(effective);
    applyTheme(effective);
  }, []);

  // Listen for OS theme changes when mode is 'system'
  useEffect(() => {
    if (mode !== 'system') return;

    const mql = window.matchMedia('(prefers-color-scheme: dark)');
    const handler = (e: MediaQueryListEvent) => {
      const effective: ResolvedTheme = e.matches ? 'dark' : 'light';
      setResolved(effective);
      applyTheme(effective);
    };

    mql.addEventListener('change', handler);
    return () => mql.removeEventListener('change', handler);
  }, [mode]);

  const setMode = useCallback((newMode: ThemeMode) => {
    setModeState(newMode);
    try {
      localStorage.setItem(STORAGE_KEY, newMode);
    } catch { /* noop */ }

    const effective = newMode === 'system' ? getSystemTheme() : newMode;
    setResolved(effective);
    applyTheme(effective);
  }, []);

  const toggle = useCallback(() => {
    setMode(mode === 'dark' ? 'light' : mode === 'light' ? 'system' : 'dark');
  }, [mode, setMode]);

  return { mode, resolved, setMode, toggle };
}
