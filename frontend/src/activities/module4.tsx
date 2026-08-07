import { useMemo, useState } from 'react';
import { BarChart, ConfusionMatrix, LineChart, ScatterChart } from '@/components/charts';
import { Prose } from '@/components/Prose';
import { Button, Callout, Metric, Reveal, Segmented, Slider } from '@/components/primitives';
import { useInteractionTracker } from '@/analytics/useInteractionTracker';
import { ActivityShell, LiveResult, type ActivityProps } from './ActivityShell';
import {
  DIAGNOSTIC_FEATURES,
  boundaryCohort,
  diagnosticCohort,
  diagnosticRisk,
  knnPredict,
} from './lib/cohorts';
import { auc, confusion, fixed, metrics, percent, rocCurve, sd } from './lib/math';

// ── Decision boundary ────────────────────────────────────────────────────────

export function DecisionBoundary(props: ActivityProps) {
  const [k, setK] = useState(1);
  const tracker = useInteractionTracker(props.activityKey, props);

  const { train, test } = useMemo(() => {
    const all = boundaryCohort(180, 11);
    return { train: all.slice(0, 126), test: all.slice(126) };
  }, []);

  const trainAccuracy = useMemo(
    () => train.filter((row) => knnPredict(train, row, k) === row.label).length / train.length,
    [k, train],
  );
  const testAccuracy = useMemo(
    () => test.filter((row) => knnPredict(train, row, k) === row.label).length / test.length,
    [k, test, train],
  );

  // Sparse grid so the boundary is visible without a canvas.
  const grid = useMemo(() => {
    const points: Array<{ x: number; y: number; label: number }> = [];
    for (let x = -3.4; x <= 3.4; x += 0.34) {
      for (let y = -3.4; y <= 3.4; y += 0.34) {
        points.push({ x, y, label: knnPredict(train, { x, y }, k) });
      }
    }
    return points;
  }, [k, train]);

  return (
    <ActivityShell heading="Overfitting and underfitting" completed={props.completed}>
      <Slider
        label="Model complexity (k nearest neighbours)"
        value={k}
        min={1}
        max={35}
        step={1}
        onChange={(value) => {
          setK(value);
          tracker.parameter('k', value);
        }}
        hint="k = 1 is the most complex model (every point defines its own region). Large k is the simplest."
      />

      <LiveResult>
        <div className="metric-row" style={{ margin: 'var(--sp-4) 0' }}>
          <Metric label="Training accuracy" value={percent(trainAccuracy, 1)} />
          <Metric label="Test accuracy" value={percent(testAccuracy, 1)} />
          <Metric
            label="Gap"
            value={percent(trainAccuracy - testAccuracy, 1)}
            tone={trainAccuracy - testAccuracy > 0.15 ? 'danger' : 'success'}
            note={trainAccuracy - testAccuracy > 0.15 ? 'overfitting' : 'generalizing'}
          />
        </div>

        <ScatterChart
          title={`Decision regions at k = ${k}`}
          xLabel="Standardized biomarker 1"
          yLabel="Standardized biomarker 2"
          height={360}
          groups={[
            {
              label: 'Predicted: outcome',
              points: grid.filter((point) => point.label === 1),
              color: 'var(--viz-1)',
            },
            {
              label: 'Predicted: no outcome',
              points: grid.filter((point) => point.label === 0),
              color: 'var(--viz-2)',
            },
          ]}
          caption={
            k <= 3
              ? 'At low k the regions fragment into islands around individual points — including the 12% of points whose labels are noise. That is memorization.'
              : k >= 20
                ? 'At high k the boundary is a smooth division. Simple, stable, and it will miss any genuinely local structure.'
                : 'A boundary that follows the broad structure without chasing individual points.'
          }
        />
      </LiveResult>

      <div style={{ marginTop: 'var(--sp-5)' }}>
        <Button
          variant="primary"
          onClick={() => {
            tracker.complete({ final_k: k, gap: Number((trainAccuracy - testAccuracy).toFixed(3)) });
            props.onComplete();
          }}
        >
          I have seen both extremes
        </Button>
      </div>

      <div style={{ marginTop: 'var(--sp-4)' }}>
        <Reveal label="Why the noisy points matter so much" eventContext={props}>
          <Prose
            body={[
              'Twelve per cent of these points have deliberately flipped labels — the equivalent of a mislabelled scan or a coding error.',
              'At k = 1 the model builds a region around every one of them, because it has no way to distinguish a mislabelled point from a genuinely unusual patient. Training accuracy hits 100% and test accuracy falls.',
              'That is the whole mechanism of overfitting: the model has enough capacity to represent noise, and no reason not to.',
            ]}
          />
        </Reveal>
      </div>
    </ActivityShell>
  );
}

