import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type { Question } from '@/content/types';

const submit = vi.fn();
vi.mock('@/api/endpoints', () => ({
  responseApi: { submit: (...args: unknown[]) => submit(...args) },
  activityApi: { save: vi.fn() },
  eventApi: { send: vi.fn(async () => ({ accepted: 1, learning_session_id: null })) },
}));

import { QuestionBlock } from './QuestionBlock';

const SINGLE: Question = {
  key: 'test.q1',
  version: 3,
  type: 'single_choice',
  prompt: 'Is a hand-written threshold rule machine learning?',
  options: [
    { value: 'no', label: 'No — the rules were written by people.', feedback: 'Correct.' },
    { value: 'yes', label: 'Yes — it uses data.', feedback: 'Using data is not learning.' },
  ],
  correct: 'no',
  explanation: 'The dividing line is the origin of the rules.',
};

const FREE_TEXT: Question = {
  key: 'test.q2',
  version: 1,
  type: 'free_text',
  prompt: 'Describe one variable where an extreme value could be real.',
  minLength: 20,
};

function serverResponse(overrides: Record<string, unknown> = {}) {
  return {
    response: {
      id: 'r1',
      question_key: 'test.q1',
      question_version: 3,
      module_key: 'module-1',
      page_key: 'm1p1',
      attempt_no: 1,
      answer: { value: 'no' },
      is_final: true,
      is_correct: true,
      score: 1,
      created_at: new Date().toISOString(),
      ...overrides,
    },
    feedback: 'Correct.',
    explanation: 'The dividing line is the origin of the rules.',
    correct_answer: 'no',
  };
}

function renderQuestion(question: Question) {
  return render(
    <QuestionBlock
      question={question}
      moduleKey="module-1"
      pageKey="m1p1"
      sectionId="s1"
      onAnswered={vi.fn()}
    />,
  );
}

describe('QuestionBlock', () => {
  beforeEach(() => {
    submit.mockReset();
    submit.mockResolvedValue(serverResponse());
    window.localStorage.clear();
  });

  it('renders the prompt as a fieldset legend with native radios', () => {
    renderQuestion(SINGLE);
    expect(screen.getByRole('group', { name: /machine learning/i })).toBeInTheDocument();
    expect(screen.getAllByRole('radio')).toHaveLength(2);
  });

  it('does not submit until an option is chosen', async () => {
    const user = userEvent.setup();
    renderQuestion(SINGLE);
    await user.click(screen.getByRole('button', { name: /check my answer/i }));
    expect(submit).not.toHaveBeenCalled();
    expect(screen.getByRole('alert')).toHaveTextContent(/complete your answer/i);
  });

  it('submits the chosen value and shows the server feedback', async () => {
    const user = userEvent.setup();
    renderQuestion(SINGLE);
    await user.click(screen.getByRole('radio', { name: /written by people/i }));
    await user.click(screen.getByRole('button', { name: /check my answer/i }));

    await waitFor(() => expect(submit).toHaveBeenCalledTimes(1));
    const payload = submit.mock.calls[0]?.[0] as Record<string, unknown>;
    expect(payload.question_key).toBe('test.q1');
    expect(payload.answer).toEqual({ value: 'no' });
    expect(payload.idempotency_key).toBeTruthy();
    // The client never sends a user id.
    expect(payload).not.toHaveProperty('user_id');

    // Both the callout title and the option marker say "Correct", which is intentional:
    // the learner sees which option was right as well as whether they got it right.
    expect((await screen.findAllByText(/✓ Correct/)).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText(/origin of the rules/i)).toBeInTheDocument();
  });

  it('takes correctness from the server, not from the content file', async () => {
    submit.mockResolvedValue(serverResponse({ is_correct: false, attempt_no: 2 }));
    const user = userEvent.setup();
    renderQuestion(SINGLE);
    await user.click(screen.getByRole('radio', { name: /written by people/i }));
    await user.click(screen.getByRole('button', { name: /check my answer/i }));
    expect(await screen.findByText(/Not quite/)).toBeInTheDocument();
    expect(screen.getByText(/attempt 2/)).toBeInTheDocument();
  });

  it('allows another attempt after answering', async () => {
    const user = userEvent.setup();
    renderQuestion(SINGLE);
    await user.click(screen.getByRole('radio', { name: /written by people/i }));
    await user.click(screen.getByRole('button', { name: /check my answer/i }));
    const retry = await screen.findByRole('button', { name: /try again/i });
    await user.click(retry);
    expect(screen.getByRole('button', { name: /check my answer/i })).toBeInTheDocument();
  });

  it('restores a previously saved answer', () => {
    render(
      <QuestionBlock
        question={SINGLE}
        moduleKey="module-1"
        pageKey="m1p1"
        sectionId="s1"
        saved={serverResponse().response as never}
        onAnswered={vi.fn()}
      />,
    );
    expect(screen.getByRole('radio', { name: /written by people/i })).toBeChecked();
  });

  it('enforces the minimum length on a reflection before submitting', async () => {
    const user = userEvent.setup();
    renderQuestion(FREE_TEXT);
    const textarea = screen.getByRole('textbox');
    await user.type(textarea, 'too short');
    await user.click(screen.getByRole('button', { name: /save my response/i }));
    expect(submit).not.toHaveBeenCalled();
    expect(screen.getByText(/9 \/ 20 characters minimum/)).toBeInTheDocument();
  });

  it('labels the reflection button as a save, not a check', () => {
    renderQuestion(FREE_TEXT);
    expect(screen.getByRole('button', { name: /save my response/i })).toBeInTheDocument();
  });
});
