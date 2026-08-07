import { useMemo, useState } from 'react';
import { BarChart, Histogram, LineChart } from '@/components/charts';
import { Prose } from '@/components/Prose';
import { Button, Callout, Metric, Reveal, Segmented, Slider, TextArea } from '@/components/primitives';
import { SaveState } from '@/components/SaveState';
import { useActivityAutosave } from '@/api/useAutosave';
import { useInteractionTracker } from '@/analytics/useInteractionTracker';
import { ActivityShell, LiveResult, PredictGate, type ActivityProps } from './ActivityShell';
import {
  diagnosticCohort,
  fitLogistic,
  predictLogistic,
  readmissionCohort,
  sepsisCohort,
} from './lib/cohorts';
import { auc, calibrationBins, confusion, fixed, metrics, percent } from './lib/math';

// ── Fairness explorer ────────────────────────────────────────────────────────

export function FairnessExplorer(props: ActivityProps) {
  const [threshold, setThreshold] = useState(0.5);
  const [prediction, setPrediction] = useState<string | null>(null);
  const [revealed, setRevealed] = useState(false);
  const tracker = useInteractionTracker(props.activityKey, props);

  const cohort = useMemo(() => diagnosticCohort(400, 7), []);
  const groups = useMemo(() => {
    return (['A', 'B'] as const).map((group) => {
      const rows = cohort.filter((row) => row.group === group);
      const m = metrics(
        confusion(
          rows.map((row) => row.label),
          rows.map((row) => row.score),
          threshold,
        ),
      );
      return { group, n: rows.length, ...m };
    });
  }, [cohort, threshold]);

  const overall = metrics(
    confusion(
      cohort.map((row) => row.label),
      cohort.map((row) => row.score),
      threshold,
    ),
  );
  const groupA = groups[0];
  const groupB = groups[1];
  const sensitivityGap = Math.abs((groupA?.sensitivity ?? 0) - (groupB?.sensitivity ?? 0));

  return (
    <ActivityShell heading="Subgroup performance explorer" completed={props.completed}>
      <PredictGate
        question="Group B is 25% of the cohort and was under-represented when the model was fitted. What do you expect?"
        options={[
          { value: 'lower_sens', label: 'Lower sensitivity in group B — the model will miss more of their cases.' },
          { value: 'lower_acc', label: 'Lower overall accuracy in group B, visible immediately.' },
          { value: 'same', label: 'Similar performance — the features are the same for both groups.' },
        ]}
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
          <Slider
            label="Decision threshold"
            value={threshold}
            min={0.05}
            max={0.95}
            step={0.01}
            format={(value) => value.toFixed(2)}
            onChange={(value) => {
              setThreshold(value);
              tracker.parameter('threshold', value);
            }}
            hint="Everyone above this predicted risk is flagged for further investigation."
          />

          <LiveResult>
            <div className="metric-row" style={{ margin: 'var(--sp-5) 0' }}>
              <Metric label="Overall accuracy" value={percent(overall.accuracy, 1)} note="looks fine" />
              <Metric
                label="Sensitivity · group A"
                value={percent(groupA?.sensitivity ?? 0, 1)}
                note={`n = ${groupA?.n ?? 0}`}
              />
              <Metric
                label="Sensitivity · group B"
                value={percent(groupB?.sensitivity ?? 0, 1)}
                note={`n = ${groupB?.n ?? 0}`}
                tone={sensitivityGap > 0.1 ? 'danger' : undefined}
              />
              <Metric
                label="Sensitivity gap"
                value={percent(sensitivityGap, 1)}
                tone={sensitivityGap > 0.1 ? 'danger' : 'success'}
              />
            </div>

            <BarChart
              title="Performance by subgroup"
              yLabel="Metric value"
              yDomain={[0, 1]}
              bars={[
                { label: 'Accuracy A', value: groupA?.accuracy ?? 0, color: 'var(--viz-1)' },
                { label: 'Accuracy B', value: groupB?.accuracy ?? 0, color: 'var(--viz-2)' },
                { label: 'Sensitivity A', value: groupA?.sensitivity ?? 0, color: 'var(--viz-1)' },
                { label: 'Sensitivity B', value: groupB?.sensitivity ?? 0, color: 'var(--viz-2)' },
                { label: 'PPV A', value: groupA?.ppv ?? 0, color: 'var(--viz-1)' },
                { label: 'PPV B', value: groupB?.ppv ?? 0, color: 'var(--viz-2)' },
              ]}
              valueFormat={(value) => value.toFixed(2)}
              caption="Accuracy is similar between groups at most thresholds. Sensitivity is not — which is why reporting accuracy alone lets a disparity through."
            />

            <Callout tone={sensitivityGap > 0.1 ? 'warning' : 'info'} title="What this means in patients">
              <p>
                At this threshold the model misses{' '}
                <strong>{groupB?.fn ?? 0} of {(groupB?.fn ?? 0) + (groupB?.tp ?? 0)}</strong> true cases in
                group B, versus <strong>{groupA?.fn ?? 0} of {(groupA?.fn ?? 0) + (groupA?.tp ?? 0)}</strong>{' '}
                in group A. Overall accuracy is {percent(overall.accuracy, 1)} either way.
              </p>
            </Callout>
          </LiveResult>

          <div style={{ marginTop: 'var(--sp-5)' }}>
            <Button
              variant="primary"
              onClick={() => {
                tracker.complete({ threshold, sensitivity_gap: Number(sensitivityGap.toFixed(3)) });
                props.onComplete();
              }}
            >
              I have explored the threshold range
            </Button>
          </div>
        </>
      ) : null}
    </ActivityShell>
  );
}

