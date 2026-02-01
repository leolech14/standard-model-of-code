import { useState, useCallback } from 'react';
import type { SearchResponse } from '@/types';

const API_BASE = '/api';

export function useSearch() {
  const [results, setResults] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const search = useCallback(async (query: string, path?: string): Promise<SearchResponse> => {
    setLoading(true);
    setError(null);

    try {
      let url = `${API_BASE}/search?q=${encodeURIComponent(query)}`;
      if (path) {
        url += `&path=${encodeURIComponent(path)}`;
      }

      const response = await fetch(url, {
        credentials: 'include'
      });

      if (!response.ok) {
        throw new Error(`Search failed: ${response.statusText}`);
      }

      const data: SearchResponse = await response.json();
      setResults(data);
      return data;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const getRecent = useCallback(async (limit: number = 20) => {
    const response = await fetch(`${API_BASE}/recent?limit=${limit}`, {
      credentials: 'include'
    });

    if (!response.ok) {
      throw new Error(`Failed to get recent files: ${response.statusText}`);
    }

    return response.json();
  }, []);

  const clear = useCallback(() => {
    setResults(null);
    setError(null);
  }, []);

  return {
    results,
    loading,
    error,
    search,
    getRecent,
    clear
  };
}
