import { useMemo, useState } from 'react';
import { BarChart } from '@/components/charts';
import { Prose } from '@/components/Prose';
import { Button, Callout, Metric, Reveal, Segmented, Slider } from '@/components/primitives';
import { SaveState } from '@/components/SaveState';
import { useActivityAutosave } from '@/api/useAutosave';
import { useInteractionTracker } from '@/analytics/useInteractionTracker';
import { ActivityShell, LiveResult, PredictGate, type ActivityProps } from './ActivityShell';
import { vitalsCohort } from './lib/cohorts';
import { fixed, iqrBounds, mean, median, sd, zScores } from './lib/math';

// ── Concept sorter ───────────────────────────────────────────────────────────

const SYSTEMS = [
  {
    id: 'apache',
    label: 'APACHE II severity score',
    detail: 'Points assigned to each vital sign by a published clinical formula.',
    answer: 'rules',
    why: 'Rule-based AI at most. The coefficients came from a statistical study, but the score itself is a fixed formula that does not learn from your patients.',
  },
  {
    id: 'sepsis-rf',
    label: 'Sepsis risk from a random forest',
    detail: 'Trained on 80,000 historical admissions with recorded outcomes.',
    answer: 'ml',
    why: 'Machine learning. The rules were derived from labelled examples, not written by a committee — and a forest is not a neural network, so not deep learning.',
  },
  {
    id: 'retina',
    label: 'Diabetic retinopathy screening from fundus photographs',
    detail: 'A convolutional network trained on 128,000 graded images.',
    answer: 'dl',
    why: 'Deep learning. A many-layered convolutional network learning directly from pixels — and therefore also machine learning, and also AI.',
  },
  {
    id: 'ddi',
    label: 'Drug-interaction alert in the EHR',
    detail: 'Fires when two drugs appear together in a curated interaction table.',
    answer: 'rules',
    why: 'Rule-based AI — arguably not AI at all, just a lookup. Nothing is learned. Notably, this is where most real clinical alert fatigue comes from.',
  },
  {
    id: 'logreg',
    label: 'Readmission risk from logistic regression',
    detail: 'Coefficients fitted to your own hospital\'s last three years of discharges.',
    answer: 'ml',
    why: 'Machine learning. Simple models are still machine learning — the defining feature is that the coefficients were learned from data, not chosen.',
  },
  {
    id: 'llm',
    label: 'A model that drafts discharge summaries',
    detail: 'A large language model predicting the next token from clinical notes.',
    answer: 'dl',
    why: 'Deep learning. Transformers are deep neural networks; the "generative" part describes what it is used for, not a different category.',
  },
] as const;

const LEVELS = [
  { value: 'rules', label: 'Rule-based AI' },
  { value: 'ml', label: 'Machine learning' },
  { value: 'dl', label: 'Deep learning' },
] as const;

