import React from 'react';
import { Artifact, Run, Alert } from '../types';
import { UiLink, Badge } from './Common';
import { FileCode, FileVideo, FileAudio, Archive, Clock, Terminal, Star } from 'lucide-react';

export const ArtifactInspector: React.FC<{ artifact: Artifact; onUpdate: (a: Artifact) => void }> = ({ artifact, onUpdate }) => {
    const toggleVault = () => {
        onUpdate({ ...artifact, isVaulted: !artifact.isVaulted });
    };

    return (
        <div className="flex flex-col h-full">
            <div className="p-6 border-b border-neutral-800">
                <div className="flex items-center space-x-2 text-xs text-neutral-500 font-mono mb-2">
                    <Archive className="w-3 h-3" />
                    <span>{artifact.id}</span>
                </div>
                <div className="flex items-start justify-between">
                    <h2 className="text-xl font-semibold text-neutral-200 mb-1 truncate flex-1 mr-4">{artifact.name}</h2>
                    {artifact.isVaulted && <Star className="w-5 h-5 text-emerald-500 fill-emerald-500/20" />}
                </div>
                <div className="flex items-center space-x-3 text-xs text-neutral-500">
                    <Badge status={artifact.status} />
                    <span>{artifact.stage}</span>
                    <span className="w-1 h-1 bg-neutral-700 rounded-full" />
                    <span>{artifact.size}</span>
                </div>
            </div>

            <div className="flex border-b border-neutral-800 px-6">
                {['Summary', 'Stats', 'Snippets', 'Provenance'].map((tab, i) => (
                    <button key={tab} className={`px-4 py-3 text-xs font-medium border-b-2 transition-colors ${i === 0 ? 'border-neutral-500 text-neutral-200' : 'border-transparent text-neutral-600 hover:text-neutral-400'}`}>
                        {tab}
                    </button>
                ))}
            </div>

            <div className="p-6 space-y-6 flex-1 overflow-y-auto">
                <div className="space-y-1">
                    <label className="text-[10px] uppercase text-neutral-600 font-semibold tracking-wider">Type</label>
                    <div className="flex items-center space-x-2 text-sm text-neutral-400">
                        {artifact.type === 'mp4' ? <FileVideo className="w-4 h-4" /> : artifact.type === 'wav' ? <FileAudio className="w-4 h-4" /> : <FileCode className="w-4 h-4" />}
                        <span className="uppercase">{artifact.type}</span>
                    </div>
                </div>

                <div className="space-y-1">
                    <label className="text-[10px] uppercase text-neutral-600 font-semibold tracking-wider">Tags</label>
                    <div className="flex flex-wrap gap-2">
                        {artifact.tags.map(tag => (
                            <span key={tag} className="px-1.5 py-0.5 bg-neutral-900 border border-neutral-800 rounded text-[10px] text-neutral-400 font-mono">
                                {tag}
                            </span>
                        ))}
                    </div>
                </div>

                <div className="p-4 bg-neutral-900/50 border border-neutral-800/50 rounded text-xs font-mono text-neutral-500 whitespace-pre-wrap">
{`{
  "checksum": "sha256:8f43...",
  "created_by": "service_worker_04",
  "dependencies": []
}`}
                </div>
            </div>

            <div className="p-6 border-t border-neutral-800 bg-neutral-925">
                 <UiLink
                    onClick={toggleVault}
                    className={`w-full py-2 border text-center transition-colors ${artifact.isVaulted ? 'border-emerald-900 text-emerald-500 hover:bg-emerald-900/10' : 'border-neutral-700 hover:bg-neutral-800'}`}
                 >
                    {artifact.isVaulted ? 'Remove from Vault' : 'Save to Vault'}
                 </UiLink>
            </div>
        </div>
    );
};

export const RunInspector: React.FC<{ run: Run }> = ({ run }) => (
    <div className="p-6">
         <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-neutral-200">Run Details</h2>
            <span className="font-mono text-xs text-neutral-600">{run.id}</span>
        </div>
        <div className="space-y-4">
             <div className="bg-neutral-900 p-4 rounded flex items-center justify-between">
                <span className="text-sm text-neutral-400">Status</span>
                <div className="flex items-center space-x-2">
                    <Badge status={run.status} />
                    <span className="text-sm capitalize text-neutral-200">{run.status}</span>
                </div>
             </div>
             <div className="grid grid-cols-2 gap-4">
                 <div className="p-4 border border-neutral-800 rounded">
                     <div className="text-[10px] text-neutral-600 uppercase mb-1">Duration</div>
                     <div className="text-sm text-neutral-300 font-mono">{run.duration}</div>
                 </div>
                 <div className="p-4 border border-neutral-800 rounded">
                     <div className="text-[10px] text-neutral-600 uppercase mb-1">Trigger</div>
                     <div className="text-sm text-neutral-300 font-mono">{run.triggeredBy}</div>
                 </div>
             </div>
             <div>
                <h3 className="text-xs text-neutral-500 uppercase font-semibold mb-2">Logs</h3>
                <div className="h-48 bg-neutral-950 p-3 rounded border border-neutral-800 overflow-y-auto font-mono text-[10px] text-neutral-500">
                    <p className="text-emerald-700">[INFO] Run initiated by scheduler</p>
                    <p>[INFO] Allocating resources...</p>
                    <p>[INFO] Pulling container image...</p>
                    <p className="text-amber-700">[WARN] Latency spike in sector 7</p>
                    <p>[INFO] Processing chunk 1/450...</p>
                    {run.status === 'failed' && <p className="text-rose-700">[ERR] Connection reset by peer</p>}
                </div>
             </div>
        </div>
    </div>
);

export const AlertInspector: React.FC<{ alert: Alert }> = ({ alert }) => (
    <div className="p-6">
        <div className="flex items-center space-x-2 mb-4 text-rose-500">
             <Terminal className="w-5 h-5" />
             <span className="text-sm font-bold uppercase tracking-widest">{alert.severity} ALERT</span>
        </div>
        <h2 className="text-xl font-medium text-neutral-200 mb-2">{alert.message}</h2>
        <div className="text-xs text-neutral-500 font-mono mb-8">{alert.id} • {new Date(alert.timestamp).toLocaleString()}</div>

        <div className="space-y-4">
            <div className="bg-neutral-900 p-4 rounded border-l-2 border-neutral-700">
                <div className="text-xs text-neutral-400 mb-1">Source Component</div>
                <div className="text-sm text-neutral-200 font-mono">{alert.source}</div>
            </div>

             <div className="flex items-center justify-between pt-8">
                 <span className="text-xs text-neutral-500">Status: {alert.acknowledged ? 'Acknowledged' : 'Pending'}</span>
                 <label className="flex items-center space-x-2 cursor-pointer">
                     <div className={`w-10 h-5 rounded-full relative transition-colors ${alert.acknowledged ? 'bg-emerald-600' : 'bg-neutral-700'}`}>
                         <div className={`absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full transition-transform ${alert.acknowledged ? 'translate-x-5' : ''}`} />
                     </div>
                     <span className="text-xs text-neutral-400">Acknowledge</span>
                 </label>
             </div>
        </div>
    </div>
);
