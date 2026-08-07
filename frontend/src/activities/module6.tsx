import { useMemo, useState } from 'react';
import { BarChart } from '@/components/charts';
import { Prose } from '@/components/Prose';
import { Button, Callout, Metric, Reveal, Segmented, Slider, TextInput } from '@/components/primitives';
import { useInteractionTracker } from '@/analytics/useInteractionTracker';
import { ActivityShell, LiveResult, type ActivityProps } from './ActivityShell';
import { percent } from './lib/math';

// ── Tokenizer ────────────────────────────────────────────────────────────────

/**
 * Frequency-aware demonstration tokenizer.
 *
 * Not a real BPE vocabulary — it reproduces the pedagogically important behavior (common words stay
 * whole, rare biomedical terms fragment) without shipping a megabyte of merge rules.
 */
const COMMON_WORDS = new Set([
  'the', 'a', 'an', 'and', 'or', 'of', 'in', 'to', 'is', 'was', 'for', 'with', 'patient',
  'blood', 'heart', 'test', 'risk', 'high', 'low', 'not', 'no', 'we', 'this', 'that',
  'study', 'data', 'model', 'result', 'results', 'showed', 'after', 'before', 'day', 'days',
]);
const COMMON_PIECES = ['tion', 'ing', 'ed', 'er', 'ic', 'al', 'ology', 'itis', 'osis', 'ium', 'ate'];

function tokenizeDemo(text: string): Array<{ text: string; whole: boolean }> {
  const words = text.split(/(\s+|[.,;:()])/).filter((part) => part !== '');
  const tokens: Array<{ text: string; whole: boolean }> = [];
  for (const word of words) {
    if (/^\s+$/.test(word) || /^[.,;:()]$/.test(word)) {
      tokens.push({ text: word === ' ' ? '␣' : word, whole: true });
      continue;
    }
    const lower = word.toLowerCase();
    if (COMMON_WORDS.has(lower) || word.length <= 4) {
      tokens.push({ text: word, whole: true });
      continue;
    }
    // Rare/long words: split on recognizable pieces, then into chunks of 3.
    let remaining = word;
    const pieces: string[] = [];
    while (remaining.length > 0) {
      const suffix = COMMON_PIECES.find((piece) => remaining.toLowerCase().endsWith(piece));
      if (suffix && remaining.length > suffix.length + 2) {
        pieces.unshift(remaining.slice(-suffix.length));
        remaining = remaining.slice(0, -suffix.length);
        continue;
      }
      if (remaining.length <= 4) {
        pieces.unshift(remaining);
        break;
      }
      pieces.unshift(remaining.slice(-3));
      remaining = remaining.slice(0, -3);
    }
    for (const piece of pieces) tokens.push({ text: piece, whole: pieces.length === 1 });
  }
  return tokens;
}

const EXAMPLES = [
  'The patient was started on metoprolol after the test.',
  'Pembrolizumab plus chemotherapy improved survival.',
  'A pathogenic variant in BRCA1 was identified.',
  'We observed hypereosinophilia with thrombocytopenia.',
];

