import React from 'react';
import { Ghost } from 'lucide-react';

/**
 * Shared UI Components for Refinery Platform
 * All components consume parametric tokens from globals.css.
 */

// Clickable capsule/pill component
export const UiLink: React.FC<React.HTMLAttributes<HTMLSpanElement> & { active?: boolean }> = ({
  className,
  children,
  active,
  onClick,
  ...props
}) => {
  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onClick) onClick(e as any);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (onClick && (e.key === 'Enter' || e.key === ' ')) {
      e.preventDefault();
      e.stopPropagation();
      onClick(e as any);
    }
  };

  return (
    <span
      className={`
        inline-flex items-center justify-center px-2 py-0.5 rounded-full text-xs font-medium
        cursor-pointer transition-all duration-200 select-none
        ${active
          ? 'bg-surface text-text shadow-sm'
          : 'text-text-muted hover:text-text-secondary hover:bg-bg focus:outline-none focus-visible:ring-1 focus-visible:ring-border'
        }
        ${className || ''}
      `}
      tabIndex={0}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      role="button"
      {...props}
    >
      {children}
    </span>
  );
};

// Clickable row with subtle tick indicator
export const UiRow: React.FC<React.HTMLAttributes<HTMLDivElement> & { selected?: boolean }> = ({
  className,
  children,
  selected,
  onClick,
  ...props
}) => {
  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onClick) onClick(e as any);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (onClick && (e.key === 'Enter' || e.key === ' ')) {
      e.preventDefault();
      e.stopPropagation();
      onClick(e as any);
    }
  };

  return (
    <div
      className={`
        group relative flex items-center w-full px-3 py-2 cursor-pointer
        transition-colors duration-150 outline-none select-none
        ${selected ? 'bg-bg/50' : 'hover:bg-bg/30'}
        focus-visible:bg-bg/30
        ${className || ''}
      `}
      tabIndex={0}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      role="button"
      {...props}
    >
      {/* Left tick indicator */}
      <div className={`
        absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-4 bg-border-subtle rounded-r-sm
        transition-opacity duration-200
        ${selected ? 'opacity-100' : 'opacity-0 group-hover:opacity-50 group-focus-visible:opacity-50'}
      `} />
      {children}
    </div>
  );
};

// Status badge with glow effects (OKLCH-only)
export const Badge: React.FC<{
  status: 'success' | 'failed' | 'running' | 'idle' | 'warning' | 'info' | 'live' | 'critical' | 'active' | string
}> = ({ status }) => {
  let color = 'bg-elevated';

  if (status === 'success' || status === 'live' || status === 'active') {
    color = 'bg-success/80 shadow-[0_0_8px_-2px_var(--color-success-glow)]';
  }
  if (status === 'failed' || status === 'critical') {
    color = 'bg-danger/80 shadow-[0_0_8px_-2px_var(--color-danger-glow)]';
  }
  if (status === 'running') {
    color = 'bg-info/80 animate-pulse';
  }
  if (status === 'warning') {
    color = 'bg-warning/80';
  }
  if (status === 'idle') {
    color = 'bg-border-subtle';
  }

  return <span className={`w-1.5 h-1.5 rounded-full inline-block ${color}`} />;
};

// Section header with optional action
export const SectionHeader: React.FC<{
  title: string;
  action?: React.ReactNode
}> = ({ title, action }) => (
  <div className="flex items-center justify-between px-4 py-3 border-b border-border mb-2">
    <h3 className="text-xs font-semibold uppercase tracking-wider text-text-muted">
      {title}
    </h3>
    {action}
  </div>
);

// Empty state with ghost icon
export const EmptyState: React.FC<{
  message: string;
  submessage?: string
}> = ({ message, submessage }) => (
  <div className="flex flex-col items-center justify-center py-24 text-center opacity-60">
    <Ghost className="w-8 h-8 text-text-muted mb-4" />
    <p className="text-sm text-text-secondary font-medium">{message}</p>
    {submessage && (
      <p className="text-xs text-text-muted mt-1 max-w-xs">{submessage}</p>
    )}
  </div>
);
