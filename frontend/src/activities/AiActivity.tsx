/**
 * AI-powered activity.
 *
 * The prompt, the model, and the credential all live on the backend. This component posts the
 * learner's input to `/ai/activity` and renders whatever comes back — either markdown-ish text or the
 * structured Fact-or-Fiction verdict.
 */

import { useState } from 'react';
import { ApiError } from '@/api/client';
import { aiApi } from '@/api/endpoints';
import type { FactOrFictionVerdict } from '@/api/types';
import { trackEvent } from '@/analytics/track';
import { Prose } from '@/components/Prose';
import { Button, Callout, Reveal, TextArea } from '@/components/primitives';
import { ActivityShell } from './ActivityShell';

type Props = {
  promptKey: string;
  heading: string;
  intro?: string;
  inputLabel: string;
  placeholder?: string;
  submitLabel?: string;
  render?: 'verdict';
  moduleKey: string;
  pageKey: string;
  sectionId: string;
  completed: boolean;
  onComplete: () => void;
};

const VERDICT_TONE: Record<string, 'success' | 'danger' | 'warning' | 'info'> = {
  FACT: 'success',
  'MOSTLY FACT': 'success',
  'CURRENTLY FACT': 'success',
  FICTION: 'danger',
  'MOSTLY FICTION': 'danger',
  'CURRENTLY FICTION': 'danger',
  MISLEADING: 'warning',
  'NOT A STATEMENT': 'warning',
};

function VerdictView({ verdict }: { verdict: FactOrFictionVerdict }) {
  const tone = VERDICT_TONE[verdict.verdict ?? ''] ?? 'info';
  const lists: Array<{ label: string; items: string[] | null }> = [
    { label: 'Real biomedical examples', items: verdict.examples },
    { label: 'Limitations and challenges', items: verdict.limitations },
    { label: 'AI concepts to know', items: verdict.concepts },
    { label: 'Relevant public datasets', items: verdict.datasets },
    { label: 'Research directions', items: verdict.research_directions },
    { label: 'Further reading', items: verdict.citations },
  ];

  return (
    <div>
      <Callout tone={tone} title={verdict.verdict ?? 'No verdict returned'}>
        {verdict.summary ? <Prose body={[verdict.summary]} /> : null}
        {verdict.correction ? (
          <p style={{ marginTop: 'var(--sp-3)' }}>
            <strong>A more accurate phrasing:</strong> {verdict.correction}
          </p>
        ) : null}
      </Callout>

      <div style={{ display: 'grid', gap: 'var(--sp-2)', marginTop: 'var(--sp-4)' }}>
        {lists
          .filter((entry) => entry.items && entry.items.length > 0)
          .map((entry) => (
            <Reveal key={entry.label} label={entry.label}>
              <ul>
                {(entry.items ?? []).map((item, index) => (
                  <li key={index} style={{ marginBottom: 'var(--sp-2)' }}>
                    {item}
                  </li>
                ))}
              </ul>
            </Reveal>
          ))}
      </div>
    </div>
  );
}

export function AiActivity(props: Props) {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [text, setText] = useState<string | null>(null);
  const [structured, setStructured] = useState<FactOrFictionVerdict | null>(null);
  const [error, setError] = useState<string | null>(null);

  const context = {
    moduleKey: props.moduleKey,
    pageKey: props.pageKey,
    sectionId: props.sectionId,
    activityKey: props.promptKey,
  };

  const submit = async () => {
    const trimmed = input.trim();
    if (trimmed.length < 10) {
      setError('Please write a little more — at least a full sentence.');
      return;
    }
    setLoading(true);
    setError(null);
    setText(null);
    setStructured(null);
    trackEvent('ai_message_sent', context, { prompt_key: props.promptKey, chars: trimmed.length });

    try {
      const result = await aiApi.activity({
        prompt_key: props.promptKey,
        input: trimmed,
        module_key: props.moduleKey,
        page_key: props.pageKey,
      });
      if (props.render === 'verdict' && result.structured) {
        setStructured(result.structured as FactOrFictionVerdict);
      } else if (result.content) {
        setText(result.content);
      } else if (result.structured) {
        setText(JSON.stringify(result.structured, null, 2));
      }
      props.onComplete();
    } catch (caught) {
      if (caught instanceof ApiError) {
        setError(
          caught.status === 429
            ? `You have reached the AI usage limit for now. ${caught.retryAfter ? `Try again in about ${Math.ceil(caught.retryAfter / 60)} minutes.` : 'Please try again later.'}`
            : caught.message,
        );
      } else {
        setError('Something went wrong reaching the AI service. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <ActivityShell heading={props.heading} intro={props.intro} completed={props.completed}>
      <Callout tone="neutral" title="Generated feedback">
        <p>
          This activity uses a generative model. Its output is a study aid, not an authority — read it
          critically, and verify anything you would act on or cite.
        </p>
      </Callout>

      <div style={{ marginTop: 'var(--sp-4)' }}>
        <TextArea
          label={props.inputLabel}
          placeholder={props.placeholder}
          rows={5}
          value={input}
          onChange={(event) => setInput(event.target.value)}
          disabled={loading}
        />
      </div>

      <div
        style={{
          display: 'flex',
          gap: 'var(--sp-3)',
          alignItems: 'center',
          marginTop: 'var(--sp-4)',
          flexWrap: 'wrap',
        }}
      >
        <Button variant="primary" loading={loading} onClick={() => void submit()}>
          {loading ? 'Thinking' : (props.submitLabel ?? 'Submit')}
        </Button>
        {error ? (
          <span className="field__error" role="alert">
            {error}
          </span>
        ) : null}
      </div>

      <div aria-live="polite" style={{ marginTop: 'var(--sp-5)' }}>
        {structured ? <VerdictView verdict={structured} /> : null}
        {text ? (
          <div className="panel">
            <Prose body={text.split('\n\n').filter(Boolean)} />
          </div>
        ) : null}
      </div>
    </ActivityShell>
  );
}
