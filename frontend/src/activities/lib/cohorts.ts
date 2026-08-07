/**
 * Synthetic cohort generators.
 *
 * Distribution parameters are taken from the legacy notebooks (eICU-style vitals, the diabetes
 * feature set, the sepsis and readmission simulators) so the rebuilt activities behave like the
 * originals — without redistributing patient data.
 */

import { clamp, gamma, normal, rng, sigmoid } from './math';

export type Patient = {
  id: number;
  age: number;
  heartRate: number;
  systolic: number;
  temperature: number;
  lactate: number;
  wbc: number;
  creatinine: number;
  glucose: number;
  bmi: number;
  smoker: 0 | 1;
  group: 'A' | 'B';
  label: 0 | 1;
  score: number;
};

/** ICU-style vitals with a few deliberate data-entry errors and real physiological extremes. */
export function vitalsCohort(n = 30, seed = 42) {
  const next = rng(seed);
  const rows = Array.from({ length: n }, (_, i) => ({
    id: i + 1,
    heartRate: Math.round(normal(next, 78, 11)),
    map: Math.round(normal(next, 85, 12)),
    temperature: Number(normal(next, 37, 0.55).toFixed(1)),
  }));
  // Two transcription errors and two genuine extremes, at fixed indices so the lab is stable.
  if (rows[3]) rows[3].heartRate = 2; // impossible — transcription error
  if (rows[11]) rows[11].heartRate = 168; // real: septic tachycardia
  if (rows[18]) rows[18].map = 212; // implausible — cuff artifact
  if (rows[24]) rows[24].temperature = 41.6; // real: severe hyperthermia
  return rows;
}

export type SepsisRow = { age: number; lactate: number; wbc: number; label: 0 | 1 };

/** Sepsis cohort with tunable covariate shift on lactate and WBC (legacy 2.5 Activity 1). */
export function sepsisCohort(n: number, driftSeverity: number, seed = 42): SepsisRow[] {
  const next = rng(seed);
  return Array.from({ length: n }, () => {
    const age = Math.round(clamp(normal(next, 65, 12), 18, 98));
    const lactate = clamp(gamma(next, 2, 1.5) + driftSeverity * 2.0, 0.2, 18);
    const wbc = clamp(normal(next, 10, 3) + driftSeverity * 1.5, 0.5, 40);
    const logit = -5 + 0.05 * age + 0.8 * lactate + 0.1 * wbc;
    const label: 0 | 1 = next() < sigmoid(logit) ? 1 : 0;
    return { age, lactate, wbc, label };
  });
}

/** Simple logistic fit by gradient descent — enough to demonstrate retraining honestly. */
export function fitLogistic(
  rows: Array<{ features: number[]; label: number }>,
  iterations = 400,
  learningRate = 0.06,
): { weights: number[]; intercept: number } {
  const dim = rows[0]?.features.length ?? 0;
  if (dim === 0) return { weights: [], intercept: 0 };

  // Standardize so gradient descent converges in a fixed iteration budget.
  const means = Array.from({ length: dim }, (_, j) =>
    rows.reduce((a, row) => a + (row.features[j] ?? 0), 0) / rows.length,
  );
  const sds = Array.from({ length: dim }, (_, j) => {
    const m = means[j] ?? 0;
    const v = rows.reduce((a, row) => a + ((row.features[j] ?? 0) - m) ** 2, 0) / rows.length;
    return Math.sqrt(v) || 1;
  });

  let weights = new Array<number>(dim).fill(0);
  let intercept = 0;

  for (let iter = 0; iter < iterations; iter += 1) {
    const gradW = new Array<number>(dim).fill(0);
    let gradB = 0;
    for (const row of rows) {
      let z = intercept;
      for (let j = 0; j < dim; j += 1) {
        z += (weights[j] ?? 0) * (((row.features[j] ?? 0) - (means[j] ?? 0)) / (sds[j] ?? 1));
      }
      const error = sigmoid(z) - row.label;
      for (let j = 0; j < dim; j += 1) {
        gradW[j] =
          (gradW[j] ?? 0) + error * (((row.features[j] ?? 0) - (means[j] ?? 0)) / (sds[j] ?? 1));
      }
      gradB += error;
    }
    const scale = learningRate / rows.length;
    weights = weights.map((w, j) => w - scale * (gradW[j] ?? 0));
    intercept -= scale * gradB;
  }

  // Fold standardization back into the coefficients so predict() takes raw features.
  const rawWeights = weights.map((w, j) => w / (sds[j] ?? 1));
  const rawIntercept =
    intercept - rawWeights.reduce((a, w, j) => a + w * (means[j] ?? 0), 0);
  return { weights: rawWeights, intercept: rawIntercept };
}

export function predictLogistic(
  model: { weights: number[]; intercept: number },
  features: number[],
): number {
  let z = model.intercept;
  for (let j = 0; j < model.weights.length; j += 1) {
    z += (model.weights[j] ?? 0) * (features[j] ?? 0);
  }
  return sigmoid(z);
}

/** Readmission cohort where local population mismatch can be dialled up (legacy 2.5 Activity 2). */
export function readmissionCohort(n: number, mismatch: number, seed = 101) {
  const next = rng(seed);
  return Array.from({ length: n }, () => {
    const comorbidity = clamp(normal(next, 5 + mismatch * 3, 2), 0, 15);
    const income = normal(next, 60 + mismatch * -25, 15);
    const logit = -4 + 0.4 * comorbidity - 0.02 * income;
    const label: 0 | 1 = next() < sigmoid(logit) ? 1 : 0;
    return { comorbidity, income, label };
  });
}

