import React, { useState, useEffect, useRef, useLayoutEffect } from 'react';
import { createPortal } from 'react-dom';
import { GripHorizontal, Maximize2 } from 'lucide-react';
import { repository, LayoutState } from '../services/mockData';

interface FloatingPanelProps {
    id: string; // Key for persistence
    title: React.ReactNode;
    defaultRect: LayoutState;
    minWidth?: number;
    minHeight?: number;
    onClose?: () => void;
    children: React.ReactNode;
    className?: string;
    containerRef?: React.RefObject<HTMLDivElement>; // Deprecated but kept for API compatibility
}

export const FloatingPanel: React.FC<FloatingPanelProps> = ({
    id,
    title,
    defaultRect,
    minWidth = 200,
    minHeight = 100,
    onClose,
    children,
    className
}) => {
    // Default to a safe position if no persisted state
    const [rect, setRect] = useState<LayoutState>(defaultRect);
    const [isDragging, setIsDragging] = useState(false);
    const [isResizing, setIsResizing] = useState(false);

    // Drag/Resize Refs
    const startPos = useRef({ x: 0, y: 0 });
    const startRect = useRef<LayoutState>(defaultRect);

    // Load persisted layout on mount
    useLayoutEffect(() => {
        const saved = repository.getLayout(id);
        if (saved) {
            setRect(saved);
        } else {
            setRect(defaultRect);
        }
    }, [id]);

    const save = (r: LayoutState) => {
        repository.saveLayout(id, r);
    };

    // --- Drag Handlers ---
    const handleMouseDownDrag = (e: React.MouseEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(true);
        startPos.current = { x: e.clientX, y: e.clientY };
        startRect.current = rect;
        document.body.style.cursor = 'grabbing';
    };

    const handleMouseDownResize = (e: React.MouseEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsResizing(true);
        startPos.current = { x: e.clientX, y: e.clientY };
        startRect.current = rect;
        document.body.style.cursor = 'nwse-resize';
    };

    useEffect(() => {
        const handleMouseMove = (e: MouseEvent) => {
            if (isDragging) {
                const dx = e.clientX - startPos.current.x;
                const dy = e.clientY - startPos.current.y;

                let newX = startRect.current.x + dx;
                let newY = startRect.current.y + dy;

                // Clamp to Window Viewport
                const maxX = window.innerWidth - rect.w;
                const maxY = window.innerHeight - rect.h;

                // Allow some overhang but keep handle visible
                if (newY < 0) newY = 0;
                if (newY > window.innerHeight - 20) newY = window.innerHeight - 20;
                if (newX < -rect.w + 20) newX = -rect.w + 20;
                if (newX > window.innerWidth - 20) newX = window.innerWidth - 20;

                setRect(prev => ({ ...prev, x: newX, y: newY }));
            }

            if (isResizing) {
                const dx = e.clientX - startPos.current.x;
                const dy = e.clientY - startPos.current.y;

                setRect(prev => ({
                    ...prev,
                    w: Math.max(minWidth, startRect.current.w + dx),
                    h: Math.max(minHeight, startRect.current.h + dy)
                }));
            }
        };

        const handleMouseUp = () => {
            if (isDragging || isResizing) {
                setIsDragging(false);
                setIsResizing(false);
                document.body.style.cursor = '';
                save(rect);
            }
        };

        if (isDragging || isResizing) {
            window.addEventListener('mousemove', handleMouseMove);
            window.addEventListener('mouseup', handleMouseUp);
        }

        return () => {
            window.removeEventListener('mousemove', handleMouseMove);
            window.removeEventListener('mouseup', handleMouseUp);
        };
    }, [isDragging, isResizing, minWidth, minHeight, rect, id]);

    // Use Portal to render into body, allowing full screen movement
    return createPortal(
        <div
            className={`fixed flex flex-col bg-neutral-900/95 border border-neutral-800 backdrop-blur-md shadow-[0_10px_40px_-10px_rgba(0,0,0,0.5)] rounded-lg overflow-hidden animate-in fade-in zoom-in-95 duration-200 z-[100] ${className || ''}`}
            style={{
                left: rect.x,
                top: rect.y,
                width: rect.w,
                height: rect.h,
                boxShadow: isDragging ? '0 20px 50px rgba(0,0,0,0.6)' : undefined,
                transition: isDragging || isResizing ? 'none' : 'box-shadow 0.2s'
            }}
            onMouseDown={(e) => e.stopPropagation()}
            onClick={(e) => e.stopPropagation()}
        >
            {/* Header / Drag Handle */}
            <div
                className={`
                    h-10 border-b border-neutral-800 flex justify-between items-center px-3
                    ${isDragging ? 'cursor-grabbing bg-neutral-800' : 'cursor-grab bg-neutral-900/50 hover:bg-neutral-800/50'}
                    transition-colors select-none flex-shrink-0
                `}
                onMouseDown={handleMouseDownDrag}
            >
                <div className="flex items-center space-x-2 text-neutral-400">
                    <GripHorizontal className="w-4 h-4 opacity-50" />
                    <div className="text-xs font-semibold uppercase tracking-wider truncate max-w-[150px]">{title}</div>
                </div>
                {onClose && (
                    <button
                        onClick={(e) => { e.stopPropagation(); onClose(); }}
                        className="text-neutral-600 hover:text-neutral-300 p-1 rounded hover:bg-neutral-800"
                    >
                        <span className="sr-only">Close</span>
                        <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
                    </button>
                )}
            </div>

            {/* Content Area */}
            <div className="flex-1 overflow-auto min-h-0 relative bg-neutral-900/50">
                {children}
            </div>

            {/* Resize Handle */}
            <div
                className="absolute bottom-0 right-0 w-4 h-4 cursor-nwse-resize z-50 flex items-center justify-center text-neutral-600 hover:text-neutral-400"
                onMouseDown={handleMouseDownResize}
            >
                <Maximize2 className="w-2.5 h-2.5 rotate-90" />
            </div>
        </div>,
        document.body
    );
};
