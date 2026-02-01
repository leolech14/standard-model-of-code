import { useState, useCallback } from 'react';

const API_BASE = '/api';

interface HistoryState {
  canUndo: boolean;
  canRedo: boolean;
}

export function useHistory() {
  const [state, setState] = useState<HistoryState>({
    canUndo: false,
    canRedo: false
  });
  const [loading, setLoading] = useState(false);

  const refreshState = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/state`, {
        credentials: 'include'
      });
      const data = await response.json();
      setState({
        canUndo: data.can_undo,
        canRedo: data.can_redo
      });
    } catch {
      // Ignore errors
    }
  }, []);

  const undo = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/undo`, {
        method: 'POST',
        credentials: 'include'
      });
      const result = await response.json();
      await refreshState();
      return result;
    } finally {
      setLoading(false);
    }
  }, [refreshState]);

  const redo = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/redo`, {
        method: 'POST',
        credentials: 'include'
      });
      const result = await response.json();
      await refreshState();
      return result;
    } finally {
      setLoading(false);
    }
  }, [refreshState]);

  return {
    canUndo: state.canUndo,
    canRedo: state.canRedo,
    loading,
    undo,
    redo,
    refreshState
  };
}
