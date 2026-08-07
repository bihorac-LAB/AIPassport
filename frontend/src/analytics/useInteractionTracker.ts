/**
 * Interaction tracking for simulators.
 *
 * The legacy Streamlit app re-ran the entire page (and would have logged an event) on every slider
 * tick. Here a drag produces at most one `parameter_changed` per 1500ms of quiet, plus one
 * `activity_completed` carrying the final parameter set and the total interaction count.
 */

import { useCallback, useEffect, useMemo, useRef } from 'react';
import { trackEvent, type EventContext } from './track';

const DEBOUNCE_MS = 1500;

export type InteractionTracker = {
  /** Emitted once when the learner first touches the activity. */
  start: () => void;
  /** Debounced; safe to call on every render of a controlled slider. */
  parameter: (name: string, value: number | string | boolean) => void;
  /** Immediate: a discrete, meaningful action. */
  run: (metadata?: Record<string, unknown>) => void;
  predict: (metadata?: Record<string, unknown>) => void;
  complete: (metadata?: Record<string, unknown>) => void;
  reset: () => void;
  interactionCount: () => number;
};

export function useInteractionTracker(
  activityKey: string,
  context: Omit<EventContext, 'activityKey'>,
): InteractionTracker {
  const started = useRef(false);
  const interactions = useRef(0);
  const pending = useRef<Record<string, number | string | boolean>>({});
  const timer = useRef<number | null>(null);

  const fullContext = useMemo<EventContext>(
    () => ({ ...context, activityKey }),
    [activityKey, context],
  );

  const flushParameters = useCallback(() => {
    timer.current = null;
    const params = pending.current;
    pending.current = {};
    if (Object.keys(params).length === 0) return;
    trackEvent('parameter_changed', fullContext, {
      parameters: params,
      interaction_count: interactions.current,
    });
  }, [fullContext]);

  const start = useCallback(() => {
    if (started.current) return;
    started.current = true;
    trackEvent('activity_started', fullContext);
  }, [fullContext]);

  const parameter = useCallback(
    (name: string, value: number | string | boolean) => {
      start();
      interactions.current += 1;
      pending.current[name] = value;
      if (timer.current !== null) window.clearTimeout(timer.current);
      timer.current = window.setTimeout(flushParameters, DEBOUNCE_MS);
    },
    [flushParameters, start],
  );

  const run = useCallback(
    (metadata: Record<string, unknown> = {}) => {
      start();
      trackEvent('simulation_run', fullContext, {
        ...metadata,
        interaction_count: interactions.current,
      });
    },
    [fullContext, start],
  );

  const predict = useCallback(
    (metadata: Record<string, unknown> = {}) => {
      start();
      trackEvent('prediction_submitted', fullContext, metadata);
    },
    [fullContext, start],
  );

  const complete = useCallback(
    (metadata: Record<string, unknown> = {}) => {
      if (timer.current !== null) {
        window.clearTimeout(timer.current);
        flushParameters();
      }
      trackEvent('activity_completed', fullContext, {
        ...metadata,
        interaction_count: interactions.current,
      });
    },
    [flushParameters, fullContext],
  );

  const reset = useCallback(() => {
    interactions.current = 0;
    trackEvent('activity_reset', fullContext);
  }, [fullContext]);

  // Flush any trailing parameter change when the learner navigates away mid-drag.
  useEffect(
    () => () => {
      if (timer.current !== null) {
        window.clearTimeout(timer.current);
        flushParameters();
      }
    },
    [flushParameters],
  );

  return useMemo(
    () => ({
      start,
      parameter,
      run,
      predict,
      complete,
      reset,
      interactionCount: () => interactions.current,
    }),
    [complete, parameter, predict, reset, run, start],
  );
}
