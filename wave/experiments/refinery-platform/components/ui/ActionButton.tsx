'use client';

import React, { useState } from 'react';
import { Modal } from './Modal';

/**
 * POST/PUT/DELETE button with loading state + optional confirm modal.
 * Follows the plan: ActionButton -> Modal -> API -> Toast
 *
 * Usage:
 *   <ActionButton onClick={handleDeploy} confirm="Deploy to production?">
 *     Deploy
 *   </ActionButton>
 *
 *   <ActionButton onClick={handleRestart} variant="danger" loading={isRestarting}>
 *     Restart
 *   </ActionButton>
 */

type Variant = 'primary' | 'secondary' | 'danger' | 'ghost';

interface ActionButtonProps {
  children: React.ReactNode;
  onClick: () => void | Promise<void>;
  /** If provided, shows a confirmation modal before executing */
  confirm?: string;
  /** Confirmation modal title */
  confirmTitle?: string;
  /** Button variant */
  variant?: Variant;
  /** External loading state (from useMutation) */
  loading?: boolean;
  disabled?: boolean;
  className?: string;
  /** Size */
  size?: 'sm' | 'md';
}

const variantStyles: Record<Variant, string> = {
  primary:   'bg-[var(--color-accent)] text-[var(--color-accent-text)] hover:bg-[var(--color-accent-hover)]',
  secondary: 'bg-[var(--color-surface)] text-[var(--color-text)] border border-[var(--color-border)] hover:bg-[var(--color-surface-hover)]',
  danger:    'bg-[var(--color-danger)] text-white hover:brightness-110',
  ghost:     'bg-transparent text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-hover)] hover:text-[var(--color-text)]',
};

const sizeStyles: Record<'sm' | 'md', string> = {
  sm: 'px-2.5 py-1.5 text-xs',
  md: 'px-4 py-2 text-sm',
};

export function ActionButton({
  children,
  onClick,
  confirm,
  confirmTitle = 'Confirm Action',
  variant = 'primary',
  loading = false,
  disabled = false,
  className = '',
  size = 'md',
}: ActionButtonProps) {
  const [showConfirm, setShowConfirm] = useState(false);
  const [internalLoading, setInternalLoading] = useState(false);

  const isLoading = loading || internalLoading;

  const execute = async () => {
    setShowConfirm(false);
    setInternalLoading(true);
    try {
      await onClick();
    } finally {
      setInternalLoading(false);
    }
  };

  const handleClick = () => {
    if (confirm) {
      setShowConfirm(true);
    } else {
      execute();
    }
  };

  return (
    <>
      <button
        onClick={handleClick}
        disabled={disabled || isLoading}
        className={`
          inline-flex items-center justify-center gap-2
          font-medium rounded-[var(--radius)]
          transition-all
          focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent)]
          disabled:opacity-50 disabled:cursor-not-allowed
          ${variantStyles[variant]}
          ${sizeStyles[size]}
          ${className}
        `}
      >
        {isLoading && (
          <svg
            className="animate-spin h-3.5 w-3.5"
            viewBox="0 0 24 24"
            fill="none"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
            />
          </svg>
        )}
        {children}
      </button>

      {confirm && (
        <Modal
          open={showConfirm}
          onClose={() => setShowConfirm(false)}
          title={confirmTitle}
        >
          <p>{confirm}</p>
          <Modal.Actions>
            <button
              onClick={() => setShowConfirm(false)}
              className={`${sizeStyles.md} rounded-[var(--radius)] ${variantStyles.secondary}`}
            >
              Cancel
            </button>
            <button
              onClick={execute}
              className={`${sizeStyles.md} rounded-[var(--radius)] ${variantStyles[variant === 'ghost' ? 'primary' : variant]}`}
            >
              Confirm
            </button>
          </Modal.Actions>
        </Modal>
      )}
    </>
  );
}
