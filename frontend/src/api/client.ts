/**
 * Typed API client.
 *
 * The access token lives in module memory only — never localStorage — so an XSS payload cannot
 * exfiltrate a long-lived credential. Session continuity comes from the HttpOnly refresh cookie,
 * which JavaScript cannot read; this module only knows how to *ask* for a refresh.
 */

const RAW_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000';
export const API_BASE = RAW_BASE.replace(/\/+$/, '');
const V1 = `${API_BASE}/api/v1`;

export class ApiError extends Error {
  constructor(
    readonly status: number,
    readonly code: string,
    message: string,
    readonly fields?: Array<{ field: string; message: string }>,
    readonly retryAfter?: number,
  ) {
    super(message);
    this.name = 'ApiError';
  }

  get isAuthError(): boolean {
    return this.status === 401;
  }

  get isTransient(): boolean {
    return this.status === 0 || this.status === 408 || this.status === 429 || this.status >= 500;
  }
}

type TokenState = { accessToken: string | null; csrfToken: string | null };
const tokens: TokenState = { accessToken: null, csrfToken: null };

let refreshInFlight: Promise<boolean> | null = null;
const authListeners = new Set<() => void>();

export function setAccessToken(token: string | null, csrfToken?: string | null): void {
  tokens.accessToken = token;
  if (csrfToken !== undefined) tokens.csrfToken = csrfToken;
}

export function getAccessToken(): string | null {
  return tokens.accessToken;
}

/** Notified when a refresh attempt fails and the user must sign in again. */
export function onAuthExpired(listener: () => void): () => void {
  authListeners.add(listener);
  return () => authListeners.delete(listener);
}

function notifyAuthExpired(): void {
  for (const listener of authListeners) listener();
}

function readCsrfCookie(): string | null {
  const match = document.cookie.match(/(?:^|;\s*)aip_csrf=([^;]+)/);
  return match?.[1] ? decodeURIComponent(match[1]) : null;
}

function csrfHeader(): Record<string, string> {
  const token = tokens.csrfToken ?? readCsrfCookie();
  return token ? { 'X-CSRF-Token': token } : {};
}

async function toApiError(response: Response): Promise<ApiError> {
  let code = 'http_error';
  let detail = response.statusText || 'Request failed.';
  let fields: Array<{ field: string; message: string }> | undefined;
  try {
    const body = (await response.json()) as {
      detail?: string;
      code?: string;
      fields?: Array<{ field: string; message: string }>;
    };
    if (body.detail) detail = body.detail;
    if (body.code) code = body.code;
    if (body.fields) fields = body.fields;
  } catch {
    // Non-JSON error body (proxy error page); keep the status text.
  }
  const retryAfterHeader = response.headers.get('retry-after');
  const retryAfter = retryAfterHeader ? Number(retryAfterHeader) : undefined;
  return new ApiError(response.status, code, detail, fields, retryAfter);
}

async function attemptRefresh(): Promise<boolean> {
  refreshInFlight ??= (async () => {
    try {
      const response = await fetch(`${V1}/auth/refresh`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json', ...csrfHeader() },
      });
      if (!response.ok) return false;
      const body = (await response.json()) as { access_token: string; csrf_token: string };
      setAccessToken(body.access_token, body.csrf_token);
      return true;
    } catch {
      return false;
    } finally {
      // Cleared on the next tick so concurrent 401s share this single attempt.
      setTimeout(() => {
        refreshInFlight = null;
      }, 0);
    }
  })();
  return refreshInFlight;
}

export type RequestOptions = {
  method?: 'GET' | 'POST' | 'PATCH' | 'DELETE';
  body?: unknown;
  /** Send the refresh cookie and the CSRF header (auth endpoints only). */
  withCredentials?: boolean;
  /** Skip the automatic refresh-and-retry (used by the auth endpoints themselves). */
  skipRefresh?: boolean;
  signal?: AbortSignal;
  keepalive?: boolean;
};

export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, withCredentials, skipRefresh, signal, keepalive } = options;

  const send = async (): Promise<Response> => {
    const headers: Record<string, string> = { Accept: 'application/json' };
    if (body !== undefined) headers['Content-Type'] = 'application/json';
    if (tokens.accessToken) headers.Authorization = `Bearer ${tokens.accessToken}`;
    if (withCredentials) Object.assign(headers, csrfHeader());

    return fetch(`${V1}${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
      credentials: withCredentials ? 'include' : 'same-origin',
      signal,
      keepalive,
    });
  };

  let response: Response;
  try {
    response = await send();
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') throw error;
    throw new ApiError(0, 'network_error', 'Could not reach the server. Check your connection.');
  }

  if (response.status === 401 && !skipRefresh) {
    const refreshed = await attemptRefresh();
    if (refreshed) {
      try {
        response = await send();
      } catch {
        throw new ApiError(0, 'network_error', 'Could not reach the server.');
      }
    } else {
      setAccessToken(null, null);
      notifyAuthExpired();
    }
  }

  if (!response.ok) throw await toApiError(response);
  if (response.status === 204) return undefined as T;

  const text = await response.text();
  return (text ? JSON.parse(text) : undefined) as T;
}

export const api = {
  get: <T>(path: string, options?: Omit<RequestOptions, 'method' | 'body'>) =>
    request<T>(path, { ...options, method: 'GET' }),
  post: <T>(path: string, body?: unknown, options?: Omit<RequestOptions, 'method' | 'body'>) =>
    request<T>(path, { ...options, method: 'POST', body }),
  patch: <T>(path: string, body?: unknown, options?: Omit<RequestOptions, 'method' | 'body'>) =>
    request<T>(path, { ...options, method: 'PATCH', body }),
  refresh: attemptRefresh,
};