/**
 * Two-subgroup diagnostic cohort with a deliberate performance gap (legacy 2.7 / 4.7).
 *
 * Tuned to behave like a real diagnostic study: prevalence around 20%, AUC around 0.85, and a
 * subgroup gap driven by the model being fitted mostly on group A. Features are centred so the
 * intercept controls prevalence directly.
 */
export const DIAGNOSTIC_CENTRES = { age: 56, glucose: 120, bmi: 30, bp: 128 } as const;
const TRUE_COEFFS = { age: 0.075, glucose: 0.05, bmi: 0.15, bp: 0.03 } as const;
const TRUE_INTERCEPT = -3.1;

function trueLogit(row: { age: number; glucose: number; bmi: number; bp: number }): number {
  return (
    TRUE_INTERCEPT +
    TRUE_COEFFS.age * (row.age - DIAGNOSTIC_CENTRES.age) +
    TRUE_COEFFS.glucose * (row.glucose - DIAGNOSTIC_CENTRES.glucose) +
    TRUE_COEFFS.bmi * (row.bmi - DIAGNOSTIC_CENTRES.bmi) +
    TRUE_COEFFS.bp * (row.bp - DIAGNOSTIC_CENTRES.bp)
  );
}

export function diagnosticCohort(n = 400, seed = 7) {
  const next = rng(seed);
  return Array.from({ length: n }, (_, i) => {
    // Group B is the smaller subgroup and was under-represented when the model was fitted.
    const group: 'A' | 'B' = next() < 0.75 ? 'A' : 'B';
    const age = Math.round(clamp(normal(next, group === 'A' ? 58 : 47, 13), 18, 92));
    const glucose = clamp(normal(next, group === 'A' ? 118 : 132, 32), 55, 320);
    const bmi = clamp(normal(next, group === 'A' ? 29 : 32, 6), 15, 55);
    const bp = clamp(normal(next, 128, 17), 80, 210);
    const row = { age, glucose, bmi, bp };
    const label: 0 | 1 = next() < sigmoid(trueLogit(row)) ? 1 : 0;

    // The deployed model approximates the truth, with extra shrinkage for group B — which is what
    // produces a genuine sensitivity gap rather than a cosmetic one.
    const modelLogit =
      trueLogit(row) * (group === 'B' ? 0.62 : 1.0) +
      (group === 'B' ? -0.5 : 0) +
      normal(next, 0, 0.6);
    return { id: i + 1, group, ...row, label, score: sigmoid(modelLogit) };
  });
}

export const DIAGNOSTIC_FEATURES = [
  { key: 'age', label: 'Age', unit: 'years', min: 18, max: 92, step: 1, weight: TRUE_COEFFS.age },
  {
    key: 'glucose',
    label: 'Glucose',
    unit: 'mg/dL',
    min: 55,
    max: 320,
    step: 1,
    weight: TRUE_COEFFS.glucose,
  },
  { key: 'bmi', label: 'BMI', unit: 'kg/m²', min: 15, max: 55, step: 0.5, weight: TRUE_COEFFS.bmi },
  {
    key: 'bp',
    label: 'Systolic BP',
    unit: 'mmHg',
    min: 80,
    max: 210,
    step: 1,
    weight: TRUE_COEFFS.bp,
  },
] as const;

/** Same centred model the cohort uses, so the what-if risks match the rest of the module. */
export function diagnosticRisk(profile: Record<string, number>): number {
  return sigmoid(
    trueLogit({
      age: profile.age ?? DIAGNOSTIC_CENTRES.age,
      glucose: profile.glucose ?? DIAGNOSTIC_CENTRES.glucose,
      bmi: profile.bmi ?? DIAGNOSTIC_CENTRES.bmi,
      bp: profile.bp ?? DIAGNOSTIC_CENTRES.bp,
    }),
  );
}

export const DIAGNOSTIC_CENTRE_VALUES: Record<string, number> = { ...DIAGNOSTIC_CENTRES };

/** kNN-style two-feature cohort for the decision-boundary activity (legacy 4.6). */
export function boundaryCohort(n = 140, seed = 11) {
  const next = rng(seed);
  return Array.from({ length: n }, () => {
    const label: 0 | 1 = next() < 0.5 ? 1 : 0;
    const cx = label === 1 ? 1.05 : -1.05;
    const x = normal(next, cx, 1.0);
    const y = normal(next, label === 1 ? 0.75 : -0.75, 1.05);
    // 12% label noise creates the points a k=1 model will contort itself around.
    const noisy: 0 | 1 = next() < 0.12 ? ((1 - label) as 0 | 1) : label;
    return { x, y, label: noisy };
  });
}

export function knnPredict(
  train: Array<{ x: number; y: number; label: number }>,
  point: { x: number; y: number },
  k: number,
): number {
  const distances = train
    .map((row) => ({ label: row.label, d: (row.x - point.x) ** 2 + (row.y - point.y) ** 2 }))
    .sort((a, b) => a.d - b.d)
    .slice(0, Math.max(1, k));
  const votes = distances.reduce((sum, row) => sum + row.label, 0);
  return votes / distances.length >= 0.5 ? 1 : 0;
}