export function ConceptSorter(props: ActivityProps) {
  const [choices, setChoices] = useState<Record<string, string>>({});
  const [checked, setChecked] = useState(false);
  const tracker = useInteractionTracker(props.activityKey, props);
  const { status, save } = useActivityAutosave(props.activityKey, props.moduleKey, props.pageKey);

  const correctCount = SYSTEMS.filter((system) => choices[system.id] === system.answer).length;
  const allAnswered = SYSTEMS.every((system) => choices[system.id]);

  return (
    <ActivityShell heading="Sort the systems" completed={props.completed}>
      <div style={{ display: 'grid', gap: 'var(--sp-3)' }}>
        {SYSTEMS.map((system) => {
          const choice = choices[system.id];
          const isRight = checked && choice === system.answer;
          const isWrong = checked && choice !== undefined && choice !== system.answer;
          return (
            <fieldset
              key={system.id}
              className="panel"
              style={{
                border: `1px solid ${isRight ? 'var(--success-border)' : isWrong ? 'var(--danger-border)' : 'var(--border)'}`,
                background: isRight
                  ? 'var(--success-soft)'
                  : isWrong
                    ? 'var(--danger-soft)'
                    : 'var(--bg-subtle)',
              }}
            >
              <legend style={{ fontWeight: 650, fontSize: 'var(--text-sm)', padding: '0 var(--sp-2)' }}>
                {system.label}
              </legend>
              <p style={{ fontSize: 'var(--text-sm)', color: 'var(--text-muted)', marginBottom: 'var(--sp-3)' }}>
                {system.detail}
              </p>
              <div style={{ display: 'flex', gap: 'var(--sp-2)', flexWrap: 'wrap' }}>
                {LEVELS.map((level) => (
                  <label
                    key={level.value}
                    className="choice"
                    style={{ flex: '1 1 8rem', padding: 'var(--sp-2) var(--sp-3)' }}
                  >
                    <input
                      type="radio"
                      name={`sorter-${system.id}`}
                      checked={choice === level.value}
                      disabled={checked}
                      onChange={() => {
                        setChoices((prev) => ({ ...prev, [system.id]: level.value }));
                        tracker.parameter(system.id, level.value);
                      }}
                    />
                    <span className="choice__body">{level.label}</span>
                  </label>
                ))}
              </div>
              {checked ? (
                <p style={{ fontSize: 'var(--text-sm)', marginTop: 'var(--sp-3)' }}>
                  <strong>{isRight ? '✓ ' : '✕ '}</strong>
                  {system.why}
                </p>
              ) : null}
            </fieldset>
          );
        })}
      </div>

      <div
        style={{
          display: 'flex',
          gap: 'var(--sp-3)',
          alignItems: 'center',
          marginTop: 'var(--sp-5)',
          flexWrap: 'wrap',
        }}
      >
        {!checked ? (
          <Button
            variant="primary"
            disabled={!allAnswered}
            onClick={() => {
              setChecked(true);
              tracker.complete({ correct: correctCount, total: SYSTEMS.length });
              save({ choices, correct: correctCount, total: SYSTEMS.length }, true);
              props.onComplete();
            }}
          >
            Check my answers
          </Button>
        ) : (
          <Button
            variant="outline"
            onClick={() => {
              setChecked(false);
              setChoices({});
              tracker.reset();
            }}
          >
            Reset
          </Button>
        )}
        <SaveState status={status} />
      </div>

      {checked ? (
        <LiveResult>
          <Callout
            tone={correctCount === SYSTEMS.length ? 'success' : 'info'}
            title={`${correctCount} of ${SYSTEMS.length} correct`}
          >
            <p>
              The test that resolves every one of these: <strong>where did the rules come from?</strong>{' '}
              Written by people → rule-based. Derived from labelled examples → machine learning.
              Derived by a many-layered network → deep learning.
            </p>
          </Callout>
        </LiveResult>
      ) : null}
    </ActivityShell>
  );
}

// ── AI timeline ──────────────────────────────────────────────────────────────

type Era = 'all' | 'symbolic' | 'ml' | 'deep' | 'generative';

const TIMELINE = [
  { year: 1950, era: 'symbolic', title: 'Turing proposes the imitation game', body: 'Turing asks whether a machine can produce behavior indistinguishable from a human\'s — reframing "can machines think" as an empirical question about observable output.' },
  { year: 1956, era: 'symbolic', title: 'The Dartmouth workshop', body: 'The term "artificial intelligence" is coined. The founding assumption — that intelligence can be captured in explicit symbolic rules — shapes the next thirty years.' },
  { year: 1966, era: 'symbolic', title: 'ELIZA', body: 'Weizenbaum\'s pattern-matching therapist convinces users it understands them. He is disturbed by this. The gap between apparent and actual understanding is now called the ELIZA effect.' },
  { year: 1972, era: 'symbolic', title: 'MYCIN', body: 'A rule-based system diagnoses blood infections at roughly specialist level — the first serious clinical AI. It is never deployed: maintaining the rules proves harder than writing them.' },
  { year: 1974, era: 'symbolic', title: 'The first AI winter', body: 'Funding collapses after the Lighthill report. The lesson that recurs: systems that work on curated problems do not survive contact with real-world variability.' },
  { year: 1986, era: 'ml', title: 'Backpropagation popularized', body: 'A practical way to train multi-layer networks. The idea that will dominate 2012 onward exists now — and lacks the data and compute to matter.' },
  { year: 1997, era: 'ml', title: 'Deep Blue beats Kasparov', body: 'A landmark for search and specialized hardware, not for learning. Deep Blue evaluated 200 million positions per second and learned nothing.' },
  { year: 2006, era: 'ml', title: 'Random forests and SVMs mature', body: 'Ensemble methods and kernel machines become the workhorses of applied prediction. On tabular clinical data they remain highly competitive today.' },
  { year: 2012, era: 'deep', title: 'AlexNet', body: 'A convolutional network halves the ImageNet error rate. The technique is from the 1980s; what is new is 1.2 million labelled images and two GPUs.' },
  { year: 2015, era: 'deep', title: 'Deep learning reaches medical imaging', body: 'Diabetic retinopathy, skin lesion, and chest radiograph models reach specialist-comparable accuracy on retrospective datasets — and expose how differently they behave prospectively.' },
  { year: 2017, era: 'deep', title: 'Attention and the transformer', body: 'A architecture that processes sequences in parallel rather than step by step. Every large language model in use today descends from this paper.' },
  { year: 2018, era: 'deep', title: 'AlphaFold', body: 'Protein structure prediction moves from a decades-old open problem to largely solved, changing the daily practice of structural biology.' },
  { year: 2020, era: 'generative', title: 'Large language models scale', body: 'Models trained only to predict the next token turn out to perform tasks they were never explicitly trained for. Capability now tracks scale more than architecture.' },
  { year: 2023, era: 'generative', title: 'Clinical LLM deployment begins', body: 'Ambient documentation and drafting tools enter hospitals at scale, arriving faster than the evaluation frameworks meant to assess them.' },
  { year: 2025, era: 'generative', title: 'Multimodal and agentic systems', body: 'Systems that combine text, images, and tool use in sequence. Evaluation, accountability, and regulation are all now behind capability.' },
] as const;