// ── Complexity curve ─────────────────────────────────────────────────────────

export function ComplexityCurve(props: ActivityProps) {
  const [maxK, setMaxK] = useState(25);
  const tracker = useInteractionTracker(props.activityKey, props);

  const { train, test } = useMemo(() => {
    const all = boundaryCohort(180, 11);
    return { train: all.slice(0, 126), test: all.slice(126) };
  }, []);

  const curves = useMemo(() => {
    const trainPoints: Array<{ x: number; y: number }> = [];
    const testPoints: Array<{ x: number; y: number }> = [];
    for (let k = 1; k <= maxK; k += 1) {
      trainPoints.push({
        x: k,
        y: train.filter((row) => knnPredict(train, row, k) === row.label).length / train.length,
      });
      testPoints.push({
        x: k,
        y: test.filter((row) => knnPredict(train, row, k) === row.label).length / test.length,
      });
    }
    return { trainPoints, testPoints };
  }, [maxK, test, train]);

  const best = curves.testPoints.reduce(
    (bestSoFar, point) => (point.y > bestSoFar.y ? point : bestSoFar),
    { x: 1, y: 0 },
  );

  return (
    <ActivityShell heading="Find the sweet spot" completed={props.completed}>
      <Slider
        label="Complexity range to test"
        value={maxK}
        min={5}
        max={40}
        step={1}
        onChange={(value) => {
          setMaxK(value);
          tracker.parameter('max_k', value);
        }}
      />

      <LiveResult>
        <LineChart
          title="Training and test accuracy across complexity"
          xLabel="k (higher = simpler model)"
          yLabel="Accuracy"
          yDomain={[0.4, 1.02]}
          series={[
            { label: 'Training accuracy', points: curves.trainPoints, color: 'var(--viz-2)' },
            { label: 'Test accuracy', points: curves.testPoints, color: 'var(--viz-1)' },
          ]}
          markers={[{ x: best.x, label: `best k = ${best.x}` }]}
          caption="Read right to left: at large k both curves are low and together (underfitting). As k falls they separate — the training curve keeps rising while the test curve turns over. That turning point is where you stop."
        />
        <div className="metric-row" style={{ marginTop: 'var(--sp-4)' }}>
          <Metric label="Best k on test data" value={`${best.x}`} />
          <Metric label="Test accuracy there" value={percent(best.y, 1)} />
          <Metric
            label="Gap at k = 1"
            value={percent(
              (curves.trainPoints[0]?.y ?? 0) - (curves.testPoints[0]?.y ?? 0),
              1,
            )}
            tone="danger"
          />
        </div>
      </LiveResult>

      <Callout tone="warning" title="The trap this activity sets">
        <p>
          You just picked k by looking at the test set. That makes this test score optimistic — it is
          now a *tuning* set, not a held-out one. In a real study you tune on a validation split (or
          inner cross-validation folds) and touch the test set exactly once, at the end.
        </p>
      </Callout>

      <div style={{ marginTop: 'var(--sp-5)' }}>
        <Button
          variant="primary"
          onClick={() => {
            tracker.complete({ best_k: best.x, best_accuracy: Number(best.y.toFixed(3)) });
            props.onComplete();
          }}
        >
          I have found the divergence point
        </Button>
      </div>
    </ActivityShell>
  );
}

// ── Cross-validation ─────────────────────────────────────────────────────────

type CvStrategy = 'single' | 'kfold' | 'stratified' | 'grouped';

