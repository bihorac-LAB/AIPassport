import { useMemo, useState } from 'react';
import { BarChart, Histogram } from '@/components/charts';
import { Prose } from '@/components/Prose';
import { Button, Callout, Metric, Reveal, Segmented, Slider } from '@/components/primitives';
import { SaveState } from '@/components/SaveState';
import { useActivityAutosave } from '@/api/useAutosave';
import { useInteractionTracker } from '@/analytics/useInteractionTracker';
import { ActivityShell, LiveResult, type ActivityProps } from './ActivityShell';
import { clamp, cohenKappa, fixed, mean, median, percent, rng, sd, zScores } from './lib/math';

// ── Consent rewriter ─────────────────────────────────────────────────────────

const CONSENT_LEVELS = [
  {
    value: 'legal',
    label: 'Legal standard',
    text:
      'The undersigned participant hereby grants irrevocable permission for the indefinite utilization of biological specimens and associated metadata, waiving all rights to pecuniary gain arising therefrom, and acknowledges that derived data may be disseminated to third-party entities at the discretion of the Principal Investigator.',
    reading: 'Graduate level (approx. grade 17)',
    comprehension: 0.18,
    verdict: 'fail' as const,
    finding:
      'A participant who signs this has documented consent without giving informed consent. They cannot state what they agreed to, so the ethical requirement is unmet even though the legal one is satisfied.',
  },
  {
    value: 'standard',
    label: 'Plain but transactional',
    text:
      'You agree to let researchers use your samples and health data for future research. You will not receive payment. Your data may be shared with other researchers. You may withdraw at any time by contacting the study team.',
    reading: 'Approximately grade 11',
    comprehension: 0.58,
    verdict: 'partial' as const,
    finding:
      'Readable, and still transactional — it tells the participant what they are giving up without telling them why it matters or what happens next. Withdrawal is mentioned but not explained.',
  },
  {
    value: 'plain',
    label: 'Plain and empowering',
    text:
      'We are asking permission to use your sample to help researchers understand this disease. Here is what that means: your sample will be stored with a code, not your name. Other researchers may use it, and we will tell you what we learn. Saying no will not affect your care in any way. You can change your mind later — email us or call the number on this page, and we will stop using your sample. Ask us anything before you decide.',
    reading: 'Approximately grade 7',
    comprehension: 0.89,
    verdict: 'pass' as const,
    finding:
      'Compliant. The participant knows what happens to the sample, that refusal is costless, how to withdraw, and that they will hear back. Consent is now a decision rather than a signature.',
  },
] as const;

export function ConsentRewriter(props: ActivityProps) {
  const [level, setLevel] = useState<string>('legal');
  const tracker = useInteractionTracker(props.activityKey, props);
  const current = CONSENT_LEVELS.find((entry) => entry.value === level) ?? CONSENT_LEVELS[0];

  return (
    <ActivityShell heading="Audit 1 · Consent as comprehension" completed={props.completed}>
      <Segmented
        label="Language level"
        value={level}
        options={CONSENT_LEVELS.map((entry) => ({ value: entry.value, label: entry.label }))}
        onChange={(value) => {
          setLevel(value);
          tracker.parameter('level', value);
        }}
      />

      <LiveResult>
        <div className="panel" style={{ margin: 'var(--sp-4) 0' }}>
          <p className="kicker">What the participant reads</p>
          <p style={{ marginTop: 'var(--sp-2)', fontSize: 'var(--text-sm)', lineHeight: 1.65 }}>
            {current.text}
          </p>
        </div>

        <div className="metric-row">
          <Metric label="Reading level" value={current.reading.split('(')[0]?.trim() ?? ''} />
          <Metric
            label="Understood what they agreed to"
            value={percent(current.comprehension)}
            tone={current.verdict === 'pass' ? 'success' : current.verdict === 'partial' ? 'warning' : 'danger'}
          />
          <Metric
            label="Audit verdict"
            value={current.verdict === 'pass' ? 'Pass' : current.verdict === 'partial' ? 'Partial' : 'Fail'}
            tone={current.verdict === 'pass' ? 'success' : current.verdict === 'partial' ? 'warning' : 'danger'}
          />
        </div>

        <Callout
          tone={current.verdict === 'pass' ? 'success' : current.verdict === 'partial' ? 'warning' : 'danger'}
          title="Audit finding"
        >
          <p>{current.finding}</p>
        </Callout>
      </LiveResult>

      <div style={{ marginTop: 'var(--sp-5)' }}>
        <Button
          variant="primary"
          onClick={() => {
            tracker.complete({ final_level: level });
            props.onComplete();
          }}
        >
          I have compared all three
        </Button>
      </div>
    </ActivityShell>
  );
}

