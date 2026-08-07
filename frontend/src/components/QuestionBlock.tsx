/**
 * Renders any question type, submits it, and shows the server's feedback.
 *
 * Correctness comes from the API, not from the content file, so a learner cannot read the answer out
 * of the bundle before submitting.
 */

import { useCallback, useEffect, useId, useMemo, useRef, useState } from 'react';
import { trackEvent } from '@/analytics/track';
import { useResponseAutosave } from '@/api/useAutosave';
import type { ResponseRecord, ResponseResult } from '@/api/types';
import type { Question } from '@/content/types';
import { Button, Reveal, Slider } from './primitives';
import { Prose, inlineFormat } from './Prose';
import { SaveState } from './SaveState';

type Props = {
  question: Question;
  moduleKey: string;
  pageKey: string;
  sectionId: string;
  heading?: string;
  intro?: string;
  saved?: ResponseRecord;
  onAnswered: () => void;
};

type Answer = Record<string, unknown>;

function initialAnswer(question: Question, saved?: ResponseRecord): Answer {
  if (saved?.answer) return saved.answer as Answer;
  switch (question.type) {
    case 'multi_choice':
      return { values: [] };
    case 'free_text':
      return { text: '' };
    case 'numeric':
    case 'slider_estimate':
      return { value: question.min ?? 0 };
    case 'likert':
      return { value: Math.round(((question.min ?? 1) + (question.max ?? 5)) / 2) };
    case 'structured':
      return { fields: {} };
    default:
      return {};
  }
}

function isAnswerable(question: Question, answer: Answer): boolean {
  switch (question.type) {
    case 'single_choice':
      return typeof answer.value === 'string' && answer.value.length > 0;
    case 'multi_choice':
      return Array.isArray(answer.values) && answer.values.length > 0;
    case 'free_text': {
      const text = typeof answer.text === 'string' ? answer.text.trim() : '';
      return text.length >= (question.minLength ?? 1);
    }
    case 'structured': {
      const fields = (answer.fields ?? {}) as Record<string, unknown>;
      const required = question.requiredFields ?? [];
      return required.every((name) => {
        const value = fields[name];
        return typeof value === 'string' ? value.trim().length > 0 : value != null;
      });
    }
    default:
      return typeof answer.value === 'number';
  }
}

