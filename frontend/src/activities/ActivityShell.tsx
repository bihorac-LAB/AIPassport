import type { ReactNode } from 'react';
import { Badge } from '@/components/primitives';

export type ActivityProps = {
  activityKey: string;
  moduleKey: string;
  pageKey: string;
  sectionId: string;
  onComplete: () => void;
  completed: boolean;
};

export function ActivityShell({
  heading,
  intro,
  completed,
  children,
  footer,
}: {
  heading: string;
  intro?: string;
  completed?: boolean;
  children: ReactNode;
  footer?: ReactNode;
}) {
  return (
    // The visible heading is rendered by the page so the outline stays h1 → h2 with no duplicate;
    // aria-label keeps the card identifiable to assistive technology.
    <section className="activity" aria-label={heading}>
      {completed ? (
        <div className="activity__header">
          <p className="activity__title">{heading}</p>
          <Badge tone="success">✓ Completed</Badge>
        </div>
      ) : null}
      <div className="activity__body">
        {intro ? <p className="activity__intro">{intro}</p> : null}
        {children}
        {footer ? <div style={{ marginTop: 'var(--sp-5)' }}>{footer}</div> : null}
      </div>
    </section>
  );
}

/** Live region so a screen-reader user perceives a simulator update the way a sighted user does. */
export function LiveResult({ children }: { children: ReactNode }) {
  return (
    <div aria-live="polite" aria-atomic="true">
      {children}
    </div>
  );
}

export function PredictGate({
  question,
  options,
  value,
  onChange,
  revealed,
  onReveal,
}: {
  question: string;
  options: Array<{ value: string; label: string }>;
  value: string | null;
  onChange: (value: string) => void;
  revealed: boolean;
  onReveal: () => void;
}) {
  return (
    <fieldset className="choice-list" style={{ marginBottom: 'var(--sp-5)' }}>
      <legend className="choice-list__legend">{question}</legend>
      {options.map((option) => (
        <label className="choice" key={option.value}>
          <input
            type="radio"
            name={`predict-${question.slice(0, 20)}`}
            value={option.value}
            checked={value === option.value}
            disabled={revealed}
            onChange={() => onChange(option.value)}
          />
          <span className="choice__body">{option.label}</span>
        </label>
      ))}
      {!revealed ? (
        <button
          type="button"
          className="btn btn--primary"
          style={{ justifySelf: 'start', marginTop: 'var(--sp-2)' }}
          disabled={value === null}
          onClick={onReveal}
        >
          Lock in my prediction
        </button>
      ) : null}
    </fieldset>
  );
}