const ERAS: Array<{ value: Era; label: string }> = [
  { value: 'all', label: 'All' },
  { value: 'symbolic', label: 'Symbolic' },
  { value: 'ml', label: 'Machine learning' },
  { value: 'deep', label: 'Deep learning' },
  { value: 'generative', label: 'Generative' },
];

export function AiTimeline(props: ActivityProps) {
  const [era, setEra] = useState<Era>('all');
  const [open, setOpen] = useState<number | null>(1950);
  const tracker = useInteractionTracker(props.activityKey, props);

  const visible = TIMELINE.filter((item) => era === 'all' || item.era === era);
  const viewed = useMemo(() => new Set<number>(), []);

  return (
    <ActivityShell heading="The AI timeline" completed={props.completed}>
      <div style={{ marginBottom: 'var(--sp-5)' }}>
        <Segmented
          label="Filter by paradigm"
          value={era}
          options={ERAS}
          onChange={(value) => {
            setEra(value);
            tracker.parameter('era', value);
          }}
        />
      </div>

      <ol style={{ listStyle: 'none', margin: 0, padding: 0, borderLeft: '2px solid var(--border)' }}>
        {visible.map((item) => {
          const expanded = open === item.year;
          return (
            <li key={item.year} style={{ position: 'relative', paddingLeft: 'var(--sp-5)' }}>
              <span
                aria-hidden="true"
                style={{
                  position: 'absolute',
                  left: -6,
                  top: '1.1rem',
                  width: 10,
                  height: 10,
                  borderRadius: 999,
                  background: expanded ? 'var(--accent)' : 'var(--border-strong)',
                }}
              />
              <button
                type="button"
                aria-expanded={expanded}
                onClick={() => {
                  const next = expanded ? null : item.year;
                  setOpen(next);
                  if (next !== null && !viewed.has(next)) {
                    viewed.add(next);
                    tracker.parameter('milestone', next);
                    if (viewed.size >= 5) {
                      tracker.complete({ milestones_viewed: viewed.size });
                      props.onComplete();
                    }
                  }
                }}
                style={{
                  display: 'block',
                  width: '100%',
                  textAlign: 'left',
                  background: 'none',
                  border: 0,
                  padding: 'var(--sp-3) 0',
                  cursor: 'pointer',
                  color: 'inherit',
                }}
              >
                <span
                  style={{
                    fontFamily: 'var(--font-mono)',
                    fontSize: 'var(--text-xs)',
                    color: 'var(--accent)',
                    fontWeight: 700,
                  }}
                >
                  {item.year}
                </span>
                <span
                  style={{
                    display: 'block',
                    fontWeight: 650,
                    fontSize: 'var(--text-md)',
                    lineHeight: 1.35,
                  }}
                >
                  {item.title}
                </span>
              </button>
              {expanded ? (
                <p
                  style={{
                    fontSize: 'var(--text-sm)',
                    color: 'var(--text-muted)',
                    paddingBottom: 'var(--sp-4)',
                    maxWidth: '60ch',
                  }}
                >
                  {item.body}
                </p>
              ) : null}
            </li>
          );
        })}
      </ol>

      <Reveal label="What the shape of this timeline tells you" eventContext={props}>
        <Prose
          body={[
            'Two AI winters, both following the same pattern: a technique works on a curated problem, expectations outrun it, funding leaves.',
            'Every jump since 2012 has been driven by **more data and more compute** applied to ideas that already existed. That is the useful scepticism to carry into any vendor conversation: ask what changed, and whether it was the method or the scale.',
          ]}
        />
      </Reveal>
    </ActivityShell>
  );
}

