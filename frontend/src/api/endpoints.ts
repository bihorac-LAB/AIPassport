/** One place per API route. Components never build a URL. */

import { api } from './client';
import type {
  ActivityResultRecord,
  AiActivityResponse,
  AiChatResponse,
  LearningSession,
  ModuleSummaryWire,
  ModulePageWire,
  ModuleWire,
  PageProgress,
  ProgressOverview,
  ResponseRecord,
  ResponseResult,
  TokenResponse,
  Track,
  User,
} from './types';

// ── Auth ─────────────────────────────────────────────────────────────────────

export const authApi = {
  register: (body: {
    email: string;
    password: string;
    display_name: string;
    track_pref?: Track;
  }) =>
    api.post<TokenResponse>('/auth/register', body, {
      withCredentials: true,
      skipRefresh: true,
    }),

  login: (body: { email: string; password: string }) =>
    api.post<TokenResponse>('/auth/login', body, { withCredentials: true, skipRefresh: true }),

  logout: () =>
    api.post<{ detail: string }>('/auth/logout', undefined, {
      withCredentials: true,
      skipRefresh: true,
    }),

  logoutAll: () =>
    api.post<{ detail: string }>('/auth/logout-all', undefined, { withCredentials: true }),

  requestPasswordReset: (body: { email: string }) =>
    api.post<{ detail: string }>('/auth/password-reset/request', body, { skipRefresh: true }),

  confirmPasswordReset: (body: { token: string; new_password: string }) =>
    api.post<{ detail: string }>('/auth/password-reset/confirm', body, { skipRefresh: true }),

  changePassword: (body: { current_password: string; new_password: string }) =>
    api.post<{ detail: string }>('/auth/password/change', body, { withCredentials: true }),

  requestEmailVerification: () =>
    api.post<{ detail: string }>('/auth/verify-email/request'),

  confirmEmailVerification: (body: { token: string }) =>
    api.post<{ detail: string }>('/auth/verify-email/confirm', body, { skipRefresh: true }),
};

// ── User ─────────────────────────────────────────────────────────────────────

export const userApi = {
  me: () => api.get<User>('/users/me'),
  update: (body: { display_name?: string; track_pref?: Track }) =>
    api.patch<User>('/users/me', body),
};

// ── Curriculum ───────────────────────────────────────────────────────────────

export const moduleApi = {
  list: () => api.get<ModuleSummaryWire[]>('/modules'),
  get: (moduleKey: string) => api.get<ModuleWire>(`/modules/${moduleKey}`),
  page: (moduleKey: string, pageKey: string) =>
    api.get<ModulePageWire>(`/modules/${moduleKey}/pages/${pageKey}`),
};

// ── Progress ─────────────────────────────────────────────────────────────────

export const progressApi = {
  overview: () => api.get<ProgressOverview>('/progress/me'),
  update: (
    pageKey: string,
    body: {
      status?: 'in_progress' | 'completed';
      section_completed?: string;
      last_section_id?: string;
      seconds_delta?: number;
      register_visit?: boolean;
      learning_session_id?: string;
    },
  ) => api.post<PageProgress>(`/progress/pages/${pageKey}`, body),
};

export const sessionApi = {
  start: (body: {
    is_embedded: boolean;
    timezone?: string;
    viewport_width?: number;
    referrer_kind?: 'direct' | 'canvas' | 'other';
  }) => api.post<LearningSession>('/sessions', body),
  end: (id: string) => api.post<{ detail: string }>(`/sessions/${id}/end`),
};

// ── Responses ────────────────────────────────────────────────────────────────

export const responseApi = {
  submit: (body: {
    question_key: string;
    answer: Record<string, unknown>;
    is_final?: boolean;
    response_time_ms?: number;
    client_submitted_at?: string;
    learning_session_id?: string;
    idempotency_key?: string;
  }) => api.post<ResponseResult>('/responses', body),

  mine: (params?: { page_key?: string; module_key?: string }) => {
    const search = new URLSearchParams();
    if (params?.page_key) search.set('page_key', params.page_key);
    if (params?.module_key) search.set('module_key', params.module_key);
    const qs = search.toString();
    return api.get<ResponseRecord[]>(`/responses/me${qs ? `?${qs}` : ''}`);
  },

  history: (questionKey: string) =>
    api.get<ResponseRecord[]>(`/responses/me/${questionKey}/history`),
};

export const activityApi = {
  save: (body: {
    activity_key: string;
    module_key: string;
    page_key: string;
    payload: Record<string, unknown>;
    learning_session_id?: string;
    idempotency_key?: string;
  }) => api.post<ActivityResultRecord>('/activity-results', body),

  mine: (pageKey?: string) =>
    api.get<ActivityResultRecord[]>(
      `/activity-results/me${pageKey ? `?page_key=${encodeURIComponent(pageKey)}` : ''}`,
    ),
};

// ── Events ───────────────────────────────────────────────────────────────────

export type EventPayload = {
  event_type: string;
  module_key?: string;
  page_key?: string;
  activity_key?: string;
  question_key?: string;
  section_id?: string;
  metadata?: Record<string, unknown>;
  client_ts?: string;
};

export const eventApi = {
  send: (events: EventPayload[], learningSessionId?: string, keepalive = false) =>
    api.post<{ accepted: number; learning_session_id: string | null }>(
      '/events',
      { events, learning_session_id: learningSessionId },
      { keepalive },
    ),
};

// ── AI ───────────────────────────────────────────────────────────────────────

export const aiApi = {
  chat: (body: {
    message: string;
    module_key?: string;
    page_key?: string;
    section_id?: string;
    activity_key?: string;
    activity_context?: Record<string, unknown>;
    history?: Array<{ role: 'user' | 'assistant'; content: string }>;
    conversation_id?: string;
  }) => api.post<AiChatResponse>('/ai/chat', body),

  activity: (body: {
    prompt_key: string;
    input: string;
    module_key?: string;
    page_key?: string;
  }) => api.post<AiActivityResponse>('/ai/activity', body),
};
