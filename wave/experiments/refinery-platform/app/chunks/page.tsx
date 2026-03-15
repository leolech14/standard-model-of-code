'use client';

import { useEffect, useState } from 'react';
import { Box, FileText } from 'lucide-react';
import { EmptyState, SectionHeader } from '@/components/shared/Common';
import { Skeleton } from '@/components/ui';
import { localGet } from '@/lib/api';

interface Chunk {
  chunk_id: string;
  project_id: string;
  file: string;
  content: string;
  tokens: number;
}

export default function ChunksPage() {
  const [chunks, setChunks] = useState<Chunk[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedChunk, setSelectedChunk] = useState<Chunk | null>(null);

  useEffect(() => {
    localGet<{ success: boolean; data: { items: Chunk[] } }>('projects/elements/chunks?per_page=20')
      .then(data => {
        if (data.success) {
          setChunks(data.data.items);
        }
      })
      .catch(err => {
        console.error('Failed to load chunks:', err);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex h-full">
        <div className="w-96 border-r border-border p-4 space-y-3">
          {[...Array(6)].map((_, i) => <Skeleton key={i} className="h-14" />)}
        </div>
        <div className="flex-1 p-6">
          <Skeleton className="h-6 w-48 mb-4" />
          <Skeleton className="h-64" />
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full">
      {/* Chunk List */}
      <div className="w-96 border-r border-border flex flex-col">
        <SectionHeader title={`Chunks (${chunks.length})`} />

        <div className="flex-1 overflow-y-auto">
          {chunks.length === 0 ? (
            <EmptyState message="No chunks found" submessage="Process a project to generate chunks" />
          ) : (
            <div className="space-y-1 p-2">
              {chunks.map(chunk => (
                <div
                  key={chunk.chunk_id}
                  onClick={() => setSelectedChunk(chunk)}
                  className={`
                    p-3 rounded-md cursor-pointer transition-colors
                    ${selectedChunk?.chunk_id === chunk.chunk_id
                      ? 'bg-surface'
                      : 'hover:bg-surface-hover'
                    }
                  `}
                >
                  <div className="flex items-start gap-2">
                    <FileText className="w-4 h-4 text-accent mt-0.5 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="text-xs font-mono text-text-secondary truncate mb-1">
                        {chunk.file}
                      </div>
                      <div className="text-xs text-text-muted">
                        {chunk.tokens} tokens
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Chunk Detail */}
      <div className="flex-1 flex flex-col">
        {selectedChunk ? (
          <>
            <div className="border-b border-border p-4">
              <div className="flex items-center gap-2 text-xs text-text-muted mb-2">
                <Box className="w-3 h-3" />
                <span className="font-mono">{selectedChunk.chunk_id}</span>
              </div>
              <h2 className="text-sm font-semibold mb-1">{selectedChunk.file}</h2>
              <div className="text-xs text-text-muted">
                {selectedChunk.tokens} tokens &bull; {selectedChunk.project_id}
              </div>
            </div>

            <div className="flex-1 overflow-y-auto p-6">
              <pre className="text-xs font-mono text-text whitespace-pre-wrap leading-relaxed">
                {selectedChunk.content}
              </pre>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <EmptyState
              message="Select a chunk to view"
              submessage="Click a chunk from the list to see its content"
            />
          </div>
        )}
      </div>
    </div>
  );
}