export function QuestionBlock({
  question,
  moduleKey,
  pageKey,
  sectionId,
  heading,
  intro,
  saved,
  onAnswered,
}: Props) {
  const [answer, setAnswer] = useState<Answer>(() => initialAnswer(question, saved));
  const [result, setResult] = useState<ResponseResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const startedAt = useRef(Date.now());
  const viewed = useRef(false);
  const touched = useRef(false);
  const adoptedAttempt = useRef(saved?.attempt_no ?? null);
  const groupName = useId();

  // The saved response is fetched asynchronously, so it usually arrives after first render.
  // Adopt it then — but never overwrite an answer the learner has already started editing.
  useEffect(() => {
    if (!saved || touched.current) return;
    if (adoptedAttempt.current === saved.attempt_no) return;
    adoptedAttempt.current = saved.attempt_no;
    setAnswer(saved.answer as Answer);
  }, [saved]);

  const context = useMemo(
    () => ({ moduleKey, pageKey, sectionId, questionKey: question.key }),
    [moduleKey, pageKey, question.key, sectionId],
  );

  useEffect(() => {
    if (viewed.current) return;
    viewed.current = true;
    trackEvent('question_viewed', context, { type: question.type });
  }, [context, question.type]);

  const { status, save } = useResponseAutosave(question.key, {
    onSaved: (submitted) => {
      setResult(submitted);
      setError(null);
      trackEvent('question_answered', context, {
        attempt: submitted.response.attempt_no,
        is_correct: submitted.response.is_correct,
      });
      onAnswered();
    },
  });

  const updateAnswer = useCallback((next: Answer) => {
    touched.current = true;
    setAnswer(next);
  }, []);

  const submit = useCallback(() => {
    if (!isAnswerable(question, answer)) {
      setError('Please complete your answer before submitting.');
      return;
    }
    setError(null);
    save(answer, startedAt.current, true);
  }, [answer, question, save]);

  // Free text is a reflection, not a quiz: autosave as they type, with an explicit submit as well.
  const autosaveText = useCallback(
    (text: string) => {
      touched.current = true;
      setAnswer({ text });
      if (text.trim().length >= (question.minLength ?? 1)) {
        save({ text }, startedAt.current);
      }
    },
    [question.minLength, save],
  );

  const answered = result !== null;
  const graded = question.correct !== undefined;
  const correct = result?.response.is_correct ?? null;

  return (
    <div>
      {heading ? <h3 className="section__heading">{heading}</h3> : null}
      {intro ? (
        <p style={{ color: 'var(--text-muted)', marginBottom: 'var(--sp-4)', maxWidth: '68ch' }}>
          {inlineFormat(intro)}
        </p>
      ) : null}

      <div className="card">
        {question.type === 'single_choice' ? (
          <fieldset className="choice-list">
            <legend className="choice-list__legend">{inlineFormat(question.prompt)}</legend>
            {(question.options ?? []).map((option) => {
              const selected = answer.value === option.value;
              const isCorrectOption =
                answered && typeof question.correct === 'string' && option.value === question.correct;
              const wrongSelection = answered && selected && correct === false;
              const modifier = isCorrectOption
                ? ' choice--correct'
                : wrongSelection
                  ? ' choice--incorrect'
                  : '';
              return (
                <label className={`choice${modifier}`} key={option.value}>
                  <input
                    type="radio"
                    name={groupName}
                    value={option.value}
                    checked={selected}
                    disabled={answered}
                    onChange={() => updateAnswer({ value: option.value })}
                  />
                  <span className="choice__body">{inlineFormat(option.label)}</span>
                  {isCorrectOption ? (
                    <span className="choice__marker" style={{ color: 'var(--success)' }}>
                      ✓ Correct
                    </span>
                  ) : wrongSelection ? (
                    <span className="choice__marker" style={{ color: 'var(--danger)' }}>
                      ✕ Your answer
                    </span>
                  ) : null}
                </label>
              );
            })}
          </fieldset>
        ) : null}

        {question.type === 'multi_choice' ? (
          <fieldset className="choice-list">
            <legend className="choice-list__legend">{inlineFormat(question.prompt)}</legend>
            {(question.options ?? []).map((option) => {
              const values = (answer.values as string[]) ?? [];
              const selected = values.includes(option.value);
              const expected = Array.isArray(question.correct) ? question.correct : [];
              const shouldBeSelected = answered && expected.includes(option.value);
              const wrongSelection = answered && selected && !expected.includes(option.value);
              const modifier = shouldBeSelected
                ? ' choice--correct'
                : wrongSelection
                  ? ' choice--incorrect'
                  : '';
              return (
                <label className={`choice${modifier}`} key={option.value}>
                  <input
                    type="checkbox"
                    value={option.value}
                    checked={selected}
                    disabled={answered}
                    onChange={() =>
                      updateAnswer({
                        values: selected
                          ? values.filter((v) => v !== option.value)
                          : [...values, option.value],
                      })
                    }
                  />
                  <span className="choice__body">{inlineFormat(option.label)}</span>
                  {shouldBeSelected ? (
                    <span className="choice__marker" style={{ color: 'var(--success)' }}>
                      ✓ Should be selected
                    </span>
                  ) : wrongSelection ? (
                    <span className="choice__marker" style={{ color: 'var(--danger)' }}>
                      ✕ Not this one
                    </span>
                  ) : null}
                </label>
              );
            })}
          </fieldset>
        ) : null}

        {question.type === 'free_text' ? (
          <div>
            <label
              className="field__label"
              htmlFor={`${groupName}-text`}
              style={{ fontSize: 'var(--text-md)', marginBottom: 'var(--sp-3)' }}
            >
              {inlineFormat(question.prompt)}
            </label>
            <textarea
              id={`${groupName}-text`}
              className="textarea"
              rows={question.rows ?? 5}
              placeholder={question.placeholder}
              value={(answer.text as string) ?? ''}
              onChange={(event) => autosaveText(event.target.value)}
            />
            {question.minLength ? (
              <p className="field__hint">
                {((answer.text as string) ?? '').trim().length} / {question.minLength} characters
                minimum
              </p>
            ) : null}
          </div>
        ) : null}

        {question.type === 'slider_estimate' || question.type === 'numeric' ? (
          <div>
            <p
              className="choice-list__legend"
              style={{ marginBottom: 'var(--sp-4)', maxWidth: '68ch' }}
            >
              {inlineFormat(question.prompt)}
            </p>
            <Slider
              label="Your estimate"
              value={(answer.value as number) ?? question.min ?? 0}
              min={question.min ?? 0}
              max={question.max ?? 100}
              step={question.step ?? 1}
              unit={question.unit}
              disabled={answered}
              onChange={(value) => updateAnswer({ value })}
            />
          </div>
        ) : null}

        {question.type === 'likert' ? (
          <fieldset className="choice-list">
            <legend className="choice-list__legend">{inlineFormat(question.prompt)}</legend>
            <div style={{ display: 'flex', gap: 'var(--sp-2)', flexWrap: 'wrap' }}>
              {Array.from(
                { length: (question.max ?? 5) - (question.min ?? 1) + 1 },
                (_, i) => (question.min ?? 1) + i,
              ).map((point) => (
                <label
                  className="choice"
                  key={point}
                  style={{ flexDirection: 'column', alignItems: 'center', minWidth: '4rem' }}
                >
                  <input
                    type="radio"
                    name={groupName}
                    checked={answer.value === point}
                    disabled={answered}
                    onChange={() => updateAnswer({ value: point })}
                  />
                  <span className="choice__body">{point}</span>
                </label>
              ))}
            </div>
            {question.scaleLabels ? (
              <p className="field__hint">
                {question.scaleLabels[0]} → {question.scaleLabels[1]}
              </p>
            ) : null}
          </fieldset>
        ) : null}

        <div
          style={{
            display: 'flex',
            gap: 'var(--sp-3)',
            alignItems: 'center',
            flexWrap: 'wrap',
            marginTop: 'var(--sp-5)',
          }}
        >
          {!answered ? (
            <Button variant="primary" onClick={submit}>
              {graded ? 'Check my answer' : 'Save my response'}
            </Button>
          ) : (
            <Button
              variant="outline"
              onClick={() => {
                setResult(null);
                touched.current = false;
                setAnswer(initialAnswer(question));
                startedAt.current = Date.now();
              }}
            >
              Try again
            </Button>
          )}
          <SaveState status={status} />
          {error ? (
            <span className="field__error" role="alert">
              {error}
            </span>
          ) : null}
        </div>

        {answered ? (
          <div
            className={`callout callout--${correct === true ? 'success' : correct === false ? 'warning' : 'info'}`}
            style={{ marginTop: 'var(--sp-4)' }}
          >
            {graded ? (
              <p className="callout__title">
                {correct === true ? '✓ Correct' : '✕ Not quite'}
                {result?.response.attempt_no && result.response.attempt_no > 1
                  ? ` · attempt ${result.response.attempt_no}`
                  : ''}
              </p>
            ) : (
              <p className="callout__title">Response saved</p>
            )}
            {result?.feedback ? <Prose body={[result.feedback]} /> : null}
            {result?.explanation ? (
              <div style={{ marginTop: 'var(--sp-3)' }}>
                <Prose body={[result.explanation]} />
              </div>
            ) : null}
          </div>
        ) : null}

        {question.help ? (
          <div style={{ marginTop: 'var(--sp-4)' }}>
            <Reveal label="Hint" eventContext={context}>
              <Prose body={[question.help]} />
            </Reveal>
          </div>
        ) : null}
      </div>
    </div>
  );
}