export function Tokenizer(props: ActivityProps) {
  const [text, setText] = useState(EXAMPLES[0] ?? '');
  const tracker = useInteractionTracker(props.activityKey, props);

  const tokens = useMemo(() => tokenizeDemo(text), [text]);
  const wordCount = text.split(/\s+/).filter(Boolean).length;
  const fragmented = tokens.filter((token) => !token.whole && token.text !== '␣').length;

  return (
    <ActivityShell heading="Tokens, not words" completed={props.completed}>
      <TextInput
        label="Text to tokenize"
        value={text}
        onChange={(event) => {
          setText(event.target.value);
          tracker.parameter('length', event.target.value.length);
        }}
        hint="Try a common sentence, then one with a drug name or a gene symbol."
      />

      <div style={{ display: 'flex', gap: 'var(--sp-2)', flexWrap: 'wrap', margin: 'var(--sp-3) 0' }}>
        {EXAMPLES.map((example) => (
          <Button
            key={example}
            size="sm"
            variant="outline"
            onClick={() => {
              setText(example);
              tracker.parameter('example', example.slice(0, 24));
            }}
          >
            {example.slice(0, 28)}…
          </Button>
        ))}
      </div>

      <LiveResult>
        <div
          className="panel"
          style={{ display: 'flex', flexWrap: 'wrap', gap: 4, alignItems: 'center' }}
        >
          {tokens.map((token, index) => (
            <span
              key={index}
              style={{
                fontFamily: 'var(--font-mono)',
                fontSize: 'var(--text-sm)',
                padding: '2px 6px',
                borderRadius: 4,
                background: token.whole ? 'var(--accent-soft)' : 'var(--warning-soft)',
                border: `1px solid ${token.whole ? 'var(--info-border)' : 'var(--warning-border)'}`,
              }}
            >
              {token.text}
            </span>
          ))}
        </div>

        <div className="metric-row" style={{ marginTop: 'var(--sp-4)' }}>
          <Metric label="Words" value={`${wordCount}`} />
          <Metric label="Tokens" value={`${tokens.filter((t) => t.text !== '␣').length}`} />
          <Metric
            label="Fragmented pieces"
            value={`${fragmented}`}
            tone={fragmented > 3 ? 'warning' : undefined}
            note="rare terms split"
          />
        </div>

        <Callout tone={fragmented > 3 ? 'warning' : 'info'} title="What the fragments mean">
          <p>
            {fragmented > 3
              ? 'This text contains specialist vocabulary that fragments into pieces. The model has seen those pieces often but the assembled term rarely — which is precisely where it confuses similar-looking drugs, genes, and syndromes.'
              : 'This text tokenizes cleanly: mostly whole common words. The model has abundant evidence about each unit.'}
          </p>
        </Callout>
      </LiveResult>

      <div style={{ marginTop: 'var(--sp-5)' }}>
        <Button
          variant="primary"
          onClick={() => {
            tracker.complete({ fragmented, words: wordCount });
            props.onComplete();
          }}
        >
          I have compared common and rare terms
        </Button>
      </div>

      <div style={{ marginTop: 'var(--sp-4)' }}>
        <Callout tone="neutral" title="About this demonstration">
          <p>
            This is an illustrative tokenizer, not a production vocabulary — it reproduces the
            behavior that matters (frequency determines fragmentation) without shipping a real merge
            table. Exact token counts from a specific model will differ.
          </p>
        </Callout>
      </div>
    </ActivityShell>
  );
}

// ── Next-token prediction ────────────────────────────────────────────────────

const CONTEXTS = [
  {
    value: 'clinical',
    prompt: 'The patient presented with chest pain and elevated troponin, consistent with',
    logits: [
      { token: 'acute', base: 3.1 },
      { token: 'myocardial', base: 2.6 },
      { token: 'an', base: 1.8 },
      { token: 'ischemia', base: 1.4 },
      { token: 'possible', base: 0.9 },
      { token: 'unstable', base: 0.6 },
      { token: 'pericarditis', base: -0.4 },
      { token: 'pneumonia', base: -1.2 },
    ],
  },
  {
    value: 'citation',
    prompt: 'This finding was first reported by Chen et al. in the Journal of',
    logits: [
      { token: 'Clinical', base: 2.4 },
      { token: 'the', base: 2.1 },
      { token: 'Medical', base: 1.9 },
      { token: 'Immunology', base: 1.5 },
      { token: 'Cardiology', base: 1.3 },
      { token: 'Oncology', base: 1.1 },
      { token: 'Hepatology', base: 0.7 },
      { token: 'Nephrology', base: 0.5 },
    ],
  },
] as const;

function softmax(values: number[], temperature: number): number[] {
  const t = Math.max(0.05, temperature);
  const scaled = values.map((value) => value / t);
  const max = Math.max(...scaled);
  const exps = scaled.map((value) => Math.exp(value - max));
  const sum = exps.reduce((a, b) => a + b, 0);
  return exps.map((value) => value / sum);
}

