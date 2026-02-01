'use client';

import { useState, useEffect } from 'react';

interface ServiceStatus {
    name?: string;
    status: string;
    message?: string;
    present?: string[];
    missing?: string[];
    process?: { status: string; message?: string; pids?: string[] };
    logs?: { status: string; last_entry?: string; line_count?: number };
    connection?: { status: string; message?: string };
    tool_exists?: { status: string; path?: string };
    [key: string]: unknown;
}

interface HealthData {
    timestamp: string;
    overall_status: string;
    error?: string;
    stderr?: string;
    services: Record<string, ServiceStatus>;
}

const STATUS_COLORS: Record<string, string> = {
    OK: 'text-green-400 bg-green-900/30',
    UP: 'text-green-400 bg-green-900/30',
    DOWN: 'text-red-400 bg-red-900/30',
    ERROR: 'text-red-400 bg-red-900/30',
    DEGRADED: 'text-yellow-400 bg-yellow-900/30',
    WARNING: 'text-yellow-400 bg-yellow-900/30',
    UNKNOWN: 'text-gray-400 bg-gray-900/30',
};

const STATUS_ICONS: Record<string, string> = {
    OK: '●',
    UP: '●',
    DOWN: '○',
    ERROR: '✕',
    DEGRADED: '◐',
    WARNING: '◐',
    UNKNOWN: '?',
};

function getStatusDetails(svc: ServiceStatus): string {
    const details: string[] = [];

    if (svc.message) details.push(svc.message);
    if (svc.process?.message) details.push(`Process: ${svc.process.message}`);
    if (svc.connection?.message) details.push(`Connection: ${svc.connection.message}`);
    if (svc.logs?.last_entry) {
        const entry = svc.logs.last_entry.length > 80
            ? svc.logs.last_entry.substring(0, 80) + '...'
            : svc.logs.last_entry;
        details.push(`Log: ${entry}`);
    }
    if (svc.present?.length) details.push(`Keys: ${svc.present.join(', ')}`);
    if (svc.missing?.length) details.push(`Missing: ${svc.missing.join(', ')}`);
    if (svc.tool_exists?.path) details.push(`Path: ${svc.tool_exists.path}`);

    return details.join(' | ') || '-';
}

export default function OpsPage() {
    const [health, setHealth] = useState<HealthData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [lastRefresh, setLastRefresh] = useState<Date | null>(null);

    const fetchHealth = async () => {
        try {
            const res = await fetch('/api/ops/status');
            const data = await res.json();
            setHealth(data);
            setError(null);
            setLastRefresh(new Date());
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchHealth();
        const interval = setInterval(fetchHealth, 5000);
        return () => clearInterval(interval);
    }, []);

    if (loading && !health) {
        return (
            <div className="min-h-screen bg-black text-neutral-300 p-8">
                <div className="animate-pulse">Loading health status...</div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-black text-neutral-300 p-8">
            <header className="mb-8">
                <h1 className="text-2xl font-bold text-white mb-2">Operations Status</h1>
                <div className="flex items-center gap-4 text-sm text-neutral-500">
                    <span>Auto-refresh: 5s</span>
                    {lastRefresh && (
                        <span>Last update: {lastRefresh.toLocaleTimeString()}</span>
                    )}
                    <button
                        onClick={fetchHealth}
                        className="px-3 py-1 bg-neutral-800 hover:bg-neutral-700 rounded text-neutral-300"
                    >
                        Refresh Now
                    </button>
                </div>
            </header>

            {error && (
                <div className="mb-6 p-4 bg-red-900/30 border border-red-700 rounded">
                    <strong>Error:</strong> {error}
                </div>
            )}

            {health && (
                <>
                    {/* Overall Status Banner */}
                    <div className={`mb-8 p-6 rounded-lg border ${
                        health.overall_status === 'OK'
                            ? 'bg-green-900/20 border-green-700'
                            : health.overall_status === 'DEGRADED'
                            ? 'bg-yellow-900/20 border-yellow-700'
                            : 'bg-red-900/20 border-red-700'
                    }`}>
                        <div className="flex items-center gap-4">
                            <span className="text-4xl">
                                {STATUS_ICONS[health.overall_status] || '?'}
                            </span>
                            <div>
                                <div className="text-2xl font-bold text-white">
                                    {health.overall_status}
                                </div>
                                <div className="text-sm text-neutral-400">
                                    {health.timestamp}
                                </div>
                            </div>
                        </div>
                        {health.error && (
                            <div className="mt-4 text-red-400 text-sm">
                                {health.error}
                            </div>
                        )}
                    </div>

                    {/* Services Table */}
                    <div className="bg-neutral-900 rounded-lg border border-neutral-800 overflow-hidden">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-neutral-800 bg-neutral-900/50">
                                    <th className="text-left p-4 text-neutral-400 font-medium">Service</th>
                                    <th className="text-left p-4 text-neutral-400 font-medium w-24">Status</th>
                                    <th className="text-left p-4 text-neutral-400 font-medium">Details</th>
                                </tr>
                            </thead>
                            <tbody>
                                {Object.entries(health.services).map(([id, svc]) => (
                                    <tr key={id} className="border-b border-neutral-800/50 hover:bg-neutral-800/30">
                                        <td className="p-4">
                                            <div className="font-medium text-white">
                                                {svc.name || id}
                                            </div>
                                            <div className="text-xs text-neutral-500">{id}</div>
                                        </td>
                                        <td className="p-4">
                                            <span className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium ${STATUS_COLORS[svc.status] || STATUS_COLORS.UNKNOWN}`}>
                                                {STATUS_ICONS[svc.status] || '?'} {svc.status}
                                            </span>
                                        </td>
                                        <td className="p-4 text-sm text-neutral-400 max-w-xl truncate">
                                            {getStatusDetails(svc)}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>

                    {/* Raw JSON (collapsible) */}
                    <details className="mt-8">
                        <summary className="cursor-pointer text-neutral-500 hover:text-neutral-300">
                            Show raw JSON
                        </summary>
                        <pre className="mt-4 p-4 bg-neutral-900 rounded text-xs overflow-auto max-h-96">
                            {JSON.stringify(health, null, 2)}
                        </pre>
                    </details>
                </>
            )}
        </div>
    );
}
