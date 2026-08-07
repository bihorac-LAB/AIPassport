import { beforeEach, describe, expect, it, vi } from 'vitest';

const send = vi.fn(
  async (_events: unknown[], _sessionId?: string, _keepalive?: boolean) => ({
    accepted: 1,
    learning_session_id: 'session-1',
  }),
);
// The factory is hoisted, so it must reference `send` lazily rather than capture it.
vi.mock('@/api/endpoints', () => ({
  eventApi: {
    send: (...args: Parameters<typeof send>) => send(...args),
  },
}));

import {
  __queueLength,
  __resetAnalytics,
  flushEvents,
  setLearningSessionId,
  setTrackingEnabled,
  trackEvent,
} from './track';

describe('analytics queue', () => {
  beforeEach(() => {
    __resetAnalytics();
    send.mockClear();
    vi.useRealTimers();
  });

  it('queues events instead of sending one request per call', () => {
    trackEvent('page_viewed', { moduleKey: 'module-1', pageKey: 'm1p1' });
    trackEvent('question_viewed', { questionKey: 'm1p1.q1' });
    expect(send).not.toHaveBeenCalled();
    expect(__queueLength()).toBe(2);
  });

  it('flushes automatically once the batch size is reached', () => {
    for (let i = 0; i < 25; i += 1) trackEvent('parameter_changed', {}, { i });
    expect(send).toHaveBeenCalledTimes(1);
  });

  it('sends the learning session id with the batch', async () => {
    setLearningSessionId('session-42');
    trackEvent('page_viewed');
    await flushEvents();
    expect(send).toHaveBeenCalledWith(expect.any(Array), 'session-42', false);
  });

  it('includes context and metadata on each event', async () => {
    trackEvent(
      'activity_completed',
      { moduleKey: 'module-4', pageKey: 'm4p1', activityKey: 'decision-boundary' },
      { final_k: 7 },
    );
    await flushEvents();
    const batch = (send.mock.calls[0]?.[0] ?? []) as Array<Record<string, unknown>>;
    expect(batch[0]).toMatchObject({
      event_type: 'activity_completed',
      module_key: 'module-4',
      page_key: 'm4p1',
      activity_key: 'decision-boundary',
      metadata: { final_k: 7 },
    });
    expect(batch[0]?.client_ts).toBeTypeOf('string');
  });

  it('drops events entirely when tracking is disabled for anonymous visitors', async () => {
    setTrackingEnabled(false);
    trackEvent('page_viewed');
    await flushEvents();
    expect(send).not.toHaveBeenCalled();
    expect(__queueLength()).toBe(0);
  });

  it('re-queues a failed batch rather than losing it', async () => {
    send.mockRejectedValueOnce(new Error('offline'));
    trackEvent('page_viewed');
    await flushEvents();
    expect(__queueLength()).toBe(1);
  });

  it('caps the queue so an unreachable API cannot grow memory without bound', () => {
    setTrackingEnabled(true);
    send.mockImplementation(async () => {
      throw new Error('offline');
    });
    for (let i = 0; i < 400; i += 1) trackEvent('navigation', {}, { i });
    expect(__queueLength()).toBeLessThanOrEqual(200);
  });
});