// ── Lifecycle simulator ──────────────────────────────────────────────────────

type Stage = {
  id: string;
  title: string;
  prompt: string;
  options: Array<{ value: string; label: string; quality: 'good' | 'mixed' | 'poor'; consequence: string }>;
};

const STAGES: Stage[] = [
  {
    id: 'question',
    title: '1 · Define the question',
    prompt: 'Your hospital has high 30-day heart-failure readmission. What do you actually build?',
    options: [
      {
        value: 'actionable',
        label: 'Predict which patients would benefit from intensive discharge planning.',
        quality: 'good',
        consequence:
          'Strong. The prediction is tied to an action you can take, which means a positive result changes something. Ask next: do you have capacity to act on the flagged patients?',
      },
      {
        value: 'risk',
        label: 'Predict which patients will be readmitted within 30 days.',
        quality: 'mixed',
        consequence:
          'The standard framing, and publishable — but knowing who returns does not tell you what to do about it. Many such models are built, few change care.',
      },
      {
        value: 'vague',
        label: 'Use AI to reduce readmissions.',
        quality: 'poor',
        consequence:
          'Not yet a question. There is no defined outcome, population, or prediction, so there is nothing to validate and no way to fail.',
      },
    ],
  },
  {
    id: 'data',
    title: '2 · Assemble the data',
    prompt: 'Which data source do you use?',
    options: [
      {
        value: 'ehr_local',
        label: 'Your own EHR — 5 years, ~8,000 heart-failure admissions.',
        quality: 'good',
        consequence:
          'Right population, right documentation practices, and you can verify what each field means. The catch: 8,000 rows limits model complexity, so plan for a simple model.',
      },
      {
        value: 'public',
        label: 'A large public ICU dataset from other hospitals.',
        quality: 'mixed',
        consequence:
          'More rows, wrong population. Useful for pre-training or a sanity check, but a model trained here will need local validation before you believe anything.',
      },
      {
        value: 'claims',
        label: 'Insurance claims data across the region.',
        quality: 'mixed',
        consequence:
          'Excellent for capturing readmissions to *other* hospitals — a real blind spot in EHR-only studies. Weak on clinical detail, and coded for billing rather than for accuracy.',
      },
    ],
  },
  {
    id: 'outcome',
    title: '3 · Define the outcome variable',
    prompt: 'How exactly do you define "readmission"?',
    options: [
      {
        value: 'all_cause',
        label: 'Any unplanned admission within 30 days, any hospital, any cause.',
        quality: 'good',
        consequence:
          'Matches how readmission is measured for reporting and captures patients who go elsewhere. Requires the regional data linkage — worth the effort.',
      },
      {
        value: 'same_hospital',
        label: 'Any readmission to your hospital within 30 days.',
        quality: 'mixed',
        consequence:
          'Easy to compute and systematically undercounts. Patients who go elsewhere become false negatives, so your model learns that a whole group of returning patients did not return.',
      },
      {
        value: 'hf_only',
        label: 'Heart-failure-coded readmissions only.',
        quality: 'poor',
        consequence:
          'Narrow and coding-dependent. A patient readmitted with pneumonia precipitated by decompensation is exactly the case you wanted to catch, and this definition discards them.',
      },
    ],
  },
  {
    id: 'prep',
    title: '4 · Prepare the data',
    prompt: 'Lab values are missing for 22% of admissions. What do you do?',
    options: [
      {
        value: 'indicator',
        label: 'Impute, and add a "was this measured" indicator variable.',
        quality: 'good',
        consequence:
          'Best available answer. In clinical data whether a test was ordered is itself informative — often more so than its value. The indicator preserves that signal.',
      },
      {
        value: 'drop_rows',
        label: 'Drop admissions with missing labs.',
        quality: 'poor',
        consequence:
          'You just deleted 22% of your data, and not at random. The patients without labs are systematically different — usually less sick, sometimes just seen at night.',
      },
      {
        value: 'mean',
        label: 'Fill with the cohort mean.',
        quality: 'mixed',
        consequence:
          'Workable and it hides information. It also shrinks variance, which weakens any real association the variable has with the outcome.',
      },
    ],
  },
  {
    id: 'split',
    title: '5 · Split and validate',
    prompt: 'How do you construct the test set?',
    options: [
      {
        value: 'temporal_grouped',
        label: 'Train on years 1–4, test on year 5, keeping each patient in one split only.',
        quality: 'good',
        consequence:
          'This is the honest option. It mirrors deployment — a model trained on the past predicting the future — and prevents the same patient appearing on both sides.',
      },
      {
        value: 'random',
        label: 'Random 80/20 split of all admissions.',
        quality: 'poor',
        consequence:
          'Two leaks at once: the same patient can appear in both, and future information trains a model tested on the past. Expect an inflated score that will not reproduce.',
      },
      {
        value: 'cv',
        label: '10-fold cross-validation over all admissions.',
        quality: 'mixed',
        consequence:
          'A better variance estimate than a single split, with the same patient- and time-leakage problems unless you group and order the folds.',
      },
    ],
  },
  {
    id: 'deploy',
    title: '6 · Decide about deployment',
    prompt: 'Your model reaches AUC 0.74 on the held-out year. Now what?',
    options: [
      {
        value: 'silent',
        label: 'Run it silently for three months alongside current practice, then compare.',
        quality: 'good',
        consequence:
          'A silent trial is the strongest next step: you see prospective performance, alert volume, and calibration with no patient exposed to an unvalidated tool.',
      },
      {
        value: 'deploy',
        label: 'Deploy it to the discharge team now.',
        quality: 'poor',
        consequence:
          'AUC 0.74 on retrospective data is a weak basis for changing care. You do not yet know the alert volume, the PPV in practice, or whether the team can act on it.',
      },
      {
        value: 'abandon',
        label: 'Abandon it — 0.74 is not good enough.',
        quality: 'mixed',
        consequence:
          'Possibly correct, but check first: 0.74 may still beat current practice, which is the comparison that matters. "Not good enough" needs a comparator.',
      },
    ],
  },
];