// ── Drift simulator ──────────────────────────────────────────────────────────

export function DriftSimulator(props: ActivityProps) {
  const [months, setMonths] = useState(0);
  const [strategy, setStrategy] = useState<'nothing' | 'retrain'>('nothing');
  const tracker = useInteractionTracker(props.activityKey, props);
  const { status, save } = useActivityAutosave(props.activityKey, props.moduleKey, props.pageKey);

  const severity = months / 10;

  const { trainRows, currentRows, baseline } = useMemo(() => {
    const train = sepsisCohort(900, 0, 42);
    const current = sepsisCohort(500, severity, 77);
    const model = fitLogistic(
      train.map((row) => ({ features: [row.age, row.lactate, row.wbc], label: row.label })),
    );
    return { trainRows: train, currentRows: current, baseline: model };
  }, [severity]);

  const retrained = useMemo(
    () =>
      fitLogistic(
        currentRows.map((row) => ({
          features: [row.age, row.lactate, row.wbc],
          label: row.label,
        })),
      ),
    [currentRows],
  );

  const model = strategy === 'retrain' ? retrained : baseline;
  const scores = currentRows.map((row) =>
    predictLogistic(model, [row.age, row.lactate, row.wbc]),
  );
  const labels = currentRows.map((row) => row.label);
  const m = metrics(confusion(labels, scores, 0.5));
  const fpr = 1 - m.specificity;

  const fprSeries = useMemo(() => {
    const points: Array<{ x: number; y: number }> = [];
    for (let month = 0; month <= 12; month += 1) {
      const rows = sepsisCohort(400, month / 10, 77);
      const s = rows.map((row) => predictLogistic(baseline, [row.age, row.lactate, row.wbc]));
      const stats = metrics(
        confusion(
          rows.map((row) => row.label),
          s,
          0.5,
        ),
      );
      points.push({ x: month, y: 1 - stats.specificity });
    }
    return points;
  }, [baseline]);

  return (
    <ActivityShell heading="Drift and retraining" completed={props.completed}>
      <div className="activity__split">
        <div className="activity__controls">
          <Slider
            label="Months since deployment"
            value={months}
            min={0}
            max={12}
            step={1}
            unit="months"
            onChange={(value) => {
              setMonths(value);
              tracker.parameter('months', value);
            }}
            hint="A lab recalibration is gradually shifting recorded lactate upward."
          />
          <Segmented
            label="Mitigation strategy"
            value={strategy}
            options={[
              { value: 'nothing', label: 'Do nothing' },
              { value: 'retrain', label: 'Retrain on current data' },
            ]}
            onChange={(value) => {
              setStrategy(value);
              tracker.parameter('strategy', value);
              save({ months, strategy: value, fpr: Number(fpr.toFixed(3)) }, false);
            }}
          />
          <LiveResult>
            <div className="metric-row">
              <Metric
                label="False positive rate"
                value={percent(fpr, 1)}
                tone={fpr > 0.2 ? 'danger' : fpr > 0.12 ? 'warning' : 'success'}
                note={fpr > 0.2 ? 'alert fatigue territory' : 'workable'}
              />
              <Metric label="Sensitivity" value={percent(m.sensitivity, 1)} />
              <Metric label="AUC" value={fixed(auc(labels, scores), 3)} />
            </div>
          </LiveResult>
          <SaveState status={status} />
        </div>

        <div>
          <LiveResult>
            <Histogram
              title={`Lactate distribution at month ${months}`}
              xLabel="Lactate (mmol/L)"
              domain={[0, 14]}
              distributions={[
                {
                  label: 'What the model learned from',
                  values: trainRows.map((row) => row.lactate),
                  color: 'var(--viz-6)',
                },
                {
                  label: 'Patients arriving now',
                  values: currentRows.map((row) => row.lactate),
                  color: 'var(--viz-2)',
                },
              ]}
              caption="Covariate shift: the input distribution has moved away from the training distribution. The outcome relationship has not changed — only the inputs."
            />
          </LiveResult>

          <div style={{ marginTop: 'var(--sp-4)' }}>
            <LineChart
              title="False positive rate over time (no intervention)"
              xLabel="Months since deployment"
              yLabel="False positive rate"
              yDomain={[0, 0.6]}
              series={[{ label: 'Original model', points: fprSeries, color: 'var(--viz-5)' }]}
              markers={[{ x: months, label: 'now' }]}
              caption="Distribution monitoring would have flagged this in month 2 or 3, without needing a single outcome label."
            />
          </div>
        </div>
      </div>

      <div style={{ marginTop: 'var(--sp-5)' }}>
        <Button
          variant="primary"
          onClick={() => {
            tracker.complete({ months, strategy, fpr: Number(fpr.toFixed(3)) });
            save({ months, strategy, fpr: Number(fpr.toFixed(3)) }, true);
            props.onComplete();
          }}
        >
          I have tested both strategies
        </Button>
      </div>

      <div style={{ marginTop: 'var(--sp-4)' }}>
        <Reveal label="When retraining is the wrong answer" eventContext={props}>
          <Prose
            body={[
              'Retraining recovers performance here because the shift is genuine — patients really do have higher lactate now, and the outcome relationship still holds.',
              'It would be the **wrong** answer if the shift came from a miscalibrated analyzer. Then you would be teaching the model that erroneous values are normal, and you would lose the ability to detect the equipment fault at all.',
              'This is why the sequence is diagnose, then intervene. The chart above tells you *that* something moved; it cannot tell you *why*.',
            ]}
          />
        </Reveal>
      </div>
    </ActivityShell>
  );
}

