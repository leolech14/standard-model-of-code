import { useState, useCallback } from 'react';
import type { FilePreview } from '@/types';

const API_BASE = '/api';

export function usePreview() {
  const [preview, setPreview] = useState<FilePreview | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getPreview = useCallback(async (path: string): Promise<FilePreview> => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/preview?path=${encodeURIComponent(path)}`, {
        credentials: 'include'
      });

      if (!response.ok) {
        throw new Error(`Failed to get preview: ${response.statusText}`);
      }

      const data: FilePreview = await response.json();
      setPreview(data);
      return data;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const getContent = useCallback(async (path: string): Promise<string> => {
    const response = await fetch(`${API_BASE}/content?path=${encodeURIComponent(path)}`, {
      credentials: 'include'
    });

    if (!response.ok) {
      throw new Error(`Failed to get content: ${response.statusText}`);
    }

    const data = await response.json();
    return data.content;
  }, []);

  const getMetadata = useCallback(async (path: string) => {
    const response = await fetch(`${API_BASE}/metadata?path=${encodeURIComponent(path)}`, {
      credentials: 'include'
    });

    if (!response.ok) {
      throw new Error(`Failed to get metadata: ${response.statusText}`);
    }

    return response.json();
  }, []);

  return {
    preview,
    loading,
    error,
    getPreview,
    getContent,
    getMetadata
  };
}
