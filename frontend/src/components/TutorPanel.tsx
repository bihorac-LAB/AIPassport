/**
 * The AIP Guide.
 *
 * Redesigned from the legacy fixed 450px Streamlit column: a drawer at ≥1100px, a bottom sheet below
 * that, inside normal document flow so it works in a Canvas iframe. The learner's page context is
 * sent as keys — the backend resolves module/page/objectives from its own content registry, so this
 * component cannot inject instructions into the model.
 */

import { useEffect, useRef, useState } from 'react';
import { useLocation, useParams } from 'react-router-dom';
import { ApiError } from '@/api/client';
import { aiApi } from '@/api/endpoints';
import { trackEvent } from '@/analytics/track';
import { useUiStore } from '@/lib/store';
import { Button } from './primitives';
import { Prose } from './Prose';

type Message = { role: 'user' | 'assistant'; content: string };

const QUICK_ACTIONS = [
  { label: 'Explain this simply', prompt: 'Explain the main idea on this page in plain language.' },
  { label: 'How do I use this activity?', prompt: 'How do I use the activity on this page, and what should I be looking for?' },
  { label: 'Why does this matter?', prompt: 'Why does this concept matter in practice for someone in a clinical or research role?' },
];

export function TutorPanel() {
  const open = useUiStore((state) => state.tutorOpen);
  const setOpen = useUiStore((state) => state.setTutorOpen);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const params = useParams();
  const location = useLocation();
  const logRef = useRef<HTMLDivElement>(null);
  const panelRef = useRef<HTMLDivElement>(null);
  const toggleRef = useRef<HTMLButtonElement>(null);

  const moduleKey = params.moduleKey;
  const pageKey = params.pageKey;

  useEffect(() => {
    if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
  }, [messages, loading]);

  // Escape closes and returns focus to the toggle — no keyboard trap.
  useEffect(() => {
    if (!open) return;
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setOpen(false);
        toggleRef.current?.focus();
      }
    };
    document.addEventListener('keydown', onKeyDown);
    return () => document.removeEventListener('keydown', onKeyDown);
  }, [open, setOpen]);

  useEffect(() => {
    if (open) {
      trackEvent('ai_tutor_opened', { moduleKey, pageKey }, { path: location.pathname });
      panelRef.current?.querySelector('textarea')?.focus();
    }
  }, [location.pathname, moduleKey, open, pageKey]);

  const send = async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || loading) return;
    setInput('');
    setError(null);
    setMessages((prev) => [...prev, { role: 'user', content: trimmed }]);
    setLoading(true);
    trackEvent('ai_message_sent', { moduleKey, pageKey }, { chars: trimmed.length });

    try {
      const result = await aiApi.chat({
        message: trimmed,
        module_key: moduleKey,
        page_key: pageKey,
        history: messages.slice(-8),
        conversation_id: conversationId,
      });
      setConversationId(result.conversation_id);
      setMessages((prev) => [...prev, { role: 'assistant', content: result.content }]);
    } catch (caught) {
      const message =
        caught instanceof ApiError
          ? caught.status === 429
            ? 'You have reached the AI usage limit for now. Please try again later.'
            : caught.message
          : 'Could not reach the AI Guide. Please try again.';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  if (!open) {
    return (
      <button
        ref={toggleRef}
        type="button"
        className="tutor-toggle no-print"
        onClick={() => setOpen(true)}
        aria-expanded={false}
      >
        <span aria-hidden="true">✦</span> Ask the AIP Guide
      </button>
    );
  }

  return (
    <div
      className="tutor no-print"
      role="complementary"
      aria-label="AIP Guide"
      ref={panelRef}
    >
      <div className="tutor__header">
        <div>
          <p className="tutor__title">AIP Guide</p>
          <p className="tutor__subtitle">
            {pageKey ? 'Knows which page you are on' : 'Ask about anything in the course'}
          </p>
        </div>
        <div className="shell__spacer" />
        <Button
          size="sm"
          variant="ghost"
          aria-label="Close the AIP Guide"
          onClick={() => {
            setOpen(false);
            toggleRef.current?.focus();
          }}
        >
          ✕
        </Button>
      </div>

      <div className="tutor__log" ref={logRef} aria-live="polite">
        {messages.length === 0 ? (
          <div className="tutor__msg tutor__msg--assistant">
            <p>
              I can explain anything on this page, walk you through an activity, or connect a concept
              to your own work. I keep answers short.
            </p>
          </div>
        ) : null}
        {messages.map((message, index) => (
          <div
            key={index}
            className={`tutor__msg tutor__msg--${message.role}`}
          >
            <Prose body={message.content.split('\n\n').filter(Boolean)} />
          </div>
        ))}
        {loading ? (
          <div className="tutor__msg tutor__msg--assistant">
            <span className="spinner" aria-hidden="true" />
            <span className="sr-only">Thinking</span>
          </div>
        ) : null}
        {error ? (
          <div className="callout callout--warning" role="alert">
            {error}
          </div>
        ) : null}
      </div>

      {messages.length === 0 ? (
        <div className="tutor__quick">
          {QUICK_ACTIONS.map((action) => (
            <Button
              key={action.label}
              size="sm"
              variant="outline"
              onClick={() => void send(action.prompt)}
            >
              {action.label}
            </Button>
          ))}
        </div>
      ) : null}

      <form
        className="tutor__form"
        onSubmit={(event) => {
          event.preventDefault();
          void send(input);
        }}
      >
        <label className="sr-only" htmlFor="tutor-input">
          Ask the AIP Guide
        </label>
        <textarea
          id="tutor-input"
          className="textarea tutor__input"
          rows={1}
          placeholder="Ask a question…"
          value={input}
          maxLength={4000}
          onChange={(event) => setInput(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter' && !event.shiftKey) {
              event.preventDefault();
              void send(input);
            }
          }}
        />
        <Button type="submit" variant="primary" loading={loading} disabled={!input.trim()}>
          Send
        </Button>
      </form>
    </div>
  );
}