// ── Calibration lab ──────────────────────────────────────────────────────────

export function CalibrationLab(props: ActivityProps) {
  const [mismatch, setMismatch] = useState(0);
  const [prediction, setPrediction] = useState<string | null>(null);
  const [revealed, setRevealed] = useState(false);
  const tracker = useInteractionTracker(props.activityKey, props);

  const { localRows, model } = useMemo(() => {
    const vendor = readmissionCohort(1600, 0, 101);
    const fitted = fitLogistic(
      vendor.map((row) => ({ features: [row.comorbidity, row.income], label: row.label })),
    );
    return { localRows: readmissionCohort(900, mismatch, 202), model: fitted };
  }, [mismatch]);

  const scores = localRows.map((row) => predictLogistic(model, [row.comorbidity, row.income]));
  const labels = localRows.map((row) => row.label);
  const aucValue = auc(labels, scores);
  const bins = calibrationBins(labels, scores, 8);

  // Calibration slope: regression of observed on predicted through the bins.
  const slope = useMemo(() => {
    if (bins.length < 2) return Number.NaN;
    const mx = bins.reduce((a, b) => a + b.predicted, 0) / bins.length;
    const my = bins.reduce((a, b) => a + b.observed, 0) / bins.length;
    const num = bins.reduce((a, b) => a + (b.predicted - mx) * (b.observed - my), 0);
    const den = bins.reduce((a, b) => a + (b.predicted - mx) ** 2, 0);
    return den === 0 ? Number.NaN : num / den;
  }, [bins]);

  const atThreshold = metrics(confusion(labels, scores, 0.4));

  return (
    <ActivityShell heading="Calibration vs. discrimination" completed={props.completed}>
      <PredictGate
        question="As the local population becomes less like the vendor's training population, what happens to AUC?"
        options={[
          { value: 'stays', label: 'It stays roughly the same — the ranking still works.' },
          { value: 'falls', label: 'It falls sharply.' },
          { value: 'rises', label: 'It rises, because the groups become more separable.' },
        ]}
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
          <div className="activity__split">
            <div className="activity__controls">
              <Slider
                label="Population mismatch"
                value={mismatch}
                min={0}
                max={1}
                step={0.05}
                format={(value) => `${(value * 100).toFixed(0)}%`}
                onChange={(value) => {
                  setMismatch(value);
                  tracker.parameter('mismatch', value);
                }}
                hint="Higher comorbidity and lower income than the vendor's development cohort."
              />
              <LiveResult>
                <div className="metric-row">
                  <Metric
                    label="AUC (discrimination)"
                    value={fixed(aucValue, 3)}
                    note="barely moves"
                    tone={aucValue > 0.8 ? 'success' : undefined}
                  />
                  <Metric
                    label="Calibration slope"
                    value={fixed(slope, 2)}
                    note="1.00 is perfect"
                    tone={Math.abs(slope - 1) > 0.25 ? 'danger' : 'success'}
                  />
                </div>
                <div className="metric-row" style={{ marginTop: 'var(--sp-3)' }}>
                  <Metric label="Flagged at 40% cut" value={`${atThreshold.tp + atThreshold.fp}`} />
                  <Metric label="Actually readmitted" value={`${atThreshold.tp + atThreshold.fn}`} />
                </div>
              </LiveResult>
            </div>

            <div>
              <LiveResult>
                <LineChart
                  title="Reliability diagram"
                  xLabel="Predicted probability"
                  yLabel="Observed rate"
                  xDomain={[0, 1]}
                  yDomain={[0, 1]}
                  series={[
                    {
                      label: 'Perfect calibration',
                      points: [
                        { x: 0, y: 0 },
                        { x: 1, y: 1 },
                      ],
                      color: 'var(--viz-6)',
                      dashed: true,
                    },
                    {
                      label: 'Vendor model here',
                      points: bins.map((bin) => ({ x: bin.predicted, y: bin.observed })),
                      color: 'var(--viz-4)',
                    },
                  ]}
                  caption="Above the diagonal: the model under-states risk. Below it: it over-states risk. Either way your protocol threshold no longer means what it says."
                />
              </LiveResult>
            </div>
          </div>

          <Callout
            tone={Math.abs(slope - 1) > 0.25 ? 'warning' : 'info'}
            title="Two properties, measured separately"
          >
            <p>
              AUC {fixed(aucValue, 3)} says the model still ranks patients well. Calibration slope{' '}
              {fixed(slope, 2)} says its probabilities{' '}
              {slope < 0.9 ? 'are too extreme in both directions' : slope > 1.1 ? 'are too conservative' : 'are trustworthy'}
              . A care pathway keyed to an absolute percentage depends on the second number, and AUC
              never reports it.
            </p>
          </Callout>

          <div style={{ marginTop: 'var(--sp-5)' }}>
            <Button
              variant="primary"
              onClick={() => {
                tracker.complete({ mismatch, auc: Number(aucValue.toFixed(3)), slope: Number(slope.toFixed(3)) });
                props.onComplete();
              }}
            >
              I have seen both extremes
            </Button>
          </div>
        </>
      ) : null}
    </ActivityShell>
  );
}