export function NextToken(props: ActivityProps) {
  const [contextKey, setContextKey] = useState<string>('clinical');
  const [temperature, setTemperature] = useState(0.7);
  const tracker = useInteractionTracker(props.activityKey, props);

  const context = CONTEXTS.find((entry) => entry.value === contextKey) ?? CONTEXTS[0];
  const probabilities = useMemo(
    () => softmax(context.logits.map((entry) => entry.base), temperature),
    [context.logits, temperature],
  );
  const top = probabilities[0] ?? 0;
  const entropy = -probabilities.reduce((sum, p) => sum + (p > 0 ? p * Math.log2(p) : 0), 0);

  return (
    <ActivityShell heading="Watch it predict" completed={props.completed}>
      <Segmented
        label="Context"
        value={contextKey}
        options={[
          { value: 'clinical', label: 'A clinical sentence' },
          { value: 'citation', label: 'A citation' },
        ]}
        onChange={(value) => {
          setContextKey(value);
          tracker.parameter('context', value);
        }}
      />

      <div className="panel" style={{ margin: 'var(--sp-4) 0' }}>
        <p className="kicker">Text so far</p>
        <p style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--text-sm)', marginTop: 'var(--sp-2)' }}>
          {context.prompt} <span style={{ color: 'var(--accent)' }}>▌</span>
        </p>
      </div>

      <div className="activity__split">
        <div className="activity__controls">
          <Slider
            label="Temperature"
            value={temperature}
            min={0.05}
            max={2}
            step={0.05}
            format={(value) => value.toFixed(2)}
            onChange={(value) => {
              setTemperature(value);
              tracker.parameter('temperature', value);
            }}
            hint="Near 0: always take the most probable token. Above 1: flatten the distribution and sample more widely."
          />
          <LiveResult>
            <div className="metric-row">
              <Metric label="Top token probability" value={percent(top, 1)} />
              <Metric
                label="Uncertainty (entropy)"
                value={entropy.toFixed(2)}
                note="bits — higher means less committed"
                tone={entropy > 2.5 ? 'warning' : undefined}
              />
            </div>
          </LiveResult>
        </div>

        <div>
          <LiveResult>
            <BarChart
              title="Probability of each candidate next token"
              yLabel="Probability"
              yDomain={[0, 1]}
              height={280}
              bars={context.logits.map((entry, index) => ({
                label: entry.token,
                value: probabilities[index] ?? 0,
                color: index === 0 ? 'var(--viz-1)' : 'var(--viz-6)',
              }))}
              valueFormat={(value) => percent(value, 1)}
              caption="This distribution is the model's entire output. Everything a language model does is sample from this, append, and repeat."
            />
          </LiveResult>
        </div>
      </div>

      <Callout tone={contextKey === 'citation' ? 'warning' : 'info'} title={contextKey === 'citation' ? 'This is how a fake citation is born' : 'Plausibility, not truth'}>
        <p>
          {contextKey === 'citation'
            ? 'Notice that every candidate is a plausible journal name and none is grounded in whether Chen et al. exists. The model is completing a pattern. Raise the temperature and it will pick a different journal — a different fabricated citation, from the same mechanism.'
            : 'The model is ranking continuations by how well they fit the pattern of its training text. Nothing in this process consults a fact.'}
        </p>
      </Callout>

      <div style={{ marginTop: 'var(--sp-5)' }}>
        <Button
          variant="primary"
          onClick={() => {
            tracker.complete({ temperature, context: contextKey });
            props.onComplete();
          }}
        >
          I have seen the distribution reshape
        </Button>
      </div>
    </ActivityShell>
  );
}

// ── Embedding space ──────────────────────────────────────────────────────────

/** Hand-placed 2-D positions: close = used in similar contexts. */
const TERMS = [
  { term: 'myocardial infarction', x: 0.82, y: 0.71, group: 'cardiac' },
  { term: 'heart attack', x: 0.86, y: 0.68, group: 'cardiac' },
  { term: 'angina', x: 0.74, y: 0.63, group: 'cardiac' },
  { term: 'troponin', x: 0.79, y: 0.52, group: 'cardiac' },
  { term: 'hypertension', x: 0.62, y: 0.58, group: 'cardiac' },
  { term: 'hypotension', x: 0.60, y: 0.62, group: 'cardiac' },
  { term: 'metformin', x: 0.24, y: 0.29, group: 'diabetes' },
  { term: 'insulin', x: 0.27, y: 0.34, group: 'diabetes' },
  { term: 'type 2 diabetes', x: 0.20, y: 0.36, group: 'diabetes' },
  { term: 'HbA1c', x: 0.26, y: 0.22, group: 'diabetes' },
  { term: 'sepsis', x: 0.50, y: 0.86, group: 'infection' },
  { term: 'bacteremia', x: 0.55, y: 0.83, group: 'infection' },
  { term: 'lactate', x: 0.58, y: 0.76, group: 'infection' },
  { term: 'pneumonia', x: 0.44, y: 0.80, group: 'infection' },
] as const;

function distance(a: (typeof TERMS)[number], b: (typeof TERMS)[number]): number {
  return Math.hypot(a.x - b.x, a.y - b.y);
}