export function CrossValidation(props: ActivityProps) {
  const [strategy, setStrategy] = useState<CvStrategy>('single');
  const [folds, setFolds] = useState(5);
  const tracker = useInteractionTracker(props.activityKey, props);

  const cohort = useMemo(() => boundaryCohort(200, 11), []);

  /** Repeated-patient structure: every 5th row is a second admission for the previous patient. */
  const patientIds = useMemo(() => cohort.map((_, index) => Math.floor(index / 1.6)), [cohort]);

  const result = useMemo(() => {
    const k = strategy === 'single' ? 1 : folds;
    const scores: number[] = [];

    for (let fold = 0; fold < k; fold += 1) {
      let testIdx: number[];
      if (strategy === 'single') {
        testIdx = cohort.map((_, i) => i).filter((i) => i >= cohort.length * 0.8);
      } else if (strategy === 'grouped') {
        // Assign whole patients to folds so no patient straddles the split.
        testIdx = cohort
          .map((_, i) => i)
          .filter((i) => (patientIds[i] ?? 0) % k === fold);
      } else if (strategy === 'stratified') {
        // Balance outcome prevalence across folds by striping within each class.
        const positives = cohort.map((_, i) => i).filter((i) => cohort[i]?.label === 1);
        const negatives = cohort.map((_, i) => i).filter((i) => cohort[i]?.label === 0);
        testIdx = [
          ...positives.filter((_, order) => order % k === fold),
          ...negatives.filter((_, order) => order % k === fold),
        ];
      } else {
        testIdx = cohort.map((_, i) => i).filter((i) => i % k === fold);
      }

      const testSet = new Set(testIdx);
      const trainRows = cohort.filter((_, i) => !testSet.has(i));
      const testRows = cohort.filter((_, i) => testSet.has(i));
      if (trainRows.length === 0 || testRows.length === 0) continue;
      scores.push(
        testRows.filter((row) => knnPredict(trainRows, row, 7) === row.label).length / testRows.length,
      );
    }

    const meanScore = scores.reduce((a, b) => a + b, 0) / (scores.length || 1);
    return { scores, mean: meanScore, spread: sd(scores) };
  }, [cohort, folds, patientIds, strategy]);

  return (
    <ActivityShell heading="Compare validation strategies" completed={props.completed}>
      <div className="activity__split">
        <div className="activity__controls">
          <Segmented
            label="Validation strategy"
            value={strategy}
            options={[
              { value: 'single', label: 'Single 80/20' },
              { value: 'kfold', label: 'K-fold' },
              { value: 'stratified', label: 'Stratified' },
              { value: 'grouped', label: 'Grouped by patient' },
            ]}
            onChange={(value) => {
              setStrategy(value);
              tracker.parameter('strategy', value);
            }}
          />
          {strategy !== 'single' ? (
            <Slider
              label="Number of folds"
              value={folds}
              min={3}
              max={10}
              step={1}
              onChange={(value) => {
                setFolds(value);
                tracker.parameter('folds', value);
              }}
            />
          ) : null}
          <LiveResult>
            <div className="metric-row">
              <Metric label="Mean accuracy" value={percent(result.mean, 1)} />
              <Metric
                label="Fold-to-fold SD"
                value={strategy === 'single' ? '—' : percent(result.spread, 1)}
                note={strategy === 'single' ? 'one split gives no spread' : 'your uncertainty'}
                tone={result.spread > 0.08 ? 'warning' : undefined}
              />
            </div>
          </LiveResult>
        </div>

        <div>
          <LiveResult>
            {strategy === 'single' ? (
              <Callout tone="warning" title="A single split gives you one number and no uncertainty">
                <p>
                  Accuracy {percent(result.mean, 1)}. Split the data differently and you would get a
                  different answer, and you have no way to know how different. Switch to k-fold to see
                  the spread this single number is hiding.
                </p>
              </Callout>
            ) : (
              <BarChart
                title={`Accuracy per fold — ${strategy}`}
                yLabel="Accuracy"
                yDomain={[0.4, 1]}
                bars={result.scores.map((score, index) => ({
                  label: `Fold ${index + 1}`,
                  value: score,
                  color: 'var(--viz-1)',
                }))}
                referenceLine={{ value: result.mean, label: `mean ${percent(result.mean, 1)}` }}
                valueFormat={(value) => value.toFixed(2)}
                caption="The height differences between folds are your uncertainty. Reporting only the mean hides them."
              />
            )}
            <Callout tone="info" title="What this strategy does and does not fix">
              <p>
                {strategy === 'single'
                  ? 'Fast, and gives you no estimate of variance. Acceptable only with a large dataset.'
                  : strategy === 'kfold'
                    ? 'Every case is tested once and you get a spread. It does nothing about repeated patients — the same person can be in training and testing.'
                    : strategy === 'stratified'
                      ? 'Outcome prevalence is now balanced across folds, which stabilizes the estimate for imbalanced data. Repeated patients still leak.'
                      : 'Whole patients are kept in a single fold, which closes the leak. The accuracy is lower and it is the number you should report.'}
              </p>
            </Callout>
          </LiveResult>
        </div>
      </div>

      <div style={{ marginTop: 'var(--sp-5)' }}>
        <Button
          variant="primary"
          onClick={() => {
            tracker.complete({ strategy, folds, mean: Number(result.mean.toFixed(3)) });
            props.onComplete();
          }}
        >
          I have compared all four
        </Button>
      </div>
    </ActivityShell>
  );
}

