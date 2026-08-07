/**
 * Autosave for question responses and activity results.
 *
 * Behavior: local state updates immediately, the network write is debounced, the payload is mirrored
 * to localStorage so a reload does not lose work, transient failures retry with backoff, and an
 * idempotency key prevents a retry from creating a duplicate attempt.
 *
 * The mirror deliberately stores only learner answers keyed by question — never a token or an email.
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import { ApiError } from './client';
import { activityApi, responseApi } from './endpoints';
import type { ResponseResult } from './types';
import type { SaveStatus } from '@/components/SaveState';
import { getLearningSessionId } from '@/analytics/track';

const MIRROR_PREFIX = 'aip.draft.';
const MAX_RETRIES = 4;

async function hashKey(parts: unknown[]): Promise<string> {
  const input = JSON.stringify(parts);
  if (globalThis.crypto?.subtle) {
    const bytes = new TextEncoder().encode(input);
    const digest = await globalThis.crypto.subtle.digest('SHA-256', bytes);
    return Array.from(new Uint8Array(digest))
      .slice(0, 16)
      .map((byte) => byte.toString(16).padStart(2, '0'))
      .join('');
  }
  // Deterministic fallback for environments without SubtleCrypto (e.g. jsdom over http).
  let hash = 5381;
  for (let i = 0; i < input.length; i += 1) hash = ((hash << 5) + hash + input.charCodeAt(i)) | 0;
  return `f${(hash >>> 0).toString(16)}${input.length.toString(16)}`;
}

export function readDraft<T>(key: string): T | null {
  try {
    const raw = window.localStorage.getItem(MIRROR_PREFIX + key);
    return raw ? (JSON.parse(raw) as T) : null;
  } catch {
    return null;
  }
}

function writeDraft(key: string, value: unknown): void {
  try {
    window.localStorage.setItem(MIRROR_PREFIX + key, JSON.stringify(value));
  } catch {
    // Storage full or blocked: the network write is still the source of truth.
  }
}

function clearDraft(key: string): void {
  try {
    window.localStorage.removeItem(MIRROR_PREFIX + key);
  } catch {
    /* ignore */
  }
}

type UseAutosaveOptions = {
  debounceMs?: number;
  onSaved?: (result: ResponseResult) => void;
};

export function useResponseAutosave(questionKey: string, options: UseAutosaveOptions = {}) {
  const { debounceMs = 600, onSaved } = options;
  const [status, setStatus] = useState<SaveStatus>('idle');
  const timer = useRef<number | null>(null);
  const attempt = useRef(0);
  const inFlight = useRef(false);
  const latest = useRef<{ answer: Record<string, unknown>; startedAt: number } | null>(null);
  const mounted = useRef(true);

  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
      if (timer.current !== null) window.clearTimeout(timer.current);
    };
  }, []);

  const send = useCallback(async () => {
    const pending = latest.current;
    if (!pending || inFlight.current) return;
    inFlight.current = true;
    if (mounted.current) setStatus('saving');

    try {
      const idempotencyKey = await hashKey([questionKey, pending.answer]);
      const result = await responseApi.submit({
        question_key: questionKey,
        answer: pending.answer,
        is_final: true,
        response_time_ms: Math.min(86_400_000, Date.now() - pending.startedAt),
        client_submitted_at: new Date().toISOString(),
        learning_session_id: getLearningSessionId() ?? undefined,
        idempotency_key: idempotencyKey,
      });
      attempt.current = 0;
      clearDraft(questionKey);
      if (mounted.current) setStatus('saved');
      onSaved?.(result);
    } catch (error) {
      const transient = error instanceof ApiError ? error.isTransient : true;
      if (transient && attempt.current < MAX_RETRIES) {
        attempt.current += 1;
        const delay = Math.min(15_000, 800 * 2 ** (attempt.current - 1));
        if (mounted.current) setStatus('offline');
        window.setTimeout(() => {
          inFlight.current = false;
          void send();
        }, delay);
        return;
      }
      if (mounted.current) setStatus(transient ? 'offline' : 'error');
    } finally {
      if (attempt.current === 0) inFlight.current = false;
    }
  }, [onSaved, questionKey]);

  const save = useCallback(
    (answer: Record<string, unknown>, startedAt: number, immediate = false) => {
      latest.current = { answer, startedAt };
      writeDraft(questionKey, answer);
      if (timer.current !== null) window.clearTimeout(timer.current);
      if (immediate) {
        void send();
        return;
      }
      setStatus('saving');
      timer.current = window.setTimeout(() => {
        timer.current = null;
        void send();
      }, debounceMs);
    },
    [debounceMs, questionKey, send],
  );

  return { status, save };
}

export function useActivityAutosave(
  activityKey: string,
  moduleKey: string,
  pageKey: string,
  debounceMs = 900,
) {
  const [status, setStatus] = useState<SaveStatus>('idle');
  const timer = useRef<number | null>(null);
  const latest = useRef<Record<string, unknown> | null>(null);
  const mounted = useRef(true);

  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
      if (timer.current !== null) window.clearTimeout(timer.current);
    };
  }, []);

  const send = useCallback(async () => {
    const payload = latest.current;
    if (!payload) return;
    if (mounted.current) setStatus('saving');
    try {
      const idempotencyKey = await hashKey([activityKey, payload]);
      await activityApi.save({
        activity_key: activityKey,
        module_key: moduleKey,
        page_key: pageKey,
        payload,
        learning_session_id: getLearningSessionId() ?? undefined,
        idempotency_key: idempotencyKey,
      });
      clearDraft(activityKey);
      if (mounted.current) setStatus('saved');
    } catch {
      writeDraft(activityKey, payload);
      if (mounted.current) setStatus('offline');
    }
  }, [activityKey, moduleKey, pageKey]);

  const save = useCallback(
    (payload: Record<string, unknown>, immediate = false) => {
      latest.current = payload;
      writeDraft(activityKey, payload);
      if (timer.current !== null) window.clearTimeout(timer.current);
      if (immediate) {
        void send();
        return;
      }
      setStatus('saving');
      timer.current = window.setTimeout(() => {
        timer.current = null;
        void send();
      }, debounceMs);
    },
    [activityKey, debounceMs, send],
  );

  return { status, save };
}
