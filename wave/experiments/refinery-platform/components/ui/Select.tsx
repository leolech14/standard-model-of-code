'use client';

import React from 'react';

/**
 * Styled native <select> with glass-card appearance.
 * Native <select> for mobile-friendly UX -- no custom dropdown to fight with.
 *
 * Usage:
 *   <Select
 *     value={tier}
 *     onChange={setTier}
 *     options={[
 *       { value: 'T1', label: 'Tier 1' },
 *       { value: 'T2', label: 'Tier 2' },
 *     ]}
 *   />
 */

interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
}

interface SelectProps {
  value: string;
  onChange: (value: string) => void;
  options: SelectOption[];
  placeholder?: string;
  disabled?: boolean;
  className?: string;
  /** Label shown above the select */
  label?: string;
}

export function Select({
  value,
  onChange,
  options,
  placeholder,
  disabled = false,
  className = '',
  label,
}: SelectProps) {
  return (
    <div className={className}>
      {label && (
        <label className="block text-xs font-medium text-[var(--color-text-muted)] mb-1">
          {label}
        </label>
      )}
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        className={`
          w-full px-3 py-2 text-sm rounded-[var(--radius)]
          bg-[var(--color-surface)] text-[var(--color-text)]
          border border-[var(--color-border)]
          focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] focus:border-transparent
          disabled:opacity-50 disabled:cursor-not-allowed
          transition-colors
          appearance-none
          bg-[url('data:image/svg+xml;charset=utf-8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2212%22%20height%3D%2212%22%20fill%3D%22%23888%22%20viewBox%3D%220%200%2012%2012%22%3E%3Cpath%20d%3D%22M6%208L1%203h10z%22%2F%3E%3C%2Fsvg%3E')]
          bg-no-repeat bg-[right_0.75rem_center] bg-[length:12px]
          pr-8
        `}
      >
        {placeholder && (
          <option value="" disabled>
            {placeholder}
          </option>
        )}
        {options.map((opt) => (
          <option key={opt.value} value={opt.value} disabled={opt.disabled}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
}