export function EmbeddingSpace(props: ActivityProps) {
  const [selected, setSelected] = useState<string>('myocardial infarction');
  const tracker = useInteractionTracker(props.activityKey, props);

  const anchor = TERMS.find((entry) => entry.term === selected) ?? TERMS[0];
  const neighbours = useMemo(
    () =>
      TERMS.filter((entry) => entry.term !== anchor.term)
        .map((entry) => ({ ...entry, d: distance(anchor, entry) }))
        .sort((a, b) => a.d - b.d)
        .slice(0, 5),
    [anchor],
  );

  const nearest = neighbours[0];
  const misleading = anchor.term === 'hypertension' || anchor.term === 'hypotension';

  return (
    <ActivityShell heading="Similarity in embedding space" completed={props.completed}>
      <div className="field">
        <label className="field__label" htmlFor="embed-term">
          Choose a term
        </label>
        <select
          id="embed-term"
          className="select"
          value={selected}
          onChange={(event) => {
            setSelected(event.target.value);
            tracker.parameter('term', event.target.value);
          }}
        >
          {TERMS.map((entry) => (
            <option key={entry.term} value={entry.term}>
              {entry.term}
            </option>
          ))}
        </select>
      </div>

      <LiveResult>
        <BarChart
          title={`Nearest terms to "${anchor.term}"`}
          yLabel="Similarity (1 = identical position)"
          yDomain={[0, 1]}
          height={260}
          bars={neighbours.map((entry, index) => ({
            label: entry.term,
            value: 1 - entry.d,
            color: index === 0 ? 'var(--viz-1)' : 'var(--viz-6)',
          }))}
          valueFormat={(value) => value.toFixed(2)}
          caption="Terms used in similar contexts sit near each other. Nobody wrote a rule saying so — the positions emerge from co-occurrence in training text."
        />

        <Callout
          tone={misleading ? 'warning' : 'info'}
          title={misleading ? 'A dangerous kind of closeness' : `Nearest: ${nearest?.term ?? ''}`}
        >
          <p>
            {misleading
              ? '"Hypertension" and "hypotension" are near-neighbours in embedding space because they appear in almost identical contexts — same sentences, same specialties, same measurements. They are also clinical opposites. Proximity encodes contextual similarity, not equivalence, and this is exactly the failure a retrieval system can make silently.'
              : `"${anchor.term}" sits closest to "${nearest?.term ?? ''}". That is why semantic search finds relevant papers that share no keywords — and it is the mechanism behind retrieval-augmented generation.`}
          </p>
        </Callout>
      </LiveResult>

      <div style={{ marginTop: 'var(--sp-5)' }}>
        <Button
          variant="primary"
          onClick={() => {
            tracker.complete({ term: selected });
            props.onComplete();
          }}
        >
          I have found a misleading pair
        </Button>
      </div>

      <div style={{ marginTop: 'var(--sp-4)' }}>
        <Reveal label="How to check the hypertension/hypotension case" eventContext={props}>
          <Prose
            body={[
              'Select "hypertension", then "hypotension". Each is the other\'s nearest neighbour.',
              'Any system that retrieves by embedding similarity alone can substitute one for the other. Production systems handle this with exact-match filters on negation and on clinical opposites — a reminder that embeddings are a retrieval aid, not a semantics engine.',
            ]}
          />
        </Reveal>
      </div>
    </ActivityShell>
  );
}

// ── Hallucination hunt ───────────────────────────────────────────────────────

const CLAIMS = [
  {
    id: 'c1',
    text: 'Metformin is a first-line pharmacological treatment for type 2 diabetes.',
    fabricated: false,
    note: 'Accurate and well supported. This is the kind of broad, high-frequency statement models handle reliably.',
  },
  {
    id: 'c2',
    text: 'A 2019 trial in the New England Journal of Medicine (Okafor et al., DOI 10.1056/NEJMoa1904712) found metformin reduced all-cause mortality by 31%.',
    fabricated: true,
    note: 'Fabricated. Named authors, a real-sounding DOI, a specific percentage, a real journal — every element that makes a citation feel authoritative, assembled from pattern rather than retrieved. The DOI format is valid; the record is not.',
  },
  {
    id: 'c3',
    text: 'Its principal mechanism involves reducing hepatic gluconeogenesis.',
    fabricated: false,
    note: 'Accurate. Standard mechanistic content that appears frequently in training text.',
  },
  {
    id: 'c4',
    text: 'The recommended starting dose is 2,000 mg twice daily with meals.',
    fabricated: true,
    note: 'Wrong and clinically dangerous. Typical initiation is 500 mg once or twice daily, titrated upward. Note how the *format* is exactly right — that is what makes a wrong dose so easy to miss.',
  },
  {
    id: 'c5',
    text: 'It should be used cautiously in patients with reduced kidney function.',
    fabricated: false,
    note: 'Accurate, and appropriately hedged. Hedged general statements are the safest thing a model produces.',
  },
  {
    id: 'c6',
    text: 'Recent guidance from the World Health Organization now lists metformin as contraindicated above age 75.',
    fabricated: true,
    note: 'Fabricated. Attributing a specific policy position to a named authority is a high-risk pattern: it sounds checkable, which discourages checking.',
  },
] as const;

