'use client';

import React from 'react';

/**
 * SVG arc gauge for CPU/mem/disk percentages.
 * Animated fill, color shifts by threshold.
 *
 * Usage:
 *   <Gauge value={72} label="CPU" />
 *   <Gauge value={91} label="Disk" thresholds={{ warn: 80, danger: 95 }} />
 */

interface GaugeProps {
  /** Percentage 0-100 */
  value: number;
  /** Label below the value */
  label: string;
  /** Size in pixels. Default 80 */
  size?: number;
  /** Color thresholds. Default: warn=70, danger=90 */
  thresholds?: { warn: number; danger: number };
  className?: string;
}

export function Gauge({
  value,
  label,
  size = 80,
  thresholds = { warn: 70, danger: 90 },
  className = '',
}: GaugeProps) {
  const clamped = Math.max(0, Math.min(100, value));
  const strokeWidth = 6;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference * (1 - clamped / 100);

  // Color based on thresholds
  const color =
    clamped >= thresholds.danger
      ? 'var(--color-danger)'
      : clamped >= thresholds.warn
      ? 'var(--color-warning)'
      : 'var(--color-accent)';

  return (
    <div className={`inline-flex flex-col items-center gap-1 ${className}`}>
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        className="-rotate-90"
      >
        {/* Background track */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="var(--neutral-3)"
          strokeWidth={strokeWidth}
        />
        {/* Filled arc */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          style={{
            transition: `stroke-dashoffset var(--duration-slow) var(--ease-default), stroke var(--duration-base) var(--ease-default)`,
          }}
        />
      </svg>
      {/* Center value overlay */}
      <div
        className="absolute flex flex-col items-center justify-center"
        style={{ width: size, height: size }}
      >
        <span
          className="font-semibold text-[var(--color-text)]"
          style={{ fontSize: size * 0.22 }}
        >
          {Math.round(clamped)}%
        </span>
      </div>
      <span className="text-xs text-[var(--color-text-muted)]">{label}</span>
    </div>
  );
}