// ── Threshold explorer ───────────────────────────────────────────────────────

export function ThresholdExplorer(props: ActivityProps) {
  const [threshold, setThreshold] = useState(0.5);
  const tracker = useInteractionTracker(props.activityKey, props);

  const cohort = useMemo(() => diagnosticCohort(400, 7), []);
  const labels = cohort.map((row) => row.label);
  const scores = cohort.map((row) => row.score);
  const m = metrics(confusion(labels, scores, threshold));
  const roc = useMemo(() => rocCurve(labels, scores, 50), [labels, scores]);
  const aucValue = useMemo(() => auc(labels, scores), [labels, scores]);

  const operating = { x: 1 - m.specificity, y: m.sensitivity };

  return (
    <ActivityShell heading="Move the threshold" completed={props.completed}>
      <Slider
        label="Decision threshold"
        value={threshold}
        min={0.02}
        max={0.98}
        step={0.01}
        format={(value) => value.toFixed(2)}
        onChange={(value) => {
          setThreshold(value);
          tracker.parameter('threshold', value);
        }}
        hint="Every patient with a predicted risk at or above this value is flagged."
      />

      <LiveResult>
        <div className="metric-row" style={{ margin: 'var(--sp-5) 0' }}>
          <Metric label="Sensitivity" value={percent(m.sensitivity, 1)} note="cases caught" />
          <Metric label="Specificity" value={percent(m.specificity, 1)} note="healthy cleared" />
          <Metric
            label="PPV"
            value={percent(m.ppv, 1)}
            note={`at ${percent(m.prevalence, 1)} prevalence`}
          />
          <Metric label="F1" value={fixed(m.f1, 3)} />
          <Metric label="Accuracy" value={percent(m.accuracy, 1)} note="least useful here" />
        </div>

        <div
          className="activity__split"
          style={{ gridTemplateColumns: 'minmax(0, 1.15fr) minmax(0, 1fr)' }}
        >
          <div>
            <ConfusionMatrix tn={m.tn} fp={m.fp} fn={m.fn} tp={m.tp} />
            <Callout tone={m.fn > m.tp ? 'danger' : 'info'} title="In patients">
              <p>
                <strong>{m.fn}</strong> patients with the condition are missed.{' '}
                <strong>{m.fp}</strong> without it are sent for unnecessary further investigation.
                Which of those two numbers you would rather reduce is a clinical judgement, not a
                statistical one.
              </p>
            </Callout>
          </div>
          <div>
            <LineChart
              title="ROC curve and your operating point"
              xLabel="False positive rate (1 − specificity)"
              yLabel="Sensitivity"
              xDomain={[0, 1]}
              yDomain={[0, 1]}
              height={320}
              series={[
                {
                  label: 'Chance',
                  points: [
                    { x: 0, y: 0 },
                    { x: 1, y: 1 },
                  ],
                  color: 'var(--viz-6)',
                  dashed: true,
                },
                {
                  label: `Model (AUC ${fixed(aucValue, 3)})`,
                  points: roc.map((point) => ({ x: point.fpr, y: point.tpr })),
                  color: 'var(--viz-1)',
                },
                { label: 'Your threshold', points: [operating], color: 'var(--viz-2)' },
              ]}
              caption="Moving the slider slides your operating point along a fixed curve. The curve — and the AUC — never change."
            />
          </div>
        </div>
      </LiveResult>

      <div style={{ marginTop: 'var(--sp-5)' }}>
        <Button
          variant="primary"
          onClick={() => {
            tracker.complete({ threshold, sensitivity: Number(m.sensitivity.toFixed(3)), ppv: Number(m.ppv.toFixed(3)) });
            props.onComplete();
          }}
        >
          I have explored the trade-off
        </Button>
      </div>
    </ActivityShell>
  );
}

// ── Explanation lab ──────────────────────────────────────────────────────────