export function HallucinationHunt(props: ActivityProps) {
  const [flagged, setFlagged] = useState<string[]>([]);
  const [checked, setChecked] = useState(false);
  const tracker = useInteractionTracker(props.activityKey, props);

  const fabricated = CLAIMS.filter((claim) => claim.fabricated);
  const caught = fabricated.filter((claim) => flagged.includes(claim.id)).length;
  const falseAlarms = CLAIMS.filter(
    (claim) => !claim.fabricated && flagged.includes(claim.id),
  ).length;

  return (
    <ActivityShell heading="Hallucination hunt" completed={props.completed}>
      <Callout tone="neutral" title="Generated output about metformin">
        <p>
          Three of these six claims are wrong. Flag the ones you would not act on without checking.
        </p>
      </Callout>

      <fieldset className="choice-list" style={{ marginTop: 'var(--sp-4)' }}>
        <legend className="sr-only">Claims to flag</legend>
        {CLAIMS.map((claim) => {
          const isFlagged = flagged.includes(claim.id);
          const correct = checked && isFlagged === claim.fabricated;
          const wrong = checked && isFlagged !== claim.fabricated;
          return (
            <label
              className={`choice${correct ? ' choice--correct' : wrong ? ' choice--incorrect' : ''}`}
              key={claim.id}
            >
              <input
                type="checkbox"
                checked={isFlagged}
                disabled={checked}
                onChange={() => {
                  const next = isFlagged
                    ? flagged.filter((id) => id !== claim.id)
                    : [...flagged, claim.id];
                  setFlagged(next);
                  tracker.parameter(claim.id, !isFlagged);
                }}
              />
              <span className="choice__body">
                {claim.text}
                {checked ? (
                  <span style={{ display: 'block', marginTop: 'var(--sp-2)', fontSize: 'var(--text-xs)' }}>
                    <strong>{claim.fabricated ? '✕ Wrong: ' : '✓ Accurate: '}</strong>
                    {claim.note}
                  </span>
                ) : null}
              </span>
            </label>
          );
        })}
      </fieldset>

      <div style={{ marginTop: 'var(--sp-5)', display: 'flex', gap: 'var(--sp-3)', flexWrap: 'wrap' }}>
        {!checked ? (
          <Button
            variant="primary"
            disabled={flagged.length === 0}
            onClick={() => {
              setChecked(true);
              tracker.complete({ caught, false_alarms: falseAlarms, total: fabricated.length });
              props.onComplete();
            }}
          >
            Check my flags
          </Button>
        ) : (
          <Button
            variant="outline"
            onClick={() => {
              setChecked(false);
              setFlagged([]);
              tracker.reset();
            }}
          >
            Try again
          </Button>
        )}
      </div>

      {checked ? (
        <LiveResult>
          <div className="metric-row" style={{ marginTop: 'var(--sp-4)' }}>
            <Metric
              label="Fabrications caught"
              value={`${caught} / ${fabricated.length}`}
              tone={caught === fabricated.length ? 'success' : 'warning'}
            />
            <Metric label="False alarms" value={`${falseAlarms}`} note="accurate claims you flagged" />
          </div>
          <Callout tone="info" title="The pattern in the wrong ones">
            <p>
              All three fabrications carry a <strong>specific, checkable-looking detail</strong>: a DOI,
              a dose, a named authority. All three accurate claims are general and hedged. That is the
              triage rule — highlight every number and every identifier first, because that is where
              the risk concentrates.
            </p>
          </Callout>
        </LiveResult>
      ) : null}
    </ActivityShell>
  );
}