export function LifecycleSimulator(props: ActivityProps) {
  const [choices, setChoices] = useState<Record<string, string>>({});
  const tracker = useInteractionTracker(props.activityKey, props);
  const { status, save } = useActivityAutosave(props.activityKey, props.moduleKey, props.pageKey);

  const answered = STAGES.filter((stage) => choices[stage.id]).length;
  const goodChoices = STAGES.filter((stage) => {
    const choice = choices[stage.id];
    return stage.options.find((option) => option.value === choice)?.quality === 'good';
  }).length;

  return (
    <ActivityShell heading="Run a study end to end" completed={props.completed}>
      <div className="meter" style={{ marginBottom: 'var(--sp-5)' }}>
        <div
          className="meter__fill"
          style={{ width: `${(answered / STAGES.length) * 100}%` }}
          role="progressbar"
          aria-valuenow={answered}
          aria-valuemin={0}
          aria-valuemax={STAGES.length}
          aria-label="Lifecycle decisions made"
        />
      </div>

      <div style={{ display: 'grid', gap: 'var(--sp-5)' }}>
        {STAGES.map((stage, index) => {
          const unlocked = index === 0 || Boolean(choices[STAGES[index - 1]?.id ?? '']);
          const choice = choices[stage.id];
          const selected = stage.options.find((option) => option.value === choice);
          if (!unlocked) {
            return (
              <div key={stage.id} className="placeholder">
                {stage.title} — complete the previous decision to continue
              </div>
            );
          }
          return (
            <fieldset key={stage.id} className="choice-list">
              <legend className="choice-list__legend">
                <span className="kicker" style={{ display: 'block', marginBottom: 4 }}>
                  {stage.title}
                </span>
                {stage.prompt}
              </legend>
              {stage.options.map((option) => (
                <label className="choice" key={option.value}>
                  <input
                    type="radio"
                    name={`lifecycle-${stage.id}`}
                    checked={choice === option.value}
                    onChange={() => {
                      const next = { ...choices, [stage.id]: option.value };
                      setChoices(next);
                      tracker.parameter(stage.id, option.value);
                      const good = STAGES.filter(
                        (s) =>
                          s.options.find((o) => o.value === next[s.id])?.quality === 'good',
                      ).length;
                      save({ choices: next, strong_choices: good }, false);
                      if (Object.keys(next).length === STAGES.length) {
                        tracker.complete({ strong_choices: good });
                        props.onComplete();
                      }
                    }}
                  />
                  <span className="choice__body">{option.label}</span>
                </label>
              ))}
              {selected ? (
                <LiveResult>
                  <Callout
                    tone={
                      selected.quality === 'good'
                        ? 'success'
                        : selected.quality === 'mixed'
                          ? 'warning'
                          : 'danger'
                    }
                    title={
                      selected.quality === 'good'
                        ? 'Strong choice'
                        : selected.quality === 'mixed'
                          ? 'Defensible, with a cost'
                          : 'This will cause a problem'
                    }
                  >
                    <p>{selected.consequence}</p>
                  </Callout>
                </LiveResult>
              ) : null}
            </fieldset>
          );
        })}
      </div>

      <div style={{ marginTop: 'var(--sp-5)', display: 'flex', gap: 'var(--sp-4)', alignItems: 'center' }}>
        <Metric label="Strong choices" value={`${goodChoices} / ${STAGES.length}`} />
        <SaveState status={status} />
      </div>
    </ActivityShell>
  );
}

