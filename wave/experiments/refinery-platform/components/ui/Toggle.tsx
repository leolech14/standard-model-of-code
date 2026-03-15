'use client';

import React from 'react';

/**
 * Switch toggle for boolean values.
 * Uses role="switch" for accessibility.
 *
 * Usage:
 *   <Toggle
 *     checked={isEcoMode}
 *     onChange={setIsEcoMode}
 *     label="Eco Mode"
 *   />
 */

interface ToggleProps {
  checked: boolean;
  onChange: (value: boolean) => void;
  label?: string;
  disabled?: boolean;
  className?: string;
}

export function Toggle({
  checked,
  onChange,
  label,
  disabled = false,
  className = '',
}: ToggleProps) {
  return (
    <label
      className={`
        inline-flex items-center gap-2 select-none
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        ${className}
      `}
    >
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        disabled={disabled}
        onClick={() => onChange(!checked)}
        className={`
          relative inline-flex h-5 w-9 shrink-0 items-center rounded-full
          border-2 border-transparent transition-colors
          focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--color-bg)]
          ${checked ? 'bg-[var(--color-accent)]' : 'bg-[var(--neutral-4)]'}
        `}
      >
        <span
          className={`
            pointer-events-none inline-block h-3.5 w-3.5 rounded-full
            bg-white shadow-sm transition-transform
            ${checked ? 'translate-x-4' : 'translate-x-0.5'}
          `}
        />
      </button>
      {label && (
        <span className="text-sm text-[var(--color-text-secondary)]">{label}</span>
      )}
    </label>
  );
}
