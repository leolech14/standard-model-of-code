/**
 * Centralized fetch layer for Refinery Platform.
 *
 * Two endpoint families:
 *   /api/openclaw/:path*  --  proxied to OpenClaw (localhost:8100)
 *   /api/v1/:path*        --  local Next.js API routes
 *
 * All functions throw on non-2xx so callers can catch uniformly.
 */

const DEFAULT_TIMEOUT = 10_000; // 10s

export class ApiError extends Error {
  status: number;
  body: unknown;

  constructor(status: number, body: unknown, url: string) {
    super(`API ${status} from ${url}`);
    this.name = 'ApiError';
    this.status = status;
    this.body = body;
  }
}

/** Internal fetch with timeout + error normalization */
async function request<T>(
  url: string,
  init?: RequestInit & { timeout?: number }
): Promise<T> {
  const { timeout = DEFAULT_TIMEOUT, ...fetchInit } = init ?? {};
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);

  try {
    const res = await fetch(url, {
      ...fetchInit,
      signal: controller.signal,
    });

    if (!res.ok) {
      const body = await res.json().catch(() => res.statusText);
      throw new ApiError(res.status, body, url);
    }

    // 204 No Content
    if (res.status === 204) return undefined as T;

    return (await res.json()) as T;
  } catch (err) {
    if (err instanceof ApiError) throw err;

    // AbortController timeout
    if (err instanceof DOMException && err.name === 'AbortError') {
      throw new ApiError(408, 'Request timed out', url);
    }

    // Network failure (OpenClaw down, DNS, etc.)
    throw new ApiError(0, String(err), url);
  } finally {
    clearTimeout(timer);
  }
}

// ── Public API ──────────────────────────────────────

/**
 * GET from OpenClaw proxy.
 * Usage: `apiGet<HealthData>('health')`  -->  fetch('/api/openclaw/health')
 */
export function apiGet<T = unknown>(
  path: string,
  opts?: { timeout?: number }
): Promise<T> {
  return request<T>(`/api/openclaw/${path}`, {
    method: 'GET',
    timeout: opts?.timeout,
  });
}

/**
 * POST to OpenClaw proxy.
 * Usage: `apiPost('llm/mode', { mode: 'eco' })`
 */
export function apiPost<T = unknown>(
  path: string,
  body?: unknown,
  opts?: { timeout?: number }
): Promise<T> {
  return request<T>(`/api/openclaw/${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: body != null ? JSON.stringify(body) : undefined,
    timeout: opts?.timeout,
  });
}

/**
 * PUT to OpenClaw proxy.
 */
export function apiPut<T = unknown>(
  path: string,
  body?: unknown,
  opts?: { timeout?: number }
): Promise<T> {
  return request<T>(`/api/openclaw/${path}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: body != null ? JSON.stringify(body) : undefined,
    timeout: opts?.timeout,
  });
}

/**
 * DELETE to OpenClaw proxy.
 */
export function apiDelete<T = unknown>(
  path: string,
  opts?: { timeout?: number }
): Promise<T> {
  return request<T>(`/api/openclaw/${path}`, {
    method: 'DELETE',
    timeout: opts?.timeout,
  });
}

/**
 * GET from local Next.js API routes.
 * Usage: `localGet<InfraData>('infrastructure')`  -->  fetch('/api/v1/infrastructure')
 */
export function localGet<T = unknown>(
  path: string,
  opts?: { timeout?: number }
): Promise<T> {
  return request<T>(`/api/v1/${path}`, {
    method: 'GET',
    timeout: opts?.timeout,
  });
}
