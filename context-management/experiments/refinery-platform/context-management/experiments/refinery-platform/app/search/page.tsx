'use client';

import { useState } from 'react';
import { Search, FileText, Sparkles } from 'lucide-react';
import { EmptyState } from '@/components/shared/Common';

interface SearchResult {
  chunk: {
    chunk_id: string;
    project_id: string;
    file: string;
    content: string;
    tokens: number;
  };
  score: number;
  highlights: string[];
}

export default function SearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setSearched(true);

    try {
      const res = await fetch('/api/v1/chunks/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, limit: 50 })
      });

      const data = await res.json();
      if (data.success) {
        setResults(data.data.results);
      }
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold mb-2">Search Context</h1>
        <p className="text-neutral-400 text-sm">
          Search across all projects • Text search (semantic coming soon)
        </p>
      </div>

      {/* Search Bar */}
      <form onSubmit={handleSearch} className="mb-8">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-500" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search chunks, files, code..."
            className="w-full pl-12 pr-4 py-3 bg-neutral-900/50 border border-neutral-800 rounded-lg
                     text-white placeholder-neutral-500 focus:outline-none focus:border-emerald-500
                     transition-colors"
          />
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="absolute right-2 top-1/2 -translate-y-1/2 px-4 py-1.5 bg-emerald-500
                     hover:bg-emerald-400 disabled:bg-neutral-700 disabled:text-neutral-500
                     text-black rounded-md text-sm font-medium transition-colors"
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </form>

      {/* Results */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="flex items-center gap-3 text-emerald-500">
            <Sparkles className="w-5 h-5 animate-pulse" />
            <span>Searching context...</span>
          </div>
        </div>
      ) : searched && results.length === 0 ? (
        <EmptyState
          message="No results found"
          submessage={`Try different keywords or check project spelling`}
        />
      ) : results.length > 0 ? (
        <div className="space-y-4">
          <div className="text-sm text-neutral-500 mb-4">
            Found {results.length} {results.length === 1 ? 'result' : 'results'}
          </div>

          {results.map((result, idx) => (
            <div
              key={result.chunk.chunk_id}
              className="glass-card rounded-lg p-5 hover:border-emerald-500/30 transition-colors"
            >
              {/* Header */}
              <div className="flex items-start gap-3 mb-3">
                <FileText className="w-4 h-4 text-emerald-500 mt-1 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-sm mb-1 truncate">
                    {result.chunk.file}
                  </h3>
                  <div className="flex items-center gap-2 text-xs text-neutral-500">
                    <span className="font-mono">{result.chunk.project_id}</span>
                    <span>•</span>
                    <span>{result.chunk.tokens} tokens</span>
                    <span>•</span>
                    <span className="text-emerald-500">Score: {result.score}</span>
                  </div>
                </div>
              </div>

              {/* Highlights */}
              {result.highlights.length > 0 && (
                <div className="space-y-2">
                  {result.highlights.map((highlight, hidx) => (
                    <div
                      key={hidx}
                      className="text-xs font-mono text-neutral-400 bg-neutral-900/50 p-3 rounded
                               border border-neutral-800"
                    >
                      {highlight}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-20 text-neutral-600">
          <Search className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p className="text-sm">Enter a query to search across all context</p>
        </div>
      )}
    </div>
  );
}
