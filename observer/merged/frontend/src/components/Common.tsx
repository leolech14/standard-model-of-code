import React, { useEffect, useRef, useState } from 'react';
import { Ghost, X, Command, ArrowRight, Search, Keyboard } from 'lucide-react';
import { ContextMenuRequest } from '../types';

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

// --- NEW COMPONENTS ---

export interface ToastMessage {
    id: string;
    title: string;
    description?: string;
    type: 'info' | 'error' | 'success' | 'warning';
}

export const ToastContainer: React.FC<{ toasts: ToastMessage[]; onDismiss: (id: string) => void }> = ({ toasts, onDismiss }) => {
    return (
        <div className="fixed bottom-6 right-6 z-[200] flex flex-col items-end space-y-2 pointer-events-none">
            {toasts.map(toast => (
                <div
                    key={toast.id}
                    className={`
                        pointer-events-auto w-80 p-4 rounded bg-neutral-900/95 border border-neutral-800 backdrop-blur shadow-2xl
                        animate-in slide-in-from-right-10 fade-in duration-300 flex items-start group
                    `}
                >
                    <div className={`mt-0.5 w-1.5 h-1.5 rounded-full mr-3 flex-shrink-0 ${toast.type === 'error' ? 'bg-rose-500' : toast.type === 'success' ? 'bg-emerald-500' : toast.type === 'warning' ? 'bg-amber-500' : 'bg-blue-500'}`} />
                    <div className="flex-1 min-w-0">
                        <h4 className="text-sm font-medium text-neutral-200">{toast.title}</h4>
                        {toast.description && <p className="text-xs text-neutral-500 mt-1 truncate">{toast.description}</p>}
                    </div>
                    <button onClick={() => onDismiss(toast.id)} className="text-neutral-600 hover:text-neutral-400 opacity-0 group-hover:opacity-100 transition-opacity">
                        <X className="w-4 h-4" />
                    </button>
                </div>
            ))}
        </div>
    );
};

interface CommandAction {
    id: string;
    label: string;
    shortcut?: string;
    icon?: React.ReactNode;
    perform: () => void;
}