// ── Model card builder ───────────────────────────────────────────────────────

const CARD_FIELDS = [
  {
    name: 'intendedUse',
    label: 'Intended use',
    hint: 'Who uses it, for which decision, at what point in the workflow.',
    placeholder: 'ED triage nurses, to prioritize sepsis screening within 30 minutes of arrival…',
  },
  {
    name: 'outOfScope',
    label: 'Out-of-scope use',
    hint: 'The most important field. Name specific populations and settings.',
    placeholder: 'Not validated for patients under 18, for immunosuppressed patients, or for inpatients already on the ward…',
  },
  {
    name: 'trainingData',
    label: 'Training population',
    hint: 'Where, when, how many, and who is under-represented.',
    placeholder: '900 adult ED encounters, single academic centre, 2019–2023. 84% one ancestry group…',
  },
  {
    name: 'metrics',
    label: 'Performance and operating point',
    hint: 'Not just AUC. State the threshold and the metrics at it.',
    placeholder: 'At threshold 0.5: sensitivity 0.81, specificity 0.86, PPV 0.34 at 12% prevalence…',
  },
  {
    name: 'subgroups',
    label: 'Subgroup findings',
    hint: 'Report the gaps you found, including the ones you cannot yet explain.',
    placeholder: 'Sensitivity 0.79 in group A vs 0.63 in group B (n=94, CI wide)…',
  },
  {
    name: 'limitations',
    label: 'Caveats and limitations',
    hint: 'What could go wrong, and what monitoring would detect it.',
    placeholder: 'Depends on lactate being drawn; performance degrades if the analyzer is recalibrated…',
  },
] as const;