export function ExplanationLab(props: ActivityProps) {
  const [patientIndex, setPatientIndex] = useState(0);
  const tracker = useInteractionTracker(props.activityKey, props);

  const cohort = useMemo(() => diagnosticCohort(60, 7), []);
  const patient = cohort[patientIndex] ?? cohort[0];

  const cohortMeans = useMemo(
    () =>
      Object.fromEntries(
        DIAGNOSTIC_FEATURES.map((feature) => [
          feature.key,
          cohort.reduce((sum, row) => sum + (row[feature.key as keyof typeof row] as number), 0) /
            cohort.length,
        ]),
      ) as Record<string, number>,
    [cohort],
  );

  /** Global importance: |weight| × feature spread, the standard transparent proxy. */
  const globalImportance = useMemo(
    () =>
      DIAGNOSTIC_FEATURES.map((feature) => {
        const values = cohort.map((row) => row[feature.key as keyof typeof row] as number);
        return { label: feature.label, value: Math.abs(feature.weight) * sd(values) };
      }).sort((a, b) => b.value - a.value),
    [cohort],
  );

  /** Local contribution: weight × (this patient − cohort mean), i.e. why *this* prediction. */
  const localContributions = useMemo(() => {
    if (!patient) return [];
    return DIAGNOSTIC_FEATURES.map((feature) => {
      const value = patient[feature.key as keyof typeof patient] as number;
      return {
        label: feature.label,
        value: feature.weight * (value - (cohortMeans[feature.key] ?? 0)),
        raw: value,
        unit: feature.unit,
      };
    }).sort((a, b) => Math.abs(b.value) - Math.abs(a.value));
  }, [cohortMeans, patient]);

  const topGlobal = globalImportance[0]?.label;
  const topLocal = localContributions[0]?.label;
  const disagrees = topGlobal !== topLocal;

  return (
    <ActivityShell heading="Explain the model" completed={props.completed}>
      <div className="activity__split" style={{ gridTemplateColumns: 'minmax(0,1fr) minmax(0,1fr)' }}>
        <div>
          <h4 style={{ marginBottom: 'var(--sp-3)', fontSize: 'var(--text-md)' }}>
            Global · across all patients
          </h4>
          <BarChart
            title="Feature importance across the cohort"
            yLabel="Contribution to variation in risk"
            height={260}
            bars={globalImportance.map((row, index) => ({
              label: row.label,
              value: row.value,
              color: index === 0 ? 'var(--viz-1)' : 'var(--viz-6)',
            }))}
            valueFormat={(value) => value.toFixed(2)}
            caption="Computed as |coefficient| × the feature's spread in this cohort. A feature with a large coefficient but no variation drives nothing."
          />
        </div>

        <div>
          <h4 style={{ marginBottom: 'var(--sp-3)', fontSize: 'var(--text-md)' }}>
            Local · this patient
          </h4>
          <Slider
            label="Patient"
            value={patientIndex}
            min={0}
            max={cohort.length - 1}
            step={1}
            format={(value) => `#${value + 1} of ${cohort.length}`}
            onChange={(value) => {
              setPatientIndex(value);
              tracker.parameter('patient', value);
            }}
          />
          <LiveResult>
            <div className="metric-row" style={{ margin: 'var(--sp-3) 0' }}>
              <Metric
                label="Predicted risk"
                value={percent(patient?.score ?? 0, 1)}
                tone={(patient?.score ?? 0) > 0.5 ? 'warning' : undefined}
              />
              <Metric label="Actual outcome" value={patient?.label === 1 ? 'Positive' : 'Negative'} />
            </div>
            <BarChart
              title="Why this patient's prediction"
              yLabel="Push on log-odds"
              height={260}
              bars={localContributions.map((row) => ({
                label: row.label,
                value: row.value,
                color: row.value > 0 ? 'var(--viz-5)' : 'var(--viz-3)',
                note: `${fixed(row.raw, 0)} ${row.unit}`,
              }))}
              valueFormat={(value) => (value > 0 ? `+${value.toFixed(2)}` : value.toFixed(2))}
              caption="Positive bars pushed this patient's risk up relative to the cohort average; negative bars pushed it down."
            />
          </LiveResult>
        </div>
      </div>

      <LiveResult>
        <Callout tone={disagrees ? 'warning' : 'info'} title={disagrees ? 'Global and local disagree here' : 'Global and local agree here'}>
          <p>
            {disagrees
              ? `Across the cohort, ${topGlobal} drives the most variation. For patient #${patientIndex + 1}, the biggest push comes from ${topLocal}. Both are correct — they answer different questions, which is exactly why a clinician needs the local view and a reviewer needs the global one.`
              : `${topGlobal} dominates both views for this patient. Move through a few more patients to find one where they diverge.`}
          </p>
        </Callout>
      </LiveResult>

      <div style={{ marginTop: 'var(--sp-5)' }}>
        <Button
          variant="primary"
          onClick={() => {
            tracker.complete({ patients_viewed: patientIndex + 1, found_divergence: disagrees });
            props.onComplete();
          }}
        >
          I have compared global and local views
        </Button>
      </div>
    </ActivityShell>
  );
}