// ── Representation planner ───────────────────────────────────────────────────

const STRATEGIES = [
  {
    id: 'liaisons',
    label: 'Community liaisons',
    gain: 14,
    cost: 'Requires salaried positions and 6+ months of relationship-building before recruitment starts.',
  },
  {
    id: 'translation',
    label: 'Translated materials and interpreters',
    gain: 8,
    cost: 'Modest cost; needs certified medical translation, not machine translation.',
  },
  {
    id: 'logistics',
    label: 'Transport, childcare, or a mobile clinic',
    gain: 13,
    cost: 'The most expensive option and the one that removes the most real barriers.',
  },
  {
    id: 'hours',
    label: 'Evening and weekend appointments',
    gain: 9,
    cost: 'Staffing cost; reaches people who cannot take unpaid time off work.',
  },
  {
    id: 'compensation',
    label: 'Compensation for time and travel',
    gain: 7,
    cost: 'Needs IRB review — must compensate without becoming coercive.',
  },
] as const;

export function RepresentationPlanner(props: ActivityProps) {
  const [target, setTarget] = useState(30);
  const [selected, setSelected] = useState<string[]>([]);
  const tracker = useInteractionTracker(props.activityKey, props);
  const { status, save } = useActivityAutosave(props.activityKey, props.moduleKey, props.pageKey);

  const baseline = 5;
  const achieved =
    baseline +
    STRATEGIES.filter((strategy) => selected.includes(strategy.id)).reduce(
      (sum, strategy) => sum + strategy.gain,
      0,
    );
  const met = achieved >= target;

  return (
    <ActivityShell heading="Audit 2 · Who is missing" completed={props.completed}>
      <div className="activity__split">
        <div className="activity__controls">
          <Callout tone="warning" title="Baseline: passive recruitment">
            <p>
              An email to the patient portal reaches <strong>5%</strong> representation from the
              under-served group — well below their 24% share of the catchment population.
            </p>
          </Callout>

          <Slider
            label="Representation target"
            value={target}
            min={5}
            max={60}
            step={1}
            unit="%"
            onChange={(value) => {
              setTarget(value);
              tracker.parameter('target', value);
            }}
            hint="Set this from the statistical power you need for subgroup analysis, not from what feels achievable."
          />

          <fieldset className="choice-list">
            <legend className="choice-list__legend" style={{ fontSize: 'var(--text-sm)' }}>
              Active strategies
            </legend>
            {STRATEGIES.map((strategy) => (
              <label className="choice" key={strategy.id} style={{ padding: 'var(--sp-2) var(--sp-3)' }}>
                <input
                  type="checkbox"
                  checked={selected.includes(strategy.id)}
                  onChange={() => {
                    const next = selected.includes(strategy.id)
                      ? selected.filter((id) => id !== strategy.id)
                      : [...selected, strategy.id];
                    setSelected(next);
                    tracker.parameter(strategy.id, !selected.includes(strategy.id));
                    save({ target, strategies: next, achieved }, false);
                  }}
                />
                <span className="choice__body">
                  {strategy.label} <span style={{ color: 'var(--success)' }}>+{strategy.gain}%</span>
                  <span
                    style={{
                      display: 'block',
                      color: 'var(--text-faint)',
                      fontSize: 'var(--text-xs)',
                      marginTop: 2,
                    }}
                  >
                    {strategy.cost}
                  </span>
                </span>
              </label>
            ))}
          </fieldset>
          <SaveState status={status} />
        </div>

        <div>
          <LiveResult>
            <BarChart
              title="Projected representation"
              yLabel="% of sample from the under-served group"
              yDomain={[0, 70]}
              bars={[
                { label: 'Passive only', value: baseline, color: 'var(--viz-6)' },
                {
                  label: 'With your strategies',
                  value: achieved,
                  color: met ? 'var(--viz-3)' : 'var(--viz-2)',
                },
              ]}
              referenceLine={{ value: target, label: `Target ${target}%` }}
              valueFormat={(value) => `${value.toFixed(0)}%`}
            />
            <Callout tone={met ? 'success' : 'warning'} title={met ? 'Target reached' : 'Target not reached'}>
              <p>
                {met
                  ? `Your plan projects ${achieved}% representation. Now the honest question: is every strategy you selected actually funded in the budget, or aspirational?`
                  : `Your plan reaches ${achieved}% against a ${target}% target. Add strategies, or lower the target and state plainly in the protocol that subgroup analysis will be underpowered.`}
              </p>
            </Callout>
          </LiveResult>
        </div>
      </div>

      <div style={{ marginTop: 'var(--sp-5)' }}>
        <Button
          variant="primary"
          disabled={selected.length === 0}
          onClick={() => {
            tracker.complete({ target, achieved, strategies: selected.length });
            save({ target, strategies: selected, achieved }, true);
            props.onComplete();
          }}
        >
          Save my recruitment plan
        </Button>
      </div>
    </ActivityShell>
  );
}