export function ModelCardBuilder(props: ActivityProps) {
  const [fields, setFields] = useState<Record<string, string>>({});
  const tracker = useInteractionTracker(props.activityKey, props);
  const { status, save } = useActivityAutosave(props.activityKey, props.moduleKey, props.pageKey);

  const filled = CARD_FIELDS.filter((field) => (fields[field.name] ?? '').trim().length > 10).length;

  return (
    <ActivityShell heading="Build a model card" completed={props.completed}>
      <div className="activity__split" style={{ gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr)' }}>
        <div style={{ display: 'grid', gap: 'var(--sp-4)' }}>
          {CARD_FIELDS.map((field) => (
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
          <SaveState status={status} />
        </div>

        <div>
          <div className="card" style={{ position: 'sticky', top: 'var(--sp-6)' }}>
            <p className="kicker">Model card preview</p>
            <h4 style={{ margin: 'var(--sp-2) 0 var(--sp-4)' }}>Sepsis Early Warning v1.0</h4>
            {CARD_FIELDS.map((field) => (
              <div key={field.name} style={{ marginBottom: 'var(--sp-4)' }}>
                <p
                  style={{
                    fontSize: 'var(--text-xs)',
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em',
                    color: 'var(--text-faint)',
                  }}
                >
                  {field.label}
                </p>
                <p style={{ fontSize: 'var(--text-sm)', marginTop: 4 }}>
                  {(fields[field.name] ?? '').trim() || (
                    <em style={{ color: 'var(--warning)' }}>Not specified — must be documented</em>
                  )}
                </p>
              </div>
            ))}
            <div className="meter">
              <div className="meter__fill" style={{ width: `${(filled / CARD_FIELDS.length) * 100}%` }} />
            </div>
            <p className="field__hint">
              {filled} of {CARD_FIELDS.length} fields documented
            </p>
          </div>
        </div>
      </div>

      <div style={{ marginTop: 'var(--sp-5)' }}>
        <Button
          variant="primary"
          disabled={filled < 4}
          onClick={() => {
            tracker.complete({ fields_completed: filled });
            save(fields, true);
            props.onComplete();
          }}
        >
          {filled < 4 ? `Complete at least 4 fields (${filled}/4)` : 'Save my model card'}
        </Button>
      </div>

      <div style={{ marginTop: 'var(--sp-4)' }}>
        <Reveal label="The field people write badly" eventContext={props}>
          <Prose
            body={[
              '"Out-of-scope use" is where model cards are usually weakest, because a generic caveat feels safer to write than a specific one.',
              '**Weak:** "Clinical judgement should always be used." Nobody has learned anything.',
              '**Strong:** "Not validated for patients under 18, for patients already on vasopressors, or where lactate has not been drawn within 4 hours. Do not use for inpatient deterioration — the model was fitted on ED presentations only."',
              'The second version can actually stop a wrong use. That is the entire purpose of the document.',
            ]}
          />
        </Reveal>
      </div>
    </ActivityShell>
  );
}
