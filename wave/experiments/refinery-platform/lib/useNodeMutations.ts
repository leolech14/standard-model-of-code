'use client';

import { useRef, useState, useCallback } from 'react';
import { apiPost, apiPut, apiDelete, ApiError } from './api';
import type { NodeDefinition, MutationDefinition } from './nodes/types';

/**
 * Imperative mutation management hook.
 *
 * Solves: React hooks can't be called in loops.
 * Scans all node definitions for mutations[], creates API
 * handlers keyed by mutation ID, tracks loading state per ID.
 *
 * Usage:
 *   const { handlers, loading } = useNodeMutations(nodes, toast, refreshAll);
 */

export interface ToastAPI {
  success: (message: string, duration?: number) => void;
  error: (message: string, duration?: number) => void;
}

export function useNodeMutations(
  nodes: NodeDefinition[],
  toast: ToastAPI,
  onSuccess?: () => void,
): {
  handlers: Record<string, (payload: Record<string, unknown>) => void>;
  loading: Record<string, boolean>;
} {
  const [, setTick] = useState(0);
  const bump = useCallback(() => setTick((t) => t + 1), []);

  // Track loading state per mutation ID imperatively
  const loadingRef = useRef<Record<string, boolean>>({});

  // Build handlers once per node set (stable via ref pattern)
  const handlersRef = useRef<Record<string, (payload: Record<string, unknown>) => void>>({});

  // Collect all mutations from all nodes
  const allMutations: { mut: MutationDefinition; node: NodeDefinition }[] = [];
  for (const node of nodes) {
    if (node.mutations) {
      for (const mut of node.mutations) {
        allMutations.push({ mut, node });
      }
    }
  }

  // Build handler map
  const newHandlers: Record<string, (payload: Record<string, unknown>) => void> = {};

  for (const { mut } of allMutations) {
    newHandlers[mut.id] = async (payload: Record<string, unknown>) => {
      loadingRef.current[mut.id] = true;
      bump();

      try {
        let result: unknown;
        switch (mut.method) {
          case 'PUT':
            result = await apiPut(mut.endpoint, payload);
            break;
          case 'DELETE':
            result = await apiDelete(mut.endpoint);
            break;
          default:
            result = await apiPost(mut.endpoint, payload);
        }

        const msg =
          (result as Record<string, unknown>)?.message as string | undefined;
        toast.success(msg || `${mut.label} completed`);

        // Delay refresh slightly to let backend state settle
        if (onSuccess) {
          setTimeout(onSuccess, 2000);
        }
      } catch (err) {
        const msg =
          err instanceof ApiError
            ? err.status === 0
              ? 'Connection failed'
              : `Error ${err.status}: ${typeof err.body === 'string' ? err.body : JSON.stringify(err.body)}`
            : String(err);
        toast.error(`${mut.label} failed: ${msg}`);
      } finally {
        loadingRef.current[mut.id] = false;
        bump();
      }
    };
  }

  handlersRef.current = newHandlers;

  // Build loading snapshot from ref
  const loading: Record<string, boolean> = {};
  for (const { mut } of allMutations) {
    loading[mut.id] = loadingRef.current[mut.id] ?? false;
  }

  return { handlers: handlersRef.current, loading };
}