// ── Security audit ───────────────────────────────────────────────────────────

const LAYERS = [
  {
    id: 'transit',
    label: 'Encryption in transit (TLS)',
    essential: true,
    addresses: 'Interception on the network.',
    residual: 'Does nothing once the data is at rest on a server or laptop.',
  },
  {
    id: 'rest',
    label: 'Encryption at rest',
    essential: true,
    addresses: 'A stolen laptop or a decommissioned disk.',
    residual: 'Useless against an attacker who has valid application credentials.',
  },
  {
    id: 'access',
    label: 'Role-based access control with least privilege',
    essential: true,
    addresses: 'Curiosity browsing and lateral movement after one account is compromised.',
    residual: 'Requires someone to actually review the roles; they drift over years.',
  },
  {
    id: 'audit',
    label: 'Immutable audit logging',
    essential: true,
    addresses: 'Detecting misuse and proving what happened afterwards.',
    residual: 'Detects rather than prevents, and only if someone reads the logs.',
  },
  {
    id: 'deid',
    label: 'De-identification before analysis',
    essential: true,
    addresses: 'Limits the damage of every other control failing.',
    residual: 'Free-text notes and rare diagnoses can re-identify even after names are removed.',
  },
  {
    id: 'mfa',
    label: 'Multi-factor authentication',
    essential: true,
    addresses: 'Credential theft and phishing — the most common real breach route.',
    residual: 'Push-fatigue attacks still work against inattentive users.',
  },
  {
    id: 'airgap',
    label: 'Fully air-gapped analysis enclave',
    essential: false,
    addresses: 'Exfiltration by a determined insider.',
    residual: 'Proportionate for genomic or highly sensitive data; for most projects it blocks the science without adding much protection.',
  },
] as const;

export function SecurityAudit(props: ActivityProps) {
  const [selected, setSelected] = useState<string[]>([]);
  const tracker = useInteractionTracker(props.activityKey, props);

  const essentials = LAYERS.filter((layer) => layer.essential);
  const covered = essentials.filter((layer) => selected.includes(layer.id)).length;
  const passing = covered === essentials.length;

  return (
    <ActivityShell heading="Audit 3 · Protecting the data" completed={props.completed}>
      <fieldset className="choice-list">
        <legend className="choice-list__legend">Select the protections this protocol needs</legend>
        {LAYERS.map((layer) => {
          const on = selected.includes(layer.id);
          return (
            <label className="choice" key={layer.id}>
              <input
                type="checkbox"
                checked={on}
                onChange={() => {
                  const next = on ? selected.filter((id) => id !== layer.id) : [...selected, layer.id];
                  setSelected(next);
                  tracker.parameter(layer.id, !on);
                }}
              />
              <span className="choice__body">
                {layer.label}
                {!layer.essential ? (
                  <span className="badge" style={{ marginLeft: 'var(--sp-2)' }}>
                    situational
                  </span>
                ) : null}
                {on ? (
                  <span style={{ display: 'block', fontSize: 'var(--text-xs)', marginTop: 4 }}>
                    <strong>Addresses:</strong> {layer.addresses}
                    <br />
                    <strong style={{ color: 'var(--warning)' }}>Residual risk:</strong> {layer.residual}
                  </span>
                ) : null}
              </span>
            </label>
          );
        })}
      </fieldset>

      <LiveResult>
        <div className="metric-row" style={{ marginTop: 'var(--sp-4)' }}>
          <Metric
            label="Essential layers covered"
            value={`${covered} / ${essentials.length}`}
            tone={passing ? 'success' : 'warning'}
          />
        </div>
        <Callout tone={passing ? 'success' : 'warning'} title={passing ? 'Audit passed' : 'Gaps remain'}>
          <p>
            {passing
              ? 'Every essential layer is present. Note that each one still has residual risk — security is defence in depth precisely because no single control is sufficient.'
              : `${essentials.length - covered} essential layer(s) missing. Notice that de-identification and least privilege do the most work: they limit the damage when the others fail.`}
          </p>
        </Callout>
      </LiveResult>

      <div style={{ marginTop: 'var(--sp-5)' }}>
        <Button
          variant="primary"
          disabled={!passing}
          onClick={() => {
            tracker.complete({ layers: selected.length, passing });
            props.onComplete();
          }}
        >
          {passing ? 'Sign off the security audit' : 'Cover the essential layers to continue'}
        </Button>
      </div>
    </ActivityShell>
  );
}

