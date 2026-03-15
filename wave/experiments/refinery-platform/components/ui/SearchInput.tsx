'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';

/**
 * Debounced search input with search icon.
 *
 * Usage:
 *   <SearchInput
 *     value={query}
 *     onChange={setQuery}
 *     placeholder="Search memories..."
 *     debounce={300}
 *   />
 */

interface SearchInputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  /** Debounce delay in ms. Default 300. Set 0 for immediate. */
  debounce?: number;
  disabled?: boolean;
  className?: string;
}

export function SearchInput({
  value,
  onChange,
  placeholder = 'Search...',
  debounce = 300,
  disabled = false,
  className = '',
}: SearchInputProps) {
  const [internal, setInternal] = useState(value);
  const timerRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  // Sync external value changes
  useEffect(() => {
    setInternal(value);
  }, [value]);

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const val = e.target.value;
      setInternal(val);

      if (debounce <= 0) {
        onChange(val);
        return;
      }

      clearTimeout(timerRef.current);
      timerRef.current = setTimeout(() => onChange(val), debounce);
    },
    [onChange, debounce]
  );

  // Cleanup timer on unmount
  useEffect(() => () => clearTimeout(timerRef.current), []);

  return (
    <div className={`relative ${className}`}>
      {/* Search icon */}
      <svg
        className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--color-text-muted)]"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        strokeWidth={2}
      >
        <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
      <input
        type="text"
        value={internal}
        onChange={handleChange}
        placeholder={placeholder}
        disabled={disabled}
        className={`
          w-full pl-9 pr-3 py-2 text-sm rounded-[var(--radius)]
          bg-[var(--color-surface)] text-[var(--color-text)]
          border border-[var(--color-border)]
          placeholder:text-[var(--color-text-muted)]
          focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] focus:border-transparent
          disabled:opacity-50 disabled:cursor-not-allowed
          transition-colors
        `}
      />
      {/* Clear button */}
      {internal && (
        <button
          onClick={() => {
            setInternal('');
            onChange('');
          }}
          className="absolute right-2 top-1/2 -translate-y-1/2 text-[var(--color-text-muted)] hover:text-[var(--color-text)] text-xs"
          aria-label="Clear search"
        >
          \u2715
        </button>
      )}
    </div>
  );
}
