'use client';

import React, {
  createContext,
  useContext,
  useState,
  useCallback,
  useEffect,
  useRef,
} from 'react';

/**
 * Toast notification system.
 * Provider + hook, bottom-left stack, auto-dismiss 4s.
 *
 * Setup: Wrap layout with <ToastProvider>
 * Usage: const toast = useToast();
 *        toast.success('Deployed');
 *        toast.error('Connection failed');
 *        toast.info('Polling paused');
 */

type ToastType = 'success' | 'error' | 'warning' | 'info';

interface Toast {
  id: string;
  message: string;
  type: ToastType;
  duration: number;
}

interface ToastContextValue {
  success: (message: string, duration?: number) => void;
  error: (message: string, duration?: number) => void;
  warning: (message: string, duration?: number) => void;
  info: (message: string, duration?: number) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

const DEFAULT_DURATION = 4000;
const MAX_TOASTS = 5;

let toastId = 0;

const typeStyles: Record<ToastType, string> = {
  success: 'border-l-[var(--color-success)]',
  error:   'border-l-[var(--color-danger)]',
  warning: 'border-l-[var(--color-warning)]',
  info:    'border-l-[var(--color-info)]',
};

const typeIcons: Record<ToastType, string> = {
  success: '\u2713',
  error:   '\u2717',
  warning: '\u26A0',
  info:    '\u2139',
};

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback((type: ToastType, message: string, duration = DEFAULT_DURATION) => {
    const id = `toast-${++toastId}`;
    setToasts((prev) => [...prev.slice(-(MAX_TOASTS - 1)), { id, message, type, duration }]);
  }, []);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const value: ToastContextValue = {
    success: (msg, dur) => addToast('success', msg, dur),
    error: (msg, dur) => addToast('error', msg, dur),
    warning: (msg, dur) => addToast('warning', msg, dur),
    info: (msg, dur) => addToast('info', msg, dur),
  };

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div
        className="fixed bottom-4 left-4 flex flex-col-reverse gap-2 pointer-events-none"
        style={{ zIndex: 'var(--z-toast)' } as React.CSSProperties}
      >
        {toasts.map((toast) => (
          <ToastItem key={toast.id} toast={toast} onDismiss={removeToast} />
        ))}
      </div>
    </ToastContext.Provider>
  );
}

function ToastItem({ toast, onDismiss }: { toast: Toast; onDismiss: (id: string) => void }) {
  const timerRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  useEffect(() => {
    timerRef.current = setTimeout(() => onDismiss(toast.id), toast.duration);
    return () => clearTimeout(timerRef.current);
  }, [toast.id, toast.duration, onDismiss]);

  return (
    <div
      className={`
        pointer-events-auto
        flex items-start gap-3 min-w-[280px] max-w-sm
        px-4 py-3 rounded-[var(--radius)]
        bg-[var(--color-elevated)] border border-[var(--color-border)]
        border-l-4 ${typeStyles[toast.type]}
        shadow-lg
        animate-[slideIn_0.2s_ease-out]
      `}
      role="alert"
    >
      <span className="text-sm mt-0.5 shrink-0">{typeIcons[toast.type]}</span>
      <p className="text-sm text-[var(--color-text)] flex-1">{toast.message}</p>
      <button
        onClick={() => onDismiss(toast.id)}
        className="text-[var(--color-text-muted)] hover:text-[var(--color-text)] text-xs ml-2 shrink-0"
        aria-label="Dismiss"
      >
        \u2715
      </button>
    </div>
  );
}

export function useToast(): ToastContextValue {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used within <ToastProvider>');
  return ctx;
}
