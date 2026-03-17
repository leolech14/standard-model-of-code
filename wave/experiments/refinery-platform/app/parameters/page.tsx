'use client';

import React, { useState, useCallback, useEffect } from 'react';
import {
  PARAMETERS, DOMAINS, getParamsByDomain,
  type ParameterDef, type ParamDomain,
} from '@/lib/engine/parameters';
import { validateBeauty } from '@/lib/engine/beauty';
import {
  getParam, setParam, resetAll, resetDomain, exportState, importState,
} from '@/lib/engine/runtime';
import {
  RotateCcw, Download, Upload, AlertTriangle, Shield,
} from 'lucide-react';

/* ── Domain Labels ────────────────────────────── */

const DOMAIN_LABELS: Record<ParamDomain, string> = {
  achromatic: 'Achromatic',
  chromatic: 'Chromatic',
  spacing: 'Spacing',
  radius: 'Radius',
  shadow: 'Shadow',
  glass: 'Glass',
  motion: 'Motion',
  coefficient: 'Coefficients',
};

/* ── Slider Component ─────────────────────────── */

function ParamSlider({
  def, value, onChange,
}: {
  def: ParameterDef;
  value: number;
  onChange: (id: string, val: number) => void;
}) {
  const pct = ((value - def.min) / (def.max - def.min)) * 100;

  return (
    <div className="flex items-center gap-3 py-1.5 group">
      <div className="w-36 shrink-0">
        <div className="text-xs text-[var(--color-text-secondary)] font-medium truncate">{def.label}</div>
        <div className="text-[9px] text-[var(--color-text-muted)] font-mono">{def.id}</div>
      </div>
      <div className="flex-1 relative">
        <input
          type="range"
          min={def.min}
          max={def.max}
          step={def.step}
          value={value}
          onChange={(e) => onChange(def.id, parseFloat(e.target.value))}
          className="w-full h-1.5 rounded-full appearance-none cursor-pointer
            bg-[var(--color-surface-hover)]
            [&::-webkit-slider-thumb]:appearance-none
            [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3
            [&::-webkit-slider-thumb]:rounded-full
            [&::-webkit-slider-thumb]:bg-[var(--color-accent)]
            [&::-webkit-slider-thumb]:shadow-sm
            [&::-webkit-slider-thumb]:hover:scale-125
            [&::-webkit-slider-thumb]:transition-transform"
        />
        {/* Beauty region indicator */}
        <div
          className="absolute top-0 h-1.5 rounded-full bg-[var(--color-accent)]/20 pointer-events-none"
          style={{ left: '0%', width: `${pct}%` }}
        />
      </div>
      <div className="w-16 text-right">
        <span className="text-xs font-mono text-[var(--color-text)]">
          {typeof value === 'number' ? (Number.isInteger(value) ? value : value.toFixed(3)) : value}
        </span>
        {def.unit && (
          <span className="text-[9px] text-[var(--color-text-muted)] ml-0.5">{def.unit}</span>
        )}
      </div>
    </div>
  );
}

/* ── Beauty Status ────────────────────────────── */

function BeautyStatus({ params }: { params: Record<string, number> }) {
  const { allOk, results } = validateBeauty(params);
  const violations = results.filter(r => !r.ok);

  return (
    <div className={`flex items-start gap-2 p-3 rounded-[var(--radius)] border transition-colors ${
      allOk
        ? 'border-[var(--color-accent)]/30 bg-[var(--color-accent)]/5'
        : 'border-[var(--color-danger)]/30 bg-[var(--color-danger)]/5'
    }`}>
      {allOk ? (
        <>
          <Shield className="w-4 h-4 text-[var(--color-accent)] shrink-0 mt-0.5" />
          <div>
            <div className="text-xs font-medium text-[var(--color-accent)]">Beauty Region: Safe</div>
            <div className="text-[10px] text-[var(--color-text-muted)]">All {results.length} constraints passing</div>
          </div>
        </>
      ) : (
        <>
          <AlertTriangle className="w-4 h-4 text-[var(--color-danger)] shrink-0 mt-0.5" />
          <div>
            <div className="text-xs font-medium text-[var(--color-danger)]">
              {violations.length} violation{violations.length > 1 ? 's' : ''}
            </div>
            {violations.map(v => (
              <div key={v.id} className="text-[10px] text-[var(--color-text-muted)] mt-0.5">
                {v.id}: {v.message}
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

/* ── Main Page ────────────────────────────────── */

export default function ParametersPage() {
  const [values, setValues] = useState<Record<string, number>>({});
  const [activeDomain, setActiveDomain] = useState<ParamDomain>('achromatic');

  // Initialize from DOM on mount
  useEffect(() => {
    const state: Record<string, number> = {};
    for (const p of PARAMETERS) {
      state[p.id] = getParam(p.id);
    }
    setValues(state);
  }, []);

  const handleChange = useCallback((id: string, val: number) => {
    setParam(id, val);
    setValues(prev => ({ ...prev, [id]: val }));
  }, []);

  const handleResetDomain = useCallback((domain: string) => {
    resetDomain(domain);
    // Re-read from DOM
    const updated = { ...values };
    for (const p of PARAMETERS) {
      if (p.domain === domain) updated[p.id] = getParam(p.id);
    }
    setValues(updated);
  }, [values]);

  const handleResetAll = useCallback(() => {
    resetAll();
    const state: Record<string, number> = {};
    for (const p of PARAMETERS) {
      state[p.id] = getParam(p.id);
    }
    setValues(state);
  }, []);

  const handleExport = useCallback(() => {
    const json = JSON.stringify(exportState(), null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `algebra-ui-params-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }, []);

  const handleImport = useCallback(() => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = () => {
        try {
          const state = JSON.parse(reader.result as string);
          importState(state);
          setValues(state);
        } catch { /* invalid JSON */ }
      };
      reader.readAsText(file);
    };
    input.click();
  }, []);

  const domainParams = getParamsByDomain(activeDomain);

  return (
    <div className="flex h-full">
      {/* Domain sidebar */}
      <div className="w-48 border-r border-[var(--color-border)] bg-[var(--color-surface)]/30 shrink-0 flex flex-col">
        <div className="p-3 border-b border-[var(--color-border)]">
          <div className="text-xs font-semibold uppercase tracking-wider text-[var(--color-text-muted)]">Parameters</div>
          <div className="text-[10px] text-[var(--color-text-muted)] mt-0.5">{PARAMETERS.length} tunable</div>
        </div>
        <div className="flex-1 overflow-y-auto py-1">
          {DOMAINS.map(domain => {
            const count = getParamsByDomain(domain).length;
            const isActive = activeDomain === domain;
            return (
              <button
                key={domain}
                onClick={() => setActiveDomain(domain)}
                className={`w-full flex items-center justify-between px-3 py-1.5 text-xs transition-colors ${
                  isActive
                    ? 'bg-[var(--color-surface-hover)] text-[var(--color-text)] font-medium'
                    : 'text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-hover)]/30'
                }`}
              >
                <span>{DOMAIN_LABELS[domain]}</span>
                <span className="text-[9px] font-mono opacity-50">{count}</span>
              </button>
            );
          })}
        </div>
        {/* Actions */}
        <div className="p-2 border-t border-[var(--color-border)] space-y-1">
          <button onClick={handleResetAll} className="w-full flex items-center gap-2 px-2 py-1.5 text-[10px] rounded-[var(--radius-sm)] text-[var(--color-text-muted)] hover:bg-[var(--color-surface-hover)] transition-colors">
            <RotateCcw className="w-3 h-3" /> Reset All
          </button>
          <button onClick={handleExport} className="w-full flex items-center gap-2 px-2 py-1.5 text-[10px] rounded-[var(--radius-sm)] text-[var(--color-text-muted)] hover:bg-[var(--color-surface-hover)] transition-colors">
            <Download className="w-3 h-3" /> Export
          </button>
          <button onClick={handleImport} className="w-full flex items-center gap-2 px-2 py-1.5 text-[10px] rounded-[var(--radius-sm)] text-[var(--color-text-muted)] hover:bg-[var(--color-surface-hover)] transition-colors">
            <Upload className="w-3 h-3" /> Import
          </button>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        <div className="p-4 border-b border-[var(--color-border)] flex items-center justify-between">
          <div>
            <h1 className="text-lg font-semibold text-[var(--color-text)]">{DOMAIN_LABELS[activeDomain]}</h1>
            <p className="text-xs text-[var(--color-text-muted)]">{domainParams.length} parameters — slide within beauty regions</p>
          </div>
          <button
            onClick={() => handleResetDomain(activeDomain)}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-[var(--radius)] border border-[var(--color-border)] text-[var(--color-text-muted)] hover:bg-[var(--color-surface-hover)] transition-colors"
          >
            <RotateCcw className="w-3 h-3" /> Reset {DOMAIN_LABELS[activeDomain]}
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-1">
          {domainParams.map(def => (
            <ParamSlider
              key={def.id}
              def={def}
              value={values[def.id] ?? def.dark}
              onChange={handleChange}
            />
          ))}
        </div>

        {/* Beauty status */}
        <div className="p-3 border-t border-[var(--color-border)]">
          <BeautyStatus params={values} />
        </div>
      </div>
    </div>
  );
}
