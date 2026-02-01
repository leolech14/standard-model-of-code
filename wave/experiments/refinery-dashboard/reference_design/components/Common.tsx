import React from 'react';
import { Ghost } from 'lucide-react';

// Subtle click affordance 1: Capsule Ghost
export const UiLink: React.FC<React.HTMLAttributes<HTMLSpanElement> & { active?: boolean }> = ({ className, children, active, onClick, ...props }) => {
    const handleClick = (e: React.MouseEvent) => {
        e.stopPropagation(); // Prevent bubbling to main canvas (which would close drawer)
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
                inline-flex items-center justify-center px-2 py-0.5 rounded-full text-xs font-medium cursor-pointer transition-all duration-200 select-none
                ${active
                    ? 'bg-neutral-800 text-neutral-200 shadow-sm'
                    : 'text-neutral-500 hover:text-neutral-300 hover:bg-neutral-900 focus:outline-none focus-visible:ring-1 focus-visible:ring-neutral-700'
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

// Subtle click affordance 2: Row Tick
export const UiRow: React.FC<React.HTMLAttributes<HTMLDivElement> & { selected?: boolean }> = ({ className, children, selected, onClick, ...props }) => {
    const handleClick = (e: React.MouseEvent) => {
        e.stopPropagation(); // Prevent bubbling to main canvas
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
                group relative flex items-center w-full px-3 py-2 cursor-pointer transition-colors duration-150 outline-none select-none
                ${selected ? 'bg-neutral-900/50' : 'hover:bg-neutral-900/30'}
                focus-visible:bg-neutral-900/30
                ${className || ''}
            `}
            tabIndex={0}
            onClick={handleClick}
            onKeyDown={handleKeyDown}
            role="button"
            {...props}
        >
            {/* The "Tick" Indicator */}
            <div className={`
                absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-4 bg-neutral-600 rounded-r-sm transition-opacity duration-200
                ${selected ? 'opacity-100' : 'opacity-0 group-hover:opacity-50 group-focus-visible:opacity-50'}
            `} />
            {children}
        </div>
    );
};

export const Badge: React.FC<{ status: 'success' | 'failed' | 'running' | 'idle' | 'warning' | 'info' | string }> = ({ status }) => {
    let color = 'bg-neutral-700';
    if (status === 'success' || status === 'live') color = 'bg-emerald-500/80 shadow-[0_0_8px_-2px_rgba(16,185,129,0.5)]';
    if (status === 'failed' || status === 'critical') color = 'bg-rose-500/80 shadow-[0_0_8px_-2px_rgba(244,63,94,0.5)]';
    if (status === 'running') color = 'bg-blue-500/80 animate-pulse';
    if (status === 'warning') color = 'bg-amber-500/80';
    if (status === 'idle') color = 'bg-neutral-600';

    return <span className={`w-1.5 h-1.5 rounded-full inline-block ${color}`} />;
};

export const SectionHeader: React.FC<{ title: string; action?: React.ReactNode }> = ({ title, action }) => (
    <div className="flex items-center justify-between px-4 py-3 border-b border-neutral-900/50 mb-2">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-neutral-500">{title}</h3>
        {action}
    </div>
);

export const EmptyState: React.FC<{ message: string; submessage?: string }> = ({ message, submessage }) => (
    <div className="flex flex-col items-center justify-center py-24 text-center opacity-60">
        <Ghost className="w-8 h-8 text-neutral-700 mb-4" />
        <p className="text-sm text-neutral-400 font-medium">{message}</p>
        {submessage && <p className="text-xs text-neutral-600 mt-1 max-w-xs">{submessage}</p>}
    </div>
);