// ── OMOP mapper ──────────────────────────────────────────────────────────────

const SOURCE_ROW = [
  { field: 'Patient name', value: 'Maria S. Delgado', answer: 'drop', note: 'Direct identifier. Never enters the standardized table.' },
  { field: 'Street address', value: '418 Oak Ave, Apt 3', answer: 'drop', note: 'Direct identifier. Geography is retained only at a coarse level if an analysis needs it.' },
  { field: 'Sex', value: 'F', answer: '8532', note: 'Mapped to concept 8532 (FEMALE). "F", "2", and "female" from three hospitals all become the same identifier.' },
  { field: 'Date of birth', value: '1961-04-17', answer: 'year', note: 'Reduced to year of birth (1961). Age is analytically necessary; the exact date is not.' },
  { field: 'Race', value: 'Black', answer: '8516', note: 'Mapped to concept 8516. The source value is also retained so the mapping stays auditable.' },
  { field: 'Diagnosis', value: 'E11.9 (ICD-10)', answer: '201826', note: 'Mapped to SNOMED-derived concept 201826 (Type 2 diabetes mellitus). This is what lets a query run identically across coding systems.' },
] as const;

const MAP_OPTIONS = [
  { value: 'keep', label: 'Keep as is' },
  { value: 'year', label: 'Reduce precision' },
  { value: 'drop', label: 'Drop entirely' },
  { value: '8532', label: 'Concept 8532' },
  { value: '8516', label: 'Concept 8516' },
  { value: '201826', label: 'Concept 201826' },
];

