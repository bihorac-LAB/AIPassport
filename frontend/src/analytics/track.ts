/**
 * Event tracking.
 *
 * Educational components call `trackEvent(...)`; nothing else. Events are queued and flushed in
 * batches so a slider drag never produces a request per tick, and the flush is best-effort: analytics
 * must never block or break a learner's work.
 */

import { eventApi, type EventPayload } from '@/api/endpoints';

export type EventType =
  | 'session_started'
  | 'session_ended'
  | 'module_opened'
  | 'module_completed'
  | 'page_viewed'
  | 'page_completed'
  | 'page_section_completed'
  | 'activity_started'
  | 'activity_completed'
  | 'activity_reset'
  | 'question_viewed'
  | 'question_answered'
  | 'prediction_submitted'
  | 'simulation_run'
  | 'parameter_changed'
  | 'hint_opened'
  | 'explanation_opened'
  | 'ai_tutor_opened'
  | 'ai_message_sent'
  | 'navigation';

export type EventContext = {
  moduleKey?: string;
  pageKey?: string;
  activityKey?: string;
  questionKey?: string;
  sectionId?: string;
};

const BATCH_SIZE = 25;
const FLUSH_INTERVAL_MS = 5000;
const MAX_QUEUE = 200;

let queue: EventPayload[] = [];
let flushTimer: number | null = null;
let learningSessionId: string | null = null;
let enabled = true;

export function setLearningSessionId(id: string | null): void {
  learningSessionId = id;
}

export function getLearningSessionId(): string | null {
  return learningSessionId;
}

/** Disabled for anonymous visitors and in unit tests. */
export function setTrackingEnabled(value: boolean): void {
  enabled = value;
  if (!enabled) queue = [];
}

function toPayload(
  type: EventType,
  context: EventContext = {},
  metadata: Record<string, unknown> = {},
): EventPayload {
  return {
    event_type: type,
    module_key: context.moduleKey,
    page_key: context.pageKey,
    activity_key: context.activityKey,
    question_key: context.questionKey,
    section_id: context.sectionId,
    metadata,
    client_ts: new Date().toISOString(),
  };
}

function scheduleFlush(): void {
  if (flushTimer !== null) return;
  flushTimer = window.setTimeout(() => {
    flushTimer = null;
    void flushEvents();
  }, FLUSH_INTERVAL_MS);
}

export function trackEvent(
  type: EventType,
  context: EventContext = {},
  metadata: Record<string, unknown> = {},
): void {
  if (!enabled) return;
  queue.push(toPayload(type, context, metadata));
  // Drop the oldest rather than growing without bound if the API is unreachable.
  if (queue.length > MAX_QUEUE) queue = queue.slice(-MAX_QUEUE);
  if (queue.length >= BATCH_SIZE) {
    void flushEvents();
  } else {
    scheduleFlush();
  }
}

export async function flushEvents(options: { keepalive?: boolean } = {}): Promise<void> {
  if (!enabled || queue.length === 0) return;
  const batch = queue.splice(0, BATCH_SIZE);
  try {
    const result = await eventApi.send(
      batch,
      learningSessionId ?? undefined,
      options.keepalive ?? false,
    );
    if (result.learning_session_id) learningSessionId = result.learning_session_id;
  } catch {
    // Re-queue once; if it fails again the events are dropped rather than retried forever.
    queue = [...batch.slice(-BATCH_SIZE), ...queue].slice(-MAX_QUEUE);
  }
}

/** Sends immediately, surviving page unload. */
export async function trackImmediate(
  type: EventType,
  context: EventContext = {},
  metadata: Record<string, unknown> = {},
): Promise<void> {
  if (!enabled) return;
  queue.push(toPayload(type, context, metadata));
  await flushEvents({ keepalive: true });
}

let lifecycleAttached = false;

export function attachLifecycleFlush(): () => void {
  if (lifecycleAttached) return () => undefined;
  lifecycleAttached = true;

  const onHidden = () => {
    if (document.visibilityState === 'hidden') void flushEvents({ keepalive: true });
  };
  const onPageHide = () => {
    void flushEvents({ keepalive: true });
  };

  document.addEventListener('visibilitychange', onHidden);
  window.addEventListener('pagehide', onPageHide);

  return () => {
    document.removeEventListener('visibilitychange', onHidden);
    window.removeEventListener('pagehide', onPageHide);
    lifecycleAttached = false;
  };
}

/** Test seam. */
export function __resetAnalytics(): void {
  queue = [];
  if (flushTimer !== null) window.clearTimeout(flushTimer);
  flushTimer = null;
  learningSessionId = null;
  enabled = true;
}

export function __queueLength(): number {
  return queue.length;
}
