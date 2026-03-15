'use client';

import React from 'react';

/**
 * Pulse placeholder for loading states.
 *
 * Usage:
 *   <Skeleton className="h-4 w-32" />          -- text line
 *   <Skeleton className="h-20 w-full" />        -- card placeholder
 *   <Skeleton className="h-4 w-full" count={3} /> -- multiple lines
 */

interface SkeletonProps {
  className?: string;
  /** Number of skeleton elements to render. Default 1. */
  count?: number;
}

export function Skeleton({ className = 'h-4 w-full', count = 1 }: SkeletonProps) {
  return (
    <>
      {Array.from({ length: count }, (_, i) => (
        <div
          key={i}
          className={`
            animate-pulse rounded-[var(--radius-sm)]
            bg-[var(--neutral-3)]
            ${className}
          `}
        />
      ))}
    </>
  );
}

/**
 * Card-shaped skeleton matching glass-card dimensions.
 */
export function SkeletonCard({ className = '' }: { className?: string }) {
  return (
    <div className={`glass-card rounded-lg p-4 space-y-3 ${className}`}>
      <Skeleton className="h-4 w-1/3" />
      <Skeleton className="h-3 w-full" />
      <Skeleton className="h-3 w-2/3" />
    </div>
  );
}