// ── Split strategy ───────────────────────────────────────────────────────────

const SPLITS = [
  {
    value: 'random',
    label: 'Random 80/20',
    internal: 0.94,
    external: 0.71,
    why: 'The same patient, scanner, and month appear on both sides. The model can succeed by recognizing the setting, and your test set rewards it for doing so.',
  },
  {
    value: 'patient',
    label: 'Grouped by patient',
    internal: 0.9,
    external: 0.72,
    why: 'Closes the patient leak — a real improvement. Scanner and time still leak, so the internal number is still optimistic.',
  },
  {
    value: 'temporal',
    label: 'Train on years 1–2, test on year 3',
    internal: 0.85,
    external: 0.74,
    why: 'Mirrors deployment: past predicting future. It also exposes protocol changes over time, which a random split hides completely.',
  },
  {
    value: 'site',
    label: 'Hold out an entire hospital',
    internal: 0.79,
    external: 0.77,
    why: 'The lowest internal number and the only one close to the truth. Internal and external nearly agree, which is the property you actually want.',
  },
] as const;

export function SplitStrategy(props: ActivityProps) {
  const [selected, setSelected] = useState<string>('random');
  const [prediction, setPrediction] = useState<string | null>(null);
  const [revealed, setRevealed] = useState(false);
  const tracker = useInteractionTracker(props.activityKey, props);

  const current = SPLITS.find((split) => split.value === selected) ?? SPLITS[0];

  return (
    <ActivityShell heading="Split the data four ways" completed={props.completed}>
      <PredictGate
        question="Which splitting strategy will report the highest internal accuracy?"
        options={SPLITS.map((split) => ({ value: split.value, label: split.label }))}
        value={prediction}
        onChange={setPrediction}
        revealed={revealed}
        onReveal={() => {
          setRevealed(true);
          tracker.predict({ predicted: prediction });
        }}
      />

      {revealed ? (
        <>
          <Callout tone={prediction === 'random' ? 'success' : 'info'} title="The result">
            <p>
              {prediction === 'random'
                ? 'Correct — and notice that the highest internal score belongs to the worst method. A flattering number is a warning sign, not a result.'
                : 'The random split reports the highest internal accuracy (0.94) and the second-worst external accuracy. The highest internal number came from the weakest method.'}
            </p>
          </Callout>

          <div style={{ margin: 'var(--sp-5) 0' }}>
            <Segmented
              label="Splitting strategy"
              value={selected}
              options={SPLITS.map((split) => ({ value: split.value, label: split.label }))}
              onChange={(value) => {
                setSelected(value);
                tracker.parameter('split', value);
              }}
            />
          </div>

          <LiveResult>
            <BarChart
              title={`Internal vs. external accuracy — ${current.label}`}
              yLabel="Accuracy"
              yDomain={[0, 1]}
              bars={[
                { label: 'Reported (internal)', value: current.internal, color: 'var(--viz-2)' },
                { label: 'New hospital (external)', value: current.external, color: 'var(--viz-1)' },
              ]}
              valueFormat={(value) => value.toFixed(2)}
              caption="External accuracy is measured on a hospital that contributed no training data."
            />
            <Callout tone="neutral" title={`Gap: ${(current.internal - current.external).toFixed(2)}`}>
              <p>{current.why}</p>
            </Callout>
          </LiveResult>

          <div style={{ marginTop: 'var(--sp-5)' }}>
            <Button
              variant="primary"
              onClick={() => {
                tracker.complete({ final_split: selected });
                props.onComplete();
              }}
            >
              I have compared all four
            </Button>
          </div>
        </>
      ) : null}
    </ActivityShell>
  );
}

