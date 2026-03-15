'use client';

import React, { useEffect, useRef, useCallback } from 'react';

/**
 * Confirmation dialog with backdrop blur, focus trap.
 *
 * Usage:
 *   <Modal
 *     open={showConfirm}
 *     onClose={() => setShowConfirm(false)}
 *     title="Confirm Restart"
 *   >
 *     <p>This will restart the voice service.</p>
 *     <Modal.Actions>
 *       <button onClick={() => setShowConfirm(false)}>Cancel</button>
 *       <ActionButton onClick={handleRestart}>Restart</ActionButton>
 *     </Modal.Actions>
 *   </Modal>
 */

interface ModalProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  /** Max width class. Default 'max-w-md' */
  maxWidth?: string;
}

export function Modal({
  open,
  onClose,
  title,
  children,
  maxWidth = 'max-w-md',
}: ModalProps) {
  const dialogRef = useRef<HTMLDivElement>(null);

  // Trap focus and close on Escape
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
        return;
      }

      if (e.key === 'Tab' && dialogRef.current) {
        const focusable = dialogRef.current.querySelectorAll<HTMLElement>(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        if (focusable.length === 0) return;

        const first = focusable[0];
        const last = focusable[focusable.length - 1];

        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    },
    [onClose]
  );

  useEffect(() => {
    if (!open) return;
    document.addEventListener('keydown', handleKeyDown);
    // Focus first focusable element
    const timer = setTimeout(() => {
      const first = dialogRef.current?.querySelector<HTMLElement>(
        'button, [href], input, select, textarea'
      );
      first?.focus();
    }, 50);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      clearTimeout(timer);
    };
  }, [open, handleKeyDown]);

  // Lock body scroll
  useEffect(() => {
    if (open) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => { document.body.style.overflow = ''; };
  }, [open]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 flex items-center justify-center p-4"
      style={{ zIndex: 'var(--z-modal-backdrop)' } as React.CSSProperties}
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
        aria-hidden
      />

      {/* Dialog */}
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-label={title}
        className={`
          relative ${maxWidth} w-full
          bg-[var(--color-elevated)] border border-[var(--color-border)]
          rounded-[var(--radius-lg)] shadow-xl
          p-6
        `}
        style={{ zIndex: 'var(--z-modal)' } as React.CSSProperties}
      >
        {title && (
          <h2 className="text-base font-semibold text-[var(--color-text)] mb-4">
            {title}
          </h2>
        )}
        <div className="text-sm text-[var(--color-text-secondary)]">
          {children}
        </div>
      </div>
    </div>
  );
}

/** Action bar at the bottom of a Modal */
Modal.Actions = function ModalActions({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex justify-end gap-2 mt-6 pt-4 border-t border-[var(--color-border)]">
      {children}
    </div>
  );
};
