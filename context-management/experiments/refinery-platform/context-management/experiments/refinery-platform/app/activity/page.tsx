'use client';

import { useEffect, useState } from 'react';
import { Activity, Database, Search, Settings, AlertCircle } from 'lucide-react';
import { EmptyState, Badge } from '@/components/shared/Common';

interface ActivityEvent {
  id: string;
  timestamp: string;
  action: string;
  project_id: string;
  details: Record<string, any>;
  category: 'processing' | 'search' | 'update' | 'error' | 'system';
}

const ACTION_LABELS: Record<string, string> = {
  'project_registered': 'Project Registered',
  'chunks_processed': 'Chunks Processed',
  'chunks_updated': 'Chunks Updated',
  'search_query': 'Search Query',
  'processing_triggered': 'Processing Triggered',
  'file_change_detected': 'File Change Detected',
};

const CATEGORY_ICONS: Record<string, any> = {
  'processing': Activity,
  'search': Search,
  'update': Database,
  'system': Settings,
  'error': AlertCircle,
};

const CATEGORY_COLORS: Record<string, string> = {
  'processing': 'text-blue-500',
  'search': 'text-purple-500',
  'update': 'text-emerald-500',
  'system': 'text-neutral-500',
  'error': 'text-red-500',
};

export default function ActivityPage() {
  const [activity, setActivity] = useState<ActivityEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [hours, setHours] = useState(24);

  useEffect(() => {
    loadActivity();
  }, [hours]);

  const loadActivity = () => {
    setLoading(true);
    fetch(`/api/v1/activity?hours=${hours}&limit=100`)
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          setActivity(data.data.items);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load activity:', err);
        setLoading(false);
      });
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-pulse text-emerald-500">Loading activity...</div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold mb-2">Activity Timeline</h1>
        <p className="text-neutral-400 text-sm">
          Recent events across all projects
        </p>
      </div>

      {/* Time Filter */}
      <div className="mb-6 flex items-center gap-3">
        <span className="text-sm text-neutral-500">Show last:</span>
        {[6, 12, 24, 48, 168].map(h => (
          <button
            key={h}
            onClick={() => setHours(h)}
            className={`
              px-3 py-1.5 rounded-md text-xs font-medium transition-colors
              ${hours === h
                ? 'bg-emerald-500 text-black'
                : 'bg-neutral-800 text-neutral-400 hover:bg-neutral-700'
              }
            `}
          >
            {h < 24 ? `${h}h` : `${h / 24}d`}
          </button>
        ))}
      </div>

      {/* Timeline */}
      {activity.length === 0 ? (
        <EmptyState
          message="No recent activity"
          submessage={`No events in the last ${hours} hours`}
        />
      ) : (
        <div className="space-y-3">
          {activity.map((event, idx) => {
            const Icon = CATEGORY_ICONS[event.category] || Activity;
            const colorClass = CATEGORY_COLORS[event.category] || 'text-neutral-500';

            return (
              <div
                key={event.id}
                className="glass-card rounded-lg p-4 hover:border-neutral-700 transition-colors"
              >
                <div className="flex items-start gap-4">
                  {/* Icon */}
                  <div className={`mt-0.5 ${colorClass}`}>
                    <Icon className="w-4 h-4" />
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-semibold text-sm">
                        {ACTION_LABELS[event.action] || event.action}
                      </span>
                      <Badge status={event.category} />
                    </div>

                    <div className="text-xs text-neutral-500 mb-2">
                      <span className="font-mono">{event.project_id}</span>
                      <span className="mx-2">•</span>
                      <span>{formatTimestamp(event.timestamp)}</span>
                    </div>

                    {/* Details */}
                    {Object.keys(event.details).length > 0 && (
                      <div className="text-xs font-mono text-neutral-400 bg-neutral-900/50 p-2 rounded border border-neutral-800">
                        {Object.entries(event.details).map(([key, value]) => (
                          <div key={key}>
                            <span className="text-neutral-600">{key}:</span>{' '}
                            <span>{typeof value === 'object' ? JSON.stringify(value) : String(value)}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Timestamp */}
                  <div className="text-xs text-neutral-600 font-mono">
                    {new Date(event.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