// ── Outlier lab ──────────────────────────────────────────────────────────────

type Handling = 'none' | 'remove' | 'winsorize' | 'median';
type Variable = 'heartRate' | 'map' | 'temperature';

const VARIABLES: Array<{ value: Variable; label: string; unit: string }> = [
  { value: 'heartRate', label: 'Heart rate', unit: 'bpm' },
  { value: 'map', label: 'Mean arterial pressure', unit: 'mmHg' },
  { value: 'temperature', label: 'Temperature', unit: '°C' },
];

const HANDLING: Array<{ value: Handling; label: string; note: string }> = [
  { value: 'none', label: 'Leave as is', note: 'The baseline. Outliers stay in the analysis.' },
  {
    value: 'remove',
    label: 'Remove the rows',
    note: 'Deletes those patients entirely — including the genuinely sick ones.',
  },
  {
    value: 'winsorize',
    label: 'Winsorize to the bound',
    note: 'Keeps the patient, caps the value. Preserves sample size and direction while limiting influence.',
  },
  {
    value: 'median',
    label: 'Replace with the median',
    note: 'Keeps the patient and erases the signal. Rarely the right choice for physiological extremes.',
  },
];

export function OutlierLab(props: ActivityProps) {
  const [variable, setVariable] = useState<Variable>('heartRate');
  const [multiplier, setMultiplier] = useState(1.5);
  const [handling, setHandling] = useState<Handling>('none');
  const tracker = useInteractionTracker(props.activityKey, props);
  const { status, save } = useActivityAutosave(props.activityKey, props.moduleKey, props.pageKey);

  const rows = useMemo(() => vitalsCohort(30, 42), []);
  const values = rows.map((row) => row[variable]);
  const bounds = iqrBounds(values, multiplier);
  const flagged = rows.filter(
    (row) => row[variable] < bounds.lower || row[variable] > bounds.upper,
  );

  const handled = useMemo(() => {
    switch (handling) {
      case 'remove':
        return values.filter((value) => value >= bounds.lower && value <= bounds.upper);
      case 'winsorize':
        return values.map((value) => Math.min(bounds.upper, Math.max(bounds.lower, value)));
      case 'median': {
        const inliers = values.filter((v) => v >= bounds.lower && v <= bounds.upper);
        const m = median(inliers);
        return values.map((value) =>
          value < bounds.lower || value > bounds.upper ? m : value,
        );
      }
      default:
        return values;
    }
  }, [bounds.lower, bounds.upper, handling, values]);

  const unit = VARIABLES.find((v) => v.value === variable)?.unit ?? '';

  return (
    <ActivityShell heading="Outlier handling lab" completed={props.completed}>
      <div className="activity__split">
        <div className="activity__controls">
          <Segmented
            label="Variable"
            value={variable}
            options={VARIABLES.map((v) => ({ value: v.value, label: v.label }))}
            onChange={(value) => {
              setVariable(value);
              tracker.parameter('variable', value);
            }}
          />
          <Slider
            label="IQR multiplier"
            value={multiplier}
            min={0.5}
            max={3}
            step={0.1}
            onChange={(value) => {
              setMultiplier(value);
              tracker.parameter('multiplier', value);
            }}
            hint={`Flags values below ${fixed(bounds.lower, 1)} or above ${fixed(bounds.upper, 1)} ${unit}. 1.5 is conventional; 3.0 is conservative.`}
          />
          <fieldset className="choice-list">
            <legend className="choice-list__legend" style={{ fontSize: 'var(--text-sm)' }}>
              Handling strategy
            </legend>
            {HANDLING.map((option) => (
              <label className="choice" key={option.value} style={{ padding: 'var(--sp-2) var(--sp-3)' }}>
                <input
                  type="radio"
                  name="handling"
                  checked={handling === option.value}
                  onChange={() => {
                    setHandling(option.value);
                    tracker.parameter('handling', option.value);
                    save(
                      {
                        variable,
                        multiplier,
                        handling: option.value,
                        flagged: flagged.length,
                      },
                      false,
                    );
                  }}
                />
                <span className="choice__body">
                  {option.label}
                  <span style={{ display: 'block', color: 'var(--text-faint)', fontSize: 'var(--text-xs)' }}>
                    {option.note}
                  </span>
                </span>
              </label>
            ))}
          </fieldset>
          <SaveState status={status} />
        </div>

        <div>
          <LiveResult>
            <div className="metric-row" style={{ marginBottom: 'var(--sp-4)' }}>
              <Metric label="Flagged" value={`${flagged.length} of ${rows.length}`} />
              <Metric
                label="Mean"
                value={`${fixed(mean(values), 1)} → ${fixed(mean(handled), 1)}`}
                note={unit}
              />
              <Metric
                label="Std. deviation"
                value={`${fixed(sd(values), 1)} → ${fixed(sd(handled), 1)}`}
                note={unit}
              />
              <Metric
                label="Median"
                value={`${fixed(median(values), 1)} → ${fixed(median(handled), 1)}`}
                note="barely moves"
              />
            </div>

            <BarChart
              title="Effect of handling on summary statistics"
              yLabel={unit}
              bars={[
                { label: 'Mean before', value: mean(values), color: 'var(--viz-6)' },
                { label: 'Mean after', value: mean(handled), color: 'var(--viz-1)' },
                { label: 'SD before', value: sd(values), color: 'var(--viz-6)' },
                { label: 'SD after', value: sd(handled), color: 'var(--viz-2)' },
              ]}
              valueFormat={(value) => value.toFixed(1)}
              caption="The standard deviation is far more sensitive to outliers than the median. That asymmetry is the whole reason this decision matters."
            />
          </LiveResult>

          {flagged.length > 0 ? (
            <div className="table-wrap" style={{ marginTop: 'var(--sp-4)' }}>
              <table className="data-table">
                <caption className="sr-only">Flagged patients</caption>
                <thead>
                  <tr>
                    <th scope="col">Patient</th>
                    <th scope="col" className="num">
                      Value
                    </th>
                    <th scope="col">Plausible?</th>
                  </tr>
                </thead>
                <tbody>
                  {flagged.map((row) => {
                    const value = row[variable];
                    const impossible =
                      (variable === 'heartRate' && (value < 20 || value > 220)) ||
                      (variable === 'map' && (value < 30 || value > 200)) ||
                      (variable === 'temperature' && (value < 30 || value > 43));
                    return (
                      <tr key={row.id}>
                        <th scope="row">#{row.id}</th>
                        <td className="num">
                          {value} {unit}
                        </td>
                        <td>
                          {impossible
                            ? '✕ Physiologically impossible — treat as missing'
                            : '✓ Possible — likely a genuinely sick patient'}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="placeholder" style={{ marginTop: 'var(--sp-4)' }}>
              No values flagged at this multiplier.
            </p>
          )}
        </div>
      </div>

      <div style={{ marginTop: 'var(--sp-5)' }}>
        <Button
          variant="primary"
          onClick={() => {
            tracker.complete({ variable, multiplier, handling, flagged: flagged.length });
            save({ variable, multiplier, handling, flagged: flagged.length }, true);
            props.onComplete();
          }}
        >
          I have compared the strategies
        </Button>
      </div>

      <div style={{ marginTop: 'var(--sp-4)' }}>
        <Reveal label="Why the same rule cannot serve both cases" eventContext={props}>
          <Prose
            body={[
              'The table above separates the two kinds of flagged value, and no statistical rule can do that for you. A heart rate of 2 is impossible; a heart rate of 168 is a patient in trouble. The IQR rule flags both identically.',
              'The defensible workflow: enforce a **clinical plausibility range** first and treat violations as missing; then use a statistical rule only to *review* the remainder, not to delete it; then report a sensitivity analysis.',
            ]}
          />
        </Reveal>
      </div>
    </ActivityShell>
  );
}

/** Small z-score demonstration reused by the Module 3 preprocessing activity. */
export function zScoreOutliers(values: number[], threshold: number) {
  const scores = zScores(values);
  return values.map((value, index) => ({
    value,
    z: scores[index] ?? 0,
    isOutlier: Math.abs(scores[index] ?? 0) > threshold,
  }));
}
