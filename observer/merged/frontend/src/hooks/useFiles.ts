import { useState, useCallback } from 'react';
import type { FileItem, DirectoryListing, OperationResult } from '@/types';

const API_BASE = '/api';

export function useFiles(initialPath: string = '') {
  const [files, setFiles] = useState<FileItem[]>([]);
  const [currentPath, setCurrentPath] = useState(initialPath);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const listDirectory = useCallback(async (path: string) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/list?path=${encodeURIComponent(path)}`, {
        credentials: 'include'
      });

      if (!response.ok) {
        throw new Error(`Failed to list directory: ${response.statusText}`);
      }

      const data: DirectoryListing = await response.json();
      setFiles(data.files);
      setCurrentPath(data.path);
      return data;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const createFolder = useCallback(async (name: string): Promise<OperationResult> => {
    const response = await fetch(`${API_BASE}/create-folder`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ path: currentPath, name })
    });
    return response.json();
  }, [currentPath]);

  const deleteFiles = useCallback(async (paths: string[]): Promise<OperationResult> => {
    const response = await fetch(`${API_BASE}/delete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ files: paths })
    });
    return response.json();
  }, []);

  const renameFile = useCallback(async (path: string, newName: string): Promise<OperationResult> => {
    const response = await fetch(`${API_BASE}/rename`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ path, new_name: newName })
    });
    return response.json();
  }, []);

  const pasteFiles = useCallback(async (
    files: string[],
    destination: string,
    operation: 'copy' | 'move'
  ): Promise<OperationResult> => {
    const response = await fetch(`${API_BASE}/paste`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ files, destination, operation })
    });
    return response.json();
  }, []);

  const uploadFile = useCallback(async (file: File, path: string = currentPath): Promise<OperationResult> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('path', path);

    const response = await fetch(`${API_BASE}/upload`, {
      method: 'POST',
      credentials: 'include',
      body: formData
    });
    return response.json();
  }, [currentPath]);

  const refresh = useCallback(() => {
    if (currentPath) {
      return listDirectory(currentPath);
    }
  }, [currentPath, listDirectory]);

  return {
    files,
    currentPath,
    loading,
    error,
    listDirectory,
    createFolder,
    deleteFiles,
    renameFile,
    pasteFiles,
    uploadFile,
    refresh
  };
}