// ── What-if simulator ────────────────────────────────────────────────────────

export function WhatIf(props: ActivityProps) {
  const [profile, setProfile] = useState<Record<string, number>>(() =>
    Object.fromEntries(
      DIAGNOSTIC_FEATURES.map((feature) => [feature.key, Math.round((feature.min + feature.max) / 2)]),
    ),
  );
  const tracker = useInteractionTracker(props.activityKey, props);

  const risk = diagnosticRisk(profile);

  /** Sensitivity: risk change from moving each feature across its interquartile-ish range. */
  const sensitivity = useMemo(
    () =>
      DIAGNOSTIC_FEATURES.map((feature) => {
        const span = (feature.max - feature.min) * 0.25;
        const lo = diagnosticRisk({ ...profile, [feature.key]: (profile[feature.key] ?? 0) - span });
        const hi = diagnosticRisk({ ...profile, [feature.key]: (profile[feature.key] ?? 0) + span });
        return { label: feature.label, value: Math.abs(hi - lo) };
      }).sort((a, b) => b.value - a.value),
    [profile],
  );

  return (
    <ActivityShell heading="What-if simulator" completed={props.completed}>
      <div className="activity__split">
        <div className="activity__controls">
          {DIAGNOSTIC_FEATURES.map((feature) => (
            <Slider
              key={feature.key}
              label={feature.label}
              value={profile[feature.key] ?? feature.min}
              min={feature.min}
              max={feature.max}
              step={feature.step}
              unit={feature.unit}
              onChange={(value) => {
                setProfile((prev) => ({ ...prev, [feature.key]: value }));
                tracker.parameter(feature.key, value);
              }}
            />
          ))}
        </div>

        <div>
          <LiveResult>
            <div
              className="card"
              style={{
                textAlign: 'center',
                background: risk > 0.5 ? 'var(--danger-soft)' : 'var(--success-soft)',
                borderColor: risk > 0.5 ? 'var(--danger-border)' : 'var(--success-border)',
              }}
            >
              <p className="kicker">Model output</p>
              <p
                style={{
                  fontSize: 'var(--text-3xl)',
                  fontWeight: 700,
                  fontVariantNumeric: 'tabular-nums',
                  color: risk > 0.5 ? 'var(--danger)' : 'var(--success)',
                  margin: 'var(--sp-2) 0',
                }}
              >
                {percent(risk, 1)}
              </p>
              <p style={{ fontSize: 'var(--text-sm)', fontWeight: 650 }}>
                {risk > 0.5 ? 'Above the 50% threshold — would be flagged' : 'Below the 50% threshold — would not be flagged'}
              </p>
              <div className="meter" style={{ marginTop: 'var(--sp-4)' }}>
                <div
                  className="meter__fill"
                  style={{
                    width: `${risk * 100}%`,
                    background: risk > 0.5 ? 'var(--danger)' : 'var(--success)',
                  }}
                />
              </div>
            </div>

            <div style={{ marginTop: 'var(--sp-4)' }}>
              <BarChart
                title="Which variable moves the prediction most"
                yLabel="Change in predicted risk"
                height={240}
                bars={sensitivity.map((row, index) => ({
                  label: row.label,
                  value: row.value,
                  color: index === 0 ? 'var(--viz-2)' : 'var(--viz-6)',
                }))}
                valueFormat={(value) => percent(value, 1)}
                caption="Measured by moving each variable across a quarter of its range from the current profile."
              />
            </div>

            <Callout tone="warning" title="The question this activity is really asking">
              <p>
                <strong>{sensitivity[0]?.label}</strong> moves this prediction most. Is that
                clinically sensible? If a model is most sensitive to a variable a clinician would call
                secondary, you have found either a real insight or a data artifact — and it is worth
                knowing which before deployment.
              </p>
            </Callout>
          </LiveResult>
        </div>
      </div>

      <div style={{ marginTop: 'var(--sp-5)' }}>
        <Button
          variant="primary"
          onClick={() => {
            tracker.complete({ profile, risk: Number(risk.toFixed(3)), most_sensitive: sensitivity[0]?.label });
            props.onComplete();
          }}
        >
          I have explored the model's sensitivity
        </Button>
      </div>
    </ActivityShell>
  );
}
