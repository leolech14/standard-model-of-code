'use client';

import React, { createContext, useContext } from 'react';
import { useTheme, type UseThemeReturn } from '@/lib/useTheme';

/**
 * ThemeProvider -- exposes the theme machine to the component tree.
 *
 * Wrap in layout.tsx. Any component can then:
 *   const { mode, resolved, setMode, toggle } = useThemeContext();
 *
 * The actual theme switching happens in CSS via data-theme attribute.
 * This context just provides the controls.
 */

const ThemeContext = createContext<UseThemeReturn | null>(null);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const theme = useTheme();
  return (
    <ThemeContext.Provider value={theme}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useThemeContext(): UseThemeReturn {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error('useThemeContext must be used within <ThemeProvider>');
  return ctx;
}