export function OmopMapper(props: ActivityProps) {
  const [choices, setChoices] = useState<Record<string, string>>({});
  const [checked, setChecked] = useState(false);
  const tracker = useInteractionTracker(props.activityKey, props);

  const correct = SOURCE_ROW.filter((row) => choices[row.field] === row.answer).length;
  const allAnswered = SOURCE_ROW.every((row) => choices[row.field]);

  return (
    <ActivityShell heading="Standardize a patient record" completed={props.completed}>
      <div className="table-wrap">
        <table className="data-table">
          <caption className="sr-only">Source record fields and their standardized mapping</caption>
          <thead>
            <tr>
              <th scope="col">Source field</th>
              <th scope="col">Source value</th>
              <th scope="col">Your mapping</th>
            </tr>
          </thead>
          <tbody>
            {SOURCE_ROW.map((row) => {
              const choice = choices[row.field];
              const right = checked && choice === row.answer;
              const wrong = checked && choice !== row.answer;
              return (
                <tr
                  key={row.field}
                  style={{
                    background: right ? 'var(--success-soft)' : wrong ? 'var(--danger-soft)' : undefined,
                  }}
                >
                  <th scope="row">{row.field}</th>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--text-xs)' }}>
                    {row.value}
                  </td>
                  <td>
                    <label className="sr-only" htmlFor={`map-${row.field}`}>
                      Mapping for {row.field}
                    </label>
                    <select
                      id={`map-${row.field}`}
                      className="select"
                      style={{ minWidth: '11rem' }}
                      value={choice ?? ''}
                      disabled={checked}
                      onChange={(event) => {
                        setChoices((prev) => ({ ...prev, [row.field]: event.target.value }));
                        tracker.parameter(row.field, event.target.value);
                      }}
                    >
                      <option value="">Choose…</option>
                      {MAP_OPTIONS.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                    {checked ? (
                      <p style={{ fontSize: 'var(--text-xs)', marginTop: 4, whiteSpace: 'normal' }}>
                        {right ? '✓ ' : '✕ '}
                        {row.note}
                      </p>
                    ) : null}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div style={{ marginTop: 'var(--sp-5)', display: 'flex', gap: 'var(--sp-3)', flexWrap: 'wrap' }}>
        {!checked ? (
          <Button
            variant="primary"
            disabled={!allAnswered}
            onClick={() => {
              setChecked(true);
              tracker.complete({ correct, total: SOURCE_ROW.length });
              props.onComplete();
            }}
          >
            Check my mapping
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
      </div>

      {checked ? (
        <LiveResult>
          <Callout tone={correct === SOURCE_ROW.length ? 'success' : 'info'} title={`${correct} of ${SOURCE_ROW.length} correct`}>
            <p>
              Two fields vanished and one lost precision. Every remaining field survived the same
              question: <strong>what analysis becomes impossible without it?</strong>
            </p>
          </Callout>
        </LiveResult>
      ) : null}
    </ActivityShell>
  );
}

// ── Label agreement ──────────────────────────────────────────────────────────

/** Twelve fixed cases: clear positives, clear negatives, and four genuinely borderline. */
const CASES = [
  { id: 1, difficulty: 'easy', truth: 0 },
  { id: 2, difficulty: 'easy', truth: 0 },
  { id: 3, difficulty: 'easy', truth: 1 },
  { id: 4, difficulty: 'hard', truth: 1 },
  { id: 5, difficulty: 'easy', truth: 0 },
  { id: 6, difficulty: 'hard', truth: 0 },
  { id: 7, difficulty: 'easy', truth: 1 },
  { id: 8, difficulty: 'hard', truth: 1 },
  { id: 9, difficulty: 'easy', truth: 0 },
  { id: 10, difficulty: 'hard', truth: 0 },
  { id: 11, difficulty: 'easy', truth: 1 },
  { id: 12, difficulty: 'easy', truth: 0 },
] as const;

function annotatorReads(annotator: number): number[] {
  const next = rng(1000 + annotator * 37);
  return CASES.map((c) => {
    const errorRate = c.difficulty === 'hard' ? 0.42 : 0.05;
    return next() < errorRate ? 1 - c.truth : c.truth;
  });
}

export function LabelAgreement(props: ActivityProps) {
  const [annotators, setAnnotators] = useState(2);
  const tracker = useInteractionTracker(props.activityKey, props);

  const reads = useMemo(
    () => Array.from({ length: annotators }, (_, i) => annotatorReads(i + 1)),
    [annotators],
  );

  const consensus = CASES.map((_, index) => {
    const votes = reads.reduce((sum, read) => sum + (read[index] ?? 0), 0);
    return votes / reads.length >= 0.5 ? 1 : 0;
  });

  const first = reads[0] ?? [];
  const second = reads[1] ?? first;
  const rawAgreement =
    CASES.filter((_, index) => (first[index] ?? 0) === (second[index] ?? 0)).length / CASES.length;
  const kappa = cohenKappa(first, second);
  const consensusAccuracy =
    CASES.filter((c, index) => consensus[index] === c.truth).length / CASES.length;

  const disagreements = CASES.map((c, index) => ({
    ...c,
    votes: reads.map((read) => read[index] ?? 0),
    split: new Set(reads.map((read) => read[index])).size > 1,
  })).filter((row) => row.split);

  return (
    <ActivityShell heading="Inter-rater agreement" completed={props.completed}>
      <div className="activity__split">
        <div className="activity__controls">
          <Slider
            label="Number of annotators"
            value={annotators}
            min={2}
            max={5}
            step={1}
            onChange={(value) => {
              setAnnotators(value);
              tracker.parameter('annotators', value);
            }}
            hint="Each reads all 12 cases independently. Four of the twelve are genuinely borderline."
          />
          <LiveResult>
            <div className="metric-row">
              <Metric label="Raw agreement (readers 1 & 2)" value={percent(rawAgreement)} />
              <Metric
                label="Cohen's kappa"
                value={fixed(kappa, 2)}
                tone={kappa > 0.6 ? 'success' : kappa > 0.4 ? 'warning' : 'danger'}
                note={kappa > 0.8 ? 'almost perfect' : kappa > 0.6 ? 'substantial' : kappa > 0.4 ? 'moderate' : 'fair or worse'}
              />
              <Metric
                label="Consensus label accuracy"
                value={percent(consensusAccuracy)}
                note="the ceiling for any model"
              />
            </div>
          </LiveResult>
        </div>

        <div>
          <LiveResult>
            <BarChart
              title="Effect of annotator count on label quality"
              yLabel="Accuracy of the consensus label"
              yDomain={[0.5, 1]}
              bars={[2, 3, 4, 5].map((count) => {
                const r = Array.from({ length: count }, (_, i) => annotatorReads(i + 1));
                const c = CASES.map((_, index) => {
                  const votes = r.reduce((sum, read) => sum + (read[index] ?? 0), 0);
                  return votes / r.length >= 0.5 ? 1 : 0;
                });
                const acc = CASES.filter((cs, index) => c[index] === cs.truth).length / CASES.length;
                return {
                  label: `${count} readers`,
                  value: acc,
                  color: count === annotators ? 'var(--viz-1)' : 'var(--viz-6)',
                };
              })}
              valueFormat={(value) => value.toFixed(2)}
              caption="Adding readers improves the consensus label — with diminishing returns, and never past the ambiguity of the borderline cases themselves."
            />
          </LiveResult>

          {disagreements.length > 0 ? (
            <div className="table-wrap" style={{ marginTop: 'var(--sp-4)' }}>
              <table className="data-table">
                <caption className="sr-only">Cases where readers disagree</caption>
                <thead>
                  <tr>
                    <th scope="col">Case</th>
                    <th scope="col">Reads</th>
                    <th scope="col">Kind</th>
                  </tr>
                </thead>
                <tbody>
                  {disagreements.map((row) => (
                    <tr key={row.id}>
                      <th scope="row">#{row.id}</th>
                      <td style={{ fontFamily: 'var(--font-mono)' }}>
                        {row.votes.map((v) => (v === 1 ? 'pos' : 'neg')).join(' · ')}
                      </td>
                      <td>{row.difficulty === 'hard' ? 'Genuinely borderline' : 'Reader error'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : null}
        </div>
      </div>

      <div style={{ marginTop: 'var(--sp-5)' }}>
        <Button
          variant="primary"
          onClick={() => {
            tracker.complete({ annotators, kappa: Number(kappa.toFixed(3)) });
            props.onComplete();
          }}
        >
          I have compared annotator counts
        </Button>
      </div>

      <div style={{ marginTop: 'var(--sp-4)' }}>
        <Reveal label="Why the disagreement cases are the interesting ones" eventContext={props}>
          <Prose
            body={[
              'The table lists the cases where readers split. These are not noise to be averaged away — they are the cases where the label definition is underspecified.',
              'The productive response is to look at them together and write a rule: "an opacity is called positive only if it crosses the fissure." Then re-read. Agreement rises because the *task* got clearer, not because the readers got better.',
              'A model trained without that step learns to reproduce the ambiguity, and its errors will cluster exactly here.',
            ]}
          />
        </Reveal>
      </div>
    </ActivityShell>
  );
}

// ── Preprocessing pipeline ───────────────────────────────────────────────────

type Impute = 'mean' | 'median' | 'zero' | 'indicator';
type Scale = 'none' | 'minmax' | 'standard';

export function PreprocessingPipeline(props: ActivityProps) {
  const [zThreshold, setZThreshold] = useState(3);
  const [impute, setImpute] = useState<Impute>('mean');
  const [scaling, setScaling] = useState<Scale>('none');
  const tracker = useInteractionTracker(props.activityKey, props);
  const { status, save } = useActivityAutosave(props.activityKey, props.moduleKey, props.pageKey);

  const raw = useMemo(() => {
    const next = rng(21);
    return Array.from({ length: 200 }, (_, i) => {
      // 3% are equipment errors; the rest are plausible white cell counts.
      const isError = i % 33 === 0;
      const wbc = isError ? 50_000 + next() * 200_000 : clamp(7000 + (next() - 0.5) * 5000, 1500, 22_000);
      // 10% missing oxygen saturation, and the missing ones are the healthier patients.
      const missing = i % 10 === 0;
      const o2 = missing ? null : clamp(96 + (next() - 0.5) * 5, 82, 100);
      return { id: i, wbc, o2, isError, missing };
    });
  }, []);

  const wbcValues = raw.map((row) => row.wbc);
  const z = zScores(wbcValues);
  const kept = raw.filter((_, index) => Math.abs(z[index] ?? 0) <= zThreshold);
  const removed = raw.length - kept.length;
  const realErrorsRemoved = raw.filter(
    (row, index) => row.isError && Math.abs(z[index] ?? 0) > zThreshold,
  ).length;
  const totalErrors = raw.filter((row) => row.isError).length;

  const observedO2 = kept.filter((row) => row.o2 !== null).map((row) => row.o2 as number);
  const fill =
    impute === 'mean'
      ? mean(observedO2)
      : impute === 'median'
        ? median(observedO2)
        : impute === 'zero'
          ? 0
          : mean(observedO2);
  const imputedO2 = kept.map((row) => row.o2 ?? fill);

  const scaled = useMemo(() => {
    if (scaling === 'none') return imputedO2;
    if (scaling === 'minmax') {
      const lo = Math.min(...imputedO2);
      const hi = Math.max(...imputedO2);
      return imputedO2.map((v) => (hi === lo ? 0 : (v - lo) / (hi - lo)));
    }
    const m = mean(imputedO2);
    const s = sd(imputedO2) || 1;
    return imputedO2.map((v) => (v - m) / s);
  }, [imputedO2, scaling]);

  return (
    <ActivityShell heading="Preprocessing pipeline" completed={props.completed}>
      <div className="activity__split">
        <div className="activity__controls">
          <Slider
            label="Z-score threshold"
            value={zThreshold}
            min={1.5}
            max={5}
            step={0.1}
            onChange={(value) => {
              setZThreshold(value);
              tracker.parameter('z_threshold', value);
            }}
            hint="Rows whose white cell count exceeds this many standard deviations are dropped."
          />
          <Segmented
            label="Imputation"
            value={impute}
            options={[
              { value: 'mean', label: 'Mean' },
              { value: 'median', label: 'Median' },
              { value: 'zero', label: 'Zero' },
              { value: 'indicator', label: 'Mean + indicator' },
            ]}
            onChange={(value) => {
              setImpute(value);
              tracker.parameter('impute', value);
              save({ zThreshold, impute: value, scaling }, false);
            }}
          />
          <Segmented
            label="Scaling"
            value={scaling}
            options={[
              { value: 'none', label: 'None' },
              { value: 'minmax', label: 'Min–max' },
              { value: 'standard', label: 'Standardize' },
            ]}
            onChange={(value) => {
              setScaling(value);
              tracker.parameter('scaling', value);
            }}
          />
          <LiveResult>
            <div className="metric-row">
              <Metric label="Rows dropped" value={`${removed}`} note={`of ${raw.length}`} />
              <Metric
                label="Real errors caught"
                value={`${realErrorsRemoved} / ${totalErrors}`}
                tone={realErrorsRemoved === totalErrors ? 'success' : 'warning'}
              />
              <Metric
                label="Values imputed"
                value={`${kept.filter((row) => row.o2 === null).length}`}
                note={impute === 'zero' ? 'filled with 0 — implausible' : `filled with ${fixed(fill, 1)}`}
              />
            </div>
          </LiveResult>
          <SaveState status={status} />
        </div>

        <div>
          <LiveResult>
            <Histogram
              title="Oxygen saturation after imputation"
              xLabel={scaling === 'none' ? 'O₂ saturation (%)' : 'Scaled value'}
              distributions={[
                {
                  label: 'Observed only',
                  values: scaling === 'none' ? observedO2 : scaled.slice(0, observedO2.length),
                  color: 'var(--viz-1)',
                },
                { label: 'After imputation', values: scaled, color: 'var(--viz-2)' },
              ]}
              caption={
                impute === 'zero'
                  ? 'Filling with zero creates a spike at an impossible value. Any model will treat it as a signal.'
                  : 'Imputation creates a spike at the fill value, shrinking variance. The "mean + indicator" option keeps the fact that the value was absent.'
              }
            />
            <Callout
              tone={impute === 'indicator' ? 'success' : impute === 'zero' ? 'danger' : 'warning'}
              title="What this choice assumes"
            >
              <p>
                {impute === 'indicator'
                  ? 'Best available option: you fill the value and keep a flag recording that it was absent, so the model can learn from the missingness itself.'
                  : impute === 'zero'
                    ? 'Zero is not a possible oxygen saturation. The model will learn that "0%" means "not measured", which works until deployment changes documentation practice.'
                    : `Filling with the ${impute} assumes patients without a recorded saturation are typical. In this cohort they are systematically healthier — which is why they were not measured.`}
              </p>
            </Callout>
          </LiveResult>
        </div>
      </div>

      <div style={{ marginTop: 'var(--sp-5)' }}>
        <Button
          variant="primary"
          onClick={() => {
            tracker.complete({ zThreshold, impute, scaling, removed });
            save({ zThreshold, impute, scaling, removed }, true);
            props.onComplete();
          }}
        >
          I have tested each stage
        </Button>
      </div>
    </ActivityShell>
  );
}

// ── Federated round ──────────────────────────────────────────────────────────

export function FederatedRound(props: ActivityProps) {
  const [heterogeneity, setHeterogeneity] = useState(0.3);
  const [ran, setRan] = useState(false);
  const tracker = useInteractionTracker(props.activityKey, props);

  const result = useMemo(() => {
    const next = rng(303);
    const siteA = Array.from({ length: 240 }, () => ({
      x: 7000 + (next() - 0.5) * 4000,
      y: next() < 0.22 ? 1 : 0,
    }));
    const siteB = Array.from({ length: 180 }, () => ({
      x: 7000 + heterogeneity * 4000 + (next() - 0.5) * 4000,
      y: next() < 0.22 + heterogeneity * 0.18 ? 1 : 0,
    }));
    const wA = mean(siteA.map((r) => r.x));
    const wB = mean(siteB.map((r) => r.x));
    const global = (wA * siteA.length + wB * siteB.length) / (siteA.length + siteB.length);
    const pooled = mean([...siteA, ...siteB].map((r) => r.x));
    // Simple averaging diverges from the pooled fit as the sites diverge.
    const naiveAverage = (wA + wB) / 2;
    return {
      wA,
      wB,
      global,
      pooled,
      naiveAverage,
      nA: siteA.length,
      nB: siteB.length,
      degradation: Math.abs(naiveAverage - pooled) / pooled,
    };
  }, [heterogeneity]);

  return (
    <ActivityShell heading="Run a federated round" completed={props.completed}>
      <div className="activity__split">
        <div className="activity__controls">
          <Slider
            label="Site heterogeneity"
            value={heterogeneity}
            min={0}
            max={1}
            step={0.05}
            format={(value) => `${(value * 100).toFixed(0)}%`}
            onChange={(value) => {
              setHeterogeneity(value);
              tracker.parameter('heterogeneity', value);
            }}
            hint="How different site B's population is from site A's."
          />
          <Button
            variant="primary"
            onClick={() => {
              setRan(true);
              tracker.run({ heterogeneity });
            }}
          >
            Run one federated round
          </Button>
          <Metric label="Patient records transmitted" value="0" tone="success" note="only parameters move" />
        </div>

        <div>
          {ran ? (
            <LiveResult>
              <div className="metric-row">
                <Metric label="Site A parameter" value={fixed(result.wA, 0)} note={`n = ${result.nA}, stays local`} />
                <Metric label="Site B parameter" value={fixed(result.wB, 0)} note={`n = ${result.nB}, stays local`} />
                <Metric label="Aggregated (n-weighted)" value={fixed(result.global, 0)} />
                <Metric label="Pooled (if data could move)" value={fixed(result.pooled, 0)} />
              </div>
              <BarChart
                title="Aggregation strategies vs. the pooled reference"
                yLabel="Learned parameter"
                bars={[
                  { label: 'Site A', value: result.wA, color: 'var(--viz-6)' },
                  { label: 'Site B', value: result.wB, color: 'var(--viz-6)' },
                  { label: 'Simple average', value: result.naiveAverage, color: 'var(--viz-2)' },
                  { label: 'n-weighted', value: result.global, color: 'var(--viz-3)' },
                  { label: 'Pooled', value: result.pooled, color: 'var(--viz-1)' },
                ]}
                valueFormat={(value) => value.toFixed(0)}
                caption="Weighting by site size tracks the pooled result closely. A simple unweighted average drifts as the sites diverge — the smaller site gets equal say."
              />
              <Callout
                tone={result.degradation > 0.05 ? 'warning' : 'success'}
                title={`Simple average is ${percent(result.degradation, 1)} off the pooled reference`}
              >
                <p>
                  Zero patient records left either institution — that part genuinely works. What
                  federation did not solve: the two sites still had to agree on the preprocessing
                  pipeline beforehand, and any group absent from both remains absent from the model.
                </p>
              </Callout>
              <div style={{ marginTop: 'var(--sp-4)' }}>
                <Button
                  variant="primary"
                  onClick={() => {
                    tracker.complete({ heterogeneity, degradation: Number(result.degradation.toFixed(4)) });
                    props.onComplete();
                  }}
                >
                  I have run rounds at several heterogeneity levels
                </Button>
              </div>
            </LiveResult>
          ) : (
            <p className="placeholder">Run a round to see what leaves each site.</p>
          )}
        </div>
      </div>
    </ActivityShell>
  );
}
