/**
 * Content model.
 *
 * Educational copy lives in these typed structures, never inside component JSX, so wording can be
 * revised without touching behavior. Question keys are stable forever and each question carries a
 * version so a stored response stays interpretable after the wording changes.
 */

export type Tone = 'info' | 'success' | 'warning' | 'danger' | 'neutral';

export type QuestionOption = {
  /** Stable within the question; never renumber. */
  value: string;
  label: string;
  /** Shown immediately after the learner picks this option. */
  feedback?: string;
};

export type QuestionKind =
  | 'single_choice'
  | 'multi_choice'
  | 'free_text'
  | 'numeric'
  | 'likert'
  | 'slider_estimate'
  | 'structured';

export type Question = {
  /** e.g. "m1p1.q2" — permanent identifier used by the API and analytics. */
  key: string;
  version: number;
  type: QuestionKind;
  prompt: string;
  help?: string;
  options?: QuestionOption[];
  /** Correct value(s) or accepted numeric range. Omit for ungraded reflection. */
  correct?: string | string[] | { min: number; max: number } | number;
  tolerance?: number;
  min?: number;
  max?: number;
  step?: number;
  unit?: string;
  scaleLabels?: [string, string];
  minLength?: number;
  placeholder?: string;
  rows?: number;
  fields?: Array<{ name: string; label: string; placeholder?: string; multiline?: boolean }>;
  requiredFields?: string[];
  explanation?: string;
  correctFeedback?: string;
  incorrectFeedback?: string;
};

export type Section =
  | { kind: 'prose'; id: string; heading?: string; summary?: string; body: string[] }
  | { kind: 'callout'; id: string; tone: Tone; heading: string; body: string[] }
  | { kind: 'reveal'; id: string; label: string; body: string[] }
  | { kind: 'question'; id: string; heading?: string; intro?: string; question: Question }
  | {
      kind: 'activity';
      id: string;
      activity: string;
      heading: string;
      intro?: string;
      summary?: string;
    }
  | {
      kind: 'aiActivity';
      id: string;
      promptKey: string;
      heading: string;
      intro?: string;
      inputLabel: string;
      placeholder?: string;
      submitLabel?: string;
      /** Renders the structured Fact-or-Fiction verdict instead of markdown-ish text. */
      render?: 'verdict';
    };

export type ModulePage = {
  /** e.g. "m1p1" */
  key: string;
  slug: string;
  position: 1 | 2;
  kind: 'explore' | 'apply';
  title: string;
  kicker: string;
  lede: string;
  objectives: string[];
  estimatedMinutes: number;
  contentVersion: number;
  /** Section ids that must be completed for the page to count as done. */
  requiredSections: string[];
  sections: Section[];
};

export type ModuleAccent = 'blue' | 'teal' | 'violet' | 'amber' | 'rose' | 'green' | 'slate';

export type Module = {
  /** e.g. "module-1" */
  key: string;
  position: number;
  title: string;
  subtitle: string;
  summary: string;
  accent: ModuleAccent;
  contentVersion: number;
  pages: [ModulePage, ModulePage];
};

/** Every section that a learner can "complete" contributes progress. */
export function completableSections(page: ModulePage): string[] {
  return page.sections
    .filter((section) => section.kind === 'question' || section.kind === 'activity' || section.kind === 'aiActivity')
    .map((section) => section.id);
}

export function pageQuestions(page: ModulePage): Question[] {
  return page.sections.flatMap((section) =>
    section.kind === 'question' ? [section.question] : [],
  );
}