export const CommandPalette: React.FC<{
    open: boolean;
    onClose: () => void;
    actions: CommandAction[]
}> = ({ open, onClose, actions }) => {
    const [query, setQuery] = React.useState('');
    const [selectedIndex, setSelectedIndex] = React.useState(0);
    const inputRef = useRef<HTMLInputElement>(null);

    const filteredActions = actions.filter(action =>
        action.label.toLowerCase().includes(query.toLowerCase())
    );

    useEffect(() => {
        if (open) {
            setQuery('');
            setSelectedIndex(0);
            setTimeout(() => inputRef.current?.focus(), 50);
        }
    }, [open]);

    // Handle arrow navigation
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (!open) return;

            if (e.key === 'ArrowDown') {
                e.preventDefault();
                setSelectedIndex(i => Math.min(i + 1, filteredActions.length - 1));
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                setSelectedIndex(i => Math.max(i - 1, 0));
            } else if (e.key === 'Enter') {
                e.preventDefault();
                if (filteredActions[selectedIndex]) {
                    filteredActions[selectedIndex].perform();
                    onClose();
                }
            } else if (e.key === 'Escape') {
                e.preventDefault();
                onClose();
            }
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [open, filteredActions, selectedIndex, onClose]);

    if (!open) return null;

    return (
        <div className="fixed inset-0 z-[100] bg-black/50 backdrop-blur-[2px] flex items-start justify-center pt-[20vh]" onClick={onClose}>
            <div
                className="w-full max-w-lg bg-neutral-950 border border-neutral-800 rounded-lg shadow-2xl overflow-hidden animate-in zoom-in-95 duration-150"
                onClick={e => e.stopPropagation()}
            >
                <div className="flex items-center px-4 py-3 border-b border-neutral-900">
                    <Command className="w-4 h-4 text-neutral-500 mr-3" />
                    <input
                        ref={inputRef}
                        type="text"
                        value={query}
                        onChange={e => { setQuery(e.target.value); setSelectedIndex(0); }}
                        className="flex-1 bg-transparent border-none focus:ring-0 text-sm text-neutral-200 placeholder-neutral-600 h-6"
                        placeholder="Type a command or search..."
                    />
                    <kbd className="hidden md:inline-flex px-1.5 py-0.5 text-[10px] font-mono text-neutral-600 border border-neutral-800 rounded">ESC</kbd>
                </div>
                <div className="max-h-[300px] overflow-y-auto p-2">
                    {filteredActions.map((action, i) => (
                        <div
                            key={action.id}
                            className={`
                                flex items-center px-3 py-2 rounded cursor-pointer text-sm
                                ${i === selectedIndex ? 'bg-neutral-900 text-neutral-200' : 'text-neutral-500 hover:text-neutral-300 hover:bg-neutral-900/50'}
                            `}
                            onClick={() => { action.perform(); onClose(); }}
                            onMouseEnter={() => setSelectedIndex(i)}
                        >
                            {action.icon && <span className="mr-3 opacity-70">{action.icon}</span>}
                            <span className="flex-1">{action.label}</span>
                            {action.shortcut && <span className="text-[10px] font-mono text-neutral-600">{action.shortcut}</span>}
                            {i === selectedIndex && <ArrowRight className="w-3 h-3 text-neutral-500" />}
                        </div>
                    ))}
                    {filteredActions.length === 0 && (
                        <div className="px-4 py-8 text-center text-xs text-neutral-600">
                            No matching commands found.
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

// --- CONTEXT MENU ---
export interface ContextMenuItem {
    label: string;
    icon?: React.ElementType;
    action: () => void;
    danger?: boolean;
}

export const ContextMenu: React.FC<{
    request: ContextMenuRequest | null;
    items: ContextMenuItem[];
    onClose: () => void;
}> = ({ request, items, onClose }) => {
    const menuRef = useRef<HTMLDivElement>(null);
    const [position, setPosition] = useState({ x: 0, y: 0 });

    useEffect(() => {
        if (request && menuRef.current) {
            const { innerWidth, innerHeight } = window;
            const { offsetWidth, offsetHeight } = menuRef.current;
            let x = request.x;
            let y = request.y;

            if (x + offsetWidth > innerWidth) x = innerWidth - offsetWidth - 8;
            if (y + offsetHeight > innerHeight) y = innerHeight - offsetHeight - 8;

            setPosition({ x, y });
        }
    }, [request]);

    if (!request) return null;

    return (
        <div
            className="fixed inset-0 z-[150]"
            onClick={onClose}
            onContextMenu={(e) => { e.preventDefault(); onClose(); }}
        >
            <div
                ref={menuRef}
                className="absolute bg-neutral-900/95 backdrop-blur border border-neutral-800 rounded-lg shadow-2xl py-1 min-w-[160px] animate-in fade-in zoom-in-95 duration-100 origin-top-left"
                style={{ top: position.y, left: position.x }}
                onClick={(e) => e.stopPropagation()}
            >
                {items.map((item, i) => (
                    <button
                        key={i}
                        className={`
                            w-full text-left px-3 py-2 text-xs flex items-center space-x-3 hover:bg-neutral-800 transition-colors
                            ${item.danger ? 'text-rose-400 hover:text-rose-300' : 'text-neutral-300 hover:text-white'}
                        `}
                        onClick={() => { item.action(); onClose(); }}
                    >
                        {item.icon && <item.icon className="w-3.5 h-3.5 opacity-70" />}
                        <span>{item.label}</span>
                    </button>
                ))}
            </div>
        </div>
    );
};

export const KeyboardShortcuts: React.FC<{ open: boolean; onClose: () => void }> = ({ open, onClose }) => {
    if (!open) return null;

    const shortcuts = [
        { key: 'Cmd+K', desc: 'Command Palette' },
        { key: 'Esc', desc: 'Close Overlay / Back' },
        { key: '?', desc: 'Show Shortcuts' },
        { key: '/', desc: 'Global Search' },
    ];

    return (
        <div className="fixed inset-0 z-[200] bg-black/60 backdrop-blur-sm flex items-center justify-center" onClick={onClose}>
             <div className="bg-neutral-950 border border-neutral-800 p-6 rounded-lg shadow-2xl w-full max-w-sm animate-in zoom-in-95 duration-200" onClick={e => e.stopPropagation()}>
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center space-x-2 text-neutral-200">
                        <Keyboard className="w-5 h-5" />
                        <h3 className="font-semibold">Keyboard Shortcuts</h3>
                    </div>
                    <button onClick={onClose}><X className="w-4 h-4 text-neutral-500 hover:text-white" /></button>
                </div>
                <div className="space-y-3">
                    {shortcuts.map(s => (
                        <div key={s.key} className="flex justify-between items-center text-sm">
                            <span className="text-neutral-400">{s.desc}</span>
                            <kbd className="bg-neutral-900 border border-neutral-800 px-2 py-1 rounded text-neutral-300 font-mono text-xs">{s.key}</kbd>
                        </div>
                    ))}
                </div>
             </div>
        </div>
    );
};
