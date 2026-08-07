import { useState } from 'react';
import { Prose } from '@/components/Prose';
import { Button, Callout, Metric, Reveal, TextArea } from '@/components/primitives';
import { SaveState } from '@/components/SaveState';
import { useActivityAutosave } from '@/api/useAutosave';
import { useInteractionTracker } from '@/analytics/useInteractionTracker';
import { ActivityShell, type ActivityProps } from './ActivityShell';

const DESIGN_FIELDS = [
  {
    name: 'question',
    label: '1 · The question',
    hint: 'What decision would change if you knew the answer?',
    placeholder:
      'Which post-operative patients over 65 are at high enough delirium risk to justify a pre-emptive geriatrics consult?',
  },
  {
    name: 'data',
    label: '2 · The data',
    hint: 'What exists, for whom, how many, and does it actually contain the outcome?',
    placeholder:
      'Anaesthesia records 2018–2023, ~4,000 patients over 65. Delirium recorded via CAM-ICU in 62% of cases — the rest is a gap I need to address.',
  },
  {
    name: 'comparator',
    label: '3 · The comparator and baseline',
    hint: 'Current practice, plus the simple model you must beat. The most commonly missing piece.',
    placeholder:
      'Current practice: clinician gestalt at pre-op. Baseline: logistic regression on age, prior cognitive impairment, and surgery duration.',
  },
  {
    name: 'metric',
    label: '4 · The metric and operating point',
    hint: 'Which number matters, at what threshold, and why that threshold.',
    placeholder:
      'Sensitivity at a threshold that flags no more than 15% of patients — that is the consult capacity we actually have.',
  },
  {
    name: 'validation',
    label: '5 · The validation plan',
    hint: 'What would make you believe it generalizes?',
    placeholder:
      'Temporal split: train 2018–2022, test 2023. Then a silent prospective run for three months before any clinical use.',
  },
  {
    name: 'risk',
    label: '6 · The primary risk',
    hint: 'The most likely way this is wrong. Be honest here — it is the most useful field.',
    placeholder:
      'Delirium is under-documented, so my labels may be biased toward patients who were assessed at all. That could make the model predict assessment rather than delirium.',
  },
] as const;

export function StudyDesigner(props: ActivityProps) {
  const [fields, setFields] = useState<Record<string, string>>({});
  const tracker = useInteractionTracker(props.activityKey, props);
  const { status, save } = useActivityAutosave(props.activityKey, props.moduleKey, props.pageKey);

  const filled = DESIGN_FIELDS.filter((field) => (fields[field.name] ?? '').trim().length > 20).length;
  const hasComparator = (fields.comparator ?? '').trim().length > 20;

  return (
    <ActivityShell heading="Specify your study" completed={props.completed}>
      <div style={{ display: 'grid', gap: 'var(--sp-4)' }}>
        {DESIGN_FIELDS.map((field) => (
          <TextArea
            key={field.name}
            label={field.label}
            hint={field.hint}
            placeholder={field.placeholder}
            rows={3}
            value={fields[field.name] ?? ''}
            onChange={(event) => {
              const next = { ...fields, [field.name]: event.target.value };
              setFields(next);
              save(next, false);
              tracker.parameter(field.name, event.target.value.length);
            }}
          />
        ))}
      </div>

      <div
        style={{
          display: 'flex',
          gap: 'var(--sp-4)',
          alignItems: 'center',
          marginTop: 'var(--sp-5)',
          flexWrap: 'wrap',
        }}
      >
        <Metric
          label="Specified"
          value={`${filled} / ${DESIGN_FIELDS.length}`}
          tone={filled === DESIGN_FIELDS.length ? 'success' : undefined}
        />
        <Metric
          label="Comparator stated"
          value={hasComparator ? 'Yes' : 'Not yet'}
          tone={hasComparator ? 'success' : 'warning'}
        />
        <SaveState status={status} />
      </div>

      <div style={{ marginTop: 'var(--sp-4)' }}>
        <Button
          variant="primary"
          disabled={filled < 4}
          onClick={() => {
            tracker.complete({ fields_completed: filled, has_comparator: hasComparator });
            save(fields, true);
            props.onComplete();
          }}
        >
          {filled < 4 ? `Specify at least 4 elements (${filled}/4)` : 'Save my study design'}
        </Button>
      </div>

      {filled >= 4 && !hasComparator ? (
        <Callout tone="warning" title="The gap a reviewer will find first">
          <p>
            You have not stated a comparator or baseline. "Our model achieves AUC 0.85" invites the
            question <em>better than what?</em> — and it is the question that most often sinks an
            otherwise sound AI study. Fill in field 3 before you request the AI review below.
          </p>
        </Callout>
      ) : null}

      <div style={{ marginTop: 'var(--sp-4)' }}>
        <Reveal label="How specific is specific enough?" eventContext={props}>
          <Prose
            body={[
              '**Too vague:** "Use machine learning to improve outcomes." Nothing here can be validated, so nothing can fail.',
              '**Specific enough:** "Predict CAM-ICU-positive delirium within 72 hours of surgery in patients over 65, from pre-operative and intra-operative variables available at PACU arrival, compared against a logistic regression on three known risk factors, evaluated by sensitivity at a 15%-flag-rate threshold on a held-out year."',
              'The second version tells you exactly what would count as failure. That is the property that makes a design reviewable.',
            ]}
          />
        </Reveal>
      </div>
    </ActivityShell>
  );
}
