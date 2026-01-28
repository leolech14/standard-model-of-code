'use client';

import { useState } from 'react';
import { Settings, Database, Cloud, Shield } from 'lucide-react';
import { SectionHeader } from '@/components/shared/Common';

export default function SettingsPage() {
  const [config, setConfig] = useState({
    dataPath: process.env.ELEMENTS_PATH || '/Users/lech/PROJECTS_all/PROJECT_elements',
    autoProcess: true,
    searchMode: 'text',
    maxChunksPerProject: 10000,
    apiVersion: 'v1'
  });

  return (
    <div className="p-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold mb-2">Platform Settings</h1>
        <p className="text-neutral-400 text-sm">
          Configure Refinery Platform behavior and integrations
        </p>
      </div>

      {/* Settings Sections */}
      <div className="space-y-6">
        {/* Data Configuration */}
        <div className="glass-card rounded-lg overflow-hidden">
          <SectionHeader title="Data Configuration" />
          <div className="p-4 space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                <Database className="w-4 h-4 inline mr-2" />
                Data Path
              </label>
              <input
                type="text"
                value={config.dataPath}
                onChange={(e) => setConfig({ ...config, dataPath: e.target.value })}
                className="w-full px-3 py-2 bg-neutral-900 border border-neutral-800 rounded-md
                         text-sm font-mono focus:outline-none focus:border-emerald-500"
                readOnly
              />
              <p className="text-xs text-neutral-600 mt-1">
                Base path for project data (read-only in production)
              </p>
            </div>

            <div>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={config.autoProcess}
                  onChange={(e) => setConfig({ ...config, autoProcess: e.target.checked })}
                  className="w-4 h-4 rounded border-neutral-700 bg-neutral-900 text-emerald-500
                           focus:ring-emerald-500 focus:ring-offset-0"
                />
                <span className="text-sm">Auto-process new files</span>
              </label>
              <p className="text-xs text-neutral-600 mt-1 ml-6">
                Automatically generate chunks when files change
              </p>
            </div>
          </div>
        </div>

        {/* Search Configuration */}
        <div className="glass-card rounded-lg overflow-hidden">
          <SectionHeader title="Search Configuration" />
          <div className="p-4 space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Search Mode</label>
              <select
                value={config.searchMode}
                onChange={(e) => setConfig({ ...config, searchMode: e.target.value })}
                className="w-full px-3 py-2 bg-neutral-900 border border-neutral-800 rounded-md
                         text-sm focus:outline-none focus:border-emerald-500"
              >
                <option value="text">Text Search (current)</option>
                <option value="semantic" disabled>Semantic Search (coming soon)</option>
                <option value="hybrid" disabled>Hybrid Search (coming soon)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Max Chunks Per Project</label>
              <input
                type="number"
                value={config.maxChunksPerProject}
                onChange={(e) => setConfig({ ...config, maxChunksPerProject: parseInt(e.target.value) })}
                className="w-full px-3 py-2 bg-neutral-900 border border-neutral-800 rounded-md
                         text-sm focus:outline-none focus:border-emerald-500"
              />
              <p className="text-xs text-neutral-600 mt-1">
                Limit chunks to prevent memory issues
              </p>
            </div>
          </div>
        </div>

        {/* Cloud Integration */}
        <div className="glass-card rounded-lg overflow-hidden">
          <SectionHeader title="Cloud Integration" />
          <div className="p-4 space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                <Cloud className="w-4 h-4 inline mr-2" />
                Cloud Storage
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value="gs://refinery-context/"
                  className="flex-1 px-3 py-2 bg-neutral-900 border border-neutral-800 rounded-md
                           text-sm font-mono focus:outline-none focus:border-emerald-500"
                  readOnly
                />
                <button className="px-4 py-2 bg-neutral-800 hover:bg-neutral-700 text-sm rounded-md">
                  Test
                </button>
              </div>
              <p className="text-xs text-neutral-600 mt-1">
                Google Cloud Storage bucket for multi-tenant data
              </p>
            </div>

            <div className="flex items-center gap-2 text-xs">
              <Shield className="w-3 h-3 text-emerald-500" />
              <span className="text-neutral-500">Configured for production deployment</span>
            </div>
          </div>
        </div>

        {/* Platform Info */}
        <div className="glass-card rounded-lg overflow-hidden">
          <SectionHeader title="Platform Information" />
          <div className="p-4 space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-neutral-500">Platform Level</span>
              <span className="font-mono text-emerald-400">L7 → L8</span>
            </div>
            <div className="flex justify-between">
              <span className="text-neutral-500">API Version</span>
              <span className="font-mono text-purple-400">v1</span>
            </div>
            <div className="flex justify-between">
              <span className="text-neutral-500">Type</span>
              <span className="font-mono text-blue-400">Independent Spinoff</span>
            </div>
            <div className="flex justify-between">
              <span className="text-neutral-500">Origin</span>
              <span className="font-mono text-neutral-400">PROJECT_elements</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
